# Round 3 statistical review and prospective plan

9 October 2026. Author: empirical statistician/adversarial critic. Reviewer: director.
This is a recommendation for the director's registry, written before any new
simulation by this agent. The registry must adopt concrete candidate names and
seed counts before each affected stage. No simulation seeds were run here.

## Estimand and eligibility

For policy p and seed s, Y[p,s] is the mean of six family episode qualified
MSMI/100 ratios after action days 0–59 and 40 follow-up days. The primary paired
effect is mean_s(Y[candidate,s]−Y[shipped greedy,s]). Six families sharing a seed
are one cluster, not six independent replicates. Retain episode denominators;
report pooled ratios separately from means of episode ratios. The current
policy.py is modified: the comparator must implement kit.baseline_asks and
kit.baseline_match through a frozen observation-only JSON adapter.

Every planned row must be present once, valid, and contain failure accounting.
Invalid policies are ineligible for superiority; failures are retained, never
silently omitted. Harness/environment reruns require a documented cause and
retain original rows; policy-related failures cannot be discarded as accidents.

## Partitions and staged design

The inventory conservatively excludes all inherited observations and intended
round-2 ranges even where complete records are absent. Additionally reserve
1–10000 as a guard band. Recommended disjoint partitions are training 10001–10040
(optional), screening 11001–11012, focused 12001–12032, selection 13001–13020,
and untouched confirmation reserve 14001–14200. The director may adopt alternate
fresh ranges after verifying the inventory; recorded ranges take precedence.
Never use the confirmation reserve for diagnostics, calibration, debugging or
power pilots. Training outcome rows cannot also become untouched validation.

Stage A uses inherited seeds or clearly designated development smoke seeds.
Stage B screens 8–12 diverse candidates on 12 paired clusters × six families.
These are explicitly noisy exploratory results. Promote at most three eligible
candidates with nonnegative paired mean and a concrete mechanism, plus one
prelisted simple control. A credible simplification or structural failure result
may justify a control with negative mean; record the exception before Stage C.
Screening p-values receive Holm adjustment over all candidate-versus-greedy
contrasts, including rejected candidates. Unadjusted effects and intervals remain
visible. This screen cannot establish superiority.

Stage C compares survivors and mechanism ablations on 32 fresh clusters. This
meets the requested 30–50 cluster serious-comparison scale. Prefer candidates
with consistent paired gains and acceptable scenario/resource behavior; do not
use a single influential seed or descriptive mechanism as causal proof.
Register the ablation list first. Report leave-one-seed-out effects and per-family
results. Ablation contrasts receive Holm correction within a declared family.

Stage D evaluates at most three frozen finalists plus greedy on 20 fresh selection
clusters. No refitting, feature changes, or threshold changes after selection.
Select among eligible finalists within .03 MSMI/100 of the highest selection
mean by the prelisted complexity order, then lower maximum latency, then
alphabetical name. The .03 band is an engineering choice, not equivalence.
Freeze all inference/preprocessing/config hashes and specify exactly one primary
candidate-versus-greedy confirmation. If all candidates fail promotion, a
registered simplest control can still receive confirmation to quantify a negative
result; the registry must declare this before viewing selection results.

## Fixed confirmation and power

A practical gain is +.10 MSMI/100. Confirmatory superiority at alpha .05 requires
a positive lower endpoint of the two-sided 95% Student-t paired cluster interval,
a positive mean, and complete valid execution. A point estimate >=.10 alone is
insufficient. A claim that the gain exceeds .10 requires the lower endpoint >.10.
An upper endpoint below .10 rejects that targeted magnitude under interval
coverage assumptions; failure to reject zero does not establish equivalence.

Before opening confirmation, use only the 32 Stage-C paired differences for the
selected candidate to choose a fixed sample. Conservative planning sigma is
max(.21, observed Stage-C SD). Fixed n = max(40, ceil(1.10 ×
((1.959964+.841621) × sigma/.10)^2)), capped at 200 clusters. This is an approximate
80% power calculation with 10% sample margin, not guaranteed power. For sigma
=.21, n=40; sigma=.30 gives n=78; sigma=.40 gives n=139. If the formula exceeds
200, fix n=200 and disclose approximate underpower rather than claiming 80%.
The confirmation registry must record sigma, n, exact seed list, code hashes,
comparison and decision rule before execution. No significance-driven extension,
retuning, replacement candidate, or early success stopping. Finish the full sample.

The prior completed confirmation has paired SD .15447, but adaptive new policies
may have higher variance; using that SD alone would understate potential cost.
At n=40 and sigma=.21, a normal 95% half-width is about .065 MSMI/100.

## Analysis and diagnostics

Primary: paired mean, SD, standardized paired effect, Student-t CI and two-sided
p-value, with one confirmatory comparison. Sensitivity: 10,000 paired-seed
bootstrap means with RNG seed 993710 and percentile CI. The bootstrap is not an
independent confirmation and cannot override the registered t criterion. Rare
rewards, nonnormal differences and finite seed support limit approximate coverage.

Report per-family paired estimates, coverage, acceptance/assignment,
dates/mutual acceptance, positive pauses, deadline losses, repeat endpoints,
queries/cost, mean/p95/p99/max invocation latency and serialized memory/request
sizes. Counts with zero denominators must be labeled and retained. Use all six
family outcomes together when bootstrapping a seed. Secondary outcome claims
are descriptive unless a separate multiplicity-controlled family was registered.

Predictive comparisons require identical assignment-time examples and publicly
resolved outcomes, with no hidden truth in training. Compute assignment-weighted
log loss/Brier and seed-balanced means separately. Pending labels remain censored
until supported deadlines resolve. Reliability uncertainty resamples seeds;
all-zero small bins cannot imply certainty. Offline logged-policy learning must
report action coverage and avoid unsupported counterfactual evaluation.

Common random seeds do not imply identical funnel draws when dyad/day changes:
rand_for keys seed, endpoints and assignment day. Allocation changes and altered
retirement histories change support. Scenario families are correlated and drift
or delayed variants have different mechanisms. Mechanism attribution needs
registered interventions/ablations, not only trajectory descriptions.
