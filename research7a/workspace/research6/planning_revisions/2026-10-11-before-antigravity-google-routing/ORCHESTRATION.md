# Team and orchestration contract

The environment has four concurrent agent slots **including the director**. Use root plus three workers in waves; do not manufacture extra capacity through nested agents. Actual experiment processes use a separate bounded pool of three, not one independent pool per agent. The director owns shared registry/decision files and the launcher; developers never edit them concurrently.

## Model and reasoning routing — active user preference

The user requested smaller models for simple delegation and stronger models for
complex work, with effort no higher than `high`. This preference is persistent in
the repository's [AGENTS.md](../AGENTS.md) and machine-readable
[agent_routing.json](agent_routing.json). The live delegation helper
[agent_router.py](agent_router.py) constructs validated arguments for the actual
`collaboration.spawn_agent` tool; it does not call an API or launch the research
experiment runner.

| Task | Requested model | Effort | Review responsibility |
|---|---|---|---|
| Find files, source locations; bounded reading; run specified mechanical checks | `gpt-6-luna` | low | Return paths/lines/raw evidence; director or Sol interprets |
| Structured extraction, inventories, artifact indexes | `gpt-6-luna` | medium | Sol reviews completeness/denominators/scientific interpretation |
| Bounded implementation, independent implementation review | `gpt-6.1-sol` | medium | Separate developer/reviewer ownership |
| Simulator audit, algorithms, prediction, statistics, independent replication, production and criticism | `gpt-6.1-sol` | high | Own technical conclusions and written reviews |
| Difficult proofs/bound certification and coupled dynamic-planning reductions | `gpt-6-astra` | high | Independent Sol/Astra critique and director integration |
| Director | Existing root `gpt-6.1-sol` | medium | Shared registry, slot accounting and final decisions |

These are requested routes supported by this environment's exposed model list,
not measured cost/performance comparisons or a claim about every account's model
availability. `low`/`medium`/`high` are reasoning settings, not hard thinking-token
budgets. No `xhigh`, `max` or `ultra` route is permitted. CPU allowances and concise
output targets are work-order limits, not timers enforced by the helper.

Bundle related small reads in one Luna task rather than spawning one agent per
file. Give Luna explicit paths, a bounded question, requested evidence format and
a named stronger reviewer. It may identify contradictions but cannot approve a
scientific claim, promote a policy, select confirmation seeds or certify a proof
by itself. Send reasoning-intensive interpretation as a separate Sol/Astra task.
For example, Luna can collect every exit/busy source location; Sol determines the
correct transition semantics; Astra proves a contested adaptive occupancy bound.

All routed spawns explicitly set `model`, `reasoning_effort`, and
`fork_turns="none"`, supplying the needed context in the message. Full-history
forks do not accept model overrides in the current tool. A bounded recent-history
fork may be used manually if needed, but must retain explicit model/effort and be
recorded. A follow-up keeps the original agent's model/effort; do not assume it
retunes a previously expensive worker into Luna. Reuse only a matching idle
worker; otherwise queue/spawn an appropriate new task within the actual limits.

Before each spawn, inspect live agents. The helper checks the provided active
count, including root, and rejects a fifth active agent; the live tool remains
authoritative if that count becomes stale or a separate thread limit is hit.
Children request additional work from the director rather than spawning nested
pools. Keep a critic active during substantive waves. If all slots are busy, queue
simple reads until a slot opens instead of creating unnecessary larger-model
work or weakening independent review.

Escalate once per bounded work order only for an evidenced ambiguity/failure:
Luna low → Luna medium or Sol medium; Luna medium → Sol medium; Sol medium →
Sol high; Sol high → Astra high. Record the original task/profile, reason,
replacement profile and reviewer in the director's delegation ledger. The helper
validates an allowed escalation edge but has no persistent task history; the
director enforces the one-escalation rule. Astra high has no higher route. If the
model is unavailable, report it and queue or explicitly amend the assignment;
never silently substitute or exceed high effort.

Work orders include concrete question, falsifiable hypothesis, deliverable,
exclusive files/read-only scope, CPU allowance and reviewer. Model selection does
not change the four global slots or the three offline simulation workers.

Example Python payload preparation, from the repository root:

```python
from research6.agent_router import build_spawn_args
payload = build_spawn_args(
    "file_discovery", "find_return_rules",
    "Where are return and busy-time rules defined?",
    "The shipped simulator has explicit return boundaries.",
    "A concise path/line evidence list with missing information.",
    "Read only: kit.py, evaluate.py; no file ownership.",
    "/root", active_agents=1, cpu_seconds=30,
)
```

The director then submits `payload` to the live `collaboration.spawn_agent` tool.
It requests Luna/low with no inherited full history. Running this Python example
alone does not spawn anything. Before production delegation, record the routing
file hash, requested/resolved settings when exposed, task ID, context policy,
reviewer and escalation reason. Do not infer exact token usage or resolved model
identity from a name-only agent listing.

On 11 October 2026 this routing was exercised with an explicit Luna/low read-only
inventory task and a Sol/medium independent router review. These were orchestration
checks, not matching-policy experiments. See
[MODEL_ROUTING_REVIEW.md](MODEL_ROUTING_REVIEW.md) for review evidence and limits.
The previous planning snapshot is retained in
`planning_revisions/2026-10-11-before-model-routing/`.

Official OpenAI documentation supports focused independent delegation and notes
that extra agents add overhead; reasoning effort guides thinking rather than
being an exact token cap. The exact model/fork/slot restrictions here come from
the live collaboration tool, not generic API defaults.
[Multi-agent documentation](https://developers.openai.com/api/docs/guides/responses-multi-agent),
[reasoning documentation](https://developers.openai.com/api/docs/guides/reasoning).

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
