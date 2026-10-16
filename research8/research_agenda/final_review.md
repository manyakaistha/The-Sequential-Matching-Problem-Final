# Final independent review of the research agenda

Date: 2026-10-14. Reviewer: `/root/agenda_final_review`; integrating reviewer: root.
Scope: `REPORT.md`, `theory.md`, `model.md`, `critique.md`, the metric/check artifacts, repository delegation instructions, and narrow simulator/evaluator source checks. This reviewer owns only this file. No new episode, fit, policy selection, latent world, or archived-file edit was performed. Numerical checking consumed under three CPU seconds, below the 60-second allowance.

## Disposition

**Accept as a completed research synthesis and finite proposed development agenda.** No mathematical blocker was found in the conditional improvement arguments or declared examples. Acceptance does not admit a learned asset, certify a deployed policy, launch the proposed stages, or establish observation-only superiority. The package clearly separates these claims.

`REPORT.md` is the director's adopted synthesis. Its smaller stage sizes and eight-arm selection/replication cap govern this proposal; the larger 48-screen/96-replication/12-arm recipe in the earlier `critique.md` is an alternative recommendation, not a second authorized campaign. This review completes independent integration of the report and theory; the critic's final sentence saying that integration is pending is historical draft status. The director should make this precedence visible in the final package.

## Theory and edge cases

The history-space one-step improvement proof is valid when the deployed action has nonnegative **true conditional** baseline advantage at every reachable history. The policy-library proof is also valid: the next-step switching value dominates the selected complete policy's continuation. Neither requires an exhaustive action menu, and neither establishes global optimality. The coordinated-wait example correctly shows why full-horizon evaluation followed by G can still miss two successive waits.

The retained-suffix telescoping identity is correct on augmented public history containing the incumbent descriptor and memory. It requires actual execution of the selected controller and preservation of its suffix. A reset to G after the first hold can invalidate the guarantee. Consequently references in `model.md` to retaining the “validated parent” must mean the current validated incumbent suffix for this route; ordinary static experiments may retain their ordinary fixed parent. An option's declared unsupported-state fallback must be included in its evaluated continuation. An unexpected execution failure is not covered by the theorem.

The report's normalized terminal objective and the theory's assignment-booked normalized contributions are compatible. Pending introductions contribute a common conditional term in candidate comparisons, while their released feedback remains in future state evolution. Their outcomes must not be counted repeatedly. Count improvement alone is insufficient with a random final denominator; the theory's two-world reversal is valid. On day59 the arrived-by59 denominator is already determined, so maximizing true conditional eventual edge rewards maximizes that day's endpoint expectation. “Calibrated” estimated scores do not make this an exact true-law optimizer without further assumptions.

The isolated stopping threshold is correct under its stated absorbing/disposable-partner model and an offer-independent survival probability. Waiting is worth `.8 × p × .9 = .72p`; today's `.5` is rejected iff `p > 25/36`, with a declared tie rule at equality. It does not reduce the actual graph to independent actor prices. Shared future-partner competition and changed joint return laws prevent that reduction.

The learned-model distinction is sound. The paired value-error allowance is `epsilon_J + epsilon_I`; robustness must minimize a candidate-minus-incumbent advantage under the same model. Population calibration, ensemble agreement, or a held-out average error cannot establish uniform history-conditioned bounds. Joint persistent profiles, selective stage eligibility, observation releases, pause, and availability must remain coherent; controllers cannot observe hidden sampled information.

The Monte Carlo statements have the required independence/multiplicity qualifications. Fresh checking of one selected pair avoids a menu correction; using the same draws to select and certify all candidates requires simultaneous control. Repeated checking until positive is excluded. The report's conservative two-sided union illustration gives radius `24.008069782998017` for eight comparisons, 64 draws and failure level `.01`. The theory's one-sided independent-check formula is also correct. Realized endpoint range `[0,50]` is justified by pause before busy release for every qualified pair; that bound need not apply to a sum of conditional probability estimates along one sampled path. Adaptive certificate failure is correctly treated as an unconditional expected-loss allowance, not a claim obtained by conditioning the environment on “no failures.”

## Independent checks and numerical scope

Running `check_theory_examples.py` passed and exactly reproduced `constructed_results.json`: static exchange `.6→.8`; coordinated wait `.5→.9`; day13 omitted-tail failure; arrival-risk values `.36` and `.648`; two-hard-bundle complementarity at cost six; and shared-partner double counting. These checks verify declared arithmetic, not a model fit or simulator policy result. They do not exercise every fixture proposed in theory section 9; those are future implementation tests.

A separate read-only scan of all **4,608** P4 commit JSONs verified a complete `96 × 6 × 8` grid, unique cells, both stored validity flags, empty validation-error lists, denominator 200, stored endpoint `Q/2`, and one common world hash per seed/family across arms. It exactly reproduced every arm mean and all four seed-cluster contrasts in `root_metric_check.json`, including its exploratory 95% t intervals with 95 degrees of freedom. The canonical sorted compact-JSON `[seed,family,policy,Q,A,Y]` SHA256 was:

`2f33c5a11a38d8fb250100addf84c1f615f8805f7799262616e53fc89d414793`

This checks committed counts, denominators and metadata. It does **not** independently derive reward from public event logs, establish latent-world correctness, or turn closed P4 into a new confirmation sample. The factor-two reporting correction and cluster-unit correction are supported at precisely that metric layer. The no-contender disposition survives the correction; neither P/Q6 superiority nor A1 harm/equivalence is established.

The adopted development arithmetic is correct:

| Stage | Maximum cells |
|---|---:|
| E1: `(32+16) × 6 × 3` | 864 |
| E2: `32 × 6 × 8` | 1,536 |
| E3: `16 × 6 × 8` | 768 |
| E4: `48 × 6 × 8` | 2,304 |
| Total | **5,472** |

At 20 CPU seconds per cell this is 30.4 CPU hours. It excludes E0 extraction/audit, fitting, storage/analysis and E5 confirmation. Eight direct-search configurations include the unmodified parent, as specified in `model.md`; eight selection/replication arms include G/Q6/P and all necessary own parents. Two entrants are a maximum, not a promise that any two mechanisms and their controls fit. E5 has seven arms across six families: 1,107 clusters imply 46,494 episodes. Independent noncentral-t calculation reproduced all six critic sample-size entries: 282/1,107/4,409 at SD `.30`, and 381/1,504/5,999 at SD `.35`, for separations `.10/.05/.025` with the stated 10% inflation. These are assumption-based power calculations, not measured effect forecasts.

## Practical priority and remaining claims

The adopted first work is proportionate: public-data maturity/opportunity inventory, a small scorer and same-score allocation repair, then a finite complete-episode search. This can answer useful empirical questions without first building an entire joint simulator. Full-horizon G rollout is a transition/tail control; persistent options address its separate weak-continuation failure. Query coupling should follow evidence that packages change useful complete actions and that the post-answer controller is modeled faithfully. No larger neural model is justified yet.

Future execution still needs one concrete freeze choosing the finite recipe, exact gates, code/assets, controls, fresh seed partitions and measured resources. That is an execution prerequisite, not an additional requirement to finish this research package. A failed support, action-change, own-parent, or runtime gate should produce simplification or a no-promotion result within the cap. No new fitting or episodes are needed to make the present synthesis reviewable.

Remaining unproved claims are the size/prevalence of real action-changing headroom; public-model calibration and off-policy support; faithful joint transition inference; safe practical switch bounds; active planning/distillation latency; and repeatable endpoint gains against both own parents and the complete frozen reference panel. The unconditional superiority of an observation-only policy remains open. The accepted accomplishment is a coherent, falsifiable route toward testing it.

## Supplemental receipt: reference identity and soft-query headroom

After the director updated report section 1 and its priority order, a bounded independent follow-up reproduced every mean in `historical_funnel_summary.json` from the commits. All **1,728 G/P/Q6 cells** have stored `soft_asks=0`, not merely an average rounding to zero. G's mean `.6875` and Q6's `.7569444444` qualified introductions are counts per 200-member episode; their per-100 endpoints remain half those values. Funnel means are descriptive, not stage-specific causal effects. This follow-up used under one additional CPU second and no new episode, fit, public action replay or latent world.

The workspace `policy.py` and `research7/policies/references.py` hashes exactly match the frozen P4 source manifest:

* `policy.py`: `c745c385a5a1e8dd0ac88320ec8bee2c3d3270e0b23cce3d847b743c551d650a`.
* `research7/policies/references.py`: `91fe001e6382702c39f3d83cd83cda56537331f8c9b432ead4d0e4e6a8436628`.

The three other files listed in `reference_source_audit.json` also independently match the frozen manifest. Source inspection confirms R maps to official `mode='random'`; its ask branch calls unchanged `baseline_asks`, while only the legal matching edge order is shuffled. Thus the frozen R is random matching with the baseline FIFO hard-bundle asks, **not RandomAsks or a random-soft acquisition control**. Frozen-source identity and stored counts support this correction; this receipt is not an independent reconstruction of the ask event stream.

The revised early priority—targeted soft questions using genuinely unused same-day budget, alongside missingness-aware scoring—is justified as an **untested mechanism hypothesis**. Hard-only leading references do not refute soft acquisition. The proposed parent-hard batch preservation, pre-answer complete package selection, same-allocator targeted/random-eligible/no-soft controls, and explicit displacement accounting identify the relevant comparison. Information can worsen a fixed heuristic allocator, and filling unused budget has no automatic reward guarantee. Available legal alternatives, useful unknown fields and actual slack must still be measured; the episode-total hard counts do not locate these opportunities in time. The new hypothesis fits within the adopted finite portfolio by reducing other entrants if its controls consume slots. This supplemental finding changes the practical priority, while the scoped acceptance and remaining unproved superiority claims stay intact.
