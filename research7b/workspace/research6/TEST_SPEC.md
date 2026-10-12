# Tests to orchestrate for round six

This is the proposed acceptance-test design. No new algorithm has passed these tests yet. `validate_plan.py` checks the planning arithmetic/links only; it does not run any policy evaluation. A future implementation must turn the cases below into runnable tests and retain failures as evidence.

## A0 — preserve and reconcile

Read old final manifests/reviews; fingerprint the new run's inherited dependencies without rewriting them. Inventory observed, planned, reserved, interrupted and replayed seeds. Never run a legacy utility with a sealed output path. Record both the legacy known metadata exceptions and current bytes separately; no new unexplained exception is accepted.

Verify source facts with focused tests: eleven hard fields, permanent declines, partial incompatibility pruning, a dyad's permanent no-repeat exclusion, endpoint-disjoint matching, reuse after return, ask budget/costs and duplicate `(member,field)` handling. Same-member constraints plus useful soft is legal; two adaptive ask batches on one day and individual hard-field requests are outside the intended protocol. Ensure `False` child values are not treated as missing.

Two requests per action day, 120 total, days 0–59; final day 100 after 40 empty advances. Assert every supported day-59 delayed outcome has matured by day 97. Explicitly test that scheduled events survive exits. Do not use a shortened feedback run as a reward test.

## A1 — exact simplified models

Specify states/actions/transition probabilities in JSON and solve with rational `Fraction` arithmetic. An independent enumerator checks every policy value/Bellman action on held-out instances. Models may expose deterministic future release/arrival information only when explicitly part of that model; evaluated policies do not receive that privileged information.

| Case | Exact construction | Required result |
|---|---|---|
| Complementary verification | No verified endpoints; only AB possible; both A/B require a bundle | Each single bundle adds zero immediate matching value, joint pair adds one; ordinary diminishing returns fails |
| Collision versus distinct partners | Two one-bundle candidates share one partner, edges present independently with probability 4/5; alternative two candidates have distinct partners, each probability 7/10 | Shared batch expected count 24/25 versus distinct 7/5; degree-sum 8/5 versus 7/5 selects wrong batch |
| Local cardinality repair | Four-node path; greedy uses middle edge, outer edges disjoint | Length-three augmentation gives two introductions; reversed high-quality-middle rewards show cardinality is not universally optimal |
| Odd sets | Unit triangle | Degree-only fractional relaxation 3/2; actual matching maximum one; odd-set constraint required |
| Known return reservation | Days 0/1; current AB probability .11, BD .10; C returns on day1 and AC .10; assignments remove their endpoints through horizon | AB value .11; BD then AC value .20; removing future AC reverses preference |
| Soft value versus hard cost | AB value .9 or .1 equally likely; AC .5; reveal AB state | Information raises choice value .5→.7; displacing hard opportunity .25 gives net −.05 |
| Repeat opportunities | Triangle, each unused dyad success .1/retirement; failure returns after eight days; action days 0/8/16 | Expected success 1−.9³=.271; horizon ending before day8 permits only .1; no repeated dyad |
| Nonseparable alternatives | Two current assignments compete with the same future partner alternative | Summing endpoint losses double-counts continuation; joint DP disagrees with node-price reduction |
| Last action day | Existing matching and a legal edge between unmatched endpoints | Adding edge weakly increases reward with full follow-up; shipped G is already maximal, so this alone cannot beat G |
| No usable learning horizon | Single introduction or no-return model | Outcome exploration has no later decision benefit; occupancy cost is charged |

Also reproduce inherited exact waiting/throughput/terminal-penalty counterexamples rather than deleting inconvenient cases. Generate small graph/property sweeps, including odd cycles, empty components and changed horizons. Exact toy wins establish behavior in the toy, not full-simulator superiority.

## A2 — public model fidelity

**Hard completion:** independently check generator-conditioned age-radius, gender subset, zone, structure, smoking/children and schedule distributions. One sampled member realization is shared across all incident hypothetical edges. Existing disclosed fields/statuses remain fixed; declined fields never become verified. Test complementary and collision query subsets. Eight-candidate subsets of size ≤4 total 163; complete-eight graph has 764 matchings.

**Return calendar:** construct public histories for failed introduction (t+8), both first yes with pending date, observed canceled date (D+6), happened date with pending seconds, positive pause, and uncertain exit. Check exact discrete conditioning on no observed date/event yet. Do not deduce a hidden exit from an unavailable flag until every public busy/pause explanation is excluded. Prospective return forecasts predict day/never-return distributions; verify against later public availability, with an ambiguous unavailable category where cause is not identified. Report Brier/log loss, window coverage and remaining-action-horizon slices on identical examples.

**Reciprocal posterior:** exhaustive tiny latent grids independently normalize likelihoods. Test shared dyad effect across all logits, actor response reuse, conditional stage existence, available-actor exact response posterior moments, missing soft integration and known-prior behavior. Compare joint posterior to high-resolution enumeration on constructed histories; quantify errors before choosing a lower-cost approximation. No response flag should update preference yes/no bias. No pending event becomes a negative label. Count each public event exactly once.

**Timing/leakage:** alter future events, later profile disclosures, hidden seed/variant/truth/bias/release fields and audit file paths while holding permitted request bytes fixed; policy response must remain identical. Policy process receives none of those hidden fields to begin with. Historical assignment examples retain their earlier fields; legally disclosed current evidence may update current beliefs, but cannot rewrite the old prediction snapshot.

**Known constants:** date probability .78; feedback qualification 9/25; delayed date tail 671/686; reused response second moments; expected sigmoid versus sigmoid of mean. Check numerical quadrature convergence and rare-logit stability. Calibrated model claims require held-out public labels, not these arithmetic checks alone.

## A3 — policy implementation and production

Every entry has observable-only inputs, bounded history, fixed action/sample limits, a legal fallback and a resource contract. Tests cover empty/no-feasible pools, permanent declines, exhausted budgets, repeated/overlapping dyads, malformed/nonfinite memory, oversized request and serialized memory, pending history, dense graphs/odd cycles, numerous distinct actor histories, pruning and subprocess startup.

Force solver exceptions and **actual clock interruption** during expensive computation; confirm guard cannot be swallowed by a broad exception handler. Test outer timer behavior and fallback legality. Measure parse/startup/output separately from internal compute budget. Use a fixed maximum amount of work for deterministic action semantics, with time guard as safety; do not let optional solver exploration vary silently by machine and claim identical execution.

Run actual evaluator-style restricted containers: two cores, 1 GiB/swap cap, 64 PIDs, read-only root, no egress, unprivileged user/capability limits and documented 2 GiB image ceiling. Probe effective limits and runtime source hashes. Measure wall and CPU, sampled/actual peak RSS scope, mean/p95/p99/max latency, maximum request/stdout/stderr/memory bytes. Memory must be strictly <1 MiB even where evaluator's boundary comparison is weaker. Finite stress results do not establish a universal ten-second guarantee.

Compare direct, new-process and container responses on the same recorded requests. Report separately: unordered matching semantics; ordered ask/pair equality; canonical action digest; literal stdout bytes. Nonidentical JSON formatting is not semantic failure, but different action order must not be hidden if the registered digest requires it.

## B/C — paired policy reward and mechanism tests

Precompute exact job grids and expected cluster counts. Every launched cell records an attempt ID and immutable source/configuration/simulator/recorder/environment hashes. Match initial-world canonical hashes across policies. Aggregate family ratios within seeds; do not pool assignments for reward significance.

For each new policy compare G plus its frozen parent. C includes targeted controls before combinations. Examples: FIFO versus joint batch with identical budget/scorer; same three bundles with/without soft; same predictor with/without local repair; same randomization with learning frozen; joint posterior with second stage disabled; teacher versus distilled policy. Publish every tested contrast and relevant Holm family, including negative results.

Log all intervention triggers: queries considered/chosen, displaced bundle, matching alternatives, posterior score/uncertainty, reservation reason/window, predicted return distribution, rollout candidate count/sample count/termination and fallback reason. Sampling RNG state comes from policy randomness and is replayable, never evaluator seed. Debug artifacts live on host; stdout remains valid protocol.

Mechanism tables retain correct stage denominators. Separate uncertainty from bias, prediction from action changes, current matching value from sequential reward, and arrival/exit/pause/busy causes. Inspect influential/typical trajectories using a deterministic disclosed selection rule. Different dyad/day assignments receive different keyed random streams; do not assert causal mediation from count differences.

## D/E — selection, freeze and independent confirmation

D's no-candidate rule and one-sided 90% selection bound are fixed before D. Freeze exact selected code, preprocessing, model and configurations; compute E n from D variance only through the registry formula. Hash the fixed grid and all sources before any E world. Policy updates are frozen algorithms using public online history, not host refitting.

During E display progress/health but do not run superiority tests for stopping. Complete every cell. Any invalid/fallback/timeout is visible and affects eligibility; do not omit its row. Operational recovery keeps every committed attempt and source attribution and runs only original missing cells. Preserve uncommitted errors/partial gzip bytes, distinguish completed/attempted totals, and refuse outcome-based replacement or a fresh seed sample.

Independent analysis uses standard-library/SciPy arithmetic written separately, without importing director statistics functions. Reconstruct qualified counts from full public traces, score denominators, all seed differences, paired means/SD/t intervals/power parameters and bootstrap from the registered sample. Compare tolerance and publish discrepancies. Coverage/funnel/resource checks cover all committed episodes, not only replay examples.

Predeclare replay grid: G/selected × first two **already completed E** seeds × six families × direct/subprocess =48 replays. They reuse examined outcomes and add no independent confirmation clusters. Actual restricted-container replay on the first completed E seed across all six families and both policies adds12 production episodes. Retain source versions, complete logs and ordered/semantic comparisons. Deviations due to time guards are reported, not silently blessed as equivalent. A separate security/resource stress grid uses constructed/examined requests.

## Full-record and archive acceptance

Save every information category available to the runner: exact public input/output bytes, parsed values, errors/return codes, attempt/cell IDs, memory sequence, timings/resources, source/config/RNG provenance, prospective predictions/actions, initial/final host worlds and public trajectories. Privileged evidence is separate from inference/training access. Unknown unsaved bytes after an interruption remain explicitly unknown; logging cannot reconstruct them by assertion.

Use durable, independently decompressible invocation chunks or an equivalent indexed compressed stream that minimizes crash damage. Preserve chunks written before a crash and raw incomplete buffers; never delete them to make logs look clean. An atomic cell commit follows stream closure and validation. Check 120 successful phase calls for a completed valid episode, causal observation reconstruction, legal actions, final follow-up, metric/digest reconciliation and request/memory bounds. Full audits regenerate observations from initial world and saved actions, not future-aware features fed back into policies.

Archive indexes contain exactly the intended file set with byte lengths/SHA-256; validate archive digests and stream **every member**, including interrupted attempts. Secure restore refuses traversal, unexpected members, duplicates, links/symlink destinations and overwrite of differing bytes. Existing equal files may be reused after verification. Test archive-only restoration, corrupt gzip/CRC, differing files, missing members, root/parent/leaf symlinks and interrupted archives. Lossless compression saves everything; removal of redundant raw copies requires later explicit user authorization.

Final gate is fail-closed: registered grids, frozen hashes, independent statistics, full log audit, replay/production evidence, archive sets, inherited preservation and closed reviews. Write final gate JSON before sealing it in the manifest. Rehash the sealed package independently afterward without modifying it. Report scope and omissions rather than claiming hashes provide tamper-proof historical timestamps.

## Expected orchestrator console

Illustration of a future implementation, **not output from an existing runnable script**:

```text
[preflight] registration <digest> | sources OK | seed inventory OK
[storage] complete-stage forecast 18.4 GiB | free 197 GiB | reserve 20 GiB
[logs] public=results/research6/<run>/public  audit=<run>/privileged
[stage B] 40 seeds × 6 families × 12 policies = 2880 episodes
[worker 1] started pid=...   [worker 2] started pid=...   [worker 3] started pid=...
B [####................] 576/2880 (20.0%) elapsed ... ETA ...
[heartbeat] active=N3/... L1/... G/... committed=576 failed=0 attempts=578
[stage B complete] grid=2880/2880 | see effects.json and decisions.json
[decision] promoted N3,N1 to fixed C controls; exploratory only
```

The example IDs/bytes/promotion are placeholders, not predictions. Startup/status must appear immediately, updates/heartbeat at most 15 seconds apart, with durable terminal and structured logs. Final output gives the exact report/verification paths and the honest eligibility/result. SIGINT prints preserved/resume status without deleting current data.
