"""Completed simulator funnels, offline counterfactual feature interventions.
Policy decisions observe public JSON only. Hidden truth used ONLY for scientific audit.
"""
import collections
from concurrent.futures import ProcessPoolExecutor
import itertools
import json
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from kit import Simulator,generate,eligibility,baseline_asks,baseline_match
from research_policy import decide,FEATURES
from research.audit import survival,distribution

def run(job):
    name,variant,seed=job;sim=Simulator(generate(seed,200,'evaluation',variant));memory=None;daily=[]
    for day in range(60):
        state=sim.observe()
        if name=='greedy':asks=baseline_asks(state)
        else:
            response=decide(dict(state=state,phase='ask',memory=memory),{'fusion':'product'} if name=='product' else {})
            memory=response['memory'];asks=response['asks']
        sim.resolve_asks(asks);state=sim.observe()
        if name=='greedy':pairs=baseline_match(state)
        else:
            response=decide(dict(state=state,phase='match',memory=memory),{'fusion':'product'} if name=='product' else {})
            memory=response['memory'];pairs=response['pairs']
        daily.append(dict(day=day,assignments=len(pairs),asks=sum(3 if a['field']=='constraints' else 1 for a in asks)))
        sim.advance(pairs)
    for _ in range(40):sim.advance([])
    es=collections.defaultdict(list)
    for e in sim.events:es[e['introduction_id']].append(e)
    rows=[];records=collections.defaultdict(list);yesboth=late_date=late_feedback=bothlate=0;busy=[]
    for i in sim.introductions:
        events=es[i['introduction_id']];rs=[e for e in events if e['event']=='introduction_response'];ds=[e for e in events if e['event']=='date_happened'];ss=[e for e in events if e['event']=='second_meeting_intention']
        rows.append(tuple(int(e['value']=='yes') for e in sorted(rs,key=lambda e:e['member_id'])))
        for e in rs:records['assignment_to_response'].append((e['observed_day']-i['assigned_day'],1 if e['value'] is not None else 2))
        rdays=sorted(e['occurred_day'] for e in rs if e['occurred_day'] is not None)
        if rdays:
            if len(rdays)==2:records['first_to_second_response'].append((rdays[1]-rdays[0],1))
            else:records['first_to_second_response'].append((max(e['observed_day'] for e in rs)-rdays[0],2))
        busy.append(ds[0]['occurred_day']-i['assigned_day']+6 if ds else 8)
        if ds:
            start=max(e['occurred_day'] for e in rs)
            records['mutual_acceptance_to_date'].append((ds[0]['occurred_day']-start,1 if ds[0]['value'] else 2))
        if ds and ds[0]['value']:
            for e in ss:records['date_to_feedback'].append((e['observed_day']-ds[0]['occurred_day'],1 if e['value'] is not None else 2))
            if len(ss)==2 and all(e['value']=='yes' for e in ss):
                yesboth+=1;a=ds[0]['occurred_day']-i['assigned_day']>30;b=any(e['occurred_day']-ds[0]['occurred_day']>3 for e in ss)
                late_date+=a;late_feedback+=b;bothlate+=a and b
    return dict(policy=name,variant=variant,seed=seed,metrics=sim.metrics(),daily=daily,
                acceptance=distribution(rows),observed_both_second_yes=yesboth,late_date=late_date,late_feedback=late_feedback,both_late=bothlate,
                busy_mean=float(np.mean(busy)) if busy else 0,busy_max=max(busy,default=0),survival={k:survival(v) for k,v in records.items()},
                final_weights=memory.get('weights') if memory else None)

def interventions():
    z,w=np.polynomial.hermite.hermgauss(24);z=z*math.sqrt(2)*.45;w=w/math.sqrt(math.pi);sigmoid=lambda x:1/(1+np.exp(-x));out={}
    for variant in ('development','shift'):
        coeff=[.7,.4,.25,.2] if variant=='development' else [.25,.8,-.25,.5];effects=collections.defaultdict(list);interactions=[];n=0
        for seed in range(201,206):
            world=generate(seed,200,'intervention',variant)
            for a,b in itertools.combinations(world['members'],2):
                if eligibility(dict(a,fields=a['truth']),dict(b,fields=b['truth']))['status']!='feasible':continue
                n+=1;equal=[a['truth'][k]==b['truth'][k] for k in FEATURES]
                def q(eq):
                    fit=sum(ww*(1 if e else -.5) for ww,e in zip(coeff,eq));p=sigmoid(-.25+a['bias']+fit+z)*sigmoid(-.25+b['bias']+fit+z)
                    second=sigmoid(.15+a['second_bias']+z+.4*eq[0])*sigmoid(.15+b['second_bias']+z+.4*eq[0])
                    return float(w@(p*second))*.78*.36*(a['response_rate']*b['response_rate'])**2
                for j,k in enumerate(FEATURES):
                    x=equal.copy();x[j]=True;y=equal.copy();y[j]=False;effects[k].append(q(x)-q(y))
                vals={}
                for pace,conv in itertools.product((False,True),repeat=2):
                    eq=equal.copy();eq[1]=pace;eq[3]=conv;vals[pace,conv]=q(eq)
                interactions.append(vals[True,True]-vals[True,False]-vals[False,True]+vals[False,False])
        out[variant]=dict(feasible_pairs=n,mean_terminal_probability_effect={k:float(np.mean(v)) for k,v in effects.items()},
                          conversations_pace_mean_probability_interaction=float(np.mean(interactions)),
                          caveat='Causal intervention within synthetic structural model, not real-world or snapshot causal evidence. Numeric Gaussian quadrature; all other latent attributes fixed.')
    return out
if __name__=='__main__':
    jobs=[(p,v,s) for p in ('greedy','full','product') for v in ('development','sparse','cold_start','delayed','shift','drift') for s in range(101,106)]
    with ProcessPoolExecutor(max_workers=2) as pool:rows=list(pool.map(run,jobs))
    out=dict(episodes=rows,feature_interventions=interventions())
    Path('results/research/funnel_audit.json').write_text(json.dumps(out,indent=2)+'\n');print('Completed',len(rows),'funnel audits')
