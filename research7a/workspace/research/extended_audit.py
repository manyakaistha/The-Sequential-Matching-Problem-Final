"""Offline research audit. Hidden world is used only in explicitly labeled oracle comparisons.
Evaluated decisions receive JSON observations only; assignment predictions are snapshotted.
"""
import argparse
import collections
import copy
import itertools
import functools
import json
import math
from pathlib import Path
import sys
sys.path[:] = [p for p in sys.path if Path(p or '.').resolve() != Path(__file__).resolve().parent]
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from scipy import stats
import evaluate
from kit import Simulator,generate,HARD,OPTIONS,eligibility
from research.benchmark import run as old_run
from research.extended_analysis import analyze,interval,paired_p,holm

STAGES=('both_response','both_accept_unconditional','date_unconditional','both_second_yes_unconditional','terminal')

def inventory():
    out={}
    for p in Path('.').rglob('*.json'):
        if '.venv' in p.parts or '.git' in p.parts or 'extended' in p.parts:continue
        try:obj=json.loads(p.read_text())
        except (ValueError,OSError):continue
        seeds=set()
        def walk(x):
            if isinstance(x,dict):
                if isinstance(x.get('seed'),int):seeds.add(x['seed'])
                if isinstance(x.get('seeds'),list):seeds.update(s for s in x['seeds'] if isinstance(s,int))
                for v in x.values():walk(v)
            elif isinstance(x,list):
                for v in x:walk(v)
        walk(obj)
        if seeds:out[str(p)]=sorted(seeds)
    return {'artifact_seed_inventory':out,'additional_source_seeds':[42,201,202,203,204,205,20260926],
      'reserved_new_ranges':{'development':[1001,1008],'selection':[2001,2012],'confirmation':[3001,3040]}}

def starting_audit():
    prior={name:json.loads(Path('results/research/'+name+'.json').read_text())['episodes'] for name in ('benchmark','holdout')}
    findings={name:analyze(rows) for name,rows in prior.items()}
    comp=next(x for x in findings['holdout']['comparisons'] if x['policy']=='product')
    sd=comp['difference']['sd'];planning={str(delta):math.ceil(((stats.norm.ppf(.975)+stats.norm.ppf(.8))*sd/delta)**2) for delta in (.05,.10)}
    rows=[old_run((p,v,101,False)) for p in ('greedy','full','product') for v in evaluate.VARIANTS]
    known={(r['policy'],r['variant'],r['seed']):r for r in prior['benchmark']}
    reproduced=[]
    for row in rows:
        old=known[row['policy'],row['variant'],row['seed']]
        fields=('assignments','mutual_acceptances','dates','mutual_second_meeting_intention','ask_cost','action_sha256')
        reproduced.append({'policy':row['policy'],'variant':row['variant'],'seed':row['seed'],'equal':all(row[k]==old[k] for k in fields),'fields':{k:{'old':old[k],'rerun':row[k]} for k in fields}})
    timing={}
    for delayed in (False,True):
        delays=[max(a,b)+d+extra for a,b,d,extra in itertools.product(range(1,8),range(1,8),range(1,15),range(5,13) if delayed else [0])]
        timing['delayed' if delayed else 'standard']={'max_date_delay':max(delays),'date_deadline_probability':sum(d<=30 for d in delays)/len(delays),'max_feedback_delay':max(delays)+5,'expected_mutual_busy_duration':np.mean(delays)+6}
    return {'seed_inventory':inventory(),'previous_findings':findings,'reproduction':reproduced,'episodes':rows,
      'numerical_approximation_audit':numerical_approximation_audit(),'pilot_paired_sd':sd,'sample_planning_normal_80pct_power_2sided_05':planning,
      'timing_exact_enumeration':timing,'feedback_both_within_3_of_date_probability':.36,
      'hard_fields':HARD,'simulator_reconciled':{'decision_days':[0,59],'follow_up_days':40,'exit_member_probability':.12,'exit_day_support':[22,60],
        'busy_release_latent':True,'retirement_ignores_qualification_deadlines':True,'same_dyad_repeat':False,'distinct_repeat_introductions':True,
        'declines_permanent':True,'all_followup_complete':True},
      'counterexamples':{'harmonic':{'p_a':.5,'p_b':.5,'harmonic':.5,'independent_joint':.25},
        'complementarity':'One edge uv, both endpoints require clarification. Neither singleton query exposes an edge; querying both exposes one. Marginal value rises from 0 to 1.',
        'connectivity':'On five vertices, graph {01} and graph {01,23} are both disconnected with lambda_2=0; maximum matching cardinality rises from one to two.'}}

def numerical_approximation_audit():
    from research.terminal_model import integrated,REGIMES,NODES,WEIGHTS
    max_single=0.;max_joint=0.;examples=[];errors=[]
    sig=lambda x:1/(1+math.exp(-x))
    for regime,weights in enumerate(REGIMES):
        for eq in itertools.product((0.,1.,None),repeat=4):
            probs=[p if p is not None else 1/c for p,c in zip(eq,(2,3,3,4))]
            unknown=[i for i,p in enumerate(eq) if p is None]
            for bias in (-4.,-1.,0.,1.,4.):
                exact=joint=0.;zmean=-.25+bias+sum(w*(1.5*p-.5) for w,p in zip(weights[:4],probs))
                for bits in itertools.product((0.,1.),repeat=len(unknown)):
                    e=list(probs);mass=1.
                    for i,bit in zip(unknown,bits):mass*=probs[i] if bit else 1-probs[i];e[i]=bit
                    p=sig(-.25+bias+sum(w*(1 if a else -.5) for w,a in zip(weights[:4],e)))
                    exact+=mass*p;joint+=mass*p*p
                plug=sig(zmean);error=abs(exact-plug);errors.append(error)
                if error>max_single:max_single=error;examples=[{'regime':regime,'equality_prior':probs,'actor_bias':bias,'exact':exact,'sigmoid_expected_feature':plug}]
                max_joint=max(max_joint,abs(joint-plug**2))
    qerrors=[]
    z,w=np.polynomial.hermite.hermgauss(32);z=z*np.sqrt(2);w=w/np.sqrt(np.pi)
    actor_sig=lambda x,var:float(w@(1/(1+np.exp(-(x+np.sqrt(var)*z)))))
    for regime in range(3):
        for eq in itertools.product((0.,1.),repeat=4):
            five=integrated(eq,(0.,.49,0.,.25),(0.,.49,0.,.25),0,regime,True)
            fit=-.25+sum(ww*(1 if e else -.5) for ww,e in zip(REGIMES[regime][:4],eq));sec=.15+.4*eq[0]
            exact=[0.]*5
            for shared,ww in zip(.45*z,w):
                pa=actor_sig(fit+shared,.49);sa=actor_sig(sec+shared,.25)
                for j,val in enumerate((pa,pa,pa*pa,sa*sa,pa*pa*sa*sa)):exact[j]+=ww*val
            qerrors.append(max(abs(a-b) for a,b in zip(five,exact)))
    return {'missing_feature_logistic_error_grid':{'comparisons':len(errors),'max_absolute_directional_error':max_single,'mean_absolute_directional_error':float(np.mean(errors)),'max_absolute_joint_error':max_joint,'max_error_example':examples,
          'scope':'Public logits only, enumerated missing equality priors; this grid is not an error bound outside tested settings.'},
          'five_vs_32_node_nested_quadrature':{'comparisons':len(qerrors),'max_absolute_probability_error':max(qerrors),
          'scope':'All 16 fully observed equality patterns x 3 regimes, prior zero actor means and .49/.25 variances, assignment day0; not universal quadrature certificate.'}}

@functools.lru_cache(maxsize=1)
def delayed_deadline_probability():
    return sum(max(x,y)+d+ex<=30 for x,y,d,ex in itertools.product(range(1,8),range(1,8),range(1,15),range(5,13)))/(7*7*14*8)

def oracle_funnel(a,b,day,variant,n=32):
    """Oracle expectation integrates S, holding actor truth fixed. Not a policy input."""
    z,w=np.polynomial.hermite.hermgauss(n);z=z*np.sqrt(2)*.45;w=w/np.sqrt(np.pi)
    sig=lambda x:1/(1+np.exp(-x))
    eq=[a['truth'][k]==b['truth'][k] for k in ('relationship_goal','relationship_pace','lifestyle','conversations')]
    weights=[.25,.8,-.25,.5] if variant=='shift' else [.7,.4,.25,.2]
    fit=sum(c*(1 if e else -.5) for c,e in zip(weights,eq))-(.5 if variant=='drift' and day>=35 else 0)
    acceptance=sig(-.25+a['bias']+fit+z)*sig(-.25+b['bias']+fit+z)
    second=sig(.15+a['second_bias']+z+.4*eq[0])*sig(.15+b['second_bias']+z+.4*eq[0])
    rr=a['response_rate']*b['response_rate'];mutual=float(w@acceptance)*rr
    secondyes=float(w@(acceptance*second))*rr**2*.78
    timing=1 if variant!='delayed' else delayed_deadline_probability()
    return {'both_response':rr,'both_accept_unconditional':mutual,'date_unconditional':mutual*.78,'both_second_yes_unconditional':secondyes,'terminal':secondyes*.36*timing}

def labels(intro,events):
    rs=[e for e in events if e['event']=='introduction_response'];ds=[e for e in events if e['event']=='date_happened'];ss=[e for e in events if e['event']=='second_meeting_intention']
    bothresponse=len(rs)==2 and all(e['value'] is not None for e in rs)
    mutual=len(rs)==2 and all(e['value']=='yes' for e in rs)
    date=bool(ds and ds[0]['value']);bothyes=date and len(ss)==2 and all(e['value']=='yes' for e in ss)
    deadline=bool(bothyes and ds[0]['occurred_day']-intro['assigned_day']<=30 and all(e['occurred_day']-ds[0]['occurred_day']<=3 for e in ss))
    return dict(zip(STAGES,map(int,(bothresponse,mutual,date,bothyes,deadline))))

def calibration(rows,key='pred',reps=1000):
    result={};rng=np.random.default_rng(90210)
    seeds=sorted({r['seed'] for r in rows});indices={s:np.asarray([i for i,r in enumerate(rows) if r['seed']==s]) for s in seeds}
    for stage in STAGES:
        p=np.asarray([r[key][stage] for r in rows]);y=np.asarray([r['label'][stage] for r in rows]);clipped=np.clip(p,1e-9,1-1e-9)
        loss=-(y*np.log(clipped)+(1-y)*np.log1p(-clipped));brier=(p-y)**2
        bins=[];cuts=np.unique(np.quantile(p,np.linspace(0,1,6))) if len(p) else np.asarray([])
        if len(cuts)==1:cuts=np.asarray([cuts[0],cuts[0]])
        for j,(lo,hi) in enumerate(zip(cuts[:-1],cuts[1:])):
            mask=(p>=lo)&((p<=hi) if j==len(cuts)-2 else (p<hi));ix=np.flatnonzero(mask)
            if not len(ix):continue
            boot=[]
            for _ in range(reps):
                drawn=rng.choice(seeds,len(seeds),replace=True);sel=np.concatenate([indices[s] for s in drawn]);sel=sel[mask[sel]]
                if len(sel):boot.append(float(y[sel].mean()))
            bins.append({'n':len(ix),'predicted':float(p[ix].mean()),'observed':float(y[ix].mean()),'observed_ci95_seed_bootstrap':np.quantile(boot,[.025,.975]).tolist() if boot and len({rows[i]['seed'] for i in ix})>1 and not (all(y[ix]==0) or all(y[ix]==1)) else None,'uncertainty_note':'Bootstrap degenerate for zero-event/all-event cells; reliable bin uncertainty cannot be estimated from these observed clusters.' if all(y[ix]==0) or all(y[ix]==1) else ('Fewer than two contributing seed clusters.' if len({rows[i]['seed'] for i in ix})<2 else None),'supporting_seed_clusters':len({rows[i]['seed'] for i in ix}),'range':[float(lo),float(hi)]})
        result[stage]={'n_seed_clusters':len(seeds),'n':len(p),'events':int(y.sum()),'predicted_mean':float(p.mean()),'observed_mean':float(y.mean()),'log_loss':float(loss.mean()),'brier':float(brier.mean()),'signed_observed_minus_predicted_by_seed':interval([float(np.mean(y[ix]-p[ix])) for ix in indices.values()]),'log_loss_by_seed':interval([float(np.mean(loss[ix])) for ix in indices.values()]),'brier_by_seed':interval([float(np.mean(brier[ix])) for ix in indices.values()]),'roc_auc':float(stats.mannwhitneyu(p[y==1],p[y==0],alternative='two-sided').statistic/(sum(y==1)*sum(y==0))) if any(y==1) and any(y==0) else None,'reliability':bins,
          'scenario':{v:{'n':len(ix),'predicted_mean':float(p[ix].mean()),'observed_mean':float(y[ix].mean()),'log_loss':float(loss[ix].mean()),'brier':float(brier[ix].mean())} for v in evaluate.VARIANTS if len(ix:=np.asarray([i for i,r in enumerate(rows) if r['variant']==v]))}}
    return result

def conditional_calibration(rows):
    stages=collections.defaultdict(list)
    for r in rows:
        pred=r['pred'];snap=r['snapshot'];a=snap.get('user_a',snap.get('a',{}).get('member_id'));b=snap.get('user_b',snap.get('b',{}).get('member_id'))
        rs=[e for e in r['events'] if e['event']=='introduction_response'];ss=[e for e in r['events'] if e['event']=='second_meeting_intention'];ds=[e for e in r['events'] if e['event']=='date_happened']
        for e in rs:
            suffix='a' if e['member_id']==a else 'b'
            stages['directional_response'].append((r['seed'],pred['response_'+suffix],int(e['value'] is not None)))
            if e['value'] is not None:stages['directional_acceptance_given_response'].append((r['seed'],pred['accept_'+suffix],int(e['value']=='yes')))
        if r['label']['both_response']:stages['mutual_acceptance_given_both_response'].append((r['seed'],pred['both_accept_conditional'],r['label']['both_accept_unconditional']))
        if r['label']['both_accept_unconditional']:stages['date_given_mutual_acceptance'].append((r['seed'],pred['date_conditional'],r['label']['date_unconditional']))
        if r['label']['date_unconditional']:
            stages['both_positive_seconds_given_date'].append((r['seed'],pred['both_second_yes_unconditional']/max(1e-9,pred['date_unconditional']),r['label']['both_second_yes_unconditional']))
            for e in ss:
                suffix='a' if e['member_id']==a else 'b';key='second_'+suffix+'_given_mutual'
                if e['value'] is not None and key in pred:stages['directional_second_yes_given_response_and_date'].append((r['seed'],pred[key],int(e['value']=='yes')))
        if r['label']['both_second_yes_unconditional']:stages['qualified_given_both_positive_seconds'].append((r['seed'],pred['deadline_conditional'],r['label']['terminal']))
    out={}
    for key,values in stages.items():
        p=np.clip(np.asarray([v[1] for v in values]),1e-9,1-1e-9);y=np.asarray([v[2] for v in values]);loss=-(y*np.log(p)+(1-y)*np.log1p(-p))
        out[key]={'n':len(p),'events':int(y.sum()),'mean_predicted':float(p.mean()),'mean_observed':float(y.mean()),'log_loss':float(loss.mean()),'brier':float(((p-y)**2).mean()),'note':'Selected stage-eligible assignments, not unconditional population probability.'}
    return out

def slice_scores(rows):
    """Discrimination/calibration summaries for timing and sparse feedback, without fitting."""
    result={}
    for stage in STAGES:
        p=np.clip(np.asarray([r['pred'][stage] for r in rows]),1e-9,1-1e-9);y=np.asarray([r['label'][stage] for r in rows]);loss=-(y*np.log(p)+(1-y)*np.log1p(-p))
        result[stage]={'n':len(p),'events':int(y.sum()),'predicted_mean':float(p.mean()),'observed_mean':float(y.mean()),'log_loss':float(loss.mean()),'brier':float(((p-y)**2).mean()),'roc_auc':float(stats.mannwhitneyu(p[y==1],p[y==0]).statistic/(sum(y==1)*sum(y==0))) if any(y==1) and any(y==0) else None}
    return result

def calibrated_rollout(policy,variant,seed):
    from extended_policy import decide,DEFAULT
    from research.extended_candidates import CANDIDATES
    from research.terminal_model import predict_funnel
    cfg=dict(DEFAULT);cfg.update(CANDIDATES[policy]);memory=None;sim=Simulator(generate(seed,200,'evaluation',variant));snap={};daily=[];served=set();counts=collections.Counter()
    for day in range(60):
        for phase in ('ask','match'):
            request=json.loads(json.dumps({'phase':phase,'state':sim.observe(),'memory':memory},allow_nan=False))
            response=decide(request,cfg);response=evaluate.validate_response(json.loads(json.dumps(response,allow_nan=False)),phase);memory=response['memory']
            if phase=='ask':sim.resolve_asks(response['asks'])
            else:
                by={m['member_id']:m for m in request['state']['members']}
                for u,v in response['pairs']:
                    a,b=by[u],by[v];snap['|'.join(sorted((u,v)))+':'+str(day)]={'pred':predict_funnel(a,b,request['state'],memory,cfg),'snapshot':{'day':day,'a':copy.deepcopy(a),'b':copy.deepcopy(b)}}
                    served.update((u,v));counts.update((u,v))
                daily.append({'day':day,'assignments':len(response['pairs']),'verified_available':sum(all(m['fields'].get(k) is not None for k in HARD) and m['available'] for m in by.values())})
                sim.advance(response['pairs'])
    pending60=sum(e['observed_day']>=60 for e in sim.events)
    for _ in range(40):sim.advance([])
    byintro=collections.defaultdict(list)
    for e in sim.receive_feedback():byintro[e['introduction_id']].append(e)
    rows=[]
    for intro in sim.introductions:
        u,v=intro['user_a'],intro['user_b'];key='|'.join(sorted((u,v)))+':'+str(intro['assigned_day']);entry=snap[key]
        rows.append({'policy':policy,'variant':variant,'seed':seed,'introduction_id':intro['introduction_id'],'assigned_day':intro['assigned_day'],'pred':entry['pred'],'oracle':oracle_funnel(sim.members[u],sim.members[v],intro['assigned_day'],variant),'label':labels(intro,byintro[intro['introduction_id']]),'snapshot':entry['snapshot'],'events':byintro[intro['introduction_id']]})
    demo={}
    for field in ('gender','zone','age_group'):
        groups=collections.defaultdict(list)
        for m in sim.members.values():groups[m[field] if field!='age_group' else ('21–29' if m['age']<30 else '30–39' if m['age']<40 else '40–46')].append(m['member_id'])
        demo[field]={k:{'members':len(ids),'served':sum(i in served for i in ids),'introductions':sum(counts[i] for i in ids)} for k,ids in groups.items()}
    return rows,{'policy':policy,'variant':variant,'seed':seed,'metrics':sim.metrics(),'daily':daily,'pending_events_at_day60':pending60,'demographic_descriptive':demo,'repeat_assignments':sum(max(0,n-1) for n in counts.values())}

def trace_audit(trace_dir,policies=None,oracle=True):
    """Consume runner trajectories; no additional policy evaluation is performed."""
    allrows=[];episodes=[];worlds={}
    for path in sorted(Path(trace_dir).glob('*.json')):
        trace=json.loads(path.read_text());policy=trace['policy']
        if policies and policy not in policies:continue
        if not trace['assignment_snapshots'] or 'prediction' not in trace['assignment_snapshots'][0]:continue
        seed,variant=trace['seed'],trace['variant'];events=collections.defaultdict(list)
        for e in trace['completed_feedback']:events[e['introduction_id']].append(e)
        intros={('|'.join(sorted((i['user_a'],i['user_b'])))+':'+str(i['assigned_day'])):i for i in trace['introductions']}
        worldkey=(seed,variant)
        if oracle and worldkey not in worlds:worlds[worldkey]={m['member_id']:m for m in generate(seed,200,'evaluation',variant)['members']}
        served=set();counter=collections.Counter();funnel=collections.Counter()
        oracle_sum=0.;snapshot_unknown=collections.Counter()
        for snap in trace['assignment_snapshots']:
            u,v=snap['user_a'],snap['user_b'];intro=intros['|'.join(sorted((u,v)))+':'+str(snap['assigned_day'])]
            label=labels(intro,events[intro['introduction_id']]);funnel.update(label);served.update((u,v));counter.update((u,v))
            row={'policy':policy,'variant':variant,'seed':seed,'introduction_id':intro['introduction_id'],'assigned_day':intro['assigned_day'],
                 'pred':snap['prediction'],'label':label,'snapshot':snap,'events':events[intro['introduction_id']]}
            unknown=sum(snap[m]['fields'].get(k) is None for m in ('member_a','member_b') for k in ('relationship_goal','relationship_pace','lifestyle','conversations'))
            row['missing_soft_fields']=unknown;snapshot_unknown[unknown]+=1
            if oracle:
                w=worlds[worldkey];row['oracle']=oracle_funnel(w[u],w[v],intro['assigned_day'],variant);oracle_sum+=row['oracle']['terminal']
            allrows.append(row)
        demo={}
        for field in ('gender','zone','age_group'):
            groups=collections.defaultdict(list)
            for m in trace['final_public_members']:groups[m[field] if field!='age_group' else ('21–29' if m['age']<30 else '30–39' if m['age']<40 else '40–46')].append(m['member_id'])
            demo[field]={k:{'members':len(ids),'served':sum(i in served for i in ids),'introductions':sum(counter[i] for i in ids)} for k,ids in groups.items()}
        episodes.append({'policy':policy,'variant':variant,'seed':seed,'assignments':len(trace['assignment_snapshots']),
          'funnel_counts':dict(funnel),'oracle_sum_assigned_terminal':oracle_sum if oracle else None,
          'observed_terminal':funnel['terminal'],'realized_minus_oracle_conditional_sum':funnel['terminal']-oracle_sum if oracle else None,'repeat_assignments':sum(max(0,n-1) for n in counter.values()),
          'pending_events_at_day60':sum(e['observed_day']>=60 for es in events.values() for e in es),
          'snapshot_unknown_soft_histogram':dict(snapshot_unknown),'demographic_descriptive':demo,
          'late_feedback_both_yes':sum(r['label']['both_second_yes_unconditional'] and not r['label']['terminal'] for r in allrows if r['policy']==policy and r['variant']==variant and r['seed']==seed)})
    if not allrows:raise ValueError('No model prediction snapshots found')
    bypolicy={name:[r for r in allrows if r['policy']==name] for name in sorted({r['policy'] for r in allrows})}
    out={'scope':'OFFLINE trace audit; assignment-time predictions use only observations. Oracle probabilities are a separate hidden-truth audit and cannot train or authorize the policy.',
         'assignment_rows':allrows,'episodes':episodes,'calibration_by_policy':{p:calibration(rows) for p,rows in bypolicy.items()},
         'conditional_calibration_by_policy':{p:conditional_calibration(rows) for p,rows in bypolicy.items()},
         'marginal_product_reference_calibration':{p:calibration([dict(r,pred=dict(r['pred'],both_accept_unconditional=r['pred']['both_accept_independent'],terminal=r['pred']['terminal_independent'])) for r in rows]) for p,rows in bypolicy.items() if all('terminal_independent' in r['pred'] for r in rows)},
         'oracle_calibration_by_policy':{p:calibration(rows,'oracle') for p,rows in bypolicy.items()} if oracle else {},
         'calibration_by_history':{p:{label:slice_scores(rs) for label,rs in [('prior_feedback_lt20',[r for r in rows if r['snapshot'].get('prior_feedback',0)<20]),('prior_feedback_ge20',[r for r in rows if r['snapshot'].get('prior_feedback',0)>=20])] if rs} for p,rows in bypolicy.items()},
         'calibration_by_epoch_and_scenario':{p:{v:{label:slice_scores(rs) for label,rs in [('before35',[r for r in rows if r['variant']==v and r['assigned_day']<35]),('day35plus',[r for r in rows if r['variant']==v and r['assigned_day']>=35])] if rs} for v in evaluate.VARIANTS} for p,rows in bypolicy.items()},
         'calibration_by_missingness':{p:{str(n):calibration([r for r in rows if (r['missing_soft_fields']>=4 if n==4 else r['missing_soft_fields']==n)],reps=300) for n in range(5) if any((r['missing_soft_fields']>=4 if n==4 else r['missing_soft_fields']==n) for r in rows)} for p,rows in bypolicy.items()},
         'marginal_product_diagnostic_caveat':'Products of mixed marginal acceptance/second probabilities remove both common Gaussian dependence and feature/regime-mixture dependence. This is distinct from independent_fifo, which removes only common Gaussian dependence conditional on a mixture state.',
         'uncertainty':'Reliability intervals resample whole seed clusters. Signed calibration error, log-loss and Brier t intervals equally average within-seed assignment means, so their target differs slightly from pooled assignment-weighted means. Pooled assignment metrics target selected assignments, not all feasible pairs. Sparse terminal labels give weak discrimination evidence.',
         'demographics_caveat':'Synthetic descriptive associations only; demographic coverage is not a causal intervention.',
         'oracle_sum_caveat':'Sum of conditional oracle probabilities along realized assignments is a descriptive low-noise quality audit. Adaptation and retirement make this neither an oracle-policy score nor a causal mechanism proof.'}
    return out

def replay_graph_metrics(trace):
    """Replay recorded legal actions; graph calculations use recreated public observations.

    Before/after query comparisons hold simulator outcomes/actions fixed. They measure
    visibility expansion, not causal policy terminal-reward improvement.
    """
    import networkx as nx
    sim=Simulator(generate(trace['seed'],200,'evaluation',trace['variant']));daily=[]
    def graph(state):
        past={tuple(sorted((i['user_a'],i['user_b']))) for i in state['introductions']}
        members=[m for m in state['members'] if m['available'] and all(m['fields'].get(k) is not None for k in HARD) and not any(m['field_status'].get(k)=='declined' for k in HARD)]
        edges={tuple(sorted((a['member_id'],b['member_id']))) for a,b in itertools.combinations(members,2) if tuple(sorted((a['member_id'],b['member_id']))) not in past and eligibility(a,b)['status']=='feasible'}
        return edges,len(members)
    before=set()
    for phase,day,action in trace['actions']:
        if day!=sim.day:raise ValueError('Recorded trace day mismatch')
        if phase=='ask':before,_=graph(sim.observe());sim.resolve_asks(action)
        else:
            after,verified=graph(sim.observe());g=nx.Graph();g.add_edges_from(after)
            daily.append({'day':day,'verified_available_nodes':verified,'verified_feasible_untried_edges':len(after),'new_edges_from_queries':len(after-before),'maximum_cardinality':len(nx.max_weight_matching(g,maxcardinality=True)),
                          'largest_nonisolated_component':max((len(c) for c in nx.connected_components(g)),default=0),'assignments':len(action)})
            sim.advance(action)
    if sim.introductions!=trace['introductions']:raise ValueError('Replay introduction mismatch')
    return {'daily':daily,'mean_verified_available_nodes':float(np.mean([d['verified_available_nodes'] for d in daily])),
      'mean_verified_feasible_untried_edges':float(np.mean([d['verified_feasible_untried_edges'] for d in daily])),
      'total_new_edges_from_queries':sum(d['new_edges_from_queries'] for d in daily),
      'mean_maximum_cardinality':float(np.mean([d['maximum_cardinality'] for d in daily])),
      'mean_largest_nonisolated_component':float(np.mean([d['largest_nonisolated_component'] for d in daily])),
      'scope':'Recorded actions replayed with identical public observations. Before/after asks isolate realized visibility changes only, not expected matching value or causal terminal reward.'}

def mechanism_audit(trace_dir,policies=None,reference='greedy',replay_graphs=False):
    """All selected trajectories, including legacy policies without prediction fields."""
    output=[];worlds={};representative={};oraclecache={};queryplans={}
    for path in sorted(Path(trace_dir).glob('*.json')):
        t=json.loads(path.read_text());p,v,s=t['policy'],t['variant'],t['seed']
        if policies and p not in policies and p!=reference:continue
        key=(s,v)
        if key not in worlds:worlds[key]={m['member_id']:m for m in generate(s,200,'evaluation',v)['members']}
        events=collections.defaultdict(list)
        for e in t['completed_feedback']:events[e['introduction_id']].append(e)
        member_counts=collections.Counter();busy=[];qsum=0.;funnel=collections.Counter();retired=set();details=[]
        latefeedback=latedate=0
        for i in t['introductions']:
            u,w=i['user_a'],i['user_b'];member_counts.update((u,w));es=events[i['introduction_id']];ys=labels(i,es);funnel.update(ys)
            ds=[e for e in es if e['event']=='date_happened'];ss=[e for e in es if e['event']=='second_meeting_intention'];busy.append(ds[0]['occurred_day']-i['assigned_day']+6 if ds else 8)
            for e in es:
                if e['event']=='pause_after_mutual_interest':retired.update((u,w))
            if ys['both_second_yes_unconditional']:
                latedate+=ds[0]['occurred_day']-i['assigned_day']>30;latefeedback+=any(e['occurred_day']-ds[0]['occurred_day']>3 for e in ss)
            ok=(s,v,u,w,i['assigned_day'])
            if ok not in oraclecache:oraclecache[ok]=oracle_funnel(worlds[key][u],worlds[key][w],i['assigned_day'],v)
            q=oraclecache[ok]['terminal'];qsum+=q
            details.append({'dyad':[u,w],'assignment_day':i['assigned_day'],'oracle_terminal':q,'observed_labels':ys,'busy_duration':busy[-1],'events':es})
        asks=[(d,a) for phase,d,actions in t['actions'] if phase=='ask' for a in actions]
        queryplans[p,v,s]={d:sorted((a['member_id'],a['field']) for a in acts) for phase,d,acts in t['actions'] if phase=='ask'}
        askcost=sum(3 if a['field']=='constraints' else 1 for d,a in asks)
        demo={}
        for field in ('gender','zone','age_group'):
            groups=collections.defaultdict(list)
            for m in t['final_public_members']:groups[m[field] if field!='age_group' else ('21–29' if m['age']<30 else '30–39' if m['age']<40 else '40–46')].append(m['member_id'])
            demo[field]={k:{'members':len(ids),'served':sum(member_counts[x]>0 for x in ids),'assignments':sum(member_counts[x] for x in ids)} for k,ids in groups.items()}
        knownsoft=[sum(snap[m]['fields'].get(k) is not None for m in ('member_a','member_b') for k in ('relationship_goal','relationship_pace','lifestyle','conversations')) for snap in t['assignment_snapshots']]
        row={'policy':p,'variant':v,'seed':s,'assignments':len(t['introductions']),'served':len(member_counts),'repeat_endpoint_assignments':sum(max(0,n-1) for n in member_counts.values()),
          'funnel':dict(funnel),'qualified_per100':.5*funnel['terminal'],'oracle_sum_assigned_terminal':qsum,'oracle_mean_assignment_quality':qsum/max(1,len(t['introductions'])),'realized_minus_oracle_conditional_sum':funnel['terminal']-qsum,
          'hard_bundle_queries':sum(a['field']=='constraints' for d,a in asks),'soft_queries':sum(a['field']!='constraints' for d,a in asks),'ask_cost':askcost,
          'assigned_before_day35':sum(i['assigned_day']<35 for i in t['introductions']),'mean_known_soft_fields_of8':float(np.mean(knownsoft)) if knownsoft else None,
          'busy_mean':float(np.mean(busy)) if busy else 0.,'busy_max':max(busy,default=0),'retired_members':len(retired),'late_date_bothpositive':latedate,'late_feedback_bothpositive':latefeedback,'demographics':demo}
        if replay_graphs:row['public_graph_replay']=replay_graph_metrics(t)
        output.append(row);representative[(p,v,s)]=details
    for row in output:
        key=(reference,row['variant'],row['seed'])
        if key in queryplans:
            refplan=queryplans[key];own=queryplans[row['policy'],row['variant'],row['seed']]
            row['ask_schedule_difference_days_vs_reference']=[d for d in sorted(set(refplan)|set(own)) if refplan.get(d)!=own.get(d)]
    grouped=collections.defaultdict(lambda:collections.defaultdict(list))
    for r in output:grouped[r['policy']][r['seed']].append(r)
    trajectories=[]
    for p,seedrows in grouped.items():
        if p==reference or reference not in grouped:continue
        differences={s:float(np.mean([r['qualified_per100'] for r in rs]))-float(np.mean([r['qualified_per100'] for r in grouped[reference][s]])) for s,rs in seedrows.items() if s in grouped[reference] and len(rs)==6 and len(grouped[reference][s])==6}
        chosen=[]
        if differences:chosen=[max(differences,key=differences.get),min(differences,key=differences.get)]
        for s in sorted(set(chosen)):
            relevant=[r for r in seedrows[s] if r['funnel'].get('terminal',0)!=next(x for x in grouped[reference][s] if x['variant']==r['variant'])['funnel'].get('terminal',0)]
            trajectories.append({'policy':p,'seed':s,'scenario_balanced_difference':differences[s],'families':[
              {'variant':r['variant'],'candidate_summary':r,'reference_summary':next(x for x in grouped[reference][s] if x['variant']==r['variant']),
               'candidate_introductions':representative[p,r['variant'],s],'reference_introductions':representative[reference,r['variant'],s]} for r in relevant]})
    return {'scope':'OFFLINE conditional quality and completed trajectory audit. Evaluated policies remain observation-only.',
      'episodes':output,'representative_largest_positive_negative_seed_clusters':trajectories,'all_queried_schedules_equal_to_reference':all(not r.get('ask_schedule_difference_days_vs_reference',[]) for r in output),'representative_selection_note':'Maximum and minimum paired cluster differences are selected; both can have the same sign.',
      'caveats':['Oracle summed assignment probabilities are descriptive low-noise quality measures along realized trajectories, not expected full-policy rewards or causal effects.',
                  'Busy durations include cancellation lockout; positive but unqualified seconds can retire both members.',
                  'Demographic coverage is synthetic descriptive association, not causal discrimination evidence.',
                  'Known soft fields are an assignment snapshot proxy. Optional public-graph replay reconstructs the exact observation history from recorded legal actions.']}

def common_cohort_audit(trace_dir):
    """Prospective teacher-forced validation on identical recorded greedy assignments.

    Four independent model memories receive exactly the same observation histories.
    No model chooses an action, and no model or configuration is changed by this audit.
    """
    from extended_policy import DEFAULT
    from research.extended_candidates import CANDIDATES
    from research.terminal_model import update_memory,predict_funnel,equality_probabilities
    names=('terminal_fifo','independent_fifo','simple_fifo','no_learning_fifo');cohort=[]
    for path in sorted(Path(trace_dir).glob('greedy_*.json')):
        trace=json.loads(path.read_text());seed,variant=trace['seed'],trace['variant'];sim=Simulator(generate(seed,200,'evaluation',variant))
        memories={n:None for n in names};configs={n:dict(DEFAULT,**CANDIDATES[n]) for n in names};snapshots=[]
        for phase,day,action in trace['actions']:
            state=json.loads(json.dumps(sim.observe(),allow_nan=False))
            if day!=state['day']:raise ValueError('Common-cohort replay day mismatch')
            for name in names:memories[name]=update_memory(state,memories[name],configs[name])
            if phase=='ask':sim.resolve_asks(action)
            else:
                by={m['member_id']:m for m in state['members']}
                for u,v in action:
                    predictions={}
                    for name in names:
                        memory=memories[name];pred=predict_funnel(by[u],by[v],state,memory,configs[name]);predictions[name]=pred
                        key='|'.join(sorted((u,v)))+':'+str(day)
                        memory['snapshots'][key]={'day':day,'users':[u,v],'equal':list(equality_probabilities(by[u],by[v])),'pred':pred}
                    snapshots.append({'user_a':u,'user_b':v,'assigned_day':day,'member_a':by[u],'member_b':by[v],
                      'prior_feedback':len(state['feedback']),'prior_introductions':len(state['introductions']),'model_predictions':predictions})
                sim.advance(action)
        if sim.introductions!=trace['introductions']:raise ValueError('Common-cohort greedy action replay failed')
        for _ in range(40):sim.advance([])
        events=collections.defaultdict(list)
        for e in sim.receive_feedback():events[e['introduction_id']].append(e)
        intros={('|'.join(sorted((i['user_a'],i['user_b'])))+':'+str(i['assigned_day'])):i for i in sim.introductions}
        for snap in snapshots:
            i=intros['|'.join(sorted((snap['user_a'],snap['user_b'])))+':'+str(snap['assigned_day'])]
            cohort.append({'seed':seed,'variant':variant,'assigned_day':snap['assigned_day'],'introduction_id':i['introduction_id'],
              'label':labels(i,events[i['introduction_id']]),'events':events[i['introduction_id']],'snapshot':snap,
              'model_predictions':snap.pop('model_predictions')})
        print('Common cohort',variant,seed,len(snapshots),flush=True)
    if not cohort:raise ValueError('No greedy cohort trajectories')
    cal={};conditional={};rowsbymodel={}
    for name in names:
        rows=[dict(r,pred=r['model_predictions'][name]) for r in cohort];rowsbymodel[name]=rows;cal[name]=calibration(rows);conditional[name]=conditional_calibration(rows)
    comparisons=[];cluster_losses={}
    for name,rows in rowsbymodel.items():
        for stage in STAGES:
            for metric in ('log_loss','brier'):
                by=collections.defaultdict(lambda:collections.defaultdict(list))
                for r in rows:
                    p=max(1e-9,min(1-1e-9,r['pred'][stage]));y=r['label'][stage]
                    loss=-(y*math.log(p)+(1-y)*math.log1p(-p)) if metric=='log_loss' else (p-y)**2
                    by[r['seed']][r['variant']].append(loss)
                vals={s:float(np.mean([np.mean(fs[v]) for v in evaluate.VARIANTS])) for s,fs in by.items() if set(fs)==set(evaluate.VARIANTS)}
                cluster_losses[name,stage,metric]=vals
                if name!='terminal_fifo':
                    ref=cluster_losses['terminal_fifo',stage,metric];seeds=sorted(set(vals)&set(ref));diff=np.asarray([vals[s]-ref[s] for s in seeds])
                    comparisons.append({'model':name,'reference':'terminal_fifo','stage':stage,'metric':metric,'difference':interval(diff),'paired_t_p':paired_p(diff),'seeds':seeds,
                      'interpretation':'Negative loss difference favors this model on the identical greedy-selected prospective cohort.'})
    tests=[c for c in comparisons if c['paired_t_p'] is not None]
    for c,p in zip(tests,holm([c['paired_t_p'] for c in tests])):c['holm_all_30_exploratory_p']=p
    for stage in STAGES:
        for metric in ('log_loss','brier'):
            subset=[c for c in tests if c['stage']==stage and c['metric']==metric]
            for c,p in zip(subset,holm([c['paired_t_p'] for c in subset])):c['holm_three_models_within_stage_metric_p']=p
    return {'scope':'OFFLINE prospective validation on identical recorded greedy DEVELOPMENT assignments and histories. No evaluated actions are chosen here; no model/config is modified or trained across episodes.',
       'models':list(names),'independent_seed_clusters':len({r['seed'] for r in cohort}),'assignment_rows':cohort,'calibration_by_model':cal,'conditional_calibration_by_model':conditional,
       'family_balanced_cluster_loss_summaries':{name:{stage:{metric:interval(list(cluster_losses[name,stage,metric].values())) for metric in ('log_loss','brier')} for stage in STAGES} for name in names},
       'paired_proper_loss_comparisons':comparisons,'comparison_weighting':'Within each seed, equally average six family mean assignment losses; pair those seed values across models.',
       'caveats':['This establishes predictive performance on greedy-selected contexts, not terminal reward superiority when models allocate different pairs.',
                  'Model memories learn only from observation histories visible at each replayed action time. Assignment snapshots precede all outcomes for that introduction.',
                  'Eight development seed clusters and rare terminal labels provide exploratory evidence only. All30 stage/metric/model comparisons receive global Holm adjustment; within-stage3 adjustment also recorded.',
                  'Simple directional conditional fields are auxiliary parametric diagnostics; primary joint predictions are direct mature empirical counts.']}


def draw_common_cohort(data,path):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    names=data['models'];fig,axes=plt.subplots(2,5,figsize=(18,7))
    for j,stage in enumerate(STAGES):
        for row,(metric,key) in enumerate((('log_loss','log_loss_by_seed'),('brier','brier_by_seed'))):
            ax=axes[row,j];means=[];errors=[]
            for name in names:
                entry=data['family_balanced_cluster_loss_summaries'][name][stage][metric];means.append(entry['mean']);errors.append(entry['mean']-entry['ci95'][0] if entry['ci95'] else 0.)
            ax.bar(range(len(names)),means,yerr=errors,capsize=3,color=['#276b85','#999999','#bd6d35','#668c56']);ax.set_xticks(range(len(names)),[n.replace('_','\n') for n in names],fontsize=7);ax.set_title(stage.replace('_unconditional','').replace('_',' '));ax.set_ylabel(metric.replace('_',' '));ax.grid(axis='y',alpha=.2)
    fig.suptitle('Identical greedy development cohort: model proper losses, seed-cluster intervals');fig.tight_layout();fig.savefig(path,dpi=160);plt.close(fig)

def draw_calibration(data,path):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,5,figsize=(17,3.5))
    for ax,stage in zip(axes,STAGES):
        bins=data[stage]['reliability'];p=[b['predicted'] for b in bins];y=[b['observed'] for b in bins]
        lo=[max(0,b['observed']-b['observed_ci95_seed_bootstrap'][0]) if b['observed_ci95_seed_bootstrap'] else 0. for b in bins];hi=[max(0,b['observed_ci95_seed_bootstrap'][1]-b['observed']) if b['observed_ci95_seed_bootstrap'] else 0. for b in bins]
        ax.errorbar(p,y,yerr=[lo,hi],fmt='o',capsize=3);missing=[j for j,b in enumerate(bins) if b['observed_ci95_seed_bootstrap'] is None]
        if missing:ax.scatter([p[j] for j in missing],[y[j] for j in missing],marker='x',s=65,c='#bc6027',zorder=4)
        m=max(p+y+[.025])*1.12;ax.plot([0,m],[0,m],ls='--',color='gray');ax.set_xlim(0,m);ax.set_ylim(0,m);ax.set_title(stage.replace('_unconditional','').replace('_',' '));ax.set_xlabel('Predicted');ax.set_ylabel('Observed')
    fig.suptitle('95% seed-bootstrap intervals where estimable; × lacks reliable bin uncertainty' if data[STAGES[0]].get('n_seed_clusters',0)>1 else 'Single-cluster debug audit; uncertainty cannot be estimated');fig.tight_layout();fig.savefig(path,dpi=160);plt.close(fig)

def draw_mechanisms(data,path):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows=data['episodes'];names=sorted({r['policy'] for r in rows})
    fields=(('qualified_per100','Qualified MSMI/100'),('oracle_sum_assigned_terminal','Sum oracle q on realized assignments'),('assignments','Assignments'),('repeat_endpoint_assignments','Repeat endpoint assignments'),('busy_mean','Mean busy duration (days)'),('ask_cost','Ask cost'))
    fig,axes=plt.subplots(2,3,figsize=(15,8))
    for ax,(field,title) in zip(axes.flat,fields):
        means=[];errors=[]
        for name in names:
            by=collections.defaultdict(list)
            for r in rows:
                if r['policy']==name:by[r['seed']].append(r[field])
            result=interval([np.mean(v) for v in by.values()]);means.append(result['mean']);errors.append(result['mean']-result['ci95'][0] if result['ci95'] else 0.)
        ax.bar(range(len(names)),means,yerr=errors,capsize=3,color=['#777777' if n=='greedy' else '#276b85' for n in names]);ax.set_xticks(range(len(names)),[n.replace('_','\n') for n in names],fontsize=8);ax.set_title(title);ax.grid(axis='y',alpha=.2)
    fig.suptitle('Descriptive trajectory mechanisms; 95% seed-cluster t intervals' if len({r['seed'] for r in rows})>1 else 'Single-cluster debug mechanisms; uncertainty cannot be estimated');fig.tight_layout();fig.savefig(path,dpi=160);plt.close(fig)

def main():
    p=argparse.ArgumentParser();p.add_argument('--calibration-policy');p.add_argument('--traces');p.add_argument('--common-cohort',action='store_true');p.add_argument('--mechanisms',action='store_true');p.add_argument('--replay-graphs',action='store_true');p.add_argument('--policies');p.add_argument('--seeds',default='1001,1002');p.add_argument('--output',default='results/extended/audit.json');a=p.parse_args();target=Path(a.output);target.parent.mkdir(parents=True,exist_ok=True)
    if a.traces and a.common_cohort:
        out=common_cohort_audit(a.traces);target.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');draw_common_cohort(out,target.with_suffix('.png'));print('Common-cohort assignments',len(out['assignment_rows']))
    elif a.traces and a.mechanisms:
        out=mechanism_audit(a.traces,a.policies.split(',') if a.policies else None,replay_graphs=a.replay_graphs);target.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');draw_mechanisms(out,target.with_suffix('.png'));print('Mechanism episodes',len(out['episodes']))
    elif a.traces:
        out=trace_audit(a.traces,a.policies.split(',') if a.policies else None);target.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
        for name,data in out['calibration_by_policy'].items():draw_calibration(data,target.with_name(target.stem+'_'+name+'.png'))
        print('Audited',len(out['assignment_rows']),'assignment snapshots')
    elif a.calibration_policy:
        rows=[];episodes=[]
        for s in map(int,a.seeds.split(',')):
            for v in evaluate.VARIANTS:
                rr,e=calibrated_rollout(a.calibration_policy,v,s);rows.extend(rr);episodes.append(e);print(a.calibration_policy,v,s,len(rr),flush=True)
        out={'scope':'OFFLINE audit. Policy receives observation-only JSON. Oracle probabilities use hidden actors/truth solely as audit comparators. No audit result authorizes a match.','assignment_rows':rows,'episodes':episodes,'calibration':calibration(rows),'oracle_calibration':calibration(rows,'oracle'),'uncertainty':'Reliability uncertainty resamples whole seed clusters; development seeds provide exploratory uncertainty, not confirmation.','demographics_caveat':'Synthetic descriptive associations, no causal demographic claim.'}
        target.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');draw_calibration(out['calibration'],target.with_suffix('.png'))
    else:
        out=starting_audit();target.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print('Reproduced',sum(r['equal'] for r in out['reproduction']),'/',len(out['reproduction']),flush=True)
if __name__=='__main__':main()
