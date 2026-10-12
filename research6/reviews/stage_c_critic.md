# Stage C adversarial critique

Author: independent adversarial critic (`pro`, high); date: 2026-10-11.
Subject: Critical examination of Stage C results, ablations, and promotion to Stage D.

## 1. Evaluation of evidence
1. **Replication of positive effect**:
   - Both `N3` (+0.04167) and `N3_two` (+0.04306) replicated the positive sign from Stage B (+0.03333).
   - However, neither effect reaches conventional two-sided statistical significance at n=60 (N3 p=0.2275, N3_two p=0.1840). The 95% confidence intervals continue to include zero.
2. **Causal mechanism confirmed via ablation**:
   - The batch size control `N3_fifo4` produced a difference of exactly **0.00000** against `G`. This is an informative diagnostic: it proves that asking 4 constraint bundles per day in FIFO order does not improve MSMI over G. Therefore, the observed point gain in N3 and N3_two is caused by intelligent query coordination (complementarity and collision avoidance), not batch size.
3. **Simplicity contrast (N3 vs N3_two)**:
   - Full 4-bundle combinatorial evaluation (`N3`) did not outperform 2-query optimization with FIFO filler (`N3_two`) (paired difference -0.00139, p=0.9613).
   - Complexity is not evidence of superiority: `N3_two` achieves equivalent or slightly superior point reward with substantially lower combinatorial complexity (28 pair evaluations vs 71 4-bundle evaluations).
   - On Stage C, `N3_two` achieved a positive one-sided 90% lower bound (+0.00154), while `N3` had a negative lower bound (-0.00261).

## 2. Recommendation for Stage D
- Advance both `N3` and `N3_two` as contenders to Stage D (80 fresh clusters, 130001–130080) alongside `G` and `P`.
- Strictly enforce Stage D selection rules: to qualify for confirmation (Stage E), a candidate must achieve:
  1. Mean paired difference vs G >= +0.025.
  2. One-sided 90% paired-t lower bound strictly greater than 0.
- If neither passes in Stage D, the program must conclude cleanly with greedy retained. No relaxation of thresholds or sample extensions permitted.
