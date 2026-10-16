# Research 5 archived duplicate cleanup

Only the exact extracted files listed in `verified_manifest.json` are eligible for removal. Their current hashes and sizes matched the lossless archive index; the archives matched the original exhaustive verification anchors. All archives, indexes, reports, summaries, source, public data and every unindexed file are retained. Research 6 and Research 7 outputs are untouched.

`cleanup_result.json` records completion and observed disk space. `removed_files.jsonl` records each unlink intent and completed removal. `approval.json` binds the independent review to the exact script and manifest. `restoration_probe.json` records successful sample restorations from all three archives. Logical bytes removed and filesystem free-space gain can differ because of APFS allocation and snapshots.

To restore the Research 5 extracted logs later, run from the repository root:

```bash
python3 research5/archive_results.py restore --destination .
```

The restoration script skips identical existing files and refuses to overwrite differing files. Restore before using old verification scripts that expect the extracted paths. This is a storage/access change, not a deletion of archived research evidence or a change to prior findings.
