# Independent Oral Defense & Technical Exercises

This workbook contains 10 rigorous, unsolved technical practice problems designed to prepare candidates for oral examination and technical defense of the Sequential Reciprocal Matching benchmark. Problems span statistical derivations, algorithmic proofs, information boundary analysis, and adversarial defense strategy.

Complete solutions, proofs, and defense scripts are provided in [`study_notes/defense/answer_keys.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/defense/answer_keys.md).

---

### Problem 1: Clustered Variance Inflation and Intracluster Correlation
In Study Q1, candidate arm $G_{\text{arr}}$ is evaluated against baseline $G$ across $m = 16$ changing-condition laws and $n = 12$ pseudo-random seed clusters ($N = n \times m = 192$ episodes per arm).
1. Suppose an analyst mistakenly models the episode differences as independent and identically distributed: $d_{s\ell} = Y_{s\ell a} - Y_{s\ell G} \sim \text{i.i.d. } \mathcal{N}(\mu, \sigma_e^2)$. Derive the theoretical variance of the sample mean $\text{Var}_{\text{naive}}(\bar{D})$.
2. Now introduce a random seed effect: $d_{s\ell} = \mu + u_s + \epsilon_{s\ell}$, where $u_s \sim \mathcal{N}(0, \sigma_u^2)$ is the cluster-level random effect and $\epsilon_{s\ell} \sim \mathcal{N}(0, \sigma_\epsilon^2)$ is the idiosyncratic episode disturbance. Show that the true variance of the sample mean is:
   $$\text{Var}_{\text{cluster}}(\bar{D}) = \frac{\sigma_u^2 + \sigma_\epsilon^2 / m}{n} = \frac{\sigma_{\text{total}}^2}{N} \left[ 1 + (m - 1)\rho \right]$$
   where $\rho = \frac{\sigma_u^2}{\sigma_u^2 + \sigma_\epsilon^2}$ is the intracluster correlation coefficient (ICC).
3. Using the observed naive standard error $\text{SE}_{\text{naive}} \approx 0.0300$ and the corrected cluster standard error $\text{SE}_{\text{cluster}} = 0.07682$, solve for the empirical intracluster correlation $\rho$. Explain why ignoring $\rho > 0$ invalidates hypothesis testing in oral defense.

---

### Problem 2: Multiplicity Control: Holm Step-Down vs. Hochberg Step-Up vs. Benjamini-Hochberg
Consider an exploratory screening study testing $k = 5$ candidate mechanisms against a control:
* Sorted $p$-values: $p_{(1)} = 0.008, \; p_{(2)} = 0.012, \; p_{(3)} = 0.018, \; p_{(4)} = 0.024, \; p_{(5)} = 0.045$.
1. Compute the Holm step-down adjusted $p$-values for all 5 hypotheses at family-wise error rate $\alpha = 0.05$. Which hypotheses are rejected?
2. Compute the Hochberg step-up procedure rejections at $\alpha = 0.05$. (Recall: Hochberg starts at $i = k$ and rejects all $H_{(j)}$ for $j \le i$ if $p_{(i)} \le \frac{\alpha}{k - i + 1}$).
3. Compute the Benjamini-Hochberg (BH) false discovery rate (FDR) adjusted $q$-values at $q^* = 0.05$.
4. In the context of defending negative confirmatory results, why did the authors select the Holm step-down procedure rather than Benjamini-Hochberg FDR control for the Q1–Q3 supplemental studies?

---

### Problem 3: Rare-Event Brier Score Decomposition and the Skill Floor
In Study Q2, 5,009 introductions selected by Greedy have an observed MSMI qualification prevalence of $\bar{y} = 62 / 5009 \approx 0.012378$ ($1.238\%$).
1. Derive the Brier Score for a constant-prediction model $p_i = c$ for all $i \in \{1, \dots, N\}$. Show analytically that the choice of $c$ that minimizes the Brier score on this sample is exactly the sample prevalence $c^* = \bar{y}$.
2. The Brier Skill Score (BSS) relative to the sample prevalence reference is defined as:
   $$\text{BSS} = 1 - \frac{\text{BS}_{\text{model}}}{\text{BS}_{\text{prev}}}$$
   Compute the BSS for:
   * The simulator-informed prior model (`sim`), where $\text{BS}_{\text{sim}} = 0.01219332$.
   * The empirical observable-fit model (`emp`), where $\text{BS}_{\text{emp}} = 0.01225016$.
3. Interpret the resulting BSS values. What fraction of the sample uncertainty is resolved by each model? How does this mathematical result refute the claim that "a Brier score of 0.012 demonstrates excellent prediction"?

---

### Problem 4: Competitive Ratio Bounds for Online Greedy Matching
Consider an online bipartite matching graph $G = (U \cup V, E)$ where offline vertices $U$ are known at $t = 0$ and online vertices $V$ arrive sequentially at $t = 1, 2, \dots, T$.
1. Prove that for unweighted graphs, any deterministic online greedy matching algorithm achieves a competitive ratio of at least $1/2$ against an oblivious adversary:
   $$\frac{|M_{\text{Greedy}}|}{|M_{\text{Opt}}|} \ge \frac{1}{2}$$
2. Construct a concrete graph instance and arrival sequence showing that this bound is tight (i.e., $|M_{\text{Greedy}}| / |M_{\text{Opt}}| = 1/2$).
3. In the Sequential Reciprocal Matching benchmark, the graph is non-bipartite (general preference graph) and edges carry delayed stochastic rewards. Explain why a myopic greedy policy may achieve a competitive ratio strictly *less* than $1/2$ in terms of terminal realized MSMI.

---

### Problem 5: Combinatorial Asking Budget Optimization
Under the benchmark rules, the daily asking budget is $B = 12$ credits.
* Asking a `constraints` bundle costs 3 credits and simultaneously reveals all unobserved hard constraints for that member.
* Asking a specific soft-field question costs 1 credit.
1. Formulate the daily query selection problem as an integer knapsack problem where the objective is to maximize immediate edge verification.
2. Suppose there are 5 available members who each have unverified hard constraints, and 10 pairs whose hard constraints are fully verified but each lack 2 soft-field values.
   * Can the policy verify all 5 members' hard bundles today?
   * If the policy spends all 12 credits on hard bundles (4 bundles), how many credits remain for soft queries?
   * Explain why the baseline Greedy policy chooses to request *only* hard-constraint bundles and never requests soft-attribute questions.

---

### Problem 6: The Qualification Funnel: Survival and Attrition Algebra
Under standard generator parameters, let an introduction between members $A$ and $B$ be formed on day $t$.
1. Define the exact mathematical condition for this introduction to achieve a qualified outcome ($Q = 1$).
2. Let $p_{\text{resp}} \approx 0.765$ be the average response rate, $p_{\text{accept}} \approx 0.38$ be the conditional acceptance probability given response, $p_{\text{date}} = 0.78$ be the date occurrence probability, and $p_{\text{second\_yes}} \approx 0.50$ be the conditional second-meeting acceptance probability.
   * Derive the expected probability that both members respond with "yes" at the initial introduction.
   * Conditional on a date occurring, what is the probability that both post-date responses arrive within the required 3-day window ($\tau_a - d \le 3$ and $\tau_b - d \le 3$), assuming delay $\sim \text{Uniform}(\{1, 2, 3, 4, 5\})$?
   * Combine these probabilities to estimate the unconditional probability $P(Q = 1)$ for an assigned introduction. Compare your theoretical estimate to the empirical frequency observed in Study Q2 ($1.238\%$).

---

### Problem 7: Right-Censoring and Snapshot Truncation Bias in Empirical Priors
In `fit_priors.py`, the empirical prior model estimates the date-occurrence probability $\hat{p}_{\text{happen}}$ using a public state snapshot extracted at day $t = 30$.
* Across the 2,000 members in the snapshot data, the estimator records $\hat{p}_{\text{happen}} = 0.4762$.
* The ground-truth simulator parameter in `kit.py` is $p_{\text{happen}} = 0.7800$.
1. Trace the simulator mechanics: when an introduction achieves mutual acceptance on day $t_{\text{intro}}$, on what day does the date occur?
2. Explain mathematically why evaluating introductions from a day-30 snapshot introduces severe right-censoring for introductions assigned between day 16 and day 30.
3. Show why treating unobserved dates as "did not occur" creates negative truncation bias, and prove that $\hat{p}_{\text{happen}} = 0.4762$ is an artifact of snapshot censoring rather than an accurate empirical recovery.

---

### Problem 8: Directional Calibration with Moving-Window Estimation
Candidate policy $X_1$ estimates a drift adjustment $\hat{\Delta}$ over a trailing window of $W = 21$ days.
1. Suppose on day $t = 40$, the policy observes $n_{21} = 45$ mutual acceptance feedback events in the past 21 days, with sample mean logit residual $\hat{\Delta} = -0.32$ and sample standard deviation $s = 1.10$.
   * Compute $\text{SE}(\hat{\Delta})$.
   * Compute the shrinkage test threshold $1.64485 \cdot \text{SE}(\hat{\Delta})$.
   * Determine the exact value of $\Delta_{\text{applied}}$.
2. Now suppose the observed sample has $\hat{\Delta} = -0.55$ with the same standard error.
   * Determine $\Delta_{\text{applied}}$.
   * Trace the effect of this non-zero offset on the probability of acceptance for a pair whose baseline logit was $z_0 = 0.20$.

---

### Problem 9: Demographic Access Disparities vs. Algorithmic Bias
Review the empirical findings from [`subgroups_q1_greedy.csv`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/subgroups_q1_greedy.csv):
* Men: $64.69\%$ unserved. Women: $64.52\%$ unserved. Non-binary: $63.09\%$ unserved.
* Complete hard profile at arrival: $47.11\%$ unserved.
* Incomplete hard profile at arrival: $77.84\%$ unserved.
* Declined at least one hard field: $100.00\%$ unserved.
1. Does the near-identical unserved rate across gender ($64.69\%$ vs. $64.52\%$) prove that the Greedy baseline is "fair" across gender? Give two statistical or domain reasons why this aggregate metric is insufficient.
2. An auditor asserts: *"Your policy discriminates against users who decline questions because 100% of them are unserved."*
   Formulate a rigorous defense explaining the structural difference between algorithmic bias and hard eligibility verification under the benchmark data contract.

---

### Problem 10: Adversarial Defense Strategy: The "Why Retain Greedy?" Oral Challenge
You are defending your benchmark submission before a skeptical faculty committee. An examiner poses the following challenge:
> *"In your report, chronological asking ($G_{\text{arr}}$) achieved an MSMI/100 of 0.5547 compared to Greedy's 0.4557, which is a +21.7% relative gain. Furthermore, in Round 1 you submitted a policy named simple_fifo. Yet in Round 2, you retain the basic Greedy baseline and conclude that no replacement is confirmed superior. Isn't this an overly timid, cowardly conclusion? Why shouldn't an engineering team deploy $G_{\text{arr}}$ immediately?"*

Draft a structured, 3-minute oral defense response that:
1. Distinguishes exploratory point estimates from confirmatory superiority.
2. Directly quotes the seed-cluster 95% confidence interval and Holm-adjusted $p$-value for $G_{\text{arr}}$.
3. Explains the difference between list-order asking and arrival-time sorting.
4. Identifies the operational, latency, and dependency risks of deploying an unconfirmed candidate.
5. Concludes with a defensible, principled engineering recommendation.
