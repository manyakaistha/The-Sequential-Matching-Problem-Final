# Round 1 submission map for the final response

## What Round 1 established, and what it did not

The Round 1 entry selects `simple_fifo` and explicitly reports a negative confirmatory result. Across 40 fresh seed clusters (3001–3040; 240 episodes per policy), its MSMI was 0.331 per 100 arrived members versus 0.373 for supplied greedy: paired difference −0.042, 95% paired-t CI [−0.091, +0.008], p=0.096, standardized effect −0.270. The cluster-bootstrap CI is [−0.090, +0.004]. It therefore did not show improvement and excludes the registered +0.10 target at the reported CI bound. Coverage, mutual acceptance per assignment, and mean ask cost were equal (0.340, 0.137, and 203.0); dates per mutual acceptance were 0.779 vs 0.754.

The six-family confirmation differences (simple_fifo minus greedy) are development −0.100, sparse −0.013, cold start +0.037, delayed 0, shift −0.062, and drift −0.113 MSMI/100. The report attributes the drift/shift weakness to a static policy, and flags sparse geography as structurally constrained: 2.0 visible feasible edges before clarification and 45.6 under all-arrival truth, on average. These are synthetic-simulator findings, not claims about real markets.

Other reported findings and limits to address plainly:

- The graph is general and sparse, not naturally bipartite. Mean development feasible edges are reported as 17.8 before clarification, 59.6 after resolving non-declined hard fields, and 265.0 under all-arrival truth. The sparse-family corresponding counts are 2.0, 8.2, and 45.6. The report says about 35% of members decline at least one hard field.
- Missing hard constraints block an introduction; soft scores cannot override reciprocal hard infeasibility. The policy asks hard bundles (3 units) under a daily 12-unit budget; soft questions cost 1. A hard bundle is therefore at most four asks per day. Declined fields are not re-asked.
- The selected scoring model has near-chance terminal discrimination (AUC 0.507) and its predictions are near constant. The stated calibration table overpredicts each outcome stage below response; terminal mean prediction/observation is 0.0115/0.0088. The selected policy does not learn online. The report’s 38-day maturity restriction is described for the research model; do not imply it makes the selected simple model discriminative.
- Outcome funnel on 18,133 `simple_fifo` introductions: 58.3% both responded, 13.4% mutually accepted, 10.5% had a date, 2.7% were both positive for the second meeting, and 0.88% qualified. Only 159 qualified outcomes are listed. The submission attributes substantial loss to dates beyond 30 days and/or late second-meeting feedback; it gives 330/489 both-positive outcomes disqualified for the candidate. Under its stated response-delay model, both responses meet the three-day deadline with probability (3/5)^2 = 0.36, so late feedback alone disqualifies 64% in expectation.
- The LP is an expected-reward relaxation for seed 101 with clairvoyant hard-field information and relaxed constraints; it is not a seedwise realized-outcome ceiling. The theory section also notes non-submodular clarification value, insufficiency of node prices without odd-set constraints in general graphs, and nonseparable per-member continuation costs.
- Round 1’s planned Round 2 directions are improved feature interaction/scoring, aggregate regime detection, query strategies beyond FIFO, deadline-aware allocation, and multi-day lookahead. They are plans, not demonstrated gains.

## Clarification: FIFO and Greedy are different

In Round 1, `simple_fifo` means FIFO ordering for hard-bundle questions plus a greedy first-fit matching step. “Greedy baseline” is the supplied reference action policy, whose ask behavior and allocation behavior are separate functions. FIFO is a query-order rule; greedy is an allocation procedure. The submission’s “FIFO Clarification Invariance” claim concerns query schedules when policies all use the same pure FIFO hard-bundle rule: because incomplete members cannot be matched and availability is exogenous, changing the matching decision does not change those ask schedules. It does not say that FIFO allocation and greedy allocation are the same, nor that all policies have identical matches or outcomes.

The current repository-root [`policy.py`](../../policy.py) is the reference-baseline adapter, not the Round 1 `simple_fifo` candidate. In ask phase it calls `kit.baseline_asks(state)`, except `no_asks` returns an empty list. In match phase it calls `kit.baseline_match(state)` for `greedy` and `no_asks`; only `random` builds legal feasible edges, shuffles them with `Random(17 + day)`, and greedily takes a disjoint batch. Thus the root executable has no `simple_fifo` scoring, FIFO candidate-specific query implementation, learned/aggregate model, or candidate memory. Memory is passed through unchanged.

## Executable and report alignment

The Round 1 PDF text says the production executable has a seven-second SIGALRM guard, solver fallback, and reports stress results (including 7.1-second dense matching, peak RSS 95.6 MiB, 52.8 MB image); its reproducibility section reports latency and memory. The current repository-root Dockerfile packages only `kit.py` and the baseline `policy.py` on Python 3.12.7 slim, with no solver dependency or such guard. These Round 1 executable claims therefore do **not** describe the current root executable.

There is a separate later research implementation: [`research_policy.py`](../../research_policy.py), packaged by [`Dockerfile.research`](../../Dockerfile.research), which [`research/REPORT_2026-10-07.md`](../../research/REPORT_2026-10-07.md) says was executed separately while the root kit and policy remained unchanged. That report identifies its candidate as frozen product fusion, not Round 1 `simple_fifo`, and gives separate reproduction and container evidence. Do not merge those evidence sets or describe the research executable as the Round 1 candidate. The report’s statement that the main research executable was executed is consistent with the separate research source/package; it does not make it the currently configured root submission. The Round 1 note’s production-safety paragraph cannot be source-verified from the current root files inspected here.

## Reproduction commands and comparator names

The current final-submission contract in `docs/SUBMISSION.md` requires full-episode machine-readable results for **greedy, no-clarification, random-feasible, and the proposed method on identical seeds and scenarios**. The local root CLI uses `--baseline greedy`, `--baseline no_asks`, and `--baseline random` (see README); these are implementation names for greedy, no-clarification, and random-feasible. Its documented current commands are:

```bash
python -m unittest -v
python verify_data.py
python evaluate.py --seeds 101,102,103 --variants all --output results/final.json
docker build -t sequential-policy:submission .
python evaluate.py --image sequential-policy:submission --seeds 101 --output results/container_check.json
```

For separate baseline result files, `README.md` gives:

```bash
python evaluate.py --baseline greedy --seeds 101,102,103 --variants all --output results/greedy.json
python evaluate.py --baseline no_asks --seeds 101,102,103 --variants all --output results/no_asks.json
python evaluate.py --baseline random --seeds 101,102,103 --variants all --output results/random.json
```

Round 1’s own historical reproduction commands instead run `research/extended_benchmark.py --seeds 3001-3040 --variants all` and `evaluate.py --image sequential-policy:submission --seeds 101`; these reproduce claims only if their required historical research files/assets are present and the command version matches the archived report. The Round 1 report’s benchmark configuration names include `greedy` and `simple_fifo`, plus ablation names such as `no_learning_fifo`, `terminal_soft`, `blossom-full`, and `hungarian`; those are research variants, not the three root CLI `--baseline` choices.

## Chart and report assets available

The Round 1 note references these renderable assets under `research/plots/`: `fig1_primary_comparison.png`, `fig2_scenario_breakdown.png`, `fig3_funnel.png`, `fig4_feasibility.png`, `fig5_calibration.png`, and `fig6_ablation_dotplot.png`. Its Markdown counterpart references the relative `plots/...` paths, which resolve from the `research/` directory. Useful visual answers are: paired primary comparison (Fig. 1), per-scenario gains and losses (Fig. 2), outcome attrition (Fig. 3), scarcity and clarification (Fig. 4), weak calibration/discrimination (Fig. 5), and component/query ablations (Fig. 6). Preserve the captions and denominators when reusing these charts; the main Round 1 prose explicitly says the confirmatory stage has 240 episodes per policy, while seed clusters—not episodes—are the independent paired units.

## Source consistency notes for editorial review

The attached PDF text and `research/ROUND1_SUBMISSION.md` are not fully identical. The PDF says 22 development configurations and its architecture/results sections describe 22; the Markdown hypothesis paragraph says 20, while its development-stage table again says 22. The PDF also contains a few expanded details (e.g. feedback deadline disqualification wording). Use the submitted PDF as the frozen Round 1 record where they differ, and avoid silently harmonizing contradictory counts. Both documents agree on the negative confirmatory result and candidate description. The document also labels six scenario families but the generated-world table uses “Shift” and “Drift” while prose elsewhere calls them shifted outcome weights/changing response conditions; keep the scenario labels consistent with the released evaluation (`shift`, `drift`).
