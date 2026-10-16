"""Source-bound finite screen and one selected final confirmation policy."""
import itertools,json
from pathlib import Path
from research8.soft_query_followup.v2.registration import ROOT,CAPS,FAMILIES,POLICIES as REFERENCES,strict_json,file_sha256,registration_hash,write_once
BASE=ROOT/'research9/final_campaign'
CANDIDATES=['model_greedy','model_soft','model_repair','model_continuation']
STORAGE={'max_evidence_bytes':15*2**30,'audit_transient_max_bytes':512*2**20,'raw_attempt_max_bytes':512*2**20}
ANALYSIS={'primary':'qualifiedMSMI/100 arrived by59 with followup99','inference_unit':'seed mean across6families','n_final_seed_clusters':96,'tests':'fixed hierarchical one-sided paired t alpha.05 C-G thenC-Q6 thenC-P; claims stop atfirstfailure','selection':'positive screen mean versusG; highest candidate mean; exactties fixedsimplerorder','no_optional_stopping':True,'no_final_repairs':True}

def source_manifest(root=ROOT):
    previous=strict_json((root/'research8/continuation_probe/registration.json').read_text())
    sources=dict(previous['source_manifest'])
    paths=list((root/'research9/final_campaign').rglob('*.py'))
    paths += [root/'research9/final_campaign'/p for p in ('CAMPAIGN_PLAN.md','TRAINING_PROTOCOL.md','split.json','data_freeze.json','fit_freeze.json','dataset_ready.json','prediction_report.json','selected_model.json','final_seed_reservation.json','reviews/final_seed_review.json')]
    for p in paths:
        if '__pycache__' not in p.parts and not any(x.startswith('.') for x in p.relative_to(root).parts):sources[str(p.relative_to(root))]=file_sha256(p)
    return sources

def policy_specs(arms):
    asset=BASE/'selected_model.json';sha=file_sha256(asset)
    return {arm:(REFERENCES[arm] if arm in REFERENCES else {'entrypoint':'research9.final_campaign.policy:decide','config':{'id':arm,'model_path':str(asset),'model_sha256':sha}}) for arm in arms}

def verify_registration(reg,root=ROOT):
    if reg.get('schema_version')!='R9-final-campaign-v1' or reg.get('status')!='frozen_execution_registration' or reg.get('execution_authorized') is not True or reg.get('registration_sha256')!=registration_hash(reg):raise ValueError('campaign registration invalid')
    if reg['families']!=FAMILIES or reg['resource_forecast']!=CAPS or reg['storage']!=STORAGE or reg['analysis']!=ANALYSIS:raise ValueError('campaign contracts changed')
    if (reg['active_days'],reg['followup_days'],reg['observation_cutoff'])!=(60,40,99):raise ValueError('campaign horizon changed')
    split=strict_json((BASE/'split.json').read_text());asset=strict_json((BASE/'selected_model.json').read_text())
    receipt=strict_json((BASE/'reviews/final_seed_review.json').read_text())
    if receipt.get('status')!='passed' or receipt.get('reservation_file_sha256')!=file_sha256(BASE/'final_seed_reservation.json'):raise ValueError('independent seed review missing or stale')
    if reg['stage_id']=='R9_final_screen_v1':
        seeds=split['validation'][:8];arms=['G','Q6','P']+CANDIDATES[:4 if asset['probability_admitted'] else 3]
    elif reg['stage_id']=='R9_final_confirmation_v1':
        reserve=strict_json((BASE/'final_seed_reservation.json').read_text());selection=strict_json((BASE/'selection.json').read_text())
        if reserve['status']!='reviewed_independent_random_draws' or selection['status']!='one_candidate_selected':raise ValueError('confirmation admission missing')
        if file_sha256(BASE/'final_seed_reservation.json')!=reg['seed_reservation_sha256'] or file_sha256(BASE/'selection.json')!=reg['selection_sha256']:raise ValueError('confirmation selection/reservation changed')
        allowed=CANDIDATES[:4 if asset['probability_admitted'] else 3]
        if selection.get('candidate') not in allowed:raise ValueError('selected candidate not admitted')
        summary=selection.get('arm_summary',{})
        if set(summary)!=set(['G','Q6','P']+allowed):raise ValueError('selection summary arms changed')
        eligible=[a for a in allowed if summary[a]['mean_msmi']>summary['G']['mean_msmi']]
        deterministic=min(eligible,key=lambda a:(-summary[a]['mean_msmi'],CANDIDATES.index(a))) if eligible else None
        if deterministic!=selection['candidate']:raise ValueError('selection rule changed')
        if any(summary[a]['cells']!=48 or summary[a]['n_seed_clusters']!=8 or summary[a]['fallbacks']!=0 for a in summary):raise ValueError('selection summary incomplete')
        screen=strict_json((BASE/'screen_registration.json').read_text())
        if selection.get('screen_registration_sha256')!=screen['registration_sha256'] or selection.get('screen_audit_proof_sha256')!=file_sha256(BASE/'screen_audit_proof.json'):raise ValueError('selection not bound to audited screen')
        seeds=reserve['seeds'];arms=['G','Q6','P',selection['candidate']]
        if any(type(seed) is not int or not 2**127<=seed<2**128 for seed in seeds):raise ValueError('confirmation seed integer contract violated')
        if len(seeds)!=96 or len(set(seeds))!=96 or set(seeds)&set(sum([split[k] for k in ('train','validation','development_test')],[])):raise ValueError('confirmation overlap')
    else:raise ValueError('unknown stage')
    if reg['ordered_seed_list']!=seeds or reg['policy_ids']!=arms or reg['policies']!=policy_specs(arms):raise ValueError('campaign grid/policy changed')
    cells=[dict(stage_id=reg['stage_id'],seed=s,family=f,policy_id=a,cell_key=f"{reg['stage_id']}_{s}_{f}_{a}") for s,f,a in itertools.product(seeds,FAMILIES,arms)]
    if reg['cells']!=cells or reg['total_cells']!=len(cells):raise ValueError('incomplete declared grid')
    if reg['source_manifest']!=source_manifest(root):raise ValueError('campaign source closure changed')
    for relative,value in reg['source_manifest'].items():
        if file_sha256(root/relative)!=value:raise ValueError('frozen source changed: '+relative)
    return reg

def freeze(stage):
    split=strict_json((BASE/'split.json').read_text());asset=strict_json((BASE/'selected_model.json').read_text())
    if stage=='screen':
        stageid='R9_final_screen_v1';seeds=split['validation'][:8];arms=['G','Q6','P']+CANDIDATES[:4 if asset['probability_admitted'] else 3]
    elif stage=='confirmation':
        stageid='R9_final_confirmation_v1';seeds=strict_json((BASE/'final_seed_reservation.json').read_text())['seeds'];arms=['G','Q6','P',strict_json((BASE/'selection.json').read_text())['candidate']]
    else:raise ValueError('unknownstage')
    reg=dict(schema_version='R9-final-campaign-v1',status='frozen_execution_registration',execution_authorized=True,stage_id=stageid,ordered_seed_list=seeds,families=FAMILIES,policy_ids=arms,policies=policy_specs(arms),source_manifest=source_manifest(),resource_forecast=CAPS,storage=STORAGE,analysis=ANALYSIS,active_days=60,followup_days=40,observation_cutoff=99)
    reg['cells']=[dict(stage_id=stageid,seed=s,family=f,policy_id=a,cell_key=f'{stageid}_{s}_{f}_{a}') for s,f,a in itertools.product(seeds,FAMILIES,arms)];reg['total_cells']=len(reg['cells'])
    if stage=='confirmation':reg.update(seed_reservation_sha256=file_sha256(BASE/'final_seed_reservation.json'),selection_sha256=file_sha256(BASE/'selection.json'))
    reg['registration_sha256']=registration_hash(reg);verify_registration(reg);write_once(BASE/(stage+'_registration.json'),reg)
    return reg
