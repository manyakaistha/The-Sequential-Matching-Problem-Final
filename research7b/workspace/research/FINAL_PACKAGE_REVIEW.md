# Independent final package review

8 October 2026. Read-only audit of inference, recorded experiments, registry,
report builder and packaging. This review ran no new simulator experiments or
test suites. Checks below were independently recomputed from existing files.

## Verified integrity

* All six current inference hashes equal `frozen_candidate.json`; the three
  frozen auxiliary hashes (`policy.py`, benchmark and selection code) also match.
  Selection, confirmation and subprocess experiments record the frozen hashes.
* The archived `research/extended_policy_development.py` exactly matches the
  original development SHA-256. All other inference files match across original
  development and guarded confirmation. The recorded guard regression covers
  132 episodes (22 configurations/comparators × six families at seed 1001), with
  no semantic, outcome or ordering differences. Original development maximum
  invocation time was below the newly introduced seven-second guard.
* Development: 1,056/1,056 valid episodes; guard: 132/132; selection: 504/504;
  confirmation: 480/480; subprocess: 12/12. The original baseline audit reproduces
  18/18 existing episodes.
* Every one of the 12 subprocess rows matches its corresponding guarded seed-1001
  episode on assignments, acceptance, dates, qualified reward, missing feedback,
  ask cost, arrivals, coverage, validity and failure count. Both semantic action
  hashes and byte action hashes match, across all six scenario families and both
  greedy and simple_fifo.
* `research/REPORT_2026-10-07.md` exactly matches the earlier report SHA-256 in
  `results/research/manifest.json`. All earlier inference/analysis source files
  and `Dockerfile.research` covered by that manifest remain hash-identical.
  The legacy manifest itself and recorded previous results remain present.
* Existing logs record 22 passing original tests and 28 passing extended policy
  and safety tests. The pipeline explicitly sets
  `EXTENDED_SAFETY_TEST_TARGET=actual`, so its safety tests exercise the adopted
  inference source rather than only the proposal file.
* The completed production record uses selected `{"model":"simple"}` in all
  three execution modes. Recorded action digests and outcomes match. Maximum
  invocation times are 0.0312 s in process, 0.0879 s subprocess and 0.2318 s Docker;
  serialized memory is 152,643 bytes and peak request is 631,222 bytes.
* The completed production record measures actual cgroup quota `200000 100000`,
  RAM `1073741824`, PIDs `64`, root-write error 30, UID 65534, only loopback up and
  image size 52,761,330 bytes. The four-file inference image includes only the
  public kit and observation-only policy/model/config modules, not audit code.
* Confirmatory interpretation agrees with raw statistics: selected simple_fifo
  has a paired difference of −0.0416667 MSMI/100, 95% CI
  [−0.0910680, 0.00773463], two-sided p=0.0959605 across 40 clusters. Superiority
  is not established; neither is inferiority at the registered .05 level.

## Finalization fixes requested of the lead

1. Complete the exact command ledger with the initial development matrix and
   audit/calibration/common-cohort/mechanism/report/manifest commands. Mark any
   reconstructed command or timestamp as reconstructed rather than prospective.
   The current pipeline ledger begins at guard adoption and does not describe
   all existing artifacts.
2. Supply source-version-aware reproduction instructions. Replaying development
   with current guarded source may preserve ordinary semantics, but cannot
   reproduce the original recorded source hash. Use the archived development
   source in a separate staging directory for that matrix; use frozen guarded
   source for selection/confirmation. Do not rerun the orchestration over completed
   files: it would overwrite the development-source archive with guarded source
   before its original-hash assertion fails.
3. State an explicit selected executable command, including
   `--config '{"model":"simple"}'`. Bare `Dockerfile.extended` entrypoint runs
   the integrated default; final production replay correctly supplies the simple
   config. Preserve frozen inference instead of changing its default afterward.
4. Archive large raw trace directories and raw calibration assignment rows with
   hashes and exact restoration paths. Trace JSON totals approximately 1.18 GiB;
   development and confirmation calibration JSON each exceed 150 MiB, above a
   usual GitHub per-file limit. Keep report-needed summaries accessible, document
   decompression, and include compressed artifacts in final provenance. Existing
   report text already claims trace archives but they were not yet present during
   this audit.
5. Generate provenance only after final source/report/review/command/archive edits.
   Include this review, the archived previous report/theory/reference materials,
   the public data manifest, any reproduction guide/lockfile and archive restore
   script in source provenance. Validate every claimed artifact exists. Current
   manifest builder includes inference, analysis, registry and report files but
   not all of these additional review/reproduction inputs.
6. In the report builder, replace “directional error bound” with “absolute error
   bound”: the theorem bounds absolute sigmoid mean-substitution error and does
   not give a Jensen direction. Rebuild the report after fixing wording.

The current `legacy_references.md` is the earlier unverified bibliography, not a
snapshot of the verified `docs/REFERENCES.md` hashed by the prior manifest. The
new verified bibliography is intentionally updated. Do not claim an exact
preserved previous-reference snapshot unless it is recovered separately. Earlier
report/result/source preservation is independently verified as described above.

## Review limits

Actual Docker enforcement and replay are supported by their completed JSON/build
logs. A lightweight attempt to independently rehash the packaged `/app` files
could not connect to the currently stopped Docker daemon; no new live image-hash
verification is claimed. The earlier manifest hashes sources but does not hash
all its raw artifacts, so this review verifies earlier artifact presence and
source/report preservation rather than asserting a newly proved byte identity
for every old raw file. Guard equivalence and production compliance have the
tested finite scope documented in their artifacts, not a proof over arbitrary
requests or market sizes.

## Finalization follow-up

The lead addressed the six requested packaging fixes. This follow-up independently
read the completed reproduction guide, archive implementation/index, updated
report/manifest builders, command ledger and completed-pipeline gate. No simulator
experiments, test suites or restoration writes were performed.

* Independently hashed all eight compressed archives against the index, then
  streamed every decompressed member and checked its exact uncompressed length
  and SHA256. All 1,687 raw files passed: 480 confirmation traces, 1,056
  development traces, 132 guard traces, four smoke traces, 12 subprocess traces
  and three full calibration JSON files. All tar members are regular files at
  the registered repository-relative paths, with no duplicates or omitted indexed
  members. Archive content checks establish restoration-byte consistency without
  rewriting the retained local raw files.
* All three accessible summaries exactly retain every raw JSON field other than
  `assignment_rows`, with the correct archive pointer and removed-row count:
  development 17,749, confirmation 18,133 and common cohort 3,567 assignments.
  The report's `load` and `exists` helpers accept these summaries when the ignored
  raw JSON is absent. Thus a checkout containing compressed archives and summaries
  can build the report before restoration; detailed audits require restoration.
* Restoration verifies compressed hashes first, creates missing original paths,
  and verifies every restored or already-present raw file. Existing differing
  bytes are not overwritten and cause verification to fail. The reproduction
  guide accurately describes this behavior and separates re-analysis from
  repeated rollouts of previously examined seeds.
* The guide uses a separate staging directory, deliberately switches between
  archived development and guarded selection/confirmation source, and preserves
  original extension outputs. It explicitly identifies selected simple-model CLI
  configuration, host/container version differences and timing-sensitive fallback
  limitations. The pipeline now refuses a completed-study rerun before source
  adoption can overwrite the archive.
* The initial development and calibration/mechanism commands are recorded as
  reconstructed with null historical timestamps, preserving the distinction from
  actual timestamped pipeline records. Final archive/report/manifest execution
  records may be added as those finalization steps finish.
* The exact prior verified bibliography was recovered as
  `research/REFERENCES_2026-10-07.md`; its SHA256 equals the prior manifest's
  `docs/REFERENCES.md` hash. This supersedes the earlier missing-snapshot caveat:
  the separate `legacy_references.md` remains the older unverified bibliography.
* All six frozen inference and three frozen auxiliary hashes remain unchanged.
  The updated manifest builder includes final reviews, reproduction guide,
  archive code, previous report/reference snapshots, data manifest and exact host
  lockfile. The report now states the absolute-error bound and scoped runtime
  evidence, including work outside the decision alarm.

No remaining blocking package issue was identified. The final report and
provenance manifest are to be generated after this review edit and final command
ledger edits. This statement does not claim a subsequently generated manifest
was already inspected. The earlier limitation on current live Docker rehashing
remains; completed resource/replay evidence is unchanged.
