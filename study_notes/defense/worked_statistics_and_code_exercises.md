# Worked Statistics and Code Exercises: Oral Defense Preparation

This guide presents complete, step-by-step mathematical derivations, algorithmic traces, and code-level calculations for the key analytical foundations of the Sequential Reciprocal Matching benchmark. Every formula is derived from first principles and numerically executed using the exact datasets preserved in [`study_notes/data/`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/).

---

## 1. Seed-Cluster Contrast Derivation and Step-by-Step Calculation

### 1.1 The Statistical Challenge: Clustered Dependence Across Experimental Conditions
In the Supplemental Robustness Study (Q1), an experimental policy is evaluated across 16 changing-condition laws $\mathcal{L} = \{\ell_1, \ell_2, \dots, \ell_{16}\}$ and 12 pseudo-random seed initializations $\mathcal{S} = \{s_1, s_2, \dots, s_{12}\}$ (seeds `4000101` through `4000112`).
A naive analyzer might treat each episode as an independent observation, yielding:
$$N_{\text{naive}} = 12 \text{ seeds} \times 16 \text{ laws} = 192 \text{ episodes per arm}$$
Treating these 192 episodes as independent violates the fundamental Gauss-Markov assumption of uncorrelated residuals: within a seed cluster $s$, the underlying member population and demographic characteristics are identical across all 16 laws. Consequently, episode-level errors are positively correlated ($\text{Cov}(e_{s\ell a}, e_{s\ell' a}) > 0$). Naive variance estimation deflates standard errors and artificially inflates degrees of freedom from 11 to 191, producing spuriously tight confidence intervals.

### 1.2 Mathematical Derivation of the Cluster-Mean Contrast
To produce an exact, design-consistent estimate of the policy contrast between a candidate arm $a$ (e.g., chronological asking $G_{\text{arr}}$) and the baseline control $G$, we aggregate outcomes within each seed cluster before computing the contrast standard error.

Let $Y_{s\ell a}$ denote the realized metric (MSMI per 100 arrived members) for seed $s$, law $\ell$, and policy arm $a$.
For each seed cluster $s \in \mathcal{S}$, define the within-seed average paired difference across all $|\mathcal{L}| = 16$ executed laws:
$$D_s = \frac{1}{|\mathcal{L}|} \sum_{\ell \in \mathcal{L}} \left( Y_{s\ell a} - Y_{s\ell G} \right)$$

The overall sample contrast estimator is the sample mean of the cluster differences:
$$\bar{D} = \frac{1}{n} \sum_{s=1}^n D_s, \quad \text{where } n = 12$$

The sample variance of the cluster differences is:
$$s_D^2 = \frac{1}{n - 1} \sum_{s=1}^n \left( D_s - \bar{D} \right)^2$$

The cluster standard error of the mean difference is:
$$\text{SE}(\bar{D}) = \frac{s_D}{\sqrt{n}} = \sqrt{\frac{1}{n(n-1)} \sum_{s=1}^n (D_s - \bar{D})^2}$$

Under the central limit theorem for the 12 cluster means (or assuming cluster differences are approximately normally distributed), the test statistic follows a Student-$t$ distribution with $df = n - 1 = 11$ degrees of freedom:
$$t = \frac{\bar{D}}{\text{SE}(\bar{D})} \sim t_{11}$$

The two-sided $(1 - \alpha)$ confidence interval is:
$$\text{CI}_{1-\alpha} = \left[ \bar{D} - t_{1 - \alpha/2, \, n-1} \cdot \text{SE}(\bar{D}), \; \bar{D} + t_{1 - \alpha/2, \, n-1} \cdot \text{SE}(\bar{D}) \right]$$

### 1.3 Step-by-Step Numerical Walkthrough: $G_{\text{arr}}$ vs. $G$ in Study Q1
From [`study_notes/data/study_analysis.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/study_analysis.json) and [`episode_metrics.csv`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/episode_metrics.csv), we extract the exact vector of 12 cluster differences $D_s$ for chronological asking ($G_{\text{arr}}$) versus Greedy ($G$):

| Seed Cluster Index ($i$) | Seed ID | Mean Difference across 16 Laws ($D_s$) | Deviation $(D_s - \bar{D})$ | Squared Deviation $(D_s - \bar{D})^2$ |
|:---:|:---:|:---:|:---:|:---:|
| 1 | 4000101 | $+0.093750$ | $-0.005208$ | $0.00002713$ |
| 2 | 4000102 | $+0.250000$ | $+0.151042$ | $0.02281358$ |
| 3 | 4000103 | $-0.093750$ | $-0.192708$ | $0.03713651$ |
| 4 | 4000104 | $+0.687500$ | $+0.588542$ | $0.34638129$ |
| 5 | 4000105 | $-0.343750$ | $-0.442708$ | $0.19599071$ |
| 6 | 4000106 | $+0.062500$ | $-0.036458$ | $0.00132921$ |
| 7 | 4000107 | $+0.156250$ | $+0.057292$ | $0.00328233$ |
| 8 | 4000108 | $+0.125000$ | $+0.026042$ | $0.00067817$ |
| 9 | 4000109 | $-0.062500$ | $-0.161458$ | $0.02606880$ |
| 10 | 4000110 | $+0.343750$ | $+0.244792$ | $0.05992297$ |
| 11 | 4000111 | $-0.187500$ | $-0.286458$ | $0.08205839$ |
| 12 | 4000112 | $+0.156250$ | $+0.057292$ | $0.00328233$ |
| **Sum** | | **$+1.187500$** | **$0.000000$** | **$0.77897142$** |

**Step 1: Calculate Sample Mean $\bar{D}$**
$$\bar{D} = \frac{1}{12} \sum_{s=1}^{12} D_s = \frac{1.187500}{12} = 0.09895833 \approx +0.0990 \text{ MSMI per 100 members}$$

**Step 2: Calculate Sample Variance $s_D^2$ and Standard Deviation $s_D$**
$$s_D^2 = \frac{1}{12 - 1} \sum_{s=1}^{12} (D_s - \bar{D})^2 = \frac{0.77897142}{11} = 0.07081558$$
$$s_D = \sqrt{0.07081558} = 0.26611196$$

**Step 3: Calculate Cluster Standard Error $\text{SE}(\bar{D})$**
$$\text{SE}(\bar{D}) = \frac{s_D}{\sqrt{12}} = \frac{0.26611196}{3.46410162} = 0.07681991 \approx 0.0768$$

**Step 4: Determine Two-Tailed Critical $t$-Value**
For $df = 11$ and $\alpha = 0.05$:
$$t_{0.975, \, 11} = 2.20098516$$

**Step 5: Compute the 95% Confidence Interval**
$$\text{Margin of Error} = 2.20098516 \times 0.07681991 = 0.16907948$$
$$\text{Lower Bound} = 0.09895833 - 0.16907948 = -0.07012114 \approx -0.0701$$
$$\text{Upper Bound} = 0.09895833 + 0.16907948 = +0.26803781 \approx +0.2680$$
$$\mathbf{95\% \text{ CI}} = [-0.0701, \; +0.2680]$$

**Step 6: Compute $t$-Statistic and Two-Sided $p$-Value**
$$t = \frac{\bar{D}}{\text{SE}(\bar{D})} = \frac{0.09895833}{0.07681991} = 1.288186$$
Using the Student-$t$ survival function $2 \times P(T_{11} \ge 1.288186)$:
$$p_{\text{two-sided}} = 0.22411871 \approx 0.2241$$

### 1.4 Contrast with the Flawed Naive Analysis
In earlier exploratory work, analysts treated the $N = 192$ episodes as independent. The naive standard error was:
$$\text{SE}_{\text{naive}} \approx 0.0300, \quad df = 191, \quad t_{0.975, 191} = 1.972$$
$$\text{CI}_{\text{naive}} = [+0.040, \; +0.158], \quad p_{\text{naive}} \approx 0.001$$
This naive calculation excluded zero and claimed statistical significance. The corrected cluster analysis proves that once the true level of randomization (the seed cluster) is respected, the confidence interval easily spans zero $[-0.0701, +0.2680]$, demonstrating that the candidate policy cannot be confirmed superior.

---

## 2. Holm Step-Down Multiplicity Procedure: Step-by-Step Execution

### 2.1 The Need for Family-Wise Error Rate (FWER) Control
When testing multiple candidate policies against a control baseline $G$ within the same study, conducting independent hypothesis tests at nominal level $\alpha = 0.05$ causes severe family-wise alpha inflation. For $k$ simultaneous tests, the probability of at least one false positive under the global null is $1 - (1 - \alpha)^k$. For $k = 5$ tests, this probability is $1 - (0.95)^5 = 22.62\%$.
The Holm step-down procedure controls the FWER strongly at level $\alpha$ while being strictly more powerful than the single-step Bonferroni correction.

### 2.2 The Holm Step-Down Algorithm
Let $H_{(1)}, H_{(2)}, \dots, H_{(k)}$ be the family of $k$ null hypotheses, sorted in ascending order of their unadjusted two-sided $p$-values:
$$p_{(1)} \le p_{(2)} \le \dots \le p_{(k)}$$

To determine adjusted $p$-values that preserve monotonicity:
1. For each rank $i \in \{1, 2, \dots, k\}$, calculate the nominal step-down adjusted value:
   $$p_{(i)}^{\text{step}} = \min(1.0, \; (k - i + 1) \cdot p_{(i)})$$
2. Enforce the cumulative maximum constraint so that adjusted $p$-values are non-decreasing:
   $$p_{(1)}^{\text{adj}} = p_{(1)}^{\text{step}}$$
   $$p_{(i)}^{\text{adj}} = \max\left( p_{(i-1)}^{\text{adj}}, \; p_{(i)}^{\text{step}} \right) \quad \text{for } i = 2, \dots, k$$

### 2.3 Step-by-Step Numerical Walkthrough: Study Q1 Robustness Contrasts
In Study Q1, $k = 5$ candidate arms are tested against baseline $G$: $\{P, G_{\text{arr}}, G_{\text{deg}}, Q6, G_{\text{lifo}}\}$.

**Step 1: Extract and Sort Raw Two-Sided $p$-values from Cluster $t$-tests**
From [`study_notes/data/study_analysis.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/study_analysis.json):
1. Arm $P$: $p = 0.114632$
2. Arm $G_{\text{arr}}$: $p = 0.224119$
3. Arm $G_{\text{deg}}$: $p = 0.407552$
4. Arm $Q6$: $p = 0.509494$
5. Arm $G_{\text{lifo}}$: $p = 0.955471$

**Step 2: Compute Step-by-Step Multipliers and Cumulative Maximums**

| Rank ($i$) | Arm | Raw $p_{(i)}$ | Multiplier $(k - i + 1)$ | Unconstrained Value $(k - i + 1) \cdot p_{(i)}$ | Running Cumulative Maximum $\max(p_{(i-1)}^{\text{adj}}, \dots)$ | Final Holm Adjusted $p$ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | $P$ | $0.114632$ | $5 - 1 + 1 = 5$ | $5 \times 0.114632 = 0.573161$ | $0.573161$ | **$0.573161$** |
| 2 | $G_{\text{arr}}$ | $0.224119$ | $5 - 2 + 1 = 4$ | $4 \times 0.224119 = 0.896475$ | $\max(0.573161, 0.896475) = 0.896475$ | **$0.896475$** |
| 3 | $G_{\text{deg}}$ | $0.407552$ | $5 - 3 + 1 = 3$ | $3 \times 0.407552 = 1.222656 \to 1.0$ | $\max(0.896475, 1.000000) = 1.000000$ | **$1.000000$** |
| 4 | $Q6$ | $0.509494$ | $5 - 4 + 1 = 2$ | $2 \times 0.509494 = 1.018988 \to 1.0$ | $\max(1.000000, 1.000000) = 1.000000$ | **$1.000000$** |
| 5 | $G_{\text{lifo}}$ | $0.955471$ | $5 - 5 + 1 = 1$ | $1 \times 0.955471 = 0.955471$ | $\max(1.000000, 0.955471) = 1.000000$ | **$1.000000$** |

### 2.4 Critical Oral Defense Observation: Monotonicity Constraint
Notice Rank 5 ($G_{\text{lifo}}$): the unconstrained product is $1 \times 0.955471 = 0.955471$.
If an analyst fails to apply the cumulative maximum constraint, Rank 5 would report an adjusted $p$-value ($0.955$) *lower* than Rank 3 and Rank 4 ($1.000$). This is logically impossible because rejecting hypothesis 5 would require first rejecting hypotheses 1, 2, 3, and 4. The cumulative maximum operator guarantees that adjusted $p$-values are monotonically increasing with rank.

---

## 3. Brier Score Decomposition and Probability Calibration

### 3.1 Mathematical Definition and Decomposition of Brier Score
For binary classification of events $y_i \in \{0, 1\}$ given predicted probabilities $p_i \in [0, 1]$ over $N$ observations, the Brier Score is the mean squared error:
$$\text{BS} = \frac{1}{N} \sum_{i=1}^N (p_i - y_i)^2$$

Murphy (1973) proved that the Brier score can be partitioned into three orthogonal components based on $K$ calibration bins:
$$\text{BS} = \underbrace{\frac{1}{N} \sum_{k=1}^K N_k (p_k - \bar{y}_k)^2}_{\text{Reliability (Calibration Error)}} - \underbrace{\frac{1}{N} \sum_{k=1}^K N_k (\bar{y}_k - \bar{y})^2}_{\text{Resolution (Discrimination)}} + \underbrace{\bar{y}(1 - \bar{y})}_{\text{Uncertainty (Base Rate Floor)}}$$
where $N_k$ is the number of predictions in bin $k$, $p_k$ is the mean predicted probability in bin $k$, $\bar{y}_k$ is the observed empirical frequency in bin $k$, and $\bar{y} = \frac{1}{N}\sum y_i$ is the overall sample prevalence.

### 3.2 Controlled Evaluation: 5,009 Identical G-Selected Introductions in Study Q2
To evaluate model scoring without confounding from different policy actions, the benchmark records shadow predictions for two prior models—`sim` (simulator-informed prior) and `emp` (empirical observable-fit prior)—on the exact same 5,009 introductions selected by Greedy ($G$) during Study Q2. Across these 5,009 introductions, exactly 62 resulted in qualified MSMI outcomes ($y_i = 1$).

#### 3.2.1 Benchmark Baseline Comparators
1. **Always-Zero Predictor ($p_i = 0$ for all $i$):**
   $$\text{BS}_0 = \frac{1}{N} \sum_{i=1}^N (0 - y_i)^2 = \frac{1}{N} \sum_{i=1}^N y_i = \bar{y} = \frac{62}{5009} = 0.01237772$$
2. **Sample Prevalence Predictor ($p_i = \bar{y} = 0.01237772$ for all $i$):**
   $$\text{BS}_{\text{prev}} = \frac{1}{N} \sum_{i=1}^N (\bar{y} - y_i)^2 = \bar{y}(1 - \bar{y}) = 0.01237772 \times (1 - 0.01237772) = 0.01222451$$

#### 3.2.2 Exact Calibration Metrics Comparison

| Metric | Simulator Prior (`sim`) | Empirical Prior (`emp`) | Interpretation |
|:---|:---:|:---:|:---|
| **Mean Predicted Probability** | $0.010693$ ($1.0693\%$) | $0.005897$ ($0.5897\%$) | Empirical prior severely underpredicts base rate |
| **Observed Prevalence ($\bar{y}$)** | $0.012378$ ($1.2378\%$) | $0.012378$ ($1.2378\%$) | True underlying qualification frequency |
| **Signed Error ($\bar{p} - \bar{y}$)** | $-0.001684$ ($-0.1684$ pp) | $-0.006481$ ($-0.6481$ pp) | `emp` underpredicts by over $52\%$ of true rate |
| **Brier Score (MSE)** | **$0.012193$** | **$0.012250$** | Both are near the zero-prediction baseline ($0.012378$) |
| **Expected Calibration Error (ECE)** | **$0.003093$** | **$0.007425$** | `sim` has $2.4\times$ lower calibration error |

### 3.3 The Defense Trap: Why a Low Brier Score Does Not Imply a Useful Policy
In an oral defense, an examiner may ask:
> *"Your empirical prior achieves a Brier score of 0.01225, which represents less than 1.3% mean squared error. Why do you claim it is poorly calibrated and inadequate?"*

**The Defense Answer:**
The Brier score is dominated by the base rate uncertainty floor:
$$\text{Uncertainty} = \bar{y}(1 - \bar{y}) = 0.012378 \times 0.987622 = 0.012225$$
A brainless model that predicts $p_i = 0$ for all pairs achieves $\text{BS} = 0.012378$. A model predicting the constant prevalence achieves $\text{BS} = 0.012225$.
The empirical prior's Brier score of $0.012250$ is actually *worse* than the trivial constant-prevalence baseline ($0.012225$). Furthermore, `emp` underpredicts the true rate by $-0.6481$ percentage points (predicting $0.5897\%$ against an actual $1.2378\%$), caused directly by snapshot truncation of pending dates at day 30. A low Brier score under severe class imbalance is a statistical artifact of rare outcomes, not proof of discriminative ranking power.

---

## 4. Greedy Matching Counterexamples

### 4.1 Static Graph: Greedy Maximal Matching vs. Maximum Cardinality Matching
Greedy matching iteratively selects an edge of maximum available weight (or arbitrary legal edge) and removes both incident vertices. While simple and fast, greedy matching only guarantees a **maximal** matching, not a **maximum cardinality** matching, with a worst-case competitive ratio of $1/2$.

#### Counterexample Graph: The 4-Vertex Path $P_4$
Consider 4 members arriving on day 0: $V = \{v_1, v_2, v_3, v_4\}$.
All 4 members are mutually available and satisfy hard reciprocal constraints.
The feasible edge set consists of 3 edges:
$$E = \{ (v_1, v_2), \; (v_2, v_3), \; (v_3, v_4) \}$$

Soft-attribute overlap scores:
* $\text{Score}(v_2, v_3) = 4$
* $\text{Score}(v_1, v_2) = 3$
* $\text{Score}(v_3, v_4) = 3$

```
      Score = 3             Score = 4             Score = 3
(v1) ------------ (v2) ==================== (v3) ------------ (v4)
```

**Step 1: Greedy Execution**
1. Greedy evaluates all feasible edges in descending order of soft score:
   $$\text{Sorted edges}: [(4, (v_2, v_3)), \; (3, (v_1, v_2)), \; (3, (v_3, v_4))]$$
2. Greedy greedily selects $(v_2, v_3)$ because it has the highest score ($4$).
3. Vertices $v_2$ and $v_3$ are added to the used set: $\text{Used} = \{v_2, v_3\}$.
4. Edge $(v_1, v_2)$ is evaluated: rejected because $v_2 \in \text{Used}$.
5. Edge $(v_3, v_4)$ is evaluated: rejected because $v_3 \in \text{Used}$.
6. Algorithm terminates.
$$\mathbf{M}_{\text{Greedy}} = \{ (v_2, v_3) \}, \quad |M_{\text{Greedy}}| = 1 \text{ match}$$
$$\text{Total Score} = 4$$
Members $v_1$ and $v_4$ are left unserved and exit the pool.

**Step 2: Optimal Maximum Cardinality Allocation**
Select edges $(v_1, v_2)$ and $(v_3, v_4)$:
$$\mathbf{M}_{\text{Opt}} = \{ (v_1, v_2), \; (v_3, v_4) \}, \quad |M_{\text{Opt}}| = 2 \text{ matches}$$
$$\text{Total Score} = 3 + 3 = 6$$

**Mathematical Conclusion:**
$$\frac{|M_{\text{Greedy}}|}{|M_{\text{Opt}}|} = \frac{1}{2} = 50\%$$
Greedy achieves exactly half the cardinality and only $4/6 = 66.7\%$ of the total score.

### 4.2 Dynamic Sequential Counterexample: Myopic Matching vs. Optimal Continuation
In a sequential matching horizon ($t = 0, 1, \dots, 59$), a myopic greedy policy matches feasible pairs immediately today. However, introducing a member today locks them into a multi-day state transition (7-day response window + date delay + follow-up delay = at least 8 to 20 days unavailable), preventing them from being matched with higher-compatibility members arriving tomorrow.

#### Concrete 2-Period Markov Decision Process (MDP) Trace
* **Day 0:**
  * Member $A$ arrives. Member $B$ arrives.
  * Feasibility: $(A, B)$ is feasible.
  * True conditional probability of qualified MSMI: $P(Q = 1 \mid A, B) = 0.05$.
* **Day 1:**
  * Member $C$ arrives with probability $1.0$.
  * Compatibility: $(B, C)$ is incompatible. $(A, C)$ has extraordinary compatibility: $P(Q = 1 \mid A, C) = 0.40$.
  * If member $A$ was introduced to $B$ on Day 0, $A$ is busy on Day 1 (and remains busy until Day 8 at minimum):
    $$\text{available}(A) = \text{False on Day } 1$$

**Policy Comparison:**
1. **Myopic Greedy Policy (No Waiting):**
   * Day 0: Matches $(A, B)$ because it is feasible. Expected reward $= 0.05$.
   * Day 1: Member $C$ arrives. $A$ is busy. $B$ is busy. No match can be formed.
   * Expected total MSMI $= 0.05$.
2. **Optimal Dynamic Policy (Strategic Reservation / Waiting):**
   * Day 0: Recognizes that member $A$'s continuation value $V_1(A)$ exceeds the immediate match reward:
     $$R(A, B) = 0.05 < \mathbb{E}[V_1(A)] = 0.40$$
     Policy intentionally yields an empty match: $\text{Pairs}_0 = \emptyset$.
   * Day 1: Member $C$ arrives. $A$ is available. Policy introduces $(A, C)$.
   * Expected total MSMI $= 0.40$.

**Defense Takeaway:**
Myopic greedy matching is provably suboptimal in sequential allocation with arrivals. However, as documented in [`REPORT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/final_report/REPORT.md) Section 3.3, developing a dynamic reservation policy in this benchmark failed because continuation value estimators broke down under sparse terminal feedback (1.2% base rate), causing learned reservation policies to withhold matches that never materialized.

---

## 5. Wilson Score Interval for Binomial Proportions with Zero Events

### 5.1 Failure of the Normal (Wald) Approximation
For a binomial proportion $\hat{p} = y / n$, the standard Wald confidence interval is:
$$\text{CI}_{\text{Wald}} = \hat{p} \pm z_{1-\alpha/2} \sqrt{\frac{\hat{p}(1-\hat{p})}{n}}$$
When $y = 0$ successes are observed in $n$ trials:
$$\hat{p} = 0 \implies \text{SE}_{\text{Wald}} = \sqrt{\frac{0(1)}{n}} = 0 \implies \text{CI}_{\text{Wald}} = [0, 0]$$
The Wald interval claims that when 0 events are observed, the upper bound of the true probability is exactly 0, which is completely false.

### 5.2 Derivation of the Wilson Score Interval
The Wilson interval inverts the score test for the binomial parameter $p$:
$$\left| \frac{\hat{p} - p}{\sqrt{p(1-p)/n}} \right| \le z$$
Squaring both sides yields a quadratic equation in $p$:
$$(\hat{p} - p)^2 = z^2 \frac{p(1-p)}{n}$$
$$\hat{p}^2 - 2\hat{p}p + p^2 = \frac{z^2}{n} p - \frac{z^2}{n} p^2$$
$$\left(1 + \frac{z^2}{n}\right) p^2 - \left(2\hat{p} + \frac{z^2}{n}\right) p + \hat{p}^2 = 0$$

Applying the quadratic formula $p = \frac{-B \pm \sqrt{B^2 - 4AC}}{2A}$:
$$A = 1 + \frac{z^2}{n}$$
$$B = -\left(2\hat{p} + \frac{z^2}{n}\right)$$
$$C = \hat{p}^2$$

The roots define the Wilson score interval:
$$\text{Center} = \frac{\hat{p} + \frac{z^2}{2n}}{1 + \frac{z^2}{n}}$$
$$\text{Half-Width} = \frac{z}{1 + \frac{z^2}{n}} \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}$$
$$\text{CI}_{\text{Wilson}} = \left[ \text{Center} - \text{Half-Width}, \; \text{Center} + \text{Half-Width} \right]$$

### 5.3 Numerical Walkthrough: Study Q2 Calibration Reliability Bins
From [`study_notes/data/reliability_bins.csv`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/reliability_bins.csv), for calibration series `q2_G_shadow_sim_terminal`:

#### Case 1: Low-Probability Bin with Zero Positives ($n = 364, y = 0, p \in [0.0025, 0.005)$)
* $n = 364$, $y = 0 \implies \hat{p} = 0.0$
* $z = 1.95996398$ ($95\%$ level), $z^2 = 3.8414588$
* Denominator factor: $1 + \frac{z^2}{n} = 1 + \frac{3.8414588}{364} = 1 + 0.01055346 = 1.01055346$
* Center:
  $$\text{Center} = \frac{0 + \frac{3.8414588}{2 \times 364}}{1.01055346} = \frac{0.00527673}{1.01055346} = 0.00522162$$
* Radical term:
  $$\sqrt{0 + \frac{3.8414588}{4 \times (364)^2}} = \sqrt{\frac{3.8414588}{530016}} = \sqrt{7.247817 \times 10^{-6}} = 0.00269218$$
* Half-width:
  $$\text{Half-Width} = \frac{1.95996398 \times 0.00269218}{1.01055346} = \frac{0.00527657}{1.01055346} = 0.00522147$$
* Bounds:
  $$\text{Lower} = \max(0, \; 0.00522162 - 0.00522147) = 0.000000$$
  $$\text{Upper} = 0.00522162 + 0.00522147 = 0.01044309 \approx \mathbf{0.010443}$$
  $$\mathbf{95\% \text{ Wilson CI}} = [0.000000, \; 0.010443]$$
*(Matches `reliability_bins.csv` exactly: `[0.0, 0.010443245938100362]`)*

#### Case 2: Calibration Bin with 1 Positive ($n = 358, y = 1, p \in [0.005, 0.0075)$)
* $n = 358$, $y = 1 \implies \hat{p} = 1 / 358 = 0.00279330$
* $z^2 / n = 3.8414588 / 358 = 0.01073033$
* Denominator factor: $1.01073033$
* Center:
  $$\text{Center} = \frac{0.00279330 + 0.00536517}{1.01073033} = \frac{0.00815847}{1.01073033} = 0.00807186$$
* Radical:
  $$\sqrt{\frac{0.00279330 \times 0.9972067}{358} + \frac{3.8414588}{4 \times (358)^2}} = \sqrt{7.78077 \times 10^{-6} + 7.49320 \times 10^{-6}} = \sqrt{1.527398 \times 10^{-5}} = 0.00390819$$
* Half-width:
  $$\frac{1.95996398 \times 0.00390819}{1.01073033} = \frac{0.00765992}{1.01073033} = 0.00757860$$
* Bounds:
  $$\text{Lower} = 0.00807186 - 0.00757860 = \mathbf{0.00049326}$$
  $$\text{Upper} = 0.00807186 + 0.00757860 = \mathbf{0.01565046}$$
*(Matches `reliability_bins.csv` exactly: `[0.0004932556426906157, 0.01565044121209347]`)*

---

## 6. Directional Calibration Shrinkage Thresholding Trace

### 6.1 Algorithmic Formulation
In Study Q3, the adaptive candidate policy $X_1$ updates its acceptance logit predictions online using recent observations from a rolling 21-day window. To prevent fitting to sampling noise while responding to true population drift, the policy computes a sample logit bias $\hat{\Delta}$ and its standard error $\text{SE}(\hat{\Delta})$.
The applied logit correction $\Delta_{\text{applied}}$ is governed by a directional soft-thresholding shrinkage operator:
$$\Delta_{\text{applied}} = \text{sign}(\hat{\Delta}) \max\left( 0, \; |\hat{\Delta}| - 1.64485 \cdot \text{SE}(\hat{\Delta}) \right)$$

### 6.2 Mathematical Properties of the Shrinkage Operator
1. **Critical Constant $1.64485$:**
   $1.64485$ is the $95\text{th}$ percentile of the standard normal distribution ($z_{0.95} = \Phi^{-1}(0.95) = 1.6448536$).
   This corresponds to a one-sided $95\%$ confidence threshold (or two-sided $90\%$ confidence threshold).
2. **Zero-Zone (Deadband):**
   If the estimated drift magnitude does not exceed $1.64485$ standard errors:
   $$|\hat{\Delta}| \le 1.64485 \cdot \text{SE}(\hat{\Delta}) \implies \Delta_{\text{applied}} = 0$$
   The policy applies zero correction, perfectly insulating the model against small stochastic perturbations.
3. **Directional Shrinkage:**
   When $|\hat{\Delta}| > 1.64485 \cdot \text{SE}(\hat{\Delta})$, the offset is shrunk toward zero by exactly $1.64485 \cdot \text{SE}(\hat{\Delta})$, preserving the directional sign while damping parameter volatility.

### 6.3 Code Execution Trace and Action Invariance
In Study Q3, the component ablation arm $X1_{\text{nocal\_emp}}$ completely removes this directional calibration operator (setting $\Delta_{\text{applied}} = 0$ unconditionally).
Comparing $X1_{\text{emp}}$ (with directional calibration) and $X1_{\text{nocal\_emp}}$ (without directional calibration) across all 72 executed episodes in Study Q3 yields an extraordinary empirical finding:
* In [`study_notes/data/study_analysis.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/study_analysis.json):
  $$\text{Identical Action Cells} = 72 \text{ out of } 72 \quad (100.0\%)$$
  $$\text{Qualified Pairs}_{X1\_\text{emp}} = 64, \quad \text{Qualified Pairs}_{X1\_\text{nocal\_emp}} = 64$$
  $$\text{MSMI/100}_{X1\_\text{emp}} = 0.4444, \quad \text{MSMI/100}_{X1\_\text{nocal\_emp}} = 0.4444$$
  $$\Delta(\text{MSMI}) = 0.000000, \quad \text{Action Digest SHA256 Agreement} = 100\%$$

**Why Did Calibration Leave Action Digests Unchanged?**
1. **Monotonicity Over Common Edges:** The directional correction adds a scalar logit offset $\Delta_{\text{applied}}$ to the logit of mutual acceptance. Because logistic sigmoid $\sigma(z + \Delta)$ is strictly monotonic in $z$, shifting all edges by a common scalar offset does not alter the relative ranking of edges unless interaction terms are present.
2. **Greedy Maximal Matching Without Reservation Threshold:** Unlike an optimal stopping controller that reserves members when $p(e) < \theta_{\text{reserve}}$, Greedy matches any feasible edge with score $> 0$ in rank order. Because the rank order was preserved and the feasible set was identical (governed by the same asking log), the exact same batch of introductions was executed on every single day across all 72 episodes.
