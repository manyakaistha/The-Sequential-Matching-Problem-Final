# Phase 1: Round 1 and Extended Candidates (Audited Benchmark)

**Document Reference**: `study_notes/phases/01_round1_and_extended_candidates.md`  
**Base Repository Artifacts**: [`ROUND1_SUBMISSION.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/ROUND1_SUBMISSION.md), [`REPORT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/REPORT.md), [`research/`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research/), [`results/research/`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/results/research/), [`results/extended/`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/results/extended/)  
**Primary Executables & Audits**: [`candidate_optimal.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/candidate_optimal.py), [`extended_policy.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/extended_policy.py), [`research_policy.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research_policy.py), [`kit.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/kit.py), [`evaluate.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/evaluate.py)

---

## 1. Context and Problem Formulation

The Sequential Matching Problem is formulated over a finite horizon of 60 active decision days ($t \in \{0, \dots, 59\}$), followed by 40 observation follow-up days (days 60–99) to resolve delayed date scheduling and post-date feedback. On each decision day $t$, an autonomous policy receives observable profile updates, pending event notifications, and an inquiry budget, making two sequential batch decisions:
1. **Clarification Decision**: Select which unknown profile attributes to query, subject to a strict daily budget constraint of 12 units. Legal queries are strictly partitioned into:
   - Hard constraint bundle (`"constraints"`): Costs 3 units; reveals all 11 non-declined hard constraint fields simultaneously.
   - Named soft attribute query (one of 7 individual soft fields): Costs 1 unit per named attribute.
2. **Allocation Decision**: Select a batch of non-overlapping, reciprocally feasible introductions from currently available members.

### The Feasibility Landscape and Bottlenecks
A pair of members $(u, v)$ is legally eligible for introduction if and only if:
- `kit.eligibility(u, v)` returns `is_feasible = True` in both directions ($u \to v$ and $v \to u$).
- All 11 hard constraint fields are verified and non-missing: `age_min`, `age_max`, `who_to_meet`, `relationship_structure`, `smoking`, `partner_smoking`, `has_children`, `partner_children`, `wants_children`, `acceptable_zones`, and `schedule`.
- Both $u$ and $v$ are currently available (neither is exited, busy on an active date, or paused following mutual positive feedback).
- The dyad $(u, v)$ has never been previously introduced in the episode (endpoint reuse with a new partner is legal once released, but dyad reuse is strictly prohibited).

Across the 10 public synthetic pools (200 members each), the hard feasibility graph is extraordinarily sparse:
- Visible feasible edges prior to clarification: Mean 17.8 edges in `development` (out of $\approx 19,900$ potential dyads), and only 2.0 edges in `sparse`.
- After complete non-declined hard field resolution: Expands to 59.6 edges in `development` and 8.2 edges in `sparse`.
- Permanent declines: Approximately 35% of members permanently decline at least one hard constraint field (`field_status == 'declined'`), irreversibly blocking any introduction involving them.
- Non-bipartite structure: Because members encompass men, women, and non-binary individuals with arbitrary preference topologies (`who_to_meet`), the compatibility graph is a general non-bipartite graph.

---

## 2. Hypotheses Tested

The initial research investigated whether an advanced sequential policy integrating:
1. **Exact reciprocal feasibility checking** with permanent-decline pruning,
2. **Targeted clarification** of missing hard constraints and soft attributes,
3. **Multi-stage terminal probability forecasting** decomposing the funnel into reciprocal response, mutual acceptance, date occurrence, and mutual second-meeting feedback, and
4. **Maximum-weight general graph matching** via Edmonds' blossom algorithm with continuation penalties,

could deliver an improvement of at least **$+0.10$ MSMI per 100 arrived members** over the baseline greedy first-fit policy (`policy_greedy.py`).

### Competing Sub-Hypotheses
- **Information Value Hypothesis**: Clarifying soft attributes (e.g., `relationship_goal`, `communication_style`, `pace`) to compute fine-grained dyadic compatibility scores would yield higher MSMI than purely verifying hard feasibility.
- **Blossom vs. Greedy Hypothesis**: Exact maximum-weight matching on the general graph (via NetworkX blossom) would resolve trade-offs between competing dyads and outperform myopic first-fit greedy allocation.
- **Dynamic Reservation Hypothesis**: Imposing opportunity-cost continuation penalties based on node degree or market thickness would prevent premature matching of scarce members.

---

## 3. Status and Historical Timeline

- **7 October 2026**: Initial exploratory round documented in `research/REPORT_2026-10-07.md`. High exploratory variance observed across small seed sets (seeds 101–108).
- **8 October 2026**: Formal registered extension protocol locked in [`research/EXPERIMENT_REGISTRY.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research/EXPERIMENT_REGISTRY.md). Execution of a 3-stage protocol: Development (seeds 1001–1008), Selection (seeds 2001–2012), and Confirmation (seeds 3001–3040).
- **8 October 2026**: Pre-registered confirmation frozen in `results/extended/frozen_candidate.json` selecting candidate configuration `simple_fifo`. Confirmatory evaluation yielded an established **negative result** against the supplied baseline greedy policy.
- **Outcome Status**: Closed negative confirmatory finding. Shipped greedy retained.

---

## 4. Algorithmic Architecture and Evolution

The experimental search spanned 22 distinct configurations across four modular design axes:

```
[Candidate Configuration Space]
├── Scoring Model
│   ├── Integrated: Full 5-stage joint integral with Gaussian quadrature
│   ├── Independent: Factorized marginals ignoring shared dyadic shock S
│   ├── Simple: Empirical aggregate mature completion rate (constant per dyad)
│   ├── No-Learning: Fixed population priors, zero within-episode updates
│   └── Product Fusion: Heuristic multiplication of uncalibrated stage probabilities
├── Clarification Strategy
│   ├── FIFO: List-order hard constraint bundle queries (budget 12 -> 4 bundles/day)
│   ├── Potential Degree: Prioritizes uncontradicted neighbor count
│   ├── Prior Entropy: Exact Shannon entropy of hard constraint bundle
│   ├── Monte Carlo VoI: Estimated matching-value delta via sampled rollouts
│   └── Soft Questioning: Target decision-changing soft fields (cost 1)
├── Allocation Solver
│   ├── Greedy First-Fit: Descending score order on canonical edge IDs
│   ├── Edmonds' Blossom: Exact MWM on general graphs (500ms timeout fallback)
│   └── Hungarian: Bipartite projection solver
└── Dynamic Control
    ├── Opportunity Cost: Dual-price / hazard reservation thresholds
    └── Component Batching: Waiting 3, 5, or 7 days in small connected components
```

### The Terminal Probability Model
For a dyad $(u, v)$, the theoretical success probability decomposes through the physical simulator funnel:

$$\mathbb{P}(\text{MSMI}_{u,v} = 1) = \mathbb{P}(\text{Date} \le 30) \times \mathbb{P}(\text{Feedback} \le 3 \mid \text{Both Yes})^2 \times d \times k_u k_v \times \mathbb{E}_S \left[ \sigma(a_u + S) \sigma(a_v + S) \sigma(s_u + S) \sigma(s_v + S) \right]$$

where:
- $\mathbb{P}(\text{Feedback} \le 3 \mid \text{Both Yes})^2 = (3/5)^2 = 0.36$: Both members must submit their feedback within 3 days (feedback delay is drawn uniformly $U\{1, 5\}$).
- $h = \mathbb{P}(\text{Date} \le 30)$: Date delay is drawn uniformly $U\{1, 30\}$ in standard families ($h = 1.0$), and $U\{1, 45\}$ in `delayed` ($h = 30/45 \approx 0.667$; empirical simulator truncation gives $5368/5488 \approx 0.978$).
- $d = 0.78$: Physical date occurrence rate conditional on mutual acceptance ($0.22$ cancellation probability).
- $k_u = \mathbb{E}[R_u^2]$: Second moment of response propensity under $U[0.55, 0.98]$ prior ($\mathbb{E}[R] = 0.765, \mathbb{E}[R^2] = 0.6006$).
- $S \sim \mathcal{N}(0, 0.45^2)$: Shared latent dyadic Gaussian shock linking Stage 1 acceptance ($a_u$) and Stage 2 second-meeting endorsement ($s_u$).

### Missing Soft Feature Enumeration
Rather than substituting the sigmoid of the expected soft features (which incurs Jensen inequality bias), the integrated model enumerates up to $2^4 = 16$ unobserved categorical equality configurations weighted by public prior probabilities, integrating via 5-node Gauss-Hermite quadrature.

### The Selected Candidate: `simple_fifo`
Due to severe over-fitting of complex models during development, the pre-registered selection rule picked `simple_fifo`:
- Clarification: Pure FIFO query of `"constraints"` bundles.
- Scoring: Static aggregate mature completion rate ($\approx 0.0115$), incorporating only historical dyads older than 38 days to avoid truncation bias.
- Ranking: Because the predicted score is identical across all candidate pairs, dyadic edge weights are uniform, and matching reduces to greedy first-fit in canonical member-ID order.

---

## 5. Code Map and Concrete Execution Trace

### Repository Code Structure
- [`kit.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/kit.py): Core interface definitions, `eligibility(a, b)` function, `baseline_asks()`, and `baseline_match()`.
- [`candidate_optimal.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/candidate_optimal.py): Top-level executable wrapper with 7-second `SIGALRM` deadline, safety guards, and fallback routing.
- [`extended_policy.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/extended_policy.py): Complete multi-stage integrated scoring, Gauss-Hermite quadrature, and Blossom allocation engines.
- [`research_policy.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research_policy.py): Experimental policy harness used during exploratory ablations.
- [`evaluate.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/evaluate.py): Master evaluation engine executing 60 decision days and 40 observation follow-up days.

### Concrete Daily Execution Trace (Day $t$)
1. **Observation Ingestion**: `policy.act(observation)` receives:
   - `available_members`: List of currently unengaged member dictionaries.
   - `incoming_feedback`: Notifications of date cancellations, responses, or second-meeting ratings.
   - `ask_budget`: Current budget units (12).
2. **Clarification Phase (`ask_action`)**:
   - Filter `available_members` for members with missing, non-declined hard fields.
   - Sort members by arrival order (FIFO).
   - Emit `AskAction(queries=[AskQuery(member_id, "constraints"), ...])` up to $\lfloor 12 / 3 \rfloor = 4$ bundles.
   - Any member with a declined hard constraint is flagged in `decline_cache` and never queried.
3. **Simulator Intermission**: Simulator executes queries; newly resolved fields appear immediately in the subsequent match invocation on the same day.
4. **Matching Phase (`match_action`)**:
   - Query pairwise `kit.eligibility(u, v)`.
   - Discard previously matched dyads stored in `matched_history`.
   - Score eligible edges using the terminal model. In `simple_fifo`, each edge receives constant weight $\hat{q} \approx 0.0115$.
   - Greedily extract maximal disjoint matching: iterate edges in descending score order (tie-broken by canonical string tuple `(min(u, v), max(u, v))`).
   - Emit `MatchAction(pairs=[(u_1, v_1), (u_2, v_2), ...])`.

---

## 6. Experimental Design

### Scenario Families (Equal 1/6 Weighting)
1. `development`: Standard generative parameters, balanced geography and demographics.
2. `sparse`: Severe geographic dispersion; viable geographic overlaps are exceptionally rare.
3. `cold_start`: Slow arrival rate; pool density accumulates late in the horizon.
4. `delayed`: Extended date latency ($U\{1, 45\}$ vs $U\{1, 30\}$), causing dates to breach the 30-day qualification window.
5. `shift`: Lifestyle feature weights reverse sign halfway through the episode.
6. `drift`: Day-35 sudden negative logit shift in base reciprocal acceptance probability.

### Three-Stage Experimental Partitioning
To guarantee zero data snooping, seeds were partitioned into non-overlapping clusters:
- **Development Stage** (Seeds 1001–1008, 8 clusters $\times$ 6 families = 48 episodes per policy; 22 configurations tested = 1,056 episodes).
- **Selection Stage** (Seeds 2001–2012, 12 clusters $\times$ 6 families = 72 episodes per policy; 7 configurations tested = 504 episodes).
- **Confirmation Stage** (Seeds 3001–3040, 40 clusters $\times$ 6 families = 240 episodes per policy; 2 frozen policies tested = 480 episodes).

### Primary Metric
$$\text{MSMI per 100 arrivals} = \frac{\sum_{i=1}^N \mathbf{1}(\text{Qualified MSMI}_i)}{N_{\text{arrived}}} \times 100$$
Equal weighting across all six scenario families within each seed cluster.

---

## 7. Pre-Outcome Rules and Decision Gates

1. **Power Sizing Criterion**: Sizing based on pilot paired standard deviation $\sigma_d \approx 0.205$. To achieve 80% statistical power at two-sided $\alpha = 0.05$ for detecting a target effect $\delta = +0.10$, the required sample size was:
   $$n \ge \left( \frac{z_{1 - \alpha/2} + z_{1 - \beta}}{\delta / \sigma_d} \right)^2 = \left( \frac{1.96 + 0.8416}{0.10 / 0.205} \right)^2 \approx 33.1 \implies 40 \text{ seed clusters pre-registered}.$$
2. **Lexicographic Candidate Selection Rule**:
   - Filter selection stage configs whose mean MSMI is within $0.05$ of the top-performing candidate.
   - Minimize implementation complexity tuple: `(model_complexity, query_complexity, solver_complexity)`.
   - `simple_fifo` (cost 0) preferred over frozen parametric (cost 1) and full parametric (cost 2).
3. **Confirmatory Success Gate**:
   - Two-sided paired Student-t test lower bound $CI_{95\%} > 0$ on the confirmation partition.
   - Point effect $\ge +0.10$ MSMI/100.

---

## 8. Actual Execution and Omissions

- **Completed Grid**: All 1,056 development, 504 selection, and 480 confirmation episodes completed with 100% validity.
- **Failures and Fallbacks**: Zero unhandled exceptions; zero fallback invocations triggered.
- **Runtime Latency**: Mean invocation latency 11.1 ms; p95 19.8 ms; max 53.8 ms (well below 7.0s safety cutoff and 10.0s hard container limit). Peak RSS memory was 95.6 MiB.
- **Omissions & Corrections**:
  - Soft-query allocation during development (`terminal_soft`) demonstrated promising initial scores (0.510 in Dev) but collapsed in Selection (0.278), leading to its elimination.
  - Edmonds' blossom matching incurred significant CPU overhead without increasing qualified pairs on sparse graphs; it was abandoned in favor of greedy first-fit.

---

## 9. Results with Uncertainty and Discrepancies

### Development and Selection Trajectory
In development, complex candidates appeared to achieve substantial gains over greedy baseline:
- `no_learning_fifo`: 0.510 MSMI/100 (+0.094 vs greedy 0.417)
- `terminal_soft`: 0.510 MSMI/100 (+0.094)
- `simple_fifo`: 0.469 MSMI/100 (+0.052)
- `greedy`: 0.417 MSMI/100

However, in the independent Selection stage (seeds 2001–2012), performance severely regressed:
- `no_learning_fifo`: 0.347 [0.198, 0.497]
- `terminal_fifo`: 0.340 [0.175, 0.505]
- `greedy`: 0.312 [0.159, 0.466]
- `simple_fifo`: 0.312 [0.173, 0.452]
- `terminal_soft`: 0.278 [0.098, 0.457]

### Frozen Confirmatory Results (Seeds 3001–3040, 480 Episodes)

| Metric | Shipped Greedy (`policy_greedy.py`) | Frozen Candidate (`simple_fifo`) | Paired Difference | 95% Confidence Interval |
|---|---:|---:|---:|---:|
| **MSMI per 100 arrived** | **0.3729** (179 pairs) | **0.3313** (159 pairs) | **-0.0417** | **[-0.0911, +0.0077]** |
| Member Coverage | 0.340 | 0.340 | 0.000 | — |
| Mutual Acceptance / Assigned | 0.137 (2,428 / 17,954) | 0.134 (2,434 / 18,133) | -0.003 | — |
| Dates / Mutual Acceptance | 0.761 (1,849 / 2,428) | 0.786 (1,912 / 2,434) | +0.025 | — |
| Mean Inquiry Cost | 203.0 | 203.0 | 0.0 | — |

- **Two-sided paired t-test**: $t(39) = -1.701$, $p = 0.0960$.
- **Standardized Effect**: Cohen's $d = -0.270$.
- **Cluster Bootstrap 95% CI** (10,000 resamples): `[-0.0896, +0.0042]`.
- **Seed Cluster Outcomes**: 10 favored candidate, 12 tied, 18 favored greedy.

### Per-Scenario Family Breakdown (Confirmation)

| Scenario Family | Greedy MSMI/100 | `simple_fifo` MSMI/100 | Difference | Mechanistic Vulnerability |
|---|---:|---:|---:|---|
| `development` | 0.4625 | 0.3625 | -0.1000 | Tie-breaking and stochastic deadline attrition |
| `sparse` | 0.1000 | 0.0875 | -0.0125 | Structural graph starvation (mean 2.0 visible edges) |
| `cold_start` | 0.4375 | 0.4750 | +0.0375 | Late pool density favors uniform canonical ordering |
| `delayed` | 0.4000 | 0.4000 | 0.0000 | Date latency breaches 30-day window identically |
| `shift` | 0.3750 | 0.3125 | -0.0625 | Fails to detect lifestyle weight reversal |
| `drift` | 0.4625 | 0.3500 | -0.1125 | Day-35 logit collapse destroys unadapted dyads |

---

## 10. Mechanistic Analysis and Mathematical Proofs

### Proof of FIFO Clarification Invariance
**Theorem**: *Let $P_1$ and $P_2$ be any two policies that query missing hard-constraint bundles using identical list-order FIFO priority under the same daily budget $B=12$. Then for any world realization $W$, $P_1$ and $P_2$ execute the exact same query sequences on every day $t$, regardless of their matching decisions.*  
**Proof Outline**: A member $u$ is legally eligible for matching if and only if all 11 hard constraints are verified. Incomplete members can never be matched or placed into busy date states. Therefore, the availability and arrival sequence of unverified members is strictly exogenous and independent of matching actions. Since FIFO queries process unverified members strictly by arrival index, both policies query the exact same member IDs at every time step $t$.

### Qualified Reward Identity and Deadline Attrition
Under the simulator's independent uniform feedback delay distribution ($U\{1, 5\}$), post-date feedback arrives within the 3-day qualification deadline with probability:
$$\mathbb{P}(\tau_{\text{feedback}} \le 3) = \frac{3}{5} = 0.60$$
Because both partners must submit positive feedback within 3 days:
$$\mathbb{P}(\text{Qualified} \mid \text{Both Positive Seconds}) = \left(\frac{3}{5}\right)^2 = 0.36$$
In the confirmation evaluation, of the 489 dyads achieving mutual positive second-meeting feedback under `simple_fifo`, **330 dyads (67.5%) were disqualified** due to feedback arriving on day 4 or 5, or date latency exceeding 30 days.

### Non-Submodularity of Information Acquisition
Revealing constraints on member $u$ yields zero marginal match value if all potential partners $v \in N(u)$ have unverified constraints. Only when constraints on partner $v$ are also acquired does the edge $(u, v)$ become feasible. Thus, the information acquisition value function is complementary:
$$V(A \cup \{u, v\}) - V(A \cup \{u\}) > V(A \cup \{v\}) - V(A)$$
violating submodularity and rendering myopic greedy Value-of-Information (VoI) approximations ineffective.

### Calibration and Discrimination Collapse
Evaluating `simple_fifo` prospective predictions across 18,133 confirmation introductions:
- Mean predicted terminal probability: 0.0115 (1.15%)
- Mean observed qualified rate: 0.0088 (0.88%)
- Systematic over-forecasting: $-0.00281$ (95% CI `[-0.0050, -0.0010]`)
- Terminal AUC: **0.507** (indistinguishable from random guessing; AUC 0.500)

```
[The Conversion Funnel: 18,133 Introductions]
18,133 Introductions (100.0%)
  │
  ├── 10,576 Both First Responded (58.3%)
  │     │
  │     ├── 2,434 Mutual Acceptance (13.4%)
  │     │     │
  │     │     ├── 1,912 Date Occurred (10.5%)
  │     │     │     │
  │     │     │     ├── 489 Both Positive Second Meeting (2.70%)
  │     │     │     │     │
  │     │     │     │     └── 159 Qualified MSMI (0.88%)
  │     │     │     │           [330 Disqualified by Deadlines (67.5%)]
```

---

## 11. Review and Critic Objections

1. **The "Pseudo-Predictor" Objection**: The critic proved that `simple_fifo` possesses an AUC of 0.507 and assigns an identical terminal probability ($\approx 0.0115$) to every eligible edge. The candidate did not perform intelligent dyadic matching; it executed greedy allocation ordered strictly by canonical member ID strings. Any difference between `simple_fifo` and baseline greedy was an artifact of arbitrary ID sorting and tie-breaking.
2. **Development Winner's Curse**: The apparent $+0.052$ gain in development was driven by a single fortunate seed (seed 1001), where a day-12 dyad (`8c7752` / `6a5af1`) qualified in both `development` and `drift` families due to shared random number streams. When tested across 40 fresh confirmation seeds, this variance-driven gain evaporated.
3. **The Soft-Query Distraction**: Purchasing soft-attribute queries squandered budget units without resolving the hard feasibility bottleneck. A pair missing hard constraints has zero probability of introduction regardless of soft alignment.

---

## 12. Final Decision and Action Taken

- **Decision**: Reject candidate configuration `simple_fifo`.
- **Policy Deployment**: Shipped greedy (`policy_greedy.py`) is retained as the authoritative production benchmark.
- **Pruning Directive**: Prohibit further exploration of uncalibrated parametric scoring and soft-query acquisition unless hard feasibility is fully unlocked.

---

## 13. Learnings and Anti-Learnings

### Validated Scientific Learnings
- **Hard Constraints are Structurally Binding**: Verifying 11 hard constraints is the primary gatekeeper of market liquidity. Soft attribute matching is irrelevant for unverified dyads.
- **The FIFO Invariance Principle**: In list-ordered FIFO queries, matching policies have identical inquiry trajectories; querying cannot be used as an independent policy lever unless prioritized dynamically.
- **Severe Stochastic Attrition**: 64% of mutually enthusiastic pairs are eliminated purely by post-date feedback latency ($\tau > 3$). Model-based scoring cannot overcome exogenous deadline noise.

### Anti-Learnings (What NOT to Do)
- **Do Not Trust Development Point Estimates**: Complex models with multiple tunable hyperparameters readily overfit small seed sets (seeds 1001–1008).
- **Do Not Substitute Means into Nonlinear Sigmoids**: Jensen's inequality induces massive over-optimism when evaluating missing features via $\sigma(\mathbb{E}[X])$.
- **Do Not Rely on Edmonds' Blossom on Ultra-Sparse Graphs**: When maximum degree is $\le 2$, greedy first-fit is identical or near-identical to exact maximum-weight matching, rendering blossom algorithms computationally wasteful.

---

## 14. Defense Practice and Exam Exercises

### Question 1: Mathematical Invariance
*Prove why two policies operating under list-order FIFO query selection with budget $B=12$ necessarily experience identical query histories on any given simulator world.*  
**Model Defense Answer**: Under simulator rules, a member cannot be matched unless all 11 hard fields are fully verified. Incomplete members remain in the pool until exogenous departure. Because FIFO selects strictly by arrival index from unverified available members, no matching action can alter the set or order of unverified members. Hence, inquiry selection is completely decoupled from matching decisions.

### Question 2: Deadline Attrition Derivation
*Derive the theoretical upper bound on the qualification fraction of mutually positive dates under the standard simulator delay distributions.*  
**Model Defense Answer**: Let date delay $T_d \sim U\{1, 30\}$ and feedback delays $T_{f1}, T_{f2} \sim U\{1, 5\}$. A date qualifies if $T_d \le 30$ (probability 1.0) and $\max(T_{f1}, T_{f2}) \le 3$. Since $T_{f1}, T_{f2}$ are independent, $\mathbb{P}(T_{f1} \le 3 \cap T_{f2} \le 3) = (3/5)^2 = 0.36$. Thus, at most $36\%$ of mutually positive dates can ever generate qualified MSMI rewards.
