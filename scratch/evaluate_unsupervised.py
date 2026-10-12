import json
import numpy as np
from sklearn.metrics import log_loss, brier_score_loss, roc_auc_score

with open('scratch/outcomes.json', 'r') as f:
    data = json.load(f)

y_term = np.array([1 if d['y_terminal'] else 0 for d in data])
y_acc = np.array([1 if d['y_mutual_accept'] else 0 for d in data])

# Unsupervised metric: weighted sum of equalities (based on offline training or just uniform)
# Let's say we just use average equality probability
preds_unsupervised = []
for d in data:
    eq = d['eq']
    # scale it to a valid probability range for log loss, e.g. mapping [0,1] to [0.005, 0.05]
    val = sum(eq) / 4.0
    prob = 0.001 + val * 0.05
    preds_unsupervised.append(prob)

preds_unsupervised = np.array(preds_unsupervised)

print("--- Terminal Unsupervised/Population Rule ---")
print(f"Log Loss: {log_loss(y_term, preds_unsupervised):.4f}")
print(f"Brier Score: {brier_score_loss(y_term, preds_unsupervised):.4f}")
print(f"AUC: {roc_auc_score(y_term, preds_unsupervised):.4f}")
