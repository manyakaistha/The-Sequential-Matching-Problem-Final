# Comprehensive Answer Keys to Independent Defense Exercises

This document provides complete, rigorous mathematical solutions, code-level derivations, and defense scripts for the 10 problems in [`study_notes/defense/independent_exercises.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/defense/independent_exercises.md).

---

### Solution 1: Clustered Variance Inflation and Intracluster Correlation

#### Part 1: Derivation of the Naive Variance
When $N = n \times m$ observations $d_{s\ell}$ are treated as independent and identically distributed with variance $\sigma_e^2$:
$$\bar{D} = \frac{1}{N} \sum_{s=1}^n \sum_{\ell=1}^m d_{s\ell}$$
$$\text{Var}_{\text{naive}}(\bar{D}) = \frac{1}{N^2} \sum_{s=1}^n \sum_{\ell=1}^m \text{Var}(d_{s\ell}) = \frac{N \sigma_e^2}{N^2} = \frac{\sigma_e^2}{N} = \frac{\sigma_e^2}{n \cdot m}$$

#### Part 2: Derivation of the Clustered Variance and Intracluster Correlation
Under the random effects model $d_{s\ell} = \mu + u_s + \epsilon_{s\ell}$, where $u_s \sim \mathcal{N}(0, \sigma_u^2)$ and $\epsilon_{s\ell} \sim \mathcal{N}(0, \sigma_\epsilon^2)$:
The within-cluster mean is:
$$\bar{d}_s = \frac{1}{m} \sum_{\ell=1}^m (\mu + u_s + \epsilon_{s\ell}) = \mu + u_s + \bar{\epsilon}_s$$
Because $u_s$ and $\bar{\epsilon}_s$ are independent:
$$\text{Var}(\bar{d}_s) = \text{Var}(u_s) + \text{Var}(\bar{\epsilon}_s) = \sigma_u^2 + \frac{\sigma_\epsilon^2}{m}$$
The overall sample mean is the average of the $n$ independent cluster means:
$$\bar{D} = \frac{1}{n} \sum_{s=1}^n \bar{d}_s \implies \text{Var}_{\text{cluster}}(\bar{D}) = \frac{1}{n^2} \sum_{s=1}^n \text{Var}(\bar{d}_s) = \frac{\sigma_u^2 + \sigma_\epsilon^2 / m}{n}$$

To express this in terms of the total variance $\sigma_{\text{total}}^2 = \sigma_u^2 + \sigma_\epsilon^2$ and the intracluster correlation $\rho = \frac{\sigma_u^2}{\sigma_{\text{total}}^2}$:
Note that $\sigma_u^2 = \rho \sigma_{\text{total}}^2$ and $\sigma_\epsilon^2 = (1 - \rho)\sigma_{\text{total}}^2$.
Substitute these into $\text{Var}_{\text{cluster}}(\bar{D})$:
$$\text{Var}_{\text{cluster}}(\bar{D}) = \frac{1}{n} \left[ \rho \sigma_{\text{total}}^2 + \frac{(1 - \rho)\sigma_{\text{total}}^2}{m} \right] = \frac{\sigma_{\text{total}}^2}{n \cdot m} \left[ m\rho + 1 - \rho \right] = \frac{\sigma_{\text{total}}^2}{N} \left[ 1 + (m - 1)\rho \right]$$
The term $\text{VIF} = 1 + (m - 1)\rho$ is known as the **Variance Inflation Factor** or design effect.

#### Part 3: Numerical Recovery of $\rho$
Given:
* $\text{SE}_{\text{naive}} \approx 0.03000 \implies \text{Var}_{\text{naive}} = (0.03000)^2 = 0.0009000$
* $\text{SE}_{\text{cluster}} = 0.07682 \implies \text{Var}_{\text{cluster}} = (0.07682)^2 = 0.0059013$
* Number of conditions per cluster: $m = 16$.
$$\text{VIF} = \frac{\text{Var}_{\text{cluster}}}{\text{Var}_{\text{naive}}} = \frac{0.0059013}{0.0009000} = 6.557$$
Solve for $\rho$:
$$1 + (16 - 1)\rho = 6.557 \implies 15\rho = 5.557 \implies \rho = \frac{5.557}{15} \approx 0.3705$$
**Oral Defense Implication:**
An ICC of $\rho \approx 37\%$ indicates substantial shared variance across conditions within the same seed. Ignoring this correlation deflates standard errors by a factor of $\sqrt{6.557} \approx 2.56$ and leads to catastrophic false-positive claims (e.g., reporting $p = 0.001$ instead of the true $p = 0.224$).

---

### Solution 2: Multiplicity Control: Holm vs. Hochberg vs. Benjamini-Hochberg

Given sorted $p$-values: $p_{(1)} = 0.008, \; p_{(2)} = 0.012, \; p_{(3)} = 0.018, \; p_{(4)} = 0.024, \; p_{(5)} = 0.045$ with $k = 5$ and $\alpha = 0.05$.

#### Part 1: Holm Step-Down Procedure
Compare each $p_{(i)}$ to the threshold $\frac{\alpha}{k - i + 1}$:
1. $i = 1$: $p_{(1)} = 0.008 \le \frac{0.05}{5} = 0.010$. **Reject $H_{(1)}$**.
   * Adjusted $p_{(1)}^{\text{adj}} = \min(1.0, 5 \times 0.008) = 0.040$.
2. $i = 2$: $p_{(2)} = 0.012 \le \frac{0.05}{4} = 0.0125$. **Reject $H_{(2)}$**.
   * Adjusted $p_{(2)}^{\text{adj}} = \max(0.040, \min(1.0, 4 \times 0.012)) = \max(0.040, 0.048) = 0.048$.
3. $i = 3$: $p_{(3)} = 0.018 > \frac{0.05}{3} \approx 0.01667$. **Fail to reject $H_{(3)}$**.
   * Step-down stops immediately. All remaining hypotheses ($H_{(3)}, H_{(4)}, H_{(5)}$) are retained.
   * Adjusted $p_{(3)}^{\text{adj}} = \max(0.048, 3 \times 0.018) = 0.054$.
   * Adjusted $p_{(4)}^{\text{adj}} = \max(0.054, 2 \times 0.024) = 0.054$.
   * Adjusted $p_{(5)}^{\text{adj}} = \max(0.054, 1 \times 0.045) = 0.054$.
* **Rejections under Holm:** Only $H_{(1)}$ and $H_{(2)}$.

#### Part 2: Hochberg Step-Up Procedure
Hochberg is a step-up procedure: start at the largest $p$-value $i = k = 5$ and step downward.
Find the largest $i$ such that $p_{(i)} \le \frac{\alpha}{k - i + 1}$:
* $i = 5$: $p_{(5)} = 0.045 \le \frac{0.05}{1} = 0.050$. **Condition satisfied!**
* Since the condition is satisfied at $i = 5$, Hochberg rejects **all** hypotheses $H_{(1)}, H_{(2)}, H_{(3)}, H_{(4)}, H_{(5)}$.
* **Rejections under Hochberg:** All 5 hypotheses rejected.

#### Part 3: Benjamini-Hochberg (BH) FDR Procedure
For FDR control at $q^* = 0.05$, find the largest $i$ such that $p_{(i)} \le \frac{i}{k} q^*$:
* $i = 5$: $p_{(5)} = 0.045 \le \frac{5}{5}(0.05) = 0.050$. **Condition met!**
* Therefore, BH rejects all hypotheses $j \le 5$, meaning **all 5 hypotheses are rejected**.

#### Part 4: Why Holm was Chosen Over Benjamini-Hochberg
In benchmark policy defense, promoting an unverified candidate to production carries asymmetric costs: an algorithm promoted on false discovery degrades match quality for real human users. Controlling the False Discovery Rate (FDR) allows a fixed proportion of promoted policies to be false positives ($\mathbb{E}[\text{False Discoveries} / \text{Total Discoveries}] \le q^*$). In contrast, the Holm procedure guarantees strong control of the Family-Wise Error Rate (FWER): the probability of promoting *even a single* ineffective policy is bounded by $\alpha = 0.05$. Holm represents the conservative, ethically sound engineering choice.

---

### Solution 3: Rare-Event Brier Score Decomposition and Skill Floor

#### Part 1: Optimization of Constant Prediction
Let $p_i = c$ for all $i \in \{1, \dots, N\}$.
$$\text{BS}(c) = \frac{1}{N} \sum_{i=1}^N (c - y_i)^2 = \frac{1}{N} \sum_{i=1}^N \left( c^2 - 2c y_i + y_i^2 \right) = c^2 - 2c \bar{y} + \frac{1}{N}\sum_{i=1}^N y_i^2$$
To minimize $\text{BS}(c)$, take the derivative with respect to $c$ and set to zero:
$$\frac{d \text{BS}}{dc} = 2c - 2\bar{y} = 0 \implies c^* = \bar{y}$$
Since $\frac{d^2 \text{BS}}{dc^2} = 2 > 0$, $c^* = \bar{y}$ is the unique global minimum.
The minimum Brier score for a constant predictor is:
$$\text{BS}(\bar{y}) = \bar{y}^2 - 2\bar{y}^2 + \bar{y} = \bar{y}(1 - \bar{y})$$
For $\bar{y} = 62 / 5009 \approx 0.01237772$:
$$\text{BS}_{\text{prev}} = 0.01237772 \times (1 - 0.01237772) = 0.01222451$$

#### Part 2: Computation of Brier Skill Score (BSS)
1. **Simulator-informed Prior (`sim`):**
   $$\text{BSS}_{\text{sim}} = 1 - \frac{\text{BS}_{\text{sim}}}{\text{BS}_{\text{prev}}} = 1 - \frac{0.01219332}{0.01222451} = 1 - 0.9974486 = +0.0025514 \approx \mathbf{+0.26\%}$$
2. **Empirical Prior (`emp`):**
   $$\text{BSS}_{\text{emp}} = 1 - \frac{\text{BS}_{\text{emp}}}{\text{BS}_{\text{prev}}} = 1 - \frac{0.01225016}{0.01222451} = 1 - 1.0020982 = -0.0020982 \approx \mathbf{-0.21\%}$$

#### Part 3: Oral Defense Interpretation
The Brier Skill Score measures percentage improvement in probabilistic forecast skill over the trivial sample prevalence baseline.
* The simulator prior resolves only **$0.26\%$** of the baseline uncertainty.
* The empirical prior achieves a **negative** skill score ($-0.21\%$), meaning its predictions are less accurate than simply guessing the constant base rate $1.238\%$.
* **Defense Talking Point:** When outcomes are rare ($1.2\%$), $98.8\%$ of the Brier score is dictated by the uncertainty floor $\bar{y}(1-\bar{y})$. Quoting an absolute Brier score of $0.012$ without referencing the prevalence floor is deceptive; the skill score reveals that the model provides essentially zero discriminative value over constant guessing.

---

### Solution 4: Competitive Ratio Bounds for Online Greedy Matching

#### Part 1: Proof that Greedy $\ge 1/2$ on Unweighted Graphs
Let $M_{\text{Greedy}}$ be the matching produced by any deterministic greedy algorithm on an unweighted graph $G = (V, E)$, and let $M_{\text{Opt}}$ be a maximum cardinality matching.
By definition of greedy selection, $M_{\text{Greedy}}$ is a **maximal matching**: no additional edge from $E$ can be added without sharing an endpoint with an edge already in $M_{\text{Greedy}}$.
Consider any edge $e = (u, v) \in M_{\text{Opt}}$.
Because $M_{\text{Greedy}}$ is maximal, at least one of its endpoints $u$ or $v$ must be matched in $M_{\text{Greedy}}$. (If neither were matched, edge $e$ could be added to $M_{\text{Greedy}}$, contradicting maximality.)
Each edge in $M_{\text{Greedy}}$ can cover at most two vertices, and therefore can intersect at most two distinct edges in $M_{\text{Opt}}$.
Summing over all edges in $M_{\text{Opt}}$:
$$|M_{\text{Opt}}| \le 2 \cdot |M_{\text{Greedy}}| \implies \frac{|M_{\text{Greedy}}|}{|M_{\text{Opt}}|} \ge \frac{1}{2}$$

#### Part 2: Tightness Instance
Consider a path of 3 edges on 4 vertices: $v_1 - v_2 - v_3 - v_4$.
* Offline vertices: $v_1, v_4$.
* Online vertices arrive: $v_2$ arrives at $t=1$, revealing edge $(v_1, v_2)$. Then $v_3$ arrives at $t=2$, revealing edges $(v_2, v_3)$ and $(v_3, v_4)$.
* If greedy matches $(v_2, v_3)$ (e.g., due to tie-breaking or arrival order), both $v_2$ and $v_3$ become unavailable.
* Greedy achieves $|M_{\text{Greedy}}| = 1$ (edge $(v_2, v_3)$).
* Optimal offline matching selects $|M_{\text{Opt}}| = 2$ (edges $(v_1, v_2)$ and $(v_3, v_4)$).
* Ratio: $|M_{\text{Greedy}}| / |M_{\text{Opt}}| = 1/2$.

#### Part 3: Sub-1/2 Competitive Ratio Under Stochastic Delayed Outcomes
In the Sequential Reciprocal Matching benchmark:
1. **Multi-Stage Stochastic Degradation:** Even if greedy finds a valid edge, terminal MSMI requires a 5-stage survival chain (response $\to$ acceptance $\to$ date occurrence $\to$ second response $\to$ second yes). A greedy edge with low survival probability $p_1 = 0.01$ will produce an expected reward of $0.01$, whereas saving the member for an arriving partner with survival probability $p_2 = 0.40$ would yield $0.40$. The ratio of expected rewards is $0.01 / 0.40 = 1/40 \ll 1/2$.
2. **Prolonged Lockout Period:** Introducing a pair locks both participants into a non-preemptible busy state for 8 to 20 days. Myopic matching blocks future high-value matches for up to one-third of the episode horizon.

---

### Solution 5: Combinatorial Asking Budget Optimization

#### Part 1: Integer Knapsack Formulation
Let $x_i \in \{0, 1\}$ be the binary decision to ask the `constraints` bundle for member $i$, costing $c_{\text{hard}} = 3$.
Let $z_{jk} \in \{0, 1\}$ be the decision to query soft attribute $k$ for member $j$, costing $c_{\text{soft}} = 1$.
The daily budget constraint is:
$$\sum_{i} 3 x_i + \sum_{j, k} z_{jk} \le 12$$
Let $\Delta V(x, z)$ be the expected marginal increase in feasible edge verification and ranking accuracy. The optimal daily action solves:
$$\max_{x, z} \Delta V(x, z) \quad \text{subject to } \quad 3 \sum_i x_i + \sum_{j, k} z_{jk} \le 12, \quad x_i, z_{jk} \in \{0, 1\}$$

#### Part 2: Budget Allocation Analysis
* **Can the policy verify 5 hard bundles?**
  Cost $= 5 \times 3 = 15$ credits. Since the daily budget is 12, $15 > 12$. **No**, at most $\lfloor 12 / 3 \rfloor = 4$ bundles can be asked per day.
* **Credits remaining after 4 hard bundles:**
  $12 - (4 \times 3) = 0$ credits. Exactly zero credits remain for soft queries.
* **Why Greedy Prioritizes Only Hard Bundles:**
  Under the benchmark data contract, **hard constraint eligibility is an absolute prerequisite for introducing a pair**. If a member's hard constraints are unverified, they are strictly ineligible for *any* introduction, regardless of soft compatibility score. Soft questions refine ranking among already-feasible pairs, but hard questions *create* feasible edges from zero. Because feasible edges are sparse, converting an unavailable member into an eligible participant provides an infinitely higher marginal return than slightly refining a soft tie-break.

---

### Solution 6: Qualification Funnel: Survival and Attrition Algebra

#### Part 1: Mathematical Condition for $Q = 1$
For an introduction assigned on day $t$:
$$Q = \mathbf{1}\left\{ \text{date occurred}, \; d - t \le 30, \; y_a = \text{yes}, \; y_b = \text{yes}, \; \tau_a - d \le 3, \; \tau_b - d \le 3 \right\}$$

#### Part 2: Step-by-Step Probability Chain
1. **Initial Mutual Acceptance:**
   Both members must respond and both must accept:
   $$P(\text{Mutual Yes}) = (p_{\text{resp}} \cdot p_{\text{accept}})^2 \approx (0.765 \times 0.38)^2 = (0.2907)^2 \approx 0.0845 \quad (8.45\%)$$
2. **Date Occurrence and Scheduling:**
   Date occurs with probability $p_{\text{date}} = 0.78$. Under standard delay laws, the date day $d$ satisfies $d - t \le 30$ with probability $> 0.99$.
   $$P(\text{Date Occurred} \mid \text{Mutual Yes}) \approx 0.78$$
   Cumulative probability of date: $0.0845 \times 0.78 \approx 0.0659$ ($6.59\%$).
3. **On-Time Post-Date Response:**
   Both members must submit second-meeting feedback within 3 days. Since delay $\sim \text{Uniform}(\{1, 2, 3, 4, 5\})$:
   $$P(\text{Delay} \le 3) = \frac{3}{5} = 0.60$$
   Assuming independent delays for actor $a$ and actor $b$:
   $$P(\text{Both On-Time}) = \left(\frac{3}{5}\right)^2 = \frac{9}{25} = 0.36 \quad (36.0\%)$$
4. **Mutual Second-Meeting Intention:**
   Both members must respond and both must indicate "yes":
   $$P(\text{Both Second Yes} \mid \text{Date}) = (p_{\text{resp}} \cdot p_{\text{second\_yes}})^2 \approx (0.765 \times 0.50)^2 = (0.3825)^2 \approx 0.1463$$
5. **Total Unconditional Probability $P(Q = 1)$:**
   $$P(Q = 1) \approx P(\text{Mutual Yes}) \times P(\text{Date}) \times P(\text{Both Second Yes}) \times P(\text{Both On-Time})$$
   $$P(Q = 1) \approx 0.0845 \times 0.78 \times 0.1463 \times 0.36 \approx 0.00347 \quad (0.35\%)$$
* Accounting for positive homophily in soft traits (which increases $p_{\text{accept}}$ and $p_{\text{second\_yes}}$ above population averages for matched pairs), the empirical probability on matched edges rises to **$1.238\%$** ($62 / 5009$).
* **Oral Defense Takeaway:** Even after mutual acceptance and date occurrence, the 3-day deadline filter alone eliminates $(1 - 0.36) = 64\%$ of potential successes!

---

### Solution 7: Right-Censoring and Snapshot Truncation Bias in Empirical Priors

#### Part 1: Date Scheduling Mechanics in `kit.py`
In `kit.py` (lines 165–175):
* Mutual acceptance responses take between 1 and 7 days: $t_{\text{resp}} = \max(\text{delay}_a, \text{delay}_b) \in [1, 7]$.
* Date day is scheduled as:
  $$d = t_{\text{resp}} + \text{randint}(1, 14)$$
* Total elapsed time from introduction assignment to date occurrence:
  $$\Delta t_{\text{date}} = d - t_{\text{intro}} \in [2, 21] \text{ days}$$

#### Part 2: Mathematical Censoring Mechanism at Day 30
In `fit_priors.py`, the empirical prior script examines introductions in a snapshot taken at $t = 30$.
* For an introduction assigned on day $t_{\text{intro}} = 22$, the scheduled date day is $d = 22 + \Delta t_{\text{date}}$.
* Since $\Delta t_{\text{date}}$ has mean $4 + 7.5 = 11.5$ days, the expected date day is $d \approx 33.5 > 30$.
* At day 30, the simulator event `date_happened` has **not yet fired** because $d > 30$.
* The snapshot records this introduction as:
  $$\text{mutual\_acceptance} = \text{True}, \quad \text{date\_happened} = \text{False}$$

#### Part 3: Proof of Negative Truncation Bias
The naive snapshot estimator computes:
$$\hat{p}_{\text{happen}} = \frac{\sum_{i=1}^M \mathbf{1}\{\text{date observed by day 30}\}}{\sum_{i=1}^M \mathbf{1}\{\text{mutual acceptance observed by day 30}\}}$$
Let $C_i = \mathbf{1}\{d_i \le 30\}$ be the observation indicator. Then:
$$\mathbb{E}[\hat{p}_{\text{happen}}] = p_{\text{happen}} \cdot P(d \le 30 \mid \text{assigned before day } 30) < p_{\text{happen}}$$
Introductions assigned in the second half of the snapshot window are heavily right-censored. Treating unobserved pending dates as negative outcomes artificially depresses the estimate from the ground truth $0.78$ down to $\hat{p} = 0.4762$.
* **Defense Conclusion:** The empirical prior's low date prediction ($7.26\%$ vs. observed $10.92\%$) is not a reflection of real-world conservatism; it is a mathematical artifact of naive snapshot estimation without Kaplan-Meier survival correction.

---

### Solution 8: Directional Calibration with Moving-Window Estimation

#### Part 1: Case 1 Trace ($n = 45, \hat{\Delta} = -0.32, s = 1.10$)
1. **Standard Error:**
   $$\text{SE}(\hat{\Delta}) = \frac{s}{\sqrt{n_{21}}} = \frac{1.10}{\sqrt{45}} = \frac{1.10}{6.7082} = 0.16398$$
2. **Shrinkage Threshold:**
   $$\text{Threshold} = 1.64485 \times \text{SE}(\hat{\Delta}) = 1.64485 \times 0.16398 = 0.26972$$
3. **Deadband Comparison:**
   $$|\hat{\Delta}| = 0.32 > 0.26972$$
   Since the drift magnitude exceeds the threshold, the policy applies directional shrinkage:
   $$\Delta_{\text{applied}} = \text{sign}(-0.32) \times (| -0.32 | - 0.26972) = -1 \times (0.32 - 0.26972) = \mathbf{-0.05028}$$

#### Part 2: Case 2 Trace ($n = 45, \hat{\Delta} = -0.55, s = 1.10$)
1. **Deadband Comparison:**
   $$|\hat{\Delta}| = 0.55 > 0.26972$$
2. **Applied Offset:**
   $$\Delta_{\text{applied}} = -1 \times (0.55 - 0.26972) = \mathbf{-0.28028}$$
3. **Effect on Logit and Probability:**
   * Baseline logit: $z_0 = 0.20 \implies P_0 = \frac{1}{1 + e^{-0.20}} = \frac{1}{1 + 0.81873} = 0.5498$ ($54.98\%$).
   * Calibrated logit: $z_{\text{new}} = z_0 + \Delta_{\text{applied}} = 0.20 - 0.28028 = -0.08028$.
   * Calibrated probability:
     $$P_{\text{new}} = \frac{1}{1 + e^{-(-0.08028)}} = \frac{1}{1 + 1.0836} = 0.4800 \quad (48.00\%)$$
   * Probability is adjusted downward by $6.98$ percentage points in response to detected negative drift.

---

### Solution 9: Demographic Access Disparities vs. Algorithmic Bias

#### Part 1: Why Equal Unserved Rates Do Not Prove Fairness
1. **Simpson's Paradox and Confounding by Zone/Age:**
   The aggregate unserved rates ($64.69\%$ men vs. $64.52\%$ women) average across disparate geographic zones and arrival days. If men are overrepresented in sparse geographic zones where overall match probability is lower, equal aggregate rates could conceal disparate treatment conditional on zone.
2. **Failure of Conditional Demographic Parity (Equality of Opportunity):**
   Fairness in matching requires evaluating outcomes *conditional on eligibility*:
   $$P(\text{served} \mid \text{eligible}, \, \text{gender} = \text{man}) \stackrel{?}{=} P(\text{served} \mid \text{eligible}, \, \text{gender} = \text{woman})$$
   The reported table in `subgroups_q1_greedy.csv` conditions only on arrival, not on whether a feasible partner existed in the pool. True algorithmic fairness cannot be established without conditioning on graph degree and mutual preference feasibility.

#### Part 2: Rigorous Defense Against "Discrimination Against Incomplete Profiles"
**Candidate Defense Script:**
> *"The 100% unserved rate among members who decline hard questions is not algorithmic discrimination; it is a direct consequence of the benchmark data contract and reciprocal user consent.
> Under the problem specification, hard constraints encompass mandatory legal and safety boundaries: age limits, geographic zones, relationship structure, and child preferences. The data contract strictly prohibits introducing pairs whose mutual eligibility cannot be verified. When a user declines to provide a hard field, that field remains permanently unobserved. The policy cannot guess, impute, or override a declined field with a compatibility score.
> Treating voluntary refusal to provide eligibility criteria as algorithmic bias confuses two distinct concepts: algorithmic bias involves disparate treatment among equally qualified individuals; here, the unserved status reflects non-fulfillment of prerequisite eligibility criteria necessary for mutual consent."*

---

### Solution 10: Adversarial Defense Script: The "Why Retain Greedy?" Oral Challenge

**Examiner Prompt:**
*"In your report, chronological asking ($G_{\text{arr}}$) achieved an MSMI/100 of 0.5547 compared to Greedy's 0.4557, which is a +21.7% relative gain. Furthermore, in Round 1 you submitted simple_fifo. Yet in Round 2, you retain Greedy and conclude that no replacement is confirmed superior. Isn't this an overly timid conclusion? Why shouldn't an engineering team deploy $G_{\text{arr}}$ immediately?"*

**Model 3-Minute Candidate Defense Script:**
> *"Thank you for that challenge, Professor. It cuts directly to the distinction between exploratory data snooping and confirmatory statistical engineering. I will defend our decision to retain Greedy on three precise grounds: statistical uncertainty, mechanistic evidence, and operational risk.
>
> First, regarding the statistical evidence: the +0.0990 point difference for $G_{\text{arr}}$ in Study Q1 is an exploratory result across 12 shared seed clusters. When we correctly cluster by seed—as required by the repeated-measures experimental design—the 95% confidence interval is $[-0.0701, \; +0.2680]$ with a Holm-adjusted $p$-value of $0.8965$. This interval comfortably covers zero and extends down to $-0.07$ MSMI per 100 members. To promote an algorithm into production based on a post-hoc point estimate whose confidence interval includes substantial negative harm would violate basic empirical rigor.
>
> Second, the narrative that FIFO question ordering provides a structural advantage is refuted by the broader experimental record. In Round 1, the submitted `simple_fifo` candidate was subjected to a registered 40-seed confirmatory trial against Greedy. The result was negative: a difference of $-0.0417$ MSMI/100, 95% CI $[-0.0911, +0.0077]$. Furthermore, the hypothesized mechanism for FIFO—that it reduces waiting—is empirically false in our data: in Study Q1, $G_{\text{arr}}$ had a *longer* mean served wait (6.81 days) than baseline Greedy (6.66 days), with an identical unserved fraction of 64.4%. Chronological ordering did not improve user throughput or waiting dynamics.
>
> Third, from a systems and software engineering perspective, the baseline Greedy policy is zero-overhead, completely deterministic, has zero hyperparameter dependencies, requires no runtime state persistence, and passed all 22 unit tests with execution times under 0.10 seconds. In contrast, the candidate learned models failed the registered calibration gate and were completely rejected in the audited 288-cell screen.
>
> In conclusion: we do not claim Greedy is mathematically optimal. We claim that across thousands of simulated episodes, richer alternatives—whether chronological query ordering, learned neural scorers, or adaptive logit adjustments—failed to establish confirmatory superiority over this simple baseline. Retaining Greedy is not timidity; it is disciplined engineering that protects users against unverified complexity."*
