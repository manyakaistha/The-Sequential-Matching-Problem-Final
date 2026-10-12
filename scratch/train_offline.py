import json
import numpy as np
import math
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, brier_score_loss, roc_auc_score
import os

with open('scratch/outcomes.json', 'r') as f:
    data = json.load(f)

# Feature matrix:
# eq has 4 elements
X = []
y_term = []
y_acc = []
for d in data:
    X.append(d['eq'])
    y_term.append(1 if d['y_terminal'] else 0)
    y_acc.append(1 if d['y_mutual_accept'] else 0)

X = np.array(X)
y_term = np.array(y_term)
y_acc = np.array(y_acc)

model_acc = LogisticRegression()
model_acc.fit(X, y_acc)
prob_acc = model_acc.predict_proba(X)[:, 1]

model_term = LogisticRegression()
model_term.fit(X, y_term)
prob_term = model_term.predict_proba(X)[:, 1]

print("--- Data stats ---")
print(f"Total samples: {len(X)}")
print(f"Accept rate: {y_acc.mean():.4f}")
print(f"Terminal rate: {y_term.mean():.4f}")

print("\n--- Accept ML Model (Logistic Regression) ---")
print(f"Log Loss: {log_loss(y_acc, prob_acc):.4f}")
print(f"Brier Score: {brier_score_loss(y_acc, prob_acc):.4f}")
print(f"AUC: {roc_auc_score(y_acc, prob_acc):.4f}")
print("Coefficients:", model_acc.coef_[0], "Intercept:", model_acc.intercept_[0])

print("\n--- Terminal ML Model (Logistic Regression) ---")
print(f"Log Loss: {log_loss(y_term, prob_term):.4f}")
print(f"Brier Score: {brier_score_loss(y_term, prob_term):.4f}")
print(f"AUC: {roc_auc_score(y_term, prob_term):.4f}")
print("Coefficients:", model_term.coef_[0], "Intercept:", model_term.intercept_[0])

y_pred_integrated_accept = np.array([d['pred_integrated']['both_accept_unconditional'] for d in data])
y_pred_integrated_term = np.array([d['pred_integrated']['terminal'] for d in data])

print("\n--- Baseline Integrated Model - Accept ---")
print(f"Log Loss: {log_loss(y_acc, y_pred_integrated_accept):.4f}")
print(f"Brier Score: {brier_score_loss(y_acc, y_pred_integrated_accept):.4f}")
print(f"AUC: {roc_auc_score(y_acc, y_pred_integrated_accept):.4f}")

print("\n--- Baseline Integrated Model - Terminal ---")
print(f"Log Loss: {log_loss(y_term, y_pred_integrated_term):.4f}")
print(f"Brier Score: {brier_score_loss(y_term, y_pred_integrated_term):.4f}")
print(f"AUC: {roc_auc_score(y_term, y_pred_integrated_term):.4f}")

