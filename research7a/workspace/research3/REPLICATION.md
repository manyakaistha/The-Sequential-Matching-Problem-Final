# Independent replication record

9 October 2026. Owner: independent replicator/adversarial critic; reviewer: director.
Allowance: one worker, ten CPU minutes, only already-exposed or director-selected
registered seeds. This implementation imports neither director benchmark.py nor
analyze.py nor evaluator.py. It imports public Simulator/generate and the actual
observation-only policy, then independently runs its own JSON request loop,
response checks, 60 action days, 40 observation days, public-event reward scorer,
action digests and seed-cluster t statistics.

## Initial old-seed reproduction

Exact commands:

```
.venv/bin/python -m research3.independent_replicator --policies greedy,clean --seeds 101 --variants development --reference results/research3/smoke.json
.venv/bin/python -m research3.independent_replicator --policies greedy,clean --seeds 101 --variants development --mode subprocess --reference results/research3/smoke.json
```

All four episodes match the director's recorded smoke on every shared outcome
metric, ordered actions, semantic actions, byte action SHA256 and semantic SHA256.
All have zero fallback, including subprocess stderr inspection. Greedy introduces
108 dyads, clean109; each scores one qualified dyad (.5 MSMI/100) and four positive
pauses. This is implementation evidence on one already-used world, not a reward
improvement comparison. No fresh unregistered seeds were generated.

Direct wall times2.44s/2.42s; subprocess7.42s/7.49s, maximum call .095s. Parent
process CPU across direct episodes4.82s and subprocess episodes1.78s; subprocess
child CPU is not measured by time.process_time and must not be counted as zero.
These finite times do not establish a universal production limit. Raw results,
source hashes, commands and precise digests are retained in
results/research3/replication.json. Repeat invocations append runs rather than
replace prior evidence.

## Independent analysis scope

The cluster reconstruction validates exactly six families per seed per policy,
complete paired seed support, valid rows and zero reported fallback. It averages
family episode ratios within seed, then computes paired sample mean/SD and
Student-t CI/test. It can reproduce selected director experiment statistics
without importing their analysis code. This is independent implementation, not
independent data; replayed worlds remain their original partition.

Registered-seed serious-candidate replay awaits a director-selected candidate
and list. Confirmation replicates can inspect only the frozen policy and must
not change fitting, selection or sample size. Exact ordering and semantic
agreement are checked separately; a mismatch is recorded rather than treated
as success because scores happen to agree.

## Serious candidate C reproduction

Executed after the director selected offline for replication and its reference
rows existed (C itself still underway):

```
.venv/bin/python -m research3.independent_replicator --policies offline --seeds 71001,71002 --variants all --reference results/research3/focus.json
```

All12episodes match shared full100-day metrics, ordered actions, semantic actions,
byte and semantic digests exactly; zero fallback. No new independent sample or
unregistered seed was added. The separately written loop/scorer confirms the
serious candidate's implementation on two registered C clusters. Direct replay
CPU29.75seconds, episode wall sum29.92seconds, maximum invocation .0565seconds.
Result rows and exact measured times are retained in replication.json. This is
finite replication evidence, not a statistical superiority or universal timeout
claim. No C aggregate reward ranking was used before its completion.

Also independently reconstructed all thirteen completed B seed-balanced means,
paired effects and t intervals using cluster_audit; every value matches the
director's analysis to1e-12. Independent code uses the same recorded data and
therefore supplies analysis verification, not a separate experiment.

## Frozen selected confirmation reproduction

On10October2026, independently replayed greedy and selected clean on registered
seeds73001/73002, all six families, in both direct and fresh-subprocess modes:
48 episodes total. Every full100-day public-scored metric, ordered action,
semantic action and both action digests matches confirmation exactly. All48
are valid with zero fallback, including captured subprocess stderr. These are
replays of existing E worlds, not new statistical observations.

Exact commands (both output to `replication_confirmation.json`):

```
.venv/bin/python -m research3.independent_replicator --policies greedy,clean --seeds 73001,73002 --variants all --reference results/research3/confirmation.json --output results/research3/replication_confirmation.json
.venv/bin/python -m research3.independent_replicator --policies greedy,clean --seeds 73001,73002 --variants all --mode subprocess --reference results/research3/confirmation.json --output results/research3/replication_confirmation.json
.venv/bin/python -m research3.final_statistics_review
```

The separate full-grid audit checks every registered B/C/D/E cell and recomputes
all means/paired intervals/tests independently; agreement is1e−12. It separately
checks E freeze/registry, reproduces the registered bootstrap and reports
influential-seed sensitivity. Its full40-cluster `cluster_audit` result is also
embedded in the last replay run's `independent_statistics` without rerunning
simulator episodes merely to attach statistics.

Direct episode wall sum70.79s, process CPU68.18s, maximum call .1474s. Subprocess
episode wall sum196.94s, replicator-parent CPU21.65s, maximum call .3443s. Crucially,
OS child usage of the outer execution includes all policy subprocess startup:
68.75s direct and192.34s subprocess (261.09s total). The180CPU-second estimate/
allowance was exceeded; this discrepancy was reported to the director and no
further simulation is planned by this reviewer. Parent-only21.65s must not be
represented as total subprocess compute. Exact UTC, wall and OS CPU records are
in commands_critic.json. Finite tested timings are not a universal timeout claim.
