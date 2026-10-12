import json
import csv
import math
import itertools
from collections import Counter, defaultdict
from pathlib import Path
import sys

REPO_ROOT = Path('/Volumes/1700 APFS/PERSONAL_PROGRAMMING_PROJECTS/romio-juliet/The-Sequential-Matching-Problem')
sys.path.insert(0, str(REPO_ROOT))
from kit import eligibility

DATA_DIR = REPO_ROOT / 'data'
pool_dirs = sorted([d for d in DATA_DIR.glob('public_*') if d.is_dir()])

pool_results = {}
pooled_ages = []
pooled_genders = Counter()
pooled_zones = Counter()
pooled_who_to_meet = Counter()
pooled_who_to_meet_missing = 0
pooled_orientations = Counter()
pooled_edge_genders = Counter()
pooled_pair_statuses = Counter()

for pool_dir in pool_dirs:
    pool_id = pool_dir.name
    with open(pool_dir / 'state.json', 'r') as f:
        state = json.load(f)
    
    members = state['members']
    past_intros = {tuple(sorted((i['user_a'], i['user_b']))) for i in state.get('introductions', [])}
    
    # Ages
    ages = [m['age'] for m in members]
    pooled_ages.extend(ages)
    age_mean = sum(ages) / len(ages)
    age_std = math.sqrt(sum((x - age_mean) ** 2 for x in ages) / len(ages))
    sorted_ages = sorted(ages)
    age_median = (sorted_ages[len(sorted_ages)//2] + sorted_ages[(len(sorted_ages)-1)//2]) / 2
    
    # Genders
    genders = Counter(m['gender'] for m in members)
    pooled_genders.update(genders)
    
    # Zones
    zones = Counter(m['zone'] for m in members)
    pooled_zones.update(zones)
    
    # who_to_meet
    who_to_meet_counts = Counter()
    who_to_meet_missing = 0
    orientations = Counter()
    
    for m in members:
        wtm = m['fields'].get('who_to_meet')
        g = m['gender']
        if wtm is None:
            who_to_meet_missing += 1
            pooled_who_to_meet_missing += 1
            who_to_meet_counts['[MISSING]'] += 1
            pooled_who_to_meet['[MISSING]'] += 1
            orientations['missing'] += 1
            pooled_orientations['missing'] += 1
        else:
            wtm_key = "/".join(sorted(wtm))
            who_to_meet_counts[wtm_key] += 1
            pooled_who_to_meet[wtm_key] += 1
            
            # Sexual orientation categories
            wtm_set = set(wtm)
            if g == 'man':
                if wtm_set == {'woman'}:
                    orientations['men_seeking_women_only'] += 1
                elif wtm_set == {'man'}:
                    orientations['men_seeking_men_only'] += 1
                elif wtm_set == {'non_binary'}:
                    orientations['men_seeking_nb_only'] += 1
                else:
                    orientations['men_seeking_multiple'] += 1
            elif g == 'woman':
                if wtm_set == {'man'}:
                    orientations['women_seeking_men_only'] += 1
                elif wtm_set == {'woman'}:
                    orientations['women_seeking_women_only'] += 1
                elif wtm_set == {'non_binary'}:
                    orientations['women_seeking_nb_only'] += 1
                else:
                    orientations['women_seeking_multiple'] += 1
            elif g == 'non_binary':
                if len(wtm_set) == 1:
                    orientations['nb_seeking_single_gender'] += 1
                else:
                    orientations['nb_seeking_multiple'] += 1
    pooled_orientations.update(orientations)
    
    # Pairwise graph connectivity
    total_pairs = len(members) * (len(members) - 1) // 2
    pair_status = Counter()
    feasible_edges = []
    
    for a, b in itertools.combinations(members, 2):
        res = eligibility(a, b)
        st = res['status']
        pair_status[st] += 1
        pooled_pair_statuses[st] += 1
        if st == 'feasible':
            feasible_edges.append((a, b))
            
    # Degree distribution (all members)
    degrees = defaultdict(int)
    for m in members:
        degrees[m['member_id']] = 0
    for a, b in feasible_edges:
        degrees[a['member_id']] += 1
        degrees[b['member_id']] += 1
        
    deg_list = list(degrees.values())
    deg_mean = sum(deg_list) / len(deg_list)
    deg_std = math.sqrt(sum((x - deg_mean) ** 2 for x in deg_list) / len(deg_list))
    sorted_deg = sorted(deg_list)
    deg_median = (sorted_deg[len(sorted_deg)//2] + sorted_deg[(len(sorted_deg)-1)//2]) / 2
    deg_hist = Counter(deg_list)
    isolated_count = sum(1 for d in deg_list if d == 0)
    
    # Components
    adj = defaultdict(set)
    for a, b in feasible_edges:
        adj[a['member_id']].add(b['member_id'])
        adj[b['member_id']].add(a['member_id'])
    
    visited = set()
    components = []
    for m in members:
        mid = m['member_id']
        if mid not in visited:
            comp = []
            q = [mid]
            visited.add(mid)
            while q:
                curr = q.pop(0)
                comp.append(curr)
                for nxt in adj[curr]:
                    if nxt not in visited:
                        visited.add(nxt)
                        q.append(nxt)
            components.append(comp)
    comp_sizes = sorted([len(c) for c in components], reverse=True)
    
    # Bipartiteness & Edge gender pairings
    edge_genders = Counter()
    for a, b in feasible_edges:
        eg = tuple(sorted((a['gender'], b['gender'])))
        eg_str = f"{eg[0]}-{eg[1]}"
        edge_genders[eg_str] += 1
        pooled_edge_genders[eg_str] += 1
        
    # 2-colorability
    color = {}
    is_bipartite = True
    for m in members:
        mid = m['member_id']
        if mid not in color:
            color[mid] = 0
            q = [mid]
            while q and is_bipartite:
                curr = q.pop(0)
                for nxt in adj[curr]:
                    if nxt not in color:
                        color[nxt] = 1 - color[curr]
                        q.append(nxt)
                    elif color[nxt] == color[curr]:
                        is_bipartite = False
                        break
                        
    # Available members graph
    avail_members = [m for m in members if m.get('available', False)]
    avail_feasible_edges = []
    avail_feasible_unintro = []
    avail_degrees = defaultdict(int)
    for m in avail_members:
        avail_degrees[m['member_id']] = 0
        
    for a, b in itertools.combinations(avail_members, 2):
        if eligibility(a, b)['status'] == 'feasible':
            pair_key = tuple(sorted((a['member_id'], b['member_id'])))
            avail_feasible_edges.append(pair_key)
            avail_degrees[a['member_id']] += 1
            avail_degrees[b['member_id']] += 1
            if pair_key not in past_intros:
                avail_feasible_unintro.append(pair_key)
                
    avail_deg_list = list(avail_degrees.values()) if avail_degrees else [0]
    avail_deg_mean = sum(avail_deg_list) / len(avail_deg_list)
    avail_isolated = sum(1 for d in avail_deg_list if d == 0)
    
    pool_results[pool_id] = {
        'pool_id': pool_id,
        'total_members': len(members),
        'available_members': len(avail_members),
        'past_introductions': len(past_intros),
        'age': {
            'min': min(ages), 'max': max(ages),
            'mean': round(age_mean, 2), 'std': round(age_std, 2),
            'median': age_median
        },
        'gender': dict(genders),
        'zones': dict(zones),
        'who_to_meet': dict(who_to_meet_counts),
        'who_to_meet_missing': who_to_meet_missing,
        'orientations': dict(orientations),
        'pair_status': dict(pair_status),
        'feasible_edges': len(feasible_edges),
        'degrees_all': {
            'min': min(deg_list), 'max': max(deg_list),
            'mean': round(deg_mean, 2), 'median': deg_median,
            'std': round(deg_std, 2),
            'isolated_count': isolated_count,
            'isolated_pct': round(isolated_count / len(members) * 100, 2),
            'histogram': {str(k): v for k, v in sorted(deg_hist.items())}
        },
        'connected_components': {
            'total_components': len(components),
            'largest_component': comp_sizes[0] if comp_sizes else 0,
            'components_gt_1': sum(1 for s in comp_sizes if s > 1),
            'top_component_sizes': comp_sizes[:5]
        },
        'graph_structure': {
            'is_bipartite': is_bipartite,
            'edge_gender_breakdown': dict(edge_genders)
        },
        'available_graph': {
            'avail_members': len(avail_members),
            'avail_feasible_edges': len(avail_feasible_edges),
            'avail_feasible_unintroduced': len(avail_feasible_unintro),
            'avail_deg_mean': round(avail_deg_mean, 2),
            'avail_isolated': avail_isolated,
            'avail_isolated_pct': round(avail_isolated / len(avail_members) * 100, 2)
        }
    }

# Pooled stats
pooled_age_mean = sum(pooled_ages) / len(pooled_ages)
pooled_age_std = math.sqrt(sum((x - pooled_age_mean) ** 2 for x in pooled_ages) / len(pooled_ages))
sorted_pooled_ages = sorted(pooled_ages)
pooled_age_median = (sorted_pooled_ages[len(sorted_pooled_ages)//2] + sorted_pooled_ages[(len(sorted_pooled_ages)-1)//2]) / 2

overall_summary = {
    'total_pools': len(pool_dirs),
    'total_members': len(pooled_ages),
    'pooled_age': {
        'min': min(pooled_ages), 'max': max(pooled_ages),
        'mean': round(pooled_age_mean, 2), 'std': round(pooled_age_std, 2),
        'median': pooled_age_median
    },
    'pooled_gender': {k: {'count': v, 'pct': round(v / len(pooled_ages) * 100, 2)} for k, v in pooled_genders.items()},
    'pooled_zones': {k: {'count': v, 'pct': round(v / len(pooled_ages) * 100, 2)} for k, v in pooled_zones.items()},
    'pooled_who_to_meet': {k: {'count': v, 'pct': round(v / len(pooled_ages) * 100, 2)} for k, v in pooled_who_to_meet.items()},
    'pooled_pair_statuses': {k: {'count': v, 'pct': round(v / (10 * 19900) * 100, 2)} for k, v in pooled_pair_statuses.items()},
    'pooled_edge_genders': {k: {'count': v, 'pct': round(v / sum(pooled_edge_genders.values()) * 100, 2)} for k, v in pooled_edge_genders.items()},
}

out_data = {
    'overall_summary': overall_summary,
    'per_pool': pool_results
}

out_path = REPO_ROOT / 'scratch' / 'eda_demographics_results.json'
with open(out_path, 'w') as f:
    json.dump(out_data, f, indent=2)

print("Saved detailed results to", out_path)
print(json.dumps(overall_summary, indent=2))
