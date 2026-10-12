import json
import numpy as np

def ece_and_print(y_true, y_prob, n_bins=10):
    bin_limits = np.linspace(0, 1, n_bins + 1)
    bin_lowers = bin_limits[:-1]
    bin_uppers = bin_limits[1:]
    
    ece_val = 0.0
    print(f"| Bin           | Count | True Prop | Pred Prob |")
    print(f"|---------------|-------|-----------|-----------|")
    for lower, upper in zip(bin_lowers, bin_uppers):
        in_bin = (y_prob > lower) & (y_prob <= upper)
        count = in_bin.sum()
        prop_in_bin = in_bin.mean()
        if prop_in_bin > 0:
            accuracy_in_bin = y_true[in_bin].mean()
            avg_confidence_in_bin = y_prob[in_bin].mean()
            ece_val += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
            print(f"| ({lower:.2f}, {upper:.2f}] | {count:5d} | {accuracy_in_bin:.4f}    | {avg_confidence_in_bin:.4f}    |")
    print(f"ECE: {ece_val:.4f}\n")
    return ece_val

def log_loss(y_true, y_prob):
    y_prob = np.clip(y_prob, 1e-15, 1 - 1e-15)
    return -np.mean(y_true * np.log(y_prob) + (1 - y_true) * np.log(1 - y_prob))

def brier_score(y_true, y_prob):
    return np.mean((y_true - y_prob)**2)

def roc_auc(y_true, y_prob):
    # simple O(N log N) auc
    order = np.argsort(y_prob)[::-1]
    y_true = y_true[order]
    
    n_pos = np.sum(y_true)
    n_neg = len(y_true) - n_pos
    if n_pos == 0 or n_neg == 0: return float('nan')
    
    tp = np.cumsum(y_true)
    fp = np.cumsum(1 - y_true)
    auc = np.sum(y_true * (len(y_true) - np.arange(len(y_true)) - 1 - tp + 1)) / (n_pos * n_neg)
    return auc


with open('scratch/outcomes.json', 'r') as f:
    data = json.load(f)

y_terminal_true = np.array([1 if d['y_terminal'] else 0 for d in data])
y_terminal_prob = np.array([d['pred_integrated']['terminal'] for d in data])

print(f"Total samples: {len(y_terminal_true)}")
print(f"Event rate (terminal): {y_terminal_true.mean():.4f}")
print(f"Mean predicted (terminal): {y_terminal_prob.mean():.4f}")
print("--- TERMINAL INTEGRATED MODEL METRICS ---")
print(f"Log Loss: {log_loss(y_terminal_true, y_terminal_prob):.4f}")
print(f"Brier Score: {brier_score(y_terminal_true, y_terminal_prob):.4f}")
print(f"AUC: {roc_auc(y_terminal_true, y_terminal_prob):.4f}")
ece_and_print(y_terminal_true, y_terminal_prob)

y_accept_true = np.array([1 if d['y_mutual_accept'] else 0 for d in data])
y_accept_prob = np.array([d['pred_integrated']['both_accept_unconditional'] for d in data])

print(f"Total samples: {len(y_accept_true)}")
print(f"Event rate (accept): {y_accept_true.mean():.4f}")
print(f"Mean predicted (accept): {y_accept_prob.mean():.4f}")
print("--- ACCEPT INTEGRATED MODEL METRICS ---")
print(f"Log Loss: {log_loss(y_accept_true, y_accept_prob):.4f}")
print(f"Brier Score: {brier_score(y_accept_true, y_accept_prob):.4f}")
print(f"AUC: {roc_auc(y_accept_true, y_accept_prob):.4f}")
ece_and_print(y_accept_true, y_accept_prob)
