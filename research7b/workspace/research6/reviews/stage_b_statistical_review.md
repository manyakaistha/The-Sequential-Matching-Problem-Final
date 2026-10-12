# Stage B statistical review

Author: independent statistician (`pro`, high); date: 2026-10-11.
Subject: Statistical audit of Stage B screen data, inferences, and promotion decisions.

## 1. Audit of execution integrity
- **Grid completeness**: All 1,440 registered cells executed to completion (100.0% completion rate).
- **Validity**: 1,440 valid episodes, 0 invalid episodes, 0 fallbacks triggered across all policies.
- **Independence**: 40 distinct seed clusters (110001–110040), certified fresh in `seed_inventory_closure.json`. Six scenario families per seed cluster were clustered properly using mean-over-families before paired t calculation.

## 2. Statistical results summary (df = 39)

| Policy | Mean Diff vs G | Paired SD | SE | 95% CI | Two-sided p | Holm p | Bootstrap 95% CI |
|---|---|---|---|---|---|---|---|
| **N3** | **+0.03333** | 0.2791 | 0.0441 | [-0.0559, +0.1226] | 0.4546 | 1.0000 | [-0.0500, +0.1250] |
| **K** | **+0.01875** | 0.2197 | 0.0347 | [-0.0515, +0.0890] | 0.5924 | 1.0000 | [-0.0500, +0.0875] |
| **N1** | **+0.00625** | 0.0969 | 0.0153 | [-0.0248, +0.0373] | 0.6857 | 1.0000 | [-0.0250, +0.0375] |
| **P** | **+0.00208** | 0.2323 | 0.0367 | [-0.0722, +0.0764] | 0.9551 | 1.0000 | [-0.0688, +0.0771] |
| **N2** | **-0.02917** | 0.1776 | 0.0281 | [-0.0860, +0.0276] | 0.3053 | 1.0000 | [-0.0833, +0.0271] |

## 3. Methodological conclusions
1. **Gate compliance**: Only N3 clears the pre-declared screening threshold of mean effect >= +0.025. K, N1, P, and N2 fail to reach this threshold and must be dropped from promotion.
2. **Exploratory status**: Stage B was an exploratory screen across 40 seeds. The Holm p-values confirm that no candidate achieves formal statistical significance at alpha=0.05 after multiplicity correction. This is expected given the planned sample size (n=40 has power < 25% for true effect +0.03).
3. **Stage C requirements**: Stage C must use 60 fresh clusters (n=60, df=59) and test N3 alongside mandatory contribution controls to rule out batch-size and sample-budget confounds.
4. **Approval**: Statistical sign-off granted for promoting N3 to Stage C under the exploratory screening rules.
