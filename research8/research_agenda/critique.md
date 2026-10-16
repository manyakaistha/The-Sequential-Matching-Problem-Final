# Constructive independent critique of the next research agenda

Date: 2026-10-14. Reviewer: `/root/w2_critic`, Sol/high; director integrates.
Scope: source/closed-metric inspection, primary literature and analytical power
calculations. No fit or new simulator episode was run. Ownership: this file only.

## Recommendation

The highest-value sequence is (1) isolate score versus static optimizer effects,
(2) admit a modest public-data joint outcome model, (3) evaluate full-remaining-
horizon parent rollout with a small coordinated-wait extension, then (4) add
complete-package query VOI under the same deployed allocator. These are specific
falsifiable experiments, not a requirement to build every proposed subsystem
before doing useful work. Static score-controlled allocation can be investigated
while dynamic model work proceeds. B1 supplies a tiny-model teacher/checker; its
12-day horizon and availability-only kernel do not certify a production policy.

## Historical evidence: two numerical corrections and causal limits

Read sources: `research7/STATISTICS.md`, `research8/w2/README.md`, the reservation
planning note and review, and the P4 frozen registration, `policies/a1.py` and
`reviews/p4_replication_results.md` in `research7b/workspace`. The reservation note
correctly notices that A1's config `{"id":"A1"}` makes weight_model=None and
therefore runs observed-soft agreement counts, not the promised population
qualified-probability asset. Preserve the tested policy as A1-soft. Its result
does not identify omission of continuation as the cause of failure.

This review additionally read all **4,608 closed P4 commit JSONs** under
`research7b/workspace/results/research7/research7_20261012/7b/P4_replication/commits`.
They contain 96 complete seed clusters, six families and eight arms, with unique
cells, valid flags, registered config hashes, matching world hashes across
policies, and denominator 200 in every cell. Stored per-100 reward equals Q/2.
The P4 report's numerical “Mean MSMI per 100” column is instead mean Q: its
per-100 means and differences are inflated by exactly two.

| Contrast | Correct mean per-100 difference | Seed-cluster SE | Exploratory 95% interval |
|---|---:|---:|---:|
| A1-soft − G | −0.00954861 | 0.03045079 | [−0.07000107, 0.05090385] |
| P − G | 0.03298611 | 0.02243409 | [−0.01155118, 0.07752340] |
| Q6 − G | 0.03472222 | 0.02725197 | [−0.01937977, 0.08882422] |
| Q1 − Q6 | −0.00173611 | 0.03002545 | [−0.06134417, 0.05787195] |
| K − G | −0.03125000 | 0.02325966 | [−0.07742626, 0.01492626] |

These are reconstructed **metric-layer exploratory summaries**, not independent
public-event reward reconstruction, a new sample or a confirmation analysis.
The 96-cluster aggregation averages six family differences within each seed,
then computes SE across seeds with 95 degrees of freedom. It replaces neither
the required simultaneous confirmation intervals nor the archived report. The
canonical SHA256 of sorted `[seed,family,policy,Q,A,Y]` rows encoded as compact
JSON is `2f33c5a11a38d8fb250100addf84c1f615f8805f7799262616e53fc89d414793`.

The archived no-contender decision remains justified by the registered point
gates: A1-soft is negative versus G, and Q1 is negative versus its own parent Q6.
“No registered contender” is supported; “all observation-only policies cannot
improve” and equivalence of Q1/Q6 are not. The intervals leave room for meaningful
positive or negative effects. P4's 576-cell t statistics also use the wrong unit
for the adopted statistical protocol, independently of the factor-two scaling.

Further causal corrections:

* Hard answers are immediate. Delayed-family losses cannot be explained as
  queries receiving delayed/uninformative hard answers. Downstream dates,
  qualified-reward windows, occupancy and shifted random draws are alternatives.
* N cannot legally introduce hard-unverified pairs. Its lower descriptive reward
  primarily reflects a smaller unlocked legal graph; it is not evidence that
  N wastes valid introductions on hidden hard violations.
* Static matching can optimize its frozen surrogate and still lower eventual
  reward through misscoring, pairing-induced return differences, ties or global
  future competition. A1-soft's point loss proves none of these individually.
* Same numerical seeds do not preserve downstream random draws after changing
  simulator delay logic. Diagnostic RNG interventions need a separate schema and
  all controls; keep their evidence separate from the official benchmark.

## Four prioritized experiments

### 1. Score-controlled static allocation

Freeze a 2×2 comparison: soft score versus an explicit qualified-reward score,
each allocated by the same-score greedy or maximum-weight solver. Fix FIFO asks,
feasibility, quantization, ties and fallback. Historical P is a frozen reference;
a newly fitted score's greedy parent is a distinct policy even if both are
called population scoring. Include G/Q6/P as relevant unchanged references.

First replay examined public snapshots: measure changed whole actions, surrogate
sum improvement, graph components/edge density and latency. Maximum-weight's
surrogate gain is an implementation theorem, not reward evidence. Then a fresh
complete paired rollout screen distinguishes optimization from score quality.
Stop an action-identical variant before expensive screening. Reject unsupported
asset loads explicitly; do not silently fall back to soft counts labeled q.

### 2. Modest multi-stage public model, with a direct baseline

Begin with regularized direct-terminal logistic prediction and a small
hierarchical multi-stage model; defer a large ensemble/neural policy. The joint
qualified probability factors through **conditional** first-response, timely
date and timely second-intention laws. Multiplying separately fitted marginal
yes rates loses shared dyad/actor dependence and selection into later stages.
Model pause separately: late positive intentions may pause without qualifying.

Use only decision-time public features. `build_public_data.py` currently creates
day-30 snapshots; using their later-revealed fields to predict an earlier
introduction leaks information. Reconstruct field values at assignment using
field_observed_day, released feedback at or before that decision, and deduped
past introductions. Unknown future values remain unknown. Label only mature
trials or fit a censoring-aware event-time likelihood; absence of a not-yet-
released date/second response is not failure. Full 60+40 follow-up is preferable
for new training collection.

Hold out entire seed clusters/pools, all their actors and all behavior replays.
Freeze the feature allowlist and finite model/calibration search before seeing
validation labels. Report joint terminal log loss/Brier and reliability with
whole-world uncertainty, conditional stage denominators, pause/return survival
and calibration on the action-changing score region. AUC or average Brier alone
does not establish useful action ordering or a uniform Q-error bound. Proper
scores assess honest probabilistic prediction; that objective still differs
from policy value. [Gneiting and Raftery](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf).

Practical collection can reuse the **structure**, not the already reserved seed
numbers, of R7 P2: 128 training and 64 validation seed clusters across six
families, with G/R/Q6 and a feasibility-safe exploration collector. R7 lists
4,608 behavior episodes in total; correlated policies on the same world do not
multiply independent worlds. Audit existing data first, forecast mature positive
counts and runtime, and register a smaller finite collection if the full budget
is unnecessary. Minimum mature-event/support criteria are fixed before data,
with an upper collection cap; failure selects a simpler model or narrower state
support rather than new validation until success.

Exit, busy and pause causes are not individually observed. Prefer a joint model
of public availability/releases, or an explicitly latent mixture conditioned on
pending history, over fabricated true-exit labels. Likewise anonymous arrivals
and profiles must be learned from public all-arrived histories, not hardcoded
family schedules, decoded IDs or generator mixtures. Existing P constants remain
a historical control, not proof of calibrated public training provenance.

### 3. Full-horizon parent rollout with robust switching

The clean improvement reference evaluates each complete candidate current action
with the **same frozen parent** through the remaining days 0–59, booking eventual
reward for a day-59 introduction. Including the parent and exact expectation
under the true public transition law yields a baseline-improvement result;
approximate transitions/Monte Carlo do not inherit it. [Bertsekas rollout lecture](https://ocw.mit.edu/courses/6-231-dynamic-programming-and-stochastic-control-fall-2015/resources/mit6_231f15_lec9/).

Full remaining horizon addresses B1's day-13 blind spot but does not discover all
coordinated waiting. In AB(day0)=1/2, AC(day1)=2/5, AD(day2)=9/10 with absorption,
holding today then following greedy tomorrow earns only 2/5. One-step rollout
therefore still chooses AB. Include a small two-decision lookahead or a wait-aware
base controller as a separately tested extension; retain one-step rollout as its
own control. Do not advertise policy improvement as global optimality.

Use common scenarios for action differences, an independent fixed winner-parent
check and a model set frozen from public training. Robust advantage is
`min_m[Q_m(action)−Q_m(parent)]`, using the same joint model for both actions;
unrelated pessimistic values do not evaluate the paired counterfactual. Retain
the parent if model disagreement, tail sensitivity, cap or guard is unresolved.
An ensemble is a sensitivity tool unless its uncertainty set is independently
shown to cover the true law. Baseline bootstrapping motivates conservative
unsupported-state behavior, but its MDP assumptions and guarantees cannot be
asserted for this fitted partial-observation simulator. [SPIBB](https://proceedings.mlr.press/v97/laroche19a.html).

Use the full-horizon version as an offline teacher first. Distill paired
action-parent advantages or a switch classifier only after teacher headroom;
test false-positive switch rate on independently evaluated held-out actions.
Every live invocation must profile full startup/parsing/scoring/search/output
costs. The existing 200-member **G fallback** timing is not active B1 evidence.

### 4. Complete-package targeted query VOI

Evaluate complete legal packages under the actual post-answer allocator, with
hard cost 3, soft cost 1 and budget 12. Start with immediate VOI under admitted
static matching; add dynamic VOI only after rollout fidelity. Include FIFO and
Q6 packages, displaced alternatives and no-query control. Joint actor profiles
are reused across incident edges. Declines/False remain actual answers; soft
queries never verify hard eligibility.

Condition answer/profile laws on selection and known status. Do not use entropy,
number of newly feasible edges or independently optimized hidden profiles as
reward VOI. Increased information need not improve a fixed heuristic allocator;
the relevant controller must be both simulated and deployed. Stop if the best
packages are action-identical to the parent or do not improve their own-parent
rollout contrast. Avoid a query×rollout integration before either component
demonstrates headroom; it consumes controls and runtime without identifying the
cause of a result.

## Identifiability and what new logging can establish

Historical deterministic propensities=None offer no known support for unchosen
whole matching/query actions. They support descriptive on-policy prediction,
not an unbiased IPS/DR policy certificate. A consistent outcome model can
extrapolate under additional assumptions; validation on selected actions does
not identify arbitrary alternatives. Standard logged-bandit propensity methods
explicitly depend on behavior action probabilities; matching occupancy also
makes this problem sequential, rather than an independent row-level bandit.
[Swaminathan and Joachims](https://proceedings.mlr.press/v37/swaminathan15.pdf).

If new exploration is collected, freeze its whole-action randomization and log
known probabilities/support plus pre-action public histories. Approximate
marginal edge probabilities are not full-matching trajectory probabilities.
Use these logs for coverage-aware fitting and local diagnostics; complete-policy
rollouts on held-out worlds remain the primary evaluation. Mixing deterministic
collectors broadens coverage but does not magically identify every unseen action.
Actor, pair and day replays share latent worlds and cannot be treated as
independent samples.

## Practical power, stopping and finite research scope

Retain independent seed clusters, equal six-family weights, terminal MSMI per
100 arrived by59 and 60+40 observation. A compact new screen can reuse R7's
**stage structure**: 48 complete clusters, at most two mechanism families
promoted; 96-cluster own-parent replication within the 12-arm cap; 128-cluster
selection only if a contender remains. Exact counts/controls/resources and new
fresh seed namespaces require a new freeze, not continuation of closed P4.
Use only the necessary portfolio: six references leave six P4 slots for
candidates and own-parent controls. Defer integration rather than omit controls.

These small stages allocate research; they are not powered confirmation of tiny
gains. Under the existing six-comparison .01 simultaneous protocol, independent
noncentral-t calculation gives the following 10%-inflated fixed sample counts:

| Planned cluster SD | Effect separation .10 | Separation .05 | Separation .025 |
|---|---:|---:|---:|
| .30 | 282 | 1,107 | 4,409 |
| .35 | 381 | 1,504 | 5,999 |

The calculation uses per-comparison positive-tail power 1−.10/6 and
`t_(1−.01/12,n−1)`. These are assumptions, not empirical variance guarantees.
At .30 SD, rejecting zero when truth is +.05 requires 1,107 clusters, or 46,494
episodes for one candidate plus six references across six families. Certifying
a lower bound above +.025 at truth +.05 has separation .025 and exceeds the
existing 1,800-cluster cap. A claim merely of observed mean≥+.025 is different
from certified practical superiority. Size from held-out selection-stage
variances before sealed confirmation, respecting the .30 floor; never use E
means/variances or extend until significance. A true +.05 gap against G alone
does not imply +.05 against P and Q6.

Stop criteria should be constructive and explicit: no incremental action firing
or no same-score mechanism headroom => drop that variant; failed mature-count,
proper-score or conditional-support gate => simplify model/support; failure of
own-parent point gain or service screen on a complete replication grid => no
promotion; measured runtime/resource excess => reduce the registered portfolio
before a new freeze; no selected contender => no confirmation. Preserve all
negative variants and evaluate all registered comparisons. Use no unregistered
interim reward peeks or significance stopping. Family safety point filters are
not all-family noninferiority proofs; nonsignificance is not equivalence.

## Review integration

Theory and director REPORT review will be appended when their drafts are
available. Current recommendations are executable work orders for future
registered development, not claims that any proposed policy already wins.
