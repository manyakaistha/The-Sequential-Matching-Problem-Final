# Stage B registration and preflight review

Reviewer: independent critic / director; date: 2026-10-11.
Scope: Stage B diverse candidate screening registration, seed freshness certification, candidate admission, resource forecast, and statistical analysis protocol.

## 1. Candidate admission and comparison graph
Admitted candidates for Stage B:
- `G`: Shipped greedy baseline (reference control).
- `P`: Frozen round-five population control (historical non-learning benchmark).
- `K`: Maximum cardinality matching on shipped soft score (allocation control).
- `N1`: Local alternating-path repair (length-three augmenting paths and 2-edge exchanges).
- `N2`: Periodic stable reranking (8-day block hash priority on near-tie score classes).
- `N3`: Collision-aware joint hard acquisition (32 particles, up to 4 constraint bundles).

Deferred candidates (under explicit Stage A gates):
- `N4`: Matching-valued hard/soft packages deferred due to lack of demonstrated net modeled value over 4-hard bundles.
- `N5`: Public return reservations deferred due to uncalibrated return distributions on small samples.
- `N6`: Component belief rollouts deferred due to planner complexity and lack of empirical headroom over local repair without privileged state.
- `N7`: Uncertainty-gated allocation deferred due to uncalibrated whole-matching uncertainty.
- `L1`: Reciprocal survivor inference deferred due to sparse repeat-actor history support.
- `L2`: Continuation distillation deferred because teacher N6 is deferred; training/validation stages omitted accordingly.

## 2. Seed freshness and partition certification
- Partition B: seeds 110001 through 110040 (40 seeds).
- `research6/audits/seed_inventory_closure.json` certified zero overlap with repository-visible prior seeds (max prior seed: 90430).
- All six scenario families are evaluated: `development`, `sparse`, `cold_start`, `delayed`, `shift`, `drift`.
- Total Stage B episodes: 40 seeds × 6 families × 6 policies = 1,440 episodes.

## 3. Resource forecast and limits
- Per-episode compute: ~3.3s–5.3s CPU time.
- Total stage CPU forecast: 1,440 × 5.5s = 7,920 CPU seconds (~2.2 CPU hours), well within the 40 CPU-hour allowance.
- Storage forecast: ~500 KB per episode = 720 MB, well within 333 GiB free disk and preserving the 20 GiB reserve.
- Workers: 3 offline parallel processes with numerical thread pinning (`OMP_NUM_THREADS=1`, etc.).

## 4. Promotion and decision rules
- Stage B promotion gate:
  - Complete, valid execution of all 1,440 episodes (zero unhandled fallbacks).
  - Mean paired MSMI/100 difference against G >= +0.025.
  - Positive own-parent difference where applicable (N1 vs K, N3 vs G).
  - Nontrivial decision change observed in actual episodes.
  - At most two distinct mechanisms promoted to Stage C.
  - If no candidate meets the threshold, stop research cleanly and preserve greedy as the benchmark.

Verdict: **PASS**. Registration is certified and approved for frozen execution.
