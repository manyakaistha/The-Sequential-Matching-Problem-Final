# Reproduce this separate research round

Use repository root, Python3.14.7, numpy2.5.3, scipy1.18.1. Full host package pins
are in results/research3/environment.json. Inference uses standard Python only;
container separately pins python3.12.7-slim and packages no audit files or data.

Restore and inspect compressed raw traces:

```sh
python3 -m research3.archive restore
python3 -m research3.archive verify
```

Archives preserve every original relative path, byte length and SHA256. Restore
refuses differing existing files. Raw traces include prospective observed fields,
actions and completed public feedback. Separate oracle files are privileged audit
evidence, never deployable training or observation inputs.

Reanalysis commands (write alternate outputs to preserve recorded artifacts):

```sh
python3 -m research3.analyze results/research3/screen.json --output /tmp/screen_analysis.json
python3 -m research3.analyze results/research3/focus.json --output /tmp/focus_analysis.json
python3 -m research3.analyze results/research3/selection.json --output /tmp/selection_analysis.json
python3 -m research3.analyze results/research3/confirmation.json --output /tmp/confirmation_analysis.json
python3 -m unittest -v research3.test_round3
python3 -m research3.tiny_models
```

The tiny-model command writes its owned artifact; run it in a staging copy if exact
recorded output identity matters. Direct/subprocess/container replay is finite
scope evidence; timing may differ on another host. All episodes are60action days
and40follow-up days. No action-day60 censoring shortcut is valid.

Exact executed commands, code hashes, seeds and planned grids are in each experiment
JSON and commands.jsonl. A fresh directory is required for rollouts: benchmark and
stage drivers refuse existing experiment outputs. Replay already examined seeds
does not create independent confirmation. The original registered confirmation
must not be expanded or retuned. Use frozen source/config hashes before replay.

Full registered stages used commands of this form:

```sh
python3 -m research3.benchmark --policies greedy,clean,goal,canonical,random_order,public_weight,population,scarce,response,throughput,offline,goal_queries,four_queries --seeds 70001:70012 --workers 2 --output results/research3/screen.json --traces results/research3/screen_traces
python3 -m research3.stages focus
python3 -m research3.stages selection
python3 -m research3.stages confirmation
```

Selection and confirmation specifics are frozen in freeze.json; stages deterministically
apply registry rules. Independent_replicator.py does not import director analysis
or runner. Production script records semantic equivalence, ordering/digests, actual
resource enforcement, request/memory/image sizes and tested latency scope.

Owned audit/test/image/probe executions are additionally recorded in
commands_forensics.json, commands_models.json and commands_critic.json. Historical
timestamps not captured are explicitly null/reconstructed. Production replay:

```sh
python3 -m research3.production --candidate SELECTED_NAME --skip-build --output /tmp/production_replay.json
```

Replace SELECTED_NAME with freeze.json's policy. Omit --skip-build to create the
five-file image in a temporary context (the root .dockerignore excludes research
files). Reusing an image requires its packaged source hashes match the freeze;
the original resource probe and image ID record that comparison.

Inherited studies remain in place. Start-of-round inherited_manifest.json records
their actual bytes, including sources differing from old freezes. Exact old frozen
policy.py and extended_policy.py recovered from checkpoint1f35149e3bd0b9067c660a970ce00085849ed504
are only in research3/recovered_frozen. New greedy uses shipped kit mechanisms;
root policy.py is preserved and is not this round's baseline implementation.

The confirmation host process was interrupted after396/480 cells. Its complete
original partial JSON is retained as confirmation_interrupted.json. The recorded
resume command `python3 -m research3.resume_confirmation` executes only84 missing
jobs of the original40cluster frozen sample, verifies freeze/registry hashes,
retains original rows and writes the final statistics. This is not sample extension.
Resume wall/childCPU are recorded separately in commands.jsonl; unrecorded CPU
from the interrupted host run is not inferred from elapsed time.
