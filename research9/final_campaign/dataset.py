"""Public, assignment-time supervised rows from immutable audited R8 archives.

Only actions.jsonl and final_public.json are decoded. Other archive members are
streamed through a hash, never materialized or interpreted. Metadata is separate
from X; seed/family/arm and opaque actor IDs are never passed to feature code.
"""
from functools import lru_cache
import hashlib
import io
import json
import os
from pathlib import Path
import tarfile
import tempfile

import numpy as np

from research8.soft_query_followup.v3 import storage
from research8.soft_query_followup.v3.audit import reconstruct_public
from research8.w2.protocol import sanitize_observation

REPO = Path(__file__).resolve().parents[2]
DEFAULT_PROOF = REPO / 'research8/soft_query_followup/audit_efficiency/full_grid_proof.json'
MAX_ROWS = 6000  # 200 actors / two endpoints, on each of sixty days.
MAX_LINE = 8 * 2**20


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _json(path):
    return json.loads(Path(path).read_bytes())


@lru_cache(maxsize=4)
def _proof(path, identity):
    proof = _json(path)
    require(proof['payload_sha256'] == digest({k: v for k, v in proof.items() if k != 'payload_sha256'}), 'Proof digest mismatch')
    result = proof['result']
    require(result['status'] == 'passed' and result['complete_registered_grid'] and result['verified_cells'] == result['expected_cells'] == 2880, 'Incomplete audited old grid')
    require(result['private_world_read'] is False, 'Proof used private worlds')
    index = {r['cell_key']: r['checkpoint_sha256'] for r in proof['checkpoints']}
    require(len(index) == len(proof['checkpoints']) == 2880, 'Proof checkpoint coverage mismatch')
    for relative, expected in proof['implementation']['frozen_sources'].items():
        require(storage._hash_file(storage._path(REPO, relative))['sha256'] == expected, 'Frozen audit implementation changed')
    return proof, index


def _verified_manifest(root, commit_path, proof_path):
    """Rebind current bytes to one checkpoint named in the complete-grid proof."""
    row = _json(commit_path)
    require(row['is_valid'] is True and row['metrics']['valid'] is True and row.get('error') is None, 'Invalid cell')
    key = row['cell']['cell_key']
    require(Path(commit_path) == storage._path(root, 'commits/' + key + '.json'), 'Unexpected commit path')
    logical = row['attempt_relative_path']
    catalog_path = storage._path(root, 'archive_manifests/' + hashlib.sha256(logical.encode()).hexdigest() + '.json')
    manifest = _json(catalog_path)
    storage._validate_manifest(manifest)
    require(manifest['original_relpath'] == logical, 'Archive logical identity mismatch')
    require({k: v['sha256'] for k, v in manifest['files'].items()} == row['artifact_hashes'], 'Archive commit coverage mismatch')
    require(sum(v['bytes'] for v in manifest['files'].values()) <= 512 * 2**20, 'Cell exceeds512MiB')
    archive_identity = storage._hash_file(storage._path(root, manifest['archive_relative_path']))
    require(archive_identity == dict(sha256=manifest['archive_sha256'], bytes=manifest['archive_bytes']), 'Archive identity mismatch')
    proof_identity = storage._hash_file(proof_path)
    proof, index = _proof(str(proof_path), proof_identity['sha256'])
    binding = dict(commit=storage._hash_file(commit_path), sources=proof['sources'], registration=proof['registration'], cell_registration_sha256=row['registration_sha256'], evidence=dict(kind='archive', catalog=storage._hash_file(catalog_path), archive=archive_identity), implementation=proof['implementation'])
    checkpoint_path = storage._path(Path(proof_path).parent, 'checkpoints/' + digest(binding) + '.json')
    require(key in index and storage._hash_file(checkpoint_path)['sha256'] == index[key], 'Checkpoint not bound by proof')
    checkpoint = _json(checkpoint_path)
    require(checkpoint['payload_sha256'] == digest({k: v for k, v in checkpoint.items() if k != 'payload_sha256'}), 'Checkpoint digest mismatch')
    require(checkpoint['binding'] == binding and checkpoint['cell_key'] == key and checkpoint['result']['status'] == 'passed', 'Checkpoint binding mismatch')
    return row, manifest, dict(commit_sha256=binding['commit']['sha256'], catalog_sha256=binding['evidence']['catalog']['sha256'], archive_sha256=archive_identity['sha256'], proof_sha256=proof_identity['sha256'], checkpoint_sha256=index[key])


class _HashedReader(io.RawIOBase):
    def __init__(self, stream):
        self.stream, self.hash, self.size = stream, hashlib.sha256(), 0

    def readable(self):
        return True

    def readinto(self, buffer):
        block = self.stream.read(len(buffer))
        buffer[:len(block)] = block
        self.hash.update(block)
        self.size += len(block)
        return len(block)


def _action_rows(stream, feature_api):
    """Retain only features and join keys; never rebuild requests from final data."""
    rows = []
    action_digest = hashlib.sha256()
    for sequence in range(1, 121):
        line = stream.readline(MAX_LINE + 1)
        require(0 < len(line) <= MAX_LINE, 'Missing/oversized action line')
        action = json.loads(line)
        phase, day = ('ask', 'match')[(sequence - 1) % 2], (sequence - 1) // 2
        require((action['sequence'], action['phase'], action['day']) == (sequence, phase, day), 'Action chronology mismatch')
        request, response = action['request'], action['response']
        require(request['phase'] == phase and request['state']['day'] == day, 'Request chronology mismatch')
        pairs_or_asks = response['pairs' if phase == 'match' else 'asks']
        action_digest.update(json.dumps([phase, day, pairs_or_asks], sort_keys=True, allow_nan=False).encode())
        if phase == 'ask':
            continue
        sanitize_observation(request)
        state = request['state']
        context = feature_api.prepare_state(state)
        members = {m['member_id']: m for m in state['members']}
        request_hash = digest(request)
        for pair in pairs_or_asks:
            require(len(pair) == 2 and pair[0] != pair[1], 'Invalid assignment pair')
            a, b = sorted(pair)
            vector = np.asarray(feature_api.pair_features(state, members[a], members[b], context=context), dtype=np.float32)
            require(vector.shape == (len(feature_api.feature_names()),) and np.isfinite(vector).all(), 'Invalid feature vector')
            rows.append(dict(pair=(a, b), day=day, X=vector, request_sha256=request_hash))
            require(len(rows) <= MAX_ROWS, 'Assignment bound exceeded')
    require(not stream.read(1), 'Extra action records')
    return rows, action_digest.hexdigest()


def public_labels(public):
    """Labels and stage risk sets, after independent public chronology validation."""
    metrics = reconstruct_public(public)
    events = {}
    for event in public['feedback']:
        events.setdefault(event['introduction_id'], []).append(event)
    result = {}
    for intro in public['introductions']:
        ident = intro['introduction_id']
        rows = events.get(ident, [])
        first = [e for e in rows if e['event'] == 'introduction_response']
        mutual = len(first) == 2 and all(e['value'] == 'yes' for e in first)
        dates = [e for e in rows if e['event'] == 'date_happened']
        timely = mutual and bool(dates) and dates[0]['value'] is True and 0 <= dates[0]['occurred_day'] - intro['assigned_day'] <= 30
        second = [e for e in rows if e['event'] == 'second_meeting_intention']
        qualified = timely and len(second) == 2 and all(e['value'] == 'yes' and e['occurred_day'] is not None and 0 <= e['occurred_day'] - dates[0]['occurred_day'] <= 3 for e in second)
        key = (intro['assigned_day'], tuple(sorted((intro['user_a'], intro['user_b']))))
        require(key not in result, 'Duplicate label key')
        result[key] = dict(introduction_id=ident, y_terminal=int(qualified), y_first=int(mutual), y_date_given_first=int(timely), y_second_given_timelydate=int(qualified), mask_first=True, mask_date_given_first=mutual, mask_second_given_timelydate=timely)
    require(sum(r['y_terminal'] for r in result.values()) == metrics['mutual_second_meeting_intention'], 'Qualified label count mismatch')
    return result, metrics


def _stream_cell(root, manifest, feature_api):
    rows = public = action_hash = None
    seen = set()
    archive = storage._path(root, manifest['archive_relative_path'])
    with archive.open('rb') as raw, storage._compression(raw, manifest['codec']) as compressed:
        limit = 32768 + sum(v['bytes'] + 8192 + len(k.encode()) * 2 for k, v in manifest['files'].items())
        bounded = storage._BoundedReader(compressed, limit)
        with tarfile.open(fileobj=bounded, mode='r|') as tar:
            for member in tar:
                name = storage._rel(member.name)
                require(member.isfile() and name not in seen and name in manifest['files'], 'Unsafe/extra archive member')
                info = manifest['files'][name]
                require(member.size == info['bytes'], 'Member size mismatch')
                seen.add(name)
                with tar.extractfile(member) as source:
                    hashed = _HashedReader(source)
                    with io.BufferedReader(hashed) as stream:
                        if name == 'actions.jsonl':
                            rows, action_hash = _action_rows(stream, feature_api)
                        elif name == 'final_public.json':
                            require(member.size <= 16 * 2**20, 'Final public size bound exceeded')
                            public = json.loads(stream.read())
                        while stream.read(storage.CHUNK):
                            pass
                    require(hashed.size == info['bytes'] and hashed.hash.hexdigest() == info['sha256'], 'Member hash mismatch: ' + name)
        while block := bounded.read(storage.CHUNK):
            require(not block.strip(b'\0'), 'Nonzero trailing archive bytes')
    require(seen == set(manifest['files']) and rows is not None and public is not None, 'Missing archive evidence')
    return rows, public, action_hash


def extract_cell(root, commit_path, dest, *, proof_path=DEFAULT_PROOF):
    """Write a single immutable .npz after complete streaming verification.

    dest is a directory. Rows retain opaque join IDs and request hashes outside X.
    Stage targets use zero outside their risk set; corresponding mask is required.
    An assignment at day<=59 has all qualified deadlines by92, observed through99.
    """
    from . import features
    root, commit_path, proof_path = Path(root).resolve(), Path(commit_path).resolve(), Path(proof_path).resolve()
    row, manifest, provenance = _verified_manifest(root, commit_path, proof_path)
    rows, public, action_hash = _stream_cell(root, manifest, features)
    require(action_hash == row['action_sha256'], 'Action digest mismatch')
    labels, metrics = public_labels(public)
    require(all(row['metrics'].get(k) == v for k, v in metrics.items()), 'Committed endpoint mismatch')
    keys = [(r['day'], r['pair']) for r in rows]
    require(len(keys) == len(set(keys)) and set(keys) == set(labels), 'Actual response/introduction join mismatch')
    n = len(rows)
    arrays = dict(X=np.stack([r['X'] for r in rows]) if rows else np.empty((0, len(features.feature_names())), dtype=np.float32), feature_names=np.asarray(features.feature_names()), assigned_day=np.asarray([r['day'] for r in rows], dtype=np.int16), user_a=np.asarray([r['pair'][0] for r in rows]), user_b=np.asarray([r['pair'][1] for r in rows]), request_sha256=np.asarray([r['request_sha256'] for r in rows]), introduction_id=np.asarray([labels[k]['introduction_id'] for k in keys]))
    for target in ('y_terminal', 'y_first', 'y_date_given_first', 'y_second_given_timelydate', 'mask_first', 'mask_date_given_first', 'mask_second_given_timelydate'):
        arrays[target] = np.asarray([labels[k][target] for k in keys], dtype=np.uint8)
    metadata = dict(schema='r9-public-supervised-cell-v1', cell=row['cell'], rows=n, qualified=int(arrays['y_terminal'].sum()), provenance=provenance, private_world_read=False, feature_source='captured_post_query_match_request', labels_observed_through=99)
    arrays['metadata_json'] = np.asarray(json.dumps(metadata, sort_keys=True))
    arrays['group_seed'] = np.full(n, row['cell']['seed'], dtype=np.int64)
    arrays['family'] = np.full(n, row['cell']['family'])
    arrays['arm'] = np.full(n, row['cell']['policy_id'])
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    path = storage._path(dest, row['cell']['cell_key'] + '.npz')
    fd, temporary = tempfile.mkstemp(prefix='.dataset-', suffix='.npz', dir=dest)
    try:
        with os.fdopen(fd, 'wb') as output:
            np.savez_compressed(output, **arrays)
            output.flush()
            os.fsync(output.fileno())
        os.link(temporary, path)  # Exclusive publication; never replace an old artifact.
        storage._sync_dir(dest)
    finally:
        os.unlink(temporary)
    return dict(metadata, path=str(path), output_identity=storage._hash_file(path))
