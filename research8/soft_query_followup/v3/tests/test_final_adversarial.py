"""Independent continuation counterexamples; synthetic metadata, no episodes."""
import copy
import itertools
import json

import pytest

from research8.soft_query_followup.v2.registration import registration_hash
from research8.soft_query_followup.v3 import continuation


def fixed_fixture(tmp_path):
    seeds = list(range(96))
    families = [f'family{i}' for i in range(6)]
    policies = [f'policy{i}' for i in range(5)]
    cells = [dict(stage_id='fixed', seed=s, family=f, policy_id=p,
                  cell_key=f'fixed_{s}_{f}_{p}')
             for s, f, p in itertools.product(seeds, families, policies)]
    (tmp_path / 'AGENTS.md').write_text('synthetic review fixture\n')
    source = tmp_path / 'original.py'
    source.write_text('original executable bytes\n')
    original = dict(stage_id='fixed', ordered_seed_list=seeds, families=families,
                    policy_ids=policies, policies={p: {'entrypoint': p} for p in policies},
                    cells=cells, total_cells=2880, analysis={'fixed': True},
                    resource_forecast={'max_workers': 7, 'invocation_wall_seconds': 10},
                    source_manifest={'original.py': continuation.file_sha256(source)})
    original['registration_sha256'] = registration_hash(original)
    path = tmp_path / 'original.json'
    path.write_text(json.dumps(original))
    output = tmp_path / 'output'
    commits = output / 'commits'
    commits.mkdir(parents=True)
    row = dict(cell=cells[0], registration_sha256=original['registration_sha256'],
               source_sha256=original['source_manifest'], is_valid=True, metrics={'valid': True})
    commit = commits / (cells[0]['cell_key'] + '.json')
    commit.write_text(json.dumps(row))
    note = tmp_path / 'recovery.json'
    note.write_text('{"status":"stopped"}\n')
    reg = continuation.build(path, output, note, root=tmp_path)
    return original, reg, output, row


@pytest.mark.parametrize('field', ['ordered_seed_list', 'families', 'policy_ids',
                                  'policies', 'cells', 'analysis', 'resource_forecast'])
def test_changed_experiment_metadata_rejected_even_with_fresh_self_hash(tmp_path, field):
    original, reg, output, _ = fixed_fixture(tmp_path)
    changed = copy.deepcopy(reg)
    value = changed[field]
    if isinstance(value, list):
        changed[field] = value[:-1]
    else:
        changed[field]['changed'] = True
    changed['registration_sha256'] = registration_hash(changed)
    with pytest.raises(ValueError):
        continuation.verify_continuation(changed, original, root=tmp_path, output=output)


def test_retained_and_new_commit_sources_are_bound_separately(tmp_path):
    original, reg, output, row = fixed_fixture(tmp_path)
    assert continuation.verify_commit_identity(output, row, reg, original) == original
    new = copy.deepcopy(row)
    new['cell'] = reg['cells'][1]
    with pytest.raises(ValueError, match='attribution mismatch'):
        continuation.verify_commit_identity(output, new, reg, original)
    new['registration_sha256'] = reg['registration_sha256']
    new['source_sha256'] = reg['source_manifest']
    assert continuation.verify_commit_identity(output, new, reg, original) == reg
    new['source_sha256'] = {'unregistered.py': 'f'*64}
    with pytest.raises(ValueError, match='attribution mismatch'):
        continuation.verify_commit_identity(output, new, reg, original)


def test_retained_bytes_and_original_source_cannot_be_changed(tmp_path):
    original, reg, output, row = fixed_fixture(tmp_path)
    path = output / 'commits' / (row['cell']['cell_key']+'.json')
    saved = path.read_bytes()
    path.write_bytes(saved + b'\n')
    with pytest.raises(ValueError, match='retained commit changed'):
        continuation.verify_continuation(reg, original, root=tmp_path, output=output)
    path.write_bytes(saved)
    (tmp_path/'original.py').write_text('changed source\n')
    with pytest.raises(ValueError, match='source hash mismatch'):
        continuation.verify_continuation(reg, original, root=tmp_path, output=output)


def test_source_path_escape_rejected_even_with_fresh_self_hash(tmp_path):
    original, reg, _, _ = fixed_fixture(tmp_path)
    reg['source_manifest']['../outside.py'] = '0'*64
    reg['registration_sha256'] = registration_hash(reg)
    with pytest.raises(ValueError, match='unsafe source path'):
        continuation.verify_continuation(reg, original, root=tmp_path)


def test_unregistered_new_dependency_is_rejected(tmp_path):
    original, reg, _, _ = fixed_fixture(tmp_path)
    newdir = tmp_path/'research8/soft_query_followup/v3'
    newdir.mkdir(parents=True)
    (newdir/'added.py').write_text('new unbound source\n')
    with pytest.raises(ValueError, match='dependency missing'):
        continuation.verify_continuation(reg, original, root=tmp_path)


def test_recovery_record_change_rejected(tmp_path):
    original, reg, _, _ = fixed_fixture(tmp_path)
    (tmp_path/'recovery.json').write_text('{"status":"changed"}\n')
    with pytest.raises(ValueError, match='recovery note changed'):
        continuation.verify_continuation(reg, original, root=tmp_path)


@pytest.mark.parametrize('field,value', [('execution_authorized', False),
                                       ('status', 'unfrozen')])
def test_authorization_status_cannot_be_disabled_and_rehashed(tmp_path, field, value):
    original, reg, _, _ = fixed_fixture(tmp_path)
    reg[field] = value
    reg['registration_sha256'] = registration_hash(reg)
    with pytest.raises(ValueError, match='invalid continuation'):
        continuation.verify_continuation(reg, original, root=tmp_path)


def test_archive_audit_refuses_oversize_before_materialization(tmp_path, monkeypatch):
    from research8.soft_query_followup.v2.tests import test_metrics_audit as fixtures
    from research8.soft_query_followup.v3 import audit, storage
    import hashlib
    output, reg, _, row = fixtures.AuditTests()._closure(tmp_path)
    manifest = storage.archive_attempt(output, row['attempt_relative_path'],
                                       row['artifact_hashes'], codec='gzip', remove_raw=True)
    first = next(iter(manifest['files']))
    manifest['files'][first]['bytes'] = 512*2**20 + 1
    catalog = output/'archive_manifests'/(hashlib.sha256(
        row['attempt_relative_path'].encode()).hexdigest()+'.json')
    catalog.write_text(json.dumps(manifest))
    def forbidden(*args, **kwargs):
        raise AssertionError('materialization should not be called')
    monkeypatch.setattr(storage, 'materialize_attempt', forbidden)
    with pytest.raises(ValueError, match='materialization exceeds'):
        audit.audit_cell(output, row, reg)


def test_storage_reservation_counts_existing_bytes_worker_slots_and_audit(tmp_path, monkeypatch):
    from research8.soft_query_followup.v3 import launcher
    reg = {'storage': {'max_evidence_bytes': 15*2**30,
                       'audit_transient_max_bytes': 512*2**20}}
    reservation = 7*(1100*2**20) + 512*2**20
    monkeypatch.setattr(launcher, 'evidence_bytes', lambda output: 15*2**30-reservation)
    assert launcher.storage_dispatch_allowed(tmp_path, reg, pending_count=7)
    monkeypatch.setattr(launcher, 'evidence_bytes', lambda output: 15*2**30-reservation+1)
    assert not launcher.storage_dispatch_allowed(tmp_path, reg, pending_count=7)
    assert launcher.storage_dispatch_allowed(tmp_path, reg, pending_count=6)


@pytest.mark.parametrize('workers', [0, 8, True, 1.0])
def test_worker_pool_rejects_noninteger_or_more_than_seven(workers):
    from research8.soft_query_followup.v3 import launcher
    with pytest.raises(ValueError):
        launcher.validate_worker_count(workers, {'max_workers': 7})


def test_single_process_snapshot_sums_worker_and_all_descendants():
    from research8.soft_query_followup.v3 import launcher
    snapshot = '10 1 100 0:02\n11 10 200 0:03\n12 11 300 0:04\n20 1 900 0:09\n'
    assert launcher.proc_usage(10, snapshot) == (600*1024, 9)
    assert launcher.proc_usage(20, snapshot) == (900*1024, 9)


def test_worker_cannot_launch_without_coordinator_lease(tmp_path):
    from research8.soft_query_followup.v3 import launcher
    with pytest.raises(ValueError, match='locked coordinator'):
        launcher.worker_main(tmp_path/'not-read.json', tmp_path, 'not-run')
