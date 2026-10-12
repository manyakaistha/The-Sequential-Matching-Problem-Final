"""EDA of Missingness and Clarification Mechanics across 10 Public Pools.
Investigates:
1. Missingness rates for each individual field across all 10 pools.
2. Declined fields and rates (field-level and member-level).
3. Simulator missingness generation (kit.py generation logic, MCAR vs block correlation).
4. Cost-benefit analysis of clarification asks (12 units/day budget).
5. Impact of clarifying constraints on pair feasibility (transition matrix & reasons).
"""

import copy
import json
import math
from collections import Counter, defaultdict
import sys
from pathlib import Path

BASE_DIR = Path('/Volumes/1700 APFS/PERSONAL_PROGRAMMING_PROJECTS/romio-juliet/The-Sequential-Matching-Problem')
sys.path.insert(0, str(BASE_DIR))

from kit import HARD, OPTIONS, SOFT, VERSION, eligibility, generate

BASE_DIR = Path('/Volumes/1700 APFS/PERSONAL_PROGRAMMING_PROJECTS/romio-juliet/The-Sequential-Matching-Problem')
DATA_DIR = BASE_DIR / 'data'
ALL_FIELDS = HARD + SOFT


def load_pool_members(pool_name):
    path = DATA_DIR / pool_name / 'members.jsonl'
    members = []
    with path.open() as f:
        for line in f:
            if line.strip():
                members.append(json.loads(line))
    return members


def load_pool_state(pool_name):
    path = DATA_DIR / pool_name / 'state.json'
    with path.open() as f:
        return json.load(f)


def analyze_missingness(all_members):
    """Computes field-level missingness at snapshot (day 30) and at initial arrival."""
    total_members = len(all_members)
    
    # 1. Snapshot missingness (day 30)
    snapshot_counts = {k: Counter() for k in ALL_FIELDS}
    for m in all_members:
        for k in ALL_FIELDS:
            status = m['field_status'].get(k, 'unknown')
            snapshot_counts[k][status] += 1
            
    # 2. Initial arrival missingness (before any rollout asks)
    # If field_observed_day > arrived_day, it was learned via ask during rollout
    initial_counts = {k: Counter() for k in ALL_FIELDS}
    for m in all_members:
        arr_day = m['arrived_day']
        for k in ALL_FIELDS:
            obs_day = m['field_observed_day'].get(k)
            curr_status = m['field_status'].get(k)
            if curr_status == 'declined':
                init_status = 'declined'
            elif obs_day is not None and obs_day == arr_day:
                init_status = 'observed'
            elif obs_day is not None and obs_day > arr_day:
                # Was asked later during rollout
                init_status = 'not_asked'
            else:
                init_status = 'not_asked'
            initial_counts[k][init_status] += 1

    return snapshot_counts, initial_counts, total_members


def analyze_declines(all_members):
    """Computes field-level and member-level decline statistics."""
    total_members = len(all_members)
    
    # Member-level decline metrics
    members_with_declined_hard = 0
    members_with_declined_soft = 0
    members_with_any_declined = 0
    decline_count_dist = Counter()
    hard_decline_count_dist = Counter()
    
    for m in all_members:
        declined_hard = [k for k in HARD if m['field_status'].get(k) == 'declined']
        declined_soft = [k for k in SOFT if m['field_status'].get(k) == 'declined']
        all_declined = declined_hard + declined_soft
        
        if declined_hard:
            members_with_declined_hard += 1
        if declined_soft:
            members_with_declined_soft += 1
        if all_declined:
            members_with_any_declined += 1
            
        decline_count_dist[len(all_declined)] += 1
        hard_decline_count_dist[len(declined_hard)] += 1
        
    return {
        'total_members': total_members,
        'members_with_declined_hard': members_with_declined_hard,
        'pct_with_declined_hard': members_with_declined_hard / total_members * 100,
        'members_with_declined_soft': members_with_declined_soft,
        'pct_with_declined_soft': members_with_declined_soft / total_members * 100,
        'members_with_any_declined': members_with_any_declined,
        'pct_with_any_declined': members_with_any_declined / total_members * 100,
        'decline_count_dist': dict(sorted(decline_count_dist.items())),
        'hard_decline_count_dist': dict(sorted(hard_decline_count_dist.items()))
    }


def analyze_generation_correlation(all_members):
    """Analyzes correlation across fields and correlation with demographics."""
    # Compute pairwise correlation (phi coefficient) of missingness between fields at arrival
    # Let X_i = 1 if field i is observed initially, 0 otherwise
    binary_obs = []
    demographics = []
    
    for m in all_members:
        arr_day = m['arrived_day']
        row = []
        for k in ALL_FIELDS:
            obs_day = m['field_observed_day'].get(k)
            is_obs = 1 if (obs_day is not None and obs_day == arr_day) else 0
            row.append(is_obs)
        binary_obs.append(row)
        demographics.append({
            'age': m['age'],
            'gender': m['gender'],
            'zone': m['zone'],
            'obs_count': sum(row)
        })
        
    n = len(binary_obs)
    # Correlation between fields
    phi_matrix = {}
    pair_phis = []
    for i in range(len(ALL_FIELDS)):
        for j in range(i + 1, len(ALL_FIELDS)):
            f_i = ALL_FIELDS[i]
            f_j = ALL_FIELDS[j]
            x = [binary_obs[r][i] for r in range(n)]
            y = [binary_obs[r][j] for r in range(n)]
            mean_x = sum(x) / n
            mean_y = sum(y) / n
            var_x = sum((val - mean_x) ** 2 for val in x) / n
            var_y = sum((val - mean_y) ** 2 for val in y) / n
            cov = sum((x[r] - mean_x) * (y[r] - mean_y) for r in range(n)) / n
            phi = cov / math.sqrt(var_x * var_y) if var_x > 0 and var_y > 0 else 0
            phi_matrix[f'{f_i}__{f_j}'] = phi
            pair_phis.append(phi)
            
    # Check correlation with demographics
    # Pearson r with age
    ages = [d['age'] for d in demographics]
    obs_counts = [d['obs_count'] for d in demographics]
    mean_age = sum(ages) / n
    mean_obs = sum(obs_counts) / n
    cov_age = sum((ages[r] - mean_age) * (obs_counts[r] - mean_obs) for r in range(n)) / n
    var_age = sum((a - mean_age) ** 2 for a in ages) / n
    var_obs = sum((o - mean_obs) ** 2 for o in obs_counts) / n
    r_age = cov_age / math.sqrt(var_age * var_obs)
    
    # Missingness across genders
    gender_obs = defaultdict(list)
    for d in demographics:
        gender_obs[d['gender']].append(d['obs_count'])
    gender_means = {g: sum(vals) / len(vals) for g, vals in gender_obs.items()}
    
    # Missingness across zones
    zone_obs = defaultdict(list)
    for d in demographics:
        zone_obs[d['zone']].append(d['obs_count'])
    zone_means = {z: sum(vals) / len(vals) for z, vals in zone_obs.items()}
    
    # Complete responders count (18/18 fields observed)
    complete_members = sum(1 for o in obs_counts if o == 18)
    zero_members = sum(1 for o in obs_counts if o == 0)
    
    return {
        'mean_pairwise_phi': sum(pair_phis) / len(pair_phis),
        'min_pairwise_phi': min(pair_phis),
        'max_pairwise_phi': max(pair_phis),
        'r_age_obs_count': r_age,
        'gender_means_obs_count': gender_means,
        'zone_means_obs_count': zone_means,
        'complete_members': complete_members,
        'pct_complete_members': complete_members / n * 100,
        'zero_obs_members': zero_members,
        'obs_count_distribution': dict(Counter(obs_counts))
    }


def analyze_feasibility_transitions(pool_names):
    """Evaluates pair feasibility before and after clarifying constraints."""
    total_pairs = 0
    overall_transitions = Counter()
    failure_reason_counts = Counter()
    
    pool_results = {}
    
    for pool_idx, pool_name in enumerate(pool_names):
        seed = 20261000 + pool_idx
        # Generate world with ground truth
        world = generate(seed, 200, pool_name)
        members_init = world['members']
        
        # Test 1: Full pool (200 members)
        members_pre = copy.deepcopy(members_init)
        
        # Pre-clarification eligibility
        pre_pairs = {}
        for i in range(len(members_pre)):
            for j in range(i + 1, len(members_pre)):
                res = eligibility(members_pre[i], members_pre[j])
                pre_pairs[(i, j)] = res['status']
                
        # Now clarify constraints for everyone where not declined
        members_post = copy.deepcopy(members_pre)
        for m in members_post:
            for k in HARD:
                if m['field_status'][k] != 'declined':
                    m['fields'][k] = copy.deepcopy(m['truth'][k])
                    m['field_status'][k] = 'observed'
                    
        # Post-clarification eligibility
        pool_trans = Counter()
        for i in range(len(members_post)):
            for j in range(i + 1, len(members_post)):
                res_post = eligibility(members_post[i], members_post[j])
                post_status = res_post['status']
                pre_status = pre_pairs[(i, j)]
                pool_trans[(pre_status, post_status)] += 1
                overall_transitions[(pre_status, post_status)] += 1
                if pre_status == 'needs_clarification' and post_status == 'infeasible':
                    for reason in res_post.get('reasons', []):
                        failure_reason_counts[reason] += 1
                        
        n_pairs = len(members_init) * (len(members_init) - 1) // 2
        total_pairs += n_pairs
        pool_results[pool_name] = {
            'total_pairs': n_pairs,
            'transitions': {f'{k[0]} -> {k[1]}': v for k, v in pool_trans.items()}
        }
        
    return {
        'total_pairs_across_10_pools': total_pairs,
        'overall_transitions': {f'{k[0]} -> {k[1]}': v for k, v in overall_transitions.items()},
        'failure_reasons_for_clarified_infeasible': dict(failure_reason_counts.most_common()),
        'pool_results': pool_results
    }


def analyze_ask_logs(pool_names):
    """Analyzes the actual asks made during the 30-day rollout in state.json."""
    total_asks = 0
    total_cost = 0
    ask_fields = Counter()
    unlocked_fields = Counter()
    declined_encountered = Counter()
    
    for pool_name in pool_names:
        state = load_pool_state(pool_name)
        log = state.get('ask_log', [])
        total_asks += len(log)
        for entry in log:
            field = entry['field']
            ask_fields[field] += 1
            cost = 3 if field == 'constraints' else 1
            total_cost += cost
            statuses = entry.get('statuses', {})
            for k, s in statuses.items():
                if s == 'observed':
                    unlocked_fields[k] += 1
                elif s == 'declined':
                    declined_encountered[k] += 1
                    
    return {
        'total_asks': total_asks,
        'total_cost': total_cost,
        'ask_fields': dict(ask_fields),
        'unlocked_fields': dict(unlocked_fields),
        'declined_encountered': dict(declined_encountered)
    }


def run_full_eda():
    pool_names = [f'public_{i:02d}' for i in range(1, 11)]
    print('Loading all 10 pools...')
    all_members = []
    for p in pool_names:
        all_members.extend(load_pool_members(p))
    print(f'Loaded {len(all_members)} members total.\n')
    
    # 1. Missingness analysis
    print('--- Question 1 & 2: Missingness and Declines ---')
    snap_counts, init_counts, n = analyze_missingness(all_members)
    decline_data = analyze_declines(all_members)
    
    # 2. Simulator generation & correlation
    print('--- Question 3: Simulator Generation Analysis ---')
    corr_data = analyze_generation_correlation(all_members)
    
    # 3. Cost-benefit analysis
    print('--- Question 4: Cost-Benefit Analysis of Asks ---')
    ask_log_data = analyze_ask_logs(pool_names)
    
    # 4. Feasibility transitions
    print('--- Question 5: Feasibility Transitions ---')
    trans_data = analyze_feasibility_transitions(pool_names)
    
    # Compile complete results dictionary
    results = {
        'metadata': {
            'total_pools': 10,
            'total_members': n,
            'pools': pool_names
        },
        'field_missingness_snapshot_day30': {
            k: {
                'observed': snap_counts[k]['observed'],
                'observed_pct': snap_counts[k]['observed'] / n * 100,
                'not_asked': snap_counts[k]['not_asked'],
                'not_asked_pct': snap_counts[k]['not_asked'] / n * 100,
                'declined': snap_counts[k]['declined'],
                'declined_pct': snap_counts[k]['declined'] / n * 100,
            }
            for k in ALL_FIELDS
        },
        'field_missingness_arrival': {
            k: {
                'observed': init_counts[k]['observed'],
                'observed_pct': init_counts[k]['observed'] / n * 100,
                'not_asked': init_counts[k]['not_asked'],
                'not_asked_pct': init_counts[k]['not_asked'] / n * 100,
                'declined': init_counts[k]['declined'],
                'declined_pct': init_counts[k]['declined'] / n * 100,
            }
            for k in ALL_FIELDS
        },
        'decline_analysis': decline_data,
        'generation_correlation_analysis': corr_data,
        'cost_benefit_analysis': {
            'daily_budget': 12,
            'constraints_cost': 3,
            'constraints_unlocked_fields': 11,
            'soft_field_cost': 1,
            'soft_fields_total': 7,
            'max_people_unblocked_per_day_matching': 12 // 3,
            'max_people_unblocked_per_day_full_profile': 12 // (3 + 7),
            'wasted_ask_risk_pct_members': decline_data['pct_with_declined_hard'],
            'actual_rollout_asks': ask_log_data
        },
        'feasibility_transition_analysis': trans_data
    }
    
    # Save results to json
    out_json = BASE_DIR / 'scratch' / 'eda_missingness_results.json'
    out_json.write_text(json.dumps(results, indent=2))
    print(f'Saved results to {out_json}')
    
    return results


if __name__ == '__main__':
    run_full_eda()
