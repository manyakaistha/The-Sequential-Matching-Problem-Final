# P3 Full Mechanism Screening Scope & Execution Amendment

**Date:** 2026-10-12  
**Scope:** `P3_screen`  
**Execution Authority:** Research 7 Program Coordinator under user autonomous execution authorization.

---

## 1. Single Machine Shard Amendment

Per `METHODOLOGY.md` Section 1 and `guide_review.md`, the Research 7 execution operates under Mac-only scheduling on `mac-01`:
1. **Topology:** Single coordinator on `mac-01` managing at most 2 concurrent simulation workers.
2. **Budgets:** Charged to the program ledgers (160 simulation/test CPU-hours, 100 GiB new output cap, free reserve floor ≥ 30 GiB, combined working RSS ≤ 10 GiB).
3. **Calibrated Phase Caps:** Max 65 CPU-hours (accommodating 2,592 physical attempts × 90s reservation; actual expected ~11.5 CPU-hours) and max 35 GiB output (expected ~32.4 GiB).
4. **Workspace Isolation:** Executed from `research7b/workspace` into designated output directory `results/research7/research7_20261012/7b/P3_screen`.

---

## 2. Experimental Grid and Arms

1. **Seeds:** 48 fresh clusters: 730001 through 730048 (certified fresh in `research7/audits/program_freshness_audit.json`).
2. **Families:** All 6 governing families (`development`, `sparse`, `cold_start`, `delayed`, `shift`, `drift`).
3. **Panel (9 arms ≤ 16 arm cap):**
   - **Reference Panel (6 arms):**
     - `G`: Shipped greedy baseline anchor (`references.py:decide`).
     - `N`: No-asks baseline (`references.py:decide`).
     - `R`: Random soft-ask baseline (`references.py:decide`).
     - `P`: Population scorer greedy baseline (`references.py:decide`).
     - `K`: Cardinality-first matching baseline (`references.py:decide`).
     - `Q6`: Round 6 query acquisition baseline (`references.py:decide`).
   - **Candidate Panel (3 arms):**
     - `Q1`: Collision-aware deterministic query acquisition (`q1.py:decide`).
     - `A1`: Unrestricted general-graph maximum weight matching (`a1.py:decide`).
     - `H1`: Released-history actor Beta shrinkage scorer (`h1.py:decide`).
4. **Total Grid:** 48 seeds × 6 families × 9 policies = 2,592 distinct cells (≤ 4,608 ceiling).

---

## 3. Screening Decision Gates

Per `PLAN.md` Section 7:
1. **Primary Metric:** Qualified MSMI per 100 arrived members by day 59 (`msmi_per_100_arrived_members`).
2. **Eligibility Criteria vs `G`:**
   - Paired mean difference $\Delta \ge +0.025$ MSMI per 100 arrived members.
   - At least 3 of 6 family point differences nonnegative ($\Delta_f \ge 0$).
   - No family point difference $< -0.10$.
   - Coverage decline $\le 0.02$.
   - Zero invalid episodes.
3. **Promotion Cap:** At most 2 distinct mechanism families advance to Phase P4 replication/ablations.
4. **No Manufactured Winners:** If no candidate meets the eligibility threshold, report the scoped null outcome cleanly and stop.
