# Research7: a testable attempt to improve on greedy

Status: **planning only, prepared 11-12 October 2026**. No round-seven simulator episodes, fitting, candidate benchmarks, confirmation, or exact-model solver runs have been performed. No policy improvement is claimed. The user requested planning, not execution.

Start with [PLAN.md](PLAN.md), then give the smaller machine [PLAN_7A.md](PLAN_7A.md) and this Mac [PLAN_7B.md](PLAN_7B.md). These are cooperating branches of one experiment program, not two independent opportunities to select a winner.

| File | Purpose |
|---|---|
| [EVIDENCE_REVIEW.md](EVIDENCE_REVIEW.md) | Research6 findings, qualifications, both team reports, simulator implications |
| [STRATEGIES.md](STRATEGIES.md) | Ten bounded hypotheses, formulas, implementation contracts, controls and failure gates |
| [TEST_SPEC.md](TEST_SPEC.md) | Exact cases and phase-by-phase correctness, learning, inference and production tests |
| [ORCHESTRATION.md](ORCHESTRATION.md) | Agent waves, model routing, ownership, work orders and cheap-director rules |
| [MERGE_PROTOCOL.md](MERGE_PROTOCOL.md) | Two-machine registration, shard leases, artifacts, retries, duplicates and independent analysis |
| [STATISTICS.md](STATISTICS.md) | Endpoint, six-baseline claim, multiplicity, selection, power and honest conclusions |
| [LITERATURE.md](LITERATURE.md) | Primary-source research and transfer limits; Google routing documentation |
| [plan.json](plan.json) | Inert machine-readable phase limits and unverified seed reservations |
| [routing_profiles.json](routing_profiles.json) | Separate Codex, Antigravity and direct-Gemini routing policies |
| [work_orders.json](work_orders.json) | Bounded tasks and reviewer/ownership assignments |
| [PLANNING_MANIFEST.json](PLANNING_MANIFEST.json) | Input/document fingerprints, current machine facts and scope of validation |

The future implementation paths and CLI interfaces in these documents are specifications. They are not installed runners. Do not point research6's runner at these files or reuse its single-baseline confirmation script unchanged.

All research6 and older source/results/archives remain preserved. Research6 data, including its old confirmation, are now development evidence for research7 and cannot be recycled as new confirmation.

The planning package can be copied to both machines. Before future execution, produce a reviewed execution registration with audited seed freshness, actual source/dependency fingerprints, exact candidate assets, signed-off work orders, machine identities and fixed budgets. Then run only the work authorized in that later execution task. A request to read this plan alone does not authorize experiments.

Final independent planning reviews: [scientific/statistical closure](reviews/FINAL_PLAN_REVIEW.md) and [coupled-strategy closure](reviews/STRATEGY_PLAN_REVIEW.md). The reviews preserve every identified defect and its resolution. [STATIC_CHECKS.md](STATIC_CHECKS.md) records only document/JSON/arithmetic/hash checks; no phase tests passed or executed.
