# Research7 Requirement-to-Evidence Matrix and Execution Readiness

**Date:** 2026-10-12  
**Coordinator:** Research7 Program Coordinator  
**Workspace Authority:**
- **Authoritative Execution Workspace:** `research7b/workspace` (owns coordinator runtime, cell leases, registration, experiment execution, candidate policies, and durable outputs).
- **Independent Verification Workspace:** `research7a/workspace` (owns independent exact-model oracle, independent metrics, adversarial merge validation, independent statistics, and archive verification).
- **Rule:** No blind merging of source trees or package overlays between 7a and 7b.

---

## 1. Requirement-to-Evidence Matrix

| Requirement | Evidence Path & Hash | Tested Scope | Remaining Gap | Owner | Independent Reviewer |
|---|---|---|---|---|---|
| **Completed Reference P1 Smoke** | `research7b/workspace/results/research7/research7_20261012/7b/P1_smoke/progress.json`<br>`SHA-256: 257ccce29547afd5215a1b005a61a47569c4a41d15ad543a8b3db36e1f783949`<br>`smoke_completed_integrity.json`<br>`SHA-256: 9a9a87377c16e6411435927f96ae47d1aa2484ba23fa4faa136d5835a6b9d662` | 144 reference-only cells, 4 seeds (700001–700004), 6 families, 6 unchanged reference policies (G, N, R, P, K, Q6). 0 invalid commits, 0 fallbacks. | Reference baseline calibration only; does not evaluate or admit candidate policies (Q1, A1, H1, D1, etc.). | Coordinator / Runtime Developer | `r7_live_critic` (`smoke_admission.json`) |
| **17,280 Wire Invocations** | `research7b/workspace/reviews/smoke_completed_integrity.json`<br>`SHA-256: 9a9a87377c16e6411435927f96ae47d1aa2484ba23fa4faa136d5835a6b9d662` | 144 cells × 120 calls/cell = 17,280 calls. 0 invalid commits, 0 fallbacks, max concurrency 2. | In-process execution mode only (`trusted_inprocess`). Does not test candidate subprocess isolation or memory limits. | Runtime Developer | `r7_live_critic` |
| **Finite Reduced-Model Oracle** | `research7a/workspace/research7/exact_independent/evidence/transition_20261012/review_receipt.json`<br>`SHA-256: ad4c5432ca1e7f1a0d0ced4c706ba6ce0a28cf6d58aa1cf384bfaf53980d5530`<br>`test_exact_transitions.py` | Standalone history-tree DP and vertex enumeration for declared reduced cases (T02–T10, T31). 7 tests pass in 12.4s. | Finite declared reduced model only; not deployed candidate controllers (D1/D2/L2), not full official simulator protocol or soft-ask dominance mapping. | 7a Independent Exact Developer | Theory Specialist / `r7_live_critic` |
| **Lossless Storage Prototype** | `research7/reviews/codec_probe.md`<br>`SHA-256: 1ad0b5346b2a9441fd4bc99ecf497871beff5c4e9ea11e04bfa6318f501b8c11` | Standalone COPY/literal delta codec on 12 existing smoke cells (1,440 calls, policy G). 93.592% byte reduction on request + segment files. | Offline prototype only; not integrated into live runtime `DurableRecorder`; lacks durable pre-call persistence, live crash recovery, torn tail handling, fsync failure handling. | 7b Recorder Developer | Independent Runtime Reviewer / Critic |
| **Adversarial Merge & Lease Verification** | `research7a/workspace/research7/merge_independent.py`<br>`research7a/workspace/research7/test_merge_adversarial.py` | Synthetic failure injection: transport duplicate, conflicting action digest, invalid commit, stale lease, incomplete cluster, corrupted wire. 7 tests pass. | Tested on synthetic mock bundles; live end-to-end multi-shard bundle validation and final archive restoration checks remain to be run with real stage outputs. | 7a Independent Merger | Production Critic |
| **Governing Simulator Integrity** | `kit.py`<br>`SHA-256: 0d2cb3d3b46ca2a6ee7c8b74b78c55642ef98686e59a890ec18f66f2cabc1f3e`<br>`evaluate.py`<br>`SHA-256: d09cc14bf634a741515ad9965469821cac336a0d037b4da265eb1bf5fe20e162` | Frozen governing simulator files verified against registration `P1_smoke.frozen.json`. | Must be continuously enforced across all future phase registrations. | Coordinator | Critic |
| **Public Wire Isolation & Interfaces** | `research7b/workspace/research7/runtime/interfaces.py`<br>`test_runtime_interfaces.py` | Sanitization of evaluator requests, strict JSON serialization, ask batch legality (12 budget, 3 hard, 1 soft), match batch legality (dyads, overlap, availability, eligibility), 1 MiB memory cap. | Comprehensive TEST_SPEC edge fixture suite (T11–T16: decline domination, age reciprocity, conflicting who_to_meet, schedule/children contradictions, feedback maturity, day-59 terminal reward). | Runtime Developer | Critic |
| **Candidate Execution & Subprocess Mode** | `research7b/workspace/research7/runtime/invocation.py`<br>`runner.py` | `TrustedInvocation` (reference policies only) and basic `SubprocessInvocation`. | Restricted candidate container / subprocess mode with strict 10s invocation limit, memory cap, cold startup, serialization, dense graph stress, and deterministic fallback (T18). | 7b Production Engineer | Production Reviewer |
| **Seed Freshness & Provenance** | `research7b/workspace/research7/audits/smoke_freshness_v2.json`<br>`registry/audit_seeds.py` | Scanned repo for P1 smoke seeds (700001–700004); verified 0 collisions with prior round 1–6 seeds. | Audit and certify freshness for all proposed future seeds (P2: 720001+, P2a: 710001+, P3: 730001+, P4: 740001+, P5: 750001+, P6: 760001+). | Registry Developer | Independent Auditor / Critic |
| **Candidate Portfolio Development** | `STRATEGIES.md`<br>`research7b/workspace/research7/policies/` | Reference panel (G, N, R, P, K, Q6) implemented in `references.py`. | Candidate implementations missing: Q1 (collision-aware hard queries), A1 (unrestricted general-graph matching), H1 (released history model), D1 (joint continuation). | Policy Developers | Independent Implementation Reviewers / Critic |

---

## 2. Resource & Budget Status

- **Mac Host Observed:** Apple M4 Mac mini, 16 GiB RAM, ~241 GiB free disk on APFS volume.
- **Current Limits:**
  - Simulation/test CPU ceiling: 160 CPU-hours
  - Fitting CPU ceiling: 24 CPU-hours (max 12 fits)
  - Output cap: 100 GiB new output
  - Free reserve floor: 30 GiB minimum free reserve
  - Working RSS cap: 10 GiB combined
  - Simulation workers: default 2 (max 3 only after calibration)
  - Agent slots: max 4 globally (coordinator + up to 3 child agents)
- **Completed P1 Smoke Consumption:**
  - Recorded CPU seconds: 861.57s (~0.24 CPU-hours)
  - Recorded Output bytes: 1.72 GB
  - Working RSS observed: ~73.5 MB peak
  - Completed distinct cells: 144 / 384 P1 cell cap.

---

## 3. Next Actionable Roadmap to Close Admission Gates

1. **Gate 4A (Correctness & Isolation):** Implement and verify comprehensive TEST_SPEC test fixtures (T11–T16, T05, T10, T31).
2. **Gate 4B (Integrated Lossless Recording & Recovery):** Integrate the delta-compression engine into `recorder.py` as `DurableRecorderV2`, persist request identity before inference, implement crash recovery, torn tail handling, fsync failure handling, and archive restoration.
3. **Gate 4C (Production Execution):** Complete candidate subprocess execution path with strict timeout/memory enforcement, cold startup, and deterministic fallback.
4. **Gate 4D (Freshness & Provenance):** Audit seed freshness across the entire repo and archives for planned future stages.
5. **Stage 5 (Candidate Development & Admission):**
   - Implement `Q1` (collision-aware legal query acquisition).
   - Implement `A1` (static whole-matching general-graph allocation).
   - Audit `H1` opportunity on public data; implement if count gate passes.
   - Implement `D1` continuation controller and verify against T03/T05/T07/T31.
