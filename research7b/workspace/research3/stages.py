"""Deterministic registered stage advancement; refuses overwrite and verifies freezes."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import resource
import time
from pathlib import Path
import subprocess
import sys
from research3.analyze import analyze
from research3.benchmark import hashes
from research3.policy import CANDIDATES

ROOT = Path('results/research3')


def save_new(name, obj):
    path = ROOT / name
    with path.open('x') as file:
        json.dump(obj, file, indent=2)
        file.write('\n')


def ledger(command, status, **extra):
    with (ROOT/'commands.jsonl').open('a') as file:
        file.write(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(), command=command, status=status, **extra))+'\n')


def benchmark(stage, names, lo, hi):
    command = [sys.executable, '-m', 'research3.benchmark', '--policies', ','.join(names),
               '--seeds', f'{lo}:{hi}', '--workers', '2', '--output', str(ROOT/f'{stage}.json'),
               '--traces', str(ROOT/f'{stage}_traces')]
    ledger(command, 'started')
    before=resource.getrusage(resource.RUSAGE_CHILDREN)
    wall_started=time.perf_counter()
    with (ROOT/f'{stage}.log').open('x') as out:
        completed = subprocess.run(command, stdout=out, stderr=subprocess.STDOUT)
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    ledger(command, 'finished', returncode=completed.returncode,
           wall_seconds=time.perf_counter()-wall_started,
           child_cpu_seconds=(after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime),
           compute_scope='OS child usage including reaped worker usage, separate from episode wall sum')
    if completed.returncode:
        raise ValueError('benchmark failed; retain all rows/logs')
    result = analyze(ROOT/f'{stage}.json')
    save_new(f'{stage}_statistics.json', result)
    return result


def top(result, n):
    return sorted([name for name in result['policies'] if name != 'greedy'],
                  key=lambda name: (-result['policies'][name]['primary']['mean'], name))[:n]


def cost(name):
    cfg = CANDIDATES[name]
    mode = cfg.get('mode', 'greedy')
    c = 1 if mode == 'offline' else 3 if mode == 'response' else 2 if mode in ('population','throughput') else 0
    return c, int(bool(cfg.get('soft')))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['focus', 'selection', 'confirmation'])
    args = parser.parse_args()
    if args.phase == 'focus':
        screen = analyze(ROOT/'screen.json')
        if screen['code_hashes'] != hashes():
            raise ValueError('B source changed before C')
        save_new('screen_statistics.json', screen)
        promoted = top(screen, 3)
        names = set(promoted + ['greedy', 'clean', 'population'])
        for name in promoted:
            if name == 'goal_queries': names.add('public_weight')
            if name == 'four_queries': names.add('population')
        plan = dict(stage='C', selected_from_B=promoted, policies=sorted(names), seeds=[71001,71032],
                    recorded_before_run=datetime.now(timezone.utc).isoformat(), code_hashes=hashes())
        save_new('focus_plan.json', plan)
        benchmark('focus', sorted(names), 71001,71032)
    elif args.phase == 'selection':
        focus = analyze(ROOT/'focus.json')
        if focus['code_hashes'] != hashes():
            raise ValueError('C source changed before D')
        promoted = top(focus, 2)
        names = sorted(set(promoted+['greedy','clean','population']))
        save_new('selection_plan.json', dict(stage='D', selected_from_C=promoted, policies=names,
                                            seeds=[72001,72020],code_hashes=hashes(), utc=datetime.now(timezone.utc).isoformat()))
        selection = benchmark('selection', names, 72001,72020)
        if selection['code_hashes'] != hashes():
            raise ValueError('D source changed before freeze')
        candidates = [n for n in names if n != 'greedy']
        best = max(selection['policies'][n]['primary']['mean'] for n in candidates)
        band = [n for n in candidates if selection['policies'][n]['primary']['mean'] >= best-.025]
        chosen = min(band,key=lambda n:(*cost(n),-selection['policies'][n]['primary']['mean'],n))
        variance_source = chosen if chosen in focus['policies'] else 'population'
        sd = max(.21,focus['policies'][variance_source]['paired']['sd'])
        uncapped = math.ceil(1.10*((1.959964+.841621)*sd/.10)**2)
        n = min(160,max(40,uncapped))
        save_new('freeze.json', dict(policy=chosen, configuration=CANDIDATES[chosen], code_hashes=hashes(),
            frozen_utc=datetime.now(timezone.utc).isoformat(), eligible_selection_band=band,
            selection_rule='registered engineering cost then higher score then alphabetical within .025',
            confirmation_n=n,uncapped_power_n=uncapped,planning_sd=sd,variance_source=variance_source,
            confirmation_seeds=[73001,73000+n],comparison='selected minus shipped greedy',
            fit_data='only old seeds1001--1005; all models frozen before B', registry_sha256=hashlib.sha256(Path('research3/EXPERIMENT_REGISTRY.md').read_bytes()).hexdigest()))
    else:
        freeze=json.loads((ROOT/'freeze.json').read_text())
        if freeze['code_hashes'] != hashes():
            raise ValueError('frozen inference/runner changed')
        if freeze['registry_sha256'] != hashlib.sha256(Path('research3/EXPERIMENT_REGISTRY.md').read_bytes()).hexdigest():
            raise ValueError('registry changed after freeze')
        benchmark('confirmation', ['greedy',freeze['policy']], *freeze['confirmation_seeds'])


if __name__ == '__main__':
    main()
