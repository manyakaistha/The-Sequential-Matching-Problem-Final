# Independent review of coupled strategy specifications

Reviewer `/root/r7_theory`, explicit Astra/high work order; director `/root`, independent critic `/root/r7_critic`. Date 2026-10-12. Scope: D1/D2/L2 value, public-only teaching, action timing, causal controls and exact-test realizability. Read-only review elsewhere; this file is the exclusive output. Allowance90 CPU seconds, analytical reading only. No tests, solvers, simulations, fitting or world generation were executed.

**Verdict: revise before implementation admission.** The central value definition and intended information boundary are coherent. L2 has a definite circular admission dependency. Several action/parent/teacher definitions need narrowing before an implementer can realize a unique policy. These are planning defects, not empirical evidence against the mechanisms.

## Accepted mathematical and information contracts

1. STRATEGIES' Bellman objective books each assignment's expected eventual qualified reward once, while keeping its future observations in the state transition. This is valid here because subsequent policy actions cannot change the already scheduled attempt's eventual reward, and follow-up covers all supported event times. At any later decision, expected reward from old assignments is independent of the new action and can be omitted from the optimization. Do not add old observed reward again. No independence of reward, pause and feedback is implied.
2. `V_60=0` is correct for **new assignment reward** after all earlier assignments have been booked. It is not a statement that pending attempts have zero actual eventual outcomes. A planning cutoff before60 likewise includes full q for assignments made before cutoff, but omitted *future assignments* create declared tail error.
3. Persistent public-conditioned actor/profile draws, fresh introduction-specific shocks and observable-history merging avoid the most obvious hidden-state shortcuts. Explicit model-generated anonymous arrivals are permissible surrogate futures. True future identities, exits, busy timers and original latent values are not permissible teacher features or labels.
4. The rational T03–T08 constructions are internally coherent as reduced models, subject to their full laws in TEST_SPEC and the preserved theory note. Their numbers are neither new simulator estimates nor guarantees that the mechanisms occur often. T04's real-budget embedding is correctly still required. Independent history/action enumeration remains necessary; an explicit hidden-state MDP without observational-history constraints would not prove policy feasibility.
5. The plan correctly separates downstream delay from immediate hard-answer timing, and distinguishes qualification from positive pause. Its family-effect/intervention restrictions avoid the earlier unsupported causal latency claim. A same-seed modified simulator intervention alone does not preserve changed random streams.

## R1 — blocking circular L2 admission

**Locations:** STRATEGIES lines141–143; PLAN_7B lines50,54,68–74; PLAN's P4 gate at line89; TEST_SPEC T30/P2 matrix.

L2 is permitted only after D1 wins its own-parent P4 comparison, but must be trained/frozen and included in the same P4 grid. That comparison is unavailable before the grid runs. Moving target generation to “P4 entry” does not resolve this: entry precedes the required outcome. A post-P4 student cannot be inserted retrospectively into the completed grid, and P5 disallows a new fit.

**Recommended repair:** distinguish *admission* from *advancement*. If D1 passes transition/teacher fidelity and the P3 development gate, train the predeclared L2 configuration on the already fixed P2/public training partition, evaluate its imitation gates on the fixed held-out P2 partition, and freeze both before any P4 generation. Run D1, L2, A1 and required references in the predeclared P4 grid. Require D1's own-parent P4 win **only for L2's advancement to P5**, alongside L2's own stated P4 criteria. No P4 outcomes enter student fitting. This preserves one conditional slot and the12-arm cap.

Alternatively preserve the strict “teacher must first win P4” rule and defer L2 entirely to a later round. A separate new student replication phase would require an explicit new phase/seed/count/statistical amendment; it is not implied by current caps.

State L2's primary own-parent explicitly. A faithful student equal to D1 cannot satisfy a strict positive reward difference against D1, even when the teacher beats A1 and all references. If L2 is intended as compression, use A1 as the reward parent and D1 as the teacher-retention comparator, with a preregistered retention criterion and no unproved equivalence claim. If superiority to D1 is intended, retain D1 as the reward parent but admit that this tests an improved controller, not merely successful compression. Either choice must propagate into the comparison graph and P4 gate before outcomes.

## R2 — D1 local action menu is not yet realizable for every input

**Location:** STRATEGIES lines101–109.

The contract simultaneously includes full G, A1 and an empty action, fixes all outside pairs, and permits at most six affected actors plus six boundary actors. Full G can differ from A1 on arbitrarily many actors. A globally empty action changes every outside assignment when outside pairs exist. These requirements cannot always all hold.

**Required repair:** define one deterministic affected region relative to A1, with a precise boundary inclusion rule. Include G only if its full symmetric difference from A1 fits that region, otherwise record its omission; or use a specifically named feasible local G-derived replacement. Define wait as removing the region's pairs while retaining outside A1 pairs; global wait is allowed only when the represented region contains every assigned actor. Every alternative's changed endpoints must meet the same cap. Explain whether boundary actors may become affected and how that consumes capacity. An unsupported boundary returns A1, without pretending to certify isolation.

Also freeze the *rollout ask controller* (default FIFO) in addition to the rollout match controller. “Correct query budget” does not determine which future asks occur. D1's zero-continuation control equals A1 only when both use the same weights, quantization, tie rule and actual feasible solver scope; a score-greedy solver fallback is a separately recorded behavior.

## R3 — D2 needs an explicit approximation target and matched acquisition control

**Locations:** common J_C definition; Q2 at lines87–95; D2 at lines115–117.

Q2 is defined by hypothetical A1 matching. Merely replacing deployed matching by D1 makes “Q2+D1” inconsistent with the common requirement to value questions under the controller actually deployed. There are two legitimate controls, with different interpretations:

- A **controller-consistent immediate-value control** evaluates the immediate q sum of D1's chosen action after each answer branch, with acquisition tail value disabled; D1 matching still uses its fixed continuation model.
- An **explicitly mismatched acquisition control** retains original Q2's A1 hypothetical evaluator but deploys D1. This tests controller mismatch and cannot isolate acquisition horizon alone.

Choose/name the first as the primary horizon ablation if that is the intended contrast. A surrogate may approximate it, but the same surrogate family and approximation checks should apply to the corresponding D2 parent; otherwise the contrast changes both horizon and evaluator fidelity.

For D2 targets define the teacher scalar precisely: the selected D1 action's immediate q plus that action's continuation under the frozen rollout policy, measured on independent teacher-evaluation draws. The maximum of noisy selection values is a different, optimistically selected target. Record teacher action, selected value, baseline value, horizon and fallback status. Train only on public states and public-model-generated answer branches derived from the registered P2 partitions, not private actual branch values. Distinct answers must be passed through an observation-only controller; sampled future latent state can generate outcomes but cannot select the controller's action directly.

Add a held-out D2 surrogate error/action-ranking gate (currently only L2 has explicit teacher agreement thresholds). A cheap surrogate of a valid teacher is realizable; “actual D1 value” cannot be asserted without this approximation qualification. Any fitted D2 target model consumes the shared fit budget, as does L2; caching is not a second uncounted training channel.

## R4 — exact tests must target the stated model, not a different estimator

T09's exact3/8 forecast assumes a fair two-point response-type prior (.75/.25). H1 instead specifies Beta(1,1) for **first Yes**, whose predictive value after one observed zero is1/3. First Yes additionally includes response and acceptance, so it is not the response-only target in T09. H1 cannot be required to reproduce3/8 without changing its declared model.

Split the tests: retain3/8 for a reference two-type response posterior/L1 component, and add H1's own Beta algebra with an explicit event target (1/3 after one mature zero under its fixed Beta(1,1) default). If P2 selects an empirical-Bayes prior, expected outputs must use that frozen prior. This is a model-contract blocker for H1, not a refutation of either estimator.

T04 is a query-choice test of D2. D1 with fixed FIFO asking need not choose the optimal preparing query; its T04 responsibility can be transition/return consistency only. Gate D1 on its action-value cases and gate D2 on the query-choice optimum, rather than requiring FIFO D1 to solve an acquisition problem outside its action class.

Specify a direct pending-reward double-count fixture: one already assigned pending attempt with expected reward r and no future legal edge has new-assignment continuation0 for every action; with one new disjoint q edge its action advantage is q, not q+r. Existing prose asks for this check but the numbered ledger does not fully instantiate it.

## R5 — workload bounds must include independent validation

The shared planner bound32 particles×12 actions×12 steps=4,608 accounts for selection only. Winner-versus-parent margin checking with32 independent draws adds up to768 steps, for5,376 if only those two are checked. Evaluating all12 alternatives twice would be9,216. Freeze the intended count, whether current action is included in the12 epochs, and its resource forecast. D2 separately has up to96×32 package-branch evaluations plus independent margin checking and surrogate inference. No runtime guarantee follows from these arithmetic caps, but the ledger must not omit a whole validation pass.

## Closure required

Director should amend source strategy, phase, machine-plan and test contracts consistently, then request a bounded read-only closure check. Until R1 is resolved, L2's conditional slot must remain unavailable; R2/R3/R4 block the affected implementations' specification approval. R5 blocks a complete resource forecast, not mathematical validity. None of these corrections authorizes running the program.

Reviewed source fingerprints (SHA-256):

- STRATEGIES.md: d6916bb4e2dea05c027e466a6e2674aab3b8f91aeef76ee4a959627d3f058b7d
- TEST_SPEC.md: 5a0fa346036e4707673b954397df213105902fb4f950af3c8de9ced518fc5ce6
- PLAN.md: e40734df9e5019d82571dcff5449051d6aa74a81fa06555034149b136f0cbf52
- PLAN_7B.md: 8de182c9d63642c08024711d71b8dcbda49ffe542da45984358d0d4badc8f2dc

`research7/plan.json` was referenced by prose but was absent in the reviewed filesystem. No machine-readable phase/dependency closure is certified by this review.

## Bounded amendment closure review — 2026-10-12

A new read-only review examined the amended STRATEGIES, TEST_SPEC, PLAN, PLAN_7B and now-present plan.json under a50 CPU-second analytical allowance. No tests, scripts, model execution, fitting or simulation ran; source reads and fingerprints only. The earlier findings above are preserved as the original review record. The independent critic had read that record and concurred with R1–R5; this closure is the theory reviewer's inspection of the subsequent amendments, not a claim of new independent test execution.

| Finding | Resolution in amended specification | Disposition |
|---|---|---|
| R1 L2 circular admission | D1 fidelity, P3 admission and positive P3 A1 contrast permit student preparation on fixed P2 partitions before P4 freeze. D1's P4 own-parent win is now an advancement prerequisite only. A1 is L2's reward parent; D1 is the separately named observed retention comparator. The retention mean/coverage screen explicitly makes no equivalence or noninferiority claim. Machine plan and JSON first phase/parent agree. | Closed as a planning dependency |
| R2 full versus local menu | Region selection is deterministic relative to A1; full G is conditional on fitting the region; local empty retains outside pairs; changed boundary actors consume the six-actor cap. Unsupported regions/actions are rejected. T04 no longer demands that FIFO D1 optimize acquisition. | Substantive menu defect closed; one controller wording discrepancy below |
| R3 D2 target/control | Selected D1 action is valued on independent evaluation draws; public-model answer branches and nonanticipation are explicit; surrogate admission thresholds and shared fit ledger are specified. Immediate acquisition control uses the actual D1 action with tail disabled, rather than Q2's A1 action. | Closed as an approximate-controller contract |
| R4 estimator/exact fixtures | Final TEST_SPEC clarification separates mixture3/8 from H1 Beta1/3, distinguishes D1 transition from D2 query-choice testing, and makes pending-reward T31 mandatory for D1/D2/L2 teachers. | Closed; old short T09 ledger text should eventually be synchronized with its controlling clarification |
| R5 omitted validation work | Selection4,608 plus winner-parent768 gives5,376 future model steps; current-action overhead is separate. D2 counts3,072 selection plus64 validation surrogate branches, total3,136. JSON agrees with these bounds. | Closed as accounting; runtime feasibility remains untested |

**One remaining literal discrepancy:** the shared bounds freeze future rollout asking to FIFO and matching to A1, whereas D1's per-action paragraph still permits “A1 or frozen score-greedy, chosen before P3.” These are two different continuation controllers. Resolve by replacing that parenthetical with the already specified frozen A1/FIFO controller, or consistently declare an explicit registered choice everywhere. The director has been notified. This small wording correction is necessary before claiming a single fully frozen rollout specification; it does not reopen the repaired circular admission, value booking or menu construction.

The corrected contracts are otherwise coherent and realizable as bounded, model-dependent specifications. They establish neither that the fidelity gates can be passed nor that any policy will improve reward. Dataset separation, observation-only model transitions, independent exact enumeration, approximation sensitivity, full own-parent controls and runtime testing remain mandatory future work. The current machine-readable file records phase/parent/work caps; this read-only review did not execute its validator or certify the entire registry.

Closure-read fingerprints (SHA-256):

- STRATEGIES.md: 8687be6caeccadc091bf673caa4d20df908a5c57e6949d89ef28dbd6177282be
- TEST_SPEC.md: 91c3c697b4d37d592b37f920d70281fa7c023736135e6bcaae32753f89fd617d
- PLAN.md: e40734df9e5019d82571dcff5449051d6aa74a81fa06555034149b136f0cbf52
- PLAN_7B.md: 6204730f7f4e5211b00182ce6246afe05c9f1486cc4077a4ea63dd23fa5407af
- plan.json: e74db56c2fefc52c9a49b7271cbb16815fd7eb8133a4d07dfe99a248ae54b34c

### Final controller wording closure

The director corrected D1's per-action paragraph to “frozen A1 matching with frozen FIFO asks; its separately recorded solver fallback remains part of that controller.” A fresh source read confirms agreement with the common bounds. STRATEGIES.md at this check hashes to `2a5b61a92274281ff08e77e74a3a435636b847d8172e89e69044e809f0186f0a`.

**Final theory-plan disposition: R1–R5 closed at specification level; no unresolved substantive contradiction found in this bounded review.** The retained T09 short-row editorial note is resolved by its explicit final clarification and does not block implementation. This approves the reviewed planning definitions for future implementation/review; it is not execution authorization, passing-test evidence, empirical promotion or production certification. Subsequent cosmetic formatting may change file hashes without changing these findings; any substantive change requires renewed scoped review.
