# R8 first-wave independent criticism and review

Date: 2026-10-14. Reviewer: `/root/critic`, requested `gpt-6.1-sol/high`.
Disposition: **approved for the registered reduced-model development scope only**.
This is not production admission, model calibration, or authorization to claim a
new simulator winner. No official episodes or fits were performed by this review.

## Reviewed behavior and evidence

The exact planner partitions successor scenarios by their public observation and
normalizes the posterior **before** selecting the next action. Its cache includes
the whole posterior, horizon and continuation controller. Qualified expectation
is booked once at a new assignment, including the terminal action day; hidden
clocks are not supplied to the greedy controller. Joint outcomes and arrival
events have explicitly declared independence assumptions. These are valid finite
toy laws, not the simulator's complete observation or feedback law.

The query evaluator groups indistinguishable complete answer batches, integrates
the still-hidden reward weights, and then applies the terminal matching
controller. It does not average separately optimized hidden scenarios. Hard
verification is required on both endpoints; a soft answer, False hard answer, or
decline cannot substitute for it. Complete packages obey the declared daily
budget. The returned optimum is exact within the declared query domain, not the
official unrestricted question domain.

The reduced menu retains legal full matchings, outside parent pairs, the parent,
and a local empty action. It deduplicates at most twelve actions and checks the
six-changed-actor limit. Current-component overflow returns the parent alone.
Its closure includes current available legal edges only; it does not represent
unresolved-hard or pending-return boundary alternatives. Because the boundary is
a subset of the closed region, its separate boundary-overflow guard is not an
independently exercised production six-boundary implementation. Explicit
`tie_parent` now retains the registered current parent on equal rollout values;
the previously implicit greedy tie preference was corrected before grid closure.

Independent verification ran `python3 -m unittest discover -s research8/tests`
with bytecode writes disabled and CPU/wall guards of 90/120 seconds. All **18
tests passed in 0.031 seconds**. The meaningful cases include the lawful hidden
clock value `3/5` versus clairvoyant `4/5`, all 64 four-node action graphs, the 764
matchings on K8, fast/slow return reversal, dyad exhaustion/reuse, shared future
opportunity, terminal allocation, real-budget soft/hard displacement, query
complement/collision, and explicit parent retention on a dynamic tie. Additional
read-only checks forced transition, joint-branch and cumulative-support caps and
rejected duplicate/unknown available actors; every forced cap raised an error
instead of returning a partial optimum.

## Independent closed-grid reconstruction

The fixed registration contains 144 Cartesian cases. This review reconstructed
every row using only `Fraction`, the registered parameter arrays and the closed
JSON, without importing the planner or director analysis. For current reward
`q`, future reward `r`, and arrival probability `p`:

* Fast return: current-match value is `q + (1-q)*p*r`.
* Slow/absorbing return: current-match value is `q`.
* Hold value is `p*r`; optimum is the larger of hold and match.

All keys were unique and the exact registered grid was complete. Every exact,
greedy, full-menu and re-evaluated zero-horizon value matched these formulas.
All recorded model-use counters were within registered caps. Summary
reconstruction agreed exactly: **20 strict improvements/holds**, mean count-value
gain **31/720**, zero menu regret on this grid, and maximum zero-horizon regret
**7/10**. Recorded timing aggregates also reconstructed. The four source hashes
and registration hash matched the files read at review closure.

Reviewed grid artifact SHA256:
`6c289223f5419a0dfc0ea4910e0726699927c718510f8c95859cafa9e72799ef`.

## Remaining scientific and production limits

The 144 cases each have only two sparse opportunities on four declared actors.
Greedy continuation is optimal after the first decision in this particular
construction. Zero menu regret therefore does not show that greedy continuation
or the bounded menu is generally adequate. The mean is an equally weighted
predetermined toy-grid summary, not an estimate with 144 independent simulator
samples. The objective is expected introduction count, not a proof about random-
denominator MSMI per 100 arrived members.

Declared exit calendars and future edge laws are public **toy assumptions**;
production requests do not reveal actual exit or future calendars. The model
does not yet implement released response/date feedback, delayed pause visibility,
publicly fitted arrival/profile laws or a complete observation adapter. Supplied
initial scenarios are post-arrival conditional priors, not certified reachable
states reconstructed from every past event. Asymmetric permanent absorption is
a reduced resource law, not source-exact pair-pause behavior. Test and solve
timings do not establish subsecond 200-member cold-process invocation behavior.

Public asset provenance/calibration, observation/transition fidelity, pending
survival conditioning, complete own-parent controls, measured restricted-runtime
behavior, and new seed/resource registration remain gates before any reward
comparison. Preserve the closed registration, source identity and outputs when
starting another grid; do not revise the completed recipe to make a later
diagnostic appear preregistered.

## Smallest next falsifier

A four-actor, two-epoch declared model exposes greedy-tail failure without menu
exclusion: day0 has only AB, reward `7/10`, with certain pair absorption
(`7/10` qualified and `3/10` unqualified). Day1 has AB=`3/5`, AC=`1/2`, BD=`1/2`,
and no CD. The first-action menu contains both AB and wait. Greedy-tail rollout
values wait at `3/5` and AB at `7/10`, so introduces AB now. Exact belief planning
values wait at `1` (AC+BD tomorrow) and AB at `7/10`, so waits. Exact first-action
regret is **3/10**. This is an analytical proposed witness, not another executed
grid. Register it separately before execution and attribute the gap to the
continuation controller, rather than particles, menu pruning or simulator bias.

## Subsequent registered continuation amendment

The original W1 source/configuration/tests were subsequently preserved in
`history/w1/`. This reviewer independently checked every snapshot manifest hash
and verified that the closed 144-row grid references exactly those historical
source hashes. The grid artifact above remains unchanged; current planner
changes are a separately registered amendment, not a retrospective W1 repair.

The amendment adds an explicit `myopic` continuation controller that maximizes
the current full matching's reward, retaining `greedy` as a separate control.
Inspection confirms it takes a public view, uses the same legal full-action
domain, and does not recursively invoke the dynamic solver. Before the final
pending-reward test addition, independent guarded verification passed all
**20 tests in 0.033 seconds**.

The root committed `results/falsifiers.json` under the separately registered
`continuation_amendment.json`. A simultaneous reviewer execution completed its
model assertions but encountered `FileExistsError` at the exclusive-create
commit. It did not overwrite the first result and was not retried or counted as
an additional sample. This review then reconstructed both closed result rows
from their exact arithmetic and checked current source hashes, without importing
the director's analysis or result-generation helper:

| Case | Exact first-action value/choice | Greedy tail | Myopic tail |
|---|---|---|---|
| Future static matching | `1`, wait | `7/10`, AB now; regret `3/10` | `1`, wait; regret `0` |
| Future waiting | `9/10`, wait | `1/2`, AB now; regret `2/5` | `1/2`, AB now; regret `2/5` |

The future-waiting case has day0 AB=`1/2`, day1 AC=`2/5`, day2 AD=`9/10`, four
present actors, and certain absorption on every introduction. Exact planning
waits through both early opportunities. Static maximum-weight continuation still
commits at day1 and therefore undervalues holding at day0. Both choices are in
the initial menu: this is a continuation-policy limitation, not menu exclusion.

Both approximate controllers exceed the registered maximum first-action regret
`1/100`. The recorded **FAIL** verdict and exclusion from production/reward-screen
admission are correct. Adding a static optimal allocator fixes the first witness
but does not establish dynamic fidelity. Exact finite belief enumeration remains
a useful declared-model oracle; none of these results admits it as a production
controller.

Closed falsifier artifact SHA256:
`0b640f69c2385d5928a62cf7c6039924adb47ec367cbb8d2400757d5d3bae96b`.
Reviewed amended planner SHA256:
`49d1332459c09be381b86f070c5238f580ea8305530d16de09ccfd95d5834153`.

## Final receipt

After the separately added pending-reward regression, this reviewer independently
ran all **21 tests in 0.032 seconds**, with the same 90 CPU-second/120 wall-second
guards. All passed. The new test changes a past introduction's originally booked
probability from `1/4` to `3/4` while preserving the supplied pending state; a new
disjoint assignment contributes exactly `3/10` in either case. This verifies
bookkeeping in the reduced model, not a full released-feedback posterior adapter.

Final checks reconfirmed the unchanged W1 grid and amended falsifier artifact
hashes above and their respective historical/current source identities. The
final README correctly limits the sparse-grid result and reports the failed
approximate-continuation gate. Review disposition remains: **reduced exact-core
and query correctness accepted within declared scope; greedy/myopic continuation
prototypes fail fidelity and are excluded from reward-screen/production
admission**. No official simulator episodes, fitting, or superiority result is
part of this work.
