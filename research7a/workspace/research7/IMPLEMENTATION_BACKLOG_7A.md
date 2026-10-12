# Research 7a Implementation Backlog and Interface Audit

**Branch**: `7a` (Host: `small-01`)  
**Status**: Setup and P0/P1 Implementation Delivered (Static Verification Only; No Empirical Workload)  
**Date**: 12 October 2026  
**Director**: 7a Machine Director  

---

## 1. Analysis of Absent Modules and Interfaces

Prior to this setup/implementation delivery, the `research7/` tree was strictly a **planning specification** package without an executable runtime or implementation modules:

| Required Module / Interface | Initial State | Current State on Branch 7a | Owning Host |
|---|---|---|---|
| `research7.exact_independent` | Completely absent | **Implemented** (`schema.py`, `solver.py`, `specifications.py`) | 7a exclusive |
| `research7.metrics_independent` | Completely absent | **Implemented** (`metrics_independent.py`) | 7a exclusive |
| `research7.merge_independent` | Completely absent | **Implemented** (`merge_independent.py` + failure injection suite) | 7a exclusive |
| `research7/reviews/7a_inventory.md` | Absent | **Delivered** (WO00 evidence audit) | 7a exclusive |
| `work_orders_7a_dispatched.json` | Unresolved placeholders | **Delivered** (Concrete input hashes, named reviewers, model routing) | 7a exclusive |
| Future results path `results/research7/<program>/7a/` | Absent | **Initialized** (`results/research7/pending/7a/`) | 7a exclusive |
| `research7.runtime` (Runner, Recorder, Leases) | Absent specification | **Unimplemented** (Blocks execution) | 7b exclusive |
| Shared Experiment Registry (`registry/`) | Absent specification | **Unimplemented** (Blocks execution) | Coordinator (7b) |
| Candidate Policies (`Q1`, `H1`, `A1`, `A2`, `D1`, `D2`, etc.) | Absent specifications | **Unimplemented** (Phase P2/P3) | Distributed (7a/7b) |
| Global Seed Freshness Certification | Uncertified | **Uncertified** (Awaiting external archive audit) | Coordinator only |

---

## 2. Concrete Bounded Implementation Deliverables on 7a

### A. Independent Reduced-Model Exact Solver (`research7/exact_independent/`)
- **Schema (`schema.py`)**: Data contracts for `ReducedActor`, `ReducedEdge`, `ReducedState`, `ReducedAction`, and `ReducedBranch`.
- **Solver (`solver.py`)**:
  - Vertex-recursive matching enumeration for arbitrary graphs.
  - Verification of 64 labelled 4-vertex simple graphs and odd cycles 3, 5, 7 (confirming triangle matching cardinality = 1, not fractional 1.5).
  - Rational history-tree dynamic programming via backward induction with observable history merging (nonanticipation).
  - Hard state enumeration cap enforced ($\le 100,000$ states/case).
  - Scheduled future rewards booked exactly once.
- **Specifications (`specifications.py`)**: Concrete specifications and math ledgers for:
  - **T02**: Static 4-node trap (optimum 1.30 vs greedy 0.95; triangle cardinality 1).
  - **T03**: Downstream delay reversal (fast AB 21/25 vs wait 20/25; slow AB 13/25 vs wait 20/25).
  - **T04**: Exact query tree future-preparing information threshold ($p > 1/4$).
  - **T05**: Dyad exhaustion (3 actors: 271/1000; 2 actors: 0.1).
  - **T06**: Hard query complement and shared neighbor ($24/25$ vs $7/5$; degree sum $8/5$).
  - **T07**: Continuation non-additivity (joint current $1.0 > 0.9$ future; additive penalties double-count).
  - **T08**: Static price invariance for matchings covering identical endpoint sets.
  - **T09**: Public posterior response update (two-type rational $3/8$ vs H1 Beta surrogate $1/3$).
  - **T10**: Terminal day 59 with full follow-up (duration has zero opportunity cost).
  - **T31**: Pending reward one-time booking (action advantage $q$, never $q + r$).

### B. Independent Metric Reconstruction (`research7/metrics_independent.py`)
- Independent event processor reading public introduction and feedback events.
- Strict evaluation of the 30-day date qualification window and 3-day second-meeting intention window.
- Explicitly isolates and tracks unqualified late-positive pauses (where mutual interest was indicated but outside the SLA, triggering simulator pauses without earning MSMI reward).
- Full accounting of coverage, wait times, declines, and arrived-member denominator (200 members).
- Built-in verification against synthetic boundary fixtures.

### C. Independent Safe Merger and Failure Suite (`research7/merge_independent.py`)
- Adheres strictly to `MERGE_PROTOCOL.md`.
- Verifies canonical cell key identities:
  $$\text{hash}(program\_id, stage\_id, seed, family, policy\_id, config\_hash, source\_tree\_hash, inference\_assets\_hash)$$
- Validates bundle structure, shard leases, and path safety (rejecting directory traversal `..`, absolute paths, and symlink escapes).
- Deduplicates identical transport bundles to 1 authoritative cell with logged provenance.
- Detects scientific conflicts and fails closed (quarantines conflicting cells; refuses to output primary analysis).
- Preserves committed invalidities as permanent disqualifications.
- Includes synthetic failure injection test suite verifying all 7 protocol rejection modes.

---

## 3. Dispatched Work Orders Summary (`work_orders_7a_dispatched.json`)

| WO ID | Phase | Role Profile | Deliverable | Live Reviewer | Status |
|---|---|---|---|---|---|
| **WO00** | P0 | `evidence_medium` (`gpt-6-luna` / `flash`) | `research7/reviews/7a_inventory.md` | `independent_critic_7a` (`gpt-6.1-sol`/high / `pro`) | Complete |
| **WO02** | P1 | `implementation_medium` (`gpt-6.1-sol` / `flash`) | `exact_independent/` + `metrics_independent.py` | `theory_reviewer_7a` (`gpt-6.1-sol`/high / `pro`) | Complete |
| **WO04** | P1 | `implementation_medium` (`gpt-6.1-sol` / `flash`) | `merge_independent.py` + Failure Suite | `production_critic_7a` (`gpt-6.1-sol`/high / `pro`) | Complete |
| **WO06** | P2a | `implementation_medium` | Light policy modules (`Q1`, `H1`) | Unassigned | Blocked (later phase) |
| **WO11** | P5–P7 | `science_high` | Independent statistical reconstruction | Unassigned | Blocked (later phase) |
| **WO13** | P7 | `evidence_medium` | Final archive inventory | Unassigned | Blocked (later phase) |

---

## 4. Unexecuted Tests and Workload Prohibition

In strict compliance with the director mandate, **zero experimental workloads, simulator episodes, model fitting, or phase tests have been executed or claimed as passed**.

The following tests remain **unexecuted and pending future execution authorization**:
1. **Empirical Phase Episodes**:
   - P1 Smoke: 384 episodes across 4 clusters.
   - P2 Training / Validation: 4,608 episodes.
   - P2a Light Pilot: 360 episodes across 12 clusters.
   - P3 Screen: 4,608 episodes across 48 clusters.
   - P4 Replication & Ablation: 6,912 episodes across 96 clusters.
   - P5 Independent Selection: 6,912 episodes across 128 clusters.
   - P6 Confirmation: Up to 75,600 episodes across $n \le 1,800$ clusters.
2. **Phase Integration & Security Tests**:
   - T01: Full package closure test on remote/archive sync.
   - T11–T16: Live container isolation, protocol compliance, and memory leakage profiling.
   - T17–T20: Runtime crash recovery, segment fsync chunking, and process retry loops.
   - T22: Live multi-agent provider dispatch.
   - T23: Exhaustive repository and external machine seed freshness audit.
   - T25: Cross-machine numerical parity between Mac and Linux hosts.
   - T28–T30: Supervised feature training, student model distillation, and stage count feasibility gates.

---

## 5. Runtime Blockers and Prerequisites for Execution

Before any future phase execution can be authorized:
1. **Coordinator Execution Registration**: A frozen `registration.json` with status `frozen_execution_registration` must be authored by the 7b coordinator.
2. **Seed Freshness Certification**: The coordinator alone must audit all historical rounds (R1–R6), external declarations, and raw archives to certify unused fresh seed blocks.
3. **Runner Implementation on 7b**: Host 7b must deliver `research7/runtime/runner.py`, `recorder.py`, and lease management.
4. **Environment Parity**: Validate wheel compatibility and numerical determinism between Linux x86_64 (`small-01`) and macOS arm64 (`mac-01`).
5. **Explicit Execution Authorization**: The user must issue an explicit instruction authorizing empirical execution.
