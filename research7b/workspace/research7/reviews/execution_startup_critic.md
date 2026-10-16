# Independent Research7 execution startup review

Date: 2026-10-12. Reviewer: `/root/r7_execution_critic`, Sol/high. Named integrating reviewer: root director. Evidence classes: observed_artifact and source_deduction. This review generated no simulator worlds, episodes, fits, or provider calls. Implementation ownership remains separate; this reviewer owns this report only.

## Verdict and currently admissible scope

The user has authorized Research7 execution. That closes the user-authorization prerequisite; it does not certify the existing implementation or seed reservations. The supplied code is not ready to run the official P1 smoke or later empirical phases.

The immediately admissible phase is **P0 startup repair and registration work, plus bounded synthetic P1 infrastructure/constructed checks**. This includes source/wire/schema integration, fixed baseline identification, independent metric and merge repair, constructed exact cases, process/recorder failure injection, and resource/environment inspection without world generation. Preserve all historical results. Constructed tests do not certify research reward improvement. Do not label the existing self-check flags as full T01-T31 completion.

Before the official P1 smoke: close the relevant P0/P1 correctness, leakage, exact-case, merge and registration reviews; implement the episode loop against unchanged kit/evaluate semantics; freeze the exact smoke grid/policy source/assets; resolve seed freshness with a reviewed local inventory and external declaration; enforce attempt/CPU/disk/process budgets; and measure the registered smoke workload. The full 4-cluster/6-family/at-most-16-arm smoke is a cap, not justification to invent unsupported candidate arms. Any smaller initial integration panel needs an explicit pre-data registration/amendment. No P2 training, P2a pilot, P3 screen, P4/P5 holdout, or P6 confirmation is currently admitted. Unrelated optional candidate dependencies may remain empty, but the same candidate cannot pass with incomplete dependencies.

## Evidence actually executed

`python3 -m unittest discover -s research7/tests -v` from the 7b workspace: **23 existing tests passed in 0.011 seconds**. These tests use integer IDs and invented observation/ask fixtures; they do not exercise the official wire schema, expired commits, successful executable registration, crash interruption, simultaneous commit races, actual source closure, or reconstructed feedback metrics.

Additional bounded, in-memory/synthetic counterexamples reproduced the following:

- Expired lease: `issue_lease(..., duration_seconds=-1)` yields `verify_lease_for_generation=False`, but `commit_lease=True`.
- An official-shaped public request is sanitized to an empty population and feedback history; an official `{'member_id':'a','field':'constraints'}` ask and string-ID match are rejected.
- An official-shaped introduction with string IDs yields coverage zero, and an official ask log entry yields cost zero.
- A single invalid merger commit blocks analysis; two identical copies of that invalid commit permit primary analysis.
- Empty registration plus no bundles permits primary analysis; a registered key paired with the wrong seed/family/policy also permits it.
- A ZIP entry marked as a Unix symlink with target `../../outside` passes archive safety inspection.
- The 7a arithmetic specification suite returns `all_verified=True`; source shows it does not call the history-tree DP.

All these checks completed well inside the 120 CPU-second allowance. Temporary directories were removed. The reproductions are synthetic evidence, not official episodes.

## Prioritized blocking findings

### 1. Actual observation and action protocol is incompatible with the runtime

`runtime/interfaces.py:48` expects `state.network`, integer `available_users`, `past_introductions`, and `released_feedback`. Governing `kit.py:102` emits string-ID `members`, individual `available` flags, `introductions`, `feedback`, and `ask_budget_remaining`. The sanitizer discards the official population, public hard/soft fields/status/timestamps and released outcomes. Its invented hard/soft vocabularies and pair-shaped asks conflict with official asks: dictionaries containing string `member_id` and `field`, with the bundle named `constraints` and soft fields from `kit.SOFT` (`kit.py:9`, `kit.py:119`, `evaluate.py:29`). It also allows individual hard fields that the official simulator rejects. The match validator lacks the required pair eligibility test.

Repair: preserve the exact official public request vocabulary and wire responses; validate shapes/types, current availability, complete public eligibility, dyad history, budget and memory using constructed official-shaped fixtures. An independent eligibility implementation must agree with governing eligibility on all boundary fixtures. Do not convert IDs to integers or rewrite official inputs to fit this scaffold. Public provenance must be whitelisted structurally; arbitrary nested `revealed_attributes`, logs and memory copying does not prove that every private leak is rejected.

### 2. Runtime metrics cannot reconstruct the primary endpoint

`runtime/metrics.py:6` has no feedback argument. It infers reward from invented introduction `status` substrings or `mutual_second` flags; governing introductions contain neither. It counts served IDs only when they are integers and expects ask `cost`, absent from official ask logs. Consequently actual wire histories would report zero reward, zero served members, and zero ask cost. It also does not implement the date<=30 and second-intention<=3 qualification windows, late positive pause separation, or arrived-by59 denominator identity.

Repair: derive Q from released terminal feedback tied to official introduction IDs and events, A from arrived-by59 public members, coverage from distinct served arrived IDs, and costs from official ask fields. Keep full precision and independent reconstruction. The 7a implementation is closer but needs strict event/member identity/completeness validation, use of `arrived_member_ids`, an explicit zero-denominator result, and removal of rounding at `metrics_independent.py:131-132` before the registered 1e-10 agreement check. It currently ignores its arrived-ID filter argument and does not deliver wait-time arrays.

### 3. Registration currently cannot describe the intended executable benchmark

`registry/schema.py:79` hardcodes `cold_start,sparse,dense,bipartite,delayed,heterogeneous`, instead of the registered/official `development,sparse,cold_start,delayed,shift,drift`. The strict schema rejects `execution_authorized`, while `runtime/runner.py:66` requires it. Existing tests only assert a minimal registration with empty cells is schema-valid; no complete grid/type/source/seed/policy/panel validation occurs. One arbitrary approved review is enough; its scope/hash/independence is not checked. `source_manifest` is compared only to an optional manifest, not all actual source bytes (`registry/validator.py:84`).

Repair: one canonical registration schema, official ordered families, explicit authorized scope semantics, exact nonempty cell cross-product, baseline identities and transitive source/config/assets/dependency closure, checked independent review scopes/digests, unique seed/cell/shard ownership, and immutable freeze digest. A certified boolean must reference actual freshness evidence and unresolved parser/external gaps must block launch.

### 4. Runner is deliberately non-executable

`runtime/runner.py:111` unconditionally raises after all checks pass. It has no world creation, 60 ask/refresh/match iterations, 40 follow-up days, invocation isolation/timeout/resource handling, observed-prefix invalid commit, recorder integration, or source/config/asset identity verification. Merely changing status/authorization cannot launch research. Public `evaluate.py` provides authoritative semantics, but its direct invocation must be wrapped with Research7 attempt/lease/grid/freeze/recording requirements; do not bypass those by running an unregistered CLI study.

### 5. Lease and commit durability is not yet the registered authority contract

The reproduced expired commit at `runtime/leases.py:131-179` violates T26. The process limit constant is not enforced. Quarantine evidence exists only in memory; reload discards it. `DurableRecorder.write_commit` uses exists-check then `os.replace` (`recorder.py:252-262`), so concurrent writers can both pass and the second can overwrite the authoritative invalidity. Lease commitment and recorder commitment are separate, so a crash can leave a lease committed without an authoritative result, or the inverse. Neither validates closed attempts/120 calls/horizon/digests before valid commit. File fsync without parent-directory fsync does not establish rename durability.

Repair: expiry/status/generation check at commit, durable quarantine/audit records, single coordinator process permits, exclusive publication without replacement, and an interruption-recoverable authority transaction. Kill-before-chunk/index/commit and simultaneous-writer fixtures must preserve the first valid or invalid result and all attempts. A sequential FileExistsError test is insufficient.

### 6. Recorder does not yet meet lossless failure logging or storage admission

`recorder.py:120` decodes response bytes as strict UTF-8 before logging; a malformed/non-UTF8 response can fail logging precisely when the invalid prefix must be retained. Reusing a segment sequence opens the same file with `wb` (`recorder.py:141`) and overwrites an indexed chunk. Reads do not compare the index checksum/size. There is no restart/index reconstruction or immutable finalization/commit-artifact linkage. The implementation stores full request/memory/action JSON in a separately gzipped blob each invocation and full worlds in each attempt; it implements neither content-addressed world dedup nor event/memory deltas. This cannot support the plan's storage claim without measured compression and whole-program forecast.

Repair: exact reversible arbitrary-byte wire encoding, exclusive segment identities, verified index reconstruction and append ordering, immutable closure, artifact digest linkage, and measured lossless storage strategy. Actual child/group CPU/RSS accounting is needed; RUSAGE_SELF is host lifetime peak, not peak worker RSS. Compression/resource calibration must precede P2/P3 capacity admission.

### 7. 7a merger is fail-open and incompatible with 7b outputs

`merge_independent.py:155` skips committed-invalidity checking on duplicate transport rows. Its empty `expected_cell_keys` defaults disable grid checks; this occurs when handed the 7b schema, which exposes `cells` instead. 7a hashes keys with `|` (`:35`); 7b uses `:` (`registry/schema.py:39`). 7a expects flat `cell_key`/`valid`; 7b recorder emits `cell_key_hash`/`is_valid` and nested `cell`. Fields are never recomputed from the registered identity. Lease authority is inferred from optional bundle booleans, not authoritative generation/time/host lineage. Duplicate comparison ignores source/assets/world/memory/denominator/counts/raw artifact differences. The manifest validator is never called during merge and only verifies optional inline payload keys, allowing unchecked paths/hashes/missing files.

Repair: one specified interoperable serialization and identity digest, a strict nonempty registration/grid, actual bundle source/file-set/hash/lease/log validation, exact row identity recomputation, committed-invalidity checks on every route, complete scientific conflict fields and world/denominator equality. Add duplicate-invalid, malformed-empty-registration, wrong-identity, missing-attempt, corrupted-wire/source-asset mismatch, and wrong-world fixtures. No analysis or scientific seal from current merger output.

### 8. Archive safety misses ZIP symlinks and exact restoration verification

`runtime/transfer.py` rejects TAR links but never checks ZIP external attributes; the synthetic Unix ZIP symlink passes. Literal duplicate-name checks miss normalized aliases. Manifest generation follows filesystem symlinks through `is_file`, without proving root containment. There is no actual safe restoration with exact file-set/hash validation. Reject symlinks/links and nonregular special files, normalize names consistently, enforce resource limits during restoration, restore to a new directory, and verify manifest completeness before admission.

### 9. Independent exact implementation does not fulfill dynamic-test claims

T03-T10/T31 in `exact_independent/specifications.py` calculate prewritten scalar formulas; `rational_history_tree_dp` is imported but not used. T04 has no useful competing real 12-unit budget embedding; T05 has no separate q<p pause branch; T06/T07 retain no full branch observations/actions; T31 subtracts two constants rather than testing a planner's bookkeeping. T02 genuinely enumerates small matchings, but its all-64 check only asserts cardinality<=2 rather than independently verifying all optimal values/action sets. The DP uses floating values/rounding and memoizes `(day,observation_history)` to the first hidden state's optimum, without a posterior-weighted belief over indistinguishable branches; this is not by itself a valid observable-history reduction. It does not implement transition legality, dyad/busy/pause evolution or pending reward one-time bookkeeping, which are delegated to absent case transition callbacks.

Repair: developer supplies actual reduced-state/action/branch transitions with observable-history beliefs, exact rational arithmetic or a justified error bound, reachable action sets and ties, and all specified counterfactual toggles. Independent stronger mathematical review owns any nonanticipation/DP conclusion. Existing arithmetic flags remain useful ledgers but must not count as complete T03-T10/T31 execution.

## Earlier review claims and planned repair assessment

`reviews/runtime_scaffolding_review.md` says Approved and “meets all architectural specifications.” Its cited tests only establish narrow scaffold behavior and the counterexamples above refute that broader verdict. `reviews/simulator_semantics.md` claims the sanitizer enforces all private isolation and the immediate-query/delay distinction by construction; the cited interface lacks simulator transitions and the official public schema. Preserve these documents as historical artifacts, append a superseding assessment, and do not use their approval as execution admission.

The root director has assigned itself bounded repairs to `runner.py`, `validator.py`, `leases.py`, `recorder.py`, and focused execution-gate tests. The proposed expiry/no-overwrite/gate repairs address findings 3-6, but approval requires review of the delivered diff and independent regression evidence. A safe interim runner may remain intentionally blocked until the official loop and all startup prerequisites close. Runtime interfaces/metrics/registry and the independent merge/exact modules need separate explicit ownership and independent review. No completed patch or successful workload is inferred from assignment alone.

At initial diagnosis the external seed-use declaration was pending. The updated declaration and its remaining implications are recorded below. No official world is admissible merely because the local reserved numeric intervals do not collide.

## Handoff stop condition

Review remains **blocked for empirical launch**, with synthetic startup work admitted. Re-review each repaired component using official-shaped constructed fixtures and preserve this report's counterexamples as regression cases. Root integrates closed reviewers and registration before granting a runner launch. Full phase tests, capacity/parity/container proofs and reward superiority remain unestablished.

## Final startup repair assessment (supersedes initial defect status)

The director reports that the user declared **no previous Research7 runs anywhere and all work will occur here on one Mac**. That closes the pending user external-R7-use declaration. It does not turn old-round seed reservations into a reviewed local all-round freshness certificate. Cross-host confirmation parity is unnecessary while the registered experiment remains Mac-only; adding a host later needs its own pre-data admission.

I independently read the delivered official-contract changes in `runtime/interfaces.py`, `runtime/metrics.py`, `registry/schema.py`, and their focused tests. They now preserve official string member IDs, request/member/log field names, `constraints` and official soft asks, public hard eligibility, qualification event timing, arrived-by59 denominators, unique coverage, wait arrays and ask costs. The family constant matches `evaluate.VARIANTS`, and `execution_authorized` is now a required boolean schema field. This closes the **specific invented-protocol/metric/family/authorization-field defects** for trusted governing records. It does not certify every malformed or hostile record: for example `fields.age_min={'truth':'private sentinel'}` still passes the sanitizer, since field value shapes/types are not validated. The helper's use of governing eligibility is suitable for runtime validation, but independent eligibility verification remains separate.

I independently read the root gate changes. Lease commit now invokes active-generation/host/expiry verification and rejects nonpositive/bool durations. Commit publication uses atomic `os.link` without replacement and fsyncs the commits directory. ZIP Unix symlinks are now rejected. Source-manifest entries are verified against local bytes and rooted paths, empty cell grids and nonempirical scopes are rejected, and runner checks exact membership in the frozen cell list. These are accepted bounded fixes to the reproduced expiry, overwrite and ZIP-link failures. Lease/result publication is still not an integrated recoverable transaction; quarantine remains memory-only; recorder arbitrary-byte/crash-recovery/storage issues remain; and validator does not yet prove full cross-product/source/assets/dependency/panel/review closure merely by these checks.

The final independently executed synthetic suite was **29 tests passing in 0.014 seconds**. Director-captured evidence is under `results/research7/startup_20261012/7b/{unit_tests.json,unit_tests.log,startup_status.json}`. Tests now include directly constructed two-member simulator observations and metric boundary comparison at date delays 30/31 and second-response delays 3/4. These are constructed fixtures, with no `generate()` or policy episodes. The suite includes adversarial expiry, concurrent exclusive commit and ZIP-link checks. This narrows the earlier 23-test criticism but does not complete T01-T31.

The director separately assigned repairs to the 7a fail-open merger. No completed merger diff was available within this final assessment, so initial finding 7 remains unclosed here; a later independent review must close it. Arithmetic-only exact tests remain unclosed under finding 9. Preserved earlier approval reports must be read together with this superseding startup assessment.

The runner now explicitly reports **“Empirical simulator integration is not implemented; user authorization does not implement it.”** This is an appropriate fail-closed state. The director also reports Docker daemon unavailability despite CLI `info` returning zero; container readiness is therefore unestablished and the captured stderr matters. No production isolation approval follows from CLI presence.

**Final admission:** P0 startup repair/registration and bounded constructed P1 checks may continue. **Official P1 smoke and every later empirical phase remain denied by implementation prerequisites**, not by lack of user permission. The immediate blockers are the unimplemented registered episode loop; incomplete exact/nonanticipation/query/dyad/pending-reward checks; unresolved merger/provenance/recorder crash-logging closure; missing frozen full panel/grid/freshness/resource registration; and unmeasured execution/storage capacity. A single-Mac scope removes the current cross-machine dependency, but none of these remaining blockers. No simulator world or empirical result was produced by this review.
