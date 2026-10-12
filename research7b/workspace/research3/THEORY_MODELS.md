# Round 3 theory, scoring and learning audit

Owned by the mathematical/predictive/dynamic researcher; reviewer: adversarial critic. Maximum allowance one CPU worker and ten CPU minutes. Executed work before full-policy screening: one tiny-DP/old-cohort fitting command, initial wall time 0.36 seconds; corrected-mixture rerun0.35 seconds. One intermediate descriptive per-seed audit edit failed from an array-shape mismatch; fixed before writing the final artifact. No full-simulator episodes or new seeds were consumed by this task. Sources reviewed: prior theory and extension, algorithm, final theory/statistical/package reviews, report/reproduction/registry/reference documents, `kit.py`, `evaluate.py`, and all three earlier policies plus terminal-model/candidate modules. The completed package is preserved.

## Evidence boundary and reconciliation

Observations comprise disclosed fields/statuses, public demographics/arrivals, current availability, introductions and public feedback. The model cannot observe scenario, seed, undisclosed truth, response propensity, either actor bias, shared dyadic effect, exit date, release time or scheduled future events. Reading public generator/transition code establishes mechanisms; it does not authorize reading a generated world's private values at inference.

Actions run days 0–59 and all supported feedback arrives by day 97, inside official day 100 follow-up. The eleven hard fields, availability, no prior dyad, and disjoint batch endpoints are legality checks owned by the director's wrapper. Hard declines are permanent. Constraints queries cost three; a bundle reveals every nondeclined hard field. Non-mutual introductions occupy eight days. Mutual accepts occupy until date plus six even after cancellation; all both-positive second submissions cause permanent positive pause irrespective of reward deadline. Exits do not cancel scheduled outcomes. Arrival cutoff is day20; exit mixture is 12% total uniformly on days22–60, not 12% each day. Delayed dates add5–12 days. Relative date deadline is assignment+30; seconds must be within date+3.

The shared Gaussian enters both introduction and both second logits. Response propensity is reused for introduction and second submission. Therefore terminal probability uses actor response second moments, not squared mean propensity, and a common random-effect expectation of four factors. Missing soft equality indicators are enumerated under public uniform categorical priors. Five-point Gaussian quadrature is approximate. Delayed-family deadline qualification is coupled to ordinary-regime logits: terminal joint weight is `(3+671/686)/6` times normal plus shift/6 plus drift/6. Occupancy similarly couples delayed8.5-day extra lag to normal-family mutual probability/6. Marginal mixtures are not multiplied independently. Public soft priors are correct before feedback selection; applying them to an available/history-selected pool ignores posterior selection and is an approximation.

The prior confirmation remains negative: simple_fifo .331250 versus greedy .372917; difference−.041667, registered CI[−.091068,+.007735]. Superiority, inferiority and equivalence were not established; the targeted+.10 was excluded. The simple model's common positive score yields canonical-ID greedy ordering; learning that scalar cannot change edge order. Integrated diagnostics still run. FIFO hard-query schedules coincide by the prior proved proposition. Development no_learning_fifo/terminal_soft estimates did not receive their own confirmation. No contrary narrative follows from the new methods.

## Proven deductions from the public score mechanism

Conditional on fixed actor parameters and fixed other soft fields, changing goal inequality to equality increases introduction logits by+.375 in shifted and+1.05 in ordinary families, and second logits by+.4 in every family. Changing pace inequality to equality increases introduction logits by+.6 or+1.2; conversation equality adds+.3 or+.75. Every sigmoid factor is increasing, so each change weakly increases the common-effect-integrated immediate terminal probability (strictly for finite logits and positive response propensities). Lifestyle equality has opposite signs across regimes; no regime-universal monotonic ranking follows for it.

`emotional_availability`, `space_for_relationship`, and `relocate` never enter any funnel probability or hard eligibility. Holding the world parameters, other features, and chosen dyad/day fixed, changing these three values leaves its outcome distribution unchanged under the intended independent-draw stochastic interpretation. The shipped baseline counts their equalities in its seven-field ranking. Their inclusion can change choices without changing the corresponding immediate reward model. This is a structural nuisance-ranking diagnosis, not a proof that removing them improves dynamic reward. These fields may correlate with other state after selection despite independent generation; the policy's future allocation can change.

No new mathematical novelty is claimed: coordinatewise monotonicity and conditional irrelevance follow directly from simulator source. The strongest new contribution, if useful, would be a reproducible empirical isolation of nuisance ranking and cardinality/occupancy tradeoffs in this observation process.

## Exact simplified models

`python3 -m research3.tiny_models` exhaustively enumerates legal current matchings, including wait, and independent Bernoulli successes with rational arithmetic. Success gives unit reward and retires both endpoints; failure blocks endpoints for a specified duration; dyads cannot repeat. Edge schedules are known deterministic inputs. These are specified finite models, not exact full-simulator solutions. Terminal reward is booked at assignment; busy duration affects future introductions only.

| Instance | Exact optimum | Refuted alternative |
|---|---:|---|
| Four-node path: outer q=.10, middle q=.11; last action day | .20 | largest-edge greedy .11 |
| AB q=.90, AC/BD q=.10; last day | .90 | scarce-endpoint-first .20 |
| AB q=.20/busy8, AC q=.30/busy20; last day | .30 | q/busy ordering .20 |
| AB today q=.10/busy8, AC tomorrow q=.90 | .90, wait today | immediate positive edge .10 |
| AB today q=.20/busy1, AC tomorrow q=.80 | .84, attempt today | wait .80 |

The first example supports cardinality when edge differences are small; the second shows a cardinality or scarcity objective can lose when edge differences are material. Third shows occupancy penalties should vanish at final assignment horizon, since follow-up still matures pending reward. Fourth and fifth separate long blocking occupancy from short failed-attempt return value. Neither implies a universal waiting threshold. General-graph odd-set constraints and nonseparable continuation objections from prior theory remain intact.

## Candidate contracts

All inference in `model_candidates.py` is observation-only, without files/network accesses. Interface: `score_edges(state, legal_pairs, mode, memory=None)` returns unsorted `(score, canonical_pair)` rows. Caller owns sorting (descending weight then canonical pair), queries, matching engine, hard checks and legal fallback. No score imposes a positive-edge cutoff. Constant/canonical and shipped greedy controls are provided by the director. At200 endpoints O(E) score methods and bounded caches fit intended inference budget; actual production measurements belong to the director. Malformed input handling belongs to the wrapper, not these internal score functions.

| Mode | Objective and learning | Hypothesis; simple isolation | Principal objection |
|---|---|---|---|
| public_weight | goal equality1.0, pace.55, conversation.25; lifestyle omitted; missing equals integrated as equality probabilities; no updates | remove nuisance soft fields and ambiguous lifestyle sign; compare shipped seven-field equality ranking | chosen weights are heuristic, not calibrated; ignores actor and future value |
| population | frozen full-funnel prior; regime weights4/6 ordinary,1/6 shift,1/6 ordinary with late drift; common S and missing-equality integration | true public mechanisms improve immediate discrimination; compare public_weight and existing no-learning | selected available actors differ from fresh population priors; known mixture is assumed, not observed |
| scarce | lexicographically prefer smallest endpoint degree, then degree sum; no updates | improve cardinality by preventing scarce endpoints losing partners; compare constant/canonical, maximum-cardinality | exact counterexample shows reward loss; current degree ignores future arrivals, queries and competing dyads |
| response | population q times strongly shrunk resolved-event actor response second moments | repeated response/nonresponse is more learnable than sparse acceptance bias; compare population | Beta approximates uniform generator; ignores pending-response survival, selection and posterior cross-dependence |
| throughput | population q divided by expected busy duration8+10.642857*P(mutual)+8.5*P(mutual,delayed) | reduce unproductive occupancy; compare population, late-horizon penalty ablation | nonseparable capacity value; horizon-independent penalty explicitly fails last-day toy |
| offline | fixed direct terminal logistic from old baseline snapshots, ridge slopes25 and intercept penalty2 | shrunk data-driven equality weights beat public assumptions; compare population and constant | only40 positive labels across train/validation; baseline action coverage; empirical model not a coherent full funnel |

None has been promoted by this task; all are falsifiable exploratory candidates pending registered reward evaluation. Strongest case: these modes cheaply separate unnecessary feature noise, actor response evidence, immediate probability, cardinality, and occupancy. Strongest opposing case: terminal events are rare, two dynamic heuristics already have counterexamples, and public prior prediction may worsen as successful actors retire. Their empirical point estimates must be challenged rather than accepted.

## Offline learning and common-cohort prediction audit

Only already examined `audit_common_cohort_calibration.json` baseline-selected assignment snapshots were read. Training seeds1001–1005:2351 assignments/26 qualified. Held-out old validation seeds1006–1008:1216/14. Scenario labels are excluded from features. Feature vector is intercept, four centered assignment-time equality probabilities, and day≥35; no subsequently disclosed fields enter. Validation did not choose penalty, features, or coefficients; the ridge penalty was fixed before the first fit. Frozen weights appear in inference source and the result JSON. There are only three validation clusters; this is exploratory validation, not untouched confirmation or sufficient evidence for calibration uncertainty.

| Validation score, identical examples | Log loss | Brier | Mean prediction | Observed |
|---|---:|---:|---:|---:|
| Frozen offline ridge | .062707 | .0113774 | .0109914 | .0115132 |
| Public population integration | .062178 | .0113668 | .0100609 | .0115132 |
| Constant training rate | .062854 | .0113808 | .0110591 | .0115132 |

These are assignment-weighted means, not seed-balanced uncertainty estimates. Population point scores are better here; the ridge barely changes the constant proper scores. No model-quality superiority or policy-value claim is made. The fitted lifestyle and conversation slopes are negative despite positive mixture conversation effect; sparse/selected labels plausibly explain noise, not discovered causal preference. No inverse-propensity policy evaluation is valid: logs omit action propensities and deterministic baseline coverage leaves alternative edges unobserved. AUC/reliability/stage audits on future common prospective cohorts are required for any serious predictor.

The direct logistic uses observed equality probabilities as descriptive covariates; it does not claim `sigmoid(E[latent logit])=E[sigmoid(latent logit)]`. The mechanistic population comparator enumerates missing equalities. The prior absolute Taylor bound Var(Z)/(12sqrt(3)) quantifies generic mean-substitution error but has no global Jensen sign. Further empirical calibration is required rather than interpreting fitted logistic as exact integration.

## Learning paradigm suitability

| Paradigm | Representative or decision | Data/cost and decisive failure risk |
|---|---|---|
| Supervised | offline ridge direct terminal plus prior full funnel | snapshot labels; tiny terminal effective sample; prospective common-cohort audit required |
| Unsupervised | current graph degree/components via scarce mode | public graph, no labels, O(E); grouping only matters if it changes reward; no latent-regime identification claim |
| Self-supervised | reject large masked-feature model this round | generator independently draws soft categories; conditional on public fields missing soft category has exact uniform prior; neural representation cannot discover absent prior signal; selected histories could add signal but require outcome model |
| Online | response-only Beta shrinkage | resolved response labels, O(H+E); censoring/pending survival omitted; control population isolates update value |
| Offline population learning | fixed old-data ridge | seed-separated train/validation, cheap optimizer; distribution/action-selection shift |
| Contextual bandit | no large implementation justified yet | introductions alter future availability and feedback; actor/dyad arms share endpoints; sparse terminal rewards and poor logging coverage undermine simple bandit assumptions |
| Reinforcement learning | exact small DP implemented, full model-free RL deferred | broad action-space/partial-observation search needs many episodes; bounded exact tiny models falsify reductions first; no learned full-simulator optimality |
| Offline policy learning | reject importance-weighted value estimates from existing logs | no logged propensities and unsupported alternatives; fitting a predictor is permissible but does not solve coverage |
| Model-based planning | throughput proxy plus exact toy planning | public delays used rather than relearned; endpoint value is not generally separable, finite horizon matters |
| Hybrid | population probability plus degree/throughput allocation comparisons | low inference cost, modular ablations; any useful combination must outperform own architecture, not just weak baseline |

Large unsupervised/self-supervised models are not ruled out universally. Independent fresh categorical generation implies no masked-feature predictive signal from other fresh fields under the source prior; public outcome histories can create posterior dependencies. Using hidden labels to learn representations would violate the evaluated interface. Hierarchical actor/latent dyad models would need many actors across seeds but ID effects do not transfer across generated worlds; within episode sparse histories motivate strong population shrinkage. Shared dyadic effect is fresh for each never-repeated dyad, so a persistent dyad-ID embedding is unidentifiable and has no legal repeat exploitation.

## Closest literature and generalization

The prior bibliography already supplies dynamic-market, matching-polytope, proper-score and shrinkage primary sources. The tiny counterexamples are standard decision-theory constructions, not new algorithms. Population integration inherits common-effect random-effects modeling and finite quadrature; degree-first is a standard scarcity heuristic. Any simulator contribution is the specific controlled comparison with reciprocal delayed reward and reuse. Generalization would require verifying observation process, fresh pair effect, delays, retirement, actor heterogeneity and action coverage; none is established for real markets.

## Review status

Critic review requested before full screening. Director owns reward registry, wrappers, ablations and promotion/rejection. Independent implementation reviewer must check returned score ordering, prior-mixture weights, response count construction, exact-DP state transitions and coefficients against snapshot audit. Unresolved objections: population prior selection bias, scarce degree surrogate, response pending survival, throughput final-day mismatch and unsupported action coverage. These are recorded rather than obscured by favorable exploratory point estimates.

## Pre-screen strongest cases and falsifiers

Population scoring is strongest because it discriminates using the actual full funnel without fitting sparse actor biases; it fails if identical prospective examples show no proper-score benefit and matched-seed policy reward fails promotion. Public-weight scoring trades calibrated probabilities for simple monotone ranks; it fails if removing nuisance features changes choices but reward remains no better than clean-equality/canonical controls. Scarcity is strongest when mostly equal edge values make cardinality more important than uncertain ranking; it fails if matched episodes do not gain introduction/positive-pause opportunities or observed gain disappears versus maximum-cardinality control. Response-only adaptation isolates an observable repeated actor parameter; it fails if response updates change ranks but proper-score/reward results worsen versus frozen priors, or gain disappears under fixed score versus own architecture. Throughput is strongest early in thick markets; it fails if reduced occupancy does not increase future useful introductions or its effect is driven only by last-day ranking errors. Offline ridge is the explicit data-driven control; its own old validation already fails to beat population point proper scores and no useful ranking improvement should be assumed.

A clean-equality control should count only four operative soft fields and use identical query schedule/allocator/ties to shipped greedy. Comparing public_weight alone conflates useless-field removal with coefficient changes and missing-feature integration. Surplus soft queries need same scorer with and without those queries; hard FIFO invariance holds only while soft fill does not displace hard bundles. Query decisions should be evaluated for changed legal opportunities/pair ranks, not entropy reduction alone. A surplus query may cause lower terminal reward through premature attractive-but-occupying choices; more observed soft information is not automatically better sequential value.

Reviewer exchange: critic found no hidden-information leakage or tiny-DP inconsistency, requested correct regime/deadline coupling, identified approximate Beta prior/pending survival, heuristic weights, tiny validation uncertainty and initially empty frozen offline coefficients. All concrete corrections were made; pending-survival and selected-pool prior errors remain declared approximation objections. Full written review belongs to critic-owned files.

## Finite-domain throughput ordering counterexample

A separate cheap executed-score audit enumerated all81 equality probability patterns (each of four fields has equality0, its missing-category prior, or1) for pre/post-day35 state. It checked all3240 pairwise pattern orderings in each state using the frozen score functions, without modifying sources or generating episodes. Population and throughput actions were identical on all72 StageB paired episodes, but their score ordering is **not universally equivalent** on this finite domain:25 inversions before day35 and16 after it, with no exact tie mismatches.

Before day35, pattern(goal0,pace0,lifestyle1,conversation missing) has population q=.004970522 versus pattern(goal0,pace missing,lifestyle missing,conversation0) q=.004967256, but throughput scores reverse: .0005517968 versus.0005519534. After day35 a larger example has pattern(goal0,pace missing,lifestyle1,conversation1), q=.007497909, throughput.0007843311 versus(goal missing,pace0,lifestyle0,conversation missing), q=.007348351, throughput.0007946171. These are implemented floating/quadrature calculations, not exact simulator probabilities. `score_ordering.json` preserves all patterns and counterorderings. The identical StageB actions are finite empirical redundancy, not a theorem that the occupancy proxy cannot change allocation.

For the frozen offline logistic scorer, its intercept and day≥35 coefficient add a common offset to every edge logit at one invocation. The sigmoid is strictly increasing mathematically, so neither common term changes mathematical edge ranking. Removing these offsets could simplify ranking, but finite floating rounding/tie/zero-cutoff behavior is not certified byte-identical here; the executable remains unchanged. Runtime for the enumeration was.0099 CPU seconds.
