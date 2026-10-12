"""Exact rational small-market DP, counterexamples and old-data learning audit.
Run: python3 -m research3.tiny_models
No new full-simulator episodes; no confirmation/truth data are read.
"""
import functools
import itertools
import json
import math
from fractions import Fraction as F
from pathlib import Path
from research3.model_candidates import features, population

def matchings(edges):
    out = [()]
    for edge in sorted(edges):
        out += [old+(edge,) for old in list(out) if not set(edge).intersection(i for e in old for i in e)]
    return out

def exact_dp(n, horizon, schedule):
    """Known deterministic edge schedules; Bernoulli success retires endpoints.

    Failure consumes an edge-specific known duration, dyads cannot repeat, and
    success grants unit reward. Rational independence is explicit; this is not
    the shipped four-stage hidden-state simulator.
    """
    @functools.lru_cache(None)
    def solve(day,busy,retired,past):
        if day >= horizon:
            return F(0), ()
        edges = {e: x for e,x in schedule.get(day,{}).items() if e not in past and not set(e)&set(retired) and all(busy[i] <= day for i in e)}
        best = (F(-1), ())
        for action in matchings(edges):
            value = F(0)
            for flags in itertools.product((0,1), repeat=len(action)):
                probability = F(1); new_busy=list(busy); new_ret=set(retired)
                for edge, success in zip(action,flags):
                    q,duration=edges[edge]
                    probability *= q if success else 1-q
                    if success:
                        new_ret.update(edge)
                    else:
                        for i in edge:new_busy[i]=day+duration
                tail,_=solve(day+1,tuple(new_busy),tuple(sorted(new_ret)),tuple(sorted(set(past)|set(action))))
                value += probability*(sum(flags)+tail)
            if value > best[0]:best=(value,action)
        return best
    value,action=solve(0,(0,)*n,(),())
    return {'expected_reward':str(value),'first_action':[list(e) for e in action],'states':solve.cache_info().currsize}

def cases():
    p={(0,1):(F(1,10),8),(1,2):(F(11,100),8),(2,3):(F(1,10),8)}
    weighted={(0,1):(F(9,10),8),(0,2):(F(1,10),8),(1,3):(F(1,10),8)}
    throughput={(0,1):(F(1,5),8),(0,2):(F(3,10),20)}
    wait={0:{(0,1):(F(1,10),8)},1:{(0,2):(F(9,10),8)}}
    result={
      'greedy_cardinality_path':{'exact':exact_dp(4,1,{0:p}),'greedy_reward':'11/100','maximum_cardinality_reward':'1/5','claim_refuted':'largest immediate edge gives best matching'},
      'scarcity_weight_tradeoff':{'exact':exact_dp(4,1,{0:weighted}),'scarce_reward':'1/5','claim_refuted':'minimum-degree-first always improves reward'},
      'throughput_last_day':{'exact':exact_dp(3,1,{0:throughput}),'ratio_reward':'1/5','claim_refuted':'reward per busy day is a universal finite-horizon edge ordering'},
      'waiting_future_arrival':{'exact':exact_dp(3,2,wait),'immediate_reward':'1/10','claim_refuted':'introducing any currently legal positive edge is optimal'},
    }
    # Two-day retry case. AB is low-value but leaves AC available after a failure.
    retry={0:{(0,1):(F(1,5),1)},1:{(0,2):(F(4,5),1)}}
    result['retry_option']={'exact':exact_dp(3,2,retry),'wait_reward':'4/5','immediate_then_retry_reward':'21/25','claim_supported_only_in_specified_model':'short occupancy can make present low-probability attempts useful'}
    return result

def fit_audit():
    """Strongly shrunk direct terminal logistic; old cohort train/validation split.

    These are assignment-time equality features, not truth. No scenario string
    enters predictors. Empirical conditional expectation model, not the invalid
    substitution sigmoid(E[mechanistic latent logit]). No mechanistic equality
    is claimed for its predictions; proper-score validation tests that choice.
    """
    import numpy as np
    from scipy.optimize import minimize
    data=json.loads(Path('results/extended/audit_common_cohort_calibration.json').read_text())['assignment_rows']
    train=[r for r in data if 1001<=r['seed']<=1005]
    validation=[r for r in data if 1006<=r['seed']<=1008]
    def arrays(rows):
        return np.array([features(r['snapshot']['member_a'],r['snapshot']['member_b'],r['assigned_day']) for r in rows]), np.array([r['label']['terminal'] for r in rows])
    X,y=arrays(train)
    # Prelisted ridge penalty; only intercept anchored to 1% rare-event rate.
    anchor=np.array([math.log(.01/.99),0,0,0,0,0])
    penalty=np.array([2.,25.,25.,25.,25.,25.])
    def objective(w):
        z=X@w
        loss=np.logaddexp(0,z).sum()-y@z+.5*np.sum(penalty*(w-anchor)**2)
        p=1/(1+np.exp(-z))
        gradient=X.T@(p-y)+penalty*(w-anchor)
        return loss,gradient
    fit=minimize(objective,anchor,jac=True,method='BFGS',options={'gtol':1e-8,'maxiter':150})
    w=fit.x
    def metrics(rows):
        Z,Y=arrays(rows);learned=1/(1+np.exp(-(Z@w)))
        mech=np.array([population(r['snapshot']['member_a'],r['snapshot']['member_b'],r['assigned_day'])[0] for r in rows])
        def proper(p, labels=None):
            labels = Y if labels is None else labels
            p=np.clip(p,1e-9,1-1e-9)
            return {'predicted_mean':float(p.mean()),'observed_mean':float(labels.mean()),'log_loss':float(-(labels*np.log(p)+(1-labels)*np.log1p(-p)).mean()),'brier':float(((p-labels)**2).mean())}
        return {'n':len(rows),'positive':int(Y.sum()),'offline':proper(learned),'population':proper(mech),'constant_training_rate':proper(np.full(len(rows),y.mean())), 'per_seed':{str(seed): {'n':sum(r['seed']==seed for r in rows), 'offline':proper(learned[np.array([r['seed']==seed for r in rows])],Y[np.array([r['seed']==seed for r in rows])]), 'population':proper(mech[np.array([r['seed']==seed for r in rows])],Y[np.array([r['seed']==seed for r in rows])])} for seed in sorted(set(r['seed'] for r in rows))}}
    return {'scope':'old selected baseline cohort, assignment-weighted descriptive audit; no new untouched seeds','train_seeds':list(range(1001,1006)),'validation_seeds':list(range(1006,1009)),'features':['intercept','goal_eq-.5','pace_eq-1/3','lifestyle_eq-1/3','conversation_eq-.25','day>=35'],'penalty':penalty.tolist(),'weights':w.tolist(),'optimizer_success':bool(fit.success),'gradient_max':float(np.abs(objective(w)[1]).max()),'train':metrics(train),'validation':metrics(validation),'coverage_limitation':'baseline selected actions only; no propensity logging; no counterfactual policy-value estimate'}

def main():
    result={'exact_simplified_models':cases(),'offline_learning':fit_audit()}
    Path('results/research3').mkdir(parents=True,exist_ok=True)
    Path('results/research3/tiny_models.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))
def score_ordering():
    """Reproduce the finite frozen-score domain audit without full episodes."""
    from datetime import datetime, timezone
    import time
    from research3.model_candidates import FEATURES, score_edge, OFFLINE_WEIGHTS
    started=datetime.now(timezone.utc).isoformat();cpu=time.process_time();output=[]
    for day in (0,40):
        rows=[]
        for pattern in itertools.product((0,'missing',1),repeat=4):
            a={'member_id':'a','fields':{k:'a' for k in FEATURES}}
            b={'member_id':'b','fields':{k:('a' if v==1 else 'b' if v==0 else None) for k,v in zip(FEATURES,pattern)}}
            rows.append({'pattern':list(pattern),'population':score_edge(a,b,{'day':day},'population'),'throughput':score_edge(a,b,{'day':day},'throughput')})
        inversions=[];ties=[];minimum=float('inf')
        for a,b in itertools.combinations(rows,2):
            q=a['population']-b['population'];v=a['throughput']-b['throughput']
            if q:minimum=min(minimum,abs(q))
            if q*v<0:inversions.append({'a':a,'b':b})
            if (q==0)!=(v==0):ties.append({'a':a,'b':b})
        output.append({'day':day,'rows':rows,'inversions':inversions,'tie_mismatches':ties,'min_nonzero_q_separation':minimum})
    path=Path('results/research3/score_ordering.json')
    if path.exists():
        previous=json.loads(path.read_text());assert previous['days']==output
    else:
        path.write_text(json.dumps({'started_utc':started,'cpu_seconds':time.process_time()-cpu,'scope':'All81observableequalitypatterns xpre/post35day, executedfloat/quadraturescores not exact probabilities','all_pair_orders_and_ties_identical':all(not d['inversions'] and not d['tie_mismatches'] for d in output),'days':output,'offline_weights':OFFLINE_WEIGHTS},indent=2,sort_keys=True)+'\n')
    print(json.dumps({'verified_existing_output':path.exists(),'days':[(r['day'],len(r['inversions']),len(r['tie_mismatches'])) for r in output],'cpu_seconds':time.process_time()-cpu}))

if __name__=='__main__':
    import sys
    if '--score-ordering' in sys.argv:score_ordering()
    else:main()

