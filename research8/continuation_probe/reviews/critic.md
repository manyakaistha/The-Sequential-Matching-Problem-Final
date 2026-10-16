# Independent continuation critic — initial admission review

Reviewer: `/root/continuation_critic`; integrating reviewer: `/root`.
Date: 2026-10-15. Exclusive ownership: this new file. Read-only source audit;
no episodes, fits, seed selection, browsing or changes to prior research.
Allowance: at most 120 CPU seconds / eight minutes. Work performed: bounded
source inspection and analytic counterexamples; no simulation CPU used.

## Disposition

Admit a narrowly declared **Q6-parent holding heuristic for exploratory
mechanism screening** after the conditions below. Do not call it a calibrated
D1 controller, a reward improvement, or a consequence of the completed
soft-query null. The latter result was supplied by the director and was not
independently reconstructed in this work order. A negative holding result is
an acceptable outcome; there is no source deduction that waiting must help.

A full joint probability model is necessary to claim accurate expected
continuation values. It is not necessary to test one frozen, explicitly
heuristic public holding rule directly against its unchanged parent. This
distinction avoids turning an inexpensive falsification into unauthorized
fitting or an unjustified probability claim.

## Source facts and strongest objections

1. **Q6 has no special matching rule.** The frozen adapter maps Q6 to N3_two
   (`research7b/workspace/research7/policies/references.py:15–18`). That policy
   changes hard-query selection, while its match phase calls the shipped
   baseline (`research6/policies/allocation.py:115–121`; acquisition.py:196–197).
   Its matching score counts all seven equal observed soft values
   (`kit.py:213–221`), rather than estimating qualified reward. A score of zero
   means no observed soft agreement; it is not proof of a bad edge. Unknown
   attributes and observed disagreements must remain separate diagnostics.

2. **Every introduction consumes a substantial opportunity even when it fails,
   but also creates a nonnegative chance of reward.** Both actors are busy until
   assignment+8 regardless of first responses (`kit.py:157–168`). Mutual first
   acceptance extends both busy clocks to date+6, even if the date does not
   happen (`169–176`). An early public rejection does not release either actor
   early. Holding saves this occupancy only by foregoing the current attempt;
   the net value depends on alternative unused partners, query completion,
   returns, arrival supply and remaining action days. Counting saved actor-days
   or fewer low-score assignments as success ignores the lost opportunity.

3. **Pause is not qualified reward.** Pause follows two affirmative second
   responses, irrespective of their timeliness (`kit.py:177–188`). MSMI requires
   a happened date within 30 days of assignment and each affirmative second
   response within three days of that date (`190–197`). Delayed dates and late
   positive responses can absorb actors without reward. First acceptance,
   date, pause rate and coverage are secondary mechanism diagnostics. The
   governing public endpoint implementation also requires released events by
   day99 and counts arrived-by59 members (`soft_query_followup/v2/metrics.py`).

4. **The busy/paused/exit explanation is hidden.** Public observation exposes
   arrived_day, current available, introductions, released feedback and query
   history, but omits exit_day, busy clocks and future arrivals
   (`kit.py:97–111`). Unavailability alone is not a pause or departure.
   Source-exact new-introduction clocks are shared across the two endpoints;
   arbitrary independently returning endpoints are a richer toy assumption.
   No pending or future actor may become a supposedly known alternative just
   because the trusted host can inspect the world.

5. **Holding can only reschedule a dyad, not repeat an executed one.** Every
   introduced dyad is permanently past (`kit.py:150–153`); waiting does not add
   it to past. Holding can preserve an unused option, but it may lose other
   opportunities before actor exit or day60. In a fixed two-actor opportunity
   with no useful new information or supply, waiting adds no substantive
   mechanism. With a last-chance edge before an unknown exit it can be harmful.
   Construction of a better future alternative proves possibility, not its
   frequency in the target population.

6. **Final-day reward is eventual.** Day59 introductions receive full eventual
   qualified reward with follow-up through day99. A continuation policy must
   not subtract occupancy after the final action day, require completion by
   day59, or count pending reward twice. Under a deletion-only heuristic,
   day59 should reproduce the complete Q6 parent, including zero-score edges.
   This is a parent safeguard, not a proof Q6 is statically optimal.

7. **Short truncation already has a known failure.** W2's accepted engine is a
   declared 4–8 actor reduced model, with no complete simulator feedback,
   unknown-exit or query process. Its independent review records a day13
   alternative worth .9 against an immediate .5: H12 chooses now and incurs
   .4 full-horizon regret (`research8/w2/review.md`, separately closed tail
   diagnostic). Do not advertise an H12 estimate as certified continuation
   value, omit open neighbors, or interpret the earlier G-fallback timing as
   active full-population planning performance. This matters if this probe
   later imports W2; a model-free heuristic need not pretend to use that engine.

8. **Paired worlds do not hold edge outcomes fixed across assignment days.**
   Introduction randomness is keyed by seed, dyad and day (`kit.py:154`). A
   held edge introduced tomorrow receives different stochastic draws. A paired
   world-level comparison is still useful, but an individual observed reward
   difference is not proof of a specific saved-opportunity causal story.
   Family and timing diagnostics must remain descriptive; never search salts,
   days or thresholds until a favorable reroll appears.

## Cheap discriminating checks before a reward screen

These are proposed checks, not executed results.

- **Exact control and deadline checks:** ask responses match Q6 on identical
  public states; a disabled hold gate exactly matches Q6; day59 matches Q6;
  no legal held edge is entered as past; unchanged outside pairs remain in the
  full action; permanent decline/unknown hard fields never become eligible.
  Fail closed to the whole validated parent on malformed states or work caps.
- **No-opportunity negative witness:** a currently legal low-observed-score
  isolated pair and no declared future opportunities should not be presented
  as a demonstrated holding benefit. Include a last-chance/near-horizon witness
  to expose indiscriminate deletion. A bounded maximum hold duration or a
  frozen release rule is needed to prevent indefinite deferral of the same
  pair when its public score never changes.
- **Occupancy counterexample:** an introduction with an early no is unavailable
  through day7 and can return day8; a failed date stays busy through date+5;
  late-positive pause can be unqualified. A model that frees actors at the no
  response or equates every pause with reward fails the source-fidelity gate.
- **Opportunity witness:** a held endpoint gains a publicly realizable, unused,
  hard-verified alternative after query completion or return, and the candidate
  actually uses it. Record the original parent edge, holding trigger, subsequent
  legal action and countervailing lost opportunities. Hypothetical hard answers
  may estimate an opportunity but never authorize the real introduction.
- **Mechanism inventory before breadth:** count eligible parent decisions,
  trigger days, affected dyads/endpoints, complete-action disagreements, hold
  duration, reintroduced versus never-introduced held dyads, replacement edges,
  information gained during hold and remaining horizon. Use all examined states
  as the denominator. Zero/very rare firing closes the feasibility question;
  do not add thresholds merely to manufacture a larger effect.

## Required screen contract and scope

1. Freeze one public heuristic, its constants, time/release rule, source/config
   hashes and parent identity before new outcomes. State plainly whether it
   drops edges only or reruns matching after deletions. Rerunning can introduce
   new pairs and is a distinct allocation mechanism. If the contract says the
   candidate is a subset of Q6, verify that exact invariant.
2. Keep unchanged Q6 asks as the own-parent control and preserve explicit
   fallback telemetry. Actions will change future public states, so asks need
   not remain equal across diverged trajectories; equality is required on
   identical requests. Do not silently add soft queries, history fitting,
   population ranking, threshold sweeps or a new future-arrival prior.
3. Use a bounded, registered development comparison with fixed complete cells
   and seed-group analysis. The primary effect is qualified MSMI/100 arrived,
   not acceptance or reward per introduction. Keep shared seed/family clusters,
   complete outcomes and uncertainty. If several gates/arms are searched,
   account for that search; a winner is exploratory, not fresh confirmation.
4. Register the null/no-promotion outcome, resource/invalidity stop rules and
   action-disagreement reporting. Seven cell workers globally and combined
   monitored worker-tree RSS <=8GiB are ceilings, not a requirement to run seven.
   No reward stop or sample extension to obtain significance.
5. Preserve all original studies and seed-bearing provenance. New development
   seeds require a review against registrations, inventories and commits,
   including archived evidence catalogs; do not relabel old worlds fresh.
   If new evidence is archived, use the existing quiescent attempt wrapper and
   independent archive-aware audit rather than inventing reduced captures.
6. A launch requires the director's independent implementation/registration
   review. This source audit grants no authority to execute cells and does not
   close audit, endpoint, storage or runtime gates. Any later favorable result
   must survive unchanged-parent comparisons and an honest account of failed
   families, sparse firing and uncertainty. A null result should close this
   frozen rule without claiming all continuation mechanisms are impossible.

The critic remains available for the bounded implementation and registration
review. No source or prior result was modified by this review.

## Proposed one-day return-trigger refinement (source challenge only)

Forensics proposed a narrower rule during this review: retain Q6 asks, remove
at most one G edge ab before day59 when a currently unavailable hard-verified
c has a publicly failed first-response introduction whose assignment+8 is
exactly tomorrow, unused feasible ac has a strictly higher observed soft count,
and each withheld endpoint has not previously been held this episode. Resume
ordinary G next day without forcing ac. This is a defensible bounded hypothesis,
not a probability model or a guarantee that c returns or ac is chosen.

Additional admission details for that rule:

- Bind the released no/no_response to c's **latest** public introduction;
  verify actual released timing and explicit no_response missingness. An old
  failed introduction does not explain a current busy period. Reject a public
  pause for c; c must be distinct from both held endpoints.
- Say "scheduled potential return" rather than "known availability tomorrow":
  exit_day remains hidden. Do not assume the generator's exit support or import
  source-private calendars to certify future survival.
- Freeze deterministic selection among several ab/ac witnesses. Freeze whether
  either endpoint may serve as a and how ties are resolved. Capture the witness
  in telemetry so it is auditable without changing the public policy interface.
- Validate episode-local memory so a held endpoint is charged once even if it
  is held with another partner later; no cross-world accumulator. Missing or
  inconsistent memory must have a declared parent-safe behavior. The hard cap
  prevents indefinite deferral but does not establish scientific benefit.
- Count all scheduled potential-return witnesses, selected deletions, actual
  next-day c availability, ac selected, other replacement selected, same ab
  later selected, and held endpoints never subsequently introduced. This
  distinguishes an occupancy mechanism from random rescheduling and attrition.

## Implementation and fixed 24-cell admission receipt

Reviewed 2026-10-15 after the separate developer's fixes. **Accepted for the
fixed mechanism smoke**, conditional on the separate runtime review, final
source freeze and subsequent independent evidence audit. This is permission
within the director's existing authorized scope, not a scientific promotion.
The director retains launch ownership. No episode was executed by this critic.

The actual frozen tie contract supersedes the earlier canonical-tie suggestion:
choose largest integer score gap, then parent matching index, endpoint position,
and public member order. A witness c that was previously withheld is also
excluded, while only the omitted pair's two endpoints are charged as held.
These are defensible conservative heuristic choices. SEMANTICS must describe
this same contract, rather than imply canonical IDs or an endpoint-only witness
eligibility cap. The role of public order is disclosed, not an invariance claim.

Two concrete review defects were corrected before admission:

1. no_response initially accepted any released no-response record. The final
   candidate requires response_deadline_day=assigned_day+7 and the no-response
   observation exactly on that deadline. A newly added early-release regression
   rejects the malformed witness.
2. The initial hold record lost the chosen endpoint a, retaining only the pair
   {a,b} and c. The final record persists held_endpoint and target_day=day+1,
   with memory validation. The actual witness-use diagnostic must test that
   exact {a,c} at the target day, rather than accept {b,c} as the intended edge.

Source reading confirms unchanged Q6 delegation, separate wrapper/parent memory,
one omitted existing parent pair at most per day, no added pair or forced future
matching, per-episode withheld-endpoint cap, latest nonmutual introduction
calendar, hard eligibility and unused ac, strict ordinal improvement, released
pause/date contradictions excluded, and no day59 holding. A frozen-parent
fallback raises and invalidates the experimental invocation rather than silently
changing the arm. The no-hold arm directly returns the unchanged Q6 response.
These guarantees apply to the source-valid public simulator requests and the
stated tests; arbitrary adversarial corrupted histories are not certified.

Independent validation used a 30 CPU-second guard, no sampled episodes:

- A constructed public graph used the **real Q6 adapter**, rather than a mocked
  parent. The control response exactly equaled Q6, the candidate deleted one
  edge while preserving its other pair, and the recorded a/c/target day agreed
  with the unique constructed witness. Ask calls matched real Q6 exactly.
  Day59 retained the full real parent matching.
- All eight developer policy tests independently passed in 0.006 seconds.
  An initial independent-fixture assertion assumed a unique witness while two
  equal witnesses existed; making the declared fixture unique resolved that
  test-construction error without a policy change.
- A separate guarded in-memory registration check validated the complete
  24-key Cartesian grid and current source manifest. Seven re-signed mutations
  (stage, active days, follow-up days, cutoff, seeds, analysis contract and grid
  truncation) were rejected. No registration file was written by this check.

Reviewed hashes:

- policy.py: `3dc881beb7f57834dd5dc40ec8d8bbcae2511ce8c9388768d33fc404d7791bce`
- registration.py: `5f351737a5d3607e580ab3e0f79af7c5e7d66703b4a5b946b2ae751c6cd82ed7`
- tests/test_policy.py: `5b719d4facde06031ff1d9eb232e603f8e085da5a556e2085f6ec7698c68e12e`

The design is deliberately two previously used development seeds (840001 and
840002), six fixed families, and unchanged Q6 versus Q6_return_hold: 24 cells.
It is a feasibility/mechanism smoke, not 24 fresh inferential samples. The
registration fixes 60 action days, 40 follow-up days, released cutoff99, exact
arms, source closure, original resource caps, complete-cell requirement and
analysis scope. The seed choice is deterministic rather than selected for
observed holding reward. All cells, including zero-trigger cells, remain in
reporting.

The registered null gate is appropriate: zero holding triggers or zero actual
intended replacement use closes this frozen rule for scaling. Passing that
gate establishes that the mechanism can act; it does **not** authorize reward
promotion or automatic larger replication. Reward, assignment/coverage loss,
conditional return failures and family diagnostics remain descriptive in this
two-seed reused-world study. No sample extension or threshold revision in
response to reward is admitted. Before claiming the gate passed, reconstruct
holds and exact next-day ac use from immutable public captures and perform all
24 independent endpoint/legality audits plus parent action/world parity with
prior Q6. Root owns that integration; runtime and storage review are separate.
