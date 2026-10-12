# Stage B adversarial critique

Author: independent adversarial critic (`pro`, high); date: 2026-10-11.
Subject: Review of Stage B screen results and promotion claims.

## 1. Challenge to N3's apparent gain
While N3 cleared the +0.025 point estimate threshold (+0.03333 MSMI/100), this result is exploratory and statistically indistinguishable from noise:
- The standard error is 0.0441, larger than the point estimate itself.
- The 95% paired confidence interval [-0.0559, +0.1226] comfortably spans zero.
- The two-sided p-value is 0.4546, and the Holm-adjusted p-value across the 5 candidates tested against G is 1.0000.
- The one-sided 90% lower bound is **-0.02420**, which is negative.
- The observed gain could readily arise from favorable deadline uniforms or keyed random stream divergence for the handful of extra pairs introduced, rather than systematic superiority in query coordination.

## 2. Examination of other candidates
- **K (Maximum cardinality matching)**: Achieved +0.01875 (SE 0.0347, p=0.5924). Failed the +0.025 threshold. Pure cardinality matching does not reliably translate to higher qualified MSMI because lower-quality dyads take up busy capacity without reaching mutual intention.
- **N1 (Local alternating path repair)**: Achieved +0.00625 (SE 0.0153, p=0.6857). Minimal difference from G. Lengthening alternating paths rarely finds augmenting opportunities that mature to qualified dates.
- **P (Frozen population control)**: Achieved +0.00208 (SE 0.0367, p=0.9551). Re-confirms the round-five null result; population score weighting provides no reproducible edge over greedy.
- **N2 (Stable reranking)**: Achieved -0.02917 (SE 0.0281, p=0.3053). Negative point effect; arbitrarily freezing priorities within 8-day blocks introduces priority distortions that harm matching throughput.

## 3. Conditions for Stage C advancement
If N3 is promoted as the sole eligible candidate under the exploratory screening rule:
1. It must face fresh, independent seeds (Stage C: 60 clusters, 120001–120060).
2. It must be benchmarked against:
   - `G` (reference greedy baseline)
   - `P` (frozen population control)
   - Pre-declared contribution controls:
     - `N3_two`: 2-query optimization filled with FIFO actors to isolate 4-bundle jointness.
     - `N3_fifo4`: matched batch size FIFO (always asking 4 bundles in FIFO order) to separate bundle count from query selection.
3. Promotion to Stage D must require positive point effect replication on C AND positive own-parent effect against its contribution controls.
4. If N3 fails to replicate positive effects on Stage C, the program must terminate cleanly with greedy retained.
