# Round 3: sequential matching research

The registered confirmation does not establish superiority over shipped greedy.

The frozen candidate is `clean`, config `{"mode": "clean"}`. Greedy scores 0.412500 MSMI/100; candidate 0.427083. Paired effect +0.014583, registered 95% seed-cluster CI [-0.030536, +0.059702], two-sided p=0.5170935942784989. The interval excludes the targeted +0.10 improvement. Nonsignificance does not establish equivalence. Selection estimates and exploratory rankings do not establish that this candidate is best.

## Preservation and evidence boundary

The previous completed extension remains negative/inconclusive: greedy .372917, simple_fifo .331250, difference −.041667, CI [−.091068,+.007735]. Its common positive score cannot rank dyads differently through updates; auxiliary diagnostics still execute. FIFO schedules are identical and favorable deadline outcomes plausibly contributed to development estimates. Those facts were independently reproduced. No_learning_fifo and terminal_soft did not receive their own old confirmation.

Inherited root policy.py and extended_policy.py differed from their old freeze hashes at this round’s start. Initial bytes were fingerprinted and preserved; exact old frozen versions were recovered into research3/recovered_frozen from a git checkpoint. No old result, report, source, archive or manifest was overwritten. All eight old archives and 1,687 raw members verified. The new greedy adapter directly calls shipped kit mechanisms and reproduced an old action digest. Root policy.py remains the inherited research2 candidate, not this round’s greedy comparator.

Research2’s asserted proof of +.10 contradicted its own negative result, and its fast scripts omitted official follow-up. Those claims were rejected; all planned/exposed seeds were excluded. See [critic audit](CRITIC.md), [seed inventory](../results/research3/seed_inventory.json), and [decisions](DECISIONS.md).

## Bottlenecks and influenceable losses

Independent old-confirmation counts: greedy 17,954 introductions; 7,419 fail reciprocal response; among 10,535 both-respond pairs, 8,107 fail mutual acceptance. Of 2,428 mutual accepts, 579 dates cancel; 1,849 dates yield 727 reciprocal second nonresponses and 611 negative pairs among 1,122 both-respond seconds. Of 511 positive pauses, 332 miss date or feedback qualification, leaving 179 qualified. These are pooled counts with stage-specific denominators, not independent assignment-level tests.

Public date cancellation probability is .22, feedback qualification .36 conditional on both-positive outcomes, and delayed date qualification671/686. Assigning earlier does not repair relative deadlines. Pair quality, clarification timing and future opportunity availability can change response/acceptance/pause counts; deadline draws themselves cannot be predicted from permitted inputs.

A new deterministic timing lemma shows that a currently available endpoint has every scheduled event from each prior introduction already observed: failed introductions release on assignment+8 after the day+7 response maximum; mutual introductions release on date+6 after the date+5 feedback maximum. Legal later introductions cannot overwrite an unresolved busy interval. The old48-world audit found zero violations in458,829 available-endpoint invocations. Thus pending-survival corrections cannot change this round’s current legal-edge actor response estimate; global learning from unavailable actors is a separate question. See [available-feedback theorem](AVAILABLE_FEEDBACK_THEOREM.md).

Static privileged old development graphs average only74.625 nonblocked nonisolated endpoints in ordinary worlds and30.625 in sparse worlds. Every nonblocked member eventually becomes verified under FIFO; final verification completion is not the dominant missed-opportunity count. The dynamic edge-day audit separates not-arrived, used, exited, paused, busy, unverified and available states using an explicit precedence. It is descriptive and privileged, not a causal opportunity bound. See [forensics](FORENSICS.md).

## Registered experiments and candidate decisions

Training used old seeds1001–1005, validation1006–1008, prospective assignment snapshots and public resolved labels only. Screen70001–70012 used13 candidates; focused development71001–71032 used the registered top three plus mandatory architecture controls/ablations; selection72001–72020 used its fixed rule. Confirmation code/config and sample were frozen before seeds73001 onward. Six families sharing a seed were always clustered together. No fitting or retuning after screening, and no confirmation extension.

### Exploratory screening

| Policy | MSMI/100 | Paired effect | 95% seed CI | Exploratory Holm p |
|---|---:|---:|---|---:|
| offline | 0.472222 | +0.118056 | [+0.035231, +0.200880] | 0.1135 |
| goal_queries | 0.451389 | +0.097222 | [-0.037925, +0.232370] | 1.0000 |
| random_order | 0.444444 | +0.090278 | [-0.040314, +0.220870] | 1.0000 |
| scarce | 0.423611 | +0.069444 | [-0.023185, +0.162074] | 1.0000 |
| four_queries | 0.416667 | +0.062500 | [-0.043695, +0.168695] | 1.0000 |
| public_weight | 0.409722 | +0.055556 | [-0.048723, +0.159834] | 1.0000 |
| goal | 0.402778 | +0.048611 | [-0.069693, +0.166916] | 1.0000 |
| response | 0.402778 | +0.048611 | [-0.045722, +0.142944] | 1.0000 |
| population | 0.361111 | +0.006944 | [-0.097639, +0.111528] | 1.0000 |
| throughput | 0.361111 | +0.006944 | [-0.097639, +0.111528] | 1.0000 |
| greedy | 0.354167 | reference | — | — |
| clean | 0.340278 | -0.013889 | [-0.130839, +0.103061] | 1.0000 |
| canonical | 0.333333 | -0.020833 | [-0.071944, +0.030277] | 1.0000 |

### Focused development and ablations

| Policy | MSMI/100 | Paired effect | 95% seed CI | Exploratory Holm p |
|---|---:|---:|---|---:|
| population | 0.432292 | +0.057292 | [-0.006756, +0.121340] | 0.4665 |
| random_order | 0.403646 | +0.028646 | [-0.097355, +0.154647] | 1.0000 |
| public_weight | 0.398438 | +0.023437 | [-0.052200, +0.099075] | 1.0000 |
| goal_queries | 0.393229 | +0.018229 | [-0.062076, +0.098535] | 1.0000 |
| clean | 0.382812 | +0.007812 | [-0.045803, +0.061428] | 1.0000 |
| offline | 0.380208 | +0.005208 | [-0.047075, +0.057492] | 1.0000 |
| greedy | 0.375000 | reference | — | — |

### Independent candidate selection

| Policy | MSMI/100 | Paired effect | 95% seed CI | Exploratory Holm p |
|---|---:|---:|---|---:|
| clean | 0.362500 | +0.025000 | [-0.047800, +0.097800] | 0.9621 |
| population | 0.341667 | +0.004167 | [-0.094235, +0.102569] | 0.9621 |
| greedy | 0.337500 | reference | — | — |
| random_order | 0.270833 | -0.066667 | [-0.173738, +0.040405] | 0.6242 |

Selected `clean` by the registered engineering-cost preference within .025 of the best selection mean. This band does not mean equivalence. Confirmation fixed n=40 seed clusters from pilot SD floor/estimate 0.210000; uncapped planning n=39. The practical target was +.10. Power planning is approximate for rare discrete rewards.

### Frozen confirmation

Paired bootstrap sensitivity95% [-0.027083, +0.058333], standardized paired effect 0.10337083227118515. All planned cells must be valid with zero optimized-path fallback before analysis. Failures are retained and disqualify conclusions rather than silently removed.

| Family | Candidate | Greedy | Difference |
|---|---:|---:|---:|
| development | 0.587500 | 0.600000 | -0.012500 |
| sparse | 0.162500 | 0.150000 | +0.012500 |
| cold_start | 0.450000 | 0.400000 | +0.050000 |
| delayed | 0.437500 | 0.412500 | +0.025000 |
| shift | 0.387500 | 0.387500 | +0.000000 |
| drift | 0.537500 | 0.525000 | +0.012500 |
| Secondary metric | Candidate | Greedy |
|---|---:|---:|
| Mean episode coverage | 0.352812 | 0.353229 |
| Mean episode ask cost | 194.750 | 194.750 |
| Pooled mutual acceptance / assignments | 0.148269 | 0.147029 |
| Pooled dates / mutual acceptance | 0.794180 | 0.785638 |

These pooled conditional rates differ from means of episode ratios. Raw denominators are retained; secondary metrics carry no separate confirmatory superiority claim.

## Mechanism evidence, disagreements and alternatives

Confirmation introductions 19006 versus 19037, positive pauses 512 versus 508, qualified 205 versus 198, deadline disqualified 307 versus 310. Representative full traces, paired count effects, query schedule equality, busy duration and repeat endpoint counts are in [confirmation mechanisms](../results/research3/confirmation_mechanisms.json).

These chosen-trajectory changes do not identify a causal mechanism. Different dyads/days change hashed outcome streams; common worlds do not share every downstream draw. Architecture controls isolate score/query differences at the policy level, while descriptive occupancy/pause/deadline comparisons can still reflect chance and endogenous future assignments. The critic’s strongest alternatives and resolutions appear in SCREEN_REVIEW.md and FINAL_REVIEW.md. No retrospective truth enters candidate features.

A controlled final-day intervention establishes a narrower result: with collision-free introduction IDs and full follow-up, appending a legal edge between unmatched available endpoints on day59 leaves every existing outcome unchanged and can only add terminal reward. The zero-score filter therefore has no final-day continuation justification. Across24 already examined trajectories,37 such edges were added; existing events were byte-identical, realized additional qualification was zero and the numerical conditional expected total was .159206. This is small, rare-event headroom, not a confirmed substantial gain. No augmented candidate entered the frozen selection/confirmation. See [final-day audit](FINAL_DAY_AUGMENTATION.md).

## Prediction, learning and oracle headroom

Prediction models were compared on identical prospective greedy examples, not their own selected populations. The old split contains only14 terminal positives across three validation clusters; response shrinkage’s favorable proper-score/AUC points were exploratory. Frozen offline ridge failed to beat population validation point proper scores. The focused32-seed common-cohort audit supplies full-funnel logloss/Brier, calibration uncertainty and scenario/missingness/time/history slices. It does not fit models or evaluate confirmation for selection. See [prediction audit](PREDICTION_AUDIT.md).

Stored raw snapshot prediction values are auxiliary inherited integrated-prior diagnostics with a uniform three-regime mixture, not each candidate’s forecast or the new six-family population prior. Independent audits recompute named forecasts on identical examples; recording diagnostics do not enter actions. See [prospective data contract](PROSPECTIVE_DATA_CONTRACT.md).

The learning-paradigm assessment implements supervised offline ridge, public model integration, online response shrinkage, graph structure/scarcity, busy-duration allocation and exact tiny model-based planning. Large self-supervised/unsupervised feature models lack fresh generator cross-feature signal; offline policy importance sampling lacks logged propensities/action coverage; full model-free RL and bandit reductions are unjustified by the sparse coupled data here. These are scoped decisions, not impossibility theorems. Strong nonlearning controls remain mandatory.

Privileged diagnostic levels separately disclose actor/family parameters, soft truth, or free hard truth; none sees future random outcomes.120 old-world greedy oracle episodes did not establish superiority. Stronger information did not monotonically improve realized reward; these heuristics are not optimized dynamic bounds. Tiny exact future-state planning is exact only for specified toy models.

The inherited optimistic capacity LP on old seed1001 has mean bound candidate 0.637692 MSMI/100 across six families, sparse 0.102205. It reveals latent parameters/arrivals/exits and all nondeclined hard truth, relaxes schedules fractionally and drops retirement/extra occupancy. Numerical quadrature and fresh-stream assumptions apply. One seed and a loose expected bound cannot quantify attainable population improvement.

## Mathematical and empirical classification

| Evidence class | Supported scope |
|---|---|
| Proven mathematical results | Available endpoints have all prior-introduction events resolved; final-day legal augmentation weakly adds reward under collision-free IDs/full follow-up. Three soft fields are absent from current-edge outcome/eligibility laws; goal/pace/conversation equality increases fixed-parameter immediate funnel probability. Inherited scoped pause identity/FIFO invariance retained. No global policy optimality follows. |
| Exact simulator calculations | Legal bundle/soft costs,11 hard constraints,60+40 horizon, reused shared effect/response parameters, .36 feedback factor and delayed tail671/686. Exact uniform-prior response posterior moments under stated response sampling model. |
| Exact simplified-model solutions | Rational DP counterexamples refute universal greedy, scarcity, occupancy-ratio and waiting rules. Finite81-pattern scoring enumeration finds25/16 population-throughput ranking inversions before/afterday35 despite identical B actions. |
| Empirical findings | Registered paired seed reward, identical-cohort predictive scores, finite resource/parity tests, descriptive funnel and oracle trajectories. |
| Approximation assumptions | Gaussian quadrature, uniform missing-feature priors after selection, moment-matched Beta shrinkage, fixed prior regime mixture, logistic observational fit and nonseparable occupancy heuristic. Pending-survival omission is irrelevant for currently legal actor ranking under the proved source timing lemma. |
| Unvalidated hypotheses | Exact uniform response posterior ranking, better history-conditioned feature beliefs, component-local dynamic planners, coordinated query/assignment bundles and transfer beyond these public families. |

## Production and reproduction

Selected executable: `python3 -m research3.policy --candidate clean`. The root policy.py is not replaced. Selected full seed101 direct/subprocess/restricted-container replay records True validity and action/outcome equivalence. Image inspect size 44742809 bytes, below the documented2GiB limit. All candidates passed constructed200-node dense container parity; memory2 bytes. Actual cgroup probe records2cores,1GiB,64PIDs, unprivileged UID, read-only root and blocked network egress.

Confirmation measured in-process mean/p95/p99/max seconds {'mean': 0.019191261331453973, 'p95': 0.047171091349719065, 'p99': 0.06128208457958857, 'max': 0.1732519590004813}; peak request 496256 bytes; returned memory 2 bytes. Startup/container timings are separate. The7second optimized alarm, bounded request and empty legal fallback do not constitute a universal10second guarantee for arbitrary machines/requests. Tests cover actual interruption, outer timers, malformed/oversized/pending inputs and no solver dependence. Per-call stderr fallback warnings are captured for the selected production replay.

No old source or artifact was changed. Lossless archives preserve raw trajectories, with verified non-overwriting restoration. Commands/versions/compute, seed partitions, written cross-reviews, independent replays, source/config hashes and final manifest are included. See [reproduction instructions](REPRODUCTION.md). Primary-source novelty assessment in [literature](LITERATURE.md) attributes established methods; broad novelty is uncertain.

## Most informative unresolved question

Can coordinated clarification and assignment timing increase expected positive pauses among scarce legal endpoints, after holding score quality fixed and accounting jointly for future occupancy? Current static oracle and sparse learning evidence does not solve this dynamic question. Any next round needs fresh seeds and a new registered fixed confirmation, rather than extending this one.

Focused control contrasts: goal_queries minus public_weight −.005208 (95% CI [−.054629,+.044212]); offline minus population −.052083 (CI [−.093708,−.010459], exploratory Holm p=.063440). None establishes adjusted benefit. On the identical 14,444 greedy assignments from32 seeds, all10 terminal proper-score contrasts have Holm p≥.19577. The completed confirmation contains480/480 valid episodes with zero failures and optimized fallbacks. The interrupted host run resumed only84 missing registered cells; original partial rows and frozen hashes are preserved.
