# Research 7 planning evidence inventory

Scope: requested R6 report, four stage analysis JSONs, four Stage E reviews, the two team planning texts, and the supplied transcript. Read-only extraction; no experiment, fit, simulation, or tests were run. The transcript is a working log, not an independent source of empirical evidence.

## R6 findings and strength of evidence

The controlling result is negative: the sole frozen contender, `N3_two`, did not establish superiority to shipped greedy `G` on the pre-registered Stage E comparison. The supporting record is consistent across `research6/REPORT.md` (“Executive Summary,” “Stage E: Frozen Confirmation,” and “Final Conclusions”), `results/research6/stage_e_confirmation/confirmation_analysis.json`, and all four `research6/reviews/stage_e_*.md`. This means the confidence interval includes zero; it does not establish equality, equivalence, universal superiority of G, or robustness over every possible policy.

The report’s distinct mechanisms/results:

| R6 mechanism or claim | Report location | Evidence class and careful reading |
|---|---|---|
| Pairwise hard-constraint acquisition has complementary value / feasible-edge revelation is non-submodular | “Proven Mathematical Results” §1.2 | Mathematical result within stated constructed model; it motivates joint acquisition but does not show a live-policy gain. |
| Exact 2-query coordination over candidate complementary pairs; small-world dynamic planning | “Exact Simplified-Model Solutions” §1.3 | Exact only for the small constructed model (2 pairs/4 actors) and stated latency condition. Not a general optimality result. |
| `N3`: collision-aware joint hard-query acquisition (4 bundles) | Stages B–D | Empirical point gains in exploratory stages; all stage intervals overlap zero and are selection-stage estimates. Not confirmatory superiority. |
| `N3_fifo4`: four hard bundles in FIFO order | Stage C | Exact observed equality with G on 60 clusters × six families (360 paired episodes). Supports equality on these registered worlds/implementation; “proves zero improvement” is too broad outside that finite comparison. |
| `N3_two`: collision-aware 2-query acquisition with FIFO completion | Stages C–E | Exploratory positive means in C/D, then near-zero Stage E confirmatory estimate. No established general gain. |
| Static hard queries can help in `cold_start` and hurt in `delayed` | Stage E family breakdown | Exact family point estimates are opposite (+0.034151/−0.034151), but this decomposition alone does not identify a causal mechanism. The explanation “upfront query budget is wasted before delayed feedback matures” is plausible and consistent with the policy/scenario contrast, but remains mechanistic interpretation. |
| Online latency-regime detection and dual-price reservation | “Unvalidated Hypotheses” §1.6 | Explicitly unvalidated. R6 should motivate a future test, not be cited as evidence these work. |

### Stage facts (from JSON; metric is paired seed-cluster mean difference in MSMI/100)

| Stage | Design | Candidate results vs G | Inferential caveat |
|---|---|---|---|
| B screen | 40 clusters, seeds 110001–110040; 1,440 episodes; exploratory | K +0.018750; N1 +0.006250; N2 −0.029167; N3 +0.033333; P +0.002083. N3 passed the stated +0.025 screening gate. | N3 SE 0.04414; 95% CI [−0.05594, +0.12261], p=.4546; one-sided 90% lower −0.02420. All candidate CIs include zero; Holm adjusted p=1.0. Gate is a screening rule, not evidence of an effect. |
| C replication/ablation | 60 clusters, 120001–120060; 1,800 episodes; exploratory | N3 +0.041667 (SD .26464); N3_two +0.043056 (SD .24811); N3_fifo4 exactly 0 (SD 0, all six family means 0); P −0.013889. N3_two one-sided 90% lower +0.001542. | N3 CI [−.02670,+.11003], p=.2275; N3_two CI [−.02104,+.10715], p=.1840; Holm .7361. The zero FIFO contrast is a finite-seed implementation contrast. `N3` vs `N3_two` comparison is reported in the R6 report as p=.9613, SD .2646 vs .2481; matching point values do not establish equivalence. |
| D independent selection | 80 clusters, 130001–130080; 1,920 episodes; exploratory | N3 +0.040625 (SD .27367; 90% one-sided lower .001083); N3_two +0.040625 (SD .26749; lower .001975); P +.035417 (SD .23932; lower .000837). N3_two selected by registered lower-bound/simple-tier rule. | N3 CI [−.02028,+.10153], p=.1881; N3_two CI [−.01890,+.10015], p=.1782; Holm .5346. Selection/tie-break chooses a contender for E; it does not establish a difference from G. |
| E fixed confirmation | 571 untouched clusters, 140001–140571; 6,852 episodes; `N3_two` vs G; two-sided alpha .01 | Mean +.003210741; SD .256047; SE .010715; t=.29964 (df 570); p=.764559; 99% CI [−.024483,+.030904]. Bootstrap 99% CI [−.023351,+.031232]. Family means: development +.012259; sparse −.002627; cold_start +.034151; delayed −.034151; shift +.005254; drift +.004378. | Pre-registered lower-bound criterion fails. “Perfect cancellation” applies only to the cold_start and delayed family estimates; their equal/opposite values do not explain the whole total, which is +.003211. No equivalence margin was registered. |

Overall R6 accounting: stages B–E have 751 fresh clusters and 12,012 episodes (1,440 + 1,800 + 1,920 + 6,852). The report further claims zero invalid episodes/fallbacks and 108 production replays / 12,960 calls; those are execution-integrity facts, not efficacy evidence.

## Distinct proposed mechanisms in the supplied R7 texts

These are hypotheses/designs, not observed gains. The page references are the printed page numbers in `team_approach.txt` / round-one proposal format; section references are from `team_proposal.txt`.

| Proposed mechanism | Location | Concrete operation / novelty | Status and limitation stated in source |
|---|---|---|---|
| Reciprocal feasibility gate | Approach pp. 3–4; proposal §D, pp. 5–6 | Before scoring, classify pair as feasible, known-infeasible, or clarification-needed; preserve unknown/declined semantics; check both directions. | Core correctness layer, not itself an efficacy claim. |
| Allocation-aware clarification / truth-blind within-day VoI | Approach p. 6; proposal §§E.3/F, pp. 6–8 | Prioritize hard bundles that can flip candidate-edge feasibility; for a bounded shortlist of soft asks, enumerate hypothetical answers and ask only if the selected matching would change. | Proposal reports earlier 576-episode VoI experiment as inconclusive. A changed allocation is an intermediate event, not proof of extra mature MSMI. |
| Feedback-adaptive field/member choice (`n03`) | Proposal §F, p. 8 | Use ask log and released feedback/conversion history to choose which member/soft field to query over time; could persist per-field rates. | Explicitly untested; cold-start sparsity, declines, late asks and selective outcomes are known constraints. |
| Feedback-reweighted edge scores (`n02`) | Proposal §E/RQ1, pp. 6–7 | Reweight pair scores using conversion history already visible in feedback/introduction logs. | Explicitly untested; R6 decision-state autopsy found no registered decision-time feature passed its gate, so personalization needs fresh evidence. |
| Conditional MSMI prediction funnel | Approach p. 5; proposal §E, pp. 6–7 | Estimate conditional stages (mutual acceptance, date conditional on mutual, second-yes conditional on date) and multiply to rank by composite outcome; maturity masks restrict training to released/closed labels. | Proposed architecture; proposal’s prior composite AUC .5937 and worse-than-prevalence log loss constrain use to ranking, not calibrated probability. |
| Global non-overlap matching | Approach p. 7; proposal §E/RQ3, pp. 7–8 | On feasible graph, maximize sum of edge values subject to vertex-disjoint selection (general-graph maximum-weight matching), with deterministic feasible-greedy fallback. | Approach presents as primary contribution; proposal is more cautious and gates graph optimization on score/value alignment. R6 report’s N3 collision handling does not validate global weighted matching. |
| Guarded waiting / lookahead (`n04`) | Proposal §E.6 / RQ4, pp. 6–7; Approach pp. 2, 9 | Estimate arrival scarcity and wait only if expected future option value exceeds current edge value; default no-wait in thin markets. | Untested successor to failed unconditional waiting rules; requires guarding coverage and uncertainty in arrival estimates. |
| Optional exploration and recency adaptation | Approach p. 9 | Small/decaying feasibility-safe exploration; conservative recency weighting or change detector using released feedback. | Optional, must earn inclusion by paired ablation; no claim of evidence. |
| Hard bundle completion tiers | Proposal §E.3, p. 6 | Rank bundles by number of feasibility-flippable pairs, then fill hard fields for high-degree clarification-blocked members; soft asks subordinate. | Proposed rule. No R6 finding establishes these tiers raise reward. |

## Overclaims, discrepancies, and causal-evidence cautions

1. **R6’s strongest causal-sounding language exceeds its design evidence.** Stage E is a paired fixed-policy simulation on untouched seed clusters and estimates the total policy contrast under the simulator distribution. It does not isolate the proposed mediator “feedback arrives too late” or identify deadweight loss as the unique cause. Report/reviews call the exact family cancellation a “mechanistic root cause”; better wording is “family pattern consistent with the proposed timing mechanism; mediator not directly identified.”
2. **“N3_fifo4 proves capacity alone has zero value” should be scoped** to the registered `N3_fifo4` implementation, compared with G, over Stage C’s 60 seed clusters / 360 episodes. The JSON proves identical observed scores there. It cannot establish zero effect for other implementations/seeds or a general absence of capacity value.
3. **R6 superiority and “greedy undisputed champion/robust across all families” are not supported by a non-significant superiority test.** E supports “N3_two superiority not established; retain G as supported default.” It neither proves G optimal nor establishes statistical equivalence. Stage E includes negative and positive family estimates and no per-family equivalence tests.
4. **Selection stages are exploratory even when the one-sided bound is positive.** B/C/D estimates are candidates screened, replicated, then selected; the report’s progression (+.0333, +.0431, +.0406) should not be summarized as three independent confirmations. E is the confirmatory estimate and shrinks to +.0032.
5. **Proposal-level R6 statements are internally careful in places, but headline compression can reverse the nuance.** Proposal §C explicitly says greedy is best only among evaluated candidates and offline estimates are not forecasts; its reported +18.7% full-reveal offline bound is not live policy efficacy. Keep that caveat alongside any use of the number.
6. **Allocation scope differs between R7 texts.** Approach p. 7 proposes global maximum-weight general-graph matching as the primary contribution; proposal §E.5 initially describes descending-score greedy non-overlap plus optional single-swap local improvement, and §RQ3 says weighted matching is conditional on RQ1 score/value correlation. They are distinct algorithm variants; don't present them as one already-fixed method.
7. **Transcript provenance:** the supplied transcript around lines 678–731 appends hypothesis-ledger outcomes, and lines 754–787 restate Stage E stats and the mechanistic interpretation; lines 981 onward reproduce the final report. These repetitions are not independent replications. It also includes implementation/test commands from past work; they do not add evidence for causal mechanisms.

## Source map

- R6 primary summary: `research6/REPORT.md`, “Executive Summary,” “Categorization of Scientific Knowledge,” especially Empirical Findings §4 / Stage B–E, “Final Conclusions.”
- Numeric source: `results/research6/stage_b_screen/analysis.json`, `stage_c_replication/analysis.json`, `stage_d_selection/analysis.json`, and `stage_e_confirmation/confirmation_analysis.json`.
- Stage E interpretation/audit: `research6/reviews/stage_e_critic.md` §1–2; `stage_e_developer_case.md` §§1–3; `stage_e_registration_review.md` §§1–4; `stage_e_statistical_review.md` §§1–4.
- R7 proposal: `scratch/research7_planning/team_proposal.txt`, §§C–F and H–I; printed pages 4–11, especially explicit statuses and limitations.
- R7 approach: `scratch/research7_planning/team_approach.txt`, pp. 3–9, especially primary contribution, global matching, system design, learning and optional modules.
- Supplied transcript: `/Users/manyakaistha/.t3/userdata/attachments/c075bd75-f89f-40db-9bfc-d2970d6feaf5-6072b775-9de4-4582-869d-f00f86e6dda6-txt.txt`; relevant R6 summary spans lines 754–795 and 981–1096. Transcript line numbers are locator aids, not independent evidence.
