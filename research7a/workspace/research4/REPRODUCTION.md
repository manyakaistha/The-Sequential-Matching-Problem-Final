# Reproduction

Run from repository root using Python3.10+ and requirements-research.txt for offline
SciPy/NumPy/Matplotlib analyses. Inference is standard library only. Preserve root
policy.py; deployable entrypoint is python3 -m research4.policy --candidate NAME.

Eight source/configurations are frozen before B in screen_freeze.json. Complete
finite experiment pipeline: python3 -m research4.run_registered . Its fixed stage
plans/rows/codehashes/commands are in results/research4; it refuses existing outputs.
To reproduce use a separate checkout or output directory and identical source
hashes; never overwrite recorded experiments. Each episode uses evaluate.episode,
60 actiondays plus40 followup. JSON roundtrips expose only public observations.
Raw assignment snapshots are prospective public member fields; greedy match_states
retain match-time observations except unusedask_log for same-example predictions.
Final completedfeedback is label data and never a current-policy feature.

Correctness: python3 -m unittest -v research4.test_candidates . Wrapper and
production checks have dedicated review/source/commands. Analysis:
python3 -m research3.analyze results/research4/confirmation.json --output /tmp/reanalysis.json
python3 -m research4.mechanisms results/research4/focus.json --output /tmp/mechanisms.json

The privileged mechanisms audit reconstructs true actors/family solely offline,
never future draws. It is not an evaluated policy or tight oracle bound. Nominal
95%confirmationCI and three-test98.333%programCI are separate. No source/config/
training changes during frozen confirmation. Sample size is frozen usingCvariance,
not significance. UnknownCPU usage is not inferred from walltime. Exact recorded
childCPU/wall appear commands.jsonl; other agent ledgers retain measured scopes.

After C completes, `python3 -m research4.prediction_audit` computes prospective
same-cohort forecasts, including independently reconstructed full-funnel model
projections whose terminal probability must match the evaluated scorer. Eight
terminal proper-score tests form the fixed Holm family; stage/slice summaries
are descriptive. No confirmation data is opened by this audit.

Lossless archives: `python3 -m research4.archive build`, then `verify`; `restore`
restores only missing registered regular files and refuses differing existing
bytes. Build requires absent archives; preserve originals when reproducing.
Final `python3 -m research4.package` verifies previous round manifests/files,
source/registry freeze, exact planned grids, independent selected replay,
production enforcement/parity, required reviews and every archive member before
writing results/research4/manifest.json. The gate finalizes its own package_gate.log before collecting hashes. Invoke it directly and never redirect stdout to any file inside either manifest root; the tool transcript captures final completion. Do not append ledgers or review notes after sealing.


Frozen selected policy: `population_control`; confirmation seeds83001–83056,
56 clusters/672 episodes. Independent replays use existing83001/83002, all six
families, both direct/subprocess modes and full40-day follow-up. Exact invocations:

```sh
.venv/bin/python -m research4.independent_replicator --policies greedy,population_control --seeds 83001,83002 --variants all --reference results/research4/confirmation.json --cluster-audit --output results/research4/replication_confirmation.json
.venv/bin/python -m research4.independent_replicator --policies greedy,population_control --seeds 83001,83002 --variants all --mode subprocess --reference results/research4/confirmation.json --cluster-audit --output results/research4/replication_confirmation.json
```

The replicator appends a separate run record, preserving direct/subprocess scope.
Reproduce in a separate output path to avoid duplicating an existing evidence set.
Production build/replay commands and failed missing-image attempt are separately
retained in commands_production.jsonl; application source hashes match even though
rebuilt Docker image IDs differ. All actual cgroup values and calls are recorded.

Five raw archives cover four stages plus eight smoke traces. `archive_index.json`
contains archive and member hashes; restoration does not overwrite different
existing bytes. Original raw traces are retained as well as compressed copies.
Three inherited round-three review/log hash discrepancies are documented in
PROVENANCE_RECONCILIATION.md, with exact manifested prefixes and current hashes;
all original older files and manifest remain unchanged.
