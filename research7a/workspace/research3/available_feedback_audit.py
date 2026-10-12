"""Offline invariant replay and exact response-posterior diagnostic.
All worlds are old seeds1001--1008. Hidden scheduled events only audit availability.
No evaluated model source is changed or supplied with private values.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from fractions import Fraction as F
import functools
import hashlib
import json
import math
from pathlib import Path
import sys
import time
from kit import Simulator, generate

A,B=F(11,20),F(49,50)
MU=(A+B)/2;VAR=(B-A)**2/12;CONC=MU*(1-MU)/VAR-1
ALPHA,BETA=MU*CONC,(1-MU)*CONC

@functools.lru_cache(None)
def integral(s,f,k=0):
    # Polynomial integrals with exact rational endpoints; no cancellation loss.
    return sum(((-1)**i)*math.comb(f,i)*(B**(s+i+k+1)-A**(s+i+k+1))/F(s+i+k+1) for i in range(f+1))

@functools.lru_cache(None)
def moments(s,f):
    z=integral(s,f)
    exact=(integral(s,f,1)/z,integral(s,f,2)/z)
    a,b=ALPHA+s,BETA+f;beta=(a/(a+b),a*(a+1)/((a+b)*(a+b+1)))
    return {'respond':s,'no_response':f,'uniform_mean':float(exact[0]),'uniform_second':float(exact[1]),'beta_mean':float(beta[0]),'beta_second':float(beta[1]),'mean_difference':float(beta[0]-exact[0]),'second_difference':float(beta[1]-exact[1])}

def main():
    started=datetime.now(timezone.utc).isoformat();cpu=time.process_time();rows=[];violations=[];counts=Counter();prior_cells=Counter();trace_hashes={};available_total=assigned_total=event_total=0
    families=('development','sparse','cold_start','delayed','shift','drift')
    for seed in range(1001,1009):
        for variant in families:
            path=Path(f'results/extended/development_traces/greedy_{variant}_{seed}.json');trace=json.loads(path.read_text());trace_hashes[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest();sim=Simulator(generate(seed,200,'evaluation',variant));local_checks=local_events=0
            for phase,day,actions in trace['actions']:
                assert sim.day==day
                if phase=='ask':sim.resolve_asks(actions);continue
                state=sim.observe();observed={e['introduction_id']+':'+str(e['member_id'])+':'+e['event'] for e in state['feedback']};prior=defaultdict(list)
                for intro in sim.introductions:
                    prior[intro['user_a']].append(intro['introduction_id']);prior[intro['user_b']].append(intro['introduction_id'])
                by_intro=defaultdict(list)
                for event in sim.events:by_intro[event['introduction_id']].append(event)
                response=defaultdict(lambda:[0,0])
                for e in state['feedback']:
                    if e['event'] in ('introduction_response','second_meeting_intention') and e['member_id']:
                        response[e['member_id']][0 if e['value'] is not None else 1]+=1
                for member in state['members']:
                    if not member['available']:continue
                    local_checks+=1;available_total+=1
                    for intro_id in prior[member['member_id']]:
                        for event in by_intro[intro_id]:
                            local_events+=1;event_total+=1
                            token=intro_id+':'+str(event['member_id'])+':'+event['event']
                            if event['observed_day']>day or token not in observed:
                                violations.append({'seed':seed,'variant':variant,'day':day,'member':member['member_id'],'event':event})
                for pair in actions:
                    for ident in pair:
                        assigned_total+=1;s,f=response[ident];prior_cells[(s,f)]+=1;counts[s+f]+=1
                sim.advance(actions)
            assert sim.introductions==trace['introductions']
            rows.append({'seed':seed,'variant':variant,'available_endpoint_invocations':local_checks,'prior_introduction_events_checked':local_events,'assignments':len(sim.introductions)})
    grid=[moments(s,f) for s in range(21) for f in range(21-s)]
    cohort=[dict(moments(s,f),assigned_endpoint_examples=n) for (s,f),n in sorted(prior_cells.items())]
    result={'started_utc':started,'completed_utc':datetime.now(timezone.utc).isoformat(),'command':sys.argv,'scope':'48oldgreedyworldreplays1001--1008; no newseeds; offline scheduled-event invariant check only','source_sha256':hashlib.sha256(Path('kit.py').read_bytes()).hexdigest(),'trace_sha256':trace_hashes,'episodes':rows,'available_endpoint_invocations':available_total,'prior_introduction_events_checked':event_total,'assigned_endpoint_examples':assigned_total,'violations':violations,'all_checks_passed':not violations,'response_trial_count_histogram':dict(sorted(counts.items())),'exact_uniform_posterior':{'support':[float(A),float(B)],'formula':'E[R^k|s,f] = integral_a^b r^(s+k)(1-r)^f dr / integral_a^b r^s(1-r)^f dr; rational polynomial integration','beta_prior_parameters':[float(ALPHA),float(BETA)],'scope':'Independent Bernoulli response draws under intended stochastic mechanism, ignorable adapted trial selection and explicit response/nonresponse labels; actual PRNG independence not a proved lemma','finite_count_grid_max_mean_abs':max(abs(r['mean_difference']) for r in grid),'finite_count_grid_max_second_abs':max(abs(r['second_difference']) for r in grid),'grid_total_count_up_to':20,'grid':grid,'assigned_cohort_count_cells':cohort,'cohort_weighted_mean_abs_error':sum(r['assigned_endpoint_examples']*abs(r['mean_difference']) for r in cohort)/assigned_total,'cohort_weighted_second_abs_error':sum(r['assigned_endpoint_examples']*abs(r['second_difference']) for r in cohort)/assigned_total,'cohort_max_second_abs_error':max(abs(r['second_difference']) for r in cohort)},'cpu_seconds':time.process_time()-cpu}
    assert result['all_checks_passed'];Path('results/research3/available_feedback.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('available_endpoint_invocations','prior_introduction_events_checked','assigned_endpoint_examples','all_checks_passed','cpu_seconds')}));print(json.dumps({k:v for k,v in result['exact_uniform_posterior'].items() if k not in ('grid','assigned_cohort_count_cells')}))
if __name__=='__main__':main()
