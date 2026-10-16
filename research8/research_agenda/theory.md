# Full-horizon policy-library rollout with retained continuations

Date: 2026-10-14. Status: proposed research direction; conditional proofs below are not evidence of a simulator win. Author: `/root/policy_theory`; independent reviewers: `/root/w2_critic` and director. Scope: this note only; no episodes, training fits, policy implementation, or edits to closed results. Shell work was source reading and document creation, below the 180 CPU-second allowance.

## 1. Recommendation and the two separate failures it addresses

The strongest tractable next candidate is a small library of complete observation-only policies, evaluated through the last assignment day, with a retained incumbent continuation when switching policies. Its policies include exact frozen G, fixed-score allocation repairs, and cheap contingent multi-day reservation/query options. It simulates policies along trajectories; it does not recursively optimize an action tree at every simulated day. Full-horizon G rollout is a useful control, but **is not sufficient** to discover decisions requiring several future waits.

These are two distinct falsifiers:

* **Missing tail:** W2's declared day-13 case offers AB=.5 now and AC=.9 on day13 with permanent absorption. Twelve future epochs omit AC, so W2 takes AB and loses .4 against the full oracle. Extending an otherwise correct evaluation through day59 addresses this truncation.
* **Weak continuation:** a three-day declared model offers AB=.5 on day0, AC=.4 on day1, AD=.9 on day2; all introductions permanently absorb A, and other actors have no useful opportunities. Full-horizon one-step G rollout values “match now” at .5 and “wait then G” at .4. It takes AB, while a policy that waits twice earns .9. Repeating one-step lookahead does not fix a first action already rejected. A library policy that explicitly reserves A through day1 supplies the missing continuation. These are reduced laws, not claims that simulator pauses occur deterministically.

W2 `bounded.py` addresses weak continuation by recursively optimizing its bounded menu at every future public belief; its cost can expand with branches, epochs and belief support, and its zero tail remains wrong on day13. This note instead proposes a bounded policy library with complete cheap continuations. It sacrifices global optimality for a tractable, testable policy-improvement structure.

The basic rollout/policy-improvement principle is standard; see [Bertsekas's lecture on simulation-based policy iteration](https://ocw.mit.edu/courses/6-231-dynamic-programming-and-stochastic-control-fall-2015/resources/mit6_231f15_lec19/). Multiple-policy POMDP rollout is studied by [Chang, Givan and Chong](https://engineering.purdue.edu/~givan/papers/deds01.pdf). The finite-horizon history-space proofs here specify the additional query, persistence, objective and model-error conditions needed in this repository; they do not import an unconditional guarantee from those papers.

## 2. State, objective and lawful hypothetical information

Let H_t be the complete public history at the beginning of day t, including bounded policy memory when that memory affects actions. Decisions end after day59. A day's action is a **contingent macro action** (A,C): a legal nonadaptive ask package A, followed by the public answer-to-matching map C. C receives only the refreshed public observation H_t^Y and must return a globally legal matching. A controller is a complete sequence of such public-history functions, including its documented unsupported-input and runtime fallbacks.

The random public history is a sufficient information state when kept in full. A compressed memory/belief is sufficient only if justified. The true conditional law used in a theorem is the actual distribution of latent profiles, future arrivals, outcomes, exits and observation releases given H_t. In practice that law is unknown. Sampling latent variables is lawful inside a model; the simulated controller must see only synthetic public observations released by that day. Optimizing separately for indistinguishable hidden particles is clairvoyant and invalidates all the proofs.

Every latent actor profile is shared across its incident edges and history; fresh introduction-specific shocks remain separate. Assignment immediately consumes the dyad. Pending introductions retain their released-history posterior, occupancy and informational effects. q is qualified eventual reward, not pause probability. Exits, busy durations and pause are joint transition variables. Real hard feasibility is always recomputed from actual answers.

For count reward, book at assignment

    r_t(H,A,C) = E[sum of eventual qualified indicators for today's pairs | H,A,C].

Full follow-up makes this equal in expectation to the ultimate count. Already pending rewards need not be counted again, because future policy cannot change their qualification; their feedback still changes future decisions. Stop assignments at59, but resolve/evaluate their qualification through the actual evaluation cutoff. Never discard a day59 introduction's reward merely because its feedback occurs later.

The registered endpoint is Y=100Q/max(1,N), where N is the final arrived-member denominator. A count-improvement theorem does **not** automatically prove endpoint improvement when N is random. For the actual endpoint, use

    r_t = E[100 * sum(today's qualified indicators) / max(1,N) | H,A,C].

The remaining denominator must be modeled through the evaluation definition. An arrival process independent of actions permits paired common-denominator scenarios; it does not remove reward/denominator correlation. All the proofs below work for either additive conditional objective, but one must be frozen explicitly. A convenient unbiased rollout target is the complete realized normalized endpoint from newly initiated introductions, with common pending contributions canceled. In the actual simulator an actor cannot qualify twice: qualifying second responses arrive by date+3 and permanently pause the actor before busy release at date+6. Consequently complete realized Q<=floor(N/2) and Y<=50. This range requires faithful pause semantics. A sum of sequential conditional q values along one sampled path need not satisfy that same pathwise bound; do not use 50 for such an estimator without a separate proof.

## 3. Exact one-step G improvement: useful but limited

Let g denote the complete frozen G policy, including its asks, ties, legal matching and fallback rules. On history space define

    V_t^g(H) = expected remaining objective under g,
    Q_t^g(H,a) = r_t(H,a) + E[V_(t+1)^g(H') | H,a],
    V_60^g = 0.

Let a_t^g be G's contingent macro action and let the candidate menu contain it. Suppose a public policy μ chooses a_t with

    Q_t^g(H,a_t) >= V_t^g(H)

at every history reachable under μ. Then V_t^μ(H)>=V_t^g(H).

**Proof.** At day60 both are zero. If the inequality holds at t+1, then

    V_t^μ = r_t(H,a_t) + E[V_(t+1)^μ]
          >= Q_t^g(H,a_t) >= V_t^g(H).

Backward induction proves the claim. The menu can be tiny and omit the globally optimal action; completeness beyond including a valid baseline is unnecessary for this baseline guarantee. Arbitrary menu pruning does destroy an optimality claim. Exact baseline ties may simply retain G.

More generally, with A_t^g(H,a)=Q_t^g(H,a)-V_t^g(H), telescoping gives

    V_0^μ - V_0^g = E_μ[sum_(t=0)^59 A_t^g(H_t,a_t)].

Thus A_t^g>=-η_t gives loss at most E_μ sum η_t. Strict improvement requires positive total expected advantage, e.g. a positive reachable switch advantage and no negative advantages elsewhere. It cannot be concluded from “G is included.” This theorem explains both safety and the future-wait limitation in §1.

## 4. Fixed policy libraries and the stronger continuation guarantee

Let Π={π_1,...,π_K} be finitely many complete feasible public policies defined at every history, with g in Π. Define F_t(H)=max_j V_t^(π_j)(H). Choose j_t maximizing this value and execute π_jt's current day's macro action. Call the resulting switching policy S.

**Policy-switching theorem.** Under exact conditional values and correct complete continuations,

    V_t^S(H) >= F_t(H) >= V_t^g(H).

**Proof.** At60 all values are zero. Let j maximize F_t. By induction V_(t+1)^S>=F_(t+1)>=V_(t+1)^(π_j) for each public next history. Therefore

    V_t^S = r_t^(π_j) + E[V_(t+1)^S]
          >= r_t^(π_j) + E[V_(t+1)^(π_j)]
          = V_t^(π_j) = F_t.

This proof evaluates each policy through the full remaining horizon but optimizes only over K policy values at the real decision. Simulated days call the selected cheap policy, never recursively call S. Runtime scales linearly in horizon and library size for fixed trajectory count. Inclusion of the twice-waiting policy raises F_0 from .5 to .9 in §1's deterministic witness.

This is related to parallel rollout, but the specification here uses direct policy switching, not an unexplained interchange of expectation and maximization. In particular, E[max_j realized return_j] is a clairvoyant upper envelope, not max_j E[return_j] and not the value of an implementable policy chosen before future observations.

A fixed history-defined library can carry its own simulated memory. Its memory state at an off-policy history must have an explicit public initialization/update rule; one cannot assume that a counterfactual policy was followed since day0 and somehow knows answers it never asked. The next section avoids this issue for locally created reservation policies by carrying the selected suffix explicitly.

## 5. Retained incumbent suffixes: dynamic options without exponential planning

Local options are naturally anchored at the day they are proposed: reserve selected actors until an absolute expiry date, ask a named legal package on specified contingencies, accept an eligible alternative above a frozen threshold, then resume G. Restarting “wait two days” at every replan can postpone forever. Reconstructing the option from scratch can also discard precisely the future action that made it valuable.

Maintain I_t, a complete incumbent policy for the remaining horizon, represented by a small immutable option descriptor plus its current public memory. Initially I_0=g. At real day t:

1. Build a bounded menu containing I_t, exact g, and new fully specified public options. New options include their continuation, fallback and absolute expiry.
2. Compare V_t^π(H_t) to V_t^(I_t)(H_t), using paired full-horizon trajectories. Select J_t only if the registered guard supports its advantage; otherwise retain I_t.
3. Execute J_t's actual ask batch and its specified current-day answer-to-matching function. After observing the next day's public state, set I_(t+1) to the correctly updated suffix of J_t.
4. Reconsider only at the next registered decision epoch; changing the match after answers is permitted only with a separate valid improvement over the committed current continuation.

**Retained-suffix theorem.** Suppose selected policies satisfy

    Δ_t = V_t^(J_t)(H_t) - V_t^(I_t)(H_t) >= -η_t

conditionally at every real history, and the next incumbent is J_t's actual suffix. Then

    V_0^deployed - V_0^g = E[sum_t Δ_t] >= -E[sum_t η_t].

**Proof.** Let B_t=V_t^(I_t)(H_t). Because the current day really executes J_t, its policy Bellman identity gives

    E[r_t+B_(t+1) | H_t,I_t,J_t] = V_t^(J_t)(H_t)=B_t+Δ_t.

Take expectations and sum. B_60=0 and B_0=V_0^g; all intermediate B values cancel. Exact nonnegative switches imply noninferiority, and positive E sum Δ_t implies strict superiority. Randomized selection is handled by conditioning additionally on the policy's selection randomness; fresh rollout samples must be independent of the actual latent future conditional on public history.

Unlike §3, an option's first action can have negative advantage when followed by G; its preserved continuation supplies the benefit. Thus **silently reverting to G mid-option does not preserve this theorem**. Resource/model-selection failure should keep the cheap validated incumbent. An option can itself have a predefined public unsupported-state → G fallback, but that fallback must already be part of its simulated complete policy. Unexpected failure remains an invalid-attempt/production issue; including “G exists” is not a proof that every recovery is harmless.

A retained incumbent can be harmed by model error just like a new option. Initially adopting it requires the same gate, and every switch comparison must assess its current conditional value, not reuse yesterday's unconditional value. It need not be recomputed when no switch is considered; simply executing its cheap suffix remains well-defined.

## 6. A small concrete policy library and query coupling

Proposed first library, requiring a new frozen implementation specification rather than edits to closed R7/R8 artifacts:

| Policy family | Cheap complete continuation | Mechanism and likely failure |
|---|---|---|
| Exact G | Frozen asks and matching through59 | Control and initial incumbent |
| Immediate global/local repair | Frozen score, legal maximum-weight or bounded exchange matching; G asks | Corrects greedy collisions; score misspecification/occupancy may reverse benefit |
| Short reservation | Select a public contested local region; hold specified actors until fixed expiry or a declared observable acceptance condition; keep other matching global; resume G afterward | Captures consecutive waits; speculative future supply can make waiting harmful |
| Reservation with query preparation | Same persistence, plus a complete hard/soft package rule before matching, conditioned only on released answers and public state | Prepares future legal graph; query bottleneck may be absent in real workloads |

At most a few predetermined expiries/thresholds, anchored to public time, should enter the first configuration. No hidden exit deadline, true arrival calendar, family label or generator-derived individual latent trait is allowed. Specify last-day behavior explicitly: no future reservation charge remains, and the option uses its prescribed legal terminal allocator. Holding a positive edge with no conflicting opportunity on day59 is not justified by occupancy after59.

The current library cap and option templates are proposals, not justified optimal hyperparameters. Use one library configuration for research screening; a large threshold sweep is a larger search and must be counted. Tractable inference is plausible because policy execution is cheap; sub-second compliance is unmeasured.

**Query coupling.** A query candidate is a complete pair (A,C), not an entropy score. For the current day followed by option suffix I, its value is

    J_(C,I)(A|H) = E_Y[r(H^Y,C(H^Y))
                        + E[V_(t+1)^I(H') | H^Y,C(H^Y)]].

The same C must execute after real answers. Joint hard/soft packages must fit budget12; a hard bundle costs3, a soft question1. Their costs are budget displacement, not arbitrary reward penalties. All queried answers and declines are drawn jointly with profiles used downstream; a soft answer cannot authorize unresolved hard feasibility. Compare complete packages including displaced alternative asks and exact G package.

A small menu of complete policies avoids 96 query packages × a recursively invoked matching planner. Each trajectory executes one candidate query rule and one cheap matching rule per day. Ask-phase selection stores the selected controller and option state for match-phase execution. The selected descriptor must be validated against the public request and version/hash; raw hypothetical answers never enter memory as facts.

There is also a legitimate cheaper lower-bound design: ask choices improve the baseline's true query Q-value, then a separately certified match-phase rollout improves baseline value pointwise. The phase-expanded policy-improvement theorem proves noninferiority even though the ask evaluator uses baseline matching. But that score is **not** the actual enhanced controller's acquisition value and can miss query/reservation complementarity. The recommended option design scores and deploys one complete policy consistently.

## 7. Model, simulation and tail errors are separate

Write V_P^π for the true conditional value and V_hatP^π for the public learned-model value. Exact policy switching in hatP gives a theorem in hatP only. Average calibration, a good proper score, bootstrap agreement or a small held-out MAE do not establish the uniform decision-conditioned error needed below. Off-policy histories created by reservations are particularly important.

For one selected candidate J and incumbent I, suppose

    |V_P^π(H)-V_hatP^π(H)| <= ε_π(H),  π in {J,I}.

Then Δ_true>=Δ_model-ε_J-ε_I. If L_MC is a valid lower bound on model advantage and e_eval bounds additional numerical/distillation/truncation error in that advantage, the sufficient true-model switch rule is

    L_MC > ε_J + ε_I + e_eval.

No such ε is established by the present repository. A practical model-robustness gate should be labeled empirical/heuristic unless its uncertainty set is proven to contain the true conditional law. If P belongs to a set U and inf_(P in U)[V_P^J-V_P^I]>=0, then true improvement follows; pessimistic value of J compared only against pessimistic value of I is insufficient because their minimizing models can differ. Shared-model paired advantage is the right robust quantity.

A transparent sufficient trajectory bound is available. For a fixed public policy π, suppose the complete true and modeled trajectory distributions can be coupled with disagreement probability at most d_π, including initial posterior, observation releases, rewards and final denominator. For a realized return in [0,B],

    |V_P^π-V_hatP^π| <= B*d_π.

If initial posterior total variation is δ_0 and conditional transition-kernel total variation is at most δ_s uniformly over relevant histories/actions, sequential maximal coupling gives

    d_π <= min(1, δ_0 + sum_s δ_s).

Proof: while trajectories agree, the next mismatch probability is at most δ_s; union-bound the first mismatch. On agreement the return is identical and otherwise its difference is at most B. This is deliberately strong: observed outcome marginals alone do not bound the joint trajectory law, especially for persistent actors and selective delayed labels. Bounds can become vacuous over60 days. Neither copying hidden simulator states nor assuming a convenient fitted model is exact solves this inferential problem.

**Monte Carlo gate.** Choose a winner on selection draws, then use n fresh IID conditional-model paired trajectories for winner versus incumbent. Let D_i=Z_i(J)-Z_i(I) in [-B,B]. Conditional on the selected pair, Hoeffding yields

    L_MC = mean(D) - B*sqrt(2*log(1/δ)/n),
    Pr(Δ_model >= L_MC) >= 1-δ.

This one independent check does not require a menu multiplicity factor. Simultaneously inspecting K same-sample candidate bounds requires at least the corresponding union correction, e.g. log(K/δ). A sequence of real decision checks needs preallocated δ_t with sum δ_t<=δ_total and conditional validity for adaptive histories. Repeatedly redrawing after a failed bound until one passes invalidates the guarantee. Frozen quadrature or a deterministic selected salt is not IID conditional sampling; deterministic replay and probabilistic coverage are distinct claims.

With complete realized normalized return B=50, n=32 and δ=.05, the range-only margin is about21.64 endpoint points. This is enormously larger than a proposed .025 improvement. Common random numbers can substantially lower variance but do not by themselves lower the proven range. Strong small-sample certification may simply never switch. A nominal paired t interval or finite bootstrap gate is a useful separately labeled heuristic, not a distribution-free certificate. Use independent empirical reward evaluation to assess practical value.

For multiple decisions, a clean statement averages over both real trajectories and the algorithm's sampling. Suppose at every history the selection/check randomness has conditional probability at most δ_t of accepting a comparison that violates Δ_t>=-η_t, and Δ_t>=-B always. Then E[Δ_t | history]>=-η_t-B*δ_t, so the retained-suffix telescoping identity gives unconditional expected loss at most sum η_t+B*sum δ_t. This assumes the stated model/evaluation bounds are valid; an unquantified possibility of model misspecification is not covered by δ_t. A union bound also controls failure of any certificate along the adaptive sampled trajectory, but it must not be converted into a policy-value theorem by conditioning the environment on “no failure.” Stronger high-probability statements must specify whether they concern random fitted policies, certificates along a trajectory, or realized reward; those are different objects. Uniform fixed-policy guarantees over all reachable histories would require corresponding uniform error/coverage control.

**Tail.** Full-horizon baseline/library rollouts have no omitted assignment tail. They still require correct post59 reward evaluation. If truncated at τ, with terminal approximation W_τ and |W_τ(H)-V_τ^π(H)|<=e_π on all reached histories, a policy value has terminal error at most e_π, and a paired comparison at most e_J+e_I. Zero terminal value is a lower bound for each policy with nonnegative rewards but not for their difference. In day13's witness the two omitted tails differ by .9. A 12→24-day sensitivity check is useful evidence but is not a60-day bound. Simulation suffix splicing is exact only when full public/policy states and future conditional laws coincide; identical currently available actor sets do not erase different exhausted dyads, pending histories or option memories.

## 8. Computational plan and why it remains research

For K cheap complete policies, n selection trajectories, n_check independent winner/incumbent trajectories, and H remaining days, the upper trajectory-day count is

    (K*n + 2*n_check)*H,

plus current menu construction and validation. Example only: K=8, n=n_check=16, H=60 gives9,600 simulated days. This is a linear workload, not a measured sub-second runtime. Baseline matching/eligibility across200 actors may still make it far too slow. Shared exogenous actor/arrival draws and paired dyad/time randomness reduce variance and can cache invariant computations, but every trajectory maintains its own consumed edges, public releases and action-dependent availability.

Do not optimize different particles independently. Do not couple by freezing action-dependent outcome histories across candidates. A coupling is valid when each candidate's marginal conditional law remains correct; using the same random numbers is a variance-reduction choice and its variance effect should be measured.

A practical development order is: cheap global score repair as control; full-horizon G rollout as tail/transition control; a small persistent-option library to address the future-wait witness; then query preparation only if answer-model and query-pressure evidence support it. This is an ordered mechanism investigation, not four automatically admitted research candidates. If active full-horizon library evaluation exceeds the runtime budget, use a frozen offline-trained policy-value/advantage surrogate only with a separately measured decision-error gate. That introduces another error term and loses exact online expectation. No claim of safety arises from simply distilling a successful teacher.

At day t the selection optimization is over a small explicit policy menu. There is no claim to solve the full POMDP, no guarantee the useful option is in the menu, and no need to exhaust all matchings to establish the conditional baseline guarantee. A stronger continuation can hurt if its predictive model is wrong; promising exact witnesses establish mechanism possibility, not prevalence or net benefit.

## 9. Static fixes, counterexamples and discriminating validation

Static score repairs should remain serious lower-cost competitors. At the last day, exact maximum-weight matching using true conditional endpoint weights maximizes today's expected endpoint. A .9/.05 matching is worse than the alternative .65/.65 matching (.95 versus1.30). General-graph matching or a bounded alternating exchange can recover this gap. But calibrated edge scores and future opportunity are distinct questions: using incorrect scores, maximizing cardinality, or assuming that a static gain implies sequential gain supplies no theorem against G.

Subtracting one common price per matched actor cannot distinguish pairings that cover the same actor set. Independent actor opportunity charges can double-count a shared future partner. Reward-per-busy-day ranking can reject a positive last-day opportunity even though no future assignment capacity remains. Conversely, an actual whole-action rollout can represent shared alternatives, uncertain return, exhausted dyads and globally interacting outside actors. Keeping outside current assignments fixed does not make future outside rewards action-independent.

Minimum independent exact fixtures for the new specification:

1. Day13 omitted-tail witness and day0/1/2 future-wait witness; both must be solved by the relevant full-horizon option, while G-rollout's .5 result on the latter is preserved as an expected limitation.
2. Negative-arrival/no-arrival counterpart: reservation should lose against G in the declared law and the exact selector should retain G.
3. Same covered actors with different joint return outcomes; shared future-partner competition; no-repeat and release boundaries; no action after59 but full reward for day59 assignment.
4. Two indistinguishable public latent branches requiring different clairvoyant actions: a legal controller must share its action until distinguishing feedback arrives.
5. Stateful hold expiry carried across replan; late G fallback destroys the .9 continuation in an explicit case; validated incumbent survives selection-budget overflow.
6. Query package reveals information useful only to a particular reservation/matching policy; score and execute the same controller; also a wrong-controller case where the apparent query gain reverses.
7. Conditional model-error reversal even when population-average calibration is perfect; query/match histories unsupported in training must trigger declared support behavior.
8. Random denominator reversal: two equally likely worlds, N=2 and N=200. Candidate-minus-parent qualified counts -1 and +2 yield mean count gain .5 but mean endpoint change (-50+1)/2=-24.5. A count theorem is therefore not an endpoint theorem. These are abstract attainable objective values, not a claim about the repository's world-size distribution.
9. Complete-pair Monte Carlo selection and independent checking, no repeated-until-positive draws, and trace checks that changing latent model samples cannot directly change a controller action at an identical synthetic public observation.

Model admission must cover joint return/pause/reward and conditional public observation emission, not merely marginal q calibration. Deterministic historical propensities do not provide arbitrary off-policy causal evaluation support. [Laroche, Trichelair and Tachet des Combes](https://proceedings.mlr.press/v97/laroche19a.html) motivate baseline restriction in uncertain regions and give guarantees under their own batch-RL assumptions; those assumptions cannot be presumed for these delayed deterministic-policy logs.

Scientific disposition: recommend the retained-policy-library architecture as the strongest tractable extension to study. The exact theorem is a true-law conditional policy-improvement result; the same algorithm with learned values has only model-relative or explicitly error-bounded guarantees. The actual model asset, supported-state coverage, runtime and simulator reward advantage remain unestablished.
