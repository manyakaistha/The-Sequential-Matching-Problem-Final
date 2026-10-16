# Independent storage-continuation production review

Reviewer: `/root/storage_final_review`, independent of storage and runtime developers.
Scope: v3 storage, continuation, archive-aware audit, runner and launcher; public
metadata and synthetic fixtures only. No fitting, complete campaign, seed
selection, or private-world inspection is part of this review. The initial
allowance was 120 CPU seconds / 12 minutes wall; the director extended it by
60 CPU seconds / 10 minutes to permit review of the completed launcher.

## Decision

The storage-only continuation has passed independent production review. G and
Q6 diagnostic replays matched their original world digests, action digests,
complete metric dictionaries, invocation counts and fallback counts, and passed
the archive-aware independent cell audit. Evidence is recorded in
`../storage_recovery/diagnostic_replay_result.json`; the reviewer inspected that
record and the replay assertions. Replays use already retained worlds in separate
output and do not add scientific observations. This review does not certify the
incomplete campaign or a policy improvement.

The regular-file archive format preserves each original file's exact bytes and
SHA-256, including empty files. The catalog is published durably before raw
deletion, verification streams each member, and extraction rejects traversal,
symlinks, duplicate members, unexpected members, physical corruption and
decompression truncation. A retry tolerates partial raw deletion only after
verification of the already committed archive. Archive callers must first stop
writers; the implementation explicitly states this requirement.

The continuation carries the original registration file digest and retains the
original source manifest. Its grid, policy specifications, analysis and execution
resource caps must equal the original. Original retained commit files are bound
by their exact file digests; newly completed cells must identify the continuation
registration and augmented source manifest. Recovery-note integrity and explicit
authorization/status validation were added after review feedback.

The independent archive-aware audit compares the exact artifact hash inventory,
reconstructs public metrics and actions, and distinguishes original and continued
commit attribution. It now rejects an archive larger than 512 MiB before
materialization and extracts into output-local temporary storage. An output-local
flock now spans materialization, audit reads and cleanup, serializing concurrent
archive auditors into the single reserved extraction slot.

`python3 -m pytest research8/soft_query_followup/v3/tests -q` passed:
51 tests, 10 subtests, 0.54 seconds on the final reviewed sources. The independent synthetic tests added in
`tests/test_final_adversarial.py` cover fixed 2,880-cell metadata mutations,
policy/analysis/resource mutation, original source mutation, retained commit-byte
mutation, original/new source separation, source path escape, added unbound
dependencies, recovery-note mutation, authorization mutation and the audit
materialization cap. Additional tests cover the exact storage admission boundary,
invalid worker counts, worker-plus-descendant process accounting and required
coordinator lease. These are production evidence checks, not scientific runs.

The runner's simulation/action/metric body was compared with frozen v2. Its
substantive changes are continuation verification, per-attempt evidence checks,
and archiving after publication of the unchanged logical commit record. It uses
the unchanged v2 cold invocation transport and metric implementation. Existing
commits are verified against their registered identity and exact archive hash
coverage before being returned.

The launcher shares the original simulation lock, permits at most seven workers,
preserves the original wall/CPU/wire/RSS/free-space limits, and uses one process
snapshot per monitoring pass. It counts all existing output-file bytes and
reserves 1,100 MiB per pending worker plus the 512 MiB audit slot before dispatch.
This includes raw/archive duplication and compression framing; per-attempt raw
size is checked at phase boundaries. Budget exhaustion preserves evidence and
the fixed grid. A requested drain stops dispatch and lets active workers finish.
The final full-grid audit remains required after all 2,880 cells complete.

A bounded post-replay launcher correction allows a newly created continuation
output to resume and requires exact dictionary equality for either the original
binding or continuation binding, including stage and registration-file SHA-256.
The reviewer inspected this correction and reran the full v3 suite. The runner,
policies, simulator and audit sources used by the parity replays were unchanged.
The director reported an initial coordinator stopped before any worker dispatch;
its superseded startup registration and binding are preserved separately.

The migration record reports 480 attempts containing 47,520,617,679 logical bytes
in 379,165,348 archive bytes. Independent metadata checks found 480 unique valid
original-version commits, all 40 original source hashes unchanged, 480 archive
catalogs, and all current retained commit-file hashes equal to the migration
record. The reviewer did not independently decompress the entire 47.52 GB;
streaming archive verification was performed by the director's migration process.

Reviewed SHA-256 identities:

| File | SHA-256 |
|---|---|
| storage.py | `75cd1205c9dd4fd5f09c213cd23ef4d5687505d2f06898eb7e5a6f237cfde349` |
| continuation.py | `b86bbd4b1f5e14b84dca265b36f293989b40fb5525dd38b061726d421c647ff3` |
| audit.py | `8e54d17ba737c763cae44cd4c866abfae82fd9288e779f877b4003e80d8a1565` |
| runner.py | `db5cf29bd9a6fd91ae89209b9c460ea7e43aaecf45fb524af036e0a0c8a3c3ef` |
| launcher.py | `2ef4d1faa9b3a06e711e0cfeb29530c549a5b3c053cd7affe12ac7d26d088f72` |
| tests/test_final_adversarial.py | `ae734954f429d13738798dfa3bd9a0066debc0388e88b313b5a2ff2487271c85` |
