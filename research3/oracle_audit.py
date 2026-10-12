"""Privileged diagnostic rollouts on already examined seeds; never policy package.
No seed/outcome reverse engineering. Seeds generate previously examined worlds.
"""
import hashlib
import itertools
import json
import math
import statistics
import time
from pathlib import Path
from kit import HARD, Simulator, baseline_asks, eligibility, generate
from research3.prediction_audit import funnel, interval

FAMILIES=('development','sparse','cold_start','delayed','shift','drift')
LEVELS=('observation_prior','known_parameter_missing','full_truth','full_truth_free_hard')

def rollout(seed,variant,level):
    sim=Simulator(generate(seed,200,'evaluation',variant));truth=sim.members
    expected=0.;oracle_edges=0;means=[];busy_available=[];digest=hashlib.sha256();started=time.process_time()
    for day in range(60):
        if level=='full_truth_free_hard':
            # Altered-information diagnostic: free complete hard disclosure only
            # for arrived actors without any permanent hard decline. No constraints
            # are relaxed and scheduled outcomes/exits remain shipped mechanisms.
            for m in truth.values():
                if m['arrived_day']<=day and not any(m['field_status'][k]=='declined' for k in HARD):
                    for k in HARD:
                        m['fields'][k]=m['truth'][k];m['field_status'][k]='observed';m['field_observed_day'][k]=day
        else:sim.resolve_asks(baseline_asks(sim.observe()))
        state=sim.observe();members=[m for m in state['members'] if m['available']];past={tuple(sorted((i['user_a'],i['user_b']))) for i in state['introductions']};edges=[]
        for a,b in itertools.combinations(members,2):
            pair=tuple(sorted((a['member_id'],b['member_id'])))
            if pair in past or eligibility(a,b)['status']!='feasible':continue
            pa,pb=truth[a['member_id']],truth[b['member_id']]
            if level=='observation_prior':q=funnel(a,b,day)['terminal']
            elif level=='known_parameter_missing':q=funnel(a,b,day,private=(pa,pb,variant))['terminal']
            else:q=funnel(pa,pb,day,private=(pa,pb,variant),truth=True)['terminal']
            edges.append((q,pair))
        used=set();pairs=[]
        for _,pair in sorted(edges,key=lambda x:(-x[0],x[1])):
            if used.intersection(pair):continue
            pairs.append(list(pair));used.update(pair)
            pa,pb=(truth[i] for i in pair);expected+=funnel(pa,pb,day,private=(pa,pb,variant),truth=True)['terminal']
        oracle_edges+=len(edges);means.append(len(edges));busy_available.append(len(members))
        digest.update(json.dumps([day,pairs],sort_keys=True).encode());sim.advance(pairs)
    for _ in range(40):sim.advance([])
    out=sim.metrics();out.update(seed=seed,variant=variant,level=level,expected_qualified_on_chosen_trajectory=expected,expected_msmi100_on_chosen_trajectory=expected/2,positive_pauses=sum(e['event']=='pause_after_mutual_interest' for e in sim.receive_feedback()),mean_current_legal_edges=statistics.mean(means),mean_available=statistics.mean(busy_available),cpu_seconds=time.process_time()-started,action_sha256=digest.hexdigest())
    return out

def main():
    started=time.process_time();rows=[]
    for seed in range(1001,1006):
        for variant in FAMILIES:
            for level in LEVELS:
                rows.append(rollout(seed,variant,level))
    baseline={}
    for seed in range(1001,1006):
        for family in FAMILIES:
            trace=json.loads(Path(f'results/extended/development_traces/greedy_{family}_{seed}.json').read_text())
            feedback=trace['completed_feedback'];count=0
            for intro in trace['introductions']:
                es=[e for e in feedback if e['introduction_id']==intro['introduction_id']];ds=[e for e in es if e['event']=='date_happened' and e['value']];ss=[e for e in es if e['event']=='second_meeting_intention']
                count+=bool(ds) and len(ss)==2 and ds[0]['occurred_day']-intro['assigned_day']<=30 and all(e['value']=='yes' and e['occurred_day']-ds[0]['occurred_day']<=3 for e in ss)
            baseline[(seed,family)]=count/2
    summaries={}
    for level in LEVELS:
        level_rows=[r for r in rows if r['level']==level]
        summaries[level]={key:interval([statistics.mean(r[key] for r in level_rows if r['seed']==seed) for seed in range(1001,1006)]) for key in ('msmi_per_100_arrived_members','expected_msmi100_on_chosen_trajectory','assignments','positive_pauses')}
        summaries[level]['realized_minus_shipped_greedy']=interval([statistics.mean(r['msmi_per_100_arrived_members']-baseline[(seed,r['variant'])] for r in level_rows if r['seed']==seed) for seed in range(1001,1006)])
    result={'scope':'privileged diagnostic policies, old1001--1005 five seed clusters x6 families x4 levels; exploratory; not candidate selection, deployable performance, or dynamic upper bounds','information':{'observation_prior':'disclosed JSON observations and fixed public family prior only; current-greedy scoring; numerical15-node quadrature may differ from frozen5-node candidate','known_parameter_missing':'knows true actor bias/second_bias/response propensity and family; missing soft equalities integrated uniformly; ignores feedback posterior for missing features','full_truth':'also knows undisclosed soft truth; legal graph still requires disclosed hard fields','full_truth_free_hard':'also supplies free hard disclosure on arrival for every actor with no permanent hard decline; altered information/query cost, same constraints and legal graph checks; no future outcome draw access'},'limitations':'A stronger informational level can have worse realized reward, and greedy full-truth score need not optimize dynamic value. Expected current-edge probabilities summed on adaptively chosen observed trajectories are a diagnostic; sample averaging has only5 clusters. Action changes move pair/day hash streams, so downstream common random numbers are incomplete. No policy sees future arrivals, exits, schedules, pair Gaussian or Bernoulli draws.','rows':rows,'summary':summaries,'cpu_seconds':time.process_time()-started}
    Path('results/research3/oracles.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'cpu_seconds':result['cpu_seconds'],'summary':summaries},indent=2))
if __name__=='__main__':main()
