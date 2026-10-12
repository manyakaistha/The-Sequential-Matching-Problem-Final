# Plan 7a: smaller/slower machine

## Mission and boundaries

Make the research reliable and inexpensive to coordinate: build independent evidence, exact small tests, public-only light policies, merge checks and statistical reconstruction. This machine is not asked to train large models or run the main candidate tournament. It contributes a small pilot and can later contribute a few whole confirmation clusters if the frozen candidate is deployable here. Its pilot is development evidence, never independent confirmation.

Read README, PLAN, EVIDENCE_REVIEW, TEST_SPEC, ORCHESTRATION and MERGE_PROTOCOL. Transfer actual source bytes/assets, not just a Git branch: current repository contains untracked research artifacts. Register `host_id=small-01` later with OS/architecture, Python/lock digest, cores/RAM/free disk and exact package digest. No assumptions about this machine's hardware beyond the limits below.

Default ceiling: one simulation process and one numerical thread; working RSS<=2 GiB; new output<=8 GiB; >=4 GiB free reserve; total<=6CPU-hours for all7a work. If hardware cannot support these, reduce concurrency and task scope before execution, never silently drop rows. The global coordinator owns the four-agent and three-simulation-process limits across both hosts. The small-machine director session counts as a slot; normally it acts as one worker under the Mac coordinator.

## A0: receive, verify and inventory (<=30 CPU-minutes)

**Entry.** User later authorizes7a execution; coordinator issues immutable work orders and a source package. **Workers.** Evidence reader Flash-Lite/Luna low or medium; independent critic Pro/Sol high owns conclusions. **Exclusive outputs.** `results/research7/<program>/7a/A0/` and `research7/reviews/7a_inventory.md`; no writes to old rounds/shared registry.

1. Recompute every package path/hash/size. Check no missing imported model assets, external editable dependency, absolute path, symlink escape or untracked file omitted by Git export.
2. Extract all R6 stage summaries/analysis and report tables without changing files; compare quoted numeric means/CIs/counts to raw authoritative analysis. Treat transcript repetitions as one evidence source.
3. Enumerate old seed uses/reservations from all rounds and copied archives; retain parser coverage, unparseable files and external-machine seed declarations. Submit inventory contribution to coordinator; do not allocate new seed IDs locally.
4. Detect routing incompatibilities. `research6/agent_router.py` currently emits Antigravity names and an extra `subagent_type`; it is not a valid direct Codex spawn adapter. Use the new provider-specific contract later, leaving R6 untouched.
5. Create capability record from read-only hardware/dependency inspection; no benchmark worlds yet. Declare missing Docker unsupported for7a if absent;7b owns mandatory restricted-container tests.

**Tests.** T01 package closure, T21 hostile archive, T22 routing schema, T23 seed scan. **Exit.** Independent reviewer agrees all sources and omissions are named; coordinator resolves freshness/route conflicts. A checksum match alone is not independent scientific validation.

## A1: independent exact models and metric checker (<=90 CPU-minutes)

**Entry.** Common observation/metric definitions frozen. **Developer/reviewer.** Separate implementation agent and theory reviewer; do not let the policy developer approve its own exact checker. **Files.** Future `research7/exact_independent/` and `research7/metrics_independent.py`; owns no main planner code.

Implement vertex-recursive enumeration and rational history-tree dynamic programming from a standalone reduced-model schema, not by importing R6/R7 developer solvers. Support hidden-state branches merged by equal observable history, nonadaptive ask batches, post-answer matching, busy/pause/dyad mask and scheduled future reward booked once. This is a toy model, not the official simulator.

Run T02-T10: static four-node trap, downstream delay reversal, future query complement (scaled plus real-budget embedding), reuse/dyad exhaustion, nonseparable continuation, price invariance, posterior response history, last-day/full-follow-up and nonanticipation. Expected rational answers are specified in TEST_SPEC. Cap each small case<=6 actors/3 opportunity epochs and total enumerated states<=100,000/case; report skipped cases without calling them verified. A1's analysis is exact only for the registered reduced model. Enumerate64 labelled four-vertex simple graphs and odd cycles3/5/7 for static matching legality.

Write independent metric reconstruction from public introduction/feedback logs: assignment-relative date<=30, date-relative second response<=3, exactly two on-time Yes, one pair reward, arrived-by59 denominator, unique coverage. Include late-positive pause without qualified reward and nonmutual/canceled/missing/late events. No terminal truth is necessary to count released outcomes after full follow-up.

**Exit.** All rational values/actions/tie sets match a separately developed solver; no hidden branch uses unavailable knowledge; denominator/qualification cases agree. A mismatch blocks dependent policy work; send the smallest counterexample to director for one escalation.

## A2: light policy modules and read-only tests (<=60 CPU-minutes)

**Entry.** Work order specifies one module, fixed formula and named reviewer. **Scope.** Q1 and H1 may be implemented on7a; A1/A2 only after frozen assets/solver dependencies arrive from7b. Assignment files are exclusive under `research7/policies/`; no shared registry edits. Implementation Sol/Flash medium, separate implementation review same tier; science critic remains stronger.

- Q1 implements deterministic possible-edge hard batches with no sampled hidden values.
- H1 implements mature public actor first-Yes history, deduplication, Beta shrinkage and episode reset.
- A1 receives locked static scorer and bounded general-graph allocation interface; compare to score-greedy parent.
- A2 receives frozen ensemble and evaluates complete matching differences; does not train local variants.

Use constructed public JSON fixtures with empty pools, all declined, no hard known values, False values, known contradiction+missing, busy actors, exhausted dyads, dense feasible graph and mixed hard/soft budget. Run T11-T16. Request/response/memory must fit1 MiB; internal memory target<=64KiB for H1,<=256KiB for all light modules. Exact fields/times are preserved.

Emit code/test/dependency hashes and developer case; reviewer submits its own report without editing implementation. If module requires fitting, queue it for7b; do not widen this task into local training.

## A3: lossless transfer and failure-injection tests (<=45 CPU-minutes)

Use tiny **synthetic log files**, not new official worlds, to implement/verify the independent merger and archive reader. Own future `research7/merge_independent.py`, schema fixtures and `research7/reviews/merge_review.md`. Run T17/T20/T21/T24-T27.

Inject byte corruption, missing segment, truncated compressed chunk, duplicate transport file, same cell with different action digest, invalid committed row, stale lease, missing policy/family, extra unknown cell, dependency mismatch, wrong N, invocation119/121, delayed retry and late duplicate commit. A committed invalid result must remain visible and disqualifying. Use disjoint path prefixes and source snapshot IDs. Round-trip lossless request deltas must reconstruct original wire bytes, including memory and ordering.

**Exit.** Merge fails closed on scientific conflict/incompleteness, deduplicates only equivalent transport evidence, retains all attempts and validates expected exact grid. This unlocks7b runner tests, not policy superiority.

## A4: light pilot, proposed 12 clusters/360 episodes (<=60 CPU-minutes)

**Entry.** Future execution registration has freshness audit, exact seeds/configs/assets, reviews, preflight parity and full-phase resource forecast. Proposed reservation710001-710012; do not generate before certification. Freeze G,Q1,H1,A1,A2 exactly; an inadmissible arm remains absent, reducing cells. Every evaluated seed receives all six families and all admitted pilot arms on this host.

One worker; fixed thread env `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1`. Full60+40 horizon,120 calls/episode, lossless logs/all attempts. No command is provided as currently runnable; coordinator later builds reviewed `research7 run --registration ... --shard ...` implementation.

Measure validity, full-action disagreement, query costs, history reuse, coverage, funnel, recorder bytes and CPU/RSS. Report paired12-cluster means/CIs as explicitly noisy development diagnostics. Do not retain a pilot winner as E contender without P3/P4/P5; do not combine pilot rows with Mac P3 rows or treat360 episodes as360 independent observations. Any tuning prompted by this pilot must finish and change config before the P3 freeze.

CPU guard stops scheduling before forecast<=60min allocation is exceeded; incomplete pilot has no reward verdict. Without full logs/parity it cannot be used for comparisons. A4 can be omitted for resource limits; independent constructed/test work remains useful, and the main P3 grid still owns promotion.

## A5: ongoing independent analysis and portability (<=45 CPU-minutes)

As each completed Mac phase bundle arrives, verify raw counts, expected grid, hashes, attempt statuses and phase transitions with independently written code. Reconstruct seed-cluster means, all declared contrasts, exploratory Holm summaries, influence and family/service diagnostics. Use only completed public development phase data; during E receive health counts/errors only until global closure.

Run ordered action/memory replay on predeclared already examined public requests. Make sure byte-exact memory comparisons and semantic pair comparisons are not confused. Exact differing score ties may reflect stable opaque-ID order; route non-tie divergence to developer. Floating model assets must produce identical quantized actions across CPU architectures. If parity fails,7a cannot supply interchangeable E episodes until a corrected pre-E version is frozen.

If selected candidate is sufficiently light, coordinator may issue up to24 complete E seed clusters to7a **before any E outcome is inspected**. Small host estimates remaining CPU/disk and may decline the entire shard before generation. Those clusters are part of global n, not extra samples. Mac reclaims revoked unstarted/missing leases without changing seeds/configs.7a does not generate E worlds merely to benchmark speed. A previously examined parity cluster is used instead.

## A6: final merge audit/handoff (<=30 CPU-minutes)

Provide `7a_bundle_manifest.json` containing experiment/phase registration hashes, package digest, host capabilities, owned paths, row/artifact counts/bytes, completed/incomplete cell lists, every attempt state, resource totals and independent reviews. Use portable relative paths; include prior source package reference and public-only policy assets, not host-private worlds in inference directories. Preserve any privileged audit files in explicitly restricted host bundle namespaces.

Export one immutable archive and file index; test restoration in an empty directory. Final handoff includes every negative test/candidate, arithmetic output, pilot results, deviation and unresolved contradiction. Future merge uses MERGE_PROTOCOL; do not overwrite7b files with7a copies or merge metrics by averaging machine means.

## Work that runs independently of7b

A0 evidence/source scan, A1 toy/metric checks, A3 synthetic merge failure tests and reviewer preparation can run while7b implements recorder/models. A2 requires ownership locks; A4 requires common freeze, seeds and parity; optional E requires selected asset freeze. A5/P7 await sealed completed phase data. If Mac never finds a contender,7a still delivers an independent null-result audit.

## Small-machine stop/deferral rules

No simulator process if measured available RAM or disk reserve is insufficient. No full solver over six-actor dynamic cases beyond state cap. No GPU, large tree ensemble training or dense online rollout. Errors block the dependent phase; no hidden sample deletion, same-model self-review or parameter search to manufacture a gain. Ask the director for a specific amended work order once, with smallest failing fixture, implicated files and requested routing. Keep the output even when the assignment fails.
