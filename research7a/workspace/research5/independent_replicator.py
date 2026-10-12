"""Independent direct simulator loop and seed-cluster reward reconstruction.
Adapted independently owned round4 request loop/public scorer to round5 verification.
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
                assert child.returncode==0 and len(child.stdout)<=LIMIT and len(child.stderr)<=LIMIT, {"returncode":child.returncode,"stdout":child.stdout[:2048].decode(errors="replace"),"stderr":child.stderr[:2048].decode(errors="replace")}
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
        data=REFERENCE_DATA if REFERENCE_DATA is not None else json.loads(Path(reference).read_text())
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

REFERENCE_DATA=None

def main():
    import resource, traceback
    from datetime import datetime,timezone
    global REFERENCE_DATA
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['direct','subprocess'],required=True);p.add_argument('--output',required=True);args=p.parse_args()
    target=Path(args.output);assert not target.exists(),'refuse overwrite'
    reference='results/research5/confirmation.json';REFERENCE_DATA=json.loads(Path(reference).read_text())
    design=json.loads(Path('results/research5/design.json').read_text());assert REFERENCE_DATA['complete']
    assert REFERENCE_DATA['code_hashes']==design['frozen_inherited_hashes']
    for path,h in design['frozen_inherited_hashes'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h,path
    sources=['kit.py','research/terminal_model.py','research3/policy.py','research3/model_candidates.py','research4/policy.py','research4/candidates.py',__file__]
    before={f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in sources}
    start=time.process_time();wall=time.monotonic();child=resource.getrusage(resource.RUSAGE_CHILDREN)
    obj={'command':sys.argv,'started_utc':datetime.now(timezone.utc).isoformat(),'scope':'Independent request loop/public reward scoring; approved existing90001/90002 all6families bothpolicies only; no new confirmation sample','source_hashes':before,'reference_sha256':hashlib.sha256(Path(reference).read_bytes()).hexdigest(),'episodes':[],'complete':False}
    def save():target.write_text(json.dumps(obj,indent=2)+'\n')
    save()
    for seed in (90001,90002):
        for variant in FAMILIES:
            for name in ('greedy','population_control'):
                try:row=replay(name,seed,variant,args.mode,reference)
                except Exception as error:row={'policy':name,'seed':seed,'variant':variant,'execution':args.mode,'valid':False,'error_type':type(error).__name__,'error':str(error),'traceback':traceback.format_exc()}
                obj['episodes'].append(row);save()
                print(json.dumps({k:row.get(k) for k in ('policy','seed','variant','execution','valid','fallback_count','byte_digest_match','metric_differences')}),flush=True)
    end=resource.getrusage(resource.RUSAGE_CHILDREN)
    obj.update(complete=True,completed_utc=datetime.now(timezone.utc).isoformat(),self_cpu_seconds=time.process_time()-start,os_child_cpu_seconds=end.ru_utime+end.ru_stime-child.ru_utime-child.ru_stime,wall_seconds=time.monotonic()-wall,source_hashes_after={f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in sources})
    obj['source_bytes_unchanged']=obj['source_hashes_after']==before;save()
    good=all(r.get('valid') and not r.get('fallback_count') and not r.get('metric_differences') and all(r.get(k) for k in ('byte_digest_match','semantic_digest_match','ordered_actions_equal','semantic_actions_equal')) for r in obj['episodes'])
    assert good and obj['source_bytes_unchanged'],'Verification discrepancies retained in output'
    print(json.dumps({k:obj[k] for k in ('self_cpu_seconds','os_child_cpu_seconds','wall_seconds','source_bytes_unchanged')}))
if __name__=='__main__':main()
