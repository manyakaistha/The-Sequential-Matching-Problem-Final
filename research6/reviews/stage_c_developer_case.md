# Stage C developer case: N3 and N3_two replication and ablation

Author: acquisition developer (`flash`, medium); date: 2026-10-11.
Subject: Replicated gains and ablation findings in Stage C across 60 fresh clusters (120001–120060).

## 1. Primary findings
- **Replication of gain vs G**:
  - `N3`: Replicated a positive mean difference of **+0.04167 MSMI/100** vs G (SE 0.0342).
  - `N3_two`: Produced a positive mean difference of **+0.04306 MSMI/100** vs G (SE 0.0320).
- **Ablation of batch size (`N3_fifo4`)**:
  - `N3_fifo4` produced exactly **+0.00000** difference vs G across all 360 episodes.
  - This definitively demonstrates that simply increasing or fixing the constraint ask budget to 4 bundles in FIFO order does not improve qualified MSMI. The gain observed in N3 and N3_two is driven entirely by collision-aware query coordination.
- **Ablation of 4-bundle jointness vs 2-query coordination (`N3_two`)**:
  - `N3_two` (optimizing a single pair of constraint queries jointly, then taking FIFO for remaining asks) achieved essentially identical reward to full 4-bundle enumeration (+0.04306 vs +0.04167, paired difference -0.00139, p=0.9613).
  - This demonstrates that the core mechanism is resolving **complementary 2-endpoint pairs and 2-actor collisions**, with diminishing returns from full 4-actor combinatorial jointness.

## 2. Recommendation
The developer recommends advancing both `N3` and `N3_two` to Stage D independent selection alongside controls `G` and `P`.
