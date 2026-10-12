#!/usr/bin/env python3
"""Generate fig1 (primary comparison), fig2 (scenario breakdown), fig5 (calibration)."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

outdir = '/Volumes/1700 APFS/PERSONAL_PROGRAMMING_PROJECTS/romio-juliet/The-Sequential-Matching-Problem/research/plots'
os.makedirs(outdir, exist_ok=True)
sns.set_style('whitegrid')

# ── Fig 1: Primary score comparison ──
fig, ax = plt.subplots(figsize=(8, 3))
methods = ['greedy', 'simple_fifo']
scores = [0.373, 0.331]
colors = ['#2196F3', '#FF9800']
bars = ax.barh(methods, scores, color=colors, height=0.5, edgecolor='black', linewidth=0.5)
ax.set_xlim(0, 0.5)
ax.set_xlabel('MSMI per 100 arrived members', fontsize=11)
ax.set_title('Confirmatory Primary Score (40 seed clusters)', fontsize=13, fontweight='bold')
ax.axvline(x=0.373, color='#2196F3', linestyle='--', alpha=0.5, linewidth=1)
for bar, score in zip(bars, scores):
    ax.text(score + 0.005, bar.get_y() + bar.get_height()/2, f'{score:.3f}',
            va='center', fontsize=11, fontweight='bold')
ax.annotate('Δ = −0.042,  p = 0.096\n95% CI [−0.091, +0.008]',
            xy=(0.35, 0.65), fontsize=9, color='#555',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#f5f5f5', edgecolor='#ccc'))
plt.tight_layout()
fig.savefig(os.path.join(outdir, 'fig1_primary_comparison.png'), dpi=300, bbox_inches='tight')
plt.close()
print('fig1 saved')

# ── Fig 2: Per-scenario breakdown ──
scenarios = ['Development', 'Sparse', 'Cold Start', 'Delayed', 'Shift', 'Drift']
greedy_scores = [0.463, 0.100, 0.438, 0.400, 0.375, 0.463]
candidate_scores = [0.362, 0.087, 0.475, 0.400, 0.312, 0.350]
diffs = [c - g for c, g in zip(candidate_scores, greedy_scores)]

x = np.arange(len(scenarios))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 5))
bars1 = ax.bar(x - width/2, greedy_scores, width, label='greedy', color='#2196F3',
               edgecolor='black', linewidth=0.5)
bars2 = ax.bar(x + width/2, candidate_scores, width, label='simple_fifo', color='#FF9800',
               edgecolor='black', linewidth=0.5)
ax.axhline(y=0.373, color='#2196F3', linestyle='--', alpha=0.5, linewidth=1,
           label='Greedy mean (0.373)')
ax.set_xlabel('Scenario Family', fontsize=11)
ax.set_ylabel('MSMI per 100 arrived', fontsize=11)
ax.set_title('Per-Scenario MSMI/100 (Confirmation, 40 clusters)', fontsize=13, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(scenarios, fontsize=10)
ax.legend(fontsize=9)
ax.set_ylim(0, 0.6)

for i, d in enumerate(diffs):
    max_h = max(greedy_scores[i], candidate_scores[i])
    sign = '+' if d >= 0 else ''
    color = '#2e7d32' if d >= 0 else '#c62828'
    ax.text(x[i], max_h + 0.015, f'{sign}{d:.3f}', ha='center', va='bottom',
            fontsize=8, color=color, fontweight='bold')
plt.tight_layout()
fig.savefig(os.path.join(outdir, 'fig2_scenario_breakdown.png'), dpi=300, bbox_inches='tight')
plt.close()
print('fig2 saved')

# ── Fig 5: Calibration ──
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Left: Funnel calibration
stages = ['Both\nRespond', 'Both\nAccept', 'Date', 'Both\nPositive 2nd', 'Qualified\nTerminal']
predicted = [0.585, 0.177, 0.138, 0.032, 0.0115]
observed = [0.583, 0.134, 0.105, 0.027, 0.0088]

ax1.plot([0.005, 1], [0.005, 1], 'k--', alpha=0.3, label='Perfect calibration')
ax1.scatter(predicted, observed, s=80, c='#2196F3', zorder=5, edgecolors='black', linewidth=0.5)
for i, stage in enumerate(stages):
    offset_x = 0.15 if i < 3 else 0.3
    ax1.annotate(stage.replace('\n', ' '), (predicted[i], observed[i]),
                textcoords="offset points", xytext=(10, -5 if i % 2 == 0 else 8),
                fontsize=7.5, color='#333')
ax1.plot(predicted, observed, '-', color='#2196F3', alpha=0.5)
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xlim(0.005, 1)
ax1.set_ylim(0.005, 1)
ax1.set_xlabel('Mean Predicted Rate', fontsize=10)
ax1.set_ylabel('Mean Observed Rate', fontsize=10)
ax1.set_title('Funnel Calibration (log scale)', fontsize=11, fontweight='bold')
ax1.legend(fontsize=8)

# Right: Reliability diagram
bin_pred = [0.00623, 0.01219]
bin_obs = [0.00840, 0.00882]
bin_n = [2143, 15990]
bin_labels = [f'Bin 1\n(n={bin_n[0]})', f'Bin 2\n(n={bin_n[1]})']

x_pos = np.arange(len(bin_pred))
width = 0.35
bars_p = ax2.bar(x_pos - width/2, bin_pred, width, label='Predicted', color='#FF9800',
                 edgecolor='black', linewidth=0.5)
bars_o = ax2.bar(x_pos + width/2, bin_obs, width, label='Observed', color='#2196F3',
                 edgecolor='black', linewidth=0.5)
ax2.set_xticks(x_pos)
ax2.set_xticklabels(bin_labels, fontsize=9)
ax2.set_ylabel('Terminal Rate', fontsize=10)
ax2.set_title('Terminal Reliability Diagram', fontsize=11, fontweight='bold')
ax2.legend(fontsize=8)
ax2.annotate('Signed error = −0.00281\n(systematic overprediction)',
            xy=(0.55, 0.85), xycoords='axes fraction', fontsize=8.5, color='#c62828',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#fff3e0', edgecolor='#FF9800'))

plt.tight_layout()
fig.savefig(os.path.join(outdir, 'fig5_calibration.png'), dpi=300, bbox_inches='tight')
plt.close()
print('fig5 saved')

# ── Rename funnel plot ──
import shutil
src = os.path.join(outdir, 'fig3_funnel_centered.png')
dst = os.path.join(outdir, 'fig3_funnel.png')
if os.path.exists(src) and not os.path.exists(dst):
    shutil.copy2(src, dst)
    print('fig3 copied')
elif os.path.exists(src):
    print('fig3 already exists')
else:
    # create a simple funnel
    stages_f = ['Introductions\n(18,133)', 'Both Responded\n(10,576)', 'Mutual Accept\n(2,434)',
                'Date Occurred\n(1,912)', 'Both +ve 2nd\n(489)', 'Qualified MSMI\n(159)']
    counts = [18133, 10576, 2434, 1912, 489, 159]
    pcts = [100, 58.3, 13.4, 10.5, 2.7, 0.88]
    blues = ['#bbdefb', '#90caf9', '#64b5f6', '#42a5f5', '#2196f3', '#1565c0']

    fig, ax = plt.subplots(figsize=(10, 5))
    y_pos = np.arange(len(stages_f))[::-1]
    bars = ax.barh(y_pos, counts, color=blues, edgecolor='black', linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(stages_f, fontsize=9)
    for i, (bar, pct) in enumerate(zip(bars, pcts)):
        ax.text(bar.get_width() + 200, bar.get_y() + bar.get_height()/2,
                f'{pct:.1f}%', va='center', fontsize=9)
    ax.axvline(x=179, color='#c62828', linestyle='--', linewidth=1.5,
               label='Greedy qualified (179)')
    ax.set_xlabel('Count', fontsize=10)
    ax.set_title('Outcome Funnel: Introduction to Qualified MSMI', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    plt.tight_layout()
    fig.savefig(dst, dpi=300, bbox_inches='tight')
    plt.close()
    print('fig3 created from scratch')

print('All plots done')
