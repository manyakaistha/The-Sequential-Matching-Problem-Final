"""Fixed, small development replay; no fresh-seed or inferential promotion claim."""
import itertools,json
from pathlib import Path
from research8.soft_query_followup.v2.registration import ROOT,CAPS,FAMILIES,strict_json,file_sha256,registration_hash,write_once
ARMS=['Q6_parent','Q6_return_hold']
POLICIES={a:{'entrypoint':'research8.continuation_probe.policy:decide','config':{'id':a}} for a in ARMS}
STAGE='R8_return_hold_mechanism_v1'
ANALYSIS={'purpose':'mechanism smoke; two reused development seeds, six families, paired unchanged Q6; no significance/winner/promotion claim','success_gates':['all24 valid and independent audits passed','parent action and world parity with prior Q6','hold constraints and actual witness use reported'],'null_gate':'zero triggers or no replacement use closes this frozen rule for scaling; no reward-based sample extension','seed_scope':'lowest two seeds of completed development run reused deliberately; not fresh; not additional independent evidence'}

def manifest(root=ROOT):
    old=strict_json((root/'research8/soft_query_followup/storage_recovery/continuation_registration.json').read_text())
    result=dict(old['source_manifest'])
    for p in (root/'research8/continuation_probe').rglob('*.py'):
        if '__pycache__' not in p.parts and not any(x.startswith('.') for x in p.relative_to(root).parts):result[str(p.relative_to(root))]=file_sha256(p)
    result['research8/soft_query_followup/audit_efficiency/fast_audit.py']=file_sha256(root/'research8/soft_query_followup/audit_efficiency/fast_audit.py')
    return result

def verify_registration(reg,root=ROOT):
    if reg.get('schema_version')!='R8-return-hold-mechanism-v1' or reg.get('registration_sha256')!=registration_hash(reg):raise ValueError('probe registration invalid')
    if reg.get('execution_authorized') is not True or reg.get('status')!='frozen_development_replay':raise ValueError('probe not frozen')
    if reg.get('stage_id')!=STAGE or (reg.get('active_days'),reg.get('followup_days'),reg.get('observation_cutoff'))!=(60,40,99) or reg.get('analysis')!=ANALYSIS:raise ValueError('probe horizon/purpose changed')
    if reg['ordered_seed_list']!=[840001,840002] or reg['families']!=FAMILIES or reg['policy_ids']!=ARMS or reg['policies']!=POLICIES:raise ValueError('fixed replay grid changed')
    cells=[dict(stage_id=STAGE,seed=s,family=f,policy_id=a,cell_key=f'{STAGE}_{s}_{f}_{a}') for s,f,a in itertools.product(reg['ordered_seed_list'],FAMILIES,ARMS)]
    if reg['cells']!=cells or reg['total_cells']!=24 or reg['resource_forecast']!=CAPS:raise ValueError('probe cells/caps changed')
    if reg['storage']!={'max_evidence_bytes':15*2**30,'audit_transient_max_bytes':512*2**20,'raw_attempt_max_bytes':512*2**20}:raise ValueError('storage changed')
    if reg['source_manifest']!=manifest(root):raise ValueError('probe source closure changed')
    for relative,digest in reg['source_manifest'].items():
        if file_sha256(root/relative)!=digest:raise ValueError('probe source changed: '+relative)
    return reg

def freeze():
    reg=dict(schema_version='R8-return-hold-mechanism-v1',status='frozen_development_replay',execution_authorized=True,stage_id=STAGE,ordered_seed_list=[840001,840002],families=FAMILIES,policy_ids=ARMS,policies=POLICIES,resource_forecast=CAPS,source_manifest=manifest(),total_cells=24,active_days=60,followup_days=40,observation_cutoff=99,storage={'max_evidence_bytes':15*2**30,'audit_transient_max_bytes':512*2**20,'raw_attempt_max_bytes':512*2**20},analysis=ANALYSIS)
    reg['cells']=[dict(stage_id=STAGE,seed=s,family=f,policy_id=a,cell_key=f'{STAGE}_{s}_{f}_{a}') for s,f,a in itertools.product(reg['ordered_seed_list'],FAMILIES,ARMS)]
    reg['registration_sha256']=registration_hash(reg);verify_registration(reg)
    write_once(ROOT/'research8/continuation_probe/registration.json',reg)
if __name__=='__main__':freeze()
