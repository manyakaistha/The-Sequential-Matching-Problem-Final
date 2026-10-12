# Round six: finding decision value beyond greedy

Prepared 11 October 2026. **Research design, not an executed experiment.** No new policy episodes, training runs, or confirmation worlds were generated while preparing this package. Prior studies remain unchanged. The detailed test contract is [TEST_SPEC.md](TEST_SPEC.md), the prospective execution conditions are [EXPERIMENT_REGISTRY.md](EXPERIMENT_REGISTRY.md), and team scheduling is [ORCHESTRATION.md](ORCHESTRATION.md).

The goal is a reproducible increase in scenario-balanced qualified MSMI/100 over `kit.baseline_asks` plus `kit.baseline_match`. A policy that merely predicts better, completes more dates, or wins on searched seeds does not satisfy that goal. We will search for legitimate advantages in the public mechanisms and stop if the evidence does not justify another confirmation.

## 1. What the next study must explain

The strongest current result is the round-five fixed 430-seed comparison, not the earlier favorable development estimate:

| Completed comparison | Candidate | Greedy | Paired difference | Registered interval |
|---|---:|---:|---:|---|
| Original extended study, `simple_fifo` | .331250 | .372917 | −.041667 | 95% [−.091068, +.007735] |
| Round three, `clean` | .427083 | .412500 | +.014583 | 95% [−.030536, +.059702] |
| Round four, `population_control` | .370536 | .313988 | +.056548 | Program 98.3333% [−.018553, +.131648] |
| Round five, same frozen population policy | .382171 | .381395 | +.000775 | 98.75% [−.027215, +.028766] |

No comparison establishes superiority. The last interval excludes the planned +.05 gain for that frozen policy. It does not establish equivalence, inferiority, or greedy optimality. The original study completed 2,040 registered main episodes; round five completed 5,160 episodes and exhaustive checks of 619,200 logged calls. Successful verification supports the measurement, not a win.

The original `simple_fifo` assigns the same positive terminal score to every edge; updating its common score cannot improve rankings. Pure FIFO hard queries have the same schedule across the relevant policies. `no_learning_fifo` and `terminal_soft` had exploratory promise but no individual original confirmation. Removing irrelevant fields, public population integration, marginal response learning, simple acceptance shrinkage, static blossom, heuristic occupancy penalties and soft acquisition have already been investigated. They may be controls; repeating them unchanged is not a new contribution. Earlier screens were small and often benefited from favorable deadline marks. The next design spends more effort on causal contrasts and independent selection.

Evidence anchors: [round-five report](../research5/FINAL_REPORT.md), [round-three report](../research3/FINAL_REPORT.md), [round-four report](../research4/FINAL_REPORT.md), [original theory review](../research/FINAL_THEORY_REVIEW.md), and [deadline diagnostic](../research4/DEADLINE_INVARIANCE.md). Round-five interrupted attempts and damaged partial logs remain disclosed; zero failures refers to committed episodes, not all attempts.

## 2. Research thesis and priority order

**The leading hypothesis is that useful headroom lies in the distribution of future legal endpoints, rather than another unconditional dyad probability formula.** This is a hypothesis, not a finding. Population ranking's null result and the scarcity of actor histories motivate testing it; neither proves it.

Investigate in this order:

1. Measure how often a different legal allocation or query batch can change a useful opportunity. If almost all current graphs are isolated dyads, global optimization has little immediate work to do.
2. Test fixed-score local matching repair and coordinated hard revelation. These expose structural headroom without learning confounds.
3. Use publicly inferable return times to decide whether a weak edge should be used now or reserved for a returning partner. Optimize whole small components to avoid double-counting the same alternative.
4. Test whether resolved reciprocal histories, especially failed second stages, supply repeat-actor signal that the earlier marginal models missed.
5. Only then learn or distill continuation values, infer preference regimes, or explore for future information.

The most interesting possible failure result is that better prediction and stronger current matchings do little because legal graphs are thin, repeated informative histories are scarce, and relative deadline qualification is largely uncontrollable. Quantify that possibility rather than interpreting low absolute reward as proof of bad allocation.

## 3. Reconciled simulator contract

Use the shipped `kit.py` and `evaluate.py`; retain their hashes. The policy sees JSON state and its returned memory. The host may see privileged worlds only in separately labeled audit processes.

| Mechanism | Source-of-truth interpretation | Consequence for research |
|---|---|---|
| Horizon | Ask then match on days 0–59; 40 empty follow-up days, final day 100 | No day-60 introductions; no truncated-score shortcuts |
| Hard information | All eleven hard fields must be disclosed; known incompatibilities also prune partially observed pairs | A sampled feasible edge never authorizes a real introduction |
| Declines | Declined hard answers remain unavailable permanently | Do not spend bundles hoping to override a decline |
| Ask batch | Budget 12/day; constraints bundle costs 3; each named soft field costs 1 | At most four bundles; no legal individual hard-field query |
| Information timing | All asks resolve before match; a member may receive constraints and soft queries in one batch | Joint hard/soft acquisition is legal; adapting a second ask batch to that day's answers is not |
| Reuse | Endpoint reuse is legal after availability returns; a dyad never repeats; each batch has disjoint endpoints | Reuse models must track used dyads, not just member degree |
| Failed introductions | Busy until assignment+8; first labels are observed by assignment+7 | All prior incident labels are resolved for currently available endpoints |
| Mutual first acceptance | Date at max(first response days)+lag; busy through date+6, even if date cancels | Public observed dates give exact release boundaries; pending dates require distributions |
| Positive pause | Both positive second intentions permanently pause both endpoints, even if qualification fails | Successful actors leave the reusable pool |
| Arrivals/exits | 70% arrive at day 0, otherwise days 1–20; 12% draw exit in days 22–60, others effectively never exit | Exit is a mixture, not a daily 12% hazard; future individual exits are hidden |
| Post-exit events | Scheduled dates/feedback still occur | Exit affects future assignment opportunities, not cancellation of existing rewards |
| Deadlines | Date within assignment+30; both positive seconds within date+3 | Earlier assignment does not repair these relative deadlines |
| Shared uncertainty | Actor response rate is reused at first/second stages; one fresh dyad Gaussian affects all four preference logits | Products of independently fitted marginals generally miss dependence |
| Outcome features | Only goal, pace, lifestyle, conversations affect first acceptance; goal also affects seconds | Three remaining soft fields are nuisance signals for current-edge reward |
| Public regimes | Shift changes acceptance coefficients; drift changes acceptance after day 35; delayed changes date lag | Infer only from public support/history; never pass the family label to a policy |

The eleven fields are `age_min`, `age_max`, `who_to_meet`, `relationship_structure`, `smoking`, `partner_smoking`, `has_children`, `partner_children`, `wants_children`, `acceptable_zones`, `schedule`. Age/gender/zone, disclosed partial constraints and timestamps are permitted inputs. UUIDs may identify actors and provide reproducible arbitrary ties, but may not recover generator state, seeds, or outcomes.

For each model, explicitly list: observed inputs; latent actor/preferences/regime variables; exact public transition laws; fitted quantities. Do not learn the known .78 date-occurrence constant or uniform deadline laws just to add flexibility. Missing categorical equality enumeration and shared-effect integration precede any approximation of the full expectation. Sigmoid of expected features is not expected sigmoid; quantify any substitution error.

## 4. Establish influenceable losses and headroom first

Round-five greedy's pooled funnel illustrates the issue:

| Transition | Count / correct denominator | Conditional rate |
|---|---|---:|
| Both first responses | 112,549 / 193,225 introductions | 58.25% |
| Both accept | 27,919 / 112,549 both responding | 24.81% |
| Date happens | 22,038 / 27,919 mutual accepts | 78.94% |
| Both second responses | 13,506 / 22,038 dates | 61.29% |
| Both positive seconds | 5,444 / 13,506 both responding seconds | 40.31% |
| Qualified | 1,968 / 5,444 positive pauses | 36.15% |

These are descriptive pooled ratios, not independent assignment-level evidence. The candidate's corresponding rates were similar. Of the 5,444 greedy positive pauses, 27 failed the date deadline and another 3,449 failed feedback deadlines after an on-time date. Ranking can influence which actors and preferences face the funnel; it cannot choose favorable unseen deadline uniforms.

### Required public bottleneck audit

Use designated previously examined **development** traces first, then the new training/development partitions. Do not fit on any prior confirmation. Report counts and both episode/seed-balanced and pooled summaries separately:

- Graphs before/after asks: verified available endpoints, legal unused edges, component sizes, isolated vertices, degree distribution, bridges, maximum-cardinality gap, weighted matching gap and best-alternative gaps.
- Query backlog: nondeclined incomplete members; public contradictions; bundles revealing zero/one/several usable edges; edges requiring two or more queried endpoints; overlapping candidate neighborhoods; days waiting for verification.
- Available-day opportunity partitions: not arrived, permanent decline, hard-infeasible, not verified, used dyad, exited, positive pause, busy, legal unassigned. State the precedence so losses are not double-counted.
- Outcome losses: first nonresponse, responding rejection, date cancellation, second nonresponse, responding negative second, date/feedback deadline disqualification. Retain the denominator at every branch.
- Occupancy and reuse: full busy duration, endpoint-days unavailable during action horizon, reusable releases before day 60, return with any legal unused neighbor, assignments of previously introduced endpoints, missed return windows, and actions displaced by waiting.
- Actor-history support: available actors with 0/1/2+ first trials and 0/1/2+ date-stage trials; fraction of chosen edges whose second-bias posterior could change; evidence arriving early enough to affect another introduction.
- Exits and positive pauses separately: neither is a generic unavailable state. Do not count the simulator's unused `retired` set as observed retirement.

A privileged audit may reveal full hard truth to count possible partners and latent exits to classify unavailability. Its values may label losses offline, but never become training features or evaluated-policy inputs. Descriptive potential edge-days are not a causal sum of recoverable rewards.

### Oracle hierarchy and exact benchmarks

Compare each level on identical states before expensive policy rollouts. Information levels and controller quality are separate axes:

| Level | Extra information | Purpose and limitation |
|---|---|---|
| O0 public mechanism model | Current observation/history only; integrated public priors | Deployable score reference; not an oracle with extra information |
| O1 known parameters | True actor response/bias parameters and mechanism regime; missing soft values still integrated | Diagnostic value of learning actor/regime quantities; selected missingness posterior remains a modeling issue |
| O2 full current-edge truth | O1 plus useful soft truth and legal hard truth for currently verified endpoints | Isolate current-edge ranking headroom; no future outcomes |
| O3 privileged finite lookahead | O2 plus latent arrivals/exits and busy state, with future outcomes integrated | Diagnose continuation headroom; same bounded planner need not improve monotonically with information |
| O4 full hard graph / renewal relaxation | All nonblocked hard truth, schedules/parameters, relaxed capacity | Upper-bound candidate; certify relaxation/integration before using the word bound |
| T exact tiny models | Fully specified 2–8 endpoint models and short horizon | Exhaustive Bellman reference, exact only for the stated reduced model |

No oracle receives the evaluated seed's future outcome stream. Never reverse-engineer outcome draws. Full-truth scoring with a greedy allocator is a privileged heuristic, not an upper bound on attainable reward.

Investigate two bound constructions. First, positive-pause edges are vertex-disjoint, so their number cannot exceed the maximum matching number of the full hard-feasible graph. Combined with the inherited expected qualification/pause identity this yields a generally loose ideal-model ceiling. Second, develop a time-indexed **renewal occupancy LP**: expected edge-day assignment variables, dyad nonrepeat constraints and endpoint/day capacities weighted by the full expected busy-or-permanent-pause occupancy kernel. Arrivals/exits restrict legal assignment days. Conditional on fixed latent parameters and independent fresh assignment draws, disjoint realized occupancy intervals suggest a valid relaxation. The theory reviewer must check that argument, pause timing, conditioning and integration bounds. Gaussian quadrature plus a numerical LP gives an approximate diagnostic unless a numerical certificate is supplied. Repeat the older loose capacity calculation across development worlds rather than extrapolating from one seed's .637692 value.

Stage-A decision: prioritize querying if verification timing has recoverable gaps; prioritize local allocation if matching gaps occur; prioritize waiting if known/credible returns compete with current assignments; admit personalized models only if repeat-history support and privileged current-edge discrimination show useful potential. If all stronger diagnostics show little improvement, produce a limits report instead of a large learning architecture. A weak heuristic oracle's null result alone is not proof of no headroom.

## 5. Algorithms to investigate

Three baseline/control policies and nine distinct new mechanisms form a **maximum 12-policy** screen. Each must pass Stage A; rejected entries are not filled with arbitrary replacements. Exact configurations and parent contrasts are frozen before B. See [STRUCTURAL_PROPOSALS.md](STRUCTURAL_PROPOSALS.md) and [LEARNING_PROPOSALS.md](LEARNING_PROPOSALS.md) for fuller cases and objections.

### Controls

- **G shipped greedy:** exact shipped FIFO asks and seven-soft-equality greedy allocation. Preserve its tie order and digest.
- **P frozen population:** exact round-five score/FIFO architecture. It is a nonlearning control, not a promoted new candidate.
- **K cardinality control:** same shipped edge ordering/soft score and FIFO, but maximum-cardinality general-graph matching with shipped score as a secondary objective. Compare blossom against exhaustive small graphs. K may advance as an allocation mechanism if it earns its same-score contribution contrast; P remains an unchanged control. No claim that maximum current cardinality maximizes future reward.

### N1 — local alternating-path repair

Start with G's matching. Search bounded length-three augmenting paths and legal two-edge exchanges; prefer increased cardinality, then the fixed shipped objective. Work component by component with a fixed enumeration budget. Ask whether cheap structural repair captures most of K's benefit without solver overhead. Controls are G and K with identical scoring/querying; a cardinality-only ablation isolates informative ranking. A greedy trap on four vertices must be repaired, and triangles must remain legal. Reject if current gaps are rare, future positive-pause opportunities do not increase, or extra introductions merely occupy useful substitutes.

### N2 — periodic stable reranking

Use coherent arbitrary endpoint priorities within an eight-day block, refreshing at block boundaries; use them only within a prespecified near-tie score class. The period reflects the minimum failed-introduction reuse cycle, not a claim that eight days is optimal. Compare to fixed arbitrary order and daily reranking using the same primary score and query schedule. All randomness comes from documented policy randomness/public IDs, independent of hidden seed/outcomes. Hypothesis: stable priorities distribute competition across reusable scarce endpoints better than repeated canonical ties. The closest reusable-resource literature motivates it; its bipartite guarantees do not transfer. A point gain driven by one hash salt or disappearing versus frozen-learning randomization rejects the mechanism. Use one frozen salt/configuration for the B entry; fixed/daily/alternate-salt policies are separately counted C controls within its cap. Confirmation tests the selected deployed salt/configuration, not an unreported search over randomization replicates.

### N3 — collision-aware hard-query batches

Select up to four hard bundles jointly to create useful **distinct** matching opportunities, not maximize a sum of degrees. Sample each member's missing hard truth once per hypothetical world and reuse that sample across incident edges. Enumerate a bounded set of batch candidates or use a small beam over a public shortlist; value actual matching gain and a limited next-return window. Actual match legality always uses the later real disclosure. Compare FIFO-four, earlier single-bundle priority, and the earlier two-query/value approach ported to the same fixed scorer. Separate four-bundle jointness from increased sample count in C; a 32-particle two-query control prevents claiming a sample-budget gain as a new objective. A two-incomplete-endpoint edge and two candidates competing for one verified partner are required toy cases. Reject if value comes only from a different predictor, fewer/more queries, or optimistic completion priors. Earlier matching-value queries already accounted for collision through their matching objective; the proposed difference is bounded joint enumeration up to four, public-conditioned sampling fidelity, return opportunities and stronger contribution tests, not rediscovery of that objective.

### N4 — decision-changing hard/soft packages

Compare four hard bundles against three hard bundles plus up to three useful soft answers, including answers for those newly verified members in the same batch. Score a package by expected change in the **whole selected matching**, including displaced hard capacity; do not query for entropy alone. Restrict to fields with outcome relevance, matchings likely to change, and a fixed enumeration budget. Required controls: same scorer without soft queries, surplus-only soft querying, and three hard bundles with unused residual budget. Separate timing, budget displacement and choice quality through a focused factorial. Reject if regret reduction exists only under the policy's internal model or the net reward fails versus its parent. This revisits a failed/promising acquisition line with a different decision criterion and stronger controls.

### N5 — public-return reservations

Construct return distributions from public introduction/date/response events. Failed introductions return at assigned+8 unless an exit intervenes; an observed canceled date gives a date+6 release; positive pauses never return. Pending mutual dates require the exact public lag law conditioned on observations. Reserve an endpoint only when a joint component comparison favors a credible returning partner over the current legal matching, including exit risk and finite horizon. Compare always-act, point-return reservation and distributional reservation with identical scores. Reject if waiting reduces useful attempts without quality compensation, relies on hidden release/exit times, or treats all busy actors as future partners. Release reservations after a fixed bounded window or when public evidence invalidates them.

### N6 — bounded component belief rollouts

For components of at most eight active/relevant endpoints, compare a small menu of legal matchings and wait. Simulate from public-history beliefs, exact known delay mechanisms, shared effects and nonrepeat state; use a fixed 16–24-day lookahead and a conservative terminal value. Larger components use a deterministic legal parent. Sample unknown actor/profile parameters once per trajectory to preserve cross-stage/history dependence. Compare identical predictor with greedy, K/current weighted matching, N5 and the rollout. Independent samples evaluate the chosen rollout action to expose optimizer's curse. Reject if only internal predicted value rises, wait dominates through an optimistic terminal heuristic, or gains disappear with a larger diagnostic rollout budget. Privileged-state planning stays in the oracle process.

### N7 — uncertainty-gated structural allocation

Compare a few whole legal matchings using a fixed public or supported learned predictor. Preserve G unless a frozen posterior value-margin rule justifies a change; where distinctions are weak, prefer cardinality rather than a noisy edge ordering. Controls: unconditional score reorder, fixed score blend, cardinality control, and the same matching menu without uncertainty gating. Edge intervals are not independent matching-value intervals, and posterior credible intervals are not automatically frequentist confidence bounds. Reject if the gate simply reproduces arbitrary ties, suppresses useful introductions, or uses uncalibrated uncertainty to manufacture confidence. No query changes in this contrast.

### L1 — joint reciprocal history and survivor inference

Keep FIFO and the same greedy allocation to test the predictor separately. Maintain a strongly shrunk approximate posterior for acceptance and second-intention biases, integrating shared past dyad effects and missing useful preferences. Include resolved negative second stages and the public history explaining why repeat actors remain available. Keep exact available-actor response moments; do not replace them with a new approximate survival model. Compare population, exact-response-only, marginal acceptance, joint-first-history-only, and full second-history updates. Tiny exhaustive likelihoods quantify approximation error. Admit only if held-out identical-example proper scores improve and changed legal decisions are supported by enough repeat histories. Sparse successful actors retire, so personalization may fit noise rather than supply reusable signal.

### L2 — compact continuation distillation

Only after N5/N6 have credible exact-model behavior, train a small value correction or action selector from an observation-only planner and **public rollout outcomes on training seeds**. Inputs are public component structure, history summaries, horizon and return distributions. No privileged teacher labels, hidden parameter targets, evaluated seed IDs or future feature reconstruction. Hold out entire seeds and tiny-model classes. Fit the student before validation; when L2 is attempted, the three validation policies are G, its observation-only teacher and its already-fitted student. Admit L2 to B only if the teacher and student have positive validation actual-reward effects versus G and the compression/production checks pass. Those point effects are admission evidence, not superiority. If this cannot be completed before B, defer L2 rather than fit it after C and insert it into D. Export a compact immutable artifact and verify inference parity. Decision-focused learning is an inherited method; the simulator-specific target and observation process are possible contributions, not established novelty.

### Deferred backlog, with explicit admission gates

| Direction | Why it could help | Gate before another policy grid |
|---|---|---|
| Episode-level regime filter | Joint public outcomes may distinguish shift/drift/delay | Known-regime diagnostics must change useful actions; posterior likelihood audited against selected actor histories |
| Coherent offline residual model | Correct repeat/survivor bias missed by public priors | Held-out proper-score improvement beyond population/intercept controls; no final-confirmation fitting |
| Renewal opportunity prices | Account for complete stochastic occupancy, not a universal busy penalty | LP relaxation reviewed; compare a joint component controller and show node-price failure cases |
| Information-directed/bandit introductions | One introduction teaches reusable actor/regime information | Exact toy information value, timely reuse, and advantage over identical randomization with learning frozen |
| Graph clustering/self-supervision | Public graph regimes might need different controllers | Decision value beyond analytic degree/component summaries on held-out seeds |
| Decision-focused policy fitting | Optimize choices rather than AUC | Supported public training returns/action alternatives; internal pseudo-values labeled model-dependent |

No persona autoencoder is admitted merely because it is available. Soft categories and actor priors are independent of demographics under the generator; unconditional masked-feature prediction has no new preference signal. No large model-free RL run is justified without a sample/compute argument. Deterministic historic actions have zero support for most alternative matchings; IPS/doubly robust estimation cannot repair that absence. Randomized supported local menus can study narrow questions, but final policy value still requires paired simulator episodes.

## 6. Learning and prediction evaluation

All offline fitting uses a designated training partition; validation chooses regularization, representation and calibration once. Freeze those choices before B. Online updates within an episode use only feedback already visible at that invocation. Never use any previous or new final-confirmation outcomes for offline fitting, hyperparameters or feature selection.

Log a full assignment-time observation snapshot **before** future disclosures. Named models score identical prospective examples, including public stage labels after maturation. Distinguish a factual selected-assignment audit from predicting every feasible unchosen edge: unchosen labels are absent. Counterfactual oracle labels must not quietly fill that gap.

Model the nested funnel coherently: both respond; both accept; date occurs; both positive seconds; qualified. Explicit no-response is a resolved failure, not administrative censoring. Pending events are not negatives; final 40-day follow-up matures supported assignment outcomes. Available actors have complete incident feedback by the timing result, while global learning from unavailable actors may still require pending-event likelihoods. Stage existence and prior shared-effect selection must not be counted twice.

Report log loss, Brier, reciprocal joint calibration, terminal reliability with whole-seed uncertainty, conditional-stage calibration, and missingness/history/time/family slices. Keep assignment-weighted and seed-balanced results distinct. A rare-event constant can have good Brier score without useful ranking. Predictor admission requires at least one preregistered held-out proper-score contrast with a favorable multiplicity-adjusted interval, no material degradation in the other primary proper score, and demonstrable action disagreement. This is prediction evidence, not reward evidence; fixed query/allocation parent contrasts remain mandatory.

## 7. Fixed experimental funnel

All six families are used. Numeric ranges below are **proposed reserves**, pending a new inventory of observed/planned/archived seeds; no world in them has been generated for this plan. Prior reserved but unrun seeds remain conservatively excluded. Do not execute the old inventory script in place because it writes into a sealed package.

| Stage | Proposed seeds | Maximum grid | Question |
|---|---|---:|---|
| A audit/correctness | Constructed cases and designated examined development seeds | No new reward sample | Is there headroom and is the claimed mechanism implemented legally? |
| Training | 100001–100120 | 120 × 6 × 3 = 2,160 episodes, conditional | Fit only admitted models; collect supported public histories |
| Validation | 101001–101040 | 40 × 6 × 3 = 720 episodes, conditional | Lock model/calibration/hyperparameters before B |
| B diverse screen | 110001–110040 | 40 × 6 × 12 = 2,880 | Screen distinct mechanisms, not dozens of tuned variants |
| C replication/ablations | 120001–120060 | 60 × 6 × at most 12 = 4,320 | Replicate at most two promoted mechanisms against their own controls |
| D independent selection | 130001–130080 | 80 × 6 × at most 4 = 1,920 | Decide whether any frozen candidate merits confirmation |
| E confirmation | First fixed n of 140001–142000 reserve | 12n; illustrative n=447 gives 5,364 | Test exactly one frozen candidate against shipped greedy |

The maximum illustrative main grid is 17,364 episodes including optional training/validation, excluding oracle diagnostics, replays and production. Do not run all entries by default: training is conditional, C is built from the written parent graph, and E occurs only after credible development/selection evidence. The critic's smaller 8-policy alternative remains in [STATISTICAL_CRITIQUE.md](STATISTICAL_CRITIQUE.md). The director chooses the 12-entry cap for broader structural diversity, compensating with at most two promotions and a baseline/no-candidate stopping rule.

Three fixed training collectors are G, K and a supported local-menu randomized control using the same public scorer/FIFO. Log the full menu probability, not a fabricated independent edge propensity. The randomized collector introduces variation for factual training coverage; it does not identify arbitrary off-policy sequential value. Record its probability/configuration before training. Validation uses those three configurations by default; if L2 is attempted, register G/observation-only teacher/already-fitted student instead, before validation starts, retaining the three-policy/720-episode cap. All named predictors can be audited on the same G snapshots without adding policy episodes. Extra public-model teacher rollouts use the separate offline planning allowance and have their own job/source ledger.

**B advancement:** exact grid, protocol/resources passed, no unresolved implementation/leakage objections; mean actual-reward effect at least +.025; mechanism changes real decisions; its declared opportunity metric moves in the predicted direction. Rank eligible mechanisms by actual paired mean, then lower complexity, then ID; promote at most two. For a mechanism whose parent is present, require a positive own-parent point effect. Screen results are exploratory, with all planned candidate/control contrasts and Holm adjustment reported. A +.025 searched point is not evidence of superiority.

**C advancement:** same frozen mechanisms on fresh C seeds with prelisted own-parent controls; actual candidate-minus-greedy and own-parent effects must both remain positive, and contributions/trajectories must agree with the named hypothesis. Required ablations take priority over optional combinations. Permit at most one predeclared combination of separately supported mechanisms, only if its specification and all parents fit the C cap and freeze before C; it must earn both contribution contrasts. No newly tuned architecture based on C may enter D. Failure to clear C ends that line.

**D selection:** at most two contenders plus G/P controls. A contender must pass C and production eligibility, have D paired mean at least +.025, and have a positive **one-sided 90%** paired-t lower bound against G. This is a conservative selection heuristic, not a superiority test. Choose highest lower bound; within .005 choose simpler/lower p99 latency, then ID. The director adopts 90% instead of the critic's suggested 80% for this plan. If none qualifies, retain G and stop without E. Do not relax the rule or extend D until someone passes.

**E:** freeze source, configuration, learned artifact, preprocessing, seed list, sample size, analysis and environment before generating any E world. Run the complete fixed grid; no effect-based monitoring, retuning, substitute policy or sample extension. No unchanged P confirmation is admissible as a new mechanism.

## 8. Statistical claims and power

Let `Y(p,s,f)=100*qualified(p,s,f)/arrived(p,s,f)`. The paired cluster difference is `d(s)=mean_f[Y(candidate,s,f)−Y(G,s,f)]`; the primary effect is the mean of independent seed clusters. Treat the six families sharing a seed as correlated. Never use assignment-level standard errors for policy reward.

Practical planning effect: **+.05 MSMI/100**, about 13% of current G's mean. +.025 is interesting but considerably harder to resolve; +.10 is a stretch target. Rejecting zero when truth is +.05 does not prove the effect exceeds +.05.

The proposed finite reporting family includes four prior valid primary comparisons plus at most one round-six confirmation. New program-level claims use two-sided alpha **.01**, a **99%** paired-t interval, and a positive lower endpoint. Historical original intervals/reports stay untouched; any common-family reinterpretation is separately labeled. This is not an unlimited lifetime guarantee for repeated rounds. Additional future confirmations require a new prospective multiplicity/alpha-spending decision.

With assumed seed SD .26 and 90% power under a normal seed-difference model, exact noncentral-t planning gives minimum n=406 for a true +.05 effect; 10% inflation gives **447 clusters / 5,364 episodes**. For +.025 it gives 1,775 inflated clusters / 21,300 episodes; for +.10, 115 / 1,380. These are planning calculations, not simulator power guarantees. Higher divergence may increase SD substantially.

Before E use `planning_SD=max(.26,1.10*selected_D_paired_SD)`, then the smallest n with positive-tail noncentral-t power ≥.90 at two-sided alpha .01 and effect .05, then `ceil(1.10*n)`. Freeze once. The variance inflation is a heuristic, not a bound. A ceiling of 900 clusters stops confirmation if the formula exceeds available resources; do not silently cap n and claim planned power. The 2,000-seed reserve is not permission to extend the sample. Planning does not use E outcomes.

Report nominal 95% and primary 99% intervals, paired effect/SD/standardized effect, fixed-RNG 10,000 whole-seed bootstrap sensitivity, exploratory family means, leave-one-seed influence, and all failures. Do not elevate a favorable bootstrap endpoint over the registered primary result. Sign-flip/permutation tests are not automatically exact without their own randomization/symmetry assumptions. Secondary outcomes and mechanism claims carry explicit exploratory status/multiplicity.

Use positive pauses to diagnose controllable signal. The inherited *unconditional expectation* identity under ideal independent draws applies to adapted legal policies: `E[Q|family]=c_f E[P|family]`, with `c=.36` ordinarily and `6039/17150` in delayed. A delay-integrated conditional/Rao–Blackwell claim additionally requires the new policy's relevant action invariance; old source-specific proofs do not transfer to global learning/calendar policies automatically. Keep actual qualified score primary. The weighted-pause proxy may explain noise or support future estimator research; it cannot replace a failed confirmation after looking at results.

## 9. Explain each apparent gain before promotion

Preselect a deterministic diagnostic sample: largest positive/negative cluster effects, median effects, each family, and mechanism-trigger/no-trigger trajectories. Selection of examples is disclosed; examples do not estimate effect size.

For every serious candidate record its strongest case, strongest alternative explanation and discriminating intervention. Examples:

- More queries versus better query coordination: hold bundle count, scorer and acquisition timing fixed.
- Better matching versus noisy edge scores: keep predictions/ties fixed and change only local repair; compare K and cardinality-only.
- Better waiting versus favorable day/dyad outcome draws: use exact tiny models and return-model calibration, plus fresh policy-level paired tests. Different actions do not share all downstream draws.
- Learning benefit versus survivor noise: freeze learning with identical randomization/queries and compare joint/second-off likelihood controls.
- Higher observed qualified reward versus lucky feedback deadlines: report pauses/date-qualified pauses and residuals with their assumptions; preserve actual score.
- Distillation versus a good teacher: first verify the observation-only teacher's external reward, then measure loss from compression.

World generation is shared across policies; keyed outcomes stay shared only for identical sorted dyad and assignment day, with stage draw reuse depending on the same funnel branch. Moving a pair one day changes its stream. Do not say common seeds make all individual outcomes paired.

## 10. Resources, full logging and production

Use three bounded offline simulation workers, respecting the user's prior preference. Four agent slots include the director; nested delegation does not increase that limit. Default numerical-library threads to one. Evaluated policy limits remain two CPU cores, 1 GiB RAM, 64 PIDs, read-only/offline execution, ten-second invocation, serialized memory **strictly below** 1 MiB, and the documented 2 GiB image limit.

At approximately 3.25 CPU seconds/simple episode, the illustrative 17,364 grid costs about 15.7 CPU hours and an ideal three-worker wall near 5.2 hours, before planning overhead, audits, archives, startup and containers. New planners may cost several times more. Measure actual existing-seed recorder/inference costs before each stage; a fixed local CPU budget of 40 hours for main experiments and 10 hours for offline fitting/planning is proposed. If a planned fixed stage cannot fit, revise the **unlaunched** design or stop; do not outcome-select the completed prefix. No external paid compute is assumed.

The current volume showed about **197 GiB free** during planning, despite the user's earlier 300 GB figure. Save all public input/output bytes, errors, memory, snapshots, source versions, initial/final worlds and diagnostic traces. Privileged logs are host-only. Use lossless streaming compression from the start; no information is discarded. Avoid a second full uncompressed copy of every request log. Forecast storage from actual measured bytes with ≥25% headroom plus 20 GiB free reserve. If archives are duplicated, include both copies in the forecast. Stop cleanly before disk exhaustion, preserve partial attempts and report incomplete stages. No old run deletion is authorized by this plan.

The orchestrator must visibly print preflight/log destinations, stage/cell counts, three worker starts, a progress bar/ETA, ≤15-second heartbeat, active cells, retained/error/failed counts, final summary and exact verification paths. Use separate console and durable structured logs. SIGINT stops new scheduling, closes streams, records worker termination and preserves all completed/partial attempts. Resume every committed cell, including failures, with its actual source attribution; never choose the most favorable attempt.

Production must test empty/no-edge/declined/exhausted states, malformed/oversized memory/request, pending feedback, dense odd-cycle graphs, diverse histories, pruning, actual deadline interruption, solver exceptions and subprocess startup. Require direct/subprocess/restricted-container semantic and ordered action checks, byte digests reported separately, and effective resource/image probes. No universal timeout guarantee follows from finite stress cases. Timing-dependent fallbacks belong to the evaluated executable and must be counted, not suppressed.

## 11. Deliverables and completion

Implement in `research6/`; write new run artifacts only under `results/research6/`. Preserve root/previous policies, frozen manifests, archives and metadata. A future run first seals its execution registration; this planning package is not that seal.

Required outputs: assumption reconciliation; seed inventory with scanned/skipped evidence; candidate/config/contrast graph; hypothesis and decision ledgers; exact commands and environment pins; complete raw rows and prospective examples; calibration figures; graph/funnel/occupancy/reuse analyses; exact tiny models/counterexamples; oracle information disclosures; developer cases, critiques and rebuttals; independently computed statistics/replays; production checks; lossless archives/restoration fixtures; compute/storage accounting; source/config hashes; final manifest generated after all reviewers close files.

Finish with one of two outcomes:

1. A selected new mechanism passes the fixed untouched E comparison, independent replication and production/package checks. State the precise tested distribution and effect; practical target and superiority are separate claims.
2. No credible contender survives, or E does not establish a win. Say so plainly. Preserve rejection evidence, estimated headroom/limitations, and the most informative unresolved question. No automatic new candidate or fresh confirmation follows.

The final report separates proven results, exact simulator calculations, exact simplified-model solutions, empirical findings, approximation assumptions and unvalidated hypotheses. The most informative starting question is: **can joint query/allocation decisions create more successful endpoint retirements by using scarce partners and public return opportunities better, after holding prediction and deadline noise accountable?**
