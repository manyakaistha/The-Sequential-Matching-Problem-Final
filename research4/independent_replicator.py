"""Independent direct simulator loop and seed-cluster reward reconstruction.
Adapted independently owned round3 request loop/public scorer to round4.
Does not import director benchmark.py/analyze.py or evaluate.py. Policy inference
imports only the evaluated policy. Privileged world is confined to Simulator.
One worker; only registered or already-exposed seeds specified by director.
"""
import argparse, collections, hashlib, json, math, statistics, subprocess, sys, time
from pathlib import Path
from kit import Simulator, generate, VERSION

LIMIT=1048576
FAMILIES=('development','sparse','cold_start','delayed','shift','drift')

def strict(raw):
    return json.loads(raw,parse_constant=lambda v:(_ for _ in ()).throw(ValueError('nonfinite')))

def validate(response,phase):
    key='asks' if phase=='ask' else 'pairs'
    assert isinstance(response,dict) and set(response)=={key,'memory'}
    assert isinstance(response[key],list)
    assert len(json.dumps(response['memory'],allow_nan=False).encode())<LIMIT
    if phase=='ask':
        assert all(isinstance(a,dict) and set(a)=={'member_id','field'} and all(isinstance(v,str) for v in a.values()) for a in response[key])
    else:
        assert all(isinstance(p,list) and len(p)==2 and all(isinstance(v,str) for v in p) for p in response[key])
    return key

def rewards(sim):
    # Independent public-event scorer, not Simulator.metrics.
    events=collections.defaultdict(list)
    for event in sim.receive_feedback():events[event['introduction_id']].append(event)
    accepts=dates=qualified=pauses=0
    for intro in sim.introductions:
        es=events[intro['introduction_id']]
        rs=[e for e in es if e['event']=='introduction_response']
        ds=[e for e in es if e['event']=='date_happened' and e['value'] is True]
        ss=[e for e in es if e['event']=='second_meeting_intention']
        accepts+=len(rs)==2 and all(e['value']=='yes' for e in rs)
        dates+=bool(ds)
        pauses+=len(ss)==2 and all(e['value']=='yes' for e in ss)
        if ds and len(ss)==2 and all(e['value']=='yes' for e in ss):
            qdate=ds[0]['occurred_day']-intro['assigned_day']<=30
            qfeedback=all(e['occurred_day']-ds[0]['occurred_day']<=3 for e in ss)
            qualified+=qdate and qfeedback
    arrived=len([m for m in sim.observe()['members'] if m['arrived_day']<=59])
    served=len({u for i in sim.introductions for u in (i['user_a'],i['user_b'])})
    return dict(assignments=len(sim.introductions),mutual_acceptances=accepts,dates=dates,
                mutual_second_meeting_intention=qualified,positive_pause_dyads=pauses,
                arrived_members=arrived,served_members=served,coverage=served/max(1,arrived),
                ask_cost=sim.asks_total,msmi_per_100_arrived_members=100*qualified/max(1,arrived))

def replay(name,seed,variant,mode,reference=None):
    import research4.policy as policy
    sim=Simulator(generate(seed,200,'evaluation',variant)); memory=None
    actions=[];latencies=[];fallbacks=0;initial=policy.FALLBACK_COUNT;digest=hashlib.sha256()
    start=time.process_time();wall=time.perf_counter()
    for day in range(60):
        assert sim.day==day
        for phase in ('ask','match'):
            request={'schema_version':VERSION,'phase':phase,'state':sim.observe(),'memory':memory}
            encoded=json.dumps(request,allow_nan=False).encode();assert len(encoded)<=LIMIT
            tick=time.perf_counter()
            if mode=='subprocess':
                child=subprocess.run([sys.executable,'-m','research4.policy','--candidate',name],input=encoded,capture_output=True,timeout=10)
                assert child.returncode==0 and len(child.stdout)<=LIMIT and len(child.stderr)<=LIMIT
                fallbacks+=child.stderr.count(b'round4 fallback:')
                response=strict(child.stdout)
            else:response=strict(json.dumps(policy.decide(strict(encoded),policy.CANDIDATES[name]),allow_nan=False))
            latencies.append(time.perf_counter()-tick)
            key=validate(response,phase);memory=response['memory'];act=response[key]
            actions.append([phase,day,act]);digest.update(json.dumps([phase,day,act],sort_keys=True).encode())
            if phase=='ask':sim.resolve_asks(act)
            else:sim.advance(act)
    for _ in range(40):sim.advance([])
    assert sim.day==100
    if mode=='direct':fallbacks=policy.FALLBACK_COUNT-initial
    canonical=[[phase,day,sorted([sorted(a) if phase=='match' else a for a in acts],key=lambda a:json.dumps(a,sort_keys=True))] for phase,day,acts in actions]
    row=dict(policy=name,seed=seed,variant=variant,execution=mode,valid=True,
             metrics=rewards(sim),action_sha256=digest.hexdigest(),
             semantic_action_sha256=hashlib.sha256(json.dumps(canonical,sort_keys=True).encode()).hexdigest(),
             fallback_count=fallbacks,cpu_seconds=time.process_time()-start,wall_seconds=time.perf_counter()-wall,
             max_call_seconds=max(latencies),invocations=len(latencies))
    if reference:
        data=json.loads(Path(reference).read_text())
        rs=[r for r in data['episodes'] if r['policy']==name and r['seed']==seed and r['variant']==variant]
        assert len(rs)==1
        old=rs[0];row['reference']=str(reference)
        row['metric_differences']={k:[old.get(k),v] for k,v in row['metrics'].items() if k in old and old[k]!=v}
        row['byte_digest_match']=old['action_sha256']==row['action_sha256']
        row['semantic_digest_match']=old.get('semantic_action_sha256')==row['semantic_action_sha256']
        if old.get('trace') and Path(old['trace']).exists():
            oldactions=json.loads(Path(old['trace']).read_text())['actions']
            row['ordered_actions_equal']=actions==oldactions
            row['semantic_actions_equal']=all(p1==p2 and d1==d2 and (sorted(map(sorted,a1))==sorted(map(sorted,a2)) if p1=='match' else sorted(a1,key=lambda a:json.dumps(a,sort_keys=True))==sorted(a2,key=lambda a:json.dumps(a,sort_keys=True))) for (p1,d1,a1),(p2,d2,a2) in zip(actions,oldactions)) and len(actions)==len(oldactions)
    return row

def cluster_audit(reference):
    from scipy.stats import t
    data=json.loads(Path(reference).read_text());assert data['complete'];groups=collections.defaultdict(lambda:collections.defaultdict(dict))
    for r in data['episodes']:
        assert r['valid'] and not r.get('failure_count',0) and not r.get('optimized_fallback_count',0)
        assert r['variant'] not in groups[r['policy']][r['seed']]
        groups[r['policy']][r['seed']][r['variant']]=r['msmi_per_100_arrived_members']
    expected={(p,s,v) for p in data['planned_policies'] for s in data['planned_seeds'] for v in FAMILIES}
    found=[(r['policy'],r['seed'],r['variant']) for r in data['episodes']]
    assert len(found)==len(expected)==data['planned_episodes'] and set(found)==expected
    seeds=set(groups['greedy']);assert all(set(ss)==seeds for ss in groups.values())
    assert all(set(v)==set(FAMILIES) for ss in groups.values() for v in ss.values())
    means={p:{s:sum(v.values())/6 for s,v in ss.items()} for p,ss in groups.items()}
    out={}
    for p,values in means.items():
        d=[values[s]-means['greedy'][s] for s in sorted(seeds)];m=statistics.mean(d);sd=statistics.stdev(d) if len(d)>1 else 0
        err=float(t.ppf(.975,len(d)-1))*sd/math.sqrt(len(d)) if len(d)>1 else None
        out[p]={'n':len(d),'mean':statistics.mean(values.values()),'paired_difference':m,'paired_sd':sd,'ci95':[m-err,m+err] if err is not None else None,'p_two_sided':float(2*t.sf(abs(m)/(sd/math.sqrt(len(d))),len(d)-1)) if sd else None}
    result={'source':reference,'clusters':out,'method':'independent six-family seed average and paired t; no director analysis imports'}
    if Path(reference).stem=='confirmation':
        import numpy as np
        freeze=json.loads((Path(reference).parent/'freeze.json').read_text())
        assert data['code_hashes']==freeze['code_hashes']
        assert all(hashlib.sha256(Path(f).read_bytes()).hexdigest()==h for f,h in freeze['code_hashes'].items())
        assert data['planned_seeds']==list(range(freeze['confirmation_seeds'][0],freeze['confirmation_seeds'][1]+1))
        assert len(seeds)==freeze['confirmation_n'] and set(groups)=={'greedy',freeze['policy']}
        assert hashlib.sha256(Path('research4/EXPERIMENT_REGISTRY.md').read_bytes()).hexdigest()==freeze['registry_sha256']
        selected=freeze['policy'];d=np.array([means[selected][seed]-means['greedy'][seed] for seed in sorted(seeds)])
        m,sd=float(d.mean()),float(d.std(ddof=1));radius=float(t.ppf(1-.05/6,len(d)-1))*sd/math.sqrt(len(d))
        ci=[m-radius,m+radius];pvalue=out[selected]['p_two_sided']
        draws=np.random.default_rng(90210).integers(0,len(d),(10000,len(d)))
        result['confirmation_checks']={'selected':selected,'freeze_hashes_grid_registry_match':True,'program_family_tests':3,'program_alpha':.05/3,'program_ci98_333333':ci,'nominal_superiority':out[selected]['ci95'][0]>0,'program_superiority':bool(ci[0]>0 and pvalue is not None and pvalue<.05/3),'bootstrap95':np.quantile(d[draws].mean(axis=1),[.025,.975]).tolist(),'seed_differences':dict(zip(map(str,sorted(seeds)),d.tolist())),'leave_one_seed_out_range':[float(min(np.delete(d,i).mean() for i in range(len(d)))),float(max(np.delete(d,i).mean() for i in range(len(d))))],'resource_counts':{'invalid':sum(not r['valid'] for r in data['episodes']),'failures':sum(r.get('failure_count',0) for r in data['episodes']),'fallbacks':sum(r.get('optimized_fallback_count',0) for r in data['episodes'])},'qualified_counts':{policy:sum(r['mutual_second_meeting_intention'] for r in data['episodes'] if r['policy']==policy) for policy in groups}}
    return result

def preservation_audit():
    """Independent full inherited-manifest check with exactly documented exceptions."""
    def sha(path):
        digest=hashlib.sha256()
        with Path(path).open('rb') as stream:
            for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
        return digest.hexdigest()
    old=json.loads(Path('results/research3/manifest.json').read_text())
    older=json.loads(Path('results/research3/inherited_manifest.json').read_text())
    note=json.loads(Path('results/research4/inherited_manifest_exceptions.json').read_text())
    assert sha('results/research3/manifest.json')==note['prior_manifest_sha256']
    allowed={e['path']:e for e in note['exceptions']}
    assert set(allowed)=={'research3/FINAL_REVIEW.md','research3/REPLICATION.md','results/research3/package_gate.log'}
    for path,item in allowed.items():
        current=Path(path).read_bytes();prefix=Path(item['manifest_matching_prefix_copy']).read_bytes()
        original=old['files'][path]
        assert original==item['manifest_record']
        assert len(prefix)==original['bytes'] and hashlib.sha256(prefix).hexdigest()==original['sha256']
        assert current[:len(prefix)]==prefix and len(current)==item['current_bytes']
        assert hashlib.sha256(current).hexdigest()==item['current_sha256']
        assert len(current)-len(prefix)==item['appended_bytes']
    changed={}
    for label,mapping in [('round3',old['files']),('older',older['files'])]:
        mismatches=[]
        for path,item in mapping.items():
            assert Path(path).is_file(),path
            if sha(path)!=item['sha256'] or Path(path).stat().st_size!=item['bytes']:mismatches.append(path)
        changed[label]=sorted(mismatches)
    assert set(changed['round3'])==set(allowed) and not changed['older']
    return {'audited_round3_records':len(old['files']),'audited_older_records':len(older['files']),'actual_mismatches':changed,'prefix_and_exact_current_copy_checks':True,'scope':'Independent full-file hashing; recovered prefixes are present-day reconciliation, not historical prelaunch snapshots. No prior bytes changed by audit.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--policies',default='greedy,population_control');p.add_argument('--seeds',default='101');p.add_argument('--variants',default='development');p.add_argument('--mode',choices=['direct','subprocess'],default='direct');p.add_argument('--reference');p.add_argument('--cluster-audit',action='store_true');p.add_argument('--output',default='results/research4/replication.json');args=p.parse_args()
    seeds=[int(x) for x in args.seeds.split(',')];variants=FAMILIES if args.variants=='all' else args.variants.split(',')
    # Explicit authorization scope, not outcome knowledge: old101 or registered
    # B/C/D/E seed blocks. Nothing else can be generated accidentally.
    assert all(s==101 or 80001<=s<=80012 or 81001<=s<=81032 or 82001<=s<=82020 or 83001<=s<=83160 for s in seeds)
    rows=[replay(name,s,v,args.mode,args.reference) for s in seeds for v in variants for name in args.policies.split(',')]
    obj={'command':sys.argv,'scope':'independent loop and public-event scoring; single-worker replay, no new unregistered seeds','episodes':rows,'source_hashes':{f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in ['kit.py','research/terminal_model.py','research3/policy.py','research3/model_candidates.py','research4/policy.py','research4/candidates.py','research4/independent_replicator.py']}}
    if args.cluster_audit:obj['independent_statistics']=cluster_audit(args.reference)
    target=Path(args.output)
    if target.exists():
        old=json.loads(target.read_text());obj={'runs':old.get('runs',[old])+[obj]}
    target.write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
