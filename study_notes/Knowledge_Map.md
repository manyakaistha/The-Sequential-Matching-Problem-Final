---
title: The Sequential Matching Problem — Master Knowledge Map
tags: [smp/moc, smp/curriculum, smp/architecture]
status: complete
date: 2026-10-17
---

# The Sequential Matching Problem — Master Knowledge Map

> **Master Curriculum Architecture & Cross-Reference Index**  
> Comprehensive learning spine connecting theoretical formulations, algorithmic mechanics, empirical evidence, research phase forensics, and oral defense mastery.  
> Governed by the pedagogical discipline: **Concept → Code → Output → Interpretation**.

**Central Hub:** [`README.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/README.md) · [`defense/question_bank.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/defense/question_bank.md) · [`reference/quick_reference.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reference/quick_reference.md)

---

## 1. The 13-Chapter Monograph Spine

| Chapter | Title | Core Research Question | Status | Key Asset Reference |
| :---: | :--- | :--- | :---: | :--- |
| **[[00_learning_path_and_diagnostic\|Ch 00]]** | Learning Path & Pre-Assessment Diagnostic | What foundational knowledge is required, and what traps fail unprepared candidates? | Complete | Self-diagnostic baseline rubric |
| **[[01_problem_statement_and_rules\|Ch 01]]** | Problem Statement, Rules, and Objective | How is sequential reciprocal matching formalized, and what governs qualified MSMI? | Complete | `fig10_outcome_funnel` |
| **[[02_foundations_python_probability_and_graphs\|Ch 02]]** | Python, Probability, and Graph Theory | How do bipartite feasibility graphs, coupling, and blossom algorithms constrain decisions? | Complete | Blossom LP duality matrix |
| **[[03_simulator_protocol_and_event_timeline\|Ch 03]]** | Simulator Protocol & Event Timeline | What happens within the discrete event loop between Day 0 and Follow-up Day 99? | Complete | Two-phase discrete event loop |
| **[[04_data_information_boundaries_and_leakage\|Ch 04]]** | Information Boundaries & Anti-Leakage | Which attributes belong to the policy versus the environment, and where is leakage fatal? | Complete | Public vs Private state boundary |
| **[[05_asking_matching_and_baselines\|Ch 05]]** | Elicitation, Matching, and Baselines | Why does Greedy matching dominate, and why does budget-constrained elicitation break submodularity? | Complete | `fig12_supplied_baselines_historical` |
| **[[06_models_learning_and_calibration\|Ch 06]]** | Models, Learning, and Calibration | Why did supervised conversion models fail their validation gate, and why does calibration preserve greedy actions? | Complete | `fig06_calibration`, `fig07_drift_calibration` |
| **[[07_sequential_decisions_and_theory\|Ch 07]]** | Sequential Decisions & MDP Theory | How does continuous-time matching theory collapse under finite arrivals, and why is promptness penalizing? | Complete | 0.36 timing penalty derivation |
| **[[08_experimental_design_and_statistics\|Ch 08]]** | Experimental Design & Clustered Statistics | Why does treating episodes as independent cause pseudoreplication, and how does Holm correction work? | Complete | `fig02_robustness_contrasts`, `fig03_condition_heatmap` |
| **[[09_cross_phase_discoveries_and_final_decision\|Ch 09]]** | Cross-Phase Discoveries & Final Decision | How did candidate beliefs evolve across 10 phases, and why was Greedy chosen for production? | Complete | `fig01_confirmation_context` |
| **[[10_code_atlas_and_walkthroughs\|Ch 10]]** | Code Atlas, Symbol Index & Walkthroughs | Where are classes, functions, invariants, and state mutations defined in the codebase? | Complete | Exhaustive symbol lookup matrix |
| **[[11_reproducibility_runtime_and_evidence_storage\|Ch 11]]** | Reproducibility, Runtime & Evidence Storage | How does Zstandard level 3 compression and safe tarfile streaming protect archived runs? | Complete | Bounded streaming extraction |
| **[[12_limitations_contradictions_and_unknowns\|Ch 12]]** | Limitations, Contradictions & Open Questions | What are the unresolved paradoxes (64.5% unserved) and architectural boundaries? | Complete | `fig08_waiting_and_coverage`, `fig09_access_subgroups` |

---

## 2. The 10-Phase Empirical Research Archive

| Phase | File | Title & Core Investigation | Sample Size ($N$) | Decisive Finding |
| :---: | :--- | :--- | :---: | :--- |
| **01** | [[phases/01_round1_and_extended_candidates\|Phase 01]] | Round 1 & Extended Candidates | $N=40$ runs | `simple_fifo` collapsed ($0.075$ MSMI); high volume does not yield quality. |
| **02** | [[phases/02_research2\|Phase 02]] | Scarcity Penalties & Truncation Forensics | $N=120$ episodes | Incomplete profiles suffer severe graph disconnects; truncation bias detected. |
| **03** | [[phases/03_research3_feedback_and_forensics\|Phase 03]] | Feedback Timing & 3-Day Qualification Drop | $N=180$ episodes | The 3-day post-date promptness rule eliminates 64% of mutually positive pairs. |
| **04** | [[phases/04_research4_invariance_and_factorisation\|Phase 04]] | Deadline Invariance & Response Factorization | $N=240$ episodes | Response delay factorizes independently of preference affinity; invariant holds. |
| **05** | [[phases/05_research5_replication_and_world_audit\|Phase 05]] | Replication Review & World Hash Audit | 430 clusters ($10^6$ mbrs) | First full-scale audit; identical `world_sha256` verified within all cells. |
| **06** | [[phases/06_research6_stages_and_confirmation\|Phase 06]] | Multi-Stage Screening & $N3_{\text{two}}$ Collapse | $N=571$ episodes | $N3_{\text{two}}$ collapsed under delayed feedback; confirmation trap documented. |
| **07** | [[phases/07_research7_branching_and_reservations\|Phase 07]] | Branching Protocols & Reservation Theory | $N=0$ sim runs | Strict workspace isolation between coordinator and satellite; zero leaks. |
| **08** | [[phases/08_research8_reduced_planning_and_soft_queries\|Phase 08]] | Reduced Planning & Soft-Query Trials | $N=432$ episodes | Soft queries yielded $+0.0625$ point gain, but failed Holm significance ($p=0.0842$). |
| **09** | [[phases/09_research9_closed_learned_campaign\|Phase 09]] | Closed Learned Campaign & Gate Collapse | 288 tournament cells | Predictive models failed validation gate; confirmation seeds kept pristine. |
| **10** | [[phases/10_research9_supplemental_round2_studies\|Phase 10]] | Round 2 Supplemental Studies (Q1–Q3) | 2,076 records (12 seeds) | Clustered testing proves no policy arm beats baseline Greedy ($G$). |

---

## 3. Oral Examination & Defense Training Curriculum

The defense curriculum prepares candidates for comprehensive oral examination, dissertation defense, and skeptical technical interrogation:

* **150-Question Master Question Bank**: [`defense/question_bank.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/defense/question_bank.md)  
  * Section 1: Beginner Comprehension (Q1–Q25)
  * Section 2: Algorithm & Code Tracing (Q26–Q50)
  * Section 3: Mathematical & Statistical Derivations (Q51–Q75)
  * Section 4: Experimental Design & Provenance (Q76–Q100)
  * Section 5: Interpretation of Results & Limitations (Q101–Q125)
  * Section 6: Production, Runtime & Evidence Storage (Q126–Q140)
  * Section 7: Adversarial Interrogation & Follow-Up Chains (Q141–Q150)
* **Worked Derivations & Code Traces**: [`defense/worked_statistics_and_code_exercises.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/defense/worked_statistics_and_code_exercises.md)
* **Independent Practice Problems**: [`defense/independent_exercises.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/defense/independent_exercises.md)
* **Complete Answer Keys & Defense Scripts**: [`defense/answer_keys.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/defense/answer_keys.md)
* **Three 100-Point Mock Defense Examinations**: [`defense/mock_examinations.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/defense/mock_examinations.md)
* **Candidate Readiness & Scoring Rubric**: [`defense/readiness_rubric.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/defense/readiness_rubric.md)

---

## 4. Concept Spine & Cross-Cutting Themes

```
                             THE SEQUENTIAL MATCHING PROBLEM
                                           │
         ┌─────────────────────────────────┼─────────────────────────────────┐
         ▼                                 ▼                                 ▼
   GRAPH MECHANICS                  DECISION THEORY                 STATISTICAL RIGOR
  • Bipartite Feasibility          • Partially Observable MDP      • Clustered Paired Tests
  • Resource Contention            • Multi-Stage Elicitation       • Holm FWER Step-Down
  • Submodularity Breakdown        • Monotonic Ranking Invariance   • Murphy Brier Decomposition
  • Degree Concentration           • 0.36 Timing Penalty           • Degrees of Freedom (df=11)
```

### 4.1 Graph Mechanics & Allocation Topology
- **Sparse Feasibility**: Graph density $< 0.3\%$ under hard demographic and preference constraints.
- **Resource Contention**: Bilateral matching commits both nodes, destroying all alternative incident edges for up to 30 days.
- **Submodularity Breakdown**: Hard constraints require multi-attribute query bundles, violating diminishing returns and breaking standard greedy submodular guarantees.

### 4.2 Decision Theory & Sequential Control
- **Two-Phase Daily MDP**: Daily inquiry phase ($\le 12$ credits) followed by daily matching phase (disjoint edge batch).
- **The Monotonic Calibration Invariance**: Calibration maps logits via strictly increasing transformations, which preserves edge rankings $\prec_w$ and leaves discrete greedy matchings 100% bit-identical.
- **The Promptness Penalty (0.36)**: Post-date feedback delay $D \sim \text{Uniform}\{1, \dots, 5\}$ requires both parties to submit within 3 days: $(3/5)^2 = 0.36$.

### 4.3 Statistical Discipline & Governance
- **Cluster Pseudoreplication**: 2,076 records across 1,968 cells share only 12 independent seeds. Naive $N=1,968$ inference collapses standard errors by $4\times$, creating spurious significance.
- **Strict Closed Protocol**: Research was formally frozen. No new simulation episodes, no modified model fits, no consumption of the 96 confirmation seeds.

---

## 5. Central System Pipeline

$$\textbf{Dynamic Arrivals} \longrightarrow \textbf{Public State Filter} \longrightarrow \textbf{Elicitation Policy} \longrightarrow \textbf{Matching Policy} \longrightarrow \textbf{Simulator Feedback} \longrightarrow \textbf{Qualified MSMI}$$

1. **Member Arrival**: Stochastically generated members enter the candidate pool with observed baseline demographics and masked private preferences.
2. **State Filtration**: Policy receives strictly scrubbed `PublicState`, eliminating unasked fields and future arrivals.
3. **Elicitation Phase**: Policy expends up to 12 credits to resolve hard constraints or soft preferences.
4. **Matching Phase**: Policy computes disjoint edges on the active feasibility subgraph.
5. **Event Progression**: Simulator evaluates mutual acceptances, schedules physical dates, collects dual feedback, and applies the 3-day promptness gate.
6. **Terminal Outcome**: Episodes are evaluated at Day 99 by counting qualified pairs normalized per 100 arrived members.

---

## 6. Visual Asset Index & Evidence Grounding

All publication figures are stored in SVG and PNG formats in [`study_notes/assets/`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/) and generated deterministically via [`study_notes/scripts/reproduce_figures.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/scripts/reproduce_figures.py):

1. **Figure 1**: Confirmation Context & Historical Trajectory ([`01_confirmation_context.png`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/01_confirmation_context.png))
2. **Figure 2**: Paired Contrasts & Confidence Intervals in Study Q1 ([`02_robustness_contrasts.png`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/02_robustness_contrasts.png))
3. **Figure 3**: Environmental Condition Heatmap ([`03_condition_heatmap.png`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/03_condition_heatmap.png))
4. **Figure 4**: Prior Sensitivity Analysis across Scorer Variants ([`04_prior_sensitivity.png`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/04_prior_sensitivity.png))
5. **Figure 5**: Adaptive Drift Ablations in Study Q3 ([`05_adaptive_ablations.png`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/05_adaptive_ablations.png))
6. **Figure 6**: Multi-Stage Conversion Calibration Funnel ([`06_calibration.png`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/06_calibration.png))
7. **Figure 7**: Calibration Reliability under Non-Stationary Drift ([`07_drift_calibration.png`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/07_drift_calibration.png))
8. **Figure 8**: Waiting Time Distributions & Coverage Densities ([`08_waiting_and_coverage.png`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/08_waiting_and_coverage.png))
9. **Figure 9**: Subgroup Access Inequity & Feature Disparities ([`09_access_subgroups.png`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/09_access_subgroups.png))
10. **Figure 10**: The Downstream Outcome Qualification Funnel ([`10_outcome_funnel.png`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/10_outcome_funnel.png))
11. **Figure 11**: Closed Learned Campaign Tournament Results ([`11_closed_learned_screen.png`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/11_closed_learned_screen.png))
12. **Figure 12**: Supplied Historical Baselines Comparison ([`12_supplied_baselines_historical.png`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/assets/12_supplied_baselines_historical.png))
