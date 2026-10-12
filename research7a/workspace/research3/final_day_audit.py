"""Registered final-day controlled intervention; already examined B worlds only."""
import copy
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time
from kit import Simulator, eligibility, generate
from research3.model_candidates import score_edge
from research3.prediction_audit import funnel

FAMILIES=('development','sparse','cold_start','delayed','shift','drift')

def qualified(sim):
    out=set()
    for intro in sim.introductions:
        events=[e for e in sim.receive_feedback() if e['introduction_id']==intro['introduction_id']];dates=[e for e in events if e['event']=='date_happened' and e['value']];seconds=[e for e in events if e['event']=='second_meeting_intention']
        if dates and len(seconds)==2 and dates[0]['occurred_day']-intro['assigned_day']<=30 and all(e['value']=='yes' and e['occurred_day']-dates[0]['occurred_day']<=3 for e in seconds):out.add(intro['introduction_id'])
    return out

def run(seed,family,policy):
    path=Path(f'results/research3/screen_traces/{policy}_{family}_{seed}.json');trace=json.loads(path.read_text());sim=Simulator(generate(seed,200,'evaluation',family));original_pairs=None
    for phase,day,actions in trace['actions']:
        assert sim.day==day
        if phase=='ask':sim.resolve_asks(actions)
        elif day<59:sim.advance(actions)
        else:original_pairs=actions;break
    assert sim.day==59 and original_pairs is not None
    state=sim.observe();used={i for pair in original_pairs for i in pair};past={tuple(sorted((i['user_a'],i['user_b']))) for i in state['introductions']};members=[m for m in state['members'] if m['available'] and m['member_id'] not in used];edges=[]
    for a,b in itertools.combinations(members,2):
        pair=tuple(sorted((a['member_id'],b['member_id'])))
        if pair in past or eligibility(a,b)['status']!='feasible':continue
        if score_edge(a,b,state,'public_weight')==0:edges.append(pair)
    extra=[]
    for pair in sorted(edges):
        if not used.intersection(pair):extra.append(list(pair));used.update(pair)
    truth=sim.members;expected=sum(funnel(truth[a],truth[b],59,private=(truth[a],truth[b],family),truth=True)['terminal'] for a,b in extra)
    baseline=copy.deepcopy(sim);augmented=copy.deepcopy(sim);baseline.advance(original_pairs);augmented.advance(original_pairs+extra)
    for _ in range(40):baseline.advance([]);augmented.advance([])
    assert baseline.day==augmented.day==100
    old_ids={i['introduction_id'] for i in baseline.introductions};added_ids={i['introduction_id'] for i in augmented.introductions}-old_ids
    assert len(old_ids)==len(baseline.introductions) and len(added_ids)==len(extra)
    original_events=baseline.receive_feedback();retained_events=[e for e in augmented.receive_feedback() if e['introduction_id'] in old_ids]
    old_bytes=json.dumps(original_events,sort_keys=True,separators=(',',':')).encode();new_bytes=json.dumps(retained_events,sort_keys=True,separators=(',',':')).encode()
    assert old_bytes==new_bytes and original_events==trace['completed_feedback'] and baseline.introductions==trace['introductions']
    original_q=qualified(baseline);augmented_q=qualified(augmented);assert original_q<=augmented_q
    return {'seed':seed,'variant':family,'policy':policy,'trace_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'zero_legal_edges_between_original_unmatched':len(edges),'appended_pairs':extra,'original_pairs_day59':len(original_pairs),'existing_event_bytes_identical':True,'existing_event_sha256':hashlib.sha256(old_bytes).hexdigest(),'original_qualified':len(original_q),'augmented_qualified':len(augmented_q),'qualified_gain':len(augmented_q)-len(original_q),'new_qualified':len(augmented_q&added_ids),'added_edge_expected_qualified_numerical':expected,'baseline_metrics':baseline.metrics(),'augmented_metrics':augmented.metrics()}

def constructed():
    hard={'age_min':21,'age_max':40,'who_to_meet':['man','woman'],'relationship_structure':'monogamous','smoking':'no','partner_smoking':'any','has_children':False,'partner_children':'any','wants_children':'unsure','acceptable_zones':['zone_a'],'schedule':['weekday_evening']}
    a={'member_id':'constructed_a','pool_id':'constructed','age':30,'gender':'man','zone':'zone_a','fields':dict(hard,relationship_goal='long_term',relationship_pace='slow',lifestyle='quiet',conversations='ideas')}
    b={'member_id':'constructed_b','pool_id':'constructed','age':30,'gender':'woman','zone':'zone_a','fields':dict(hard,relationship_goal='exploring',relationship_pace='quick',lifestyle='social',conversations='stories')}
    for m in (a,b):m.update(truth=dict(m['fields']),bias=0.,second_bias=0.,response_rate=.765)
    score=score_edge(a,b,{'day':59},'public_weight');q=funnel(a,b,59,private=(a,b,'development'),truth=True)['terminal']
    assert eligibility(a,b)['status']=='feasible' and score==0 and q>0
    return {'specified_fields':[a['fields'],b['fields']],'biases':0,'response_propensity':.765,'family':'development','day':59,'public_weight':score,'terminal_q_15point_quadrature':q,'analytic_positive':'Every sigmoid and propensity factor is strictly positive; date=.78 and feedback deadline=.36; standard date meetsdeadline. Integral therefore positive irrespective of finite quadrature.'}

def main():
    started=datetime.now(timezone.utc).isoformat();cpu=time.process_time();target=Path('results/research3/final_day_augmentation.json')
    if target.exists():raise RuntimeError('refuse overwrite registered diagnostic')
    registry=Path('research3/FINAL_DAY_AUGMENTATION.md');before=hashlib.sha256(registry.read_bytes()).hexdigest();rows=[run(seed,family,policy) for seed in (70001,70002) for family in FAMILIES for policy in ('public_weight','goal_queries')]
    result={'started_utc':started,'completed_utc':datetime.now(timezone.utc).isoformat(),'command':sys.argv,'registry_sha256_before_run':before,'scope':'24controlledposthocdiagnostictrajectories on12alreadyexaminedBworlds; no newseeds/neweligiblepolicy/frozenmoduleedits','rows':rows,'constructed_example':constructed(),'summary':{'trajectory_count':len(rows),'appended_edges':sum(len(r['appended_pairs']) for r in rows),'realized_qualified_gain':sum(r['qualified_gain'] for r in rows),'numerical_expected_qualified_gain_sum':sum(r['added_edge_expected_qualified_numerical'] for r in rows),'all_existing_event_bytes_identical':all(r['existing_event_bytes_identical'] for r in rows)},'cpu_seconds':time.process_time()-cpu}
    target.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps({'summary':result['summary'],'constructed':result['constructed_example'],'cpu_seconds':result['cpu_seconds']},indent=2))
if __name__=='__main__':main()
