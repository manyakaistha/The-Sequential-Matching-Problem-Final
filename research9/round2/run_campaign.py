"""Master execution campaign for Round 2 studies.
Runs Study Q1, Study Q2, and Study Q3 sequentially under the 7-worker limit,
then triggers full statistical analysis and exports the markdown report.
"""
import sys
import time
from pathlib import Path

from .study import run_grid
from .analyze import analyze_study, RESULTS_DIR


def run_campaign(seeds_count=16, workers=7):
    base_seed = 4000101
    seeds = range(base_seed, base_seed + seeds_count)
    
    t_start = time.time()
    print("=" * 60)
    print(f"ROUND 2 CAMPAIGN START: {seeds_count} seeds per cluster, {workers} workers")
    print("=" * 60)

    # 1. Study Q1: Robustness of FIFO and baselines across changing conditions
    q1_laws = [
        'development', 'sparse', 'cold_start', 'delayed', 'shift', 'drift',
        'A_sorted', 'A_reverse', 'A_late', 'A_waves',
        'W_half_shift', 'W_strong_shift', 'W_goal_zero',
        'R_low', 'R_decay', 'R_date_low',
    ]
    q1_arms = ['G', 'P', 'Q6', 'G_arr', 'G_lifo', 'G_deg']
    run_grid('study_q1_robustness', seeds, q1_laws, q1_arms, workers=workers)

    # 2. Study Q2: Priors estimated from observable training data vs simulator parameters
    q2_laws = ['development', 'cold_start', 'delayed', 'shift', 'drift']
    q2_arms = ['PS_sim', 'PS_emp', 'PS_flat', 'N3e_sim', 'N3e_emp', 'N3e_flat', 'G']
    run_grid('study_q2_priors', seeds, q2_laws, q2_arms, workers=workers)

    # 3. Study Q3: Small adaptive alternative for drift with directional calibration
    q3_laws = ['drift', 'D_early', 'D_strong', 'D_positive', 'D_reversal', 'development']
    q3_arms = ['G', 'PS_emp', 'X1_emp', 'X1_sim', 'X1_nocal_emp', 'X1_nolearn_emp', 'X1_oracle']
    run_grid('study_q3_drift', seeds, q3_laws, q3_arms, workers=workers)

    total_time = time.time() - t_start
    print("=" * 60)
    print(f"ALL ROUND 2 STUDIES COMPLETED IN {total_time:.1f}s ({total_time/60:.2f} min)")
    print("=" * 60)


if __name__ == '__main__':
    n_seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    run_campaign(n_seeds, w)
