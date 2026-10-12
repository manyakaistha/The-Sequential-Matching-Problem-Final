"""
Benchmark and formulation script for combinatorial matching step.
Compares Greedy matching vs Edmonds' Blossom Maximum Weight Matching (networkx.max_weight_matching).
Analyzes graph bipartiteness, odd cycles, runtime latency (ms), and matching quality.
"""

import time
import json
import itertools
import random
from collections import Counter
from pathlib import Path
import numpy as np
import networkx as nx
from scipy.optimize import linear_sum_assignment

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from kit import generate, Simulator, eligibility, SOFT, HARD


def greedy_matching(nodes, edges_with_weights):
    """
    Greedy baseline matching:
    Sort edges in descending order of weight, pick greedily without overlap.
    edges_with_weights: list of (weight, u, v)
    """
    sorted_edges = sorted(edges_with_weights, key=lambda x: x[0], reverse=True)
    used = set()
    matching = []
    total_weight = 0.0
    for w, u, v in sorted_edges:
        if u not in used and v not in used:
            used.add(u)
            used.add(v)
            matching.append((u, v))
            total_weight += w
    return matching, total_weight


def blossom_max_weight_matching(nodes, edges_with_weights, maxcardinality=False):
    """
    Edmonds' Blossom algorithm via networkx.max_weight_matching.
    Finds optimal maximum weight matching on general (non-bipartite) graph.
    """
    G = nx.Graph()
    G.add_nodes_from(nodes)
    for w, u, v in edges_with_weights:
        G.add_edge(u, v, weight=w)
    
    start_time = time.perf_counter()
    matching_pairs = nx.max_weight_matching(G, maxcardinality=maxcardinality, weight='weight')
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    
    total_weight = 0.0
    matching = []
    for u, v in matching_pairs:
        matching.append((u, v))
        total_weight += G[u][v]['weight']
        
    return matching, total_weight, elapsed_ms


def check_bipartiteness_and_odd_cycles(nodes_dict, edges):
    """
    Inspects graph bipartiteness and identifies odd cycles.
    nodes_dict: {node_id: attributes}
    edges: list of (u, v)
    """
    G = nx.Graph()
    for n, attr in nodes_dict.items():
        G.add_node(n, **attr)
    G.add_edges_from(edges)
    
    is_bip = nx.is_bipartite(G)
    cycles = nx.cycle_basis(G)
    odd_cycles = [c for c in cycles if len(c) % 2 != 0]
    
    triangle_count = sum(1 for c in odd_cycles if len(c) == 3)
    c5_count = sum(1 for c in odd_cycles if len(c) == 5)
    
    example_triangles = []
    for c in odd_cycles:
        if len(c) == 3:
            example_triangles.append({
                'cycle': c,
                'genders': [G.nodes[n].get('gender') for n in c],
                'who_to_meet': [G.nodes[n].get('who_to_meet') for n in c]
            })
            if len(example_triangles) >= 3:
                break
                
    return {
        'is_bipartite': is_bip,
        'num_nodes': G.number_of_nodes(),
        'num_edges': G.number_of_edges(),
        'total_basis_cycles': len(cycles),
        'total_odd_cycles': len(odd_cycles),
        'triangles': triangle_count,
        'c5_cycles': c5_count,
        'example_triangles': example_triangles
    }


def benchmark_200_node_synthetic(num_nodes=200, target_edges=500, num_trials=100, seed=42):
    """
    Benchmarks networkx.max_weight_matching on a 200-node graph with ~500 feasible edges.
    Measures runtime distributions (mean, median, p95, p99, min, max in ms).
    """
    rng = random.Random(seed)
    runtimes = []
    greedy_runtimes = []
    weight_gains = []
    cardinality_diffs = []
    
    edge_prob = (2.0 * target_edges) / (num_nodes * (num_nodes - 1))
    
    for trial in range(num_trials):
        nodes = [f"node_{i}" for i in range(num_nodes)]
        edges = []
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                if rng.random() < edge_prob:
                    # Score between 1 and 7 (like matching SOFT fields)
                    weight = rng.randint(1, 7)
                    edges.append((weight, nodes[i], nodes[j]))
                    
        # Greedy
        t0 = time.perf_counter()
        g_match, g_weight = greedy_matching(nodes, edges)
        g_time = (time.perf_counter() - t0) * 1000.0
        greedy_runtimes.append(g_time)
        
        # Blossom
        b_match, b_weight, b_time = blossom_max_weight_matching(nodes, edges, maxcardinality=False)
        runtimes.append(b_time)
        
        gain_pct = ((b_weight - g_weight) / max(1e-5, g_weight)) * 100.0
        weight_gains.append(gain_pct)
        cardinality_diffs.append(len(b_match) - len(g_match))
        
    return {
        'num_trials': num_trials,
        'num_nodes': num_nodes,
        'target_edges': target_edges,
        'blossom_time_ms': {
            'mean': np.mean(runtimes),
            'median': np.median(runtimes),
            'min': np.min(runtimes),
            'max': np.max(runtimes),
            'p95': np.percentile(runtimes, 95),
            'p99': np.percentile(runtimes, 99)
        },
        'greedy_time_ms': {
            'mean': np.mean(greedy_runtimes),
            'median': np.median(greedy_runtimes),
            'p95': np.percentile(greedy_runtimes, 95)
        },
        'weight_gain_pct': {
            'mean': np.mean(weight_gains),
            'median': np.median(weight_gains),
            'min': np.min(weight_gains),
            'max': np.max(weight_gains)
        },
        'cardinality_diff': {
            'mean': np.mean(cardinality_diffs),
            'blossom_larger_cases': sum(1 for d in cardinality_diffs if d > 0)
        }
    }


def benchmark_edge_density_scaling(num_nodes=200, edge_counts=[100, 250, 500, 1000, 2000, 5000], num_trials=25):
    """
    Measures how Blossom runtime scales with edge density.
    """
    results = []
    rng = random.Random(12345)
    
    for num_edges in edge_counts:
        edge_prob = (2.0 * num_edges) / (num_nodes * (num_nodes - 1))
        times = []
        for _ in range(num_trials):
            nodes = [f"n_{i}" for i in range(num_nodes)]
            edges = []
            for i in range(num_nodes):
                for j in range(i + 1, num_nodes):
                    if rng.random() < edge_prob:
                        edges.append((rng.uniform(1.0, 10.0), nodes[i], nodes[j]))
            _, _, elapsed = blossom_max_weight_matching(nodes, edges)
            times.append(elapsed)
        results.append({
            'num_edges': num_edges,
            'mean_ms': np.mean(times),
            'median_ms': np.median(times),
            'p95_ms': np.percentile(times, 95),
            'max_ms': np.max(times)
        })
    return results


def run_full_dataset_analysis():
    """
    Analyzes all public datasets and runs real daily states through Greedy and Blossom.
    """
    data_dir = Path(__file__).parent.parent / "data"
    public_datasets = sorted(list(data_dir.glob("public_*")))
    
    dataset_reports = []
    for pdir in public_datasets:
        mfile = pdir / "members.jsonl"
        if not mfile.exists():
            continue
        members = [json.loads(line) for line in mfile.read_text().splitlines() if line.strip()]
        
        # Build node info
        nodes_dict = {
            m['member_id']: {
                'gender': m['gender'],
                'age': m['age'],
                'zone': m['zone'],
                'who_to_meet': m['fields'].get('who_to_meet')
            }
            for m in members
        }
        
        # Check all pairs eligibility on observed fields
        feasible_edges = []
        for a, b in itertools.combinations(members, 2):
            if eligibility(a, b)['status'] == 'feasible':
                # Soft score
                score = sum(a['fields'].get(k) is not None and a['fields'].get(k) == b['fields'].get(k) for k in SOFT)
                # base positive weight
                feasible_edges.append((score + 1.0, a['member_id'], b['member_id']))
                
        plain_edges = [(u, v) for _, u, v in feasible_edges]
        bip_stats = check_bipartiteness_and_odd_cycles(nodes_dict, plain_edges)
        
        # Run Greedy vs Blossom
        nodes = list(nodes_dict.keys())
        g_match, g_weight = greedy_matching(nodes, feasible_edges)
        b_match, b_weight, b_time = blossom_max_weight_matching(nodes, feasible_edges)
        
        dataset_reports.append({
            'dataset': pdir.name,
            'nodes': len(members),
            'feasible_edges': len(feasible_edges),
            'is_bipartite': bip_stats['is_bipartite'],
            'odd_cycles': bip_stats['total_odd_cycles'],
            'triangles': bip_stats['triangles'],
            'greedy_pairs': len(g_match),
            'greedy_weight': g_weight,
            'blossom_pairs': len(b_match),
            'blossom_weight': b_weight,
            'weight_gain_pct': ((b_weight - g_weight) / max(1e-5, g_weight)) * 100.0,
            'blossom_runtime_ms': b_time
        })
    return dataset_reports


def test_bipartite_failure_demonstration():
    """
    Demonstrates mathematically and empirically why Scipy's linear_sum_assignment
    cannot be used on this graph:
    1. Any partition of nodes into 2 sets (e.g. Men vs Women+NB) cuts off all intra-set edges.
    2. Shows edges lost and matching weight degradation when artificially forcing bipartite structure.
    """
    world = generate(20260926, 200)
    members = world['members']
    
    # Ground truth edges to see full potential graph
    edges = []
    genders = {m['member_id']: m['gender'] for m in members}
    for a, b in itertools.combinations(members, 2):
        ma = dict(a, fields=a['truth'])
        mb = dict(b, fields=b['truth'])
        if eligibility(ma, mb)['status'] == 'feasible':
            score = sum(ma['fields'].get(k) == mb['fields'].get(k) for k in SOFT)
            edges.append((score + 1.0, a['member_id'], b['member_id']))
            
    # Classify edge types
    edge_types = Counter()
    for _, u, v in edges:
        g1, g2 = sorted([genders[u], genders[v]])
        edge_types[f"{g1}-{g2}"] += 1
        
    # Full Blossom MWM
    nodes = list(genders.keys())
    b_match, b_weight, _ = blossom_max_weight_matching(nodes, edges)
    
    # If we forced bipartite by Men vs Women (ignoring non-binary or putting NB with women)
    # Bipartite only allows edges across set A and set B
    set_A = {m for m, g in genders.items() if g == 'man'}
    set_B = {m for m, g in genders.items() if g != 'man'}
    
    bipartite_edges = [(w, u, v) for w, u, v in edges if (u in set_A and v in set_B) or (u in set_B and v in set_A)]
    lost_edges = len(edges) - len(bipartite_edges)
    
    # Matching on bipartite graph
    bip_match, bip_weight, _ = blossom_max_weight_matching(nodes, bipartite_edges)
    
    return {
        'total_feasible_edges': len(edges),
        'edge_types': dict(edge_types),
        'edges_lost_by_bipartite_assumption': lost_edges,
        'lost_percentage': (lost_edges / len(edges)) * 100.0,
        'blossom_general_weight': b_weight,
        'blossom_general_pairs': len(b_match),
        'bipartite_restricted_weight': bip_weight,
        'bipartite_restricted_pairs': len(bip_match),
        'loss_pct': ((b_weight - bip_weight) / b_weight) * 100.0
    }


def compare_simulator_rollout(seed=20260926, n=200, days=60):
    """
    Compares 60-day sequential simulation rollout using:
    1. Baseline Greedy Matching
    2. Edmonds' Blossom Maximum Weight Matching
    """
    def blossom_match_policy(state):
        members = [m for m in state['members'] if m['available']]
        past = {tuple(sorted((i['user_a'], i['user_b']))) for i in state['introductions']}
        edges = []
        for a, b in itertools.combinations(members, 2):
            key = tuple(sorted((a['member_id'], b['member_id'])))
            if key in past or eligibility(a, b)['status'] != 'feasible':
                continue
            # Score
            score = sum(a['fields'].get(k) is not None and a['fields'].get(k) == b['fields'].get(k) for k in SOFT)
            edges.append((score + 1.0, a['member_id'], b['member_id']))
        nodes = [m['member_id'] for m in members]
        match, _, _ = blossom_max_weight_matching(nodes, edges)
        return [list(p) for p in match]

    from kit import baseline_asks, baseline_match
    
    # 1. Greedy Run
    world1 = generate(seed, n)
    sim_greedy = Simulator(world1)
    t0 = time.perf_counter()
    for _ in range(days):
        sim_greedy.resolve_asks(baseline_asks(sim_greedy.observe()))
        sim_greedy.advance(baseline_match(sim_greedy.observe()))
    for _ in range(40):
        sim_greedy.advance([])
    greedy_time = time.perf_counter() - t0
    m_greedy = sim_greedy.metrics()

    # 2. Blossom Run
    world2 = generate(seed, n)
    sim_blossom = Simulator(world2)
    t0 = time.perf_counter()
    for _ in range(days):
        sim_blossom.resolve_asks(baseline_asks(sim_blossom.observe()))
        sim_blossom.advance(blossom_match_policy(sim_blossom.observe()))
    for _ in range(40):
        sim_blossom.advance([])
    blossom_time = time.perf_counter() - t0
    m_blossom = sim_blossom.metrics()

    return {
        'seed': seed,
        'greedy_metrics': m_greedy,
        'greedy_total_time_s': greedy_time,
        'blossom_metrics': m_blossom,
        'blossom_total_time_s': blossom_time
    }


if __name__ == '__main__':
    print("=" * 70)
    print("STEP 1: CHECKING GRAPH BIPARTITENESS & ODD CYCLES ACROSS DATASETS")
    print("=" * 70)
    dataset_reports = run_full_dataset_analysis()
    for r in dataset_reports:
        print(f"Dataset {r['dataset']}: {r['nodes']} nodes, {r['feasible_edges']} edges | "
              f"Bipartite: {r['is_bipartite']}, Odd Cycles: {r['odd_cycles']}, Triangles: {r['triangles']} | "
              f"Greedy W: {r['greedy_weight']:.1f} vs Blossom W: {r['blossom_weight']:.1f} (+{r['weight_gain_pct']:.2f}%) | "
              f"Blossom time: {r['blossom_runtime_ms']:.2f}ms")

    print("\n" + "=" * 70)
    print("STEP 2: DEMONSTRATING BIPARTITE MATCHING FAILURE (SCIPY / HUNGARIAN)")
    print("=" * 70)
    bip_fail = test_bipartite_failure_demonstration()
    print(f"Total feasible edges: {bip_fail['total_feasible_edges']}")
    print(f"Edge types breakdown: {bip_fail['edge_types']}")
    print(f"Edges eliminated by forcing bipartite structure: {bip_fail['edges_lost_by_bipartite_assumption']} ({bip_fail['lost_percentage']:.1f}%)")
    print(f"General Blossom Weight: {bip_fail['blossom_general_weight']} ({bip_fail['blossom_general_pairs']} pairs)")
    print(f"Bipartite Restricted Weight: {bip_fail['bipartite_restricted_weight']} ({bip_fail['bipartite_restricted_pairs']} pairs)")
    print(f"Quality Loss by forcing bipartite: -{bip_fail['loss_pct']:.2f}%")

    print("\n" + "=" * 70)
    print("STEP 3: RUNTIME BENCHMARK ON 200-NODE GRAPH WITH ~500 FEASIBLE EDGES")
    print("=" * 70)
    bench_200 = benchmark_200_node_synthetic(num_nodes=200, target_edges=500, num_trials=100)
    print("Blossom MWM Runtime (ms) over 100 trials:")
    print(f"  Mean:   {bench_200['blossom_time_ms']['mean']:.2f} ms")
    print(f"  Median: {bench_200['blossom_time_ms']['median']:.2f} ms")
    print(f"  Min:    {bench_200['blossom_time_ms']['min']:.2f} ms")
    print(f"  Max:    {bench_200['blossom_time_ms']['max']:.2f} ms")
    print(f"  P95:    {bench_200['blossom_time_ms']['p95']:.2f} ms")
    print(f"  P99:    {bench_200['blossom_time_ms']['p99']:.2f} ms")
    print(f"Greedy Runtime (ms): Mean = {bench_200['greedy_time_ms']['mean']:.2f} ms")
    print(f"Average Weight Gain of Blossom over Greedy: +{bench_200['weight_gain_pct']['mean']:.2f}% (max: +{bench_200['weight_gain_pct']['max']:.2f}%)")
    print(f"Blossom matched strictly more pairs in {bench_200['cardinality_diff']['blossom_larger_cases']}/{bench_200['num_trials']} trials.")

    print("\n" + "=" * 70)
    print("STEP 4: RUNTIME SCALING ACROSS EDGE DENSITIES (200 NODES)")
    print("=" * 70)
    scaling = benchmark_edge_density_scaling(num_nodes=200, edge_counts=[100, 250, 500, 1000, 2000, 4000])
    for s in scaling:
        print(f"Edges: {s['num_edges']:4d} | Mean: {s['mean_ms']:6.2f} ms | Median: {s['median_ms']:6.2f} ms | P95: {s['p95_ms']:6.2f} ms | Max: {s['max_ms']:6.2f} ms")

    print("\n" + "=" * 70)
    print("STEP 5: FULL 60-DAY SEQUENTIAL ROLLOUT SIMULATOR COMPARISON")
    print("=" * 70)
    rollout_res = compare_simulator_rollout(seed=20260926, n=200, days=60)
    print("Greedy Metrics:")
    for k, v in rollout_res['greedy_metrics'].items():
        print(f"  {k}: {v}")
    print(f"  Greedy total rollout time: {rollout_res['greedy_total_time_s']:.3f} s")
    print("Blossom Metrics:")
    for k, v in rollout_res['blossom_metrics'].items():
        print(f"  {k}: {v}")
    print(f"  Blossom total rollout time: {rollout_res['blossom_total_time_s']:.3f} s")
