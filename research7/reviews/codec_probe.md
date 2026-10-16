# Offline compact-log prototype: engineering evidence

This is a provisional method, not an integrated runtime or storage admission certificate. The frozen runtime sources, original evidence and all official worlds/episodes/fits were unchanged. The only runtime executed was this standalone standard-library codec reading existing files. Root and `r7_methodology_critic` own admission review.

## Predeclared sample and measurements

Before opening any request payload, the probe wrote `execution_guide/codec_evidence/sample_manifest.json`: policy G, the first two ascending seeds (700000, 700001), every one of the six families. No outcomes, policy comparisons or compression results informed selection. All 12 selected cells were already completed. Inputs were the existing `research7b/workspace/results/research7/research7_20261012/7b/P1_smoke` artifacts. There are 120 invocations per cell, 1,440 total. The sample is a bounded engineering probe, not a random representative estimate for future policies or stages.

| Measured component | Bytes |
|---|---:|
| Existing request gzip files | 58,131,529 |
| Existing segment gzip files | 90,265,315 |
| Existing request + segment total | 148,396,844 |
| Decoded request wire bytes | 573,936,977 |
| Full standalone zlib request frames, same frame header | 32,308,330 |
| Proposed COPY/literal request frames | 8,733,658 |
| Proposed completion metadata + exact response frames | 775,350 |
| Proposed request + completion total | 9,509,008 |

The observed reduction for these two artifact categories is 93.592%; the request codec is 72.968% smaller than standalone full request frames. These are logical byte counts, not allocated filesystem blocks. Other public artifacts, indexes, privileged world/final-state artifacts, starts/finishes, commits and reservations are excluded from both comparator totals and remain necessary. The prototype output directory totals approximately 9.52 MB including JSON evidence. There is no extrapolation establishing storage for other stages, policy memory or failure rates.

The final full probe used 13.508454 CPU seconds (13.99 wall seconds); its encode/decode portion was 5.445579 CPU seconds. A separate expanded corruption test used 0.010697 CPU seconds. Two earlier bounded development executions each ran approximately 12 seconds; one reached a synthetic test-fixture error after all real-wire roundtrips passed, and one preceded the disk reread addition. Total task compute stayed well below the 180 CPU-second allowance; the first execution was not separately instrumented, so the exact aggregate CPU is unavailable. No fitting or policy execution occurred.

## Schema and exactness

Each opaque request record has a 117-byte header: magic/version, mode, decoded length, stored payload length, predecessor digest, decoded SHA-256, stored-payload SHA-256. Modes are literal raw bytes, full zlib bytes, or zlib-compressed COPY/literal operations. COPY refers to byte ranges of the immediately preceding request. Exact raw chunks are found by splitting at the opaque byte delimiter `},`; the implementation does not parse, normalize, reorder or assume UTF-8. Dictionary keys are actual bytes, so a hash collision cannot create an incorrect copy. Equal data retains exact original bytes.

Every twelfth request is a full checkpoint; 120 checkpoints and 1,320 delta frames were produced. Each checkpoint was verified with no predecessor. Replaying a chain needs at most eleven preceding request transitions, beginning with its checkpoint. Frame position/index discovery is still a production responsibility. All 1,440 exact request and response wire bytes passed immediate roundtrip assertions; all 1,440 on-disk request/completion pairs were decoded again with request-digest consistency checked.

Completion records retain all non-wire segment fields, including sequence/day/phase, action, before/after memory, status, stdout/stderr, timing and timestamp, plus request-envelope metadata, request SHA-256 and response Base64. Request and response display strings are deterministically regenerated with UTF-8 replacement decoding; this equivalence was asserted for every input. This preserves original wire bytes and metadata values, **not** original gzip bytes, JSON spacing/order or raw metadata serialization. Original segment text must remain archived if that stronger requirement is adopted. Arbitrary non-UTF8, empty bytes, malformed prefixes and ordering-sensitive request bytes are supported by the opaque codec; current completed cells do not empirically exercise production failures or large persistent policy memory.

## Growth, CPU and memory bounds

The encoder always considers raw/full-compressed fallback before a delta. Therefore any record's stored frame is at most `raw_length + 117` bytes; no assumed compressibility is required. Records exceeding 16 MiB are rejected explicitly, never silently truncated. A production design must choose a declared larger cap or bounded chunked raw fallback if arbitrary-size policy memory is required. The current cap is an admission limitation, not proof that memory cannot exceed it.

Chunk discovery and indexing are linear in record size with average dictionary lookup complexity; no quadratic sequence alignment is used. Each request and predecessor has at most 32,768 indexed chunks; exceeding that limit abandons delta construction for full/raw fallback. Decoder decompression is capped, operation sizes and COPY bounds are checked before copying, and only the current record, predecessor and bounded payload/operations are required. Overall memory is linear in capped record size plus capped chunk count. We did not claim a measured RSS ceiling or a hard adversarial dictionary-CPU bound. SHA-256 detects accidental corruption but is not an authenticity mechanism against an attacker who can rewrite digests.

## Failures and durability contract

Detected synthetic failures: truncated payload, payload bit flip, missing predecessor, wrong predecessor, corrupt magic, out-of-bounds copy, decoded output overrun, unknown operation, truncated operation and decompression expansion above its cap. The archive scanner rejects incomplete headers/payload tails and yields only the complete prefix. Checkpoint recovery and raw malformed/non-UTF8 byte roundtrips passed. Tests do not establish crash consistency for a real filesystem or policy timeout behavior.

Before inference, a production recorder must persist a uniquely identified request frame (attempt/sequence/day/phase and predecessor/checkpoint reference) and only call inference after append, flush and successful `fsync`. Request identity must be durable before the call; the prototype's compact completion metadata supplies identity after the fact and is therefore insufficient as a production pre-call schema by itself. The included `persist_before_call` demonstrates the flush/fsync ordering only and is not connected to inference. New-file/directory durability, exclusive writer ownership, torn-tail recovery, indexes, restart idempotency and filesystem behavior must be implemented and crash-tested before admission.

Completion must then append independently with exact response bytes or the raw partial/malformed response prefix, invocation status/exception/timeout and resource facts, with memory/action semantics conditional on successful parsing. A durable request with absent completion means incomplete/unknown execution, never an invented successful result. A torn request tail means uncommitted request; a torn completion retains the complete request and marks completion unknown. Storage exhaustion/fsync failure must prevent calling inference if request persistence failed. Logging overhead must be included in runtime budgets and must not change policy-facing bytes, memory or scheduling.

The next admission gate is implementation in an isolated future schema, independent review and crash/failure tests without changing the frozen completed run. The reduction above supports prototyping; it does not authorize another batch or prove that all evidence requirements are satisfied.
