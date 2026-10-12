"""Counterfactual public-state diversity stress; never fresh seeds or private labels."""
import argparse,contextlib,hashlib,io,json,resource,sys,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import evaluate
from kit import HARD,Simulator,generate,eligibility
from research4 import policy
from research4.production import captured_invoke
from research3.model_candidates import response_counts

def fixture():
    sim=Simulator(generate(101,200,'evaluation'));sim.day=20;s=sim.observe();s['day']=59
    fields=dict(age_min=18,age_max=65,who_to_meet=['man'],relationship_structure='monogamous',smoking='no',partner_smoking='any',has_children=False,partner_children='any',wants_children='unsure',acceptable_zones=['zone_a'],schedule=['weekend_day'])
    soft=dict(relationship_goal=['long_term','exploring'],relationship_pace=['slow','steady','quick'],lifestyle=['quiet','mixed','social'],conversations=['ideas','stories','practical','playful'])
    for i,m in enumerate(s['members']):
        m.update(age=30,gender='man',zone='zone_a',available=True);m['fields'].update(fields)
        for k in HARD:m['field_status'][k]='observed';m['field_observed_day'][k]=0
        for n,(k,values) in enumerate(soft.items()):
            m['fields'][k]=None if (i+3*n)%13==0 else values[(i//(n+1)+n)%len(values)]
            m['field_status'][k]='unobserved' if m['fields'][k] is None else 'observed'
    ids=[m['member_id'] for m in s['members']];s['introductions']=[];s['feedback']=[]
    for i,ident in enumerate(ids):
        for j in range(i%7):
            intro='heterogeneous_'+str(i)+'_'+str(j);other=ids[(i+j+1)%len(ids)]
            s['introductions'].append(dict(introduction_id=intro,user_a=ident,user_b=other,assigned_day=34+(i+j)%3))
            # Reused response mechanism: None is explicit nonresponse; no/yes both responded.
            label=(None,'no','yes','yes')[(i+2*j)%4]
            s['feedback'].append(dict(introduction_id=intro,member_id=ident,event='introduction_response',value=label,observed_day=45))
    return s

def legality(response,state):
    by_id={m['member_id']:m for m in state['members']};past={tuple(sorted((i['user_a'],i['user_b']))) for i in state['introductions']};used=set()
    for p in response['pairs']:
        if used.intersection(p) or tuple(sorted(p)) in past or eligibility(*(by_id[i] for i in p))['status']!='feasible':return False
        used.update(p)
    return True

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--image',default='sequential-round4:research');a=p.parse_args();target=Path(a.output)
    if target.exists():raise ValueError('refuse overwrite')
    utc=datetime.now(timezone.utc).isoformat();start=time.monotonic();self0=resource.getrusage(resource.RUSAGE_SELF);child0=resource.getrusage(resource.RUSAGE_CHILDREN)
    s=fixture();request=dict(phase='match',state=s,memory={'corrupt':'ignored'});rows=[]
    for name,cfg in policy.CANDIDATES.items():
        before=policy.FALLBACK_COUNT;started=time.monotonic()
        with contextlib.redirect_stderr(io.StringIO()) as captured:direct=policy.decide(request,cfg)
        direct_seconds=time.monotonic()-started;direct_stderr=captured.getvalue()
        try:
            container,seconds,stderr=captured_invoke(evaluate.docker_command(a.image)+['--candidate',name],request)
            error=None
        except Exception as e:
            container=None;seconds=None;stderr='';error=type(e).__name__+': '+str(e)
        fallback=policy.FALLBACK_COUNT-before;child_fallbacks=stderr.count('round4 fallback:')
        row=dict(candidate=name,direct_seconds=direct_seconds,container_seconds=seconds,direct_fallback_count=fallback,container_fallback_warning_count=child_fallbacks,direct_stderr=direct_stderr,container_stderr=stderr,error=error,exact_response_equal=container==direct,legal_direct=legality(direct,s),legal_container=legality(container,s) if container else False,direct_pairs=len(direct['pairs']),container_pairs=len(container['pairs']) if container else None,request_bytes=len(json.dumps(request).encode()),memory_bytes=len(json.dumps(direct['memory']).encode()))
        row['optimized_pass']=row['exact_response_equal'] and row['legal_direct'] and row['legal_container'] and not fallback and not child_fallbacks and not error
        rows.append(row);print(json.dumps(row),flush=True)
    self1=resource.getrusage(resource.RUSAGE_SELF);child1=resource.getrusage(resource.RUSAGE_CHILDREN)
    counts=response_counts(s);summaries=Counter(tuple(counts.get(m['member_id'],(0,0))) for m in s['members'])
    out=dict(scope='Synthetic counterfactual 200endpoint dense hardverified public observation; varied soft fields and response/acceptance histories. Partial constructed event logs need not correspond to a complete legal simulator trajectory. Finite stress, no universal guarantee.',rows=rows,all_optimized_pass=all(r['optimized_pass'] for r in rows),public_state_sha256=hashlib.sha256(json.dumps(s,sort_keys=True).encode()).hexdigest(),members=len(s['members']),public_feedback_events=len(s['feedback']),public_label_counts=dict(Counter(str(e['value']) for e in s['feedback'])),response_history_counts={str(k):v for k,v in sorted(summaries.items())},wall_seconds=time.monotonic()-start,compute=dict(started_utc=utc,host_self_cpu_seconds=self1.ru_utime+self1.ru_stime-self0.ru_utime-self0.ru_stime,host_children_cpu_seconds=child1.ru_utime+child1.ru_stime-child0.ru_utime-child0.ru_stime,docker_daemon_container_cpu_seconds=None),command=[sys.executable,'-m','research4.test_diverse']+sys.argv[1:],source_hashes={q:hashlib.sha256(Path(q).read_bytes()).hexdigest() for q in ('research4/policy.py','research4/candidates.py','research4/test_diverse.py')})
    target.write_text(json.dumps(out,indent=2)+'\n')
    with Path('results/research4/commands_production.jsonl').open('a') as f:f.write(json.dumps(dict(command=out['command'],output=str(target),compute=out['compute'],wall_seconds=out['wall_seconds']))+'\n')
if __name__=='__main__':main()
