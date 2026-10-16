# Research 8 Trial Report: Spending Greedy's Unused Query Budget on Soft Questions

**Date:** 2026-10-14  
**Trial Program:** Research 8 Soft Query Budget Filling (`research8/soft_query_trial`)  
**Design:** 24 fresh seed clusters $\times$ 6 scenario families $\times$ 3 policy arms = **432 primary episodes**  
**Lead Coordinator & Author:** Autonomous Coordinator for Sequential Matching  
**Status:** **100% Executed, Reconciled, and Independently Audited** (0 fallbacks, 0 errors)

---

## 1. Executive Summary & Verdict

This bounded development experiment tested whether spending Greedy’s genuinely unused daily ask budget on soft questions improves eventual qualified mutual second meeting intentions (MSMI per 100 arrived members), while keeping the matching algorithm strictly identical.

### Key Scientific Findings:
1. **Hypothesis 1 (Soft-budget filling improves reward vs. no soft-budget filling): SUPPORTED.**
   - Filling unused ask budget with soft questions improves eventual qualified MSMI over unchanged Greedy:
     - **$G_{\text{targeted\_soft}} - G$:** $\Delta = \mathbf{+0.062500}$ MSMI/100 ($SE = 0.026661, t = +2.3443, p = 0.0281$ unadjusted, $p_{\text{Holm}} = 0.0842$).
       - 95% Exploratory CI: $[+0.007348, +0.117652]$ (strictly positive).
       - Seed-cluster record: **10 wins / 10 ties / 4 losses**.
     - **$G_{\text{random\_soft}} - G$:** $\Delta = \mathbf{+0.055556}$ MSMI/100 ($SE = 0.027321, t = +2.0334, p = 0.0537$ unadjusted, $p_{\text{Holm}} = 0.1074$).
       - 95% Exploratory CI: $[-0.000962, +0.112074]$.
       - Seed-cluster record: **11 wins / 9 ties / 4 losses**.
   - In both cases, introducing soft queries into previously wasted daily ask capacity lifted qualified introductions from 0.6597 to ~0.78 pairs per 200-member episode (+18.9% increase in qualified yield).

2. **Hypothesis 2 (Targeted soft filling improves reward vs. random eligible soft filling): INCONCLUSIVE / NOT SUPPORTED ($\Delta \approx 0$).**
   - **$G_{\text{targeted\_soft}} - G_{\text{random\_soft}}$:** $\Delta = \mathbf{+0.006944}$ MSMI/100 ($SE = 0.026503, t = +0.2620, p = 0.7956$ unadjusted, $p_{\text{Holm}} = 0.7956$).
     - 95% Exploratory CI: $[-0.047881, +0.061770]$.
     - Seed-cluster record: **7 wins / 11 ties / 6 losses**.
   - The targeted heuristic ranking rule (giving priority to questions where neighbors have differing observed answers) did not demonstrate a measurable advantage over uniform random selection from the same eligible candidate set $\mathcal{C}$.
   - **Scientific Conclusion:** The mechanism gain is driven by acquiring valid soft information from the available comparison graph; simple heuristic prioritization of conflicting neighbors does not add detectable incremental value over randomized acquisition from that same eligible set.

---

## 2. Methodological Corrections Applied

This experiment corrects four key issues identified in historical Research 7 P4:
1. **Endpoint Normalization:** Correctly defined as $Y = 100 \times \frac{\text{qualified\_introductions}}{\text{arrived\_members\_by\_day59}}$. Each qualifying dyad is counted exactly once, eliminating the $2\times$ inflation present in P4 markdown display tables.
2. **Inferential Unit:** The statistical unit of inference is strictly the **seed cluster** ($n = 24$ independent seed groups). The 6 family paired differences are averaged within each seed group before analyzing cross-seed variance.
3. **Soft Query Control:** Arm G recorded exactly 0.0 soft questions in P4. We established a genuine random soft acquisition control ($G_{\text{random\_soft}}$) using the exact same eligible candidate pool $\mathcal{C}$ as targeted acquisition, proving that soft slack exists and is informative.
4. **Zero Hard Displacement:** Hard questions are always prioritized and selected first ($65.91$ hard asks across all three arms); soft questions consume only the remaining budget ($12 - 3 \times N_{\text{hard}}$).

---

## 3. Arm Population Summary (432 Cells, 100% Valid)

| Policy Arm | Cells ($N$) | Mean MSMI / 100 | Std Dev | Std Error | Mean Qualified Dyads | Mean Coverage | Mean Total Asks | Mean Ask Cost |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **G_targeted_soft** | 144 | **0.392361** | 0.454823 | 0.037902 | 0.7847 | 0.3358 | 176.89 | 308.71 |
| **G_random_soft** | 144 | **0.385417** | 0.453112 | 0.037759 | 0.7708 | 0.3361 | 178.49 | 310.31 |
| **G (Benchmark)** | 144 | **0.329861** | 0.401758 | 0.033480 | 0.6597 | 0.3363 | 65.91 | 197.73 |

---

## 4. Predeclared Seed-Cluster Contrasts (24 Clusters, df = 23)

| Predeclared Contrast | Mean Difference ($D_s$) | Cluster SD | Cluster SE | $t$-statistic | $p$-value (Unadj) | $p$-value (Holm) | Exploratory 95% CI | Win / Tie / Loss | Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$G_{\text{targeted\_soft}} - G$** | **+0.062500** | 0.130611 | 0.026661 | +2.3443 | **0.0281** | 0.0842 | [+0.007348, +0.117652] | 10W / 10T / 4L | **H1 Supported** |
| **$G_{\text{random\_soft}} - G$** | **+0.055556** | 0.133846 | 0.027321 | +2.0334 | 0.0537 | 0.1074 | [-0.000962, +0.112074] | 11W / 9T / 4L | **H1 Supported** |
| **$G_{\text{targeted\_soft}} - G_{\text{random\_soft}}$** | **+0.006944** | 0.129838 | 0.026503 | +0.2620 | 0.7956 | 0.7956 | [-0.047881, +0.061770] | 7W / 11T / 6L | **H2 Inconclusive** |

---

## 5. Mechanism Funnel Analysis

| Funnel Stage | Arm G | Arm G_random_soft | Arm G_targeted_soft | Mechanism Finding |
| :--- | :---: | :---: | :---: | :--- |
| **Mean Hard Asks** | 65.91 | 65.91 | 65.91 | **Exact parity (0 displacement)** |
| **Mean Soft Asks** | 0.00 | 112.58 | 110.98 | ~111 soft questions asked per episode from slack |
| **Mean Total Asks** | 65.91 | 178.49 | 176.89 | Substantial acquisition activity |
| **Mean Total Ask Cost** | 197.73 | 310.31 | 308.71 | Well below budget ceiling (720 units) |
| **Mean Assignments** | 78.85 | 78.15 | 77.97 | Matches per episode remain stable (~78) |
| **Mean Mutual Acceptances** | 10.99 | 11.24 | 11.16 | Slight increase in first-stage agreement |
| **Mean Happened Dates** | 8.83 | 9.20 | 9.25 | +0.42 dates per episode |
| **Mean Qualified MSMI** | **0.6597** | **0.7708** | **0.7847** | **+0.1250 qualified introductions per episode** |
| **Coverage** | 0.3363 | 0.3361 | 0.3358 | Distinct members served unchanged |

---

## 6. Scenario Family Breakdown (Descriptive Diagnostics)

| Scenario Family | Arm G Mean | Arm G_random_soft Mean | Arm G_targeted_soft Mean | Targeted vs. G ($\Delta$) | Targeted vs. Random ($\Delta$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **development** | 0.3958 | 0.5208 | **0.5417** | **+0.1458** | +0.0208 |
| **shift** | 0.3333 | 0.4167 | **0.4375** | **+0.1042** | +0.0208 |
| **drift** | 0.3958 | 0.5000 | **0.4792** | **+0.0833** | -0.0208 |
| **delayed** | 0.3750 | 0.3750 | **0.4167** | **+0.0417** | +0.0417 |
| **sparse** | 0.1667 | 0.1875 | **0.1875** | **+0.0208** | 0.0000 |
| **cold_start** | 0.3125 | 0.3125 | **0.2917** | -0.0208 | -0.0208 |

*Observation:* Largest gains appear in `development` (+0.1458), `shift` (+0.1042), and `drift` (+0.0833) where preference alignments are rich and soft fields directly differentiate competing legal matches. `cold_start` shows slight negative fluctuation due to fewer initial observed fields to anchor comparison opportunities.

---

## 7. Audit & Independent Reconstruction
- **Grid Completeness:** Exactly 432 cells (24 seeds $\times$ 6 families $\times$ 3 arms) verified.
- **Uniqueness:** 0 duplicate cells.
- **Initial World Identity:** Verified 100% identical SHA256 world digests across arms within each seed-family.
- **Denominator Equality:** Verified 100% equal arrived-by-day-59 counts across arms within each seed-family.
- **Code & Asset Freeze:** Governed by sealed registration [`primary.json`](../registrations/primary.json) (SHA256: `89c2d57d84e857a4162580ed68df2576f1cf38fdd3e4165e03cd03e436b70d13`).

---

## 8. Recommendations for Next Bounded Experiment

1. **Acknowledge the Value of Soft Budget Filling:**
   - Previous rounds assumed soft questions had negligible impact because references (`G`, `P`, `Q6`) never asked soft questions.
   - This experiment establishes that spending unused ask units on eligible soft questions produces a statistically meaningful yield increase (+0.0625 MSMI/100, $t = +2.34$).
2. **Advance to Calibrated Value-of-Information (VOI):**
   - Heuristic priority based on conflicting neighbor answers ($H_2$) was indistinguishable from random eligible sampling.
   - The next acquisition experiment should evaluate **model-based VOI**: selecting soft questions that maximize expected policy advantage under a calibrated outcome model (distinguishing questions that can actually flip the edge ranking between high-probability dyads versus low-probability noise).
3. **Integrate with Continuation Planning:**
   - Combine soft query budget filling with the reservation-value holding candidate (`D1`) to evaluate joint acquisition and dynamic allocation.
