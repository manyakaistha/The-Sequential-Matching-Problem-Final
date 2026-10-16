# 02. Mathematical Foundations: Graphs, Correlated Probabilities & Calibration

This document develops the theoretical and mathematical foundations of sequential reciprocal matching: combinatorial optimization on general non-bipartite graphs, correlated reciprocal probability models, latent chemistry integration, statistical calibration, and information acquisition dynamics.

---

## 1. Disambiguation: "PS" in Algorithmic Formulation

* **PS (Problem Statement)**: The external environmental specification ([`PROBLEM_STATEMENT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/PROBLEM_STATEMENT.md)).
* **PS (Parametric Scorer)**: The algorithmic family of multi-stage scoring models (`PS_sim`, `PS_emp`, `PS_flat`) defined in [`research9/round2/policies/model.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research9/round2/policies/model.py). The parametric scorer computes edge weights using simulated or empirical posterior estimates of acceptance and meeting intentions.

---

## 2. Combinatorial Optimization & General Graph Matching

### Layer 1: The Question
Why is bipartite matching insufficient for the reciprocal introduction problem, and why does myopic Maximum Weight Matching (MWM) or Maximum Cardinality Matching (Blossom) fail to achieve dynamic optimality across sequential rounds?

### Layer 2: Intuition
1. **Non-Bipartite Structure**: The pool contains individuals of diverse genders (`woman`, `man`, `non_binary`) with heterogeneous `who_to_meet` preferences. Because men can meet men, women can meet women, and non-binary individuals can meet any gender, the compatibility graph $G = (V, E)$ contains odd cycles (triangles, 5-cycles). It is a **general (non-bipartite) graph**.
2. **Myopic vs. Dynamic Opportunity Cost**: In static graph theory, Edmonds' Blossom algorithm finds the global maximum weight matching. However, in an online sequential process with stochastic arrivals and departures, matching a vertex today forfeits its option value tomorrow (the "price of anarchy" in online allocation).

### Layer 3: Minimal Concrete Counterexample: Blossom vs. Waiting
Consider a 2-day horizon with vertices $\{A, B, C\}$. On Day 0, vertices $A$ and $B$ are available with a single feasible edge $(A, B)$ of expected value $V(A, B) = 0.20$. Member $C$ is known to arrive on Day 1 with high probability, having expected values $V(A, C) = 0.85$ and $V(B, C) = 0.10$.

```
Day 0 Topology:                  Day 1 Prospective Topology:
    A ────────────── B                     A ══════════════ C (V = 0.85)
        V = 0.20                           │
                                           │ V = 0.20
                                           │
                                           B ────────────── C (V = 0.10)
```

* **Myopic Maximum Cardinality / Weight (Blossom on Day 0)**:
  1. Day 0: Matches $(A, B)$ with value $0.20$.
  2. Day 1: $A$ and $B$ are busy. $C$ arrives with degree 0 among available members.
  3. Total Value = $\mathbf{0.20}$.
* **Dynamic Reservation Policy (Waiting on Day 0)**:
  1. Day 0: Submits `pairs = []` (waits).
  2. Day 1: $C$ arrives. Matches $(A, C)$ with value $0.85$.
  3. Total Value = $\mathbf{0.85}$ (a **$325\%$ gain**).

### Layer 4: Formal Graph Definitions
Let $G_t = (V_t, E_t)$ be an undirected, edge-weighted graph at day $t$:
* **Matching**: A subset $\mathcal{M} \subseteq E_t$ such that no two edges share a common vertex:
  $$\forall e_1, e_2 \in \mathcal{M}, \quad e_1 \cap e_2 = \emptyset \quad (e_1 \neq e_2).$$
* **Maximal Matching**: A matching $\mathcal{M}$ where no edge from $E_t \setminus \mathcal{M}$ can be added without violating the matching property.
* **Maximum Cardinality Matching (MCM)**: A matching that maximizes $|\mathcal{M}|$. On general graphs, computed in $\mathcal{O}(|V|^2 |E|)$ via Edmonds' Blossom Algorithm using blossom shrinking on odd alternating cycles.
* **Maximum Weight Matching (MWM)**: A matching that maximizes $\sum_{e \in \mathcal{M}} w(e)$, solvable via primal-dual interior point or blossom scaling methods.
* **Greedy Maximal Matching**: Sequentially adds the highest-weight available edge and removes both incident vertices. Guarantees a $\frac{1}{2}$-approximation to static MWM:
  $$\sum_{e \in \mathcal{M}_{\text{greedy}}} w(e) \ge \frac{1}{2} \sum_{e \in \mathcal{M}_{\text{opt}}} w(e).$$

### Layer 5: Algorithm Comparison

```python
# Comparison of Allocation Paradigms
def greedy_maximal_matching(nodes, edges, weights):
    """Greedy 1/2-approximation, O(|E| log |E|)."""
    sorted_edges = sorted(edges, key=lambda e: weights[e], reverse=True)
    matching, used = [], set()
    for u, v in sorted_edges:
        if u not in used and v not in used:
            matching.append((u, v))
            used.add(u); used.add(v)
    return matching
```

In [`kit.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/kit.py#L210-L225), the reference baseline implements a deterministic greedy maximal matching where edge weight is the count of matching observed soft fields:

```python
# From kit.py: baseline_match()
def baseline_match(state):
    members = [m for m in state['members'] if m['available']]
    past = {tuple(sorted((i['user_a'], i['user_b']))) for i in state['introductions']}
    edges = []
    for a, b in itertools.combinations(members, 2):
        key = tuple(sorted((a['member_id'], b['member_id'])))
        if key in past or eligibility(a, b)['status'] != 'feasible':
            continue
        score = sum(a['fields'].get(k) is not None and a['fields'].get(k) == b['fields'].get(k) for k in SOFT)
        edges.append((-score, key))
    used = set(); out = []
    for _, pair in sorted(edges):
        if not used.intersection(pair):
            out.append(list(pair))
            used.update(pair)
    return out
```

### Layer 6: Empirical Benchmark Results
In [`final_report/REPORT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/final_report/REPORT.md#L140-L160), empirical tests across 1,152 episodes in the Q1 study show:
* Greedy matching by soft agreement (`G`) achieves **0.4557 MSMI/100** (175 qualified pairs).
* Degree-prioritized matching (`G_deg`) achieves **0.3880 MSMI/100** (a drop of $-0.0677$, 95% CI $[-0.2408, +0.1054]$).
* Random-order matching (`R`) on the historical baseline grid achieves **0.3167 MSMI/100** vs. Greedy's **0.3500**.

See [Figure 1: Exploratory Paired Arm Contrasts](assets/02_robustness_contrasts.png).

---

## 3. Reciprocal Probability Theory & Correlated Chemistry

### Layer 1: The Question
If person $A$ has probability $p_{A \to B}$ of accepting $B$, and person $B$ has probability $p_{B \to A}$ of accepting $A$, under what mathematical conditions is the probability of mutual acceptance $P(A \leftrightarrow B) = p_{A \to B} \times p_{B \to A}$? Why does this independence assumption collapse in realistic human matching and in the simulator?

### Layer 2: Intuition
Romantic chemistry is an interaction phenomenon, not two isolated coin flips. When two people meet, shared environmental factors, mutual conversational flow, and serendipitous rapport simultaneously affect both participants. If one person experiences high rapport, the other person is much more likely to experience high rapport. Mathematically, this manifests as a **latent random effect** (shared chemistry) that enters both utility functions. Conditioning on observed attributes alone leaves this variable unobserved, inducing **positive covariance**.

```
                Unobserved Latent Chemistry: γ ~ Normal(0, 0.45²)
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       A's Logit Acceptance            B's Logit Acceptance
         zA = ... + γ                    zB = ... + γ
                 │                               │
                 ▼                               ▼
        A Accepts: yA = 1               B Accepts: yB = 1
```

### Layer 3: Minimal Concrete Example: The Covariance Gap
Suppose for a given pair, $A$ and $B$ have baseline log-odds $z_0 = 0$. In $50\%$ of encounters, the shared chemistry is positive ($\gamma = +1.0$), making $z = +1.0$ ($p \approx 0.731$). In $50\%$ of encounters, shared chemistry is negative ($\gamma = -1.0$), making $z = -1.0$ ($p \approx 0.269$).

1. **Directional Marginal Probability for $A$**:
   $$P(A \to B) = 0.5 \times 0.731 + 0.5 \times 0.269 = \mathbf{0.500}$$
2. **Directional Marginal Probability for $B$**:
   $$P(B \to A) = 0.5 \times 0.731 + 0.5 \times 0.269 = \mathbf{0.500}$$
3. **Naive Product (Independence Assumption)**:
   $$P_{\text{naive}}(A \leftrightarrow B) = P(A \to B) \times P(B \to A) = 0.500 \times 0.500 = \mathbf{0.250}$$
4. **True Correlated Joint Probability**:
   $$P_{\text{true}}(A \leftrightarrow B) = \mathbb{E}_\gamma [P(A \to B \mid \gamma) P(B \to A \mid \gamma)] = 0.5(0.731)^2 + 0.5(0.269)^2 = 0.267 + 0.036 = \mathbf{0.303}$$

The naive product underestimates mutual acceptance by **$21.2\%$** because $\text{Cov}(y_A, y_B) > 0$.

### Layer 4: Mathematical Derivation: Generative Formulation
In [`kit.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/kit.py#L145-L160), the exact generative likelihood is formulated as follows:

Let $f_A, f_B$ be the ground truth attributes of members $A$ and $B$.
1. **Soft Feature Fit**:
   $$\text{fit}(A, B) = \sum_{k \in \mathcal{K}_{\text{soft}}} w_k \cdot \phi(f_A[k], f_B[k]), \quad \phi(u, v) = \begin{cases} +1.0 & \text{if } u = v \\ -0.5 & \text{if } u \neq v \end{cases}$$
   Where base weights are:
   $$w_{\text{goal}} = 0.7, \quad w_{\text{pace}} = 0.4, \quad w_{\text{lifestyle}} = 0.25, \quad w_{\text{conversations}} = 0.20.$$
2. **Latent Latent Variables**:
   * Individual member biases: $\alpha_A \sim \mathcal{N}(0, 0.7^2)$, $\alpha_B \sim \mathcal{N}(0, 0.7^2)$.
   * Response rates: $\rho_A, \rho_B \sim \text{Uniform}(0.55, 0.98)$.
   * Shared dyadic chemistry: $\gamma_{AB} \sim \mathcal{N}(0, 0.45^2)$.
3. **Directional Acceptance Probability**:
   $$z_{A \to B} = -0.25 + \alpha_A + \text{fit}(A, B) + \gamma_{AB} + \delta_{\text{drift}}$$
   $$p_{A \to B}(\gamma_{AB}) = \sigma(z_{A \to B}) = \frac{1}{1 + e^{-z_{A \to B}}}$$
4. **Joint Mutual Acceptance Likelihood**:
   $$P(A \leftrightarrow B \mid f_A, f_B, \alpha_A, \alpha_B) = \rho_A \rho_B \int_{-\infty}^{\infty} \sigma(z_{A \to B}(\gamma)) \sigma(z_{B \to A}(\gamma)) \frac{1}{\sqrt{2\pi}\sigma_\gamma} e^{-\frac{\gamma^2}{2\sigma_\gamma^2}} \, d\gamma$$
   By Chebyshev's association inequality, because $\sigma(z)$ is monotonically increasing in $\gamma$, the integrand satisfies:
   $$\mathbb{E}[\sigma(z_A(\gamma))\sigma(z_B(\gamma))] > \mathbb{E}[\sigma(z_A(\gamma))] \cdot \mathbb{E}[\sigma(z_B(\gamma))].$$

### Layer 5: Downstream Conditional Delay Derivation
Following mutual acceptance, a date occurs with probability $P(\text{date} \mid A \leftrightarrow B) = 0.78$.
Given that a date occurs at day $d$, members independently submit second-meeting responses with delay $\Delta \tau_A, \Delta \tau_B \sim \text{DiscreteUniform}\{1, 2, 3, 4, 5\}$.
The requirement for MSMI qualification is that both responses arrive within 3 days:
$$\Delta \tau_A \le 3 \quad \text{and} \quad \Delta \tau_B \le 3.$$
Under discrete uniform independence:
$$P(\text{timely} \mid \text{second meeting response}) = \left(\frac{3}{5}\right) \times \left(\frac{3}{5}\right) = \frac{9}{25} = \mathbf{0.36}$$
Thus, **$64\%$ of mutually positive second-meeting intentions are filtered out purely by response delay!**

---

## 4. Statistical Estimation, Scoring & Calibration

### 4.1 Brier Score & The Rare-Event Fallacy
The Brier score measures mean squared prediction error for binary outcomes $y \in \{0, 1\}$ with predicted probabilities $\hat{p} \in [0, 1]$:

$$\text{BS} = \frac{1}{K} \sum_{k=1}^K (\hat{p}_k - y_k)^2$$

* **The Fallacy of Low Brier Scores**: In [`final_report/REPORT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/final_report/REPORT.md#L240-L260), the observed terminal qualified outcome rate is only $1.24\%$.
* A trivial predictor that constantly predicts $\hat{p} = 0.0$ achieves:
  $$\text{BS}_{\text{zero}} = 0.012378$$
* The complex `PS_sim` model achieves $\text{BS} = 0.012193$, and `PS_emp` achieves $\text{BS} = 0.012250$.
* *Insight*: An ultra-low Brier score ($0.012$) is an artifact of outcome sparsity, **not** proof of predictive prowess or ranking utility.

### 4.2 Expected Calibration Error (ECE) & Reliability Diagrams
Given $B$ probability bins $I_b = (l_b, u_b]$:

$$\text{ECE} = \sum_{b=1}^B \frac{|K_b|}{K} \left| \bar{y}_b - \bar{p}_b \right|$$

Where $\bar{y}_b$ is the empirical fraction of positives in bin $b$ and $\bar{p}_b$ is the mean predicted probability.
* In the benchmark calibration audit ([Figure 5](assets/06_calibration.png)), `PS_emp` exhibits an ECE of $0.007425$, underpredicting the terminal outcome rate by $-0.648$ percentage points.

```
       Reliability Diagram (Calibration)
       1.0 ┌─────────────────────────────/
           │                            /
  Empirical│                           /
  Positive │                          /
    Rate   │                         /  Ideal: y = p
   (y_bar) │                        /
           │           ┌───┐       /
           │           │   │      /
       0.0 └───┴───┴───┴───┴─────/───────
           0.0                 1.0
             Predicted Probability (p_bar)
```

### 4.3 Directional Calibration in Adaptive Policy X1
In [`research9/round2/policies/model.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research9/round2/policies/model.py), policy `X1` adjusts for environmental drift by estimating a logit offset $\hat{\Delta}$ over a rolling 21-day window of observed introduction responses. To prevent noise amplification, it applies a **conservative shrinkage operator**:

$$\Delta_{\text{applied}} = \text{sign}(\hat{\Delta}) \cdot \max\left(0, \; |\hat{\Delta}| - 1.64485 \cdot \text{SE}(\hat{\Delta})\right)$$

Where $1.64485$ corresponds to the 95th percentile of the standard normal distribution (one-sided $z$-score).
* *Operational Consequence*: In [`final_report/REPORT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/final_report/REPORT.md#L210-L230), testing `X1` with and without calibration (`X1_emp` vs. `X1_nocal_emp`) left **all 72 action digests completely identical**. Shifting predicted probabilities uniformly across edges did not alter the relative order of edges, leaving greedy matching decisions unchanged.

See [Figure 4: Adaptive Ablations](assets/05_adaptive_ablations.png) and [Figure 6: Drift Calibration](assets/07_drift_calibration.png).

---

## 5. Information Acquisition & Query Submodularity

### 5.1 Hard Bundles vs. Soft Fields
* **Constraint Bundle** (Cost 3): Simultaneously reveals all 11 hard fields for member $u$.
* **Soft Query** (Cost 1): Reveals a single soft attribute (e.g., `lifestyle`).

### 5.2 Complementarity of Hard Queries
Information acquisition in matching is **supermodular (complementary)** rather than submodular:
* If member $A$ is unclarified and member $B$ is unclarified, querying $A$ alone yields $0$ feasible edges if $B$ remains unclarified.
* Querying $B$ alone yields $0$ feasible edges.
* Querying **both** $A$ and $B$ reveals whether edge $(A, B)$ is feasible, unlocking positive value:
  $$V(A \cup B) > V(A) + V(B).$$
This structural complementarity inspired the `Q6` (coordinated acquisition) algorithm, which coordinates budget across pairs. However, confirmatory testing in Stage E across 6,852 episodes showed no statistically significant gain over baseline Greedy list-order questioning ($+0.0032$ MSMI/100, $p = 0.765$; see [Figure 11](assets/01_confirmation_context.png)).

---

Proceed to [03. Simulator Protocol, Event Timeline, and Execution Architecture](03_simulator_protocol_and_event_timeline.md).
