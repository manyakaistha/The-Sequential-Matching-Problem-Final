# Independent implementation correctness review

9 October 2026. Reviewer owns this file, `test_round3.py`, and correctness JSON;
reviewed implementation files are director/theory-model researcher owned. Named
reviewer: critic. Question: can observation-only legality or full-horizon protocol
be falsified? Hypothesis: no violation on valid shipped requests; finite tests do
not prove correctness on arbitrary inputs. Compute budget 10 CPU minutes, one
worker; only examined seed101 and constructed requests.

## Source review

`research3/policy.py` receives JSON observations only. It imports public `kit`
constants and checks; model inference imports public coefficients/constants but
has no file/network/world access. Matching candidates receive only legal edges;
verified feasibility, current availability, used dyads and endpoint-disjointness
are checked independently of ranking. The greedy candidate directly calls shipped
`baseline_asks` and `baseline_match`; one-shot exact actions were independently
compared. The surplus soft query modes preserve FIFO hard-bundle choices and use
budget left after them. They query only currently legal-edge endpoints; a member
newly verified by this invocation will not receive its soft query until a later
ask, since query selection precedes bundle resolution. This is a design
limitation, not leakage or illegality.

The model scorer's uniform-response second moment is exact for the generator;
Beta response updates are a moment-matched approximation, not the exact posterior
under a truncated uniform prior. Regime probability mixture assumes equal shipped
families, fixed selection-independent prior weights and no regime updates. Actor
bias/soft expectations use inherited five-point Gaussian quadrature and independent
missing-field priors. These are documented approximations. Response counts use
only received explicit events; pending introductions add no failures. Shared
Gaussian dyadic effect survives integrated population scoring. Offline coefficients
are embedded from old development seed-separated snapshots, not loaded at inference.

`research3/benchmark.py` delegates the unchanged shipped 60-action-day plus
40-follow-up `evaluate.episode`; it validates JSON shapes and resource sizes,
records failed rows, and saves assignment-time observed member fields before
advancing actions. Snapshots' `prediction` is a auxiliary inherited integrated-prior diagnostic, not
necessarily each candidate's scoring function: calibration analyses must identify
it accordingly. All completed-feedback labels are public; hidden world data remain
inside Simulator. In-process JSON actions and subprocess share policy code. The
worker allowance is explicitly restricted to one or two processes. Full-episode
request and memory checks are retained; inference wall limits in direct mode are
measured retrospectively in addition to the policy's interrupting alarm.

## Disagreement, correction and finite tests

Found an actionable timer bug in first implementation: it discarded a caller's
existing ITIMER_REAL deadline. Director corrected this before screening, preserving
handler and adjusted timer and respecting a shorter outer deadline. The independent
outer-alarm regression passes. Empty-action fallback is legal but forfeits reward;
all fallback counts must remain visible, especially subprocess stderr warnings
that are not currently summarized as per-episode fallback counts.

Independent suite covers shipped-greedy exact actions; all 13 candidate legal
ask/match actions; empty pools; permanently declined/no-feasible-edge pools;
exhausted budget; malformed memory reset; oversized requests; pending outcome
label exclusion; blocked solver imports; actual SIGALRM interruption; direct versus
subprocess actions across five diverse modes; and outer deadline restoration.
Twelve tests pass. Test harness initially omitted synthetic response parameters
when constructing a simulator state; corrected reviewer harness, not policy.

Constructed dense test has 200 endpoints, 19,900 feasible pairs and 800 resolved
response history events. All 13 candidates return 100 disjoint legal pairs.
Observed call times .045–.083 seconds, request439,886 bytes, memory2 bytes. This
single dense shape does not prove arbitrary worst-case runtime. Candidate caches
remain bounded by inherited integrated-model cache limits. Serialized policy
memory is always `{}`; feedback histories are public request input, so no hidden
persistent personalized memory is required and pruning is vacuous.

Full existing seed101 greedy episode independently compares in-process and
subprocess actions/outcomes (120 invocations, complete follow-up). Exact byte
action digest is compared separately from semantic results; results in JSON.

## Container limitation

Read-only `docker info` failed: cannot connect to
`/Users/manyakaistha/.docker/run/docker.sock`. Consequently this review does not
claim new container execution, read-only filesystem resource enforcement, image
size, 64-PID isolation or startup latency. Prior extended-policy container evidence
cannot certify the new policy image. Host tests and source offline checks are
useful finite evidence; new deployable proposal requires a current restricted
container test when Docker is available. No simulator/evaluator files were edited.

## Superseding current restricted-container evidence

Director restored Docker; server27.4.0 became available. First build failed because
repository `.dockerignore` excluded the new inference files; the failed
`production_greedy.json` is retained. A corrected build creates an isolated
temporary context of five inference source files plus Dockerfile, with no research
data or audit modules. `production_greedy_retry.json` records a complete oldseed101
three-execution greedy replay, all120calls each, exact byte action/semantic digest
and funnel parity. Actual inspected image size44,742,809bytes is below documented
**2GiB** limit (docs/POLICY_INTERFACE.md:37); this is Docker inspect uncompressed
Size, not an inferred compressed download size. Resource command enforces2CPUs,
1GiB RAM/swap,64PIDs,read-only,no-network,unprivileged65534 and64MiB/tmp.

`production_dense.json` adds all13 candidates on200 dense endpoints and800
resolved-history events under the same restrictions. Host/container responses are
exactly equal,100pairs each, maximum call time.39524seconds. The application file
inventory contains only kit.py,terminal_model.py,model_candidates.py,policy.py and
research3/__init__.py. The dense diagnostic briefly overlapped the last portion
of the greedy replay; this deviation from the one-worker plan is disclosed, with
no claim that latency was measured on an otherwise idle machine. All reported
limits are configured actual Docker command limits; no exact peakRSS is claimed.
These tests supersede the current-infrastructure gap above for the tested image
and workloads. Selected-candidate full-episode parity remains pending selection.

## Actual enforcement probe and fallback telemetry follow-up

`resource_probe.json` now observes effective cgroup values inside the restricted
image: `cpu.max = 200000 100000`, `memory.max = 1073741824`,
`memory.swap.max = 0`, `pids.max = 64`. UID and GID are 65534. Attempted root
write fails with errno 30 (read-only filesystem); egress socket connect fails with
errno 101 (network unreachable). The interface list contains loopback and virtual
tunnel devices, retained verbatim; this is not a claim that only loopback exists.
All five application source hashes exactly match host files. Probe command and its
actual UTC start timestamp are recorded.

The production runner now uses bounded file-backed child stdout/stderr capture,
matching strict evaluator shape/size/deadline handling while retaining fallback
warnings per invocation. A malformed-state diagnostic produces one captured
`round3 fallback: TypeError` warning for each subprocess/container call. Historical
full-greedy replay used the original evaluator, so its subprocess/container
fallback counts remain unknown rather than being retrospectively asserted zero.
The selected replay will use the updated capture implementation.

`commands_forensics.json` retains exact commands, captured probe timestamp and
reconstructed null timestamps for prior executions. Historical production child
and Docker daemon CPU was not instrumented; it remains unknown. Measured elapsed
time is reported separately and is not substituted for CPU usage.
