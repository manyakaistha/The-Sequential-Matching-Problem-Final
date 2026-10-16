"""Constructed public artifacts only; no simulator episodes or private worlds."""
import copy
import json

import pytest

from research8.soft_query_followup.v2.tests import test_metrics_audit as fixtures
from research8.soft_query_followup.v2.registration import registration_hash
from research8.soft_query_followup.v3 import audit, storage


def closure(tmp_path):
    return fixtures.AuditTests()._closure(tmp_path)


def test_raw_and_archived_public_reconstruction_identical(tmp_path):
    output, reg, attempt, row = closure(tmp_path)
    before = audit.audit_cell(output, row, reg)
    storage.archive_attempt(output, row['attempt_relative_path'], row['artifact_hashes'],
                            codec='gzip', level=3, remove_raw=True)
    assert not attempt.exists()
    assert audit.audit_cell(output, row, reg) == before
    assert audit.audit_campaign(output, reg)['verified_cells'] == 1
    assert before['metrics']['arrived_members'] == 0
    assert before['private_world_read'] is False


def test_corrupt_archive_rejected(tmp_path):
    output, reg, _, row = closure(tmp_path)
    manifest = storage.archive_attempt(output, row['attempt_relative_path'], row['artifact_hashes'],
                                       codec='gzip', level=3, remove_raw=True)
    path = output / manifest['archive_relative_path']
    with path.open('ab') as stream:
        stream.write(b'corruption')
    with pytest.raises(ValueError, match='Archive hash/length mismatch'):
        audit.audit_cell(output, row, reg)


@pytest.mark.parametrize('kind', ['invalid', 'source', 'registration', 'metrics', 'artifact'])
def test_bad_commit_rejected(tmp_path, kind):
    output, reg, _, row = closure(tmp_path)
    row = copy.deepcopy(row)
    if kind == 'invalid':
        row['is_valid'] = False
    elif kind == 'source':
        row['source_sha256'] = {'arbitrary.py': 'c'*64}
    elif kind == 'registration':
        row['registration_sha256'] = 'c'*64
    elif kind == 'metrics':
        row['metrics']['assignments'] = 1
    else:
        del row['artifact_hashes']['status.json']
    with pytest.raises(ValueError):
        audit.audit_cell(output, row, reg)


def test_incomplete_grid_explicitly_operational_only(tmp_path):
    output, regpath, _, row = closure(tmp_path)
    reg = json.loads(regpath.read_text())
    another = dict(row['cell'], cell_key='other', seed=2)
    reg['cells'].append(another)
    reg['registration_sha256'] = registration_hash(reg)
    row['registration_sha256'] = reg['registration_sha256']
    (output / 'commits' / 'cell.json').write_text(json.dumps(row))
    with pytest.raises(ValueError, match='Incomplete registered grid'):
        audit.audit_campaign(output, reg)
    result = audit.audit_campaign(output, reg, allow_incomplete=True)
    assert result['status'] == 'passed_partial_operational_audit'
    assert result['complete_registered_grid'] is False
    assert (result['verified_cells'], result['expected_cells']) == (1, 2)


def test_archive_catalog_cannot_rebind_committed_hashes(tmp_path):
    output, reg, _, row = closure(tmp_path)
    storage.archive_attempt(output, row['attempt_relative_path'], row['artifact_hashes'],
                            codec='gzip', level=3, remove_raw=True)
    row['artifact_hashes']['actions.jsonl'] = 'd'*64
    with pytest.raises(ValueError, match='Archive commit hash coverage mismatch'):
        audit.audit_cell(output, row, reg)


def continuation_fixture(output, original, row, *, retain):
    cont = dict(cells=original['cells'], source_manifest=dict(original['source_manifest'],
                **{'v3.py': 'e'*64}), original_registration_sha256=original['registration_sha256'],
                retained_commits=[dict(cell_key='cell', commit_sha256=audit._sha(output/'commits/cell.json'))]
                if retain else [])
    cont['registration_sha256'] = registration_hash(cont)
    return cont


def test_retained_identity_and_new_identity_kept_separate(tmp_path, monkeypatch):
    output, regpath, _, row = closure(tmp_path)
    original = json.loads(regpath.read_text())
    # Full production freeze validation has its own fixed2880-cell tests.
    monkeypatch.setattr('research8.soft_query_followup.v3.continuation.verify_continuation',
                        lambda continuation, original: original)
    retained = continuation_fixture(output, original, row, retain=True)
    assert audit.audit_campaign(output, original, retained)['verified_cells'] == 1
    new = continuation_fixture(output, original, row, retain=False)
    with pytest.raises(ValueError, match='Registration digest mismatch'):
        audit.audit_campaign(output, original, new)
    row['registration_sha256'] = new['registration_sha256']
    row['source_sha256'] = new['source_manifest']
    (output/'commits/cell.json').write_text(json.dumps(row))
    assert audit.audit_campaign(output, original, new)['verified_cells'] == 1
    with pytest.raises(ValueError, match='Retained commit hash mismatch'):
        audit.audit_campaign(output, original, retained)


def test_arbitrary_new_source_is_rejected_even_with_correct_continuation_digest(tmp_path, monkeypatch):
    output, regpath, _, row = closure(tmp_path)
    original = json.loads(regpath.read_text())
    monkeypatch.setattr('research8.soft_query_followup.v3.continuation.verify_continuation',
                        lambda continuation, original: original)
    new = continuation_fixture(output, original, row, retain=False)
    row['registration_sha256'] = new['registration_sha256']
    row['source_sha256'] = {'unregistered.py': 'f'*64}
    (output/'commits/cell.json').write_text(json.dumps(row))
    with pytest.raises(ValueError, match='Registered source digest mismatch'):
        audit.audit_campaign(output, original, new)
