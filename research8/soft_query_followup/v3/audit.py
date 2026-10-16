"""Archive-aware independent closure audit; never reads private worlds."""
import argparse
import fcntl
from contextlib import contextmanager
import hashlib
import tempfile
from collections import defaultdict
import itertools
import json
from pathlib import Path

from research8.soft_query_followup.v2.audit import (
    _require, _json, _lines, _safe, _sha, reconstruct_public, _audit_stream,
)
from research8.soft_query_followup.v2.registration import registration_hash
from research8.w2.protocol import sanitize_observation
from research8.w2.public_rules import VERSION


def _registration(value):
    reg = _json(Path(value)) if isinstance(value, (str, Path)) else value
    _require(isinstance(reg, dict), 'Registration schema')
    _require(reg.get('registration_sha256') == registration_hash(reg),
             'Invalid registration self digest')
    return reg


@contextmanager
def _attempt(output, row):
    """Prefer a committed archive catalog; safely handle partial raw removal."""
    from .storage import materialize_attempt
    logical = row['attempt_relative_path']
    raw = _safe(output, logical)
    catalog = _safe(output, 'archive_manifests/' + hashlib.sha256(logical.encode()).hexdigest() + '.json')
    if catalog.exists():
        manifest = _json(catalog)
        _require(manifest['original_relpath'] == logical, 'Archive logical attempt mismatch')
        _require({k: v['sha256'] for k, v in manifest['files'].items()} == row['artifact_hashes'],
                 'Archive commit hash coverage mismatch')
        if sum(v['bytes'] for v in manifest['files'].values()) > 512*2**20:
            raise ValueError('audit materialization exceeds512MiB')
        staging=output/'.audit_tmp'
        staging.mkdir(exist_ok=True)
        # One reserved extraction slot per campaign, including concurrent auditors.
        with (staging / '.materialization.lock').open('a+b') as lease:
            fcntl.flock(lease.fileno(), fcntl.LOCK_EX)
            with tempfile.TemporaryDirectory(prefix='r8-independent-audit-',dir=staging) as tmp:
                yield materialize_attempt(output, manifest, Path(tmp) / 'attempt')
    else:
        _require(raw.is_dir(), 'Missing attempt directory/archive catalog')
        yield raw


def audit_cell(output, commit, source_registration):
    """Independently reconstruct one cell; raise on any evidence mismatch."""
    output = Path(output)
    reg = _registration(source_registration)
    row = _json(Path(commit)) if isinstance(commit, (str, Path)) else commit
    _require(row['is_valid'] is True and row['metrics']['valid'] is True
             and row.get('error') is None, 'Invalid cell commit')
    _require(row['registration_sha256'] == reg['registration_sha256'],
             'Registration digest mismatch')
    _require(row['source_sha256'] == reg['source_manifest'] and bool(row['source_sha256']),
             'Registered source digest mismatch')
    _require(row['cell'] in reg['cells'], 'Unexpected cell metadata')
    _require(isinstance(row['world_sha256'], str) and len(row['world_sha256']) == 64
             and all(c in '0123456789abcdef' for c in row['world_sha256']),
             'Missing world identity digest')
    with _attempt(output, row) as attempt:
        hashes = row['artifact_hashes']
        required_files = {'actions.jsonl', 'final_public.json', 'requests.jsonl', 'responses.jsonl',
                          'invocations.jsonl', 'query_answers.jsonl', 'daily_telemetry.jsonl',
                          'released_feedback.jsonl', 'event_log.jsonl', 'status.json', 'arrived_by59.json'}
        _require(isinstance(hashes, dict) and required_files <= set(hashes),
                 'Required artifact hashes missing')
        descendants = list(attempt.rglob('*'))
        _require(all(not p.is_symlink() for p in descendants), 'Symlink attempt artifact')
        actual_files = {str(p.relative_to(attempt)) for p in descendants if p.is_file()}
        _require(actual_files == set(hashes), 'Artifact hash coverage mismatch')
        for name, digest in hashes.items():
            artifact = _safe(attempt, name)
            _require(artifact.is_file() and _sha(artifact) == digest, 'Artifact hash mismatch: '+name)
        public = _json(attempt / 'final_public.json')
        status = _json(attempt / 'status.json')
        expected_status = dict(status='completed', is_valid=True, error=None,
                               sequence=120, attempt_id=row['attempt_id'])
        _require(status == expected_status, 'Terminal status mismatch')
        event_log = _lines(attempt / 'event_log.jsonl')
        _require(event_log == [dict(event='attempt_started', attempt_id=row['attempt_id']),
                               dict(expected_status, event='attempt_finished')], 'Lifecycle event log mismatch')
        inventory = _json(attempt / 'arrived_by59.json')
        _require(isinstance(inventory, list), 'Arrival inventory schema')
        sanitize_observation(dict(schema_version=VERSION, phase='match', memory=None,
                                  state=dict(schema_version=VERSION, synthetic=True, day=60,
                                             ask_budget_remaining=12, members=inventory,
                                             introductions=[], feedback=[], ask_log=[])))
        _require({m['member_id']: m['arrived_day'] for m in inventory}
                 == {m['member_id']: m['arrived_day'] for m in public['members'] if m['arrived_day'] <= 59}
                 and len(inventory) == len({m['member_id'] for m in inventory}), 'Public arrival inventory mismatch')
        metrics = reconstruct_public(public)
        for metric, value in metrics.items():
            _require(metric in row['metrics'] and row['metrics'][metric] == value,
                     'Independent metric mismatch: '+metric)
        limit = reg.get('resource_forecast', {}).get('invocation_wall_seconds', 10)
        _require(0 < limit <= 10, 'Invalid registered invocation limit')
        _require(_audit_stream(attempt, public, limit) == row['action_sha256'], 'Action digest mismatch')
        actions = _lines(attempt / 'actions.jsonl')
        elapsed = [a['elapsed_seconds'] for a in actions]
        _require(row['invocation_count'] == 120 and row['fallback_count'] == 0
                 and row['invocation_seconds_total'] == sum(elapsed)
                 and row['invocation_seconds_max'] == max(elapsed), 'Invocation aggregate mismatch')
    return dict(status='passed', metrics=metrics, public_event_reconstruction_verified=True, private_world_read=False)


def audit_campaign(output, original_registration, continuation_registration=None, *, allow_incomplete=False):
    """Verify original fixed grid and explicitly registered old/new provenance."""
    output = Path(output)
    original = _registration(original_registration)
    if original.get('schema_version') == 'R8-evidence-v2':
        from research8.soft_query_followup.v2.registration import verify_registration
        verify_registration(original)
    expected = {}
    for cell in original['cells']:
        key = cell['cell_key']
        _require(key not in expected, 'Duplicate registered cell')
        expected[key] = cell
    _require(bool(expected), 'Empty registered grid')
    if {'ordered_seed_list', 'families', 'policy_ids', 'stage_id'} <= set(original):
        grid = [dict(stage_id=original['stage_id'], seed=s, family=f, policy_id=p,
                     cell_key=f"{original['stage_id']}_{s}_{f}_{p}")
                for s, f, p in itertools.product(original['ordered_seed_list'],
                                                original['families'], original['policy_ids'])]
        _require(original['cells'] == grid and original['total_cells'] == len(grid),
                 'Registered grid metadata mismatch')
    continuation = None
    retained = {}
    if continuation_registration is not None:
        continuation = _registration(continuation_registration)
        from .continuation import verify_continuation
        verify_continuation(continuation, original)
        _require(continuation['original_registration_sha256'] == original['registration_sha256'],
                 'Continuation original registration mismatch')
        _require(continuation['cells'] == original['cells'], 'Continuation changed grid')
        for row in continuation['retained_commits']:
            key = row['cell_key']
            _require(key in expected and key not in retained, 'Invalid retained commit inventory')
            retained[key] = row['commit_sha256']
    commits, worlds, denoms = {}, defaultdict(set), defaultdict(set)
    commit_dir = _safe(output, 'commits')
    for path in sorted(commit_dir.glob('*.json')):
        _require(not path.is_symlink(), 'Symlink commit')
        row = _json(path)
        cell, key = row['cell'], row['cell']['cell_key']
        _require(key in expected and key not in commits and cell == expected[key],
                 'Unexpected/duplicate cell metadata')
        _require(path.stem == key, 'Commit filename/cell mismatch')
        reg = original
        if continuation is not None:
            if key in retained:
                _require(_sha(path) == retained[key], 'Retained commit hash mismatch')
            else:
                reg = continuation
        result = audit_cell(output, row, reg)
        group = cell['seed'], cell['family']
        worlds[group].add(row['world_sha256'])
        denoms[group].add(result['metrics']['arrived_members'])
        commits[key] = row
    _require(set(retained) <= set(commits), 'Missing retained commit')
    complete = set(commits) == set(expected)
    _require(complete or allow_incomplete, 'Incomplete registered grid')
    _require(all(len(v) == 1 for v in worlds.values()), 'Common world mismatch')
    _require(all(len(v) == 1 for v in denoms.values()), 'Common denominator mismatch')
    return dict(status='passed' if complete else 'passed_partial_operational_audit',
                complete_registered_grid=complete, verified_cells=len(commits),
                expected_cells=len(expected), all_valid=True, world_parity_verified=True,
                denominator_parity_verified=True, public_event_reconstruction_verified=True,
                private_world_read=False)


def audit_run(output, registration_path, continuation_path=None, *, allow_incomplete=False):
    return audit_campaign(output, registration_path, continuation_path,
                          allow_incomplete=allow_incomplete)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--registration', required=True)
    parser.add_argument('--continuation')
    parser.add_argument('--output', required=True)
    parser.add_argument('--allow-incomplete', action='store_true',
                        help='Operational partial audit only; no complete-grid certification')
    args = parser.parse_args()
    try:
        result = audit_campaign(args.output, args.registration, args.continuation,
                                allow_incomplete=args.allow_incomplete)
    except Exception as exc:
        print(json.dumps(dict(status='failed', error=f'{type(exc).__name__}: {exc}')))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
