# Phase 6: Research 6 (Stages, Pre-Registration, and Confirmatory Collapse)

**Document Reference**: `study_notes/phases/06_research6_stages_and_confirmation.md`  
**Base Repository Artifacts**: [`research6/REPORT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research6/REPORT.md), [`research6/PLAN.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research6/PLAN.md), [`research6/EXPERIMENT_REGISTRY.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research6/EXPERIMENT_REGISTRY.md), [`research6/ORCHESTRATION.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research6/ORCHESTRATION.md)  
**Registries, Reviews & Data**: [`research6/registry/`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research6/registry/), [`research6/reviews/`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research6/reviews/), [`results/research6/`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/results/research6/), [`study_notes/data/historical_confirmation.json`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/study_notes/data/historical_confirmation.json)

---

## 1. Context and Problem Formulation

Entering Round 6, all prior rounds (1 through 5) had established that static soft-attribute scoring, uncalibrated parametric matching, and naive greedy tie-breaking could not beat shipped greedy baseline (`G`). The central open bottleneck was identified as **inquiry coordination**.

In all previous policies, the 12-unit daily inquiry budget was spent in list-order FIFO: the policy simply queried missing hard bundles for the first 4 available members in arrival order. Because feasible edge revelation is non-submodular (verifying member $u$ provides zero matching value unless candidate partner $v$ is also verified), blind FIFO frequently verified "lonely" members who had no compatible partners in the pool, wasting scarce inquiry budget.

Research 6 was conceived as the definitive, pre-registered, multi-stage investigation into **joint constraint acquisition, combinatorial query coordination, and structural allocation mechanisms**.

---

## 2. Hypotheses Tested

1. **The Combinatorial Joint Acquisition Hypothesis (`N3` / `N3_two`)**: Verifying hard constraints on *candidate pairs* simultaneously (coordinating 2 complementary queries on $u$ and $v$ within the same day's budget) unlocks feasible edges immediately, avoiding budget fragmentation and beating blind FIFO greedy.
2. **The Query Capacity Ablation Hypothesis (`N3_fifo4`)**: The performance difference between greedy and advanced acquisition is driven by joint dyadic coordination, not simply expanding query capacity to 4 bundles per day.
3. **The Cardinality Matching Hypothesis (`K` / `N1`)**: When feasible components contain multiple edges, maximum cardinality matching (or local alternating-path augmentations) will outperform greedy first-fit allocation.
4. **The Delay-Integrated Expectation Theorem**: Under independent random draws across scenario families, expected qualified reward decomposes as $\mathbb{E}[Q] = c_f \mathbb{E}[P]$, where $c_f = 0.36$ in standard families and $c_f = 6,039 / 17,150 \approx 0.3521$ in delayed feedback scenarios.

---

## 3. Status and Historical Timeline

- **11 October 2026**: Integrated plan and machine-readable limits locked in [`research6/PLAN.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research6/PLAN.md) and `plan.json`. Multi-agent team established under strict concurrency controls (root plus 3 worker agents; Luna, Sol, Astra routing).
- **11 October 2026**: Stage B Screening executed across 40 fresh seed clusters (seeds 110001–110040, 1,440 episodes). Candidate `N3` won promotion (+0.03333 MSMI/100).
- **11 October 2026**: Stage C Replication & Ablation executed across 60 fresh seed clusters (seeds 120001–120060, 1,800 episodes). `N3_two` established +0.04306 MSMI/100; `N3_fifo4` scored +0.00000.
- **11 October 2026**: Stage D Selection executed across 80 fresh seed clusters (seeds 130001–130080, 1,920 episodes). Contenders `N3` and `N3_two` tied at +0.040625; `N3_two` won selection via the pre-registered simplicity tie-breaker.
- **11 October 2026**: Stage E Confirmatory evaluation executed across 571 fresh seed clusters (seeds 140001–140571, 6,852 episodes).
- **Outcome Status**: **Definitive Confirmatory Failure**. Point difference collapsed to **+0.003211 MSMI/100** ($p = 0.7646$). Shipped greedy retained.

---

## 4. Algorithmic Architecture of Evaluated Candidates

Research 6 systematically evaluated 12 candidate architectures across 5 engineering cost tiers:

```
[Research 6 Candidate Roster]
├── Comparator & Controls
│   ├── G: Shipped kit.baseline_asks and kit.baseline_match (Tier 0 reference)
│   ├── P: Frozen Round 5 population log-odds with FIFO asks (Tier 2 control)
│   └── K: Maximum cardinality matching via blossom, shipped score secondary (Tier 2)
├── Local Augmentation & Reranking
│   ├── N1: Length-3 augmenting paths / local exchange at fixed score (Tier 1)
│   └── N2: Period-stable priorities in frozen near-tie classes (Tier 1)
├── Joint Acquisition Architectures
│   ├── N3: Joint collision-aware up-to-4 hard bundle batches (Tier 3)
│   ├── N3_two: Joint collision-aware 2-query hard batch + FIFO completion (Tier 2)
│   └── N3_fifo4: Uncoordinated 4-bundle FIFO query ablation (Tier 1 control)
└── Complex Structural & Dynamic Planning (Deferred / Screened)
    ├── N4: Matching-valued hard/soft packages (Tier 3)
    ├── N5: Distributional public-return reservations (Tier 3)
    ├── N6: Bounded public-belief component rollouts (Tier 4)
    ├── N7: Whole-matching uncertainty gate (Tier 2)
    └── L1 / L2: Joint history posterior & policy distillation (Tiers 2–4)
```

### The Winning Contender: `N3_two` (Tier 2)
1. **Dyadic Compatibility Enumeration**: On day $t$, identify all available pairs $(u, v)$ where both members need hard-constraint clarification, but neither has a permanent decline, and public demographics (age brackets, gender/who-to-meet, acceptable zones) are mutually compatible.
2. **Complementary 2-Query Batch**: Select the single highest-scoring compatible pair $(u^*, v^*)$ and emit hard bundle queries for both $u^*$ and $v^*$ simultaneously (consuming $2 \times 3 = 6$ units of budget).
3. **FIFO Completion**: Spend the remaining 6 budget units on standard list-order FIFO hard bundles.
4. **Greedy Matching**: Allocate verified feasible edges greedily in canonical order.

---

## 5. Code Map and Concrete Execution Trace

### Repository Code Structure
- [`research6/PLAN.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research6/PLAN.md): Complete architectural protocol, noncentral-t sample sizing formulas, and stage transition gates.
- [`research6/EXPERIMENT_REGISTRY.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research6/EXPERIMENT_REGISTRY.md): Machine-readable candidate definitions, engineering tiers, and hypotheses.
- [`research6/REPORT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research6/REPORT.md): Full final scientific report and breakdown.
- [`research6/registry/`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research6/registry/): Immutable cryptographic digests of candidate source files, stage manifests, and frozen configs.

### Concrete Execution Trace (`N3_two` Acquisition)
```python
# In research6 candidate implementation (N3_two)
def decide_asks(state, budget):
    asks = []
    unverified = [m for m in state['members'] if m['available'] and needs_hard(m)]
    
    # 1. Search for mutually compatible unverified dyad (u, v)
    best_pair = None
    best_priority = -1
    for u, v in combinations(unverified, 2):
        if public_hard_compatible(u, v):
            priority = compute_demographic_density(u, v, state['members'])
            if priority > best_priority:
                best_priority = priority
                best_pair = (u, v)
                
    # 2. Spend 6 budget units on coordinated pair if found
    if best_pair and budget >= 6:
        u, v = best_pair
        asks.append({'member_id': u['member_id'], 'field': 'constraints'})
        asks.append({'member_id': v['member_id'], 'field': 'constraints'})
        budget -= 6
        unverified.remove(u)
        unverified.remove(v)
        
    # 3. Spend remaining budget on standard FIFO
    for m in unverified:
        if budget >= 3:
            asks.append({'member_id': m['member_id'], 'field': 'constraints'})
            budget -= 3
            
    return asks
```

---

## 6. Experimental Design

### Multi-Stage Tournament Grids (751 Fresh Seed Clusters, 12,012 Episodes)
- **Stage B (Screening)**: Seeds 110001–110040 ($n=40$ clusters, 6 families, 6 policies = 1,440 episodes).
- **Stage C (Replication & Ablation)**: Seeds 120001–120060 ($n=60$ clusters, 6 families, 5 policies = 1,800 episodes).
- **Stage D (Independent Selection)**: Seeds 130001–130080 ($n=80$ clusters, 6 families, 4 policies = 1,920 episodes).
- **Stage E (Frozen Confirmation)**: Seeds 140001–140571 ($n=571$ clusters, 6 families, 2 policies = 6,852 episodes).

All seed ranges were pre-verified against repository inventory to guarantee zero overlap with historical data.

---

## 7. Pre-Outcome Rules and Confirmatory Sample Sizing

### Power Planning via Noncentral-t Distribution
To achieve 90% power ($1 - \beta = 0.90$) at two-sided $\alpha = 0.01$ for a design effect size $\delta = +0.05$ MSMI/100:
1. Standard deviation estimate from Stage C and D: $\sigma_d = 0.2560$.
2. Degrees of freedom and noncentrality parameter:
   $$\delta_{\text{ncp}} = \frac{0.05 \sqrt{m}}{\sigma_d}, \quad t_{\text{crit}} = t_{0.995, m-1}$$
3. Solving for the smallest integer $m$ satisfying $1 - F_{t}(t_{\text{crit}} \mid \delta_{\text{ncp}}) \ge 0.90$ yielded $m = 519$.
4. Applying a pre-registered $10\%$ inflation factor for cluster design effects:
   $$n = \lceil 1.10 \times 519 \rceil = 571 \text{ seed clusters (6,852 episodes)}.$$

### Confirmatory Decision Rule
- Primary $\alpha = 0.01$ (Two-sided 99% paired-t confidence interval).
- Lower bound of 99% CI must strictly exceed zero ($CI_{99\%} \text{ lower} > 0$).

---

## 8. Actual Execution, Container Stress Tests, and Omissions

- **Completed Grid**: All 12,012 planned tournament episodes executed with 100% validity, zero unhandled exceptions, and zero fallback activations.
- **Production Container Verification**:
  - Replayed 108 complete episodes (12,960 invocations) across direct Python, subprocess execution, and unprivileged Docker containers (`sequential-round6:smoke`, `network=none`, read-only root, UID 65534).
  - P99 latency: 18.4 ms (greedy), 24.1 ms (`N3_two`); peak RAM 78 MiB (well within 10-second timeout and 1 GiB limits).
- **Dropped Candidates**:
  - Complex dynamic planning algorithms ($N5, N6, L1, L2$) were barred from Stage B admission due to failing container latency constraints ($> 2.5$s per invocation) and lack of positive effect on examined development states.

---

## 9. Results with Uncertainty: The Confirmatory Collapse

### Progression Across Experimental Stages

```
[Stage B Screen (n=40)]      [Stage C Ablation (n=60)]     [Stage D Selection (n=80)]    [Stage E Confirmation (n=571)]
N3:      +0.03333*           N3_two:  +0.04306*            N3_two:  +0.040625*           N3_two: +0.003211
K:       +0.01875            N3:      +0.04167*            N3:      +0.040625*           99% CI: [-0.024483, +0.030904]
N1:      +0.00625            P:       +0.00139             P:       +0.003125            p = 0.764559 (COLLAPSE!)
P:       +0.00208            N3_fifo4:+0.00000             G:       reference            Superiority REJECTED
N2:      -0.02917            G:       reference            (N3_two wins tier tie-break)
G:       reference
(* passed promotion gate >= +0.025)
```

### Stage C Definitive Ablation Finding
In Stage C, candidate `N3_fifo4` (which simply queried 4 hard bundles per day in blind FIFO order) scored an exact paired difference of **+0.00000 MSMI/100** across all 360 episodes. This proved conclusively that merely increasing query throughput without coordination yields zero benefit over baseline.

### Stage E Confirmatory Results (Seeds 140001–140571, 6,852 Episodes)

| Metric | Shipped Greedy (`G`) | Confirmatory Contender (`N3_two`) | Paired Difference | Uncertainty Intervals & Tests |
|---|---:|---:|---:|---:|
| **Qualified MSMI Dyads** | **2,635** | **2,657** | **+22 dyads** | — |
| **MSMI per 100 arrived** | **0.384560** | **0.387771** | **+0.003211** | **Primary 99% CI: [-0.024483, +0.030904]** |
| | | | | **Nominal 95% CI: [-0.017835, +0.024257]** |
| | | | | **Bootstrap 99% CI: [-0.023351, +0.031232]** |
| | | | | **Bootstrap 95% CI: [-0.017809, +0.024376]** |

- **Student-t test**: $t(570) = 0.2996$, two-sided $p = 0.764559$.
- **Standard Error**: $SE = 0.010715$; Paired Standard Deviation: $\sigma_d = 0.256047$.
- **Standardized Effect Size**: Cohen's $d = 0.0125$.
- **Leave-One-Seed-Out Range**: `[+0.000731, +0.004825]`.
- **Verdict**: The primary 99% confidence interval spans zero broadly. The confirmatory superiority criterion ($CI_{99\%} \text{ lower} > 0$) **fails completely**.

---

## 10. Mechanistic Analysis: The Exact Scenario Cancellation

Why did `N3_two` appear so robust in Stages B (+0.033), C (+0.043), and D (+0.041), only to collapse to +0.003 in Stage E?

### Per-Scenario Family Breakdown (Stage E Confirmation)

| Scenario Family | Greedy MSMI/100 | `N3_two` MSMI/100 | Paired Difference | Physical Mechanistic Cause |
|---|---:|---:|---:|---|
| `cold_start` | 0.3897 | 0.4238 | **+0.034151** | Low member arrival rate; joint querying rapidly creates the only feasible edges in pool |
| `delayed` | 0.4072 | 0.3730 | **-0.034151** | Long date latency ($U\{1, 45\}$) breaches 30-day window; early coordinated queries lock actors into deadweight loss |
| `development` | 0.4501 | 0.4623 | **+0.012259** | Balanced environment; slight advantage from dyadic coordination |
| `shift` | 0.3704 | 0.3757 | **+0.005254** | Mid-episode lifestyle inversion attenuates soft matching |
| `drift` | 0.3669 | 0.3713 | **+0.004378** | Acceptance logit collapse dominates edge structure |
| `sparse` | 0.3231 | 0.3205 | **-0.002627** | Severe geographic dispersion; joint compatible pairs rarely exist |

### The Exact Mathematical Cancellation
In Stage E, the gain in `cold_start` was **+0.034151**, and the loss in `delayed` was **-0.034151**. They cancelled each other out to the sixth decimal place!
$$\Delta_{\text{cold\_start}} + \Delta_{\text{delayed}} = +0.034151 - 0.034151 = 0.000000$$

### The Deadweight Loss of Front-Loaded Inquiries
Under `delayed`, date scheduling delays are drawn from $U\{1, 45\}$, meaning dates regularly occur after the 30-day qualification cutoff. When `N3_two` coordinates queries on pair $(u, v)$, it front-loads inquiry budget on a dyad that subsequently encounters date delay disqualification. The baseline greedy policy, by spreading queries passively via FIFO, preserves inquiry budget for later-arriving members who have shorter remaining horizons, inadvertently avoiding the delayed-date trap.

---

## 11. Review and Critic Objections

1. **The Fallacy of Small-Tournament Consistency**: A superficial reviewer would argue that observing positive gains across three independent stages (B: +0.033, C: +0.043, D: +0.041) established that `N3_two` was a genuine winner. The critic proved that across small samples ($n=40, 60, 80$), scenario-family variance is sufficiently large that positive draws in `cold_start` and `development` routinely masked the latent deficit in `delayed`. Only the fully powered confirmatory test ($n=571$) unmasked the exact cancellation.
2. **Cardinality Matching Irrelevance**: The critic noted that candidate `K` (maximum cardinality matching) failed to clear the Stage B screen (+0.01875). On sparse graphs where components are stars ($S_k$) or paths ($P_2, P_3$), maximum cardinality matching coincides with greedy matching in $> 92\%$ of configurations.

---

## 12. Final Decision and Program Conclusion

- **Confirmatory Verdict**: Definitive rejection of superiority for `N3_two`.
- **Baseline Retention**: Shipped greedy (`kit.baseline_match` and `kit.baseline_asks`) is retained as the permanent production default.
- **Scientific Conclusion of the 6-Phase Program**:
  Across 6 research rounds, spanning over 25,000 evaluated episodes and thousands of CPU hours, **no policy has demonstrated statistically significant confirmatory superiority over greedy first-fit matching**.
  The combination of extreme feasible graph sparsity, 64% feedback deadline disqualification, and exogenous date latency creates a market environment where dynamic planning and information acquisition provide virtually zero exploitable surplus over simple greedy heuristics.

---

## 13. Learnings and Anti-Learnings

### Validated Scientific Learnings
- **The Cross-Scenario Cancellation Trap**: Algorithmic interventions that optimize for thick or slow markets (`cold_start`) can create equal and opposite vulnerabilities in delayed-feedback markets (`delayed`). Robustness requires evaluation across balanced scenario mixtures.
- **Query Throughput is Not Query Coordination**: Expanding query capacity from 3 to 4 bundles per day without coordination (`N3_fifo4`) produces exactly +0.00000 improvement.
- **Pre-Registration is the Only Defense Against False Breakthroughs**: Had Research 6 stopped at Stage D, `N3_two` would have been deployed based on a "+0.041 gain." The pre-registered 571-cluster confirmatory stage saved the engineering team from deploying a zero-value policy.

### Anti-Learnings
- **Do Not Declare Victory from Screening Tournaments**: Consistent positive direction in exploratory stages ($n < 100$) does not guarantee confirmatory success when underlying market dynamics contain cancelling failure modes.
- **Do Not Blame the Random Number Generator**: When a confirmatory test fails ($p = 0.76$), it reflects the true physical properties of the market, not "bad random draws."

---

## 14. Defense Practice and Exam Exercises

### Question 1: Noncentral-t Confirmatory Sample Sizing
*Derive the formula for determining the minimum sample size $m$ required to achieve power $1 - \beta$ at significance level $\alpha$ for a paired continuous outcome with standard deviation $\sigma$ and minimum detectable effect $\delta$.*  
**Model Defense Answer**: Under the alternative hypothesis $H_1: \mu = \delta$, the test statistic $T = \frac{\bar{D}}{\sigma / \sqrt{m}}$ follows a noncentral Student-t distribution with $\nu = m - 1$ degrees of freedom and noncentrality parameter $\lambda = \frac{\delta \sqrt{m}}{\sigma}$. For a two-sided test at level $\alpha$, the critical threshold is $t_{\text{crit}} = t_{1 - \alpha/2, \nu}$. The statistical power is the probability that $T$ exceeds this threshold:
$$\text{Power} = 1 - F_{t, \nu, \lambda}(t_{1 - \alpha/2, \nu}) \ge 1 - \beta$$
Because $F_{t}$ depends nonlinearly on $m$ through both degrees of freedom and $\lambda$, $m$ is found by numerical root-finding or grid search over candidate integers.

### Question 2: The Mechanism of Scenario Cancellation
*Explain how an inquiry coordination algorithm can produce a $+0.034$ advantage in a cold-start market while suffering a $-0.034$ deficit in a delayed-feedback market.*  
**Model Defense Answer**: In `cold_start`, arrivals are slow, creating a severely starved pool. By coordinating queries on compatible pairs $(u, v)$, the policy unlocks feasible edges days before blind FIFO would, allowing these scarce pairs to be matched before horizon end. In `delayed`, dates take up to 45 days, causing many dates to breach the 30-day qualification window. By concentrating budget on early pairs, the coordinated policy matches members into dates destined to fail the deadline, exhausting their availability. The FIFO greedy baseline, by acquiring information more slowly, introduces pairs later in the episode with different timing dynamics, avoiding this specific deadline trap. Across the balanced distribution, these two opposing forces cancel out completely.
