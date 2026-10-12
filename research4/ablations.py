"""Fixed focused contrasts; exploratory, clustered by seed, no fitting."""
import argparse
import json
from pathlib import Path
import numpy as np
from research3.analyze import analyze,interval
from evaluate import VARIANTS

CONTRASTS=(('coordinated_goal','goal_surplus_control','samebatch timing and bundle displacement'),
           ('hard_priority','population_control','public verification priority at fixed score'),
           ('response_uniform','response_beta_control','exact response prior at fixed architecture'),
           ('acceptance_shrinkage','response_uniform','shrunk acceptance update at fixed response'))


def main():
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--output',required=True);a=p.parse_args()
    valid=analyze(a.input);data=json.loads(Path(a.input).read_text())
    rows={(r['policy'],r['seed'],r['variant']):r for r in data['episodes']}
    rng=np.random.default_rng(90210);seeds=valid['seeds'];draws=rng.integers(0,len(seeds),(10000,len(seeds)))
    out={'source':a.input,'scope':'prelisted exploratory focused contrasts, not confirmatory or causal occupancy mediation','contrasts':{}}
    for lhs,rhs,question in CONTRASTS:
        if lhs not in valid['policies'] or rhs not in valid['policies']:continue
        d=np.array([sum(rows[lhs,s,v]['msmi_per_100_arrived_members']-rows[rhs,s,v]['msmi_per_100_arrived_members'] for v in VARIANTS)/6 for s in seeds])
        item={'question':question,'paired':interval(d.tolist()),'bootstrap95':np.quantile(d[draws].mean(axis=1),[.025,.975]).tolist()}
        out['contrasts'][lhs+' minus '+rhs]=item
    tests=sorted((r['paired']['p_two_sided'] if r['paired']['p_two_sided'] is not None else 1.,n) for n,r in out['contrasts'].items())
    running=0
    for i,(pvalue,name) in enumerate(tests):
        running=max(running,min(1,(len(tests)-i)*pvalue));out['contrasts'][name]['holm_p']=running
    Path(a.output).write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':main()
