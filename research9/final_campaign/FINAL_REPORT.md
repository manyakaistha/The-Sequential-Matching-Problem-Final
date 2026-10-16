# Final Research Campaign Closed

## Outcome: Negative Result (No Candidate Qualified)

In accordance with the pre-registered protocol in CAMPAIGN_PLAN.md:
- An audited 288-episode development screen was conducted across 8 validation seed clusters, 6 environment families, and 6 policy arms.
- All 288 cells were independently audited and verified with zero fallbacks, full world parity, and exact public event reconstruction.
- All 144 reference replays (G, Q6, P) achieved exact bit-for-bit parity with historical baselines.
- Candidate admission required exceeding the baseline Greedy (G) policy in mean qualified MSMI per 100 arrived members.

### Screen Performance Summary
| Arm | Type | Mean MSMI / 100 | Qualified Pairs | Mean Assignments | Coverage |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **G** | Unchanged Baseline | **0.322917** | **31** | 68.46 | 0.3345 |
| **Q6** | Unchanged Reference | 0.229167 | 22 | 69.46 | 0.3354 |
| **model_soft** | Learned Candidate | 0.218750 | 21 | 68.90 | 0.3360 |
| **model_repair** | Learned Candidate | 0.218750 | 21 | 68.96 | 0.3363 |
| **P** | Unchanged Baseline | 0.197917 | 19 | 67.92 | 0.3327 |
| **model_greedy** | Learned Candidate | 0.187500 | 18 | 68.46 | 0.3351 |

### Scientific Conclusion
No candidate heuristic outperformed Greedy (G). In fact, standard Greedy substantially outperformed all learned ranking heuristics on the screening worlds (0.3229 vs. 0.1875 - 0.2188). 

Under the pre-registered rules:
- No candidate qualified for final confirmation testing.
- The 96 reserved fresh confirmation seed clusters were NOT opened and remain completely pristine.
- No further tuning, retries, model fitting, or sample expansion are authorized.
- The negative result is fully preserved as definitive evidence regarding this candidate portfolio.
