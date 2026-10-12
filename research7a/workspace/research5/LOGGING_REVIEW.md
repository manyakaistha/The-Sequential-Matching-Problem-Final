# Independent full-logging amendment review

Prepared, not executed, 10 October 2026. Owner: independent statistical/adversarial reviewer; named reviewer: director. Accept the corrected logging amendment within the finite scope below. No confirmation world 90001–90430, other generated simulator world, or full episode was run by this review. All behavioral tests used mocked generation, simulator, policy and episode functions; temporary files were deleted. No sealed research-four source or result was edited.

## Preserved scientific registration

I independently checked all ten copied v1 preparation records against their original preparation manifest: every byte count and SHA matches. The original design SHA remains `1a4e1b3cee790ee87ccdb4704ed294622ccc51f130181813ffc98dd060202ee6` in the preserved snapshot. The original TEST_REVIEW is historical evidence of that preparation, not an assertion that its old anchor authenticates the amended design.

The final amended design SHA is:

`1d61bf3a8a9f2d9542b7a554ac346d5b9d82a2bc1afbf5fe6865d8a76caa2e76`

Independent preflight passes. Eighteen scientific fields match v1 exactly: policy/configuration/baseline, seed list, six families, n430, 5,160 episodes, 60+40 horizon, alpha .0125, family size four, adjusted confidence .9875, target .05, SD .26, minimum n390, inflation1.10 and fixed-n modeled power. The amendment does not reselect or refit anything. Newly bound recorder/source/schema hashes distinguish amended recording from the sealed prior recorder. The separate logging_amendment.json preserves the intermediate unlaunched draft and explains the supersession before any test world was generated. Final launch must use this amended anchor; prior manifest/source bytes remain preserved.

## What the recorder captures

For registered in-process JSON execution, each attempted call flushes the complete public request, incoming memory, sequence, command, timeout and UTC before inference. Successful responses, outgoing memory and elapsed time are flushed immediately afterward. Invocation and episode exceptions retain diagnostics and traceback. Actual successful memory byte size is measured, replacing the old recorder's assumed two-byte peak. Per-episode public prospective traces remain available.

Separate privileged gzip JSONL files save the generated initial world before simulator initialization and the final simulator attribute state, including latent world data, event schedule and endpoint state. These records never enter a policy request or model fit. A top-level set is serialized as a sorted JSON list; this is a semantic state encoding interpreted with the immutable simulator source, not a Python pickle preserving every object identity. Seed/variant metadata and hidden audit files are forbidden evaluated signals.

The registered recorder refuses subprocess mode because the inherited invoke interface does not expose complete child streams. In-process execution has no separate child stdout/stderr; the launcher console log retains process diagnostics. Independent direct/subprocess and restricted-container checks remain required after the complete test. Valid JSON request/response values are saved completely. Invalid Python values use safe repr/JSON-string diagnostics; nonfinite, cyclic or hostile-repr objects are not falsely represented as losslessly serializable JSON. Initial generation failure cannot produce a nonexistent world snapshot and is explicitly retained as an invalid row/error.

After gzip close, each audit file is bound by byte size and SHA in its episode row. The initial world, complete final state, source and public I/O make many computations reconstructible, but no separate machine-instruction or individual RNG-call trace is claimed. The recorder does not record every intermediate private attribute after every transition.

## Independent mocked tests and corrections

A two-call synthetic episode stub produced complete request/response records and separate initial/final privileged records. Mocked policy inputs contained no hidden marker, while the private initial-world file did. The new and sealed old recorders produced identical stub actions, semantic digest and outcome. This supports the tested wrapper transformation, not empirical full-episode parity.

Malformed response shape, NaN response, cyclic Python response and a value whose repr raises each retained request, invocation_error and episode_error, with an invalid row. Mocked generation failure retained episode_error and an invalid row without indexing a missing simulator or fabricating privileged state. No real policy was invoked.

A launcher mock verifies exact command arguments: research5.benchmark, both frozen policies, seeds90001:90430, two workers, all families and one correct prospective-trace path. A second mocked launch refuses the existing execution record, leaves its bytes unchanged and starts no replacement process. The inherited evaluate.invoke binding is restored after run completion/failure. Fixtures consume well below one CPU second and do not approach the 60-CPU-second review allowance.

This review identified and the director corrected three initial issues before final freeze: a malformed two-argument str call in the launcher path, error logging that could itself fail when attempting to encode an invalid response, and the initially broader timing boundary. Safe diagnostic fallbacks were independently retested. The intermediate design is preserved as unlaunched evidence; no failed empirical cell was suppressed.

## Equivalence, durability and resource limits

No additional policy-visible fields or state mutations were added. On normal execution, actions and simulator outcomes follow the same decision and transition implementations. Full recording nevertheless cannot prove universal guard-level execution equivalence: compression/I/O can change host load, scheduling and available storage. The reviewer identified an initially broader timer that included request JSON encoding; the director corrected it before the definitive freeze to start after encoding/size validation, matching the sealed recorder boundary. The two superseded unlaunched logging drafts are preserved. Added log writes themselves lie outside that inference timer. Zero observed fallback in future data alone will not prove every counterfactual guarded invocation equivalent.

Streaming compressed files limits recording buffers but does not remove original prospective-trace accumulation or guarantee RAM/storage bounds. The prior runtime and 57GB raw/3GB compressed estimates exclude added full logging. Its size/overhead is unknown until measured. A 200GB free-space launch reserve is operational protection, not a rigorous upper bound. Disk exhaustion or other recording failure makes the test incomplete; it must not cause selective exclusion or new-seed replacement.

Flush is not fsync or crash-proof durability. Abrupt death can leave an incomplete gzip member; some records may be salvageable, but incomplete evidence is not a complete test. File-open/write/compression failures can terminate the recorder before a row or final state is emitted; no claim that every catastrophic filesystem failure is itself fully recorded is supported. Explicit non-overwriting and failure-preservation rules remain essential.

Statistical success remains the fresh fixed-grid adjusted test, followed by independent full-cluster analysis, replay, production, archives and final review. Privileged logging is diagnostic only. It provides no authorization for future-information fitting, seed leakage, interim effect peeking, sample extension or alternate endpoint selection. The amended design is ready for execution; this review supplies no evidence of policy superiority.
