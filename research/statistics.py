"""Scenario-balanced summaries; dependence handled by aggregating within seed.
Student t intervals, paired seed tests, exact sign-flip tests and Holm correction.
"""
import collections
import itertools
import json
import math
from pathlib import Path
import numpy as np
from scipy import stats

METRICS=('msmi_per_100_arrived_members','coverage','mutual_acceptance_rate','date_completion_rate','ask_cost','mean_inference_ms')
def interval(values):
    a=np.asarray(values,dtype=float);n=len(a);mean=float(a.mean());sd=float(a.std(ddof=1)) if n>1 else 0
    radius=float(stats.t.ppf(.975,n-1))*sd/math.sqrt(n) if n>1 else 0
    return dict(n=n,mean=mean,sd=sd,ci95=[mean-radius,mean+radius])

def analyse(path, reference='greedy'):
    data=json.loads(Path(path).read_text());rows=data['episodes'];groups=collections.defaultdict(list)
    for r in rows:groups[r['policy'],r['variant']].append(r)
    summaries={}
    for (name,variant),rs in groups.items():summaries.setdefault(name,{})[variant]={k:interval([r[k] for r in rs]) for k in METRICS}
    seed_scores=collections.defaultdict(lambda:collections.defaultdict(list))
    for r in rows:seed_scores[r['policy']][r['seed']].append(r['msmi_per_100_arrived_members'])
    overall={name:interval([np.mean(vals) for seed,vals in seeds.items()]) for name,seeds in seed_scores.items()}
    comparisons=[]
    for name,seeds in seed_scores.items():
        if name==reference or reference not in seed_scores:continue
        common=sorted(set(seeds)&set(seed_scores[reference]))
        diff=np.array([np.mean(seeds[s])-np.mean(seed_scores[reference][s]) for s in common]);n=len(diff)
        if not n:continue
        t=float(stats.ttest_1samp(diff,0).pvalue) if np.std(diff)>0 else 1. if np.mean(diff)==0 else 0.
        exact=sum(abs(np.mean(diff*np.array(sign)))>=abs(np.mean(diff))-1e-12 for sign in itertools.product((-1,1),repeat=n))/2**n
        comparisons.append(dict(policy=name,seeds=common,difference=interval(diff),paired_t_p=t,exact_seed_signflip_p=exact))
    ordered=sorted(comparisons,key=lambda c:c['paired_t_p']);running=0
    for i,c in enumerate(ordered):running=max(running,min(1,c['paired_t_p']*(len(ordered)-i)));c['holm_p']=running
    return dict(source=path,reference=reference,complete=data.get('complete'),overall=overall,scenario_summaries=summaries,comparisons=comparisons,
                caveat='95% t intervals with five independent seed clusters are fragile; negative CI limits are not clipped. Exact paired sign-flip validity requires symmetric differences; common seeds do not share all pair outcome streams when assignment days differ.')

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('input',nargs='?',default='results/research/benchmark.json');p.add_argument('--reference',default='greedy');p.add_argument('--output',default='results/research/statistics.json');a=p.parse_args()
    out=analyse(a.input,a.reference);Path(a.output).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['overall'],indent=2))
