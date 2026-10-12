"""Independent direct simulator loop and seed-cluster reward reconstruction.
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
    import research3.policy as policy
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
                child=subprocess.run([sys.executable,'-m','research3.policy','--candidate',name],input=encoded,capture_output=True,timeout=10)
                assert child.returncode==0 and len(child.stdout)<=LIMIT and len(child.stderr)<=LIMIT
                fallbacks+=child.stderr.count(b'round3 fallback:')
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
    seeds=set(groups['greedy']);assert all(set(ss)==seeds for ss in groups.values())
    assert all(set(v)==set(FAMILIES) for ss in groups.values() for v in ss.values())
    means={p:{s:sum(v.values())/6 for s,v in ss.items()} for p,ss in groups.items()}
    out={}
    for p,values in means.items():
        d=[values[s]-means['greedy'][s] for s in sorted(seeds)];m=statistics.mean(d);sd=statistics.stdev(d) if len(d)>1 else 0
        err=float(t.ppf(.975,len(d)-1))*sd/math.sqrt(len(d)) if len(d)>1 else None
        out[p]={'n':len(d),'mean':statistics.mean(values.values()),'paired_difference':m,'paired_sd':sd,'ci95':[m-err,m+err] if err is not None else None,'p_two_sided':float(2*t.sf(abs(m)/(sd/math.sqrt(len(d))),len(d)-1)) if sd else None}
    return {'source':reference,'clusters':out,'method':'independent six-family seed average and paired t; no director analysis imports'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--policies',default='greedy,clean');p.add_argument('--seeds',default='101');p.add_argument('--variants',default='development');p.add_argument('--mode',choices=['direct','subprocess'],default='direct');p.add_argument('--reference');p.add_argument('--cluster-audit',action='store_true');p.add_argument('--output',default='results/research3/replication.json');args=p.parse_args()
    seeds=[int(x) for x in args.seeds.split(',')];variants=FAMILIES if args.variants=='all' else args.variants.split(',')
    # Explicit authorization scope, not outcome knowledge: old101 or registered
    # B/C/D/E seed blocks. Nothing else can be generated accidentally.
    assert all(s==101 or 70001<=s<=70012 or 71001<=s<=71032 or 72001<=s<=72020 or 73001<=s<=73160 for s in seeds)
    rows=[replay(name,s,v,args.mode,args.reference) for s in seeds for v in variants for name in args.policies.split(',')]
    obj={'command':sys.argv,'scope':'independent loop and public-event scoring; single-worker replay, no new unregistered seeds','episodes':rows,'source_hashes':{f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in ['kit.py','research3/policy.py','research3/model_candidates.py','research3/independent_replicator.py']}}
    if args.cluster_audit:obj['independent_statistics']=cluster_audit(args.reference)
    target=Path(args.output)
    if target.exists():
        old=json.loads(target.read_text());obj={'runs':old.get('runs',[old])+[obj]}
    target.write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
