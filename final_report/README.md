# Final Round 2 report

Open [REPORT.md](REPORT.md). Keep `assets/` beside it when publishing or sharing the Markdown.

The report contains 12 figures (PNG and SVG), explicit answers to the submission form and feedback, source-linked results, calibration and waiting analyses, limitations, and reproduction commands. The evidence supports retaining Greedy; it does not establish a new winner.

`data/` holds extracted tables, corrected seed-cluster analyses and input/output hashes. `sources/` preserves the submitted Round 1 PDF and extracted text. `reviews/` contains independent reviews and the validation logs recorded during report preparation.

## Rebuild without running research

From the repository root:

```bash
.venv/bin/python final_report/build_assets.py
```

For a separate report environment, use Python 3.14.7 (the recorded analysis version) and install [requirements-report.txt](requirements-report.txt). Keep the raw source result paths in their repository locations, as described in the report. The script performs saved-evidence analysis only; it never launches a policy, fits a model or runs a simulation.

Historical result links depend on the repository layout. Publish the corresponding evidence paths with the source repository if reviewers need to inspect or reproduce the tables. `data/provenance.json` gives input identities and version information.

Docker was unavailable during report preparation. See REPORT Section 13 for the recorded validation and remaining evidence gaps.
