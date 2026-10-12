# Independent progress and interrupted-run recovery review

Reviewed 10 October 2026. Owner: statistical/adversarial reviewer; named reviewer: director. Accept recovery of the original fixed sample under the documented protocol. This is continuation of an interrupted test, not a new untouched confirmation. I performed code/hash checks and synthetic mocked tests only: no simulator world, policy inference or full episode was generated, and no real partial outcomes were inspected or analyzed. No sealed prior-study file was edited.

## Definitive registration and preservation

The reviewed recovery design SHA256 is:

`74e2e9c1b48d82ca3ac7f978805bd180caee26b65bf93c645b1ab663fa1db79e`

The official launch anchor and independent preflight agree. The registered comparison remains exactly population_control versus shipped greedy, seeds90001–90430, six families,430clusters/5,160episodes, alpha.0125 and the original fixed sample/power assumptions. No old result is pooled into a newly enlarged sample. The interrupted current preparation/results/source snapshot are preserved under the archived run recorded by the design, rather than destroyed to conceal failed or unfavorable data.

I independently ran the complete recovery preflight: it binds the archived prior design, source-result file and archive manifest hashes, and checks every archived evidence byte count/hash. It passes. This cryptographic check reads evidence bytes without using their outcomes for a decision. A mocked source-result digest alteration is refused. The archive contains372 manifest-bound records according to the reviewed recovery evidence. Root reports108 persisted rows; this reviewer does not infer any reward result from that count.

The new benchmark `run` function's AST is identical to the archived source snapshot's `run` function. Changes are controller recovery/progress and launcher streaming/interrupt handling. Frozen inference, simulator/evaluator, configuration and invocation logging semantics are preserved. The old recorder version is retained in original metadata and assigned to every recovered row; new rows identify the new controller version. A new top-level recorder hash does not falsely overwrite historical execution attribution.

## Recovery eligibility and scope

The controller validates original planned policy/seed/family grid, code hashes, horizon and logging schema; rejects duplicate or out-of-grid row keys and configuration drift; checks relocated audit-file sizes/hashes; and preserves every persisted row. It does not filter on valid status, failure count, fallback count, score or success. It schedules only original keys absent from the saved row set. Archived traces/logs remain readable at rewritten paths. Orphan/uncommitted partial artifacts remain in the archive and cannot select a replacement outcome for a committed cell.

The final analyzer still requires exact complete grid and all original validity/failure/fallback gates. A saved invalid/failing cell therefore blocks a superiority claim, even though recovery can finish computing the remaining sample. No failed committed cell is retried, no fresh seed is substituted, no policy is retuned and no sample is extended. A further interruption requires another reviewed recovery and preserved evidence rather than automatic exclusion.

Uncommitted cells may be recomputed only at their original keys under this protocol. System interruption can leave evidence not represented by a committed episode row; all such traces, exceptions and failure attempts must remain disclosed in the final package and reviewed before any claim. Completion-count status alone cannot establish scientific eligibility or that every earlier attempted invocation succeeded.

## Independent mocked tests

A fabricated twelve-cell miniature grid with one persisted invalid/failure/fallback row demonstrated that the row is retained unchanged, its original recorder is attributed, and exactly eleven missing original keys are submitted. Unknown keys, duplicate rows and configuration changes each fail. All fixtures were synthetic temporary files, not real episode outcomes; no process pool actually executed a simulator job.

A mocked launcher checks immediate check/start/log-path messages, exact original seed/policy/family command with resume-from, progress teeing to terminal and console log, and a virtual15-second idle heartbeat. No score, MSMI or effect is printed by those progress paths. No real subprocess was started. Existing-output refusal remains in force.

A separate Ctrl-C mock checks process-group SIGTERM dispatch, retained console/execution records with interrupted status, exception propagation and no analysis call. No actual process or signal was used. The successful full archived-evidence preflight consumed about.91 process CPU seconds; synthetic checks were each below.1 CPU second, well within the60CPU-second allowance.

## Progress and operational limitations

Startup is visible before potentially expensive checks. Completed-cell bars show count, percentage, elapsed time and estimated time remaining; idle heartbeats explain that workers are active. They do not expose interim outcomes or change the fixed stopping rule. ETA is an extrapolation of completed work, not a runtime guarantee. The final full-grid analysis may show the registered result only after completion.

Streaming and process-group interrupt control improve observability and cleanup but do not guarantee crash-proof durability, instantaneous worker shutdown in every OS failure, or exactly15-second notices under arbitrary blocked I/O/host load. A signal can leave incomplete gzip members and uncommitted jobs; the existing evidence-preservation and recovery rules remain necessary. Source-identical policy invocation does not prove universal timing/fallback equivalence under every changed host load.

The prepared recovery can be launched through the anchored entrypoint. No confirmation outcome or superiority claim is supplied by this review. Final claims still require complete eligible fixed-grid analysis, independent replay/statistics, production/source checks, archives and written final review.
