# Independent R5 duplicate cleanup review

Approved for the current, quiescent R5 repository only. Named reviewer: `/root`; independent reviewer: `/root/cleanup_critic`. Review was read-only except this review and the hash-bound approval. No research workloads, archive-wide rehash, source-wide rehash, or deletion was performed by this reviewer.

## Evidence and scope

- Independently checked the original `research5/archive_results.py` source SHA-256 `f1ed68e285221dc716b3bdcc1b04c167044617f9f2bcd37fe5ab465a1b4695b5` against the historical build report and archive index.
- Independently checked current index SHA-256 `7fce78beefa52c25cae8bcf2c6068bb796d146b35a55cc3bacafce8d509996e6` against the historical report.
- Historical source performs exhaustive streamed archive verification: regular members, no duplicate names, exact expected membership, each member's length and SHA-256, and each original file's size and SHA-256. Historical report records successful verification of all 15,501 members plus restore/non-overwrite checks.
- Current cleanup verifier freshly hashed all three retained archives and all 15,501 originals before creating the exclusive-create manifest. The reviewed implementation fails closed on any mismatch.
- Independently compared every manifest row's path, bytes, SHA-256 and archive mapping to the anchored original index; no missing, extra or duplicated rows. Independently checked every current source stat seal and every indexed path's regular-file, non-symlink, repository containment and untracked status.
- Proposal deletes 15,501 exact duplicate extracted files totaling 85,029,342,282 logical bytes (79.19 GiB). All three archives, indexes, reports, summaries and unindexed files remain outside the deletion set.

## Safety argument and application conditions

SHA-256 equality of the current archive and the historically exhaustively verified archive, with the unchanged index anchor, preserves the prior member-by-member content result. Fresh equality of each current original with its indexed digest establishes that the original adds no bytes missing from the retained archive. Restreaming every tar member would repeat the established result without adding meaningful assurance in this quiescent context.

The removal action must use the exact approved script and manifest; it verifies those hashes, repository/index context, current archive hashes, all source stat seals before any deletion, and each row again immediately before unlink. It writes and fsyncs an intent record before each unlink; partial execution remains recoverable from retained archives. Exclusive-create outputs prevent accidental journal/report overwrites.

No blocking issue found. R5 must remain without concurrent writers for the duration. The dev/inode/size/mtime seal detects ordinary writes and replacement; it does not claim protection against deliberate mutation that preserves mtime, or a hostile check/unlink race. Adding ctime or descriptor-based unlink guards would harden that adversarial case, but is not required under the confirmed quiescent R5 operating condition. This approval does not authorize deleting archives, unique outputs, tracked files, or any other research round.

Validation: in-memory Python compile succeeded; full indexed-path inspection found zero unsafe, tracked or duplicate paths; full manifest/index comparison and current stat-seal inspection passed. Review compute remained well below the 120 CPU-second allowance.
