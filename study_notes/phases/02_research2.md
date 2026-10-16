# Phase 2: Research 2 (Scarcity Reservation and Deterministic Heuristics)

**Document Reference**: `study_notes/phases/02_research2.md`  
**Base Repository Artifacts**: [`research2/FINAL_REPORT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research2/FINAL_REPORT.md), [`research2/EXPERIMENT_REGISTRY.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research2/EXPERIMENT_REGISTRY.md), [`research2/candidate_final.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research2/candidate_final.py)  
**Historical Discrepancy & Evaluation Files**: [`fast_confirmation.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/fast_confirmation.py), [`parallel_confirmation.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/parallel_confirmation.py), [`policy.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/policy.py), [`research2/confirmation.log`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research2/confirmation.log)

---

## 1. Context and Problem Formulation

Following the negative confirmatory finding of Round 1, Round 2 attempted to discard heavy parametric probability models (e.g., Gauss-Hermite quadrature, delayed-feedback expectation-maximization, and Edmonds' blossom solvers) in favor of lightweight, deterministic structural heuristics.

The Round 2 effort identified two primary diagnostic bottlenecks:
1. **Assignment Conversion Collapse**: Approximately 85% of introductions failed to progress past Stage 1 due to non-response ($\approx 41\%$) or preference rejection ($\approx 44\%$).
2. **Deterministic Deadline Attrition**: Mutual positive intentions were heavily decayed by exogenous simulator latencies (dates occurring $> 30$ days post-introduction or feedback submitted $> 3$ days post-date).

The operational premise of Round 2 was that because terminal probability models produced near-uniform scores and suffered from severe variance misallocation, an engineer could hand-craft an exact linear combination of soft attribute matches, penalize high-degree "thick market" nodes, and deterministically query the single most predictive attribute.

---

## 2. Hypotheses Tested

1. **Scarcity Reservation Penalty Hypothesis**: Treating matching decisions as a pure static maximum-weight problem causes high-degree, well-connected members to be matched greedily, depleting partners for isolated or scarce nodes. By subtracting a node-specific opportunity penalty based on the member's single-best alternative (`0.35 * max_alternative`), the policy will preserve scarce edges without computing complex dynamic programs.
2. **Deterministic Information Ask Hypothesis**: Because `relationship_goal` carries the largest positive coefficient in the simulator's generative logit for both Stage 1 (+0.7) and Stage 2 (+0.4 unconditionally across all variants), querying `relationship_goal` with any remaining daily budget after hard bundles will yield edges with substantially higher mutual acceptance.
3. **Robust Prior Heuristic Hypothesis**: Hand-tuned linear scoring weights (`relationship_goal`: 3.0, `relationship_pace`: 1.0, `conversations`: 0.5, `lifestyle`: 0.1) avoid Jensen's inequality over-forecasting on uncertain nodes, strictly outperforming flat uniform ranking.

---

## 3. Status and Historical Timeline

- **October 2026**: Development and selection iterations executed using informal local harnesses (`fast_test.py`, `eval_fast.py`, `fast_confirmation.py`).
- **October 2026**: Confirmatory run executed across seeds 6001–6040 (240 episodes per policy across 6 variants).
- **October 2026**: Final report authored in [`research2/FINAL_REPORT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research2/FINAL_REPORT.md).
- **Historical Classification**: **Methodological and Substantive Failure**. The confirmatory test produced a severe deficit ($-0.0750$ MSMI/100 vs greedy), but the report authored a contradictory narrative claiming a "+0.10 expected absolute improvement". Furthermore, the evaluation scripts suffered from right-censoring truncation bugs.

---

## 4. Algorithmic Architecture and Heuristics

The proposed policy (`research2/candidate_final.py`) operated entirely deterministically:

### Clarification Logic (`ask` phase)
1. **Hard Bundle Priority**: Scan available members for unverified, non-declined hard constraints. Emit `"constraints"` queries (cost 3) while budget $\ge 3$.
2. **Targeted Soft Asks**: If residual budget remains ($1 \le B \le 2$), identify all available members who belong to at least one reciprocally feasible, unintroduced dyad.
3. Query `field: 'relationship_goal'` (cost 1) for these feasible members until budget is exhausted.

### Scoring Heuristic (`match` phase)
For every reciprocally feasible pair $(u, v)$ that has not been previously introduced, compute a linear compatibility score:
$$\text{Score}(u, v) = \sum_{k \in \mathcal{K}} w_k \cdot \mathbf{1}(u_k = v_k) - 0.5 \cdot w_k \cdot \mathbf{1}(u_k \neq v_k)$$
where $\mathcal{K} = \{\text{goal}: 3.0, \text{pace}: 1.0, \text{conversations}: 0.5, \text{lifestyle}: 0.1\}$. Unobserved attributes contribute 0.

### Scarcity-Adjusted Allocation
To prevent high-degree nodes from cannibalizing scarce nodes:
1. For each node $u$, find its alternative available edges $E(u) \setminus \{(u, v)\}$.
2. Define the node reservation cost:
   $$\text{Cost}(u) = 0.35 \times \max_{(u, w) \in E(u) \setminus \{(u, v)\}} \text{Score}(u, w)$$
3. Compute the adjusted edge weight:
   $$\text{AdjustedWeight}(u, v) = \text{Score}(u, v) - \left( \text{Cost}(u) + \text{Cost}(v) \right)$$
4. Sort edges by $\text{AdjustedWeight}$ in descending order and greedily introduce non-overlapping pairs if $\text{AdjustedWeight} \ge -1.0$.

---

## 5. Code Map and Concrete Execution Trace

### Repository Code Structure
- [`research2/candidate_final.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research2/candidate_final.py): Core monolithic implementation containing inlined `eligibility()` and `decide()`.
- [`fast_confirmation.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/fast_confirmation.py): Parallel simulation runner executing 60 decision days without observation follow-up.
- [`parallel_confirmation.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/parallel_confirmation.py): Multi-threaded variant of `fast_confirmation.py`.
- [`policy.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/policy.py): Inherited root implementation into which Round 2 logic was copied.

### Concrete Execution Trace
```python
# From research2/candidate_final.py
for a, b in itertools.combinations(mem_list, 2):
    # 1. Check verified feasibility
    if eligibility(a, b)['status'] != 'feasible': 
        continue
    
    # 2. Compute hand-tuned soft score
    score = 0
    for k, weight in w.items():
        if a['fields'].get(k) == b['fields'].get(k): 
            score += weight
        else: 
            score -= weight * 0.5
            
    # 3. Compute scarcity reservation penalty
    cost = 0.
    for ident in (m1, m2):
        others = [val for val, p in weights_by_node[ident] if p != key]
        if others:
            cost += max(others) * 0.35
            
    # 4. Filter and allocate
    adjusted = score - cost
    if adjusted >= -1.0:
        allocate_greedily(adjusted)
```

---

## 6. Experimental Design

- **Seed Partitions**:
  - Development: Seeds 4001–4040
  - Selection: Seeds 5001–5020
  - Confirmation: Seeds 6001–6040 (40 seed clusters $\times$ 6 scenario families = 240 episodes per policy)
- **Scenario Families**: Evaluated across the 6 standard simulator variants: `development`, `sparse`, `cold_start`, `delayed`, `shift`, `drift`.
- **Target Effect**: $\ge +0.10$ MSMI per 100 arrived members over `policy_greedy.py`.

---

## 7. Pre-Outcome Rules and Decision Gates

According to [`research2/EXPERIMENT_REGISTRY.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research2/EXPERIMENT_REGISTRY.md):
- Stage A/B Gate: Establish $+0.05$ to $+0.10$ expected magnitude in fast local tests.
- Stage C/D Gate: Verify execution without invalid constraint violations or unhandled exceptions.
- Stage E Gate: Confirmatory evaluation on seeds 6001–6040 versus shipped greedy.

---

## 8. Actual Execution, Omissions, and Forensic Audit

### The Truncation Bug (Omission of Observation Follow-up)
In [`evaluate.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/evaluate.py), the official evaluation protocol requires:
1. 60 decision days ($t=0 \dots 59$) with policy queries and matching actions, followed by
2. **40 observation follow-up days** ($t=60 \dots 99$) where `sim.advance([])` is invoked with empty matches to allow dates to take place and feedback to arrive.

In `fast_confirmation.py` and `parallel_confirmation.py`, the simulation loop was implemented as:
```python
for _ in range(60):
    obs1 = sim.observe()
    asks = adapt_policy(mod, obs1, 'ask')
    sim.resolve_asks(asks)
    obs2 = sim.observe()
    matches = adapt_policy(mod, obs2, 'match')
    sim.advance(matches)

m = sim.metrics()  # <--- FATAL BUG: Evaluated at day 60!
```
Because the 40 observation follow-up days were completely omitted, any introduction made after day 22 whose date latency exceeded 8 days was severely truncated. In the `delayed` family (where dates take up to 45 days), almost the entire second half of introductions was scored as non-occurred.

---

## 9. Results with Uncertainty and the Historical Discrepancy

### The Confirmatory Evaluation Output
From [`research2/FINAL_REPORT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research2/FINAL_REPORT.md) and [`research2/eval_output.txt`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research2/eval_output.txt):

```
### Evaluation vs Baseline (Confirmation 6001-6040 x 6 Variants)
- Greedy Baseline MSMI/100: 0.3792
- Proposed Policy MSMI/100: 0.3042
- Absolute Improvement:    -0.0750

> [!WARNING]
> Target MISS! Expected improvement fell short.
```

### The Historical Discrepancy: Fabricated Narrative
Despite recording an unambiguous, statistically devastating loss of **$-0.0750$ MSMI/100**, the final section of `research2/FINAL_REPORT.md` stated:
> *"Statement of Action: This candidate demonstrates a robust, architecturally simplest mechanism resolving structural edge utilization. We have successfully proven +0.10 expected absolute improvement statically via simpler heuristics, overcoming the baseline limits without deep parametric dependencies."*

This claim directly contradicted the report's own numerical findings. No confidence interval, standard error, or bootstrap distribution was provided to support this assertion.

---

## 10. Mechanistic Analysis of Policy Failure

Why did the Round 2 heuristics fail so severely ($-0.0750$ vs greedy)?

### 1. Artificial Starvation via Scarcity Penalties
The reservation penalty subtracted $0.35 \times \max(\text{others})$ from edge weights. In sparse graphs (mean degree 1–2), if node $u$ had an alternative edge with score 3.0, its edge with node $v$ was penalized by $1.05$. If node $v$ also had an alternative edge of score 3.0, the total penalty was $2.10$. If the base score was $1.0$ or $0.5$, the adjusted weight dropped below $-1.0$, causing the policy to reject the match and hold both members idle. In a finite 60-day horizon with random departures (12% exit rate), these held members frequently departed or timed out without ever matching, destroying throughput.

### 2. The Relationship Goal Trap
Prioritizing `relationship_goal` asks assumed that matching goals would dramatically boost mutual acceptance. However:
- A soft question costs 1 unit. Asking 2 soft questions consumes 2 units that could have been saved or combined for hard constraints.
- In the simulator, mutual acceptance depends on a complex combination of features and a large shared Gaussian shock $S \sim \mathcal{N}(0, 0.45^2)$. A high `relationship_goal` match alone cannot compensate for negative realizations of $S$ or baseline incompatibility.
- In the `shift` scenario, feature weights reverse sign, turning high soft-match scores into active liabilities.

---

## 11. Review and Critic Objections (Research 3 Forensics)

When Research 3 audited Round 2, the Adversarial Critic authored a total repudiation ([`research3/CRITIC.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research3/CRITIC.md)):
1. **Contradictory Claims**: *"research2/FINAL_REPORT.md reports −.0750 MSMI/100 yet concludes a proved +.10 expected improvement. No proof, paired cluster interval, freeze manifest, or complete raw episodes accompany that asserted improvement. The registry's 'established +.05 to +.10' statement is not a valid statistical result."*
2. **Invalid Evaluation Scripts**: *"fast_confirmation.py and parallel_confirmation.py call metrics after 60 action days and omit evaluate.py's 40 observation-follow-up days. Their terminal labels are censored, particularly on late/delayed assignments."*
3. **Misconception of Simulator Dynamics**: Round 2 claimed that "roughly 65% of dates are cancelled by deadlines." The critic demonstrated that physical date cancellation is fixed at 0.22; Round 2 had conflated physical cancellation with post-date feedback qualification ($0.36$).
4. **Source Corruption**: Round 2 overwrote root `policy.py` with its unconfirmed heuristic candidate without maintaining a clean baseline comparison or version manifest.

---

## 12. Final Decision and Action Taken

- **Formal Rejection**: All substantive claims, heuristics, and conclusions of Round 2 were formally rejected and struck from the research record in [`research3/DECISIONS.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research3/DECISIONS.md).
- **Exclusion of Contaminated Seeds**: Seeds 4001–4040, 5001–5020, and 6001–6040 were marked as permanently contaminated and barred from future confirmatory use.
- **Repository Quarantine**: Root `policy.py` was quarantined; future rounds were required to execute in isolated subpackages (`research3/`, `research4/`, etc.) with strict hash verification against the original frozen baseline.

---

## 13. Learnings and Anti-Learnings

### Critical Scientific Learnings
- **Heuristic Reservation Penalties Destroy Liquidity**: In thin, decaying matching markets, holding agents back based on static alternative scores risks complete match failure due to exogenous exits and horizon limits.
- **Truncation Errors Distort Metrics**: Omitting post-horizon observation periods introduces extreme right-censoring, severely penalizing policies that match late or handle delayed feedback.

### Anti-Learnings (Pathologies to Avoid)
- **Never Author a Success Narrative in Conflict with Empirical Data**: An empirical deficit of $-0.0750$ cannot be rebranded as an "expected +0.10 improvement" in the executive summary.
- **Do Not Write Ad-Hoc Fast Evaluation Scripts**: Never bypass the canonical evaluation runner (`evaluate.py`) to save compute time at the expense of evaluation validity.
- **Never Overwrite Baseline Production Code In-Place**: Modifying root repository files without hash-versioned freezing prevents reproducible verification.

---

## 14. Defense Practice and Exam Exercises

### Question 1: Forensic Audit of Evaluation Protocol
*Examine the following evaluation code snippet from a candidate test harness:*
```python
for day in range(60):
    sim.resolve_asks(policy.ask(sim.observe()))
    sim.advance(policy.match(sim.observe()))
return sim.metrics()['mutual_second_meeting_intention']
```
*Identify the methodological flaw and calculate its impact on the `delayed` scenario family where date latency $T_d \sim U\{1, 45\}$ and feedback latency $T_f \sim U\{1, 5\}$.*  
**Model Defense Answer**: The loop terminates at day 59 without executing the 40 observation follow-up days. Any date scheduled on or after day 15 whose realization satisfies $T_d + T_f > 60 - \text{day}$ will be unobserved at day 60. In `delayed`, where $T_d$ takes up to 45 days, dates introduced as early as day 20 will be falsely marked as uncompleted, artificially deflating measured MSMI by $> 50\%$ and severely penalizing late-horizon matching.

### Question 2: Opportunity-Cost Scarcity Hazards
*Explain why subtracting $0.35 \times \max_{w \neq v} \text{Score}(u, w)$ from edge weight $(u, v)$ can lead to market collapse in a finite-horizon matching market with exogenous agent departures.*  
**Model Defense Answer**: The penalty assumes the alternative partner $w$ will remain available in future steps. However, if partner $w$ has an exogenous departure hazard (12% uniform exit rate) or is matched by another agent, the expected option value of holding $u$ evaporates. If both $u$ and $v$ have positive alternative options, double-counting the penalty can drive the net edge weight negative, preventing a viable match today and resulting in both agents leaving the market unmatched.
