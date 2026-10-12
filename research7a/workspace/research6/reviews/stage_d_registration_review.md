# Stage D registration and preflight review

Reviewer: independent critic / director; date: 2026-10-11.
Scope: Stage D independent selection registration.

## 1. Experimental scope and partition
- Partition D: seeds 130001 through 130080 (80 fresh clusters).
- Certified fresh in `seed_inventory_closure.json`.
- All six scenario families: `development`, `sparse`, `cold_start`, `delayed`, `shift`, `drift`.
- Policies evaluated: `G`, `P`, `N3`, `N3_two` (4 policies).
- Total episodes: 80 seeds × 6 families × 4 policies = 1,920 episodes.

## 2. Contenders and selection mechanism
- Contenders:
  - `N3`: Full 4-bundle collision-aware joint hard acquisition.
  - `N3_two`: 2-query joint collision coordination with FIFO filler for remaining queries.
- Controls:
  - `G`: Greedy baseline (production control).
  - `P`: Population-based allocation control.
- Primary metric: Seed-cluster mean of equal-six-family qualified MSMI/100 differences against G.

## 3. Registered selection criteria and stopping rule
1. Eligibility threshold:
   - Sample mean paired difference vs G >= +0.025 MSMI/100.
   - One-sided 90% paired-t lower bound strictly greater than 0.
2. Contender selection:
   - Select contender with highest one-sided 90% lower bound.
   - If lower bounds are within 0.005 (`D_tie_band`), prefer the simpler tier (`N3_two` Tier 2 over `N3` Tier 3).
3. Stopping rule:
   - If neither contender passes both criteria, retain `G` as the winner, conclude the research program without Stage E, and produce the final negative report.
4. Stage E sizing rule (if a contender qualifies):
   - Paired standard deviation estimate: $\sigma = \max(0.26, 1.10 \times \text{observed\_D\_paired\_SD})$.
   - Exact noncentral-t minimum clusters $m$ for 90% power at two-sided $\alpha = 0.01$ on effect $\delta = +0.05$.
   - Sample inflation: $n = \lceil 1.10 \times m \rceil$ clusters (capped at 900 clusters).

## 4. Resource forecast and ceilings
- Per-episode compute: ~3.5s–4.5s CPU time.
- Total CPU forecast: 1,920 × 5.0s = 9,600 CPU seconds (2.7 CPU hours), well below the 40-hour limit.
- Storage forecast: ~500 KB per episode = ~960 MB, well within available disk storage.
- Workers: 3 offline processes with numerical thread pinning (`OMP_NUM_THREADS=1`, etc.).

Verdict: **PASS**. Approved for Stage D registered execution.
