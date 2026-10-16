"""Reanalyse existing evidence and render figures. Never runs a policy or simulator.

Run from the repository root: .venv/bin/python final_report/build_assets.py
Only writes beneath final_report/{assets,data}. No fitting or simulation imports.
"""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import platform
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy import stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ASSETS, DATA = HERE / 'assets', HERE / 'data'
for directory in (ASSETS, DATA):
    directory.mkdir(exist_ok=True)
COLORS = {'G': '#202e42', 'G_arr': '#007f78', 'G_lifo': '#709299',
          'G_deg': '#b77c37', 'P': '#9d5367', 'Q6': '#6572a7'}
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.titleweight': 'bold', 'axes.labelcolor': '#243147',
    'text.color': '#243147', 'xtick.color': '#445166', 'ytick.color': '#445166',
    'figure.facecolor': 'white', 'axes.facecolor': 'white', 'savefig.facecolor': 'white',
    'svg.fonttype': 'none', 'svg.hashsalt': 'sequential-matching-final-report-v1', 'axes.grid': False})
MANIFEST = {'analysis': 'saved-result reanalysis; no new simulations or fits',
    'python': platform.python_version(), 'numpy': np.__version__,
    'scipy': scipy.__version__, 'matplotlib': matplotlib.__version__, 'inputs': {}}


def bind(path):
    path = Path(path)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    MANIFEST['inputs'][str(path.relative_to(ROOT))] = {
        'sha256': h.hexdigest(), 'bytes': path.stat().st_size}


def load(relative):
    path = ROOT / relative
    bind(path)
    return json.loads(path.read_text())


def dump(name, value):
    (DATA / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def write_csv(name, rows):
    if not rows:
        return
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with (DATA / name).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def estimate(values):
    x = np.asarray(values, dtype=float)
    n = len(x)
    mean = float(x.mean())
    se = float(x.std(ddof=1) / math.sqrt(n)) if n > 1 else 0.
    crit = float(stats.t.ppf(.975, n - 1)) if n > 1 else 0.
    p = float(2 * stats.t.sf(abs(mean / se), n - 1)) if se else (1. if mean == 0 else 0.)
    return {'mean': mean, 'se': se, 'lower': mean - crit * se,
            'upper': mean + crit * se, 'p_two_sided': p, 'n_seed_clusters': n}


def holm(rows):
    ordered = sorted(rows, key=lambda r: r['p_two_sided'])
    running = 0.
    for rank, row in enumerate(ordered):
        running = max(running, min(1., (len(rows) - rank) * row['p_two_sided']))
        row['holm_p'] = running


def wilson(successes, n):
    if not n:
        return [0., 0.]
    p, z = successes / n, 1.959963984540054
    center = (p + z*z/(2*n)) / (1 + z*z/n)
    half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1 + z*z/n)
    return [center - half, center + half]


def calibration(rows):
    # Rows are (seed, prediction, observed), distinct from probability fitting.
    if not rows:
        return {}
    a = np.asarray(rows, dtype=float)
    p, y = a[:, 1], a[:, 2]
    edges = [0., .0025, .005, .0075, .01, .015, .02, .03, .05, .1, 1.000001]
    bins = []
    for lo, hi in zip(edges, edges[1:]):
        mask = (p >= lo) & (p < hi)
        n = int(mask.sum())
        if n:
            sy = int(y[mask].sum())
            bins.append({'lower': lo, 'upper': hi, 'n': n,
                'prediction': float(p[mask].mean()), 'observed': sy/n,
                'positives': sy, 'wilson': wilson(sy, n)})
    signed_by_seed = [float((a[a[:, 0] == s, 1] - a[a[:, 0] == s, 2]).mean())
                      for s in sorted(set(a[:, 0]))]
    return {'n': len(p), 'positives': int(y.sum()), 'mean_prediction': float(p.mean()),
        'mean_observed': float(y.mean()), 'signed_error_prediction_minus_observed': float((p-y).mean()),
        'brier': float(((p-y)**2).mean()), 'zero_prediction_brier': float(y.mean()),
        'same_sample_prevalence_brier_descriptive': float(y.mean()*(1-y.mean())),
        'ece': float(sum(b['n'] * abs(b['prediction']-b['observed']) for b in bins)/len(p)),
        'seed_mean_signed_error': estimate(signed_by_seed), 'bins': bins}


def savefig(name, fig, subtitle):
    fig.text(.01, .012, subtitle, fontsize=8, color='#5e697a')
    fig.tight_layout(rect=(0, .055, 1, .98))
    for ext in ('png', 'svg'):
        fig.savefig(ASSETS / f'{name}.{ext}', dpi=190, metadata={'Date': None} if ext == 'svg' else None)
    plt.close(fig)


def paired(by, seeds, laws, arm, control='G', metric='msmi_per_100_arrived_members'):
    return [float(np.mean([by[s, law, arm]['metrics'][metric] -
                           by[s, law, control]['metrics'][metric] for law in laws])) for s in seeds]


ALL_CELLS, STUDIES, CAL_ROWS, WAIT, GROUPS, DRIFT_HIST = [], {}, defaultdict(list), {}, [], {}
REPEAT_CELLS = {}
for short, filename in [('q1', 'study_q1_robustness'), ('q2', 'study_q2_priors'), ('q3', 'study_q3_drift')]:
    raw = load(f'research9/round2/results/{filename}.json')
    records, seeds, laws, arms = raw['records'], raw['seeds'], raw['laws'], raw['arms']
    by = {(r['seed'], r['law'], r['arm']): r for r in records}
    expected = set(itertools.product(seeds, laws, arms))
    assert len(by) == len(records) == raw['episodes_count'] == len(expected)
    assert set(by) == expected and all(r['valid'] and r['error'] is None for r in records)
    checks = defaultdict(int)
    for key, r in by.items():
        s, law, arm = key
        m, intros, members = r['metrics'], r['intros'], r['members']
        assert len(members) == m['arrived_members'] == 200
        assert len(intros) == m['assignments']
        assert sum(row[6] for row in intros) == m['mutual_acceptances']
        assert sum(row[7] for row in intros) == m['dates']
        assert sum(row[8] for row in intros) == m['mutual_second_meeting_intention']
        served = sum(row[8] is not None for row in members)
        assert served == m['served_members']
        assert math.isclose(m['coverage'], served / len(members))
        assert math.isclose(m['msmi_per_100_arrived_members'], 100*sum(row[8] for row in intros)/len(members))
        assert m['ask_cost'] == 3*m['hard_asks'] + m['soft_asks']
        assert math.isclose(m['expected_msmi_per_100'], 100*sum(row[5] for row in intros)/len(members), abs_tol=1e-6)
        # Same world across arms; same-order asking controls are checked by digest.
        assert r['world_sha256'] == by[s, law, 'G']['world_sha256']
        if arm in ['G', 'P', 'PS_sim', 'PS_emp', 'PS_flat', 'X1_emp', 'X1_sim',
                   'X1_nocal_emp', 'X1_nolearn_emp', 'X1_oracle']:
            assert r['ask_log_sha256'] == by[s, law, 'G']['ask_log_sha256']
            checks['identical_asking_control_cells'] += 1
        checks['aggregate_row_checks'] += 1
        old = REPEAT_CELLS.get(key)
        signature = (r['world_sha256'], r['action_sha256'], r['ask_log_sha256'],
                     json.dumps(m, sort_keys=True))
        if old is not None:
            assert old == signature
            checks['exact_cross_study_repeat_cells'] += 1
        REPEAT_CELLS[key] = signature
        ALL_CELLS.append({'study': short, 'seed': s, 'law': law, 'arm': arm,
            **{k: v for k, v in m.items() if isinstance(v, (int, float))},
            'max_inprocess_call_seconds': r['timing']['max_call']})
        if short == 'q1':
            waits = WAIT.setdefault(arm, {'served_waits': [], 'arrived': 0, 'served': 0})
            waits['arrived'] += len(members)
            for row in members:
                if row[8] is not None:
                    waits['served_waits'].append(row[8]-row[1])
                    waits['served'] += 1
            if arm == 'G':
                for row in members:
                    GROUPS.append({'seed': s, 'law': law, 'gender': row[2], 'zone': row[3],
                        'age_group': '<30' if row[4] < 30 else ('30-39' if row[4] < 40 else '40+'),
                        'complete_at_arrival': row[5], 'declined_hard': row[6],
                        'served': int(row[8] is not None)})
        for row in intros:
            # Comparable shadow predictions on exactly G's selected Q2 edges.
            if short == 'q2' and arm == 'G':
                for prior, idx in [('sim', 12), ('emp', 13)]:
                    assert row[idx] is not None
                    for stage, pi, yi in [('mutual', 0, 6), ('date', 1, 7), ('terminal', 2, 8)]:
                        CAL_ROWS[f'q2_G_shadow_{prior}_{stage}'].append((s, row[idx][pi], row[yi]))
            if short == 'q3' and row[11] is not None:
                CAL_ROWS[f'q3_{arm}_terminal'].append((s, row[11][2], row[8]))
                if law == 'drift':
                    period = 'pre35' if row[0] < 35 else 'post35'
                    CAL_ROWS[f'q3_drift_{arm}_{period}'].append((s, row[11][2], row[8]))
        if short == 'q3' and r.get('x1_hist'):
            DRIFT_HIST[f'{s}|{law}|{arm}'] = r['x1_hist']
    summaries = {}
    for arm in arms:
        rs = [by[s, l, arm] for s in seeds for l in laws]
        summaries[arm] = {'cells': len(rs), 'qualified_pairs': sum(r['metrics']['mutual_second_meeting_intention'] for r in rs)}
        for metric in ['msmi_per_100_arrived_members', 'expected_msmi_per_100', 'dates_per_100',
                       'coverage', 'assignments', 'mutual_acceptances_per_100', 'ask_cost', 'hard_asks', 'soft_asks', 'missing_feedback']:
            summaries[arm][metric] = float(np.mean([r['metrics'][metric] for r in rs]))
        summaries[arm]['maximum_inprocess_call_seconds'] = max(r['timing']['max_call'] for r in rs)
    contrasts = []
    for arm in arms:
        if arm != 'G':
            vals = paired(by, seeds, laws, arm)
            contrasts.append({'arm': arm, **estimate(vals), 'seed_differences': vals,
                'expected_diagnostic': estimate(paired(by, seeds, laws, arm, metric='expected_msmi_per_100'))})
    holm(contrasts)
    direct = []
    if short == 'q2':
        for base in ['PS', 'N3e']:
            for prior in ['sim', 'flat']:
                direct.append({'contrast': f'{base}_emp - {base}_{prior}',
                    **estimate(paired(by, seeds, laws, f'{base}_emp', f'{base}_{prior}'))})
    if short == 'q3':
        for parent in ['PS_emp', 'X1_nocal_emp', 'X1_nolearn_emp']:
            direct.append({'contrast': f'X1_emp - {parent}', **estimate(paired(by, seeds, laws, 'X1_emp', parent)),
                'same_action_cells': sum(by[s, l, 'X1_emp']['action_sha256'] == by[s, l, parent]['action_sha256'] for s in seeds for l in laws)})
    holm(direct)
    per_law = {l: {a: summaries[a]['msmi_per_100_arrived_members'] for a in []} for l in laws}
    law_contrasts = {}
    for law in laws:
        per_law[law] = {a: float(np.mean([by[s, law, a]['metrics']['msmi_per_100_arrived_members'] for s in seeds])) for a in arms}
        law_contrasts[law] = {a: estimate(paired(by, seeds, [law], a)) for a in arms if a != 'G'}
    STUDIES[short] = {'source': f'research9/round2/results/{filename}.json', 'created_at': raw['created_at'],
        'elapsed_seconds_recorded': raw['elapsed_seconds'], 'seeds': seeds, 'laws': laws, 'arms': arms,
        'episodes': len(records), 'checks': dict(checks), 'summary': summaries,
        'contrasts': contrasts, 'direct_contrasts': direct, 'per_law_means': per_law,
        'per_law_contrasts_unadjusted': law_contrasts,
        'ledger_records': sum('ledger' in r for r in records)}
    del raw, records, by

CAL = {name: calibration(rows) for name, rows in CAL_ROWS.items()}
write_csv('episode_metrics.csv', ALL_CELLS)
write_csv('paired_contrasts.csv', [{'study': q, **{k:v for k,v in row.items() if k not in ('seed_differences', 'expected_diagnostic')}}
          for q, study in STUDIES.items() for row in study['contrasts']])
write_csv('subgroup_member_rows.csv', GROUPS)
WAIT_SUMMARY = {}
for arm, values in WAIT.items():
    x = np.asarray(values['served_waits'])
    WAIT_SUMMARY[arm] = {'arrived_member_episodes': values['arrived'], 'served_member_episodes': values['served'],
        'unserved_fraction': 1-values['served']/values['arrived'], 'mean_served_wait': float(x.mean()),
        'median_served_wait': float(np.median(x)), 'p90_served_wait': float(np.quantile(x, .9)),
        'wait_histogram': {str(int(v)): int((x==v).sum()) for v in sorted(set(x))}}
SUBGROUPS = []
for field in ['complete_at_arrival', 'declined_hard', 'gender', 'age_group', 'zone']:
    for group in sorted(set(r[field] for r in GROUPS), key=str):
        rows = [r for r in GROUPS if r[field] == group]
        unserved = sum(not r['served'] for r in rows)
        SUBGROUPS.append({'field': field, 'group': group, 'n_member_episodes': len(rows),
            'unserved': unserved, 'unserved_fraction': unserved/len(rows)})
write_csv('subgroups_q1_greedy.csv', SUBGROUPS)
dump('study_analysis.json', STUDIES)
dump('calibration.json', CAL)
dump('waiting.json', WAIT_SUMMARY)
write_csv('reliability_bins.csv', [{'series': name, **{k:v for k,v in b.items() if k!='wilson'},
           'wilson_lower': b['wilson'][0], 'wilson_upper': b['wilson'][1]} for name,c in CAL.items() for b in c['bins']])

# Historical reference summaries remain separate from the new descriptive grids.
r1=load('results/extended/confirmation_statistics.json')['comparisons'][0]
r6=load('results/research6/stage_e_confirmation/confirmation_analysis.json')
dump('historical_confirmation.json', {'round1':r1,'research6':r6})
historical=load('results/research/holdout.json')
historical_baselines={}
expected_historical=None
for arm in ['greedy','no_asks','random']:
    rows=[r for r in historical['episodes'] if r['policy']==arm]
    contexts={(r['seed'],r['variant']) for r in rows}
    assert len(rows)==len(contexts)==30 and all(r['valid'] for r in rows)
    assert len({s for s,l in contexts})==5 and len({l for s,l in contexts})==6
    if expected_historical is None:expected_historical=contexts
    assert contexts==expected_historical
    historical_baselines[arm]={'episodes':len(rows),'seeds':sorted({s for s,l in contexts}),
        'qualified_pairs':sum(r['mutual_second_meeting_intention'] for r in rows),
        'mean_msmi':float(np.mean([r['msmi_per_100_arrived_members'] for r in rows])),
        'dates_per_100':float(np.mean([100*r['dates']/r['arrived_members'] for r in rows])),
        'coverage':float(np.mean([r['coverage'] for r in rows])),
        'ask_cost':float(np.mean([r['ask_cost'] for r in rows]))}
dump('historical_baselines.json',historical_baselines)
# 01. Evidence chronology; confidence levels explicitly differ.
fig, ax = plt.subplots(figsize=(9, 3.8))
for y, mean, lo, hi, label in [(1, r1['difference']['mean'], *r1['difference']['ci95'], 'Round 1: simple_fifo − G | 40 seeds | reported 95% CI'),
                             (0, r6['mean_difference'], *r6['primary_ci_99'], 'Research 6: N3_two − G | 571 seeds | reported 99% CI')]:
    ax.errorbar(mean, y, xerr=[[mean-lo], [hi-mean]], fmt='o', capsize=5, color='#007f78', lw=2)
    ax.text(.035, y+.15, f'{mean:+.4f}', fontsize=10)
ax.axvline(0, color='#9aa2ad', lw=1)
ax.set(yticks=[1,0], yticklabels=['Round 1', 'Research 6'], ylim=(-.6,1.6), xlim=(-.11,.08),
       xlabel='Candidate minus Greedy: qualified MSMI per 100 arrived', title='Confirmation did not establish a gain')
savefig('01_confirmation_context', fig, 'Historical machine-readable intervals: Round 1 95% (40 seeds), R6 99% (571 seeds). Different cohorts/confidence levels; do not pool.')


def forest(study, name, title):
    q = STUDIES[study]
    rows = sorted(q['contrasts'], key=lambda r:r['mean'], reverse=True)
    fig, ax = plt.subplots(figsize=(10, max(3.8, .6*len(rows)+1.4)))
    for i, r in enumerate(rows):
        color = COLORS.get(r['arm'], '#007f78')
        ax.errorbar(r['mean'], i, xerr=[[r['mean']-r['lower']], [r['upper']-r['mean']]], fmt='o', capsize=4, color=color, lw=2)
        ax.text(.99, i, f"{r['mean']:+.3f}  |  Holm p={r['holm_p']:.3f}", va='center', ha='right', transform=ax.get_yaxis_transform(), fontsize=9)
    ax.axvline(0, color='#a6adb7', lw=1)
    ax.set(yticks=range(len(rows)), yticklabels=[r['arm'] for r in rows], xlabel='Difference from G: qualified MSMI / 100 arrived', title=title)
    ax.invert_yaxis()
    lo=min(r['lower'] for r in rows); hi=max(r['upper'] for r in rows)
    ax.set_xlim(lo-.025, hi+.18)
    savefig(name, fig, f"{study.upper()}: {len(q['seeds'])} seed clusters; equal law weights within seed; Student-t 95% CIs. Holm within study; exploratory.")

forest('q1','02_robustness_contrasts','Asking order: a positive exploratory signal, not a confirmed winner')
forest('q3','05_adaptive_ablations','Adaptive scoring did not establish an advantage over Greedy')

# 03. Law-by-law effect matrix; all means, no significance encoding.
q=STUDIES['q1']; display=['G_arr','G_lifo','G_deg','Q6','P']
matrix=np.asarray([[q['per_law_means'][l][a]-q['per_law_means'][l]['G'] for a in display] for l in q['laws']])
fig,(ax,bx)=plt.subplots(1,2,figsize=(10,9),gridspec_kw={'width_ratios':[5,1]})
lim=max(abs(matrix.min()),abs(matrix.max()))
im=ax.imshow(matrix,cmap='BrBG',vmin=-lim,vmax=lim,aspect='auto')
for i in range(len(q['laws'])):
    for j in range(len(display)):
        ax.text(j,i,f'{matrix[i,j]:+.2f}',ha='center',va='center',fontsize=9,color='white' if abs(matrix[i,j])>.65*lim else '#253146')
ax.set(xticks=range(5),xticklabels=display,yticks=range(len(q['laws'])),yticklabels=q['laws'],title='Difference from G by condition')
base=np.asarray([q['per_law_means'][l]['G'] for l in q['laws']])
bx.barh(range(len(base)),base,color=COLORS['G']);bx.invert_yaxis();bx.set(yticks=[],xlabel='G MSMI/100',title='G level')
fig.colorbar(im,ax=ax,shrink=.55,label='Candidate − G')
savefig('03_condition_heatmap',fig,'Q1: 12 seeds per law. Descriptive differences; 16 laws are related conditions, not 16 independent replications.')

# 04. Prior sensitivity: realized and host-only conditional expectation.
q=STUDIES['q2'];fig,axes=plt.subplots(1,2,figsize=(11,4.7),sharey=True)
for ax,base in zip(axes,['PS','N3e']):
    labels=['sim','emp','flat'];x=np.arange(3)
    means=[q['summary'][f'{base}_{p}']['msmi_per_100_arrived_members'] for p in labels]
    rb=[q['summary'][f'{base}_{p}']['expected_msmi_per_100'] for p in labels]
    ax.bar(x-.15,means,width=.3,color='#007f78',label='Realized qualified MSMI')
    ax.bar(x+.15,rb,width=.3,color='#b3becd',label='Host-only expectation diagnostic')
    ax.axhline(q['summary']['G']['msmi_per_100_arrived_members'],color=COLORS['G'],ls='--',label='Realized G')
    ax.set(xticks=x,xticklabels=labels,title=base,xlabel='Prior variant')
    for xi,m in zip(x,means):ax.text(xi-.15,m+.012,f'{m:.3f}',ha='center',fontsize=9)
axes[0].set_ylabel('Qualified MSMI per 100 arrived');axes[1].legend(fontsize=8,loc='lower right')
fig.suptitle('Observable-fit priors changed estimates, without establishing a policy gain',fontweight='bold')
savefig('04_prior_sensitivity',fig,'Q2: 12 seeds × 5 laws per arm. emp retains structural assumptions; host expectations are not policy-observable inputs or confirmation.')

# 06. Reliability on identical chosen edges, avoiding policy-selection confounding.
fig,(ax,bx)=plt.subplots(1,2,figsize=(11,4.8))
for prior,color in [('sim','#6572a7'),('emp','#007f78')]:
    c=CAL[f'q2_G_shadow_{prior}_terminal']; bins=[b for b in c['bins'] if b['n'] >= 50]
    xs=np.asarray([b['prediction']*100 for b in bins]);ys=np.asarray([b['observed']*100 for b in bins])
    ax.errorbar(xs,ys,yerr=[ys-np.asarray([b['wilson'][0]*100 for b in bins]),np.asarray([b['wilson'][1]*100 for b in bins])-ys],fmt='o-',capsize=3,color=color,label=f'{prior}, n={c["n"]:,}')
ax.plot([0,7],[0,7],ls='--',color='#a5adb8');ax.set(xlabel='Mean predicted qualified outcome (%)',ylabel='Observed qualified outcome (%)',title='Terminal reliability on G-selected introductions',xlim=(0,2.7),ylim=(0,7));ax.legend(fontsize=8)
stages=['mutual','date','terminal'];x=np.arange(3)
for offset,prior,color in [(-.2,'sim','#6572a7'),(0,'emp','#007f78')]:
    bx.bar(x+offset,[100*CAL[f'q2_G_shadow_{prior}_{s}']['mean_prediction'] for s in stages],width=.2,label=f'{prior} predicted',color=color)
bx.bar(x+.2,[100*CAL[f'q2_G_shadow_emp_{s}']['mean_observed'] for s in stages],width=.2,label='Observed',color='#c18b48')
bx.set(xticks=x,xticklabels=['Mutual yes','Date occurred','Qualified MSMI'],ylabel='Introductions (%)',title='Stage-level predictions and realized outcomes');bx.legend(fontsize=8)
savefig('06_calibration',fig,'Q2 G edges. Reliability displays bins n≥50 (sim omits 8/5,009 rows); all bins retained in data. Wilson bars ignore seed dependence.')

# 07. Directional calibration and applied offsets, standard drift only.
fig,(ax,bx)=plt.subplots(1,2,figsize=(11,4.7))
for i,arm in enumerate(['PS_emp','X1_emp','X1_nocal_emp']):
    for j,period in enumerate(['pre35','post35']):
        c=CAL.get(f'q3_drift_{arm}_{period}',{})
        if c:
            ax.bar(i+(j-.5)*.32,100*c['signed_error_prediction_minus_observed'],width=.3,color=['#acb9c9','#007f78'][j],label=['Assigned before day 35','Assigned day 35–59'][j] if i==0 else None)
ax.axhline(0,color='#a5adb8');ax.set(xticks=range(3),xticklabels=['PS_emp','X1_emp','X1_nocal_emp'],ylabel='Mean prediction − outcome (percentage points)',title='Terminal signed error in standard drift');ax.legend(fontsize=8)
for arm,color in [('X1_emp','#007f78'),('X1_nolearn_emp','#9d5367')]:
    histories=[v for k,v in DRIFT_HIST.items() if k.split('|')[1:] == ['drift',arm]]
    per_day=[]
    for day in range(60):
        vals=[r[5] for hist in histories for r in hist if r[0]==day]
        per_day.append(np.mean(vals) if vals else 0.)
    bx.plot(range(60),per_day,label=arm,color=color)
bx.axvline(35,color='#a5adb8',ls='--');bx.axhline(0,color='#c6cbd2');bx.set(xlabel='Assignment day',ylabel='Mean applied logit offset',title='Recorded directional correction');bx.legend(fontsize=8)
savefig('07_drift_calibration',fig,'Q3 standard drift: 12 seeds; terminal outcomes assigned pre/post change, evaluated after follow-up. Signed error <0 means underprediction.')

# 08. CDF includes only served; adjacent unserved rates prevent survivor-only story.
fig,(ax,bx)=plt.subplots(1,2,figsize=(11,4.8),gridspec_kw={'width_ratios':[2,1]})
for arm in ['G','G_arr','Q6','P']:
    x=np.sort(WAIT[arm]['served_waits']);ax.step(x,np.arange(1,len(x)+1)/len(x),where='post',label=arm,color=COLORS[arm])
ax.set(xlabel='Days from arrival to first introduction',ylabel='Cumulative fraction of served member-episodes',title='Waiting among served members',xlim=(0,59),ylim=(0,1.02));ax.legend()
arms=['G','G_arr','Q6','P'];vals=[100*WAIT_SUMMARY[a]['unserved_fraction'] for a in arms]
bx.bar(arms,vals,color=[COLORS[a] for a in arms]);bx.set(ylabel='Unserved by last assignment day (%)',title='Members with no introduction',ylim=(0,100))
for i,v in enumerate(vals):bx.text(i,v+1,f'{v:.1f}%',ha='center')
savefig('08_waiting_and_coverage',fig,'Q1: 38,400 arrived member-episodes per arm, from 12 seeds × 16 laws × 200 members. Repeated people/worlds across laws; not independent participants.')

# 09. Descriptive access by information and demographic group.
fig,axes=plt.subplots(1,3,figsize=(12,4.7))
for ax,fields,title in [(axes[0],['declined_hard','complete_at_arrival'],'Information status'),(axes[1],['gender'],'Gender'),(axes[2],['age_group'],'Age')]:
    rows=[r for r in SUBGROUPS if r['field'] in fields]
    labs=[]
    for r in rows:
        if r['field']=='declined_hard':lab='Hard decline' if r['group'] else 'No hard decline'
        elif r['field']=='complete_at_arrival':lab='Complete on arrival' if r['group'] else 'Incomplete on arrival'
        else:lab=str(r['group']).replace('_',' ')
        labs.append(lab)
    vals=[100*r['unserved_fraction'] for r in rows]
    ax.barh(range(len(rows)),vals,color='#657d96');ax.invert_yaxis()
    ax.set(yticks=range(len(rows)),yticklabels=labs,xlim=(0,112),xlabel='Unserved (%)',title=title)
    for i,v in enumerate(vals):ax.text(v+1,i,f'{v:.1f}',va='center',fontsize=9)
savefig('09_access_subgroups',fig,'Q1 Greedy only: 38,400 member-episodes. Overlapping categories; observational associations do not establish demographic fairness or causal explanations.')

# 10. Outcome funnel, common denominator, logarithmic scale.
fig,ax=plt.subplots(figsize=(10,4.7));x=np.arange(4)
for arm in ['G','G_arr','P','Q6']:
    rs=[r for r in ALL_CELLS if r['study']=='q1' and r['arm']==arm]
    vals=[np.mean([100*r[k]/r['arrived_members'] for r in rs]) for k in ['assignments','mutual_acceptances','dates','mutual_second_meeting_intention']]
    ax.plot(x,vals,'o-',label=arm,color=COLORS[arm])
    if arm=='G':
        for xi,v in zip(x,vals):ax.annotate(f'{v:.3f}',(xi,v),xytext=(0,9),textcoords='offset points',ha='center',fontsize=9)
ax.set(xticks=x,xticklabels=['Introductions','Mutual acceptance','Date occurred','Qualified MSMI'],yscale='log',ylabel='Events per 100 arrived (log scale)',title='The downstream outcome funnel is much narrower than allocation');ax.legend()
savefig('10_outcome_funnel',fig,'Q1: 192 episodes per arm. Dates occurred is the kit metric, not every date necessarily within 30 days; qualification applies to MSMI.')

# 11. Closed learned screen is distinct from the exploratory 12-seed studies.
screen=load('research9/final_campaign/selection.json')
fig,ax=plt.subplots(figsize=(10,4.5));names=['G','Q6','P','model_greedy','model_soft','model_repair']
vals=[screen['arm_summary'][a]['mean_msmi'] for a in names]
ax.bar(names,vals,color=[COLORS.get(a,'#aeb8c7') for a in names])
for i,a in enumerate(names):ax.text(i,vals[i]+.007,f"{vals[i]:.3f}\n{screen['arm_summary'][a]['qualified_pairs']} qualified",ha='center',fontsize=9)
ax.set(ylabel='Qualified MSMI per 100 arrived',ylim=(0,.4),title='Closed learned-policy screen: no candidate qualified')
savefig('11_closed_learned_screen',fig,'Separate cohort: 8 reused development seed groups × 6 families × 6 arms = 288 audited cells. No confirmation outcomes were opened.')

dump('closed_screen_summary.json', screen)
fig,axes=plt.subplots(1,2,figsize=(10,4.4))
names=['greedy','no_asks','random'];labels=['Greedy','No clarification','Random feasible']
for ax,metric,title in [(axes[0],'mean_msmi','Qualified outcome'),(axes[1],'coverage','Member coverage')]:
    vals=[historical_baselines[a][metric]*(100 if metric=='coverage' else 1) for a in names]
    ax.bar(labels,vals,color=['#202e42','#aeb8c7','#9d5367'])
    ax.set(title=title,ylabel='Served members (%)' if metric=='coverage' else 'Qualified MSMI / 100 arrived')
    ax.set_ylim(0,max(vals)*1.25)
    for i,v in enumerate(vals):ax.text(i,v+max(vals)*.025,f'{v:.1f}%' if metric=='coverage' else f'{v:.3f}',ha='center')
fig.suptitle('Supplied baselines: separate historical matched-seed comparison',fontweight='bold')
savefig('12_supplied_baselines_historical',fig,'Historical holdout: seeds 301–305 × 6 standard families; 30 episodes/arm. Not the 12-seed Round 2 grid; no fresh inference claimed.')
bind(ROOT/'final_report/sources/round1_submission.pdf')
for pattern in ['research9/round2/*.py','research9/round2/policies/*.py','research9/round2/priors/*.json',
                'research6/REPORT.md','research9/final_campaign/prediction_report.json',
                'research9/final_campaign/fit_freeze.json','research9/final_campaign/selection.json',
                'docs/POLICY_INTERFACE.md','docs/SUBMISSION.md','kit.py','policy.py','Dockerfile']:
    for path in sorted(ROOT.glob(pattern)):
        bind(path)
bind(Path(__file__))
MANIFEST['validation']={'recorded_episodes':len(ALL_CELLS),'unique_seed_law_arm_cells':len(REPEAT_CELLS),
    'independent_seed_identifiers':len(set(r['seed'] for r in ALL_CELLS)),
    'recorded_grid_complete':True,'all_recorded_cells_valid':True,
    'stored_row_aggregates_consistent':True,'world_hashes_match_within_cells':True,
    'same_asking_control_hashes_match':True,'repeated_cell_hashes_match':True,
    'scope':'Stored-row consistency only; not independent event reconstruction, sandbox audit, source-at-run attestation, or seed-freshness certification.'}
MANIFEST['outputs']={str(p.relative_to(HERE)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
    for directory in [ASSETS,DATA] for p in sorted(directory.iterdir()) if p.is_file() and p.name!='provenance.json'}
dump('provenance.json', MANIFEST)
print(json.dumps({'validation':MANIFEST['validation'], 'q1':STUDIES['q1']['contrasts'],
    'q2_direct':STUDIES['q2']['direct_contrasts'],'q3_direct':STUDIES['q3']['direct_contrasts'],
    'calibration':{k:{a:v for a,v in c.items() if a not in ['bins','seed_mean_signed_error']} for k,c in CAL.items() if k.startswith('q2_G')},
    'waiting':{k:{a:v for a,v in c.items() if a!='wait_histogram'} for k,c in WAIT_SUMMARY.items()}},indent=2))
