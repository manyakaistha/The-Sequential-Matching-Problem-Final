# Structural algorithms proposed for round six

Planning document, 2026-10-11. Owner: structural mechanisms researcher. Exclusive
ownership: this file only. Named reviewer: `/root/next_mechanisms`; director:
`/root`. Allowance: 120 CPU seconds for source reading and constructed arithmetic,
no full simulator episodes and no fresh seed worlds. No previous source, result,
archive or manifest was changed. This document specifies future work; none of
its candidates has been implemented or empirically promoted.

## What the evidence permits

**Observed evidence.** The completed round-five population scorer versus shipped
greedy comparison is 0.3821705426 versus 0.3813953488 MSMI/100, effect +0.0007751938,
registered 98.75% seed-cluster interval [-0.0272154463,+0.0287658339]. It establishes
neither a win nor equivalence and excludes the planned +0.05 effect. The 430
independent seed clusters contain six correlated families each. Nothing below
relabels this result as success. Round four's verification-priority exploratory
gain was fragile: its focused point effect changed sign after removing the
largest-gain seed, and the broad screening gain contained substantial second-
deadline residual luck. Round-three scarcity, global throughput, simple
population ranking and prediction improvements already have negative or
inconclusive evidence. Reimplementing one of those alone is not a new thesis.

**Exact source facts.** `kit.py` and `evaluate.py` specify one ask batch and one
match invocation each day 0–59, followed by 40 empty advances. Constraints cost
three units and reveal every nondeclined hard field; a named soft field costs
one. Daily budget is 12. All eleven hard fields at both endpoints must actually
be observed before introduction. Individual hard-field queries are illegal.
Hard declines are permanent. Queries require currently available endpoints.
The same member may receive a constraints and soft query in one batch, provided
the member/field combinations differ and the total budget fits. All those
answers appear in the same day's match observation. There is no intervening
ask invocation to adapt the remainder of that day's query batch.

Nonmutual introductions release at assignment+8. Mutual accepts release at
date+6 even after cancellation, unless positive pause or exit prevents return.
Scheduled outcomes continue after exits. Each dyad can be used only once;
endpoints may return for other partners. Arrivals stop after day 20. Exit is a
12% population mixture with one exit day uniform on 22–60, not a daily 12%
hazard. Both-positive second intentions cause permanent pause even when the
reward deadline fails. The date deadline is assignment-relative and the second
deadline is date-relative. Earlier introductions do not mechanically improve
these independent qualification delays.

**Inherited deductions.** Available endpoints have fully resolved prior incident
feedback, but unavailable endpoints and the global market may have pending
information. Full return distributions for unavailable endpoints cannot use
that lemma to omit survival information. A final-day legal addition between
unmatched endpoints weakly adds reward with full follow-up and unchanged
existing dyad/day streams. However shipped greedy visits every legal edge and
is already maximal: this addition cannot, by itself, improve shipped greedy.
Final-day replacement of one edge by two is a different question.

**Working hypothesis, not a result.** After the large static-ranking null, the
most informative route is to change the *set and timing* of legal opportunities:
collision-aware verification, local matching repairs, and finite-horizon use
of returning endpoints. There is no evidence yet that these have a large
attainable effect. The plan must estimate their actual incidence and expected
headroom before paying for an elaborate planner.

## First measure the decision-changing opportunity mass

Use already examined development logs only for a nonconfirmatory inventory;
read assignment-time observations rather than the final disclosed profiles.
If restoration is needed, copy through the canonical hardened restoration
helper into a new-round location; leave old artifacts unchanged.

For each day/seed/family, record: available hard-verified graph; legal edges
excluding past dyads; connected components; augmenting paths of lengths three
and five relative to greedy; exact maximum-cardinality gap in small components;
pending endpoints with publicly inferable return windows; query candidates
with one-bundle versus two-bundle opportunity requirements; competing queries
that share the same verified partner; and how often a soft answer can change
a matching rather than merely change a numerical score. Denominators must be
explicit: eligible ask days, candidate bundles, newly verified endpoints, legal
components, greedy matchings and pending introductions are different units.

Separate two inventories: (a) deployable observation-based forecasts, (b)
privileged diagnostic hard truth/release/exit labels. The latter may diagnose
forecast mistakes but cannot train an evaluated actor model or enter its
policy. Do not call the maximum-cardinality gap expected reward headroom;
occupancy, retirement and heterogeneous probabilities can reverse that gain.
Historical state re-scoring estimates opportunity incidence, not alternative
policy value after its endogenous state diverges.

## Algorithm H: collision-aware hard-verification batches

**Objective and mechanism.** Choose up to four constraints bundles jointly to
maximize expected *additional matching value*, rather than the sum of each
candidate's potential degree. This directly addresses two omissions in round
four `hard_priority`: two missing endpoints need complementary verification,
and several promising candidates can compete for one verified partner.

**Specified first implementation.** Candidate pool: at most eight available
members missing hard fields with no permanent hard decline, plus their already
verified available neighbors. Keep both the top one-bundle prospects and
two-bundle pairs; prune only source-proven impossibilities and observed public
failures. Enumerate all query subsets of size zero through four, at most 163.
Generate 32 deterministic policy-owned completion samples conditioned on
current public fields. Enumerate matchings exactly only on neighborhoods with
at most eight endpoints; otherwise use the same bounded local repair used by
the control. Score a query batch by average post-reveal matching value minus
current matching value, with the *same frozen edge scorer and allocator* in
both terms. Start with constant edge value to isolate legal opportunity
creation; a population-weighted version is a separately named contrast.
Actual matching always uses actual answers and legality checks, never sampled
fields. Ties: fewer queries, then arrival order and canonical public IDs.

The hard-completion sampler must implement the public source distributions
and their dependencies, not multiply round-four's incomplete proxies and call
the result exact. Age-radius support, reciprocal gender inclusion, smoking,
children, structure and schedule constraints all matter. Ordinary versus sparse
zone supports are publicly distinguishable (`zone_a` etc versus `zone_0` etc);
ordinary zone support does not reveal shift/drift/delayed labels. Values not
learnable from observations remain integrated. This is a source-prior model,
not a claim of empirically correct postselection probabilities.

**Controls.** FIFO with four bundles; FIFO with the same chosen batch size;
round-four one-member priority with four bundles; collision-aware one-member
greedy selection without two-bundle enumeration; and a uniform random batch
with fixed policy randomness. Preserve fixed scorer, allocation, fallback and
soft-query treatment. These distinguish changed batch size/warm-up from joint
complementarity and collision handling. Do not compare H only to the previously
selected population policy.

**Falsifiable hypothesis.** H increases newly created legal disjoint
introductions and positive-pause opportunity count, then terminal reward,
against its own four-bundle/FIFO parent. Reject if opportunity incidence is
negligible, gains disappear against the batch-size control, or terminal reward
fails registered promotion despite more verification throughput.

**Strongest objection.** Snapshot matching value can favor immediate matches
that consume scarce endpoints and can permanently starve a member whose useful
partner arrives or returns later. Completion sampling may be biased after
feedback-dependent selection. A one-day delay to a later FIFO member can
outweigh the apparent query gain.

## Algorithm R: return-calendar verification scheduling

**Objective and mechanism.** Verify available members whose best useful partners
are likely to return within the next eight days, before those returning actors
lose their next introduction opportunity. This uses *pending public timelines*,
not a hidden busy dictionary. No unavailable member is queried.

**Event forecast.** An observed nonmutual outcome gives release at t+8, subject
to exit. Both first yes answers give a date lag distribution from their observed
response days; before the date is received, lack of a date event truncates that
distribution. Before both responses resolve, pending survival and hidden mutual
acceptance affect the return distribution. A received date gives release at
D+6 unless positive pause or exit prevents it. Once a pause is observed, return
probability is zero. Date cancellation does not shorten busy time. A no-date
branch may release at t+8 even when response feedback arrived earlier.

Exit uncertainty is explicitly retained. Calendar predictions output a
distribution over each return day and never-return, not a fabricated known
exit/release time. Initial forecast uses known source priors; any fitted correction
requires seed-separated development labels available when returns/exits become
observed. A public availability flag can establish an exit only when all
remaining public busy/pause explanations are ruled out. Prior absence of an
arrived member cannot be treated as a future-arrival oracle.

**Specified policy.** H's query pool and collision objective, adding potential
neighbors from public pending introductions with forecast return mass on d+1
through min(d+8,59). Weight opportunity samples by the first expected day of
availability, probability of still being query-eligible, and a fixed horizon
discount registered before screening. Start with discount one; compare a
registered linear horizon discount separately. Cap query candidates at eight
and pending neighbors at eight, recheck returned actors' legal fields at actual
allocation. Use FIFO when forecasts are unsupported or computing exceeds its
budget. No actor parameters are learned in this initial version.

**Controls and falsifier.** H with no pending-neighbor forecast; calendar-only
ordering without joint batches; a deliberately truncated forecast using only
the exact t+8 nonmutual cases. Register forecast log loss/Brier and daily
return-window coverage on identical prospective public predictions. Better
calendar accuracy alone does not promote R. If synchronized verification does
not create additional usable introductions or terminal gain against H, reject
the claimed mechanism.

**Strongest objection.** FIFO already verifies all nonblocked members eventually;
there may be little return-specific bottleneck. Forecast error, cancellation
selection, exits and permanently retired high-quality actors can make preparing
for returns wasteful. Adding future partners can restore the proxy collision
problem unless the query batch objective remains joint.

## Algorithm L: bounded local matching repair

**Objective and mechanism.** Recover displaced disjoint opportunities without a
global solver or a universal degree rule. Starting from shipped greedy's
matching, find alternating paths/cycles on at most eight endpoints. Replace a
local incumbent matching only when its alternative improves a registered local
objective. This keeps query schedule and predictor fixed.

**Specified initial variants.** L-count: improve cardinality first, shipped
score sum second. L-weight: improve the sum of one fixed population terminal
score, without a cardinality bonus. L-robust: improve count only if the ratio of
alternative expected-reward sum to incumbent expected-reward sum exceeds one
under each registered plausible regime/response-prior model. L-count is a
diagnostic cheap control; L-robust is not a statistical guarantee or a Bayesian
credible-interval claim. Enumerate length-three and length-five augmenting paths,
then complete ≤8-endpoint connected components (764 matchings on complete eight
vertices). Canonical tie/order; at most two repair passes, fixed node/edge bounds.
For larger components use bounded ego neighborhoods and revalidate global
endpoint disjointness after each accepted repair.

**Controls.** Identical greedy allocation/scorer with no repair; exact
maximum-cardinality on the same local neighborhoods; local maximum-weight
using constant scores; and population greedy. Old globally implemented blossom
matching is an engineering/empirical comparator if available, not the central
novelty claim. General-graph odd cycles are handled by actual matching enumeration;
node prices alone do not solve odd-set constraints.

**Falsifiable hypothesis.** Small local exchange gaps occur often and can yield
more positive pauses at fixed prediction quality. Reject if repairs are rare,
the maximum-cardinality own-parent control explains the entire point gain,
or additional introductions reduce terminal reward through occupancy.

**Strongest objection.** More introductions can retire or block the wrong actors;
local reward-sum monotonicity does not imply sequential reward monotonicity.
At the last action day sum of exact conditional reward probabilities is the
correct immediate expected objective, but the implemented scores are approximate.
The component boundary can hide superior external partners. Do not advertise
an eight-node solver as an exact full-market solution.

## Algorithm P: event-calendar component lookahead

**Objective and mechanism.** Make a bounded joint choice among matched edges,
small reservations and waiting, using the probability of unsuccessful actors
returning and the disappearance of positive-paused endpoints. Replace global
q/busy division with explicit local future states.

**Specified first planner.** Restrict to genuinely isolated public potential
components of ≤8 members; larger components initially fall back to L. Start
with verified hard fields and no new acquisitions inside lookahead. State:
current available endpoints, past dyads, public resolved labels, pending-event
beliefs, current day, and remaining action horizon. Candidate actions: incumbent
matching, each top local alternative, and wait, at most eight actions. Run 64
policy-owned particles per action, looking ahead to min(d+16,59), using the exact
public source delay and retirement rules and a frozen observation-only actor
model. After the first action, use the same fixed L rollout policy for all
actions. Terminal tail value initially zero and is an explicit approximation.
Do not learn a tail value until this simpler representative passes tiny tests.

For a deployable planner, particles condition on observed fields/history and
generate legal futures under its source model. They never call the actual
episode world's private RNG, use its seed, or read scheduled future events.
Policy randomness uses a documented fixed internal sampler independent of
world IDs/seed; internal draws may be shared across alternative plans to reduce
planner noise, but this is not common-random-number equivalence to real future
dyad/day streams. A deterministic CPU/node budget is essential: return incumbent
when improvement estimates are too uncertain or the inner budget is exhausted.

**Controls and falsifier.** L; depth-zero identical planner; planner forced to
introduce a maximal current matching; planner with deterministic mean return
dates; planner without positive-pause retirement; and a no-wait/no-reservation
version. Fidelity tests first: tiny exact dynamic programs, where transition
and continuation values can be exhaustively checked, then common-cohort
prospective calendar calibration. Reject if gains occur only in its own imagined
worlds, disappear when horizons/particles change modestly, or fail terminal
own-parent comparisons.

**Strongest objection.** The public potential graph is rarely truly isolated
before all arrivals and verification; its later external edges are unknown.
Source-prior misspecification and particle winner's curse can dominate a small
lookahead gain. An exact delay model does not make the uncertain compatibility
and actor model exact. Endpoint continuation is generally nonseparable.

## Algorithm I: decision-changing hard/soft query bundles

**Objective and mechanism.** Allocate one-cost goal/pace/conversation questions
only when they can change a valuable matching choice; coordinate with hard
verification of that same member. This goes beyond round-four coordinated_goal's
fixed three-hard/three-goal budget split and degree-based soft ordering.

**Specified initial policy.** Enumerate H's hard batches and attach zero through
three soft questions, with total cost ≤12. Limit soft candidates to unseen,
nondeclined operative features on members incident to competing observed or
sampled feasible edges. Enumerate categorical soft answers exactly for each
candidate question using its source prior, conditional on relevant public
history if the model supports it. Score expected post-reveal local matching
value minus the identical no-query local matching value, subtracting the
registered marginal opportunity cost of displaced hard bundles. An observation
that cannot change the selected local matching has zero decision value under
this one-step objective. Questions must be chosen together before answers;
there is no adaptive second question in that day's ask phase. On unsupported
history-conditioned beliefs, use conservative prior/no-query rather than claim
inferred individual preferences.

**Controls and falsifier.** H with no soft queries; H with surplus-only goal
queries; fixed coordinated_goal split; identical batch-size hard queries with
random operative soft fields. Compare changed pair choices, displaced hard
bundles and terminal reward, not entropy or AUC. Reject if information improves
forecast proper scores but cannot change decisions, or if the displacement
control explains losses.

**Strongest objection.** Soft outcomes are sparse and selected; naive category
independence after history is approximate. One-step value of information can
be negative for sequential reward by making attractive-but-occupying introductions.
Three irrelevant soft fields already have a source-level negative control;
querying them cannot be framed as an unexplored learned advantage without a
history-dependent signal and a tested causal decision mechanism.

## Algorithm D: distill a verified tiny planner into a small policy

**Objective and mechanism.** If P establishes a genuine mechanism but its
latency/variance is unattractive, fit a compact continuation/choice model from
exact toy solutions and observation-only development planner decisions.
Distillation is a later engineering candidate, not a reason to skip P's direct
value test.

**Specified representative.** Enumerate fully specified toy components with
3–6 members, bounded horizons, missing-hard uncertainty, fixed public lag laws,
past-dyad masks and retirement. Derive exact action advantages by rational DP.
Fit a depth≤4 decision tree or strongly regularized linear advantage model using
only permutation-invariant public summaries: component edge count, matching
gap, verified/unknown endpoint count, return-window counts, horizon and edge
score differences. Augment training only with development public planner
decisions; never private episode labels. Deploy against an incumbent-matching
fallback with a registered margin. Compare held-out tiny structures not merely
held-out parameter draws; test actor-ID permutation equivariance.

**Controls and falsifier.** L, direct P, an unfitted hand-rule on identical
summaries, and fitted depth-zero constant action. Reject if it mimics teacher
actions but loses terminal reward, overfits toy structures, or never improves
the simpler own-parent. Demonstrating offline toy regret alone is insufficient.

**Strongest objection.** Toy distribution transfer can be poor, and public
summaries can destroy nonseparable/odd-cycle information. A slow teacher's
apparently good simulated value may be wrong. No policy-learning guarantee
comes from matching a teacher's labels. Model-based planning/distillation are
established paradigms, not inherently novel simulator contributions.

## Exact tiny tests to implement before any new-world screen

These are fully specified simplified constructions. Numbers are analytical,
not measured full-simulator rewards. An independent rational enumerator should
reproduce them and generate counterexamples before promotion.

1. **Hard-query complementarity.** Two missing endpoints a,b can form the only
   usable edge after both bundles are asked. Let that edge's expected reward be
   p>0. Set F(empty)=F({a})=F({b})=0, F({a,b})=p. The marginal value of b increases
   after querying a; ordinary diminishing returns/submodularity fails. A
   single-member greedy acquisition theorem therefore cannot be borrowed without
   checking additional assumptions. Test H's batch enumeration and I's cost.
2. **Collision penalty.** Two one-bundle candidates share one verified partner;
   each compatible edge is independently present with probability 4/5. Asking
   both yields expected maximum matching cardinality 1-(1/5)^2=24/25, despite
   the edge-probability sum 8/5. Two candidates each incident to separate verified
   partners with probabilities 7/10 yield expected cardinality 7/5. A sum-degree
   proxy chooses the wrong batch, while the exact expected-matching objective
   chooses the second. This is a one-day equal-reward toy, not a universal H win.
3. **Calendar edge unavailable today.** Horizon consists of action days 0,1;
   failure blocks eight days and success gives reward one/retirement. Current
   edges AB with q=11/100 and BD with q=1/10. C is already known to return on
   day1, when AC with q=1/10 becomes usable. Introducing AB yields 11/100 total.
   Introduce BD today and AC tomorrow yields 1/5 regardless of BD's outcome.
   No current-graph repair sees the future AC edge. Remove AC or make its q=0
   and AB becomes better: calendar waiting/reservation is not universally right.
4. **Soft query's opportunity cost.** AB reward probability is 9/10 or 1/10
   with equal prior; AC is constant1/2. Without information the best expected
   reward is1/2. A query revealing AB's state lets the allocator obtain
   (9/10+1/2)/2=7/10, value1/5. If that query displaces a hard bundle worth1/4,
   net gain is−1/20. Test both I's positive decision value and its rejection
   when a competing hard bundle earns more.
5. **Reuse exhaustion.** Three-member complete graph, every unused edge succeeds
   with probability1/10 independently, success retires its two endpoints,
   failure returns them after eight days. On action days0,8,16 there can be
   three sequential different introductions if all prior attempts fail, giving
   total expected reward1-(9/10)^3=271/1000. On a horizon ending before day8,
   only1/10 is possible. A planner that forgets past dyads or charges a universal
   busy penalty fails one of these horizons. This does not compare to a greedy
   policy; it verifies return and no-repeat semantics.
6. **Inherited counterexamples remain mandatory.** Reproduce the old four-node
   outer-edge versus middle-edge cardinality example and the reversed high-
   quality-middle example; long-versus-short occupancy; final-day penalty
   failure; odd-cycle matching. None of H–D is allowed to declare these obsolete.

For each constructed test report exact legal state, action set, transition
probabilities, terminal objective, enumeration output, CPU and independent
review. Tests with deterministic future arrivals/release dates use those inputs
only as specified toy information, not as evaluated-policy observations.
Planning arithmetic was checked with standalone standard-library `Fraction`
calculations: 163 hard batches, 764 complete-eight matchings, 24/25 versus7/5
collision expectations, 11/100 versus1/5 calendar values, 1/5 information gain,
−1/20 displaced-bundle net gain, and271/1000 reuse reward. The arithmetic
body consumed0.000038 CPU seconds (excludes Python startup/read tools). This
is not the proposed independent exhaustive DP verification and not empirical
policy-value evidence. No simulator world was generated or episode run.

## Oracle ladder and causal interpretation

- **Observation conditional scorer:** numerical integration of current public
  state under the specified source model. No extra private data; not an exact
  attainable bound because postselection priors/quadrature are approximate.
- **Known-parameter current scorer:** actor latent biases/response propensities
  and true regime, but missing soft fields remain integrated and hard fields
  remain subject to real verification. Offline diagnostic only.
- **Full-truth current-edge scorer:** private actor parameters and soft truth
  for presently legal verified edges, no future draw or event. Heuristic
  matching value is not a dynamic upper bound.
- **Query-completion oracle:** sees currently undisclosed nondeclined hard truth
  to diagnose batch regret, but still charges actual queries and uses actual
  availability. It does not see future events/exit days. Batch optimization
  alone is not a bound on full policy reward.
- **Privileged finite-horizon local planner:** private hard/soft truth, parameters,
  arrivals and exit dates in a ≤8-node specified neighborhood; integrates fresh
  future outcome draws rather than seeing them. Exact only if every transition
  and all feasible continuation actions in the specified tiny model are
  enumerated; truncation/candidate restriction destroys an optimality claim.
- **Future-draw clairvoyance:** optional loose offline ceiling, explicitly reads
  realized future outcomes. Never a predictor-training target or deployable
  comparator; changing assignment day/dyad changes the actual keyed stream, so
  a pretabulated subset is not automatically a global full-policy ceiling.

For actual controlled interventions, hold world fixed and compare identical
scorers/acquisition/allocators except the named mechanism. Only identical
dyad/day introductions share complete actual outcome streams. Changing timing
or partner changes those streams; descriptive pause/occupancy differences are
not causal mediation estimates. Use independent selection and frozen terminal
confirmation for value. Distinguish two .36 statements: under the intended
independent future second-delay streams and predictably formed introductions,
unconditional E[qualified]=.36 E[K] can remain valid even when prior second
timestamps change future actions; K counts both-positive pairs with on-time
dates. The stronger statement that .36K is the conditional expectation given
all non-second-delay primitives, with guaranteed Rao–Blackwell variance
reduction, needs the earlier trajectory-invariance conditions and may fail
for these planners/global learners. Complete follow-up, legal trajectories,
guard behavior and absence of outcome-dependent exclusion still need scope
checks. Raw qualified MSMI remains primary; neither statement licenses changing
the primary endpoint after disappointing results.

## A stronger headroom diagnostic to develop, not a policy

The director proposes a renewal-occupancy LP that improves on the old minimum-
eight-day capacity relaxation. Condition on fixed full profiles, actor
parameters, actual arrivals/exits and the true regime; use ideal independent
fresh outcome streams, not privileged realized future draws. Let x(e,t) be
the probability/expected indicator of assigning unused dyad e on day t.
Let q(e,t) be its full conditional terminal qualification probability.
For an endpoint of e and later decision day s≥t, define u(e,t;s) as the
probability that this introduction still prevents that endpoint from being
assigned on s through busy occupancy or permanent positive pause. Include
assignment day itself with u(e,t;t)=1. For later days u includes the complete
nonmutual/mutual date lag, cancellation, second submission/yes and retirement
law; it is not simply eight days or an average duration.

Candidate relaxation: maximize sum(e,t) q(e,t)x(e,t), with x≥0,
sum(t)x(e,t)≤1 for each dyad, and for every endpoint i/day s,
sum(e incident to i,t≤s)u(e,t;s)x(e,t)≤1. Remove assignment variables outside
the arrival/exit/action window or hard-truth eligibility. This ignores hard
verification cost and information limits, so the proposed value is diagnostic
headroom only. Delays/qualification continue after exits; do not truncate q
when an assigned endpoint exits. Capacity after exit is irrelevant because
there are no legal later assignment variables.

**Potential mathematical justification, to be independently proved.** On a
legal sample path, assignment-caused occupancy intervals incident to one actor
are disjoint; a positive-pause interval is permanent. Therefore their summed
occupancy indicators on a day are at most one. Conditional on fixed actor
parameters and fresh independent dyad/day streams, the assignment decision
at t is made before that introduction's random outcomes. This permits
E[assignment indicator × its occupancy indicator]=x(e,t)u(e,t;s), and the
same argument gives expected terminal reward sum qx. Relaxing information and
verification constraints then supplies an expected-reward upper bound under
those assumptions. The theorem is not yet proved in this round, and a finite
hashed PRNG does not itself imply the independence assumption.

**Important numerical distinction.** A quadrature estimate of q and u inside
the LP is only an approximate bound candidate. A certified numerical upper
bound needs outward error control: use upper enclosures q+ in the objective
and lower enclosures u− in capacity constraints, then a certified LP upper
certificate. Using approximate q or *larger* occupancy coefficients can
underestimate the true upper bound. Gaussian tail bounds, interval arithmetic,
discrete exact delay sums and LP dual certificate residuals are separate work.
Compare this relaxation on development worlds only, with the earlier min-eight
LP and actual policy reward, showing both privileged scopes and looseness.
Do not fit deployable continuation targets from its privileged coefficients.

A cheap additional deterministic ceiling is qualified dyads≤positive-paused
dyads≤maximum matching cardinality of the full hard-truth graph. Qualified
pairs necessarily pause, and no endpoint can legally be reintroduced after
its pause; busy release occurs after that pair's second outcomes. Include
all arrived members and clearly say whether blocked hard declines are ignored
as an optimistic relaxation. This ceiling is usually loose because it drops
funnel failures, occupancy, query costs and timing. It is not a claim that a
maximum-cardinality policy attains it.

## Proposed order, resource guard and review resolution

**First wave:** opportunity inventory, exact H/L tiny tests, source-prior sampler
review, then H and fixed-score L with simple architecture controls. Those are
the critic's priorities because combining four changes initially would obscure
what works. **Second wave:** R's prospective return-calendar audit and I's
decision-value tests only if opportunity mass justifies them. **Third wave:** P
only after fidelity tests; D only after a directly tested planner benefit.
Do not screen the entire Cartesian product. Promote an interaction only after
each isolated contribution has credible evidence or an explicit exact
complementarity argument.

Planning caps are not measured execution guarantees: H/I query pools≤8,
32 completion particles, hard batches≤163; L components≤8/two passes; P
eight actions×64 particles×16 action-day horizon. A monotonic internal budget
of ≤6 seconds reserves startup/serialization/fallback within the official
ten-second invocation limit. Memory stores at most capped public forecast
summaries and sampler state, target≤64KiB; returned memory must remain strictly
below1MiB. Use no runtime files/network/extra processes, at most two cores and
the evaluator's actual read-only container/1GiB/64-PID restrictions. The legal
fallback reconstructs shipped greedy on the received public observation.
Benchmark candidate-pool construction and dense graph behavior before assuming
these caps fit. If they do not, reduce computation before reward experiments.

Named critic explicitly objected to (1) treating query-calendar dates as known
despite exit uncertainty, (2) confounding batch size with priority, (3) selling
extra cardinality as reward, and (4) accepting imagined planner reward. The
specifications above retain probabilistic exits, matched batch-size controls,
count/weighted repair controls and exact-fidelity/terminal gates. Unresolved:
actual decision-changing opportunity incidence, source-prior postselection
error, component boundary leakage and how much effect remains after return
forecast uncertainty. The director records promotions/rejections separately;
this file makes no promotion recommendation based on a point estimate.

## Closest methods and novelty limits

Batch value of information, stochastic matching, finite-horizon planning and
policy distillation are established ideas. The primary-source stochastic
matching formulation commonly queries an edge and must commit upon its
existence; this simulator's node-bundle disclosure, noncommitting questions,
repeatable endpoints, busy time and permanent retirement differ. Its published
approximation factors therefore do not transfer automatically. See Bansal,
Gupta, Li, Mestre, Nagarajan and Rudra,
[When LP is the Cure for Your Matching Woes](https://arxiv.org/abs/1008.5356).

Adaptive submodularity supplies greedy guarantees under its stated diminishing-
returns hypotheses; the two-endpoint verification example above violates the
ordinary analogous property. This is a reason to check hypotheses, not a claim
that the established theory is wrong. See Golovin and Krause,
[Adaptive Submodularity](https://arxiv.org/abs/1003.3967).

Potential simulator-specific contributions: a characterized complementary
query objective, a publicly conditioned return belief with tested calendar
fidelity, a reproducible small-component continuation benchmark, or a verified
policy gain that survives its architecture controls. Broad algorithmic novelty
is unestablished. No seed/UUID reverse engineering, hidden-state access,
deadline draw inference, invalid action or scorer vulnerability counts as an
improvement.

Source evidence read: `kit.py`, `evaluate.py`, `research3/FORENSICS.md`,
`research3/THEORY_MODELS.md`, `research3/AVAILABLE_FEEDBACK_THEOREM.md`,
`research3/FINAL_REPORT.md`, `research3/policy.py`,
`research3/model_candidates.py`, `research4/MECHANISMS.md`,
`research4/candidates.py`, `research4/FINAL_REPORT.md`,
`research4/DEADLINE_INVARIANCE.md`, and `research5/FINAL_REPORT.md`.
