# Research 8: executable reservation and acquisition development

Status: reduced-model correctness/development work. **No simulator win, deployment admission, public model fit, or confirmation.** Research7's completed null result and all prior sources/results are preserved.

## Implemented algorithms

- `planner.py`: exact rational public-belief dynamic matching and fixed-first-action rollout with greedy, immediate maximum-weight, or exact belief continuation. Hidden occupancy clocks are carried in an internal posterior; histories with identical public observations share their continuation action. Rewards are booked once, used dyads remain exhausted, and the final action day retains eventual reward. Complete legal matchings are enumerated for4–8 declared toy actors.
- `bounded_action_menu`: up to12 globally legal matching actions, parent retention, holds/deletions/exchanges, closed current-graph region, six changed actors, outside pairs fixed, explicit overflow fallback. This is a reduced current-graph menu, **not the full D1 menu** with unresolved hard/pending-return boundaries.
- `query_packages.py`: exact nonadaptive complete-package acquisition under a finite joint answer model. Hard asks cost3, soft asks1, total≤12. Identical disclosed answer branches merge before posterior edge scoring/matching. Soft answers never verify hard constraints. Declines and False remain failures; hidden profile scenarios are never independently optimized.

All model probabilities are explicit rational **hypotheses**, not learned simulator beliefs. Actor exit calendars and named future edge/arrival support are declared toy laws; no real future arrival/exit calendar enters a production policy. The current engine has no `decide` adapter and imports no simulator, family, seed, or external API. Its public observation law reveals availability only, not detailed first/date/second-response feedback. Joint disjoint-edge outcome laws and daily arrival events are independent in this reduced model; arbitrary correlated future hidden regimes are not implemented.

## Executed correctness tests

Run from repository root:

```bash
python3 -m unittest discover -s research8/tests -v
```

All21 tests passed in the final independent review run (0.032s), including the pending-reward regression. Checks include every matching action on all64 four-node graphs, K8's764 matchings, dynamic fast/slow return reversal, unused-dyad reuse, terminal reward, hidden-clock nonanticipation, complete query packages, soft/hard budget displacement, explicit caps, menu closure/outside preservation and retention of a distinct parent on exact value ties.

The hidden-clock oracle trap is particularly important: lawful expected value is3/5; maximizing separately for each hidden return-time realization falsely gives4/5. The new engine returns3/5.

In the collision query witness, two shared queries give24/25 and two distinct queries7/5, but a **mixed** package gives3/2. Pairwise comparisons of only the two original packages would miss the optimum. This is a constructed finite model, not simulator evidence.

## Registered reduced sweep

`registration.json` records the recipe/allowances before execution. `run_reduced_grid.py` executed all144 combinations of current reward, future reward, arrival probability, and fast/slow/absorbing return modes. Results are preserved in `results/reduced_grid.json` with source/config hashes and all rows.

- 20 strict improvements over same-model myopic greedy;20 holding decisions.
- Mean expected toy-count gain31/720 (approximately.0431) across this fixed grid.
- Zero bounded-menu rollout regret versus exact DP on this sparse four-actor family.
- Zero-horizon control has maximum full-horizon regret7/10.
- Maximum exact solve time observed approximately.0021s; this excludes process startup, live200-member data, query enumeration and adapter costs. It is **not a sub-second production benchmark**.

The sparse grid contains only an AB opportunity today and AC opportunity onday8. Both future rollout and exact control have only one meaningful future matching choice. Thus zero regret here cannot establish fidelity for rich overlapping future graphs or future waiting decisions. No p-values or finite-sample error bars are relevant to this fully enumerated deterministic recipe; its external validity remains unestablished.

To recompute without overwriting the closed output:

```bash
python3 -c 'import json; from research8.run_reduced_grid import run; print(json.dumps(run()["summary"], indent=2))'
```

The script's default artifact writer uses exclusive creation; it intentionally refuses to overwrite `results/reduced_grid.json`.

## Adversarial continuation results and disposition

`continuation_amendment.json` registered two constructed falsifiers before running them; `results/falsifiers.json` retains the result. Original W1 sources are preserved under `history/w1/` with hashes.

| Falsifier | Greedy tail regret | Static max-weight tail regret | Exact belief continuation regret |
|---|---:|---:|---:|
| Future competing static edges |3/10|0|0|
| Future waiting opportunity |2/5|2/5|0|

These are **initial-action** regrets: evaluate the selected current action with optimal lawful continuation afterward, rather than comparing unlike truncated estimates. The true hold action was already in the menu. Failures therefore arise from continuation evaluation, not missing current actions.

The first fix (a static maximum-weight continuation controller) repairs the competing-edge case but fails the future-waiting case. Both inexpensive approximations exceed the registered1/100 regret limit. **Production fidelity gate: FAIL.** They are excluded from reward screening; no claims of an admitted D1 candidate or simulator gain are made.

The lead algorithm is now the **capped exact belief-continuation core**. It passes these reduced witnesses and can serve as a teacher/reference for future bounded approximation; it is limited to≤8 declared actors and not a200-member runtime controller. A production continuation approximation must preserve *future* holds/exchanges, not only evaluate waiting at the current step. Any new approximation gets its own freeze and held-out fidelity cases; the failed controls remain archived.

The independent review duplicated a falsifier execution after root had committed the first result. Exclusive artifact creation refused overwrite; `results/duplicate_attempt.json` records the noncommitting attempt. It contributes no extra sample/evidence count and no simulator episodes.

## Gates before real reward experiments

1. Expand held-out reduced cases to interacting future graphs; quantify first-action/menu/controller/tail errors separately. The existing≤.01 constructed regret gate is not established outside the sparse family.
2. Build and independently validate simulator-shaped public feedback/occupancy transitions, including cancellation, late positive pause, conditioned pending histories, public-only arrival models and hard declines.
3. Train or admit **public-data** composite reward, answer, pause and return models with complete provenance and whole-world validation. Planned R7 P2 training data was not generated. Existing population-score assumptions do not automatically constitute calibrated admissible new assets; do not silently import generator mixtures/day35 regimes into a new candidate.
4. Add the actual `decide(request, config)` adapter with strict real-answer legality and an already validated frozen fallback; profile full200-member invocations against the user's<1s target and governing10s cap.
5. Freeze a new candidate/config/control graph and new seed audit/registration. Include unchanged G/Q6/P and necessary own parents, respect≤12 replication arms, and analyze independent seed clusters. Prior P4 remains closed; no repeated significance hunting or confirmation before admission.

The user authorized future tests/algorithms; this first registered wave limited itself to correctness/reduced development. A fresh training/evaluation work order must name its dataset splits, resource forecast, independent reviewer and fixed stopping gates before execution. No existing seed audit is misrepresented as certifying a new namespace.
