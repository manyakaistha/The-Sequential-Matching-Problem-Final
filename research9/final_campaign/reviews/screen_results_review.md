# Independent Review: Screen Results & Campaign Closure

2026-10-15; `/root/continuation_critic`, integrating reviewer `/root`.
Read-only review of `results/research9/final_campaign/screen`, `screen_audit_proof.json`, `selection.json`, and `campaign_closed.json`.

## 1. Audit & Verification Findings

- **Grid Integrity**: All 288 declared cells in `screen_registration.json` (8 validation seed clusters × 6 families × 6 policy arms) were durably completed, committed, and archived as `.tar.zst` level 3 files.
- **Independent Full-Grid Event Reconstruction**: `screen_audit_proof.json` passed all checks:
  - `all_valid: true`
  - `complete_registered_grid: true`
  - `world_parity_verified: true`
  - `denominator_parity_verified: true`
  - `public_event_reconstruction_verified: true`
  - `private_world_read: false`
- **Reference Parity**: All 144 reference replays (`G`, `Q6`, `P` across the 48 validation worlds) achieved exact bit-for-bit parity with the historical Research 8 development replication baseline across action digests, final metrics, invocation counts, and zero fallbacks.
- **Fail-Closed Evidence Preservation**: An infrastructure-level live RSS monitor timeout that occurred during the initial 7-worker dispatch on seed group 840090 was cleanly preserved. Seven interrupted attempts and their manifests were retained in `interrupted_failed_attempts/`. The 9 remaining original cells were completed under reduced worker concurrency without altering any frozen sources.

## 2. Statistical Findings & Decision Gate

| Arm | Description | Mean MSMI / 100 | Qualified Pairs | Mean Assignments | Coverage | Cluster SD | Cluster SE |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **G** | Unchanged Greedy Baseline | **0.322917** | **31** | 68.46 | 0.3345 | 0.2614 | 0.0924 |
| **Q6** | Unchanged Q6 Reference | 0.229167 | 22 | 69.46 | 0.3354 | 0.2260 | 0.0799 |
| **model_soft** | Learned Heuristic (Soft Query) | 0.218750 | 21 | 68.90 | 0.3360 | 0.1722 | 0.0609 |
| **model_repair** | Learned Heuristic (Local Repair) | 0.218750 | 21 | 68.96 | 0.3363 | 0.2269 | 0.0802 |
| **P** | Unchanged Random Baseline | 0.197917 | 19 | 67.92 | 0.3327 | 0.1833 | 0.0648 |
| **model_greedy** | Learned Heuristic (Ranked Greedy) | 0.187500 | 18 | 68.46 | 0.3351 | 0.1768 | 0.0625 |

### Gate Decision
The pre-registered candidate admission rule in `CAMPAIGN_PLAN.md` required a candidate to achieve a positive paired mean difference against Greedy (`mean_msmi > summary['G']['mean_msmi']`).
- `model_greedy - G`: -0.135417
- `model_soft - G`: -0.104167
- `model_repair - G`: -0.104167

Zero candidates satisfied the admission threshold. Standard unlearned Greedy outperformed every learned ranking heuristic on the screening distribution.

## 3. Scientific Disposition & Conclusion

1. **Definitive Negative Result**: The candidate portfolio (direct ridge/funnel edge prediction adapted into greedy ranking, soft acquisition, and bounded repair) does not improve upon simple Greedy matching in this sequential setting. Edge-level probability modeling failed to translate into counterfactual policy value.
2. **Fresh Confirmation Integrity**: The 96 reserved fresh confirmation seed clusters were never opened and remain unexamined.
3. **No Retries or Rescues**: In compliance with the campaign charter, no post-hoc tuning, model search, threshold adjustments, or sample expansions are permitted. The campaign is formally closed with status `closed_no_candidate_qualified`.
