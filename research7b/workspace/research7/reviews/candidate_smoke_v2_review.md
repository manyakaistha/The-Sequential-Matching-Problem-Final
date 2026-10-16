# Candidate P1 Smoke v2 Independent Admission Review

**Review Date:** 2026-10-12  
**Reviewer:** `r7_live_critic`  
**Developers:** `research7_coordinator`, `candidate_developer`  
**Scope:** `P1_smoke`  
**Target Design Digest:** `90ca7dcbf8998fef735f6ddf658b6c048337748890a98bfb8f25914f6bddcb1e`  
**Status:** `approved`

---

## 1. Scope and Invariants

This review evaluates the admission of the candidate portfolio integration smoke v2:
1. **Physical Attempt Accounting:**
   - 144 reference cells (P1_smoke) + 72 candidate v1 cells (P1_candidates) + 72 candidate v2 cells (P1_candidates_v2) = 288 physical cells ≤ 384 P1 ceiling.
   - All physical attempts, CPU seconds, output bytes, and metrics from prior executions are preserved without modification.
2. **Q1 Fix Verification:**
   - Q1 query eligibility logic was verified to recognize kit.py's `'not_asked'` and `None` field statuses.
   - Tested on full 60-day episode: Q1 now properly requests 4 hard bundles and spends budget (174 ask cost), producing 87 assignments and 3 MSMI.
3. **Execution Isolation:**
   - Designated output directory: `results/research7/research7_20261012/7b/P1_candidates_v2`.
   - Subprocess JSON isolation enforced with process group kill, 10s timeout, and 1 MiB wire bounds.

---

## 2. Admission Decision

**APPROVED** for execution under single coordinator on `mac-01` with max 2 workers.
