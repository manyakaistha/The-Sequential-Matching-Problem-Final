"""Guard and transport regressions, using declared fixtures only."""
import copy
import json
from pathlib import Path
from unittest.mock import patch

import pytest
from research8.soft_query_followup.v2 import registration as regmod
from research8.soft_query_followup.v2.launcher import worker_main, check_disk
from research8.soft_query_followup.v2.reference_adapter import decide


def fixture_registration(tmp_path, monkeypatch):
    (tmp_path/'source.py').write_text('fixture source')
    monkeypatch.setattr(regmod, 'source_manifest', lambda root: {'source.py': regmod.file_sha256(root/'source.py')})
    audit = {'status':'repository_visible_no_overlap', 'proposed_seeds':[1], 'collisions':[],
             'archives_not_decoded':[], 'unreadable_or_oversized':[]}
    regmod.write_once(tmp_path/'audit.json',audit)
    regmod.write_once(tmp_path/'review.json', {'status':'accepted_repository_visible_freshness',
        'proposed_seeds':[1], 'audit_sha256':regmod.file_sha256(tmp_path/'audit.json'),
        'reviewer':'constructed fixture', 'archive_omissions_disposition':'fixture has no archives'})
    return regmod.build_registration('fixture',[1],['G'],tmp_path/'audit.json',tmp_path/'review.json',root=tmp_path)


def test_source_tampering_rejected(tmp_path,monkeypatch):
    reg=fixture_registration(tmp_path,monkeypatch)
    (tmp_path/'source.py').write_text('changed')
    # Do not update the registered dependency closure: actual current source must fail.
    with pytest.raises(ValueError,match='source hash mismatch'):
        regmod.verify_registration(reg,tmp_path)


@pytest.mark.parametrize('key,value', [('max_attempt_wall_seconds',181),('max_attempt_cpu_seconds',91),
    ('max_rss_gib',5),('max_total_worker_rss_gib',9),('max_workers',8),('free_reserve_gib_min',1),('boot_free_reserve_gib_min',.01)])
def test_resigned_registration_cannot_expand_guards(tmp_path,monkeypatch,key,value):
    reg=fixture_registration(tmp_path,monkeypatch)
    reg['resource_forecast'][key]=value
    reg['registration_sha256']=regmod.registration_hash(reg)
    with pytest.raises(ValueError):regmod.verify_registration(reg,tmp_path)


def test_resigned_path_traversal_rejected(tmp_path,monkeypatch):
    reg=fixture_registration(tmp_path,monkeypatch)
    reg['stage_id']='../unsafe'
    reg['registration_sha256']=regmod.registration_hash(reg)
    with pytest.raises(ValueError,match='unsafe stage'):regmod.verify_registration(reg,tmp_path)


def test_missing_cell_rejected(tmp_path,monkeypatch):
    reg=fixture_registration(tmp_path,monkeypatch)
    reg['cells'].pop()
    reg['registration_sha256']=regmod.registration_hash(reg)
    with pytest.raises(ValueError,match='grid'):regmod.verify_registration(reg,tmp_path)


def test_unleased_worker_is_rejected():
    with pytest.raises(ValueError,match='locked coordinator'):
        worker_main('unused','unused','unused')


def test_output_disk_guard(tmp_path):
    with patch('research8.soft_query_followup.v2.launcher.shutil.disk_usage') as disk:
        disk.return_value=type('Usage',(),{'free':1})()
        with pytest.raises(RuntimeError,match='results drive'):
            check_disk(tmp_path,regmod.CAPS)


def test_reference_fallback_status_propagated():
    from research8.soft_query_followup.v2 import reference_adapter
    with patch.object(reference_adapter.references,'decide',return_value={'asks':[],'memory':None}), \
         patch.object(reference_adapter.references,'LAST_STATUS',{'fallback':True,'reason':'fixture'}):
        assert decide({}, {'id':'P'})=={'asks':[],'memory':None}
        assert reference_adapter.LAST_STATUS['fallback'] is True
    reference_adapter.LAST_STATUS={'fallback':False,'reason':None}


@pytest.mark.parametrize('workers',[1,3,6,7])
def test_user_authorized_worker_counts(workers):
    from research8.soft_query_followup.v2.launcher import validate_worker_count
    validate_worker_count(workers,regmod.CAPS)


@pytest.mark.parametrize('workers',[0,8,True,3.5])
def test_excess_or_invalid_worker_counts_rejected(workers):
    from research8.soft_query_followup.v2.launcher import validate_worker_count
    with pytest.raises(ValueError):validate_worker_count(workers,regmod.CAPS)


def test_combined_worker_memory_guard():
    from research8.soft_query_followup.v2.launcher import check_combined_rss
    check_combined_rss(8*2**30,regmod.CAPS)
    with pytest.raises(RuntimeError,match='combined'):
        check_combined_rss(8*2**30+1,regmod.CAPS)
