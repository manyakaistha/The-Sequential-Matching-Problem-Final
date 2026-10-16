"""One declared four-actor simulator fixture; never an official research episode.

Exercises all120 cold policy calls and independent event audit. Registration
preflight is separately tested; the small fixture deliberately has no scientific
freshness certificate and is not accepted by the campaign launcher.
"""
import copy
import json
from pathlib import Path
import hashlib

from kit import HARD, SOFT
from research8.soft_query_followup.v2 import runner, registration, audit


def test_complete_public_capture_from_declared_simulator_fixture(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[4]
    hard = dict(age_min=18,age_max=65,who_to_meet=['woman'],relationship_structure='monogamous',
        smoking='no',partner_smoking='any',has_children=False,partner_children='any',
        wants_children='yes',acceptable_zones=['zone_a'],schedule=['weekend'])
    members=[]
    for ident in ('fixture_A','fixture_B','fixture_C','fixture_D'):
        fields=dict(hard,**{k:'shared' for k in SOFT})
        members.append(dict(member_id=ident,pool_id='declared_fixture',synthetic=True,age=30,
            gender='woman',zone='zone_a',arrived_day=0,fields=fields,
            field_status={k:'observed' for k in HARD+SOFT},
            field_observed_day={k:0 for k in HARD+SOFT},source='declared_test_fixture',
            truth=copy.deepcopy(fields),exit_day=10000,bias=100,response_rate=1,second_bias=100))
    world=dict(schema_version='1.0.0',seed=1,variant='development',members=members)
    monkeypatch.setattr(runner,'generate',lambda **kw:copy.deepcopy(world))
    monkeypatch.setattr(registration,'verify_registration',lambda *a:True)
    cell=dict(cell_key='declared_fixture_G',stage_id='declared_fixture',seed=1,
              family='development',policy_id='G')
    reg=dict(cells=[cell],source_manifest={'kit.py':registration.file_sha256(root/'kit.py')},
        policies={'G':registration.POLICIES['G']},resource_forecast=dict(registration.CAPS))
    reg['registration_sha256']=registration.registration_hash(reg)
    regpath=tmp_path/'fixture_registration.json'
    registration.write_once(regpath,reg)
    output=tmp_path/'capture'
    record=runner.Research8Runner(root,reg,output).execute_cell(cell)
    assert record['is_valid'],record.get('error')
    assert record['invocation_count']==120
    assert record['metrics']['assignments']>0
    result=audit.audit_run(output,regpath)
    assert result['public_event_reconstruction_verified'] is True
    assert result['private_world_read'] is False
    assert not list(output.rglob('world.json'))
    # Leave a durable summary outside the pytest temporary directory.
    summary={'scope':'one constructed four-actor test, not a sampled reward study',
        'audit':result,'invocations':record['invocation_count'],
        'invocation_seconds_max':record['invocation_seconds_max'],
        'metrics':record['metrics'],'artifact_hashes':record['artifact_hashes']}
    artifact=root/'research8/soft_query_followup/v2/validation/capture_summary.json'
    artifact.parent.mkdir(parents=True,exist_ok=True)
    if not artifact.exists():registration.write_once(artifact,summary)
