"""Predefined development difference-in-differences and representative traces."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from research.extended_analysis import interval, paired_p, holm
from evaluate import VARIANTS

CONTRASTS={
 'model_x_query': [('simple_degree',1),('simple_fifo',-1),('terminal_degree',-1),('terminal_fifo',1)],
 'model_x_allocation': [('simple_blossom',1),('simple_fifo',-1),('terminal_blossom',-1),('terminal_fifo',1)],
 'query_x_allocation': [('terminal_degree_blossom',1),('terminal_degree',-1),('terminal_blossom',-1),('terminal_fifo',1)],
 'query_x_waiting': [('terminal_degree_batching',1),('terminal_degree_blossom',-1),('terminal_batching',-1),('terminal_blossom',1)],
}


def main():
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--output',default='results/extended/interactions.json');a=p.parse_args()
    raw=json.loads(Path(a.input).read_text());rows=raw['episodes']
    scores={(r['policy'],r['variant'],r['seed']):r['msmi_per_100_arrived_members'] for r in rows if r['valid']}
    seeds=sorted({r['seed'] for r in rows});out=[]
    for name,terms in CONTRASTS.items():
        diffs=[];used=[]
        for seed in seeds:
            if not all((n,f,seed) in scores for n,_ in terms for f in VARIANTS):continue
            used.append(seed);diffs.append(sum(c*sum(scores[n,f,seed] for f in VARIANTS)/len(VARIANTS) for n,c in terms))
        out.append(dict(contrast=name,terms=terms,seeds=used,estimate=interval(diffs),paired_t_p=paired_p(np.asarray(diffs))))
    tests=[r for r in out if r['paired_t_p'] is not None]
    for row,adjusted in zip(tests,holm([r['paired_t_p'] for r in tests])):row['holm_p']=adjusted
    result=dict(scope='Exploratory factorial interaction contrasts on the new architecture; seed-cluster differences in differences.',
                complete=raw['complete'],contrasts=out,
                caveat='Eight development clusters are exploratory. Null interaction tests do not establish independence or equivalence.')
    Path(a.output).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
