"""Primary statistical and mechanism analysis for Research 8 soft query trial.

Calculates:
- Seed-cluster paired differences D_s across the 24 seed groups (averaging over 6 families per seed).
- Predeclared contrasts:
    1. G_random_soft - G (H1 component)
    2. G_targeted_soft - G (H1 component)
    3. G_targeted_soft - G_random_soft (H2: targeted vs random)
- Arm means, standard deviations, standard errors, exploratory 95% CIs.
- Holm-Bonferroni adjusted p-values.
- Stage-by-stage mechanism funnel and diagnostics:
    Assignments, mutual acceptances, dates, qualified MSMI, coverage,
    hard asks, soft asks, daily budget remaining, changed matchings.
"""

from collections import defaultdict
import json
import math
from pathlib import Path
from statistics import mean, stdev
from typing import Any, Dict, List
from scipy.stats import t


def holm_adjust(p_values: List[float]) -> List[float]:
    """Compute step-down Holm-adjusted p-values."""
    m = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    adjusted = [0.0] * m
    cum_max = 0.0
    for rank, (orig_idx, p_val) in enumerate(indexed):
        adj = min(1.0, p_val * (m - rank))
        cum_max = max(cum_max, adj)
        adjusted[orig_idx] = cum_max
    return adjusted


def analyze_results(commits_dir: Path, stage_id: str = "R8_primary") -> Dict[str, Any]:
    commits_dir = Path(commits_dir)
    data = {}
    metrics_by_cell = {}
    arms = defaultdict(list)
    worlds = defaultdict(set)
    denominators = defaultdict(set)

    for p in sorted(commits_dir.glob("*.json")):
        row = json.loads(p.read_text())
        cell = row["cell"]
        if cell.get("stage_id") != stage_id:
            continue
        key = (cell["seed"], cell["family"], cell["policy_id"])
        metric = row["metrics"]

        if not row["is_valid"] or not metric["valid"]:
            raise ValueError(f"Cell {key} is marked invalid: {row.get('error')}")

        denom = metric["arrived_members"]
        count = metric["mutual_second_meeting_intention"]
        endpoint = 100.0 * count / denom

        data[key] = endpoint
        metrics_by_cell[key] = metric
        arms[cell["policy_id"]].append(endpoint)
        worlds[(cell["seed"], cell["family"])].add(row["world_sha256"])
        denominators[(cell["seed"], cell["family"])].add(denom)

    seeds = sorted({k[0] for k in data})
    families = sorted({k[1] for k in data})
    policy_ids = sorted({k[2] for k in data})

    # Paired world check
    for sf, wset in worlds.items():
        if len(wset) != 1:
            raise ValueError(f"World hash mismatch across arms for seed-family {sf}: {wset}")
    for sf, dset in denominators.items():
        if len(dset) != 1:
            raise ValueError(f"Denominator mismatch across arms for seed-family {sf}: {dset}")

    # Compute arm population stats
    arm_summary = {}
    for arm, values in sorted(arms.items()):
        arm_summary[arm] = {
            "n_cells": len(values),
            "mean_msmi": mean(values),
            "std_dev": stdev(values) if len(values) > 1 else 0.0,
            "se": stdev(values) / math.sqrt(len(values)) if len(values) > 1 else 0.0,
        }

    # Predeclared contrasts on seed clusters
    predeclared_contrasts = [
        ("G_random_soft", "G", "H1a: Random soft filling vs No soft filling"),
        ("G_targeted_soft", "G", "H1b: Targeted soft filling vs No soft filling"),
        ("G_targeted_soft", "G_random_soft", "H2: Targeted soft vs Random soft filling"),
    ]

    contrast_results = {}
    raw_p_values = []
    contrast_keys = []

    for cand, parent, desc in predeclared_contrasts:
        if cand not in policy_ids or parent not in policy_ids:
            continue

        diffs = [
            mean(data[(s, f, cand)] - data[(s, f, parent)] for f in families)
            for s in seeds
        ]
        n_clusters = len(diffs)
        avg_diff = mean(diffs)
        sd_cluster = stdev(diffs) if n_clusters > 1 else 0.0
        se_cluster = sd_cluster / math.sqrt(n_clusters) if n_clusters > 1 else 0.0

        if se_cluster > 0:
            t_stat = avg_diff / se_cluster
            df = n_clusters - 1
            p_val = 2.0 * float(t.sf(abs(t_stat), df))
            t_crit = float(t.ppf(0.975, df))
            ci_95 = [avg_diff - t_crit * se_cluster, avg_diff + t_crit * se_cluster]
        else:
            t_stat = 0.0
            p_val = 1.0
            ci_95 = [0.0, 0.0]

        key = f"{cand} - {parent}"
        contrast_keys.append(key)
        raw_p_values.append(p_val)

        contrast_results[key] = {
            "description": desc,
            "candidate": cand,
            "parent": parent,
            "n_clusters": n_clusters,
            "mean_diff": avg_diff,
            "sd_seed_cluster": sd_cluster,
            "se": se_cluster,
            "t_statistic": t_stat,
            "p_value_unadjusted": p_val,
            "ci_95": ci_95,
            "cluster_differences": diffs,
        }

    adjusted_p = holm_adjust(raw_p_values)
    for key, adj_p in zip(contrast_keys, adjusted_p):
        contrast_results[key]["p_value_holm"] = adj_p

    # Mechanism diagnostics by arm
    mechanism_diagnostics = {}
    for arm in policy_ids:
        cell_keys = [k for k in metrics_by_cell if k[2] == arm]
        ms = [metrics_by_cell[k] for k in cell_keys]

        mechanism_diagnostics[arm] = {
            "mean_assignments": mean(m["assignments"] for m in ms),
            "mean_mutual_acceptances": mean(m["mutual_acceptances"] for m in ms),
            "mean_dates": mean(m["dates"] for m in ms),
            "mean_qualified_msmi": mean(m["mutual_second_meeting_intention"] for m in ms),
            "mean_coverage": mean(m["coverage"] for m in ms),
            "mean_hard_asks": mean(m["hard_asks"] for m in ms),
            "mean_soft_asks": mean(m["soft_asks"] for m in ms),
            "mean_total_asks": mean(m["total_asks"] for m in ms),
            "mean_ask_cost": mean(m["ask_cost"] for m in ms),
            "mean_unserved": mean(m["unserved_members"] for m in ms),
        }

    return {
        "stage_id": stage_id,
        "n_seeds": len(seeds),
        "n_families": len(families),
        "total_cells": len(data),
        "arm_summary": arm_summary,
        "contrasts": contrast_results,
        "mechanism_diagnostics": mechanism_diagnostics,
    }
