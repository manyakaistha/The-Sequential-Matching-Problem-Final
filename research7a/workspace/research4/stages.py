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
from research4.benchmark import hashes
from research4.policy import CANDIDATES

ROOT = Path('results/research4')


def save_new(name, obj):
    path = ROOT / name
    with path.open('x') as file:
        json.dump(obj, file, indent=2)
        file.write('\n')


def ledger(command, status, **extra):
    with (ROOT/'commands.jsonl').open('a') as file:
        file.write(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(), command=command, status=status, **extra))+'\n')


def benchmark(stage, names, lo, hi):
    command = [sys.executable, '-m', 'research4.benchmark', '--policies', ','.join(names),
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
    return {'population_control':0,'goal_surplus_control':1,'coordinated_goal':1,'hard_priority':2,'response_beta_control':2,'response_uniform':2,'acceptance_shrinkage':3}[name],

CONTROL={'coordinated_goal':'goal_surplus_control','hard_priority':'population_control','response_uniform':'response_beta_control','acceptance_shrinkage':'response_uniform','goal_surplus_control':'population_control','response_beta_control':'population_control'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['focus', 'selection', 'confirmation'])
    args = parser.parse_args()
    if args.phase == 'focus':
        screen = analyze(ROOT/'screen.json')
        if screen['code_hashes'] != hashes():
            raise ValueError('B source changed before C')
        save_new('screen_statistics.json', screen)
        promoted = sorted([n for n in screen['policies'] if n not in ('greedy','population_control')],key=lambda n:(-screen['policies'][n]['primary']['mean'],n))[:2]
        names = set(promoted + ['greedy', 'population_control'])
        for name in promoted:
            names.add(CONTROL[name])
        plan = dict(stage='C', selected_from_B=promoted, policies=sorted(names), seeds=[81001,81032],
                    recorded_before_run=datetime.now(timezone.utc).isoformat(), code_hashes=hashes())
        save_new('focus_plan.json', plan)
        benchmark('focus', sorted(names), 81001,81032)
    elif args.phase == 'selection':
        focus = analyze(ROOT/'focus.json')
        if focus['code_hashes'] != hashes():
            raise ValueError('C source changed before D')
        promoted = top(focus, 2)
        names = sorted(set(promoted+['greedy','population_control']))
        save_new('selection_plan.json', dict(stage='D', selected_from_C=promoted, policies=names,
                                            seeds=[82001,82020],code_hashes=hashes(), utc=datetime.now(timezone.utc).isoformat()))
        selection = benchmark('selection', names, 82001,82020)
        if selection['code_hashes'] != hashes():
            raise ValueError('D source changed before freeze')
        candidates = [n for n in names if n != 'greedy']
        best = max(selection['policies'][n]['primary']['mean'] for n in candidates)
        band = [n for n in candidates if selection['policies'][n]['primary']['mean'] >= best-.025]
        chosen = min(band,key=lambda n:(*cost(n),-selection['policies'][n]['primary']['mean'],n))
        variance_source = chosen if chosen in focus['policies'] else 'population_control'
        sd = max(.21,focus['policies'][variance_source]['paired']['sd'])
        uncapped = math.ceil(1.10*((1.959964+.841621)*sd/.10)**2)
        n = min(160,max(40,uncapped))
        save_new('freeze.json', dict(policy=chosen, configuration=CANDIDATES[chosen], code_hashes=hashes(),
            frozen_utc=datetime.now(timezone.utc).isoformat(), eligible_selection_band=band,
            selection_rule='registered engineering cost then higher score then alphabetical within .025',
            confirmation_n=n,uncapped_power_n=uncapped,planning_sd=sd,variance_source=variance_source,
            confirmation_seeds=[83001,83000+n],comparison='selected minus shipped greedy',
            fit_data='no offline fitting; fixed public priors and observation-only per-invocation feedback updates', registry_sha256=hashlib.sha256(Path('research4/EXPERIMENT_REGISTRY.md').read_bytes()).hexdigest()))
    else:
        freeze=json.loads((ROOT/'freeze.json').read_text())
        if freeze['code_hashes'] != hashes():
            raise ValueError('frozen inference/runner changed')
        if freeze['registry_sha256'] != hashlib.sha256(Path('research4/EXPERIMENT_REGISTRY.md').read_bytes()).hexdigest():
            raise ValueError('registry changed after freeze')
        benchmark('confirmation', ['greedy',freeze['policy']], *freeze['confirmation_seeds'])


if __name__ == '__main__':
    main()
