"""Post-run public funnel and privileged conditional-quality trajectory audit.
No inference import path reaches this module; no future random draws are read.
"""
import argparse,collections,hashlib,json,statistics,time
from pathlib import Path
from kit import generate
from research3.analyze import analyze,interval
from research3.mechanisms import count
from research3.trajectory_review import oracle

CONTRASTS=(('coordinated_goal','goal_surplus_control'),('hard_priority','population_control'),('response_uniform','response_beta_control'),('acceptance_shrinkage','response_uniform'))
def audit(source):
    begin=time.perf_counter();cpu=time.process_time();valid=analyze(source);data=json.loads(Path(source).read_text());worlds={};rows={};totals=collections.defaultdict(collections.Counter)
    for episode in data['episodes']:
        trace=json.loads(Path(episode['trace']).read_text());key=(episode['seed'],episode['variant'])
        if key not in worlds:worlds[key]={m['member_id']:m for m in generate(*key[:1],200,'evaluation',key[1])['members']}
        truth=worlds[key];c=count(trace);assert c['qualified']==episode['mutual_second_meeting_intention'];quality=[]
        for i in trace['introductions']:quality.append(oracle(truth[i['user_a']],truth[i['user_b']],i['assigned_day'],episode['variant']))
        c.update({'goal_unknown_endpoint_at_assignment':0,'goal_known_endpoint_at_assignment':0,'new_goal_unknown_endpoint':0,'new_goal_known_endpoint':0,'same_batch_hard_goal':0})
        used=set()
        for snap in trace['assignment_snapshots']:
            for member in (snap['member_a'],snap['member_b']):
                known=member['fields'].get('relationship_goal') is not None
                c['goal_known_endpoint_at_assignment' if known else 'goal_unknown_endpoint_at_assignment']+=1
                if member['member_id'] not in used:c['new_goal_known_endpoint' if known else 'new_goal_unknown_endpoint']+=1
                used.add(member['member_id'])
        for phase,day,acts in trace['actions']:
            if phase=='ask':
                hard={a['member_id'] for a in acts if a['field']=='constraints'};goal={a['member_id'] for a in acts if a['field']=='relationship_goal'};c['same_batch_hard_goal']+=len(hard&goal)
        sums={k:sum(q[k] for q in quality) for k in ('terminal','pause','mutual_accept')}
        row=dict(policy=episode['policy'],seed=episode['seed'],variant=episode['variant'],counts=c,privileged_expected_sums=sums,qualified_per100=c['qualified']/2,conditional_terminal_per100=sums['terminal']/2,mean_assignment_day=statistics.mean(i['assigned_day'] for i in trace['introductions']) if quality else None,trace=episode['trace'])
        rows[episode['policy'],*key]=row;totals[episode['policy']].update(c)
    seeds=data['planned_seeds'];variants=data['planned_variants'];names=data['planned_policies'];pairs=[(n,'greedy') for n in names if n!='greedy']+[(a,b) for a,b in CONTRASTS if a in names and b in names];comparisons=[]
    for lhs,rhs in pairs:
        cluster=[]
        for seed in seeds:
            a=[rows[lhs,seed,v] for v in variants];b=[rows[rhs,seed,v] for v in variants]
            item={'seed':seed,'qualified_per100':statistics.mean(x['qualified_per100']-y['qualified_per100'] for x,y in zip(a,b)),'conditional_terminal_per100':statistics.mean(x['conditional_terminal_per100']-y['conditional_terminal_per100'] for x,y in zip(a,b))}
            for k in totals[lhs]:item[k]=statistics.mean(x['counts'][k]-y['counts'][k] for x,y in zip(a,b))
            cluster.append(item)
        comparisons.append(dict(candidate=lhs,control=rhs,effects={k:interval([r[k] for r in cluster]) for k in cluster[0] if k!='seed'},clusters=cluster,representative_gain=max(cluster,key=lambda r:r['qualified_per100']),representative_loss=min(cluster,key=lambda r:r['qualified_per100'])))
    rates={}
    for n,c in totals.items():
        def rate(numerator,denominator):return {'numerator':c[numerator],'denominator':c[denominator],'ratio':c[numerator]/c[denominator] if c[denominator] else None}
        rates[n]={'both_respond_per_assignment':rate('both_respond','assignments'),'mutual_per_both_respond':rate('mutual','both_respond'),'date_per_mutual':rate('dates','mutual'),'positive_pause_per_date':rate('positive_pause','dates'),'qualified_per_pause':rate('qualified','positive_pause'),'known_goal_first_endpoint':{'numerator':c['new_goal_known_endpoint'],'denominator':c['new_goal_known_endpoint']+c['new_goal_unknown_endpoint']},'mean_busy_days_per_intro':rate('busy_days','assignments')}
    return {'source':str(source),'scope':'Descriptive chosen trajectory public counts and privileged true-parameter conditional expected funnel sums; no future outcome draws, no policy/oracle rollout, no causal mediation or attainable bound. Sum remains conditional along endogenous histories; realized-minus-q can reflect random outcomes. Quadrature32 approximate inherited independently audited against64 on old examples.','source_sha256':hashlib.sha256(Path(source).read_bytes()).hexdigest(),'counts':dict(totals),'conditional_rates':rates,'episode_rows':list(rows.values()),'comparisons':comparisons,'compute':{'wall_seconds':time.perf_counter()-begin,'cpu_seconds':time.process_time()-cpu,'workers':1}}
def main():
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--output',required=True);a=p.parse_args();target=Path(a.output);assert not target.exists();target.write_text(json.dumps(audit(a.input),indent=2)+'\n')
if __name__=='__main__':main()
