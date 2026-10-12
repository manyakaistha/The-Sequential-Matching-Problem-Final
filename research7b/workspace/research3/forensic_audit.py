"""Read-only completed-study forensic audit; no policy rollout or fresh seed use.
Hidden generator truth is used solely for labeled static development-graph audit.
"""
import collections, copy, hashlib, itertools, json, statistics, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from kit import HARD, SOFT, Simulator, eligibility, generate

def funnel(trace):
    c=collections.Counter(); grouped=collections.defaultdict(list); uses=collections.Counter()
    for e in trace['completed_feedback']:grouped[e['introduction_id']].append(e)
    for i in trace['introductions']:
        c['assignments']+=1;uses.update((i['user_a'],i['user_b']))
        es=grouped[i['introduction_id']]; rs=[e for e in es if e['event']=='introduction_response']
        assert len(rs)==2
        if any(e['value'] is None for e in rs):c['nonresponse_loss']+=1;continue
        c['both_respond']+=1
        if any(e['value']!='yes' for e in rs):c['rejection_loss_given_both_respond']+=1;continue
        c['mutual_accept']+=1
        ds=[e for e in es if e['event']=='date_happened']; assert len(ds)==1
        busy=ds[0]['occurred_day']+6-i['assigned_day'];c['mutual_busy_days']+=busy
        if ds[0]['value'] is False:c['date_cancellation']+=1;continue
        c['dates']+=1;ss=[e for e in es if e['event']=='second_meeting_intention'];assert len(ss)==2
        if any(e['value'] is None for e in ss):c['second_nonresponse']+=1;continue
        c['both_second_respond']+=1
        if any(e['value']!='yes' for e in ss):c['negative_second']+=1;continue
        c['both_positive_pause']+=1
        ld=ds[0]['occurred_day']-i['assigned_day']>30
        lf=any(e['occurred_day']-ds[0]['occurred_day']>3 for e in ss)
        c['late_date_positive']+=ld;c['late_feedback_positive']+=lf;c['overlap_deadlines_positive']+=ld and lf
        if ld or lf:c['deadline_disqualified']+=1
        else:c['qualified']+=1
    c['served_members']=len(uses);c['repeat_endpoint_assignments']=sum(uses.values())-len(uses)
    c['arrived_members']=len(trace['final_public_members'])
    for phase,day,actions in trace['actions']:
        if phase=='ask':
            c['ask_cost']+=sum(3 if a['field']=='constraints' else 1 for a in actions)
            c['hard_bundles']+=sum(a['field']=='constraints' for a in actions)
            c['soft_queries']+=sum(a['field']!='constraints' for a in actions)
            c['unused_budget']+=12-sum(3 if a['field']=='constraints' else 1 for a in actions)
    return dict(c)

def ratios(c):
    pairs=(('both_response_per_assignment','both_respond','assignments'),('mutual_accept_given_both_respond','mutual_accept','both_respond'),('date_given_mutual','dates','mutual_accept'),('both_second_response_given_date','both_second_respond','dates'),('both_positive_given_both_second_respond','both_positive_pause','both_second_respond'),('qualified_given_positive','qualified','both_positive_pause'),('qualified_per_assignment','qualified','assignments'),('coverage','served_members','arrived_members'))
    return {name:dict(numerator=c.get(a,0),denominator=c.get(b,0),ratio=c.get(a,0)/c[b] if c.get(b,0) else None) for name,a,b in pairs}

def static_graph(trace):
    # Regenerate already-examined world; latent truth never reaches a candidate.
    world=generate(trace['seed'],200,'evaluation',trace['variant']);public={m['member_id']:m for m in trace['final_public_members']}
    truth=[];verify=[];blocked=[]
    for m in world['members']:
        t=copy.deepcopy(m);t['fields']=t['truth'];truth.append(t)
        p=public[m['member_id']]
        if any(p['field_status'][k]=='declined' for k in HARD):blocked.append(m['member_id'])
        if all(p['fields'][k] is not None for k in HARD):verify.append(p)
    def graph(ms):
        edges=[];deg=collections.Counter()
        for a,b in itertools.combinations(ms,2):
            if eligibility(a,b)['status']=='feasible':
                e=(a['member_id'],b['member_id']);edges.append(e);deg.update(e)
        return dict(edges=len(edges),nonisolated_members=len(deg),isolated_members=len(ms)-len(deg),mean_degree=2*len(edges)/max(1,len(ms)))
    return dict(truth_all_members_ignores_arrival_exit_busy_pause=graph(truth),truth_nonblocked_ignores_time=graph([m for m in truth if m['member_id'] not in blocked]),final_verified_ignores_time=graph(verify),blocked_hard_decline=len(blocked),final_verified_members=len(verify),unblocked_incomplete_members=200-len(blocked)-len(verify))

def dynamic_opportunities(trace):
    """Offline realized-trajectory audit; never a counterfactual policy reward."""
    world=generate(trace['seed'],200,'evaluation',trace['variant'])
    public={m['member_id']:m for m in trace['final_public_members']}
    members={m['member_id']:m for m in world['members']}
    grouped=collections.defaultdict(list)
    for e in trace['completed_feedback']:grouped[e['introduction_id']].append(e)
    intervals=collections.defaultdict(list); pauses={};past={};edges=[]
    for i in trace['introductions']:
        es=grouped[i['introduction_id']];ds=[e for e in es if e['event']=='date_happened']
        release=ds[0]['occurred_day']+6 if ds else i['assigned_day']+8
        pair=tuple(sorted((i['user_a'],i['user_b'])));past[pair]=i['assigned_day']
        for ident in pair:
            intervals[ident].append((i['assigned_day'],release))
            ps=[e['observed_day'] for e in es if e['event']=='pause_after_mutual_interest']
            if ps:pauses[ident]=min(ps)
    for a,b in itertools.combinations(public.values(),2):
        if eligibility(a,b)['status']=='feasible':edges.append(tuple(sorted((a['member_id'],b['member_id']))))
    totals=collections.Counter();daily=[]
    for day in range(60):
        c=collections.Counter();available={};verified={}
        for ident,m in members.items():
            arrived=m['arrived_day']<=day;exit_now=day>=m['exit_day'];paused=pauses.get(ident,10000)<=day
            busy=any(start<day<end for start,end in intervals[ident])
            # Assignment start==day is not busy yet at preallocation observation.
            available[ident]=arrived and not exit_now and not paused and not busy
            verified[ident]=all(public[ident]['fields'][k] is not None and public[ident]['field_observed_day'][k]<=day for k in HARD)
            if arrived:
                c['arrived_member_days']+=1;c['exited_member_days']+=exit_now;c['paused_member_days']+=paused;c['busy_member_days']+=busy
                c['available_member_days']+=available[ident];c['available_verified_member_days']+=available[ident] and verified[ident]
        possible=set();active=set()
        for pair in edges:
            c['final_legal_edge_days']+=1
            if not all(members[i]['arrived_day']<=day for i in pair):c['edge_not_yet_arrived']+=1;continue
            if past.get(pair,10000)<day:c['edge_previously_used']+=1;continue
            if any(day>=members[i]['exit_day'] for i in pair):c['edge_endpoint_exited']+=1;continue
            if any(pauses.get(i,10000)<=day for i in pair):c['edge_endpoint_paused']+=1;continue
            if any(not available[i] for i in pair):c['edge_endpoint_busy']+=1;continue
            possible.update(pair);c['available_unused_final_legal_edge_days']+=1
            if not all(verified[i] for i in pair):c['edge_not_yet_verified']+=1;continue
            active.update(pair);c['available_verified_unused_edge_days']+=1
        c['available_members_with_final_legal_unused_partner']=len(possible)
        c['available_members_with_verified_unused_partner']=len(active)
        assigned=sum(i['assigned_day']==day for i in trace['introductions']);c['actual_assignments']=assigned
        if c['available_verified_unused_edge_days'] and not assigned:c['zero_assignment_days_with_verified_edge']+=1
        totals.update(c);daily.append(dict(day=day,**c))
    return dict(seed=trace['seed'],variant=trace['variant'],counts=dict(totals),daily=daily)

def main():
    start=time.process_time();rows=[];pooled={};graphs=[];opportunities=[]
    for p in sorted((ROOT/'results/extended/confirmation_traces').glob('*.json')):
        t=json.loads(p.read_text());c=funnel(t);rows.append(dict(policy=t['policy'],seed=t['seed'],variant=t['variant'],counts=c))
        pooled.setdefault(t['policy'],collections.Counter()).update(c)
    assert len(rows)==480
    for p in sorted((ROOT/'results/extended/development_traces').glob('greedy_*.json')):
        t=json.loads(p.read_text());graphs.append(dict(seed=t['seed'],variant=t['variant'],**static_graph(t)));opportunities.append(dynamic_opportunities(t))
    means={}
    for variant in sorted({r['variant'] for r in graphs}):
        rs=[r for r in graphs if r['variant']==variant]
        means[variant]={k:statistics.mean(r[k] for r in rs) for k in ('blocked_hard_decline','final_verified_members','unblocked_incomplete_members')}
        for level in ('truth_all_members_ignores_arrival_exit_busy_pause','truth_nonblocked_ignores_time','final_verified_ignores_time'):
            means[variant][level]={k:statistics.mean(r[level][k] for r in rs) for k in rs[0][level]}
    illegal=[]
    for field in HARD:
        sim=Simulator(generate(1001,1));ident=next(iter(sim.members))
        try:sim.resolve_asks([dict(member_id=ident,field=field)])
        except ValueError as e:illegal.append(dict(field=field,error=str(e)))
    assert len(illegal)==11
    prior=json.loads((ROOT/'results/extended/confirmation_statistics.json').read_text())
    out=dict(scope='Read-only completed confirmation traces plus privileged static graphs on prior development worlds. No fresh rollouts.',counts_by_policy={p:dict(c) for p,c in pooled.items()},pooled_conditional_rates={p:ratios(c) for p,c in pooled.items()},episode_rows=rows,development_static_graph_rows=graphs,development_realized_opportunity_rows=opportunities,development_static_graph_means=means,illegal_individual_hard_queries=illegal,legal_query_fields=['constraints']+SOFT,irrelevant_to_truth_funnel_soft_fields=['emotional_availability','space_for_relationship','relocate'],public_exact_mechanisms=dict(feedback_qualification_given_positive=.36,standard_date_qualification=1,delayed_date_qualification=671/686,arrival_max=20,exit_probability=.12,exit_day_support=[22,60],nonmutual_busy_duration=8,mutual_busy_release='date_day + 6, including cancelled dates',action_days=[0,59],final_observation_day=100),used_seed_ranges=dict(earlier=[101,105,201,205,301,305],extended_development=[1001,1008],extended_selection=[2001,2012],extended_confirmation=[3001,3040],round2_declared_development=[4001,4040],round2_declared_selection=[5001,5020],round2_declared_confirmation=[6001,6040],other=[42,20260926,*range(20261000,20261010)]),source_hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ('kit.py','evaluate.py','research3/forensic_audit.py')},compute_cpu_seconds=time.process_time()-start,command='python3 research3/forensic_audit.py')
    target=ROOT/'results/research3/forensics.json';target.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(counts=out['counts_by_policy'],rates=out['pooled_conditional_rates'],graphs=means,cpu_seconds=out['compute_cpu_seconds']),indent=2))
if __name__=='__main__':main()
