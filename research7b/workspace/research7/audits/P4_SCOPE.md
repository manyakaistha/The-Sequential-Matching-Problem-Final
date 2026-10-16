# Phase P4 Replication & Own-Parent Ablations Scope Amendment

**Date:** 2026-10-13  
**Scope:** `P4_replication`  
**Execution Authority:** Research 7 Program Coordinator under user autonomous execution authorization.

---

## 1. Execution Topology and Resource Caps

Per `METHODOLOGY.md` Section 1, `CONCURRENCY_AMENDMENT.md`, and user instructions:
1. **Topology:** Single coordinator on `mac-01` managing **6 concurrent simulation workers** (`--workers 6`).
2. **Budgets:** Charged to the program ledgers (160 simulation/test CPU-hours, 100 GiB new output cap, free reserve floor ≥ 30 GiB, combined working RSS ≤ 10 GiB).
3. **Calibrated Phase Caps:**
   - `max_cpu_hours`: 120.0 CPU-hours (accommodating 4,608 physical attempts $\times$ 90s reservation ledger; actual expected ~19.8 CPU-hours).
   - `max_output_gib`: 55.0 GiB (expected ~50.6 GiB).
   - Volume free reserve: APFS volume has ~206 GiB free (far above the 30 GiB minimum reserve floor).
4. **Workspace Isolation:** Executed from `research7b/workspace` into designated output directory `results/research7/research7_20261012/7b/P4_replication`. Subprocess execution pipes use workspace `.tmp` on APFS to prevent system disk swap. Startup verification is cached in `RegisteredRunner`.

---

## 2. Experimental Grid and Arms

1. **Seeds:** 96 fresh clusters: 740001 through 740096 (certified fresh in `research7/audits/program_freshness_audit.json`).
2. **Families:** All 6 governing families (`development`, `sparse`, `cold_start`, `delayed`, `shift`, `drift`).
3. **Policy Panel (8 arms ≤ 12 arm cap):**
   - **Reference Panel (6 arms):**
     - `G`: Shipped greedy baseline anchor (`references.py:decide`).
     - `N`: No-asks baseline (`references.py:decide`).
     - `R`: Random soft-ask baseline (`references.py:decide`).
     - `P`: Population scorer greedy baseline (`references.py:decide`).
     - `K`: Cardinality-first matching baseline (`references.py:decide`).
     - `Q6`: Round 6 query acquisition baseline (`references.py:decide`).
   - **Promoted Candidates from Phase P3 (2 arms):**
     - `Q1`: Collision-aware deterministic query acquisition (`q1.py:decide`).
     - `A1`: Unrestricted general-graph maximum weight matching (`a1.py:decide`).
4. **Total Grid:** 96 seeds $\times$ 6 families $\times$ 8 policies = **4,608 distinct cells** (≤ 6,912 ceiling).

---

## 3. Replication Decision Gates

Per `PLAN.md` Section 7:
1. **Primary Metric:** Qualified MSMI per 100 arrived members by day 59 (`msmi_per_100_arrived_members`).
2. **Eligibility Criteria:**
   - Paired mean difference $\Delta \ge +0.025$ MSMI per 100 arrived members vs `G`.
   - Paired difference $> 0$ vs designated own-parent baseline (`Q1` vs `Q6`/`G`; `A1` vs `P`/`G`).
   - At least 3 of 6 family point differences nonnegative ($\Delta_f \ge 0$).
   - No family point difference $< -0.10$.
   - Coverage decline $\le 0.02$.
   - Zero invalid episodes.
3. **Promotion Cap:** At most 3 contenders advance to Phase P5 selection.
4. **No Manufactured Winners:** If no candidate meets the eligibility threshold, declare the scoped null outcome cleanly and stop.
