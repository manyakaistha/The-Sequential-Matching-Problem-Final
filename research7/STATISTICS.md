# Fixed statistical protocol for research7

This file supersedes the critic memorandum's illustrative grid/budgets; the adopted counts/resources are exactly PLAN.md, PLAN_7A.md and PLAN_7B.md. The memorandum is preserved as planning review history, not a competing registration. All numbers here are planning choices. No new reward data were generated.

## Endpoint and sampling unit

Families F=(development,sparse,cold_start,delayed,shift,drift), each equal weight. For policy p, seed s and family f, let Q_psf be qualified terminal MSMI introductions, A_sf the number arriving by day59, and Y_psf=100 Q_psf/A_sf (zero if A=0). Use60 action+40 follow-up days. One qualifying pair counts once. Coverage uses distinct arrived-by59 members served, divided by that same A.

For candidate C and baseline j:

    D_sj = (1/6) sum_f (Y_Csf - Y_Bj,sf)
    mean_j = mean_s D_sj
    sd_j = sample_sd_s D_sj
    SE_j = sd_j / sqrt(n).

Independent seed clusters are the inferential units. Families, policies, repeated actors and introductions within a seed are correlated. Complete all six families/all registered policies before a cluster is admissible. Missing/invalid cells cannot be dropped to obtain a favorable result. Require initial-world hashes and denominator equality across policies. Same numerical seed across scenario families does not imply identical latent worlds, because generation consumes variant-dependent random streams.

Frozen panel: G,N,R,P,K,Q6 with exact implementations/source/config/assets hashes. Q6 means the unchanged R6 N3_two. Existing policy names alone are insufficient to identify baselines. Official random behavior is preserved exactly, not weakened or newly seeded to help the challenger. Any panel failure is resolved before new stage data; a strong/inconvenient comparator is never silently dropped.

## Primary comparisons and verdict

Only one selected/frozen R7 candidate enters confirmation. Round7 family alpha=.01. For6 comparisons use simultaneous Bonferroni two-sided intervals

    L_j,U_j = mean_j +/- t.ppf(1-.01/(2*6), n-1) SE_j.

Each interval has nominal99.833333% coverage, giving at least99% simultaneous coverage under valid individual t approximations. Contrast dependence does not invalidate Bonferroni. Publish unadjusted p-values with Holm-adjusted six-comparison p-values as supporting summaries; the lower-bound rule owns the verdict. If all differences are identically zero, interval=[0,0], p=1 and no superiority. A constant nonzero difference requires explicit degeneracy reporting; do not silently divide by zero or claim standard-t assumptions were verified.

Adopt candidate only if every L_j>0, observed mean_G>=+.025, all assessed episodes valid, complete provenance and independent production/statistical reviews close. This proves neither all-family superiority nor global optimality. Observed+.025 is a practical-size screen, not a certified minimum benefit. Established practical superiority requires L>.025; the ordinary design below is powered for rejecting0 at true+.05, not for certifying+.025 at true+.05.

If one panel contrast fails, the all-panel claim fails; individually supported simultaneous comparisons may still be reported. If G comparison fails, retain G by default. No equivalence or noninferiority conclusion is inferred from nonsignificance. A round-specific alpha allocation does not create a lifetime guarantee over arbitrary future research rounds.

## Development stages and selection

P2a small pilot is development only; it is not merged with P3 or counted as independent confirmation. P3/P4/P5 gates and candidate limits are frozen in master plan. Analyze all predeclared comparisons, not only survivors; report raw means/95% exploratory intervals and Holm summaries over each stage's complete comparison graph. P5 nominal one-sided90% bounds rank contenders; they do not establish confirmatory effects after search.

P3 at most10 screened entries, retain2 mechanism families; P4 at most12 arms including6 references and necessary own-parent controls; P5 at most3 contenders plus6 references. At most1 integration entry, within the ten-entry portfolio. Each gate is applied at full-precision means. Deterministic tie order is cost tier then ID after registered bound tie band .005. No new candidate/model/threshold after selection/confirmation results. Model/fit revisions consume their original finite budget and finish before corresponding phase freeze.

## Variance-only fixed sample size

Before any E generation, select candidate using P5 rules, freeze code/assets, then use **D/P5 variances** against all 6 references:

    sigma_j = max(.30, 1.10 * sd_D,j)
    n_j = smallest integer n>=2 satisfying
      nct.sf(t.ppf(1-.01/12,n-1), n-1,
             .05*sqrt(n)/sigma_j) >= 1-.10/6
    n_E = ceil(1.10 * max_j n_j).

The calculation uses positive upper rejection tail, conservatively not crediting negative-tail rejection as successful superiority. Per-contrast target98.333333% assumed power gives joint>=90% by union bound if every true contrast>=+.05 and the IID normal approximation/SD planning assumptions hold. Floors/inflation are heuristics, not certified variance upper bounds. Same n applies to all6comparisons, seven policies and six families. Use no E mean/variance in sizing.

Analytical critic calculations with sigma .30/.35 give inflated n1107/1504; sigma .26 gives833 but the adopted floor.30 makes .26 unavailable as actual sizing. Exact noncentral-t computation and rounding must be independently repeated later and recorded before E. These are analytic planning calculations, not empirical test results.

n<=1800 and complete CPU/disk forecast must fit. Otherwise do not launch a study advertised with this power. Pre-E reviewed amendment may specify a fixed lower-powered study with honest limitations; never extend to significance. N/R may have large paired variance but much larger actual mean gaps: using+.05 for every reference is conservative and can block E. Retain that rule rather than rescue it with outcome-driven assumptions. Comparator-specific alternative effects would require a frozen rationale/amendment before D, not estimated E gaps.

For a certificate L>.025 with truth+.05 the separation is .025 and sample requirement is roughly four times larger; verify exact sizing and cap before making that claim. For truth+.075 against+.025, separation is .05 and ordinary sizing applies. None of these true effects is established by planning.

## Family/service diagnostics and limits

Report six family means and intervals, coverage, first-introduction waiting/unserved, assignment count, mutual first responses, date<=30, qualified MSMI, missing/late feedback, clarification costs and inference/fallback. Baseline G remains the family safety reference. P3/P4/P5 family/coverage thresholds are operational selection filters, not powered noninferiority tests.

Default confirmation family analysis is descriptive: six point differences plus simultaneous six-family99% intervals vs G can be reported but do not automatically support safety. If every-family noninferiority is required, register all family lower bounds>-.05 before E and size for that conjunction separately. To keep one round-wide .01 familywise guarantee, open this optional NI family only after all six primary panel nulls reject (serial gatekeeping), or freeze an explicit alpha split before execution; two unrelated .01 families give only separate guarantees; true0 vs margin-.05 and family SD.50 already needs2161 clusters for90% per-family power, more than E cap. Joint-family power requires still more. Do not assert 'no harm' because no subgroup p-value is significant. A balanced win can coexist with negative family effects.

The canceled opposite cold_start/delayed means in R6 are no causal mediation result. Hard answers are immediate. Controlled public-model/host audit interventions must distinguish downstream delay, qualification, occupancy, day-keyed outcomes and shifted random draws. A redesigned RNG creates a new diagnostic/benchmark; all panel methods must share it and its results stay separate from the official endpoint.

## Sensitivities and independent reconstruction

Prespecify seed-cluster bootstrap10000replicates, analysis RNG salt/seed 907007, resampling full seeds jointly across families and policy panel. Report paired95/99% percentile intervals as sensitivity, leaving simultaneous t intervals primary. Chunk bootstrap arrays to bounded memory. Report leave-one-seed-out min/max mean, largest absolute seed contributions and family decomposition without changing weights or dropping outliers.

A sign-flip/permutation test is not automatically exact: policy labels were not randomly assigned and symmetry is an extra assumption. AUC/Brier/log-loss model intervals use whole worlds/pools, not row-wise independence. Deterministic historical propensity=None cannot justify unbiased IPS/DR for unchosen matching actions. New behavior logging does not automatically solve sequential support/occupancy confounding; complete-policy rollouts remain primary.

Independent code reconstructs Q/A from full public released outcomes, validates all cell/cluster identities and source hashes, then rebuilds D/means/SD/intervals without importing director analysis helpers. Counts/action digests must agree exactly; floating means/interval endpoints within1e-10 given the same libraries or documented higher-precision reference. If disagreement exceeds tolerance, block final scientific seal and preserve both outputs.

## Sealing and interruptions

During E, candidate developers/director health displays see scheduling/log/error/resource information only. No pooled or machine-level means/CIs/pvalues until exact grid closure and operational review. First durable committed result is authoritative, including invalidity. Infrastructure retries retain original cell/config/seed and every failed attempt; no best-result selection. A committed policy invalidity disqualifies the version. A resource stop creates an incomplete study, not permission to analyze a smaller significant subset.

Merge raw cell rows and reconstruct global seed clusters once. Do not average machine means, combine local p-values, or count repeated portability replays as independent worlds. Null/negative results and failed candidates remain in the final archive.
