# Independent exact-model and renewal-theory review

Reviewer `/root/critic`, Sol high; named reviewer director. Date 11 October 2026. Exclusive file: this review. CPU ceiling 300 seconds shared with freshness review. Read-only proof/source/result checks and independent rational arithmetic; no simulator worlds, policy episodes, fitting or source edits. Developer `/root/exact` is separate from this reviewer.

**Verdict:** accept the final v2 exact reduced-model results and the stated conditional ideal-stream occupancy relaxation theorem within their explicit scopes. Independently close the separate reduced-model enumerator/value and rational-certificate checks. No full-simulator numerical bound, calibrated public controller or empirical reward improvement is supplied by this package, and none is approved here.

## Final sources and preserved v1 provenance

Final reviewed attempt: `results/research6/stage_a_exact_v2/20261011T042343.113219Z`. Its registration SHA is `627368194ceb5cd52c9d9ff499d8791dfa72765a22361cb9b2e452f6626c1095`; specifications SHA `68185d4f437e5e4746cee4a84e2641c01ea8a08a4cba6520f58c83303563e717`. Independently verified all six registered source files against both the attempt's saved source snapshot and current source bytes, including THEORY.md, tests, run, solver and specifications. All four saved artifact size/hash entries agree. These are byte-consistency checks, not authenticated historical timestamps.

The original v1 attempt `results/research6/stage_a_exact/20261011T041946.639650Z` remains intact. Its current run.py initially differed from its registered source. The four files recovered under `research6/exact/history/v1/` each match the original registration exactly; this closes original-source attribution without editing the v1 registration or pretending the later executable generated it. V2 adds actual rational evaluation of the adaptive-conditioning tables and snapshots all sources before solving. V2 model JSON is byte-identical to v1; v2 solutions JSON adds the explicit checked table. Scientific result scope is unchanged.

Final proof hash: `research6/exact/THEORY.md` = `cf62f463b88a39e88ce20d5f70d893747053bd0799253c7aa42072ca073394d6`; final run.py hash = `184c0d74998b0e77a98322615e64e30df380ff9abe8418b49f7b709f266390c4`. A later source change requires its own amendment/review; this verdict is attached to these bytes.

## Independent numerical and action-menu reconstruction

Used inline standard-library JSON/Fraction/recursive enumeration code, without importing any developer solver, compiler, statistics or model-generation functions. These checks read the saved reduced models only:

- All 102 models (23 named and 79 constructed sweeps): independently reconstructed 2,231 state values, 1,512 action values and every optimal-action tie set using rational recursive expected-value evaluation. Every saved value/action set matches. Independently checked positive transition probabilities, exact mass one and increasing ranks/acyclicity.
- All 98 matching models: a separately written vertex-first matching enumerator reconstructs each legal action menu from the source specification/current busy, retired, past, arrival/exit and action-day state. Independently reconstructs all 1,491 matching-action transition distributions, retirement flags, release vectors, permanent no-repeat history and assignment-booked reward. Every saved menu/transition matches. This corroborates the compiler as well as the value solver; it is not merely the developer's alternate policy evaluator run twice.
- Three exact rational LPs: independently checked nonnegative primal/dual witnesses, every primal capacity inequality, every dual dominance inequality and equal objectives. Triangle degree relaxation 3/2, triangle with odd-set row 1, and two-day renewal 3/4 all certify exactly those toy LPs. The last agrees with its exact dynamic model.
- V2 adaptive table: independently recomputed x_first=1/2, prior occupancy u=1/2, actual selected occupancy zero before the always-legal second assignment. Averaged-prior capacity is 5/4 while actual expected capacity is 1. Reward selection independently gives actual expectation 1/2 versus prior-q-times-x 1/4. The saved v2 table and runner algebra agree.

These establish every reduced Bellman action value and supplied certificate within the saved models. They do not claim exhaustive enumeration of all deterministic policies of large models after the developer's cap, statistical independence of constructed cases, or faithful replacement of the full simulator's observation/timing process.

## Adversarial review of the model assumptions and findings

The toy matching controller knows all edge/calendar probabilities and observes joint retirement by the next toy decision. That is explicitly different from simulator partial hard truth, hidden exits and delayed stage feedback. Booking q once at assignment is correct for expected additive reward even when reward/retirement are coupled, because there is no latent parameter learned from the otherwise integrated reward in this model. The model permits coupling reward as a subset of retirement with q<=p; it never substitutes q for p in occupancy. Simultaneous independent retirement draws and full reward follow-up are toy assumptions, not measured production facts.

The structural examples correctly distinguish:

- Cardinality repair can help a four-node trap, but a high-quality middle edge can reverse the preference.
- Two-bundle verification has complementarity, and collision-aware matching value can reverse degree-sum ranking.
- Reservations depend on future alternatives; independent endpoint loss terms double-count one shared alternative.
- Final-day disjoint addition has no future occupancy penalty with full follow-up, but does not expose a missing edge in already maximal shipped G.
- Qualification and permanent pause differ, so a q-based occupancy penalty can be wrong even when immediate expected reward is modeled correctly.

**The learning qualification is necessary and correct.** In `no_return_can_still_have_learning`, an earlier disjoint pair never returns and earns no reward but reveals a shared regime. Correct subsequent choice raises future expected reward from 1/2 to 1. Thus no endpoint return does not imply no learning value. Zero decision value requires that no later feasible action/expected utility can change with that observation (or no affected decision remains). This is an exact information-experiment counterexample; it neither proves that such a fully revealing event exists in the simulator nor provides a practically useful regime learner. It does bar using “no returns” alone to reject every global/shared-regime learning proposal.

## Occupancy proof: accepted conditional scope

Fix full latent environment Z: member/profile/actor/regime quantities and actual arrival/exit schedules. Under the explicitly assumed fresh independent potential dyad/day streams and policy nonanticipation, the assignment indicator X(e,t) is measurable before its own stream. Therefore conditional on Z,

`E[X U | Z] = E[X | Z] E[U | Z]`, and likewise for eventual reward R.

Pathwise nonoverlap of assignment-caused endpoint occupancy plus dyad nonrepeat supplies the capacity/nonrepeat inequalities. The required no-gap condition includes busy time followed by a permanent pause before release; the public simulator timing facts support that interval shape (failed release t+8, mutual date release D+6, second feedback by D+5). Intervals can continue after exit without admitting later actions, while already assigned rewards still mature. Finite linearity then maps any legal adapted policy to a feasible LP point with the same expected reward. Removing disclosure/query limits and using full hard truth makes a relaxation. Any dropped dyad must be impossible; ignoring declines is safe and looser.

Adaptive feedback does not invalidate this **conditional** argument, because all fixed latent quantities are in Z and each selected assignment's own stream is fresh before selection. But posterior/population-average coefficients do not factor under history-selected assignments. The explicit short/long and reward-type tables correctly refute that substitution. Integration gives `E[reward] <= E[LP*(Z)]`, not generally an LP at mean q/u. A valid deployable public-belief relaxation would need history-indexed coefficients/variables or proved envelopes.

The stated numerical direction is also correct: upper-enclose reward q and lower-enclose occupancy u, then provide a feasible nonnegative dual satisfying `A_minus^T y >= q_plus` with outward-controlled/exact residuals. Upper occupancy coefficients could exclude a legal schedule and invalidate a bound. Quadrature convergence is not an enclosure, and a floating solver objective is not a certificate.

Strongest remaining limitation: the seeded finite PRNG is not proved to be a collection of mathematically independent ideal streams. The theorem explicitly uses that ideal-model assumption; fixed-seed realized reward need not lie below an expectation bound. Full-simulator q/u integrations, continuous-latent enclosure errors and dual certificates remain unimplemented. Never report the three toy certificates or a privileged heuristic null as a certified full-simulator headroom ceiling.

## Ongoing A/N3 adversarial watch

The public A subtask is complete and independently reconciled as stated in freshness_review.md; it remains examined G-visited state opportunity evidence. It does not complete all Stage A or bypass actual-reward gates.

Read `audits/A_mechanism_design.md` N3 handoff v1. Its fixed-k query count, source-conditioned hard values, shared per-actor samples across incident edges/batches, FIFO incumbent, identical actual shipped G allocator and no soft changes make the comparison scientifically identifiable at the specification level. Source deductions on a still-incomplete nondeclined actor having no prior legal introduction, uniform ordinary-zone extension, value-independent missingness, False handling and public sparse zone support agree with kit.py under the stated ideal source distribution. Unsupported support must trigger recorded legal fallback rather than silently borrowing a hidden family label.

Concrete concerns to settle prospectively in its implementation/A registration:

1. **Optimization bias:** choosing the best of <=71 batches on the same 32 particles guarantees a nonnegative modeled count difference against the included FIFO incumbent. A strictly positive optimized modeled difference is activity evidence, not independent predictive validation. Use separately registered independent public-model evaluation particles for the selected batch versus FIFO to diagnose winner's curse; keep those separate from the frozen deployed selection particles, and do not retune on a favorable evaluation. Actual B/C reward remains primary regardless.
2. **Exact objective/ties:** specify the maximizing count/score objective and FIFO incumbent preference followed by a deterministic minimum public-index tie rule. “Lexicographically maximal objective” with an index tuple can otherwise invert FIFO order. Freeze behavior for k<4, shortlist size<k, duplicated FIFO/shortlist actors and equal-sample two-query-plus-FIFO filler controls. All batches still have exactly k legal distinct bundles.
3. **Support metric:** freeze whether two-bundle/collision incidence means partial-compatible potential relations, sampled feasible relations, or actual disclosed future edges, and their denominators. Label modeled versus observed incidence separately. The proposed >=1%/three-of-four-seeds gate is an engineering support rule on this examined cohort, not a probability bound or simulator reward guarantee.
4. **Work limits:** 32*71*19,900 is about 45 million full edge visits before eligibility/detail overhead. A cap is not evidence of latency. Benchmark the complete masked-graph evaluator, test literal-hypothetical-G equivalence and dense full work, and freeze any 16-particle/6-shortlist revision before examining its support/reward data. Partial enumeration due to a clock guard is a fallback, not the configured algorithm; every fallback remains counted/promotion-ineligible.
5. **Contribution scope:** optimizing four bundles can help merely through a better shortlist/priority or sampled tie fluctuation. C must retain equal budget, equal samples, same shortlist/scorer/timing and the two-query+filler/unchanged FIFO controls. This is a bounded joint enumeration extension of previously studied matching-value acquisition, not first discovery of collision-aware querying.

These concerns allow a bounded medium implementation and independent constructed tests now; they do not approve N3 admission or require fresh simulator worlds to test the sampler/objective. Further N4–N7/L1/L2 evidence remains required rather than being inferred absent from current allocation graphs.

Final independent conclusion: accepted exact reduced benchmarks and conditional symbolic theorem, with matched final v2 sources. Remaining simulator numerical-bound, learning support, actual policy advantage and production claims are separate unfulfilled research obligations.
