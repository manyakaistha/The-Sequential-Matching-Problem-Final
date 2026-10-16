# P2a Diagnostic Light Pilot Independent Admission Review

**Review Date:** 2026-10-12  
**Reviewer:** `r7_live_critic`  
**Developers:** `research7_coordinator`, `candidate_developer`  
**Scope:** `P2a_pilot`  
**Target Design Digest:** `5435c8730230a8d1b30175ddd813622a4e2dc0066112b0f6d4b37e5f80b53575`  
**Status:** `approved`

---

## 1. Scope and Preconditions

1. **Cell Count:** 288 cells (12 seeds 710001–710012 × 6 families × 4 policies: `G`, `Q1`, `A1`, `H1`) ≤ 360 ceiling.
2. **Freshness:** Certified fresh in `program_freshness_audit.json` under disjoint range [710001, 710012].
3. **Execution Topology:** Mac-only scheduling on `mac-01` with max 2 workers under `P2A_SCOPE.md` amendment.
4. **Execution Mode:** Uniform `subprocess_json` execution across all 4 policies.
5. **Calibrated Caps:** Max 8 CPU-hours and max 6 GiB output (covering all 288 physical attempts × 90s reservation).
6. **Role:** Diagnostic light pilot, development evidence only.

---

## 2. Evidence Basis

- **Clean Reconciled State:** 160 cells committed with 0 invalid cells, 0 fallbacks, 0 interrupted attempts.
- **Resource Calibration:** 160 cells consumed 2,588.85 CPU-seconds (~0.72 CPU-hours). The 8 CPU-hour ceiling accommodates the full 288 reservation ledger (25,920s = 7.2h).
- **Test Baseline:** 62 tests passing in `research7b/workspace/research7/tests`; 14 tests passing in `research7a/workspace/research7`.
- **Resource Reserve:** APFS workspace disk free > 240 GiB (≥ 30 GiB floor); combined RSS < 10 GiB.

---

## 3. Admission Decision

**APPROVED** for completion execution under single coordinator on `mac-01` with max 2 workers into `results/research7/research7_20261012/7b/P2a_pilot`.
