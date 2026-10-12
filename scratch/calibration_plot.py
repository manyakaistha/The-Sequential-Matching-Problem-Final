import json
import numpy as np

def print_calibration(y_true, y_prob, bins=5):
    edges = np.linspace(0, max(y_prob)+1e-9, bins+1)
    print(f"| Range | Count | True Avg | Pred Avg | Diff |")
    print(f"|---|---|---|---|---|")
    for i in range(bins):
        mask = (y_prob >= edges[i]) & (y_prob < edges[i+1])
        c = mask.sum()
        if c > 0:
            print(f"| {edges[i]:.4f} - {edges[i+1]:.4f} | {c:4d} | {y_true[mask].mean():.5f} | {y_prob[mask].mean():.5f} | {y_prob[mask].mean()-y_true[mask].mean():.5f} |")

with open('scratch/outcomes.json', 'r') as f:
    data = json.load(f)

y_term = np.array([1 if d['y_terminal'] else 0 for d in data])
y_prob_int = np.array([d['pred_integrated']['terminal'] for d in data])

# Let's also compute the simple terminal probability for each log
memory_simple_funnel = [[11.7,8.3],[3.6,16.4],[2.8,17.2],[.65,19.35],[.234,19.766]]
simple_term = memory_simple_funnel[4][0] / sum(memory_simple_funnel[4]) # 0.234 / 20 = 0.0117

print("--- Integrated Model Terminal Calibration ---")
print_calibration(y_term, y_prob_int, bins=5)

