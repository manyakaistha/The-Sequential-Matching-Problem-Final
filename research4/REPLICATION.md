# Independent frozen-confirmation replication

Completed 10 October 2026. Owner: independent replicator/statistician; named reviewer: director. No inference, registry, old-study source or raw primary grid was edited. This replication verifies execution and analysis of existing confirmation worlds; it is not another fresh-seed confirmation.

The independently owned `independent_replicator.py` implements a separate simulator request loop, public-event reward reconstruction and seed-cluster analysis. It does not import the director's benchmark/analyze or evaluator scoring code. The evaluated inference and shipped simulator necessarily remain shared dependencies. Each episode has 60 ask/match action days and 40 follow-up days. Policy input is serialized JSON public observation and memory only.

## Fixed replay coverage and findings

Selected `population_control` and shipped greedy were independently replayed on seeds 83001 and 83002, all six families, in direct and fresh-subprocess execution: exactly 48 episodes and 5,760 invocations. Both seeds were already part of the completed registered confirmation. Every episode was valid, had zero fallback, and matched the reference's complete ordered actions, canonical semantic actions, action digest, semantic digest and independently reconstructed shared outcome metrics. Thus neither ordering-only differences nor outcome-only agreement conceal a discrepancy. Every tested invocation completed below ten seconds; the largest measured call was 0.292526292 seconds. This finite scope is not a universal timeout guarantee.

The reference was the complete 672-episode `confirmation.json`, not an implementer's small selected excerpt. The replay output retains every row, both run commands, source hashes and complete-grid independent statistics in `results/research4/replication_confirmation.json`. Direct/subprocess stdout and stderr are preserved in their separate replication logs. The replicator SHA remained `d6af7874906fe4d3795ab653e70f1a4208691201fc79d6a0636ea2cee64ef874` throughout both runs.

## Independent full-grid analysis

The audit checks the exact 56-seed × six-family × two-policy grid, no duplicates or missing cells, complete status, zero invalid episodes/failures/fallbacks, frozen source/configuration/registry hashes and exact selected comparison. Each seed's six families are averaged before paired uncertainty is calculated; assignment-level independence is never assumed.

| Quantity | Independent result |
|---|---:|
| Greedy mean MSMI/100 | 0.313988095238 |
| Selected mean | 0.370535714286 |
| Paired effect | +0.056547619048 |
| Paired seed SD | 0.227584562404 |
| Nominal 95% t CI | [-0.004399924768, +0.117495162863] |
| Two-sided p | 0.068327248349 |
| Program 98.333333% CI | [-0.018552709965, +0.131647948060] |
| 10,000 whole-seed bootstrap 95% CI | [-0.001488095238, +0.114583333333] |
| Leave-one-seed-out effect range | [+0.043939393939, +0.066666666667] |
| Qualified totals, selected / greedy | 249 / 211 |

Neither nominal superiority nor the registered three-test program gate (alpha .05/3) passes. The practical +.10 effect remains inside the primary interval. No superiority, inferiority or equivalence is established. Positive leave-one-out point estimates do not overturn the registered interval.

## Exact reproduction commands and compute

Run from repository root using the recorded environment:

```sh
.venv/bin/python -m research4.independent_replicator --policies greedy,population_control --seeds 83001,83002 --variants all --reference results/research4/confirmation.json --cluster-audit --output results/research4/replication_confirmation.json
.venv/bin/python -m research4.independent_replicator --policies greedy,population_control --seeds 83001,83002 --variants all --mode subprocess --reference results/research4/confirmation.json --cluster-audit --output results/research4/replication_confirmation.json
```

The output appends runs when it already exists; reproduce into a fresh output path to avoid duplicate coverage. One worker ran each replay. An outer `RUSAGE_CHILDREN` measurement includes nested subprocess CPU, unlike the replay row's Python process CPU field.

| Run | Measured OS child CPU seconds | Wall seconds |
|---|---:|---:|
| Direct 24 | 62.793442 | 64.333617 |
| Subprocess 24 | 187.754714 | 191.382817 |
| Replay total | 250.548156 | 255.716434 |

The 48 replay episodes fit the 300-CPU-second allowance. A separate successful public-trace/provenance/production audit consumed 36.446611 process CPU seconds and 40.719580 wall seconds. Known measured replay plus this auxiliary cost is 286.994767 CPU seconds. An earlier auxiliary helper failed after reconstruction because it incorrectly compared the deployed application-file set to the host evaluator/benchmark freeze set; its CPU measurement was lost on assertion failure. It produced no evidence artifact or changed results. The corrected audit compares deployed application hashes to their corresponding host application hashes and separately verifies all frozen host hashes. Consequently the **entire** verification effort cannot be claimed to have stayed below 300 measured CPU seconds; the unsuccessful helper adds unmetered ancillary cost. The command ledger and auxiliary artifact disclose this limitation rather than treating row-level process CPU as total compute.

The auxiliary audit independently reconstructed all 672 public date-qualified positive/qualified counts and the secondary deadline-proxy paired t/bootstrap result. It also checked every inherited manifest record and selected three-mode production output, without generating more worlds. Its report is `independent_final_auxiliary_audit.json`. This is statistical and execution replication; it does not supply a second independently written policy implementation or independent random-generator implementation.
