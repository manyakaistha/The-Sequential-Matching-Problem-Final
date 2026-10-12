"""Public snapshot audit and explicitly offline simulator micro-audits.
Never imported by the evaluated policy. No reconstruction of snapshot hidden truth.
"""
import collections
import itertools
import json
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm
from kit import HARD, Simulator, generate, eligibility
from research_policy import FEATURES, blocked

ROOT=Path(__file__).resolve().parents[1]
def lines(path):return [json.loads(s) for s in path.read_text().splitlines() if s.strip()]
def distribution(rows):
    counts=collections.Counter(tuple(r) for r in rows);n=len(rows)
    if not n:return {'n':0}
    joint={str(k):v/n for k,v in counts.items()};a=sum(x for x,y in rows)/n;b=sum(y for x,y in rows)/n
    both=counts[(1,1)]/n;var=a*(1-a)*b*(1-b)
    mi=sum(v/n*math.log((v/n)/((a if x else 1-a)*(b if y else 1-b)),2) for (x,y),v in counts.items() if v)
    return dict(n=n,counts={str(k):v for k,v in counts.items()},joint=joint,p_a=a,p_b=b,p_both=both,independent_product=a*b,
                pearson=(both-a*b)/math.sqrt(var) if var else None,mutual_information_bits=mi)

def survival(records):
    """KM and Nelson-Aalen for event occurrence. Outcome 2 is competing failure;
    output Aalen-Johansen incidence rather than hiding nonresponse as censoring.
    """
    if not records:return []
    s=1.;h=0.;all_s=1.;incidence=0.;out=[]
    for t in sorted(set(t for t,k in records)):
        risk=sum(tt>=t for tt,k in records);d=sum(tt==t and k==1 for tt,k in records);f=sum(tt==t and k==2 for tt,k in records);c=sum(tt==t and k==0 for tt,k in records)
        if risk:
            s*=1-d/risk;h+=d/risk;incidence+=all_s*d/risk;all_s*=1-(d+f)/risk
        out.append(dict(day=t,risk=risk,events=d,competing=f,censored=c,km_net_survival=s,nelson_aalen=h,cumulative_incidence=incidence))
    return out

def graph(members):
    degree={m['member_id']:0 for m in members};edges=[]
    for a,b in itertools.combinations(members,2):
        if eligibility(a,b)['status']=='feasible':
            edges.append((a['member_id'],b['member_id']));degree[a['member_id']]+=1;degree[b['member_id']]+=1
    import networkx as nx
    g=nx.Graph();g.add_nodes_from(degree);g.add_edges_from(edges)
    return dict(n=len(members),edges=len(edges),density=len(edges)/max(1,len(members)*(len(members)-1)/2),
                degree_histogram=dict(collections.Counter(degree.values())),islands=sum(k<=1 for k in degree.values()),
                super_spreaders=sum(k>len(members)/2 for k in degree.values()),max_degree=max(degree.values(),default=0),
                components=nx.number_connected_components(g),bipartite=nx.is_bipartite(g))

def snapshot_audit():
    all_rows=[];responded_rows=[];poolstats=[];association={k:collections.defaultdict(list) for k in FEATURES};interaction=collections.defaultdict(list)
    records=collections.defaultdict(list);demographics=collections.defaultdict(collections.Counter);fit_rows=[]
    for directory in sorted((ROOT/'data').glob('public_*')):
        state=json.loads((directory/'state.json').read_text());members={m['member_id']:m for m in state['members']};events=collections.defaultdict(list)
        for e in state['feedback']:events[e['introduction_id']].append(e)
        rows=[];mature=0;qualified=0;mutual_second=0;late_response=0
        for i in state['introductions']:
            es=events[i['introduction_id']];rs=[e for e in es if e['event']=='introduction_response'];age=30-i['assigned_day']
            if len(rs)==2:
                rows.append(tuple(int(e['value']=='yes') for e in sorted(rs,key=lambda e:e['member_id'])))
                if all(e['value'] is not None for e in rs):
                    responded_rows.append(tuple(int(e['value']=='yes') for e in sorted(rs,key=lambda e:e['member_id'])))
            for ident in (i['user_a'],i['user_b']):
                e=next((e for e in rs if e['member_id']==ident),None)
                records['assignment_to_response'].append((e['observed_day']-i['assigned_day'],1 if e['value'] is not None else 2) if e else (age,0))
            responses=sorted(e['occurred_day'] for e in rs if e['occurred_day'] is not None)
            if responses:
                # First real response; no-response resolution is a competing endpoint.
                if len(responses)==2:records['first_to_second_response'].append((responses[1]-responses[0],1))
                else:
                    other=next((e for e in rs if e['occurred_day'] is None),None)
                    records['first_to_second_response'].append((other['observed_day']-responses[0],2) if other else (30-responses[0],0))
            ds=[e for e in es if e['event']=='date_happened'];ss=[e for e in es if e['event']=='second_meeting_intention']
            accepted=len(rs)==2 and all(e['value']=='yes' for e in rs)
            if accepted:
                start=max(e['observed_day'] for e in rs)
                records['mutual_acceptance_to_date'].append((ds[0]['observed_day']-start,1 if ds[0]['value'] else 2) if ds else (30-start,0))
            if ds and ds[0]['value']:
                start=ds[0]['occurred_day']
                for ident in (i['user_a'],i['user_b']):
                    e=next((e for e in ss if e['member_id']==ident),None)
                    records['date_to_feedback'].append((e['observed_day']-start,1 if e['value'] is not None else 2) if e else (30-start,0))
                if len(ss)==2 and all(e['value']=='yes' for e in ss):
                    mutual_second+=1
                    late=any(e['occurred_day']-start>3 for e in ss);late_response+=late
                    qualified+=not late and start-i['assigned_day']<=30
            # Day-30 public data: only mature <=4 assignments can be classified negative safely.
            terminal_known=bool(ds and not ds[0]['value']) or (len(rs)==2 and not accepted) or len(ss)==2 or age>=26
            if not terminal_known:continue
            mature+=1;terminal=int(bool(ds and ds[0]['value']) and len(ss)==2 and all(e['value']=='yes' and e['occurred_day']-ds[0]['occurred_day']<=3 for e in ss))
            a,b=members[i['user_a']],members[i['user_b']]
            matches=[]
            for k in FEATURES:
                known=a['fields'].get(k) is not None and b['fields'].get(k) is not None
                equal=int(a['fields'].get(k)==b['fields'].get(k)) if known else None
                matches.append(equal)
                if known:association[k][str(equal)].append((int(bool(ds and ds[0]['value'])),terminal))
            if matches[1] is not None and matches[3] is not None:interaction[str((matches[3],matches[1]))].append(terminal)
            if all(v is not None for v in matches):fit_rows.append((matches,terminal,directory.name))
        all_rows.extend(rows)
        for m in members.values():
            group='declined' if blocked(m) else 'not_declined';demographics[group]['n']+=1;demographics[group]['age_sum']+=m['age'];demographics[group]['gender:'+m['gender']]+=1;demographics[group]['zone:'+m['zone']]+=1
        poolstats.append(dict(pool=directory.name,day=state['day'],acceptance=distribution(rows),all_visible_graph=graph(list(members.values())),
                              active_graph=graph([m for m in members.values() if m['available']]),mature_or_resolved_introductions=mature,
                              observed_mutual_second=mutual_second,observed_qualified=qualified,late_feedback=late_response))
    def rates(vals):return dict(n=len(vals),date_rate=sum(x for x,y in vals)/max(1,len(vals)),msmi_rate=sum(y for x,y in vals)/max(1,len(vals)))
    result=dict(pools=poolstats,acceptance=distribution(all_rows),acceptance_both_responded=distribution(responded_rows),soft_associations={k:{e:rates(v) for e,v in groups.items()} for k,groups in association.items()},
                conversations_pace_interaction={k:dict(n=len(v),msmi_rate=sum(v)/len(v)) for k,v in interaction.items()},
                funnel_survival={k:survival(v) for k,v in records.items()},demographics={k:dict(v) for k,v in demographics.items()},
                limitations=['All ten pools audited descriptively; development-test never used to fit policy.',
                              'Day-30 snapshots cannot identify unobserved hard constraints or eventual outcomes.',
                              'Soft associations use snapshot fields and are descriptive, not assignment-time causal estimates.',
                              'Empirical directional dependence is selected-pair dependence; sorting arbitrary IDs defines direction.'])
    return result

def exact_delay(delayed=False):
    mass=collections.Counter()
    for a,b,d in itertools.product(range(1,8),range(1,8),range(1,15)):
        for extra in range(5,13) if delayed else [0]:mass[max(a,b)+d+extra]+=1
    n=sum(mass.values());prob={k:v/n for k,v in sorted(mass.items())}
    before60={t:sum(p for d,p in prob.items() for s1,s2 in itertools.product(range(1,6),repeat=2) if t+d+max(s1,s2)<60)/25 for t in range(60)}
    qualifying_before60={t:sum(p for d,p in prob.items() for s1,s2 in itertools.product(range(1,4),repeat=2) if d<=30 and t+d+max(s1,s2)<60)/25 for t in range(60)}
    return dict(pmf=prob,mean=sum(d*p for d,p in prob.items()),late_date_probability=sum(p for d,p in prob.items() if d>30),
                feedback_lateness_given_both_yes=1-.6**2,before60_given_date_and_both_yes=before60,
                qualifying_before60_given_date_and_both_yes=qualifying_before60,
                tcrit_conditional_completion=next((t for t,p in before60.items() if p<.05),None),
                last_day_fully_observed_with_official_followup=59+max(prob)+5)

def microaudit():
    result={}
    for variant in ('development','sparse','cold_start','delayed','shift','drift'):
        out=[]
        for seed in range(101,106):
            world=generate(seed,200,'audit',variant);sim=Simulator(world)
            before=graph(sim.observe()['members'])
            for m in sim.members.values():
                for k in HARD:
                    if m['field_status'][k]!='declined':m['fields'][k]=m['truth'][k];m['field_status'][k]='observed'
            after=graph(sim.observe()['members'])
            truth=[dict(m,fields=m['truth']) for m in world['members']]
            out.append(dict(seed=seed,before=before,after_unlimited_non_declined_constraints=after,
                            truth_graph_all_arrivals=graph(truth),declined_fraction=sum(blocked(m) for m in world['members'])/200))
        result[variant]=out
    return result

def sign_detection():
    """Independent randomized fully observed logistic experiment, not adaptive policy confidence.
    Synthetic shift detection power; clustered effects make this optimistic for actual policy.
    """
    rng=np.random.default_rng(719);out=[]
    for n in (100,300,1000,3000):
        successes=0;estimates=[]
        for _ in range(80):
            x=np.column_stack([np.ones(n)]+[1.5*(rng.random(n)<p)-.5 for p in (.5,1/3,1/3,.25)])
            true=np.array([-.25,.25,.8,-.25,.5]);p=1/(1+np.exp(-x@true));y=rng.random(n)<p
            fit=minimize(lambda b:np.logaddexp(0,x@b).sum()-y@(x@b),np.zeros(5),jac=lambda b:x.T@(1/(1+np.exp(-x@b))-y),method='BFGS')
            b=fit.x;pp=1/(1+np.exp(-x@b));cov=np.linalg.inv(x.T@(x*(pp*(1-pp))[:,None]))
            detected=b[3]+norm.ppf(.95)*math.sqrt(cov[3,3])<0;successes+=detected;estimates.append(float(b[3]))
        out.append(dict(n=n,trials=80,detection_probability=successes/80,mean_lifestyle_estimate=sum(estimates)/80))
    # One-sided 95% confidence AND 95% power planning bound.
    information=.25*(1.5**2*(1/3)*(2/3))
    return dict(randomized_experiment=out,optimistic_information_bound=information,
                optimistic_n_for_95_confidence_95_power=math.ceil((2*norm.ppf(.95))**2/(.25**2*information)),
                warning='Not a guarantee: adaptive sampling, shared dyadic effects, missingness and nuisance covariance lower information.')

if __name__=='__main__':
    out=dict(public=snapshot_audit(),offline_graph_audit=microaudit(),delays={v:exact_delay(v=='delayed') for v in ('standard','delayed')},shift_detection=sign_detection())
    (ROOT/'results/research/audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Saved public, survival, graph, timing and detection audits')
