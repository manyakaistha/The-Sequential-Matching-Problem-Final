# Research delegation

For sequential-matching research, follow the user's model/effort routing in
`research6/agent_routing.json` and the role/wave contract in
`research6/ORCHESTRATION.md`. Use `research6/agent_router.py` to prepare and
validate explicit `collaboration.spawn_agent` arguments when useful.

- Delegate file discovery, bounded reading and mechanical evidence collection
  to `gpt-6-luna` with `low` effort. Structured extraction uses `medium`.
- Implementation and bounded implementation review use `gpt-6.1-sol` with
  `medium` effort. Simulator analysis, predictive research, statistics,
  production review and adversarial criticism use Sol with `high`.
- Demanding mathematical proofs and coupled dynamic-planning reductions use
  `gpt-6-astra` with `high` effort. Routine work does not use Astra.
- Allowed efforts are only `low`, `medium`, `high`; never request `xhigh`,
  `max` or `ultra`. A reasoning-effort selection is not a hard token limit.
- Give every agent a bounded question/hypothesis, explicit files or read-only
  scope, deliverable, compute allowance and named reviewer. Luna supplies
  evidence; stronger reviewers own scientific and production conclusions.
- Pass an explicit `model`, `reasoning_effort` and `fork_turns="none"` when
  spawning a routed task. Supply the necessary paths/context in the message.
  A full-history fork does not support model overrides in this environment.
- Count the root among the four global active-agent slots; at most three child
  agents may run. Nested delegation does not add capacity. Every child asks
  the director to delegate additional work instead of spawning its own pool.
- Reuse an idle agent only when its originally assigned model/effort and
  ownership fit the new work. `followup_task` does not change its model.
  Do not silently reuse a larger-model agent for a Luna task or assume an idle
  agent was retuned. On unavailable models/slot limits, report the limitation
  and queue or explicitly revise routing; do not silently substitute.
- Escalate a bounded task once only when it exposes an ambiguity, failure or
  need for deeper reasoning. Record the reason and requested model/effort.
  Never increase effort beyond high or create recursive escalation loops.
- Keep one critic engaged during research waves; preserve exclusive file
  ownership and separate developer/independent-review responsibilities.

The round-six research runner remains a proposed implementation. These routing
rules govern live agent delegation now; they do not launch simulations or prove
candidate improvements. Prior completed research/results/manifests/archives are
preserved. No fitting or research confirmation is authorized merely by a task
to find/read files.
