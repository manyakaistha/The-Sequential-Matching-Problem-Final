# Research direction: a public learned scorer and a small library of complete policies

Research synthesis, 14 October 2026. This package contains source audit, primary-literature review, mathematical arguments and constructed examples. It contains **no new simulator reward experiment, model fit, admitted model asset, or demonstrated winning policy**. Previous research and the W2 negative results remain unchanged.

## Recommendation

Pursue two complementary routes. First, build a compact public-data outcome scorer and test a small family of legal allocation/query policies directly on complete episodes. Second, develop full-remaining-horizon **policy-library evaluation with incumbent continuation**, rather than enlarging the recursive 12-day search tree. The first route can produce an empirical winner without solving the much harder problem of learning an entire simulator. The second provides the strongest conditional improvement theory and a principled route to selective waiting and joint acquisition.

My priority order is: correct weights and missingness; targeted soft questions using genuinely slack ask units; same-score local repair; a small direct policy search; then learned continuation and coupled queries. A large neural model or deeper search is not justified merely by its size. This order is a research judgment, not a measured ranking of untested candidates.

The central hypothesis is that Greedy can be beaten by making **a small number of better-informed decisions where alternatives differ materially**: which hard bundles to unlock, which conflicting qualified-reward edges to use, and when an actor has enough credible future opportunity to justify waiting. Uniformly maximizing cardinality, uniformly waiting, or optimizing an inaccurate score are poor substitutes for those decisions.

## 1. What the existing evidence actually establishes

A new independent audit of all4,608 P4 commit records found a **factor-of-two reporting discrepancy**. Every stored denominator is200; the stored endpoint equals100 times qualified count divided by200. The old report displayed mean qualified counts as though they were MSMI/100. The root independently reproduced the critic’s metric-layer reconstruction:

| Arm | Stored MSMI/100 mean | Old report label/value |
|---|---:|---:|
| G |.343750|.6875|
| Q6 |.378472|.7569|
| P |.376736|.7535|
| A1 |.334201|.6684|

The report also used576 seed-family cells for its t tests, whereas the registered unit is the **96 seed clusters**. Reconstructed exploratory95% cluster intervals give Q6−G=.034722 [−.019380,.088824], P−G=.032986 [−.011551,.077523], and A1−G=−.009549 [−.070001,.050904]. These do not establish superiority of P or Q6, or harm from A1. Do not reuse the old p=.0427 as registered evidence.

This is a read-only reconstruction from committed counts/denominators, with complete cell uniqueness, stored validity, common-world hashes and denominator equality checked. It is **not** a fresh independent reconstruction from every public feedback event or a retroactive confirmation campaign. Preserve the old report and publish a correction; see [root reconstruction](root_metric_check.json) and [independent critique](critique.md). The old portfolio’s no-promotion disposition remains appropriate; its numerical scales and causal prose need correction.

Three causal claims from the mission brief need correction:

* `N` does not legally spend introductions on unknown-hard dyads. `kit.py` rejects missing hard constraints. Its loss is consistent with failing to unlock legal opportunities; the experiment does not isolate all causal pathways.
* The tested A1 configuration contains only `id: A1`. Its implementation reads `config.get('weight_model')`, receiving `None`, and uses soft-agreement counts. It did **not** test maximum-weight matching under calibrated qualified-reward probabilities. A1's negative mean cannot establish that continuation, rather than score quality, is the cause.
* Hard-query answers are immediate. A delayed-family effect is not evidence that hard queries themselves were delayed or uninformative. Downstream dates, timing, allocation changes and uncertainty need separate tests.

W2 proved correctness on its declared small models and exposed a tail failure: a .5 match today versus a .9 opportunity on day13 defeats a zero-tail 12-day planner. Its public entry point still deploys G. The measured subsecond 200-member runtime is **G fallback runtime**, not active full-population planning.

An additional source-and-metric audit changes the acquisition interpretation. **G, P and Q6 recorded zero soft questions in every P4 episode.** The shipped R adapter also uses FIFO hard asks and random matching; it is not a random-soft-query control. The current source files match their frozen P4 hashes. Therefore P4 does not test whether targeted soft acquisition beats the leading hard-only references. Preserve the random-matching R comparator and introduce a genuinely distinct random-soft acquisition control if soft acquisition is tested. See [reference identity audit](reference_source_audit.json).

The descriptive G funnel averaged73.94 assignments,10.89 mutual first acceptances,8.47 happened dates and only.6875 qualified introductions per200-member episode. Q6 averaged.75694 qualified introductions; these are counts, not per-100 rates. Outcome labels are very rare, and improving first acceptance alone is not the primary objective. These stage means are descriptive and not causal mediation evidence; [stored funnel summary](historical_funnel_summary.json).

This makes a cheap, controlled first candidate especially useful: preserve the parent’s hard-query batch, then use **only its unused same-day budget** for a few not-asked soft fields on currently available actors whose observed legal alternatives can change the matching. Package selection is completed before answers. Compare targeted versus random eligible soft filling with exactly the same allocator, and compare both to no soft filling. Never call units slack if the policy displaced a feasible hard bundle. Revealing information to the current agreement-count heuristic is not guaranteed to help; a missingness-aware score and same-controller controls are necessary. This hypothesis is less dependent on future-arrival modeling than a waiting policy.

Source anchors: [P4 report](../../research7b/workspace/research7/reviews/p4_replication_results.md), [A1](../../research7b/workspace/research7/policies/a1.py), [frozen registry](../../research7b/workspace/research7/registry/p4_replication.frozen.json), [statistics](../../research7/STATISTICS.md), [W2 status](../w2/README.md), [simulator contract](../../kit.py).

## 2. What a superior predictive model must predict

The useful target is the **joint eventual qualified outcome**, not similarity, acceptance alone, a date alone, or response propensity alone:

\[
q_e(H)=P(F_e\cap D_e\cap S_e\mid H,\operatorname{introduce}(e)),
\]

where F is mutual first acceptance, D includes a date within30 days, and S includes both positive second intentions within the required three-day date-relative window and observed by day99. The original brief omitted that three-day qualification detail; the actual metric enforces it. Day59 introductions keep their full eventual qualification opportunity.

Use a model ladder, all fitted only to permitted public training histories:

1. **Direct terminal baseline.** Regularized logistic qualified-outcome prediction with few features and strong shrinkage. Features: observed soft agreements/disagreements by field, missing/declined masks, public tenure, observed response history, released timing summaries, and graph opportunity summaries. Opaque IDs, pool identifiers, family labels and source strings are not predictive features. No hidden generator coefficients or hand-coded day35 regime.
2. **Conditional funnel model.** Separate response/acceptance, date timing/happening, and joint second-intention stages, with a direct-terminal comparison. The chain rule is exact only for correctly conditioned factors: P(F|H)P(D|F,H)P(S|D,F,H). Do not multiply unconditional endpoint marginals. Fit the downstream stages on their actual risk sets and marginalize future released histories for an assignment-time forecast.
3. **Joint transition model, only if warranted.** Learn correlated endpoint responses, shared dyad effects, conditional return/availability and pause, released feedback emissions, and anonymous arrivals. This supports planning; a good scalar q alone does not.

A public response-rate estimate can help because repeated response behavior affects both first and second feedback. Strong actor-level shrinkage is essential: many members have few observations, successes pause members, and the reusable population is selected by earlier outcomes. Availability can mean busy, paused or departed; it is not a labeled exit clock. Outcome probability and pause probability are different quantities, because late positive feedback can pause without qualifying.

All training rows must reconstruct the **decision-time** snapshot. A later field value with a timestamp after assignment is unavailable as a feature. Pending feedback is censored, not a negative outcome. Retain mature day99 endpoints for terminal labels. Split whole seed clusters, keeping every family and behavior policy for a seed in the same fold. Report both terminal calibration and ranking in the actual alternative-action regions; average log loss dominated by negatives is insufficient.

The legacy `population` implementation imports generator-prior/regime assumptions through `research/terminal_model.py`. Preserve it as its frozen benchmark, but do not relabel it a new empirically learned public model. See [model audit and implementation design](model.md).

## 3. A tractable theory for improvement over a fixed policy

Let B be a fixed complete legal policy, including its query and matching phases. Work with public histories H and the true conditional law of their future evolution. The safest objective definition is terminal U=100Q/A (zero if A=0), including day99 follow-up. It avoids confusing expected counts with expected ratios when future arrivals A are uncertain.

For a legal candidate action a, define

\[
Q^B_t(H,a)=E[U\mid H, a, \text{then follow }B],\quad
A^B_t(H,a)=Q^B_t(H,a)-Q^B_t(H,B(H)).
\]

If every decision uses an action with nonnegative true baseline advantage, the finite-horizon performance-difference identity gives noninferiority to B. Strict positive advantage on a set reached with positive probability gives strict improvement. With uniform action-value error at most epsilon, an estimated margin exceeding2epsilon is sufficient for a nonnegative true advantage. These are **conditional mathematical statements**, not a certificate for an unvalidated learned model.

A crucial limitation: full-horizon *one-step* rollout with G afterwards still misses coordinated waiting. In the four-actor example AB=.5 today, AC=.4 tomorrow, AD=.9 the next day, with absorbing assignments, waiting once then G is worth .4. One-step rollout chooses .5, while waiting twice earns .9. Longer simulation alone does not repair a weak continuation controller.

The proposed solution is a finite library of **complete public-information policies**, including a few multi-day hold rules. For a fixed library Pi and exact conditional values, choosing the first action of argmax_pi V^pi_t(H) at every epoch gives a policy at least as valuable as every library member. The proof is backward induction: the next-step library maximum dominates the chosen policy's own continuation. This is policy switching, an established result; our contribution would be an admissible, efficient matching-specific implementation and empirical evidence, not invention of the theorem. [Chang, Givan and Chong](https://engineering.purdue.edu/~givan/papers/deds01.pdf)

For locally created stateful options, retain the selected option's suffix as an **incumbent** at the next epoch. Compare new complete policies against that suffix. On an estimation/work cap retain the legal incumbent, not an unrelated freshly reset rule. Otherwise repeated replanning can abandon the future waiting that justified the original choice. Always include G initially; experimental versions using Q6 as the initial incumbent need their own exact parent control.

Joint query/match decisions can be a one-day macro: choose a complete nonadaptive query package A and a public answer-to-matching controller C before answers; execute C on the actual refreshed observation. Evaluate that macro and its committed continuation. Never choose the package after seeing sampled same-day answers. Detailed proof, bounds and limitations are in [theory.md](theory.md).

## 4. Reservation values: when waiting can help

For an isolated actor u with disposable partners, absorbing assignments and independently declared future offers, let W_t(u) be optimal value before seeing today's offer X_t. If s_t(u) is survival to tomorrow,

\[
W_t(u)=E[\max\{X_t,\ s_t(u)W_{t+1}(u)\}],\quad W_{60}=0,
\qquad \tau_t(u)=s_t(u)W_{t+1}(u).
\]

Reject an available offer q exactly when q<tau_t(u), with ties resolved by a declared convention. This is an exact threshold in that restricted model. For example, tomorrow's .9 opportunity appearing with probability p, survival .8 and no other opportunity gives tau=.72p. Reject today's .5 only if p>25/36. At p=.5, wait value=.36 and matching wins; at p=.9, wait value=.648 and waiting wins.

For actual general-graph matching, use a **whole-action** reservation comparison. Holding u and v instead of assigning e is justified only when the difference in conditional continuation values exceeds the immediate expected qualified reward, accounting for both actors, their other partners, the exhausted dyad and future query choices. Two endpoint prices need not add: if u and v both want the same future actor w, counting w's benefit twice is wrong. A vertex-price approximation is a cheap candidate score, not an exact Bellman reduction. Full day59 immediate allocation has zero remaining introduction opportunity cost; optimize conditional eventual reward among legal current matchings rather than penalizing late assignments.

Waiting cannot be guaranteed to beat G in every admissible environment: two worlds can share today's entire public history but have different future supply/exit laws requiring opposite decisions. Correctly calibrated public predictions, or an empirically useful robust heuristic, must supply the distinction. The dynamic-matching literature reinforces this limitation: its dramatic gains from patience rely on departure information that our observation contract does not supply. [Akbarpour, Li and Oveis Gharan](https://web.stanford.edu/~mohamwad/DynamicMatching.pdf)

## 5. Concrete candidate architecture

### Fast empirical route

Use a low-dimensional transparent score with learned soft-field contributions, explicit missingness, heavily shrunk response history, and at most a few public graph features. Compare:

* score-greedy;
* local alternating-path/cycle repair under exactly the same score;
* one occupancy/opportunity penalty with a time taper to zero at day59;
* a bounded query-template choice coupled to that allocator.

Tune at most eight predeclared configurations, including the unchanged parent, on training episodes with a paired terminal-reward objective. Freeze a separate selection set before tuning. This is direct policy search; it does not need to claim the score is a probability or learn hidden transition parameters. Use equal compute and seed schedules across configurations. Do not optimize millions of coefficients against rare rewards or use repeated peeks at the final test. Finite random search is a reasonable control, not a guarantee of finding an optimum. [Bergstra and Bengio](https://www.jmlr.org/papers/v13/bergstra12a.html)

### Principled continuation route

Construct at most12 globally legal candidates: incumbent; same-score repair; alternate-query/allocator combinations; and a few selective hold options with explicit expiry, release thresholds and day59 behavior. Do not require an entire connected component to contain at most6 actors: that can make a policy inert on large graphs. Bound the actors changed locally, preserve outside assignments without endpoint conflicts, and evaluate the complete resulting policy on the modeled population. If population approximation is necessary, retain boundary effects explicitly and test its error; silently ignoring neighbors is not sound.

Initially evaluate full remaining horizons **offline** with a public learned generative model. At most8 policies ×32 shared particles ×60 days is15,360 policy-days per decision; at200 members, naive O(n²) edge rebuilding approaches306million pair checks before constants. This is a workload estimate, not subsecond readiness. Cache invariant feasibility, batch score features, use small cheap policies, and profile active planning. If still too slow, learn *paired policy-advantage* predictions or distill the selected controller, then re-evaluate the deployed distilled policy independently.

Public arrival particles derive from deduplicated `arrived_day` counts, including days with zero arrivals, and training-only public initial profiles. Use a shrunk count model with uncertainty, a recent-rate alternative and a no-additional-arrival stress scenario; cap total arrivals at200. Day0 needs a declared training prior or conservative fallback, not invented certainty. Never resample a member's later fully revealed profile as its initial profile. Simulated future IDs are internal opaque tokens, never actual unseen members.

Keep separate simulator-internal latent samples and the observation emitted to each simulated policy. Sampled future actors, return clocks, shared shocks and departures must remain invisible until their public consequences are released. Condition pending introductions on all feedback already observed. Nonmutual busy ends at assignment+8; mutual-date busy ends at date+6, including cancellation. Qualification, released pause and return must be jointly consistent. Fit unknown laws from public data; contract mechanics do not license importing generator probabilities.

For each candidate and model m, estimate a paired difference Delta_m=V_m(candidate)-V_m(incumbent) on shared particles. A robust heuristic is min_m Delta_m minus sampling and approximation allowances. Do **not** subtract separately pessimistic values min_m V_m(candidate)-min_m V_m(incumbent), which need not compare the same environment. Ensemble disagreement is a warning indicator, not proof the true model lies in the ensemble.

Uniform worst-case simulation bounds are likely too conservative for tiny gains. As an illustration, U lies in[0,50] under the simulator's pause-on-success rule. For8 fixed candidates,64 independent paired simulations and failure level.01, a union-bound Hoeffding radius for differences in[-50,50] is about24.01 MSMI/100. Shared particles may greatly reduce empirical variance, but do not justify replacing the global range with a local actor bound without a coupling proof. This is why empirical policy confirmation remains essential, and why the theorem must not be marketed as a practical statistical certificate. Model-error accumulation is a known issue in model-based policy optimization. [Janner et al.](https://proceedings.neurips.cc/paper/2019/file/5faf461eff3099671ad63c6f3f094f7f-Paper.pdf)

## 6. Query selection must be evaluated as a package

For deployed post-answer controller C, evaluate

\[
J_C(A\mid H)=E_Y[V^{C,\,continuation}(H,Y;A)],\qquad \operatorname{cost}(A)\le12.
\]

Compare complete feasible packages of hard bundles (cost3) and soft questions (cost1). Do not simply choose by entropy, unlocked edge count, or single-query gain/cost. Two hard bundles can be complementary: neither endpoint alone makes a dyad legal, while both unlock it. A correct nonadaptive menu therefore includes paired hard bundles as well as hard/soft mixtures. Start with immediate matching value, then add continuation only after its own controlled benefit is established.

Soft information can have high value when it changes which of several incompatible matchings is preferred. It has no value for a fixed single action if it only refines an unbiased probability estimate and nothing downstream can change. Do not reward apparent improvement caused solely by maximizing Monte Carlo noise. Use coherent answer laws, identical evaluator/controller semantics, baseline package inclusion and independent samples or uniform comparison bounds after adaptive package generation. Nongreedy acquisition research supports testing complementary packages; its guarantees do not automatically apply to this graph. [Valancius et al.](https://proceedings.mlr.press/v235/valancius24a.html)

## 7. Experiments that distinguish the explanations

This is a proposed new development program, not a changed R7 registration or a launched campaign. Before running, freeze code, provenance, exact arms and fresh disjoint seed manifests. Proposed finite scope:

| Stage | Work | Decision |
|---|---|---|
| E0: audit and headroom | Complete public-event validation of the newly reconstructed96-cluster P4 metric correction; audit public data maturity; log same-state score/optimizer disagreements and legal exchange opportunities on designated development histories | Establish where there is action-changing room; no causal gain from replay alone |
| E1: model/data | If no authorized mature training archive exists, collect32 training +16 validation seed clusters ×6 families ×3 behaviors =864episodes | Fit the small model ladder; reject leakage, incoherent timing, or unsupported probability claims |
| E2: narrow development | Up to8 direct-search configs, including parent, on32 training clusters ×6 families =1536episodes, separately capped; reuse exact committed control cells only under a registered compatible design | Select at most2 mechanism families; all searched configs remain reported |
| E3: fresh selection |16 fresh clusters ×6 families ×up to8arms =768episodes; G,Q6,P plus admitted candidates and their necessary own-parent controls | Development selection only, no superiority claim; fewer candidates if controls do not fit |
| E4: replication |48 fresh clusters ×6 families ×up to8arms =2304episodes, frozen after E3 | Require repeatable gains versus own parent and strong references, not just versus G |
| E5: confirmation |One frozen candidate against complete G,N,R,P,K,Q6 panel; size from preconfirmation seed-cluster variance | All simultaneous lower bounds positive, complete legal grid; otherwise no panel winner |

The development ceiling above is5472episodes if every stage is needed. At an illustrative20CPU seconds/episode this is30.4CPU hours before fitting, log handling or slower candidates; forecast from a measured smoke job before scheduling. It is not a cost commitment or a claim the host can run it overnight. Stop a mechanism at its failed gate rather than automatically spending the entire ceiling. At most3 simulation processes globally, separate from agent slots. E1 training trajectories and E2 configuration evaluations are different cells unless their exact policy/world/config identities match; no casual reuse of test worlds.

Training behavior set should include G, Q6, and a predeclared randomized legal near-tie/query-template policy. Log full package/controller selection probabilities and decision-time snapshots. Such logging improves coverage; it does not turn dependent introductions into independent randomized trials. Historical deterministic propensity=None logs cannot identify arbitrary alternative policies by inverse propensity or doubly robust estimation. Use complete direct policy episodes for final value. [Jiang and Li](https://proceedings.mlr.press/v48/jiang16.html)

Own-parent contrasts must isolate each mechanism: same queries and score, change only solver; same allocator, change only scorer; same scorer/query package, change only continuation; same allocator, change only query acquisition. The frozen panel P remains distinct from a new public-data scorer. A combined winner without these contrasts does not establish why it worked.

For confirmation, carry forward the seed-cluster endpoint and multiplicity logic in R7 as an explicit new registration. Existing planning calculations require roughly1107clusters at assumed paired SD.30 and true+.05 against every comparator under their conservative joint-power rule. This is not a required size for exploratory selection and not a forecast of a true effect. A smaller observed effect or stronger minimum-effect claim can be much more expensive. Do not launch confirmation until empirical effect/variance and resource forecasts justify it.

## 8. Falsification before promotion

The independent rational script in this folder checks: static exchange (.6 versus .8); coordinated waiting (.5 versus .9); day13 tail; arrival-risk reversal (.36 match versus .648 wait); joint hard-query complementarity; and shared-partner double counting. These are declared examples, not simulator outcomes. Reproduce with `python3 research8/research_agenda/check_theory_examples.py`.

Extend implementation checks to: hidden samples yielding identical current observations must yield identical actions; no arrivals beyond59; full final-day credit; no repeated dyads; budget/disjointness/availability; pending no-response not yet failed; declined versus False; canceled dates' occupancy; late-positive pause without qualified reward; correlated endpoint outcomes; previously exhausted dyads; real fallback on runtime caps; retained incumbent suffix; action ties/relabeling sensitivity; dense200-member active planning. The final benchmark must run the **deployed** controller, not only its offline teacher.

Abandon or simplify a candidate if useful differences are too rare, validated paired advantages remain small relative to model error, benefit disappears under equivalent tie handling, or fresh own-parent comparisons fail. No amount of correct toy arithmetic can substitute for this evidence.

## 9. Ideas considered but not first priority

Deep global reinforcement learning and graph neural networks have large action spaces, sparse terminal rewards and substantial tuning costs; their added representation is unearned until compact models fail on enough mature public data. Endpoint response models are useful but cannot alone capture reciprocal shared shocks. Unsupervised persona imputation cannot create information absent from observed fields. Thompson-style exploration is useful only when actors return and timely feedback changes later decisions; success removes its own subjects. Model-free direct search in a small parameter space remains a practical competitor.

Decision-focused learning is attractive once useful labels/teachers exist: train for the ordering of competing actions rather than overall prediction error. But unchosen dyad rewards are unobserved, so full-cost training targets from a learned model are pseudo-targets, not ground truth. [Elmachtoub and Grigas](https://arxiv.org/abs/1710.08005)

Safe policy improvement suggests retaining baseline behavior where data are sparse. Its published guarantees have explicit MDP/support/estimation assumptions and cannot simply be attached to this large partially observed graph. [Laroche et al.](https://proceedings.mlr.press/v97/laroche19a.html)

The research deliverable is a plausible path with precise reasons it could succeed and tests that can refute it. A strict universal guarantee against G is unavailable; a conditional policy-improvement theorem is available, and an empirically superior observation-only policy remains an open, testable objective.

## Final integration decision

The director adopts the proposed864-cell public collection, at most8 total direct-search configurations including parent,16-cluster fresh selection and48-cluster replication with up to8arms and all necessary own parents. The critic’s earlier48/96/128-stage and12-arm alternative remains archived in `critique.md` and is not adopted. None of these counts is a launched registration; exact hashes, seeds, model recipes and resource forecasts must be frozen before execution.

Independent final review is recorded in [final_review.md](final_review.md). The predictive specialist delivered its revised draft but its final follow-up ended at a usage limit; the completed draft was retained and the separate final reviewer checked the integrated package. No model substitution or experiment was silently performed.
