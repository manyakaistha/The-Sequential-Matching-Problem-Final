# Independent analysis-code review

Reviewed `final_report/build_assets.py`, generated `study_analysis.json`, `calibration.json`, `provenance.json`, the stored-row schema in `research9/round2/episode.py`, and relevant prediction/history definitions in `policies/model.py`. Read-only analysis scope; no simulation, fitting, old `analyze.py` imports, or evidence changes. Reviewer: independent implementation reviewer; report owner: root.

## Actionable finding

**Figure 06 silently clips Wilson upper bounds.** Its left axis is fixed at 0–4%, whereas terminal calibration bins have Wilson upper bounds 32.44% (sim, n=8), 6.58%, 4.97%, 5.52%, and 5.50%. The plot visually conceals substantial uncertainty. Expand the range, use an explicitly labeled zoom/inset, or visibly annotate truncated intervals and disclose the sparse bin. Sent to root before review completion. This finding does not change the numerical calibration JSON or policy conclusions.

## Statistical checks passed

- Each study computes arm-minus-G paired differences within each seed, averages laws equally within seed, then uses the 12 resulting seed clusters for Student-t standard errors, 95% intervals, and two-sided p-values. Laws and introductions are not incorrectly counted as independent replications in these contrasts.
- Independently recomputed Q1 `G_arr − G` from raw saved JSON with NumPy/SciPy: differences `[0.09375, 0.25, -0.09375, 0.6875, -0.34375, 0.0625, 0.15625, 0.125, -0.0625, 0.34375, -0.1875, 0.15625]`; mean `0.0989583333`, SE `0.0768199072`, 95% CI `[-0.0701211423, 0.2680378090]`, p `0.2241187108`. These match generated values.
- Holm implementation is the genuine step-down cumulative maximum of `(m-rank)*p`, capped at one. Main arm-vs-G comparisons are corrected separately within each study; Q2 direct comparisons and Q3 direct comparisons each form additional separate families. Per-law comparisons are explicitly unadjusted. Report prose should preserve these family boundaries rather than imply one global correction.
- Repeated cells are checked for matching world/action/asking digests and metric signatures, and studies are analyzed separately. Provenance distinguishes 2,076 recorded episodes from 1,968 unique seed/law/arm cells, with 12 seed identifiers. There is no pooled inferential sample count that treats repeats as fresh observations.

## Calibration, denominators, and interpretation

- Introduction schema indices match the code: mutual/date/MSMI are indices 6/7/8; own/sim-shadow/emp-shadow predictions are 11/12/13. Prediction stages are unconditional introduction-level probabilities, so denominators align with the binary outcomes.
- Q2 sim/emp reliability uses exactly G-selected introductions for both priors (5,009 introductions, 62 qualified outcomes). This avoids comparing calibration across policy-selected edge populations. Q3 calibration uses each arm's own selections and should remain descriptive across arms.
- Signed error is prediction minus observation: negative values mean underprediction. Brier, zero-prediction baseline, descriptive same-sample prevalence baseline, and binned ECE are calculated with correct introduction denominators. Seed-mean signed-error intervals give seeds equal weight; pooled signed error gives introductions equal weight. These are distinct summaries, not interchangeable estimates.
- Wilson bin intervals ignore seed dependence, and the figure subtitle explicitly says so. Sparse-bin reliability and ECE should not be treated as precise validation or model selection evidence.
- Primary MSMI figures count qualified pair outcomes per 100 arrived members (200 per episode), not unique successful people. Waiting uses first introduction only, and served-only waiting distributions are accompanied by unserved proportions. Subgroups are overlapping observational groups, correctly labeled as member-episodes rather than independent participants.
- Drift split is by assignment day before/after day 35, with outcomes after follow-up; offset history index 5 is the actual recorded applied logit offset.

## Validation limits and presentation

Stored row/aggregate checks are useful but do not independently reconstruct outcomes from public event ledgers, prove deadline compliance, attest source-at-run, or certify seed freshness. Provenance explicitly limits its claims to stored-row consistency; preserve that wording in the report. Grid completeness, validity flags, aggregate counts, same-world hashes, same-asking hashes, and repeated-cell signatures are checked rather than assumed.

Figure units consistently distinguish percentage-point calibration from MSMI events per 100 arrived. Funnel uses a labeled log axis and a common arrival denominator. Historical confirmation figure explicitly distinguishes reported 95% and 99% intervals and warns against pooling cohorts. Three-decimal exploratory effects/p-values are appropriate at this precision; avoid interpreting near-zero floating residue as a substantive difference. Final regeneration should occur after any code fix so provenance hashes match the delivered assets and code.

Status: statistical calculations pass the bounded review; figure 06 uncertainty display needs correction or explicit truncation disclosure before delivery.

## Follow-up disposition after corrections and additions

The uncertainty-display finding is **resolved** in the regenerated `06_calibration.png`. The plot explicitly restricts display to bins with n≥50, discloses omission of eight sim predictions out of 5,009, and retains every bin and aggregate in JSON/CSV. The 5,001 plotted sim rows have maximum Wilson upper bound 6.5832%; all 5,009 emp rows have maximum upper bound 5.5168%, both visible on the new 0–7% axis. Inspected the regenerated image. This display filter changes neither calibration metrics nor scientific evidence.

Reviewed historical additions: `results/research/holdout.json` contains the same 30 distinct seed/family cells for each supplied arm, seeds 301–305 and six families, all with 200 arrived members. Independently checked qualified totals/rates: Greedy 21/0.3500, no-asks 3/0.0500, random 19/0.3166667. Extraction preserves separate historical scope, arithmetic means and coverage denominators. Figure 12/report label this as separate historical context and make no fresh inferential claim. Figure 01 now reads machine-readable Round 1 and Research 6 confirmation statistics instead of rounded literals; policy/cohort/confidence-level distinctions are retained. Current provenance input hashes match these three added historical sources and `build_assets.py`.

The report correctly states separate Holm families and the limits of stored-row validation. Sent one minor wording correction to root: replace abstract “corrected 95% interval” with “seed-cluster 95% interval” to avoid implying multiplicity-adjusted confidence bounds. With that wording clarified, no remaining blocking implementation finding was identified in this bounded follow-up. No simulations or fitting were performed.
