# Chapter 7: Sequential Decision Theory, POMDPs, and Dynamic Formulations

## 1. Formal Mathematical Formulation: The Sequential Matching POMDP

The Sequential Reciprocal Matching Problem is a finite-horizon, discrete-time, partially observable Markov decision process (POMDP) operating over calendar days $t \in \{0, 1, \dots, T-1\}$ with $T = 60$ action days, followed by an offline feedback monitoring phase up to Day 100.

```
       Latent State Z_t (Hidden from Policy)
  [Preferences, Biases, Response Propensities, Scheduled Events, Exits]
                         │
                         ▼ (Emission Kernel)
     Public Observation History O_t = (M_t, A_t, B_t, H_t, L_t, P_t)
                         │
                         ▼
        Belief State b_t = P(Z_t | O_{0:t}, a_{0:t-1})
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
   Ask Stage: Q_t                  Match Stage: X_t
   V_t^ask(b)                      V_t^match(b)
```

---

### 1.1 State Space Definitions
1. **The Latent World State $Z_t$**:
   Contains all ground-truth parameters governing the simulator:
   $$Z_t = \left( \{ \theta_i^{\text{truth}} \}_{i=1}^N, \{ \beta_i \}_{i=1}^N, \{ R_i \}_{i=1}^N, \{ \beta_i^{\text{second}} \}_{i=1}^N, \{ \tau_i^{\text{exit}} \}_{i=1}^N, \mathcal{S}_t^{\text{future}}, \Omega^{\text{regime}} \right)$$
   where:
   - $\theta_i^{\text{truth}}$: Complete vector of all 11 hard and 7 soft preferences.
   - $\beta_i \sim \mathcal{N}(0, 0.7^2)$: Unobserved sociability bias.
   - $R_i \sim \text{Uniform}[0.55, 0.98]$: Latent response propensity.
   - $\beta_i^{\text{second}} \sim \mathcal{N}(0, 0.5^2)$: Second-meeting intention bias.
   - $\tau_i^{\text{exit}} \in \{22, \dots, 60\} \cup \{\infty\}$: Exogenous departure day (12% of population).
   - $\mathcal{S}_t^{\text{future}}$: Pre-scheduled future events (e.g., date days, response arrivals).
   - $\Omega^{\text{regime}}$: Environmental law (weights, delays, arrival waves, drift).

2. **The Public Observation Record $O_t$**:
   $$O_t = (M_t, \mathcal{A}_t, \mathcal{B}_t, \mathcal{H}_t, \mathcal{L}_t, \mathcal{P}_t, t, B_t)$$
   where:
   - $M_t$: Member demographic records arrived by day $t$.
   - $\mathcal{A}_t \in \{0, 1\}^{|M_t|}$: Public availability indicator vector.
   - $\mathcal{B}_t$: Elapsed times of pending introductions. Note: $\mathcal{B}_t$ is **not** the true busy release time; future date schedules are hidden!
   - $\mathcal{H}_t$: Complete log of all public feedback events observed $\le t$.
   - $\mathcal{L}_t$: Clarification log of all historical ask queries and disclosures.
   - $\mathcal{P}_t$: Historical set of introduced dyads (preventing repeats).
   - $B_t$: Remaining query budget for the day ($B_t = 12$ at dawn).

3. **The Belief State $b_t$**:
   Because $Z_t$ is hidden, the policy's exact decision state is the posterior distribution:
   $$b_t = \mathbb{P}(Z_t \mid O_0, a_0, O_1, a_1, \dots, O_t)$$

---

### 1.2 Two-Stage Daily Bellman Recursion
Each action day $t \in \{0, \dots, 59\}$ consists of two coupled sub-stages:

1. **The Ask Stage Value Function**:
   $$V_t^{\text{ask}}(b) = \max_{Q \in \mathcal{Q}} \mathbb{E}_{Y_Q \sim b} \left[ V_t^{\text{match}}(\text{Bayes}(b, Y_Q)) \right]$$
   subject to the budget constraint:
   $$\sum_{q \in Q} \text{cost}(q) \le 12, \quad \text{cost}(q) = \begin{cases} 3 & \text{if } q = \text{'constraints'} \\ 1 & \text{if } q \in \text{SOFT} \end{cases}$$
   where $Y_Q$ is the stochastic answer vector returned by the simulator, and $\text{Bayes}(b, Y_Q)$ is the updated posterior belief.

2. **The Match Stage Value Function**:
   $$V_t^{\text{match}}(b) = \max_{X \in \mathcal{M}(b)} \mathbb{E}_{Y_{t+1}} \left[ r_t(X) + V_{t+1}^{\text{ask}}(\text{Bayes}(b, Y_{t+1})) \right]$$
   where:
   - $X \subseteq \binom{\mathcal{A}_t}{2}$ is a set of disjoint pairs satisfying:
     $$\sum_{j : (i, j) \in X} 1 \le 1 \quad \forall i \in \mathcal{A}_t$$
     $$\text{eligibility}(i, j \mid b) = \text{'feasible'} \quad \forall (i, j) \in X$$
     $$(i, j) \notin \mathcal{P}_t \quad \forall (i, j) \in X$$
   - $r_t(X)$ is the immediate qualified reward observed on day $t$.

---

### 1.3 The Day 60 Horizon and Follow-Up Bookkeeping
What is the terminal continuation value $V_{60}(b)$?
In an environment where feedback terminates strictly at Day 60, one would set $V_{60} = 0$. However, in this problem, the simulator runs an **offline follow-up window from Day 60 to Day 100**:
$$V_{60}(b) = \mathbb{E}\left[ \sum_{m \in \text{Pending}_{60}} \mathbb{I}(\text{qualified MSMI observed by Day 100}) \ \Bigg|\ b \right] \ne 0$$
Introductions assigned on Day 59 mature between Days 61 and 97.
- **Equivalent Bookkeeping Transformation**: By linearity of expectation, one can book the **expected eventual qualified reward** $q(e, t)$ at the exact moment of assignment:
  $$\tilde{r}_t(X) = \sum_{e \in X} q(e, t)$$
  Under this transformed reward structure, the terminal value for future assignments is strictly zero:
  $$\tilde{V}_{60}(b) = 0$$
  This identity holds because future introductions are impossible after Day 59, and all pending reward expectations have already been booked.

---

### 1.4 Why Independent Optimization Over Hidden States Is an Illegal Oracle
A common error in theoretical benchmarking is to compute an offline upper bound by solving an unconstrained maximum matching over the true latent graph $Z$:
$$\max_X \sum_{e \in E(Z)} R_e X_e$$
This represents an **illegal oracle** for three mathematical reasons:
1. **Violation of Non-Anticipativity**: An oracle uses knowledge of future arrival dates ($\tau_i^{\text{arr}} \le 20$), exact departure days $\tau_i^{\text{exit}}$, and realized PRNG delay draws to time introductions perfectly before an agent departs.
2. **Path-Dependent Availability**: In reality, matching member $a$ with $b$ on Day 5 alters $a$'s availability for the next $8$ to $38$ days. An offline solver that treats edges as independent potential outcomes selects edges that are mutually incompatible in physical time.
3. **Information Constrained Feasibility**: An agent cannot introduce pair $(a, b)$ unless both have verified hard constraints. Revealing constraints requires daily budget expenditure ($B \le 12$). An oracle that assumes costless visibility over $Z$ optimizes over an unattainable information relaxation.

---

## 2. Nonseparable Continuation Values & Failure of Node Prices

Can the dynamic matching problem be solved by assigning each individual agent an opportunity cost (or shadow price) $\lambda_i$, matching edge $(i, j)$ whenever its reward exceeds $\lambda_i + \lambda_j$?

### 2.1 Failure of Gittins and Whittle Indices
- **Gittins Index Failure**: The classical Gittins index theorem requires independent multi-armed bandits where:
  1. Exactly one arm is pulled at each step.
  2. The pulled arm transitions Markovianly.
  3. All unpulled (passive) arms remain completely frozen.
  In reciprocal matching, pulling dyad $(i, j)$ simultaneously activates endpoint $i$ and endpoint $j$, altering the availability, future partner pool, and exit hazards of all alternative dyads $(i, k)$ and $(j, l)$. The arms are deeply coupled through node-sharing.
- **Whittle Index Failure**: Whittle's restless bandit relaxation requires proving **indexability**: that the set of states where an arm is passive increases monotonically as a subsidy for passivity increases. In general-graph matching with node constraints and 60-day deadlines, passive set monotonicity does not hold.

---

### 2.2 The Nonseparable Alternatives Counterexample
From [`research6/exact/THEORY.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research6/exact/THEORY.md):

Consider four members $A, B, C, D$ evaluated at Day $t$:
- Current legal edges: $e_1 = (A, B)$ and $e_2 = (C, D)$. Each earns expected reward $q(e_1) = 1/2, q(e_2) = 1/2$.
- Both current edges retire their endpoints with probability $1$.
- Tomorrow (Day $t+1$), an alternative edge $e_3 = (A, C)$ becomes available, with high reward $q(e_3) = 9/10$.
- Endpoint $B$ and endpoint $D$ have zero future alternatives.

```
       Day t:  A ────── B   (q = 1/2)         C ────── D   (q = 1/2)
               │                               │
               :                               :
       Day t+1: └ - - - - - - - - - - - - - - - ┘
                           A ────── C   (q = 9/10)
```

#### Evaluation of Value Functions:
- If neither is assigned today, both $A$ and $C$ survive to Day $t+1$:
  $$V_{t+1}(\{A, B, C, D\}) = V_{t+1}(\{A, C\}) = \frac{9}{10}$$
- If only $A$ survives (or only $C$ survives), edge $(A, C)$ cannot form:
  $$V_{t+1}(\{A\}) = 0, \quad V_{t+1}(\{C\}) = 0, \quad V_{t+1}(\emptyset) = 0$$

#### The Failure of Additive Node Opportunity Costs:
Suppose an algorithm assigns individual opportunity costs to nodes based on their isolated standalone continuation value loss:
- Standalone opportunity cost of matching $A$:
  $$\Delta V_A = V_{t+1}(\{A, C\}) - V_{t+1}(\{C\}) = \frac{9}{10} - 0 = \frac{9}{10}$$
- Standalone opportunity cost of matching $C$:
  $$\Delta V_C = V_{t+1}(\{A, C\}) - V_{t+1}(\{A\}) = \frac{9}{10} - 0 = \frac{9}{10}$$
- **Subtractive Decision Rule**:
  - Score for $AB$: $q(AB) - \Delta V_A = \frac{1}{2} - \frac{9}{10} = -0.4 < 0 \implies \text{Reject } AB$.
  - Score for $CD$: $q(CD) - \Delta V_C = \frac{1}{2} - \frac{9}{10} = -0.4 < 0 \implies \text{Reject } CD$.
  - Both edges are rejected! The policy waits for tomorrow, earning total value:
    $$V_{\text{wait}} = \frac{9}{10} = 0.90$$
- **The True Combinatorial Choice**:
  - What if the policy assigns **both** $AB$ and $CD$ today?
  - Total reward today:
    $$W(AB) + W(CD) = \frac{1}{2} + \frac{1}{2} = 1.00$$
  - Since $1.00 > 0.90$, assigning both pairs today is strictly superior to waiting!
- **Why Separable Shadow Prices Fail**:
  Independently penalizing $AB$ by $9/10$ and $CD$ by $9/10$ **double-counts the same single future opportunity** $(A, C)$. Because $A$ and $C$ can only form one pair tomorrow, the total system opportunity loss of matching both is $9/10$, not $9/10 + 9/10 = 1.8$. Dynamic continuation values on graphs are inherently **nonseparable set functions**.

---

## 3. Stopping Thresholds, Reservation Values, and Monotonicity

In dynamic matching, when should an agent reject a currently available feasible partner to wait for a better future arrival?

### 3.1 Single-Agent Search Formulation
Consider a simplified single agent who receives independent offers $R_t \sim F$ at each calendar day $t \in \{0, \dots, T-1\}$.
At each day, the agent can either accept $R_t$ (terminating the process with reward $R_t$) or reject it.
If rejected, the agent survives to tomorrow with probability $(1 - h_t)$, where $h_t \in [0, 1]$ is the departure hazard.
The dynamic programming recursion is:
$$V_t = \mathbb{E}\left[ \max(R_t, (1 - h_t) V_{t+1}) \right], \quad V_T = 0$$
The optimal policy is a reservation threshold policy:
$$\text{Accept } R_t \iff R_t \ge c_t \quad \text{where} \quad c_t = (1 - h_t) V_{t+1}$$

> [!WARNING]
> A frequent conceptual error is asserting that the reservation threshold equals $V_t - \mathbb{E}[V_{t+1}]$.
> **Counterexample**: Suppose $h_t = 0$, $T = 2$, and $R_1 \sim \text{Uniform}[0, 1]$.
> At $t = 1$, $V_1 = \mathbb{E}[R_1] = 1/2$.
> At $t = 0$, the threshold is $c_0 = V_1 = 1/2$.
> However, $V_0 = \mathbb{E}[\max(R_0, 1/2)] = \int_0^{1/2} \frac{1}{2} dr + \int_{1/2}^1 r dr = \frac{1}{4} + \left[ \frac{r^2}{2} \right]_{1/2}^1 = \frac{1}{4} + \frac{3}{8} = \frac{5}{8}$.
> Then $V_0 - V_1 = \frac{5}{8} - \frac{1}{2} = \frac{1}{8} \ne c_0 = \frac{1}{2}$!

---

### 3.2 Monotonicity Theorem Under Stationary i.i.d. Conditions
**Theorem (Nonincreasing Thresholds)**: If offer distributions $R_t \sim F$ are stationary and non-negative, exit hazards are non-decreasing ($h_t \le h_{t+1}$), and terminal value $V_T = 0$, then the reservation threshold $c_t$ is monotonically nonincreasing in calendar time:
$$c_t \ge c_{t+1} \quad \forall t$$

**Proof**:
By backward induction:
1. Base case: $V_{T-1} = \mathbb{E}[R_{T-1}] \ge 0 = V_T$.
2. Induction hypothesis: Assume $V_{t+1} \ge V_{t+2}$.
3. Since $h_t \le h_{t+1}$, we have $(1 - h_t) \ge (1 - h_{t+1}) \ge 0$.
4. Multiplying inequalities:
   $$c_t = (1 - h_t) V_{t+1} \ge (1 - h_{t+1}) V_{t+2} = c_{t+1}$$
5. Now consider the value function $V_t$:
   $$V_t = \mathbb{E}[\max(R, c_t)]$$
   The function $g(c) = \mathbb{E}[\max(R, c)]$ is monotonically nondecreasing in $c$.
   Since $c_t \ge c_{t+1}$, it follows that $V_t \ge V_{t+1}$.
6. This completes the induction: $c_t \ge c_{t+1}$ for all $t$. $\blacksquare$

---

### 3.3 Why Real Market Dynamics Violate Monotonicity
The stationary i.i.d. assumption is completely violated in the actual sequential matching simulator:
1. **Finite Arrival Window**: In [`kit.py:L58`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/kit.py#L58), all exogenous member arrivals occur on or before **Day 20** ($t_{\text{arr}} \le 20$). After Day 20, zero new members enter the market!
2. **Depletion of Feasible Partners**: As the 60-day action horizon progresses, compatible members are either matched, paused, or exhausted (due to the strict no-repeat introduction rule).
3. **Returning Waves from Unsuccessful Dates**: Agents whose dates do not result in mutual second-meeting intention re-enter the pool after $8$ to $25$ days.
4. **Counterexample to Monotonicity**: If a member has exhausted all compatible partners on Day 14, their expected offer tomorrow is zero ($c_{14} \approx 0$). However, on Day 15, a wave of newly arrived compatible members enters the pool, raising $c_{15} > 0$. Thus, $c_t$ is **not monotonic** over calendar time.

---

## 4. The Continuous Renewal Occupancy LP Upper Bound

From [`research6/exact/THEORY.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research6/exact/THEORY.md), one can construct an optimistic, continuous linear programming upper bound on the maximum possible expected reward achievable by any adapted policy.

### 4.1 The Occupancy Indicator Kernel
For any candidate introduction of dyad $e = (i, j)$ assigned on day $t$:
- Let $R(e, t)$ be the eventual qualified reward.
- Let $U_i(e, t; s) \in \{0, 1\}$ be the **occupancy indicator**, equal to $1$ if the assignment prevents endpoint $i$ from being legally matched on day $s \ge t$, and $0$ otherwise.
- The simulator enforces:
  - Non-mutual introductions: busy until $t+8 \implies U_i(e, t; s) = 1$ for $s \in [t, t+7]$.
  - Mutual introductions: busy until $\text{date} + 6 \implies U_i(e, t; s) = 1$ through release.
  - Positive pause (both say yes to 2nd date): permanently unavailable through $T \implies U_i(e, t; s) = 1$ for all $s \ge t$.

### 4.2 The Renewal LP Formulation
Taking expectations conditional on ground truth $Z$:
- $x(e, t) = \mathbb{E}[X(e, t) \mid Z] \in [0, 1]$: Marginal probability of assigning $(e, t)$.
- $q(e, t) = \mathbb{E}[R(e, t) \mid Z]$: Expected qualified reward.
- $u_i(e, t; s) = \mathbb{E}[U_i(e, t; s) \mid Z]$: Expected occupancy probability at day $s$.

$$\begin{aligned}
\text{Maximize} \quad & \sum_{e, t} q(e, t) x(e, t) \\
\text{Subject to} \quad & x(e, t) \ge 0 \quad \forall e, t \\
& \sum_{t=0}^{59} x(e, t) \le 1 \quad \forall e \quad \text{(No repeat introductions)} \\
& \sum_{e \ni i} \sum_{t \le s} u_i(e, t; s) x(e, t) \le 1 \quad \forall i \in M, \ \forall s \in \{0, \dots, 59\} \quad \text{(Unit node capacity)}
\end{aligned}$$

**Theorem (Valid Relaxation)**: Every legal adapted policy $\pi$ maps to a feasible point $x^{\pi}$ of this LP. Therefore, the optimal value $\text{LP}^*(Z)$ bounds the expected reward of any policy:
$$\mathbb{E}[\text{Reward}(\pi) \mid Z] \le \text{LP}^*(Z)$$

---

## 5. The 0.36 Timing Factor: Derivation, Assumptions, and Scope

In Section 8.2 of the Final Report and [`research4/DEADLINE_INVARIANCE.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research4/DEADLINE_INVARIANCE.md), a fundamental mathematical constant appears: the **$0.36$ qualification factor**.

### 5.1 Complete Mathematical Derivation
In [`kit.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/kit.py#L178-L197), after an in-person date successfully occurs, both participants submit second-meeting intentions.
1. The submission delay for each actor is sampled independently:
   $$\text{delay}_a \sim \text{Uniform}\{1, 2, 3, 4, 5\}$$
   $$\text{delay}_b \sim \text{Uniform}\{1, 2, 3, 4, 5\}$$
   with $\text{delay}_a \perp \text{delay}_b$.
2. To count as a **qualified** Mutual Second-Meeting Intention in the official metric ([`kit.py:L197`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/kit.py#L197)):
   ```python
   msmi += bool(ds) and ds[0]['occurred_day'] - intro['assigned_day'] <= 30 \
           and len(ss) == 2 and all(e['value'] == 'yes' and e['occurred_day'] - ds[0]['occurred_day'] <= 3 for e in ss)
   ```
   Both second-meeting intention events must satisfy:
   $$\text{delay} \le 3 \text{ days}$$
3. For a single member, the probability of submitting within the 3-day window is:
   $$P(\text{delay} \le 3) = \frac{|\{1, 2, 3\}|}{|\{1, 2, 3, 4, 5\}|} = \frac{3}{5} = 0.60$$
4. Since the simulator samples delays independently for actor $a$ and actor $b$:
   $$P(\text{delay}_a \le 3 \land \text{delay}_b \le 3) = P(\text{delay}_a \le 3) \times P(\text{delay}_b \le 3) = \left(\frac{3}{5}\right)^2 = \frac{9}{25} = 0.36$$

```
   Actor A Delay \ Actor B Delay │  1   2   3 │  4   5  │
   ──────────────────────────────┼────────────┼─────────┤
                 1               │  ✓   ✓   ✓ │  ✗   ✗  │
                 2               │  ✓   ✓   ✓ │  ✗   ✗  │
                 3               │  ✓   ✓   ✓ │  ✗   ✗  │
   ──────────────────────────────┼────────────┼─────────┤
                 4               │  ✗   ✗   ✗ │  ✗   ✗  │
                 5               │  ✗   ✗   ✗ │  ✗   ✗  │

   Qualified Cells (✓): 9 out of 25 = 36.0%
   Disqualified by Deadline Friction (✗): 16 out of 25 = 64.0%
```

---

### 5.2 Assumptions and Exact Scope
1. **Conditional Scope**: The $0.36$ factor applies **strictly conditional** on the event that:
   - The introduction achieved mutual acceptance;
   - The date successfully occurred;
   - The date occurred within 30 days of introduction ($\text{date} - t \le 30$);
   - Both members submitted an intention of `'yes'`.
2. **Law Specificity**: It assumes the standard generative delay distribution $\text{Uniform}\{1, \dots, 5\}$. If an environmental law modifies response delays (such as `R_late` where response delays increase), the factor changes.
3. **Severe Attrition**: This derivation proves that **$64\%$ of all pairs who genuinely like each other and desire a second meeting are disqualified purely by submission latency friction!**

---

### 5.3 The Deadline Invariance Theorem & Variance-Reduced Diagnostic
From [`research4/DEADLINE_INVARIANCE.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research4/DEADLINE_INVARIANCE.md):

**Theorem (Action Invariance to Second Delays)**: Changing second-feedback delays between $1$ and $5$ days does not change availability release dates (which are fixed at $\text{date} + 6$). Therefore, the policy's action sequence is **completely invariant** to second-feedback delay draws.

This invariance allows constructing an analytical, **variance-reduced expected proxy**:
Let $K$ be the number of date-qualified, both-yes pairs across an episode.
Conditional on the delay-erased trajectory:
$$\mathbb{E}[\text{Qualified MSMI} \mid K] = 0.36 \times K$$
$$\text{MSMI/100}_{\text{proxy}} = 100 \times \frac{0.36 \times K}{N} = \frac{36 \times K}{N}$$
For a population of $N = 200$, this simplifies to:
$$\text{MSMI/100}_{\text{proxy}} = 0.18 \times K$$

In Research4 Stage E (672 episodes), replacing noisy realized counts with this analytical expectation reduced cluster standard deviation from $0.2276$ to $0.1163$ (a $48.9\%$ variance reduction), confirming that a massive fraction of observed score variance was pure feedback-delay jitter.
