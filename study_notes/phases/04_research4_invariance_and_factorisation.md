# Phase 4: Research 4 (Deadline Invariance, Response Factorisation, and Population Control)

**Document Reference**: `study_notes/phases/04_research4_invariance_and_factorisation.md`  
**Base Repository Artifacts**: [`research4/FINAL_REPORT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research4/FINAL_REPORT.md), [`research4/DECISIONS.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research4/DECISIONS.md), [`research4/ANALYSIS_PLAN.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research4/ANALYSIS_PLAN.md), [`research4/DEADLINE_INVARIANCE.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research4/DEADLINE_INVARIANCE.md)  
**Theoretical Proofs & Audits**: [`research4/RESPONSE_FACTORISATION.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research4/RESPONSE_FACTORISATION.md), [`research4/candidates.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research4/candidates.py), [`research4/stages.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research4/stages.py), [`research4/prediction_audit.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research4/prediction_audit.py)

---

## 1. Context and Problem Formulation

Entering Round 4, three major scientific questions remained open from prior rounds:
1. **The Inquiry Bottleneck**: Could a policy coordinate hard and soft acquisition within a single daily batch (e.g., purchasing 3 hard bundles and 3 soft queries = 12 budget units) to avoid displacing the critical fourth hard bundle, while prioritizing queries using public demographic compatibility?
2. **Actor Learning**: Could Bayesian actor-level updates (exact response propensity posteriors and shrunk acceptance logits) provide genuine dyadic discrimination on prospective edges?
3. **The Multiplicity Problem**: Having conducted confirmatory evaluations in Round 1 and Round 3 without establishing superiority, any subsequent confirmation required formal family-wise error rate control. Research 4 established a formal **3-test Bonferroni Program Gate** ($\alpha_{\text{program}} = 0.05 / 3 \approx 0.01667$, corresponding to a $98.333\%$ confidence interval).

---

## 2. Hypotheses Tested

1. **Coordinated Acquisition Hypothesis (`coordinated_goal` / `goal_surplus_control`)**: Purchasing 3 hard bundles (cost 9) and 3 named `relationship_goal` asks (cost 3) achieves joint hard-soft resolution without sacrificing hard verification capacity.
2. **Public Verification Priority Hypothesis (`hard_priority`)**: Prioritizing hard-constraint verification based on public demographics (e.g., age-bracket overlap, gender-preference compatibility) unlocks thick clusters of feasible edges earlier than blind list-order FIFO.
3. **Exact Response Factorization Hypothesis (`response_uniform` / `response_beta_control`)**: Updating actor response propensities via exact truncated-uniform posterior moments isolates high-responsiveness members, reducing dead-end introductions.
4. **Deadline Invariance Hypothesis**: For a fixed sequence of matching actions, varying post-date feedback latency between 1 and 5 days has zero causal impact on the policy's future action choices, because endpoints remain locked in `busy` until day $D+6$.

---

## 3. Status and Historical Timeline

- **10 October 2026**: Pre-evaluation decisions locked in [`research4/DECISIONS.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research4/DECISIONS.md); cross-zone prior corrected from local empirical frequencies to exact uniform ($1/16 = 0.0625$).
- **10 October 2026**: Stage B Screening completed (seeds 80001–80012, 8 policies, 576 episodes). `hard_priority` achieved $+0.2014$ MSMI/100 vs greedy unadjusted ($p_{\text{Holm}} = 0.0948$).
- **10 October 2026**: Stage C Focused Development completed (seeds 81001–81032, 4 policies, 768 episodes). Large Stage B point gains attenuated drastically (`hard_priority` shrank from $+0.2014$ to $+0.0573$).
- **10 October 2026**: Stage D Selection completed (seeds 82001–82020, 3 policies, 360 episodes). `population_control` selected via pre-registered engineering cost-band rule.
- **10 October 2026**: Stage E Confirmatory evaluation completed across 56 seed clusters (seeds 83001–83056, 672 episodes).
- **Outcome Status**: **Negative / Superiority Not Established**. Paired effect was $+0.0565$ MSMI/100, nominal $p = 0.0683$, failing both the nominal $\alpha = 0.05$ gate and the registered program gate ($\alpha = 0.01667$). Shipped greedy retained.

---

## 4. Algorithmic Architecture and Candidates

The 8 tested candidates spanned a disciplined factorial grid:

```
[Research 4 Architectural Matrix]
├── Baselines & Controls
│   ├── greedy: Shipped kit implementation
│   ├── population_control: Static population log-odds scoring, pure FIFO hard asks
│   └── goal_surplus_control: Soft goal queries using leftover budget (cost 1 each)
├── Acquisition Interventions
│   ├── hard_priority: Verifies hard bundles prioritized by public demographic overlap
│   └── coordinated_goal: Bundles 3 hard bundles + 3 goal queries per batch
└── Dynamic Actor Learning
    ├── response_uniform: Exact truncated-uniform posterior moments E[R^2 | s, f]
    ├── response_beta_control: Conjugate Beta(8.16, 2.51) moment matching
    └── acceptance_shrinkage: Empirical Bayes shrinkage on responded first-meeting logits
```

### Population Control Scoring
The selected candidate, `population_control`, replaced complex dynamic belief updating with a closed-form population score:
$$\text{Score}(u, v) = \sum_{k \in \mathcal{S}} \beta_k \cdot \mathbb{P}_{\text{pop}}(u_k = v_k \mid \text{disclosed})$$
where $\mathcal{S} = \{\text{goal}, \text{pace}, \text{conversations}, \text{lifestyle}\}$. Missing soft fields are integrated over marginal population base rates. Edges are sorted in descending score order and matched greedily.

---

## 5. Code Map and Concrete Execution Trace

### Repository Code Structure
- [`research4/candidates.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research4/candidates.py): Implementation of all 8 policy candidates and control ablations.
- [`research4/DEADLINE_INVARIANCE.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research4/DEADLINE_INVARIANCE.md): Theorem, proof, and diagnostic empirical harness for second-feedback latency invariance.
- [`research4/RESPONSE_FACTORISATION.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research4/RESPONSE_FACTORISATION.md): Mathematical derivation of conditional independence of actor response propensities.
- [`research4/stages.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research4/stages.py): Fixed multi-stage tournament engine running B, C, D, and E grids.
- [`research4/prediction_audit.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research4/prediction_audit.py): Evaluates proper scoring rules (log loss, Brier) on identical prospective assignments.

### Concrete Execution Trace (`hard_priority` Asks)
```python
# In research4/candidates.py
def priority_asks(state, budget):
    unverified = [m for m in state['members'] if m['available'] and needs_hard(m)]
    # Compute demographic potential score against other available members
    scores = []
    for m in unverified:
        potential = sum(1 for other in state['members'] 
                        if other['available'] and public_demographic_match(m, other))
        scores.append((potential, m['arrival_day'], m['member_id']))
    
    # Sort descending by potential, tie-break by arrival day (FIFO)
    scores.sort(key=lambda x: (-x[0], x[1], x[2]))
    
    asks = []
    for _, _, m_id in scores:
        if budget >= 3:
            asks.append({'member_id': m_id, 'field': 'constraints'})
            budget -= 3
    return asks
```

---

## 6. Experimental Design

### Registered Seeds and Partitioning
- **Stage B (Screening)**: Seeds 80001–80012 ($n=12$ clusters $\times$ 6 families $\times$ 8 policies = 576 episodes).
- **Stage C (Focused Development)**: Seeds 81001–81032 ($n=32$ clusters $\times$ 6 families $\times$ 4 policies = 768 episodes).
- **Stage D (Independent Selection)**: Seeds 82001–82020 ($n=20$ clusters $\times$ 6 families $\times$ 3 policies = 360 episodes).
- **Stage E (Frozen Confirmation)**: Seeds 83001–83056 ($n=56$ clusters $\times$ 6 families $\times$ 2 policies = 672 episodes).
- **Total Registered Main Grid**: **2,376 episodes**.

---

## 7. Pre-Outcome Rules and Decision Gates

1. **The Three-Test Bonferroni Program Gate**:
   To prevent cumulative false discovery across consecutive rounds (Round 1, Round 3, Round 4), the confirmatory decision gate required:
   $$\alpha_{\text{program}} = \frac{0.05}{3} \approx 0.01667 \implies \text{Two-sided } 98.333333\% \text{ CI lower bound } > 0$$
   Nominal 95% intervals were reported concurrently for diagnostic continuity.
2. **Power Sizing Formula**:
   Based on Stage C paired SD $\sigma_d \approx 0.2526$ and target effect $\delta = +0.10$, standard normal power planning ($10\%$ inflation) yielded:
   $$n = 56 \text{ seed clusters (672 episodes)}.$$
   *(Note: The registry explicitly disclosed that while $n=56$ provided $80\%$ power at nominal $\alpha = 0.05$, it did not guarantee $80\%$ power at the stricter program $\alpha = 0.01667$)*.
3. **Engineering Cost-Band Rule**:
   If Stage D contenders perform within $0.025$ MSMI/100 of each other, select the configuration with lower computational and architectural complexity.

---

## 8. Actual Execution, Omissions, and Retries

- **Completed Grid**: All 2,376 planned main episodes executed with 100% validity and zero fallbacks.
- **Floating-Point Boundary Check in Stage D**:
  Before Stage D finished, the Critic flagged that floating-point imprecision could misclassify candidates near the exact $0.025$ boundary. The Director paused outer orchestration to verify exact integer counts:
  - Total arrivals per policy in Stage D: $20 \text{ clusters} \times 6 \text{ families} \times 200 \text{ members} = 24,000$ members ($120$ episodes).
  - Qualification totals: Greedy = 100, `population_control` = 93, `hard_priority` = 89.
  - Difference: Greedy vs `population_control` was 7 pairs ($7 / 240 = 0.02917$); `hard_priority` vs `population_control` was 4 pairs ($4 / 240 = 0.01667 \le 0.025$). Both candidates lay within the band; `population_control` was verified as the correct minimal-complexity selection.
- **Container Stress Test**: 200 hard-verified endpoints, varied missing soft fields, 594 diverse public feedback events. Worst measured container call: 2.30s (greedy startup), 0.58s (`population_control`).

---

## 9. Results with Uncertainty and Attenuation

### Multi-Stage Tournament Trajectory

| Stage | Candidate | MSMI/100 | Paired Effect vs Greedy | 95% Confidence Interval | Holm-Adjusted $p$ |
|---|---|---:|---:|---:|---:|
| **Stage B** ($n=12$) | `hard_priority` | 0.5069 | **+0.2014** | [+0.0459, +0.3569] | 0.0948 |
| | `population_control` | 0.5000 | **+0.1944** | [+0.0584, +0.3305] | 0.0653 |
| | `greedy` | 0.3056 | reference | — | — |
| **Stage C** ($n=32$) | `hard_priority` | 0.3828 | **+0.0573** | [-0.0687, +0.1833] | 1.0000 |
| | `population_control` | 0.3516 | **+0.0260** | [-0.0650, +0.1171] | 1.0000 |
| | `greedy` | 0.3255 | reference | — | — |
| **Stage D** ($n=20$) | `greedy` | 0.4167 | reference | — | — |
| | `population_control` | 0.3875 | **-0.0292** | [-0.1232, +0.0649] | 0.9744 |
| | `hard_priority` | 0.3708 | **-0.0458** | [-0.1812, +0.0896] | 0.9744 |

### Confirmatory Results (Stage E, Seeds 83001–83056, 672 Episodes)

| Metric | Shipped Greedy Baseline | Frozen `population_control` | Paired Difference | Uncertainty Intervals |
|---|---:|---:|---:|---:|
| **MSMI per 100 arrived** | **0.313988** | **0.370536** | **+0.056548** | **Nominal 95% CI: [-0.004400, +0.117495]** |
| | | | | **Program 98.333% CI: [-0.018553, +0.131648]** |
| | | | | **Bootstrap 95% CI: [-0.001488, +0.114583]** |

- **Nominal Student-t test**: $t(55) = 1.858$, two-sided $p = 0.0683$.
- **Program Decision Gate**: **FAILS** (Lower bound $-0.0186 \le 0$).
- **Nominal Decision Gate**: **FAILS** (Lower bound $-0.0044 \le 0$).
- **Practical Target Gate ($+0.10$)**: **UNESTABLISHED** (The target $+0.10$ lies inside the confidence interval; neither superiority nor equivalence is proven).

### Per-Scenario Breakdown (Stage E Confirmation)

| Scenario Family | Greedy MSMI/100 | `population_control` MSMI/100 | Difference |
|---|---:|---:|---:|
| `development` | 0.3393 | 0.4196 | +0.0804 |
| `sparse` | 0.0893 | 0.0893 | +0.0000 |
| `cold_start` | 0.4196 | 0.4286 | +0.0089 |
| `delayed` | 0.3750 | 0.4464 | +0.0714 |
| `shift` | 0.3393 | 0.4554 | +0.1161 |
| `drift` | 0.3214 | 0.3839 | +0.0625 |

---

## 10. Mechanistic Analysis and Mathematical Proofs

### The Deterministic Semantic-Action Theorem (Deadline Invariance)
**Theorem**: *For any world realization $W$ and any of the 8 candidate configurations, let second-feedback delays be counterfactually modified to any alternative integers $\tau' \in \{1, \dots, 5\}$, holding all other primitives (response flags, date occurrences, arrivals, exits, hard/soft attributes) constant. If the policy triggers zero resource fallbacks, the normal inner decision path executes the exact same sequence of ordered asks and matched pairs on every day $t$.*  
**Proof Outline**:
1. All candidate query and matching rules depend strictly on: (a) currently available member profiles, (b) unintroduced eligible dyads, and (c) for learning policies, feedback received on prior resolved introductions.
2. In `Simulator.advance`, endpoints that execute a date are placed into `busy = date_day + 6`.
3. The maximum possible second-feedback arrival day is `date_day + 5`.
4. Therefore, whether feedback arrives on `date_day + 1` or `date_day + 5`, the endpoints remain completely unavailable until `date_day + 6`.
5. Upon becoming available on day $D+6$, all feedback from that date has already arrived under both $\tau$ and $\tau'$. Hence, observable member states, available sets, and actor histories are mathematically identical at all future decision steps.
- **Diagnostic Verification**: Across 16 full seed-101 trajectories, modifying second delays between 1 and 5 yielded **100% byte-identical ask and match actions** at every step.

### Response Posterior Factorization
**Theorem**: *Under the generator's prior $R_i \sim U[0.55, 0.98]$, conditional on public history $H_d$, the response propensities of all currently available members $i \in A_d$ are mutually independent and factorize as:*
$$p((R_i)_{i \in A_d} \mid H_d) = \prod_{i \in A_d} \frac{R_i^{s_i} (1 - R_i)^{f_i} \mathbf{1}_{[0.55, 0.98]}(R_i)}{\int_{0.55}^{0.98} r^{s_i} (1 - r)^{f_i} \, dr}$$
*independent of latent acceptance logits, soft features, or scenario family.*  
**Consequence**: The response likelihood factors cleanly; however, identical-cohort prospective audits across 14,023 assignments demonstrated that exact response updating provided negligible predictive discrimination (log loss delta $< 0.00001$ vs uniform).

---

## 11. Review and Critic Objections

1. **The Nominal vs. Program Gate Tension**: The candidate achieved a nominal paired difference of $+0.0565$ ($p = 0.0683$). A superficial analysis might declare a "near-significant trend." However, under the pre-registered Bonferroni Program Gate ($\alpha = 0.01667$, $98.333\%$ CI `[-0.0186, +0.1316]`), the result is unambiguously inconclusive.
2. **Predictive Indistinguishability**: The identical-cohort prediction audit ([`research4/PREDICTION_REVIEW.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research4/PREDICTION_REVIEW.md)) proved that all 8 candidate models had terminal log losses between $0.05609$ and $0.05627$. None established calibrated superiority.
3. **The Coordinated Query Myth**: The critic demonstrated that bundling 3 hard queries and 3 soft queries displaced the 4th hard bundle. Because hard constraints are binding, sacrificing the 4th bundle reduced total feasible edge discovery.

---

## 12. Final Decision and Action Taken

- **Decision**: Reject superiority claim for `population_control`.
- **Policy Status**: Shipped greedy (`policy_greedy.py`) is retained as the production default.
- **Termination of Round 4**: In accordance with the pre-registered protocol, the round closed permanently without sample size extensions or post-hoc retuning.

---

## 13. Learnings and Anti-Learnings

### Validated Scientific Learnings
- **The Deadline Invariance Principle**: Feedback timing variations within the busy window ($D \le t \le D+5$) cannot affect future actions; dynamic policies cannot adapt to feedback latency unless endpoints are released earlier.
- **Multiplicity Accounting Prevents False Discoveries**: Without the 3-test Bonferroni gate, the $+0.0565$ effect might have been misconstrued as evidence of breakthrough, leading to premature production deployment.

### Anti-Learnings
- **Do Not Extend Sample Sizes Post-Hoc**: Observing $p = 0.068$ does not license adding 20 more seeds to "push the result over the significance line." Such practices completely invalidate frequentist error control.
- **Do Not Rely on Soft Verification Early**: Spending inquiry budget on soft attributes before hard constraints are fully resolved reduces the overall number of viable introductions.

---

## 14. Defense Practice and Exam Exercises

### Question 1: Mathematical Proof of Deadline Invariance
*Prove that modifying post-date feedback latency from $\tau=1$ to $\tau=5$ does not alter the action choices of a policy whose inputs are restricted to currently available member profiles and historical feedback.*  
**Model Defense Answer**: Under simulator rules, any agent executing a date on day $D$ is placed into `busy = D + 6`. Availability requires `day >= busy`. For any delay $\tau \in \{1, \dots, 5\}$, feedback arrives at day $D + \tau \le D + 5 < D + 6$. During days $D$ through $D+5$, the agent is unavailable and excluded from all match and ask candidates. On day $D+6$, the agent becomes available; at this time, feedback has arrived under both $\tau=1$ and $\tau=5$. Because the policy's action on day $t \ge D+6$ depends only on the public state (which contains identical feedback under both timings) and available agents, the policy receives identical inputs and emits identical decisions.

### Question 2: Multi-Round Alpha Allocation
*Explain why a program conducting three successive confirmatory trials across three research rounds must adjust its significance threshold, and state the Bonferroni corrected threshold for family-wise error rate $\alpha = 0.05$.*  
**Model Defense Answer**: If three independent confirmatory tests are conducted at unadjusted $\alpha = 0.05$, the probability of committing at least one Type I error (declaring superiority when no true effect exists) is $1 - (1 - 0.05)^3 \approx 0.1426$ (over 14%). To maintain a family-wise error rate $\le 0.05$, the Bonferroni correction sets the per-test threshold to $\alpha_{\text{program}} = 0.05 / 3 \approx 0.016667$, requiring a two-sided $98.333\%$ confidence interval to exclude zero.
