# Public continuation semantics and a bounded hold probe

Prepared 2026-10-15 by `/root/continuation_forensics`; reviewers:
`/root/continuation_critic` and director `/root`. Source inspection only: no
episodes, fitting, outcome replays, external APIs, or changes to frozen files.
This document proposes a mechanism, not an improvement claim or authorization
to run a study.

## What the scores actually mean

`kit.py:210-222` and `research6/policies/allocation.py:16-27` define the G/Q6
matching score as the number of **disclosed, equal soft fields**, an integer in
0..7. Missing/missing contributes zero; disclosed equality contributes one.
All seven fields count equally, including three absent from first-acceptance
fit in `kit.py:135-139`. The shifted family can reverse lifestyle's effect.
Consequently this score is neither acceptance probability nor qualified reward
probability, and differences cannot be interpreted as expected reward or units
of opportunity cost. G greedily visits descending score, canonical ID ties,
and exhausts all available legal disjoint opportunities; it is maximal rather
than maximum cardinality.

Q6 is exactly R6 `N3_two`: `research7b/workspace/research7/policies/references.py:17`
and `research8/soft_query_followup/v2/reference_adapter.py:8-12`. Its acquisition
uses 32 joint hard-profile particles, a degree shortlist of eight, pair choices
with FIFO fill when k>2, and lexicographic expected greedy matching **count then
soft-score** objectives (`research6/policies/acquisition.py:83-126,155-162,210-259`).
It asks constraints bundles only. Actual post-answer matching is unchanged G
(`research6/policies/allocation.py:115-121`). Its hypothetical hard completion
law is a frozen approximation and does not provide a calibrated continuation
or terminal-reward asset.

The historical P reference uses population-model scoring through
`research4/candidates.py`, whose inherited terminal probability integrates
population assumptions (`research3/model_candidates.py:33-50`). It is distinct
from Q6. The legacy `throughput` mode divides q by an approximate busy duration
(`research3/model_candidates.py:85-91`); that scalar is not a released return
calendar or a joint pause/qualified-return posterior. No such score should be
silently substituted into a Q6 hold rule.

R7 A1 also needs identity care: `a1.py:68` obtains absent `weight_model` as None,
so the default config selects the soft-agreement fallback, although the helper's
default argument says population. Its comment claiming 0..4 is stale: its loop
uses all seven `SOFT` fields (`research7b/workspace/research7/policies/a1.py:19-33`).

## Simulator transitions

Let t be assignment day, D the scheduled date day, and R the latest observed
second-intention response day. Bounds below describe source rules, not a license
to read hidden clocks or the private variant at inference.

| Branch | Source behavior | What public history can establish |
|---|---|---|
| First responses | Individual yes/no released t+1..t+7; no response released t+7 with value None | A released no or no_response establishes that the pair is nonmutual; an early no does not release either actor early |
| Nonmutual | Both busy until t+8 | Conditional on no departure, return is exactly t+8; availability is false at t+7, true at t+8 |
| Both first responses yes | D=max(response days)+U[1,14]; delayed source adds U[5,12] | Until date feedback is released, D is hidden, including after two yes responses |
| Date branch, including cancellation | Both clocks are overwritten to D+6, whether date_happened is true or false | Released date feedback reveals D; cancellation ensures no second-intention pause from that introduction |
| Happened date | Individual second intention released D+1..D+5; nonresponse at D+5 | A released negative/nonresponse excludes mutual-positive pause; pending responses leave uncertainty |
| Both second intentions yes | Permanent pair pause at R, after both answers are publicly released | Pause is effective immediately on its observed day, even if responses were too late to qualify |

Sources: `kit.py:156-188`. In ordinary variants D-t is 2..21; in the delayed
variant it is 7..33. Date-branch nonpaused return D+6 is therefore t+8..t+27,
or t+13..t+39 in delayed. These are bounds, not mean return times. `available`
also requires arrived_day<=day<private exit_day and no released pause
(`kit.py:97-100`). Public members remain visible after exit. Unavailable alone
does not identify busy, exit, or pause, and even a known rejection-clock expiry
cannot guarantee survival to that date. The obsolete `retired` set is initialized
but not used by this availability rule.

The user's shorthand “8 days after reject / 6 days after date” therefore needs
two precise qualifications: the eight-day clock starts at **assignment**, not
the rejection response, and six-day occupancy follows the **scheduled date
event even on cancellation**. There is no release immediately after an early
negative response. Every introduced dyad is permanently exhausted immediately
at assignment (`kit.py:150-154`); a hold does not exhaust the proposed dyad.

## Qualified reward and the horizon

Qualified reward requires mutual first acceptance, a happened date within 30
days of assignment, and both positive second intentions within three days of
that date. A late date or late positive intention may still cause permanent
pause without qualified reward (`kit.py:184-197`). Do not set pause probability
equal to qualified probability or treat unqualified outcome as automatic return.

The current follow-up evaluator assigns on days0..59, then observes released
events through day99 (`research8/soft_query_followup/v3/runner.py:209-226`).
The endpoint is 100 times qualified introduction count divided by members
arrived by day59, independently reconstructed from public events
(`research8/soft_query_followup/v2/metrics.py:7-22,63-83,94-107`). It is neither
qualified members per100 nor reward per served member. The original kit metrics
uses its current simulation-day denominator; with this frozen generator all
arrivals are by day20, so these denominators agree, but that equality is
source-dependent rather than a general interface guarantee.

Day59 assignments retain their full eventual reward. Even the delayed maximum
date lag33 plus second-response lag5 releases by day97 for a day59 introduction.
No occupancy opportunity cost remains after the last assignment epoch. There
must be no “too late for feedback” reward discount or final-day hold. This does
not imply arbitrary positive edges should override stronger competing current
edges.

## What is available for continuation estimates

Observations expose currently arrived public profiles, available flags,
introductions/deadlines, released feedback and ask logs (`kit.py:101-111`). They
do not expose busy clocks, exit_day, hidden outcomes, future actors, seed,
variant, actor biases or response rates. Public history provides these narrow
calendar anchors without calibration:

* Nonmutual response evidence: t+8 conditional return, subject to exit.
* Released canceled date: D+6 conditional return, subject to exit.
* Happened date with released nonpositive second response: D+6 conditional
  return, subject to exit; with unresolved second responses, joint pause/return
  uncertainty remains until release.
* Released pause: unavailable permanently in this source.

Any empirical return hazard must use public availability/feedback and admit
departure ambiguity and right censoring. Repeated feedback is cumulative, so
deduplicate by event identity rather than counting it again each invocation.

Arrival features must count all unique arrived members by public arrived_day,
including zero days, rather than differences in available pool size.
`research8/w2/public_adapter.py:107-115` implements exactly that histogram.
Anonymous future arrival counts/profile laws are forecasts requiring frozen
public-data assumptions and validation; observed past arrivals do not reveal
the private remaining schedule. No future identities, generator constants,
private family or known day20 arrival cutoff may enter this candidate.

The exact R8 planner is a declared finite toy law, not a simulator adapter.
Its q is **qualified probability** and is checked against a joint outcome law;
qualified mass requires both permanent pauses (`research8/planner.py:179-205`).
Its availability-only observation, declared public exit days, independent
arrival events and day-indexed edge laws omit parts of the real public feedback
process (`research8/planner.py:1-14`). The bounded variant books current q even
on day59 but truncates at twelve future epochs (`research8/w2/bounded.py:1-14`).
The deployment bridge explicitly reports that no public joint model is admitted
and returns unchanged G (`research8/w2/public_adapter.py:141-148`). Reusing this
core does not supply missing calibrated laws or authorize calendar injection.

## Recommended minimal mechanism: one rejection-return hold

Prefer a transparent **ordinal-score probe**, not fitting a sparse within-episode
q estimator. Qualified labels are too rare for that fit to be a small neutral
addition. The following is tractable and distinct from static reranking:

1. Preserve Q6 acquisition code exactly, run G on the actual post-answer state,
   and keep its complete current matching M as the parent. Memory records only
   public hold history and the frozen config identity.
2. For every parent edge {a,b}, inspect either endpoint a and each currently
   unavailable c distinct from a,b. Admit a witness only if c's **most recent**
   introduction is assigned at t-7, a response on that introduction from one of
   its actual endpoints contains no or a valid no_response,
   c has no released pause, {a,c} is unexhausted and public hard-feasible, and
   score(a,c)>score(a,b). The most-recent condition prevents using an old clock
   after a later introduction. All evidence must already be released; a valid
   no_response has value/occurred_day None, explicit missing_reason=no_response,
   and release at that introduction's deadline t0+7.
3. On t<59 choose at most one witness, descending integer score gap and then
   parent-pair output position, endpoint position within that pair, and witness
   order in the public member list. These frozen public orders match the
   implementation; no extra opaque-ID tie salt is introduced. Remove that one
   edge from M, retaining every outside parent pair. Both a and b are withheld;
   neither may have been withheld before in this episode, and exclude witness c
   if it was previously withheld too. This once-per-actor
   cap rules out endless chained one-day holds. Record c and target day t+1.
4. On the next day expire the hold unconditionally and resume ordinary Q6/G.
   Do not force {a,c}, decode an ID, ask an unavailable c, retain a hold for a
   further day, or count a modeled return as actual availability. No hold on
   day59; empty parent, unsupported history, malformed memory or work exhaustion
   returns the legal unchanged parent.

The strict score comparison is ordinal, with no fitted threshold or probability
claim. A removed matching edge remains a legal partial matching even if other
future interactions were omitted from analysis. This is a heuristic tradeoff,
not a closed-region Bellman reduction: its harm can include losing b's option,
delaying reuse, exits, competing use of c, and changed future Q6 queries as
availability changes. “Unchanged acquisition” means identical Q6 code on each
arm's actual state, not identical ask actions on diverging trajectories.

Use the frozen Q6 as the no-hold own parent, contemporary G/P as references if
studied, and a separately specified opportunity-matched blind-delay control if
making a claim specific to return information rather than delay alone. The
minimal mechanism can be implemented without adding arrivals or q assets; a
larger anonymous-arrival/pending-mutual planner is a separate future candidate.

## Meaningful falsifiers before any promotion

Constructed fixtures must check t+7/t+8, early-no nonrelease, cancellation D+5/6,
late-two-yes pause without reward, assignment-day clock versus response-day
clock, most-recent-introduction selection, exhausted dyads, no hold on day59,
one-time hold memory, phase idempotence and malformed-memory parent fallback.
Two requests with identical wire history/memory/config but different host seed,
family, future arrivals and private exits must produce identical responses.

If later authorized, complete fresh paired episodes, not replayed alternative
actions on the old world trajectory, are needed for effects. Record all parent
edges, eligible witnesses and omission reasons, withheld actors, return-day
appearance, actual {a,c} selection, score changes, assignments, qualified reward,
unqualified pauses, coverage and wait distributions. Count zero-trigger cells;
do not condition the primary endpoint on successful returns or served members.
Explicitly reject a useful-mechanism claim when holds rarely trigger, witnesses
rarely return/get matched, ordinal score gains fail to yield reward gains, or
coverage/total reward deteriorate. A switched dyad/day changes the simulator's
hashed draw stream (`kit.py:154`), so a few fortunate outcomes do not establish
the asserted mechanism. A bounded negative result closes this probe; it does
not prove continuation has no value.
