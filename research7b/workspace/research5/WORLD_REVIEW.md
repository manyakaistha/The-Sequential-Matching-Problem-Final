# Independent initial-world provenance review

Completed 11 October2026. Owner: independent replicator; named reviewers: director/critic. Pass for every committed initial-world record. Prior replication/statistical files and all frozen/previous-study sources remain unchanged.

The new audit helper imports only the shipped generator for world construction. It validates each committed key belongs to the already completed original90001–90430six-family/two-policy grid before generation. It invokes no policy, evaluator episode or simulator transition, fits no model and reads no scheduled/realized outcome record. Regeneration of previously evaluated worlds is explicitly privileged offline provenance verification, not additional deployable information or a fresh test.

All5160committed privileged initial-world first records were read, with no missing, duplicate, malformed or mismatching row. The helper regenerates one world per2580seed/family cell using frozen `kit.generate(seed,200,'evaluation',variant)`, compares the first stored object directly with the generated object, and checks that the second policy's canonical initial-world digest matches the first. Separate final aggregate assertions also verify stored and generated canonical SHA256 match in every cell. Thus both greedy and population_control started from the registered identical world in all2580cells. Actor/order/parameter payload is included in the canonical digest; no outcome label was used to choose a comparison.

`results/research5/world_checks.json` retains per-cell stored/generated digests, policy coverage, full-grid status, generator-call count, failures, command, source/result hashes and timing. `world_checks.log` retains progress/final stdout/stderr. There are zero failures and no partial-check substitution. One worker used50.868995process CPU seconds and57.245222wall seconds for the measured audit body, within the120CPU-second allowance. Interpreter/import startup and small final aggregate checks are outside that body measurement.

Exact command from repository root:

```sh
.venv/bin/python -m research5.verify_worlds
```

The helper refuses an existing output. Reproduce in an isolated output location/check-out; do not overwrite the sealed result.

The verified reference confirmation SHA256 is `c45624e0ad7f77c763b5bca62d7296f2199eb37ad4dc4a56bf3fc4b37df8b334`; generator SHA is `0d2cb3d3b46ca2a6ee7c8b74b78c55642ef98686e59a890ec18f66f2cabc1f3e`; audit helper SHA is `f09f4d8ca009e269e240276e697969382a2faeb2c0c735e6dab0f4cd12ecae0c`. Source/result hashes are captured in the JSON.

This audit intentionally reads only the first gzip JSONL record. It does not certify full gzip closure/CRC, final-state correctness or all-attempt durability; the exhaustive artifact audit owns those checks. It covers committed records, while interrupted/orphan attempts remain separately preserved and reviewed. It verifies generator identity and common initial conditions, not ideal PRNG independence, universal reproducibility on every platform, legal-action execution or policy superiority. The full statistical conclusion remains unchanged.
