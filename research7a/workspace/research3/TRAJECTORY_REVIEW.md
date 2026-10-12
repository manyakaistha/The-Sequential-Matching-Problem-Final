# Independent Stage B trajectory and alternative-explanation review

9 October 2026. Analyst owns this file, `trajectory_review.py` and its JSON.
Reviewer: critic. Question: are promoted candidates' exploratory gains supported
by improved conditional current-edge quality rather than favorable realized
outcomes? Hypothesis: fixed-trace diagnostics can separate descriptive quantities,
but cannot establish a causal mechanism. No candidate/configuration fitting,
selection-rule change, fresh policy rollout or future outcome prediction.

Command: `python3 research3/trajectory_review.py`. This analyzes 432 existing
Stage B traces (six policies, 12 seeds, six families). Actual 1.572 CPU seconds,
1.706 wall seconds, one worker. It regenerates examined worlds solely offline to
recover **true soft attributes, actor bias/second bias/response propensity and
family**. Thirty-two-node Gauss-Hermite quadrature integrates the single shared
dyadic Gaussian across all four logits; public date and qualification mechanisms
are applied. It accesses no future uniform draws or scheduled outcome values in
scoring. Completed public outcomes are read separately to classify realized losses.
A 64-node check on 64 assignments has maximum terminal discrepancy 6.94e-18;
this finite numerical convergence check is not a universal quadrature certificate.

## Observed counts and privileged conditional-quality proxies

Every policy has 72 episodes, 14,400 arrived members. Rates below are means of
episode rewards. Conditional q-sums are normalized by 200 members per world.
Assignment quality is the pooled sum divided by introductions, a different
estimand. These are **not oracle-policy rewards or causal policy effects**.

| Policy | Introductions | Positive pauses | Qualified | Positive disqualified | Mean qualified/100 | Conditional q-sum/100 | Assignment-weighted q |
|---|---:|---:|---:|---:|---:|---:|---:|
| greedy | 5,299 | 137 | 51 | 86 | .354167 | .373531 | .010151 |
| offline | 5,236 | 160 | 68 | 92 | .472222 | .371556 | .010218 |
| population | 5,237 | 145 | 52 | 93 | .361111 | .375933 | .010337 |
| goal_queries | 4,945 | 171 | 65 | 106 | .451389 | .372345 | .010843 |
| public_weight | 4,963 | 156 | 59 | 97 | .409722 | .368466 | .010691 |
| random_order | 5,243 | 155 | 64 | 91 | .444444 | .368182 | .010112 |

Paired seed-cluster descriptive contrasts (12 clusters, families averaged within
seed) have these point estimates and **unadjusted** 95% t intervals. They do not
create additional registered superiority claims or override Stage B multiplicity.

| Candidate minus control | Realized MSMI/100 | Conditional q-sum/100 | q-sum descriptive interval |
|---|---:|---:|---|
| offline − greedy | +.118056 | −.001975 | [−.012303,+.008354] |
| offline − population | +.111111 | −.004377 | [−.010914,+.002159] |
| goal_queries − greedy | +.097222 | −.001186 | [−.010086,+.007714] |
| goal_queries − public_weight | +.041667 | +.003878 | [+.000687,+.007070] |
| random_order − greedy | +.090278 | −.005349 | [−.015543,+.004845] |

Offline's 17 additional qualified outcomes are accompanied by 23 additional
positive pauses and six additional positive disqualifications. Its per-introduction
truth quality is marginally higher, but fewer introductions leave its total
conditional q-sum slightly lower. The large realized point gain therefore lacks a
corresponding descriptive expected-quality gain. Favorable realized acceptance,
second-intention and deadline outcomes, together with their endogenous effect on
future assignments, remain credible alternatives. It would be wrong to attribute
all 17 outcomes to deadline luck or all to predictor improvement.

Relative to its own public_weight architecture, goal querying has a small positive
conditional q-sum proxy point difference. It spends 1,329 additional goal-query
units, makes 18 fewer introductions, produces 15 additional positive pauses and
six additional qualified outcomes. Realized reward uncertainty remains wide;
its proxy gain is small compared with the searched realized gain and is not a
causal estimate. Versus greedy, the q-sum gain disappears. Random ordering's
positive reward point difference also lacks higher conditional q-sum, demonstrating
how uninformative ranking can obtain favorable searched outcomes.

## Information and the zero-score omission mechanism

All 72 goal_queries/public_weight pairs have identical hard-bundle schedules
(4,787 bundles each); soft queries are the only ask additions. The JSON retains
first changed asks and first changed matching sets per world. Clarification does
not create new hard feasibility because both controls use the same hard protocol.

Public_weight is `goal equality probability + .55 pace equality probability +
.25 conversation equality probability`. It is **zero** when all three relevant
equalities are known false. The allocation wrapper requires score >0, so it skips
such legal edges, even though their true funnel probability remains strictly
positive. Soft queries can turn previously uncertain equalities into all-false
and create omitted edges. They can also reveal true equality and change ranking.
This is a policy omission/occupancy mechanism, not a hard-eligibility mechanism.
The registry's general phrase “positive scores” has this documented exception;
no inference or configuration was changed after freezing.

Fewer introductions and greater per-introduction truth quality under these modes
may partly reflect omission, not just better ordering. This review does not
quantify its causal contribution. A future separately registered control would
compare a common positive score offset (which restores immediate matching of
all legal edges without changing positive-edge ranking) against the existing
zero-skip behavior, with query schedules otherwise fixed. That idea must not be
inserted into the current frozen confirmation.

## Representative trajectories and disagreement

Representatives were mechanically chosen as the largest positive/negative realized
seed-cluster contrast, with the lowest seed breaking ties; no favorable scenario
was cherry-picked for selection. All six family traces and complete differing
positive-event records are retained in the JSON, including negative examples.

* Offline versus greedy, seed 70003: +.25 MSMI/100, no net positive-pause gain,
  and .5 fewer disqualified pairs per episode. In development, a candidate-only
  day-33 dyad ending `4214eb/7da81d` qualifies (q=.032518), while greedy-only
  day-15 `8dd856/6c964e` and day-46 `99c535/147cc9` are positive but late-feedback
  disqualified. First matching difference is day zero. The cluster q-sum is
  higher here, but across all clusters it is not.
* Offline versus greedy, seed 70007: −.166667 MSMI/100 and q-sum −.012499.
  In development, candidate-only day-17 `ad882e/e4fe21` has high q=.051153 but
  positive late feedback, while greedy-only day-32 `ccd608/4a23ee` also fails
  feedback. High conditional probability never guarantees realized qualification.
* Goal_queries versus public_weight, seed 70008: +.333333 MSMI/100, q-sum
  +.005305. First development matching difference is day 20. Candidate-only
  day-32 `a3523c/938f70` qualifies, while day-36 `762625/7d06bf` pauses late.
* The same contrast, seed 70010: −.25 MSMI/100 despite q-sum +.004246.
  First development difference is day 16; control-only day-32
  `66d25b/d6b520` qualifies (q=.009485). This directly counters a claim that a
  positive descriptive q-sum improvement implies a realized seed reward gain.

The strongest developer case is that goal information affects both acceptance
and second logits and produces a modest own-control truth-quality proxy gain.
The strongest alternative is that searched rare events, zero-score omission and
endogenous pauses alter the future available pool; a tiny proxy shift need not
explain reward. For offline, the case is a low-cost learned ranking with a good
exploratory reward point estimate; the objection is that identical-cohort predictive
validation and truth-conditional trajectory quality do not establish its mechanism.
Independent fresh focused development and untouched frozen confirmation remain
the appropriate resolution; this descriptive audit does not change promotion.

## Assumptions and remaining uncertainty

Scoring conditions on privileged fixed actor truth and family but integrates
unobserved shared effects and stage uniforms under the public law. Because the
realized future assignments depend on prior feedback/retirement, summing these
probabilities along recorded actions is a descriptive trajectory quality measure.
It cannot be interpreted as reward from rerunning those fixed future actions, or
an intervention separating score/query/timing. Member draws and dyad-day streams
are deterministic hashed pseudorandom functions in fixed evaluated worlds; common
seeds do not share all downstream variables when dyads or assignment days change.
No counterfactual impossibility, attained headroom or simulator optimality is
claimed. Component occupancy and early clarification causality remain unresolved.
