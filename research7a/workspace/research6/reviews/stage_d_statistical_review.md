# Stage D statistical review and confirmation sizing

Author: independent statistician (`pro`, high); date: 2026-10-11.
Subject: Statistical audit of Stage D independent selection and exact noncentral-t sample sizing for Stage E confirmation.

## 1. Audit of Stage D execution integrity
- **Grid completeness**: All 1,920 registered cells executed to completion (100.0% completion rate).
- **Validity**: 1,920 valid episodes, 0 invalid episodes, 0 fallbacks triggered across all policies.
- **Independence**: 80 distinct seed clusters (130001–130080), certified fresh in `seed_inventory_closure.json`. All 6 families per cluster were clustered properly.

## 2. Statistical results summary (df = 79)

| Policy | Mean Diff vs G | Paired SD | SE | 95% CI | Two-sided p | Holm p | 90% 1-Sided Lower |
|---|---|---|---|---|---|---|---|
| **N3_two** | **+0.040625** | 0.267494 | 0.029907 | [-0.01890, +0.10015] | 0.1782 | 0.5346 | **+0.001975** |
| **N3** | **+0.040625** | 0.273667 | 0.030597 | [-0.02028, +0.10153] | 0.1881 | 0.5346 | **+0.001083** |
| **P** | **+0.035417** | 0.239320 | 0.026757 | [-0.01784, +0.08867] | 0.1894 | 0.5346 | **+0.000837** |

## 3. Evaluation of selection criteria
- Both `N3_two` and `N3` meet the eligibility gates:
  1. Mean difference vs G $\ge +0.025$: Both +0.040625 $\ge +0.025$.
  2. One-sided 90% lower bound $> 0$: Both $> 0$.
- Winner selection:
  - `N3_two` has the higher lower bound (+0.001975 vs +0.001083).
  - Difference between lower bounds is $0.000892 < 0.005$ (`D_tie_band`).
  - By registered rule, the tie goes to the lower-complexity tier (`N3_two` Tier 2 over `N3` Tier 3).
  - Selection: **`N3_two`** is selected as the sole contender.

## 4. Stage E confirmation sample sizing calculation
According to the registered confirmation protocol in `plan.json`:
1. **Paired standard deviation estimate**:
   - $\text{sd\_floor} = 0.26$
   - Inflation factor $= 1.10$
   - Observed paired SD in D for `N3_two`: $0.267494$
   - $\sigma = \max(0.26, 1.10 \times 0.267494) = 0.294243$.
2. **Test parameters**:
   - Primary metric: Seed-cluster mean of equal-six-family qualified MSMI/100 differences against G.
   - Design effect: $\delta = +0.05$.
   - Significance level: Two-sided $\alpha = 0.01$ (99% CI).
   - Target power: $1 - \beta = 0.90$.
3. **Exact noncentral-t calculation**:
   - Critical value $t_{\text{crit}} = t_{m-1, 0.995}$.
   - Noncentrality parameter $\text{ncp} = \frac{\delta \sqrt{m}}{\sigma} = \frac{0.05 \sqrt{m}}{0.294243}$.
   - Solving $P(T_{m-1}(\text{ncp}) \ge t_{\text{crit}}) = 0.90$ yields exact minimum clusters: **$m = 519$**.
4. **Sample inflation factor**:
   - $1.10\times$ multiplier applied: $n = \lceil 1.10 \times 519 \rceil = \mathbf{571}$ clusters.
   - Capped at maximum 900 clusters: $571 \le 900$.
   - Seeds: **140001 through 140571** (571 clusters).
   - Total episodes: $571 \times 6 \times 2 = \mathbf{6,852}$ episodes.

Verdict: **SIGN-OFF**. Contender `N3_two` approved for Stage E frozen confirmation at $n = 571$ clusters.
