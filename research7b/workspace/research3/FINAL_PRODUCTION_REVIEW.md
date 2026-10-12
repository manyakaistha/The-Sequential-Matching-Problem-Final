# Selected policy production review

10 October 2026. Independent production reviewer; reviewer: director and critic.
Question: does the frozen selected `clean` policy preserve legal behavior across
direct, subprocess and restricted-container execution? Falsifiable hypothesis:
all 120 invocation actions and terminal metrics agree with zero fallback.
Only owned production outputs and reviews were changed; frozen inference sources
were read and hashed. Compute allowance was one sequential replay process, no
fresh research seeds. This is finite evidence, not a universal runtime proof.

## Observed replay

`results/research3/production_selected.json` records the complete already-examined
seed101 development episode: 60 action days and 40 follow-up days. Each execution
contains 120 calls. All modes produced109 introductions,1 qualified MSMI and198
ask cost. Ordered action digest is
`4898ee5eeffd134c73b7ea85a6b329698fc25e4747a473cc61b7d4136951db94`.
Ordered byte/action digest and separately canonicalized semantic action digest
match, as do every recorded funnel/coverage/ask-cost field. All direct fallback
counters and all captured child stderr fallback warnings are zero.

| Execution | Mean call seconds | p95 | p99 | Maximum |
|---|---:|---:|---:|---:|
| Direct |0.016779|0.036372|0.038251|0.056357|
| Subprocess |0.077385|0.150496|0.207691|0.323894|
| Container |0.345991|0.477848|0.587357|0.739009|

Quantiles use nearest-rank order statistics of120 calls. Maximum serialized request
475,720bytes, response845bytes, memory2bytes. Startup is included in child call
timing. Total replay wall55.497762seconds; CPU/daemon CPU was not instrumented.
Concurrent registered benchmark load may affect latency. No peak-RSS claim is
made. Every tested call is below the ten-second limit and memory is strictly below
one MiB. This does not establish a timeout guarantee on arbitrary requests.

## Enforced execution and source identity

Image ID is
`sha256:e8e1e0260628e4140ad95506ef643588b0abf6a5af2422f2332c55534072842a`;
Docker inspect size44,742,809bytes is below documented2GiB. It packages only five
inference source files and uses Python3.12.7-slim, UID/GID65534. The unchanged
resource command sets2CPU cores,1GiB RAM, no swap allowance beyond memory,
64PIDs, read-only root, no network, dropped capabilities, no-new-privileges and
64MiB temporary storage.

A fresh replay of the stored restricted resource-probe command verified effective
`cpu.max=200000 100000`, `memory.max=1073741824`, `memory.swap.max=0`,
`pids.max=64`, UID/GID65534, root-write errno30 and blocked-egress errno101.
Application source hashes equal the historical probe and frozen sources. An
initial raw-probe equality assertion failed because the unordered filesystem
network-interface listing changed order. The second diagnostic identified this
as the only differing key; the set of interfaces is identical. This ordering
difference has no implication for policy semantic equivalence.

The initial selected replay attempt failed before creating its JSON because the
Docker daemon was stopped. Its error log is preserved as `production_selected.log`.
Docker was started reversibly and the successful run is retained separately in
`production_selected_retry.log`. Source/configuration/freeze hashes remain exact.

## Correctness scope and package gates

Earlier independent12-test suite covers empty pools, no feasible edges, permanent
declines, exhausted budget, malformed memory, oversized requests, pending
feedback, solver independence, actual alarm interruption and outer deadline
restoration. Earlier dense200-endpoint/800-history all13-candidate container
parity remains relevant to the same frozen image. Those artifacts and limitations
are preserved in IMPLEMENTATION_REVIEW.md. Empty legal fallback remains available;
tested valid selected replay never required it.

The selected policy passes the tested production criteria. This review makes no
claim of superiority to greedy. Final package certification still requires the
director's full-grid confirmation statistics, independent confirmation replication,
final research review, lossless archive verification and inherited-file/provenance
gate. A production pass alone does not complete those scientific checks.
