# Mock Oral Examinations & Defense Grading Rubrics

This guide contains three complete, rigorous oral mock examinations designed to simulate high-stakes defenses of the Sequential Reciprocal Matching benchmark.
* **Mock Exam 1:** Conceptual Foundations & Problem Formulation
* **Mock Exam 2:** Algorithmic Architecture, Code Tracing & Statistical Derivation
* **Mock Exam 3:** Skeptical Committee Defense & Adversarial Interrogation

Each examination includes realistic examiner prompts, structured time allocations, comprehensive model answers, detailed point-by-point rubrics, common deduction penalties, and pass/fail thresholds.

---

# Mock Examination 1: Conceptual Foundations & Problem Formulation

* **Target Audience:** Master's / Ph.D. Level Oral Qualifying Exam
* **Focus Areas:** Problem boundary, information hiding, feedback timeline, metric denominators, hard vs. soft constraints, and outcome funnel mechanics.
* **Format:** 45-minute oral examination (5 questions, 20 points each, 100 points total).
* **Passing Threshold:** 75 points (Distinction: $\ge 92$ points).

---

### Question 1.1: Information Boundary and Privileged Simulator Data (20 Points)
**Examiner Prompt:**
> *"Walk us through the exact information boundary between the simulator host and the deployed matching policy. What information is strictly visible to the policy during decision steps, what information is permanently concealed, and what would happen if a candidate policy attempted to access simulator internals?"*

**Model Answer:**
The benchmark enforces a strict architectural boundary between host simulator state and policy visibility:
1. **Visible State (`state` dictionary):**
   * Member demographic attributes disclosed upon arrival: `member_id`, `pool_id`, `age`, `gender`, `zone`, `arrived_day`.
   * Observed profile fields: dictionary of hard and soft attributes where `field_status == 'observed'`.
   * Availability indicator: boolean `available` computed by the simulator (checking arrival, exit, busy lockout, and mutual interest pauses).
   * Daily query budget: integer `ask_budget_remaining` (12 credits daily).
   * Historical public logs: introductions history (`state['introductions']`), released feedback events (`state['feedback']`), and query log (`state['ask_log']`).
   * Serialized stateful memory: persistent `memory` dictionary passed between invocations.
2. **Concealed (Privileged) Simulator State:**
   * Ground-truth member traits (`truth` dictionary), including latent smoking, children preferences, and soft traits before querying.
   * Synthetic personal biases (`bias`, `second_bias`) and response propensities (`response_rate`).
   * World pseudo-random seed and PRNG state.
   * Future arrival schedules (who arrives on days $t+1 \dots 59$) and exit dates (`exit_day`).
   * Future outcome realisations and unobserved pending events.
3. **Privileged Diagnostics vs. Production Policy:**
   * In supplemental studies, the host computes "expected MSMI" diagnostics using simulator truth. These diagnostics are privileged host-side monitors and are never passed to the policy or treated as primary outcomes.
   * Attempting to access private state or read environment files violates the data contract, invalidates evaluation, and fails automated audits.

**Scoring Rubric (20 Points):**
* **5 pts:** Correctly lists all public state fields (including availability, ask budget, and serialized memory).
* **5 pts:** Accurately lists concealed simulator variables (traits, biases, seed, arrival queues, exit dates).
* **5 pts:** Clearly explains the role of host-side expected reward diagnostics and why they cannot be policy inputs.
* **5 pts:** Articulates the consequence of boundary violations under the data contract.
* **Deductions:** $-5$ if candidate claims policies receive true match probabilities; $-3$ if candidate confuses public member list with future arrival queue.

---

### Question 1.2: Feedback Maturation and the 40-Day Follow-Up Horizon (20 Points)
**Examiner Prompt:**
> *"The problem horizon specifies 60 decision days (days 0–59) followed by 40 follow-up days (days 60–99). Why are follow-up days necessary? Does the policy make matching decisions on day 65? What happens to an introduction assigned on day 59 whose second-meeting feedback arrives on day 78?"*

**Model Answer:**
1. **Role of Follow-Up Days:**
   Reciprocal matching involves multi-stage physical and behavioral delays: initial introduction response (up to 7 days), date scheduling and occurrence (up to 14–26 days), and post-date intention feedback (up to 5 days). Introductions formed in the latter half of the decision horizon (e.g., days 45–59) cannot complete this funnel before day 59. The 40 follow-up days allow all assigned interactions to mature naturally without arbitrary right-censoring.
2. **Policy Inactivity During Follow-Up:**
   The policy is active **only** during decision days $0 \dots 59$. On days $60 \dots 99$, no questions are asked and no introductions are formed. The simulator runs empty steps (`sim.advance([])`) solely to advance internal clocks and resolve pending feedback events.
3. **Fate of Day 59 Introduction Assigned:**
   An introduction formed on day 59 whose second-meeting feedback completes on day 78 is fully evaluated. If the date occurred within 30 days of introduction ($d - 59 \le 30$) and both post-date responses arrived within 3 days of the date ($\tau - d \le 3$) with positive intentions, it is counted as a **qualified MSMI outcome**. Day 59 is the assignment cutoff, not the feedback deadline.

**Scoring Rubric (20 Points):**
* **7 pts:** Explains behavioral delay mechanics and why 40 follow-up days prevent end-of-horizon censoring.
* **6 pts:** Explicitly confirms that the policy is executed only on days 0–59, with empty batches thereafter.
* **7 pts:** Traces the day 59 introduction through day 78 and correctly applies the 30-day date qualification rule.
* **Deductions:** $-7$ if candidate claims matching decisions continue during follow-up days; $-5$ if candidate claims day 59 introductions are truncated or lost.

---

### Question 1.3: Denominators and Metric Formulations (20 Points)
**Examiner Prompt:**
> *"State the precise mathematical definition of the primary benchmark metric MSMI/100. Explain its denominator. Why does the benchmark use arrived members rather than introduced members or initial pool size? Does a successful couple count as 1 or 2 in the numerator?"*

**Model Answer:**
1. **Mathematical Definition:**
   For an episode, let $\mathcal{M}_{\text{intro}}$ be the set of assigned introductions. For each introduction $k$, let:
   $$Q_k = \mathbf{1}\left\{ \text{date occurred}, \; d_k - t_k \le 30, \; y_{a, k} = \text{yes}, \; y_{b, k} = \text{yes}, \; \tau_{a, k} - d_k \le 3, \; \tau_{b, k} - d_k \le 3 \right\}$$
   The primary metric is:
   $$\text{MSMI/100} = 100 \times \frac{\sum_{k \in \mathcal{M}_{\text{intro}}} Q_k}{N_{\text{arrived}}}$$
2. **Numerator Convention:**
   One successful introduction counts as **one qualified pair** ($Q = 1$), not two individuals. A policy producing 21 qualified pairs among 200 arrived members achieves $\text{MSMI/100} = 100 \times (21 / 200) = 10.50$ (or in our benchmark scale, $0.35$ to $0.55$ per 100 members under realistic multi-episode averages).
3. **Denominator Justification:**
   * $N_{\text{arrived}}$ is the total number of distinct members who arrived in the pool on or before day 59 ($N = 200$ across standard benchmark episodes).
   * Using **introduced members** in the denominator would create perverse incentives: a policy could match exactly one cherry-picked couple, achieve $Q=1$, and claim a $100\%$ success rate while abandoning the remaining 198 users.
   * Using **initial pool size** would fail under changing arrival laws (e.g., arrival waves where members enter sequentially). Arrived members captures the entire eligible human population entrusted to the system.

**Scoring Rubric (20 Points):**
* **6 pts:** Precise formula for $Q$ and MSMI/100 including the $\times 100$ scaling factor.
* **6 pts:** Explicit clarification that numerator counts pairs, not double-counting two individuals.
* **8 pts:** Methodological defense of the arrived-members denominator against served-only conditioning and initial-pool distortion.
* **Deductions:** $-6$ if candidate double-counts pairs as two members; $-5$ if candidate suggests using served members as denominator.

---

### Question 1.4: Hard Constraints vs. Soft Preferences (20 Points)
**Examiner Prompt:**
> *"How does the system distinguish hard constraints from soft preferences? Can high soft compatibility compensate for an unresolved or violating hard constraint? What happens if a user declines a question about a hard constraint?"*

**Model Answer:**
1. **Hard Constraints (Eligibility Boundaries):**
   * Encompass age boundaries (`age_min`, `age_max`), sexual orientation / gender preferences (`who_to_meet`), geographic zones (`acceptable_zones`), relationship structure (`monogamous` vs. `non_monogamous`), smoking tolerances, children status/plans, and schedules.
   * Hard constraints define **absolute legal and reciprocal feasibility**: a pair is feasible if and only if both parties mutually satisfy all hard criteria.
   * **Incomplete Information Blocks Feasibility:** If any hard constraint remains unresolved (`None`), the pair has status `needs_clarification` and cannot be introduced.
2. **Soft Preferences (Compatibility Scoring):**
   * Encompass relationship goal, pace, lifestyle, conversation style, emotional availability, space for relationship, and relocation openness.
   * Soft attributes are used exclusively for **ranking and tie-breaking** among already-feasible pairs.
3. **No Overrides Permitted:**
   * Soft compatibility scores **never** override a hard constraint violation or unverified field. A pair with perfect 7/7 soft trait alignment cannot be introduced if one party's smoking tolerance is unknown.
4. **Handling Declined Questions:**
   * When a user declines a hard field, `field_status` is marked `'declined'`.
   * The simulator never silently imputes or guesses declined fields.
   * Because the field can never be verified, any edge requiring this information remains permanently infeasible. In `subgroups_q1_greedy.csv`, $100.0\%$ of users who declined a hard field were never introduced.

**Scoring Rubric (20 Points):**
* **5 pts:** Accurately distinguishes hard eligibility from soft ranking.
* **5 pts:** Explicitly states that missing hard data blocks feasibility (`needs_clarification`).
* **5 pts:** Clearly states that soft compatibility cannot override missing or violating hard constraints.
* **5 pts:** Correctly explains that declined fields are never imputed and result in permanent ineligibility.
* **Deductions:** $-5$ if candidate suggests imputing missing hard constraints; $-4$ if candidate claims soft score can overcome missing hard values.

---

### Question 1.5: The Five-Stage Qualification Funnel (20 Points)
**Examiner Prompt:**
> *"Describe the stages an introduction must survive to become a qualified outcome. Why does date occurrence fail to guarantee MSMI? Under standard delay laws, what proportion of mutually interested pairs fail qualification due to timing delays alone?"*

**Model Answer:**
1. **Five-Stage Attrition Funnel:**
   * **Stage 1: Introduction Assignment:** Legal, non-overlapping feasible pair introduced on day $t$.
   * **Stage 2: Mutual Acceptance:** Both members respond within 7 days, and both submit `'yes'`. (Converts introduction to mutual match; introduces 8-day busy pause).
   * **Stage 3: Date Occurrence:** Date is scheduled and successfully occurs ($P = 0.78$ under standard law).
   * **Stage 4: 30-Day Date Horizon:** Date must take place within 30 days of assignment ($d - t \le 30$).
   * **Stage 5: Mutual Timely Second-Meeting Intention:** Both members must respond to post-date survey, both must answer `'yes'`, and **both responses must occur within 3 days of the date** ($\tau_a - d \le 3$ and $\tau_b - d \le 3$).
2. **Why Date Occurrence Does Not Guarantee MSMI:**
   * A date can occur, but one or both members may decline a second meeting ($y = \text{no}$).
   * A member may fail to respond to the post-date questionnaire (`no_response`).
   * The date may occur late ($d - t > 30$).
   * Responses may arrive late ($\tau - d > 3$).
3. **Timing Attrition Calculation:**
   * Under standard generator rules, post-date response delay is drawn from $\text{Uniform}(\{1, 2, 3, 4, 5\})$.
   * The probability that a single member responds on time is $3/5 = 0.60$.
   * Assuming conditional independence of delays:
     $$P(\text{Both On-Time} \mid \text{Date Occurred}) = \left(\frac{3}{5}\right)^2 = \frac{9}{25} = 0.36 \quad (36\%)$$
   * Therefore, **$64\%$** ($1 - 0.36$) of otherwise successful second-meeting pairs are eliminated purely by the 3-day feedback deadline!

**Scoring Rubric (20 Points):**
* **6 pts:** Outlines all five funnel stages in correct sequential order.
* **6 pts:** Details the exact failure modes post-date (declines, non-response, $>30$ day delay, $>3$ day response).
* **8 pts:** Correct mathematical derivation of the $(3/5)^2 = 36\%$ survival factor and $64\%$ attrition rate.
* **Deductions:** $-6$ if candidate fails to identify the 3-day post-date deadline; $-4$ if candidate fails to square the individual probability for two participants.

---
---

# Mock Examination 2: Algorithmic Architecture, Code Tracing & Statistical Derivation

* **Target Audience:** Technical Staff / Quantitative Systems Defense
* **Focus Areas:** Execution of `kit.py` and `policy.py`, seed-cluster variance derivation, Holm multiplicity corrections, calibration mechanics, empirical prior fitting, and reproducibility.
* **Format:** 45-minute oral examination (5 questions, 20 points each, 100 points total).
* **Passing Threshold:** 75 points (Distinction: $\ge 92$ points).

---

### Question 2.1: Code Trace: Greedy Asking and Matching Execution (20 Points)
**Examiner Prompt:**
> *"Trace line-by-line how `baseline_asks` and `baseline_match` in `kit.py` operate on day $t$. In what order are members queried? How does the budget constrain asking? How are pairs sorted and matched, and how is the matching guarantee characterized in graph theory?"*

**Model Answer:**
1. **`baseline_asks(state)` Execution:**
   * Filters available members in `state['members']`: must have `available == True`, have at least one unresolved hard constraint (`fields[k] is None`), and have no declined hard fields (`field_status[k] != 'declined'`).
   * Evaluates candidates in their existing **public member-list order** (which is list order from the simulator, distinct from sorted arrival time).
   * Computes available bundle capacity: `state['ask_budget_remaining'] // 3` (at most $12 // 3 = 4$ bundles).
   * Returns a list of query requests: `[{'member_id': m['member_id'], 'field': 'constraints'}, ...]`.
2. **`baseline_match(state)` Execution:**
   * Collects all currently available members.
   * Builds history set `past` containing sorted tuples `(user_a, user_b)` from past introductions to prevent repeat matches.
   * Enumerates all combinations `itertools.combinations(members, 2)`.
   * For each pair, verifies `key not in past` and checks `eligibility(a, b)['status'] == 'feasible'`.
   * Scores each feasible pair: counts matching observed soft fields:
     $$\text{score} = \sum_{k \in \text{SOFT}} \mathbf{1}\{a[k] \text{ is not None and } a[k] == b[k]\}$$
   * Appends `(-score, key)` to `edges` list, allowing standard ascending sort to order by descending score.
   * Executes greedy edge selection: iterates through sorted edges; if neither endpoint is in `used`, adds pair to output and updates `used`.
3. **Graph-Theoretic Characterization:**
   * This algorithm produces a **greedy maximal matching** on the feasible subgraph.
   * It is **not** a maximum cardinality matching, maximum weight matching, or optimal dynamic matching. It guarantees only that no additional edge can be added without violating the 1-matching constraint.

**Scoring Rubric (20 Points):**
* **6 pts:** Step-by-step trace of `baseline_asks` (filtering criteria, budget division `// 3`, list ordering).
* **7 pts:** Step-by-step trace of `baseline_match` (combination enumeration, eligibility check, soft scoring, `-score` sorting, `used` set tracking).
* **7 pts:** Precise graph-theoretic classification (greedy maximal matching) and explicit distinction from maximum cardinality / optimal dynamic matching.
* **Deductions:** $-5$ if candidate claims `baseline_match` finds maximum cardinality; $-4$ if candidate confuses list-order asking with explicit arrival-time sorting.

---

### Question 2.2: Statistical Derivation: Clustered Contrasts vs. Naive Analysis (20 Points)
**Examiner Prompt:**
> *"Why is an ordinary two-sample t-test or pooled paired t-test across all 192 episodes in Study Q1 invalid? Write down the formula for the seed-cluster contrast $D_s$ and explain how the standard error and degrees of freedom are calculated."*

**Model Answer:**
1. **Invalidity of Pooled Analysis:**
   In Study Q1, 192 episodes per arm are constructed by crossing 12 seeds with 16 experimental laws. The same 12 seeds are reused across all laws. Episodes sharing the same seed cluster have identical member pools, leading to strong positive intracluster correlation ($\rho \approx 37\%$). Treating 192 rows as independent observations violates independent sampling, deflates standard errors by over $2.5\times$, and spuriously claims $df = 191$.
2. **Seed-Cluster Formulation:**
   For candidate arm $a$ and baseline $G$, the within-seed mean difference across the set of executed laws $\mathcal{L}$ ($|\mathcal{L}| = 16$) is:
   $$D_s = \frac{1}{|\mathcal{L}|} \sum_{\ell \in \mathcal{L}} \left( Y_{s\ell a} - Y_{s\ell G} \right)$$
   This collapses the 16 correlated measurements into a single independent cluster difference $D_s$ for each of the $n = 12$ seeds.
3. **Standard Error and Inference:**
   The sample mean contrast is $\bar{D} = \frac{1}{n}\sum_{s=1}^n D_s$.
   Sample standard deviation: $s_D = \sqrt{\frac{1}{n-1}\sum_{s=1}^n (D_s - \bar{D})^2}$.
   Cluster standard error:
   $$\text{SE}(\bar{D}) = \frac{s_D}{\sqrt{n}} = \frac{s_D}{\sqrt{12}}$$
   Inference uses Student-$t$ distribution with $df = n - 1 = 11$ degrees of freedom. For $\alpha = 0.05$, $t_{0.975, 11} = 2.200985$.
   For $G_{\text{arr}}$ vs. $G$: $\bar{D} = +0.0990$, $\text{SE} = 0.0768$, yielding $95\% \text{ CI} = [-0.0701, +0.2680]$ and $p = 0.2241$.

**Scoring Rubric (20 Points):**
* **6 pts:** Explains why repeated measures on 12 seeds create positive ICC and invalidate naive tests.
* **6 pts:** Exact formula for cluster difference $D_s$ averaging across all $|\mathcal{L}|$ laws within seed.
* **8 pts:** Correct standard error formula, identification of $df = 11$, and quotation of the correct interval $[-0.0701, +0.2680]$.
* **Deductions:** $-6$ if candidate claims $df = 191$; $-5$ if candidate cannot write the cluster mean formula.

---

### Question 2.3: Multiplicity Adjustment: Step-Down Holm Execution (20 Points)
**Examiner Prompt:**
> *"Walk us through the exact Holm step-down adjustment applied to the five candidate arms tested against G in Study Q1. Why does the procedure require a cumulative maximum constraint?"*

**Model Answer:**
1. **Holm Algorithm Mechanics:**
   Sort the $k = 5$ raw two-sided $p$-values in ascending order:
   * Rank 1 ($P$): $p = 0.114632 \implies \text{Multiplier} = 5 \implies 5 \times 0.114632 = 0.573161$.
   * Rank 2 ($G_{\text{arr}}$): $p = 0.224119 \implies \text{Multiplier} = 4 \implies 4 \times 0.224119 = 0.896475$.
   * Rank 3 ($G_{\text{deg}}$): $p = 0.407552 \implies \text{Multiplier} = 3 \implies 3 \times 0.407552 = 1.222656 \to 1.000000$.
   * Rank 4 ($Q6$): $p = 0.509494 \implies \text{Multiplier} = 2 \implies 2 \times 0.509494 = 1.018988 \to 1.000000$.
   * Rank 5 ($G_{\text{lifo}}$): $p = 0.955471 \implies \text{Multiplier} = 1 \implies 1 \times 0.955471 = 0.955471$.
2. **The Cumulative Maximum Constraint:**
   * Step-down hypothesis testing requires that rejecting hypothesis $i$ is contingent on rejecting all preceding hypotheses $j < i$. Adjusted $p$-values must therefore be monotonically non-decreasing: $p_{(1)}^{\text{adj}} \le p_{(2)}^{\text{adj}} \le \dots \le p_{(k)}^{\text{adj}}$.
   * For Rank 5 ($G_{\text{lifo}}$), the unconstrained product is $0.955471$, which is *less* than Rank 3 and 4 ($1.000000$).
   * Applying the cumulative maximum:
     $$p_{(5)}^{\text{adj}} = \max\left( p_{(4)}^{\text{adj}}, \; 0.955471 \right) = \max(1.000000, 0.955471) = 1.000000$$
   * Final Holm adjusted $p$-values: $P: 0.5732, \; G_{\text{arr}}: 0.8965, \; G_{\text{deg}}: 1.000, \; Q6: 1.000, \; G_{\text{lifo}}: 1.000$.

**Scoring Rubric (20 Points):**
* **6 pts:** Accurately states the sorting and multiplier formula $(k - i + 1) \cdot p_{(i)}$.
* **7 pts:** Correct numerical calculation across the 5 arms in Study Q1.
* **7 pts:** Clear explanation of why the cumulative maximum constraint is mathematically mandatory to preserve logical monotonicity.
* **Deductions:** $-6$ if candidate reports $0.955$ for $G_{\text{lifo}}$ without applying the cumulative maximum; $-4$ if candidate confuses Holm with Hochberg or Bonferroni.

---

### Question 2.4: Probability Calibration and the Brier Score Skill Floor (20 Points)
**Examiner Prompt:**
> *"In Study Q2, the Brier score of the empirical prior model is 0.012250, while the simulator prior is 0.012193. Contrast these with the zero-prediction and prevalence baselines. Why does a low Brier score fail to prove model utility?"*

**Model Answer:**
1. **Benchmark Brier Score Values on 5,009 Identical G-Selected Edges:**
   * Always-zero predictor ($p_i = 0$): $\text{BS}_0 = \bar{y} = 62 / 5009 = \mathbf{0.012378}$.
   * Same-sample prevalence predictor ($p_i = \bar{y}$): $\text{BS}_{\text{prev}} = \bar{y}(1 - \bar{y}) = \mathbf{0.012225}$.
   * Simulator-informed prior (`sim`): $\text{BS}_{\text{sim}} = \mathbf{0.012193}$.
   * Empirical observable-fit prior (`emp`): $\text{BS}_{\text{emp}} = \mathbf{0.012250}$.
2. **Comparison with Baselines:**
   * Both complex prior models achieve Brier scores within $0.0002$ of the trivial zero-prediction baseline.
   * Crucially, the empirical prior model's Brier score ($0.012250$) is **worse** than simply predicting the constant sample prevalence ($0.012225$).
3. **Why Low Brier Score Does Not Imply Model Utility:**
   Under severe class imbalance ($1.238\%$ positive rate), the Brier score is dominated by the base rate uncertainty $\bar{y}(1-\bar{y}) \approx 0.0122$. Even an uninformative or biased model that predicts near zero achieves a Brier score below $0.013$.
   Moreover, `emp` severely underpredicts the base rate (mean prediction $0.5897\%$ vs. actual $1.2378\%$, signed error $-0.6481$ pp) due to day-30 snapshot censoring. A low MSE is a mathematical artifact of rare events, not evidence of ranking or decision skill.

**Scoring Rubric (20 Points):**
* **6 pts:** Cites the baseline Brier values ($\text{BS}_0 = \bar{y}$ and $\text{BS}_{\text{prev}} = \bar{y}(1-\bar{y})$).
* **7 pts:** Demonstrates that `emp` is worse than the trivial constant-prevalence baseline.
* **7 pts:** Explains why severe class imbalance makes raw Brier scores misleading without skill score decomposition.
* **Deductions:** $-6$ if candidate fails to recognize that predicting zero yields $\text{BS} = 0.012378$; $-4$ if candidate equates low Brier score with good calibration.

---

### Question 2.5: Provenance, Audit Scope, and Reproducibility Limitations (20 Points)
**Examiner Prompt:**
> *"What checks pass in `provenance.json` and `build_assets.py` for the 2,076 supplemental records, and what limitations are explicitly acknowledged regarding experiment provenance and sandbox validation?"*

**Model Answer:**
1. **Checks That Pass:**
   * Complete declared grids: exactly 1,152 Q1 cells, 420 Q2 cells, 504 Q3 cells ($2,076$ total records, $1,968$ unique cells).
   * Valid status: all records show `valid == True` and `error is None`.
   * World hash agreement: across all arms within a (seed, law) cell, `world_sha256` is identical.
   * Identical asking controls: all arms using baseline asking (including all 504 Q3 cells) have identical `ask_log_sha256` digests.
   * Internal arithmetic consistency: member totals ($200$), assignment sums, coverage fractions, ask cost arithmetic ($3 \times \text{hard} + \text{soft}$), and expected value sums match perfectly.
2. **Explicit Limitations and Gaps Acknowledged:**
   * **No Contemporaneous Registration:** Q1–Q3 files lack contemporaneous freshness certificates or pre-experiment registration; they are retrospective descriptive evidence, not untouched confirmation.
   * **No Full Event Ledger:** Saved records do not include an immutable, fine-grained event ledger; public events were not independently reconstructed from scratch.
   * **Host RSS Monitoring Unverified:** The launcher capped worker counts but did not implement host RSS monitoring; compliance with the 8 GiB RAM monitor cannot be inferred.
   * **Unavailable Container Check:** During report preparation, the Docker daemon could not be reached; fresh containerized execution, sandbox isolation, and image size limits were not verified.

**Scoring Rubric (20 Points):**
* **8 pts:** Details the specific integrity checks that pass (world hash, ask log digest, grid completeness, arithmetic).
* **6 pts:** Accurately distinguishes between exploratory descriptive records and registered confirmation.
* **6 pts:** Discloses the four key provenance gaps (no pre-registration, no event ledger, unverified host RSS, unavailable Docker daemon).
* **Deductions:** $-6$ if candidate claims the supplemental runs were preregistered confirmation; $-5$ if candidate falsely claims Docker container checks passed.

---
---

# Mock Examination 3: Skeptical Committee Defense & Adversarial Interrogation

* **Target Audience:** Executive Defense / Faculty Review Committee
* **Focus Areas:** Defending negative results, refuting FIFO superiority claims, explaining learned screen failure, handling demographic access disparities, and justifying production policy retention.
* **Format:** 45-minute oral examination (5 questions, 20 points each, 100 points total).
* **Passing Threshold:** 75 points (Distinction: $\ge 92$ points).

---

### Question 3.1: Adversarial Challenge: "Why Keep Greedy Over FIFO?" (20 Points)
**Examiner Prompt:**
> *"In Study Q1, chronological asking ($G_{\text{arr}}$) achieved +0.0990 MSMI/100, which is over 20% higher than Greedy. In Round 1, your team submitted simple_fifo. Why are you abandoning FIFO in Round 2 and sticking with Greedy? Isn't this an overly conservative failure of ambition?"*

**Model Answer:**
1. **Exploratory Uncertainty vs. Confirmatory Truth:**
   The $+0.0990$ point difference is an exploratory result across 12 shared seed clusters. Under seed-cluster analysis, the $95\%$ confidence interval is $[-0.0701, \; +0.2680]$ with a Holm-adjusted $p$-value of $0.8965$. This interval includes zero and allows for substantial negative harm (down to $-0.07$ MSMI/100). Promoting an algorithm based on an unconfirmed exploratory point estimate violates engineering discipline.
2. **Confirmatory Failure of `simple_fifo` in Round 1:**
   When subjected to a registered 40-seed confirmatory trial in Round 1, `simple_fifo` failed to beat Greedy: difference $-0.0417$ MSMI/100, $95\%$ CI $[-0.0911, +0.0077]$, $p = 0.096$. The narrative that FIFO is superior was already tested and failed.
3. **Disproving the Mechanistic Hypothesis:**
   Advocates claimed FIFO wins by reducing user waiting. The empirical evidence directly refutes this: in Study Q1, $G_{\text{arr}}$ had a *higher* mean served wait ($6.81$ days) than Greedy ($6.66$ days) and an identical unserved fraction ($64.4\%$).
4. **List-Order FIFO vs. Arrival FIFO:**
   The baseline Greedy policy already uses list-order asking. Sorting strictly by arrival time adds complexity without confirmed statistical benefit. Retaining Greedy is the only decision supported by rigorous empirical evidence.

**Scoring Rubric (20 Points):**
* **6 pts:** Directly quotes the cluster-adjusted confidence interval $[-0.0701, +0.2680]$ and Holm $p = 0.8965$.
* **5 pts:** Cites the negative Round 1 confirmatory trial results for `simple_fifo`.
* **5 pts:** Refutes the waiting-time mechanism using Study Q1 waiting statistics ($6.81$ vs. $6.66$ days).
* **4 pts:** Distinguishes baseline list-order asking from arrival-time sorting.
* **Deductions:** $-6$ if candidate defends $G_{\text{arr}}$ as superior; $-5$ if candidate cites naive confidence intervals ($[+0.040, +0.158]$).

---

### Question 3.2: Adversarial Challenge: "Why Did the Learned Campaign Fail?" (20 Points)
**Examiner Prompt:**
> *"You trained machine learning models on over 216,000 historical introductions, yet your final report retains a heuristic greedy matcher. Why did modern machine learning fail so completely? Did you overfit, or was the model architecture inadequate?"*

**Model Answer:**
1. **The Registered Admission Gate:**
   The final learned campaign enforced a registered probability calibration admission gate: candidate models were required to demonstrate reliable calibration on validation data before being admitted to policy evaluation. The selected funnel model failed this gate, excluding continuation-value planners from execution.
2. **The 288-Cell Audited Development Screen:**
   Even when ranking-only variants (learned greedy, soft-query, and local repair) were permitted to compete in the 288-cell development screen across 8 development groups:
   * Greedy ($G$) achieved **$0.3229$ MSMI/100** (31 qualified pairs).
   * Learned Greedy achieved **$0.1875$ MSMI/100** (18 qualified pairs).
   * Learned Soft-Query achieved **$0.2188$ MSMI/100** (21 qualified pairs).
   * Learned Repair achieved **$0.2188$ MSMI/100** (21 qualified pairs).
   Every learned candidate performed substantially *worse* than baseline Greedy.
3. **Root Causes of Failure:**
   * **Extreme Class Imbalance:** A $1.2\%$ base rate provides an extremely sparse reward signal. Models fit to historical introductions struggled with high label noise.
   * **Distribution Shift Under Policy Execution:** In an MDP, changing the matching policy alters the state distribution of available members. Supervised learning on historical logs suffers from compounding policy covariate shift.
   * **Sparse Feasible Graphs:** Because hard constraints eliminate the vast majority of edges, the feasible graph on any given day is very sparse. Sophisticated soft reranking has minimal room to operate when only 1 or 2 edges are legally feasible.

**Scoring Rubric (20 Points):**
* **6 pts:** Explains the registered calibration admission gate and why continuation models were barred.
* **7 pts:** Cites the exact 288-cell screen results showing all learned models trailed Greedy ($0.188$–$0.219$ vs. $0.323$).
* **7 pts:** Identifies technical root causes (label sparsity, covariate shift under sequential policy execution, sparse feasible graphs).
* **Deductions:** $-6$ if candidate claims machine learning won; $-4$ if candidate fails to mention the sparse reward signal ($1.2\%$).

---

### Question 3.3: Adversarial Challenge: "Inaction of Directional Calibration" (20 Points)
**Examiner Prompt:**
> *"In Study Q3, you introduced a directional calibration mechanism for drift adaptation, yet your report reveals that removing calibration left all 72 action digests completely identical. Why did your calibration code do nothing, and why should anyone take this research seriously?"*

**Model Answer:**
1. **Acknowledgment of the Empirical Finding:**
   Across all 72 episodes in Study Q3, comparing $X1_{\text{emp}}$ (with directional calibration) and $X1_{\text{nocal\_emp}}$ (without calibration) produced **$100\%$ action digest identity** (`action_sha256`), with both variants executing the exact same introductions and achieving 64 qualified pairs.
2. **Algorithmic Reason 1: Monotonicity Under Common Scalar Offset:**
   The directional calibration mechanism computes a scalar logit offset $\Delta_{\text{applied}}$ and adds it to the acceptance logit. Because the logistic function $\sigma(z + \Delta)$ is strictly monotonically increasing in $z$, adding a common scalar offset shifts the absolute probability levels but leaves the **relative ranking of edges unchanged**.
3. **Algorithmic Reason 2: Greedy Matching Without Reservation Threshold:**
   If the policy employed a dynamic reservation threshold (e.g., only match if $P(Q=1) \ge \theta_{\text{reserve}}$), probability scaling would trigger or inhibit matches. However, $X_1$ uses greedy matching to fill disjoint edges without a threshold. Because the ranking was preserved and the feasible candidate pool was identical (governed by the same asking log), the exact same greedy edge was chosen on every single day.
4. **Research Value:**
   This negative finding is deeply informative: it proves that in threshold-free greedy matching, calibrating output probabilities provides **zero operational benefit**. Development resources should not be wasted on complex online recalibration unless the allocator uses an explicit reservation threshold.

**Scoring Rubric (20 Points):**
* **6 pts:** Explicitly acknowledges the 100% action digest identity across all 72 cells.
* **7 pts:** Explains why monotonic scalar logit shifts preserve edge rankings.
* **7 pts:** Demonstrates that threshold-free greedy matching selects identical edges regardless of probability scale, and articulates the architectural takeaway.
* **Deductions:** $-6$ if candidate claims calibration altered match choices; $-4$ if candidate cannot explain why ranking remained unchanged.

---

### Question 3.4: Adversarial Challenge: "Demographic Disparity and Bias" (20 Points)
**Examiner Prompt:**
> *"In your subgroup analysis, members who declined hard questions had a 100% unserved rate, and members with incomplete profiles were unserved at a 77.8% rate compared to 47.1% for complete profiles. Is your system biased against users with privacy concerns or incomplete profiles?"*

**Model Answer:**
1. **Consent and Eligibility vs. Algorithmic Bias:**
   Under the benchmark data contract, hard constraints represent non-negotiable legal and personal compatibility criteria: mutual age limits, geographic travel feasibility, relationship structure, and children plans. The system is legally and ethically bound never to introduce a pair without mutual eligibility verification.
2. **Permanent Infeasibility of Declined Fields:**
   When a user declines a hard question, `field_status` becomes `'declined'`. The simulator forbids guessing or imputing declined data. Because mutual feasibility cannot be verified, the member has zero feasible edges in the pool. The $100\%$ unserved rate is not algorithmic bias; it is the correct enforcement of user refusal to provide prerequisite eligibility data.
3. **Incomplete Profiles at Arrival:**
   Members arriving with incomplete profiles must wait for query budget allocation ($4$ bundles daily across the pool) to become verified. While they wait, potential partners may exit or be matched elsewhere. This structural latency accounts for the $77.8\%$ unserved rate.
4. **Fairness Limitations in the Report:**
   The report explicitly disclaims demographic fairness: aggregate parity across genders ($64.7\%$ men vs. $64.5\%$ women unserved) does not guarantee conditional equality of opportunity or intersectional fairness. However, the disparities driven by information completeness reflect the fundamental trade-off between privacy and match eligibility in reciprocal markets.

**Scoring Rubric (20 Points):**
* **6 pts:** Defends the non-negotiable status of hard constraints under the data contract.
* **7 pts:** Explains that declined fields cause permanent ineligibility rather than algorithmic bias.
* **7 pts:** Explains the operational latency of verifying incomplete profiles under the 4-bundle daily budget, while acknowledging report fairness limitations.
* **Deductions:** $-6$ if candidate suggests imputing declined fields to improve equity; $-4$ if candidate claims the report proves demographic fairness.

---

### Question 3.5: Adversarial Challenge: "Reproducibility and Docker Failure" (20 Points)
**Examiner Prompt:**
> *"Your report states that a restricted Docker container check was 'unavailable' because the Docker daemon could not be reached. How can an evaluation committee accept a submission that hasn't even verified its Docker container?"*

**Model Answer:**
1. **Transparent Disclosure Over False Claims:**
   Scientific integrity requires reporting exact execution realities. The Docker daemon was unavailable in the specific host environment during final report asset compilation. Rather than fabricating a passed container check or claiming unverified sandbox isolation, the report transparently discloses this as a pending submission check in Section 13.
2. **Alternative Validation Performed:**
   * **Unit Test Suite:** All 22 test cases in `test_kit`, `test_runner`, and `test_release` passed cleanly.
   * **Public Data Verification:** `verify_data.py` validated all 71 data files, 2,000 members, 613 introductions, and 1,270 feedback events.
   * **Analysis Code Verification:** An independent code review verified cluster contrast calculations, Holm multiplicity adjustments, and Brier decompositions.
3. **Minimal Runtime Footprint of Retained Baseline:**
   The retained policy is the supplied Greedy baseline. The root `Dockerfile` is a minimal 163-byte file based on `python:3.12.7-slim` that copies only `policy.py` and `kit.py`. It requires **zero external machine learning libraries, zero model weight files, zero GPU drivers, and zero network calls**.
4. **Exact Remediation Command:**
   Once Docker service is restored, the container is validated in under 30 seconds via:
   ```bash
   docker build -t sequential-policy:submission .
   python evaluate.py --image sequential-policy:submission --seeds 101 --output results/container_check.json
   ```

**Scoring Rubric (20 Points):**
* **6 pts:** Defends the ethics of transparent disclosure over fabricated validation passes.
* **7 pts:** Outlines the extensive unit tests, data verification, and independent code reviews that passed.
* **7 pts:** Emphasizes the minimal, dependency-free nature of the Greedy Dockerfile and provides the exact verification command.
* **Deductions:** $-6$ if candidate claims the container check actually passed; $-4$ if candidate cannot explain why the baseline Dockerfile has zero external dependencies.

---

## Defense Scoring Summary & Pass/Fail Rubric

| Total Score | Classification | Committee Recommendation |
|:---:|:---:|:---|
| **$\ge 92$ Points** | **High Pass with Distinction** | Unconditional promotion to production; benchmark defense exemplary. |
| **$85 - 91$ Points** | **Pass** | Approved for submission; minor documentation polish. |
| **$75 - 84$ Points** | **Conditional Pass** | Approved subject to resolving containerized execution and audit checks. |
| **$< 75$ Points** | **Fail / Re-examination** | Candidate fails to distinguish exploratory from confirmatory evidence or misunderstands problem boundaries. |
