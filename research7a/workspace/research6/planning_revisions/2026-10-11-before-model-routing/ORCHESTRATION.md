# Team and orchestration contract

The environment has four concurrent agent slots **including the director**. Use root plus three workers in waves; do not manufacture extra capacity through nested agents. Actual experiment processes use a separate bounded pool of three, not one independent pool per agent. The director owns shared registry/decision files and the launcher; developers never edit them concurrently.

## Planning work already completed

| Responsibility | Agent | Exclusive deliverable | Falsifiable question | Allowance | Reviewer |
|---|---|---|---|---|---|
| Director/source and literature integration | `/root` | PLAN, registry, tests, orchestration, literature, planning metadata | Does the plan identify distinct testable mechanisms while preserving the null result? | Reads/browsing/plan arithmetic; no episodes | `next_mechanisms` final plan review |
| Simulator/structural analyst and theorist | `round6_structures` | STRUCTURAL_PROPOSALS.md | Do joint queries/return calendars/local repair expose legal headroom beyond static ranking? | 120 CPU seconds; constructed arithmetic only | `next_mechanisms` |
| Predictive/learning researcher | `round6_models` | LEARNING_PROPOSALS.md | Does public repeat history supply usable signal beyond earlier marginal models? | 120 CPU seconds; no training/worlds | `next_mechanisms` |
| Statistician/adversarial critic | existing `next_mechanisms` | STATISTICAL_CRITIQUE.md, separate PLAN_REVIEW.md | Will fixed gates reject noisy winners and unsupported coverage claims? | 120 + 90 CPU seconds; analytic only | Director |

A new critic spawn hit an actual agent-thread limit; the already available critic was reassigned. The planning organization did not increase global concurrency. Source/proposal reviewers distinguished source deductions, exact toy arithmetic and untested hypotheses. No policy experiments were launched. The agents' CPU allowances are ceilings, not a claim that all tool/browsing time was measured.

## Future execution waves

Role names specify technical responsibility. The particular agent IDs may be assigned when execution begins. Each work order must state question, falsifiable hypothesis, owned files, compute ceiling and reviewer.

| Wave | Director | Worker slot 1 | Worker slot 2 | Worker slot 3 |
|---|---|---|---|---|
| A: headroom | Registration, seed inventory and scope | Simulator forensic analyst: opportunity/funnel/return audit | Mathematical theorist: exact DP, query complementarity, renewal LP proof | Critic/statistician: denominator/leakage/bound challenge |
| A: implementations | Freeze modules/configs and candidate admission | Information-acquisition researcher: N3/N4 | Dynamic allocator: N1/N2/N5/N6 | Critic plus separate implementation checks as completed |
| Training/admission | One shared data job queue and resource ledger | Predictive researcher: L1 public posterior/proper scores | Value researcher: L2 only after planner gate; N7 robustness | Critic/statistician: coverage, selection and fitting review |
| B: screening | Run exact registered queue; no shared edits | Mechanism analyst: fixed trigger/funnel summaries | Production engineer: resource/fallback/replay tests on examined requests | Critic/statistician: searched effects, influential seeds |
| C: ablations | Lock own-parent grid; promotions | Targeted query/dynamic ablations | Independent replicator: implementer-independent actions/counts | Critic: strongest alternative explanation/interventions |
| D: selection | Apply frozen no-candidate rule | Production engineer: contender checks | Independent replicator: grid/statistics cross-check | Statistician/critic: selection/variance/sample-size review |
| E: frozen test | Own scheduler, freeze and health display | Provenance engineer: recorder/source/storage health | Independent replicator: verification code preparation, no tuning | Critic: compliance only; no significance stopping |
| Verification/package | Integrate honest report; final seal | Independent replicator: all final counts/statistics/replays | Production/provenance engineer: restricted runtime, archives | Critic/theory reviewer: final claims and objections |

A developer cannot be the independent checker of their own implementation. If the critic develops a patch, rotate another completed worker into that candidate's adversarial review. Keep a critic involved in every wave; when a slot is idle assign it replication, failed-trajectory audit, simplification or counterexamples. The director integrates disagreements, not agent confidence scores.

## File ownership

Proposed exclusive areas during implementation:

- Director: `research6/registry/`, `orchestrator.py`, `analysis.py`, `decisions.jsonl`, stage job manifests and `results/research6/<run>/ledger/`.
- Forensic analyst: `research6/audits/forensics.py`, mechanism code/report and host-only audit outputs.
- Theorist: `research6/exact/`, specified toy JSON, proofs/LP certificates and THEORY_REVIEW inputs.
- Acquisition developer: `research6/policies/acquisition.py` and its focused tests/specifications.
- Dynamic developer: `research6/policies/allocation.py`, `return_model.py` and its focused tests/specifications.
- Predictive developer: `research6/models/`, public training preprocessing/artifacts and prediction tests.
- Critic/statistician: `research6/reviews/critic_*`, `statistics_review_*`; read-only access to other owners' work.
- Replicator: `research6/replication/`; no import of director analysis functions for final statistics.
- Production engineer: `research6/production/`, recorder/security/archive checks and resource reports.

These directories/modules are proposed; their presence is not claimed by this document. Shared interfaces are agreed in a director-owned contract before concurrent edits. Raw outputs are written once per unique attempt/cell, never by multiple agents. Host audit/training paths are not mounted into evaluated containers.

## Required written disagreement record

For each serious candidate maintain:

```text
hypothesis_id, candidate/configuration hash, parent/control hash
observed evidence | deduction | approximation | speculation
developer's strongest case and predicted mechanism metric
critic's strongest failure/alternative explanation
statistician's design/power/multiplicity review
separate implementation/observation-scope review
discriminating test and result (including negative evidence)
director decision: admit / defer / reject / promote / freeze
unresolved objections, owned artifacts and exact commands
```

Resolve conflicts with source inspection, constructed counterexamples, independent computation or a registered experiment. Do not resolve them by majority vote or reported confidence. Preserve superseded conclusions and negative trajectories. Reviewer files close before the manifest; a later discovery gets a separate amendment package, not an edit inside a seal.

Current decisions: population ranking is a control; joint queries and local fixed-score repair precede expensive learning; only two learning representatives enter the first screen; no unsupported offline-policy causal estimator; no final-day augmentation claim against already maximal G; no guarantee that stronger information improves a heuristic controller; actual qualified reward remains primary; D may select no contender.

Remaining disagreements: the critic prefers an initial eight-policy grid over the director's 12-policy maximum; the director retains breadth with a two-promotion cap and complete controls. The director chooses a one-sided 90% D credibility bound rather than the suggested 80%; neither is confirmatory evidence. The amount of real continuation/query headroom and the usefulness of survivor personalization remain unresolved and are the first experiments' purpose.
