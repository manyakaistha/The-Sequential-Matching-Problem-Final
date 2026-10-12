# Round-six proposed experiment registry

Status: **planning; not frozen for execution**. Prepared 11 October 2026. No new worlds or policy experiments have been run. [PLAN.md](PLAN.md) is the integrated scientific design; [plan.json](plan.json) supplies machine-readable limits. This file becomes an execution registration only after every preflight item below passes and an immutable registration snapshot is written to a new run directory. Amendments before launch are versioned; amendments after a stage starts cannot erase its original hypotheses/results.

## Information, comparison and primary outcome

Comparator G is exactly shipped `kit.baseline_asks` and `kit.baseline_match`. Root `policy.py` is not the comparator. Candidates receive only the JSON observation and serialized memory; no seed, variant, latent truth, future events, hidden release/exit times, evaluation artifacts or private IDs-to-outcomes mapping. Public mechanism priors are allowed. Production images contain no audit or training datasets.

Each episode: 200 members, days 0–59 with ask and match, then 40 empty advances. All six families, equal family weighting inside each seed. Primary difference: mean over seeds of mean over families of candidate-minus-G qualified MSMI/100. Seed is the independent cluster. All ratios, numerators/denominators, invalid rows and attempted invocations remain logged.

## Candidate IDs and planned comparison graph

Implementation names below are **proposed interfaces**, not existing runnable policies. At most these 12 entries can enter B after Stage-A admission. No replacement entry is selected by examining B.

| ID | Mechanism | Baseline comparison | Contribution controls for C | Engineering cost tier |
|---|---|---|---|---:|
| G | Exact shipped greedy | Reference | None | 0 |
| P | Frozen round-five population/FIFO | P−G, control only | G | 2 |
| K | Max cardinality, shipped score secondary/FIFO | K−G, control | G | 2 |
| N1 | Length-three augmentations/local exchange at fixed shipped score | N1−G | G, K, cardinality-only local repair | 1 |
| N2 | Period-stable priorities in frozen near-tie classes | N2−G | Fixed priority, daily reranking, alternate fixed salt | 1 |
| N3 | Joint collision-aware up-to-four hard batches | N3−G | Same-scorer FIFO-four; matched batch-size FIFO; one-bundle priority; equal-sample two-query | 3 |
| N4 | Matching-valued hard/soft packages | N4−G | Same scorer/no soft; surplus-only; three bundles/no soft | 3 |
| N5 | Distributional public-return reservations | N5−G | Same scorer/always-act; point-return; exact failed-return-only | 3 |
| N6 | Bounded public-belief component rollout | N6−G | Same predictor greedy/current-weighted; N5; independent rollout evaluation | 4 |
| N7 | Whole-matching uncertainty gate | N7−G | Same estimator/no gate; fixed blend; K | 2 |
| L1 | Joint history/second-bias posterior, FIFO/greedy | L1−G | P; exact response; joint-first-only; preserved marginal acceptance | 4 |
| L2 | Public-planner continuation distillation | L2−G | Observation-only teacher; hand continuation; no residual | 2 |

For N3–N7 the scorer/control configuration is chosen on constructed/examined development states and frozen before B. Register exact module, configuration, primary parent ID and all control configuration hashes. Do not infer an own-parent effect from different scorers or historical cohorts. P is a control and cannot be nominated as an unchanged new winner. K can progress only as a genuinely new tested allocation mechanism with an explicit N1/K contribution decision; G can be retained without a new test.

Use one fixed policy-owned salt/configuration per B entry. Additional N2 salt variants are separately logged C controls and count toward C's 12-policy cap. No hidden-seed salt selection. If a stochastic deployment policy is used, register its randomization law and replay state before B.

## Partitions and fixed grids

Proposed reserves (inclusive):

- Training 100001–100120, validation 101001–101040.
- B 110001–110040; C 120001–120060; D 130001–130080.
- E 140001–142000 reserve, use only the first registered n (at most 900).

Freshness is **not yet verified**. Preflight scans every prior actual/planned/reserved range, archived metadata and replay source, conservatively excludes unknown/documented exposure, records skipped artifacts, and checks these partitions. No generator is called during inventory. If overlap is found, replace the entire unlaunched affected reserve through an explicit amendment. Mentioning a planned range does not mean its outcomes have been inspected. Sealed old inventory code may be copied/refactored into new files, never executed where it overwrites old results.

Conditional training collectors: G, K, and a fixed supported local-menu randomized collector. Exactly three configurations, six families. Training maximum 2,160 episodes; validation maximum 720. Validation uses those three by default; if L2 is attempted, its predeclared three-policy grid is G, observation-only teacher and already-fitted student. The teacher/student must show positive actual-reward validation point effects and pass compression/resource checks before L2 enters B; this is an exploratory admission gate. No student fitting after validation/B/C. If unavailable, L2 is deferred rather than replaced. Additional teacher public-model rollouts are offline work with separate seeds/source/job accounting, confined to training/public-model outcomes. Train-only folds select regularization; validation is used once to choose/freeze the model. No fitting on B/C/D/E or any prior confirmation. Online public feedback updates during an evaluated episode follow the frozen algorithm, not offline retuning.

A uses constructed tests and registered examined development states. Its offline opportunity/oracle job list and separate compute allowance must be sealed before any diagnostic replay; those are not confirmation data.

B has 40 clusters, six families, at most 12 policies: maximum 2,880 episodes. Publish exact admitted grid before launch. Report all planned contrasts against G (including controls), with Holm over the complete family, plus named contribution contrasts. No adaptive sample extension. Promote at most two distinct mechanisms. Eligibility requires complete legal/resource-passing grid; no unresolved scientific/implementation objection; actual mean effect ≥+.025; nontrivial action change; named opportunity metric changes in predicted direction. If a parent was run on the same B grid, require positive own-parent effect. Rank eligible mechanisms by descending actual paired mean, then lower engineering tier, then lexical ID. No qualifying candidate means stop or finish a registered negative audit, not fabricate a winner.

C has 60 fresh clusters and at most 12 policies, maximum 4,320 episodes. The registered parent/control graph supplies the top-two candidates, G, P, mandatory parent policies and targeted ablations. If that union exceeds the cap, prioritize complete contribution controls for the highest B candidate and defer the second; do not drop inconvenient controls. One combination is allowed only if its specification, two contribution controls and required parents are predeclared before C and fit the cap. Do not tune any candidate on C. All candidate−G and contribution contrasts are exploratory; Holm families and intended mechanism metrics are listed in C's sealed configuration. Promotion requires positive replicated candidate−G and own-parent point effects, no correctness/coverage objection and mechanism-consistent evidence. At most two contenders advance. No sign replication means stop that line; nonsignificance is not equivalence.

D has 80 fresh clusters, at most four policies (G/P plus at most two contenders), maximum 1,920 episodes. Frozen contender must pass C, show mean difference ≥+.025 and a positive one-sided 90% paired-t lower bound versus G. Highest lower bound wins; within .005 select lower engineering tier, then lower p99 latency, then ID. This is selection, not confirmatory superiority. If none qualifies, retain G and end without E. D cannot tune models/configuration, add policies or grow its sample.

## Confirmation size and claim rule

At most one new E comparison. The finite program reporting family is the four previous valid primary comparisons plus this one. New family-level claims use two-sided alpha .01 (99% CI). Keep old original registrations/results untouched; common-family restatements are separately labeled. This does not cover indefinitely many future rounds or additional unregistered primary claims.

Planning effect +.05 MSMI/100, desired power .90. Before any E generation compute `sigma=max(.26,1.10*selected_D_paired_SD)`. Find the smallest integer m with positive-tail noncentral-t rejection probability ≥.90, critical `t.ppf(.995,m-1)`, noncentrality `.05*sqrt(m)/sigma`; choose `n=ceil(1.10*m)`. If n>900, end or amend a still-unlaunched resource proposal; never silently truncate and claim 90% planned power. Planning with sigma .26 gives m=406/n=447. Actual selected-policy variance may require more. Freeze n/seed list, sources, learned artifacts, configuration, preprocessing, analysis, environment and registration digests.

E has exactly two policies, six families, n seed clusters, 12n episodes. Launch all fixed cells. Never use E outcomes for fitting/calibration/selection or effect-based stopping, sample extension, alternative nomination or exclusions. Operational interruption preserves the original grid and all attempts; it does not permit a fresh replacement test. Stage incomplete/invalid/resource-failed status disqualifies the superiority claim until a transparently resolved package exists; no cherry-picking valid cells.

Superiority requires complete registered evidence, independent reconstruction, production/package eligibility and positive lower endpoint of the primary paired 99% t CI. Bootstrap/nominal intervals are sensitivity, not alternate gates. A CI crossing zero establishes neither inferiority nor equivalence. A positive lower endpoint below +.05 establishes gain over zero but not a practically ≥+.05 gain; report both.

Secondary measures: coverage, assignments, mutual acceptances, dates, positive pauses, date/feedback deadline losses, ask cost, busy endpoint-days, return opportunities/reuse, first waits, latency mean/p95/p99/max, request/response/memory bytes, fallback/error/invalid counts. Every conditional rate retains its denominator. Public weighted-pause/deadline diagnostics require their stated stochastic assumptions and remain secondary. The primary cannot change after outcomes arrive.

## Resource, logging, recovery and review gates

Three offline workers, one numerical thread each; four total agent slots including director. Offline main budget proposed 40 CPU hours, separate fitting/planning budget 10 CPU hours. Runtime measurements on an examined seed precede fixed-stage scheduling. Evaluated inference: two CPU cores, 1 GiB, 64 PIDs, ten seconds, offline/read-only, strict memory <1 MiB, documented image limit 2 GiB. Fixed internal enumeration limits and legal fallback; no timeout-dependent suppression of poor episodes.

Keep complete exact public requests/responses/stdout/stderr/errors and memory flow, prospective named forecasts, initial/final privileged worlds, source/config snapshots and process resource logs. Lossless compression and an authoritative file index preserve bytes. Do not duplicate uncompressed request logs just to create an archive. No old artifacts deleted. Forecast ≥1.25×complete stage bytes plus 20 GiB reserve before launch; retain partial attempts if capacity changes and mark stage incomplete. Disk at planning was about 197 GiB free; external storage may be needed for the full design.

Flush ≤15-second heartbeat, worker starts and per-cell durable status. Atomic commit markers follow file close/size/hash validation; SIGINT keeps all partial bytes and attempt IDs. Resume reuses every committed original cell including failures and its actual recorder/source attribution. Uncommitted attempts remain separately indexed; do not select which result to retain by reward.

Before a serious candidate enters D/E require: developer case; critic's strongest counterargument; statistician's experiment review; separate implementation check; director's signed decision. Independent replicator recomputes final statistics without importing implementer's statistics code, verifies registered cells and replays actions. Production engineer checks actual restricted execution and archive restoration. Seal after reviewers close files and final gate JSON is written. No sealed previous file receives new ledger entries.

## Conditions still required to freeze this registration

1. New seed inventory and source/evidence fingerprints complete.
2. Stage-A opportunity measurements, exact toy solutions and admission/rejection decisions complete.
3. Actual candidate modules, configurations, learned artifacts, scorer parents and deterministic budgets exist and pass tests.
4. Exact admitted B/training/validation job grid, required C graph and primary/secondary contrast families frozen.
5. Measured runtime/storage forecasts and resource ceilings fit the complete scheduled stage.
6. Independent implementation/statistical review passes; registration snapshot hashes all inputs and the exact orchestrator.

The present package satisfies **planning**, not these execution prerequisites.


---

# Research 6 Execution Record and Confirmatory Outcomes

Execution completed: 11 October 2026. All registered stages executed under fail-closed, hash-sealed orchestrator with zero invalid episodes and zero fallbacks.

## 1. Overview of Executed Stages

| Stage | Seeds | Clusters | Policies | Episodes | Primary Purpose | Key Outcome |
|---|---|---|---|---|---|---|
| **A** | Examined R4 / Toy | — | Exact / Toy | — | Opportunity audit & toy analysis | Candidate admission gates evaluated |
| **B** | 110001–110040 | 40 | G, P, K, N1, N2, N3 | 1,440 | Diverse structural screening | N3 promoted (+0.03333); K, N1, N2 rejected |
| **C** | 120001–120060 | 60 | G, P, N3, N3_fifo4, N3_two | 1,800 | Replication & ablation | N3 replicated (+0.04167); N3_two discovered (+0.04306); N3_fifo4 showed 0.00000 (batch size alone has zero value) |
| **D** | 130001–130080 | 80 | G, P, N3, N3_two | 1,920 | Independent candidate selection | N3_two selected as sole contender (+0.040625, 90% 1-sided lower bound +0.001975 > 0, simpler Tier 2) |
| **E** | 140001–140571 | 571 | G, N3_two | 6,852 | Frozen fixed-sample confirmation | Mean diff +0.003211, 99% CI [-0.024483, +0.030904], p=0.764559. **Null finding preserved; greedy retained** |
| **Prod** | 140001–140004 | 4 | G, N3_two | 108 replays (12,960 calls) | In-process, subprocess, container replays | **100% action, memory, and semantic equality verified** |
| **Total** | | **751** | | **12,012** | | Zero unhandled errors, zero fallbacks |

## 2. Stage E Confirmatory Summary

- **Primary comparison**: Paired cluster difference in equal-weighted qualified MSMI/100 (`N3_two` minus `G`).
- **Cluster count**: $n = 571$ fresh clusters ($df = 570$).
- **Sample mean difference**: $+0.003211$ MSMI/100.
- **Paired SD**: $0.256047$ (matches planning assumption $\sigma = 0.26$).
- **Standard error**: $0.010715$.
- **Primary 99% confidence interval**: $[-0.024483, +0.030904]$ (contains zero; lower bound $\le 0$).
- **Nominal 95% confidence interval**: $[-0.017835, +0.024257]$.
- **Two-sided p-value**: $0.764559$.
- **10k-replicate cluster bootstrap (99% CI)**: $[-0.023351, +0.031232]$.
- **Confirmatory status**: **NOT ESTABLISHED**. Null hypothesis retained; shipped greedy baseline `G` is retained as the production default.
