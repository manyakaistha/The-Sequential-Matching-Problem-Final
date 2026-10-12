# Simulator forensics and information acquisition audit

9 October 2026. Analyst owns this document, `forensic_audit.py` and
`results/research3/forensics.json`. Reviewer: adversarial critic. Compute allowance:
10 CPU minutes, one worker; actual first audit 4.72 CPU seconds (follow-up dynamic audit recorded in JSON). No fresh seeds or
policy rollouts. Command: `python3 research3/forensic_audit.py`.

## Observed evidence: completed study preserved

Read the prior report, theory, extended algorithm/empirical/registry/reproduction,
three final reviews, references, policy implementations, terminal model, candidate
map, simulator/evaluator and existing audit/manifest/archive records. The prior
confirmation contains 480 valid episodes (40 independent seeds, six correlated
families, two policies). Its reported score, effect and interval are consistent
with raw qualified counts: greedy 179 outcomes / 48,000 members ×100 = .3729167;
simple 159 /48,000 ×100 = .33125; difference −.0416667. The statistical review
independently reconstructs CI [−.0910679668,+.0077346335]. No superior, inferior or
equivalent policy was established; targeted +.10 was excluded by that interval.
`no_learning_fifo` and `terminal_soft` were promising on development and never
confirmed. `simple_fifo` gives all edges the same positive score, so updates do
not improve ranking. Auxiliary integrated computations remain in its executable.
The prior raw mechanism record establishes identical FIFO query schedules.

Round2 `fast_confirmation.py`/`parallel_confirmation.py` omit the required 40-day follow-up and available evaluator logs contain only 15/13 development episodes; those records do not support complete confirmation.

The subsequent `research2/FINAL_REPORT.md` reports candidate .3042 versus greedy
.3792 on seeds 6001–6040, yet concludes it proved +.10 improvement. That conclusion
contradicts its own numbers and must not be inherited. Its statement that roughly
65% of dates are cancelled by deadlines also conflates physical cancellation with
qualification. Source gives physical date cancellation probability .22; feedback
qualification is .36 conditional on a positive pair, and delayed date eligibility
is 671/686. No global Jensen direction justifies its variance narrative.

## Exact source reconciliation

`kit.py` and `evaluate.py` are authoritative; these are source calculations rather
than empirical estimates.

* Each day 0–59 has an ask invocation and a match invocation. Ask results are
  immediately visible at match. Forty empty advances finish on day 100; maximum
  supported feedback lag is 38 days from assignment, so outcomes are resolved.
* Hard fields: age_min, age_max, who_to_meet, relationship_structure, smoking,
  partner_smoking, has_children, partner_children, wants_children,
  acceptable_zones, schedule. All 22 endpoint field values must be nonmissing
  before a pair is eligible, even when some public checks could already be made.
  Same member/pool and adulthood checks also apply. Public failures dominate
  missingness and are safe pruning information.
* **Only `constraints` and the seven SOFT field names are legal queries.** A hard
  bundle costs 3; a named soft query costs 1; daily budget is 12. Every individual
  HARD field query was actually rejected with `unknown ask field` on an existing
  seed in the audit. Cheap partial hard completion is disproved by the protocol.
* A constraints query reveals all nondeclined hard fields. Declines are permanent.
  Repeated or already-observed queries on different days are accepted but waste
  cost. Duplicate member/field within one batch is rejected. Queries require
  currently available endpoints; exited, busy and paused members cannot be asked.
* Permanent-decline pruning already exists in shipped `baseline_asks` and all
  extended candidates. It is useful but cannot count as a new improvement.
* Introductions need disjoint endpoints in one action, availability and actual
  verified feasibility. A dyad can never repeat. An endpoint can return for a
  different partner once available. No cancellation action exists.
* Nonmutual introductions occupy endpoints until assignment+8, regardless of
  early observed rejection. Mutual acceptances occupy until scheduled date+6,
  including cancelled dates. These release times are not exposed in observations.
* Twelve percent of generated members receive one exit day uniform in 22–60;
  this is not a daily exit hazard. Seventy percent arrive at day zero; remaining
  arrivals are uniform 1–20. No arrivals after day 20. Scheduled responses, dates,
  second intentions and pauses continue after exits.
* A date qualifies if its day minus assignment day <=30. Each positive second
  answer qualifies if its day minus date day <=3. Both positive answers trigger
  permanent pause at the later answer, even if qualification fails. Availability
  does not retire anyone before these answers become public.
* Observations include every arrived member, fields/status/observation times,
  public demographics, available flag, assignments, received events, query log,
  day and remaining budget. They omit truth, future events, response/bias
  parameters, exit day, busy release and scenario label.
* Outcome stream is keyed by seed, sorted dyad IDs and assignment day. Same dyad
  and day across policies shares the stream; changing day or dyad changes it.
  One Gaussian shared effect enters both acceptance logits and both second
  logits. Actor response propensity is reused at both response stages. Distinct
  random uniforms are drawn; response-day/date/feedback delay draws also follow
  the same keyed stream. Identical world seeds do not preserve every outcome
  draw when actions differ. Across ordinary/shift/drift families generator members
  agree, but stage branching can change later stream alignment.

## Observed funnel: mutually exclusive losses and correct denominators

These pooled trace counts use all 240 episodes per policy. They are descriptive;
assignments are not independent sampling units for policy reward inference.

| Funnel/loss | Greedy | simple_fifo | Relevant denominator |
|---|---:|---:|---|
| Introductions | 17,954 | 18,133 | all introductions |
| At least one introduction nonresponse | 7,419 | 7,557 | introductions |
| Both respond | 10,535 | 10,576 | introductions |
| Rejection with both responding | 8,107 | 8,142 | both respond |
| Both accept | 2,428 | 2,434 | both respond |
| Physical date cancellation | 579 | 522 | both accept |
| Date happens | 1,849 | 1,912 | both accept |
| At least one second nonresponse | 727 | 751 | dates |
| Both second responses | 1,122 | 1,161 | dates |
| Negative second with both responding | 611 | 672 | both second responses |
| Both positive / pause dyads | 511 | 489 | both second responses |
| Positive but disqualified | 332 | 330 | both positive |
| Qualified | 179 | 159 | both positive |

Greedy conditional rates are .58678 both respond, .23047 reciprocal acceptance
among responding pairs, .76153 dates given mutual acceptance, .60681 both second
responses given a date, .45544 both positive given second responses, and .35029
qualified given both positive. Terminal success is .00997 per introduction.
Simple's analogous terminal rate is .00877. The raw audit retains counts and
rates by episode plus aggregate numerator/denominator pairs.

Deadline attribution is explicit: greedy has 3 late-date positive pairs and 331
late-feedback positive pairs, with overlap 2, hence 332 total; simple has 3 and
330, overlap 3, hence 330 total. These are losses among **positive pairs**, not
cancelled dates. The prior key `late_feedback_both_yes` conflated both mechanisms.

Both policies spent 48,720 query units, entirely 16,240 hard bundles; 124,080 daily
budget units were unused (71.8% of 172,800 potential units). Unused budget alone
is not useful information value. More dates and introductions did not imply more
reward. There were 19,579 versus 19,932 endpoint assignments beyond each member's
first. This is legal repeated endpoint use, not repeated dyads. Greedy served
16,329 episode-members (34.01875%).

## Offline privileged static graph audit: hard opportunity limits

The audit regenerates only 48 previously examined greedy development worlds.
Truth graphs replace fields with latent truth; verified graphs use final public
fields. All graphs ignore arrival, exit, busy, pause and previous dyads, so these
are generous structural diagnostics, **not feasible online policy allocations**.

| Family | Hard-declined members | Verified members | Truth edges all 200 | Nonblocked truth edges | Nonblocked nonisolated members |
|---|---:|---:|---:|---:|---:|
| Ordinary/development/shift/drift/delayed | 69.375 | 130.625 | 266.625 | 112.875 | 74.625 |
| Cold start | 83.250 | 116.750 | 238.125 | 87.250 | 67.625 |
| Sparse | 66.750 | 133.250 | 47.375 | 19.500 | 30.625 |

Every nonblocked member was hard-verified by the end in these 48 traces. Thus final
insufficient verification does not explain residual isolation; early verification
timing remains a policy lever. Many members have no physically feasible partner
and others are forever unverifiable due to declines. Only about 75 of 200 ordinary
members (31 sparse) have any legal hard-compatible partner even ignoring time.
This accounts for much of low coverage without establishing a tight reward bound.
The raw rows retain per-world counts and degrees, not only averages.

## Mathematical deductions and policy influence

A soft field outside the four fields used by `_prob` and goal equality used by
second logits has no direct effect on the simulator funnel. Consequently
`emotional_availability`, `space_for_relationship` and `relocate` have zero direct
truth-outcome value conditional on the relevant features and parameters. Shipped
greedy nevertheless includes their equality in its seven-field rank score.
Removing those terms is a legitimate falsifiable control, not a proved reward
improvement; they can indirectly proxy missingness or affect allocation ties.

The exact standard qualification thinning factor for a positive dyad is .36;
delayed adds 671/686. Under fresh independent adapted simulation and complete
follow-up, the prior proven expectation identity links qualified outcomes and
positive pause dyads. It does not make realized fixed-seed ratios constant, and
conditioning on later adaptive actions can break naive binomial descriptions.
Positive-pause endpoints are disjoint. Conditioned on the generated hard graph and averaging independent future outcome draws, a loose bound on expected terminal score
uses half the number of nonblocked nonisolated endpoints times .36 (or the delayed
factor), giving about 6.72 MSMI/100 in an ordinary 200-member graph and 2.76 sparse.
This is not a per-realized-seed maximum and not policy headroom. It is far above current performance and is deliberately labeled loose: it
ignores probabilities, incompatible endpoint demands and time. It is not evidence
that such scores are attainable.

Policies can influence pair choice, assignment timing, what gets verified early,
soft information, repeated available opportunities and occupancy induced by
mutual acceptance. They cannot change hard truth, permanent declines, intrinsic
response propensity, exogenous cancellation/delay draws, exit/arrival priors,
forced busy release or late-positive retirement. They may indirectly choose pairs
with better response propensities using legally observed histories.

## Candidate hypotheses, controls and failure criteria

1. Four-field weighted rank versus seven-field greedy, same FIFO and immediate
   matching. Objective: remove directly irrelevant noise. Inputs: public fields.
   No learning; O(n²log n); greedy legal fallback. Falsify with paired full-horizon
   reward comparisons and a goal-only control. Failure: fewer cardinal matches,
   proxy signal lost, shift weights unknown, sparse opportunities dominate.
2. Surplus goal completion after FIFO hard bundles, versus identical ranker without
   soft queries. Query only verified available nondeclined actors with candidate
   alternatives, then goal-missing counterparts. Pair bundles can be complementary.
   No claim that entropy implies value. Falsify with action-changing information
   fraction, terminal reward and query cost. Failure: queries improve prediction
   but not choices; exploration teaches nothing useful before exit/end; redundant
   endpoints; score uncertainty overwhelms known goal effect.
3. Query only incomplete members with at least one publicly possible partner,
   compare FIFO and potential-degree. Cannot prune unknown-field incompatibility.
   Existing degree and value controls were disappointing; a new version needs a
   clearly distinct mechanism, not renamed prior work. Permanent-decline pruning
   and cheap individual hard queries are rejected as new contributions.

## Oracle levels and privilege disclosures

* Observation-only population expectation: public features and known generator
  distributions; model assumptions on missingness/regime remain. Deployable if
  computed within limits; not an oracle accessing unavailable truth.
* Known-parameter missing-feature oracle: true actor biases/response rates and
  actual regime, integrating unknown soft values; still not truth-field scoring.
* Full-truth current-edge oracle: latent truth and actor parameters, exact public
  delays; sees no realized future draws. Can rank only currently legal verified
  edges, unless separately labeled hard-truth acquisition oracle.
* Privileged finite-horizon planner: adds future arrivals/exits/busy releases and
  possibly scheduled pending events. Separate variants must state each addition;
  a clairvoyant realized-outcome planner is yet stronger and unattainable.
* Exact tiny-model DP: specified state, transition kernel and information pattern.
  Exact for that model only. Cannot claim full-simulator optimality.

The static truth graph above is a truth-only opportunity diagnostic. Stronger
oracles need not furnish tight attainable bounds; action-conditioned probability
sums from recorded policies are not oracle-policy reward.

## Remaining uncertainty and seed provenance

Excluded old seed declarations: 81 (test_kit), 101–105, 201–205, 301–305, 42, 20260926 and public
20261000–20261009; extended 1001–1008, 2001–2012, 3001–3040; round2 declared
4001–4040, 5001–5020, 6001–6040. The last ranges are conservatively excluded even
where raw provenance is weak. Artifact inventory is the authority on examined
worlds; they never become untouched again. No final new-round seeds were accessed.

Early verification deficit, missed reusable edges, exit losses and detailed
occupancy opportunity costs need dynamic graph replay or new registered
interventions. This audit deliberately does not infer those causal quantities
from final graph/count differences. The prior mechanism replay remains useful
but does not prove why a candidate gained or lost reward.

## Follow-up realized opportunity audit

`development_realized_opportunity_rows` reconstructs 60 preallocation daily states
for the same 48 old greedy worlds from public assignments/events, final observed
field timestamps and privileged exit days regenerated offline. It records busy,
paused/exited, available/verified member-days and final-legal-edge days. Edge loss
classification has explicit precedence: not arrived, previously used, exited,
paused, busy, not yet verified. These are counts along a realized policy trajectory,
not causal rewards from removing a loss. Exit days are hidden audit information;
no evaluated action receives them. Same-day assignment starts do not yet count as
busy at preallocation; same-day previously revealed fields count as verified.
Reviewer found no blocking objection to funnel/static audit; requested this
expectation-bound/old-seed clarification was incorporated.
