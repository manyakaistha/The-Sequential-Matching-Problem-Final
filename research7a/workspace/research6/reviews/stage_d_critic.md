# Stage D adversarial critique

Author: independent adversarial critic (`pro`, high); date: 2026-10-11.
Subject: Critical examination of Stage D results, selection rules, and progression to Stage E.

## 1. Critical audit of Stage D evidence
1. **Exploratory significance status**:
   - Although both `N3` and `N3_two` achieved a positive point difference of +0.040625, neither achieves two-sided statistical significance at n=80 (p=0.178 for N3_two, p=0.188 for N3). The 95% confidence intervals still span zero ([-0.0189, +0.1002] for N3_two).
   - The population control `P` also showed an anomalous positive difference of +0.035417 on this seed set (compared to -0.01389 on Stage C), cautioning that seed partition D exhibited broad upward variation for non-greedy policies.
2. **Evaluation against registered selection rules**:
   - The Stage D selection rules require:
     1. Point difference vs G >= +0.025: Met (+0.040625 >= 0.025).
     2. One-sided 90% paired-t lower bound > 0: Met (+0.001975 for N3_two, +0.001083 for N3).
   - Both candidates qualified under the registered protocol.
3. **Contender selection**:
   - `N3_two` has a higher lower bound (+0.001975 vs +0.001083) and a lower paired SD (0.2675 vs 0.2737).
   - Under the registered tie-break rule (difference in lower bounds < 0.005), preference is assigned to the lower-complexity tier: `N3_two` is a Tier 2 policy while `N3` is a Tier 3 policy. Full 4-bundle enumeration produced zero incremental benefit over 2-query coordination.
   - Therefore, advancing `N3_two` is procedurally sound and respects Occam's razor.

## 2. Requirements for Stage E confirmation
- Stage E must be strictly confirmatory:
  - Untouched seeds 140001 through 140571 (571 clusters).
  - Only two policies: frozen `N3_two` vs frozen `G`.
  - Confirmatory criteria: Two-sided $\alpha = 0.01$ (99% confidence interval).
  - If the 99% CI includes zero in Stage E, the null hypothesis is retained, no superiority over greedy is claimed, and the program concludes. No post-hoc extensions or revisions are permitted.
