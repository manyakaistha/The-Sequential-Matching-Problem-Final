# Phase 3: Research 3 (Feedback Timing, Forensics, and Rigorous Governance)

**Document Reference**: `study_notes/phases/03_research3_feedback_and_forensics.md`  
**Base Repository Artifacts**: [`research3/FINAL_REPORT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research3/FINAL_REPORT.md), [`research3/DECISIONS.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research3/DECISIONS.md), [`research3/CRITIC.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research3/CRITIC.md), [`research3/FORENSICS.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research3/FORENSICS.md), [`research3/PREDICTION_AUDIT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research3/PREDICTION_AUDIT.md)  
**Theoretical Proofs & Audits**: [`research3/AVAILABLE_FEEDBACK_THEOREM.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research3/AVAILABLE_FEEDBACK_THEOREM.md), [`research3/FINAL_DAY_AUGMENTATION.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research3/FINAL_DAY_AUGMENTATION.md), [`research3/policy.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research3/policy.py), [`research3/stages.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research3/stages.py)

---

## 1. Context and Problem Formulation

Research 3 was launched as an adversarial forensic reconstruction and methodological reset following the collapse and conflicting claims of Round 2. Prior to evaluating any new policies, an Adversarial Critic and Forensic Analyst conducted an exhaustive code and data audit to establish:
1. Exact replication of the Round 1 negative confirmatory statistics,
2. Formal rejection and repudiation of Round 2’s contradictory "+0.10 improvement" claim and invalid evaluation scripts,
3. Detection of source repository corruption (detecting that root `policy.py` and `extended_policy.py` had suffered silent hash modifications),
4. Mathematical characterization of the simulator’s event timing, feedback delays, and legal inquiry spaces.

---

## 2. Hypotheses Tested

Research 3 formulated several structural and learning hypotheses:
1. **The Available Feedback Hypothesis**: It had been asserted in Round 1 that estimating response propensities required complex survival modeling (e.g., Chapelle 2014 delayed-feedback EM) to account for pending outcomes. Research 3 hypothesized that for any *currently available* member, all prior introduction feedback events are already completely resolved, rendering pending-survival adjustments mathematically redundant for legal edge scoring.
2. **Offline vs. Online Learning**: Pre-training ridge regression models on prospective assignment snapshots from early seeds would outperform static heuristic rules.
3. **Targeted Goal Querying (`goal_queries`)**: Allocating inquiry budget specifically to `relationship_goal` after hard constraints would boost conversion rates without destabilizing general feasibility.
4. **Final-Day Augmentation Dominance**: Appending legal unused edges between unmatched available members on the final decision day ($t=59$) carries zero opportunity cost and weakly dominates pathwise.

---

## 3. Status and Historical Timeline

- **9 October 2026**: Adversarial forensic audit completed; Round 2 findings officially nullified; git checkpoint `1f35149e3bd0b9067c660a970ce00085849ed504` recovered to preserve original frozen files in `research3/recovered_frozen/`.
- **9 October 2026**: Stage B Screening executed across 12 seed clusters (seeds 70001–70012, 13 candidates, 936 episodes).
- **10 October 2026**: Stage C Focused Development executed across 32 seed clusters (seeds 71001–71032, 7 policies, 1,344 episodes).
- **10 October 2026**: Stage D Selection executed across 20 seed clusters (seeds 72001–72020, 4 policies, 480 episodes). Selected candidate: `clean`.
- **10 October 2026**: Stage E Confirmatory evaluation executed across 40 seed clusters (seeds 73001–73040, 480 episodes). Host process interrupted at 396/480 cells; cleanly resumed for remaining 84 cells via `resume_confirmation.py`.
- **Outcome Status**: Confirmatory result is **negative/inconclusive** (+0.0146 MSMI/100, $p = 0.517$); the confidence interval excluded the target $+0.10$ effect.

---

## 4. Algorithmic Architecture and Structural Candidates

Research 3 evaluated 13 candidate architectures in Stage B, narrowing to key archetypes:

```
[Research 3 Candidate Hierarchy]
├── Baseline Comparator
│   └── greedy: Shipped kit.baseline_match and kit.baseline_asks (unmodified)
├── Minimalist Production Control
│   └── clean: Stripped runtime; pure FIFO hard bundles, no soft asks,
│              greedy matching in canonical ID order (zero scoring overhead)
├── Population-Based Scoring
│   └── population: Smoothed population log-odds across all 4 soft fields
├── Query-Ablation Candidates
│   ├── goal_queries: Budget prioritized for relationship_goal after hard bundles
│   └── four_queries: Requests 4 hard bundles deterministically per day
├── Learned Scorer
│   └── offline: Ridge regression model pre-trained on prospective assignment snapshots
└── Dynamic / Structural Heuristics
    ├── scarce: Single-best alternative reservation penalty
    └── random_order: Shuffled edge order to test tie-breaking sensitivity
```

---

## 5. Code Map and Concrete Execution Trace

### Repository Code Structure
- [`research3/CRITIC.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research3/CRITIC.md): Master audit cataloging source discrepancies and forensic verifications.
- [`research3/FORENSICS.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research3/FORENSICS.md): Authoritative inquiry rules, hard constraint legal bounds, and timing proofs.
- [`research3/AVAILABLE_FEEDBACK_THEOREM.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research3/AVAILABLE_FEEDBACK_THEOREM.md): Complete mathematical proof of feedback resolution on available endpoints.
- [`research3/FINAL_DAY_AUGMENTATION.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research3/FINAL_DAY_AUGMENTATION.md): Formal proof and diagnostic evaluation of final-day edge additions.
- [`research3/policy.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research3/policy.py): Factory router dispatching candidates (`clean`, `population`, `goal_queries`, etc.).
- [`research3/stages.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research3/stages.py): Multi-stage evaluation harness ensuring 60 action days and 40 follow-up days.

### Concrete Execution Trace (`clean` Mode)
```python
# In research3/policy.py: 'clean' mode execution
def decide(request):
    phase = request['phase']
    state = request['state']
    
    if phase == 'ask':
        # Pure FIFO hard bundle queries; declines cached permanently
        asks = []
        budget = state['ask_budget_remaining']
        for m in state['members']:
            if m['available'] and any(m['fields'].get(k) is None and m['field_status'].get(k) != 'declined' for k in HARD):
                if budget >= 3:
                    asks.append({'member_id': m['member_id'], 'field': 'constraints'})
                    budget -= 3
        return {'asks': asks, 'memory': {}}
        
    if phase == 'match':
        # Pure canonical greedy matching on verified feasible pairs
        used = set()
        pairs = []
        for a, b in combinations(state['members'], 2):
            if not (a['available'] and b['available']): continue
            if eligibility(a, b)['status'] != 'feasible': continue
            if a['member_id'] in used or b['member_id'] in used: continue
            pairs.append([a['member_id'], b['member_id']])
            used.add(a['member_id'])
            used.add(b['member_id'])
        return {'pairs': pairs, 'memory': {}}
```

---

## 6. Experimental Design

### Multi-Stage Gated Protocol
1. **Screening Stage B** (Seeds 70001–70012, 12 clusters $\times$ 6 families = 72 episodes per candidate; 13 candidates = 936 episodes).
2. **Focused Development Stage C** (Seeds 71001–71032, 32 clusters $\times$ 6 families = 192 episodes per candidate; 7 policies = 1,344 episodes).
3. **Independent Selection Stage D** (Seeds 72001–72020, 20 clusters $\times$ 6 families = 120 episodes per candidate; 4 policies = 480 episodes).
4. **Frozen Confirmation Stage E** (Seeds 73001–73040, 40 clusters $\times$ 6 families = 240 episodes per policy; 2 policies = 480 episodes).

Total registered volume: **3,240 episodes** across 104 certified fresh seed clusters.

---

## 7. Pre-Outcome Rules and Decision Gates

1. **Conservative Variance Floor**: The Critic enforced a planning standard deviation floor $\sigma_d \ge 0.210$ and a $10\%$ sample inflation factor for confirmation power sizing ($n = 40$ seed clusters).
2. **Candidate Selection Cost-Band Rule**: Among Stage D candidates scoring within $0.025$ MSMI/100 of the highest selection mean, choose the candidate with the lowest architectural complexity tuple.
3. **Strict Fallback Prohibition**: Any unhandled exception or invocation triggering fallback to emergency defaults would instantly disqualify a candidate from promotion.

---

## 8. Actual Execution, Operational Interruption, and Recovery

- **Screening (B)**: 936/936 valid episodes; zero fallbacks. `offline` achieved $+0.1181$ MSMI/100 unadjusted, but Holm-adjusted $p = 0.1135$ (non-significant).
- **Development (C)**: 1,344/1,344 valid episodes.
- **Selection (D)**: 480/480 valid episodes. `clean` scored 0.3625 vs `population` 0.3417 and `greedy` 0.3375. Operating within the $0.025$ band, the pre-registered cost rule selected `clean` due to its zero-parameter complexity.
- **Confirmation (E) Host Interruption**: During Stage E execution, the host environment halted after completing 396 out of 480 planned cells due to an external orchestration timeout.
  - *Recovery Action*: The research team preserved `confirmation_interrupted.json` and authored [`research3/resume_confirmation.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research3/resume_confirmation.py), resuming *only* the 84 missing planned jobs. Zero code, configuration, or seed changes were made, ensuring statistical integrity.

---

## 9. Results with Uncertainty and Regression to the Mean

### Stage-by-Stage Score Progression

```
[Screening B (n=12)]     [Development C (n=32)]    [Selection D (n=20)]     [Confirmation E (n=40)]
offline:  +0.1181        population: +0.0573       clean:      +0.0250      clean: +0.0146
goal:     +0.0972        goal:       +0.0182       population: +0.0042      95% CI [-0.0305, +0.0597]
random:   +0.0903        clean:      +0.0078       greedy:     reference    p = 0.5171 (NOT SIGNIFICANT)
greedy:   reference      offline:    +0.0052       random:     -0.0667      Target +0.10 EXCLUDED
                         greedy:     reference
```

### The Collapse of Screen Winners
- In Stage B, `offline` showed an apparent gain of $+0.1181$ MSMI/100. When tested on fresh independent seeds in Stage C, its effect shrank to $+0.0052$ (a $95.6\%$ collapse).
- `goal_queries` dropped from $+0.0972$ in Stage B to $+0.0182$ in Stage C.

### Confirmatory Results (Stage E, Seeds 73001–73040)

| Metric | Shipped Greedy Baseline | Frozen Candidate (`clean`) | Paired Difference | 95% Confidence Interval |
|---|---:|---:|---:|---:|
| **MSMI per 100 arrived** | **0.412500** (198 pairs) | **0.427083** (205 pairs) | **+0.014583** | **[-0.030536, +0.059702]** |
| Mean Ask Cost | 194.750 | 194.750 | 0.000 | — |
| Episode Member Coverage | 0.3532 | 0.3528 | -0.0004 | — |
| Mutual Acceptance / Assigned | 0.1470 (2,799 / 19,037) | 0.1483 (2,818 / 19,006) | +0.0013 | — |
| Dates / Mutual Acceptance | 0.7856 (2,199 / 2,799) | 0.7942 (2,238 / 2,818) | +0.0086 | — |

- **Two-sided paired t-test**: $t(39) = 0.654$, $p = 0.5171$.
- **Bootstrap 95% CI** (10,000 resamples): `[-0.0271, +0.0583]`.
- **Standardized Paired Effect**: Cohen's $d = 0.1034$.
- **Per-Scenario Breakdown**: `cold_start`: $+0.0500$, `delayed`: $+0.0250$, `sparse`: $+0.0125$, `drift`: $+0.0125$, `shift`: $0.0000$, `development`: $-0.0125$.

---

## 10. Mechanistic Analysis and Mathematical Proofs

### The Available Feedback Theorem
**Theorem**: *In any simulation history generated by legal calls to `Simulator.advance`, at any observation day $d$, if member $i$ has `available == True`, then every scheduled event from every prior introduction involving $i$ has already occurred (`observed_day <= d`) and is present in public feedback.*  
**Proof Outline**:
1. If an introduction at day $t$ does not result in mutual acceptance, the maximum response latency is 7 days. Non-responding or rejected endpoints are locked in `busy` until $t+8$. Thus, all response events arrive strictly before release at $t+8$.
2. If mutual acceptance occurs, the date is scheduled on day $D$. If the date occurs, all second-meeting feedback arrives by day $D+5$. Both endpoints remain locked in `busy` until $D+6$.
3. An endpoint cannot be introduced while busy. Therefore, by the time an endpoint becomes `available == True`, all previous events involving that endpoint are already in the past.
4. **Corroborating Audit**: Replaying 48 full historical worlds (seeds 1001–1008 across 6 families) over 458,829 available-endpoint invocations revealed **zero unresolved feedback events**.

### The Final-Day Augmentation Theorem
**Theorem**: *On final decision day $t=59$, let $M$ be any legal disjoint matching and $e = (u, v)$ be any feasible unassigned edge between unmatched available members. Appending $e$ to $M$ preserves all previously scheduled outcomes byte-identically and weakly increases final qualified MSMI pathwise under collision-free introduction IDs.*  
**Proof Outline**: Because no matching actions occur after day 59, matching $e$ incurs zero future opportunity cost. In `Simulator.advance`, random outcomes for dyad $(u, v)$ on day $t$ are seeded locally by `rand_for(world_seed, min(u, v), max(u, v), 59)`. Appending $e$ does not alter the PRNG sequence or arguments for any other dyad.
- **Empirical Diagnostic**: Across 24 replay trajectories, appending 37 feasible zero-score edges on day 59 preserved 100% of existing events byte-identically. However, realized additional qualified MSMI was exactly **zero** (expected value sum was only $+0.159$ across all 24 episodes), proving that final-day augmentation provides negligible practical headroom.

---

## 11. Review and Critic Objections

1. **Failure to Detect Signals in Stage B**: The critic noted that Stage B's top candidate (`offline`, $+0.1181$) was selected on a sample of only 12 clusters. Because the variance of MSMI is high ($\sigma \approx 0.25$), screening on $n=12$ creates severe regression to the mean.
2. **The Illegality of Single Hard Asks**: The forensic audit revealed that attempting to query individual hard fields (e.g., asking for `age_min` alone) triggers an `unknown ask field` error. Only the full `"constraints"` bundle is legal.
3. **The `clean` Policy Paradox**: The candidate selected for confirmation (`clean`) contained zero predictive logic, zero learning, and zero dynamic adjustment. It was identical to greedy first-fit, diverging only in subtle edge sorting tie-breaks. Its confirmatory difference of $+0.0146$ ($p=0.517$) confirmed that minor tie-break variations cannot produce a genuine $+0.10$ advantage.

---

## 12. Final Decision and Action Taken

- **Confirmatory Verdict**: Reject superiority claim. The 95% confidence interval `[-0.0305, +0.0597]` excludes the target $+0.10$ threshold.
- **Baseline Retention**: Shipped greedy remains the undisputed benchmark.
- **Protocol Solidification**: Established permanent guidelines that no candidate may be promoted to confirmation without surviving an intermediate replication stage (Stage C) designed to purge screening noise.

---

## 13. Learnings and Anti-Learnings

### Validated Scientific Learnings
- **The Available Feedback Invariance**: Policies scoring currently available members do not need to model pending feedback delays, as all prior events on available members have already matured.
- **Screening Estimates Suffer Extreme Attenuation**: Effect sizes in exploratory screening stages ($n \le 12$) overestimate true confirmatory effects by $10\times$ or more due to selection on positive noise.
- **Final-Day Omissions Have Minimal Practical Impact**: While mathematically dominant, adding leftover edges on day 59 yields $< 0.004$ MSMI/100 expected gain due to the multi-stage conversion bottleneck.

### Anti-Learnings
- **Do Not Conflate Screen Significance with Confirmatory Power**: An unadjusted $p$-value $< 0.05$ across 13 screened candidates is completely invalid without family-wise error rate control (Holm adjustment).
- **Do Not Assume Offline Models Transfer**: Offline ridge regressors trained on prospective data failed to outscore static baselines when evaluated in closed-loop interactive rollouts.

---

## 14. Defense Practice and Exam Exercises

### Question 1: Feedback Timings and Actor State
*State and prove the Available Feedback Lemma for non-accepted introductions in the synthetic simulator.*  
**Model Defense Answer**: For an introduction at day $t$ where mutual acceptance is not achieved, introduction responses arrive with delays drawn from $U\{1, 7\}$ (with explicit non-response logged on day $t+7$). In `kit.py`, both members are set to `busy = t + 8`. Since an agent is available if and only if `day >= busy`, any member available on day $d$ must satisfy $d \ge t+8 > t+7$. Thus, all introduction response events are logged strictly before the member can be re-evaluated for matching, ensuring zero pending feedback on available nodes.

### Question 2: Regression to the Mean in Multi-Stage Tournaments
*In Stage B, candidate `offline` achieved $+0.1181$ MSMI/100 across 12 seed clusters. In Stage C, it achieved $+0.0052$ across 32 seed clusters. Provide the mathematical explanation for this attenuation.*  
**Model Defense Answer**: Let measured score $\hat{\theta}_i = \theta_i + \epsilon_i$, where $\epsilon_i \sim \mathcal{N}(0, \sigma^2/n)$. When selecting the maximum $\max_{i=1 \dots 13} \hat{\theta}_i$ from 13 candidates with sample size $n=12$, the expected value of the maximum includes the extreme order statistic $\mathbb{E}[\max_i \epsilon_i] > 0$ (winner's curse). Upon re-evaluating the selected candidate on an independent sample in Stage C, $\mathbb{E}[\epsilon_{\text{new}}] = 0$, causing the estimated effect to regress to its true underlying parameter $\theta_{\text{offline}} \approx 0$.
