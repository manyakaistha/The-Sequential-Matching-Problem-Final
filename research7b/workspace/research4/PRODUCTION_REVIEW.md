# Round-four production verification

10 October2026. Independent production reviewer; director/statistician reviewers.
Owned production.py, Dockerfile, test_wrapper.py, this review and production
artifacts/ledger. Frozen candidates, wrapper, benchmark and registry are unedited.
Allowance180CPU seconds preparation and up to300CPU seconds selected replay,
sequential verification while the main two-worker research pool runs.

## Preparation and measured checks

Separate image `sequential-round4:research` was built from eight inference source
files in a temporary context. No audit modules, result data or privileged inputs
are copied. Image ID
`sha256:be49abf3061a3a5473fc93c1d5391cc6fad76f33bda18f683b7093ca3e3f2397`
has Docker inspect size44,748,144bytes, below the documented2GiB limit.
It runs Python3.12.7-slim as UID/GID65534. Existing round3 image is preserved.
Actual restricted-container probe confirms CPU quota200000/100000, RAM1073741824,
swap0, PIDs64, read-only root-write errno30 and blocked-egress errno101.
All eight packaged source hashes equal current host source bytes.

`production_prepare.json` is explicitly prepare-only: its `valid=true` verifies
image/build/probe, and its empty episode list cannot certify selected replay.
The final selected production gate must require `prepare_only=false` and120calls
in each of the three execution modes. The existing seed101 will be used only
after selection/freeze, with unchanged configuration and full40-day follow-up.

`python3 -m research4.test_wrapper --dense --output
results/research4/production_wrapper.json` passes5 independent wrapper tests:
empty/exhausted/no-edge states, malformed-memory discard, oversized request and
malformed-state legal fallback, real SIGALRM interruption with restoration of an
outer timer, and all-eight direct/subprocess action equality. The alarm test
forces a real30ms outer deadline while the inner policy would sleep200ms; it
observes interruption and fallback rather than merely measuring completed latency.
Malformed-state fallback increments the host counter and emits retained warning;
valid subprocess cases have empty stderr.

The dense public-state stress has200endpoints,800constructed public history events
and800used dyads, leaving a dense verified feasible graph. All eight policies
return100disjoint pairs and exact host/container response parity with zero fallback.
This constructed history tests computation/protocol shape, not a claim that its
partial event log is a fully realized simulator trajectory. Complete episodes
will separately test actual public histories. Stored per-candidate latency and
request sizes are in production_wrapper.json. These finite cases do not prove
arbitrary-input deadline guarantees; no peak RSS is claimed. Public request
history remains separate from the always-empty2-byte serialized policy memory.

Preparation wall5.731494seconds; wrapper+dense wall6.578700seconds. Measured host
self CPU0.013330+2.429114seconds and child CPU0.288012+0.690558seconds are recorded
separately. Docker daemon/build/container CPU is not measured by host child
getrusage and remains explicitly unknown. Exact commands and UTC starts are in
commands_production.jsonl. Main research load may influence wall latency.

## Public-only implementation scope

Candidate source uses only current JSON members, fields, availability, used-dyad
records and received public feedback. Public generator constants specify numerical
scoring priors; no scenario labels, seeds, future disclosures, private world data,
file reads or network access are inference inputs. The simulator imported in kit
exists in the image because kit is public shared source; the decision path never
invokes world generation or hidden truth. This is consistent with the earlier
independent candidates review; it does not establish predictive calibration.

Selected full episode replay is recorded below. Final package consistency checks
remain separate. No superiority claim follows from production parity.

## Heterogeneous actor-history follow-up

The initial dense fixture's yes/no labels all count as responses: every actor
had four response successes and zero failures, despite differing acceptance
labels. It therefore did not stress response-posterior diversity. This limitation
is resolved by a separate preserved test, not by revising its old artifact.

`python3 -m research4.test_diverse --output
results/research4/production_diverse.json` creates a counterfactual200-endpoint
hard-verified dense state from already-examined seed101 demographics. Its
constructed histories vary in size0through6 with explicit response failures,
yes/no acceptance labels, mixed observed soft profiles and some missing soft
fields. Assignment days span34through36 and scoring day59 exercises the public
drift threshold. The partial constructed event log need not describe a complete
legal simulator trajectory; this tests arithmetic/resource diversity on public
input shape. Actual episode replay remains the distinct full-history check.

All eight policies pass exact host/container response parity,100legal pairs each,
zero host fallback increments, zero child fallback warnings and no invocation
errors. Request528,572bytes and serialized memory2bytes satisfy the limits.
The largest measured container call across all eight policies was greedy:
2.303615seconds, including cold startup. Acceptance_shrinkage took0.672528seconds
host and0.982833seconds container. An initial summary incorrectly called the
acceptance duration the overall maximum; raw rows were unchanged, and this review
corrects that summary. This expands the finite tested scope without proving
universal runtime, calibration or reward improvement. Raw rows retain fallback
telemetry even when an optimized test would fail; the test never suppresses such
cases or substitutes a successful run.

## Frozen selected full-episode replay

The director explicitly released this check after the independent exact-count
selection audit. Frozen `population_control` and all recorded screen/freeze source
hashes were checked before invocation and again after the replay. There were no
inference changes. The first `--skip-build` attempt failed before creating selected
JSON because the earlier round4 image was absent from Docker. Its error remains
in production_selected.log and the ledger; no cause of image disappearance is
asserted. A separately recorded production_prepare_retry.json rebuild/probe
restored the identical eight application source hashes. Rebuilt image ID
`sha256:ba7e0c2fefe7e1e845bddfb008660ae83dcbd99da593e64b6b7a8af0d3683df5`
differs from the earlier build; equal application bytes are distinguished from
Docker layer/image digest identity. Size remains44,748,144bytes. Current effective
cgroups, UID/GID, read-only root, blocked egress and packaged source hashes pass.

The successful `--skip-build` replay is retained in production_selected.json and
production_selected_retry.log. Each mode makes120calls, with60action days followed
by40days of outcome follow-up on already-examined seed101 development. All modes
produce105introductions,1qualified MSMI and198ask cost. All official episode
metrics agree, including missing feedback, first-introduction waits and served/
unserved endpoints; inference elapsed seconds intentionally differ. Ordered byte
action digest is
`a5a11d9e161cbf3f31c2d65d1bfbd87c56534d12f9030dc30c89e5d764e859e8`;
separately canonicalized semantic digest is
`ebfabdde8e1f1da79db723506821170c350b8c3ac51c599a47d28eca1acce194`.
Both digests match across direct, subprocess and restricted container. Direct
fallback increments and all per-call captured child fallback warnings are zero.

| Execution | Mean call seconds | p95 | p99 | Maximum |
|---|---:|---:|---:|---:|
| Direct |0.018007|0.044628|0.071934|0.104961|
| Subprocess |0.071052|0.118096|0.131561|0.171477|
| Container |0.341788|0.451654|0.581174|0.584440|

Quantiles use nearest-rank order statistics of120calls; child timing includes
startup. Maximum request474,057bytes, response681bytes, memory2bytes. Each
tested call is below10seconds and memory is strictly below one MiB. Finite
latency evidence is not a universal timeout guarantee and does not measure peak
RSS. The actual restricted wrapper provides2cores,1GiB RAM and64PIDs under
read-only/no-network/unprivileged execution.

Selected replay wall54.576817seconds, measured host self CPU5.402923seconds,
host child CPU9.606238seconds. Child usage includes subprocess Python and Docker
client processes, not Docker daemon/container CPU; the latter remains unknown.
Rebuild wall4.151387seconds is recorded separately. Main research load may affect
latency. Selected production passes the finite requested criteria. Independent
statistical review, fixed confirmation and final provenance/archive checks remain
required for the research package; production equivalence supplies no reward-
superiority evidence.
