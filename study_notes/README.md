# The Sequential Reciprocal Matching Problem Under Changing Conditions
## Comprehensive Monograph, Reference Systems, and Curricular Study Notes

**Authoritative Technical Reference Hub**  
**Curriculum Spine:** [[Knowledge_Map|Master Knowledge Map]] · [[defense/question_bank|Oral Exam Question Bank (150 Questions)]]  
**Repository Base Path:** `/Volumes/1700 APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The Sequential Matching Problem`  
**Primary Engine:** [final_report/REPORT.md](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/final_report/REPORT.md) | **Executable Entrypoint:** [`policy.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/policy.py)

---

## 1. Monograph Overview

This monograph provides an exhaustive, mathematically rigorous, and forensically audited reference system for the **Sequential Reciprocal Matching Problem**.

The environment presents a non-stationary, two-sided sequential decision problem over a finite horizon:
1. **The Clarification Phase**: At each decision day $t \in [0, 59]$, an autonomous agent invests a scarce daily budget ($B=12$) to uncover latent hard compatibility constraints (cost 3) or soft preferences (cost 1).
2. **The Allocation Phase**: The agent proposes a disjoint batch of mutually feasible introductions from currently available members.
3. **The Multi-Stage Outcome Funnel**: Introductions progress through a realistic funnel: mutual initial acceptance $\to$ date occurrence ($p_{\text{happen}}=0.78, d-t \le 30$) $\to$ mutual second-meeting intention ($y_a=y_b=\text{yes}$) $\to$ prompt feedback reporting ($\tau-d \le 3$, timeliness factor $0.36$).

```mermaid
flowchart LR
    A["Arrived Pool (N = 200)"] -->|"Daily Budget = 12"| B["Clarification (Asks)"]
    B -->|"Hard Checks (Cost 3)"| C["Feasible Graph (<0.3% dense)"]
    C -->|"Maximal Matching"| D["Disjoint Introductions"]
    D -->|"Funnel Attrition"| E["Qualified MSMI Pairs (Q = 1)"]
```

### The Core Architectural Insight
Across nine research phases spanning over 10,000 simulated episodes, three massive confirmatory evaluations, and an audited learned campaign screen, the central empirical discovery is that **feasibility graph sparsity (<0.3% density) dominates algorithmic sophistication**.
- Complex parametric probability models, Edmonds' blossom matching, deliberate continuation waiting, and adaptive drift controllers consistently fail to outperform the **Supplied Baseline Greedy Policy ($G$)**.
- The supplied baseline—which executes list-order FIFO hard-bundle asking and soft-agreement greedy first-fit matching—remains the **provably robust, lowest-variance, production-grade standard**.

---

## 2. Five-Tier Curricular Reading Guide

To accommodate diverse review roles, the monograph is organized into five structured reading tracks:

```mermaid
graph TD
    T1["Track 1: Executive Briefing (15 min)"] --> T2["Track 2: Systems Architect & Engineer (45 min)"]
    T2 --> T3["Track 3: ML & Decision Theorist (90 min)"]
    T3 --> T4["Track 4: Empirical Auditor & Statistician (120 min)"]
    T4 --> T5["Track 5: Comprehensive Mastery (Monograph Complete)"]

    style T1 fill:#202e42,stroke:#333,stroke-width:1px,color:#fff
    style T2 fill:#007f78,stroke:#333,stroke-width:1px,color:#fff
    style T3 fill:#b77c37,stroke:#333,stroke-width:1px,color:#fff
    style T4 fill:#9d5367,stroke:#333,stroke-width:1px,color:#fff
    style T5 fill:#6572a7,stroke:#333,stroke-width:1px,color:#fff
```

### Track 1: Executive Briefing (15 Minutes)
*Goal: Understand the core tournament challenge, the empirical findings, and why Greedy was retained.*
1. Read the [Executive Quick Reference](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reference/quick_reference.md).
2. Review [Figure 1 (Confirmation Context)](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/01_confirmation_context.png) and [Figure 11 (Learned Screen)](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/11_closed_learned_screen.png).
3. Read the Executive Summary and Decision in [`final_report/REPORT.md:§1, §12`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/final_report/REPORT.md).

### Track 2: Systems Architect & Engineer (45 Minutes)
*Goal: Master runtime constraints, container limits, data contracts, and algorithmic invariances.*
1. Read the [Authoritative Data Contract](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/docs/DATA_CONTRACT.md) and [Policy Interface Specification](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/docs/POLICY_INTERFACE.md).
2. Inspect the [Policy Aliases and Lineage Registry](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reference/policy_aliases_and_lineage.md) for mechanism breakdowns.
3. Review the [Repository Source Map](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reference/source_map.md) to inspect [`policy.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/policy.py) and [`kit.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/kit.py).
4. Verify FIFO Clarification Invariance and Action Digest Invariance theorems.

### Track 3: Machine Learning & Decision Theorist (90 Minutes)
*Goal: Understand outcome modeling, funnel attrition, directional calibration, and non-stationary drift.*
1. Study [Glossary and Notation](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reference/glossary_and_notation.md) for terminal decomposition formulas.
2. Inspect [Figure 6 (Calibration)](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/06_calibration.png), [Figure 7 (Drift Calibration)](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/07_drift_calibration.png), and [Figure 10 (Outcome Funnel)](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/10_outcome_funnel.png).
3. Read [`final_report/REPORT.md:§6–8`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/final_report/REPORT.md) on hybrid empirical priors and directional shrinkage.
4. Review the [Coverage Matrix](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reference/coverage_matrix.md) across Sections II, IV, and V.

### Track 4: Empirical Auditor & Statistician (120 Minutes)
*Goal: Forensic verification of seed-cluster inference, multiplicity control, and research closure.*
1. Read the [Research and Evidence Ledger](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reference/research_and_evidence_ledger.md).
2. Examine the [Coverage Review](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reviews/coverage_review.md) and [Pedagogical Review](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reviews/pedagogical_review.md).
3. Audit the Independent Observation Fallacy and verify how 192 row degrees of freedom were properly corrected to 12 seed clusters ($t_{11}$).
4. Inspect [Figure 2 (Robustness Contrasts)](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/02_robustness_contrasts.png) and [Figure 3 (Condition Heatmap)](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/03_condition_heatmap.png).
5. Run the figure reproduction harness via [`study_notes/scripts/reproduce_figures.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/scripts/reproduce_figures.py).

### Track 5: Comprehensive Mastery
Complete sequential study of the entire repository, reference systems, master flashcards, and technical report.

---

## 3. The Visual Atlas: Complete Index of Report Figures

All 12 publication figures are preserved in both lossless PNG and vector SVG formats in [`study_notes/assets/`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/).

| Fig # | Figure Title & Formats | Methodological Role & Conceptual Scope | Key Quantitative Finding | Primary Data Source |
|---|---|---|---|---|
| **01** | **Confirmation Context**<br>[PNG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/01_confirmation_context.png) \| [SVG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/01_confirmation_context.svg) | Displays effect estimates and confidence intervals from both pre-registered confirmatory trials (Round 1 and Research 6 Stage E). | • Round 1 `simple_fifo`: $-0.0417$ MSMI/100 (95% CI [$-0.0911, +0.0077$], $p=0.096$).<br>• Research 6 `Q6`: $+0.0032$ MSMI/100 (99% CI [$-0.0245, +0.0309$], $p=0.765$). Both failed confirmation. | [`historical_confirmation.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/historical_confirmation.json) |
| **02** | **Robustness Contrasts**<br>[PNG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/02_robustness_contrasts.png) \| [SVG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/02_robustness_contrasts.svg) | Paired differences $\Delta(\text{Arm} - G)$ on the Q1 robustness grid (12 seeds $\times$ 16 laws) with honest seed-cluster 95% CIs and Holm-adjusted $p$-values. | $G_{\text{arr}}$ achieves $+0.0990$ point estimate, but its cluster 95% CI spans zero ([$-0.0701, +0.2680$], Holm $p=0.8965$). No arm statistically outperforms $G$. | [`study_analysis.json:q1`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/study_analysis.json) |
| **03** | **Condition Heatmap**<br>[PNG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/03_condition_heatmap.png) \| [SVG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/03_condition_heatmap.svg) | Per-law mean performance differences across 16 environmental laws alongside baseline Greedy outcome levels. | Illustrates stability of $G$ across arrival shocks, weight shifts, and response decays; shows where $G_{\text{arr}}$ concentrates gains (early arrival shocks). | [`study_analysis.json:q1`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/study_analysis.json) |
| **04** | **Prior Sensitivity**<br>[PNG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/04_prior_sensitivity.png) \| [SVG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/04_prior_sensitivity.svg) | Realized MSMI/100 outcomes versus host-only conditional expectations on the Q2 prior grid (sim, emp, flat). | Empirical priors suffer from snapshot date censoring ($0.4762$ vs $0.78$); all prior configurations underperform $G$ in point estimates. | [`study_analysis.json:q2`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/study_analysis.json) |
| **05** | **Adaptive Ablations**<br>[PNG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/05_adaptive_ablations.png) \| [SVG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/05_adaptive_ablations.svg) | Policy contrasts on Q3 drift comparing $X1_{\text{emp}}$, $X1_{\text{sim}}$, $X1_{\text{nocal\_emp}}$, $X1_{\text{nolearn\_emp}}$, and $X1_{\text{oracle}}$ against $G$. | $X1_{\text{emp}}$ and $X1_{\text{nocal\_emp}}$ produce **identical action digests** across all 72 episodes; $X1_{\text{oracle}}$ trails $G$ ($0.4583$ vs $0.5833$). | [`study_analysis.json:q3`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/study_analysis.json) |
| **06** | **Calibration Reliability**<br>[PNG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/06_calibration.png) \| [SVG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/06_calibration.svg) | Reliability curves and Brier decomposition evaluated on 5,009 identical candidate edges selected by $G$. | Demonstrates why raw Brier scores appear deceptively good (~0.038) due to rare events ($\bar{y} \approx 0.035$); empirical prior shows severe underprediction. | [`calibration.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/calibration.json), [`reliability_bins.csv`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/reliability_bins.csv) |
| **07** | **Drift Calibration**<br>[PNG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/07_drift_calibration.png) \| [SVG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/07_drift_calibration.svg) | Directional prediction bias and applied shrinkage offsets pre- and post-day 35 drift. | Pre-drift predictions are well-centered ($\text{bias} \approx +0.01$); post-drift exhibits severe signed bias ($-0.17$), but shrinkage dampens erratic updates. | [`study_analysis.json:q3`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/study_analysis.json) |
| **08** | **Waiting and Coverage**<br>[PNG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/08_waiting_and_coverage.png) \| [SVG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/08_waiting_and_coverage.svg) | Served-only cumulative waiting distributions shown side-by-side with unserved population proportions. | ~64.5% of arrived members remain unserved under $G$. Among served members, mean wait is 8.4 days; 80% receive intros within 15 days. | [`waiting.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/waiting.json) |
| **09** | **Access Subgroups**<br>[PNG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/09_access_subgroups.png) \| [SVG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/09_access_subgroups.svg) | Descriptive breakdown of unserved rates across profile completeness, gender identities, and age cohorts under $G$. | Declining hard fields guarantees 100% unserved rate. Across complete profiles, unserved rates are consistent (men 64.7%, women 64.5%, non-binary 63.1%). | [`subgroups_q1_greedy.csv`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/subgroups_q1_greedy.csv) |
| **10** | **Outcome Funnel**<br>[PNG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/10_outcome_funnel.png) \| [SVG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/10_outcome_funnel.svg) | Funnel progression (Introductions $\to$ Mutual Acceptance $\to$ Date $\to$ Qualified MSMI) on logarithmic axis across Q1 arms. | Massive attrition: 80.8 assignments per episode yield only 0.91 qualified pairs (~1.1% conversion efficiency). | [`study_analysis.json:q1`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/study_analysis.json) |
| **11** | **Closed Learned Screen**<br>[PNG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/11_closed_learned_screen.png) \| [SVG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/11_closed_learned_screen.svg) | Audited selection screen across 288 cells on 8 reused development seed groups testing learned model rankers against $G$. | All model candidates failed the admission gate ($0.1875 - 0.2188$ vs $G=0.3229$). The 96 confirmation seed groups remained unopened. | [`closed_screen_summary.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/closed_screen_summary.json) |
| **12** | **Supplied Baselines Historical**<br>[PNG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/12_supplied_baselines_historical.png) \| [SVG](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/12_supplied_baselines_historical.svg) | Historical matched evaluation of supplied baseline controls (`greedy`, `no_asks`, `random`) on seeds 301–305 ($N=30$ eps). | Clarification is mandatory (`no_asks` collapses to $0.0500$ MSMI); soft scoring provides meaningful structure over random feasible matching ($0.3500$ vs $0.3167$). | [`historical_baselines.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/historical_baselines.json) |

---

## 4. Master Reference System Directory

The reference system is organized into modular, purpose-built reference manuals:

- [Glossary and Notation Guide](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reference/glossary_and_notation.md): Complete mathematical symbols, metric formulas, contract schemas, and domain terminology.
- [Policy Aliases and Lineage Registry](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reference/policy_aliases_and_lineage.md): Exhaustive taxonomy mapping every policy arm, asking rule, scoring rule, allocation algorithm, and statistical verdict.
- [Repository Source Map](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reference/source_map.md): Deep architectural inventory of all root scripts, documentation, datasets, and research phase directories.
- [Research and Evidence Ledger](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reference/research_and_evidence_ledger.md): Cryptographically audited ledger tracking all formal empirical claims, inferential units, confidence intervals, and corrections.
- [Curricular Coverage Matrix](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reference/coverage_matrix.md): Systematic cross-reference mapping phases, methods, and report chapters across the 8 examination syllabus domains.
- [Master Flashcard Deck](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reference/flashcards.md): High-yield spaced-repetition Q&A deck spanning 8 thematic domains for oral defense and exam preparation.
- [Executive Quick Reference Sheet](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reference/quick_reference.md): High-density one-page cheat sheet of core numbers, formulas, theorems, and defense warnings.
- [Pedagogical Review](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reviews/pedagogical_review.md): Pedagogical audit evaluating instructional design, conceptual scaffolding, and pitfall warnings.
- [Independent Coverage Audit](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reviews/coverage_review.md): Independent audit verifying research closure, evidence tracing, and statistical honesty.

---

## 5. Oral Defense and Cross-Examination Preparation

When defending this monograph before an independent review committee or tournament jury, anticipate the following critical inquiries:

### Question 1: "Why did you abandon $G_{\text{arr}}$ if its point estimate showed a +0.0990 MSMI/100 gain over Greedy?"
* **Authoritative Defense**:
  "In the initial Round 2 draft, an analysis of 192 scenario rows claimed a spuriously tight confidence interval [$+0.040, +0.158$] with $p = 0.0009$. However, an independent statistical audit revealed that this committed the **Independent Observation Fallacy**: the 16 scenario variations evaluated on each random seed share identical member traits and baseline arrivals. When we correctly aggregate the paired contrasts to the independent **seed-cluster level** ($S=12$, Student-$t$ with 11 df), the 95% confidence interval widens to **[$-0.0701, +0.2680$]**, with a two-sided $p = 0.2241$ and a within-study Holm-adjusted $p = 0.8965$. Because the confidence interval encompasses zero and the evaluation grid was exploratory rather than pre-registered, promoting $G_{\text{arr}}$ would violate scientific integrity standards. It remains an exploratory research lead."

### Question 2: "Could earlier asking allow feedback to return before the day-60 deadline?"
* **Authoritative Defense**:
  "No. That hypothesis, though intuitive, represents the **Day-60 Feedback Cutoff Fallacy**. Under the official simulator contract, the environment implements an explicit 40-day post-decision follow-up horizon ($t \in [60, 99]$). While policy interventions (asks and introductions) freeze after day 59, the simulation continues running through day 99. Any introduction made on day 59 is granted its full 30-day date window and downstream 3-day feedback windows. Zero feedback events are truncated at day 60. Any advantage of arrival-ordered questioning stems from graph construction dynamics, not feedback latency truncation."

### Question 3: "Why did you refuse to unblind the 96 confirmation seed groups in the final learned campaign?"
* **Authoritative Defense**:
  "Under our pre-registered research governance protocol, the 96 confirmation groups were reserved strictly for candidates that successfully cleared the **selection screen admission gate**. In the 288-cell selection screen across 8 development groups, all three learned model candidates scored between $0.1875$ and $0.2188$ MSMI/100, significantly trailing the control Greedy baseline ($0.3229$). Furthermore, the learned funnel models failed the pre-registered calibrated-probability validation test. Executing the stop rule preserved the sanctity of the confirmatory data and prevented data snooping and post-hoc rationalization."

### Question 4: "Does baseline Greedy exhibit algorithmic bias against demographic subgroups?"
* **Authoritative Defense**:
  "Our access analysis indicates that descriptive unserved rates across broad gender identities (men 64.7%, women 64.5%, non-binary 63.1%) and age brackets (<30: 65.9%, 30–39: 63.3%, 40+: 64.4%) are remarkably balanced. However, we explicitly refrain from asserting that Greedy is 'provably fair'. A primary driver of non-service is profile missingness: members who decline hard constraint fields have a 100% unserved rate due to reciprocal feasibility requirements. Even among complete profiles, ~58% remain unserved purely due to graph degree sparsity. We caution against conflating observational parity with causal equity."
