# Independent Review: Research 7 Runtime Scaffolding (WO03)

- **Work Order ID:** WO03
- **Phase:** P1
- **Host:** 7b
- **Reviewer:** `independent_runtime_reviewer` (Sol / medium independent implementation reviewer)
- **Developer:** `runtime_developer_7b`
- **Date:** 12 October 2026
- **Status:** Approved
- **Evidence Class:** `observed_artifact` (unit tests and static analysis)

## 1. Scope of Implementation

The runtime developer implemented the following bounded modules under `research7/runtime/`:
1. `runner.py`: `RegisteredRunner` interface with strict preflight blocker checks.
2. `recorder.py`: `DurableRecorder` and `AttemptLogger` with compressed segment chunking, segment index, and atomic commit protocol.
3. `leases.py`: `LeaseManager` and `CellLease` with generation tracking, revocation, and late duplicate quarantine.
4. `interfaces.py`: `sanitize_observation`, `validate_ask_batch`, `validate_match_batch`, and `validate_policy_memory`.
5. `metrics.py`: Confirmatory MSMI calculation and stage diagnostic counters.
6. `transfer.py`: Archive security validator and manifest generator.

## 2. Verification of Test Ledger Assertions

1. **Lossless Wire Round-Trip (T17):**
   - Verified by `test_attempt_logging_and_wire_roundtrip_t17`:
     Compressed segment binaries decompress to byte-identical wire request/response, memory before/after, action, and fallback statuses.
     The segment index accurately indexes every chunk with SHA-256 and byte counts.

2. **Crash Resilience and Non-Erasure of Failures (T20):**
   - Verified by `test_durable_commit_and_no_overwrite_t20`:
     Commits are created via atomic rename (`.tmp` to final).
     Attempting to overwrite an existing cell commit raises `FileExistsError`.
     Unfinished attempts remain intact in `attempts/<cell_hash>/<attempt_id>/` without corrupting prior commits.

3. **Cell Lease Authority and Duplicate Quarantine (T26):**
   - Verified by `test_commit_and_duplicate_quarantine_t26`:
     Re-committing an already committed cell or committing under a revoked lease generation is automatically quarantined in `quarantined_duplicates`. No overwriting or mean-averaging occurs.

4. **Archive Security and Path Traversal Rejection (T21):**
   - Verified by `test_unsafe_path_traversal_rejected_t21` and `test_unsafe_absolute_path_rejected_t21`:
     Archives with `..` or absolute paths are rejected before decompression.

5. **Action Legality (T11):**
   - Verified by `test_validate_ask_batch_t11_fixtures` and `test_validate_match_batch_t11_fixtures`:
     Budget overruns (> 12), duplicate asks, unavailable users, member overlaps, self-matches, and past dyad repeats are strictly caught and rejected.

6. **Execution Blocker Enforcement:**
   - `RegisteredRunner` verifies that registration status must be `frozen_execution_registration`, seed freshness certified, and execution authorized. Calling it under planning status raises `RunnerBlockerError`.

## 3. Verdict

The P0/P1 runtime and registry scaffolding meets all architectural specifications.
No simulator worlds, benchmark episodes, or provider calls were launched.
Ready for inclusion in the 7b coordinator implementation handoff.
