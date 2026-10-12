# Stage C registration and preflight review

Reviewer: independent critic / director; date: 2026-10-11.
Scope: Stage C replication and ablation registration.

## 1. Experimental scope and partition
- Partition C: seeds 120001 through 120060 (60 fresh clusters).
- Certified fresh in `seed_inventory_closure.json`.
- All six scenario families: `development`, `sparse`, `cold_start`, `delayed`, `shift`, `drift`.
- Policies evaluated: `G`, `P`, `N3`, `N3_fifo4`, `N3_two` (5 policies).
- Total episodes: 60 seeds × 6 families × 5 policies = 1,800 episodes.

## 2. Hypotheses and contribution contrasts
- Primary replication hypothesis: N3 maintains a positive paired point difference vs G on fresh C seeds (N3 − G > 0).
- Batch size contribution contrast: N3 vs N3_fifo4 (isolates joint selection from querying 4 bundles).
- Jointness contribution contrast: N3 vs N3_two (isolates 4-bundle jointness from 2-bundle optimization).
- Reference contrast: P vs G (verifies stability of population control on fresh seeds).

## 3. Resource forecast and ceilings
- Per-episode compute: ~3.5s–4.5s CPU time.
- Total CPU forecast: 1,800 × 5.0s = 9,000 CPU seconds (2.5 CPU hours), well below the 40-hour budget.
- Storage forecast: ~500 KB per episode = 900 MB, well below free disk capacity.
- Workers: 3 offline processes with numerical thread pinning (`OMP_NUM_THREADS=1`, etc.).

## 4. Stage C promotion gate to Stage D
Promotion to Stage D requires:
1. Replicated positive mean effect against G on Stage C (N3 − G > 0).
2. Positive own-parent point effect against its contribution controls (N3 − N3_fifo4 > 0 and N3 − N3_two > 0).
3. Complete, valid execution with zero unhandled fallbacks.
If N3 fails any of these criteria, the line is stopped and G is retained.

Verdict: **PASS**. Approved for Stage C registered execution.
