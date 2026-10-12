# Stage C implementation review

Reviewer: independent implementation reviewer (`flash`, medium); date: 2026-10-11.
Scope: Stage C candidate and contribution control implementations (`research6/policies/acquisition.py`, `allocation.py`, `policy.py`).

## 1. Implemented candidates for Stage C
The following policies are implemented and verified:
1. `G`: Exact shipped greedy (`kit.baseline_asks` and `kit.baseline_match`).
2. `P`: Frozen round-five population control (`research4.candidates.population_control`).
3. `N3`: Collision-aware joint hard acquisition across 32 particles and up to 4 constraint bundles.
4. `N3_fifo4`: FIFO 4-bundle acquisition control (queries up to 4 constraint bundles in arrival FIFO order). Matches batch size without joint combinatorial selection.
5. `N3_two`: 2-query joint optimization filled with FIFO actors to separate 2-endpoint complementarity from 4-endpoint jointness.

## 2. Verification checks
- **Syntax and schemas**: Verified with `unittest` (all 26 tests pass).
- **Execution**: Tested on seed 101: `valid=True`, 0 fallbacks across all variants.
- **Resource bounds**: CPU time per episode is ~3.5s–4.5s, well within the 10-second limit. Memory returns `{}` (<1 MiB limit satisfied).
- **Protocol legality**: Only public observation is used. No access to latent truth, private seed state, or future events.

Verdict: **PASS**. Implementation is ready for Stage C registered execution.
