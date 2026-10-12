"""Fixed-model prospective C greedy cohort; public observations/labels only.

No fitting, world reconstruction, action-value estimation or confirmation reads.
The script refuses incomplete data and missing full prospective public states.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
import sys
import time
import numpy as np
from scipy.stats import t
from research3.model_candidates import population, response_counts, response_second
from research.terminal_model import FEATURES, PRIOR_RESPONSE, equality_probabilities, integrated
from research4.candidates import (acceptance_posteriors, personalized_population,
                                  uniform_second)

MODELS = ('population', 'beta', 'uniform', 'acceptance')
CONTRASTS = (('beta', 'population'), ('uniform', 'beta'),
             ('acceptance', 'uniform'), ('acceptance', 'population'))
FAMILIES = ('development', 'sparse', 'cold_start', 'delayed', 'shift', 'drift')
STAGES = ('both_response', 'mutual_acceptance', 'date', 'positive_pause', 'terminal')


@lru_cache(maxsize=512)
def uniform_first(successes, failures):
    low, high = Fraction(55, 100), Fraction(98, 100)
    def z(power):
        return sum(((-1)**j*math.comb(failures, j)*
                    (high**(power+j+1)-low**(power+j+1))/(power+j+1)
                    for j in range(failures+1)), Fraction(0))
    return float(z(successes+1)/z(successes))


def funnel_predictions(a, b, day, counts, actors):
    """Coherent projections of the fixed approximate scorer's generative model."""
    eq = equality_probabilities(a, b)
    prior_second = (.55**2+.55*.98+.98**2)/3
    result = {}
    for model in MODELS:
        moments = []
        for member in (a, b):
            s, f = counts.get(member['member_id'], (0, 0))
            if model == 'population':
                moments.append((.765, prior_second))
            elif model == 'beta':
                alpha, beta = PRIOR_RESPONSE[0]+s, PRIOR_RESPONSE[1]+f
                moments.append((alpha/(alpha+beta), response_second((s, f))))
            else:
                moments.append((uniform_first(s, f), uniform_second(s, f)))
        ua, ub = (actors.get(m['member_id'], (0., .49, 0., .25))
                  if model == 'acceptance' else (0., .49, 0., .25) for m in (a, b))
        values = [integrated(eq, ua, ub, day, regime) for regime in range(3)]
        joint_accept = sum(w*v[2] for w, v in zip((4/6, 1/6, 1/6), values))
        joint_all = sum(w*v[4] for w, v in zip((4/6, 1/6, 1/6), values))
        qualified_all = ((3+671/686)/6)*values[0][4]+values[1][4]/6+values[2][4]/6
        response = moments[0][0]*moments[1][0]
        second = moments[0][1]*moments[1][1]
        probabilities = dict(zip(STAGES, (response, response*joint_accept,
            .78*response*joint_accept, .78*second*joint_all, .78*.36*second*qualified_all)))
        assert all(probabilities[b] <= probabilities[a]+1e-12 for a, b in zip(STAGES, STAGES[1:]))
        result[model] = probabilities
    return result


def proper(predictions, labels):
    p, y = np.asarray(predictions, dtype=float), np.asarray(labels, dtype=float)
    if not len(p):
        return None
    if not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
        raise ValueError('invalid probability')
    clipped = np.clip(p, 1e-15, 1-1e-15)
    return {'n': len(p), 'positive': int(y.sum()), 'predicted_mean': float(p.mean()),
            'observed_mean': float(y.mean()),
            'log_loss': float((-y*np.log(clipped)-(1-y)*np.log1p(-clipped)).mean()),
            'brier': float(np.mean((p-y)**2))}


def interval(values):
    a = np.asarray(values, dtype=float)
    mean, n = float(a.mean()), len(a)
    se = float(a.std(ddof=1)/math.sqrt(n))
    radius = float(t.ppf(.975, n-1)*se)
    rng = np.random.default_rng(90210)
    boot = a[rng.integers(0, n, size=(10000, n))].mean(axis=1)
    return {'n_seed_clusters': n, 'mean': mean, 'seed_sd': float(a.std(ddof=1)),
            't95': [mean-radius, mean+radius],
            'bootstrap95': np.quantile(boot, [.025, .975]).tolist(),
            'unadjusted_two_sided_p': float(2*t.sf(abs(mean/se), n-1)) if se else (1. if mean == 0 else 0.),
            'seed_cluster_values': a.tolist()}


def terminal_label(intro, feedback):
    events = [e for e in feedback if e['introduction_id'] == intro['introduction_id']]
    dates = [e for e in events if e['event'] == 'date_happened' and e['value'] is True]
    seconds = [e for e in events if e['event'] == 'second_meeting_intention']
    return int(bool(dates) and len(seconds) == 2 and
               dates[0]['occurred_day']-intro['assigned_day'] <= 30 and
               all(e['value'] == 'yes' and e['occurred_day']-dates[0]['occurred_day'] <= 3
                   for e in seconds))


def outcome_labels(intro, feedback):
    events = [e for e in feedback if e['introduction_id'] == intro['introduction_id']]
    responses = [e for e in events if e['event'] == 'introduction_response']
    dates = [e for e in events if e['event'] == 'date_happened' and e['value'] is True]
    seconds = [e for e in events if e['event'] == 'second_meeting_intention']
    labels = dict(zip(STAGES, map(int, (len(responses) == 2 and all(e['value'] is not None for e in responses),
        len(responses) == 2 and all(e['value'] == 'yes' for e in responses), bool(dates),
        len(seconds) == 2 and all(e['value'] == 'yes' for e in seconds), terminal_label(intro, feedback)))))
    assert all(labels[b] <= labels[a] for a, b in zip(STAGES, STAGES[1:]))
    return labels


def check_public_state(state, day):
    assert state['day'] == day
    forbidden = {'truth', 'seed', 'variant', 'exit_day', 'bias', 'response_rate',
                 'second_bias', 'busy', 'future_events'}
    assert not forbidden.intersection(state)
    for member in state['members']:
        assert not forbidden.intersection(member)
        assert member['arrived_day'] <= day
        assert all(value is None or member['field_observed_day'][key] <= day
                   for key, value in member['fields'].items())
    assert all(i['assigned_day'] < day for i in state['introductions'])
    assert all(e['observed_day'] <= day for e in state['feedback'])
    assert all(a['observed_day'] <= day for a in state.get('ask_log', ()))


def extract_states(trace):
    records = trace.get('match_states')
    if records is None:
        raise ValueError('missing prospective full public match_states; no reconstruction permitted')
    states = {}
    for record in records:
        state = record.get('state', record)
        day = state['day']
        assert day not in states
        check_public_state(state, day)
        states[day] = state
    assert set(states) == set(range(60))
    return states


def audit(source):
    data = json.loads(source.read_text())
    assert data.get('complete') is True
    seeds = list(range(81001, 81033))
    assert data['planned_seeds'] == seeds
    assert set(data['planned_variants']) == set(FAMILIES)
    episodes = [r for r in data['episodes'] if r['policy'] == 'greedy']
    assert len(episodes) == 32*6
    assert {(r['seed'], r['variant']) for r in episodes} == {(s, v) for s in seeds for v in FAMILIES}
    assert all(r['valid'] and r['failure_count'] == 0 and r['optimized_fallback_count'] == 0 for r in episodes)
    rows, trace_hashes = [], {}
    prior_second = (.55**2+.55*.98+.98**2)/3
    for episode in episodes:
        path = Path(episode['trace'])
        trace = json.loads(path.read_text())
        trace_hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        assert trace['policy'] == 'greedy' and trace['seed'] == episode['seed'] and trace['variant'] == episode['variant']
        states = extract_states(trace)
        intros = {(tuple(sorted((i['user_a'], i['user_b']))), i['assigned_day']): i
                  for i in trace['introductions']}
        assert len(intros) == len(trace['assignment_snapshots']) == episode['assignments']
        seen, episode_positives = set(), 0
        day_cache = {}
        for snap in trace['assignment_snapshots']:
            day = snap['assigned_day']; state = states[day]
            ids = tuple(sorted((snap['user_a'], snap['user_b'])))
            key = ids, day
            assert key not in seen; seen.add(key)
            intro = intros[key]
            if day not in day_cache:
                members = {m['member_id']: m for m in state['members']}
                counts = response_counts(state)
                actors = acceptance_posteriors(state)
                day_cache[day] = members, counts, actors
            members, counts, actors = day_cache[day]
            a, b = (members[ident] for ident in ids)
            assert a == snap['member_a'] and b == snap['member_b']
            assert a['available'] and b['available']
            # Calling the actual fixed scoring modules is intentional: this
            # audit assesses deployed forecasts, not a substituted likelihood.
            base = population(a, b, day)[0]
            beta_factor = math.prod(response_second(counts.get(i, (0, 0))) for i in ids)/prior_second**2
            exact_factor = math.prod(uniform_second(*counts.get(i, (0, 0))) for i in ids)/prior_second**2
            predictions = {'population': base, 'beta': base*beta_factor,
                           'uniform': base*exact_factor,
                           'acceptance': personalized_population(a, b, day, actors)*exact_factor}
            funnels = funnel_predictions(a, b, day, counts, actors)
            assert all(abs(funnels[model]['terminal']-predictions[model]) <= 1e-12 for model in MODELS)
            labels = outcome_labels(intro, trace['completed_feedback'])
            label = labels['terminal']
            episode_positives += label
            histories = [sum(counts.get(i, (0, 0))) for i in ids]
            rows.append({'seed': episode['seed'], 'variant': episode['variant'],
                         'day': day, 'introduction_id': intro['introduction_id'],
                         'member_ids': ids, 'predictions': predictions,
                         'terminal_label': label, 'funnel_predictions': funnels, 'labels': labels,
                         'missing_soft_count': sum(m['fields'].get(k) is None for m in (a, b) for k in FEATURES),
                         'history_min': min(histories), 'history_sum': sum(histories),
                         'bias_mean': [actors.get(i, (0., .49, 0., .25))[0] for i in ids]})
        assert episode_positives == episode['mutual_second_meeting_intention']
    # Episode-mean losses, balanced across six families, then across seeds.
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row['seed'], row['variant'])].append(row)
    if set(grouped) != {(s, v) for s in seeds for v in FAMILIES}:
        raise ValueError('zero-assignment episode has undefined assignment loss; do not silently omit')
    episode_losses = {(s, v): {m: proper([r['predictions'][m] for r in rs],
                                          [r['terminal_label'] for r in rs]) for m in MODELS}
                      for (s, v), rs in grouped.items()}
    seed_losses = {s: {m: {metric: float(np.mean([episode_losses[(s, v)][m][metric] for v in FAMILIES]))
                          for metric in ('log_loss', 'brier')} for m in MODELS} for s in seeds}
    contrasts = {}
    for model, control in CONTRASTS:
        name = model+'_minus_'+control
        contrasts[name] = {metric: interval([seed_losses[s][model][metric]-seed_losses[s][control][metric]
                                              for s in seeds]) for metric in ('log_loss', 'brier')}
    tests = sorted((item['unadjusted_two_sided_p'], pair, metric)
                   for pair, metrics in contrasts.items() for metric, item in metrics.items())
    running = 0.
    for rank, (pvalue, pair, metric) in enumerate(tests):
        running = max(running, min(1., (len(tests)-rank)*pvalue))
        contrasts[pair][metric]['holm_p_all8'] = running
    assessment = {m: {'pooled_assignment': proper([r['predictions'][m] for r in rows],
                                                  [r['terminal_label'] for r in rows]),
                      'scenario_seed_balanced': {metric: interval([seed_losses[s][m][metric] for s in seeds])
                                                  for metric in ('log_loss', 'brier')}} for m in MODELS}
    stage_assessment, conditional_assessment = {}, {}
    for model in MODELS:
        stage_assessment[model] = {}
        conditional_assessment[model] = {}
        for stage in STAGES:
            pooled = proper([r['funnel_predictions'][model][stage] for r in rows], [r['labels'][stage] for r in rows])
            episode_scores = {(s, v): proper([r['funnel_predictions'][model][stage] for r in rs],
                                             [r['labels'][stage] for r in rs]) for (s, v), rs in grouped.items()}
            stage_assessment[model][stage] = {'pooled_assignment': pooled,
                'scenario_seed_balanced_means': {metric: float(np.mean([episode_scores[(s, v)][metric]
                                                                        for s in seeds for v in FAMILIES]))
                                                for metric in ('log_loss', 'brier')}}
        for previous, stage in zip(STAGES, STAGES[1:]):
            subset = [r for r in rows if r['labels'][previous]]
            # Ratios are the same approximate joint model's conditional forecasts,
            # not products of independently calibrated stage regressions.
            probs = [r['funnel_predictions'][model][stage]/r['funnel_predictions'][model][previous] for r in subset]
            summary = proper(probs, [r['labels'][stage] for r in subset])
            conditional_assessment[model][stage+'_given_'+previous] = summary
    slices = {}
    axes = {'scenario': lambda r: r['variant'], 'time': lambda r: 'late35plus' if r['day'] >= 35 else 'early',
            'missing': lambda r: '0' if r['missing_soft_count'] == 0 else '1to4' if r['missing_soft_count'] <= 4 else '5to8',
            'history_min': lambda r: 'zero' if r['history_min'] == 0 else '1to2' if r['history_min'] <= 2 else '3plus'}
    for axis, function in axes.items():
        slices[axis] = {}
        for value in sorted({function(r) for r in rows}):
            subset = [r for r in rows if function(r) == value]
            slices[axis][value] = {m: proper([r['predictions'][m] for r in subset],
                                            [r['terminal_label'] for r in subset]) for m in MODELS}
    reliability = {}
    for model in MODELS:
        reliability[model] = []
        for low, high in zip((0., .005, .01, .02, .04), (.005, .01, .02, .04, 1.000001)):
            subset = [r for r in rows if low <= r['predictions'][model] < high]
            if not subset:
                continue
            summary = proper([r['predictions'][model] for r in subset], [r['terminal_label'] for r in subset])
            summary.update(bin=[low, high], supporting_seeds=len({r['seed'] for r in subset}))
            totals = np.asarray([[sum(r['terminal_label'] for r in subset if r['seed'] == seed),
                                  sum(r['seed'] == seed for r in subset)] for seed in seeds])
            rng = np.random.default_rng(90210)
            sums = totals[rng.integers(0, len(seeds), (10000, len(seeds)))].sum(axis=1)
            eligible = sums[:, 1] > 0
            summary['observed_cluster_bootstrap95'] = (np.quantile(sums[eligible, 0]/sums[eligible, 1], [.025, .975]).tolist()
                if summary['supporting_seeds'] >= 6 and 0 < summary['positive'] < summary['n'] else None)
            reliability[model].append(summary)
    return {'n_assignments': len(rows), 'n_positive': sum(r['terminal_label'] for r in rows),
            'n_seed_clusters': len(seeds), 'cohort_seeds': seeds, 'assessment': assessment,
            'stage_assessment': stage_assessment, 'conditional_stage_assessment': conditional_assessment,
            'contrasts': contrasts, 'terminal_slices': slices, 'reliability': reliability,
            'seed_losses': seed_losses, 'prediction_rows': rows, 'trace_sha256': trace_hashes}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='results/research4/focus.json')
    parser.add_argument('--output', default='results/research4/prediction_audit.json')
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise ValueError('refuse overwriting completed audit')
    started, cpu = datetime.now(timezone.utc).isoformat(), time.process_time()
    source = Path(args.input)
    result = audit(source)
    paths = ('research4/candidates.py', 'research4/prediction_audit.py',
             'research3/model_candidates.py', 'research/terminal_model.py')
    result.update(started_utc=started, completed_utc=datetime.now(timezone.utc).isoformat(),
                  input_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  source_sha256={p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths},
                  command=sys.argv, cpu_seconds=time.process_time()-cpu,
                  scope='Fixed prospective terminal forecasts on C greedy cohort only; no fitting; no selection/confirmation data.',
                  estimand='Assignment loss means within episodes, equal six-family means within seed, then equal seed means. Pooled assignment losses separately labeled.',
                  uncertainty='Seed-cluster tCI and10000whole-seed percentile bootstrap, Holm8 contrasts, descriptive pooled slices/reliability. No policy-value or calibration-superiority claim follows automatically.',
                  leakage_checks='All full states recorded before match; public fields/feedback dates <=assignment; prior intros <assignment; pair snapshots equal state members; hidden keys rejected.',
                  funnel_scope='All5stage projections reconstructed coherently from the same fixed approximate generative scorer; terminal equality <=1e-12 against actual evaluatedq required. Stage and conditional-ratio summaries descriptive; primary multiplicity remains8terminal tests.',
                  implementation_scope='Recomputes actual fixed scoring functions from prospective full state; independent public label/uncertainty code. Not an independent numerical reimplementation of forecasts.')
    output.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot([0, .05], [0, .05], 'k--', lw=1)
    for model, bins in result['reliability'].items():
        valid = [b for b in bins if b['observed_cluster_bootstrap95'] is not None]
        unsupported = [b for b in bins if b['observed_cluster_bootstrap95'] is None]
        x, y = [b['predicted_mean'] for b in valid], [b['observed_mean'] for b in valid]
        lo, hi = [b['observed_cluster_bootstrap95'][0] for b in valid], [b['observed_cluster_bootstrap95'][1] for b in valid]
        line = ax.errorbar(x, y, yerr=[[max(0, a-b) for a, b in zip(y, lo)],
                                     [max(0, b-a) for a, b in zip(y, hi)]], fmt='o', capsize=3, label=model)
        ax.scatter([b['predicted_mean'] for b in unsupported], [b['observed_mean'] for b in unsupported],
                   marker='x', color=line.lines[0].get_color())
    ax.set(xlabel='Predicted terminal probability', ylabel='Observed terminal rate',
           title=f'Round4 C common greedy cohort: {result["n_assignments"]} assignments /32 seeds')
    ax.legend()
    fig.text(.02, .005, 'Crosses: uncertainty unavailable; fixed-bin pooled reliability is descriptive.', fontsize=8)
    fig.tight_layout(rect=(0, .03, 1, 1))
    fig.savefig(output.with_suffix('.png'), dpi=160)
    plt.close(fig)
    print(json.dumps({k: result[k] for k in ('n_assignments', 'n_positive', 'cpu_seconds', 'assessment', 'contrasts')}, indent=2))


if __name__ == '__main__':
    main()
