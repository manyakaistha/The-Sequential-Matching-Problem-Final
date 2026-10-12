# Independent telemetry amendment and smoke gate

Reviewer `/root/implementation_review`, Sol medium; named reviewers `/root` and independent scientific critic. 11 October 2026. Follow-up allowance 60 CPU seconds; less than two CPU seconds plus seven seconds waiting for the actual timer. Developer files remained read-only. No world generation, real episodes, fitting, or reward sample. This is a separate amendment; `implementation_review.md` retains the initial failure evidence unchanged.

**Verdict: the fallback-accounting blocker is closed. The reviewed allocation and in-process recorder/orchestrator pass the bounded constructed-case smoke gate. This does not approve production or scientific admission.**

The wrapper resets `LAST_STATUS` on every decision and marks fallback/reason before entering fallback reconstruction. The recorder additionally clears the hook before each call, copies/counts it in a `finally` immediately after the call, and saves the copied status with both returned-response and inference-error records before serialization/validation. Stderr remains preserved raw evidence and no longer determines fallback counts. This host-only hook does not change the exact public response schema or enter a later policy request.

Amended the independent failing fixture to set this authoritative hook rather than emit text. Three constructed failure paths now retain count one and the exact Deadline reason: invalid response shape, nonfinite response serialization, and a raised exception after setting fallback status. A text-only stderr diagnostic mentioning fallback on all 120 fake calls records zero fallbacks. Independent wrapper reset and recorder reset tests ensure one earlier fallback does not contaminate subsequent calls; the latter records exactly one over 120 calls. The original `0 != 1` finding remains in the initial review report, rather than being rewritten as a historical pass.

Command:

```
.venv/bin/python -m unittest research6.tests.test_allocation research6.tests.test_recorder research6.tests.test_independent_contract -v
```

Result: **20 tests passed in 7.821 seconds**. This reran actual seven-second SIGALRM interruption, G/P exact identity, five-node exhaustive K/N1 checks, N2 tie/order semantics, error byte retention, setup error commit, expected source/config verification and no-overwrite behavior. Fake simulator/generation stubs were used exclusively for recorder tests.

Reviewed SHA-256 values:

| File | SHA-256 |
|---|---|
| `research6/policies/policy.py` | `cd1448bbb192f470b4296251074f5393becdeed4e709ff5b6eb5e70bec73fbbe` |
| `research6/policies/allocation.py` | `c3b26572883fcd79e4fe0d728f9cfdc3556551c2f45b249edfe8be7293782458` |
| `research6/recorder.py` | `b1feddc2698ebdc80cfccdf5aa804b58c15c5814720affc2b655e835942d6a1a` |
| `research6/orchestrator.py` | `f80018abe9fe73bf3f77ebe3e90cb6c9483ee58cacfb48558362fa7be6092b50` |
| `research6/tests/test_independent_contract.py` | `5b7a13bc2b1408e5edb8285fdfcfbdca5f562efff40c5dda8e6d670906fc4411` |

The initial review's scope limitations remain open production gates: outer hard process timeout, restricted-container effective resource limits/image/source package, failed-invocation resource summary scope, detailed mechanism logging, directory durability/crash fault injection, exact valid-commit member/causal audit and direct/subprocess/container ordered/semantic/literal-byte replay. The hook is appropriate for single-call-per-worker in-process execution; it is process-local mutable host instrumentation, not a cross-process telemetry protocol or a thread-safe interface. No concurrent-thread inference is approved. Subprocess logging will need a host side channel that preserves exactly the same telemetry without contaminating protocol stdout.

A registered small smoke on explicitly permitted examined seeds may proceed subject to director/critic authorization and the existing scope/resource/seed registration gates. A smoke pass cannot clear the full A3 production gate, promote a candidate, establish reward superiority or authorize new research samples.
