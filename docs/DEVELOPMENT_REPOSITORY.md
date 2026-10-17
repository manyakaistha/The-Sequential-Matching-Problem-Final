# Development repository

This repository contains the supplied benchmark, policy experiments, research workspaces and the final technical report. Start with the [project README](../README.md), [final report](../final_report/REPORT.md) or [research index](RESEARCH_INDEX.md).

## Evidence and reproducibility

Source, registrations, reviews and compact results are versioned. Large selected JSON files use Git LFS. Raw trace directories, attempt/commit stores, event streams, archives and container contexts remain on the original results drive under the existing ignore rules. A clone therefore does not contain every raw campaign artifact.

`LOCAL_RESEARCH_ARTIFACTS.json` records some excluded historical artifacts; an inventory is not an integrity verification. Use the relevant source manifests, archive catalogs and audit proofs when checking an experiment. Historical reports can contain superseded interpretations; the final report identifies important corrections.

The 7a/7b workspaces contain duplicated historical source to preserve handoff context. Their original manifests describe the original snapshots, not an independently validated new experiment. See [cleanup notes](REPOSITORY_CLEANUP.md) before attempting exact historical snapshot verification on this branch.

## Repository

Development: https://github.com/manyakaistha/the-sequential-matching-problem-dev-repo-final

Original benchmark: https://github.com/RomeoJulietLove/The-Sequential-Matching-Problem

[Clone and update instructions](CLONING.md).
