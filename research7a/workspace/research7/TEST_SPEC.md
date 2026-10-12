# Research 7 phase test specification

All tests below are **planned**, not executed. Constructed arithmetic in the planning theory note is not a passed independent solver test. Future implementation must emit input/model hash, expected result, actual result, complete output, runtime/resource use, developer and independent reviewer. A reader/cheap orchestrator may collect evidence but cannot certify mathematical, statistical, or production claims.

## Test ledger and expectations

| ID | Phase/owner | Input and exact assertion | Failure consequence |
|---|---|---|---|
| T01 | P0/7a inventory | Source package includes every transitive import/config/model/preprocessor/dependency; an altered 1 byte and an omitted untracked module are detected | Registration blocked |
| T02 | P1/independent exact | 4-node weights AB=.90, CD=.05, AD=.65, BC=.65; legal greedy=.95, optimum=1.30; triangle matching cardinality 1, not fractional 1.5 | Allocation admission blocked |
| T03 | P1/theory+independent solver | Days 0, 8: AB q=.2, AC q=.8; fast AB 21/25 vs wait 4/5, slow AB 13/25 vs wait 4/5; queries immediate in both | Return model/planner blocked |
| T04 | P1/exact query tree | One bundle/day toy: now A U q=.2 or verify V; future VW q=.8 with arrival p; future-preparing query wins iff p>1/4. At p=0, now U; future 2 bundles removes tradeoff | D2 complement claim blocked |
| T05 | P1/exact reuse | Triangle days 0, 8, 16, q=p=.1, non-pause 8-day return: 271/1000; 2 actors/no dyad repeat: .1 | Reuse/dyad model blocked |
| T06 | P1/query | Hard complement F(empty)=F(A)=F(B)=0, F(AB)=1; shared-neighbor batch 24/25 vs distinct 7/5 with degree sums 8/5 vs 7/5 | Single-marginal approximation exposed; Q1/Q2 tests must distinguish |
| T07 | P1/continuation | Current AB, CD rewards .5 each and certainly retire; future AC=.9. Joint current 1 > wait .9; separate .9 loss per edge double-counts | Exact node-additive claim rejected |
| T08 | P1/static prices | Matchings covering identical endpoint set S have identical sum actor-price penalties for arbitrary rational lambdas; same-cardinality bonus cancels | Proposed price mechanism must change actor/time set or use joint residual |
| T09 | P1/public posterior | Fair type response .75/.25; observed mature nonresponse -> high posterior .25, next response 3/8; pending is not a negative trial | H1/L1 history admission blocked |
| T10 | P1/terminal | Last action day 59 with full follow-up: higher q/long duration wins over lower q/short duration absent later actions; late dual Yes may pause without qualified reward | Reward/occupancy interpretation blocked |
| T11 | P1/legality | All 11 hard fields known, False preserved; known fail dominates missing; declined unavailable; overlap/repeat/unavailable are rejected; asks cost 12 max and duplicate (member, field) rejected | Every candidate blocked |
| T12 | P2/time labels | Action-day features joined only with observed_day <= t; first-7/date-30/second-3 maturity masks; late/missing/canceled labels target-specific | Training export/model blocked |
| T13 | P1/P2 memory | A repeated public event updates once; ask->match memory preserved; episode reset to null/declared state; serialized memory < 1 MiB; no disk persistence | Candidate blocked |
| T14 | P1/refresh | Match sees real same-day query answers; all asks are chosen before any answers; identical pre-ask histories produce the same batch; hidden branches are merged | Query/planner blocked |
| T15 | P1/isolation | The same public request + memory with differing hidden seed/truth/future/variant produces the same action; no hidden module/file/network access | Any leaked version rejected |
| T16 | P1/P3 approximation | Actor draw reused across all incident edges/answer reveals; current boundary/full menu legal; shortlist-omitted-edge diagnostic; no silent graph bipartition | Planner/query admission blocked |
| T17 | B1/logging | Exact wire round-trip from compressed delta; whitespace/order/memory retained; a crash leaves closed earlier chunks verifiable; corrupted/missing chunk rejected | Fresh launch blocked |
| T18 | B1/B5 runtime | Empty + all-blocked + dense 200-node + max-history requests; whole-batch validation; startup/import/serialization including 10 sec; 2 CPU/1 GiB/64 PID/1 MiB offline container | Assessed candidate invalid |
| T19 | P2/selection | Whole-world/pool split; actor IDs disjoint; selected labels are not counterfactual ground truth; propensity None is not silently replaced; supervised features public only | Predictive claim/model blocked |
| T20 | B1/retry | Kill before commit, after chunk, and after commit; resume missing original cells; authoritative invalid retained; all attempts indexed | Runner admission blocked |
| T21 | A3/P7/archive | Archive + restoration file-set/hash exact; traversal, symlink escape, duplicate paths, and decompression bomb rejected | Transfer/final seal blocked |
| T22 | P0/routing | Provider adapter validates model/effort/fork; no Codex subagent_type/no unsupported flash_lite Antigravity assumption; fifth global slot rejected | Delegation blocked/queued |
| T23 | P0/freshness | Scan all old-seed uses + reserves + archives + external declarations; generation counts consumption; unknown parser gaps unresolved | Fresh grid blocked |
| T24 | A3/P7 grid | Missing family/policy, extra unknown cell, duplicate conflict/wrong stage rejected; unique global clusters reconstructed | Analysis blocked |
| T25 | B1/P5 hostparity | Identical examined requests/worlds across hosts/modes -> ordered actions,semantic pairs,memory,counts exact;quantized weights ties deterministic | Small-host E participation blocked; production fix before E |
| T26 | B1/P7 leases | Expired/revoked-generation lease cannot commit; late conflicting duplicate quarantined; transfer retry never reruns a cell | Stage integrity blocked |
| T27 | P5/P7 statistics | Handcrafted paired-seed rows verify equal-6-family mean, SD, n, and critical alpha .01/6; partial rows are not analyzed; independent CI tolerance 1e-10 | Confirmation report blocked |
| T28 | P2/model counts | H1 reuse >= 200 actors; L1 stage counts 2000/200/100/50 train and 20 qualified validation; no extra samples to rescue the count gate | Dependent model simplified/deferred |
| T29 | P2/P4 fidelity | Return law vs mean, pause != qualified, survival conditioning; D1 constructed regret <= .01, horizon 12 -> 24 sensitivity switch reversal <= 10% | D1/D2 rejected until bounded diagnosis resolved |
| T30 | Conditional pre-P4/L2 student | Public teacher features only; held-out agreement >= 95%, teacher-value loss <= .005, false switches <= 5%; assets <= 32 MiB | L2 conditional slot stays empty |
| T31 | P1/P2/planner teacher | An old pending attempt with expected reward r contributes zero new-assignment continuation; a new disjoint q edge adds q, never q+r | D1/D2/L2 value validation blocked |

## Detailed exact-case requirements

T03's reduced law: AB pauses with probability 1/5; two non-pause branches, each with probability 2/5. Fast returns both by 8; slow returns only one by 8. AB immediate qualified expectation 1/5. AC exists only at 8 with value 4/5. Thus immediate fast=1/5+4/5 * 4/5 = 21/25, immediate slow=1/5+2/5 * 4/5 = 13/25. The same q/asks differ solely in return law. Remove future AC or shorten to only day 0: both choose AB. These are constructed rational laws, not the simulator's delayed coefficients.

T04's scaled budget must be labeled. A real 12-unit embedding adds enough competing actor bundles that choosing V today versus U today changes tomorrow's feasible batch; independently enumerate every cost <= 12 action. Adding filler asks without useful competing opportunity cannot establish real-budget equivalence. All members queried must be currently available.

T05 must explicitly track **used dyads**, not just actors. Different partner attempts are allowed after legal return; repeating a dyad is never allowed. Toy q=p coupling is disclosed; extend a separate case with q<p to show unqualified pause and preserve late-feedback behavior.

T06 collisions use a shared verified neighbor: independent unlock probabilities 4/5 yield at least one, with probability24/25, whereas two distinct opportunities .7 + .7 = 7/5. Summing actor degrees 8/5 can choose the wrong batch. All branch observations and tie action sets are retained.

T07 proves a particular additive-loss reduction fails; it does not ban approximate duals. Independent enumerator needs no developer solver imports and must reproduce every reachable state's admissible action set/value, not only initial reported reward. Equal observed histories must share actions; otherwise oracle clairvoyance is present.

## Protocol/leakage fixtures

At least one JSON fixture each: empty population; zero ask budget; fully known; all hard-declined; known hard failure + unknown; False has_children; adult boundary 18; age min/max reciprocity; conflicting who_to_meet; differing pools; smoking/children/relationship/zone/schedule contradictions; partial soft; outstanding intro; reused actor/new partner; past dyad; overlapping batch; illegal field; duplicate ask; unavailable ask; costs 11/12/13; observed re-ask costs budget without new information; no stderr on stdout; non-finite numbers; memory limit -1/limit/limit +1.

Test source parses requests without truth/seed/family fields. Hidden-state variation uses a controlled **host fixture**, not inference access. IDs may establish identity/ties only. Randomly rename opaque IDs and preserve structure: compare non-tie decisions modulo rename; report expected tie-order changes. Deliberate seeded-truth reconstruction always fails authorization.

Timing fixtures verify response observed before deadline vs maturity; first No establishes a non-mutual branch while another response is pending; mutual Yes followed by pending date conditions lag; canceled date still occupies until D+6; both late Yes pause but are not MSMI; exited actor event still counted if it qualifies; all follow-up outcomes included. Available actors' own earlier incident outcomes have resolved before busy release, so do not invent pending personal feedback for their next introduction.

## Planned phase acceptance matrix

- P0: T01/T22/T23 and evidence/semantic/statistical registration reviews pass.
- P1: T02-T18 and T20-T27 constructed checks pass; no candidate with incomplete dependencies admitted. Smoke then profiles actual execution; constructed-only pass is insufficient.
- P2: T12/T13/T15/T19/T28-T30 plus public-provenance/answer-return validation; T30 is conditional at pre-P4 L2 admission, not a requirement for unrelated P2 candidates; stage counts are frozen feasibility gates. Failed rare-stage fits may be simplified but cannot be mislabeled personalized predictors.
- P2a/P3: completed exact grid, validity/action-trigger/coverage/family screens, all comparisons/raw diagnostics. No superiority claim from development.
- P4: same-grid/inference checks plus mandatory own-parent contrasts and T29; all interventions named separately with RNG scope. No skipped parent is promoted.
- P5: independent stats T27, full production T18/T25, freeze verification and exact power calculation. Selected-policy assets/tie/memory/work caps fixed.
- P6: complete hash-consistent grid, no committed invalidity, exact n/42n cells, sealed outcomes, no unauthorized reruns. Resource stop yields incomplete.
- P7: independent counts/CI/replay, T17/T21/T24-T27, archive restore and final-review closure. No final seal with unresolved scientific conflict.

## Stress/resources and deterministic fallback

Register normal work limits, exceptional wall guard, and logging before profiling. Force budget exhaustion at each internal checkpoint; only the already validated fallback is emitted. A native solver timeout must cancel/terminate the entire child group; no orphan process. Timing-based fallback differences across hosts block interchangeable confirmation data. Confirm the wrapper has time left for the final global guard, JSON serialization, and process exit, including cold imports. Peak RSS is platform-normalized (macOS ru_maxrss bytes, some Unix KiB); total worker RSS and numerical threads are accounted for. A few successful requests cannot certify all-input resource behavior; report the tested scope and cap.

Every stage retains zero/negative effects, all failed attempts, skipped unsupported cases and reviewer objections. A test pass does not establish policy reward superiority; only the frozen confirmatory endpoint can do that.

## Final model-target and workload clarifications

T09 has two distinct tests: the exact two-type response model gives 3/8 after mature nonresponse; H1's Beta(1,1) first-Yes surrogate gives 1/3 after one mature zero. They are different targets/priors, and neither is required to reproduce the other. An empirical-Bayes H1 prior uses its own frozen expected posterior.

T04 query-choice optimum applies to D2; D1 with FIFO asks is checked for correct transitions only. Add pending-reward test T31: an already assigned pending attempt with expected reward r and no new legal edge has new-assignment continuation 0; adding a disjoint new edge of expected reward q gives action advantage q, never q+r. Old expected rewards are not booked twice. This is mandatory for D1/D2/L2 teacher validation.

D1 selection accounts for 4608 future model steps and independent winner-parent validation adds 768, total 5376; current-action work, legality, answer sampling and serialization are additional measured costs. D2 package-surrogate branch evaluations cap 3136 including independent winner-parent draws. Training caches, teacher targets, answer/return fits and all bootstrap/student fits share one 12-fit ledger. No operation-count arithmetic implies a passed runtime test.
