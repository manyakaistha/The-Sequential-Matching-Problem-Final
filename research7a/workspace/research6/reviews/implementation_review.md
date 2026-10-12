# Independent bounded implementation review

Reviewer `/root/implementation_review`, routed Sol medium; named director reviewer `/root`, scientific critic Sol high. 11 October 2026. Exclusive ownership: this report and `research6/tests/test_independent_contract.py`. Developer implementation files read-only. CPU allowance 120 seconds; checks consumed approximately two CPU seconds plus seven seconds waiting for the real clock interruption. No simulator world generation, real episodes, fitting, or new research sample was executed. Constructed fake-simulator calls create temporary evidence that is removed by their fixture.

**Verdict: allocation implementation passes this bounded review. Runner smoke approval is blocked pending authoritative fallback telemetry, including failed invocations. Full production approval is not granted.**

## Evidence

Read AGENTS, INTERFACE, TEST_SPEC, PLAN allocation/resource sections, ORCHESTRATION, allocation/policy, recorder/orchestrator, inherited functions and developer tests/report. Ran:

```
.venv/bin/python -m unittest research6.tests.test_allocation research6.tests.test_recorder research6.tests.test_independent_contract -v
```

The initial combined run exercised seventeen cases in 8.798 seconds. All allocation cases passed, including an actual seven-second SIGALRM firing while patched candidate code slept inside a broad `except Exception`. Deadline is a BaseException and escaped that handler; shipped legal matching was returned, stderr identified Deadline, and the timer was restored. This checks a real clock, rather than injecting the Deadline exception. It does not establish an outer hard process deadline or protect against handlers that deliberately catch BaseException.

Independent checks corroborate:

- Exact G/P action identity across 64 constructed combinations of phase, ask budget, missing fields and declined statuses; permanent prior dyad exclusion retained. G invokes shipped baseline functions; P invokes the inherited population-control configuration unchanged.
- For all 1,024 five-vertex simple graphs with heterogeneous integer weights, K agrees with independent exhaustive `(cardinality,total shipped score)` maximization. N1's result stays legal and lexicographically no worse than its greedy initialization. N1 is bounded local repair, not an exact maximum matching algorithm. Enumeration order can miss a higher-scoring cardinality increase; no global score optimality is claimed.
- N2 obeys primary integer-score precedence at every selected edge; its tied decisions are independent of member-list order and stable within each eight-day block. Exact ties are the documented width-zero near-tie class. Its frozen salt has no empirical superiority evidence.
- Successful fake-simulator recording creates 120 independent request chunks and reaches day 100; attempted duplicate commits preserve a second closed attempt and fail rather than overwrite.
- Invalid response, nonfinite return, and raised inference exceptions preserve captured stdout/stderr and the return or repr before error commit. These are correctly labeled in-process serialized output; they are not actual subprocess stdout bytes.
- Failed episodes remain authoritative commits with source attribution. Source and expected-config mismatch are rejected on verification; setup generation failure is now a retained invalid zero-invocation commit with null final state. The generation function was mocked to raise, so no world was generated.

During review the director added policy-label/config-ID equality to registration, expected-config validation on resume, actual worker startup source verification, and moved setup inside retained failure handling. Focused independent tests passed for config mismatch, nonfinite stream/failure retention, source/config mismatch and setup failure.

## Blocking issue: fallback telemetry

Recorder currently increments `fallback_count` by searching captured stderr for `fallback`, and does so only after response/resource validation. The independent fixture emits the wrapper's fallback diagnostic and returns an invalid response. The resulting committed invalid row records `fallback_count=0`, although the diagnostic survives in its response artifact. Focused test output:

```
test_invalid_invocation_retains_fallback_count ... FAIL
AssertionError: 0 != 1 : failed invocations must retain fallback telemetry
```

Use an explicit per-invocation wrapper/host telemetry channel with fallback boolean and reason; persist and aggregate it even when output serialization, shape, memory, elapsed, or simulator legality rejects the invocation. A stderr substring is not authoritative and permits both false positives and missing reports. Once that hook exists, the fixture must inject the hook rather than assume a plain stderr line establishes fallback. Keep plain diagnostic text as raw evidence separately.

## Scope limitations and remaining gates

The internal seven-second candidate timer works in the examined main-thread case. The host recorder is in-process and checks ten-second elapsed time only after return. There is no outer kill timer here; a hung fallback/candidate that catches BaseException can block a worker. The developer expressly identifies this gap. Smoke use needs an explicit bounded scope and must not be called restricted production. Actual restricted containers, effective resource/image probes, process timeout, restart, source-package pinning, direct/subprocess/container byte/ordered/semantic replay and a full valid-commit file-set/causal audit remain required by TEST_SPEC.

Failed-invocation latency/request/memory peaks are raw-event evidence but are absent from successful-call summary arrays/maxima. Resource summaries must either aggregate all attempted invocations or clearly name their successful-only scope before stage/production interpretation. Peak RSS is correctly labeled process lifetime; a reused process's high-water mark is not an isolated invocation peak.

N1 implements a single global deterministic traversal budget rather than explicit connected-component traversal from PLAN. This is a documented implementation deviation to settle in registration; it does not compromise legality but may spend the budget on early components. No module logs detailed repair/alternatives/trigger diagnostics yet. These mechanism artifacts are needed before scientific admission, not evidence of a reward failure.

Atomic hard-link commit refuses overwrite and closed chunks are fsynced, but directory fsync and fault-injected crash recovery have not been independently validated. Resume verification checks registered file hashes/config/sources; hashes alone do not validate causal request/action reconstruction or the exact 120-phase member set. No source hash is a historical timestamp or production isolation proof.

This review supports implementation behavior on constructed cases. It establishes neither simulator advantage, calibrated predictions, universal latency guarantees nor production readiness.
