# Evidence synthesis: Research 6 and both external team reports

Reviewed for planning, 11–12 October 2026. Prior reports/results/manifests/archives are preserved. This document corrects interpretation without rewriting the old record. Copies of the three supplied inputs are under inputs/ with SHA256 in PLANNING_MANIFEST; they make the plan portable to 7a. The transcript is a command/conversation log and repeats the final report; repetitions are not independent evidence.

## Research 6 primary result and full funnel

Metric throughout: qualified MSMI per 100 arrived members, equal-six-family, seed-cluster mean. Authoritative numeric sources: `results/research6/stage_b_screen/analysis.json`, `stage_c_replication/analysis.json`, `stage_d_selection/analysis.json`, `stage_e_confirmation/confirmation_analysis.json`. Narrative and registration/review sources: research6/REPORT.md, MANIFEST.json, registry/, reviews/, hypotheses.jsonl, decisions.jsonl, commands.jsonl. Structural scope: exact/THEORY.md, audits/simulator_contract.md and acquisition/allocation source. R6 planning README/plan.json retain historical 'proposed' status despite later completed runtime/results; dates/status must be read in artifact context.

| Stage | Complete registered design | Main paired result vs G | Meaning for R7 |
|---|---|---|---|
| B | 40 clusters, 110001-110040, 6 families, 6 policies, 1440 episodes | N3 +.033333; K +.018750; N1 +.006250; N2 -.029167; P +.002083 | N3 cleared a point-effect gate, not significance; N3 95% CI [-.05594,+.12261] |
| C | 60 clusters, 120001-120060, 5 policies, 1800 episodes | N3 +.041667; N3_two +.043056; FIFO4 zero; P -.013889 | Coordination variants positive exploratory direction; no established equivalence or benefit decomposition |
| D | 80 clusters, 130001-130080, 4 policies, 1920 episodes | N3=N3_two +.040625; P +.035417 | N3_two chosen by registered simplicity/lower-bound tie; selection is not confirmation |
| E | 571 clusters, 140001-140571, 2 policies, 6852 episodes | N3_two +.003210741, SD .256047, SE .010715, 99% CI [-.02448254,+.03090402], p .764559 | No superiority established; keep G as default. Interval excludes +.05 for this contrast, not all new mechanisms |

Totals: 751 fresh clusters and 12012 episodes across B–E. These stage totals exclude constructed exact inputs and verification replays. Reported 108 complete production replays = 12960 invocations across direct (48), subprocess (48), and restricted-container (12). Reported committed invalid/fallback counts are zero; the independent-attempt audit remains distinct from committed-row accounting.

The selected exploratory means around +.04 shrank in untouched E. R7 cannot size for +.04 as if known, recycle E as untouched, or fit a policy on E and cite its old CI as validation. R6 data are now examined development evidence.

## What each evaluated mechanism actually did

- G: FIFO hard bundles on available unverified/non-declined actors, then feasible, descending observed soft-agreement greedy matching.
- P: frozen population control imported from Research 4; no new Round 7 fitting under its baseline name.
- K: general-graph max-cardinality **first**, shipped score second. It is not unconstrained maximum expected terminal reward matching.
- N1: two bounded passes of local augmentation/exchange with shipped score; useful implementation predecessor, failed admission in B.
- N2: deterministic 8-day-block reranking of shipped-score ties; negative B point estimate. Changing a salt/block is not a new scientific mechanism.
- N3: 32-particle, 8-actor shortlist, fixed-k hard-batch selection by lexicographic expected immediate G matching count, then soft score; actual matching remains G. Sampled profile shared on incident edges. The quantity is not finite-horizon terminal reward.
- N3_two: collision-aware 2-query coordination with FIFO completion within legal budget; not simply spending only 6 units irrespective of remaining budget. Freeze actual code, not shorthand description.
- N3_fifo4: FIFO 4 hard bundles. C observes exact zero reward difference across 360 paired episodes. This finite control does not prove all query-capacity expansions are worthless.

R6 candidates that remained unimplemented/unvalidated cannot be listed as tested failures. Conditional learning/planning slots in the old plan do not imply fitting or simulations happened. Round 7's rationale rests on actual source/status, not planned candidate names.

## Mathematical/reduced-model evidence and limits

R6 constructions establish hard-query complementarity, collision-aware batch value, local greedy traps, odd-set constraints, reusable actors vs exhausted dyads, return-sensitive reservations and nonseparable future alternatives. They show where heuristics **can** fail under stated toy laws. They do not estimate how frequently those structures occur in the live public distribution.

Its conditional adaptive renewal relaxation theorem needs fresh independent outcome streams conditional on fixed latent Z and no anticipation; source uses seeded PRNG streams. A floating full-sim LP objective is not a certified upper bound. Prior-averaged occupancy coefficients can fail under adaptive selection. Full-sim continuous integration/valid enclosures/dual certificate remain unvalidated; no small-headroom ceiling is established for R7. Actor-additive prices cancel among matchings covering the same actors and can double-count a shared future edge; joint transition planning is a distinct hypothesis.

Exact DP tests with known calendars/retirement by the next toy decision cannot certify hidden pending-feedback/query controllers without explicit observable-history/non-anticipation extensions. Host oracles can diagnose bottlenecks but cannot feed a deployable policy or public training features.

## Important simulator deductions

`kit.py:112-132` resolves all asks immediately and declines stay unavailable. `advance:141-188` keys each dyad/day outcome on world seed + actors + day; delayed adds 5–12 days to date **after** responses, also consuming extra random draws. Ordinary responses 1–7 days, date offset 1–14 days, second observation <= date + 5. A day 59 assignment's latest scheduled feedback day 97 is covered by terminal day 100.

Non-mutual assignment busy=t+8; mutual busy=date+6 even for canceled dates. Both positive second responses cause a public pause even if late and not qualified. Actual availability also depends on hidden exit; the public release boundary does not guarantee return. An earlier unavailable state can conflate busy/exit/pause. Already-available actors' previous incident feedback is resolved before their next legal use, limiting the need for personal-pending modeling at that time. Pending global/regime and unavailable-actor likelihoods still matter.

Unknown arrivals/exits are not provided. Newly observed arrival counts are available; net-availability counts conflate returns, exits, matches, and pauses. Future-calendar reconstruction from IDs/generator seed is prohibited. Equal numeric seeds across families or policies do not fix every realized outcome after trajectories/time keys diverge.

## Corrections to Research 6's narrative

1. E cold_start +.034151 and delayed -.034151 are descriptive point estimates. Their cancellation neither explains the entire net effect nor identifies deadweight query cost. Other families: development +.012259, sparse -.002627, shift +.005254, drift +.004378. B/C delayed estimates also changed sign. A causal explanation needs controlled mechanism tests.
2. Hard-answer latency cannot explain delayed-family harm: answers are immediate. Plausible untested pathways are downstream occupancy, date qualification, changed actor/pair composition and different PRNG draws.
3. '2 queries capture 100% benefit' compresses similar selected means into an unsupported general claim. E found no benefit to partition. Similar point means do not establish equivalence.
4. 'Greedy uncontested robust champion across all families' is too broad. The supported decision is retain G because the frozen challenger failed to establish superiority. It is not proof G is optimal or superior in every family.
5. 'More information cannot hurt' applies to exact optimal controllers able to ignore costless information; heuristic acquisition/matching can worsen, and paid queries displace alternatives. Training proper-score gain is not policy-value proof.

## Supplied research_proposal.pdf: useful negative record and history hypotheses

15 pages, dated 9 October 2026. The authors report: 3-seed, 6-family baseline: primary G .389, R .278, learned .250, N .139; 800 worlds/259696 labeled rows; terminal AUC .5937; a 576-episode, 4-arm VOI experiment: inconclusive; 30-method tournament ending keep greedy; decision-state autopsy with no admitted signal. These are **author-reported** unless independently mapped to local artifacts. Their dates/scopes precede R6 and do not independently replicate R6 confirmation.

Useful ideas:

- Section E/RQ1 proposes feedback-reweighted score n02, Section F/RQ2 feedback-adaptive asking n03, RQ4 scarcity-guarded waiting n04. They explicitly remain proposed.
- Page 8 reports VOI questions frequently changed allocation, but reward did not follow. R7 must separate decision change from terminal improvement.
- The authors gate global matching on value-aligned weights; the prior graph variant changed 36/36 worlds with zero MSMI difference. A1's own-parent test follows that caution.
- They use public feedback/ask log and bounded memory, but the historical claim that tournament policies ignored history must be scoped to that record; it cannot override later R4–R6 mechanisms.

Corrections/adaptations: 'maximum-value greedy' does not make an exact global optimizer; within-day rank changes matter only if pairs actually change. Answers on late asks are immediate; value can expire due to a lack of remaining decisions, not late answer arrival. Budget slack over 60 days does not remove day-specific complementarity; idle units cannot carry to tomorrow. Arrival pressure must use arrival observations, not net availability alone. The approximate +.187 offline bound cannot forecast live gain.

## Supplied Research_Approach.pdf: coherent architecture, untested integration

12 pages, 'Better Questions. Better Matches.', dated 9 October 2026. This is a proposal with explicitly no empirical performance claim. Primary core: exact feasibility, conditional MSMI funnel, allocation-aware VOI, and general-graph maximum-weight matching; optional exploration, recency adaptation, and strategic waiting. Page 6 shows approximate VOI as expected post-answer optimal matching value minus current value; page 7 uses general-graph Edmonds-style matching, without an assumed bipartition; page 8: bounded fallback/deadline architecture; page 9: maturity/censoring; pages 10–11: paired all-official-baseline comparisons and ablation ladder.

R7 adopts: controller-consistent joint-batch VOI (Q2/D2), conditional terminal targets with direct composite comparator (L1), reward matching with cardinality control (A1), time-safe exports, complete policy rollouts, separate core/optional ablation and offline fallback validation. Source papers motivate components; no competitive/regret approximation ratio transfers automatically to this two-endpoint general-graph market.

Differences from the other proposal: this report treats maximum-weight matching as primary, while the 15-page proposal starts with greedy/local repair and gates exact optimization. R7 keeps these as distinct controllers and tests its own parents rather than claiming the two team reports agree on one fixed algorithm. Optional modules default off and need a new registered entry, not post-hoc tuning.

## Priority conclusion

Lead with legal whole-action continuation and matching-consistent acquisition; test public reusable-actor history as a gated second mechanism; use lightweight query/allocation controls to locate objective alignment. Keep fits small, cap search, test toy predictions independently, quantify real opportunity frequency and require untouched multi-baseline confirmation. Neither team report nor R6 proves R7 will win. Their contribution is a more precise hypothesis, stronger failure tests and less repeated search.
