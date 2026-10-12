# Round-six planning package

Start with [PLAN.md](PLAN.md). It contains the research priorities, twelve-entry candidate/control cap, exact simulator assumptions, oracle scopes, learning admission, fixed experimental funnel, power, stopping rules and resource/logging contract.

- [EXPERIMENT_REGISTRY.md](EXPERIMENT_REGISTRY.md): proposed seed partitions, comparison graph, promotion/selection gates and requirements to freeze a real execution registration.
- [TEST_SPEC.md](TEST_SPEC.md): exact tiny-model cases, correctness/leakage tests, production checks, complete logging, independent replay/statistics and archive acceptance.
- [ORCHESTRATION.md](ORCHESTRATION.md): four-slot agent waves, exclusive ownership, three simulation workers and written criticism/review responsibilities.
- [STRUCTURAL_PROPOSALS.md](STRUCTURAL_PROPOSALS.md), [LEARNING_PROPOSALS.md](LEARNING_PROPOSALS.md): detailed mechanism cases, controls, counterexamples, failure risks and deferred learning paradigms.
- [STATISTICAL_CRITIQUE.md](STATISTICAL_CRITIQUE.md), [PLAN_REVIEW.md](PLAN_REVIEW.md): independent objections, alternative smaller design and accepted corrections.
- [LITERATURE.md](LITERATURE.md): primary sources, inherited ideas and novelty/transfer limits.
- [plan.json](plan.json): machine-readable planning limits; [PLANNING_RECORD.json](PLANNING_RECORD.json): document/dependency fingerprints and tested planning scope.

Read-only consistency check from the repository root:

```sh
.venv/bin/python research6/validate_plan.py
```

The check verifies 28 planning arithmetic/configuration/link conditions, including the illustrative noncentral-t sample size. It **does not execute the research**, evaluate algorithms, certify seed freshness, implement the future orchestrator or pass production tests. The algorithms/runner/test suite still need implementation and execution registration. No new policy episodes or training runs have been performed for this package.

All old research packages remain preserved. The new plan may terminate with greedy retained and no confirmation if development/selection finds no credible gain. It never authorizes significance-driven sample extension.
