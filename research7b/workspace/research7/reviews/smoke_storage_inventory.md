# P1 smoke storage inventory

Read-only inventory of `research7b/workspace/results/research7/research7_20261012/7b/P1_smoke`, taken 2026-10-12 (Asia/Kolkata). This is a point-in-time filesystem and metadata snapshot; the coordinator was live. The measurements below are descriptive of the captured smoke outputs only.

## Commit and resource records

At the inventory read, `commits/` contained 65 JSON records. All 65 had `is_valid: true`, `metrics.valid: true`, empty `validation_errors`, and status `simulated_not_observed_product_performance`. Their summed `fallback_count` was 0. The six policy counts were R=11, Q6=10, G=11, P=11, N=11, K=11.

| Metric over 65 commits | Aggregate or per-commit minimum / median / maximum |
|---|---:|
| CPU seconds (sum) | 386.559 s; per commit 4.838 / 5.813 / 7.535 s |
| Peak RSS | per commit 49,152,000 / 72,335,360 / 73,482,240 bytes; max 70.06 MiB |
| `evidence_bytes_before_final` | sum 768,291,104 bytes; per commit 8,392,373 / 12,512,756 / 13,403,849 bytes |

At the same point, there were 67 attempt directories with `started.json`, 65 with `finished.json`, and 65 commit files. `progress.json` still reported 27 commits / 149.417 CPU seconds and `status: running`, so that progress snapshot lagged the commit directory; the figures above are counted from the commit JSONs, not copied from progress.

## Physical storage at snapshot

A read-only walk counted 16,467 files totaling 790,952,174 logical bytes (about 754.5 MiB). This is the sum of file lengths, not filesystem allocated blocks. Main categories:

| Category | Files | Bytes |
|---|---:|---:|
| Attempt public artifacts | 16,066 | 783,331,097 |
| Attempt privileged artifacts | 132 | 5,651,812 |
| `finished.json` | 65 | 1,576,315 |
| `started.json` | 67 | 68,452 |
| Commit JSONs | 65 | 131,082 |
| Reservation JSONs | 67 | 53,980 |
| Root metadata, leases, and coordinator log/lock | 5 | 139,436 |

File suffix totals help explain the footprint: 7,982 `.request.bin` files occupied 306,329,116 bytes; 8,112 other `.bin` files occupied 482,213,302 bytes; 331 JSON files occupied 2,025,261 bytes; and 68 JSONL files occupied 2,130,569 bytes.

## Recorded payload duplication (one completed attempt)

For a representative completed attempt with 120 invocation records, each `public/NNN.request.bin` is gzip data containing a JSON envelope with `sequence`, `day`, `phase`, and `wire_request_base64`. A sampled request file was 36,014 bytes on disk; its decompressed JSON was 519,000 bytes and included a 518,928-character Base64 wire request. Decoding that Base64 gives 389,195 UTF-8 JSON bytes. Thus the standalone `.request.bin` is already gzip-compressed JSON, and the embedded payload is Base64 text inside that JSON.

The same attempt had 120 `public/segments/*.bin` gzip records. Each decompressed segment JSON includes `wire_request_base64` and `wire_request_utf8`, `wire_response_base64` and `wire_response_utf8`, plus `memory_before`, `memory_after`, `action`, `policy_status`, timing fields, and stdout/stderr. In all 120 records, Base64-decoding the request and response reproduced the corresponding UTF-8 field exactly. Across those records:

- Request Base64 fields: 58,501,612 bytes; request UTF-8 fields: 43,876,091 bytes. The decoded request is consequently represented twice in each expanded segment JSON (Base64 representation and UTF-8 representation).
- Response Base64 fields: 11,736 bytes; response UTF-8 fields: 8,717 bytes, also duplicate decoded content.
- `memory_before` values serialized as compact JSON: 242 bytes total; `memory_after`: 480 bytes total.
- The expanded request logs occupied 4,006,475 bytes across 120 gzip files. The 120 expanded segment files occupied 6,301,184 bytes on disk; their decompressed JSON lengths summed to 107,610,825 bytes.
- Other files in that attempt's public directory: `outcomes.json` 1,315 bytes and `segment_index.jsonl` 31,432 bytes. Privileged final-state/world artifacts were separate from this public-directory accounting.

For one sampled request, ordinary zlib level-6 compression of the already-gzipped 36,014-byte file's contents is not meaningful as a replacement measurement; it remained 35,981 bytes. Decompressing the request first and applying gzip to the decoded wire JSON produced 18,957 bytes, versus the 389,195-byte decoded JSON and 518,928-byte Base64 string. This is a compression-size observation only, not a recommendation or feasibility finding.

## Method and bounds

Read only commit/progress metadata and attempt artifacts; no simulator, policy, import simulator, fit, or confirmation commands were run. Compression probes were in-memory against one completed attempt, with zlib level 6. The directory was not continuously monitored, and the 65-commit counts and byte totals should be read as the snapshot at inventory time.
