# Independent final statistical review

Reviewed 8 October 2026. This review uses completed recorded results only; it does
not change policies, configurations, the registry, or results, and runs no new
simulator experiments. Calculations below were independently reconstructed with
NumPy/SciPy from raw episode rows rather than calling the project's analysis
function. Calibration summaries were independently recomputed from assignment
prediction/label rows without dumping those rows.

## Defensible confirmatory conclusion

The frozen `simple_fifo` candidate **does not establish an improvement over
shipped greedy**. Its confirmation estimate is lower, but the registered
two-sided test does not establish inferiority either. Neither policy is a
statistical winner in this confirmatory comparison. Failure to reject zero is
not evidence of equivalence.

The registered 95% paired seed-cluster interval has upper endpoint
**+0.00773463 MSMI/100**, well below the **+0.10 MSMI/100** practical improvement
used for sample-size planning. Thus the targeted +0.10 gain is excluded by that
registered interval, under its sampling and coverage assumptions. Small positive
effects remain compatible with the interval; an effect exactly equal to zero,
performance equivalence, and generalization beyond the six simulator families
are not established. The target of developing a substantially better policy was
not achieved by this candidate. The completed study is a credible negative
result, not a reason to retune on confirmation seeds or extend the sample until
significance appears.

## Independent primary reconstruction

For each policy and seed, I averaged the six family rewards, then subtracted
greedy's seed mean from the candidate's. These 40 differences, rather than 240
family rows, form the independent units.

| Quantity | Independently reconstructed result |
| --- | ---: |
| Greedy scenario-balanced MSMI/100 | 0.3729166667 |
| `simple_fifo` scenario-balanced MSMI/100 | 0.3312500000 |
| Candidate minus greedy | -0.0416666667 |
| Paired seed-difference SD | 0.1544681160 |
| Student t statistic, 39 df | -1.7060034470 |
| Registered two-sided p | 0.0959604545 |
| Registered 95% paired t CI | [-0.0910679668, +0.0077346335] |
| Standardized paired effect, mean/SD | -0.2697428294 |
| Seed clusters favoring candidate / tied / favoring greedy | 10 / 12 / 18 |
| Registered 10,000-replicate cluster bootstrap, RNG 90210 | [-0.0895833333, +0.0042187500] |
| Independent 100,000-replicate sensitivity bootstrap, RNG 8102026 | [-0.0895833333, +0.0062500000] |

The registered calculation matches `confirmation_statistics.json` exactly at
floating-point precision. The additional bootstrap is a numerical sensitivity
check, not an additional confirmatory test. Rare, discrete rewards mean Student
t coverage is approximate. Both bootstrap intervals also span zero. Pairing
controls shared generated worlds, but differing chosen dyads/days do not share
every downstream outcome stream. There is one registered confirmatory contrast;
family and calibration slices below are descriptive and should not be promoted
to unadjusted confirmatory tests.

## Completeness, provenance, and row checks

The exact Cartesian grid is present: two policies × seeds 3001–3040 × six
families = 480 rows, with no missing, extra, or duplicate cells. Every row records
`valid=true`, zero failures, 200 arrived members, and 120 JSON-interface
invocations. All 480 referenced trace paths exist. The source marks the run
complete and records 480 planned episodes. Candidate rows all use
`{"model":"simple"}`; greedy rows use `{}`.

All six inference/source SHA256 values in `frozen_candidate.json` match both
confirmation metadata and current file bytes. Its three auxiliary hashes also
match current files (`policy.py`, `research/extended_benchmark.py`, and
`research/extended_select.py`). The freeze metadata reports
2026-10-08T06:16:43.879895+00:00 and seeds 3001–3040. This is consistency evidence
for the freeze; file metadata alone is not a tamper-proof historical record.

All episode reward values equal `100 * qualified_count / arrived_members`.
Funnel count ordering, served/unserved totals, coverage denominators, mutual
acceptance rates, and date-completion rates are consistent in every row.
The 240 calibration episode summaries match raw selected-policy assignment and
qualified counts exactly. No error requiring correction was found in the
confirmatory statistics or recorded grid.

## Funnel and scenario findings

These are pooled raw counts, not independent assignment-level significance
claims. Candidate versus greedy makes 179 more introductions and completes 63
more dates, yet records 20 fewer qualified outcomes. This disproves using date
count alone as a proxy for the registered terminal objective in this run.
It does not isolate a causal mechanism for the loss.

| Policy | Introductions | Mutual accepts | Dates | Qualified MSMI |
| --- | ---: | ---: | ---: | ---: |
| Greedy | 17,954 | 2,428 | 1,849 | 179 |
| `simple_fifo` | 18,133 | 2,434 | 1,912 | 159 |

Coverage is 34.01875% versus 34.02917%; both policies incur aggregate ask cost
48,720 (episode mean 203). Episode-mean mutual acceptance rate is 13.7244%
versus 13.7111%; episode-mean date-completion rate is 75.3725% versus 77.9413%.
These means of episode ratios should not be confused with ratios of pooled
counts. Recorded mean inference latency is 15.5166 ms versus 11.1050 ms;
maximum latency is 81.3228 ms versus 53.7527 ms. Candidate maximum serialized
memory is 155,066 bytes and maximum request size is 638,461 bytes. These timing
measurements describe in-process execution, not a separately established
container latency comparison.

| Family | Greedy qualified | Candidate qualified | Candidate minus greedy MSMI/100 | Candidate both-positive / qualified |
| --- | ---: | ---: | ---: | ---: |
| Development family | 37 | 29 | -0.1000 | 99 / 29 |
| Sparse | 8 | 7 | -0.0125 | 23 / 7 |
| Cold start | 35 | 38 | +0.0375 | 97 / 38 |
| Delayed | 32 | 32 | 0.0000 | 94 / 32 |
| Shift | 30 | 25 | -0.0625 | 85 / 25 |
| Drift | 37 | 28 | -0.1125 | 91 / 28 |

“Development family” is a scenario name here; all these rows use confirmation
seeds. There are 489 both-positive outcomes for the candidate, of which 330
fail terminal qualification. The audit episode key `late_feedback_both_yes`
actually counts **any** both-positive terminal disqualification, including a
late date. It cannot attribute all 330 failures solely to feedback delay.

## Terminal and reciprocal calibration

Assignment-time prediction summaries cover 18,133 selected introductions and
40 seed clusters. I reproduced all five pooled predicted means, observed means,
log losses, and Brier scores from stored prediction/label rows. These describe
chosen introductions, not every feasible edge or an untouched new calibration
training sample.

| Unconditional stage | Events | Mean predicted | Mean observed | Log loss | Brier | AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Both respond | 10,576 | 0.585268 | 0.583246 | 0.680275 | 0.243588 | 0.501535 |
| Both accept | 2,434 | 0.176904 | 0.134230 | 0.403078 | 0.118621 | 0.487559 |
| Date | 1,912 | 0.137658 | 0.105443 | 0.343026 | 0.095706 | 0.495319 |
| Both positive second intention | 489 | 0.032005 | 0.026967 | 0.125895 | 0.026360 | 0.480253 |
| Qualified terminal | 159 | 0.011488 | 0.008769 | 0.050859 | 0.008707 | 0.507363 |

Terminal prediction is 1.14882% versus 0.876854% observed. Seed-balanced signed
observed-minus-predicted error is -0.00281034, with 95% t CI
[-0.00473234, -0.00088834]. Seed-balanced log loss is 0.0504428
(CI [0.0407694, 0.0601163]); Brier is 0.00862154
(CI [0.00654298, 0.0107001]). These estimands average within-seed assignment
metrics; they differ slightly from pooled assignment-weighted metrics above.
The direction indicates overprediction on this selected cohort, not successful
terminal calibration. AUC near 0.5 offers weak evidence of useful discrimination;
no discrimination uncertainty interval or superiority claim follows from it.

The terminal reliability bins have predicted/observed means 0.00623283/0.00839944
(n=2,143) and 0.01219255/0.00881801 (n=15,990). Whole-seed bootstrap observed
intervals are [0.00384085, 0.0134940] and [0.00666155, 0.0110601], respectively.
The larger bin shows overprediction; neither plot nor a small Brier value alone
establishes calibration of this rare-event model.

Terminal observed/predicted probabilities by family are: development
0.007993/0.011404; sparse 0.008264/0.011671; cold start 0.013518/0.011817;
delayed 0.009068/0.011516; shift 0.006812/0.011338; drift 0.007675/0.011399.
Cold start is the only family whose pooled terminal mean exceeds its prediction.
These slices lack a registered family-specific causal or superiority comparison.

With fewer than 20 prior feedback observations, n=3,859, terminal prediction is
constant 0.0117, observed 0.011143, AUC 0.5. With at least 20 observations,
n=14,274, prediction is 0.011431, observed 0.008127, AUC 0.504839. The latter
slice does not demonstrate successful adaptation; history amount also co-varies
with assignment time and selected population.

Missing-soft-feature bins show observed/predicted terminal probabilities:
zero missing 0.005618/0.011438 (n=4,806), one missing
0.055556/0.010381 (n=72; four events), two missing
0/0.012115 (n=535; no events), three missing
0.005645/0.011474 (n=2,480), **at least four** missing
0.011133/0.011490 (n=10,240). JSON key `"4"` pools four through eight missing
fields. Small subgroups and zero-event bins cannot establish robust calibration
or missingness effects.

Simple-model directional conditional fields are auxiliary parametric diagnostics;
its primary joint probabilities use direct mature empirical counts. They should
not be presented as a coherent factorization of its direct joint model. This
qualification is documented in the common-cohort audit caveat but should also
accompany any use of confirmation conditional summaries. Conditional date and
qualification means concern stage-eligible selected samples, not population
probabilities.

## Synthetic demographic associations

Candidate pooled coverage by gender is men 33.6935%, women 33.9555%, and
nonbinary members 36.3755%. By age, coverage is 32.9377% for 21–29, 35.1591%
for 30–39, and 33.8345% for 40–46. For the four ordinary zone labels it is
45.1387% (zone_a), 31.9774% (zone_b), 21.3251% (zone_c), and 11.4720%
(zone_d). The sparse-family zone_0–zone_11 labels are different groups and
should not be merged into those ordinary labels.

These are synthetic descriptive episode-member counts; repeated worlds across
families are correlated. There is no demographic intervention, adjusted causal
analysis, or independent-member sampling justification. These numbers identify
coverage associations for investigation, not policy-caused discrimination or a
confirmed demographic improvement over greedy.

## Reviewed artifact fingerprints

| Artifact | SHA256 |
| --- | --- |
| `results/extended/confirmation.json` | `12885c0e8768dd1263beef1da017d53ae521f2112ed3b97f5f125dc978755f80` |
| `results/extended/confirmation_statistics.json` | `dd493bee04c22db11d19006307c5dd194d314a7e886ac2446a448350926152df` |
| `results/extended/audit_confirmation_calibration.json` | `6416c142c37c5e36f9b444aa16f43bae1d691416a3cdf31696d3bde4c0214526` |
| `results/extended/frozen_candidate.json` | `6b33c328910a7e9523db2ee5af4711ae0caddb6c9d73235be081bcd4bd445f25` |
| `research/EXPERIMENT_REGISTRY.md` | `f28b4454f2ed748471bfec42ad6eb144173c0a9674918f2ef6471f8b551a39bd` |
