# Phase P4 Replication & Own-Parent Ablations Independent Admission Review

**Review Date:** 2026-10-13  
**Reviewer:** `r7_live_critic`  
**Developers:** `research7_coordinator`, `candidate_developer`  
**Scope:** `P4_replication`  
**Target Design Digest:** `468f86089623306effad44aa1ab14f8fac4c2dce9a17b3fb1c3bde8b85e6e5c1`  
**Status:** `approved`

---

## 1. Scope and Preconditions

1. **Cell Count:** 4,608 distinct cells (96 seeds 740001–740096 $\times$ 6 families $\times$ 8 policies: `G`, `N`, `R`, `P`, `K`, `Q6`, `Q1`, `A1`) $\le$ 6,912 ceiling.
2. **Freshness:** Certified fresh in `research7/audits/program_freshness_audit.json` under disjoint range [740001, 740096] with 0 historical collisions across Research 1–6.
3. **Execution Topology:** Single coordinator on `mac-01` managing **6 concurrent simulation workers** under `CONCURRENCY_AMENDMENT.md` and `P4_SCOPE.md` amendment.
4. **Execution Mode:** Uniform `subprocess_json` execution across all 8 arms, with process pipes directed to APFS workspace `.tmp` to avoid system disk swap. Startup verification is cached in `RegisteredRunner`.
5. **Calibrated Resource Caps:** Max 120.0 CPU-hours (covering 4,608 physical attempts $\times$ 90s reservation ledger; actual expected ~19.8 CPU-hours) and max 55.0 GiB output (expected ~50.6 GiB). APFS volume has ~206 GiB free ($\ge 30$ GiB reserve floor).
6. **Role:** Full mechanism replication and own-parent ablations under pre-registered decision gates (`PLAN.md` Section 7).

---

## 2. Evidence Basis

- **Screening Closure:** Phase P3 completed with all 2,592 cells committed (11.19 CPU-hours, 28.51 GiB output). Candidates `Q1` ($\Delta = +0.0503$, $t = +1.79$) and `A1` ($\Delta = +0.0538$, $t = +1.82$) met screening thresholds vs `G` and advanced as the two permitted mechanism families. Candidate `H1` failed screening gates ($\Delta = +0.0156$, delayed family degradation $-0.1042$) and was dropped.
- **Resource Calibration:** 6 simulation workers consume ~450–500 MB RSS, safely within physical memory on the 16 GiB host (<3% RAM). Swap usage is minimized (<250 MB).
- **Startup Latency Optimization:** `RegisteredRunner.check_execution_blockers` caches readiness validation, reducing pre-flight verification from ~19 minutes to <1 second.
- **Test Baseline:** Full 7b test suite (62 tests) passes cleanly in 1.5s; 7a independent test suite (52 tests) passes cleanly.
- **Isolation Gates:** Gates 4A (correctness & observation isolation), 4B (V2 journal streaming codec & recovery), 4C (subprocess isolation & memory limits), and 4D (seed freshness) are all independently verified and closed.

---

## 3. Replication Decision Gates

Per `PLAN.md` Section 7 and `P4_SCOPE.md`:
1. **Primary Metric:** Qualified MSMI per 100 arrived members by day 59 (`msmi_per_100_arrived_members`).
2. **Eligibility Criteria:**
   - Paired mean difference $\Delta \ge +0.025$ MSMI per 100 arrived members vs `G`.
   - Paired difference $> 0$ vs designated own-parent baseline (`Q1` vs `Q6`/`G`; `A1` vs `P`/`G`).
   - At least 3 of 6 family point differences nonnegative ($\Delta_f \ge 0$).
   - No family point difference $< -0.10$.
   - Coverage decline $\le 0.02$.
   - Zero invalid episodes.
3. **Promotion Cap:** At most 3 contenders advance to Phase P5 selection.
4. **No Manufactured Winners:** Strict adherence to registered thresholds. If no candidate qualifies, declare a valid null outcome cleanly.

---

## 4. Admission Decision

**APPROVED** for execution on `mac-01` with 6 workers into `results/research7/research7_20261012/7b/P4_replication`.
