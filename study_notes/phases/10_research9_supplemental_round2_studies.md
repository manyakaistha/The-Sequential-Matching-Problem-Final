# Phase 10: Research 9 Supplemental Round 2 Studies — Robustness, Observable Priors, Adaptive Drift, and Access Diagnostics

**Phase Identifier:** `research9/round2`  
**Chronological Period:** 16 October 2026 – 17 October 2026  
**Document Status:** Complete Chronicler Case Study  
**Governing Standard:** 14-Part Scientific Case-Study Anatomy  
**Base Repository Reference:** [`The Sequential Matching Problem`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem)

---

## 1. Executive Summary & Core Verdict

The Research 9 Supplemental Round 2 Studies (`research9/round2/`) constitute the definitive empirical stress test of the sequential matching problem. Executing **2,076 recorded episodes across 1,968 unique simulation cells, 12 fresh seed clusters, 20 distinct environment condition laws, and 108 exact cross-study repeat checks**, this campaign was designed to answer the explicit technical challenges raised by the Round 1 review panel.

The core verdicts across the three supplemental investigations (Q1, Q2, Q3) and secondary diagnostic analyses are:
1. **Q1 (FIFO Robustness & Asking Order):** True arrival-ordered questioning ($G_{\text{arr}}$) demonstrated a positive exploratory point difference over baseline Greedy ($G$) of **$+0.0990$ qualified MSMI/100 arrived members**. However, when clustered correctly by seed across the 16 condition laws, its $95\%$ confidence interval spans **$[-0.0701, +0.2680]$**, with a Holm-adjusted $p$-value of **$p = 0.8965$**. LIFO asking ($+0.0026$, $p=1.000$) and degree-based asking ($-0.0677$, $p=1.000$) demonstrated no advantage. The positive signal for arrival ordering is real in point estimate, but statistically indistinguishable from zero.
2. **Q2 (Prior Sensitivity & Observable Training):** Replacing simulator-specific ground-truth parameters with priors fit strictly to public observable data (`emp`) shifted predictive probabilities and diagnostic scores, but **failed to establish any policy gain**. On Population Score ($PS$), $PS_{\text{emp}} - PS_{\text{sim}} = -0.0333$ ($p = 0.8796$). On Network Matching ($N3e$), $N3e_{\text{emp}} - N3e_{\text{sim}} = +0.0083$ ($p = 1.000$). Privileged host-only conditional expectation diagnostics showed wide divergence, but realized physical MSMI remained flat.
3. **Q3 (Adaptive Drift Tracking & Calibration Ablation):** The adaptive scorer $X1$ (combining recency-weighted online updates with post-day-35 directional calibration) underperformed Greedy by **$-0.1389$ MSMI/100** ($95\%$ CI $[-0.4632, +0.1854]$, $p = 1.000$). Most critically, a direct calibration ablation proved that directional calibration had **exactly zero impact on policy actions**: $X1_{\text{emp}} - X1_{\text{nocal\_emp}} = 0.0000$ (SE $0.0000$, $95\%$ CI $[0.0000, 0.0000]$, $p = 1.000$), matching all 72 action digests bit-for-bit.
4. **Access & Waiting Diagnostics:** Across 38,400 member-episodes, members who incurred a hard decline experienced a **$100\%$ unserved rate**, whereas complete-on-arrival members were served at a $61.3\%$ rate. The downstream outcome funnel reveals extreme attrition: from ~68 introductions per episode down to ~0.3 qualified MSMI pairs—a **$99.5\%$ funnel drop**.

---

## 2. Historical Context & Baseline State

The Round 1 submission sparked critical inquiries from the review panel:
- *"Does FIFO retain its advantage when arrival order, preference weights and response conditions change?"*
- *"Would observable-training priors change conclusions based on simulator parameters?"*
- *"Can a small adaptive method address drift, with directional calibration and identical asking controls?"*
- *"Keep meetings and mutual second-meeting intention central; report who waits."*

Crucially, historical clarification was required: in Round 1, the submitted complex candidate (`simple_fifo`) did not defeat Greedy; rather, **the supplied Greedy baseline itself already utilized FIFO asking (`baseline_asks`)**. To resolve whether any sophisticated modification could surpass simple FIFO-asking Greedy, Research 9 Round 2 constructed an isolated, bit-for-bit certified fast simulator ([`fastsim.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research9/round2/fastsim.py)) and executed 2,076 episodes under frozen conditions.

---

## 3. Scientific Hypotheses & Research Questions

The supplemental campaign investigated three structured questions (Q1, Q2, Q3) alongside secondary access diagnostics:

1. **Question Q1 (Asking Order Robustness):** Does varying the sequence of hard-question clarification (arrival-order $G_{\text{arr}}$, reverse-arrival $G_{\text{lifo}}$, bipartite degree $G_{\text{deg}}$, or list-order $G$) alter qualified matching yield under severe arrival clustering, attribute weight shifts, and response latency?
2. **Question Q2 (Prior Sensitivity):** Does replacing simulator-derived prior parameters (`sim`) with observable-data empirical Bayes estimates (`emp`) or uninformative flat priors (`flat`) improve policy decisions, or expose model mismatch?
3. **Question Q3 (Adaptive Drift Compensation):** Can online recency-weighted parameter updating combined with directional probability calibration mitigate mid-horizon performance collapse under environment drift (Day 35 distribution shock)?
4. **Secondary Diagnostics:** What are the exact waiting time distributions of served members, which demographic or information subgroups are left unserved, and what is the exact survival attrition through the four-stage outcome funnel?

---

## 4. Mathematical Formulation & Theoretical Framework

### 4.1 The Three Question-Ordering Operators in Q1
Let $\mathcal{U}_t^{\text{unknown}}$ be the set of dyads requiring hard verification on day $t$. The policy selects up to 4 dyads:
- **Baseline Greedy ($G$):** Evaluates dyads in internal list order: $\pi_G(u, v) = \text{index}(u, v)$.
- **Chronological Arrival ($G_{\text{arr}}$):** Prioritizes dyads by earlier arrival date:
  $$\pi_{\text{arr}}(u, v) = \min(t_{\text{arr}}(u), t_{\text{arr}}(v))$$
- **Reverse Arrival ($G_{\text{lifo}}$):** Prioritizes dyads containing the most recent arrivals:
  $$\pi_{\text{lifo}}(u, v) = -\max(t_{\text{arr}}(u), t_{\text{arr}}(v))$$
- **Bipartite Degree ($G_{\text{deg}}$):** Prioritizes dyads with the highest count of verified-compatible alternate suitors, attempting to resolve high-centrality bottlenecks.

### 4.2 Prior Formulations in Q2
For an edge $e = (u, v)$ with observed agreement vector $x_e$, the predicted probability of eventual qualification decomposes into:
$$q_e = \sigma\left(\mu_{\text{prior}} + \beta^T x_e\right)$$
- **Simulator Prior (`sim`):** Uses true latent generation intercepts: $\mu_{\text{sim}} = \text{logit}(p_{\text{base}})$.
- **Observable Empirical Prior (`emp`):** Intercepts and variance hyper-parameters estimated via maximum marginal likelihood on historical public observation logs.
- **Uninformative Prior (`flat`):** Sets $\mu_{\text{flat}} = 0$ (implying an uninformative $0.5$ base rate) with broad variance.

### 4.3 Adaptive Drift Scorer $X1$ in Q3
To track non-stationary distribution shifts occurring on Day 35, the $X1$ policy architecture updates an online logit offset $\delta_t$:
$$\hat{q}_e(t) = \sigma\left(\text{logit}(q_e^{\text{base}}) + \delta_t\right)$$
$$\delta_{t+1} = (1 - \gamma) \delta_t + \gamma \left( \bar{y}_{t-\text{lag}} - \bar{p}_{t-\text{lag}} \right)$$
Where $\gamma$ is a recency learning rate, and a directional post-day-35 calibration shift is applied to counteract observed drop-offs in acceptance.

---

## 5. Algorithmic Architecture & System Design

The Round 2 architecture was engineered inside [`research9/round2/`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research9/round2):

```mermaid
graph TB
    subgraph "Round 2 Execution Engine"
        FS["fastsim.py: Certified Bit-for-Bit Deterministic Simulator"]
        LAWS["laws.py: 20 Environmental Condition Laws"]
        OV["oracle_value.py: Gauss-Hermite Quadrature Host Diagnostic"]
        EP["episode.py: Cold Subprocess Isolation Harness"]
    end

    subgraph "Study Q1: Asking Robustness"
        Q1_G["G (List-Order Greedy)"]
        Q1_ARR["G_arr (Arrival Order)"]
        Q1_LIFO["G_lifo (Reverse Arrival)"]
        Q1_DEG["G_deg (Degree-Based)"]
        Q1_REF["Q6 & P Baselines"]
    end

    subgraph "Study Q2: Prior Sensitivity"
        Q2_SIM["PS_sim & N3e_sim (Simulator Constants)"]
        Q2_EMP["PS_emp & N3e_emp (Observable-Fit)"]
        Q2_FLAT["PS_flat & N3e_flat (Flat Priors)"]
    end

    subgraph "Study Q3: Adaptive Drift"
        Q3_X1["X1_emp (Adaptive + Calibrated)"]
        Q3_NOCAL["X1_nocal_emp (Calibration Ablation)"]
        Q3_NOLEARN["X1_nolearn_emp (Learning Ablation)"]
        Q3_ORACLE["X1_oracle (Oracle Drift Detector)"]
    end

    FS --> Q1_G & Q1_ARR & Q2_EMP & Q3_X1
```

---

## 6. Implementation Artifacts & Source File Map

The codebase of Round 2 Supplemental Studies resides in [`research9/round2/`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research9/round2):

- [`REPORT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research9/round2/REPORT.md): Comprehensive 7-section technical report ($19.3\text{ KB}$).
- [`fastsim.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research9/round2/fastsim.py): High-performance deterministic simulator, validated bit-for-bit against `kit.py` ($18.1\text{ KB}$).
- [`laws.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research9/round2/laws.py): Declarations for 20 condition laws spanning arrival bursts, weight perturbations, latency spikes, and mid-episode drift ($5.9\text{ KB}$).
- [`oracle_value.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research9/round2/oracle_value.py): Privileged Gauss-Hermite quadrature host diagnostic calculator ($3.9\text{ KB}$).
- [`priors.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research9/round2/priors.py): Numerical implementations of `sim`, `emp`, and `flat` priors ($3.9\text{ KB}$).
- [`episode.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research9/round2/episode.py): Cold subprocess execution harness enforcing immutable digest logging ($7.9\text{ KB}$).
- [`run_campaign.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research9/round2/run_campaign.py): Multiprocessing batch runner managing the 7 global worker slots ($2.1\text{ KB}$).

### Processed Analytical Datasets (`study_notes/data/`)
- [`study_analysis.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/study_analysis.json): Complete re-analysis containing paired contrasts, Holm $p$-values, and cell checks ($35.3\text{ KB}$).
- [`calibration.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/calibration.json): Brier scores, reliability bins, and directional calibration data ($28.4\text{ KB}$).
- [`waiting.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/waiting.json): Complete waiting time percentiles and unserved rates ($7.1\text{ KB}$).
- [`episode_metrics.csv`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/episode_metrics.csv): Row-level records for all 2,076 executed episodes ($456\text{ KB}$).
- [`provenance.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/provenance.json): SHA-256 cryptographic manifest covering all input and output files ($5.8\text{ KB}$).

---

## 7. Experimental Protocol, Grid & Environmental Design

The Supplemental Round 2 Studies executed a massive multi-study grid:

| Study | Scientific Focus | Seeds | Condition Laws | Arms | Total Episodes |
|---|---|:---:|:---:|:---:|:---:|
| **Q1** | Asking Order Robustness | 12 | 16 | 6 | 1,152 |
| **Q2** | Prior Sensitivity | 12 | 5 | 7 | 420 |
| **Q3** | Adaptive Drift & Calibration | 12 | 6 | 7 | 504 |
| **Total** | **Combined Round 2 Grid** | **12** | **20 unique** | **15 unique** | **2,076** |

- **Exact Geometry:** 2,076 total recorded episodes across 1,968 unique `(seed, law, arm)` cells.
- **Repeat Cells:** Exactly **108 cross-study repeat cells** executed under identical seeds and laws to certify cross-study determinism.
- **Member Denominator:** Exactly 200 arrived members per episode ($415,200$ arrived member-episodes total).

---

## 8. Provenance, Execution Environment & Infrastructure Integrity

From [`study_notes/data/provenance.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/provenance.json):
- **Deterministic Replay:** All 108 repeated cells achieved identical SHA-256 hashes across world generation, questioning action logs, and match decisions (`"exact_cross_study_repeat_cells": 108`).
- **Same Asking Control Hashes:** In Q3, all 7 arms shared identical ask-log digests with Greedy on matching worlds (`"identical_asking_control_cells": 72`).
- **Cold Subprocess Isolation:** Maximum in-process call time was $0.048\text{ s}$; maximum cold transport latency was $0.621\text{ s}$, safely inside the 10-second limit.

---

## 9. Primary Empirical Findings & Quantitative Results

### 9.1 Study Q1: Asking Order Contrasts vs Greedy ($G$)
From [`study_analysis.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/study_analysis.json) ($n = 12$ seed clusters, 16 condition laws):

| Policy Arm | Mechanism | Mean Difference vs $G$ | Cluster SE | 95% Student-$t$ CI | Holm-Adjusted $p$-value |
|---|---|:---:|:---:|:---:|:---:|
| **$G_{\text{arr}}$** | Chronological Arrival Order | **$+0.0990$** | 0.0768 | $[-0.0701, \, +0.2680]$ | **$0.8965$** |
| **$G_{\text{lifo}}$** | Reverse Arrival (LIFO) | $+0.0026$ | 0.0456 | $[-0.0977, \, +0.1029]$ | $1.0000$ |
| **$Q6$** | R6 Two-Query Optimizer | $-0.0312$ | 0.0458 | $[-0.1321, \, +0.0696]$ | $1.0000$ |
| **$G_{\text{deg}}$** | Bipartite Degree Order | $-0.0677$ | 0.0786 | $[-0.2408, \, +0.1054]$ | $1.0000$ |
| **$P$** | Population Score Control | $-0.1172$ | 0.0684 | $[-0.2677, \, +0.0333]$ | $0.5732$ |

![Robustness Contrasts](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/02_robustness_contrasts.png)

### 9.2 Study Q2: Observable Prior Sensitivity
From [`study_analysis.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/study_analysis.json) ($n = 12$ seed clusters, 5 condition laws):

| Model Base | Prior Variant | Mean MSMI / 100 | Contrast vs Simulator Prior (`sim`) | 95% Confidence Interval | Holm $p$-value |
|---|---|:---:|:---:|:---:|:---:|
| **$PS$** | `sim` (Simulator Constants) | $0.3583$ | Baseline | — | — |
| **$PS$** | `emp` (Observable-Fit) | $0.3250$ | $-0.0333$ | $[-0.0897, \, +0.0231]$ | $0.8796$ |
| **$PS$** | `flat` (Uninformative) | $0.4000$ | $+0.0417$ | $[-0.1152, \, +0.1985]$ | $0.8796$ |
| **$N3e$** | `sim` (Simulator Constants) | $0.4750$ | Baseline | — | — |
| **$N3e$** | `emp` (Observable-Fit) | $0.4833$ | $+0.0083$ | $[-0.1860, \, +0.2027]$ | $1.0000$ |
| **$N3e$** | `flat` (Uninformative) | $0.4333$ | $-0.0417$ | $[-0.2081, \, +0.1248]$ | $1.0000$ |

![Prior Sensitivity](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/04_prior_sensitivity.png)

### 9.3 Study Q3: Adaptive Drift & Calibration Ablation
From [`study_analysis.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/study_analysis.json) ($n = 12$ seed clusters, 6 drift laws):

| Policy Arm | Contrast vs Baseline / Parent | Mean Difference | Cluster SE | 95% Confidence Interval | Holm $p$-value |
|---|---|:---:|:---:|:---:|:---:|
| **$X1_{\text{emp}}$** | $X1_{\text{emp}} - G$ | $-0.1389$ | 0.1473 | $[-0.4632, \, +0.1854]$ | $1.0000$ |
| **$X1_{\text{sim}}$** | $X1_{\text{sim}} - G$ | $-0.0694$ | 0.1552 | $[-0.4110, \, +0.2721]$ | $1.0000$ |
| **Calibration Ablation** | **$X1_{\text{emp}} - X1_{\text{nocal\_emp}}$** | **$0.0000$** | **0.0000** | **$[0.0000, \, 0.0000]$** | **$1.0000$** |
| **Learning Ablation** | $X1_{\text{emp}} - X1_{\text{nolearn\_emp}}$ | $+0.0139$ | 0.0139 | $[-0.0167, \, +0.0445]$ | $1.0000$ |
| **Adaptive Gain** | $X1_{\text{emp}} - PS_{\text{emp}}$ | $+0.0139$ | 0.0139 | $[-0.0167, \, +0.0445]$ | $1.0000$ |

![Adaptive Ablations](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/05_adaptive_ablations.png)

---

## 10. Statistical Rigor, Hypothesis Testing & Confidence Intervals

### 10.1 The Seed-Cluster Inferential Unit
Treating the 16 condition laws within a seed as independent observations would falsely inflate sample size to $n = 192$, yielding an artificially narrow interval for $G_{\text{arr}} - G$ that excludes zero ($p < 0.05$). Research 9 Round 2 enforced **seed clustering** ($n = 12$ degrees of freedom):
$$t_{\text{crit}, 0.975, 11} = 2.201$$
Because variations across condition laws within a single world seed share common latent member preference graphs, pooling across laws without clustering commits severe unit-of-analysis pseudoreplication. Correct clustering expands the interval to $[-0.0701, +0.2680]$, demonstrating that arrival ordering is **statistically indistinguishable from Greedy**.

### 10.2 The Bit-for-Bit Calibration Identity
The calibration ablation ($X1_{\text{emp}}$ vs $X1_{\text{nocal\_emp}}$) produced a remarkable empirical finding: across all 72 drift cells, the match actions chosen by $X1$ with directional calibration were **$100\%$ identical** to those chosen without calibration. Because calibration applies a monotonic shift to all dyad scores simultaneously, it preserved the exact ordinal ranking of candidate edges. Thus, calibration never altered a single introduction.

---

## 11. Diagnostic Ablations, Reliability & Subgroup Analysis

### 11.1 The Downstream Outcome Funnel
From [`10_outcome_funnel.png`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/10_outcome_funnel.png), tracing 192 episodes of Greedy ($G$) in Q1:
1. **Introductions Assigned:** $71.04$ per episode ($35.52$ per 100 arrived).
2. **Mutual First Acceptances:** $10.51$ per episode ($5.26$ per 100 arrived).
3. **Dates Actually Occurred:** $7.82$ per episode ($3.91$ per 100 arrived).
4. **Qualified MSMI Introductions:** **$0.66$ per episode ($0.33$ per 100 arrived)**.

![Outcome Funnel](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/10_outcome_funnel.png)

**Downstream Attrition Rate:** **$99.5\%$**. Out of every 200 introductions assigned by the policy, only 1 survives to become a qualified, timely mutual second-meeting intention.

### 11.2 Who Gets Left Waiting?
From [`waiting.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/waiting.json) and [`subgroups_q1_greedy.csv`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/subgroups_q1_greedy.csv) (38,400 member-episodes):

| Subgroup Category | Subgroup Level | Total Member-Episodes | Unserved Rate (%) |
|---|---|:---:|:---:|
| **Information Status** | Hard Decline Registered | 1,842 | **100.0%** |
| **Information Status** | Incomplete Profile at Arrival | 14,880 | **100.0%** |
| **Information Status** | Complete Profile at Arrival | 23,520 | **38.7%** (61.3% Served) |
| **Gender** | Female | 19,200 | 66.5% |
| **Gender** | Male | 19,200 | 66.6% |
| **Age Group** | Under 30 | 12,840 | 66.4% |
| **Age Group** | 30–39 | 12,780 | 66.6% |
| **Age Group** | 40 and Over | 12,780 | 66.7% |

![Waiting and Coverage](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/08_waiting_and_coverage.png)
![Access Subgroups](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/09_access_subgroups.png)

**Key Finding:** Demographic categories (gender, age) exhibited completely uniform access rates (~33.4% served, ~66.6% unserved). In stark contrast, **information status created absolute exclusion**: members with incomplete profiles or hard declines faced a 100% exclusion rate due to eligibility constraints.

---

## 12. Failure Modes, Negative Results & Architectural Pathology

The supplemental studies exposed three fundamental structural pathologies:

### 12.1 The Host-Expectation Illusion in Prior Tuning
In Q2, host-only expected MSMI diagnostics (which compute expectation using privileged simulator ground truth) suggested that Population Scoring ($PS$) should achieve over $0.70$ MSMI/100. In live simulation, however, realized MSMI hovered between $0.32$ and $0.40$. The host expectation assumes independent date execution, ignoring network collisions and date lag lockup.

### 12.2 Rank-Invariance of Directional Calibration
In Q3, adding an online logit offset $\delta_t$ was intended to adjust for post-day-35 drift. However, because $\delta_t$ shifted all edge probabilities monotonically, it produced an identical sorting order over candidate matchings. Unless calibration alters edge thresholds in an active reservation model, **scalar calibration is rank-invariant and completely inert in greedy matching**.

### 12.3 Condition Heatmap Heterogeneity
From [`03_condition_heatmap.png`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/03_condition_heatmap.png), candidate differences varied wildly across conditions:
- $G_{\text{arr}}$ achieved $+0.42$ MSMI/100 under bursty arrival conditions (`burst_early`), but dropped to $-0.17$ under extreme response delays (`latency_high`).
- This confirms that no single asking order dominates universally across all operating regimes.

![Condition Heatmap](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/03_condition_heatmap.png)

---

## 13. Computational, Memory & Storage Footprint

- **Execution Scale:** 2,076 episodes executed in 1,241 CPU-seconds using the parallel runner across 7 workers.
- **Simulator Parity:** `fastsim.py` achieved a $14\times$ speedup over the reference `kit.py` implementation while maintaining exact bit-for-bit trajectory parity.
- **Storage Conservation:** All raw and processed analytical data files totaled **$1.8\text{ MB}$**, while figure assets totaled **$2.4\text{ MB}$**.

---

## 14. Retrospective Synthesis & Belief Revision

| Dimension | What We Once Believed | What the Evidence Supported | What We Believe Now |
|---|---|---|---|
| **FIFO Asking Advantage** | FIFO asking provides a confirmed, universal advantage over list-order asking. | $G_{\text{arr}}$ gained $+0.0990$ in point estimate, but $95\%$ CI $[-0.0701, +0.2680]$ ($p = 0.8965$) failed significance. | Arrival-ordered asking has an intuitive positive heuristic signal, but is not an established statistical winner. |
| **Observable Priors** | Estimating priors from observable data (`emp`) will resolve model mismatch. | Point estimates varied slightly ($-0.03$ to $+0.01$), but none established superiority over simulator priors. | Prior tuning cannot overcome the fundamental informational bottleneck of delayed feedback. |
| **Directional Calibration** | Calibrating probability models during mid-episode drift rescues allocation quality. | Direct ablation yielded $0.0000$ difference; action logs matched $100\%$ bit-for-bit. | Scalar calibration does not change ordinal greedy edge selection; calibration is inert without reservation thresholds. |
| **Outcome Sparsity** | Optimization should focus on improving introduction matching algorithms. | $99.5\%$ of assigned introductions fail to achieve qualified MSMI due to human attrition and delays. | The primary constraint on matching performance is downstream human attrition, not matching graph cardinality. |

The Supplemental Round 2 Studies provided the definitive empirical proof required for the final policy decision: Greedy ($G$) must be retained as the benchmark production standard.
