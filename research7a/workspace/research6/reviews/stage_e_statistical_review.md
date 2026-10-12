# Stage E statistical review

Author: independent statistician (`pro`, high); date: 2026-10-11.
Subject: Final statistical audit of Stage E confirmatory execution and primary hypothesis test.

## 1. Audit of execution integrity
- **Grid completeness**: All 6,852 registered cells executed to completion (100.0% completion rate).
- **Validity**: 6,852 valid episodes, 0 invalid episodes, 0 fallbacks triggered.
- **Independence**: 571 distinct seed clusters (140001–140571), certified fresh in `seed_inventory_closure.json` with zero prior usage. All 6 families per cluster were clustered properly.

## 2. Statistical results summary (df = 570)

| Metric | Value |
|---|---|
| **Sample Clusters ($n$)** | 571 |
| **Total Episodes** | 6,852 |
| **Mean Paired Difference ($\bar{d}$)** | **+0.003211** MSMI/100 |
| **Paired Standard Deviation ($s_d$)** | **0.256047** |
| **Standard Error ($SE$)** | **0.010715** |
| **t-statistic** | 0.2996 |
| **Two-sided p-value** | **0.764559** |
| **Primary 99% CI ($\alpha = 0.01$)** | **[-0.024483, +0.030904]** |
| **Nominal 95% CI ($\alpha = 0.05$)** | **[-0.017835, +0.024257]** |
| **Bootstrap Sensitivity (99% percentile CI, 10k reps)** | **[-0.023351, +0.031232]** |
| **Standardized Effect Size (Cohen's $d$)** | +0.0125 |

## 3. Scenario family decomposition

| Scenario Family | Mean Difference vs G (MSMI/100) |
|---|---|
| `development` | +0.012259 |
| `sparse` | -0.002627 |
| `cold_start` | **+0.034151** |
| `delayed` | **-0.034151** |
| `shift` | +0.005254 |
| `drift` | +0.004378 |

## 4. Confirmatory verdict
- The pre-registered primary hypothesis test required that the lower bound of the primary two-sided 99% confidence interval be strictly positive ($CI_{99\%} \text{ lower} > 0$).
- The observed 99% confidence interval is $[-0.024483, +0.030904]$, which contains zero and whose lower bound is negative.
- **Conclusion**: Confirmatory superiority over greedy (`G`) is **NOT established**. The null hypothesis cannot be rejected. Shipped greedy baseline `G` is retained.
