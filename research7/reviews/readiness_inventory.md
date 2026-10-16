# Research7 execution readiness inventory

This file records what the inspected artifacts establish for a future execution guide. It is evidence collection, not an execution authorization or a methodology ruling. Inspection was read-only: no worlds or policy episodes were generated, and no fits, replays, tests, or hour-scale runs were launched for this inventory.

The machine-readable inventory is [readiness.json](../execution_guide/readiness.json). The root methodology critic owns conclusions drawn from these facts.

## What is implemented

The 7b workspace contains a registered coordinator at `research7b/workspace/research7/runtime/cli.py`, a guarded episode runner at `runtime/runner.py`, a fail-closed validator at `registry/validator.py`, and a smoke registration builder. The CLI accepts a registration, output path, worker count, and workspace path; it caps workers at two. The coordinator checks the exact cell grid, source and dependency hashes, freshness evidence, independent review, resource limits, leases, existing commits, and output/disk reserves. Interrupted attempts and invalid/conflicting states block continuation pending review.

The registered trusted in-process route is explicitly limited in `runner.py` to `P1_smoke` with policy IDs `G`, `N`, `R`, `P`, `K`, and `Q6`. A `subprocess_json` route exists, but the inspected runtime and smoke review do not certify a restricted production container. The available CLI is a generic registered coordinator, not a set of commands for every planned research phase. Do not invent or infer future CLI syntax from the plan.

The completed 7b P1 smoke registration contains four seeds, six families, and the six reference policies only. Its 144 cells completed with 17,280 wire invocations, zero invalid commits, zero fallbacks, and maximum observed concurrency two. Its own integrity review excludes superiority, candidate admission, learning/fitting, production-container certification, and scientific merge/archive-seal claims. Planned candidates Q1, H1, A1, A2, Q2, D1, D2, L1, L2, and X1 are absent from that smoke panel. The P1 admission receipt applies to its reviewed smoke design and cells only.

## What remains a plan

`research7/plan.json` labels itself `planning_only_not_execution_registration`, has authorization `planning_only`, and records zero new policy episodes, fits, and phase tests at plan time. It explicitly says future runtime, registry, merge modules, and CLIs are specifications, not phase execution authority. The stage table adds to 99,384 distinct planned cells/episodes: P1 384; P2 train 3,072; P2 validation 1,536; P2a 360; P3 4,608; P4 6,912; P5 6,912; P6 75,600. Physical verification replays and retries are additional attempts charged to finite budgets, not new independent samples.

`research7/TEST_SPEC.md` states that its tests are planned, not executed. It enumerates requirements for exact reduced models, deployed-candidate agreement, protocol and timing fixtures, leakage isolation, logging and crash recovery, resource and container behavior, fit provenance, retries, cross-host parity, statistics, seed freshness, and archive restoration. These become gates only when implemented, run, and reviewed with the required evidence.

## Resource observations and limits

The smoke integrity metadata records 861.571 total worker CPU seconds, a sum of 888.956 worker wall seconds, and 1,721,911,410 output bytes across 144 attempts. The resulting averages are about 5.983 CPU seconds, 6.173 wall seconds, and 11,957,718 output bytes per reference smoke attempt. Maximum observed worker peak RSS was 73,482,240 bytes. These describe this smoke and its logging path; they do not establish candidate, fitting, or later-stage runtime.

For transparent scale context only, multiplying the 99,384 planned distinct episodes by those six-reference-smoke averages gives about 165.17 CPU hours, 170.42 summed wall hours, and 1,106.79 GiB of output. At the same average, 160 CPU hours cover about 96,271 attempts and 100 GiB cover about 8,995 attempts. This arithmetic is explicitly not a candidate runtime forecast or feasibility finding. It signals that later batch sizing must use candidate-specific measured costs, the plan's 1.5 headroom factor, retries/replays and the actual output policy, then stop against the registered aggregate and free-space budgets.

Plan budgets are 160 CPU hours for 7b simulation/tests, 24 CPU hours for 7b fits, 100 GiB output, 30 GiB minimum free reserve, and 10 GiB combined working RSS. The 7a plan is 6 CPU hours, 8 GiB output, 4 GiB free reserve, and 2 GiB working RSS. The current `df -k .` snapshot reports approximately 241.89 GiB available on `/Volumes/1700 APFS`; that is point-in-time free space, not reserved batch capacity. The prior Research5 cleanup record reports 15,501 files and 85,029,342,282 logical bytes removed, with three archives retained. It is historical context, not current capacity evidence.

The smoke registration froze numpy 2.5.3, scipy 1.18.1, and networkx 3.7; the currently installed versions inspected match those values. Any later registration must freeze its own environment and source closure.

## Independent 7a receipt

The exact independent receipt in `research7a/workspace/research7/exact_independent/evidence/transition_20261012/review_receipt.json` accepts seven tests of a declared finite reduced-model oracle. It says its scope is not deployed-candidate or full official-protocol validation. Remaining gates include deployed D1/D2/L2 agreement, detailed simulator feedback/eligibility fixtures, and broader D2 admission via dominance mapping or explicit official query aliases. The receipt itself states the baseline smoke has no independent D1/D2 proof dependency.

## Evidence sources

- `research7/plan.json`, `TEST_SPEC.md`, `routing_profiles.json`, and `ORCHESTRATION.md`: planned grid, budgets, roles, and gates.
- `research7b/workspace/research7/runtime/cli.py`, `runtime/runner.py`, `registry/validator.py`, and `registry/build_smoke.py`: implemented coordinator, guard behavior, validator requirements, and smoke-only builder.
- `research7b/workspace/research7/registrations/P1_smoke.frozen.json`: frozen smoke scope and versions.
- `research7b/workspace/research7/reviews/smoke_completed_integrity.json` and `audits/smoke_admission.json`: completed smoke counts, resource observations, exclusions, and smoke-specific admission.
- `research7b/workspace/research7/reviews/smoke_storage_inventory.md`: independent read-only storage and logging format inventory; its snapshot differs in timing/progress fields and should not replace the final integrity metadata totals quoted above.
- `research7a/workspace/research7/exact_independent/evidence/transition_20261012/review_receipt.json`: reduced-model review scope and remaining gates.
- `scratch/cleanup_research5/cleanup_result.json`: historical cleanup record.
