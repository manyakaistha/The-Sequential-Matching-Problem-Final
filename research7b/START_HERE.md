# Start here: 7b

Copy the entire `research7b` directory to the intended machine. Open a terminal in that directory. Paths below are relative and work when the parent path contains spaces.

```bash
bash bootstrap.sh
```

Default setup creates `.venv`, verifies hashes/syntax and writes hardware/dependency metadata to `setup_outputs/preflight.json`; missing locked packages are reported as pending. It installs no research dependencies and starts no workload. To install the minimal R6 lock (NumPy, SciPy and NetworkX) later, after checking platform/Python wheel compatibility. The complete historical tool lock remains at `workspace/requirements-research.lock.txt` for optional legacy tools; it is not installed by bootstrap:

```bash
bash bootstrap.sh --install-deps
```

Use the environment Python for manual preflight (`.venv/Scripts/python.exe` on Windows):

```bash
.venv/bin/python preflight.py --output setup_outputs/preflight.json
```

Read `BLOCKERS.md`. Open your machine agent at **`research7b/workspace/`**, then paste this prompt. Setup does not invoke or configure that agent automatically.

```text
You are the 7b machine director. Current directory is the portable workspace root containing kit.py and research7/. Read ../README.md, ../BLOCKERS.md, ../OWNERSHIP.md, ../machine.json, ../work_orders.machine.json, research7/README.md, research7/PLAN.md, research7/PLAN_7B.md, research7/TEST_SPEC.md, research7/ORCHESTRATION.md, research7/MERGE_PROTOCOL.md, research7/routing_profiles.json, plus AGENTS.md. Original research7 is a planning package; no research7 runtime exists yet.

The original user instruction is preserved: do not run experiments, simulator worlds, exact-model solvers, synthetic phase tests, training, benchmark/confirmation, or provider/API calls as workload. Implement bounded P0/P1 code and setup scaffolding only. Static syntax, schema, hash/manifest and read-only hardware/dependency inspection are permitted; do not claim phase tests passed. Actual delegation through available collaboration tools is allowed under the routing/slot contract, but do not add direct provider calls to scripts or launch simulations.

Focus this branch on coordinator registry/registration scaffolding, durable recorder and runtime interfaces. Identify absent modules and interfaces first; produce a concrete bounded implementation backlog. Preserve all copied prior-round/root sources, public data and existing R7 planning files. Create new branch-owned files under research7/ and future result paths under results/research7/<program>/7b/. Use immutable source hashes from ../BUNDLE_MANIFEST.json. Do not create a run.sh that invokes a nonexistent module or silently reuse R6 as the R7 runner.

Before each delegated task, fill concrete input paths/hashes, exclusive file ownership, compute allowance, named live independent reviewer and provider/model/effort in the work-order template. Root counts among four global active slots; at most three children and no nested pools. Keep one independent science critic engaged, with developer/reviewer separation. Use explicit Codex models/efforts and clean contexts, or validate exposed alternative-provider schema; no silent substitution. Stop at setup/implementation delivery and report unexecuted tests plus runtime blockers. Do not activate later phases merely because their work orders are included.

Coordinator alone certifies freshness and allocates seeds after full historical/external archives are audited. Included R6 inventories and analysis are evidence, not certification of R7 reservations. Do not generate any listed seed. Send transfer bundles using research7/MERGE_PROTOCOL.md with separate owned paths, every attempt/status and original source digest; never overlay the other host or average machine means. Report files changed, static checks, omissions, dependency/hardware limitations and next authorization needed.
```

The copyable prompt authorizes implementation work on the target agent, while keeping empirical execution blocked. All phase limits/configuration values remain inert until a later explicit execution instruction and independent registration review.
