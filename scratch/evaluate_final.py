import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, brier_score_loss, roc_auc_score

with open('scratch/outcomes_with_seed.json', 'r') as f:
    data = json.load(f)

# Split train/test
train_data = [d for d in data if d['seed'] <= 105]
test_data = [d for d in data if d['seed'] > 105]

def extract(ds):
    X = np.array([d['eq'] for d in ds])
    y = np.array([1 if d['y_terminal'] else 0 for d in ds])
    pred_int = np.array([d['pred_integrated']['terminal'] for d in ds])
    return X, y, pred_int

X_train, y_train, _ = extract(train_data)
X_test, y_test, pred_int_test = extract(test_data)

# Baseline Simple
pred_simple_test = np.full_like(y_test, 0.0117, dtype=float)

# ML Rule
model = LogisticRegression(C=1.0) # Regularized
model.fit(X_train, y_train)
pred_ml_test = model.predict_proba(X_test)[:, 1]

# Unsupervised Rule (heuristic scale)
# Base probability 0.005, max 0.05
pred_unsup_test = 0.005 + (X_test.sum(axis=1) / 4.0) * 0.045

def print_metrics(name, y_true, y_prob):
    print(f"--- {name} ---")
    print(f"Log Loss: {log_loss(y_true, y_prob):.4f}")
    print(f"Brier Score: {brier_score_loss(y_true, y_prob):.4f}")
    try:
        print(f"AUC: {roc_auc_score(y_true, y_prob):.4f}")
    except:
        print("AUC: N/A")
    print(f"Mean Pred: {y_prob.mean():.4f} (True: {y_true.mean():.4f})\n")

print_metrics("Simple Constant (non-learning baseline)", y_test, pred_simple_test)
print_metrics("Integrated Model (previous)", y_test, pred_int_test)
print_metrics("Unsupervised Distance", y_test, pred_unsup_test)
print_metrics("Offline Trained Population (ML)", y_test, pred_ml_test)

