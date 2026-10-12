"""
Test and Benchmark Dynamic Reservation Utility and Temporal Threshold Matching.

Subagent 13: algo_temporal_threshold
Problem Formulation:
1. In a 60-day horizon with arrivals (up to day 20) and stochastic exits (starting day 22),
   matching a pair today incurs opportunity cost O(t).
2. Arrivals: 30% of members arrive between days 1 and 20; exits start at day 22 (12% exit rate).
3. Early phase (t < 20): Opportunity cost O(t) is high because the pool is receiving high-quality
   arrivals and soft constraints are being actively revealed. Matching hastily locks members into
   inferior pairs.
4. Mid phase (20 <= t <= 50): Arrivals have ceased. Threshold stabilizes to harvest high/medium compatibility pairs.
5. Late phase (t > 50): Horizon closes at t = 59. Continuation value V(60) = 0. Opportunity cost
   drops to 0, so reservation threshold T(t) decays to clear all remaining feasible pairs.
"""

import copy
import itertools
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import kit

# Calibrated logistic model for P(MSMI) based on observable soft attributes
# Weights aligned with ground-truth acceptance and second-meeting dynamics
SOFT_WEIGHTS = {
    'relationship_goal': 0.7,
    'relationship_pace': 0.4,
    'lifestyle': 0.25,
    'conversations': 0.2
}
OPTIONS_COUNT = {
    'relationship_goal': 2,
    'relationship_pace': 3,
    'lifestyle': 3,
    'conversations': 4
}
BETA_0 = -3.988
BETA_FIT = 0.756
BETA_GOAL = 0.303


def predict_p_msmi(member_a, member_b):
    """
    Computes expected P(MSMI_ij | observable fields) for feasible pair (a, b).
    Uses Bayesian expectations for unobserved fields.
    """
    fa, fb = member_a['fields'], member_b['fields']
    fit = 0.0
    p_goal = 0.5
    for k, w in SOFT_WEIGHTS.items():
        va, vb = fa.get(k), fb.get(k)
        if va is not None and vb is not None:
            m = (va == vb)
            fit += w * (1.0 if m else -0.5)
            if k == 'relationship_goal':
                p_goal = 1.0 if m else 0.0
        else:
            # Prior expectation over uniform categorical distribution
            p_match = 1.0 / OPTIONS_COUNT[k]
            fit += w * (p_match * 1.0 + (1.0 - p_match) * (-0.5))
            if k == 'relationship_goal':
                p_goal = 0.5

    z = BETA_0 + BETA_FIT * fit + BETA_GOAL * p_goal
    return 1.0 / (1.0 + math.exp(-z))


def get_soft_match_score(a, b):
    return sum(a['fields'].get(k) is not None and a['fields'].get(k) == b['fields'].get(k) for k in kit.SOFT)


# ==============================================================================
# Threshold and Shadow Price Formulations
# ==============================================================================

def threshold_unconstrained_greedy(t):
    """Baseline greedy: no reservation threshold (T(t) = 0)."""
    return 0.0


def threshold_static(t, fixed_val=0.030):
    """Static reservation threshold: constant across entire horizon."""
    return fixed_val


def threshold_adaptive_temporal(t, t_early=0.027, t_mid=0.022):
    """
    Adaptive Temporal Reservation Threshold T(t):
    - t < 20: High threshold (t_early) protecting pool while arrivals enter.
    - 20 <= t <= 50: Moderate threshold (t_mid) harvesting mature pool.
    - t > 50: Linear decay towards 0 as opportunity cost of holding expires.
    """
    if t < 20:
        return t_early
    elif t <= 50:
        return t_mid
    else:
        # Graceful decay from t_mid to 0 at t = 59
        return t_mid * max(0.0, (59 - t) / 9.0)


def threshold_smooth_cosine(t, t_max=0.028, t_min=0.0):
    """Smooth decay reflecting arrival phase and terminal horizon."""
    if t < 20:
        return t_max
    elif t <= 50:
        # linear transition from t_max to 0.020
        return t_max - (t_max - 0.020) * ((t - 20) / 30.0)
    else:
        return 0.020 * max(0.0, (59 - t) / 9.0)


# ==============================================================================
# Simulation Engine
# ==============================================================================

def run_simulation(seed, matching_policy_type='adaptive', custom_fn=None, variant='development'):
    world = kit.generate(seed, 200, 'dev_01', variant)
    sim = kit.Simulator(world)

    history = {
        'intro_days': [],
        'intro_scores': [],
        'intro_p_msmi': [],
        'intro_pairs': []
    }

    for day in range(60):
        # 1. Ask Phase (baseline clarification)
        state = sim.observe()
        asks = kit.baseline_asks(state)
        sim.resolve_asks(asks)

        # 2. Match Phase
        state = sim.observe()
        available_members = [m for m in state['members'] if m['available']]
        past_intros = {tuple(sorted((i['user_a'], i['user_b']))) for i in state['introductions']}

        member_map = {m['member_id']: m for m in available_members}
        candidate_edges = []

        if matching_policy_type == 'greedy_baseline':
            # Exact baseline logic from kit.py
            for a, b in itertools.combinations(available_members, 2):
                key = tuple(sorted((a['member_id'], b['member_id'])))
                if key in past_intros or kit.eligibility(a, b)['status'] != 'feasible':
                    continue
                score = get_soft_match_score(a, b)
                p_msmi = predict_p_msmi(a, b)
                candidate_edges.append((-score, -p_msmi, key, score, p_msmi))

            used = set()
            pairs = []
            for neg_s, neg_p, pair, s, p in sorted(candidate_edges):
                if not used.intersection(pair):
                    pairs.append(list(pair))
                    used.update(pair)
                    history['intro_days'].append(day)
                    history['intro_scores'].append(s)
                    history['intro_p_msmi'].append(p)
                    history['intro_pairs'].append(pair)
            sim.advance(pairs)

        elif matching_policy_type in ('adaptive', 'static', 'smooth'):
            thresh_fn = (threshold_adaptive_temporal if matching_policy_type == 'adaptive'
                         else threshold_static if matching_policy_type == 'static'
                         else threshold_smooth_cosine)
            thresh = thresh_fn(day)

            for a, b in itertools.combinations(available_members, 2):
                key = tuple(sorted((a['member_id'], b['member_id'])))
                if key in past_intros or kit.eligibility(a, b)['status'] != 'feasible':
                    continue
                p_msmi = predict_p_msmi(a, b)
                if p_msmi >= thresh:
                    score = get_soft_match_score(a, b)
                    # Sort primarily by expected MSMI, secondarily by soft score
                    candidate_edges.append((-p_msmi, -score, key, score, p_msmi))

            used = set()
            pairs = []
            for neg_p, neg_s, pair, s, p in sorted(candidate_edges):
                if not used.intersection(pair):
                    pairs.append(list(pair))
                    used.update(pair)
                    history['intro_days'].append(day)
                    history['intro_scores'].append(s)
                    history['intro_p_msmi'].append(p)
                    history['intro_pairs'].append(pair)
            sim.advance(pairs)

        elif matching_policy_type == 'shadow_price':
            # Member-specific shadow prices u_i(t)
            degrees = Counter()
            cand_pairs = []
            for a, b in itertools.combinations(available_members, 2):
                key = tuple(sorted((a['member_id'], b['member_id'])))
                if key in past_intros or kit.eligibility(a, b)['status'] != 'feasible':
                    continue
                p_msmi = predict_p_msmi(a, b)
                score = get_soft_match_score(a, b)
                cand_pairs.append((p_msmi, score, key, a, b))
                degrees[a['member_id']] += 1
                degrees[b['member_id']] += 1

            base_o = threshold_adaptive_temporal(day)
            for p_msmi, score, key, a, b in cand_pairs:
                da = degrees[a['member_id']]
                db = degrees[b['member_id']]
                # Degree scarcity adjustment: members with high degrees have higher shadow price
                # avg degree is ~8-12; degrees below 3 have reduced opportunity cost
                opt_a = 0.5 * (1.0 + min(1.0, da / 10.0))
                opt_b = 0.5 * (1.0 + min(1.0, db / 10.0))
                u_pair = base_o * 0.5 * (opt_a + opt_b)
                if p_msmi >= u_pair:
                    surplus = p_msmi - u_pair
                    candidate_edges.append((-surplus, -p_msmi, key, score, p_msmi))

            used = set()
            pairs = []
            for neg_surplus, neg_p, pair, s, p in sorted(candidate_edges):
                if not used.intersection(pair):
                    pairs.append(list(pair))
                    used.update(pair)
                    history['intro_days'].append(day)
                    history['intro_scores'].append(s)
                    history['intro_p_msmi'].append(p)
                    history['intro_pairs'].append(pair)
            sim.advance(pairs)

    # 40 follow-up days for outcome maturation
    for _ in range(40):
        sim.advance([])

    # Compute comprehensive metrics
    metrics = sim.metrics()
    arrived = {m['member_id']: m['arrived_day'] for m in sim.observe()['members'] if m['arrived_day'] <= 59}
    first_intro = {}
    for intro in sim.introductions:
        for m in (intro['user_a'], intro['user_b']):
            first_intro.setdefault(m, intro['assigned_day'])

    waits = [first_intro[m] - arrived[m] for m in first_intro if m in arrived]

    served_count = len(first_intro)
    total_arrived = len(arrived)
    coverage = served_count / max(1, total_arrived)

    # Temporal breakdown
    early_intros = sum(1 for d in history['intro_days'] if d < 20)
    mid_intros = sum(1 for d in history['intro_days'] if 20 <= d <= 50)
    late_intros = sum(1 for d in history['intro_days'] if d > 50)

    # Match quality stats
    mean_p = statistics.mean(history['intro_p_msmi']) if history['intro_p_msmi'] else 0.0
    zero_score_intros = sum(1 for s in history['intro_scores'] if s == 0)
    score_counter = dict(Counter(history['intro_scores']))

    summary = {
        'seed': seed,
        'policy': matching_policy_type,
        'assignments': metrics['assignments'],
        'mutual_acceptances': metrics['mutual_acceptances'],
        'mutual_acceptances_per_100': 100.0 * metrics['mutual_acceptances'] / total_arrived,
        'dates': metrics['dates'],
        'msmi': metrics['mutual_second_meeting_intention'],
        'msmi_per_100': metrics['msmi_per_100_arrived_members'],
        'coverage': coverage,
        'served_members': served_count,
        'unserved_members': total_arrived - served_count,
        'mean_wait_days': statistics.mean(waits) if waits else 0.0,
        'median_wait_days': statistics.median(waits) if waits else 0.0,
        'max_wait_days': max(waits) if waits else 0.0,
        'ask_cost': metrics['ask_cost'],
        'missing_feedback': metrics['missing_feedback'],
        'early_intros_d0_19': early_intros,
        'mid_intros_d20_50': mid_intros,
        'late_intros_d51_59': late_intros,
        'mean_p_msmi': mean_p,
        'zero_score_intros': zero_score_intros,
        'zero_score_ratio': zero_score_intros / max(1, metrics['assignments']),
        'score_distribution': score_counter
    }
    return summary


def main():
    print("=" * 80)
    print("EXPERIMENT 1: SEED 101 BENCHMARK (UNCONSTRAINED GREEDY VS TEMPORAL THRESHOLD)")
    print("=" * 80)

    policies = [
        ('greedy_baseline', 'Unconstrained Greedy Baseline (T(t)=0)'),
        ('static', 'Static Threshold (T=0.030)'),
        ('adaptive', 'Adaptive Temporal Threshold T(t) [0.027 -> 0.022 -> 0.0]'),
        ('shadow_price', 'Dynamic Shadow Price Matching u_i(t) + u_j(t)'),
    ]

    results_101 = {}
    for p_key, p_name in policies:
        res = run_simulation(101, matching_policy_type=p_key)
        results_101[p_key] = res
        print(f"\n--- {p_name} ---")
        print(f"  Assignments:                 {res['assignments']}")
        print(f"  Mutual Acceptances:          {res['mutual_acceptances']} ({res['mutual_acceptances_per_100']:.1f} per 100)")
        print(f"  Dates:                       {res['dates']}")
        print(f"  MSMI:                        {res['msmi']} ({res['msmi_per_100']:.1f} per 100)")
        print(f"  Coverage:                    {res['coverage']*100:.1f}% ({res['served_members']} served / {res['unserved_members']} unserved)")
        print(f"  Mean / Median Wait Days:     {res['mean_wait_days']:.1f}d / {res['median_wait_days']:.1f}d (Max: {res['max_wait_days']}d)")
        print(f"  Temporal Breakdown:          Day 0-19: {res['early_intros_d0_19']}, Day 20-50: {res['mid_intros_d20_50']}, Day 51-59: {res['late_intros_d51_59']}")
        print(f"  Mean P(MSMI) of Matches:     {res['mean_p_msmi']:.4f}")
        print(f"  Score 0 Matches (mismatches): {res['zero_score_intros']} ({res['zero_score_ratio']*100:.1f}%)")
        print(f"  Score Distribution:          {sorted(res['score_distribution'].items())}")

    print("\n" + "=" * 80)
    print("EXPERIMENT 2: MULTI-SEED VALIDATION (SEEDS 101 - 105)")
    print("=" * 80)
    seeds = [101, 102, 103, 104, 105]

    for p_key, p_name in [('greedy_baseline', 'Unconstrained Greedy'), ('adaptive', 'Adaptive Temporal T(t)')]:
        msmi_list = []
        mut_list = []
        assign_list = []
        cov_list = []
        for s in seeds:
            res = run_simulation(s, matching_policy_type=p_key)
            msmi_list.append(res['msmi'])
            mut_list.append(res['mutual_acceptances'])
            assign_list.append(res['assignments'])
            cov_list.append(res['coverage'])
        print(f"\n{p_name} across seeds {seeds}:")
        print(f"  Total MSMI across seeds:   {sum(msmi_list)} (Mean: {statistics.mean(msmi_list):.2f})")
        print(f"  Total Mutual Acceptances:  {sum(mut_list)} (Mean: {statistics.mean(mut_list):.1f})")
        print(f"  Total Assignments:         {sum(assign_list)} (Mean: {statistics.mean(assign_list):.1f})")
        print(f"  Mean Coverage:             {statistics.mean(cov_list)*100:.1f}%")

    # Save output json
    out_path = Path(__file__).resolve().parent / "results_temporal_threshold.json"
    with open(out_path, "w") as f:
        json.dump(results_101, f, indent=2)
    print(f"\nDetailed metrics saved to {out_path}")


if __name__ == '__main__':
    main()
