"""Registered C baseline common-cohort audit; fixed models, no fitting.
Does not access worlds, oracle truth, selection or confirmation artifacts.
"""
import argparse
import collections
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
import time
import numpy as np
from scipy.special import expit
from scipy.stats import t
from research3.prediction_audit import FIELDS, STAGES, audit_group, eq_prob, funnel, interval, proper
from research3.model_candidates import OFFLINE_WEIGHTS


def labels(intro,feedback):
    es=[e for e in feedback if e['introduction_id']==intro['introduction_id']]
    rs=[e for e in es if e['event']=='introduction_response'];ds=[e for e in es if e['event']=='date_happened' and e['value']];ss=[e for e in es if e['event']=='second_meeting_intention']
    outcomes=(len(rs)==2 and all(e['value'] is not None for e in rs),len(rs)==2 and all(e['value']=='yes' for e in rs),bool(ds),len(ss)==2 and all(e['value']=='yes' for e in ss),bool(ds) and len(ss)==2 and ds[0]['occurred_day']-intro['assigned_day']<=30 and all(e['value']=='yes' and e['occurred_day']-ds[0]['occurred_day']<=3 for e in ss))
    return dict(zip(STAGES,map(int,outcomes)))

def main():
    args=argparse.ArgumentParser();args.add_argument('--input',default='results/research3/focus.json');args.add_argument('--output',default='results/research3/focus_prediction_audit.json');args=args.parse_args()
    started=datetime.now(timezone.utc).isoformat();cpu=time.process_time();source=Path(args.input);focus=json.loads(source.read_text())
    if not focus.get('complete'):raise RuntimeError('registered C must be complete before common-cohort audit')
    if Path(args.output).exists():raise RuntimeError('refuse overwriting completed focus audit')
    seeds=focus['planned_seeds'];assert seeds==list(range(71001,71033))
    greedy=[r for r in focus['episodes'] if r['policy']=='greedy'];assert len(greedy)==32*6 and all(r['valid'] and r.get('optimized_fallback_count')==0 for r in greedy)
    families=('development','sparse','cold_start','delayed','shift','drift')
    assert {(r['seed'],r['variant']) for r in greedy}=={(seed,family) for seed in seeds for family in families}
    training_source=Path('results/extended/audit_common_cohort_calibration.json');old=json.loads(training_source.read_text())['assignment_rows'];train=[r for r in old if 1001<=r['seed']<=1005]
    constant={k:float(np.mean([r['label'][k] for r in train])) for k in STAGES};rows=[];trace_hashes={}
    for episode in greedy:
        path=Path(episode['trace']);trace=json.loads(path.read_text());trace_hashes[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
        assert trace['seed']==episode['seed'] and trace['variant']==episode['variant']
        intros={(tuple(sorted((i['user_a'],i['user_b']))),i['assigned_day']):i for i in trace['introductions']};feedback=trace['completed_feedback']
        assert len(trace['assignment_snapshots'])==len(trace['introductions'])==episode['assignments']
        seen_snapshots=set()
        for snap in trace['assignment_snapshots']:
            a,b=snap['member_a'],snap['member_b'];day=snap['assigned_day'];key=(tuple(sorted((a['member_id'],b['member_id']))),day);intro=intros[key]
            assert key not in seen_snapshots;seen_snapshots.add(key)
            for member in (a,b):assert all(v is None or member['field_observed_day'][field]<=day for field,v in member['fields'].items())
            counts=collections.defaultdict(lambda:[0,0]);actor_feedback=collections.Counter()
            for e in feedback:
                if e['observed_day']<=day and e['event'] in ('introduction_response','second_meeting_intention') and e['member_id']:
                    counts[e['member_id']][0 if e['value'] is not None else 1]+=1;actor_feedback[e['member_id']]+=1
            x=(1.,)+tuple(v-p for v,p in zip(eq_prob(a,b),(.5,1/3,1/3,.25)))+(float(day>=35),)
            pred={'constant':constant,'population':funnel(a,b,day),'response':funnel(a,b,day,counts),'offline':{'terminal':float(expit(sum(w*v for w,v in zip(OFFLINE_WEIGHTS,x))))}}
            label=labels(intro,feedback)
            for probs in pred.values():
                if len(probs)==5:assert all(probs[b]<=probs[a]+1e-12 for a,b in zip(STAGES,STAGES[1:]))
            rows.append({'seed':episode['seed'],'variant':episode['variant'],'day':day,'introduction_id':intro['introduction_id'],'members':[a['member_id'],b['member_id']],'missing':sum(m['fields'].get(k) is None for m in (a,b) for k in FIELDS),'prior_feedback_pooled':snap['prior_feedback'],'actor_history_min':min(actor_feedback[m['member_id']] for m in (a,b)),'actor_history_sum':sum(actor_feedback[m['member_id']] for m in (a,b)),'label':label,'pred':pred})
        assert sum(r['label']['terminal'] for r in rows if r['seed']==episode['seed'] and r['variant']==episode['variant'])==episode['mutual_second_meeting_intention']
    assessment=audit_group(rows);contrasts={}
    for model,control in (('population','constant'),('response','population'),('offline','population'),('response','constant'),('offline','constant')):
        contrasts[model+'_minus_'+control]={}
        for metric in ('log_loss','brier'):
            delta=[]
            for seed in seeds:
                rs=[r for r in rows if r['seed']==seed];y=[r['label']['terminal'] for r in rs]
                delta.append(proper([r['pred'][model]['terminal'] for r in rs],y)[metric]-proper([r['pred'][control]['terminal'] for r in rs],y)[metric])
            contrasts[model+'_minus_'+control][metric]=interval(delta)
            se=float(np.std(delta,ddof=1)/math.sqrt(len(delta)));mean=float(np.mean(delta))
            contrasts[model+'_minus_'+control][metric]['unadjusted_two_sided_p']=float(2*t.sf(abs(mean/se),len(delta)-1)) if se else 1. if mean==0 else 0.
    flat=sorted([(item['unadjusted_two_sided_p'],pair,metric) for pair,metrics in contrasts.items() for metric,item in metrics.items()]);running=0.
    for rank,(pvalue,pair,metric) in enumerate(flat):
        running=max(running,min(1.,(len(flat)-rank)*pvalue));contrasts[pair][metric]['holm_p_all10_terminal_contrasts']=running
    groups={'variant':lambda r:r['variant'],'time':lambda r:'late35plus' if r['day']>=35 else 'early','missing':lambda r:str(min(4,r['missing'])),'actor_history_min':lambda r:'zero' if r['actor_history_min']==0 else '1to2' if r['actor_history_min']<=2 else '3plus','pooled_history':lambda r:'20plus' if r['prior_feedback_pooled']>=20 else 'under20'};slices={}
    for axis,fn in groups.items():
        slices[axis]={}
        for value in sorted(set(fn(r) for r in rows)):
            rs=[r for r in rows if fn(r)==value];slices[axis][value]={model:proper([r['pred'][model]['terminal'] for r in rs],[r['label']['terminal'] for r in rs]) for model in assessment}
    reliability={};bins=(0,.005,.01,.02,.04,1.)
    for model in assessment:
        reliability[model]=[]
        for lo,hi in zip(bins,bins[1:]):
            rs=[r for r in rows if lo<=r['pred'][model]['terminal']<hi]
            if not rs:continue
            item=proper([r['pred'][model]['terminal'] for r in rs],[r['label']['terminal'] for r in rs]);item['bin']=[lo,hi]
            clusters=sorted(set(r['seed'] for r in rs));totals=np.array([[sum(r['label']['terminal'] for r in rs if r['seed']==seed),sum(r['seed']==seed for r in rs)] for seed in clusters]);rng=np.random.default_rng(12);sampled=totals[rng.integers(0,len(totals),(5000,len(totals)))].sum(axis=1)
            item['supporting_seeds']=len(clusters);item['observed_cluster_bootstrap95']=np.quantile(sampled[:,0]/sampled[:,1],[.025,.975]).tolist() if len(clusters)>=6 and 0<item['positive']<item['n'] else None
            reliability[model].append(item)
    result={'started_utc':started,'completed_utc':datetime.now(timezone.utc).isoformat(),'command':sys.argv,'scope':'RegisteredC greedy common prospective assignment cohort only; fixed models, no fitting;32seedclusters acrosssixfamilies; predictive diagnostics exploratory, not confirmation/policyvalue','stored_prediction_contract':'Ignored snapshot prediction is auxiliary inherited integrated prior with default one-third regime weights; not actual evaluated policy or six-family population forecast. This audit recomputes all forecasts independently.', 'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'training_source_sha256':hashlib.sha256(training_source.read_bytes()).hexdigest(),'model_source_sha256':hashlib.sha256(Path('research3/model_candidates.py').read_bytes()).hexdigest(),'trace_sha256':trace_hashes,'training_seeds':list(range(1001,1006)),'cohort_seeds':seeds,'n':len(rows),'assessment':assessment,'terminal_contrasts':contrasts,'terminal_slices':slices,'reliability':reliability,'prediction_rows':rows,'cpu_seconds':time.process_time()-cpu,'uncertainty':'Assignment-weighted loss within each seed across six families, then equal-weight seed means; not equal-family episode losses. T/whole-seed bootstrap sensitivities; Holm over all 10 terminal contrast tests. Exploratory contrasts without confirmatory interpretation; stageconditional/slice/AUC summaries descriptive. Reliability bins <6supportingseeds or degenerate events have no informative interval. Actorhistory count is actor-specific resolved response/second feedback available at assignment; pooledhistory remains separately labeled.'}
    Path(args.output).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(7,5));ax.plot([0,.04],[0,.04],'k--',lw=1)
    for model,data in reliability.items():
        good=[r for r in data if r['observed_cluster_bootstrap95'] is not None];bad=[r for r in data if r['observed_cluster_bootstrap95'] is None];xx=[r['predicted_mean'] for r in good];yy=[r['observed_mean'] for r in good];low=[r['observed_cluster_bootstrap95'][0] for r in good];high=[r['observed_cluster_bootstrap95'][1] for r in good];draw=ax.errorbar(xx,yy,yerr=[[max(0,y-l) for y,l in zip(yy,low)],[max(0,h-y) for y,h in zip(yy,high)]],fmt='o',capsize=3,label=model);ax.scatter([r['predicted_mean'] for r in bad],[r['observed_mean'] for r in bad],marker='x',color=draw.lines[0].get_color())
    ax.set(xlabel='Predicted terminal probability',ylabel='Observed terminal rate',title=f'RegisteredC same greedy cohort: {len(rows)} assignments /32seeds');ax.legend();fig.text(.02,.005,'Crosses: interval unavailable; bins and comparisons exploratory.',fontsize=8);fig.tight_layout(rect=(0,.03,1,1));fig.savefig(Path(args.output).with_suffix('.png'),dpi=160);plt.close(fig)
    print(json.dumps({'n':len(rows),'positive':sum(r['label']['terminal'] for r in rows),'cpu_seconds':result['cpu_seconds'],'terminal':{m:d['terminal'] for m,d in assessment.items()},'contrasts':contrasts},indent=2))
if __name__=='__main__':main()
