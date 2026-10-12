# Research organization and review ownership

Four total concurrent slots are available, including the director. There are no
nested agents in this round. Simulation grids use two worker processes; offline
analysis and replay use bounded single-worker processes. Agent count and process
count are separate limits. Three researchers rotate roles as tasks finish.

| Role | Responsible agent | Concrete question and falsifiable hypothesis | Owned deliverables and reviewer |
|---|---|---|---|
| Research director | root | Do public signals produce a registered reward gain over shipped greedy? A complete fresh confirmation can reject the claim. | PLAN, registry, runner, wrapper, stage/analysis integration, decisions, report, archives and package gate. Reviewed by statistics_review and production_review. |
| Simulator forensic analyst | root, with inherited independent forensic work | Do same-batch hard/soft queries affect assignments legally? Do release rules make second-delay timing irrelevant? Counterfactual transitions can falsify either. | Assumption integration in report/decisions; preserved research3/FORENSICS and available-feedback proof. New transition tests owned by production_review. Reviewed by statistics_review. |
| Mathematical theorist | next_mechanisms | Does complete available-actor history factor the response posterior? Does delay invariance imply a conditional reward identity? A pending-actor or availability counterexample can refute overbroad claims. | RESPONSE_FACTORISATION, DEADLINE_INVARIANCE, deadline audit and source snapshots. RESPONSE_THEORY_REVIEW and DEADLINE_REVIEW owned by statistics_review. |
| Predictive-model researcher | next_mechanisms | Do exact response moments or shrunk acceptance histories improve prospective terminal proper scores? Eight fixed comparisons can reject superiority. | candidates.py, prediction_audit.py, PREDICTION_REVIEW, calibration artifacts. Numeric review by statistics_review; code review by production_review. |
| Dynamic allocation researcher | root and next_mechanisms | Does changed verification order improve later opportunity use at fixed scoring? Own-parent C comparison can falsify it. | hard_priority candidate specification; root mechanism/ablation analyses. Criticism by statistics_review. Prior exact tiny-DP counterexamples remain preserved. |
| Information-acquisition researcher | next_mechanisms | Does coordinated hard/goal acquisition beat the surplus-query parent despite displaced verification? Own-parent screening contrast can reject it. | coordinated_goal, goal_surplus controls and MECHANISMS. Code review by production_review and criticism by statistics_review. |
| Empirical statistician | statistics_review | Do paired effects survive seed clustering, independent C/D/E and fixed program multiplicity? Independent reaggregation can contradict reported uncertainty. | STATISTICAL, SCREEN, FOCUS, SELECTION and FINAL reviews; independent statistics. Reviewed by root. |
| Adversarial critic | statistics_review throughout | Could favorable deadline draws, leakage, approximate likelihoods, searched selection or float boundary errors explain gains? Explicit alternative explanations and controls can refute each claim. | CRITIC, theory/deadline reviews, focused and final written criticism. Resolutions owned by root in DECISIONS. |
| Independent replicator | statistics_review after E | Does a separate public simulator loop reproduce actions and metrics and all primary clusters? Any discrepancy refutes execution equivalence. | independent_replicator.py, REPLICATION and confirmation replay artifacts. Reviewed by root; production_review independently checks container equivalence. |
| Production/provenance engineer | production_review, integrated by root | Does actual restricted execution equal in-process behavior and meet tested resource limits? Stress, real interruption or mismatch can falsify. | tests, Dockerfile, production.py, production reviews/artifacts/ledger. Root verifies hashes/preservation/archives; statistician critiques inference scope. |

Implementation ownership is exclusive: the model researcher alone owns candidate
source, the director alone owns the wrapper/benchmark/registry, production owns
its tests/container harness, and the statistician alone owns the independent
replicator/review files. Frozen inference sources are never edited after B.
Host analysis changes are separately timed and disclosed. No agent concurrently
edits another agent's source. A critic remains involved through all waves.

Compute allowances: model construction/tiny checks 180 CPU seconds; prospective
prediction audit five CPU minutes; production preparation 180 measured host CPU
seconds and selected replay 300; independent replay 300 OS CPU seconds. The
primary B/C/D/E grids are fixed before execution and logged with actual OS child
CPU and wall time. Docker daemon CPU is unknown. Earlier underestimated replay
costs are disclosed, not replaced by parent-only CPU. There is no external spend.

Waves: candidate/code/theory preparation; screen criticism; focused predictive
and mechanism audits while D runs; selected restricted replay alongside E;
independent confirmation replay, final critique and provenance closure. Idle
agents take verification/theory/counterexample tasks rather than starting
unregistered candidate searches. This round stops after its fixed E, regardless
of significance.
