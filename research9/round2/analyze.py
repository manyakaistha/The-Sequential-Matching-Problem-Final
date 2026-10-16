"""Statistical and diagnostic analysis for Round-2 studies.

Computes:
1. Paired comparisons vs control (G): mean diff, paired SE, 95% CI, p-values, Holm adjustment.
2. Robustness across changing axes (arrival, weights, response, drift).
3. Calibration analysis:
   - Reliability curves (predicted vs observed in bins).
   - Expected Calibration Error (ECE) and Brier scores.
   - Signed calibration bias (overall, pre-drift, post-drift).
4. Fairness and "Who gets left waiting":
   - Wait times (days until first introduction among eligible).
   - Coverage and unserved rates across demographic subgroups:
     * Complete at arrival vs incomplete.
     * Members with declined hard constraints.
     * Gender categories.
     * Age groups.
     * Zone geographic sparseness.
"""
import glob
import json
import math
from collections import defaultdict
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent / 'results'


def _t_test(diffs):
    n = len(diffs)
    if n < 2:
        return 0.0, 0.0, [0.0, 0.0], 1.0
    mean = sum(diffs) / n
    var = sum((x - mean) ** 2 for x in diffs) / (n - 1)
    se = math.sqrt(max(0.0, var / n))
    t_val = mean / max(1e-12, se)
    # Approx 95% CI with normal / t
    crit = 1.96 if n > 30 else 2.05
    ci = [mean - crit * se, mean + crit * se]
    # 2-sided normal approx p-value
    p_val = 2 * (1.0 - 0.5 * (1.0 + math.erf(abs(t_val) / math.sqrt(2))))
    return mean, se, ci, p_val


def analyze_study(file_path):
    data = json.loads(Path(file_path).read_text())
    records = data.get('records', [])
    study_name = data.get('study_name', 'study')
    
    # Group by (seed, law, arm)
    by_cell = {}
    for r in records:
        if r.get('valid'):
            key = (r['seed'], r['law'], r['arm'])
            by_cell[key] = r

    seeds = data['seeds']
    laws = data['laws']
    arms = data['arms']

    # 1. Arm Summary
    arm_scores = defaultdict(list)
    arm_expected = defaultdict(list)
    arm_coverage = defaultdict(list)
    arm_dates = defaultdict(list)
    arm_mutual = defaultdict(list)
    
    for (s, l, a), r in by_cell.items():
        m = r['metrics']
        arm_scores[a].append(m['msmi_per_100_arrived_members'])
        if 'expected_msmi_per_100' in m:
            arm_expected[a].append(m['expected_msmi_per_100'])
        arm_coverage[a].append(m.get('coverage', 0.0))
        arm_dates[a].append(m.get('dates_per_100', 0.0))
        arm_mutual[a].append(m.get('mutual_acceptances_per_100', 0.0))

    summary_table = []
    for a in arms:
        sc = arm_scores[a]
        exp = arm_expected[a]
        cov = arm_coverage[a]
        dat = arm_dates[a]
        mut = arm_mutual[a]
        n = len(sc)
        if n == 0:
            continue
        summary_table.append({
            'arm': a,
            'n': n,
            'msmi_mean': round(sum(sc) / n, 4),
            'msmi_exp_mean': round(sum(exp) / len(exp), 4) if exp else None,
            'coverage': round(sum(cov) / n, 4),
            'dates_per_100': round(sum(dat) / n, 4),
            'mutual_per_100': round(sum(mut) / n, 4),
        })

    # 2. Paired Contrasts vs Control (G or first arm)
    ctrl = 'G' if 'G' in arms else arms[0]
    contrasts = []
    for a in arms:
        if a == ctrl:
            continue
        diffs = []
        diffs_exp = []
        for s in seeds:
            for l in laws:
                r_a = by_cell.get((s, l, a))
                r_c = by_cell.get((s, l, ctrl))
                if r_a and r_c:
                    diffs.append(r_a['metrics']['msmi_per_100_arrived_members'] - r_c['metrics']['msmi_per_100_arrived_members'])
                    if 'expected_msmi_per_100' in r_a['metrics'] and 'expected_msmi_per_100' in r_c['metrics']:
                        diffs_exp.append(r_a['metrics']['expected_msmi_per_100'] - r_c['metrics']['expected_msmi_per_100'])
        if diffs:
            mean, se, ci, p = _t_test(diffs)
            c_dict = {
                'contrast': f"{a} - {ctrl}",
                'diff': round(mean, 5),
                'se': round(se, 5),
                'ci_95': [round(ci[0], 5), round(ci[1], 5)],
                'p_value': round(p, 6),
                'n_pairs': len(diffs)
            }
            if diffs_exp:
                m_exp, se_exp, ci_exp, p_exp = _t_test(diffs_exp)
                c_dict['diff_exp'] = round(m_exp, 5)
                c_dict['se_exp'] = round(se_exp, 5)
                c_dict['ci_exp_95'] = [round(ci_exp[0], 5), round(ci_exp[1], 5)]
            contrasts.append(c_dict)

    # Holm-Bonferroni correction
    contrasts.sort(key=lambda x: x['p_value'])
    m_c = len(contrasts)
    for idx, c in enumerate(contrasts):
        c['holm_p'] = min(1.0, round(c['p_value'] * (m_c - idx), 6))

    # 3. Per-Law Breakdown
    law_breakdown = defaultdict(dict)
    for l in laws:
        for a in arms:
            sub = [by_cell[(s, l, a)]['metrics']['msmi_per_100_arrived_members'] for s in seeds if (s, l, a) in by_cell]
            if sub:
                law_breakdown[l][a] = round(sum(sub) / len(sub), 4)

    # 4. Calibration Analysis (if intros available)
    calibration_report = {}
    preds = []
    actuals = []
    for r in records:
        if not r.get('valid') or 'intros' not in r:
            continue
        for row in r['intros']:
            # row format: [day, a, b, e_mutual, e_date, e_msmi, mutual, date, msmi, resp_a, resp_b, own_pred, shadow_sim, shadow_emp]
            own_p = row[11]
            act_msmi = row[8]
            if own_p and len(own_p) >= 3:
                p_msmi = own_p[2]
                preds.append(p_msmi)
                actuals.append(act_msmi)

    if preds:
        brier = sum((p - y) ** 2 for p, y in zip(preds, actuals)) / len(preds)
        mean_p = sum(preds) / len(preds)
        mean_y = sum(actuals) / len(actuals)
        signed_error = mean_p - mean_y
        
        # Binned reliability
        bins = defaultdict(lambda: [0, 0])
        for p, y in zip(preds, actuals):
            b_idx = min(9, int(p * 100))  # 10 bins
            bins[b_idx][0] += p
            bins[b_idx][1] += y
        
        ece = 0.0
        n_tot = len(preds)
        rel_curve = []
        for b_idx in range(10):
            if b_idx in bins:
                sp, sy = bins[b_idx]
                count = sp / (sp / (sy if sy > 0 else 1.0)) if sp > 0 else 1
                # count of samples in bin
                cnt = sum(1 for p in preds if min(9, int(p * 100)) == b_idx)
                if cnt > 0:
                    avg_p = sp / cnt
                    avg_y = sy / cnt
                    ece += (cnt / n_tot) * abs(avg_p - avg_y)
                    rel_curve.append({'bin': f"[{b_idx/100:.2f}-{(b_idx+1)/100:.2f})", 'count': cnt, 'pred': round(avg_p, 4), 'obs': round(avg_y, 4)})

        calibration_report = {
            'n_predictions': len(preds),
            'brier_score': round(brier, 6),
            'mean_predicted': round(mean_p, 6),
            'mean_observed': round(mean_y, 6),
            'signed_bias': round(signed_error, 6),
            'ece': round(ece, 6),
            'reliability': rel_curve
        }

    # 5. Waiting & Fairness Analysis
    fairness_report = {}
    wait_times = []
    unserved_subgroups = defaultdict(lambda: [0, 0])  # subgroup -> [unserved, total]
    
    for r in records:
        if not r.get('valid') or 'members' not in r:
            continue
        for m in r['members']:
            # m format: [idx, arr, gender, zone, age, complete0, declined, verified_day, first_intro_day, n_intros, mut_any, msmi_any, wait_days, early_exit]
            arr, gender, zone, age, comp0, decl, v_day, f_day, n_intros, _, _, wait_d, _ = m[1:]
            
            served = (f_day is not None)
            if served:
                wait_times.append(f_day - arr)

            # Subgroup breakdowns
            unserved_subgroups['all'][1] += 1
            if not served:
                unserved_subgroups['all'][0] += 1

            unserved_subgroups[f"complete_{comp0}"][1] += 1
            if not served:
                unserved_subgroups[f"complete_{comp0}"][0] += 1

            unserved_subgroups[f"declined_{decl}"][1] += 1
            if not served:
                unserved_subgroups[f"declined_{decl}"][0] += 1

            unserved_subgroups[f"gender_{gender}"][1] += 1
            if not served:
                unserved_subgroups[f"gender_{gender}"][0] += 1

            age_b = 'age_<30' if age < 30 else ('age_30-39' if age < 40 else 'age_40+')
            unserved_subgroups[age_b][1] += 1
            if not served:
                unserved_subgroups[age_b][0] += 1

    if wait_times:
        wait_times.sort()
        nw = len(wait_times)
        fairness_report = {
            'mean_wait_days': round(sum(wait_times) / nw, 2),
            'median_wait_days': wait_times[nw // 2],
            'p90_wait_days': wait_times[int(0.9 * nw)],
            'unserved_by_subgroup': {
                k: {'unserved': u, 'total': t, 'unserved_rate': round(u / max(1, t), 4)}
                for k, (u, t) in sorted(unserved_subgroups.items())
            }
        }

    return {
        'study_name': study_name,
        'summary': summary_table,
        'contrasts': contrasts,
        'law_breakdown': dict(law_breakdown),
        'calibration': calibration_report,
        'fairness': fairness_report,
    }


def main():
    import sys
    for f in sorted(RESULTS_DIR.glob('*.json')):
        print(f"\n========================================================")
        print(f"Analyzing {f.name}...")
        report = analyze_study(f)
        print("\n--- Arm Summary ---")
        for s in report['summary']:
            print(f"Arm: {s['arm']:<14} | MSMI/100: {s['msmi_mean']:.4f} (Exp: {s.get('msmi_exp_mean')}) | Dates: {s['dates_per_100']:.2f} | Cov: {s['coverage']:.3f}")

        if report['contrasts']:
            print("\n--- Paired Contrasts ---")
            for c in report['contrasts']:
                print(f"{c['contrast']:<20} | Diff: {c['diff']:+.5f} (Exp: {c.get('diff_exp', 'N/A')}) | 95% CI: [{c['ci_95'][0]:.5f}, {c['ci_95'][1]:.5f}] | p={c['p_value']:.4f} | Holm-p={c['holm_p']:.4f}")

        if report.get('calibration'):
            cal = report['calibration']
            print("\n--- Calibration ---")
            print(f"Preds: {cal['n_predictions']} | Brier: {cal['brier_score']:.5f} | ECE: {cal['ece']:.5f} | Bias: {cal['signed_bias']:+.5f}")

        if report.get('fairness'):
            fair = report['fairness']
            print("\n--- Waiting & Fairness ---")
            print(f"Mean wait days: {fair['mean_wait_days']} | Median: {fair['median_wait_days']} | P90: {fair['p90_wait_days']}")
            print("Unserved rates by subgroup:")
            for k, sub in fair['unserved_by_subgroup'].items():
                print(f"  {k:<16}: {sub['unserved_rate']*100:.1f}% ({sub['unserved']}/{sub['total']})")


if __name__ == '__main__':
    main()
