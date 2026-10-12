"""Seed-cluster policy reward analysis, exact grid validation and exploratory Holm."""
import argparse
import collections
import json
import math
from pathlib import Path
import statistics
import numpy as np
from scipy.stats import t
from evaluate import VARIANTS


def interval(xs):
    n = len(xs)
    mean = statistics.mean(xs)
    sd = statistics.stdev(xs) if n > 1 else 0
    margin = float(t.ppf(.975, n-1))*sd/math.sqrt(n) if n > 1 else None
    p = float(2*t.sf(abs(mean/(sd/math.sqrt(n))), n-1)) if n > 1 and sd > 0 else None
    return dict(n=n, mean=mean, sd=sd, ci95=[mean-margin, mean+margin] if margin is not None else None,
                p_two_sided=p, standardized=mean/sd if sd else None)


def analyze(path):
    data = json.loads(Path(path).read_text())
    if not data['complete'] or len(data['episodes']) != data['planned_episodes']:
        raise ValueError('incomplete registered run')
    groups = collections.defaultdict(dict)
    for row in data['episodes']:
        key = (row['seed'], row['variant'])
        if key in groups[row['policy']]:
            raise ValueError('duplicate episode')
        if not row['valid'] or row['failure_count'] or row.get('optimized_fallback_count', 0):
            raise ValueError('invalid/failing/fallback episode retained; analysis refused')
        groups[row['policy']][key] = row
    keys = set(groups['greedy'])
    seeds = sorted({s for s, v in keys})
    if seeds != data['planned_seeds'] or set(groups) != set(data['planned_policies']) or set(data['planned_variants']) != set(VARIANTS):
        raise ValueError('registered requested grid mismatch')
    expected = {(s,v) for s in seeds for v in VARIANTS}
    if keys != expected or any(set(g) != expected for g in groups.values()):
        raise ValueError('not exact paired six-family grid')
    means = {name: [statistics.mean(g[s,v]['msmi_per_100_arrived_members'] for v in VARIANTS) for s in seeds]
             for name, g in groups.items()}
    result = dict(estimand='equal six-family reward per seed, paired independent seed clusters',
                  seeds=seeds, source=str(path), code_hashes=data['code_hashes'], policies={})
    rng = np.random.default_rng(90210)
    draws = rng.integers(0, len(seeds), (10000,len(seeds)))
    for name, values in means.items():
        rows = list(groups[name].values())
        lat = [x for r in rows for x in r['inference_latencies']]
        diff = np.array(values)-np.array(means['greedy'])
        result['policies'][name] = dict(primary=interval(values), paired=interval(diff.tolist()),
            bootstrap95=np.quantile(diff[draws].mean(axis=1), [.025,.975]).tolist(),
            scenario_means={v: statistics.mean(groups[name][s,v]['msmi_per_100_arrived_members'] for s in seeds) for v in VARIANTS},
            totals={k: sum(r[k] for r in rows) for k in ('assignments','mutual_acceptances','dates','mutual_second_meeting_intention','served_members','arrived_members','ask_cost')},
            latency_seconds={'mean': statistics.mean(lat), 'p95': float(np.quantile(lat,.95)), 'p99': float(np.quantile(lat,.99)), 'max': max(lat)},
            mean_coverage=statistics.mean(r['coverage'] for r in rows),
            peak_request_bytes=max(r['peak_request_bytes'] for r in rows),
            peak_memory_bytes=max(r['peak_memory_bytes'] for r in rows),
            wall_seconds_sum=sum(r['wall_seconds'] for r in rows))
    tests = sorted((p['paired']['p_two_sided'] if p['paired']['p_two_sided'] is not None else 1.,name)
                   for name,p in result['policies'].items() if name != 'greedy')
    running = 0
    for i,(p,name) in enumerate(tests):
        running = max(running, min(1, (len(tests)-i)*p))
        result['policies'][name]['exploratory_holm_p'] = running
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('input')
    p.add_argument('--output', required=True)
    args = p.parse_args()
    result = analyze(args.input)
    Path(args.output).write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({n: {'mean':r['primary']['mean'], 'effect':r['paired']['mean'], 'ci':r['paired']['ci95']} for n,r in result['policies'].items()}, indent=2))


if __name__ == '__main__':
    main()
