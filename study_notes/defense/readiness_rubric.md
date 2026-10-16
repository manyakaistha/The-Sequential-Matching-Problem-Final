# Oral Examination Readiness Rubric & Defense Guide

This rubric establishes objective self-assessment criteria, behavioral benchmarks, and conceptual disambiguations for candidates preparing to defend the Sequential Reciprocal Matching benchmark before an oral qualifying committee or executive technical board.

---

# 1. Six Core Competency Evaluation Pillars

Every defense candidate is evaluated across six foundational pillars:

| Pillar | Focus Area | Passing Standard |
|:---|:---|:---|
| **Pillar 1: Conceptual Foundations & Problem Formulation** | Problem horizon, information boundary, hard vs. soft constraints, qualification funnel, metric denominators. | Demonstrates flawless understanding of data contracts, feedback delays, and why MSMI/100 uses arrived members. |
| **Pillar 2: Algorithmic Architecture & Code Tracing** | Internal mechanics of `kit.py`, `policy.py`, greedy asking, greedy matching, and data structures. | Can trace line-by-line execution of asks, matching combinations, eligibility checks, and graph-theoretic properties. |
| **Pillar 3: Mathematical Derivations & Statistical Rigor** | Seed-cluster variance formulas, Degrees of Freedom, t-intervals, Holm step-down, Brier decomposition, Wilson intervals. | Derives formulas from first principles, calculates cluster contrasts with real numbers, and enforces Holm monotonicity. |
| **Pillar 4: Experimental Design, Multiplicity & Provenance** | Historical confirmation vs. exploratory supplemental grids, 288-cell screen, hash verification, audit boundaries. | Accurately identifies experimental units, cites exact cluster counts, and articulates provenance limitations. |
| **Pillar 5: Interpretation of Results & Limitations** | Negative policy findings, refuting FIFO superiority, understanding calibration failure, access disparities. | Defends the retention of Greedy without defensiveness, explaining why tested complexity failed to confirm superiority. |
| **Pillar 6: Production Systems, Runtime & Reproducibility** | Container specifications, resource limits, in-process latency vs. startup overhead, Docker environment gaps. | Details production runtime limits, execution flags, test commands, and transparently discloses Docker status. |

---

# 2. Competency Mastery Levels

### Pillar 1: Problem Formulation
* **Level 1 (Vulnerable):** Believes matching decisions occur during follow-up days (60–99); thinks MSMI counts two outcomes per couple; confuses public profiles with hidden simulator truth.
* **Level 2 (Competent):** Correctly defines 60 decision days and 40 follow-up days; states that MSMI counts pairs over arrived members; recognizes that soft scores cannot override hard constraints.
* **Level 3 (Defense-Ready Master):** Quotes the exact qualification indicator $Q$; details the 30-day date limit and 3-day post-date response deadlines; proves that date occurrence does not guarantee MSMI ($64\%$ delay attrition); explains why arrived-member denominators prevent gaming.

### Pillar 2: Algorithmic Tracing
* **Level 1 (Vulnerable):** Claims Greedy finds a maximum cardinality matching; confuses `baseline_asks` list order with sorted arrival time; forgets that bundle asks cost 3 credits.
* **Level 3 (Defense-Ready Master):** Proves Greedy achieves a maximal matching with competitive ratio $1/2$; traces `itertools.combinations` and deterministic sorting with `-score`; constructs counterexamples on $P_4$ and dynamic sequential MDPs where myopic matching loses optimal reward.

### Pillar 3: Statistical Rigor
* **Level 1 (Vulnerable):** Uses 192 episodes as independent observations ($df = 191$); claims $G_{\text{arr}}$ is statistically superior with $p = 0.001$; forgets the cumulative maximum in Holm.
* **Level 3 (Defense-Ready Master):** Derives seed-cluster contrast $D_s = \frac{1}{|\mathcal{L}|}\sum_\ell (Y_{s\ell a} - Y_{s\ell G})$; computes $df = 11$, standard error $0.0768$, and interval $[-0.0701, +0.2680]$; calculates intracluster correlation $\rho \approx 37\%$; traces Holm step-down across 5 arms enforcing monotonicity.

### Pillar 4: Provenance & Experimental Design
* **Level 1 (Vulnerable):** Claims the supplemental Q1–Q3 studies were preregistered confirmation; treats 415,200 member rows as independent people; asserts Docker container tests passed.
* **Level 3 (Defense-Ready Master):** Cites the 40-seed Round 1 and 571-seed Research 6 confirmations as separate historical blocks; identifies 2,076 supplemental records on 12 reused seeds; discloses that host RSS monitoring was unverified and the Docker daemon was unreachable.

### Pillar 5: Interpretation of Results
* **Level 1 (Vulnerable):** Claims Greedy is mathematically optimal; argues that empirical priors failed because of learning rates; claims demographic parity across gender proves fairness.
* **Level 3 (Defense-Ready Master):** Explains that negative confirmation constrains tested mechanisms without proving Greedy optimal; shows that snapshot truncation caused empirical prior underprediction; explains why 100% action digest agreement occurred in Study Q3 directional calibration.

---

# 3. Sixteen Common-Confusion Pairs

Examiners frequently design trap questions around subtle conceptual distinctions. Candidates must master these 16 distinctions:

```
+----------------------------------------------------------------------------------------------------+
|                                    16 COMMON-CONFUSION PAIRS                                       |
+----+--------------------------------------------+--------------------------------------------------+
| #  | Term A                                     | Term B                                           |
+----+--------------------------------------------+--------------------------------------------------+
| 1  | List-Order Asking (Baseline G)             | Arrival-Time Asking (G_arr)                      |
| 2  | Date Occurrence                            | Qualified MSMI                                   |
| 3  | Independent Episodes (Naive N = 192)       | Seed Clusters (Correct N = 12)                   |
| 4  | Maximal Matching                           | Maximum Cardinality Matching                     |
| 5  | Low Absolute Brier Score                   | High Calibration / Ranking Skill                 |
| 6  | Exploratory Screening                      | Preregistered Confirmation                       |
| 7  | Family-Wise Error Rate (Holm)              | False Discovery Rate (Benjamini-Hochberg)        |
| 8  | Empirical Prior (emp)                      | Ground-Truth Simulator Prior (sim)               |
| 9  | Needs Clarification                        | Infeasible                                       |
| 10 | Decision Days (0-59)                       | Follow-up Days (60-99)                           |
| 11 | Visible Policy State                       | Privileged Simulator Diagnostics                 |
| 12 | Directional Acceptance Logit Shift         | Terminal Reward Calibration                      |
| 13 | Algorithmic Demographic Bias               | Eligibility Constraint Enforcement               |
| 14 | Served Waiting Distribution                | Population Time-to-Service                       |
| 15 | In-Process Function Execution Time         | Total Container Startup & Transport Time         |
| 16 | Zero-Prediction Baseline Brier             | Prevalence Baseline Brier                        |
+----+--------------------------------------------+--------------------------------------------------+
```

### Detailed Breakdown of the 16 Pairs:

1. **List-Order Asking vs. Arrival-Time Asking:**
   * *List-Order Asking ($G$):* Evaluates members in the public member-list order returned by the simulator.
   * *Arrival-Time Asking ($G_{\text{arr}}$):* Explicitly sorts members by `arrived_day` before selecting query candidates.
2. **Date Occurrence vs. Qualified MSMI:**
   * *Date Occurrence:* A date successfully took place between two members (`date_happened == True`).
   * *Qualified MSMI:* The date occurred within 30 days of introduction **and** both members submitted positive second-meeting intentions within 3 days of the date.
3. **Independent Episodes vs. Seed Clusters:**
   * *Independent Episodes ($N = 192$):* Mistakenly treats 16 conditions on the same seed as independent samples, deflating standard errors.
   * *Seed Clusters ($N = 12$):* Aggregates conditions within each seed into a single difference $D_s$, preserving independent sampling across 12 pseudo-random draws.
4. **Maximal Matching vs. Maximum Cardinality Matching:**
   * *Maximal Matching:* An edge set to which no further edge can be added without violating vertex disjointness (greedy achieves this, competitive ratio $1/2$).
   * *Maximum Cardinality Matching:* The largest possible set of disjoint edges in the graph (requires augmenting path algorithms like Edmonds' Blossom or Hopcroft-Karp).
5. **Low Brier Score vs. High Calibration / Ranking Skill:**
   * *Low Brier Score:* Mean squared error $\approx 0.012$ resulting entirely from the low base rate uncertainty floor $\bar{y}(1-\bar{y})$.
   * *High Calibration / Skill:* A model that accurately differentiates positive and negative outcomes and improves over constant base rate prediction ($\text{BSS} > 0$).
6. **Exploratory Screening vs. Preregistered Confirmation:**
   * *Exploratory Screening:* Retrospective analysis on reused seeds (Q1–Q3, 2,076 records) to generate hypotheses.
   * *Preregistered Confirmation:* Formal prospective trials on untouched holdout seeds (Round 1: 40 seeds; Research 6: 571 seeds) with preregistered protocols and stopping rules.
7. **Family-Wise Error Rate (Holm) vs. False Discovery Rate (Benjamini-Hochberg):**
   * *FWER (Holm):* Bounds the probability of committing even one false positive claim ($P(V \ge 1) \le \alpha$).
   * *FDR (BH):* Bounds the expected proportion of false discoveries among rejected hypotheses ($\mathbb{E}[V / R] \le q^*$).
8. **Empirical Prior (`emp`) vs. Simulator Prior (`sim`):**
   * *Empirical Prior:* Partially fitted from 10 public state snapshots (2,000 members), suffering from day-30 snapshot truncation and fixed structural assumptions.
   * *Simulator Prior:* Parameterized using true generative parameters from the simulator codebase.
9. **Needs Clarification vs. Infeasible:**
   * *Needs Clarification:* Hard constraints are currently unknown (`None`), but no stated constraint has been violated. Can potentially be resolved by asking.
   * *Infeasible:* A hard constraint has been explicitly violated (e.g., age out of bounds, smoking mismatch) or declined, making the edge permanently illegal.
10. **Decision Days (0–59) vs. Follow-up Days (60–99):**
    * *Decision Days:* Days on which the policy queries members and proposes introductions.
    * *Follow-up Days:* Post-assignment simulator horizon where no actions are taken, allowing pending introductions and dates to mature.
11. **Visible Policy State vs. Privileged Diagnostics:**
    * *Visible Policy State:* Public observations passed via stdin JSON (`state['members']`, `state['feedback']`).
    * *Privileged Diagnostics:* Host-side calculations (e.g., `expected_msmi_per_100`) using simulator hidden traits and true probabilities, never exposed to the policy.
12. **Directional Acceptance Logit Shift vs. Terminal Reward Calibration:**
    * *Directional Acceptance Logit Shift:* Scalar offset $\Delta$ applied to the logit of the first-stage acceptance model.
    * *Terminal Reward Calibration:* Probability calibration of the multi-stage compound MSMI event $Q$.
13. **Algorithmic Demographic Bias vs. Eligibility Enforcement:**
    * *Algorithmic Bias:* Unjustified disparate treatment of equally eligible individuals based on protected traits.
    * *Eligibility Enforcement:* Blocking introductions when prerequisite hard compatibility criteria are unverified or declined by the user.
14. **Served Waiting Distribution vs. Population Time-to-Service:**
    * *Served Waiting Distribution:* Time from arrival to first introduction conditioned only on members who received an introduction.
    * *Population Time-to-Service:* Survival distribution across the entire population, including the $64.5\%$ of users who are never served.
15. **In-Process Function Execution Time vs. Total Container Runtime:**
    * *In-Process Function Time:* Time spent inside `decide()` ($< 0.106$ s).
    * *Total Container Runtime:* In-process time plus Docker daemon startup, process spawning, Python interpreter initialization, and JSON IPC serialization ($< 10$ s budget).
16. **Zero-Prediction Baseline Brier vs. Prevalence Baseline Brier:**
    * *Zero-Prediction Baseline:* $\text{BS}_0 = \bar{y} = 0.012378$ (predicts $p_i = 0$ for all pairs).
    * *Prevalence Baseline:* $\text{BS}_{\text{prev}} = \bar{y}(1 - \bar{y}) = 0.012225$ (predicts $p_i = \bar{y}$ for all pairs).

---

# 4. Objective Oral Examination Readiness Checklist

Before entering an oral defense, the candidate must pass the following diagnostic checks:

### Numerical Memory Check (Must-Know Statistics):
- [ ] Round 1 Confirmatory result: $\bar{D} = -0.04167$ MSMI/100, $95\%$ CI $[-0.0911, +0.0077]$, $p = 0.09596$ across 40 seeds.
- [ ] Research 6 Confirmatory result: $\bar{D} = +0.00321$ MSMI/100, $99\%$ CI $[-0.0245, +0.0309]$, $p = 0.76456$ across 571 seeds.
- [ ] Study Q1 Chronological asking ($G_{\text{arr}}$) contrast: $\bar{D} = +0.0990$ MSMI/100, $95\%$ CI $[-0.0701, +0.2680]$, Holm $p = 0.8965$.
- [ ] Study Q1 Greedy baseline: $175$ qualified pairs, $0.4557$ MSMI/100, $4.328$ dates/100, $35.51\%$ coverage.
- [ ] Study Q2 Calibration sample: $5,009$ introductions, $62$ qualified outcomes ($1.2378\%$).
- [ ] Study Q2 Brier scores: zero-prediction $= 0.012378$, prevalence $= 0.012225$, `sim` $= 0.012193$, `emp` $= 0.012250$.
- [ ] Study Q3 Action digest agreement between $X1_{\text{emp}}$ and $X1_{\text{nocal\_emp}}$: $72 / 72$ cells ($100.0\%$).
- [ ] Unserved rate for members declining hard constraints: $100.00\%$.
- [ ] Post-date timing survival probability: $(3/5)^2 = 36\%$.

### Systems & Architecture Check:
- [ ] Production constraints: 10s invocation limit, 2 CPU cores, 1 GiB RAM, 64 MB tmpfs, 2 GiB max image, no GPU/network.
- [ ] Query costs: hard bundle $= 3$ credits, soft field $= 1$ credit, daily budget $= 12$ credits.
- [ ] Exact reproduction command: `.venv/bin/python final_report/build_assets.py`.
- [ ] Unit test validation: all 22 tests pass in `test_kit`, `test_runner`, and `test_release`.

---

# 5. Defense Emergency Scripts

### Emergency Script 1: When Stumped on an Obscure Parameter or Law
> *"While I do not have that specific generative hyperparameter memorized, I can locate it immediately in [`kit.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/kit.py) or [`laws.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research9/round2/laws.py). What is essential from an architectural perspective is that the policy receives observations through the public JSON schema and never conditions on simulator ground truth. The parameter in question governs the synthetic data generator, not the policy logic."*

### Emergency Script 2: When an Examiner Asserts Your Correction is "Too Conservative"
> *"Our seed-cluster correction is not conservative; it is mathematically design-consistent. The experimental protocol repeatedly ran 16 laws across the exact same 12 seeds. Because member populations within a seed are identical, episode errors have an intracluster correlation of roughly 37%. Treating them as independent observations deflates standard errors by a factor of 2.5 and violates Gauss-Markov assumptions. Reporting an unclustered $p = 0.001$ would be statistical malpractice; reporting the cluster-adjusted interval $[-0.070, +0.268]$ accurately reflects experimental uncertainty."*

### Emergency Script 3: When Asked About Unexecuted Laws or Out-of-Scope Extensions
> *"That law is defined in the source registry but was not part of the 20 executed laws in the supplemental grid. Under our provenance protocol, we strictly report what was verified in recorded data rather than extrapolating. Answering that question definitively would require new pre-registered simulation runs rather than post-hoc speculation."*
