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

# Evidence storage and lossless compression

For sequential-matching evidence, preserve scientific content while reducing
physical storage. The current supported implementation is
`research8/soft_query_followup/v3/storage.py` and its independent archive-aware
checker `research8/soft_query_followup/v3/audit.py`.

- Default to streaming Zstandard level3 (`.tar.zst`) using Python3.14's standard
  library `compression.zstd`. Record Python/codec versions. Explicit gzip level6
  is available for compatibility, but never silently switch codecs or assume its
  storage forecast is equivalent. Do not train a dictionary or alter evidence.
- Use one bounded archive per quiescent attempt. Store archives and catalogs
  outside the logical raw attempt directory. Avoid millions of tiny compressed
  files and enormous unindexed bundles.
- Preserve original commit/registration bytes. Bind every logical file's original
  relative path, SHA256 and byte length to the physical archive's SHA256, byte
  length, codec and level. Compression is a storage wrapper, not a new outcome.
- Publish/fsync the archive and immutable catalog, then fully decompress and
  verify original byte hashes before removing any raw duplicate. Reject unsafe
  paths, links, changed writers, extra or missing evidence, truncated archives
  and hash mismatches. Retain failed/incomplete attempts as well as completed
  cells. Never purge evidence to satisfy a size target.
- Archive only stopped/quiescent writers. Do not move, replace or compress a live
  attempt. Resume after interruption only with recorded source/registration
  identities, retained commit hashes and the exact remaining original cells.
  Never call previously executed seeds fresh or count replays as new samples.
- An archive-aware independent audit materializes at most one bounded cell at a
  time on the external results drive, validates all original hashes, reconstructs
  public events and still checks the complete fixed grid. Do not extract the
  entire campaign merely to audit it. Current audit/raw-attempt bounds are512MiB;
  the continuation launcher reserves raw-worker/archive overlap and audit space.
- Use streaming/chunked compression and hashing, external-drive temporary files,
  and measured storage forecasts across policies/families. A campaign target of
  15GiB is a guarded budget, not permission to drop logs or samples. If reserved
  capacity cannot fit, stop dispatch, drain workers and preserve the study.
- Keep seed-bearing registrations, inventories and commits in freshness reviews.
  Summarize bulky historical archives with content/provenance digests and explicit
  scope; do not exclude all result directories and claim universal freshness.
- Infrastructure-only optimizations may reduce repeated hashing and process
  monitoring overhead, but must preserve policies, simulator rules, public
  observation boundaries, deadlines, outcome definitions and independent audits.
  Frozen versions and prior attempts are preserved, not overwritten.

The current user-authorized simulation limit is seven cell workers globally,
with an8GiB combined monitored worker-tree RSS guard on the current host.
This does not change the four-agent/three-child delegation limit above.
