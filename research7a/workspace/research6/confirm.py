"""Registered confirmatory evaluation for Stage E; fixed-sample alpha=0.01."""
import argparse
import json
import math
from pathlib import Path
import statistics
import numpy as np
from scipy.stats import t


def evaluate_confirmation(commits_root, design_path, bootstrap_seed=90210, reps=10000):
    root = Path(commits_root)
    design = json.loads(Path(design_path).read_text())
    if design['stage'] != 'E':
        raise ValueError("confirm.py is restricted to Stage E confirmatory evaluation")

    rows = [json.loads(p.read_text()) for p in sorted((root / 'commits').glob('*.json'))]
    expected = {(c['policy'], c['seed'], c['family']) for c in design['cells']}
    actual = {(r['policy'], r['seed'], r['family']) for r in rows}
    if expected != actual or len(rows) != len(expected):
        raise ValueError(f"Incomplete grid: {len(rows)} commits found, expected {len(expected)}")

    candidate = design['primary_candidate']
    baseline = design['controls'][0]

    lookup = {(r['policy'], r['seed'], r['family']): r for r in rows}
    seeds = sorted({r['seed'] for r in rows})
    families = ('development', 'sparse', 'cold_start', 'delayed', 'shift', 'drift')

    ds = []
    family_d = {f: [] for f in families}
    for seed in seeds:
        values = []
        for family in families:
            a = lookup[candidate, seed, family]
            b = lookup[baseline, seed, family]
            if not a['valid'] or not b['valid']:
                raise ValueError("Invalid episode in confirmation; retain all rows")
            d = a['msmi_per_100_arrived_members'] - b['msmi_per_100_arrived_members']
            values.append(d)
            family_d[family].append(d)
        ds.append(statistics.mean(values))

    n = len(ds)
    if n != len(seeds) or n < 2:
        raise ValueError("Invalid cluster count")

    mean = statistics.mean(ds)
    sd = statistics.stdev(ds)
    se = sd / math.sqrt(n)

    # Primary 99% CI (two-sided alpha = 0.01)
    crit_99 = float(t.ppf(0.995, n - 1))
    ci_99 = [mean - crit_99 * se, mean + crit_99 * se]

    # Nominal 95% CI (two-sided alpha = 0.05)
    crit_95 = float(t.ppf(0.975, n - 1))
    ci_95 = [mean - crit_95 * se, mean + crit_95 * se]

    p_value = 2 * float(t.sf(abs(mean / se), n - 1)) if se else (1.0 if mean == 0 else 0.0)

    # Fixed seed 90210 bootstrap sensitivity
    rng = np.random.default_rng(bootstrap_seed)
    boot_samples = np.asarray(ds)[rng.integers(0, n, size=(reps, n))].mean(axis=1)
    boot_lo_99, boot_hi_99 = np.quantile(boot_samples, [0.005, 0.995])
    boot_lo_95, boot_hi_95 = np.quantile(boot_samples, [0.025, 0.975])

    # Leave-one-out influence
    loo_means = [statistics.mean(ds[:i] + ds[i+1:]) for i in range(n)]

    is_confirmed_superior = (ci_99[0] > 0.0)

    result = {
        "status": "confirmatory",
        "stage": "E",
        "candidate": candidate,
        "baseline": baseline,
        "n_clusters": n,
        "first_seed": seeds[0],
        "last_seed": seeds[-1],
        "total_episodes": len(rows),
        "primary_alpha": 0.01,
        "primary_confidence": 0.99,
        "mean_difference": mean,
        "paired_sd": sd,
        "se": se,
        "t_statistic": mean / se if se else 0.0,
        "df": n - 1,
        "p_value_two_sided": p_value,
        "standardized_effect": mean / sd if sd else 0.0,
        "primary_ci_99": ci_99,
        "nominal_ci_95": ci_95,
        "bootstrap_sensitivity": {
            "seed": bootstrap_seed,
            "replicates": reps,
            "ci_99": [float(boot_lo_99), float(boot_hi_99)],
            "ci_95": [float(boot_lo_95), float(boot_hi_95)],
            "scope": "whole seed clusters"
        },
        "family_mean_differences": {f: statistics.mean(v) for f, v in family_d.items()},
        "leave_one_seed_influence": {
            "min_mean": min(loo_means),
            "max_mean": max(loo_means),
            "std_loo_means": statistics.stdev(loo_means) if len(loo_means) > 1 else 0.0
        },
        "is_confirmed_superior": is_confirmed_superior,
        "conclusion": "confirmatory superiority established" if is_confirmed_superior else "confirmatory superiority not established; retain greedy baseline"
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True, help="Directory containing Stage E execution")
    parser.add_argument('--output', required=True, help="Path for JSON output")
    args = parser.parse_args()

    root = Path(args.run)
    design_path = root / 'registration.json'
    result = evaluate_confirmation(root, design_path)

    out_file = Path(args.output)
    out_file.write_text(json.dumps(result, indent=2))
    print(f"Confirmatory evaluation written to {out_file}")
    print(f"Candidate: {result['candidate']} vs {result['baseline']}")
    print(f"Mean difference: {result['mean_difference']:.6f}")
    print(f"99% CI: [{result['primary_ci_99'][0]:.6f}, {result['primary_ci_99'][1]:.6f}]")
    print(f"p-value: {result['p_value_two_sided']:.6e}")
    print(f"Verdict: {result['conclusion']}")


if __name__ == '__main__':
    main()
