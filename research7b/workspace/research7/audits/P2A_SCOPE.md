# P2a Diagnostic Light Pilot Scope & Mac Shard Amendment

**Date:** 2026-10-12  
**Scope:** `P2a_pilot`  
**Execution Authority:** Research 7 Program Coordinator under user autonomous execution authorization.

---

## 1. Single Machine Shard Amendment

Per `METHODOLOGY.md` Section 1 and `guide_review.md`, the Research 7 execution operates under Mac-only scheduling on `mac-01`:
1. **Topology:** Single coordinator on `mac-01` managing at most 2 concurrent simulation workers.
2. **Budgets:** Charged to the program ledgers (160 simulation/test CPU-hours, 100 GiB new output cap, free reserve floor ≥ 30 GiB, combined working RSS ≤ 10 GiB).
3. **Calibrated Pilot Caps:** Max 8 CPU-hours and max 6 GiB output (accommodating 288 physical attempts × 90s reservation).
4. **Workspace Isolation:** Executed from `research7b/workspace` into designated output directory `results/research7/research7_20261012/7b/P2a_pilot`. The independent 7a role and workspace remain preserved without source mixing.

---

## 2. Experimental Grid and Arms

1. **Seeds:** 12 fresh clusters: 710001 through 710012 (certified fresh in `research7/audits/program_freshness_audit.json`).
2. **Families:** All 6 governing families (`development`, `sparse`, `cold_start`, `delayed`, `shift`, `drift`).
3. **Admitted Policy Panel (4 arms ≤ 5 arm cap):**
   - `G`: Shipped greedy baseline anchor (`references.py:decide`, `subprocess_json`).
   - `Q1`: Collision-aware deterministic query acquisition (`q1.py:decide`, `subprocess_json`).
   - `A1`: Unrestricted general-graph maximum weight matching (`a1.py:decide`, `subprocess_json`).
   - `H1`: Released-history actor Beta shrinkage scorer (`h1.py:decide`, `subprocess_json`).
4. **Episode Count:** 12 seeds × 6 families × 4 policies = 288 distinct cells (≤ 360 ceiling).

---

## 3. Scientific Invariants and Gates

1. **Diagnostic Development Role:** `P2a_pilot` provides development evidence only. No confirmatory claims, no promotion, and no inferential selection are permitted from this stage.
2. **Untouched Confirmation Independence:** P2a seeds (710001–710012) are completely disjoint from P6 confirmation seeds (760001–761800) and screening seeds (730001–730048).
3. **Preservation:** All physical attempts, resource usage, and logs are preserved durably.
