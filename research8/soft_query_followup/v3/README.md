# Lossless storage continuation

This wrapper continues the original 2,880-cell development experiment. It preserves 480 original commits and their registration identity; 2,400 remaining cells carry a separately frozen infrastructure identity. Seeds are previously planned/used development worlds, not fresh confirmation seeds. See ../storage_recovery/recovery_note.md and final_review.md.

Python 3.14 with stdlib compression.zstd is required. No external compressor/API is used. Archive an attempt only after its writer stops. storage.archive_attempt verifies exact original bytes and publishes durable archive/catalog files before deleting duplicate raw files. Original commit JSON files are never rewritten. Archives contain every required original evidence file. Manifest SHA256 binds archive bytes and original file lengths/digests. Interrupted cleanup can be resumed safely. The independent auditor serializes one external-drive extraction at a time, reconstructs public events, validates legality and requires the complete original grid.

The 15GiB guard covers this campaign output plus reserved worker/audit transients, not all historic repository data. Seven workers each reserve 1,100MiB for raw/archive overlap; raw evidence is checked after phase boundaries against512MiB. Audit extraction has a512MiB slot. On insufficient capacity or failed verification, stop and preserve evidence. Do not omit cells, delete failures, weaken audits or relabel reused seeds as fresh. At the measured480-cell compression ratio the final archives forecast roughly2.12GiB; forecasts are not guarantees.

Run from the project root, with all temporary files on this external drive:

```sh
PYTHONPATH=. TMPDIR="$PWD/research8/soft_query_followup/v2/.tmp" python3 -m pytest research8/soft_query_followup/v3/tests -q
PYTHONPATH=. TMPDIR="$PWD/research8/soft_query_followup/v2/.tmp" python3 -B -m research8.soft_query_followup.v3.launcher --registration research8/soft_query_followup/storage_recovery/continuation_registration.json --output results/research8/soft_query_followup/v2_replication --workers 7
```

Do not launch a second coordinator. Source files and AGENTS.md must stay frozen during this run. Existing commits are verified and skipped. To drain safely, create results/research8/soft_query_followup/v2_replication/DRAIN_REQUESTED, allow workers to finish, then remove the sentinel before resuming the identical registration. An incomplete operational audit is not a completed-study certification. The launcher performs full independent public-event audit after all cells finish; retain the original registered cluster analysis and seven Holm-adjusted contrasts. No performance or policy-superiority claim follows from compression/tests alone.
