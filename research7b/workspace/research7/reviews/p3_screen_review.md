# Phase P3 Mechanism Screening Independent Admission Review

**Review Date:** 2026-10-12  
**Reviewer:** `r7_live_critic`  
**Developers:** `research7_coordinator`, `candidate_developer`  
**Scope:** `P3_screen`  
**Target Design Digest:** `c8cf3190c4e22294ac99159bcec9c680cf6d3007c06448f6060cd8b8ce81da69`  
**Status:** `approved`

---

## 1. Scope and Preconditions

1. **Cell Count:** 2,592 distinct cells (48 seeds 730001–730048 × 6 families × 9 policies: `G`, `N`, `R`, `P`, `K`, `Q6`, `Q1`, `A1`, `H1`) ≤ 4,608 ceiling.
2. **Freshness:** Certified fresh in `research7/audits/program_freshness_audit.json` under disjoint range [730001, 730048] with 0 historical collisions across Research 1–6.
3. **Execution Topology:** Single coordinator on `mac-01` managing at most 2 concurrent simulation workers under `P3_SCOPE.md` amendment.
4. **Execution Mode:** Uniform `subprocess_json` execution across all 9 arms.
5. **Calibrated Resource Caps:** Max 65 CPU-hours (covering 2,592 physical attempts × 90s reservation ledger; actual expected ~11.8 CPU-hours) and max 35 GiB output (expected ~32.4 GiB). APFS volume has ~235 GiB free (≥ 30 GiB reserve floor).
6. **Role:** Full mechanism screening under pre-registered decision gates (`PLAN.md` Section 7).

---

## 2. Evidence Basis

- **Prior Empirical Closure:**
  - Reference smoke `P1_smoke`: 144 cells committed with 0 invalid cells, 0 fallbacks.
  - Candidate smoke v2 `P1_candidates_v2`: 72 cells committed with 0 invalid cells (`Q1`: 27, `G`: 26, `Q6`: 26, `P`: 24, `R`: 22, `K`: 21, `H1`: 20, `N`: 18, `A1`: 16 MSMI).
  - Diagnostic light pilot `P2a_pilot`: 288 cells committed with 0 invalid cells, 0 fallbacks (`H1`: 70, `G`: 66, `A1`: 56, `Q1`: 49 MSMI; `Q1` achieved highest mutual acceptances at 849).
- **Test Baseline:** Full 7b test suite (62 tests in `research7b/workspace/research7/tests`) passes cleanly in 1.46s; 7a independent test suite (14 tests in `research7a/workspace/research7`) passes cleanly.
- **Isolation Gates:** Gates 4A (correctness & observation isolation), 4B (V2 journal streaming codec & recovery), 4C (subprocess isolation & memory limits), and 4D (seed freshness) are all independently verified and closed.

---

## 3. Screening Decision Gates

Per `PLAN.md` Section 7 and `P3_SCOPE.md`:
1. **Primary Metric:** Qualified MSMI per 100 arrived members by day 59 (`msmi_per_100_arrived_members`).
2. **Eligibility Criteria vs `G`:**
   - Paired mean difference $\Delta \ge +0.025$ MSMI per 100 arrived members.
   - At least 3 of 6 family point differences nonnegative ($\Delta_f \ge 0$).
   - No family point difference $< -0.10$.
   - Coverage decline $\le 0.02$.
   - Zero invalid episodes.
3. **Promotion Cap:** At most 2 distinct mechanism families advance to Phase P4 replication/ablations.
4. **No Manufactured Winners:** Strict adherence to registered thresholds. If no candidate qualifies, declare a valid null outcome cleanly.

---

## 4. Admission Decision

**APPROVED** for execution on `mac-01` with max 2 workers into `results/research7/research7_20261012/7b/P3_screen`.
