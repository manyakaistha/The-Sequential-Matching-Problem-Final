# Allocation implementation evidence

Developer: `/root/allocation_impl`, Sol medium. Named scientific reviewer:
`critic`; a separate Sol medium implementation review is required. This is a
developer report, not independent approval or empirical admission. Owned files:
`policies/allocation.py`, `policies/policy.py`, `policies/__init__.py`,
`tests/test_allocation.py`, this report. Previous artifacts untouched.

## Implemented configuration

G calls shipped `kit.baseline_asks` and `kit.baseline_match` directly. P calls
`research4.candidates.decision` with a fresh copy of its unchanged
`population_control` configuration, the round-five inherited population control.
All new allocators use the exact shipped seven-soft-equality integer score and
FIFO asks. Memory is empty. Requests/configurations are cloned by strict JSON.
No seed, simulator object, world-generation call, recorder, fit path, privileged
host input, filesystem read or outcome-derived randomness enters an action.

K uses NetworkX general-graph blossom `max_weight_matching(maxcardinality=True)`
with shipped integer score as its weight, sorted nodes/edges. NetworkX 3.7 is
installed in `.venv`; this dependency must be pinned in the director's deployment
package before admission. Determinism is for that frozen library/runtime, not a
promise of the same choice among equal optima across library versions.

N1 starts from G, tries length-three augmentations, then legal exchanges of two
matched edges that strictly improve score. Two passes, 20,000 probes total,
canonical public-ID traversal; no longer path or global-optimality claim.
N2 orders only exact integer-score ties, using SHA256 endpoint priorities with
salt `research6-N2-public-v1` and `day//8`. A pair is ordered by its sorted two
endpoint priorities, then public IDs. Salt and period are frozen constants.
The exact tie class (width zero) is the prespecified conservative near-tie class.
No alternate salt, daily/fixed priority control, or tuning search was run.

## Verification and scope

Command: `.venv/bin/python -m unittest research6.tests.test_allocation -v`.
Seven tests passed, 0.245 seconds initial runtime. Constructed observations and
constructed graph arithmetic only; no new worlds, simulator episodes, training,
historical re-scoring or benchmarks. Full five-vertex simple-graph enumeration
(1,024 graphs, deterministic heterogeneous scores) agrees with a separate
recursive exhaustive cardinality-and-total-score objective. This is a finite
check of K; the underlying library algorithm supplies general-graph behavior.
The length-three path has greedy middle edge score seven; N1 and K replace it
with the two outer edges. Triangle endpoints remain disjoint. Missing hard
fields, repeat dyads, and unavailable endpoints are excluded. G/P identity,
input immutability, block stability, strict unequal-score precedence, fresh CLI
behavior, injected exception/Deadline fallback and fallback stderr were checked.
The actual elapsed seven-second signal firing was not tested (the Deadline
exception path was injected). There is no general invocation-runtime guarantee.

Wrapper installs a seven-second SIGALRM around candidate dispatch on the main
thread and restores any prior signal/timer. Well-formed input errors rebuild
shipped fallback; malformed input returns the correctly phased empty response.
Stderr reports fallback exception class. The fallback executes outside the
candidate timer: host hard process timeout remains required. Wrapper validation
caps 200 members, one MiB serialized request, day 0–59 and budget 0–12. It checks
hard field shape, duplicate IDs, statuses and introduction endpoints. It is not
a replacement for host action legality, protocol and memory validation.
Non-main-thread invocation cannot install SIGALRM and uses reported fallback.

## Strongest case and counterexamples

Deduction/toy evidence: a legal four-node path exposes G's cardinality loss;
N1 recovers two disjoint introductions without changing acquisition or scorer.
K exactly optimizes the declared current count/score objective. N2 preserves
primary ordering while changing who wins tied competition coherently within a
reuse block. Predicted mechanism metrics are repair incidence/count increase
(N1/K) and tied-edge contention distribution/reuse opportunities (N2).

Counterexample to an N1-equals-K claim: on path `a-b-c-d-e-f` with initial
matching `b-c, d-e`, the only count-increasing augmenting path has length five.
N1 cannot produce the three-edge `a-b, c-d, e-f` matching without a qualifying
intermediate repair. K can. Bound and canonical enumeration order can miss
useful exchanges on larger graphs.

Counterexample to immediate count implying reward improvement: the tested
four-node trap assigns score seven to `b-c` and zero to `a-b,c-d`. If actual
conditional reward concentrates on the middle pair, count-first replacement
lowers expected terminal reward. Returning endpoints, occupancy and permanent
pause can also reverse sequential value. The shipped score is approximate.
N2 may replace a valuable tied edge with a worse latent edge, or may never
change any actual action. These policies are implemented hypotheses only.

Outstanding: independent implementation/observation-scope review, high-effort
scientific review, deployment dependency/timer tests, examined real-request
identity/replay and host protocol tests, director registration/admission. No
scientific promotion, production-readiness verdict or improvement claim made.

## Amendment: authoritative fallback telemetry

11 October 2026; bounded followup, same developer/route, 30 CPU-second ceiling.
Read `implementation_review.md`; independent reviewer
`/root/implementation_review` identified stderr-derived telemetry as a smoke
blocker. Added host-only module `LAST_STATUS`, reset to
`{'fallback': False, 'reason': None}` at entry to every `decide` invocation and
set to fallback true with exception-class reason before rebuilding baseline or
returning malformed-input empty output. This status is never consumed by the
allocator and does not enter action or memory JSON. Thus a failing baseline
fallback still leaves the fallback status available to the host. No earlier
report evidence or caveats were replaced. Recorder aggregation is director-owned;
independent hook/failure-retention fixture amendments are reviewer-owned.

Existing seven allocation tests pass after the patch. A constructed targeted
check verified RuntimeError fallback status, malformed KeyError fallback status,
successful-invocation reset, and unchanged response shape. No episodes or worlds.
