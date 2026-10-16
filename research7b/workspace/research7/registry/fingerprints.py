"""Canonical immutable execution fingerprints. No workload is generated here."""
import hashlib
import json
from pathlib import Path


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def registration_design(registration):
    return {k: v for k, v in registration.items() if k not in {'reviews', 'detached_signature', 'registration_design_sha256'}}
