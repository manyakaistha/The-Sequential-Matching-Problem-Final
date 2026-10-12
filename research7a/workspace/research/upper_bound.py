"""Offline time-indexed expected-capacity LP, deliberately optimistic upper bound.
Reveals non-declined constraints free, ignores retirement and long busy times.
Rewards computed from hidden parameters only here, never inside policy.
"""
import itertools
import json
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from kit import generate,eligibility,HARD
from research.audit import exact_delay
from research_policy import blocked

def bound(seed,variant):
    world=generate(seed,200,'evaluation',variant);ms=[m for m in world['members'] if not blocked(m)]
    edges=[]
    nodes,weights=np.polynomial.hermite.hermgauss(32);shared=np.sqrt(2)*.45*nodes;weights=weights/math.sqrt(math.pi)
    sigmoid=lambda z:1/(1+np.exp(-z))
    late=exact_delay(variant=='delayed')['late_date_probability']
    for a,b in itertools.combinations(ms,2):
        if eligibility(dict(a,fields=a['truth']),dict(b,fields=b['truth']))['status']!='feasible':continue
        wa=[.25,.8,-.25,.5] if variant=='shift' else [.7,.4,.25,.2]
        fit=sum(w*(1 if a['truth'][k]==b['truth'][k] else -.5) for w,k in zip(wa,('relationship_goal','relationship_pace','lifestyle','conversations')))
        goal=a['truth']['relationship_goal']==b['truth']['relationship_goal']
        def reward(drift):
            p=sigmoid(-.25+a['bias']+fit+shared+drift)*sigmoid(-.25+b['bias']+fit+shared+drift)
            second=sigmoid(.15+a['second_bias']+shared+.4*goal)*sigmoid(.15+b['second_bias']+shared+.4*goal)
            return float(weights@(p*second))*.78*.36*(a['response_rate']*b['response_rate'])**2*(1-late)
        edges.append((a,b,reward(0),reward(-.5)))
    variables=[];rewards=[]
    for e,(a,b,q,qdrift) in enumerate(edges):
        for t in range(max(a['arrived_day'],b['arrived_day']),min(60,a['exit_day'],b['exit_day'])):
            variables.append((e,t));rewards.append(qdrift if variant=='drift' and t>=35 else q)
    index={m['member_id']:j for j,m in enumerate(ms)};rr=[];cc=[];vv=[]
    # Each pair at most once; each member locked at least 8 days for every assignment.
    for c,(e,t) in enumerate(variables):
        rr.append(e);cc.append(c);vv.append(1)
        a,b,*_=edges[e]
        for m in (a,b):
            for day in range(t,min(60,t+8)):
                rr.append(len(edges)+60*index[m['member_id']]+day);cc.append(c);vv.append(1)
    if not variables:return dict(seed=seed,variant=variant,bound_msmi_per100=0)
    mat=coo_matrix((vv,(rr,cc)),shape=(len(edges)+60*len(ms),len(variables))).tocsr()
    solution=linprog(-np.array(rewards),A_ub=mat,b_ub=np.ones(mat.shape[0]),bounds=(0,1),method='highs')
    return dict(seed=seed,variant=variant,success=solution.success,variables=len(variables),edges=len(edges),
                bound_msmi_per100=-solution.fun/2 if solution.success else None,
                caveat='Expected reward upper bound, not a pathwise bound on stochastic realized MSMI; quadrature numerically approximates rewards.')
if __name__=='__main__':
    rows=[bound(101,v) for v in ('development','sparse','cold_start','delayed','shift','drift')]
    Path('results/research/upper_bound.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps(rows,indent=2))
