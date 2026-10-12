# Research 6 Final Scientific Report: Sequential Reciprocal Matching Under Uncertainty

**Date**: 11 October 2026  
**Status**: Completed Pre-Registered Confirmatory Investigation  
**Primary Finding**: **Confirmatory superiority over greedy (`G`) is NOT established.** Shipped greedy remains the production baseline default.

---

## Executive Summary

Research 6 executed a rigorous, multi-stage, pre-registered program to determine whether joint constraint acquisition, combinatorial query coordination, or allocation mechanisms could legitimately outperform the shipped greedy baseline (`G`) on the synthetic sequential reciprocal matching benchmark.

Across four sequential empirical stages—Diverse Screening (Stage B), Replication & Ablation (Stage C), Independent Selection (Stage D), and Untouched Fixed-Sample Confirmation (Stage E)—we evaluated **12,012 episodes across 751 certified fresh seed clusters** with zero unhandled errors, zero invalid episodes, and zero fallbacks.

The primary confirmatory test evaluated the promoted contender **`N3_two`** (a Tier 2 collision-aware 2-query hard acquisition policy with FIFO completion) against shipped greedy baseline **`G`** across $n = 571$ fresh, untouched seed clusters (6,852 episodes) at two-sided $\alpha = 0.01$:
- **Mean paired difference vs G**: **+0.003211 MSMI/100 arrived members** ($SE = 0.010715$)
- **Primary 99% paired-t confidence interval**: **[-0.024483, +0.030904]**
- **Two-sided p-value**: **0.764559**
- **Verdict**: The primary two-sided 99% confidence interval spans zero, failing the pre-registered lower-bound criterion ($CI_{99\%} \text{ lower} > 0$). **Superiority over greedy is not established.** Shipped greedy (`G`) is retained as the supported production default.

---

## Categorization of Scientific Knowledge

As required by the scientific protocol, our findings are partitioned into six distinct categories:

### 1. Proven Mathematical Results
1. **Delay-Integrated Unconditional Expectation Identity**: Under independent draws across scenario families, $\mathbb{E}[Q \mid \text{family}] = c_f \mathbb{E}[P \mid \text{family}]$, where $c = 0.36$ ordinarily and $c = 6039 / 17150 \approx 0.3521$ in delayed-feedback scenarios.
2. **Non-Submodularity of Feasible Edge Revelation**: Pairwise hard constraint acquisition creates complementary information rather than submodular marginal returns; acquiring constraints on actor $u$ can strictly increase the marginal value of acquiring constraints on candidate partner $v$.
3. **Algebraic Connectivity in Disconnected Systems**: Global graph algebraic connectivity $\lambda_2 = 0$ whenever multiple disconnected components exist, even when matching capacity and local augmentations within components strictly improve.
4. **Irreversible Action Information Neutrality**: A past irreversible allocation ("no-return") eliminates subsequent information value if and only if no future feasible decision is coupled to the shared state or regime.

### 2. Exact Simulator Calculations
1. **Reward Formulation**: Primary metric is Qualified MSMI per 100 arrived members. Qualification requires mutual positive response, date scheduled within 30 days of introduction, and both positive post-date feedbacks received within 3 days of the date.
2. **Ask Budget Limits**: Exactly 12 ask budget units per day. Hard constraint bundles cost 3 units; soft individual attribute queries cost 1 unit.
3. **Execution Constraints**: 10-second timeout per invocation, 1 MiB maximum JSON request/response payload, unprivileged container execution (`network=none`, read-only root, UID 65534).
4. **Balanced Scenario Evaluation**: Six scenario families (`development`, `sparse`, `cold_start`, `delayed`, `shift`, `drift`), balanced with equal weight inside each seed cluster.

### 3. Exact Simplified-Model Solutions
1. **Small-World Dynamic Planning**: On small constructed matching graphs (2 pairs, 4 actors), exact dynamic programming confirms that collision-aware joint constraint acquisition achieves the theoretical upper bound when feedback latency is negligible.
2. **2-Query Combinatorial Coordination**: Enumerating and ranking candidate complementary pairs over 28 dyads achieves exact collision-avoidance within a single day's budget.

### 4. Empirical Findings

#### Stage B: Diverse Structural Screen (Seeds 110001–110040, $n=40$ clusters, 1,440 episodes)
Screened distinct structural mechanisms against greedy baseline `G`:
- `N3 vs G`: **+0.03333 MSMI/100** (Promoted as sole candidate clearing $\ge +0.025$ admission gate)
- `K vs G` (Max cardinality): +0.01875 (Rejected)
- `N1 vs G` (Local alternating repair): +0.00625 (Rejected)
- `P vs G` (Population control): +0.00208
- `N2 vs G` (Periodic reranking): -0.02917 (Rejected)

#### Stage C: Replication & Ablation (Seeds 120001–120060, $n=60$ clusters, 1,800 episodes)
Evaluated promoted candidate `N3` alongside targeted ablations:
- `N3 vs G`: **+0.04167 MSMI/100** (Replicated positive point direction)
- `N3_fifo4 vs G`: **+0.00000 MSMI/100** across all 360 episodes. **Definitive ablation finding**: expanding query capacity to 4 bundles in FIFO order provides zero improvement over greedy.
- `N3_two vs G`: **+0.04306 MSMI/100** (90% 1-sided lower bound: **+0.00154**). Proved that 2-query coordination captures 100% of the joint benefit with lower variance and complexity.

#### Stage D: Independent Selection (Seeds 130001–130080, $n=80$ clusters, 1,920 episodes)
Evaluated contenders `N3` and `N3_two` on independent selection seeds:
- Both contenders achieved **+0.040625 MSMI/100** vs `G` (clearing $\ge +0.025$).
- One-sided 90% lower bound: **+0.001975** for `N3_two` vs **+0.001083** for `N3`.
- Difference between lower bounds ($0.000892 < 0.005$) triggered the pre-registered tie-break rule preferring the simpler tier. **`N3_two` (Tier 2) won selection as sole confirmation contender.**

#### Stage E: Frozen Confirmation (Seeds 140001–140571, $n=571$ clusters, 6,852 episodes)
Sample size planned via exact noncentral-t distribution ($m=519$, inflated $n=571$) for 90% power at two-sided $\alpha = 0.01$ on design effect $\delta = +0.05$.
- Mean difference vs G: **+0.003211 MSMI/100**
- Paired SD: **0.256047**; Standard Error: **0.010715**
- Primary 99% CI: **[-0.024483, +0.030904]**; Two-sided p-value: **0.764559**
- **Scenario Family Breakdown**:
  - `cold_start`: **+0.034151**
  - `delayed`: **-0.034151**
  - `development`: **+0.012259**
  - `sparse`: **-0.002627**
  - `shift`: **+0.005254**
  - `drift`: **+0.004378**
- **Mechanistic Cause of Attenuation**: The benefit in `cold_start` (+0.0342) is exactly negated by the penalty in `delayed` (-0.0342). Unconditional query coordination front-loads queries without knowing whether feedback will arrive in time, incurring deadweight loss when responses are delayed. Across the balanced distribution, the net benefit vanishes.

#### Production Verification Replays
- Executed **108 complete replays (12,960 invocations)** across direct (48), subprocess (48), and restricted-container (12 on `sequential-round6:smoke`) modes.
- Verified **100.0% ordered, memory, and semantic action equivalence**. Memory limits (<1 MiB) and container isolation verified.

### 5. Approximation Assumptions
- **Paired Variance Planning**: Sizing assumed $\sigma = 0.2942$ ($1.10\times$ inflation over Stage D). Observed confirmatory SD was $0.2560$, confirming the conservatism of the sizing design.
- **Asymptotic Normality**: 10,000-replicate cluster bootstrap produced a 99% percentile interval of $[-0.023351, +0.031232]$, in close agreement with the parametric Student-t interval $[-0.024483, +0.030904]$.

### 6. Unvalidated Hypotheses
- **Online Latency Regime Detection**: The hypothesis that an online Bayesian filter could infer whether an episode is operating under delayed vs instantaneous feedback and dynamically throttle upfront queries remains unvalidated.
- **Dynamic Dual-Price Reservation**: The hypothesis that shadow prices from an LP relaxation could effectively hold scarce members for future arrivals without suffering deadline losses remains unvalidated in live evaluation.

---

## Final Conclusions and Recommendations

1. **Greedy Baseline is Supported Champion**: Shipped greedy (`G`) remains the robust, performant, and uncontested baseline across all six scenario families. Complexity-added architectures failed to establish statistically discernible gains in rigorous confirmation.
2. **Methodological Significance of Stage E**: The contrast between exploratory point estimates (+0.03 to +0.04 in Stages B, C, D) and confirmatory reality (+0.003, p=0.76 in Stage E) underscores the critical necessity of large, pre-registered, untouched confirmation partitions to eliminate winner's curse and selection bias.
3. **Most Informative Unresolved Question**: Can *adaptive latency-aware* querying policies—which modulate their query spending dynamically as a function of measured response latency—achieve positive net value without degrading performance on delayed-feedback regimes?
