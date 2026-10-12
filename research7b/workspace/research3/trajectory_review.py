"""Privileged, descriptive fixed-trace Stage-B audit; no rollout, fitting or outcomes oracle.
Truth plus actor parameters and family are used only offline. Future draws never read.
"""
import collections,datetime,hashlib,json,math,statistics,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from scipy.stats import t
from kit import generate
N,W=np.polynomial.hermite.hermgauss(32);N=N*math.sqrt(2)*.45;W=W/math.sqrt(math.pi)
FEATURES=('relationship_goal','relationship_pace','lifestyle','conversations')

def oracle(a,b,day,variant,n=N,w=W):
    eq=[a['truth'][k]==b['truth'][k] for k in FEATURES]
    coef=(.25,.8,-.25,.5) if variant=='shift' else (.7,.4,.25,.2)
    fit=sum(c*(1 if e else -.5) for c,e in zip(coef,eq))-(.5 if variant=='drift' and day>=35 else 0)
    sig=lambda z:1/(1+np.exp(-z))
    accept=sig(-.25+a['bias']+fit+n)*sig(-.25+b['bias']+fit+n)
    second=sig(.15+a['second_bias']+.4*eq[0]+n)*sig(.15+b['second_bias']+.4*eq[0]+n)
    rr=a['response_rate']*b['response_rate'];pause=.78*rr**2*float(w@(accept*second))
    return dict(terminal=pause*.36*(671/686 if variant=='delayed' else 1),pause=pause,mutual_accept=rr*float(w@accept))

def interval(xs):
    n=len(xs);mean=statistics.mean(xs);sd=statistics.stdev(xs) if n>1 else 0
    margin=float(t.ppf(.975,n-1))*sd/math.sqrt(n) if n>1 else 0
    return dict(n=n,mean=mean,sd=sd,ci95=[mean-margin,mean+margin])

def summarize(trace,truth):
    grouped=collections.defaultdict(list)
    for e in trace['completed_feedback']:grouped[e['introduction_id']].append(e)
    c=collections.Counter();quality=[];details=[];uses=collections.Counter();busy=[]
    for intro in trace['introductions']:
        day=intro['assigned_day'];es=grouped[intro['introduction_id']];rs=[e for e in es if e['event']=='introduction_response'];ds=[e for e in es if e['event']=='date_happened'];ss=[e for e in es if e['event']=='second_meeting_intention'];pair=(intro['user_a'],intro['user_b']);uses.update(pair)
        q=oracle(truth[pair[0]],truth[pair[1]],day,trace['variant']);quality.append(q)
        mutual=len(rs)==2 and all(e['value']=='yes' for e in rs);date=bool(ds and ds[0]['value']);positive=len(ss)==2 and all(e['value']=='yes' for e in ss)
        late_date=positive and ds[0]['occurred_day']-day>30;late_feedback=positive and any(e['occurred_day']-ds[0]['occurred_day']>3 for e in ss);qualified=positive and not(late_date or late_feedback)
        for k,v in dict(assignments=1,mutual_accept=mutual,dates=date,positive_pause=positive,late_date_positive=late_date,late_feedback_positive=late_feedback,overlap_deadline=late_date and late_feedback,deadline_disqualified=positive and (late_date or late_feedback),qualified=qualified,assigned_before35=day<35).items():c[k]+=int(v)
        duration=ds[0]['occurred_day']+6-day if ds else 8;busy.append(duration)
        details.append(dict(introduction_id=intro['introduction_id'],pair=list(pair),assigned_day=day,q=q,positive_pause=positive,qualified=qualified,late_date_positive=late_date,late_feedback_positive=late_feedback,busy_duration=duration,events=es))
    for phase,day,asks in trace['actions']:
        if phase=='ask':
            c['hard_bundles']+=sum(a['field']=='constraints' for a in asks);c['goal_queries']+=sum(a['field']=='relationship_goal' for a in asks);c['soft_queries']+=sum(a['field']!='constraints' for a in asks);c['ask_cost']+=sum(3 if a['field']=='constraints' else 1 for a in asks)
    c['served_members']=len(uses);c['repeat_endpoint_assignments']=sum(uses.values())-len(uses)
    totals={k:sum(q[k] for q in quality) for k in ('terminal','pause','mutual_accept')}
    return dict(policy=trace['policy'],seed=trace['seed'],variant=trace['variant'],counts=dict(c),oracle_sum=totals,oracle_terminal_mean=totals['terminal']/len(quality) if quality else 0,oracle_terminal_per100=totals['terminal']/2,qualified_per100=c['qualified']/2,residual_qualified_minus_q=c['qualified']-totals['terminal'],mean_busy_days=statistics.mean(busy) if busy else 0,mean_assignment_day=statistics.mean(i['assigned_day'] for i in trace['introductions']) if quality else 0),details

def first_difference(a,b,phase='match'):
    aa={day:acts for p,day,acts in a['actions'] if p==phase};bb={day:acts for p,day,acts in b['actions'] if p==phase}
    def norm(acts):return sorted([sorted(x) if phase=='match' else x for x in acts],key=lambda x:json.dumps(x,sort_keys=True))
    for day in range(60):
        if norm(aa[day])!=norm(bb[day]):return dict(day=day,candidate=aa[day],control=bb[day])
    return None

def main():
    began=datetime.datetime.now(datetime.timezone.utc).isoformat();cpu=time.process_time();wall=time.monotonic()
    data=json.loads(Path('results/research3/screen.json').read_text());assert data['complete']
    names=['greedy','offline','population','goal_queries','public_weight','random_order'];traces={};rows={};details={};truths={}
    for episode in data['episodes']:
        if episode['policy'] not in names:continue
        key=(episode['policy'],episode['seed'],episode['variant']);trace=json.loads(Path(episode['trace']).read_text());worldkey=(episode['seed'],episode['variant'])
        if worldkey not in truths:truths[worldkey]={m['member_id']:m for m in generate(episode['seed'],200,'evaluation',episode['variant'])['members']}
        row,detail=summarize(trace,truths[worldkey]);assert row['counts']['qualified']==episode['mutual_second_meeting_intention'];traces[key]=trace;rows[key]=row;details[key]=detail
    seeds=sorted({s for _,s,_ in rows});variants=sorted({v for _,_,v in rows});comparisons=[];representatives=[]
    for candidate,control in [('offline','greedy'),('offline','population'),('goal_queries','greedy'),('goal_queries','public_weight'),('random_order','greedy')]:
        clusters=[]
        for seed in seeds:
            pairs=[(rows[candidate,seed,v],rows[control,seed,v]) for v in variants]
            clusters.append(dict(seed=seed,qualified_per100=statistics.mean(a['qualified_per100']-b['qualified_per100'] for a,b in pairs),oracle_terminal_per100=statistics.mean(a['oracle_terminal_per100']-b['oracle_terminal_per100'] for a,b in pairs),positive_pause=statistics.mean(a['counts']['positive_pause']-b['counts']['positive_pause'] for a,b in pairs),deadline_disqualified=statistics.mean(a['counts']['deadline_disqualified']-b['counts']['deadline_disqualified'] for a,b in pairs),assignments=statistics.mean(a['counts']['assignments']-b['counts']['assignments'] for a,b in pairs)))
        comp=dict(candidate=candidate,control=control,seed_clusters=clusters,paired_descriptive_intervals={k:interval([c[k] for c in clusters]) for k in clusters[0] if k!='seed'})
        comparisons.append(comp)
        for side,cluster in [('largest_positive',max(clusters,key=lambda c:(c['qualified_per100'],-c['seed']))),('largest_negative',min(clusters,key=lambda c:(c['qualified_per100'],c['seed'])))]:
            seed=cluster['seed'];vs=[]
            for v in variants:
                a,b=traces[candidate,seed,v],traces[control,seed,v]
                aset={(tuple(sorted(d['pair'])),d['assigned_day']) for d in details[candidate,seed,v]};bset={(tuple(sorted(d['pair'])),d['assigned_day']) for d in details[control,seed,v]}
                onlya=[d for d in details[candidate,seed,v] if (tuple(sorted(d['pair'])),d['assigned_day']) not in bset and d['positive_pause']]
                onlyb=[d for d in details[control,seed,v] if (tuple(sorted(d['pair'])),d['assigned_day']) not in aset and d['positive_pause']]
                vs.append(dict(variant=v,candidate_row=rows[candidate,seed,v],control_row=rows[control,seed,v],first_match_difference=first_difference(a,b),first_ask_difference=first_difference(a,b,'ask'),candidate_only_positive_events=onlya,control_only_positive_events=onlyb))
            representatives.append(dict(candidate=candidate,control=control,selection=side,cluster=cluster,variants=vs))
    queryrows=[]
    for seed in seeds:
        for v in variants:
            a,b=traces['goal_queries',seed,v],traces['public_weight',seed,v]
            hard=lambda trace:[[day,[x for x in asks if x['field']=='constraints']] for phase,day,asks in trace['actions'] if phase=='ask']
            queryrows.append(dict(seed=seed,variant=v,hard_schedules_equal=hard(a)==hard(b),first_match_difference=first_difference(a,b),first_ask_difference=first_difference(a,b,'ask'),soft_queries=rows['goal_queries',seed,v]['counts']['soft_queries']))
    means={name:dict(count_totals={k:sum(rows[name,s,v]['counts'].get(k,0) for s in seeds for v in variants) for k in rows[name,seeds[0],variants[0]]['counts']},oracle_terminal_per100=statistics.mean(rows[name,s,v]['oracle_terminal_per100'] for s in seeds for v in variants),qualified_per100=statistics.mean(rows[name,s,v]['qualified_per100'] for s in seeds for v in variants),oracle_terminal_assignment_weighted=sum(rows[name,s,v]['oracle_sum']['terminal'] for s in seeds for v in variants)/sum(rows[name,s,v]['counts']['assignments'] for s in seeds for v in variants)) for name in names}
    z64,w64=np.polynomial.hermite.hermgauss(64);z64=z64*math.sqrt(2)*.45;w64=w64/math.sqrt(math.pi);errors=[]
    for d in details['offline',seeds[0],'development'][:64]:
        a,b=(truths[seeds[0],'development'][i] for i in d['pair']);other=oracle(a,b,d['assigned_day'],'development',z64,w64);errors.append(abs(other['terminal']-d['q']['terminal']))
    out=dict(scope='Descriptive privileged truth/parameter conditional probabilities along realized B actions; not deployable scores, oracle-policy reward or causal policy effect.',source='results/research3/screen.json',code_hashes=data['code_hashes'],started_utc=began,episode_rows=list(rows.values()),means=means,comparisons=comparisons,representatives=representatives,goal_query_control_rows=queryrows,quadrature=dict(nodes=32,max32vs64_terminal_difference_on_first64_oldoffline_assignments=max(errors),tested_assignments=len(errors)),compute=dict(cpu_seconds=time.process_time()-cpu,wall_seconds=time.monotonic()-wall,workers=1),audit_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),command=['python3','research3/trajectory_review.py'])
    Path('results/research3/trajectory_review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(means=means,comparisons=[dict(candidate=c['candidate'],control=c['control'],intervals=c['paired_descriptive_intervals']) for c in comparisons],compute=out['compute']),indent=2))
if __name__=='__main__':main()
