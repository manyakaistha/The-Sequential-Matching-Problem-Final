# Round-six statistical critique and proposed experiment funnel

Owner: independent critic/statistician; reviewer: director. **Planning only: this is not an executable registration or authorization to generate worlds.** No new seeds, worlds, fitting, policies or episodes were produced. Prior sealed rounds were read without modification. Analytic computation used less than two CPU seconds; allowance 120 seconds. Proposed counts, gates and seed partitions require reconciliation with the director's final candidate list and written registry before execution.

## What the completed evidence actually says

The frozen population_control versus greedy comparison has 430 independent seed clusters, six correlated families, effect +0.0007751938 MSMI/100, paired SD 0.2314037623, and registered 98.75% interval [-0.0272154463, +0.0287658339]. Superiority is not established; the interval excludes the targeted +0.05 for that policy. The earlier favorable point estimate did not replicate. This does not prove all ranking useless, but it strongly argues against another confirmation of unchanged population scoring, another point-estimate-driven winner, or a surrogate endpoint replacing qualified terminal reward.

Selection must allow **greedy itself to win**. An unchanged policy is eligible as a control, not a new serious candidate. Any new population variant must specify which mechanism differs and its parent-policy contrast. Better proper scores, increased positive pauses or reduced runtime alone do not establish higher MSMI. Neither existing confidence intervals nor source hashes establish greedy optimality.

## Finite history and the next confirmation

A clean finite proposal is a five-comparison reporting family: the four existing primary comparisons plus at most one new round-six confirmation. Any new superiority claim about this family uses a common two-sided alpha 0.05/5 = 0.01 and 99% intervals, including newly restated historical claims. Keep every old report and its original rule unchanged, and label any new common-family reanalysis separately. None of the prior tests has an established superiority claim. Bonferroni needs individually valid tests, not independence between tests; it does not repair leakage or optional sample-size increases.

This is not an indefinite lifetime-error guarantee. If the director anticipates further rounds, preregister an alpha-spending scheme now rather than silently growing finite families forever. Retaining the old four-test .05 family while independently treating every new round as another .05 family provides no .05 program-wide guarantee. One confirmation can test the independently selected policy versus greedy; additional primary controls in confirmation would need a larger family or a hierarchical prespecified test. Development parent contrasts remain exploratory.

Primary estimand remains mean episode MSMI/100 over six equally weighted families within seed, then mean paired differences over seeds. Whole seeds—not assignments, actors or family episodes—are the independent sampling units. Report paired t intervals and a fixed-RNG whole-seed bootstrap sensitivity. Permutation/sign-flip tests are not automatically exact: policy labels were not randomized, and symmetry of differences is an additional assumption. No scenario switch, proxy switch, deadline reweighting or failed-cell deletion after observing results.

## Actual-reward power and cost

Proposed practical planning target is +0.05 MSMI/100. A smaller +0.025 target may be scientifically valuable, but it is expensive and should not be implicitly promised by a small screen. Power below is the positive-tail rejection probability of a paired t statistic under independent normal seed differences, with critical value t(.995,n−1) and noncentrality effect×sqrt(n)/SD. Search the smallest n achieving 90%, then apply a prespecified 10% inflation. These are exact calculations for the assumed normal model, not guaranteed simulator power. Rejection establishes gain over zero; it does not establish gain above the planning effect when truth equals that effect.

| Paired seed SD | True planning gain | Minimum n at 90% | Fixed n with 10% inflation | Two-policy episodes |
|---:|---:|---:|---:|---:|
| .2314037623 (observed old contrast) | .025 | 1279 | 1407 | 16884 |
| .2314037623 | .05 | 323 | 356 | 4272 |
| .2314037623 | .10 | 84 | 93 | 1116 |
| .26 (conservative starting assumption) | .025 | 1613 | 1775 | 21300 |
| .26 | .05 | 406 | 447 | 5364 |
| .26 | .10 | 104 | 115 | 1380 |
| .35 (higher action-divergence sensitivity) | .025 | 2920 | 3213 | 38556 |
| .35 | .05 | 733 | 807 | 9684 |
| .35 | .10 | 186 | 205 | 2460 |

Compute uses existing SciPy nct/t quantiles; no simulation is required. The original population difference SD cannot be assumed for a radically different query/planning policy. Before confirmation, estimate the selected candidate's actual-reward paired SD on development/selection only. Use a written formula fixed in advance, e.g. planning SD = max(.26, 1.10×observed selected-contrast SD), compute fixed n using the +.05 target/alpha .01, then inflate 10%. This empirical safety factor is a heuristic, not a guaranteed variance bound. If n exceeds a prespecified budget (suggested 900 clusters), stop or report a knowingly lower-powered fixed test; do not shrink the target or variance assumption after seeing confirmation. Freeze n before any confirmation world is generated.

At 3.2 CPU seconds per simple episode, .26 SD confirmation costs about 18.9/4.77/1.23 CPU hours for +.025/.05/.10 respectively. Round-five final run alone measured 16,410 child CPU seconds for its remaining 5,042 episodes, approximately 3.25 seconds each; the final wall was 5,658 seconds. Recovery, audit, archive and replay costs are additional. New planners can multiply inference cost substantially. These estimates are not hard resource guarantees or exact total-task CPU.

## Bounded proposed stages

Do not screen all twelve proposals simultaneously. Select at most six distinct mechanisms plus two controls initially. Avoid a hyperparameter grid disguised as six mechanisms.

| Stage | Proposed independent clusters | Maximum policies | Maximum episodes | Question |
|---|---:|---:|---:|---|
| A correctness | Existing/tiny specified examples only | All proposed | No fresh reward grid | Are actions legal; does exact toy behavior match the claimed reduction? |
| B diverse screen | 40 | 8, including greedy and frozen population | 1920 | Which new mechanisms change decisions and plausibly improve actual reward? |
| C focused ablation | 48 fresh | 5, including required parent/control | 1440 | Does the named mechanism survive replication and its own architecture control? |
| D selection | 64 untouched | 3, including greedy | 1152 | Is any frozen contender sufficiently credible to spend on confirmation? |
| E confirmation | Fixed variance-derived n; illustrative447 | 2 | Illustrative5364 | Does selected candidate establish gain on actual qualified reward? |

Upper total illustrative episodes are 9,876 before replays/production. At 3.2 seconds per episode this is about 8.8 CPU hours; three research workers imply an ideal lower-bound wall near 2.9 hours, not a promised wall time. A 5× planner makes inference dominate. Pilot runtime on existing verification seeds can determine an offline cost ceiling without consuming fresh selection/confirmation seeds. Use at most three simulation workers while four agents are active; evaluated inference remains at most two cores/one GiB/64 PIDs/10 seconds.

B is exploratory: report every candidate, seed-cluster effects and simultaneous/Holm-adjusted planned baseline contrasts. Suggested promotion gate: valid/protocol/resource eligible; distinct decisions on a nontrivial fraction of states; mean reward effect at least +.025; at least two informative families; named mechanism metric moving in the predicted direction; no unresolved leakage/correctness objection. Promote at most two candidate mechanisms. These are screening gates, not significance or superiority claims. A larger point estimate is insufficient on its own.

C should use prespecified contribution contrasts against each candidate's own parent, not only greedy. Require overall reward direction to replicate and the intended contribution to be nonnegative; examine occupancy, query displacement and deadline residuals. Drop the mechanism if reward reverses materially or its parent performs as well with less complexity. Do not insist on significance at these sample sizes; conversely, do not call nonsignificance equivalence. Preserve rejected candidates and allow a no-promote outcome.

D selection rule should be fixed before its seeds are opened: among eligible frozen candidates with point effect at least +.025 and a positive one-sided 80% paired-t lower bound, choose the highest lower bound; ties within .005 choose simpler/lower-latency policy. This is a noisy credibility screen, not a confirmatory test or proof of the best policy. Require satisfactory C contribution evidence and correctness review. If none passes, retain greedy and stop the round without E. Do not relax gates, add candidates or extend D until one qualifies. The selected code/configuration/preprocessing and E size must be frozen, hashed and reviewed before E.

## Challenges to proposed structural work

The structural researcher proposes collision-aware verification, public return-calendar scheduling, alternating-path repair, bounded component lookahead, final-day augmentation and balanced reuse. The most credible initial contrasts are collision-aware hard-query batches and fixed-score local matching repair. Their controls must hold score fixed and isolate batch size, endpoint priority and matching cardinality.

For collision batching, include FIFO with the same batch size and timing; otherwise warmup displacement or fewer soft queries can explain apparent gains. A control using collision priority without larger batching separates priority from batch coordination. Known legal constraints can be checked; unknown constraint values and future exits/arrivals cannot be treated as known. Member-ID/profile-generation order can correlate with arrival history, but no seed reconstruction or hidden generator state is admissible.

For local repair, compare constant/cardinality-only repair, population-weighted repair and the same greedy score/order. More introductions are not automatically better, because they consume busy time and endpoint options. An alternating-path result on a current graph does not prove dynamic improvement. For continuation, require exact tiny-model counterexamples and event-calendar validation before a full-simulator planner. An optimistic rollout is not evidence of deployable reward; its uncertainty, missing-feature posterior and shared funnel effects must match public information. Final-day augmentation is a low-headroom control, not a reason to launch another expensive confirmation by itself.

Positive-pause/deadline-integrated scores are secondary diagnostics. The previous abstract action-invariance theorem is scoped to its frozen policies and second-feedback-delay intervention. A new calendar/planner policy may read pending-event presence/timing or global feedback, invalidating that invariance. Do not assume .36×positive pauses is its exact conditional reward or a lower-variance primary endpoint without a fresh proof. Different assignments also change which day/dyad/stage random variables are used; matched seeds are not identical realized funnels for different actions.

## Challenges to proposed model work

The model researcher proposes joint actor nuisance posteriors, public-history regime filtering, shrunk learned residuals, continuation distillation, conservative decision-margin learning and bounded exploration. Implement at most two representatives initially, rather than every paradigm receiving a reward grid.

Joint actor feedback may add useful signal omitted by the old Gaussian approximation, but sparse actor histories and positive-pause retirement are selection mechanisms. Stage-conditional acceptance/second labels are not an IID sample of actors. Likelihoods must integrate shared dyadic effects and unavailable soft features; updating every actor as if labels were independent can manufacture confidence. Identifiability of actor bias versus regime/shared effects should be checked on exact small likelihood examples. Public snapshots must predate the outcome, and no later clarified partner feature may be retroactively attached to its historical assignment.

A regime filter must infer public evidence without scenario labels. A common population regime can be weakly identifiable from sparse selected feedback, and drift breaks stationary pooling. Report posterior uncertainty and compare to an equally regularized stationary mixture. Outcome history used to detect a regime must have arrived by invocation time. Demographic masked prediction alone is not a useful soft-feature signal under the independent generator; unrestricted model-free RL lacks a credible sample budget. Deterministic matching logs offer little action coverage: unsupported IPS/DR/offline-policy causal estimates are not a substitute for randomized or on-policy evaluation.

Predictor audit uses identical prospective examples and held-out seed splits, with terminal/stage log loss, Brier, joint calibration and slices. Favor at least one held-out proper-score improvement with uncertainty and coherent reciprocal probabilities before a learned model is sent to reward screening. This gate establishes prediction evidence only; allocation/query/learning controls must remain fixed in a separate policy reward contrast. Thresholds for conservative gating or exploration are training parameters and must be locked before selection, not tuned to the selection episodes.

## Seeds, records and no-gain stopping

Round-five design's repository inventory blocks 10,339 recorded/planned seeds before its own fresh 90001–90430 range. Prior guard 1–10000 and reserved-but-unrun ranges are not automatically available. No new round-six numerical ranges are allocated by this critique. The director must produce a new read-only inventory covering all prior results, registries, manifests, compressed artifact metadata, replay seeds and planned reserves; explicitly add all90001–90430. The old seed-inventory script writes into sealed research3 and must not be executed in place. Untouched selection/confirmation means never inspected/generated in any earlier analysis, not merely absent from the final episode file. Unrecorded external seed usage remains an acknowledged limit.

Training, development, candidate selection and confirmation get disjoint seed sets. Existing public prior-round logs may be training/development if explicitly relabeled as examined; preserve old claims and never call those seeds fresh again. Hidden truth remains confined to diagnostic oracle audits and cannot enter training/features. Do not use stored qualified outcomes from E for model fitting, calibration, selection or future-information features during E.

Before execution, freeze candidate/config hashes, comparison graph, primary/secondary outcomes, compute/disk ceilings and continuation gates. Retain all raw episode rows, complete public requests/responses/errors, prospective snapshots, action digests, source versions and invocation/resource summaries. Compressed append logs must distinguish completed cells from uncommitted attempts; interrupted gzip bytes and explicit errors remain preserved. Operational recovery reuses every committed original cell, including failures, runs only missing original cells, and needs a documented amendment; never choose between different outcomes or substitute seeds. No universal all-attempt failure-free claim from committed rows alone.

Full request logs and privileged initial/final audit state substantially increase storage. Estimate gzip bytes per episode on existing seeds; allocate disk reserve before each fixed stage, close/verify streams and stop safely at a prespecified capacity guard. Audit-only files must have separate paths and no policy/model read path. An immutable initial world plus frozen simulator supports reconstruction, but source hashes are consistency evidence rather than tamper-proof timestamps. Match initial worlds across policies by canonical digest.

Independent verification must reconstruct all final seed clusters, denominators and statistics without the director's analysis imports, then replay selected policy/greedy in direct/subprocess/restricted-container modes on prespecified already evaluated verification seeds. Verify ordered and semantic actions separately; do not confuse serialized action digest with raw stdout bytes. Secure restoration refuses traversal, unexpected members and destination symlinks; validate archive SHA/size and exact raw file set, not only that listed members exist. Seal only after gate JSON and all reviewer-owned files are closed.

Stop this round if no eligible mechanism survives B/C/D; if the confirmation budget cannot support its declared effect, report the limitation before E; and after the one fixed E sample, report its exact result regardless of significance. Negative evidence is a successful research outcome. None of these gates permits extending samples until greedy is defeated.

## Review of director's larger provisional grid

The director's provisional grid is training120×6×3=2160 episodes; B40×6×16=3840; C60×6×8=2880; D80×6×4=1920; illustrative E447×6×2=5364, plus proposed validation40seeds with its policy count still to be specified. This is at least16,164episodes before validation/replays, about14.4CPUhours at3.2seconds each, with no planner multiplier. It is a proposal, not the smaller alternative grid above. B16 is defensible only if each variant has a distinct registered contribution contrast and the screen has a strict promotion cap. Many nominally different scoring thresholds do not constitute diversity.

At40clusters and old SD.2314, a single effect's standard error is about.0366. Searching14candidate contrasts under a null can readily produce a+.05–.08 exploratory maximum; correlation changes the exact distribution, but not the basic winner's-curse problem. A gate based only on effect≥+.025 is insufficient. Keep at most two promoted mechanisms, retain parent controls in C, require contribution-direction replication and apply the frozen D lower-bound/no-candidate gate. For80Dclusters, the suggested one-sided80%lower>0 gate is only exploratory credibility; it is not a familywise superiority test. The strongest of several searched candidates still needs untouched E.

The provisional numerical partitions training100001–100120, validation101001–101040, B110001–110040, C120001–120060, D130001–130080 and E140001onward with2000reserved clusters must remain explicitly unverified until the new inventory checks them. Reserve does not authorize using all2000or extending until significance. A+.025target atSD.35would require3213inflatedclusters, exceeding that illustrative reserve; either adopt a finite larger reserve before execution or reject that power promise. For the proposed+.05target, E's illustrated447needsSD.26; divergent policies may require a larger predetermined count.

Current director-reported free disk is197GiB, not the older300GBestimate. Before each stage, estimate complete compressed artifact bytes using an already examined seed with the actual recorder, include every request/response/error and prospective state, forecast planned-episode count, then require forecast×1.25+at least20GiBfree reserve. This is a heuristic safety margin, not a storage bound. Stream lossless gzip; avoid duplicating uncompressed archives. If durable closed raw logs and archives both exist, preserve both unless a prior documented archive/restoration policy authorizes moving raw data out of the active workspace. Never silently delete old sealed evidence. A guard breach is operational stopping with preserved partial rows, not a statistical sample-size decision. If the forecast cannot fit, obtain more storage or simplify the predeclared logging/storage layout before running, rather than selectively omit successful or failed requests.

The read proposal `LEARNING_PROPOSALS.md` explicitly rejects unavailable scenario labels, soft demographic guessing, zero-support IPS and privileged teacher training. Those are appropriate constraints. L1/L2's information and headroom gates are essential: an exact posterior can still have no decision value among surviving endpoints. The optional three-policy training cohort supplies more factual labels, not three independent datasets per seed or automatic action coverage for every matching. Whole-seed train/validation folds and prospective snapshots remain mandatory. Cheap L5 robustness variants should not cause uncontrolled threshold searches that inflate B from distinct mechanisms into a tuning sweep.

Analytic power reproduction (SciPy1.18.1 on the reviewer host; no random generator or seed world called):

```python
import math
from scipy.stats import nct, t
for sd in (0.2314037623335451, 0.26, 0.35):
    for effect in (0.025, 0.05, 0.10):
        n = 2
        while nct.sf(t.ppf(0.995, n-1), n-1,
                     effect * math.sqrt(n) / sd) < 0.90:
            n += 1
        print(sd, effect, n, math.ceil(1.10*n))
```

Reviewed evidence: `results/research5/analysis.json`, `design.json` and `compute_summary.json`; `research5/FINAL_REPORT.md`, `EXPERIMENT_REGISTRY.md`, `RESULT_REPLICATION.md`; inherited `research4/PLAN.md` and seed-inventory source; round-six model proposal and direct structural-researcher messages. Numeric historical facts are artifact evidence; power is a model calculation; stage counts/promotion rules and resource margins are proposed design choices; predicted mechanism gains remain unvalidated hypotheses.

## Final proposed-grid resolution and mathematical scope

The director's revised provisional B cap is12policies: three controls (greedy, population and maximum-cardinality) plus local repair, periodic scheduling, bundled queries, decision-changing queries, reservation, component rollout, robust allocation and at most two learning mechanisms. C may retain up to12policies on60clusters to accommodate their own-parent/factorial controls; D retains at most4on80clusters. Optional training120and validation40seeds each use three collectors. This is a reasonable compromise if every contrast is registered and the cap of two promoted mechanisms, strict D/no-E rule and runtime budget remain binding. The smaller-grid objection is preserved: B12does not make noisy point estimates confirmatory, and C12may be costly if planners consume seconds per invocation. Report a single explicit episode/compute budget after deciding whether optional training is needed; optional must mean gated in advance, not switched on because B disappointed.

Read final `STRUCTURAL_PROPOSALS.md` H/L/R/I/P/D specifications and architecture controls. Their explicit exit uncertainty, matched query-batch timing, constant/count versus weighted repairs, exact toy fidelity and terminal-reward gates address the main correctness objections. First-wave H/L remains more credible than combining all six immediately. A planner's robust local objective is a heuristic, not a statistical confidence guarantee.

There are two different deadline statements. Under the intended independent stochastic-stream model, each predictably created introduction's date-on-time/both-eventually-positive indicator K_i is fixed independently of that dyad's own two second-feedback delays. The latter each have3/5chance to meet deadline, so E[qualified_i]=.36E[K_i]. Summing the bounded set of introductions gives E[qualified]=.36E[sum K_i] even when earlier feedback delays influence subsequent actions. This general **expectation identity** is not the stronger frozen-policy conditional Rao–Blackwell identity: with a new planner/global learner, realized K can depend on previous delay draws, so .36K need not equal E[reward|all non-second-delay primitives] and variance reduction is not automatic. Conditioning on a full observed history retains event-presence timing information. The independent-stream and normal-execution assumptions must be stated; privileged PRNG reconstruction is not an admissible policy. Raw qualified reward stays primary, and any proxy contrast is secondary unless explicitly registered with its exact scope before evaluation.
