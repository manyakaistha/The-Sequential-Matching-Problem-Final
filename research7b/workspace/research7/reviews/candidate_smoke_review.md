# Candidate P1 Smoke Independent Admission Review

**Review Date:** 2026-10-12  
**Reviewer:** `r7_live_critic`  
**Developers:** `research7_coordinator`, `candidate_developer`  
**Scope:** `P1_smoke`  
**Target Design Digest:** `ebb2b731012c5afd7a19279a6b05ed14777cc8558692ebfbfe62f2cd758096b8`  
**Status:** `approved`

---

## 1. Scope and Invariants

This review evaluates the admission of the candidate portfolio integration smoke under the governing Research 7 phase constraints:
1. **Cell Count:** 72 cells (4 seeds 700001–700004 × 6 families × 3 candidate policies: `Q1`, `A1`, `H1`).
   - Combined with the 144 reference cells already completed, total P1 smoke cells = 216 ≤ 384 ceiling.
2. **Execution Mode:** `subprocess_json` with strict 10s timeout, memory guards, and isolated process group execution.
3. **Policies Under Smoke:**
   - `Q1`: Collision-aware deterministic query acquisition over 8-actor shortlist.
   - `A1`: Unrestricted general-graph maximum weight matching with quantized weights.
   - `H1`: Released-history actor Beta shrinkage scorer with episode-local resets.
4. **Isolation:** Separate output directory (`research7b/workspace/results/research7/research7_20261012/7b/P1_candidates`) preserves reference evidence intact.
5. **Non-inferential Character:** Results are strictly for integration, subprocess reliability, fallback verification, and resource calibration. No promotional or confirmatory claims may be drawn.

---

## 2. Verified Evidence

- **Unit Test Suites:**
  - `research7/tests/test_portfolio_candidates.py`: 8/8 tests pass (Q1 T06/T11, A1 T02 4-node 1.30 vs 0.95, triangle matching, cardinality vs weight, H1 T09 Beta shrinkage 1/3, dedup, wire execution).
  - `research7/tests/test_spec_fixtures.py`: 6/6 tests pass (T11 legality, T12 feedback maturity, T13 memory bounds, T14 ordering, T15 isolation, T10 terminal reward retention, T31 pending non-double-counting, T05 dyad reuse).
  - `research7/tests/test_production_execution.py`: 5/5 tests pass (cold startup, serialization, dense 200-node graphs, timeout orphan cleanup, deterministic fallback).
  - `research7/tests/test_lossless_recorder_recovery.py`: 9/9 tests pass (exact reconstruction, corruption, torn tails, kill/restart, fsync failure, partial responses, lease conflicts, commits, archive restoration).
  - `research7a/workspace/research7/test_exact_transitions.py`: 14/14 tests pass.

- **Seed Freshness:** Audited 4 seeds (700001–700004) verified fresh and disjoint from historical rounds in `research7/audits/smoke_freshness_v2.json`.

---

## 3. Admission Decision

**APPROVED** for execution under single coordinator on `mac-01` with max 2 workers.
