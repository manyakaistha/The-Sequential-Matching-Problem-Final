"""Descriptive representative trajectories and common-stream overlap, not causal attribution."""
import argparse
import hashlib
import json
import statistics
from pathlib import Path

FAMILIES=('development','sparse','cold_start','delayed','shift','drift')

def summarize(lhs,rhs):
    a={x['introduction_id']:x for x in lhs['introductions']}
    b={x['introduction_id']:x for x in rhs['introductions']}
    shared=set(a)&set(b)
    def events(trace,keys):
        return sorted([x for x in trace['completed_feedback'] if x['introduction_id'] in keys],key=lambda x:json.dumps(x,sort_keys=True))
    assert all(a[k]==b[k] for k in shared)
    assert events(lhs,shared)==events(rhs,shared)
    def dyads(intros):return {tuple(sorted((i['user_a'],i['user_b']))) for i in intros.values()}
    first={}
    for phase in ('ask','match'):
        aa=[x for x in lhs['actions'] if x[0]==phase];bb=[x for x in rhs['actions'] if x[0]==phase]
        assert len(aa)==len(bb)==60
        differences=[(x,y) for x,y in zip(aa,bb) if x!=y]
        first[phase]={'day':differences[0][0][1],'candidate_action':differences[0][0][2],'control_action':differences[0][1][2]} if differences else None
    return dict(candidate_assignments=len(a),control_assignments=len(b),common_dyad_day=len(shared),common_dyad_any_day=len(dyads(a)&dyads(b)),identical_events_for_common_dyad_day=True,first_divergence=first)

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',default='results/research4/focus_mechanisms.json');p.add_argument('--candidate',default='hard_priority');p.add_argument('--control',default='population_control');p.add_argument('--output',default='results/research4/trajectory_review_focus.json');args=p.parse_args()
    source=Path(args.input);data=json.loads(source.read_text());pair=next(x for x in data['comparisons'] if x['candidate']==args.candidate and x['control']==args.control)
    clusters=pair['clusters'];means=[x['qualified_per100'] for x in clusters];loo=[statistics.mean(means[:i]+means[i+1:]) for i in range(len(means))]
    rows={(x['policy'],x['seed'],x['variant']):x for x in data['episode_rows']}
    result={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidate':args.candidate,'control':args.control,'scope':'Post-C exploratory representative trajectory inspection. Common dyad+assignment-day outcomes share hashed simulator streams; changed dyads/days do not. Selection of extreme trajectories is descriptive and not causal mediation or independent evidence. No inference or fitting changes.', 'cluster_effect':statistics.mean(means),'leave_one_seed_out_range':[min(loo),max(loo)],'representatives':[]}
    for direction,cluster in [('largest_gain',pair['representative_gain']),('largest_loss',pair['representative_loss'])]:
        details=[]
        for family in FAMILIES:
            aa=rows[args.candidate,cluster['seed'],family];bb=rows[args.control,cluster['seed'],family]
            at=json.loads(Path(aa['trace']).read_text());bt=json.loads(Path(bb['trace']).read_text())
            details.append(dict(family=family,candidate_counts=aa['counts'],control_counts=bb['counts'],candidate_conditional_terminal_per100=aa['conditional_terminal_per100'],control_conditional_terminal_per100=bb['conditional_terminal_per100'],candidate_trace=aa['trace'],control_trace=bb['trace'],**summarize(at,bt)))
        result['representatives'].append(dict(direction=direction,cluster=cluster,families=details))
    target=Path(args.output);assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
