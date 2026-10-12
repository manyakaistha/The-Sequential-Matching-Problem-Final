"""Degree versus hard-field entropy versus optimistic global lambda_2 expansion.
The spectral score adds every not-yet-contradicted edge to verified neighbors as an
optimistic query outcome; no hidden fields are used by this allocator.
"""
from concurrent.futures import ProcessPoolExecutor
import itertools
import json
import math
import collections
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import networkx as nx
import numpy as np
import evaluate
from kit import HARD,generate,eligibility
from research_policy import DEFAULT,blocked,verified,update,ask_actions,match_actions

def hard_entropy(m):
    """Exact generated prior entropy of semantic hard fields given age/zone.
    Preference and schedule sets ignore presentation order; independent fields
    make the bundle's conditional joint entropy additive in this public model.
    """
    def entropy(ps): return -sum(p*math.log2(p) for p in ps if p)
    age_min=collections.Counter(max(18,m['age']-d) for d in range(3,11))
    values={
        'age_min':entropy([n/8 for n in age_min.values()]), 'age_max':3.,
        'who_to_meet':entropy([.7/3]*3+[.2/3]*3+[.1]),
        'relationship_structure':entropy([.9,.1]),
        'smoking':entropy([.75,.2,.05]), 'partner_smoking':1.,
        'has_children':entropy([.15,.85]), 'partner_children':1.,
        'wants_children':math.log2(3),
        'acceptable_zones':entropy([.775,.075,.075,.075]) if m['zone'] in ('zone_a','zone_b','zone_c','zone_d') else 0.,
        'schedule':entropy([1/9]*6+[1/3]),
    }
    return sum(values[k] for k in HARD if m['fields'].get(k) is None)

def alternate_asks(state,mem,method):
    if method=='degree':return ask_actions(state,mem,DEFAULT)
    active=[m for m in state['members'] if m['available'] and not blocked(m)]
    candidates=[m for m in active if not verified(m)]
    budget=int(state['ask_budget_remaining']);out=[];selected=set()
    graph=nx.Graph();graph.add_nodes_from(m['member_id'] for m in active)
    for a,b in itertools.combinations(active,2):
        if eligibility(a,b)['status']=='feasible':graph.add_edge(a['member_id'],b['member_id'])
    def lambda2(g):
        if len(g)<2 or not nx.is_connected(g):return 0.
        lap=nx.laplacian_matrix(g).toarray();return float(np.linalg.eigvalsh(lap)[1])
    while budget>=3 and candidates:
        scores=[];base=lambda2(graph)
        for m in candidates:
            if method=='entropy':
                value=hard_entropy(m)
                optimistic=None
            else:
                optimistic=graph.copy()
                for n in active:
                    if (verified(n) or n['member_id'] in selected) and eligibility(m,n)['status']!='infeasible' and m['member_id']!=n['member_id']:
                        optimistic.add_edge(m['member_id'],n['member_id'])
                value=lambda2(optimistic)-base
            scores.append((value,m['member_id'],m,optimistic))
        value,ident,m,g=max(scores,key=lambda x:(x[0],x[1]));out.append(dict(member_id=ident,field='constraints'));selected.add(ident);budget-=3;candidates.remove(m)
        if g is not None:graph=g
    # Same verified-only soft fill for fair leftover comparison.
    soft_state=dict(state,ask_budget_remaining=budget)
    out.extend(ask_actions(soft_state,mem,dict(DEFAULT,asks='soft')))
    return out

def run(job):
    method,variant,seed=job;real=evaluate.invoke;peak=0
    def invoke(command,request,timeout=10):
        nonlocal peak
        start=time.perf_counter();request=json.loads(json.dumps(request));state=request['state'];mem=update(state,request.get('memory'),DEFAULT)
        key='asks' if request['phase']=='ask' else 'pairs'
        actions=alternate_asks(state,mem,method) if key=='asks' else match_actions(state,mem,DEFAULT)
        response=evaluate.validate_response(json.loads(json.dumps({key:actions,'memory':mem})),request['phase']);elapsed=time.perf_counter()-start;peak=max(peak,elapsed)
        return response,elapsed
    evaluate.invoke=invoke
    try:
        r=evaluate.episode(generate(seed,200,'evaluation',variant),[])
        r.update(policy='query_'+method,variant=variant,seed=seed,mean_inference_ms=1000*r['inference_seconds']/120,
                 mutual_acceptance_rate=r['mutual_acceptances']/max(1,r['assignments']),date_completion_rate=r['dates']/max(1,r['mutual_acceptances']),peak_latency_seconds=peak)
        return r
    finally:evaluate.invoke=real
if __name__=='__main__':
    jobs=[(m,v,s) for m in ('degree','entropy','spectral') for v in evaluate.VARIANTS for s in range(101,106)];rows=[]
    with ProcessPoolExecutor(max_workers=2) as pool:
        for r in pool.map(run,jobs):
            rows.append(r);Path('results/research/query_comparison.json').write_text(json.dumps({'episodes':rows,'complete':len(rows)==len(jobs)},indent=2)+'\n');print(r['policy'],r['variant'],r['seed'],flush=True)
