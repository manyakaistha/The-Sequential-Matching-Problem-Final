# Round four mechanism proposals and implementation contract

Owner: next-mechanisms researcher. Named reviewer: statistics_review/director.
Exclusive files: this document and `candidates.py`. No old source was edited and
no fresh evaluation seed was used. Initial allowance60 CPU seconds, additional
acceptance-likelihood allowance120 CPU seconds. Smoke checks used only already
examined seed101's day-zero observation and constructed public events. Initial
eight-candidate JSON-roundtrip legality check consumed .334 CPU seconds. These
checks are correctness evidence, not policy-value experiments.

Sources read: shipped kit/evaluator interfaces, old REPORT, round-three
FORENSICS, THEORY_MODELS, AVAILABLE_FEEDBACK_THEOREM, IMPLEMENTATION_REVIEW,
PLAN/registry, policy/model candidates, and terminal-model likelihood code.
The old negative/inconclusive confirmations remain unchanged. No implementation
here supports a claim of superiority, novelty or calibrated prediction.

## Exact public mechanisms and overlooked signals

`kit.py:113–131`: one ask batch can contain a constraints bundle and a soft query
for the **same** available member. Duplicate checking is by `(member_id, field)`;
queries are all resolved before matching. A constraints bundle costs3, soft
query1, total daily budget12. A soft query neither requires existing hard
verification nor prior introduction. Thus the first introduction after
verification can use a newly acquired soft value in that very invocation.
Round-three surplus queries considered only currently feasible edges, excluding
these newly verified endpoints. This is a legitimate information-timing gap.

`kit.py:38–65`: public age, gender and zone carry hard-completion information.
Generated age radii are uniform integers3–10; no pair with age gap>10 can become
hard feasible. Each unknown `who_to_meet` subset includes any specified gender
with probability `(.7+2*.2+3*.1)/3=7/15`. An unknown acceptable-zone set always
includes its own public zone. Ordinary families add another sampled zone with
probability .3; sparse families never add one. Fields already disclosed can
prune impossible candidates through public `eligibility`. These observations
support verification order; they never replace actual legality checks.

Initial soft categories are independently uniform under the population
generator. Completion/missingness/decline draws do not reveal their unseen values
under the intended independent-draw interpretation. Complete personas are
selected randomly, not via an undisclosed preference class. Three nuisance
soft fields have no funnel effect. Masked-feature inference from demographics
therefore offers no fresh unconditional soft-value signal. Public outcome
history can change this posterior, but naive mask prediction cannot manufacture
that signal. UUID/member order is used only for deterministic ties; recovering
PRNG/seed state from IDs would violate the user’s leakage restriction.

Zone names `zone_0` etc publicly identify a sparse geographic support, and date
lags>21 publicly exclude ordinary delays. These are legal mechanism clues, not
permission to pass evaluator scenario labels. This implementation does not
add an adaptive regime model: ordinary/shift/drift preferences are not separable
from initial profiles, and sparse lag evidence requires additional model review.

## Candidate strongest cases, controls and falsifiers

All candidates use observed availability, all11 verified hard fields, permanent
decline pruning, past-dyad exclusion and endpoint-disjoint greedy allocation.
They return `memory={}`. Population scoring inherits the public-regime mixture,
shared-Gaussian integration, missing-equality enumeration and deadline coupling
from round three; these remain numerical/selection approximations. All scored
legal edges are eligible for allocation regardless of zero-score thresholds.

|Candidate|Mechanism and strongest case|Own-architecture control|Falsifier/strongest objection|
|---|---|---|---|
|coordinated_goal|Reserve3 ask units when four FIFO hard bundles compete; reveal goal on the first3 newly verified endpoints before first introduction. Goal affects both funnel stages in every regime.|goal_surplus_control: same population score,4 FIFO hard bundles then surplus goal on already legal endpoints|Lost fourth bundle/early opportunities may cost more than better choices. Failure to improve reward or actual decision quality rejects benefit.|
|hard_priority|Spend all12 on4 bundles, prioritizing estimated single-bundle opportunities to verified available partners, then two-bundle prospects. Avoid verifying publicly impossible isolated members early.|population_control: same score and4 FIFO bundles|Partial degree can overvalue thin endpoint sets/competing partners, starve slow arrivals and choose edges that vanish. No introduction/quality gain rejects headroom.|
|response_uniform|Replace moment-matched Beta actor response second moments with exact truncated-uniform posterior integral ratios.|response_beta_control: identical population score/counts/allocation|Posterior errors are small for most histories; only sparse repeat actors differ. Better parameter correctness need not improve ranking or reward.|
|acceptance_shrinkage|Use all resolved responding yes/no labels to shrink actor acceptance bias under its known N(0,.49) prior, retaining posterior variance; combine with exact response moments.|response_uniform: identical queries/scorer except actor-bias update|Sparse histories, availability selection, latent partner/common effects and regime ambiguity can produce harmful over-personalization. Calibration and reward must justify update.|

`greedy` calls shipped functions directly. `population_control` tests whether the
inherited integrated scorer earns its complexity on this independent round.
`goal_surplus_control` is itself a comparator against population_control: it uses
all available surplus, never displacing hard acquisition. Coordinated-goal uses
FIFO hard order, not priority order, so its comparison does not confound the two
mechanisms. No combination is selected in advance of experiments.

## Approximation and complexity contracts

Hard-priority value is lexicographic `(sum completion proxies over verified
available partners, sum over all available potential partners)`, ties by arrival
then public ID. The proxy multiplies exact age-radius/gender prior factors and
partial public failures; cross-zone unknown completion uses `.3/4 * (5/6) = .0625`, since
the added zone is uniform, unlike the own-zone draw. This unconditional
six-family prior deliberately ignores information in the observed zone support. It intentionally omits smoking/children/structure/schedule prior
factors. Its product is **not an exact hard-feasibility probability**, and all
hard feasibility is rechecked after actual disclosure. Sparse different-zone
pairs receive proxy0 because their target zone is outside the ordinary support.
Critic caught an initial incorrect use of own-zone frequencies for the uniformly
chosen extra zone; this was corrected before evaluation/freeze. Priority is
O(N²), no matching solver, no learning.

Uniform-response moment uses the exact rational expansion of
`Z(s,f)=integral_.55^.98 r^s(1-r)^f dr` and returns `Z(s+2,f)/Z(s,f)` as float.
No floating cancellation affects integration. Available-endpoint feedback is
resolved by round-three timing lemma; counts are explicit public response/second
events only. Cache512 cells is bounded; supported counts0–120 are far beyond
legal60-day histories. Arithmetic correctness does not make the full score exact.

Acceptance likelihood enumerates missing soft equalities and integrates shared
Gaussian effect with five-point quadrature before weighting a five-point
N(0,.49) bias prior. Nonresponse labels are excluded from acceptance likelihood.
Responding yes/no multiplies marginal likelihood; posterior mean and variance
are retained, rounded5 decimals, and moment-matched to Gaussian for terminal
integration. Current disclosed fields may inform past compatibility at the
current invocation; no later disclosure or private truth is read. This is legal
Bayesian evidence use, not retrospective supervised prediction evaluation.
An assignment-time prospective snapshot remains essential for future audits.

Important approximations: regimes are independently marginalized per trial
instead of jointly inferred; partner response labels do not condition on the
shared past effect; past second labels/availability selection do not update
acceptance/second biases; normal approximation replaces the discrete posterior.
The predicted current shared effect is fresh for a never-repeat dyad. Response
propensity and acceptance prior remain independent given the included labels.
This is a shrinkage control, not an exact actor posterior or universal theorem.
O(H*5*16*3*5+E) cached likelihood work precedes inherited integrated scoring;
diverse posterior means can increase terminal cache misses and invocation cost.
Host guard/production measurements are director owned; no timeout guarantee is
claimed. Internal caches have fixed sizes4096 and512 plus inherited bounded caches.

## Cheap falsification evidence and planned criticism

Day-zero seed101 asks/matches passed unchanged simulator legality for all8
configs after JSON roundtrip: baseline9 pairs; population/goal-surplus/Beta/
Uniform/acceptance8; coordinated/priority7. This early difference is **not**
reward evidence. Constructed all-unequal, all-missing and all-equal soft patterns
had strictly increasing marginal yes likelihood at bias−.7,0,+.7. A constructed
single responding yes moved posterior bias positive; a no moved it negative.
Uniform prior second moment agreed to<1e−14 with its polynomial formula;
one success raises and one failure lowers it. The old diagnostic count cell
s=1,f=4 yields .403161 as expected. No episode trajectory was evaluated here.

Required reviewer objections: test same-member multi-field queries, omitted
hard-bundle costs and empty/exhausted pools; independently verify exact moments;
audit likelihood labels and past-field timing; measure actor cache/latency tails;
distinguish better conditional edge quality from favorable keyed deadline draws;
consider pairing/cardinality and delayed occupancy alternative explanations.
Promotion needs registered paired seed clusters and terminal reward, followed by
independent selection/freeze/confirmation. More optimistic source rationale is
not a substitute for those results.
