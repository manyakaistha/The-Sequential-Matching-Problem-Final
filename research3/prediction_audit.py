"""Independent same-cohort probability audit and privileged diagnostics.
Only old seeds1001--1008. This analysis module must never be packaged in policy.
"""
import collections
import functools
import hashlib
import itertools
import json
import math
import time
from pathlib import Path
import numpy as np
from scipy.special import expit
from scipy.stats import rankdata, t
from kit import generate, Simulator, eligibility
from research3.model_candidates import OFFLINE_WEIGHTS

FIELDS=('relationship_goal','relationship_pace','lifestyle','conversations')
SIZES=(2,3,3,4)
STAGES=('both_response','both_accept_unconditional','date_unconditional','both_second_yes_unconditional','terminal')
N,W=np.polynomial.hermite.hermgauss(15);N=N*math.sqrt(2);W=W/math.sqrt(math.pi)
RMEAN=.765; RSECOND=(.55**2+.55*.98+.98**2)/3
VAR=(.98-.55)**2/12; CONC=RMEAN*(1-RMEAN)/VAR-1


def eq_prob(a,b,truth=False):
    return tuple(float(a['truth' if truth else 'fields'][k]==b['truth' if truth else 'fields'][k]) if truth or (a['fields'].get(k) is not None and b['fields'].get(k) is not None) else 1/size for k,size in zip(FIELDS,SIZES))

@functools.lru_cache(maxsize=24000)
def integrated(eq,day,regime,actor=None):
    weights=(.25,.8,-.25,.5) if regime=='shift' else (.7,.4,.25,.2)
    drift=-.5 if regime=='drift' and day>=35 else 0.
    uncertain=[i for i,p in enumerate(eq) if 0<p<1];accept=full=0.
    for bits in itertools.product((0,1),repeat=len(uncertain)):
        e=list(eq);mass=1.
        for i,bit in zip(uncertain,bits):mass*=eq[i] if bit else 1-eq[i];e[i]=bit
        base=-.25+sum(w*(1 if v else -.5) for w,v in zip(weights,e))+drift
        second=.15+.4*e[0]
        if actor is None:
            a=np.sum(expit(base+.45*N[:,None]+.7*N[None,:])*W[None,:],axis=1)
            b=a
            c=np.sum(expit(second+.45*N[:,None]+.5*N[None,:])*W[None,:],axis=1);d=c
        else:
            a=expit(base+.45*N+actor[0]);b=expit(base+.45*N+actor[1])
            c=expit(second+.45*N+actor[2]);d=expit(second+.45*N+actor[3])
        accept+=mass*float(W@(a*b));full+=mass*float(W@(a*b*c*d))
    return accept,full

def funnel(a,b,day,response=None,private=None,truth=False):
    eq=eq_prob(a,b,truth)
    if private is None:
        normal=integrated(eq,min(day,35),'development');shift=integrated(eq,min(day,35),'shift');drift=integrated(eq,min(day,35),'drift')
        accept=(4*normal[0]+shift[0]+drift[0])/6
        full=(4*normal[1]+shift[1]+drift[1])/6
        qualified=((3+671/686)*normal[1]+shift[1]+drift[1])/6
        rm=(RMEAN,RMEAN);rs=(RSECOND,RSECOND)
        if response is not None:
            moments=[]
            for member in (a,b):
                yes,no=response.get(member['member_id'],(0,0));aa=RMEAN*CONC+yes;bb=(1-RMEAN)*CONC+no
                moments.append((aa/(aa+bb),aa*(aa+1)/((aa+bb)*(aa+bb+1))))
            rm=tuple(x[0] for x in moments);rs=tuple(x[1] for x in moments)
    else:
        pa,pb,variant=private
        accept,full=integrated(eq,min(day,35),variant,(pa['bias'],pb['bias'],pa['second_bias'],pb['second_bias']))
        qualified=full*(671/686 if variant=='delayed' else 1)
        rm=(pa['response_rate'],pb['response_rate']);rs=tuple(x*x for x in rm)
    r=rm[0]*rm[1];r2=rs[0]*rs[1]
    return dict(zip(STAGES,(r,r*accept,.78*r*accept,.78*r2*full,.78*.36*r2*qualified)))

def proper(p,y):
    p=np.clip(np.asarray(p),1e-12,1-1e-12);y=np.asarray(y)
    auc=None
    if 0<y.sum()<len(y):auc=float((rankdata(p)[y==1].sum()-y.sum()*(y.sum()+1)/2)/(y.sum()*(len(y)-y.sum())))
    return {'n':len(y),'positive':int(y.sum()),'predicted_mean':float(p.mean()),'observed_mean':float(y.mean()),'log_loss':float(-(y*np.log(p)+(1-y)*np.log1p(-p)).mean()),'brier':float(((p-y)**2).mean()),'auc':auc}

def interval(values):
    a=np.asarray(values);n=len(a);mean=float(a.mean());se=float(a.std(ddof=1)/math.sqrt(n)) if n>1 else None
    rng=np.random.default_rng(20261009);boot=np.mean(rng.choice(a,size=(5000,n),replace=True),axis=1)
    return {'clusters':n,'mean':mean,'t95':[mean-float(t.ppf(.975,n-1))*se,mean+float(t.ppf(.975,n-1))*se] if n>1 else None,'cluster_bootstrap95':np.quantile(boot,[.025,.975]).tolist()}

def audit_group(rows):
    output={}
    for model in sorted(rows[0]['pred']):
        output[model]={}
        for stage in rows[0]['pred'][model]:
            vals=[r['pred'][model][stage] for r in rows];labels=[r['label'][stage] for r in rows]
            item=proper(vals,labels)
            per_seed=[]
            for seed in sorted(set(r['seed'] for r in rows)):
                rs=[r for r in rows if r['seed']==seed];per_seed.append(proper([r['pred'][model][stage] for r in rs],[r['label'][stage] for r in rs]))
            item['seed_balanced']={key:interval([s[key] for s in per_seed]) for key in ('log_loss','brier','predicted_mean','observed_mean')}
            # Stage conditional calibration on identical eligible examples.
            prior={'both_accept_unconditional':'both_response','date_unconditional':'both_accept_unconditional','both_second_yes_unconditional':'date_unconditional','terminal':'both_second_yes_unconditional'}.get(stage)
            if prior and prior in rows[0]['pred'][model]:
                eligible=[r for r in rows if r['label'][prior]]
                if eligible:item['stage_conditional']=proper([r['pred'][model][stage]/max(1e-12,r['pred'][model][prior]) for r in eligible],[r['label'][stage] for r in eligible])
            output[model][stage]=item
    return output

def main():
    started=time.process_time()
    source=Path('results/extended/audit_common_cohort_calibration.json');raw=json.loads(source.read_text())['assignment_rows']
    train=[r for r in raw if r['seed']<=1005];constant={k:float(np.mean([r['label'][k] for r in train])) for k in STAGES}
    traces={};worlds={};rows=[];max_error=0.
    for old in raw:
        key=(old['seed'],old['variant'])
        if key not in traces:
            traces[key]=json.loads(Path(f'results/extended/development_traces/greedy_{key[1]}_{key[0]}.json').read_text())
            worlds[key]={m['member_id']:m for m in generate(key[0],200,'evaluation',key[1])['members']}
        snap=old['snapshot'];a,b=snap['member_a'],snap['member_b'];day=old['assigned_day'];events=traces[key]['completed_feedback'];counts=collections.defaultdict(lambda:[0,0])
        es=[e for e in events if e['introduction_id']==old['introduction_id']]
        rs=[e for e in es if e['event']=='introduction_response'];ds=[e for e in es if e['event']=='date_happened' and e['value']];ss=[e for e in es if e['event']=='second_meeting_intention']
        values=(len(rs)==2 and all(e['value'] is not None for e in rs),len(rs)==2 and all(e['value']=='yes' for e in rs),bool(ds),len(ss)==2 and all(e['value']=='yes' for e in ss),bool(ds) and len(ss)==2 and ds[0]['occurred_day']-day<=30 and all(e['value']=='yes' and e['occurred_day']-ds[0]['occurred_day']<=3 for e in ss))
        assert dict(zip(STAGES,map(int,values)))==old['label']
        for m in (a,b):
            assert all(v is None or m['field_observed_day'][k]<=day for k,v in m['fields'].items())
        # Only public labels already observed before this assignment; future labels never features.
        for e in events:
            if e['observed_day']<=day and e['event'] in ('introduction_response','second_meeting_intention') and e['member_id']:
                counts[e['member_id']][0 if e['value'] is not None else 1]+=1
        pa,pb=(worlds[key][m['member_id']] for m in (a,b))
        for obs,private in ((a,pa),(b,pb)):
            assert all(v is None or v==private['truth'][k] for k,v in obs['fields'].items())
        x=(1.,)+tuple(v-prior for v,prior in zip(eq_prob(a,b),(.5,1/3,1/3,.25)))+(float(day>=35),)
        pred={'constant':constant,'population':funnel(a,b,day),'response':funnel(a,b,day,counts),'offline':{'terminal':float(expit(sum(w*v for w,v in zip(OFFLINE_WEIGHTS,x))))},'known_parameter_missing':funnel(a,b,day,private=(pa,pb,key[1])),'full_truth_edge':funnel(pa,pb,day,private=(pa,pb,key[1]),truth=True)}
        for model,probs in pred.items():
            if len(probs)==5:
                assert all(0<=probs[k]<=1 for k in STAGES) and all(probs[b]<=probs[a]+1e-12 for a,b in zip(STAGES,STAGES[1:]))
        from research3.model_candidates import population
        max_error=max(max_error,abs(pred['population']['terminal']-population(a,b,day)[0]))
        rows.append({'seed':key[0],'variant':key[1],'day':day,'history':snap['prior_feedback'],'missing':sum(m['fields'].get(k) is None for m in (a,b) for k in FIELDS),'label':old['label'],'pred':pred})
    validation=[r for r in rows if r['seed']>=1006]
    analysis=audit_group(validation)
    contrasts={}
    for model in ('population','response','offline','known_parameter_missing','full_truth_edge'):
        differences=[]
        for seed in (1006,1007,1008):
            rs=[r for r in validation if r['seed']==seed];y=[r['label']['terminal'] for r in rs]
            differences.append(proper([r['pred'][model]['terminal'] for r in rs],y)['log_loss']-proper([r['pred']['constant']['terminal'] for r in rs],y)['log_loss'])
        contrasts[model+'_minus_constant_terminal_logloss']=interval(differences)
    slices={}
    groups={'variant':lambda r:r['variant'],'time':lambda r:'late35plus' if r['day']>=35 else 'early','missing':lambda r:str(min(4,r['missing'])),'history':lambda r:'20plus' if r['history']>=20 else 'under20'}
    for axis,fn in groups.items():
        slices[axis]={}
        for value in sorted(set(fn(r) for r in validation)):
            rs=[r for r in validation if fn(r)==value];slices[axis][value]={model:proper([r['pred'][model]['terminal'] for r in rs],[r['label']['terminal'] for r in rs]) for model in analysis}
    reliability={}
    bins=(0,.005,.01,.02,.04,1.)
    for model in analysis:
        reliability[model]=[]
        for lo,hi in zip(bins,bins[1:]):
            rs=[r for r in validation if lo<=r['pred'][model]['terminal']<hi]
            if not rs:continue
            item=proper([r['pred'][model]['terminal'] for r in rs],[r['label']['terminal'] for r in rs]);item['bin']=[lo,hi]
            clusters=[r for r in sorted(set(z['seed'] for z in rs))]
            # Fixed bins; resample whole seeds and form ratio of pooled positives/counts.
            totals=np.array([[sum(z['label']['terminal'] for z in rs if z['seed']==seed),sum(z['seed']==seed for z in rs)] for seed in clusters]);rng=np.random.default_rng(12); sampled=totals[rng.integers(0,len(totals),(5000,len(totals)))].sum(axis=1)
            item['supporting_seeds']=len(clusters)
            item['observed_cluster_bootstrap95']=np.quantile(sampled[:,0]/sampled[:,1],[.025,.975]).tolist() if len(clusters)>=3 and 0<item['positive']<item['n'] else None
            item['interval_caveat']='No informative bootstrap interval for fewer than3 supporting seeds or degenerate event cells; point is descriptive.' if item['observed_cluster_bootstrap95'] is None else 'Only3 validation clusters; finite-support bootstrap descriptive, not calibrated bin-wise confidence.'
            reliability[model].append(item)
    oracle=current_edge_oracles(traces,worlds)
    result={'scope':'old baseline-selected assignment cohort only; validation1006--1008; all-family clustered by seed; exploratory','input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'train_seeds':list(range(1001,1006)),'validation_seeds':list(range(1006,1009)),'n_train':len(train),'n_validation':len(validation),'prediction_rows':rows,'validation':analysis,'contrasts':contrasts,'slices':slices,'reliability':reliability,'quadrature15_vs_deployed5_max_terminal_abs':max_error,'oracle_diagnostics':oracle,'cpu_seconds':time.process_time()-started}
    Path('results/research3/prediction_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(7,5));ax.plot([0,.07],[0,.07],'k--',lw=1)
    for model in ('constant','population','response','offline','full_truth_edge'):
        data=reliability[model];good=[r for r in data if r['observed_cluster_bootstrap95'] is not None];bad=[r for r in data if r['observed_cluster_bootstrap95'] is None]
        xx=[r['predicted_mean'] for r in good];yy=[r['observed_mean'] for r in good];low=[r['observed_cluster_bootstrap95'][0] for r in good];high=[r['observed_cluster_bootstrap95'][1] for r in good];draw=ax.errorbar(xx,yy,yerr=[[max(0,y-l) for y,l in zip(yy,low)],[max(0,h-y) for y,h in zip(yy,high)]],fmt='o',capsize=3,label=model)
        ax.scatter([r['predicted_mean'] for r in bad],[r['observed_mean'] for r in bad],marker='x',color=draw.lines[0].get_color())
    ax.set(xlabel='Predicted terminal probability',ylabel='Observed terminal rate',title='Old held-out seed cohort; only 14 positives / 3 clusters');ax.legend(fontsize=8);fig.text(.02,.005,'Crosses: interval unavailable (degenerate bin or fewer than3 seeds). All bins are exploratory.',fontsize=8);fig.tight_layout(rect=(0,.03,1,1));fig.savefig('results/research3/prediction_reliability.png',dpi=160);plt.close(fig)
    print(json.dumps({'cpu_seconds':result['cpu_seconds'],'validation_terminal':{k:v['terminal'] for k,v in analysis.items()},'contrasts':contrasts,'oracle':oracle['summary']},indent=2))


def current_edge_oracles(traces,worlds):
    """Privileged one-step optimization on public legal graphs along old baseline.
    Not a bound on dynamic optimum and never substitutes counterfactual outcomes.
    """
    import networkx as nx
    output=[]
    for (seed,variant),trace in sorted(traces.items()):
        sim=Simulator(generate(seed,200,'evaluation',variant));by_truth=worlds[(seed,variant)]
        for phase,day,action in trace['actions']:
            assert sim.day==day
            if phase=='ask':sim.resolve_asks(action);continue
            if day in (0,20,40,59):
                state=sim.observe();members=[m for m in state['members'] if m['available']];past={tuple(sorted((i['user_a'],i['user_b']))) for i in state['introductions']};scores={};graphs={name:nx.Graph() for name in ('observation_prior','known_parameter_missing','full_truth')}
                for a,b in itertools.combinations(members,2):
                    pair=tuple(sorted((a['member_id'],b['member_id'])))
                    if pair in past or eligibility(a,b)['status']!='feasible':continue
                    pa,pb=by_truth[a['member_id']],by_truth[b['member_id']]
                    q=funnel(pa,pb,day,private=(pa,pb,variant),truth=True)['terminal'];scores[pair]=q
                    graphs['observation_prior'].add_edge(*pair,weight=funnel(a,b,day)['terminal'])
                    graphs['known_parameter_missing'].add_edge(*pair,weight=funnel(a,b,day,private=(pa,pb,variant))['terminal'])
                    graphs['full_truth'].add_edge(*pair,weight=q)
                values={};cardinality={}
                for name,g in graphs.items():
                    chosen=nx.max_weight_matching(g);values[name]=sum(scores[tuple(sorted(p))] for p in chosen);cardinality[name]=len(chosen)
                output.append({'seed':seed,'variant':variant,'day':day,'edges':len(scores),'baseline_expected_immediate':sum(scores[tuple(sorted(p))] for p in action),'oracle_true_expected_immediate':values,'oracle_cardinality':cardinality,'baseline_cardinality':len(action)})
            sim.advance(action)
        assert sim.introductions==trace['introductions']
    def seed_means(key):
        return [float(np.mean([key(r) for r in output if r['seed']==seed])) for seed in sorted(set(r['seed'] for r in output))]
    summary={name:interval(seed_means(lambda r:r['oracle_true_expected_immediate'][name]-r['baseline_expected_immediate'])) for name in ('observation_prior','known_parameter_missing','full_truth')}
    return {'information':'Current public verified legal graph, historical baseline state. observation_prior uses unknown-family public prior; known_parameter_missing knows family, actor biases/response rates but integrates missing features uniformly; full_truth also knows missing soft truth. All integrate future pair Gaussian/outcomes rather than seeing realized random draws. No future arrivals/exits/pending schedule or outcome stream is optimized.','not_bound':'Static maximum expected current reward along baseline trajectories; dynamic state distribution would change if deployed, so gains are neither attainable policy effect nor an upper bound. No hidden hard-field graph expansion.','days':[0,20,40,59],'rows':output,'summary':summary}

if __name__=='__main__':main()
