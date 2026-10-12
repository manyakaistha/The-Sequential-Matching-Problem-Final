"""Descriptive paired trajectory audit; no causal claim from selected trajectories."""
import argparse
import collections
import json
from pathlib import Path
import statistics
from research3.analyze import interval


def count(trace):
    events=collections.defaultdict(list)
    for event in trace['completed_feedback']:
        events[event['introduction_id']].append(event)
    out=collections.Counter({k:0 for k in (
        'assignments','both_respond','introduction_nonresponse','responding_rejection',
        'mutual','dates','cancelled','second_nonresponse','second_negative',
        'positive_pause','busy_days','late_date_positive','late_feedback_positive',
        'overlap_deadlines','deadline_disqualified','qualified','served_members',
        'repeat_endpoint_assignments','hard_bundles','soft_queries',
        'early_assignments','late_assignments')})
    endpoint_counts=collections.Counter()
    for intro in trace['introductions']:
        out['assignments']+=1
        endpoint_counts.update((intro['user_a'],intro['user_b']))
        es=events[intro['introduction_id']]
        rs=[e for e in es if e['event']=='introduction_response']
        ds=[e for e in es if e['event']=='date_happened']
        ss=[e for e in es if e['event']=='second_meeting_intention']
        responded=len(rs)==2 and all(e['value'] is not None for e in rs)
        mutual=len(rs)==2 and all(e['value']=='yes' for e in rs)
        date=bool(ds and ds[0]['value'])
        second_response=len(ss)==2 and all(e['value'] is not None for e in ss)
        positive=len(ss)==2 and all(e['value']=='yes' for e in ss)
        out['both_respond']+=responded
        out['introduction_nonresponse']+=not responded
        out['responding_rejection']+=responded and not mutual
        out['mutual']+=mutual
        out['dates']+=date
        out['cancelled']+=mutual and not date
        out['second_nonresponse']+=date and not second_response
        out['second_negative']+=second_response and not positive
        out['positive_pause']+=positive
        out['busy_days']+=ds[0]['occurred_day']+6-intro['assigned_day'] if mutual else 8
        if positive:
            late_date=ds[0]['occurred_day']-intro['assigned_day']>30
            late_feedback=any(e['occurred_day']-ds[0]['occurred_day']>3 for e in ss)
            out['late_date_positive']+=late_date
            out['late_feedback_positive']+=late_feedback
            out['overlap_deadlines']+=late_date and late_feedback
            out['deadline_disqualified']+=late_date or late_feedback
            out['qualified']+=not(late_date or late_feedback)
    out['served_members']=len(endpoint_counts)
    out['repeat_endpoint_assignments']=sum(n-1 for n in endpoint_counts.values())
    for phase,day,actions in trace['actions']:
        if phase=='ask':
            for action in actions:
                out['hard_bundles' if action['field']=='constraints' else 'soft_queries']+=1
        elif phase=='match':
            out['early_assignments']+=len(actions) if day<35 else 0
            out['late_assignments']+=len(actions) if day>=35 else 0
    return dict(out)


def audit(path):
    data=json.loads(Path(path).read_text())
    totals=collections.defaultdict(collections.Counter)
    by_policy=collections.defaultdict(dict)
    for row in data['episodes']:
        trace=json.loads(Path(row['trace']).read_text())
        counts=count(trace)
        if counts.get('qualified',0)!=row['mutual_second_meeting_intention']:
            raise ValueError('independent terminal label mismatch')
        totals[row['policy']].update(counts)
        by_policy[row['policy']][(row['seed'],row['variant'])]=(counts,trace)
    result=dict(source=str(path),caveat='Descriptive chosen-trajectory differences, not isolated causal mechanisms or attainable bounds.',
                totals={n:dict(x) for n,x in totals.items()},comparisons={})
    base=by_policy['greedy']
    for name,rows in by_policy.items():
        if name=='greedy':continue
        identical_queries=identical_pairs=0
        differences=collections.defaultdict(lambda:collections.defaultdict(list))
        representatives=[]
        for (seed,variant),(counts,trace) in rows.items():
            bc,bt=base[seed,variant]
            q=[a for a in trace['actions'] if a[0]=='ask']
            bq=[a for a in bt['actions'] if a[0]=='ask']
            identical_queries+=q==bq
            p=[a for a in trace['actions'] if a[0]=='match']
            bp=[a for a in bt['actions'] if a[0]=='match']
            identical_pairs+=p==bp
            for key in set(counts)|set(bc):
                differences[key][seed].append(counts.get(key,0)-bc.get(key,0))
            representatives.append(dict(seed=seed,variant=variant,qualified_difference=counts.get('qualified',0)-bc.get('qualified',0),candidate_trace=next(r['trace'] for r in data['episodes'] if r['seed']==seed and r['variant']==variant and r['policy']==name),baseline_trace=next(r['trace'] for r in data['episodes'] if r['seed']==seed and r['variant']==variant and r['policy']=='greedy')))
        result['comparisons'][name]=dict(episodes=len(rows),identical_query_schedules=identical_queries,
            identical_ordered_match_schedules=identical_pairs,
            seed_balanced_count_effects={k:interval([statistics.mean(x) for x in seeds.values()]) for k,seeds in differences.items()},
            representative_gains=sorted(representatives,key=lambda r:(-r['qualified_difference'],r['seed'],r['variant']))[:3],
            representative_losses=sorted(representatives,key=lambda r:(r['qualified_difference'],r['seed'],r['variant']))[:3])
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--output',required=True);args=p.parse_args()
    Path(args.output).write_text(json.dumps(audit(args.input),indent=2)+'\n')


if __name__=='__main__':main()
