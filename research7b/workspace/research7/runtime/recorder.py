"""Immutable, fsync-published evidence with byte-exact wire retention."""
import base64
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import uuid

from .journal import (
    JournalWriter,
    scan_journal,
    decode,
    encode,
    read_frames,
    HEADER,
    MAX_RECORD,
)


def compute_bytes_sha256(data):
    return hashlib.sha256(data).hexdigest()

def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)

def publish(path, content):
    path = Path(path)
    temp = path.with_name(path.name + '.tmp.' + uuid.uuid4().hex)
    with temp.open('xb') as f:
        f.write(content); f.flush(); os.fsync(f.fileno())
    try:
        os.link(temp, path)
        fsync_dir(path.parent)
    finally:
        temp.unlink(missing_ok=True)

def write_json(path, value):
    publish(path, (json.dumps(value, sort_keys=True, allow_nan=False)+'\n').encode())

def stamp():
    return datetime.now(timezone.utc).isoformat()

@dataclass
class SegmentMetadata:
    segment_id: str
    sequence: int
    day: int
    phase: str
    uncompressed_bytes: int
    compressed_bytes: int
    sha256: str
    timestamp_utc: str
    def to_dict(self): return asdict(self)
    def to_json(self): return json.dumps(self.to_dict(), sort_keys=True)

class AttemptLogger:
    def __init__(self, base_dir, cell_key_hash, attempt_id=None, format_version=1):
        self.base_dir, self.cell_key_hash = Path(base_dir), cell_key_hash
        self.attempt_id = attempt_id or uuid.uuid4().hex
        self.format_version = format_version
        self.attempt_dir = self.base_dir/'attempts'/cell_key_hash/self.attempt_id
        self.public_dir = self.attempt_dir/'public'
        self.privileged_dir = self.attempt_dir/'privileged'
        self.segments_dir = self.public_dir/'segments'
        self.segment_index_path = self.public_dir/'segment_index.jsonl'
        self.journal_path = self.public_dir/'journal.r7c'
        self.journal_index_path = self.public_dir/'journal_index.jsonl'
        self.outcomes_path = self.public_dir/'outcomes.json'
        self.started_path, self.finished_path = self.attempt_dir/'started.json', self.attempt_dir/'finished.json'
        self.segments = []
        self._journal_writer = None
        self._initialized = False

    def __del__(self):
        if getattr(self, '_journal_writer', None):
            self._journal_writer.close()
            self._journal_writer = None

    def initialize(self, cell_metadata, initial_world=None):
        self.public_dir.mkdir(parents=True, exist_ok=False)
        self.privileged_dir.mkdir(parents=True, exist_ok=False)
        if self.format_version == 1:
            self.segments_dir.mkdir(parents=True, exist_ok=False)
        elif self.format_version == 2:
            self._journal_writer = JournalWriter(self.journal_path, self.journal_index_path)
            self._journal_writer.open()
        else:
            raise ValueError(f'Unsupported format version: {self.format_version}')

        self._write_atomic_json(self.started_path, dict(
            attempt_id=self.attempt_id,
            cell_key_hash=self.cell_key_hash,
            format_version=self.format_version,
            cell_metadata=cell_metadata,
            pid=os.getpid(),
            started_at_utc=stamp()
        ))
        if initial_world is not None:
            self.record_world(initial_world)
        self._initialized = True

    def record_world(self, world):
        publish(self.privileged_dir/'initial_world.bin', gzip.compress(json.dumps(world, allow_nan=False).encode(), mtime=0))

    def persist_request(self, sequence, day, phase, wire_request):
        if not self._initialized:
            raise RuntimeError('AttemptLogger not initialized')
        if self.format_version == 1:
            payload=dict(sequence=sequence,day=day,phase=phase,wire_request_base64=base64.b64encode(wire_request).decode())
            publish(self.public_dir/f'{sequence:03d}.request.bin',gzip.compress(json.dumps(payload,allow_nan=False).encode(),mtime=0))
        elif self.format_version == 2:
            if not self._journal_writer:
                self._journal_writer = JournalWriter(self.journal_path, self.journal_index_path)
                self._journal_writer.open()
            self._journal_writer.persist_request(sequence, day, phase, self.attempt_id, wire_request)

    def record_step(self, sequence, day, phase, wire_request, wire_response, memory_before, memory_after,
                    action, policy_status, stdout_text, stderr_text, elapsed_seconds, cpu_seconds):
        if not self._initialized:
            raise RuntimeError('AttemptLogger not initialized')
        ident = f'{sequence:03d}_{day:02d}_{phase}'
        if self.format_version == 1:
            payload = dict(sequence=sequence,day=day,phase=phase,
                wire_request_base64=base64.b64encode(wire_request).decode(),
                wire_response_base64=base64.b64encode(wire_response).decode(),
                wire_request_utf8=wire_request.decode(errors='replace'),wire_response_utf8=wire_response.decode(errors='replace'),
                memory_before=memory_before,memory_after=memory_after,action=action,policy_status=policy_status,
                stdout=stdout_text,stderr=stderr_text,elapsed_seconds=elapsed_seconds,cpu_seconds=cpu_seconds,timestamp_utc=stamp())
            raw=json.dumps(payload,allow_nan=False).encode(); compressed=gzip.compress(raw,mtime=0)
            publish(self.segments_dir/(ident+'.bin'),compressed)
            meta=SegmentMetadata(ident,sequence,day,phase,len(raw),len(compressed),compute_bytes_sha256(compressed),payload['timestamp_utc'])
            with self.segment_index_path.open('ab') as f:
                f.write((meta.to_json()+'\n').encode()); f.flush(); os.fsync(f.fileno())
            self.segments.append(meta)
            return meta
        elif self.format_version == 2:
            if not self._journal_writer:
                self._journal_writer = JournalWriter(self.journal_path, self.journal_index_path)
                self._journal_writer.open()
            info = self._journal_writer.persist_completion(
                sequence=sequence,
                day=day,
                phase=phase,
                attempt_id=self.attempt_id,
                wire_request=wire_request,
                wire_response=wire_response,
                memory_before=memory_before,
                memory_after=memory_after,
                action=action,
                policy_status=policy_status,
                stdout_text=stdout_text,
                stderr_text=stderr_text,
                elapsed_seconds=elapsed_seconds,
                cpu_seconds=cpu_seconds,
            )
            meta = SegmentMetadata(ident, sequence, day, phase, len(wire_request) + len(wire_response),
                                   info.length, info.sha256, info.timestamp_utc)
            self.segments.append(meta)
            return meta

    def finalize(self, metrics, final_state=None, is_valid=True, error_message=None):
        if self._journal_writer:
            self._journal_writer.close()
            self._journal_writer = None
        write_json(self.outcomes_path, dict(attempt_id=self.attempt_id,cell_key_hash=self.cell_key_hash,is_valid=is_valid,
                   error_message=error_message,metrics=metrics,total_segments=len(self.segments),format_version=self.format_version))
        if final_state is not None:
            publish(self.privileged_dir/'final_state.bin',gzip.compress(json.dumps(final_state,allow_nan=False).encode(),mtime=0))
        artifacts={str(p.relative_to(self.attempt_dir)):compute_bytes_sha256(p.read_bytes())
                   for p in sorted(self.attempt_dir.rglob('*')) if p.is_file()}
        write_json(self.finished_path,dict(attempt_id=self.attempt_id,is_valid=is_valid,format_version=self.format_version,
                                            artifacts=artifacts,finished_at_utc=stamp()))

    _write_atomic_json=staticmethod(write_json)

    @staticmethod
    def read_segment(path):
        return json.loads(gzip.decompress(Path(path).read_bytes()))

def verify_attempt(path):
    path=Path(path); final=json.loads((path/'finished.json').read_bytes()); expected=final['artifacts']
    actual={str(p.relative_to(path)) for p in path.rglob('*') if p.is_file() and p != path/'finished.json'}
    if actual != set(expected): raise ValueError('Attempt artifact file set mismatch')
    for rel,digest in expected.items():
        if compute_bytes_sha256((path/rel).read_bytes()) != digest: raise ValueError('Attempt artifact hash mismatch: '+rel)
    # Format v1 verification
    index=path/'public'/'segment_index.jsonl'
    if index.exists():
        for line in index.read_text().splitlines():
            meta=json.loads(line); data=(path/'public'/'segments'/(meta['segment_id']+'.bin')).read_bytes()
            if compute_bytes_sha256(data)!=meta['sha256']: raise ValueError('Segment index digest mismatch')
    # Format v2 verification
    journal=path/'public'/'journal.r7c'
    if journal.exists():
        res = scan_journal(journal)
        if res.get('torn_tail'):
            raise ValueError(f"Journal has torn tail: {res.get('error')}")
        if res.get('pending_request'):
            raise ValueError(f"Journal has uncompleted request: {res.get('pending_request')}")
        j_index = path/'public'/'journal_index.jsonl'
        if j_index.exists():
            lines = [l for l in j_index.read_text().splitlines() if l.strip()]
            if len(lines) != res.get('frames_count'):
                raise ValueError(f"Journal index line count mismatch: {len(lines)} vs {res.get('frames_count')}")
    return final

class DurableRecorder:
    def __init__(self, root_dir):
        self.root_dir=Path(root_dir); self.commits_dir=self.root_dir/'commits'; self.attempts_dir=self.root_dir/'attempts'
        self.commits_dir.mkdir(parents=True,exist_ok=True); self.attempts_dir.mkdir(exist_ok=True)
    def create_attempt_logger(self, cell_key_hash, format_version=1):
        return AttemptLogger(self.root_dir,cell_key_hash,format_version=format_version)
    def write_commit(self,cell_key_hash,attempt_id,cell_dict,metrics,is_valid=True,error_message=None):
        if (self.commits_dir/(cell_key_hash+'.json')).exists(): raise FileExistsError('Cell already committed')
        attempt=self.attempts_dir/cell_key_hash/attempt_id
        if not attempt.exists(): raise ValueError('Cannot commit missing attempt evidence')
        verify_attempt(attempt)
        outcomes=json.loads((attempt/'public'/'outcomes.json').read_bytes())
        started=json.loads((attempt/'started.json').read_bytes())
        if outcomes['metrics'] != metrics or outcomes['is_valid'] != is_valid or outcomes['error_message'] != error_message:
            raise ValueError('Commit differs from finalized outcomes')
        if started['cell_metadata'].get('cell',cell_dict) != cell_dict:
            raise ValueError('Commit cell differs from attempt metadata')
        digest=compute_bytes_sha256((attempt/'finished.json').read_bytes())
        data=dict(cell_key_hash=cell_key_hash,attempt_id=attempt_id,cell=cell_dict,metrics=metrics,is_valid=is_valid,
                  error_message=error_message,finished_sha256=digest,committed_at_utc=stamp())
        target=self.commits_dir/(cell_key_hash+'.json'); write_json(target,data); return target
    def get_commit(self,cell_key_hash):
        path=self.commits_dir/(cell_key_hash+'.json')
        if not path.exists(): return None
        data=json.loads(path.read_bytes())
        if not data.get('finished_sha256'): raise ValueError('Commit has no finalized evidence digest')
        if data.get('finished_sha256'):
            attempt=self.attempts_dir/cell_key_hash/data['attempt_id']; final=verify_attempt(attempt)
            outcomes=json.loads((attempt/'public'/'outcomes.json').read_bytes())
            started=json.loads((attempt/'started.json').read_bytes())
            if outcomes['metrics'] != data['metrics'] or outcomes['is_valid'] != data['is_valid'] or final['is_valid'] != data['is_valid']:
                raise ValueError('Commit/outcome validity or metrics mismatch')
            if started['cell_metadata'].get('cell',data['cell']) != data['cell']:
                raise ValueError('Commit/attempt cell mismatch')
            if compute_bytes_sha256((attempt/'finished.json').read_bytes())!=data['finished_sha256']: raise ValueError('Commit digest mismatch')
        return data
    def reconcile(self):
        commits={p.stem:self.get_commit(p.stem) for p in self.commits_dir.glob('*.json')}
        attempts=[]
        for started in sorted(self.attempts_dir.glob('*/*/started.json')):
            path=started.parent; closed=(path/'finished.json').exists()
            if closed: verify_attempt(path)
            else: verify_prefix(path)
            attempts.append(dict(path=str(path),state='finished' if closed else 'interrupted'))
        return dict(commits=commits,attempts=attempts)


def verify_prefix(path):
    """Every indexed closed segment is verifiable after an interrupted process."""
    path=Path(path)
    index=path/'public'/'segment_index.jsonl'
    seen=set()
    if index.exists():
        raw=index.read_bytes()
        # A killed append may leave one uncommitted final index line. Preserve it.
        lines=raw.splitlines()
        if raw and not raw.endswith(b'\n'): lines=lines[:-1]
        for line in lines:
            meta=json.loads(line)
            if meta['segment_id'] in seen: raise ValueError('Duplicate segment index')
            seen.add(meta['segment_id'])
            segment=path/'public'/'segments'/(meta['segment_id']+'.bin')
            if compute_bytes_sha256(segment.read_bytes()) != meta['sha256']:
                raise ValueError('Interrupted attempt closed segment corruption')
    for request in (path/'public').glob('*.request.bin'):
        payload=json.loads(gzip.decompress(request.read_bytes()))
        base64.b64decode(payload['wire_request_base64'],validate=True)
    journal=path/'public'/'journal.r7c'
    if journal.exists():
        return scan_journal(journal)
