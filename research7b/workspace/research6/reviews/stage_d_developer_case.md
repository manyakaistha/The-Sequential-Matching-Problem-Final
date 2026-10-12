# Stage D developer case: N3_two selection for confirmation

Author: acquisition developer (`flash`, medium); date: 2026-10-11.
Subject: Selection case for N3_two following Stage D independent selection across 80 fresh clusters (130001–130080).

## 1. Primary findings on Stage D
- **Performance vs G**:
  - `N3_two`: Mean difference of **+0.040625 MSMI/100** vs G (SE 0.0299, paired SD 0.2675).
  - `N3`: Mean difference of **+0.040625 MSMI/100** vs G (SE 0.0306, paired SD 0.2737).
  - Both contenders easily cleared the pre-registered effect threshold of $\ge +0.025$ MSMI/100.
- **Lower bound qualification**:
  - `N3_two`: One-sided 90% paired-t lower bound is **+0.001975** (> 0).
  - `N3`: One-sided 90% paired-t lower bound is **+0.001083** (> 0).
  - Both contenders cleared the strictly positive lower bound criterion.
- **Complexity and parsimony**:
  - Direct paired contrast between `N3` and `N3_two` across all 80 clusters yielded a mean difference of exactly **0.00000**.
  - `N3_two` achieves identical point gains with lower standard deviation (0.2675 vs 0.2737) and higher lower bound (+0.001975 vs +0.001083).
  - `N3_two` evaluates only complementary candidate pairs (2-bundle coordination) and uses FIFO filling for remaining asks, avoiding the combinatorial overhead and complexity of 4-bundle enumeration.

## 2. Selection recommendation
By both the lower bound criterion (+0.001975 > +0.001083) and the registered tie-break rule (lower bounds within 0.005 prefer simpler Tier 2), the developer strongly recommends selecting **`N3_two`** as the sole contender to advance to Stage E frozen confirmation against baseline `G`.
