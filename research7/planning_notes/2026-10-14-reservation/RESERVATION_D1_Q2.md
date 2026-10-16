# Reservation matching, D1 and Q2: reviewable research specification

Date: 2026-10-14. Status: proposed specification, not an implemented or admitted policy. No fitting, official episodes or confirmation were launched. Prior artifacts are unchanged. Exact reduced-model arithmetic is distinguished from simulator evidence throughout.

## 1. Evidence and corrections that govern the design

Sources: `research7/STRATEGIES.md`, `research7/TEST_SPEC.md`, `research7/STATISTICS.md`; governing `kit.py`; `research7b/workspace/research7/runtime/{interfaces,invocation,runner}.py`; P4 `reviews/p4_replication_results.md`, `registry/p4_replication.frozen.json`, and `policies/a1.py` under the 7b workspace.

The P4 report supports the supplied descriptive means: 4,608 episodes = 96 seeds × six families × eight arms; each arm has 576 cells. Q6 .7569, P .7535, Q1 .7535, G .6875, A1 .6684, K .6250, N .2049. No new candidate passed its reported gates. These are report-derived numbers; this task did not reconstruct raw cells.

Three corrections prevent invalid conclusions:

1. Frozen statistics treat **96 seed clusters**, averaging six family contrasts within each seed, as inferential units. The P4 report's 576-cell t statistics are not the registered cluster analysis. Its quoted p=.0427 for P–G is not a confirmation certificate. Recompute uncertainty from closed raw clusters before using it inferentially.
2. P4's A1 configuration is only `{"id":"A1"}`. In `a1.py`, `config.get('weight_model')` is therefore `None`, bypassing the population branch and selecting observed-soft-field agreement counts. The tested A1 is not the promised population-terminal-value solver. Retain its identity as **A1-soft**; call the proposed frozen population-probability solver **A1-P**. Never silently relabel the old result. The old result does not identify continuation omission as its cause.
3. The API is `decide(request, config)`, with memory inside request; hard invocation cap is 10 seconds and memory cap 1 MiB. **Sub-second execution is the user's stricter new admission requirement**, not an established R7 guarantee. The existing 32-particle planning caps are operation bounds, not runtime measurements.

“No asks loses substantially in this experiment” is supported descriptively. “Queries are mathematically essential in every legal world,” “cardinality always harms,” and the supplied causal explanation of A1 are not theorems. In particular, the simulator rejects unverified hard-ineligible introductions; N primarily cannot unlock the legal graph, rather than legally spending introductions on unresolved hard failures. Hard answers are immediate even in delayed worlds; delayed downstream dates/feedback are different.

## 2. Exact reservation condition and the limits of actor thresholds

Let H be the refreshed public history, P its exhausted dyad set, and L(H) its legal full matchings. Define

    r(H,M) = Σ[e∈M] q_e(H)
    Q_t(H,M) = r(H,M) + E[V_(t+1)(H') | H,M]
    V_60 = 0.

Here q is the conditional probability of **eventual qualified** MSMI: mutual first acceptance, a happened date within 30 days of assignment, and both positive second intentions within three days of that date, released by the observation cutoff. Book each new introduction's expectation once. Pending reward is not booked again, but pending information/occupancy remains in H'. Day59 retains full eventual q.

For a baseline B containing e=(u,v), let B−e keep every other assignment unchanged. Holding that pair instead is better precisely when

    q_e(H) < E[V_(t+1)(H'_hold) − V_(t+1)(H'_match)] = T_t(e;B).

Both next histories include all other actors, other matches, future disclosure, exits, and the consumed dyad only on the match branch. This is an exact deletion comparison in the specified belief model. It is not a global optimality certificate. A globally optimal policy omits e when

    max[M∈L(H): e∉M] Q_t(H,M) > max[M∈L(H): e∈M] Q_t(H,M).

To **hold actor u entirely**, replace those conditions with u unmatched versus u matched. Omission of one edge may instead mean matching u to somebody else. Ties use the registered parent. No universal partner-independent actor threshold exists for a general dynamic graph.

A clean tractable scalar threshold does exist under a restricted model: actor u has no reuse after accepting; partners are disposable and never compete with other actors; future offers are independent conditional on the public state; survival over the next step is s_t(u); no information benefit or query bottleneck is omitted. Let X_d(u) be the best feasible qualified reward offer on day d (zero for none), with public-model law F_d. Set W_60(u)=0 and

    W_d(u) = E[max{X_d(u), s_d(u) W_(d+1)(u)}]
    τ_t(u) = s_t(u) W_(t+1)(u).

Accept q>τ; hold q<τ. τ_59=0. With a Bernoulli offer of quality a and arrival probability α_d:

    W_d = (1−α_d)s_d W_(d+1) + α_d max{a,s_d W_(d+1)}.

This backward O(60) recurrence proves the threshold by comparing accept value q with wait value τ, then induction. A two-day example: q=1/5 today, tomorrow quality4/5 with probability1/2 and survival1 gives τ=2/5, so hold. With probability1/10, τ=2/25, so match. This is an exact reduced-model result, not an empirically identified simulator arrival law.

With reuse, if the disposable partner has no independent continuation, a separable reduced model instead uses

    accept_e = q_e + R_t(e)
    τ_t(u;e) = s_t(u)W_(t+1)(u) − R_t(e),

where R_t(e) is the expectation of post-return marginal opportunity with dyad e consumed, including pause/exits exactly once. This is generally **edge dependent**. Only when R is independent of offered q and partner and the accept value has single crossing does it become a scalar threshold. Do not multiply survival outside an expectation already integrating exits. Do not jump to return day using the full system V and lose rewards earned by unrelated actors in intervening days. D1 uses the one-day whole-state transition, avoiding both errors.

Actor prices are useful menu priorities, not the decision rule: Σ(q_uv−λ_u−λ_v) has the same price deduction for every matching covering the same actors; shared future alternatives make marginal costs nonadditive.

The Bellman objective above maximizes expected introduction **counts**, consistent with STRATEGIES. The reported endpoint is E[100Q/A]. When final arrival count A is random, these objectives need not coincide. An exact endpoint controller would book E[100·I_e/A | H,assignment] instead of q_e. Because arrivals are policy-independent, denominator weights can be shared across complete scenario comparisons, but correlation with reward still matters. Register count-based planning as a surrogate and test the actual per-100 endpoint. If weighted planning is used, model the remaining denominator through day59 even when action rollout truncates at12; do not claim a count theorem proves ratio improvement.

## 3. D1 architecture

### Parent, menu and locality

Implement a separately frozen A1-P with explicit probability asset and `maxcardinality=False`. For diagnosis include same-score greedy P_A1, unchanged G, and A1-soft. D1's own parent is A1-P with identical asks, score asset and solver/fallback. P_A1 shares the A1-P probability asset, quantization and ties; frozen historical P remains a distinct reference unless source/config/asset hashes prove equality. A G-seeded variant would be a different registered policy, not an informal runtime choice.

On the refreshed match state compute validated parent B and legal G. Build a deterministic region:

* Seed the B edge with most unused feasible or potentially feasible incident neighbors, tie by canonical opaque-ID ordering. Add at most two adjacent B edges in frozen-score order. No more than six actors may change assigned partner/availability in any candidate.
* Boundary = other arrived incident feasible/unresolved-hard neighbors plus represented pending-return alternatives. Audit all incident possibilities. At most six boundary actors; a boundary actor used in an exchange also counts toward the six changed actors. If a boundary actor's parent partner would change, include that partner too. Reject overflow; do not clip a graph and call it closed.
* Keep all outside parent pairs fixed at the current step. Retain outside actors and their public state in future global rollouts; locality of the first-action menu does not imply dynamic independence. Anonymous arrivals can connect the region and outside actors. If global effects cannot be represented within the fixed work allowance, use parent.

Allocate at most12 full actions: (1) parent, (2) G if its entire symmetric difference fits the region, (3–6) up to four legal alternating paths/cycles or replacements, (7–10) up to four deletions/single-edge replacements, (11) empty local replacement, (12) one additional deterministic exchange if available. Empty local replacement means B_outside stays matched. Deduplicate and globally validate every action. Exchanges involving positive-score edges can beat simple deletion; include both. Empty parent and no feasible edge returns immediately. Unsupported open regions return parent, and audit rejection/disagreement denominators are retained.

### Public arrival particles

There is no `seen_day` wire field. Use public `arrived_day`; memory may store first-seen day as an internal alias. Deduplicate all observed member IDs, count a day's arrivals once across ask/match invocations, include days with zero arrivals, and never infer arrivals from available-pool change.

A baseline declared model is λ~Gamma(a0+Σc_d,b0+n), N_future,d|λ~Poisson(λ); draw λ once per particle to retain shared-rate uncertainty. a0,b0 and any rolling window are frozen public-training choices. No fitted prior is present merely because the formula is written. Stationarity is an approximation; compare registered zero-arrival, low/high-rate and recent-window scenarios offline. A history with no arrivals and a0>0 can predict arrivals: this is explicit prior uncertainty, not observed evidence. Unsupported prior/profile states fail closed to parent; zero-arrival model must generate zero. Cap anonymous actors at 200 minus already arrived count and stop arrivals after59; record cap saturation and reject unsupported saturation rather than claim a known remaining schedule.

Anonymous future actors are drawn from a frozen **public-data** joint profile/missingness/disclosure model, including their initially revealed fields. Do not copy latent generator parameter tables, decode IDs, condition on family, or read a future calendar. Future identities are particle-local opaque tokens. Persistent actor draws are reused on every incident edge; fresh shared dyad shocks are introduction specific. Departure law is a public-trained survival assumption, not the simulator's private exit allocation. Sample conditional on present availability/history; unavailable status alone is not a known exit or pause.

Particle randomness uses fixed policy salt, public day/phase, draw index and canonical actor positions. IDs are used only for equality/canonical tie ordering; their string structure never enters inference. Maintain a rename test with distinguishable public features to detect ID-derived scoring while allowing documented tie differences.

### Occupancy and information transitions

At assignment add the dyad to exhausted set immediately. Generate a **joint** outcome/return/feedback scenario conditional on public features; q and pause cannot be unrelated independent coin flips. Qualified reward implies mutual positive second intentions and therefore eventual pause, but pause can occur without qualified reward (late intentions or late date).

1. Nonmutual first-response branch: unavailability until assignment+8, including early explicit rejection. Each response is exposed only on its modeled released day; no-response becomes mature at its deadline.
2. Mutual first-Yes branch: modeled date day D; unavailability until D+6, including cancellation. It is six days **after the date**, not six after introduction.
3. If date happens, release individual second responses at sampled days. Both positive responses create permanent pause only when both have been publicly released. Late positive responses may pause without contributing qualified MSMI. Otherwise surviving actors return at D+6.
4. Exits, pause and busy status jointly determine availability. All arrived members remain in public members even after exits, so disappearance is not exit evidence. Busy clocks/outcomes inside a particle are not supplied to its controller; only the synthetic public observation and released events are. Real hidden timers are never read. Previously pending introductions require a posterior conditional on current released history/unavailability, not a restart of their original unconditional law.

Score current action by Σq, then up to h=min(12,59−t) **future** action epochs. At each epoch use frozen FIFO asks, expose only those answers and scheduled feedback, refresh public eligibility, then frozen A1-P allocation with its recorded bounded-solver fallback. No recursive planner. Book expected qualified reward once per newly assigned dyad. Current/past pending reward is excluded from future sums. No actions after59. Tail is zero after12, expressly an approximation; pending occupancy still affects any decisions before truncation.

Selection uses32 common scenarios for all≤12 actions; independently salted32 scenarios compare selected action with parent. Maximum5,376 modeled future step evaluations, plus current construction and validation. Score asset, model coefficients, solver tie rules, salts and caps freeze before evaluation. Compare12 versus24 horizons and pessimistic transition/arrival models offline on examined states only; existing strategy gate rejects >10% switch reversals. A day59 D1 based on A1-P must return the static parent except truly tied actions. A positive edge can still be omitted for a competing better edge; it must not be omitted solely for future occupancy that no longer has decision value.

## 4. Q2 and continuation-consistent querying

Q2 as registered uses the **actual deployed A1-P** after answers, not an optimal oracle while deploying G. Its objective is

    J_C(A|H) = E_Y[r(H^Y,C(H^Y))],  C=A1-P.

D2 is the separately gated integration:

    J_C^tail(A|H) = E_Y[r(H^Y,C(H^Y)) + modeled continuation], C=D1.

Original Q2's immediate objective must not be relabeled continuation-consistent. D2 requires D1/answer-model fidelity first and a frozen value surrogate/cache; never invoke32-particle D1 recursively for each query branch.

Compare **complete feasible packages**, not an entropy score or q gain per cost. A hard bundle h costs3; a set S of≤3 soft asks has the same maximum cost. Holding the remaining package B fixed,

    Δ(B,h,S) = J_C(B∪{h}) − J_C(B∪S).

Hard wins if Δ>0 under the guard, soft wins if Δ<0; both may be chosen when budget allows. Include the best displaced alternative package. There is no reward penalty of “three points” for a hard query and no carry-forward of unused units.

Shortlist≤8 eligible hard actors and≤4 named soft actions on≤4 actors. Exhaustive hard k≤4 packages have71 possibilities when exactly four are selected from eight, including a separately inserted FIFO control; across all cardinalities there are163 subsets, so do not incorrectly call71 an exhaustive mixed search. Restrict complete mixed packages to96 by a fixed deterministic rule, include exact FIFO+A1-P, Q6+A1-P and no-ask controls, and retain omission counts. This is bounded-search approximation, not globally optimal acquisition. Existing initial soft shortlist fields are goal, pace, lifestyle and conversations; other fields require a new frozen configuration.

Sample one joint actor profile per particle, preserving observed values, known False and declines. Candidate answers include disclosure failure/decline. Revealing a soft answer can change a qualified probability estimate, never verify hard eligibility. Hypothetical hard answers authorize hypothetical pairs only. After real answers, recompute **real** public feasibility from scratch and deploy the same C. Correlated actor attributes and shared edge endpoints cannot be redrawn per incident edge.

Use32 selection and32 independent winner-parent comparison scenarios. Q2 itself requires up to3,136 A1-P branch evaluations (3,072 selection plus64 checks); solver/cache cost counts against the sub-second target, and its speed is unresolved as well. D2's≤96×32+2×32=3,136 branches must call a cheap frozen surrogate, not nested rollout. Existing surrogate gates: held-out value MAE≤.01, ranking agreement≥90%, false-positive switch≤5%; teacher evaluations use independent draws after action selection. These are model fidelity gates, not real reward guarantees.

## 5. Finite-sample bounds and what can actually be proved

For fixed chosen action a versus parent b let D_i=Z_i(a)−Z_i(b) on independent check scenarios, D_i∈[−B,B]. Hoeffding gives a distribution-free **model-sampling** lower bound

    L_model = mean(D) − B sqrt(2 log(1/δ)/n).

A finite menu selected on another independent draw set does not require a menu multiplicity factor for this single check. Repeated checks/resampling until positive invalidate that claim; freeze one check. A simultaneous selection-set bound over K alternatives uses log(K/δ). Derive B from the maximum rewards bookable within the capped represented trajectory, not observed sample extrema or the number of changed actors. With200 actors and13 assignment epochs a deliberately loose bound is B=1300 for count reward; even a much smaller valid bound may make n=32 useless. Do not increase draws, narrow B or relax δ after a failed guard.

Fixed deterministic quadrature particles do not satisfy the IID theorem. Frozen pseudorandom replay permits reproducibility, while a sampling guarantee is over the declared independent random draw generation, not a guarantee conditional on one selected salt. A nominal paired t lower90% bound reproduces the strategy's heuristic margin check but is not a finite distribution-free certificate. Explicitly freeze either a heuristic mode or a certified-model mode before experiments. The latter returns parent whenever its bound is nonpositive; it may never switch with these budgets. Model approximation bias remains separate: if uniformly |Q_true(a)−Q_model(a)|≤ε for both actions, then true advantage≥L_model−2ε. A model certificate requires L_model>2ε plus a separately bounded tail/action-evaluation error. No such ε has been established. A good calibration average is not this uniform guarantee.

Exact full-horizon rollout with true transitions and exact continuation of an included parent can yield model policy improvement; truncated misspecified belief rollouts do not inherit that theorem. See Bertsekas, [Rollout lecture](https://ocw.mit.edu/courses/6-231-dynamic-programming-and-stochastic-control-fall-2015/resources/mit6_231f15_lec9/) for the exact/approximate distinction. This proposal proves selected reduced-model decisions, not superiority in the six simulator families.

## 6. Concrete Python production specification

Authorized next implementation would use standard library plus numpy/scipy/networkx only; no network or external APIs. Proposed separate files: `public_state.py`, `belief.py`, `transition.py`, `menu.py`, `continuation.py`, `reward_acquisition.py`, and bounded fixtures. Do not edit the existing frozen policies.

Internal interface `choose(observation,memory,phase,frozen_config)` returns `(action,new_memory,status)`; adapter signature remains `decide(request,config)`. Ask phase returns exactly `{'asks': [...], 'memory': ...}`; match returns exactly `{'pairs': [[u,v],...], 'memory': ...}`. Never send status as an extra wire key. Persist status inside bounded memory/approved recorder channel. Invalid private-key requests raise protocol failure at the boundary rather than being silently sanitized into a different request.

Illustrative control flow, a specification rather than runnable implementation:

```python
def decide(request: dict, config: dict) -> dict:
    public = validate_public_request(request)  # strict schema; private keys fail
    phase, state = public['phase'], public['state']
    mem = load_bounded_episode_memory(public['memory'], config)
    update_public_history_once(mem, state)    # dedup days, actors and events
    action_key = 'asks' if phase == 'ask' else 'pairs'
    fallback = validated_frozen_G(state, phase)
    try:
        work = DeterministicWorkBudget(config['caps'])
        if not assets_supported(state, config):
            raise PlannerUnavailable('unsupported public-model state')
        if phase == 'ask':
            action = choose_complete_query_package(state, mem, work, config)
        else:
            parent = bounded_A1_P(state, work, config)
            menu = build_global_legal_menu(state, parent, work, config)
            action = guarded_joint_rollout_choice(state, menu, work, config)
        validate_real_action(state, phase, action)  # sampled fields never used
        output = {action_key: action, 'memory': compact_memory(mem)}
        validate_wire_limits(output)
        return output
    except PlannerUnavailable as exc:
        record_bounded_fallback(mem, str(exc))
        return {action_key: fallback, 'memory': compact_memory(mem)}
```

Unexpected bugs are captured by the runner as invalid attempts, not erased by `except Exception`. If a deployment recovery rule catches unexpected failures, retain error classification/full invalid-attempt evidence and count the fallback version as the evaluated policy. Validity of G fallback and bounded serialization must also be checked; no invalid action is sent to save time.

Memory: version/config hashes, last processed arrival day, dedup actor/event counters, bounded public sufficient statistics and action diagnostics. Reconstruct exhausted dyads from full public introductions each invocation or a validated≤19,900-pair cache. No cross-episode fitting; evaluator initializes memory None. Phase idempotence and repeated historical feedback must not update twice. Never store private world labels/seed or infer episode identity by decoding IDs. Public introduction IDs may identify released trials only.

Scoring: vectorized upper-triangle≤19,900 pairs once per refreshed invocation, hard feasibility first, sparse adjacency thereafter. Separate finite probability assets from ranking weights; no silent asset-load fallback to soft counts called q. Quantize A1-P weights at1e−6; ≤100 selected edges gives≤1e−4 loose sum error, plus explicit tie handling. Do not infer calibrated probability from P's name.

Runtime: normal decisions use fixed work caps. Admission requires **every measured invocation <1 second** on the frozen target runtime, including import/process/JSON overhead if part of the user's per-step budget, and <10-second hard cap. Profile dense200-member observations, open-boundary rejection, maximum pending histories, full query shortlist, day0/day59, and unsupported-state fallbacks. Reserve a measured guard margin (candidate target .75 seconds, completion <1 second), but a timer check cannot interrupt a blocking NetworkX call. Use a cancellable bounded worker or a proven bounded solver; a thread timeout is insufficient. Guard-caused fallbacks are logged and their timing-dependent portability measured. Existing 6-second guard is incompatible with the stricter target and requires a reviewed new configuration.

If 5,376 rollout steps cannot meet that target, D1 fails deployment admission. Defer to predeclared L2 distillation only after validated teacher headroom; do not claim fewer unregistered particles or a timeout makes D1 fast. Benchmark results, not analytical operation counts, establish runtime. No runtime measurements exist for this proposal. Accompanying `check_reduced_arithmetic.py` and `arithmetic_results.json` verify exact fractions and enumerate tiny hard/soft packages and a static matching; they do not exercise this adapter or certify production behavior.

## 7. Exact fixtures and fail-closed gates

Use independent exhaustive enumeration with rational probabilities, no imports of the planner's value/transition helpers. All uncertainty is a toy law visible to the test specification, not privileged information given to the policy. Cases below have4–8 total actors; irrelevant isolated actors pad smaller cores. Real simulator realizability is a separate gate.

| Fixture | Public model and exact expected result | Failure exposed |
|---|---|---|
| Hold/match threshold,4 actors | A–B today1/5; C appears tomorrow only with probability1/2, A–C4/5, disposable partners, horizon ends tomorrow: hold2/5>1/5. With probability1/10: match1/5>2/25. | Never-wait / always-wait rules |
| Random return reversal,4 actors | AB reward1/5, pause1/5. Nonpause mass4/5 returns byday8: match21/25>hold4/5. Slow law: only mass2/5 returns byday8: match13/25<hold4/5. C exists **only onday8**, no intervening other opportunities. | Mean-timer substitution; missing expiry |
| Terminal static allocation,4 actors | Day59: AB9/10, CD1/20, AD=BC=13/20. A1-P/D1 choose AD+BC=13/10, not AB+CD=19/20. Qualifying reward observed during follow-up. | End-horizon reward discount; wrong optimizer |
| Shared future alternative,4 actors | Today AB=CD=1/2; both introductions pause with probability1 (half qualified, half late/unqualified). If both A,C held, AC9/10 tomorrow. Match both1>hold9/10; single current edge gives1/2. | Double-counting AC opportunity |
| Same covered set,4 actors | AB/CD versus AC/BD cover identical actors. Show identical node-price deduction algebraically; use distinct joint return laws for the two pairings. | Claim that static node prices distinguish joint returns |
| Actor reuse/exhaustion,4 actors | TriangleABC, fourth isolated. Edges q=p=1/10;8-day nonpause return; decision days0,8,16 only: value271/1000. Two-actor core with two isolated:1/10. | Historical repeat or double booking |
| Query collisions,7 actors | Verified A,B,C; U1,U2 unlock A with probability4/5 each; V1,V2 unlock distinct B,C with probability7/10. Two hard-bundle toy budget: shared24/25 vs distinct7/5. | Summing unlock counts; inconsistent actor draws |
| Hard versus soft,8 actors | Four disconnected pairs each verified X_i and hard-unverified Y_i. Each hard query reveals feasible w.p.1, returns terminal reward1/4; total4 bundles cost12, reward1. Each Y has three unknown soft answers that cannot remove missing hard constraints. Soft-only cost12 gives0; any one hard→three-soft replacement gives3/4. | Real12-unit competition; soft illegally unlocking hard |
| Soft versus hard with full budget,8 actors | Verified triangleABC: only AB/AC possible. One soft answer on A reveals equiprobable qualities(1,0)/(0,1): without it best reward1/2, with it1. Hard-unverified pairs DE,FG require both cost3 bundles, reward4/5,2/5 respectively; H isolated. Four hard asks cost12 give17/10. Soft+DE costs7 and gives9/5; remaining5 cannot verify FG. Soft wins by1/10. | Complete-package displacement; real12-unit soft VOI |
| Future query complement,4 actors | A is hard-verified and exits afterday0; U,V are present and hard-unverified onday0; W arrives hard-unverified onday1 with probabilityp; V,W survive throughday1. AU1/5, VW4/5. One-hard-bundle/day toy: query V iff p>1/4, U iff p<1/4. | Myopic querying; **not** proof of real12-unit pressure |
| No clairvoyance,6 actors | Identical wire history/memory/config but different host-only seeds, families and future arrivals: identical actions/memory. Zero-arrival particle law produces no arrivals. | Generator/seed imports, schedule leakage |
| Release/pause boundaries,4 actors | Nonmutual release exactlyt+8; cancellation releaseD+6; late two-Yes pauses when second response released but gives0 qualified reward. Repeat day7/8 and D+5/6 boundaries. | Off-by-one availability; pause=q assumption |
| Pending constant,6 actors | Adding already pending expected rewardr leaves each new action's marginal reward unchanged; new disjoint edge addsq, notq+r. | Double booking |
| Closure and falsity,8 actors | An alternating replacement changes seven actors on an eight-node graph: reject the six-affected cap and retain full parent. Enumerate every incident boundary alternative; test boundary overflow separately on larger graphs. False hard answer stays observed False; declined never imputed; repeated asks unavailable actors rejected. | Silent graph truncation; truthiness bugs |

The hard/soft fixtures are exact declared answer/reward models, not fitted simulator probabilities. Future-query complementary toy's one-bundle bottleneck also needs a separately exact real12-unit competition embedding before mechanism admission; arbitrary filler bundles are not proof if the optimum can skip them. Failed embeddings are evidence against relevance.

Gates in order:

1. **Contract/independent implementation:** no generator/seed/family imports, public schema fuzzing, no repeats/overlaps, exact nonadaptive12-unit asks, actual-answer eligibility, no future-event disclosure, memory≤1MiB. Restrict deployment modules away from simulator internals even if public helpers live in kit. Empty/unknown assets fail closed.
2. **Exact model fidelity:** all rational witnesses; exhaustive legal matchings≤8 nodes,≤3 decision epochs; regret≤.01 on frozen constructed grid. Independent transition checker must match every released-history branch. Own parent included and same controller simulated/deployed. No expectation-value change made to pass a failed fixture.
3. **Belief support:** public-only provenance; held-out entire-world validation of arrivals, return survival, pause and composite reward. Calibrated conditional predictions on decision-time states, pending censoring and selective labels acknowledged. No IPS/DR certificate from deterministic propensity=None. Arrival stress tests/12→24 horizon sensitivity pass; unsupported regions fall back.
4. **Resource/replay:** actual sub-second worst measured calls on specified workload; frozen10-second hard cap; bounded memory/assets and solver cancellation. Deterministic public-input replay and renaming checks. Report action disagreement and fallback rates, not just successful-call mean timing.
5. **Mechanism screening:** frozen independent new registration, keep historical failed R7 closed. Existing P3 screen requires ≥5% opportunity firing, mean gain≥.025 vs G,≥3 nonnegative family means, no family point loss<−.10, coverage loss≤.02, complete valid grid. These allocate research, not certify superiority.
6. **Parent/replication:** D1 vs A1-P and same-score greedy P_A1; Q2 vs FIFO+A1-P and Q6+A1-P; D2 vs FIFO+D1 and immediate-only acquisition under D1. Keep actual G/Q6/P frozen. Include no-wait and zero-tail controls before data; no changes to score assets to rescue an allocation effect. P4 requires positive own-parent difference and≥.025 vs G with existing service gates. No contender means stop. Enforce the existing twelve-arm P4 cap: six frozen references leave six slots total for candidates and own-parent/ablation controls. The complete D1/Q2/D2 control graph may not fit; defer D2 or reduce entrants before freeze rather than omit controls, expand the cap or opportunistically combine stages.
7. **Confirmation:** follow `research7/STATISTICS.md`: D_sj=(1/6)Σ_f(Y_Csf−Y_jsf); SE across independent seed clusters. One candidate vs six frozen references G,N,R,P,K,Q6, Bonferroni99% simultaneous two-sided intervals using t_(1−.01/12,n−1). Every lower bound>0, observed mean gain vs G≥.025, all cells valid, denominators/world hashes equal, independent reconstruction/production reviews closed. t intervals rely on sampling assumptions; add registered seed-cluster bootstrap sensitivity, not a claim of finite distribution-free coverage. Freeze variance-only sample size before sealed confirmation; never enlarge after significance peeks. No panel comparator dropped. No all-family safety/equivalence claim from nonsignificance.

## 8. Delegation and reproducibility record

Read-only clean-context workers: evidence `/root/evidence` requested gpt-6-luna/medium, command CPU allowance60s, root/critic review; theory `/root/theory` requested gpt-6-astra/high, analytic command allowance180s, critic review; critic `/root/critic` requested gpt-6.1-sol/high, command allowance120s, root integration. Root inherited gpt-6.1-sol/medium. No nested agents, maximum root+3. Requested routes were passed explicitly; resolved internal identity/token usage is not exposed. R6 JSON contains incompatible Google aliases, so live Codex routes follow AGENTS/ORCHESTRATION and tool schema; historical JSON/helper unchanged. No escalation.

Routing file SHA256: `1f323948f346c44da081176e6169f6099056c597c61f49ba78dc27f79739c6f4`. STRATEGIES SHA256: `e1660891ee7d356f4a80efaffccf66a251a1ab88e569effeec7e3772bc16d7f6`. Root and7b kit match SHA256 `0d2cb3d3b46ca2a6ee7c8b74b78c55642ef98686e59a890ec18f66f2cabc1f3e`.

Scientific disposition: reserve an implementation work order after this specification is reviewed. D1/Q2/D2 remain hypotheses. Exact toy gains, model-Monte-Carlo bounds and legal architecture do not establish a simulator winner.
