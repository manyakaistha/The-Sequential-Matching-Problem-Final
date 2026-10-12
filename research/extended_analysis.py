"""Scenario-balanced seed-cluster analysis; never treat six family rows as independent.
Usage: python research/extended_analysis.py INPUT --output OUTPUT --reference greedy
"""
import argparse
import collections
import json
import math
from pathlib import Path
import sys
sys.path[:] = [p for p in sys.path if Path(p or '.').resolve() != Path(__file__).resolve().parent]
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from scipy import stats
from evaluate import VARIANTS

METRICS = ('msmi_per_100_arrived_members','coverage','mutual_acceptance_rate',
           'date_completion_rate','ask_cost','mean_inference_ms','latency_p95_seconds',
           'latency_p99_seconds','peak_latency_seconds','peak_memory_bytes','peak_request_bytes')

def interval(values):
    x=np.asarray(values,dtype=float); n=len(x)
    if not n:return {'n':0,'mean':None,'sd':None,'ci95':None}
    m=float(x.mean());sd=float(x.std(ddof=1)) if n>1 else 0.
    half=float(stats.t.ppf(.975,n-1)*sd/math.sqrt(n)) if n>1 else None
    return {'n':n,'mean':m,'sd':sd,'ci95':[m-half,m+half] if half is not None else None}

def paired_p(diff):
    if len(diff)<2:return None
    if np.std(diff,ddof=1)==0:return 1. if np.mean(diff)==0 else None
    return float(stats.ttest_1samp(diff,0).pvalue)

def holm(pvalues):
    order=sorted(range(len(pvalues)),key=lambda i:pvalues[i]);out=[None]*len(pvalues);last=0.
    for rank,i in enumerate(order):last=max(last,min(1.,(len(order)-rank)*pvalues[i]));out[i]=last
    return out

def analyze(rows,reference='greedy',confirmatory=None):
    groups=collections.defaultdict(list)
    for row in rows:groups[row.get('policy','unspecified')].append(row)
    out={'method':'equal scenario weights, paired independent seed clusters, two-sided Student t intervals/tests',
         'reference':reference,'policies':{},'comparisons':[],
         'caveats':['Six families of one seed are correlated. Student t coverage uses an approximation; rare rewards can be nonnormal.',
                    'Shared seeds share worlds but policies with differing dyads/days do not share every outcome stream.',
                    'No inference that failed episodes are ignorable. A policy with any failure is ineligible.']}
    cluster={}
    for name,rs in groups.items():
        failures=[r for r in rs if not r.get('valid',False)]
        valid=[r for r in rs if r.get('valid',False)]
        by_seed=collections.defaultdict(dict)
        duplicates=[]
        for r in valid:
            if r['variant'] in by_seed[r['seed']]:duplicates.append((r['seed'],r['variant']))
            by_seed[r['seed']][r['variant']]=r
        complete={s:vs for s,vs in by_seed.items() if set(vs)==set(VARIANTS)}
        incomplete=sorted(set(by_seed)-set(complete))
        cluster[name]={s:float(np.mean([v[k]['msmi_per_100_arrived_members'] for k in VARIANTS])) for s,v in complete.items()}
        metrics={}
        for k in METRICS:
            vals=[float(np.mean([v[f][k] for f in VARIANTS])) for v in complete.values() if all(k in v[f] for f in VARIANTS)]
            if vals:metrics[k]=interval(vals)
        maxima={k:max((r.get(k,0) for r in valid),default=0) for k in ('peak_latency_seconds','peak_memory_bytes','peak_request_bytes')}
        out['policies'][name]={'eligible':bool(complete) and not failures and not duplicates and not incomplete,
          'episodes':len(rs),'invalid_episodes':len(failures),'failure_count':sum(r.get('failure_count',not r.get('valid',False)) for r in rs),
          'complete_seed_clusters':len(complete),'incomplete_seeds':incomplete,'duplicate_family_rows':duplicates,
          'primary':interval(list(cluster[name].values())),'metrics':metrics,'maxima':maxima,
          'scenario_metrics':{f:{k:interval([r[k] for r in valid if r['variant']==f and k in r]) for k in METRICS if any(r['variant']==f and k in r for r in valid)} for f in VARIANTS}}
    if reference in cluster:
        for name,x in cluster.items():
            if name==reference:continue
            common=sorted(set(x)&set(cluster[reference]));diff=np.asarray([x[s]-cluster[reference][s] for s in common])
            summary=interval(diff)
            rng=np.random.default_rng(90210)
            bootstrap=np.mean(rng.choice(diff,size=(10000,len(diff)),replace=True),axis=1) if len(diff) else np.asarray([])
            out['comparisons'].append({'policy':name,'seeds':common,'difference':summary,
              'paired_t_p':paired_p(diff),'paired_seed_bootstrap_ci95':np.quantile(bootstrap,[.025,.975]).tolist() if len(bootstrap) else None,
              'bootstrap_replicates':10000,'bootstrap_random_seed':90210,
              't_test_note':'Undefined for fewer than two clusters or constant nonzero difference.' if paired_p(diff) is None else None,
              'standardized_paired_effect':summary['mean']/summary['sd'] if summary['sd'] else None,
              'confirmatory':name==confirmatory})
        tests=[r for r in out['comparisons'] if r['paired_t_p'] is not None and not r['confirmatory']]
        for r,p in zip(tests,holm([r['paired_t_p'] for r in tests])):r['exploratory_holm_p']=p
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--output');p.add_argument('--reference',default='greedy');p.add_argument('--confirmatory');a=p.parse_args()
    raw=json.loads(Path(a.input).read_text());result=analyze(raw['episodes'],a.reference,a.confirmatory)
    result['source_complete']=bool(raw.get('complete',False));result['planned_episodes']=raw.get('planned_episodes')
    result['recorded_episodes']=len(raw['episodes'])
    if not result['source_complete']:
        result['caveats'].append('Source experiment is incomplete; estimates are interim and cannot establish confirmatory superiority.')
        for item in result['policies'].values():item['eligible']=False
    target=Path(a.output or str(Path(a.input).with_name(Path(a.input).stem+'_statistics.json')));target.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    for name,r in result['policies'].items():print(name,r['primary'])
    for row in result['comparisons']:print(row['policy'],row['difference'],'p=',row['paired_t_p'])
if __name__=='__main__':main()
