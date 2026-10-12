# Research7 strategy contracts

All mechanisms below are proposed. No live reward headroom, fit quality, runtime or simulator win has been established for R7. Use one frozen configuration per entry and ten screen slots maximum. Inputs always pass the common public-state/eligibility layer first. The analytical theory memorandum is preserved in [reviews/strategy_theory.md](reviews/strategy_theory.md).

## Common architecture and value definition

Define public history H_t, budget-feasible nonadaptive ask batch A, actual joint answer Y_A, refreshed state H_t^+, and legal vertex-disjoint unused matching M. The target probability q_e(H) is **qualified eventual MSMI**, not first acceptance, date, or eventual pause. Separate pause probability p_e and the joint return/feedback law. A finite-horizon belief controller would solve

    V_t(H) = max_A E_Y[ max_M {sum_(e in M) q_e(H,Y)
                              + E[V_(t+1)(H') | H,Y,M]}], V_60=0.

Expected eventual rewards are booked once at assignment; pending outcomes remain in the transition/information state but are not rewarded again. Full follow-up justifies the booking. This is a mathematical objective, not a tractable exact solver for the full simulator.

For a deployed post-answer controller C, acquisition must estimate

    J_C(A|H) = E_Y[ sum_(e in C(H,Y)) q_e(H,Y)
                    + E[V_tail(H') | H,Y,C(H,Y)] ].

Using optimal matching inside the question evaluator but greedy at deployment measures another policy. Query cost enters budget feasibility and displacement, not a made-up primary reward penalty. Ask-cost reduction matters as a tie-break/service diagnostic. Budget does not carry forward; saying an unused unit was saved for tomorrow is incorrect. Querying earlier can still change future opportunities because acquired information persists.

Every deployment begins with validated G asks/matching as available fallback. A candidate response replaces it only after final global validation. Sampled unknown attributes may estimate information value but never authorize a real introduction. No actual member object is mutated by hypothetical draws. All persistent actor draws are reused on incident edges within a particle; fresh introduction-specific shocks remain dyadic/time specific. Inference assets contain only public-training provenance. No generator imports, simulator objects, seeds, family labels or hidden event streams enter candidate modules.

### Shared fixed implementation bounds

- At most 200 observed members, 19,900 unordered potential pairs. Build exact eligibility once per observation and cache only within the invocation or explicit size-bounded memory.
- Stable input order is canonicalized; tie-breaking uses public IDs solely as opaque tokens. Deterministic RNG uses a declared policy salt, day, canonical public-position keys and draw index, never a world seed/decoded ID. Use fixed draws and fixed operation budgets.
- Acquisition shortlist 8 hard-query actors, 4 soft-query actions on at most 4 actors; include FIFO and Q6 exact candidate batches. Enumerate <=71 hard batches for fixed k<=4; mixed complete packages <=96 including controls. For each package use 32 selection particles, then 32 independently salted margin-check particles for winner vs parent. These two draw sets are model heuristics, not a simulator error bound.
- Whole-action menu <=12 including parent action. Planner affected region <=6 active endpoints plus <=6 boundary alternatives. Reject a region that cannot represent incident current feasible/unresolved edges within the cap; no silent truncation advertised as isolation.
- Local repair <=20,000 probes, two passes. General-graph weighted solver has a cancellable subprocess or proven bounded component implementation; a thread cannot safely interrupt an arbitrary blocking native call.
- Planner selection <=32 particles x12 actions x12 future decision epochs (4,608 model step evaluations), plus independent winner-versus-parent checking <=32 particles x2 actions x12 epochs (768), total<=5,376. The12 epochs are future days after the current action; current-action generation/validation is additional explicitly counted work. Each step uses a fixed cheap rollout controller, never a nested planner. Future rollout asks are frozen FIFO and rollout matching is frozen A1 using the same weights, quantization and tie rules; no nested planner. No future decision after day59; reward for any assigned edge is still full eventual q. Zero tail beyond 12 epochs is an explicit approximation.
- Before development freeze, Gate F fixes model coefficients/asset hashes and all scores. Candidate normally uses deterministic work caps; an exceptional wall guard at 6 seconds returns the already validated fallback and records reason. Reserve at least 2 seconds for guard/serialization/process startup. Profiling must demonstrate total invocation<10 seconds, not assume these deadlines do so.

## Q1: deterministic collision-aware hard acquisition (light)

**Question.** Is a cheap, exact-over-shortlist possible-edge objective competitive with R6's sampled immediate-count query chooser?

**Inputs/action.** Eligible query actor must be available, have at least one missing hard field, and have no hard-declined field. Build possible edges among verified/query-eligible actors, discard known-hard failures and past dyads. Rank query actors by count of potentially unlockable incident edges, then arrival age (older first), then canonical public tie. Take first8. Let k=min(4,budget//3,eligible count). Enumerate all k-subsets plus FIFO. For each subset, activate verified actors and that subset; compute exact maximum-cardinality matching of the optimistic possible graph within the represented actor cap, otherwise bounded deterministic greedy count. Tie prefers FIFO, then oldest actor tuple. Submit selected k bundles. Match remains shipped G.

**Distinction.** No sampled hard truth and no reward model; this is an optimistic opportunity selector. It is deliberately a cheaper control/hypothesis, not the main breakthrough. Remaining hard candidates omitted by shortlist are recorded in diagnostics.

**Parents/controls.** G, Q6; identical G matching. If Q1 and G produce identical actions, report equivalence on tested inputs and stop its empirical slot; do not tune tie salts.

**Tests.** T06 complements/collisions, T11 decline/budget, T16 shortlist exclusion. Distinct versus shared partners must prefer higher joint count where represented; a known contradiction never contributes. All observed `False` values remain observed.

**Gate/falsifier.** If optimistic action differences are rare, or candidate spends more bundles without changing feasible match opportunities, reject mechanism. Main P3 reward gate applies; no promotion from predicted counts.

## H1: released-history actor scorer (light)

**Question.** Do repeated actors carry public, reusable yes-by-deadline signal absent from static pair ranking?

**Model.** Use an explicit shrinkage surrogate for each actor's probability of recorded first-stage Yes by day7. Prior Beta(1,1) unless P2 chooses one empirical-Bayes prior by its frozen public validation rule. On each introduced actor trial, update once only after first outcome is observed or target window closes. Yes is1; No or mature no-response is0 for this event target. Unresolved is not a trial. Count by introduction ID+actor, deduplicate repeated request histories. At most10 mature first trials per actor are stored; retain aggregate older totals with a fixed cap so memory remains bounded. Posterior predictive a_i=(alpha+y_i)/(alpha+beta+n_i).

Score feasible dyad by frozen P scorer times (a_i*a_j)/(prior_mean^2), clipped to [0,1] **only if** P is an admitted probability model. Otherwise use a positive ranking weight and call it a surrogate; do not claim calibrated reward or VOI. Shared dyadic acceptance and selection mean product independence is approximate. Default allocate descending modified weights greedily, baseline FIFO asks. Reset every episode. Do not treat past shared affinity with another partner as a persistent pair effect.

**Parents.** Static P with identical asks/allocation, plus G. Own-parent controls are response-history disabled and mature histories permuted only in host-side model diagnostics. Second-stage actor updates are excluded in H1 and belong to L1.

**Admission.** Need at least200 actors with >=2 mature incident introductions in the training+validation opportunity inventory, and at least5% of examined feasible-edge opportunities with nonprior estimates. These are proposed feasibility thresholds, not facts. Whole-world held-out mature log loss and response calibration must improve over the same prior. Predicted change must alter full matching actions. If positive-history actors mostly pause or lack unused partners, reject personalized policy despite proper-score gain.

**Tests.** T09 Beta-surrogate posterior1/3 check; the separate exact two-type response construction has posterior predictive3/8 and applies only to that specified mixture, not H1; T12 mature/no-response distinctions; T13 dedup, memory reset, no cross-episode learning; T19 selected labels caveat. Personalization is re-evaluated against actual rollout reward in P3.

## A1: terminal-value general-graph allocation (light inference)

**Question.** Does unrestricted maximum **estimated reward** matching add value beyond both G and cardinality-first K?

Use frozen admitted public population scorer P or L1 only after that model is locked; initial A1 uses P. Baseline FIFO asks. Exact feasible general graph, edge weight qhat or explicitly labeled ranking weight. Maximize sum of weights with `maxcardinality=False`; solve each genuinely independent current feasible component for static allocation, retain odd cycles. Quantize weights deterministically at1e-6 before integer optimization; preserve reported quantization error bound <=100*1e-6 on a 200-actor matching. Tie on equal integer sum uses a separate deterministic canonical resolution checked against brute force. Budgeted solver must return already computed legal score-greedy action if interrupted.

**Controls.** P score-greedy with identical weights/asks is the own parent; K isolates maximum cardinality; G anchors final reward. A score gap proves only a static surrogate improvement. It does not prove qhat is correct or the sequential system benefits.

**Tests.** Four-node .90/.05/.65/.65 graph returns1.30 rather than.95; .90 single edge beats two totaling.20 where cardinality conflicts with reward. Triangle cannot allocate1.5 edges. Every component<=8 nodes gets an independent exhaustive matching check. Quantization close ties and fractional score calibration are tested.

**Gate.** P2 scorer reliability and opportunity gate must justify objective interpretation; still permit A1 as an explicit ranking-weight control if no probability claim. If objective gap exists but P3 MSMI does not improve, no rebranding the gap as success.

## A2: whole-matching uncertainty gate (light after assets)

**Question.** Can a conservative switch retain useful global allocation while avoiding unstable score-driven changes?

Start from A1's population scorer and its score-greedy own parent. Use8 fixed world-bootstrap public model assets trained on P2 training only, calibrated with held-out validation. Construct complete parent and A1 matching actions. For each model m calculate total difference d_m=sum q_m(candidate)-sum q_m(parent). Switch only if mean(d_m)>0 and min(d_m)>0; otherwise parent. No independent edge confidence penalties that double-count endpoint opportunities. No waiting/deletion here. Bootstrap assets and validation choice are fixed; no inference refitting. If8-model assets exceed32 MiB, use4 registered assets before P3 with corresponding config version; do not make host-specific choices.

**Controls.** A1 ungated, parent score-greedy; gate-disabled variant shares all assets, not a retrained model. Keep gate fire/reject counts and full action disagreement denominators.

**Limits.** The model ensemble is not a certified bound on true Q. A margin is model robustness, not a guarantee of improvement. If all models share misspecification, they can unanimously prefer the wrong matching.

**Tests.** One edge can be uncertain but a batch advantage stable; identical covered actor sets must not be distinguished by a common node-price subtraction. Force disagreement among models and require parent. Deterministic ties and asset loading match across hosts.

## Q2: reward-aligned joint hard/soft acquisition (heavy design, bounded inference)

**Question.** Did N3 optimize the wrong immediate quantity, and can downstream reward value choose better complete query packages?

Use A1 as the actual post-answer matching controller for both parent and candidate. Draw joint missing hard/soft profiles from a frozen public-trained categorical answer model with explicit disclosure/decline branches. Do not copy a hidden generator to recover individuals. Conditioning must preserve all observed hard contradictions and joint endpoint-profile consistency. For each package A evaluate E[sum qhat_e(A1(H,Y_A))]. Include FIFO+A1, Q6+A1 and no-query package; possible extra soft questions restricted initially to goal, pace, lifestyle and conversations. They may change reward scores but cannot legalize an unresolved hard pair. Joint packages meet12-unit budget and single-batch interface.

Selection particles estimate expected package advantage. Independent margin-check particles must have positive lower nominal90% model-Monte-Carlo bound over the registered parent before switching; no certification of model bias is implied. Ties favor FIFO+A1. Rebuild real eligibility after actual answers and deploy **the same A1 controller**.

**Parents.** FIFO+A1, Q6+A1, and optional one-question-at-a-time value-greedy+A1 fixed in C. Own-parent effect must hold with identical matching controller and reward asset. Compare with Q6 to separate immediate expected count from reward value.

**Failure gates.** Need calibration/answer-likelihood checks, >=5% complete action disagreements, positive model validation beyond priors, and P3/P4 reward gates. Empty missingness/known failures/declines should return parent without pointless work. Ask entropy decrease alone cannot admit Q2. Limit computation/pruning error explicitly; bigger samples are not a new mechanism.

## D1: finite-horizon joint-action continuation (lead heavy mechanism)

**Question.** Can choosing a whole matching by its effects on reuse, pause, dyad exhaustion and future supply outperform immediate ranking?

Baseline FIFO asks; initial own parent is A1. Define a local region relative to A1. Construct a full-action menu from A1, G only when its symmetric difference from A1 fits that region, <=4 local alternating exchanges, <=4 single-edge deletions or replacements, and an empty local replacement; maximum12. Empty local replacement means waiting only inside the region while retaining all outside pairs; global empty is included only when there are no outside pairs. Every menu element is a globally legal full matching, holding unaffected outside pairs fixed. Deduplicate identical actions. Deterministic region: seed with the A1 pair whose endpoints have the largest count of unused feasible or potentially feasible neighbors (canonical pair breaks ties); add at most two other A1 pairs incident to candidate replacement edges in descending frozen weight order. All changed endpoints, including any boundary actor used in a replacement, count toward the six-affected-actor cap. Boundary is the union of other arrived actors incident to feasible or unresolved-hard edges of the affected set plus publicly modeled pending-return alternatives; require at most six boundary actors. Reject an action or region exceeding these caps rather than truncate it. If A1 is empty, seed with the highest-weight legal candidate edge; if none, return the empty parent. Identify <=6 affected actors and <=6 boundary actors; reject unsupported open regions rather than use a fictitious closed graph. Missing-hard possibilities, known pending returns and publicly modeled arrivals contribute to boundary audit.

For each menu action use the **same**32 independent public-model scenario draws and a fixed cheap continuation controller (frozen A1 matching with frozen FIFO asks; its separately recorded solver fallback remains part of that controller). Simulate at most12 future action days, truncated at59, with correct no-repeat, hard decline, query budget, public-history feedback and pause transitions. Public arrival model is based on newly seen `arrived_day` values, not change in available count. Future actor samples are anonymous from declared public priors; identities, real future arrivals and exits are never known. Estimated first-action value is eventual immediate qualified reward + future assigned expected reward. Separate pause and reward; condition pending returns on released feedback and continued unavailability. Unknown exits use public-trained hazard assumptions and sensitivity bands.

Choose only if candidate advantage over A1 is positive on selection draws and independently on32 margin-check draws; near-ties or unsupported beliefs use parent. Fixed model work count is the normal cutoff, exceptional6-second guard returns G. A1 remains explicitly tested as a distinct fallback/parent; record which fallback applies.

**Fidelity gates.** Exact action-value tests T03/T05/T07 and T04 transition consistency (D1 FIFO need not solve its query-choice optimum), prospective return calibration on public validation, no-terminal-double-count test, neighbor closure audit, no-clairvoyance test. On a held-out constructed grid with<=6 actors/<=3 decision epochs, approximate model policy regret<=.01 absolute expected reward and no unexplained negative advantage after margin guard. For large horizons compare tail/horizon variants diagnostically on P2 examined states; reject if action choice reverses in>10% of switches when horizon grows12 to24 or pessimistic exit/return assumptions are used. That sensitivity is a gate, not two screened variants. Longer diagnostic solves are offline only.

**Controls.** Zero-continuation (A1), deterministic mean-return instead of return law, no-wait menu, population-history disabled. Keep only necessary controls within C12-arm cap. Last day must reduce to static nonnegative matching with no future occupancy subtraction. Common reward scaling alone cannot alter a static optimum.

## D2: continuation-consistent acquisition plus D1 (one conditional integrated slot)

**Question.** Does asking to prepare a future legal query/return/arrival sequence have complementarity with the dynamic controller?

Only admitted after D1 transition fidelity and Q2 answer-model fidelity, even if separate P3 empirical wins are not required. It is the one predeclared integration entry, not a late new11th candidate. Score complete packages with the actual D1 post-answer controller's continuation value. To avoid nested explosion, use a cheap fixed surrogate of D1 value or cached first-action menus with<=96 packages and<=32 particles; forbid recursive D1 calls per hypothetical branch. Fit/cache the surrogate only from examined P2 states and public-model answer branches, using public-only teacher inputs; label model-dependent targets. Teacher target is the selected D1 action's immediate qualified expectation plus continuation under its frozen rollout controller, evaluated on independent draws after selection, not the maximum noisy selection value. Record selected action, parent value, horizon, fallback and evaluation salt. Sampled future latent states may generate modeled outcomes but never directly select an observation-only controller action. Held-out surrogate mean absolute value error<=.01, action-ranking agreement>=90%, and false-positive switch rate<=5% are admission gates; surrogate fits count in the shared12-fit/24 CPU h ledger. The immediate-value control uses the same surrogate family/fidelity checks with acquisition tail disabled. Acquisition has<=96x32=3072 package branches plus32x2=64 winner-parent margin branches, total<=3136 surrogate branch evaluations; no recursive planner calls. Actual answer branches reveal the same latent profile sample used downstream. Match really deploys D1.

**Controls.** FIFO+D1, Q6+D1, Immediate-value acquisition evaluated on the actual D1-selected action, with tail disabled only in acquisition and the same D1 matching. Do not reuse original Q2/A1 acquisition values while silently changing its deployed controller to D1. D1+FIFO is its primary own parent. Include all required controls before deciding C entrants; if no room, defer D2 rather than drop the control.

**Exact falsifier.** Future-query complement threshold p>1/4 in T04; real-budget embedding must add competing bundles and account for all12 units. If query budget is usually slack, the toy bottleneck may not occur. Regime differences must influence real future opportunities rather than delayed hard answers.

**Gate.** Same correctness, meaningful action disagreement, P3/P4 reward and independent parent gates. Model speed/approximation must pass container limit. Forecast CPU/storage before admitting this potentially costly arm.

## L1: joint public actor/regime posterior and conditional reward (heavy fitting)

**Question.** Can released repeated-actor/global-history signal improve calibrated terminal and return predictions enough to change useful actions?

Candidates H1 and earlier marginal models supply controls. Represent actor response propensity, first acceptance tendency and second-intention tendency as persistent latent quantities; one fresh shared shock per dyad introduction must be integrated in historical likelihood and a fresh one drawn for a new future dyad. Regime evidence comes only from released first responses, dates, second feedback and observed availability. Date cancellation and late second Yes are separate likelihood events. Pending rows contribute survival likelihood, not zero labels. Actor selection, survival and pause alter usable-actor distribution; validate at action times under public states rather than a random introduction-row split.

Initially use a finite public-fitted mixture (<=16 latent types/actor), pair integration<=32 samples, shrinkage toward a global public prior; no large neural net required. Single joint pair conditional model may estimate mutual acceptance and on-time terminal label without independent directional multiplication. A funnel decomposition is a comparator: P(mutual Yes)*P(date<=30 | mutual)*P(both on-time second Yes | qualifying date, mutual). Fit conditional stages only with mature eligible denominators. A direct composite shrinkage model is a mandatory comparator. Calibration is on whole-world validation; choose exactly one asset by frozen mean mature log loss, tie<=1e-4 favors simpler model.

Scoring/online learning in evaluation is per-episode only; offline hyperparameters/assets fixed. No scenario token, cross-episode accumulator, private labels or teacher latent values. Deployment uses score-greedy allocation and FIFO asks in L1 to isolate new beliefs; separate D1 integration is not automatically another entry.

**Admission.** At least2000 mature first-response actor trials,200 mutual-acceptance introductions,100 happened qualifying dates and50 qualified MSMI events across training, with validation containing>=20 qualified events. If rarer stages fail counts, shrink them to fixed public population constants and narrow claims; no stage-specific personalized model promoted without evidence. Proper-score validation must improve point log loss and world-bootstrap95% upper interval of candidate-minus-prior loss<0 for the claimed stage; bootstrap1,000 draws with fixed analysis seed. Calibration-in-the-large error<=.02 for first response and<=.01 for terminal prediction. Sparse terminal failures may make L1 inadmissible; no sample expansion to meet counts. Count thresholds are design choices frozen before collection.

**Model choice limits.** Maximum3 model families (H1 response-only, direct composite, finite joint mixture/funnel), <=4 hyperparameter settings each and <=12 fits total, included in24 CPU-hour fit cap. Early training-validation stopping may select fit assets, but validation stays sealed from reward screening and is never reused for confirmatory claims. No unsupported DR/IPS from null-propensity deterministic logs.

## L2: public continuation distillation (heavy teacher, light inference)

**Question.** Can a validated D1 controller's action preferences be approximated cheaply without losing its objective or inference legality?

Only if D1 passes its registered P3 own-parent A1 comparison (positive point difference), P3 admission and teacher fidelity; L2's slot can remain unfilled at P3 and is not introduced after E. Before the P4 freeze, train and validate on the already examined P2 partitions; pre-register L2 as a P4-only conditional student with fixed training/validation examined partitions and include it in the12-arm C budget; it consumes the tenth-slot portfolio allowance even when absent from P3. Teacher generates targets on P2/public examined states, never on P4/D/E worlds or privileged latent states. Student predicts advantage over parent for <=12 legal action templates using fixed public features: day/horizon, feasible degree/component size, age-of-arrival, unused-partner counts, own observed history, model return summaries, boundary risk and query status. Maximum depth6 tree/linear additive model, <=32 MiB inference assets. Never imitate a raw future schedule or add seed/ID patterns.

Select student if held-out public state action agreement>=95%, model-teacher mean value loss<=.005 and switch false-positive rate<=5% (teacher estimates, not true reward). Deploy parent on uncertain/off-support states. Teacher-step savings are reported separately; P4/P5 reward evaluation establishes whether distillation is useful. Advance L2 beyond P4 only if D1 also passes its P4 own-parent gate and L2 passes its own registered reward/fidelity gates. L2's primary reward parent is A1, while D1 is its compression-retention comparator. In P4 require mean(L2-D1)>=-.025 and coverage loss<=.01, alongside L2's positive own-parent A1 gate; this observed retention screen is not statistical equivalence/noninferiority. Compare L2 vs identical teacher D1 and vs A1; faster inference alone is not a superiority mechanism. If L2 cannot enter before P4 freeze, defer to a later round.

## X1: released-history regime robustness (conditional optional slot)

**Question.** Can conservative adaptation to real response/occupancy shifts prevent a harmful static-model switch?

Use H1/P as parent. Maintain public mature first-Yes Beta summaries for blocks<=14 days and date-lag survival counts, not hard-answer lag. Freeze one detection rule: switch to recent-window estimates only when at least30 mature first trials exist in both recent/prior blocks and the absolute response-rate difference>.10 with a fixed posterior90% interval excluding0. Add a date-lag slow-law mixture only after at least10 public mutual/date histories, conditioning unresolved dates. Before evidence, use public prior. Detection is imperfect and regime labels remain hidden. An adaptive global scalar on every edge is action-invariant for static same-sized alternatives; X1 must change actor-specific ranking or dynamic occupancy decisions to be counted as firing.

Compare adaptation-off with identical priors/scorer, delay-only model and response-only model. No feature keyed to the literal family or day35 shortcut except a general public day/horizon feature; do not hardcode the hidden drift change day as a detector. False-change tests on stable constructed histories and detection delay tests on known constructed shifts are required. Optional exploration is default off; introducing it requires a predeclared behavior collector and support/delay analysis, not an extra post-screen slot.

## Deferred approaches and conditions for reconsideration

| Approach | Why not main R7 | Evidence needed first |
|---|---|---|
| Generic PPO/DQN/end-to-end graph RL | Sparse terminal reward, huge matching/query action space, opaque failure and expensive tuning | Valid public transition/teacher headroom plus demonstrable insufficiency of bounded planner |
| Ungated Thompson/UCB exploration | Reusable actors, selective labels and delayed occupancy differ from independent bandits | Future unused-partner opportunity, registered feasible action propensities, actual reward benefit vs no-exploration |
| Static dual prices / reward per busy day | Prices cancel among same-covered-set alternatives; throughput ratio fails on last day | Time/edge-specific residual, exact counterexample correctness, deployed own-parent gain |
| More N3 particles/shortlist sizes | Refines failed immediate surrogate rather than new mechanism | Admitted approximation error as current bottleneck, finite existing slot/config budget |
| Spectral connectivity objective | Disconnected graph lambda2=0 can hide improved local matching | Explicit decision-linked objective and nontrivial reward mechanism |
| Hungarian/stable marriage replacement | Preferences do not guarantee bipartition; stability is not qualified reward | Correct general-graph reduction and aligned objective proof |
| LLM interpretation of conversation templates | Synthetic text does not validate latent psychological prediction | Legitimate held-out public signal beyond structured fields and bounded offline assets |
| Hidden-truth teacher/counterfactual labels for deployment | Can leak unavailable data and overstate realizable value | Host-only oracle diagnosis with strict export exclusion; never individual latent inference |

These remain a documented backlog, not permission for a new unbounded search. A negative R7 can support a better scoped scientific conclusion without proving greedy globally optimal.
