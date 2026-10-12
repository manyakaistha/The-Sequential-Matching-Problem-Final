# Round four prospective prediction review

Owner: next-mechanisms researcher; named reviewer: empirical statistician/director.
Source frozen before screen B. Audit specification written before B results;
no fitting, coefficient changes or unseen outcome access. Execution is gated on
the **complete registered C** grid81001–81032. Compute allowance5 CPU minutes,
one offline process. Forecast correctness is separately reviewed by production;
this script recomputes actual deployed scoring modules, with independently
written label/aggregation/uncertainty calculations. It is not an independent
likelihood reimplementation.

## Prospective state contract and leakage safeguards

The runner records full public state after ask resolution and before matching at
all60 greedy invocations, including those with no assignments. Each record is
`match_states=[{'day':d,'state':...}]`. Members, disclosed fields/status/timestamps,
availability, prior introductions and received feedback are included; redundant
ask_log may be omitted. No world, truth, scenario label, future event, seed or
private actor parameters enters a forecast. Seeds/families attached externally
are for clustering/slices only.

Pair snapshots alone are insufficient for the actor-acceptance model: earlier
partners may have subsequently disclosed fields available **now**, and those
current disclosures can legitimately inform the past-fit likelihood. Rebuilding
these states from final disclosures would leak future information. The director
added full match states **before B**. The audit refuses missing states and will
not impute/reconstruct them from future logs.

At each used state it checks all member arrivals and field-observation timestamps
at/before assignment day, all prior introductions strictly before that day, and
all feedback received at/before it. It checks every pair snapshot equals the
member record in that same state, hidden parameter keys are absent,60 states
exist, all assignment snapshots correspond one-to-one to introductions, completed
public terminal labels sum exactly to official episode counts, and C baseline
grid is complete/valid/zero-fallback. Completed labels are used only after the
forecasts are computed from prospective state.

## Hypotheses and fixed comparisons

Four predictions on **identical greedy-assigned examples**: public population,
moment-matched Beta actor response, exact Uniform actor response, and acceptance
shrinkage plus exact response. Controls are the deployed architectural parents.
No new model is fitted on this cohort and none uses source snapshot predictions.
The original preparation restricted the audit to terminal scores. Before C
completion, the director requested coherent full-funnel projections derived
from the same fixed approximate model. The audit now reconstructs five stages:
both submit introduction responses; mutual acceptance; date happens; both
positive second submissions/positive pause; qualified terminal reward. It verifies
the reconstructed terminal forecast equals the actual deployed scorer within
1e−12 on every example. No inference source or terminal contrast changed.
These are approximate-model projections, not separately fitted regressions.

Four fixed contrasts, each for log loss and Brier: Beta−population,
Uniform−Beta, acceptance−Uniform, acceptance−population. Lower is better.
Acceptance improves proper loss only if the relevant upper paired95% interval
is below0; positive lower interval argues against its predictive hypothesis.
Intervals crossing0 are inconclusive. Holm correction covers all8 tests; no
post-hoc model or slice is promoted as a confirmatory result.

For each model, average assignment loss within each episode, average its six
families equally within each seed, then average32 independent seed clusters.
Paired differences use the same balancing. Report Student-t95% intervals and
10,000 whole-seed percentile bootstrap sensitivity with fixed RNG90210.
Pooled assignment-weighted losses are reported separately and can differ from
the scenario/seed-balanced estimand. Zero-assignment episodes make assignment
loss undefined; the script stops rather than silently dropping them. This
does not change policy reward, for which zero assignments is a valid zero.

Fixed reliability bins:0–.005,.005–.01,.01–.02,.02–.04,.04–1. Binned summaries
are pooled descriptive rates, with whole-seed bootstrap ratio intervals and
supporting seed counts. Fewer than6 supporting seeds or all-positive/all-negative
bins have no informative interval; plotted crosses mark them. Missingness,
history-size, time and six-scenario slices are descriptive, without assignment
independence claims. No calibration adjustment is fitted.

## Interpretation limitations

The cohort is deterministic greedy-selected, not random edge coverage. Better
proper loss on these examples does not establish better ranking of alternatives,
transport to the candidate-selected pool or higher sequential reward. Public
current fields for earlier partners are valid at each invocation but future
ones remain inaccessible. Acceptance ignores joint regime/partner/shared-effect
posterior, second-stage evidence and selection updates; Gaussian moment matching
and inherited five-point quadrature remain approximations. Exact response moments
do not make the entire full-funnel model exact. Rare terminal events constrain
power even with32 clusters. Predictive improvement must be compared to terminal
policy outcomes and trajectory quality audits before mechanism attribution.

## Prepared verification and execution

Cheap helper checks before fresh result inspection passed: proper-score known
values, mean/CI helper, exact deadline boundary label30/3 versus missed34,
public-state timestamp check and rejection of a future feedback event. The only
simulator observation used was previously examined seed101 day0; no episodes
were run by this audit task. Candidate sources were not edited in this wave.

When C is complete:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m research4.prediction_audit --input results/research4/focus.json --output results/research4/prediction_audit.json > results/research4/prediction_audit.log
```

The script refuses overwriting completed JSON, records input/trace/source hashes,
timestamps, exact argument vector and measured CPU, and produces a PNG. Final
numerical findings will be appended only after the complete fixed cohort audit.
Full-funnel projection helpers were checked against the actual deployed terminal
functions for constructed count/soft/actor states before C audit execution.


## Completed fixed-C numerical findings

All768 focused episodes were complete before launch. The audit used only192
C greedy episodes:14,023 prospective assignments,125 qualified outcomes,
32 independent seed clusters. Measured audit CPU28.84 seconds, one process,
within5-minute allowance. Prelaunch and closing source hashes agree, input hash
is unchanged, full-public-state leakage guards and terminal/core equality passed
on every example. Figure inspected: four model labels/readable axes, overlapping
cluster intervals, no implied superiority. No confirmation input was opened.

|Model|Scenario/seed-balanced log loss|Balanced Brier|Pooled log loss|Pooled Brier|
|---|---:|---:|---:|---:|
|population|.056267956|.009964263|.050796892|.008833878|
|Beta|.056099696|.009959682|.050653216|.008829657|
|Uniform|.056095477|.009959519|.050651198|.008829537|
|acceptance|.056167249|.009961018|.050721307|.008831063|

All eight paired terminal contrast intervals cross0. Holm-adjusted p is.92426
for Beta−population Brier and1 for the other seven. Bootstrap sensitivities
also cross0 for every contrast. Thus neither exact-Uniform refinement nor
acceptance learning establishes better terminal proper scores on this cohort.
Point order is not proof of useful ranking or equivalence.

|Contrast|Metric|Paired mean loss change|95% seed-cluster t interval|Holm p|
|---|---|---:|---|---:|
|Beta−population|log loss|−.000168259|[−.000460178,+.000123659]|1|
|Beta−population|Brier|−.000004581|[−.000010352,+.000001189]|.92426|
|Uniform−Beta|log loss|−.000004220|[−.000035112,+.000026673]|1|
|Uniform−Beta|Brier|−.000000163|[−.000000890,+.000000563]|1|
|acceptance−Uniform|log loss|+.000071772|[−.000083697,+.000227242]|1|
|acceptance−Uniform|Brier|+.000001499|[−.000001988,+.000004986]|1|
|acceptance−population|log loss|−.000100707|[−.000375882,+.000174468]|1|
|acceptance−population|Brier|−.000003245|[−.000008612,+.000002122]|1|

The exact response posterior has mathematical support, but its point terminal
improvement over the already matched-moment Beta prior is tiny. Acceptance's
point terminal loss is worse than Uniform while its interval is inconclusive.
The intended acceptance-update mechanism therefore does not earn a predictive
superiority claim, independent of any policy-reward results.

### Descriptive coherent funnel diagnostics

Pooled public outcomes:8,117 both-respond introductions,2,079 mutual acceptances,
1,612 dates,366 positive pauses and125 qualified outcomes. Correct conditional
rates:mutual among both responding25.613%;date among mutual77.537%;positive
pause among dates22.705%;qualification among positive pauses34.153%. These are
stage-conditional denominators, not assignment-independent samples.

Both-response prediction is improved descriptively by response history:population
pooled log loss.680749 versus Uniform.676171;Brier.243826 versus.241636.
Observed mean.578835, population forecast.585225 and Uniform.580954.
No stage-specific inferential superiority test was added.

Acceptance learning's pooled mutual-acceptance log loss.412918 is lower than
Uniform.413111, and conditional mutual-given-both-response log loss.556314 is
lower than.557386. This modest stage point benefit does not carry through to
terminal proper scores. Positive-pause forecasts remain high:Uniform mean.028328
versus observed.026100;acceptance.028137. Conditional positive-pause-given-date
forecasts~.2475–.2477 exceed observed.2270. Qualification-given-pause forecast
~.35865 versus observed.34153 is consistent with a finite sample shortfall but
has no new calibration adjustment. Date-given-mutual forecast remains the exact
public.78 versus observed.77537.

Reliability bins have overlapping uncertainty, especially the sparse high-score
bin near.02. The same examples are redistributed among bins by model scores;
those pooled bins do not establish which model ranks unobserved alternative
edges better. Scenario, missingness, actor-history and time slices are preserved
as descriptive tables in the JSON, not searched hypotheses or tuning targets.

A plausible unresolved modeling limitation is second-stage/availability selection:
actor acceptance learning does not update second bias or the nuisance posterior
from the complete reciprocal history. That is an approximation diagnosis, not
an observed causal explanation for overprediction. A future candidate would need
its own controls and independent seeds; this audit fits or retunes nothing.


## Independent numerical review

The statistician independently checked14,023 saved prediction rows/125 labels
against C greedy totals and all192 episode groups; recomputed episode/family/
seed loss balancing and all8 t/bootstrap/Holm contrasts matched within1e−12.
All intervals cross0, minimum adjustedp.9242579. The written addendum is in
FOCUS_REVIEW.md. This verifies labels and aggregation, not an independently
reimplemented numerical likelihood or a universal forecast correctness proof.
