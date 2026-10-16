# Independent evidence-runtime review

14 October 2026. Reviewer: `/root/logging_critic`, independent of the runner,
metrics/audit and director implementations. Scope: v2 source, public capture
contract, resource/protocol boundaries and constructed endpoint fixtures. No
research simulations, fitting, policy selection or reward study were run by this
reviewer. Old trial sources/results were read only. Initial allowance was
150 CPU seconds/15 minutes, extended by the director by 90 CPU seconds/10 minutes;
checks consumed only a small fraction of the CPU allowance.

The reviewed changes close concrete first-draft failures: duplicate or conflicting
respondent/date records, pre-assignment and pre-acceptance dates, occurrence after
release, contradictory missingness, duplicate late-arrival inventory, registration
file-versus-content digest mismatch, incomplete hash coverage, optional capture
streams, missing policy-memory continuity, incomplete public member inventories,
source-manifest dependency omissions, dropped reference-policy fallback telemetry
and worker termination that left a policy's separate process session running.
Owners patched their own implementation files;
the critic owns only this report and `tests/test_adversarial.py`.

The qualification boundary is one dyad counted once per qualifying introduction:
two distinct first acceptances, a happened date with nonnegative delay at most 30,
and two distinct second positive intentions with nonnegative delay at most 3.
Required events must have been released by day 99. The denominator is unique
members arrived by day 59; an event first released on day 100 cannot qualify.
Independent audit reconstructs these counts from public records without importing
production metrics or private worlds. It binds commits to the registration's
canonical self digest and source manifest, checks the complete registered grid,
requires every capture stream and verifies requests, actions, answers, released
feedback, inventory and lifecycle closure.

Verification performed:

- `python3 -m unittest research8.soft_query_followup.v2.tests.test_adversarial -v`:
  all 14 independent endpoint counterexamples passed after repairs.
- `python3 -m pytest research8/soft_query_followup/v2/tests -q`: 46 tests and
  2 subtests passed in 0.80 seconds at the reviewed checkpoint. These use public
  fixtures and fake simulator data; this reviewer launched no actual cells.
- A bounded independent process fixture gave a worker a sleeping child in a
  separate session, then called `launcher.kill_worker`; both processes stopped.
  Cleanup was repeated in a `finally` block to prevent leftover processes.

Resource claims have practical limits. The launcher uses a repository-wide
inherited flock lease and at most three participating simulator workers; it cannot
control unrelated launchers or remote machines. Wall/RSS guards poll processes,
so enforcement has polling and scheduling granularity. Unix CPU limits have
integer-second granularity and cumulative attempt CPU is also checked by the
runner. macOS address-space limits are explicitly unsupported; RSS monitoring
is used instead. Cold policy calls have bounded pipes, a minimal environment,
process-group cleanup and fail-closed latency/protocol/fallback handling. This is
trusted-source process isolation, **not a filesystem or network sandbox**. Policies
could still read paths accessible to the OS account, and ordinary Python import
caches remain part of the trusted workspace assumption. Freeze sources and stop
other simulators before any authorized campaign.

Final integration receipt: the director reported 70 tests plus 2 subtests passed
in 14.96 seconds, including the 23 unchanged-policy tests. I read
`validation/capture_summary.json`: one constructed four-actor world was executed
through the actual simulator and 120 cold policy calls, with maximum measured
cold duration 0.181973 seconds. Its public-capture audit passed and read no private
world. It produced two introductions, two mutual acceptances, one happened date,
one unqualified pause and zero qualified introductions. Positive qualification
is tested by the constructed endpoint fixtures. The capture test is not a
generated 200-member campaign cell, a 72-cell smoke, a 2,880-cell replication,
or evidence of performance at their scale. The receipt is director-produced.
After the director preserved the raw files under `validation/declared_capture/`,
I independently ran the following read-only command; it verified one expected
cell, all mandatory artifact hashes/capture streams and the public-derived
metrics, with `private_world_read=false`:

```sh
python3 -m research8.soft_query_followup.v2.audit --registration research8/soft_query_followup/v2/validation/declared_fixture_registration.json --output research8/soft_query_followup/v2/validation/declared_capture
```

This fixture registration is explicitly a minimal constructed test registration,
not an authorized v2 campaign freeze. No additional simulator calls were launched
by that audit. Source inspection also confirmed that actual v2 campaign
audits run registration preflight, and nonzero zero-variance contrasts do not
report a spurious point confidence interval.

Final small-change review: the launcher now creates exclusive timestamped
worker stdout/stderr paths for each uncommitted infrastructure attempt. Prior
logs remain intact when a coordinator restarts; a failed committed cell remains
non-retryable under that registration. I inspected the patch and independently
ran the guard and analysis tests together: 13 passed in 0.41 seconds. The two new
pure paired-data checks verify seed-cluster degrees of freedom/standard error and
the missing confidence interval for a constant nonzero difference. They invoke
no policy or simulator. The combined test inventory is now 72 tests plus 2
subtests; the earlier full combined execution was 70 tests, followed by this
independent check of the changed scope.

The director's future prompt expands instrumentation smoke to 120 cells
(4 seeds × 6 families × 5 arms), so Q6 and P adapters are exercised alongside
the three soft-query arms before the proposed 2,880-cell replication. This
supersedes the previously proposed 72-cell three-arm smoke; neither smoke grid
has been launched by this repair task.

This checkpoint is implementation evidence, not certification of a completed
replication. Frozen campaign preflight and the full registered smoke remain
future work. The old trial's missing evidence is not repaired
retroactively, no old commit is independently certified by these fixtures, and
no new causal or reward claim follows from passing them.
