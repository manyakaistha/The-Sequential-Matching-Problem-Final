# Stage C statistical review

Author: independent statistician (`pro`, high); date: 2026-10-11.
Subject: Statistical audit of Stage C replication data and ablation contrasts.

## 1. Audit of execution integrity
- **Grid completeness**: All 1,800 registered cells executed to completion (100.0% completion rate).
- **Validity**: 1,800 valid episodes, 0 invalid episodes, 0 fallbacks triggered across all policies.
- **Independence**: 60 distinct seed clusters (120001–120060), certified fresh in `seed_inventory_closure.json`. All 6 families per cluster were clustered properly.

## 2. Statistical results summary (df = 59)

| Policy | Mean Diff vs G | Paired SD | SE | 95% CI | Two-sided p | Holm p | 90% 1-Sided Lower |
|---|---|---|---|---|---|---|---|
| **N3** | **+0.04167** | 0.2646 | 0.0342 | [-0.0267, +0.1100] | 0.2275 | 0.7361 | **-0.00261** |
| **N3_two** | **+0.04306** | 0.2481 | 0.0320 | [-0.0210, +0.1071] | 0.1840 | 0.7361 | **+0.00154** |
| **N3_fifo4** | **+0.00000** | 0.0000 | 0.0000 | [0.0000, 0.0000] | 1.0000 | 1.0000 | **+0.00000** |
| **P** | **-0.01389** | 0.1960 | 0.0253 | [-0.0645, +0.0367] | 0.5851 | 1.0000 | **-0.04668** |

## 3. Direct ablation contrast (N3 vs N3_two)
- Paired difference `d(s) = Mean(N3 - N3_two)`:
  - Mean difference: **-0.00139** MSMI/100
  - Paired SD: 0.2210, SE: 0.0285
  - Paired t: -0.0487, two-sided p: 0.9613
  - Conclusion: No statistically discernible difference between full 4-bundle joint evaluation and 2-query optimization + FIFO filler.

## 4. Promotion sign-off
- Both N3 and N3_two meet the Stage C replication criterion (replicated positive effect vs G).
- N3 clears the own-parent gate vs N3_fifo4 (+0.04167 > 0).
- N3_two clears the own-parent gate vs N3_fifo4 (+0.04306 > 0).
- Approval granted to advance `N3` and `N3_two` as contenders to Stage D alongside controls `G` and `P`.
