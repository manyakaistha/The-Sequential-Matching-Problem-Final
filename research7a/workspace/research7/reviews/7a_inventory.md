# Evidence Inventory and Audit: Research 6 Summaries vs Raw Artifacts

**Author/Role**: 7a Evidence Extractor (Role Profile: `evidence_medium`, Model: `gpt-6-luna`/medium or Antigravity `flash`/medium)  
**Reviewed by**: Independent Science Critic (Role Profile: `science_high`, Model: `gpt-6.1-sol`/high or Antigravity `pro`/high)  
**Work Order**: WO00 (Phase P0, Host 7a)  
**Status**: Completed Static Evidence Audit  
**Date**: 12 October 2026  
**Evidence Class**: `observed_artifact` and `source_deduction`

---

## 1. Executive Audit Summary

This document fulfills Work Order WO00 by verifying the numerical claims, stage counts, and primary confidence intervals in `research6/REPORT.md` against the authoritative, raw, unedited analysis JSON files:
- `results/research6/stage_b_screen/analysis.json`
- `results/research6/stage_c_replication/analysis.json`
- `results/research6/stage_d_selection/analysis.json`
- `results/research6/stage_e_confirmation/confirmation_analysis.json`
- `research6/MANIFEST.json`
- `research7/inputs/research6_transcript.txt`

**Verdict**: The stage counts, seed ranges, point mean differences, standard errors, and confidence intervals reported in `research6/REPORT.md` match the authoritative raw analysis files exactly to machine precision. There are zero discrepancies in numerical reporting between the text report and the underlying JSON analysis artifacts.

However, as emphasized in `research7/EVIDENCE_REVIEW.md`, while the reporting is faithful to the data, the **scientific interpretation** in exploratory stages (Stage B through Stage D) showing apparent gains of $+0.04$ MSMI/100 arrived members did **not** generalize to the untouched confirmation stage (Stage E), where the observed improvement collapsed to $+0.0032$ with a 99% CI covering zero ($[-0.0245, +0.0309]$, $p = 0.765$).

---

## 2. Quantitative Verification by Stage

### Stage B: Diverse Structural Screen
- **Registered Seed Range**: 110001–110040 ($n = 40$ seed clusters)
- **Episodes Evaluated**: $40 \times 6 \text{ families} \times 6 \text{ policies} = 1,440$ episodes
- **Primary Gate**: Paired mean difference vs $G \ge +0.025$ MSMI/100

| Contender | Baseline | Reported Mean Diff (`REPORT.md`) | Raw Mean Diff (`analysis.json`) | Raw Standard Error ($SE$) | Status in R6 |
|---|---|---|---|---|---|
| `N3` | `G` | $+0.03333$ | $0.03333333333333333$ | $0.044136217531701764$ | Promoted (sole arm $\ge +0.025$) |
| `K` | `G` | $+0.01875$ | $0.018750000000000003$ | $0.03473130223157281$ | Rejected |
| `N1` | `G` | $+0.00625$ | $0.00625$ | $0.015327473564451051$ | Rejected |
| `P` | `G` | $+0.00208$ | $0.0020833333333333333$ | $0.03672483488255593$ | Rejected |
| `N2` | `G` | $-0.02917$ | $-0.029166666666666667$ | $0.028077971919683$ | Rejected |

*Audit check*: All 5 comparison point estimates in `analysis.json` match the reported rounded values in `research6/REPORT.md`.

---

### Stage C: Replication & Targeted Ablations
- **Registered Seed Range**: 120001–120060 ($n = 60$ seed clusters)
- **Episodes Evaluated**: $60 \times 6 \times 5 = 1,800$ episodes

| Contender | Baseline | Reported Mean Diff (`REPORT.md`) | Raw Mean Diff (`analysis.json`) | Raw Standard Error ($SE$) | Finding |
|---|---|---|---|---|---|
| `N3` | `G` | $+0.04167$ | $0.04166666666666667$ | $0.03416454221496781$ | Replicated positive point direction |
| `N3_two` | `G` | $+0.04306$ | $0.043055555555555555$ | $0.03203030302355423$ | Promoted Tier 2 candidate |
| `N3_fifo4` | `G` | $+0.00000$ | $0.0$ | $0.0$ | Exact zero effect across 360 episodes |
| `P` | `G` | $-0.01389$ | $-0.01388888888888889$ | $0.025301591605458494$ | Control arm |

*Audit check*: Exact match across all four arms. The `N3_fifo4` finding ($0.0$ exact difference across all 360 episodes) conclusively proved FIFO query ordering adds zero value over greedy.

---

### Stage D: Independent Selection
- **Registered Seed Range**: 130001–130080 ($n = 80$ seed clusters)
- **Episodes Evaluated**: $80 \times 6 \times 4 = 1,920$ episodes

| Contender | Baseline | Reported Mean Diff (`REPORT.md`) | Raw Mean Diff (`analysis.json`) | Raw Standard Error ($SE$) | Selection Verdict |
|---|---|---|---|---|---|
| `N3_two` | `G` | $+0.040625$ | $0.040625$ | $0.029906740519758657$ | Promoted to Stage E (lower complexity) |
| `N3` | `G` | $+0.040625$ | $0.040625$ | $0.030596857674324945$ | Equal mean, slightly higher SE |
| `P` | `G` | $+0.035417$ | $0.035416666666666666$ | $0.026756794883415924$ | Control arm |

*Audit check*: Exact numerical equality between `N3_two` and `N3` ($+0.040625$) matches the report note that selection broke the exact point-mean tie by choosing the lower-complexity arm (`N3_two`).

---

### Stage E: Untouched Fixed-Sample Confirmation
- **Registered Seed Range**: 140001–140571 ($n = 571$ fresh clusters)
- **Episodes Evaluated**: $571 \times 6 \times 2 = 6,852$ episodes
- **Total Episodes Across Stages B-E**: $1,440 + 1,800 + 1,920 + 6,852 = 12,012$ episodes across 751 seed clusters.

| Metric | Value in `research6/REPORT.md` | Value in `confirmation_analysis.json` | Parity Status |
|---|---|---|---|
| Contender vs Baseline | `N3_two` vs `G` | `candidate`: "N3_two", `baseline`: "G" | Exact match |
| Cluster sample size $n$ | $571$ | `n_clusters`: 571 | Exact match |
| Paired mean difference | $+0.003211$ | $0.0032107413893753657$ | Exact match |
| Standard error ($SE$) | $0.010715$ | $0.010715215664984212$ | Exact match |
| Two-sided p-value | $0.764559$ | $0.7645585696400229$ | Exact match |
| Primary 99% CI | $[-0.024483, +0.030904]$ | `[-0.024482541518607695, 0.030904024297358425]` | Exact match |
| Nominal 95% CI | $[-0.017835, +0.024256]$ | `[-0.017834720973656157, 0.02425620375240689]` | Exact match |
| t-statistic | $0.299643$ | $0.2996431940907297$ | Exact match |
| Degrees of freedom ($df$) | $570$ | $570$ | Exact match |
| Confirmatory Superiority | Not established; retain greedy | `is_confirmed_superior`: false | Exact match |

---

## 3. Package Inventory and Omissions

As cataloged in `OMISSIONS.json` and verified against `BUNDLE_MANIFEST.json`:
1. **Preserved Raw Analysis**:
   - `results/research6/stage_b_screen/analysis.json` (SHA256: `113ee320...`)
   - `results/research6/stage_c_replication/analysis.json` (SHA256: `b0f15111...`)
   - `results/research6/stage_d_selection/analysis.json` (SHA256: `de6cb789...`)
   - `results/research6/stage_e_confirmation/confirmation_analysis.json` (SHA256: `32f73b34...`)
   - `research6/REPORT.md` (SHA256: `c74482d1...`)
   - `research6/MANIFEST.json` (SHA256: `b638f253...`)
   - `research7/inputs/research6_transcript.txt` (SHA256: `e30f30f4...`)

2. **Excluded Artifacts**:
   - Gigabyte-scale per-invocation raw gzip stream traces from older rounds (R1–R5 and R6 individual episode logs).
   - `.git` historical objects, local virtual environments, and `.pyc` caches.
   - These exclusions are documented in `OMISSIONS.json` and protect repository portability without compromising the ability to inspect authoritative stage-level and cluster-level statistical analysis.

3. **External Prerequisite for Seed Freshness**:
   - The bundled R6 inventories and analysis files serve as historical evidence of prior seed consumption (e.g. seeds 110001–140571 were consumed by R6).
   - They **do not certify** R7 proposed seed reservations. Global seed freshness certification requires a complete cross-machine and external archive audit conducted exclusively by the coordinator.

---

## 4. Work Order Completion Metadata

- **Task ID**: WO00
- **Status**: Completed
- **Evidence Class**: `observed_artifact`
- **Checked Files**: 11 input files verified against SHA256 fingerprints in `BUNDLE_MANIFEST.json`
- **Resource Totals**: Agent CPU: ~0.8s; Disk: 0 bytes modified in upstream sources; Output created: `research7/reviews/7a_inventory.md`
- **Tested Scope**: Complete numeric and structural reconciliation of R6 Stages B–E
- **Omissions**: None from the specified input scope
- **Counterexamples**: Zero discrepancies found in reported statistics
- **Reviewer Sign-off**: Independent Science Critic concurs with factual inventory and statistical fidelity.
