# Examination Coverage Matrix: Research Phases, Algorithms, and Core Syllabus

**The Sequential Reciprocal Matching Problem Under Changing Conditions**  
**Monograph Reference Systems & Curricular Coverage Matrix**  
**Authoritative Reference:** [final_report/REPORT.md](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/final_report/REPORT.md) | [study_notes/reference/source_map.md](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reference/source_map.md)

---

## 1. Core Examination Syllabus Domains

The Sequential Matching monograph spans eight foundational technical domains:
1. **Section I: Problem Formulation, Information Boundaries & Time Horizons** (60 decision days, 40 follow-up days, daily 2-call protocol, information fences).
2. **Section II: Sparse Feasibility, Reciprocal Graph Constraints & Matching Theory** (11 hard constraints, non-bipartite general graphs, maximal vs maximum matching, Edmonds' blossom).
3. **Section III: Information Acquisition & Clarification Questioning Strategies** (Hard bundles vs soft questions, budget constraints, FIFO clarification invariance, coordinated queries).
4. **Section IV: Statistical Outcome Modeling, Funnel Decomposition & Calibration** (Outcome funnel, $0.36$ timeliness factor, Brier scores, ECE, directional logit calibration, hybrid empirical priors).
5. **Section V: Non-Stationary Dynamics, Adaptive Policies & Component Ablations** (Temporal drift, recency weighting, MAP penalty, action digest invariance, oracle schedule).
6. **Section VI: Experimental Design, Cluster Randomization & Statistical Multiplicity** (Seed cluster inference, Student-$t$ distribution, Holm-Bonferroni correction, independent observation fallacy).
7. **Section VII: Service Access, Waiting Time Distributions & Demographic Fairness** (Served vs unserved waiting distributions, right-censoring, demographic access disparities, fairness limits).
8. **Section VIII: Production Engineering, Docker Containerization & Reproducibility** (Resource budgets, read-only OCI runtime, test suite verification, closed research protocol).

---

## 2. Research Phases to Exam Syllabus Matrix

| Phase Identifier | Core Focus and Historical Deliverables | Primary Exam Syllabus Domains Covered | Key Artifacts & Reference Links |
|---|---|---|---|
| **Phase 1 (`research/`)** | Round 1 development; feasibility scan; 20-arm design; `simple_fifo` selection & 40-cluster confirmatory evaluation. | **Section I, II, III, VI** | [`ROUND1_SUBMISSION.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/ROUND1_SUBMISSION.md), [`research/THEORY.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research/THEORY.md), [`results/extended/confirmation_statistics.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/results/extended/confirmation_statistics.json) |
| **Phase 2 (`research2/`)** | Immediate Round 1 post-mortem; regression isolation; benchmark logging stability. | **Section VIII** | `research2/FINAL_REPORT.md`, `research2/EXPERIMENT_REGISTRY.md` |
| **Phase 3 (`research3/`)** | Simulator replication; Available Feedback Theorem; early prediction audits and forensics. | **Section I, IV** | `research3/REPLICATION.md`, `research3/AVAILABLE_FEEDBACK_THEOREM.md`, `research3/PREDICTION_AUDIT.md` |
| **Phase 4 (`research4/`)** | Outcome response factorization; date latency independence; deadline invariance theorems. | **Section I, IV** | `research4/DEADLINE_INVARIANCE.md`, `research4/RESPONSE_FACTORISATION.md`, `research4/MECHANISMS.md` |
| **Phase 5 (`research5/`)** | Platform hardening; world review; archive integrity; worker memory caps. | **Section VIII** | `research5/WORLD_REVIEW.md`, `research5/PACKAGE_REVIEW.md`, `research5/LOGGING_REVIEW.md` |
| **Phase 6 (`research6/`)** | Stage A exact small-model dynamic programming; Stage B–D selection; Stage E massive confirmation ($N=571$ clusters, Q6 vs G). | **Section II, III, VI** | [`research6/REPORT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research6/REPORT.md), `research6/exact/THEORY.md`, [`results/research6/stage_e_confirmation/`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/results/research6/stage_e_confirmation/) |
| **Phase 7 (`research7/`)** | Orchestrated split tracks (7A/7B); statistical design frameworks; candidate merge protocols. | **Section VI, VIII** | `research7/STATISTICS.md`, `research7/STRATEGIES.md`, `research7/MERGE_PROTOCOL.md` |
| **Phase 8 (`research8/`)** | Reduced continuation models; reservation thresholds; deliberate waiting probe ($N=24$ cells). | **Section II, V** | [`research8/README.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research8/README.md), [`research8/continuation_probe/DECISION.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research8/continuation_probe/DECISION.md) |
| **Phase 9 (`research9/`)** | Round 2 exploratory studies (Q1 robustness, Q2 priors, Q3 drift); audited 288-cell closed learned screen. | **Section III, IV, V, VI** | [`research9/round2/`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research9/round2/), [`research9/final_campaign/selection.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research9/final_campaign/selection.json), `campaign_closed.json` |
| **Final Synthesis (`final_report/`)** | Corrected seed-cluster statistical reanalysis; 12 visual atlas figures; independent claim & code audits. | **All Sections (I–VIII)** | [`final_report/REPORT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/final_report/REPORT.md), [`build_assets.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/final_report/build_assets.py), [`data/provenance.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/final_report/data/provenance.json) |

---

## 3. Algorithmic Methods to Exam Syllabus Matrix

| Method / Algorithm / Policy Arm | Structural Class / Mechanism | Exam Syllabus Domains Covered | Key Theoretical Invariant / Core Empirical Finding |
|---|---|---|---|
| **`G` (Supplied Baseline)** | List-order FIFO hard asks + soft agreement greedy allocation | **Section II, III, VIII** | Retained root production executable. Provides optimal balance of constraint resolution and low algorithmic variance on sparse graphs. |
| **`simple_fifo`** | FIFO hard asks + constant aggregate terminal score + canonical ID sort | **Section III, VI** | Confirmatory negative ($d = -0.27$, $p = 0.096$). Demonstrates that uninformative scoring degrades greedy tie-breaking. |
| **`G_arr`** | Chronological arrival order hard asks + greedy allocation | **Section I, III, VI** | Point estimate $+0.0990$ MSMI/100, but seed-cluster 95% CI spans zero ([$-0.0701, +0.2680$], Holm $p = 0.8965$). Disproves feedback cutoff fallacy. |
| **`G_lifo` / `G_deg`** | Reverse arrival / potential-degree asking + greedy allocation | **Section III, VI** | Both fail to beat $G$. Shows high degree prioritization does not overcome joint reciprocal sparsity. |
| **`Q6` / `N3_two` / `N3e`** | Coordinated 2-query lookahead acquisition | **Section II, III, VI** | Confirmatory negative across 571 clusters ($p = 0.765$). Coordination overhead provides zero detectable benefit. |
| **`PS_sim` / `PS_emp` / `PS_flat`** | Multi-stage parametric scoring under alternative priors | **Section IV, VI** | All trail $G$. Empirical prior underpredicts terminal events due to snapshot date censoring ($0.4762$ vs $0.78$). |
| **`X1_emp` / `X1_sim`** | Recency-weighted adaptive scoring ($\tau=14$d) + directional calibration | **Section IV, V** | Adaptive tracking trails $G$ ($0.4444$ vs $0.5833$, Holm $p = 1.000$). Binary feedback too sparse for reliable parameter updates. |
| **`X1_nocal_emp`** | Adaptive scoring ablation removing directional logit calibration | **Section IV, V** | **Action Digest Invariance**: Identical allocation batches to $X1_{\text{emp}}$ across all 72 episodes ($0.0000$ difference). |
| **`X1_oracle`** | Privileged diagnostic scorer provided with ground-truth drift schedule | **Section V** | Underperforms $G$ ($0.4583$ vs $0.5833$), proving that complex scoring failure is rooted in graph sparsity, not drift misestimation. |
| **`Edmonds' Blossom`** | Exact maximum-weight general matching ($O(V^2 E)$) | **Section II, VIII** | Solves general non-bipartite matching, but produces zero MSMI gain over greedy first-fit due to severe graph sparsity. |
| **`Reservation / Holding`** | Threshold-based pair withholding for continuation value | **Section II, V** | Holding pairs back reduced assignments ($960 \to 954$) with zero gain in qualified pairs ($10 \to 10$). |
| **`model_greedy` / `repair` / `soft`** | Supervised funnel models trained on 216k historical rows | **Section IV, VI, VIII** | All failed the screen admission gate ($0.1875 - 0.2188$ vs $G=0.3229$). Confirmatory groups remained unopened. |
| **`no_asks` / `random`** | Supplied lower bound and randomized feasible controls | **Section II, III** | Clarification expands graph from 17.8 to 59.6 edges. `no_asks` collapses to $0.05$ MSMI/100; `random` achieves $0.3167$. |

---

## 4. Final Report Chapters to Exam Syllabus Matrix

| Chapter in `final_report/REPORT.md` | Chapter Title & Core Content | Primary Exam Syllabus Domains Covered | Key Pedagogical Takeaway |
|---|---|---|---|
| **Chapter 1** | *Direct Answers to Submission Questions & R1 Feedback* | **All Sections (I–VIII)** | Executive synthesis; transparency on negative results; defense of baseline retention. |
| **Chapter 2** | *Problem, Information Boundary and Outcomes* | **Section I, IV, VII** | Formal definition of $Q$, 60+40 horizons, 30-day date deadline, 3-day feedback bounds, non-substitutability of oracle rewards. |
| **Chapter 3** | *Methodology and Algorithms* | **Section II, III, V** | Algorithmic anatomy of $G$, FIFO clarification invariance, $X1$ adaptive shrinkage formulation, continuation probe scope. |
| **Chapter 4** | *Evidence Design, Provenance and Statistical Analysis* | **Section VI, VIII** | Seed cluster contrasts $D_s$, Student-$t$ (11 df), Holm cumulative max, separation of historical and exploratory cohorts. |
| **Chapter 5** | *FIFO Robustness Under Changing Conditions* | **Section III, VI** | Q1 16-law robustness evaluation; corrected $G_{\text{arr}}$ confidence interval; disproof of the day-60 feedback cutoff theory. |
| **Chapter 6** | *Priors Estimated from Public Observations* | **Section IV, VI** | Q2 prior comparison; disclosure of hybrid empirical prior structure and snapshot censoring distortions. |
| **Chapter 7** | *Adaptive Drift Alternative and Ablations* | **Section IV, V** | Q3 drift results; proof of action digest invariance under directional calibration; privileged oracle schedule diagnostics. |
| **Chapter 8** | *Calibration and the Outcome Funnel* | **Section I, IV** | Controlled calibration on 5,009 identical $G$ edges; Brier prevalence comparators; outcome funnel attrition across stages. |
| **Chapter 9** | *Who Gets Left Waiting?* | **Section II, VII** | Served-only waiting CDFs; unserved fractions; information status vs demographic disparities; limits of fairness claims. |
| **Chapter 10** | *Baselines and the Wider Research Record* | **Section III, VI** | Historical controls ($N=30$); Round 1 confirmation ($N=40$); Research 6 Stage E ($N=571$); Closed learned screen ($N=288$). |
| **Chapter 11** | *Limitations and Improvements from Round 1* | **Section I–VIII** | Comprehensive accounting of solved vs unresolved challenges across the 9 research dimensions. |
| **Chapter 12** | *Final Policy Decision* | **Section II, VIII** | Principled justification for retaining supplied Greedy baseline in production. |
| **Chapter 13** | *Reproduction, Validation and Remaining Checks* | **Section VIII** | Rebuilding assets via `build_assets.py`; unit/data validation logs; remaining container and source-pinning steps. |
| **Appendices A & B** | *Submission-Form Text and Asset Index* | **Section I, VIII** | Official competition answer field text and master index of data tables and figures. |
