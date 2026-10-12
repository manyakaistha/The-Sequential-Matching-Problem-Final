# Stage E registration and preflight review

Reviewer: independent critic / director; date: 2026-10-11.
Scope: Stage E frozen confirmation registration.

## 1. Experimental scope and partition
- Partition E: seeds 140001 through 140571 (571 untouched clusters from the 2,000-seed reserve).
- Certified fresh in `seed_inventory_closure.json` with zero prior usage.
- All six scenario families: `development`, `sparse`, `cold_start`, `delayed`, `shift`, `drift`.
- Policies evaluated: `G` (shipped greedy baseline) and `N3_two` (sole promoted contender).
- Total episodes: 571 seeds × 6 families × 2 policies = 6,852 episodes.

## 2. Frozen contender and baseline definition
- Contender: `N3_two` (Tier 2 collision-aware 2-query hard acquisition with FIFO completion). Source code and hyperparameters frozen.
- Baseline: `G` (production greedy policy).
- Primary comparison: Paired seed-cluster difference of equal-six-family qualified MSMI/100 between `N3_two` and `G`.
- Primary test: Paired-t test at two-sided $\alpha = 0.01$ (99% confidence interval).

## 3. Confirmatory criteria and stopping rule
1. **Confirmatory superiority**: Requires that the primary two-sided 99% confidence interval lower bound is strictly greater than 0 ($CI_{99\%} \text{ lower} > 0$).
2. **Negative result retention**: If the 99% confidence interval includes zero ($CI_{99\%} \text{ lower} \le 0$), superiority over greedy is **not established**. The negative result is preserved and reported plainly.
3. **No post-hoc adaptations**:
   - Sample size $n = 571$ is immutable. No interim looks, no sample expansion, no retuning, no alternative comparisons.

## 4. Resource forecast and ceilings
- Per-episode compute: ~3.5s–4.5s CPU time.
- Total CPU forecast: 6,852 × 5.0s = ~34,260 CPU seconds (~9.5 CPU hours), well below the 40-hour limit.
- Storage forecast: ~500 KB per episode = ~3.4 GB, well within available disk capacity (330+ GB free).
- Workers: 3 offline processes with numerical thread pinning (`OMP_NUM_THREADS=1`, etc.).

Verdict: **PASS**. Approved for Stage E frozen confirmation execution.
