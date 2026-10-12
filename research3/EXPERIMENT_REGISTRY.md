# Round 3 prospective registry

Registered 9 October 2026 before new-seed policy evaluation. Completed old studies
and all their planned/exposed seeds stay excluded; see seed_inventory.json.
Old traces are training/audit evidence, never untouched confirmation.

## Endpoint and legal protocol

Primary: qualified MSMI/100, equal weights over the six shipped families, averaged
within seed before inference. Actions days 0–59; forty follow-up days. No truth,
seed, variant label, future events or busy-release time reaches policies. Public
mechanism priors are allowed and documented. Comparator is kit.baseline_asks and
kit.baseline_match, not the modified root policy.py. All invalid episodes remain
visible and disqualify promotion until a documented correction and full rerun on
development; confirmation failures never silently disappear.

## Partitions and stages

Training: old greedy prospective snapshots on seeds1001–1005. Validation1006–1008.
Only offline terminal logistic coefficients fit labels; these must be frozen
before Stage B. No new round seed contributes to population training.

A: already exposed seed101 smoke/protocol, exact tiny models, and old matched
cohort calibration. No fresh evidence claimed from these replays.

B: 70001–70012, all six families, all 13 listed candidates. Broad exploratory
screen. Eligibility requires complete grid, legal valid episodes, zero failures
and zero optimized-path fallbacks. Promote three eligible nonbaseline candidates by primary mean, ties by
alphabetical name. Record Holm adjustment over all twelve comparisons to greedy;
promotion is exploratory and does not require significance.

C: 71001–71032, all six families. Promoted three plus greedy, clean, population
(deduplicated), and each promoted query candidate's identical scoring without
queries. This supplies 32 independent clusters for serious paired comparisons.
No new configuration may enter except a documented ablation before C starts.
Top two eligible nonbaseline candidates by primary mean proceed to D; clean and
population are mandatory controls in D. Mechanism and common-cohort prediction
audits use A–C data. No fitting or hyperparameter revision after B.

D: 72001–72020, all six families, C top two + clean + population + greedy,
deduplicated. Among new policies within .025 of the highest primary score, choose
lowest engineering cost: no learned/integrated scorer (0), offline fixed (1),
population quadrature (2), online response (3); then no soft queries, then higher
mean, then alphabetical. This preference is not an equivalence claim. Greedy is
comparator, not a new candidate. Freeze selected source/config and preprocessing
before E. Selection cannot use E results.

E: fresh seeds73001 onward, selected versus greedy, all six families. Fixed sample
n=max(40,ceil(1.10*((1.959964+.841621)*s/.10)^2)), capped160, where s is max(.21, selected candidate's
paired seed SD on C). If the candidate was not in C use population's C SD and flag
this planning limitation. Register actual n and hashes before first E invocation.
Cap may reduce power; report it. Run every planned episode, no significance-driven
extension, alternate candidate, stopping or retuning. Practical target +.10.

## Analysis and multiplicity

One confirmatory paired two-sided Student t comparison alpha .05, seed clusters,
95% CI; bootstrap10,000 paired seed resamples RNG90210 as sensitivity. Superiority
requires positive lower CI; targeted +.10 is assessed separately. No nonsignificance
means equivalence. Report standardized paired effect and scenario contrasts.
Exploratory Holm family includes all candidate-versus-greedy contrasts per B/C/D,
not just promoted contrasts. Follow-up ablations are explicitly exploratory.

Report raw denominators, coverage, assignments, mutual response/acceptance, dates,
positive pauses, deadlines, repeat endpoints, asks, latency quantiles/max, failures,
request/memory sizes. Distinguish means of ratios from pooled counts. Matched
cohort prediction assessment uses logloss/Brier and seed-balanced uncertainty,
reliability/missingness/time/history/scenario slices; no AUC-only ranking claim.

## Candidates, hypotheses, falsifiers

All use legal greedy allocation, observed availability/nonrepeat and a strictly
positive-score allocation filter, deterministic canonical ties, empty serialized memory, bounded guard and
legal empty fallback. No files/network read at evaluated inference.

| Name | Change / falsifiable hypothesis |
|---|---|
| greedy | shipped reference |
| clean | remove three outcome-irrelevant soft equality fields; reward may still fail |
| goal | goal-only ranking; second-stage importance may outweigh omitted fit |
| canonical | no informative ranking; tests whether ranking earns complexity |
| random_order | public ID/day hash ordering; controls canonical order effects |
| public_weight | robust positive goal/pace/conversations ranking; avoids lifestyle regime sign |
| population | coherent integrated public population funnel; no sparse personalization |
| scarce | low-degree endpoints first; improves usable opportunity count |
| response | resolved public propensity shrinkage over population; improves repeat ranking |
| throughput | reward per expected busy duration; frees useful repeat capacity |
| offline | regularized mature terminal logistic fit on old seed-split data |
| goal_queries | public_weight plus surplus goal asks on current feasible neighbors |
| four_queries | population plus surplus four informative soft fields |

For each, effect <=0 on serious paired data challenges its reward hypothesis;
improved prediction alone cannot rescue an adverse reward result. Detailed model
assumptions/strongest cases/counterexamples are in THEORY_MODELS.md and critic review.

## Resources and record

Two worker processes max, no external spend. Pilot shipped episode costs about
2.3s wall on one process (seed101); B's936 episodes expected ~36 CPU min, ~18min
elapsed with two workers, plus trace overhead. Measure actual usage rather than
promise timings. Prospective snapshots/completed public outcomes stored separately.
Inference restrictions tested independently after freeze: two cores, one GiB,
64PIDs, read-only offline container,10s, strict memory below1MiB, image-size limit.
If infrastructure is unavailable report the limitation; don't claim tests passed.

## Descriptive clarification after B, during C (no rule or source change)

Public_weight and goal_queries can return score zero when disclosed goal, pace
and conversation equalities are all false. The existing positive-score filter
omits those legal edges. The original wording “positive scores” was imprecise;
this correction describes the already frozen executable, not a new threshold,
candidate, hypothesis test or revised promotion. Soft queries can change ranking
and zero-score omission while preserving hard-bundle schedules. Their isolated
mechanistic contributions remain unresolved. A separately documented final-day
controlled audit on already examined B worlds is diagnostic only; no derived
augmentation policy enters C/D/E or the selected comparison.

Commands, versions, hashes, written critic/statistical/correctness reviews,
replication, compressed archives/restoration and final manifest are required.
