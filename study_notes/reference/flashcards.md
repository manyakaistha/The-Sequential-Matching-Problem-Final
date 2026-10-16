# Master High-Yield Flashcards: Sequential Reciprocal Matching

**The Sequential Reciprocal Matching Problem Under Changing Conditions**  
**Monograph Reference Systems & Spaced Repetition Flashcard Deck**  
**Authoritative Reference:** [final_report/REPORT.md](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/final_report/REPORT.md) | [study_notes/reference/glossary_and_notation.md](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/reference/glossary_and_notation.md)

---

## Deck 1: Problem Formulation, Time Horizons & Outcome Funnel

### Card 1.1: Decision Horizon vs. Follow-up Horizon
* **Front**: What are the exact lengths and operational rules of the active decision window versus the post-decision follow-up window in the competition environment?
* **Back**:
  - **Decision Window**: Days $t \in [0, 59]$ ($60$ decision days). The policy interacts with the environment by calling `resolve_asks()` (clarification) and `advance()` (introductions). No introductions or asks can be issued after day 59.
  - **Follow-up Window**: Days $t \in [60, 99]$ ($40$ follow-up days). Active policy choices are frozen. The simulator continues running so that dates scheduled late in the decision window and downstream second-meeting responses can mature through their full latency windows.
  - *Key Takeaway*: Day 59 is NOT an outcome deadline. Evaluation takes place only after day 99.

### Card 1.2: The Mathematical Definition of Qualified Outcome ($Q$)
* **Front**: State the exact mathematical definition of the binary qualified outcome indicator $Q$ for an introduction assigned on day $t$.
* **Back**:
  $$Q = \mathbf{1}\left\{ \text{date occurred} \;\land\; (d - t \le 30) \;\land\; (y_a = y_b = \text{yes}) \;\land\; (\tau_a - d \le 3) \;\land\; (\tau_b - d \le 3) \right\}$$
  Where:
  1. Both members accept the initial introduction ($y_a^{(1)} = y_b^{(1)} = \text{yes}$).
  2. The date actually occurs ($d \ge t$) within 30 days of assignment ($d - t \le 30$).
  3. Both members submit positive second-meeting intentions ($y_a^{(2)} = y_b^{(2)} = \text{yes}$).
  4. Both second-meeting responses are submitted within 3 days of the date ($\tau_a - d \le 3$ and $\tau_b - d \le 3$).

### Card 1.3: Primary Evaluation Metric
* **Front**: How is the primary competition metric $\text{MSMI}/100$ computed, and what constitutes one outcome unit?
* **Back**:
  $$\text{MSMI}/100 = 100 \times \frac{\sum_{i=1}^M Q_i}{N_{\text{arrived by day 59}}}$$
  - **Numerator**: The total count of qualified introduction pairs ($Q=1$). One mutually successful pair counts as **one outcome unit** (not two individuals).
  - **Denominator**: Total distinct members who arrived in the pool on or before day 59 (nominally $200$ members).
  - *Pitfall*: Denominator is arrived members, NOT eligible pairs or total assignments.

### Card 1.4: The 0.36 Delay Factor Derivation
* **Front**: Why does the constant factor $(3/5)^2 = 0.36$ appear in the terminal probability decomposition?
* **Back**:
  In the simulator specification, each member's second-meeting feedback delay $(\tau - d)$ following a date is distributed independently and uniformly over $\{1, 2, 3, 4, 5\}$ days.
  - The probability that an individual member responds within the required 3-day deadline is:
    $$\mathbb{P}(\tau - d \le 3) = \frac{|\{1, 2, 3\}|}{|\{1, 2, 3, 4, 5\}|} = \frac{3}{5} = 0.60$$
  - Since individual delays are conditionally independent, the joint probability that **both** members meet the 3-day deadline is:
    $$\mathbb{P}(\tau_a - d \le 3 \;\land\; \tau_b - d \le 3) = (0.60)^2 = 0.36$$

---

## Deck 2: Reciprocal Feasibility & Graph Matching Theory

### Card 2.1: Hard Constraints vs. Soft Attributes
* **Front**: What distinguishes hard constraints from soft fields, and can a high soft compatibility score override a missing hard field?
* **Back**:
  - **Hard Constraints (11 fields)**: Age bounds (`age_min`, `age_max`), acceptable genders (`who_to_meet`), relationship structure, smoking, partner smoking, children status, partner children, wants children, acceptable zones, and schedule overlap.
  - **Soft Attributes (7 fields)**: Relationship goal, pace, lifestyle, conversation style, emotional availability, space for relationship, relocate.
  - **Strict Rule**: Reciprocal hard feasibility is mandatory. Missing or declined hard data returns `needs_clarification`, mathematically blocking the match. **No soft compatibility score, however high, can ever override hard infeasibility or missingness**.

### Card 2.2: General Graph vs. Bipartite Matching
* **Front**: Why must the matching allocation problem be solved on a general graph rather than a bipartite graph?
* **Back**:
  The participant population includes women, men, and non-binary individuals with non-partitionable romantic preferences (e.g., non-binary individuals seeking all genders, bisexual women/men).
  - A bipartite graph requires dividing vertices into two disjoint sets $U$ and $V$ such that edges only exist between $U$ and $V$.
  - In this environment, odd-length cycles and non-bipartite preference loops exist. Forcing a bipartite solver (such as Hungarian bipartite matching) discards valid reciprocal edges. General matching algorithms (e.g., Edmonds' Blossom or general greedy first-fit) are strictly required.

### Card 2.3: Feasibility Graph Density and Edge Attrition
* **Front**: What is the typical feasible edge count in a 200-member pool before and after hard-constraint clarification?
* **Back**:
  - Total possible dyads among 200 members: $\binom{200}{2} = 19,900$.
  - **Before Clarification**: Average of only **17.8 feasible edges** (density $< 0.1\%$).
  - **After Clarification (non-declined)**: Expands to **59.6 feasible edges** (density $\approx 0.3\%$).
  - **All-Arrival Truth (Theoretical Oracle)**: $265.0$ feasible edges.
  - *Key Takeaway*: 35% of members decline at least one hard field (permanently blocking verification). Feasibility sparsity is the primary bottleneck of the entire domain.

### Card 2.4: Maximal vs. Maximum Weight Matching
* **Front**: Why did Edmonds' Blossom (exact Maximum Weight Matching) fail to outperform greedy first-fit matching in empirical trials?
* **Back**:
  - **Greedy first-fit** produces a *maximal* matching by picking edges in descending weight order.
  - **Edmonds' Blossom** finds the global *maximum* weight matching ($O(V^2 E)$).
  - *Empirical Reason*: The feasibility graph is so sparse (average degree $< 2$) that candidate edges rarely compete for the same member. When contention is near-zero, the greedy maximal matching is already identical or near-identical to the global maximum weight matching, while avoiding algorithmic complexity and timeout fallbacks.

---

## Deck 3: Information Acquisition & Clarification Rules

### Card 3.1: Clarification Action Types and Costs
* **Front**: What are the two types of questions a policy can submit via `resolve_asks()`, their respective costs, and the daily budget?
* **Back**:
  - **Daily Budget**: $12$ units per day. Unused budget does NOT roll over.
  - **Hard Constraint Bundle (`constraints`)**: Costs **3 units**. Returns all 11 hard constraint fields for a single member. A policy can ask at most $12 / 3 = 4$ hard bundles per day.
  - **Soft Field Question**: Costs **1 unit**. Returns a single named soft attribute (e.g., `lifestyle`) for a single member.
  - *Note*: An ask can only be issued to currently available members who have not declined the field.

### Card 3.2: The FIFO Clarification Invariance Theorem
* **Front**: State the FIFO Clarification Invariance Theorem and explain why it holds.
* **Back**:
  $$\forall \pi_1, \pi_2 \in \Pi_{\text{FIFO-hard}}, \quad \text{Asks}(\pi_1, s, \ell) \equiv \text{Asks}(\pi_2, s, \ell)$$
  - *Statement*: Any two policies that request hard-constraint bundles in public member-list order on a given seed and scenario will execute the exact same sequence of queries and incur identical cumulative ask costs on every day, regardless of their matching choices.
  - *Proof Mechanism*: Members with unverified hard profiles cannot be introduced under the eligibility contract. Therefore, incomplete members are never matched, and their availability is dictated entirely by exogenous arrival schedules.

### Card 3.3: Why Soft Field Clarification Fails
* **Front**: Why did policies that spend daily budget asking soft-field questions (`terminal_soft`, `model_soft`) underperform pure hard-bundle questioning?
* **Back**:
  - Spending 1 budget unit on a soft question reduces the remaining budget for hard bundles (which require 3 units).
  - Because hard constraints are the absolute gating requirement for eligibility, every deferred hard bundle directly reduces the number of discoverable feasible edges in the pool.
  - Soft fields provide only marginal ranking discrimination among already-feasible pairs. Sacrificing edge existence to refine edge weight yields a net negative expected outcome.

---

## Deck 4: Statistical Outcome Modeling, Priors & Calibration

### Card 4.1: The Parametric Outcome Funnel Decomposition
* **Front**: State the parametric decomposition formula for pair qualification probability $\mathbb{P}(\text{Terminal} \mid u, v)$.
* **Back**:
  $$\mathbb{P}(\text{Terminal Qualified} \mid u, v) = 0.36 \times h \times d \times k_u k_v \times \mathbb{E}\left[ a_u a_v s_u s_v \right]$$
  Where:
  - $0.36$: Two-sided 3-day response timeliness factor $((3/5)^2)$.
  - $h = \mathbb{P}(d - t \le 30)$: Date latency survival probability ($1.0$ standard, $0.978$ delayed).
  - $d = 0.78$: Date occurrence probability conditional on mutual acceptance.
  - $k_u = \mathbb{E}[R_u^2]$: Second moment of member response rate $R_u \sim U[0.55, 0.98]$.
  - $a_u, a_v$: Logistic introduction acceptance probabilities.
  - $s_u, s_v$: Logistic second-meeting intention probabilities.

### Card 4.2: Snapshot Censoring in Empirical Priors
* **Front**: What is snapshot censoring and how did it corrupt the date occurrence estimate in the empirical prior (`emp`)?
* **Back**:
  - The public datasets (`public_01` to `public_10`) are captured at an interim snapshot (day 30).
  - At day 30, many mutual acceptances have occurred whose dates are scheduled after day 30.
  - Naively computing $N_{\text{dates}} / N_{\text{mutual acceptances}}$ on the snapshot treats pending dates as non-occurrences, yielding an estimated date probability of **0.4762**, whereas the true generator rate is **0.78**.
  - This unadjusted censoring caused empirical prior models to severely underestimate terminal qualification rates.

### Card 4.3: Brier Score vs. Prevalence Benchmark
* **Front**: Why is a low raw Brier score (e.g., $0.038$) misleading when evaluating match outcome models?
* **Back**:
  In rare-event domains (where true positive rate $\bar{y} \approx 0.035$ to $0.040$), a trivial dummy model that predicts $\hat{p} \equiv 0$ everywhere achieves a Brier score equal to the event prevalence:
  $$\text{BS}_0 = \frac{1}{N}\sum (0 - y_i)^2 = \bar{y} \approx 0.035$$
  - A model predicting small probabilities can appear "highly accurate" under raw Brier score while possessing zero discriminative power.
  - Models must be benchmarked against both $\text{BS}_0$ and the sample prevalence Brier $\text{BS}_{\text{prev}} = \bar{y}(1 - \bar{y})$.

---

## Deck 5: Adaptive Drift Tracking & Component Ablations

### Card 5.1: Recency-Weighted MAP Adaptation in $X1$
* **Front**: How does policy arm $X1$ adapt to non-stationary preference drift during an episode?
* **Back**:
  - $X1$ discounts past feedback events $k$ using an exponential half-life of 14 days:
    $$w_k = 2^{-(t - t_k)/14}$$
  - At each decision day, it solves a penalized logistic regression with an $L_2$ MAP shrinkage penalty towards the baseline prior:
    $$\mathcal{L}(\theta) = -\sum_k w_k \log \mathbb{P}(y_k \mid x_k; \theta) + \frac{\lambda}{2} \|\theta - \theta_{\text{prior}}\|_2^2, \quad \lambda = 0.05$$

### Card 5.2: The Action Digest Invariance under Directional Calibration
* **Front**: Why did removing directional logit calibration ($X1_{\text{nocal\_emp}}$) produce 100% identical action digests to $X1_{\text{emp}}$ across all 72 drift episodes?
* **Back**:
  - Directional calibration applies a scalar logit offset $\Delta_{\text{applied}}$ to all edges.
  - Adding a scalar to all logits is a strictly monotonic transformation:
    $$\text{logit}(p_{uv}) + \Delta > \text{logit}(p_{wz}) + \Delta \iff p_{uv} > p_{wz}$$
  - Because the allocation engine uses greedy first-fit without a reservation or holding threshold, changing the absolute probabilities without altering their relative ranking cannot change the selected batch.

### Card 5.3: The Privileged Diagnostic Arm ($X1_{\text{oracle}}$)
* **Front**: What was $X1_{\text{oracle}}$ and what profound lesson did its performance reveal?
* **Back**:
  - $X1_{\text{oracle}}$ was given exact, privileged access to the ground-truth simulator drift schedule (knowing precisely when and how weights shifted).
  - **Result**: $X1_{\text{oracle}}$ achieved only $0.4583$ MSMI/100, trailing baseline Greedy ($0.5833$).
  - **Lesson**: The failure of complex scoring models in non-stationary environments is NOT caused by imperfect drift estimation. It is caused by graph sparsity: attempting to optimize subtle edge weights on a sparse graph distorts match selection away from robust greedy coverage.

---

## Deck 6: Experimental Design, Cluster Randomization & Multiplicity

### Card 6.1: The Independent Observation Fallacy
* **Front**: Explain the Independent Observation Fallacy that occurred in early Round 2 analyses.
* **Back**:
  In early analysis scripts (`research9/round2/analyze.py`), an experiment evaluating 6 arms across 16 scenario laws on 12 seeds was treated as $N = 12 \times 16 = 192$ independent observations.
  - *The Fallacy*: The 16 laws applied to seed `4000101` share the exact same underlying synthetic population, member traits, and baseline arrivals. They are highly correlated repeated measures within a single cluster.
  - *Consequence*: Treating $N=192$ inflated statistical degrees of freedom, producing an artificially tight confidence interval [$+0.040, +0.158$] and a spurious $p = 0.0009$ for $G_{\text{arr}}$.

### Card 6.2: Honest Seed-Cluster Contrast Formulation
* **Front**: State the mathematically correct seed-cluster contrast estimator and its degrees of freedom for 12 seeds.
* **Back**:
  For seed $s \in \{1, \dots, 12\}$, compute the intra-seed average contrast across all 16 laws:
  $$D_s = \frac{1}{16}\sum_{\ell=1}^{16} \left( Y_{s\ell a} - Y_{s\ell G} \right)$$
  - Aggregate estimator: $\bar{D} = \frac{1}{12}\sum_{s=1}^{12} D_s$, with standard error $\text{SE}(\bar{D}) = \frac{s_D}{\sqrt{12}}$.
  - Confidence interval is based on the Student-$t$ distribution with **11 degrees of freedom** ($S - 1 = 11$):
    $$\text{CI}_{95\%} = \left[ \bar{D} - 2.201 \cdot \text{SE}(\bar{D}), \quad \bar{D} + 2.201 \cdot \text{SE}(\bar{D}) \right]$$
  - For $G_{\text{arr}}$, this yields [$-0.0701, +0.2680$], correctly demonstrating that superiority is not statistically established.

### Card 6.3: Step-Down Holm-Bonferroni Correction
* **Front**: How does the step-down Holm-Bonferroni procedure adjust $p$-values across an exploratory study family?
* **Back**:
  Order two-sided unadjusted $p$-values: $p_{(1)} \le p_{(2)} \le \dots \le p_{(m)}$.
  - For rank $j$, the multiplier is $(m - j + 1)$.
  - To enforce monotonicity, take the cumulative maximum of earlier adjusted values:
    $$p_{(k)}^{\text{adj}} = \max_{j \le k} \min\left(1, \; (m - j + 1) \cdot p_{(j)}\right)$$
  - Strongly controls family-wise error rate (FWER) at level $\alpha$ under arbitrary dependence.

---

## Deck 7: Service Access, Waiting Times & Fairness Boundaries

### Card 7.1: Waiting Time Conditioning Fallacy
* **Front**: Why is reporting mean waiting time across all arrived members mathematically invalid, and how must waiting distributions be reported?
* **Back**:
  In sequential matching, ~64% of arrived members are **never introduced** during the 60-day episode ($T_{\text{wait}} = \infty$).
  - Imputing an arbitrary constant (e.g., 60 days) to unserved members creates an artificial, distorted statistic that obscures policy differences.
  - **Correct Method**: Always report waiting time as a **two-part distribution**:
    1. The unserved fraction $F_{\text{unserved}} = 1.0 - \text{Coverage}$.
    2. The conditional waiting time distribution $P(T_{\text{wait}} \le t \mid \text{served})$.

### Card 7.2: Demographic Parity vs. Hard Constraint Declines
* **Front**: If baseline Greedy serves men (35.3%), women (35.5%), and non-binary members (36.9%) at similar rates, does this prove demographic fairness?
* **Back**:
  **No**.
  1. *Subgroup Confounding*: Members who decline hard constraint fields have a 0% service rate because reciprocal feasibility checks cannot clear.
  2. *Sparsity vs Discrimination*: Even among members with complete profiles, 58% remain unserved simply due to graph degree limitations.
  3. *Observational Parity $\neq$ Causal Equity*: Coarse population averages across gender or age buckets do not establish intersectional fairness, absence of geographic bias, or equal conditional utility.

---

## Deck 8: Production Engineering, Invariances & Common Traps

### Card 8.1: The Closed Research Protocol
* **Front**: What is the Closed Research Protocol and why is it essential for production governance?
* **Back**:
  The protocol mandates that once exploratory research phases conclude and final reporting begins, **no new simulations, policy runs, hyperparameter fitting, or data modifications are permitted**.
  - All report assets and tables must be generated via a standalone reanalysis script (`build_assets.py`) that strictly consumes frozen, cryptographically hashed JSON/CSV registries.
  - Prevents continuous "fishing" for favorable seeds and guarantees auditability.

### Card 8.2: The Day-60 Feedback Cutoff Fallacy
* **Front**: State the common fallacy regarding arrival-ordered questioning ($G_{\text{arr}}$) and why it is physically impossible under the simulator rules.
* **Back**:
  - *The Fallacy*: Claiming that $G_{\text{arr}}$ achieves higher MSMI because asking earlier arrivals allows their second-meeting feedback to arrive before day 60.
  - *The Fact*: The simulator implements an explicit 40-day post-decision follow-up horizon ($t=60$ to $99$). All introductions made up to day 59 are tracked through their full 30-day date and 3-day feedback windows. No outcome is truncated on day 60.

### Card 8.3: Production Retained Executable Summary
* **Front**: What is the final production policy decision, which file implements it, and what are its exact operational rules?
* **Back**:
  - **Retained Policy**: Supplied Baseline Greedy ($G$), implemented in [`policy.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/policy.py).
  - **Asks Rule**: FIFO hard-bundle asks (`constraints`, cost 3, up to 4 asks/day) sorted by public member-list order. Zero soft asks.
  - **Scoring Rule**: Number of matching, observed soft-field attributes ($S_{uv} = \sum_f \mathbf{1}\{x_{uf} = x_{vf} \neq \text{null}\}$).
  - **Matching Rule**: Greedy maximal matching sorted descending by soft score, with deterministic tie-breaks based on member IDs. Zero reservation threshold.
