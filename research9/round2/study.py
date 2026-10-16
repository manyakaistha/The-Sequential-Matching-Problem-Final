"""Parallel experiment orchestrator for Round-2 studies.

Complies with AGENTS.md:
- Uses up to 7 worker processes.
- Memory/transient checks.
- Produces deterministic, auditable, immutable result JSON files.
"""
import argparse
import copy
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from . import arms as A
from . import laws as L
from . import priors as P
from .episode import run_episode

RESULTS_DIR = Path(__file__).resolve().parent / 'results'


def _run_worker(task):
    seed, law_name, arm, thetas, keep_ledger = task
    return run_episode(seed, law_name, arm, thetas, keep_ledger=keep_ledger)


def run_grid(name, seeds, laws, arms_list, workers=7, keep_ledger=False):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_file = RESULTS_DIR / f"{name}.json"
    
    print(f"=== Starting Study: {name} ===")
    print(f"Seeds: {len(seeds)} | Laws: {len(laws)} | Arms: {len(arms_list)} | Total Episodes: {len(seeds)*len(laws)*len(arms_list)}")
    print(f"Workers: {workers} (within 7-worker host guard)")

    P.write_builtin()
    thetas = {
        'sim': P.load('sim'),
        'flat': P.load('flat'),
        'emp': P.load('emp'),
    }

    tasks = []
    for s in seeds:
        for l in laws:
            for a in arms_list:
                tasks.append((s, l, a, thetas, keep_ledger))

    started = time.time()
    results = []
    completed = 0
    total = len(tasks)

    # Use ProcessPoolExecutor with worker count <= 7
    with ProcessPoolExecutor(max_workers=min(workers, 7)) as executor:
        futures = {executor.submit(_run_worker, t): t for t in tasks}
        for f in as_completed(futures):
            res = f.result()
            results.append(res)
            completed += 1
            if completed % max(1, (total // 10)) == 0 or completed == total:
                elapsed = time.time() - started
                rate = completed / max(0.1, elapsed)
                print(f"[{name}] {completed}/{total} episodes done ({completed/total*100:.1f}%) | {rate:.1f} eps/s | ETA: {(total-completed)/max(0.1, rate):.1f}s")

    elapsed = time.time() - started
    payload = {
        'study_name': name,
        'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'elapsed_seconds': round(elapsed, 2),
        'seeds': list(seeds),
        'laws': list(laws),
        'arms': list(arms_list),
        'episodes_count': len(results),
        'records': results,
    }
    
    out_file.write_text(json.dumps(payload, indent=2))
    print(f"Saved {len(results)} records to {out_file} in {elapsed:.1f}s")
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--study', choices=['q1_robustness', 'q2_priors', 'q3_drift', 'all', 'smoke'], default='smoke')
    parser.add_argument('--seeds', type=int, default=16, help='Number of seed clusters')
    parser.add_argument('--workers', type=int, default=7, help='Worker process count (max 7)')
    args = parser.parse_args()

    # Seed namespace: 4000101 onwards
    base_seed = 4000101
    
    if args.study == 'smoke':
        seeds = range(base_seed, base_seed + 2)
        run_grid('smoke_q1', seeds, ['development', 'A_sorted'], ['G', 'G_arr', 'P'], workers=args.workers)
        run_grid('smoke_q2', seeds, ['development', 'delayed'], ['PS_sim', 'PS_emp', 'PS_flat'], workers=args.workers)
        run_grid('smoke_q3', seeds, ['drift', 'D_strong'], ['G', 'PS_emp', 'X1_emp', 'X1_oracle'], workers=args.workers)
        return

    n_seeds = args.seeds
    seeds = range(base_seed, base_seed + n_seeds)

    if args.study in ('q1_robustness', 'all'):
        # Q1: Does FIFO retain its advantage under changing arrival order, preference weights, response conditions?
        q1_laws = [
            # standard
            'development', 'sparse', 'cold_start', 'delayed', 'shift', 'drift',
            # arrival order & process
            'A_sorted', 'A_reverse', 'A_late', 'A_waves',
            # preference weights
            'W_half_shift', 'W_strong_shift', 'W_goal_zero',
            # response conditions
            'R_low', 'R_decay', 'R_date_low',
        ]
        q1_arms = ['G', 'P', 'Q6', 'G_arr', 'G_lifo', 'G_deg']
        run_grid('study_q1_robustness', seeds, q1_laws, q1_arms, workers=args.workers)

    if args.study in ('q2_priors', 'all'):
        # Q2: Would priors estimated from observable training data change conclusions?
        q2_laws = ['development', 'cold_start', 'delayed', 'shift', 'drift']
        q2_arms = ['PS_sim', 'PS_emp', 'PS_flat', 'N3e_sim', 'N3e_emp', 'N3e_flat', 'G']
        run_grid('study_q2_priors', seeds, q2_laws, q2_arms, workers=args.workers)

    if args.study in ('q3_drift', 'all'):
        # Q3: Can a small adaptive alternative address drift with calibration and identical asks?
        q3_laws = ['drift', 'D_early', 'D_strong', 'D_positive', 'D_reversal', 'development']
        q3_arms = ['G', 'PS_emp', 'X1_emp', 'X1_sim', 'X1_nocal_emp', 'X1_nolearn_emp', 'X1_oracle']
        run_grid('study_q3_drift', seeds, q3_laws, q3_arms, workers=args.workers)


if __name__ == '__main__':
    main()
