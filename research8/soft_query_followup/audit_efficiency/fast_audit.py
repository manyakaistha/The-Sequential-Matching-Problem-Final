"""Sequential checkpointed v3 audit, with one pinned pure-computation optimization.

No simulator or frozen source is modified. The exact v2 stream checker is copied
at runtime, inserting one public canonical-set cache and replacing its single
repeated set comprehension. Every other statement remains byte-for-byte intact.
Checkpoints are reusable only after rehashing all physical evidence and sources.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

from research8.soft_query_followup.v2 import audit as v2
from research8.soft_query_followup.v2.registration import ROOT
from research8.soft_query_followup.v3 import audit as v3, storage

PINS = {
    'research8/soft_query_followup/v2/audit.py': '9495186c270cf6ef2963df57ccc5e7b2da5970bc7a733eb61950fabe42781217',
    'research8/soft_query_followup/v3/audit.py': '8e54d17ba737c763cae44cd4c866abfae82fd9288e779f877b4003e80d8a1565',
    'research8/soft_query_followup/v3/storage.py': '75cd1205c9dd4fd5f09c213cd23ef4d5687505d2f06898eb7e5a6f237cfde349',
}
BOUND = 512 * 2**20
RSS_BOUND = 2 * 2**30


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def optimized_stream():
    for relative, expected in PINS.items():
        v2._require(storage._hash_file(ROOT / relative)['sha256'] == expected,
                    'Frozen audit source pin mismatch: ' + relative)
    source = inspect.getsource(v2._audit_stream)
    old = '{_canonical(x) for x in public[key]}'
    v2._require(source.count(old) == 1, 'Expected exactly one optimization site')
    anchor = '    actions = _lines(attempt / \'actions.jsonl\')\n'
    v2._require(source.count(anchor) == 1, 'Expected exactly one cache insertion site')
    source = source.replace(old, '_public_canonical[key]').replace(
        anchor, "    _public_canonical = {key: {_canonical(x) for x in public[key]}\n"
        "                         for key in ('introductions', 'feedback', 'ask_log')}\n" + anchor)
    namespace = dict(v2.__dict__)
    exec(compile(source, str(Path(__file__)) + ':pinned_stream', 'exec'), namespace)
    return namespace['_audit_stream'], hashlib.sha256(source.encode()).hexdigest()


def _source_identity(registrations):
    sources = dict(PINS)
    for reg in registrations:
        if reg is None:
            continue
        for relative, expected in reg['source_manifest'].items():
            v2._require(relative not in sources or sources[relative] == expected,
                        'Conflicting source identities')
            sources[relative] = expected
    for relative, expected in sources.items():
        target = storage._path(ROOT, relative)
        v2._require(storage._hash_file(target)['sha256'] == expected,
                    'Registered source identity mismatch: ' + relative)
    return sources


def _evidence_identity(output, row):
    """Rehash compressed bytes on every resume; raw mode rehashes every file."""
    logical = row['attempt_relative_path']
    catalog = storage._path(output, 'archive_manifests/' + hashlib.sha256(logical.encode()).hexdigest() + '.json')
    if catalog.exists():
        catalog_identity = storage._hash_file(catalog)
        manifest = v2._json(catalog)
        storage._validate_manifest(manifest)
        v2._require(manifest['original_relpath'] == logical, 'Archive logical path mismatch')
        v2._require({k: v['sha256'] for k, v in manifest['files'].items()} == row['artifact_hashes'],
                    'Archive commit coverage mismatch')
        v2._require(sum(v['bytes'] for v in manifest['files'].values()) <= BOUND, 'Evidence exceeds512MiB')
        archive = storage._hash_file(storage._path(output, manifest['archive_relative_path']))
        v2._require(archive == dict(sha256=manifest['archive_sha256'], bytes=manifest['archive_bytes']),
                    'Archive physical identity mismatch')
        return dict(kind='archive', catalog=catalog_identity, archive=archive)
    files = storage._inventory(storage._path(output, logical))
    v2._require({k: v['sha256'] for k, v in files.items()} == row['artifact_hashes'],
                'Raw commit coverage mismatch')
    v2._require(sum(v['bytes'] for v in files.values()) <= BOUND, 'Evidence exceeds512MiB')
    return dict(kind='raw', files=files)


@contextmanager
def rss_guard(limit=RSS_BOUND):
    """Monitor actual resident bytes; abort without publishing proof on breach."""
    stopped = threading.Event()
    def monitor():
        while not stopped.is_set():
            try:
                rss = int(subprocess.check_output(['ps', '-o', 'rss=', '-p', str(os.getpid())]).strip()) * 1024
                if rss > limit:
                    print(json.dumps(dict(status='failed', error='Audit RSS exceeds2GiB', rss_bytes=rss)), flush=True)
                    os._exit(75)
            except Exception as exc:
                print(json.dumps(dict(status='failed', error='RSS monitoring failed: ' + str(exc))), flush=True)
                os._exit(75)
            stopped.wait(.25)
    worker = threading.Thread(target=monitor, daemon=True)
    worker.start()
    try:
        yield
    finally:
        stopped.set()
        worker.join()


def audit_campaign(output, original_registration, continuation_registration=None, *, checkpoint_dir, proof_path):
    """Full fixed-grid v3 campaign checks, with independently bound cell caching."""
    output, checkpoint_dir, proof_path = Path(output), Path(checkpoint_dir), Path(proof_path)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    original = v3._registration(original_registration)
    continuation = v3._registration(continuation_registration) if continuation_registration else None
    stream, transformed_sha = optimized_stream()
    sources = _source_identity([original, continuation])
    implementation = dict(adapter=storage._hash_file(Path(__file__)), frozen_sources=PINS,
                          transformed_stream_sha256=transformed_sha, python=sys.version)
    registration_identity = dict(original_sha256=digest(original),
                                 continuation_sha256=digest(continuation) if continuation else None)
    original_cell, original_stream = v3.audit_cell, v3._audit_stream
    checkpoints, counts, commit_identities = [], dict(verified=0, reused=0), {}
    started = time.monotonic()

    def checkpointed_cell(out, row, reg):
        key = row['cell']['cell_key']
        commit_path = storage._path(output, 'commits/' + key + '.json')
        commit_identity = storage._hash_file(commit_path)
        commit_identities[commit_path.name] = commit_identity
        v2._require(v2._json(commit_path) == row, 'Commit changed during campaign scan')
        evidence = _evidence_identity(output, row)
        binding = dict(commit=commit_identity, sources=sources, registration=registration_identity,
                       cell_registration_sha256=reg['registration_sha256'], evidence=evidence,
                       implementation=implementation)
        path = checkpoint_dir / (digest(binding) + '.json')
        if path.exists():
            record = v2._json(path)
            payload = {k: v for k, v in record.items() if k != 'payload_sha256'}
            v2._require(record.get('payload_sha256') == digest(payload)
                        and record.get('schema') == 'r8-fast-audit-cell-v1'
                        and record.get('binding') == binding and record.get('cell_key') == key
                        and record['result']['status'] == 'passed', 'Invalid checkpoint')
            result = record['result']
            counts['reused'] += 1
        else:
            result = original_cell(out, row, reg)
            v2._require(storage._hash_file(commit_path) == commit_identity
                        and _evidence_identity(output, row) == evidence,
                        'Evidence changed during cell audit')
            record = dict(schema='r8-fast-audit-cell-v1', cell_key=key, binding=binding, result=result)
            record['payload_sha256'] = digest(record)
            storage._write_json_exclusive(path, record)
            counts['verified'] += 1
        checkpoints.append(dict(cell_key=key, checkpoint_sha256=storage._hash_file(path)['sha256']))
        if len(checkpoints) % 25 == 0:
            print(json.dumps(dict(event='audit_progress', cells=len(checkpoints), counts=counts,
                                  elapsed_seconds=time.monotonic()-started)), flush=True)
        return result

    # Scoped to this sequential adapter process, restored even on failure.
    v3.audit_cell, v3._audit_stream = checkpointed_cell, stream
    try:
        with rss_guard():
            result = v3.audit_campaign(output, original, continuation)
            v2._require(_source_identity([original, continuation]) == sources, 'Sources changed during audit')
            final_commits = {path.name: storage._hash_file(path)
                             for path in output.joinpath('commits').glob('*.json')}
            v2._require(final_commits == commit_identities, 'Commits changed during campaign audit')
            proof = dict(schema='r8-fast-independent-full-grid-proof-v1', result=result,
                         registration=registration_identity, implementation=implementation,
                         sources=sources, checkpoints=checkpoints)
            proof['payload_sha256'] = digest(proof)
            storage._write_json_exclusive(proof_path, proof)
    finally:
        v3.audit_cell, v3._audit_stream = original_cell, original_stream
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--registration', required=True)
    parser.add_argument('--continuation')
    parser.add_argument('--checkpoints', required=True)
    parser.add_argument('--proof', required=True)
    args = parser.parse_args()
    result = audit_campaign(args.output, args.registration, args.continuation,
                           checkpoint_dir=args.checkpoints, proof_path=args.proof)
    print(json.dumps(result, sort_keys=True), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
