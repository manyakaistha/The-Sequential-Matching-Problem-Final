"""One reusable independent audit and fixed registered policy inference."""
import hashlib,json,math,sys
from pathlib import Path
from statistics import mean,stdev
from scipy.stats import t
from .registration import ROOT,BASE,verify_registration,CANDIDATES
from research8.soft_query_followup.v2.registration import write_once,file_sha256
from research8.soft_query_followup.audit_efficiency.fast_audit import audit_campaign,digest,_evidence_identity,optimized_stream,PINS

def rows_for(output,reg):
    rows={}
    for path in (output/'commits').glob('*.json'):
        row=json.loads(path.read_text());c=row['cell'];key=c['cell_key']
        if key in rows:raise ValueError('duplicate commit')
        expected={cell['cell_key']:cell for cell in reg['cells']}
        if (key not in expected or c!=expected[key] or row.get('registration_sha256')!=reg['registration_sha256'] or row.get('source_sha256')!=reg['source_manifest'] or row.get('is_valid') is not True or row.get('metrics',{}).get('valid') is not True or row.get('error') is not None or row.get('fallback_count')!=0):raise ValueError('invalid committed attribution/validity')
        rows[key]=row
    if set(rows)!={c['cell_key'] for c in reg['cells']}:raise ValueError('incomplete committed grid')
    return rows

def audit_stage(stage):
    regpath=BASE/(stage+'_registration.json');reg=json.loads(regpath.read_text());verify_registration(reg)
    output=ROOT/'results/research9/final_campaign'/stage
    proof=BASE/(stage+'_audit_proof.json')
    if proof.exists():
        p=json.loads(proof.read_text());assert p['payload_sha256']==digest({k:v for k,v in p.items() if k!='payload_sha256'})
        expected_registration=dict(original_sha256=digest(reg),continuation_sha256=None)
        assert p['registration']==expected_registration
        expected_sources=dict(PINS);expected_sources.update(reg['source_manifest'])
        assert p['sources']==expected_sources
        for relative,value in expected_sources.items():assert file_sha256(ROOT/relative)==value
        from research8.soft_query_followup.audit_efficiency import fast_audit
        adapter=Path(fast_audit.__file__)
        implementation=dict(adapter=dict(sha256=file_sha256(adapter),bytes=adapter.stat().st_size),frozen_sources=PINS,transformed_stream_sha256=optimized_stream()[1],python=sys.version)
        assert p['implementation']==implementation
        expected_keys={cell['cell_key'] for cell in reg['cells']}
        assert len(p['checkpoints'])==len(expected_keys) and {r['cell_key'] for r in p['checkpoints']}==expected_keys
        closure=p['result']
        assert closure['verified_cells']==closure['expected_cells']==len(expected_keys)
        assert all(closure[k] is True for k in ('all_valid','complete_registered_grid','world_parity_verified','denominator_parity_verified','public_event_reconstruction_verified')) and closure['private_world_read'] is False
        current=rows_for(output,reg);bykey={}
        for path in (BASE/(stage+'_audit_checkpoints')).glob('*.json'):
            record=json.loads(path.read_text());key=record['cell_key']
            assert key not in bykey;bykey[key]=(path,record)
        assert set(bykey)==expected_keys
        for record in p['checkpoints']:
            path,checkpoint=bykey[record['cell_key']];assert file_sha256(path)==record['checkpoint_sha256']
            assert checkpoint['payload_sha256']==digest({k:v for k,v in checkpoint.items() if k!='payload_sha256'})
            assert checkpoint['schema']=='r8-fast-audit-cell-v1' and checkpoint['result']['status']=='passed'
            binding=checkpoint['binding'];row=current[record['cell_key']]
            assert binding['registration']==expected_registration and binding['sources']==expected_sources and binding['implementation']==implementation
            assert binding['cell_registration_sha256']==reg['registration_sha256']
            commit=output/'commits'/(record['cell_key']+'.json')
            assert binding['commit']==dict(sha256=file_sha256(commit),bytes=commit.stat().st_size)
            assert binding['evidence']==_evidence_identity(output,row)
            assert checkpoint['result']['metrics']==row['metrics']
    else:closure=audit_campaign(output,regpath,checkpoint_dir=BASE/(stage+'_audit_checkpoints'),proof_path=proof)
    assert closure['status']=='passed' and closure['complete_registered_grid']
    return reg,output,closure

def summarize(reg,rows):
    values={(r['cell']['seed'],r['cell']['family'],r['cell']['policy_id']):r for r in rows.values()}
    result={}
    for arm in reg['policy_ids']:
        selected=[r for r in rows.values() if r['cell']['policy_id']==arm]
        seed_means=[mean(values[s,f,arm]['metrics']['msmi_per_100_arrived_members'] for f in reg['families']) for s in reg['ordered_seed_list']]
        result[arm]=dict(cells=len(selected),n_seed_clusters=len(seed_means),mean_msmi=mean(seed_means),seed_cluster_sd=stdev(seed_means),seed_cluster_se=stdev(seed_means)/math.sqrt(len(seed_means)),qualified_pairs=sum(r['metrics']['mutual_second_meeting_intention'] for r in selected),mean_assignments=mean(r['metrics']['assignments'] for r in selected),mean_coverage=mean(r['metrics']['coverage'] for r in selected),fallbacks=sum(r['fallback_count'] for r in selected),maximum_cold_transport_seconds=max(r['invocation_seconds_max'] for r in selected))
    return values,result

def select():
    reg,out,closure=audit_stage('screen');rows=rows_for(out,reg);values,summary=summarize(reg,rows)
    parity=0
    for (seed,family,arm),row in values.items():
        if arm in ('G','Q6','P'):
            original=ROOT/'results/research8/soft_query_followup/v2_replication/commits'/f'R8V2_development_replication_{seed}_{family}_{arm}.json'
            old=json.loads(original.read_text())
            assert all(old[k]==row[k] for k in ('world_sha256','action_sha256','metrics','invocation_count','fallback_count'))
            parity+=1
    assert parity==8*6*3
    candidates=[a for a in CANDIDATES if a in summary and summary[a]['mean_msmi']>summary['G']['mean_msmi']]
    chosen=min(candidates,key=lambda a:(-summary[a]['mean_msmi'],CANDIDATES.index(a))) if candidates else None
    result=dict(status='one_candidate_selected' if chosen else 'no_candidate_qualified',candidate=chosen,arm_summary=summary,reference_exact_replays=parity,audit=closure,screen_registration_sha256=reg['registration_sha256'],screen_audit_proof_sha256=file_sha256(BASE/'screen_audit_proof.json'),inference_scope='8reusedvalidationgroups; selectiononly; noformalpolicyvalueclaim')
    write_once(BASE/'selection.json',result)
    print(json.dumps({'event':'screen_selection','candidate':chosen,'means':{a:s['mean_msmi'] for a,s in summary.items()}},indent=2),flush=True)
    return chosen

def final_report():
    reg,out,closure=audit_stage('confirmation');rows=rows_for(out,reg);values,summary=summarize(reg,rows)
    candidate=json.loads((BASE/'selection.json').read_text())['candidate'];contrasts={};claims_open=True
    for reference in ('G','Q6','P'):
        diffs=[mean(values[s,f,candidate]['metrics']['msmi_per_100_arrived_members']-values[s,f,reference]['metrics']['msmi_per_100_arrived_members'] for f in reg['families']) for s in reg['ordered_seed_list']]
        avg,sd=mean(diffs),stdev(diffs);se=sd/math.sqrt(len(diffs));df=len(diffs)-1
        if se:
            stat=avg/se;p=float(t.sf(stat,df));radius=float(t.ppf(.975,df))*se;ci=[avg-radius,avg+radius];lower=avg-float(t.ppf(.95,df))*se
        else:stat=None;p=1.;ci=[0.,0.] if avg==0 else None;lower=None
        tested=claims_open;passed=tested and p<.05 and avg>0
        contrasts[candidate+' - '+reference]=dict(mean_difference=avg,seed_cluster_sd=sd,seed_cluster_se=se,n_seed_clusters=len(diffs),df=df,t_statistic=stat,p_one_sided=p,exploratory_ci95_two_sided=ci,one_sided95_lower=lower,formally_tested=tested,superiority_established=bool(passed),seed_differences=diffs,wins=sum(d>0 for d in diffs),ties=sum(d==0 for d in diffs),losses=sum(d<0 for d in diffs),degeneracy='zero_variance_no_standard_t_claim' if not se else None)
        claims_open=bool(passed)
    greedy_win=contrasts[candidate+' - G']['superiority_established'];panel_win=all(c['superiority_established'] for c in contrasts.values())
    result=dict(status='completed_audited_final_campaign',candidate=candidate,greedy_superiority_established=greedy_win,strong_panel_superiority_established=panel_win,arm_summary=summary,contrasts=contrasts,audit=closure,confirmation_registration_sha256=reg['registration_sha256'],audit_proof_sha256=file_sha256(BASE/'confirmation_audit_proof.json'),seed_scope=json.loads((BASE/'final_seed_reservation.json').read_text())['scope'],selection_source='developmentonlybeforefinaloutcomes',limitations=['finiteportfolio; no guaranteeoruniversaloptimality','seedhistoricalcompletenesslimitationsandrandomdrawcollisionbounddocumented','one-daycontinuation/VOIapproximationsremainheuristics','nooptionalstopping,finalrepairoradditionalclaim-generatingrun'])
    write_once(BASE/'final_results.json',result)
    lines=['# Final campaign result','',f'Greedy superiority established: {greedy_win}. Strong-panel superiority established: {panel_win}.','',f'Selected candidate: {candidate}.96independent seed clusters, six families; all2304cells independently audited.','', '| Arm | MSMI/100 | Qualified pairs |','|---|---:|---:|']
    for a,s in summary.items():lines.append(f"|{a}|{s['mean_msmi']:.6f}|{s['qualified_pairs']}|")
    lines+=['','| Contrast | Difference | One-sided p | Formal superiority |','|---|---:|---:|---|']
    for name,c in contrasts.items():lines.append(f"|{name}|{c['mean_difference']:+.6f}|{c['p_one_sided']:.6g}|{c['superiority_established']}|")
    lines+=['','Claims follow the frozenG→Q6→P hierarchy. Later comparisons are descriptive if an earlier gate fails. Independently randomized seeds have scoped repository-visible nonoverlap; universal historical prior-use is unverified. All failures, approximation limits and intervals are in final_results.json. No further search or confirmation expansion is part of this campaign.']
    (BASE/'FINAL_REPORT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'event':'final_complete','greedy_win':greedy_win,'strong_panel_win':panel_win,'report':str(BASE/'FINAL_REPORT.md')},indent=2),flush=True)
    return result
