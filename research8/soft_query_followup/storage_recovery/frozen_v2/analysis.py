"""Seed-cluster development analysis, only after independent public-event audit."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
from statistics import mean, stdev

from .audit import audit_run
from .registration import strict_json, write_once


def analyze(output, registration_path):
    from scipy.stats import t
    output, registration_path = Path(output), Path(registration_path)
    closure = audit_run(output, registration_path)
    reg = strict_json(registration_path.read_text())
    seeds, families, arms = reg['ordered_seed_list'], reg['families'], reg['policy_ids']
    rows = {}
    for path in (output / 'commits').glob('*.json'):
        row = strict_json(path.read_text())
        c = row['cell']
        rows[c['seed'], c['family'], c['policy_id']] = row
    expected = {(s, f, a) for s in seeds for f in families for a in arms}
    if set(rows) != expected or len(seeds) < 2 or len(families) != 6:
        raise ValueError('analysis requires complete six-family grid and at least two seed groups')
    def endpoint(key):
        metric = rows[key]['metrics']
        n = metric['arrived_members']
        return 100 * metric['mutual_second_meeting_intention'] / n if n else 0.0
    summaries, family_summary = {}, {}
    for arm in arms:
        values = [endpoint((s, f, arm)) for s in seeds for f in families]
        group_means = [mean(endpoint((s, f, arm)) for f in families) for s in seeds]
        metrics = [rows[s, f, arm]['metrics'] for s in seeds for f in families]
        summaries[arm] = {'n_cells': len(values), 'n_seed_clusters': len(seeds),
                          'mean_msmi': mean(values), 'sd_seed_cluster_mean': stdev(group_means),
                          'se_seed_cluster_mean': stdev(group_means) / math.sqrt(len(seeds)),
                          'qualified_total': sum(m['mutual_second_meeting_intention'] for m in metrics),
                          'mean_qualified_dyads': mean(m['mutual_second_meeting_intention'] for m in metrics),
                          'mean_coverage': mean(m['coverage'] for m in metrics),
                          'mean_hard_asks': mean(m['hard_asks'] for m in metrics),
                          'mean_soft_asks': mean(m['soft_asks'] for m in metrics),
                          'cold_invocation_seconds_max': max(rows[s,f,arm]['invocation_seconds_max'] for s in seeds for f in families)}
        family_summary[arm] = {f: mean(endpoint((s, f, arm)) for s in seeds) for f in families}
    contrasts, pvalues = {}, []
    for candidate, parent in reg['analysis']['contrasts']:
        differences = [mean(endpoint((s, f, candidate)) - endpoint((s, f, parent)) for f in families) for s in seeds]
        average, sd = mean(differences), stdev(differences)
        se = sd / math.sqrt(len(seeds))
        if se:
            statistic = average / se
            pval = float(2 * t.sf(abs(statistic), len(seeds)-1))
            radius = float(t.ppf(.975, len(seeds)-1)) * se
            interval, degenerate = [average-radius, average+radius], None
        else:
            statistic, pval = None, 1.0
            interval = [0.0, 0.0] if average == 0 else None
            degenerate = 'all_ties' if average == 0 else 'constant_nonzero_difference_no_standard_t_inference'
        key = candidate + ' - ' + parent
        contrasts[key] = {'mean_diff': average, 'sd_seed_cluster': sd, 'se': se,
                          'n_clusters': len(seeds), 'df': len(seeds)-1, 't_statistic': statistic,
                          'p_value_unadjusted': pval, 'ci_95_exploratory': interval,
                          'degeneracy': degenerate, 'cluster_differences': differences,
                          'wins': sum(d>0 for d in differences), 'ties': sum(d==0 for d in differences),
                          'losses': sum(d<0 for d in differences)}
        pvalues.append((key, pval))
    prior = 0.0
    for rank, (key, pval) in enumerate(sorted(pvalues, key=lambda v: v[1])):
        prior = max(prior, min(1.0, pval * (len(pvalues)-rank)))
        contrasts[key]['p_value_holm'] = prior
    diagnostics = {}
    for arm in arms:
        records = []
        for s in seeds:
            for f in families:
                attempt = output / rows[s,f,arm]['attempt_relative_path']
                records.extend(strict_json(line) for line in (attempt/'daily_telemetry.jsonl').read_text().splitlines())
        diagnostics[arm] = {'recorded_actor_days_denominator': 'not computed',
                            'daily_records': len(records),
                            'days_with_slack': sum(r['budget_remaining_after_hard']>0 for r in records),
                            'days_with_candidates_and_slack': sum(r['candidate_count']>0 and r['budget_remaining_after_hard']>0 for r in records),
                            'days_matching_changed_after_queries': sum(r['match_changed'] for r in records),
                            'changed_matching_scope': 'own-history pre-answer G versus actual post-answer action; not causal soft-only attribution'}
    return {'status': 'audited_development_results', 'registration_sha256': reg['registration_sha256'],
            'independent_public_event_audit': closure, 'arm_summary': summaries,
            'contrasts': contrasts, 'family_means_descriptive': family_summary,
            'mechanism_diagnostics': diagnostics,
            'inference_scope': 'fixed development experiment; no confirmation or causal mediation claim'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--registration', required=True)
    p.add_argument('--output', required=True, help='run output directory')
    p.add_argument('--report', required=True, help='new JSON report file; never overwritten')
    args = p.parse_args()
    result = analyze(args.output, args.registration)
    write_once(args.report, result)
    print(json.dumps({'status': result['status'], 'report': args.report}))


if __name__ == '__main__':
    main()
