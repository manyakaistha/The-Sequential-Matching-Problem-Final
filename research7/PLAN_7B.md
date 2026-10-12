# Plan 7b: M4 Mac, heavy research and confirmation

## Mission/resources

Own public-model development, coupled planner implementation, complete research funnel, fixed multi-baseline confirmation and restricted production checks. Coordinate7a by immutable work orders. Host observed during planning: Apple M4 Mac mini,10 cores,16 GiB RAM, roughly173 GiB free on project APFS volume. Recheck before execution; these observations are not a capacity guarantee.

Default2 simulation workers and one numerical thread per worker; maximum3 globally when7a idle. Stay below10 GiB combined working RSS, retain OS headroom, stop increases on swap growth. New R7 output cap100 GiB; >=30 GiB free reserve; training assets and archives count. Proposed overall7b cap160 simulation/test CPU-hours plus24 fitting CPU-hours. All attempts count. Each phase forecast must fit both its cap and remaining overall budget; gate rejection reduces spending. Do not launch all phases just because the worst-case count is listed.

| Phase | Simulation/test CPU ceiling | Fit CPU ceiling | Episode cap |
|---|---:|---:|---:|
| B0 source/registration | 1h |0|0|
| B1 infrastructure/smoke | 4h |0|384|
| B2 public histories/admission | 12h |24h|4,608|
| B3 complete screen | 12h |0|4,608|
| B4 fresh replication/ablations | 18h |0|6,912|
| B5 independent selection/freeze | 18h |0|6,912|
| B6 fixed confirmation | 85h |0|75,600|
| B7 replay/audit/package | 10h |0|No new inferential worlds|

Caps sum160 simulation/test hours+24fit. B6 at its largest75,600 cells requires average<=4.05 CPU-seconds/cell to fit85h, excluding extra operational overhead; R6 averaged~4.31, so maximum n may be resource-inadmissible even for old policies. Reconcile actual forecasts **before E**, with no post-outcome n reductions. If resources prevent adequately powered E, report no confirmation, or pre-E explicit fixed lower-powered amendment. Larger disk/CPU budgets require a reviewed plan amendment before dependent launch.

## B0: freeze semantic and evidence contract

Use source hashes/actual package closure, R6 final artifacts and both team reports. Accept7a inventory contribution; coordinator owns `research7/registry/`, source manifests, seed reservation and decisions. Critic validates source deductions, metric, six references and causal limitations. Write a read-only evidence index with stage n/means/intervals, baseline source locations, abandoned mechanisms and proposals' claimed-vs-verified status.

Freeze implementation/config interface and output schema. Named files to inherit conceptually: R6 recorder/orchestrator/replay, R5 independent verification. Review missing transitive hashes, imported dependencies, denominator and multi-baseline analysis rather than copying unchanged. Audit official random/no-asks behavior in `evaluate.py` and preserve exact deterministic salt/source; do not invent a weaker baseline.

Register proposed source-independent seed namespaces only after whole-repo+external-machine usage closure. Reserved but unrun older seeds stay excluded unless explicitly released. R7 numbers in plan.json remain unverified placeholders. E reserve is never pre-generated/inspected.

**Tests/exit.** T01/T22/T23, required semantics review, routing adapters consistent; no episode launch until B1 work order is registered.

## B1: bounded infrastructure and integration

Implement common legality/public observations, metrics, policy wrapper, transitive source export, durable lossless recorder, registered runner, leases and merger under exclusive work orders. A runner must reject planning JSON status, unverified freshness, unknown policy, missing independent review, wrong hash or inconsistent counts. The validator cannot certify undeveloped runtime behavior.

Log exact request/response wire, memory before/after, action, error/stdout/stderr, deterministic cap/fallback reason, elapsed/CPU/RSS, sequence, source/config/assets and initial/final host-only state. Use reversible deltas and streaming compression only after T17 proves exact reconstruction. Privileged world/state namespaces never mount into policy containers and never join public features. Gzip/zstd choice and compression version are pinned; decompressors include bounded size/hash checks. State/event deltas must preserve field-status/timestamp and memory bytes; canonical semantic equality alone is insufficient for wire replay.

Constructed failure tests do not need official worlds. Run T11-T18/T20-T27. Smoke registration proposed 700001-700004: up to16 arms x6 families x4 clusters=384 episodes, complete horizon, noninferential. Some arms are not yet developed; smoke uses only admitted available arms and records smaller grid. Later developed heavy arms use the same examined smoke worlds for resource/replay checks, not fresh confirmation. Every extra smoke attempt counts in4h cap and storage forecast; the384 distinct-cell cap can be revisited per new config only by predeclared attempt accounting.

Calibration: compare1 vs2 workers on examined smoke requests/worlds; forecast wall/CPU/bytes/RSS for actual policy mix. Fixed work caps, host parity, serialization startup, dense graph and deadline fallback must pass. Raising to3 requires director decision backed by RSS/no-swap/log health and global7a process accounting. If compression cannot meet100 GiB whole-program forecast with1.5x headroom, do not launch training or screen.

## B2: public history/model phase (conditional)

Proposed training720001-720128 and validation721001-721064, disjoint whole seeds. Four collectors: G,R,Q6 and a frozen feasibility-safe exploration collector E0. E0 uses FIFO hard asks; feasible edge ordering based on a declared public policy RNG stream, never generator seed. E0 is a data collector, not an11th screened policy. Record behavior/matching support if exploring, but never claim unbiased sequential OPE solely from approximate marginal pair propensities. Each collector starts empty memory, uses identical worlds within seed/family, full follow-up and complete action-time records.3,072train+1,536validation=4,608 episodes; no extra rows falsely counted as independent worlds.

Features exported to fitting process come from pre-action public snapshots only. Mature event labels joined only by their observed day/window. Preserve multi-stage denominators, late response, canceled date, unqualified positive pause and selection policy. Training/validation worlds and actor IDs are disjoint. Validation predicts selected observations under declared collectors; deployment generalization remains unproved until rollout.

Fit<=12 public model configurations total for H1/L1 direct/funnel/joint families, then select one asset by frozen validation proper-score/tie rule. Max24fit CPU h includes bootstrap ensembles, categorical answer model, lag/exit hazard and student targets. A2 ensemble uses up to8 bootstrap fits **within this12-fit total**, so schedule model-family fits accordingly (e.g.,3 core fits+8 bootstrap+1student=12); if that leaves an unneeded model unfit, defer its candidate. Do not pretend each subsystem independently has12 fits. Offline analytical empirical-Bayes estimates count in fit ledger even if not a model job. Answer distribution and occupancy fitting methods/configs are registered before labels are seen.

Gate H1 reuse counts; gate L1 mature counts/proper scores/calibration; gate Q2 answer prediction; gate D1 public return/arrival fidelity; L2 teacher/student fidelity applies conditionally before P4, after D1 P3 admission; its absence does not block other B2 models. No model admission from AUC alone or lookahead hidden truth. At most one validation calibration asset per chosen model; no multiple rechecks until success. After failure, preserve simpler population constants and narrow claim or leave dependent slots empty.

Public return/exit model: first nonmutual busy boundary8, public date busy boundary D+6, explicit pause absorbs, pending mutual dates condition lag survival. Fit never-return/cause ambiguity explicitly; earlier unavailable state cannot identify true exit. Model arrival pressure from newly visible member counts by arrived_day; condition day/horizon without revealing hidden family. Evaluate proper score/survival at action times and event-time risk sets, not only at completed pairs.

Optional public distillation needs the validated D1 teacher and uses P2 examined states. After D1 passes P3 and its registered positive own-parent contrast, generate student targets and finish its finite-budget fit/validation before P4 freeze, using only P2 examined partitions; never harvest P4 holdout states for training.

**Tests/exit.** T12/T13/T19/T28-T30. Public exports independently audited by7a/critic. Code/assets/configs frozen for P3; disclose failed gates. Skip entire B2 if nonlearned candidates suffice, reducing counts and budget.

## B3: full mechanism screen

Proposed 730001-730048,48 complete clusters, six families, six references+up to10 candidates (L2 conditional may be absent):<=4,608 episodes. Freeze exact admitted grid, comparison graph, models, triggers, resource forecasts and reviewed hypotheses before any world generation.7a pilot is separate development evidence; all P3 comparisons use only this common complete grid.

Run the registered cell queue; coordinator cannot search unnamed variants. Public mechanism diagnostics: affected/eligible opportunities, actual query differences, real feasible revealed edges, selected dyad changes, reuse/pause/remaining partner counts, planner switch/margin/boundary rejection/fallback, forecast probabilities and realized mature funnels. Host-private oracle audits may identify bottlenecks but cannot become policy inputs or rank candidates by privileged predictions.

Apply master P3 rules exactly; keep at most2 distinct mechanism families, no lower-bound winner claim. Reject action-identical duplicates and invalid/resource-failing versions. Abandon high-opportunity but zero reward mechanisms honestly. Critic reviews selection before C grid is drawn. No contender means stop and publish scoped null evidence.

## B4: replication and own-parent/interaction tests

Proposed 740001-740096,96 clusters x6 families x<=12 arms=6,912 episodes. Before this grid, freeze at most2 promoted mechanisms, necessary own-parent controls and at most1 predeclared integrated strategy D2 or permitted combined entry within the10-entry portfolio. L2 may enter its reserved conditional slot only under predeclared teacher/asset rules; cannot appear after D/E failure.

Select C arms under the cap:6 references +2candidates +up to4own-parent/control arms. An integrated strategy requiring3new parents displaces another candidate/control before C freeze. Do not run a factorial search. The change isolated by each comparison must be explicit in a config graph: query controller, reward weights, continuation, history, uncertainty gate or compressed teacher; one intended change at a time.

Mechanistic intervention budgets<=2 CPU h inside18h: on examined P2/P3 states, fix a synthetic/public model and alter downstream lag/return or pause, keeping queries immediate. Separately disable continuation, change terminal rewards vs cardinality and test missed boundary alternatives. A host-only modified simulator needs explicit RNG schema and all comparator reruns; unchanged same seed does not preserve post-delay draw coupling. These diagnostics are not official benchmark observations or causal identification by themselves.

Apply P4 repeat-direction+own-parent rules and family/coverage screens; critic tests alternative explanations such as same actor set, increased ask volume, surrogate optimization, cutoff artifact, trained-on-selected labels or few influential seeds. Freeze up to3D contenders. If none, no D/E.

## B5: selection, production and sample freeze

Proposed 750001-750128,128 clusters x6 families x<=9 arms=6,912 episodes. All6 references plus<=3 contenders. No new model/scorer fit; declared per-episode public updates continue from empty memory. Apply mean+.025, nominal90% lower>0 vsG, family/coverage/validity gates and minimum-panel-bound tie rule in master plan. Publish all candidate comparisons; selection scores are not confirmation.

While independent statistician reconstructs D, production engineer tests selected candidates on predeclared **examined** requests, empty/dense histories and declared runtime modes. At least108complete trajectories for the ultimately frozen candidate across direct48,subprocess48,restricted-container12, cycling the6 families evenly; each trajectory120calls, total12,960 invocations. Replays consume compute/storage but add no independent inference seeds. Select replay trajectories by seed order/mechanism triggers fixed before inspecting favorable outcomes. Require ordered/semantic/memory parity; default deterministic work cap must agree across modes/hosts. A timeout fallback divergence is a failed interchangeability preflight, not silently accepted different policy behavior.

Restricted container uses no network, read-only root, unprivileged user,2CPU/1GiBRAM/64PIDs/10second invocation including startup, request/response/memory<=1 MiB, required inference assets<=2 GiB. Internal asset target32 MiB is stricter for portability. Test malformed/stdout noise, cancellation, isolated import/assets, host-world exclusion and all-child cleanup. Maximum invocation wall must pass actual measurements; p99 alone is insufficient. All assessed episodes must be valid.

Compute n_E from **D variances only**, frozen floor/inflation/effect/alpha/power in STATISTICS, selected single contender and all 6 references. Check resource/disk cap for complete E before accepting n. Exactly n<=1,800; if too high or no credible candidate, stop or explicitly amend a fixed lower-powered design before any E generation. Register stage cells, sources/transitive assets, scorer/tie/memory/updates, exact n, sample-size output, shard leases and reviews. Reviewers sign the freeze; ongoing developers lose E outcome access.

## B6: sealed fixed confirmation

Proposed reserve760001-761800; actual first n certified unused seeds in frozen ordered list. One candidate+six baselines, allsix families,42n episodes. Up to24wholeclusters may be leased to7a before outcomes, after old-request parity and complete forecast. Default all E on7b if candidate too heavy for smaller host.7a contributes independent audit regardless.

Health dashboard exposes remaining cells, errors, invocations, CPU/RSS/free space/log durability only; no MSMI rankings/CIs/pvalues/family summaries. No code/asset/gate/seed changes or repeated contender tries. Operational stop on reserve/CPU/worker failure preserves all attempts and original registration. Infrastructure recovery can complete missing original cells after lease revocation; a committed invalid policy episode is never replaced by successful rerun or alternate seed.

After exact complete grid and independent operational review, release bundle for one primary seed-cluster analysis using simultaneous six-baseline intervals and fixed bootstrap sensitivity. A failed lower bound is an honest completed result. Do not extend into unused reserve, split the best families, pool7a pilot or fit a patch on E.

## B7: independent verification, merging and delivery

Independent replicator on7a reconstructs every primary count, denominator, pairing and confidence bound without importing main analysis functions;7b verifies raw compressed-wire replay/digest and restricted runtime. Merge all shards once under MERGE_PROTOCOL; machine subsets are not separate experiments. Preserve optional E shard conflicts as hard failures until reconciled.

Publish final six-baseline estimates/intervals, primary verdict, allsixfamily/service/funnel/ask/compute results, bootstrap/influence, exact sample rule/assumptions, searched policies and rejected mechanisms, all errors/fallbacks/deviations, source/assets/dependencies/datasets and archive checks. Include no-family-safety/no-universal-greedy proof limits. Close independent objections before final seal; later amendments preserve original evidence. Retain G if no admissible confirmed improvement.
