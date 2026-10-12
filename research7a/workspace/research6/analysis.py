"""Registered seed-cluster comparisons; exploratory Holm and bootstrap sensitivity."""
import argparse
import json
import math
from pathlib import Path
import statistics
import numpy as np
from scipy.stats import t


def compare(rows, candidate, baseline='G', confidence=.95, bootstrap_seed=90210, reps=10000):
    lookup = {(r['policy'],r['seed'],r['family']):r for r in rows}
    seeds = sorted({r['seed'] for r in rows})
    families = ('development','sparse','cold_start','delayed','shift','drift')
    ds=[]; family_d={f:[] for f in families}
    for seed in seeds:
        values=[]
        for family in families:
            a,b = lookup[candidate,seed,family],lookup[baseline,seed,family]
            if not a['valid'] or not b['valid']:
                raise ValueError('invalid episode disqualifies comparison; retain all rows')
            d=a['msmi_per_100_arrived_members']-b['msmi_per_100_arrived_members']
            values.append(d);family_d[family].append(d)
        ds.append(statistics.mean(values))
    if len(ds)<2: raise ValueError('at least two clusters required')
    mean=statistics.mean(ds);sd=statistics.stdev(ds);se=sd/math.sqrt(len(ds))
    critical=float(t.ppf((1+confidence)/2,len(ds)-1))
    p=2*float(t.sf(abs(mean/se),len(ds)-1)) if se else (1. if mean==0 else 0.)
    rng=np.random.default_rng(bootstrap_seed)
    samples=np.asarray(ds)[rng.integers(0,len(ds),size=(reps,len(ds)))].mean(axis=1)
    lo,hi=np.quantile(samples,[(1-confidence)/2,(1+confidence)/2])
    return {'candidate':candidate,'baseline':baseline,'n_clusters':len(ds),'seeds':seeds,
            'paired_seed_differences':ds,'mean_difference':mean,'paired_sd':sd,'se':se,
            'confidence':confidence,'ci':[mean-critical*se,mean+critical*se],'p_two_sided':p,
            'standardized_effect':mean/sd if sd else None,
            'one_sided_90_lower':mean-float(t.ppf(.9,len(ds)-1))*se,
            'bootstrap_sensitivity':{'seed':bootstrap_seed,'replicates':reps,'ci':[float(lo),float(hi)],'scope':'whole seed clusters'},
            'family_mean_differences':{f:statistics.mean(v) for f,v in family_d.items()},
            'leave_one_seed_means':{str(s):statistics.mean(ds[:i]+ds[i+1:]) for i,s in enumerate(seeds)}}


def holm(results):
    ordered=sorted(enumerate(results),key=lambda iv:iv[1]['p_two_sided']);running=0.
    for rank,(index,row) in enumerate(ordered):
        running=max(running,min(1.,(len(results)-rank)*row['p_two_sided']))
        results[index]['p_holm']=running
    return results


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();root=Path(args.run)
    design=json.loads((root/'registration.json').read_text())
    if design['stage']=='E': raise ValueError('E requires explicit closed fixed-grid analysis registration; never monitor E effects')
    rows=[json.loads(p.read_text()) for p in sorted((root/'commits').glob('*.json'))]
    expected={(c['policy'],c['seed'],c['family']) for c in design['cells']}
    actual={(r['policy'],r['seed'],r['family']) for r in rows}
    if expected!=actual or len(rows)!=len(expected):raise ValueError('incomplete/duplicate grid')
    names=sorted(set(r['policy'] for r in rows)-{'G'})
    results=holm([compare(rows,n) for n in names])
    target=Path(args.output)
    with target.open('x') as stream:
        json.dump({'status':'exploratory','comparisons':results,'planned_holm_family':names},stream,indent=2,allow_nan=False)
        stream.write('\n')


if __name__=='__main__':main()
