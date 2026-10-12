# Extended modular algorithm: assumptions, interfaces and reviews

## Status and ownership

`extended_policy.py` is a separate executable; earlier `policy.py` and `research_policy.py` remain unchanged. `research/terminal_model.py` contains observation-only probability calculations and updates. `research/extended_candidates.py` contains prelisted component comparisons. This document specifies the implementation and limitations; empirical superiority requires the registered experiments, and is not implied by this architecture.

## Simulator reconciliation

The team inspected `kit.py` and `evaluate.py` before development. Actions occur on days 0–59 and follow-up extends to day 100. All eleven hard fields must be observed, neither endpoint may have a permanent decline, both endpoints must be currently available, the dyad must never have been assigned, and pair batches must be disjoint. Members can return for another dyad; the same dyad cannot return. Exit probability 12% is a one-time generator mixture, with a uniform exit day 22–60 conditional on drawing an exit. Availability does not expose future busy releases, dates, feedback or exit reasons.

Date qualification is assignment+30, while both positive second-feedback submissions must occur by date+3. Both positive second intentions retire endpoints even if qualification deadlines fail. Every response propensity is reused across introduction and second-feedback submission. The dyad Gaussian is reused in all four logits. Standard date lag has mean 12.642857 days; delayed lag has mean 21.142857. Maximum delayed date lag is 33, and feedback delay at most five; the follow-up completes all assignment-day59 outcomes by day97. These are exact calculations of public synthetic mechanisms.

## Observable versus latent versus estimated

**Observable inputs:** the JSON state, member public age/gender/zone/arrival day, disclosed field values and statuses, current availability, observed introductions and feedback with timestamps, ask log, current day and ask budget, and policy-returned memory. Assignments create snapshots before later clarification can change field information. No production call reads worlds, datasets, `truth`, bias, response_rate, second_bias, exit_day, pending simulator events, busy release or scenario labels.

**Public mechanism assumptions:** independent uniform missing soft categories; normal acceptance bias SD .7, second bias SD .5 and common dyad SD .45; uniform propensity on [.55,.98]; published two acceptance coefficient regimes and post-day35 drift possibility; Bernoulli date probability .78; discrete response, date and feedback delays; hard-field generator priors conditional on public age/zone. Sparse geography is inferred from observable zone syntax, not a hidden scenario string. These priors make this a model-informed simulator policy, not a model-free recommender. Generalization beyond these synthetic mechanisms is unvalidated.

**Estimated quantities:** actor response moments, approximate actor Gaussian intercept posteriors, tempered regime weights, date probability, posterior standard/delayed lag mixture, and direct aggregate funnel probabilities in the simple control. Hard-query outcome samples and continuation costs are estimates. Future arrivals, true departures, pending busy-release times, and individual undisclosed features are not recovered or treated as observed.

## Terminal model

Let `a_u(S,x)` and `s_u(S,x)` be actor-integrated introduction acceptance and second-intention probabilities at a specified common effect and specified soft equality vector. For response moments `m_u=E[R_u]`, `k_u=E[R_u²]`, date probability `d`, and qualified date-lag probability `h`, the model computes

```
both_response = m_u m_v
mutual_accept = m_u m_v E[a_u a_v]
date = d m_u m_v E[a_u a_v]
pause = d k_u k_v E[a_u a_v s_u s_v]
terminal = .36 h pause
```

Expectations include the same common effect through every funnel logit, a mixture over plausible acceptance regimes, and missing soft-feature equality indicators. Each actor response Beta prior exactly matches the mean and variance of the generator's uniform response propensity; it is a distributional approximation and yields the correct prior second moment. Replacing `E[R²]` with `E[R]²` is avoided. The `.36` is exactly `(3/5)²` from the two feedback deadlines. Standard date deadline probability is one; delayed deadline-failure probability is exactly `120/5488`.

Missing equality indicators are enumerated over at most 16 combinations. The code does not insert expected soft vectors into a logistic. Actor-normal expectations use five-point Gaussian quadrature, and then the shared Gaussian is integrated with the same order. Numerical quadrature is an approximation, rather than an exact simulator probability; independent offline convergence auditing belongs to the theory package. Shrinkage actor updates use one scalar Gaussian precision per stage. Second-stage updates use assignment-time `E[a_u a_v s_u]/E[a_u a_v]` to account for observation after mutual acceptance; it is still an approximate logistic update, not an exact Bayesian posterior. Unknown feature posteriors are not updated directly from responses, and cross-actor posterior correlations are not retained.

Observed no-response, yes and no are distinct events. No pending event creates a negative label. The parametric response updater uses resolved event counts and does not fully incorporate the survival likelihood of currently pending responses. It is therefore not a complete survival model and can have transient timing bias; pending-event awareness alone does not establish calibration. The direct simple control waits 38 days after assignment before adding any terminal-funnel example, preventing quick-failure overrepresentation in that control. As a result only early assignments train its terminal estimate during a 60-day episode.

Regime updates use the joint observed acceptance likelihood when both actual response values exist, tempered by .35. Actor nuisance effects in this likelihood are integrated under population priors rather than jointly refitted with the regime; the posterior weights are approximate. Standard versus delayed timing weights use exact enumerated lag likelihoods, with prior delayed probability 1/6, and are estimated only from observed dates. Pending outcomes are never exposed to inference. `learning=False` freezes every learned parameter; assignment snapshots are still created for audit.

The `independent` comparator integrates each marginal with variance increased by .45², preserving shared-effect marginal variance, and multiplies the four marginals conditional on each missing-feature vector and regime. It removes Gaussian common-effect dependence while retaining dependence induced by feature and regime mixture. It is not a comparison against independence of every uncertainty source.

The `simple` comparator fits five **unconditional** joint stage probabilities by shrunk mature-episode counts. Its terminal probability is estimated directly, without multiplying response factors again. Its `accept_a/b` and `second_a/b` diagnostic fields remain the parametric actor marginals; its five primary joint-stage fields are the simple model's predictions. Its prior terminal rate is an explicit approximate control prior, not an exact probability. `ranking_control` uses the product of directional response/acceptance marginals for allocation, while emitting the same terminal model diagnostics.

## Acquisition

All hard bundles cost three; soft fields cost one. Every action honors the remaining daily budget. Permanent hard declines prune both queries and introductions. Hypothetical revealed fields are used only to value an ask; the later match phase still checks actual observed hard fields.

1. **FIFO:** asks the first incomplete, available, nondeclined members in observation order.
2. **Potential degree:** ranks uncontradicted neighbors, with greater weight for currently verified or already selected partners. This is an optimistic expansion proxy, not expected reward.
3. **Exact model hard entropy:** computes the entropy of each missing semantic hard field from the public generator distribution conditional on age and zone, then sums bundle entropy. The calculation is exact for that assumed field prior; using entropy as allocation value is a deliberately challenged comparator.
4. **Matching value:** samples four correlated bundle worlds, preselecting ten bundles by potential degree, and estimates the change in maximum weighted matching value after revealing one bundle. Matching values use bounded blossom and fall back to greedy on deadline/failure. This is a bounded Monte Carlo approximation, restricted to immediate allocation, with no general value-of-information guarantee.
5. **Two query:** evaluates the same objective for bundle pairs and compares gain per bundle against one-query gain. Joint samples share each member's reveal across all incident edges, preserving within-bundle correlations. Complementary edges can appear only after both incomplete endpoints are selected. Budget or deadline can limit pair examination.
6. **Random:** deterministically seeded uniform bundle-order exploration within the remaining budget, with no hidden-world access.

Matching-value methods fall back to potential-degree exploration if myopic gain is zero. Thus they can still query incomplete endpoints when only complementary edges exist; this fallback is labeled exploration, not positive immediate information value. Optional soft acquisition exactly enumerates the assumed uniform category outcomes, changes affected terminal edge probabilities and asks only when estimated matching value increases. It is limited to currently verified members and by a 200-ms additional allocation budget. Already selected hard bundles are not treated as verified before their real answers arrive. Default inference does not spend otherwise unused budget on soft entropy.

Hard entropy and potential degree require O(n²) candidate checks. Model-value acquisition has restricted candidate count K=10 and samples J=4; candidate pair enumeration has O(K²) options, each potentially solving a weighted matching, so runtime rather than a full combinatorial optimum determines coverage. Soft querying enumerates category outcomes for candidate fields until its deadline. Acquisition after time-budget exhaustion uses legal deterministic fallback; timing-dependent paths can differ across machines.

## Allocation and dynamic approximations

Greedy and general-graph maximum-weight matching optimize the same immediate terminal edge objective. Greedy sorts E feasible edges in O(E log E); NetworkX weighted blossom has O(n³) complexity. No gender partition is imposed. Blossom receives a 200-ms interruptible `SIGALRM` deadline and falls back to the precomputed legal greedy matching on timeout, import failure, unavailable interrupt support or solver exceptions. This optimizes only the current graph and does not claim to solve the full dynamic simulator.

The optional throughput penalty approximates expected busy duration as

```
8 + P(mutual acceptance) * (10.642857 + 8.5 * P(delayed regime)).
```

Each endpoint's continuation proxy is half its best remaining alternative reward times estimated remaining introduction attempts. The loss fraction combines busy-time occupancy and **pause**, then discounts with the generator's small prior exit hazard. The finite horizon, current alternative edges, heterogeneous rewards, response uncertainty and learned delay mix enter the proxy. Unknown future arrivals, future clarification and competition for partners are not solved by a Bellman recursion. These values are not matching duals, and general-graph odd-set constraints are handled only by blossom's current-allocation optimization. Separable endpoint proxies can double-count overlapping continuation losses. The theory agent's explicit four-node counterexample is decisive against claiming exactness.

Optional batching waits on alternate early action days only for a current component of at least three verified members touching an available incomplete member. This is a component-sensitive heuristic for clarification and pre-cutoff arrivals, not a theorem that waiting helps. The uncertainty comparator penalizes an edge by its fraction of missing soft equalities; this is a conservative ranking penalty, not a calibrated confidence bound.

## Candidate contracts and hypotheses

All candidates use the observable inputs above, bounded version-2 memory, assignment-time snapshots, public-prior assumptions and legal solver/protocol fallback. Default updates are the approximate actor, regime and delay updates described above; `no_learning_fifo` freezes them. Candidate configuration entries combine independent components without retuning.

| Candidate | Decision objective/component | Hypothesis tested |
|---|---|---|
| terminal_fifo | integrated terminal reward, greedy, FIFO | public-mechanism full funnel improves ranking |
| terminal_degree | terminal + potential degree | verified-neighborhood expansion improves usable choices |
| terminal_blossom | terminal + blossom | better immediate matching outweighs allocation changes |
| terminal_value | terminal + immediate matching-value queries + blossom | decision-valued queries beat optimistic expansion |
| terminal_two_query | terminal + complementary query lookahead + blossom | bundled value matters in cold incomplete markets |
| terminal_entropy | terminal + exact prior entropy | entropy reduction is a useful allocation proxy |
| terminal_random | terminal + randomized hard exploration | query targeting survives a simple randomized control |
| terminal_opportunity | continuation-adjusted blossom | saved capacity outweighs deferred low-reward introductions |
| terminal_batching | terminal + early component batching + blossom | targeted waiting helps growing components |
| terminal_soft | terminal + decision-changing soft queries | soft decisions improve reward after hard expansion |
| terminal_conservative | terminal minus missingness penalty | uncertainty suppression improves robustness |
| independent_fifo | marginal-preserving Gaussian independence | shared effects materially change rankings/calibration |
| simple_fifo | mature aggregate terminal probability | actor/feature complexity beats a constant calibrated control |
| fixed_regime_fifo | fixed public-development coefficients | regime adaptation has sufficient sample support |
| no_learning_fifo | frozen actor/regime/date priors | observed fitting improves on mechanism priors |
| product_fifo | marginal response/acceptance product | terminal ranking adds value beyond reciprocal product |
| simple_degree | simple + degree | query effects depend on terminal scoring |
| simple_blossom | simple + blossom | allocation effects depend on edge heterogeneity |
| terminal_degree_blossom | terminal + degree + blossom | acquisition/allocation interaction |
| terminal_degree_batching | terminal + degree + blossom + batching | waiting interacts with expansion/allocation |

These labels name configurations rather than demonstrated gains. Any policy selection and final comparison follow the lead-maintained experiment registry, independent of these qualitative hypotheses.

## Protocol and production

`decide(request, config=None)` returns exactly `{asks,memory}` or `{pairs,memory}`. `predict_funnel(a,b,state,memory,cfg)` emits the five primary stage probabilities plus conditional and marginal diagnostics. Assignment snapshots are keyed by sorted member IDs plus assignment day and contain `day`, `users`, `equal`, and `pred`; they are prospective and stay unchanged as fields are later revealed.

Malformed, non-finite, empty and oversize inputs produce a valid phase response with empty memory. The adopted production guard uses a legal first-fit matching or FIFO hard asks when the public state is still usable, and otherwise returns empty actions. The CLI reads at most one MiB plus one byte. Serialized returned memory is strictly below one MiB; audit snapshots are bounded to 700, seen events to 6500, and larger memory is pruned or replaced by the empty fallback. The evaluator separately restricts the **whole request** size, which includes history and memory; production trajectory tests measure both. Parameter fitting and inference access no network, packages beyond standard Python and optional NetworkX, or writable file. `Dockerfile.extended` packages only public mechanism helpers and the policy modules, under UID65534. The lead's verification uses evaluator resource flags for two CPUs, one GiB, 64 PIDs, read-only root, offline networking, ten-second invocation and image-size checking.

`research/test_extended_policy.py` passed 19 tests before development freeze, including all acquisition comparators, explicit solver failure and actual interrupt, malformed JSON, empty/no-edge/declined pools, exhausted budgets, pending observations, response prior moments, missing-feature expectation linearity, marginal-preserving independence, full 60+40 observation trajectory, frozen-learning behavior and subprocess semantic equivalence. Tests use previously examined seed101, avoiding final confirmation contamination.

## Written cross-reviews

The empirical agent correctly rejected the first independence implementation: setting shared S to zero removes variance as well as dependence. The implementation now preserves marginal Gaussian variance. Both the empirical agent and lead rejected the first simple control's repeated response factors; direct unconditional mature-funnel estimates replace them. The lead also identified quick-failure observation bias and required the 38-day maturity restriction. These corrections happened before the registered frozen development matrix; transient development smoke is explicitly marked separately.

The theory agent required a common S through the full funnel, response second moments, pause-based retirement accounting, conditional second-stage actor updates, and a delayed-mixture busy-time correction. Each structural correction is implemented. Their double-counting counterexample demonstrates why the endpoint continuation proxy has no exact dynamic optimality guarantee. The chosen comparator keeps this approximation visible rather than asserting separability.

**Algorithm review of empirical conclusions:** terminal reward is rare, so ordinary row-level intervals are not credible when six scenarios share a seed. Confirmation must use seed clusters, a fixed candidate and paired outcomes; marginal stage calibration should not be confused with terminal calibration. The simple control's parameter diagnostics are not its direct joint predictions. Assignment snapshots prevent later disclosure leakage, but selected introductions still make calibration policy-conditional. Strong predictive calibration does not by itself prove higher sequential reward, and no causal mechanism follows merely from more dates or more verified edges.

**Algorithm review of theory conclusions:** exact DP results in small deterministic models can refute structural claims and illustrate regret but cannot certify full-simulator optimality. Static blossom optimality is conditional on the current weights; it says nothing about the dynamic value of allocating versus waiting. A common-S dependence theorem conditional on fixed attributes does not automatically identify unconditional covariance across differently selected dyads. Public-prior numerical convergence should be reported separately from posterior/missingness approximation error, which a finer quadrature cannot eliminate.

## Independent numerical and execution replication

The theory agent tested 30 quadrature cases against 64-node integration, including actor means at ±2.5, prior and near-zero actor variances, known and wholly missing equality vectors, three regimes and pre/postday35. The maximum absolute stage discrepancy was 6.48946e-6 and maximum relative four-logit discrepancy 2.41065e-5; 32-node versus64-node differed by at most3.33e-16. These tests support the numerical integration order for tested parameters, without validating the approximate posterior or policy calibration.

`results/extended/algorithm_replication.json` independently repeats already registered development seed1001/development for terminal_fifo, through the unchanged evaluator first in-process with strict JSON and then120 subprocess invocations. Every action digest and all recorded outcome fields agree, and the replication agrees with the corresponding development matrix row. The in-process mean invocation latency was15.03ms and maximum42.17ms during concurrent benchmark work; these are timing measurements, not resource guarantees for all inputs. This episode had zero qualified rewards, so equivalence validates execution rather than demonstrating policy performance.

## Independent production stress review

`research/extended_stress.py` constructs observation-only states without accessing simulator truth and records `results/extended/stress.json`. These are engineering inputs, not sampled simulator episodes or performance seeds. Twelve subprocess checks include fully hard-compatible 200-member pools, wholly undisclosed soft features, diverse valid actor posterior records, ten hard-incomplete members for actual value/two-query asks, malformed version-2 memory, 300 extra actor records, and oversized input.

Diverse actor posteriors reduced cache reuse: fully verified default matching took 6.968 seconds versus 0.332 seconds with homogeneous actor priors. Value and two-query matching took 7.133 and 7.198 seconds; actual ask-stage value and two-query lookahead with ten incomplete members took 8.523 and 7.982 seconds. All six dense cases met the ten-second timeout in this run, but the small margin and lack of a global **scoring** deadline are production limitations. The solver and acquisition optimization are interruptible; upstream construction of the full weighted graph is not. This does not justify a universal timeout guarantee. Maximum observed process RSS was 95.6 MiB; RSS was sampled every 50ms and can miss brief peaks.

Malformed `users`, `snapshots` and `regime_logweights` records returned valid empty protocol responses; extra 300 actor records and oversized input also produced valid responses. However malformed version-2 `date_counts=[0,0]` caused uncaught `ZeroDivisionError`, process exit1, and no valid JSON response in the **development-frozen** executable. This was a real malformed-memory robustness defect, subsequently fixed by the adopted production guard. Normal generated observations and valid policy-generated memory do not contain this record, so the finding does not invalidate recorded simulator rewards, but production completeness cannot be claimed for that archived development executable. The lead was notified before final confirmation. No frozen inference source was edited by this stress review.

## Adopted production-only amendment (separate from the frozen development experiment)

The container stress made the scoring limitation concrete: the original `sequential-extended:1.0` exceeded the evaluator's ten-second timeout on the constructed dense 200-member diverse-posterior match request. It was killed and returned no valid response. Value/two-query ask stress completed in 9.092/8.555 seconds. `results/extended/stress_container_original.json` preserves the exact resource flags and outcomes. These are engineering failures on constructed public inputs; they are not reward-evaluation episodes.

A separately tested production amendment, `research/extended_policy_safe.py`, with the corresponding `research/extended_safety.patch`, adds a seven-second deadline around the complete `decide` call, reserving three seconds for legal fallback and process overhead. Its global deadline exception deliberately derives from `BaseException` so a solver's local `except Exception` cannot swallow it. Nested solver alarms preserve the nearer global deadline. Malformed numeric memory raises `ArithmeticError`, which is now caught. On timeout, unsafe memory, unsupported alarms or non-main-thread signal access, inference returns a legal FIFO hard ask or verified first-fit matching with empty memory. Fallback still prunes permanent declines, unavailable endpoints and repeated dyads, respects the ask budget and rechecks actual observed reciprocal eligibility. It reads no latent fields.

The frozen original remained unchanged while the development matrix was running. Nine production-amendment tests passed, including real global interruption, a global deadline occurring inside the nested blossom timer, malformed zero date counts and actor precision, unsupported alarms, thread fallback, ask budget/declines, repeated/unavailable dyads, and exact normal-action/memory equivalence over a 60-day previously registered development-seed trajectory. `research/test_extended_safety.py` imports the proposal by default; after adoption it can validate the actual executable via `EXTENDED_SAFETY_TEST_TARGET=actual python -m unittest research.test_extended_safety`. Normal equivalence after adoption still requires independent replay against the archived pre-amendment matrix, rather than comparing an executable to itself.

The proposed safety image was built from a temporary minimal context containing the exact proposal renamed to the executable plus the unchanged public helpers and candidate registry. `results/extended/stress_container_safe.json` records source hash and full resource flags. All four actual offline/read-only/two-CPU/one-GiB/64-PID container cases completed with valid JSON within the evaluator deadline: dense matching7.111s, value ask7.194s, two-query ask7.193s, malformed zero date counts0.172s. The two expensive ask cases and malformed-memory case used the legal empty-memory fallback. Dense matching finished its full model before the seven-second policy deadline in that run. Runtime variation remains possible, so the tests support the protective mechanism rather than a deterministic runtime equality across hosts.

## Adoption and final validation status

After all1,056 frozen development episodes completed, the lead archived the original executable as `research/extended_policy_development.py` and adopted the separately tested safety implementation as `extended_policy.py`. `results/extended/production_guard_adoption.json` records old and new code hashes. Selection and confirmation use the guarded executable; model, query and allocation objectives remain unchanged. All28 combined mathematical/protocol and safety tests passed against the actual adopted implementation. The safety normal-equivalence test explicitly imports the archived development executable, avoiding a self-comparison. Guard-regression replay is separately recorded by the lead and should be checked before interpreting development and later-stage candidate results together.

`results/extended/stress_final.json` reran all12 constructed cases against the actual adopted executable while benchmark workers were active. Every case returned valid protocol output with no ten-second timeout. Maximum wall time was7.104s and maximum sampled process RSS95.6MiB. Both expensive ask lookaheads triggered the seven-second guard and used legal empty-memory fallback. The formerly failing zero date-count memory now returned a legal matching with empty memory. Extra300 actor records and oversized input remained valid. These final host stress results complement the guarded proposal image resource-limit checks; image rebuild and final selected-candidate container verification are owned by the lead.
