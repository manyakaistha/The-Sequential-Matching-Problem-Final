# Reproduce or verify round-five evidence

The registered test is complete. Do not relaunch launch.py, rerun preparation, edit frozen policies/design, retune on confirmation or replace/extend seeds. Existing-output refusal is intentional. Historical EX­PERIMENT_REGISTRY/README/preparation records remain byte-identical to their execution versions; FINAL_REPORT and manifest describe completion.

## Read and check

From repository root, with the registered host NumPy/SciPy versions (design.json):

```sh
python3 -m research5.package_checks
```

This checks exact grid/statistical/replay/production/world/log gates, source hashes, raw/archive hashes, interruption preservation and prior manifests. It reads many gigabytes and can take time. It does not run policy episodes or modify completed evidence. Gate assertions must be enabled; -O is refused.

Independent outputs and exact commands are in independent_commands.jsonl, production_commands.jsonl, world_checks.json, log_checks.json and archive_build_checks.json. Source scripts are preserved. Statistic/replay/audit/build scripts refuse overwriting existing outputs; to reproduce computational work use an isolated copy/output location, keeping the same data and hashes. Main sample: seeds90001–90430, six families, candidate population_control versus kit greedy, 60action+40follow-up,200members. Same fixed seed-cluster test includes118 recovered committed rows; it is not fresh after interruption.

## Lossless archives and safe restoration

archive_index.json lists repository-relative regular members, byte counts and hashes. raw_greedy.tar.gz and raw_population_control.tar.gz compress public JSON traces; raw_full_logs.tar contains already compressed complete I/O and separate privileged logs. All interrupted raw attempts are included. Inner damaged gzip records from interrupted attempts are deliberately preserved byte-for-byte; complete committed gzip records pass the exhaustive reader.

Verify archive integrity even if raw originals have later been removed:

```sh
python3 -m research5.restore_artifacts verify
```

Restore into a separate empty directory (creates repository-relative subpaths):

```sh
python3 -m research5.restore_artifacts restore --destination /tmp/research5-restored
```

Or restore missing original paths from repository root:

```sh
python3 -m research5.restore_artifacts restore --destination .
```

The helper refuses symlink root/ancestors/files and differing existing bytes; it skips identical existing files. It uses directory descriptors, O_NOFOLLOW and exclusive creation. Do not use archive_results.py's legacy restore action on directories containing symlinks. Trust a verified final manifest/index; hashes are consistency evidence, not a trusted historical signature. Extraction needs sufficient additional disk space; no automatic deletion occurs. Full archive-member streaming was checked; three real sample files were written/restored, and fourteen temporary security fixtures checked safe extraction including archive-only use. Full physical restoration of every member was not separately duplicated during packaging.

## Public versus privileged records

Each *.invocations.jsonl.gz preserves complete policy-visible requests/responses, memory, timing and errors. *.privileged.jsonl.gz contains initial generated world and final simulator attributes. Privileged files are audit-only; never feed them or seed/scenario labels into evaluated policies, fit on them, or use final confirmation for current-round model selection. No future events are present in checked invocation observations. Raw public traces retain assignment snapshots, action histories and completed public feedback.

## Provenance sealing

The final manifest.json pins completed source/report/results/archive bytes and describes tested scope. package_gate.json is finalized before hashing into that manifest. Do not redirect gate stdout into a manifested file or append reports/ledgers after sealing. To check every final manifest entry independently, stream SHA256 and compare its recorded bytes/hash; preserve any mismatch rather than overwriting it. The inherited round-three three-file metadata reconciliation is documented in roundfour and is not a new exception.
