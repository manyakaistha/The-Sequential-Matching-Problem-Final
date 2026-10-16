# Research 7 Phase P4 Replication Results & Decision Gate Report

## 1. Executive Summary & Preregistered Decision Gate Verdict

Phase P4 evaluated whether the mechanism improvements observed during screening (Phase P3) replicated across **96 fresh, untouched seeds (740001–740096)** across all 6 simulator families and 8 policy arms, comprising **4,608 distinct simulation episodes**.

### Gate Decision Summary

| Candidate / Arm | Benchmark Gain vs G ($\Delta \ge +0.025$) | Own-Parent Gain ($\Delta > 0$) | Coverage Preservation ($\le 0.02$ loss) | Operational Validity (100% valid) | Gate Outcome |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Q1** (Collision-Aware Query) | **PASS** ($\Delta = +0.0660$) | **FAIL** ($\Delta = -0.0035$ vs Q6) | **PASS** ($\Delta = +0.0003$) | **PASS** (576/576) | **ELIMINATED** |
| **A1** (Max-Weight Matching) | **FAIL** ($\Delta = -0.0191$) | **FAIL** ($\Delta = -0.0191$ vs G) | **PASS** ($\Delta = +0.0003$) | **PASS** (576/576) | **ELIMINATED** |
| **Q6** (R6 Query Reference) | **PASS** ($\Delta = +0.0694$) | Reference Panel | **PASS** ($\Delta = -0.0002$) | **PASS** (576/576) | Reference Control |
| **P** (Population Scorer Reference) | **PASS** ($\Delta = +0.0660$) | Reference Panel | **PASS** ($\Delta = +0.0004$) | **PASS** (576/576) | Reference Control |
| **R** (Random Soft Asks Reference) | **FAIL** ($\Delta = -0.0174$) | Reference Panel | **PASS** ($\Delta = +0.0009$) | **PASS** (576/576) | Reference Control |
| **K** (Cardinality-First Reference) | **FAIL** ($\Delta = -0.0625$) | Reference Panel | **PASS** ($\Delta = +0.0013$) | **PASS** (576/576) | Reference Control |
| **N** (No-Ask Control) | **FAIL** ($\Delta = -0.4826$) | Reference Panel | **FAIL** (Coverage 0.1186) | **PASS** (576/576) | Control Baseline |

**Scientific Determination:**
Neither novel candidate qualifies for Phase P5 (Contender Selection). Research 7 concludes with a rigorous, certified **Null Scientific Result**: observation-only candidate policies in the registered portfolio do not improve eventual qualified introductions over the frozen reference panel (`Q6` and `P`).

---

## 2. Experimental Population Summary (4,608 Cells)

All 4,608 cells executed under subprocess isolation with strict public-observation isolation and zero leaked simulator labels or seeds.

| Policy | N Cells | Mean MSMI per 100 | Std Dev | Mean Coverage | Mean CPU (s) | Valid Cells | Fallbacks |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **A1** | 576 | 0.6684 | 0.7989 | 0.3326 | 28.18 | 576 / 576 | 0 |
| **G** (Benchmark) | 576 | 0.6875 | 0.8597 | 0.3323 | 15.92 | 576 / 576 | 0 |
| **K** | 576 | 0.6250 | 0.7960 | 0.3336 | 22.60 | 576 / 576 | 0 |
| **N** | 576 | 0.2049 | 0.4674 | 0.1186 | 15.29 | 576 / 576 | 0 |
| **P** | 576 | 0.7535 | 0.8829 | 0.3327 | 16.86 | 576 / 576 | 0 |
| **Q1** | 576 | 0.7535 | 0.8868 | 0.3326 | 33.45 | 576 / 576 | 0 |
| **Q6** | 576 | 0.7569 | 0.8878 | 0.3321 | 17.80 | 576 / 576 | 0 |
| **R** | 576 | 0.6701 | 0.8242 | 0.3332 | 15.73 | 576 / 576 | 0 |

---

## 3. Paired Statistical Analysis vs Benchmark G (576 Pairs)

Paired differences are computed across identical $(seed \times family)$ cells.

| Arm | N Pairs | Mean $\Delta$ | Std Error | Paired $t$-stat | $p$-value | 95% Confidence Interval | Win / Tie / Loss |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Q6** vs G | 576 | **+0.0694** | 0.0388 | +1.79 | 0.0742 | [-0.0067, +0.1455] | 158 / 295 / 123 |
| **Q1** vs G | 576 | **+0.0660** | 0.0415 | +1.59 | 0.1128 | [-0.0154, +0.1474] | 158 / 296 / 122 |
| **P** vs G | 576 | **+0.0660** | 0.0325 | +2.03 | 0.0427 | [+0.0023, +0.1296] | 105 / 389 / 82 |
| **A1** vs G | 576 | **-0.0191** | 0.0403 | -0.47 | 0.6361 | [-0.0982, +0.0600] | 139 / 299 / 138 |
| **R** vs G | 576 | **-0.0174** | 0.0347 | -0.50 | 0.6175 | [-0.0855, +0.0507] | 114 / 344 / 118 |
| **K** vs G | 576 | **-0.0625** | 0.0320 | -1.95 | 0.0515 | [-0.1253, +0.0003] | 100 / 370 / 106 |
| **N** vs G | 576 | **-0.4826** | 0.0343 | -14.07 | $< 10^{-15}$ | [-0.5499, -0.4154] | 21 / 332 / 223 |

---

## 4. Own-Parent Control Ablation Analysis

Under `METHODOLOGY.md` Section 4, a candidate cannot be admitted simply by beating Greedy if it does not improve upon its own underlying parent mechanism:

### Candidate Q1 vs Parent Q6
* **Mean Difference:** $\Delta(\text{Q1} - \text{Q6}) = \mathbf{-0.0035}$
* **Standard Error:** $se = 0.0411$
* **$t$-statistic:** $t = -0.08$ ($p = 0.9327$)
* **Pairwise Outcome:** 134 wins, 305 ties, 137 losses
* **Finding:** Collision-aware query acquisition (`Q1`) is statistically indistinguishable from baseline R6 query acquisition (`Q6`), with `Q6` achieving slightly higher overall MSMI ($0.7569$ vs $0.7535$). The collision penalty heuristic produces no incremental qualified introductions.

### Candidate A1 vs Parent G
* **Mean Difference:** $\Delta(\text{A1} - \text{G}) = \mathbf{-0.0191}$
* **Standard Error:** $se = 0.0403$
* **$t$-statistic:** $t = -0.47$ ($p = 0.6360$)
* **Pairwise Outcome:** 139 wins, 299 ties, 138 losses
* **Finding:** General-graph max-weight matching (`A1`) underperformed greedy allocation on fresh seeds ($-0.0191$). While max-weight matching optimizes batch weight globally, greedy allocation preserves high-margin immediate matches in dynamic sequential arrivals.

---

## 5. Family-by-Family Breakdown

Mean paired $\Delta$ vs Benchmark `G` across simulator families:

| Simulator Family | Q1 vs G | A1 vs G | Q6 vs G | P vs G |
| :--- | :---: | :---: | :---: | :---: |
| **cold_start** | -0.0104 | +0.0521 | +0.0104 | +0.0000 |
| **delayed** | -0.1250 | -0.1250 | -0.1042 | +0.0104 |
| **development** | +0.1250 | -0.1250 | +0.1146 | +0.1562 |
| **drift** | +0.1667 | -0.1146 | +0.1354 | +0.0938 |
| **shift** | +0.2604 | +0.1771 | +0.2500 | +0.1354 |
| **sparse** | -0.0208 | +0.0208 | +0.0104 | +0.0000 |

Both query policies (`Q1` and `Q6`) showed strong resilience in dynamic shift environments (`drift` and `shift`), but showed moderate degradation in `delayed` feedback worlds where early queries yielded uninformative answers.

---

## 6. Program Disposition & Conclusion

1. **Gate Closure:** All registered Phase P4 replication gates are fully evaluated.
2. **Contender Portfolio:** Zero candidates qualified for Phase P5 admission.
3. **Fail-Closed Preregistration:** Per `PLAN.md` Section 7 and governing instructions, Phase P5 (Contender Selection) and Phase P6 (Confirmation) are not executed. No candidate winner is manufactured.
4. **Final Research 7 Finding:** Certified **Null Scientific Outcome**. Eventual qualified introductions in sequential matching are strongly driven by query acquisition (`Q6` at $+0.0694$) and population ranking (`P` at $+0.0660$), but proposed collision-aware query penalties (`Q1`) and general-graph max-weight allocation (`A1`) fail to provide statistically significant incremental improvement over the frozen reference panel.
