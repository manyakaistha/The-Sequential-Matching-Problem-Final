# Reproducing the completed extension

The main study is complete: 1,056 development, 504 selection and 480 confirmation
episodes. Replays of examined seeds are replications, not new independent evidence.
Do not extend confirmation or tune its candidate from these results. Consult
`EXPERIMENT_REGISTRY.md`, `results/extended/frozen_candidate.json` and the command
ledger before evaluating anything. The ledger distinguishes timestamped pipeline
commands from reconstructed commands whose historical timestamps were not recorded.

## Inspect and restore existing data

From the repository root, use Python 3.14.7 and the recorded exact host pins:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-research.lock.txt
.venv/bin/python -m research.extended_archive restore
.venv/bin/python -m research.extended_archive verify
```

The eight archives in `results/extended/archive_index.json` preserve exact paths,
uncompressed byte counts and SHA256 values. Five `.tar.gz` files restore the five
trace directories, and three `.json.gz` files restore the complete development,
common-cohort and confirmation calibration assignment rows. The largest archive
is about 46.6 MB. Raw files are retained locally but ignored by Git to avoid very
large individual files; compressed data are eligible for version control.
Restoration creates missing files and refuses differing existing bytes. Accessible
`.summary.json` files retain all calibration aggregates and uncertainty without
duplicating assignment rows; the report can be built directly from these summaries.

Archive verification checks archive bytes and all restored raw member bytes. The
final manifest additionally fingerprints sources, summaries, figures, logs and
individual raw files. SHA256 consistency is reproducibility evidence, not a
tamper-proof historical timestamp. The host lockfile is platform/Python dependent;
the inference container separately pins Python 3.12.7 and NetworkX 3.7.

## Analyze recorded experiments without new rollouts

```bash
.venv/bin/python -m research.extended_analysis results/extended/development.json
.venv/bin/python -m research.extended_analysis results/extended/selection.json
.venv/bin/python -m research.extended_analysis results/extended/confirmation.json --confirmatory simple_fifo
.venv/bin/python -m research.extended_interactions results/extended/development.json
.venv/bin/python -m research.extended_theory
.venv/bin/python -m research.extended_audit --traces results/extended/development_traces --policies terminal_fifo,independent_fifo,no_learning_fifo,simple_fifo,terminal_soft --output results/extended/audit_development_calibration.json
.venv/bin/python -m research.extended_audit --traces results/extended/development_traces --common-cohort --output results/extended/audit_common_cohort_calibration.json
.venv/bin/python -m research.extended_audit --traces results/extended/development_traces --policies simple_fifo,greedy --mechanisms --replay-graphs --output results/extended/mechanisms.json
.venv/bin/python -m research.extended_audit --traces results/extended/confirmation_traces --policies simple_fifo --output results/extended/audit_confirmation_calibration.json
.venv/bin/python -m research.extended_report
```

Trace auditing reconstructs final labels and oracle comparisons offline; these
inputs never reach evaluated policies. Public graph replay recreates observations
while holding recorded actions fixed. Common-cohort scoring uses the same 3,567
prospective greedy assignments with separate model memories. These audits are
descriptive or exploratory and do not add confirmatory policy comparisons.

Run analysis into a separate copy when exact original output byte identity matters:
float formatting, plotting metadata, package versions and timing can vary. Existing
results and manifest identify the actual completed execution.

## Replicate rollouts with their actual source versions

The original development executable is preserved as
`research/extended_policy_development.py`, SHA256
`6cf508147f6cb5de51185e92c35bd25501c5c5737cc5db7e22b8f9f411509c60`.
The guarded selection/confirmation executable is `extended_policy.py`, SHA256
`823794e0818b2c3c0ea61b37e89078c537f6c3117ee8bf0e036eab94b6e81891`.
Only the guard differs; the 132-episode ordinary regression has exact action and
outcome parity. This does not guarantee equivalence for all scheduling conditions.

Create a separate staging directory so the package, archived development source,
freeze record and original raw results cannot be overwritten. This copies source
and prior baseline artifacts but does not reuse the completed extension outputs:

```bash
.venv/bin/python - <<'PY'
from pathlib import Path
import shutil
root = Path.cwd()
destination = Path('/tmp/sequential-matching-replication')
destination.mkdir()  # fail if it already exists
for name in ('kit.py', 'evaluate.py', 'policy.py', 'research_policy.py',
             'extended_policy.py', 'Dockerfile.extended',
             'requirements-research.lock.txt'):
    shutil.copy2(root / name, destination / name)
shutil.copytree(root / 'research', destination / 'research',
                ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(root / 'results/research', destination / 'results/research')
PY
cd /tmp/sequential-matching-replication
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-research.lock.txt
cp research/extended_policy_development.py extended_policy.py
.venv/bin/python - <<'PY'
from research.extended_candidates import CANDIDATES
from pathlib import Path
Path('development_policies.txt').write_text(','.join(sorted(list(CANDIDATES)+['greedy','prior_product'])))
PY
.venv/bin/python -m research.extended_benchmark --policies "$(cat development_policies.txt)" --seeds 1001:1008 --output results/extended/development.json --traces results/extended/development_traces
cp research/extended_policy_safe.py extended_policy.py
.venv/bin/python -m research.extended_benchmark --policies "$(cat development_policies.txt)" --seeds 1001 --output results/extended/guard_regression.json --traces results/extended/guard_regression_traces
.venv/bin/python -m research.extended_guard_verify
.venv/bin/python -m research.extended_analysis results/extended/development.json
.venv/bin/python -m research.extended_select shortlist
.venv/bin/python -m research.extended_benchmark --policies no_learning_fifo,terminal_soft,independent_fifo,simple_fifo,terminal_fifo,greedy,prior_product --seeds 2001:2012 --output results/extended/selection.json
.venv/bin/python -m research.extended_analysis results/extended/selection.json
.venv/bin/python -m research.extended_select freeze
.venv/bin/python -m research.extended_benchmark --policies greedy,simple_fifo --seeds 3001:3040 --output results/extended/confirmation.json --traces results/extended/confirmation_traces
.venv/bin/python -m research.extended_analysis results/extended/confirmation.json --confirmatory simple_fifo
```

Those confirmation commands replicate already examined seeds and a fixed candidate;
they do not turn them back into untouched test data. The recorded shortlist, config
and original freeze are authoritative. If timing-sensitive fallbacks change a
replication, report the change rather than refreezing or silently replacing results.
Do not run `research.extended_pipeline` over completed artifacts: it performs a
one-time source adoption and selection. A completion gate now rejects that use.

## Verify the selected executable

The **selected** candidate requires explicit configuration. The bare executable
and image entrypoint use the integrated model, which is a different comparator.

```bash
.venv/bin/python extended_policy.py --config '{"model":"simple"}' < request.json
docker build -f Dockerfile.extended -t sequential-extended:1.0 .
docker run --rm -i --network none --cpus 2 --memory 1g --pids-limit 64 --read-only sequential-extended:1.0 --config '{"model":"simple"}' < request.json
EXTENDED_SAFETY_TEST_TARGET=actual .venv/bin/python -m unittest -v research.test_extended_policy research.test_extended_safety
.venv/bin/python -m unittest -v
.venv/bin/python -m research.extended_production --config '{"model":"simple"}' --output results/extended/production_replication.json
```

The completed production record enforces offline networking, two cores, one GiB,
64 PIDs and a read-only root. It compares semantics separately from action ordering
and byte digests over a full seed-1001 development episode. The observed image size
is 52,761,330 bytes. Original stress timeout/error artifacts are retained alongside
the guarded valid cases. The seven-second alarm covers optimized decision work;
parsing, output and fallback are outside it. Evidence concerns the shipped
200-member workload, not a universal timeout guarantee.

## Finalization and preserved history

After deliberate report/audit changes, rebuild lossless archives, then write the
manifest last. Do this in the replication copy when preserving this package's
manifest and original recorded evidence:

```bash
.venv/bin/python -m research.extended_archive build
.venv/bin/python -m research.extended_archive verify
.venv/bin/python -m research.extended_report
.venv/bin/python -m research.extended_manifest
```

The exact earlier report and verified bibliography are preserved as
`REPORT_2026-10-07.md` and `REFERENCES_2026-10-07.md` in `research/`, with hashes
equal to the previous manifest. Earlier theory, source and result artifacts remain.
The final statistical, mathematical and package review documents are included in
provenance. Their finalization requests were addressed by the completed command
ledger, source-aware instructions, explicit selected invocation, lossless archives,
final manifest and corrected absolute-error-bound wording. Frozen inference and
the registered comparison were unchanged.
