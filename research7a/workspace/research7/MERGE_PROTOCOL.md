# Two-machine registration, transfer and merge protocol

This is a future implementation specification. No runner, merger or research launch is implemented by this planning package. Both plans contribute to one program and one fixed confirmation grid.

## 1. Authority and portable identities

7b coordinator is the only writer of global registration, cell leases, decision ledger and final merged index. 7a owns assigned implementation/check files and shard outputs. Avoid shared writable cloud folders for live attempt directories; transfer only closed immutable bundles. A second machine never invents new seeds, thresholds, model assets, policies or an independent confirmation sample.

Program ID example `r7-YYYYMMDD-<source_digest_prefix>` is assigned at execution. Registration JSON status must be `frozen_execution_registration`, never `planning_only`. The canonical JSON digest excludes only its detached-signature field; record both canonical and raw-file hashes. Stable cell identity:

    (program_id, stage_id, seed, family, policy_id, config_sha256,
     source_tree_sha256, inference_assets_sha256)

Attempt UUID is separate; machine ID/run timestamp/transport filename are not scientific sample identities. Keep relative POSIX artifact paths rooted under bundle ID. No sealed row may depend on a machine-local absolute attempt_path.

The source tree digest covers actual transitive code, configs, model/preprocessor assets, dependency lock and declared baseline implementations; package untracked files. Record OS/arch/Python/BLAS/compression versions/container digest and executable command. Dependency bytes/version closure and preflight parity are necessary; source hash equality alone does not guarantee identical runtime behavior.

## 2. Proposed registration schema

Required fields and checks:

| Field | Meaning/check |
|---|---|
| schema_version/program_id/stage_id/status | Supported schema, immutable experiment identity, executable freeze status |
| source_manifest/inference_assets/dependency_manifest | Paths, sizes, SHA256, import closure and package digest |
| governing_simulator | kit/evaluate hashes, 200 members, 60+40 days, metric version |
| policies/configs/parents | Exact IDs/hash/cost tiers/observations/update rules and comparison graph |
| seed_inventory_hash/freshness_review | Complete coverage/unknowns/reserve exclusions; reviewer closure |
| ordered_seed_list/families/cells | Exact cell set; no unknown or duplicate cell identities |
| selection/statistics | Stage gates, six references, alpha/power/sample formula, and n before E |
| shard_assignments | Whole-seed owner, machine identity, and lease generation |
| resource_forecast | CPU, bytes with 1.5 headroom, attempts/replays, RSS/workers, disk reserve |
| reviews | Independent reviewer report hash/scope/status; developer cannot self-approve |
| predecessor_freeze_hash | Parent phase closure and decision evidence |
| authorized_scope | Exact later user-approved execution task; plan reading alone insufficient |

A machine receives a read-only global registration plus its detached shard assignment. No differing scenario weights/horizons/asset choices per host. An execution validator must fail on unknown fields/invalid status/hash mismatches/incomplete freeze rather than fill defaults that alter science.

## 3. Shards, leases and reassignment

Default 7a light pilot is its own P2a registration, never part of P3/P6. For a shared phase, assign **complete seed clusters**, containing all families/all policy arms. Example: optional E indices 0–23 to 7a if its capability gate passes; remaining indices to 7b. If n < 24, the entire maximum is min(n, 24) but default remains Mac-only until feasibility established. The list is fixed before E outcomes; use an explicit ordered assignment, not opportunistic favorable-family routing. The same source/model must run on both.

Coordinator issues lease `(cell_key,host_id,generation,issued_at,expires_at)`. Worker checks lease/current registration before generating world and before durable commit. One active owner per cell. Global process pool <= 3, including both hosts; global agent slots <= 4, including both directors. Process/agent permits are returned when jobs close; child agents cannot create extra pools.

Reassign only missing/uncommitted original cells for a logged infrastructure reason. Coordinator revokes old lease and confirms no authoritative commit before issuing a higher generation. The original worker must not commit under a revoked generation. Late duplicates are quarantined for comparison, never averaged. A durable committed invalidity remains authoritative and cannot be erased through reassignment. Unknown old-worker status blocks a concurrent rerun until lease authority resolves it.

CPU/disk failure stops new scheduling and drains safe in-flight work. It does not reduce planned n or open replacement seeds. Resume the same registration/source/cell list. Scientific code/asset repair requires a new development version and fresh later registration, never patch E.

## 4. Durable attempt layout

Proposed portable layout:

    bundle/
      registration.json
      shard_assignment.json
      sources/manifest.json
      hosts/host_id.json
      ledger/events.jsonl
      attempts/<cell_key_hash>/<attempt_uuid>/
        started.json
        public/segments/<segment_id>.bin
        public/segment_index.jsonl
        public/outcomes.json
        privileged/initial_world.bin
        privileged/final_state.bin
        finished.json
      commits/<cell_key_hash>.json
      reviews/<review_id>.md
      bundle_manifest.json

Close compressed segments with checksums, uncompressed length, and reconstruction sequence before index append/fsync. Lossless compression and content dedup can reuse public initial requests/world blobs where identical, but every logical invocation retains a resolvable reference. Keep exact wire bytes, mem_before/after, stdout/stderr, fallback/error, sequence/phase/day/timing and validation status. Host-private-world blobs are restricted; no policy/container mount or fitting export can access them. Public training rows must have explicit provenance to public wire records; host-private-oracle data is never silently joined.

A commit row is written only after closed artifacts/hashes and final-episode validation. Use atomic exclusive create/link/rename semantics tested on each filesystem. Retain started/incomplete attempts; never overwrite previous attempt directories. A valid commit includes 120 invocations, 60 action days, and final day 100, denominator, count/funnel/coverage, ordered action/memory digests, and all hashes. An invalid commit contains the observed prefix, error, and artifact references and is equally durable.

## 5. Bundle closure and transfer

The worker stops writing to the closed bundle. The manifest enumerates every relative path, byte count, SHA256, and privilege class. Include expected/complete/missing/invalid-cell lists, all-attempt status, resource totals, ownership leases, source/config hashes and review reports. The archive filename is transport metadata, not a sample ID.

Transfer copies immutable bytes. On the destination, verify the archive hash, safe paths, no traversal/absolute members/symlink escape/duplicate file names and bounded decompression. Restore to a new directory with no overlay on a prior bundle. Verify exact manifest file set/bytes/hashes and count. A copy retry reuses the same bytes; it must never run a simulator cell. No private-world file may be unpacked into an inference asset path.

For disk pressure build streaming archive and verify restoration on registered storage with forecasted space. Do not delete older R6 data. Index the external archive digest/location/readability in final manifest if used; absent/unverifiable raw artifacts prevent the final seal.

## 6. Deterministic merge algorithm

The future `research7.merge` interface is specified, not supplied:

    merge(registration, closed_bundles, output_new_dir, independent_review)

Steps:

1. Verify program/stage/registration/source/assets/dependencies and shard lease lineage.
2. Validate every bundle file/hash, raw-log reconstruction, row schema, calls/horizon/denominator and privilege boundaries.
3. Map each row to exact registered cell identity. Reject extra/unregistered cells; collect all attempts separately.
4. Detect transport duplicates with identical artifact/row identity; retain provenance and count one cell. Raw timing/host metadata can differ across replay attempts, so compare scientific fields and require authoritative lease/commit selection, not identical JSON alone.
5. For same-cell scientific conflicts (actions/memory/world/count/validity/config), halt/quarantine and investigate before analysis. Do not use first-arrival/best-reward arbitration for an unexplained conflict. A registered replay is tagged verification and never replaces the authoritative scientific commit.
6. Check exactly one authoritative commit/cell and expected full grid. An invalid row triggers eligibility failure; a missing row yields an incomplete result, no primary analysis.
7. Verify world-hash equality within seed/family across policies, expected denominator and no cross-stage seed reuse. Build complete seed clusters.
8. Produce immutable merged-cell index containing origin bundle/attempt/hash mapping; do not edit sealed origin rows. Independently recompute all metrics/statistics from logs.
9. Seal only after independent counts/stats/replay/resource/provenance reviews close. Preserve unresolved objections in final report; they can block claims.

Do not average 7a and 7b local means, meta-analysis of p-values, best-host choice or duplicated seed count. Identical examined-world replays are portability checks, not additional independent observations.

## 7. Information access by phase

Development-completed bundles may be analyzed by developers to diagnose hypotheses before next freeze. P4/P5 holdout states cannot enter fitting or new-teacher targets. During E, only operation counts/errors/resource health leave sealed execution storage. Candidate developers cannot inspect E state/outcome/score; independent verifier prepares code using constructed/examined fixtures. After complete E operational closure, release the raw result bundle once for fixed analysis.

The cheap director is authorized to schedule/resume the same cells, collect reviews and apply frozen rules; it cannot alter the inference model or sample size, alpha, seed-family weights, baseline panel or acceptance gate. Any amendment records the reason, author/reviewer, and timestamp, old/new hash and before/after data exposure. An amendment after E exposure cannot preserve an untouched-confirmation claim for that candidate/version.

## 8. Merge test acceptance

T17/T20/T21/T24-T27 must pass before a shared grid. Required fixtures include equivalent-copy duplicate, conflicting cell, revoked lease, incomplete cluster, corrupted wire, source-asset mismatch, invalid commit, wrong world/denominator, unseen family, deleted attempt and hostile archive. The independent merger has a separate owner and does not import main-analysis functions. Hash tests are mechanical evidence; stronger review owns the scientific conclusion.

## 9. What to send when later requesting a merge

Provide both closed-bundle directories/archives plus their manifests, global registration/source package and any lease reassignment ledger. State the intended phase and whether either machine inspected E outcomes before closure. A later request 'merge 7a and 7b' authorizes verification and assembling existing evidence; it does not authorize filling missing cells/training/new confirmation. Missing cells or contradictions are reported with exact identities and resolution options rather than silently run.
