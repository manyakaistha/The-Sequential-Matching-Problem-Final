# Independent deadline-invariance and diagnostic review

10 October2026. Owner: statistician/adversarial critic; reviewer: director.
Read frozen simulator/candidate/wrapper code, DEADLINE_INVARIANCE, deadline_audit,
raw intervention/public-trace results, bootstrap supplement and execution note.
No new simulator world or episode was run. Independent trace/count/statistical
checks consumed approximately8CPUseconds, within the30-second allowance.

## Verdict and corrected conditioning scope

Accept the deterministic **normal inner-decision** theorem for all eight frozen
configs. Changing second delays within1–5 cannot change availability: before
D+6 the endpoints are busy regardless of whether a pause has arrived; at D+6
all second labels and any positive pause are already observed. Query modules
use current available profiles, partial feasibility and past dyads, not pooled
second-feedback counts/timestamps. Greedy/population weights ignore seconds;
Beta/Uniform response counts for legal-edge endpoints are complete at release.
Acceptance posteriors use introduction response labels, assignment day and then-
public profiles, unaffected by second timing. Computing histories for unavailable
actors does not change the available actors' scored histories. Thus induction
preserves ask actions/disclosures, pair/day assignments and nonintervened draws.

I challenged the initial phrase “delay-erased trajectory”: deleting timestamps
from an observation sequence can still retain event presence/absence by day,
which reveals second delays. Developer corrected the definition to the sigma-
field of all non-second-feedback-delay primitive variables and independent
policy randomness. Under ideal independent draws, actions and K are functions
of that core; second feedback delays remain independent uniform1–5 draws.
For K both-positive pairs with date−assignment<=30, each qualified indicator
has conditional probability.36. Therefore the semantic-policy conditional
expected score is100*.36*K/N, at N200=.18K. Date delays/qualification, cancellation,
actor responses/preferences and occupancy are **not** integrated away.

The second correction concerns executable guards. Merely observing zero fallback
on the actual trajectory does not prove exact guarded-executable integration:
request size/latency failures could depend on counterfactual delays. An exact
executable extension requires its normal path for every relevant delay assignment
at fixed core, not conditioning on observed no-failure. The revised document
states this and declines an unconditional guarded-executable estimator claim.
Finite fast/slow tests do not establish all counterfactual resource success.
This preserves the exact semantic theorem while keeping production scope honest.

No theorem extends to global-feedback learners, time-sensitive pending queries,
D+2 releases, pauses delayed beyond release, R-dependent delay laws, correlated
feedback-delay/core priors or finite deterministic PRNG independence. Response
and yes/no flags being unchanged is essential. The subclass mutates timestamps
after all original draws, rather than reassigning PRNG delays in a way that could
change subsequent random draws. Full100-day follow-up contains all supported
events; late truncation would invalidate the labels/identity.

## Independent verification of artifacts

For all16 extreme-lag interventions on already examined101development, directly
compared stored fast and slow ordered actions, availability lists and introduction
lists; all agree, all fallback counts are zero, fast qualified=K, slow qualified=0.
I additionally compared both extreme actions/introduction lists to the existing
unmodified smoke trace for each of the eight policies: all agree exactly. No
extra normal simulator replay was needed. This verifies finite interventions,
not a universal guard guarantee or a deployable changed-delay policy.

Independently reconstructed K and qualified counts from all576 original B public
traces, including zero-event episodes. Both-positive second flags agree with
pause events; qualification matches official episode totals; arrived denominators
and all actual/proxy means match to1e−12. Recomputed all13 deadline-proxy paired
Student-t intervals from six-family means within each seed: exact agreement.
All39 supplementary bootstrap means/intervals also match using10,000whole-seed
resamples/RNG90210. These are independent analysis of existing data, not new
independent reward evidence. No hidden truth was read; future completed public
events are used only as offline outcome labels.

## What the screen decomposition supports

| Policy vs greedy | Actual effect | Deadline-integrated proxy effect | Actual−proxy difference |
|---|---:|---:|---:|
| hard_priority | +.201389 | +.040000 | +.161389 |
| population_control | +.194444 | +.055000 | +.139444 |
| goal_surplus_control | +.194444 | +.042500 | +.151944 |
| coordinated_goal | +.090278 | −.017500 | +.107778 |

Hard-priority proxy CI[−.063235,+.143235], population[−.032096,+.142096], and
coordinated[−.110333,+.075333] include zero. Thus their B qualified-reward headlines
include a large favorable realized feedback-deadline residual; strong underlying
positive/date-qualified opportunity gains are not established by this screen.
This is a valid algebraic decomposition and scoped model-based noise diagnostic,
not proof that a particular ranking/occupancy mechanism causally explains reward.
Changed pair/day streams and endogenous future states remain relevant.

Beta's proxy+.090000 has an unadjusted positive interval, but it was searched on
these same12clusters. It cannot replace the registered primary, promotion or
selected candidate. Uniform−Beta proxy−.002500 and acceptance−Uniform−.032500
provide no supported positive incremental mechanism. Their posterior correctness
and calibration must remain separate from reward. The conditional integration
idea resembles standard conditional-expectation variance reduction; no broad
novelty or statistically superior policy follows automatically.

No assignment-independent standard errors or post hoc proxy-based promotion are
acceptable. Preserve the actual qualified score for C/D/E and both nominal and
program-wide confirmation gates. A future primary variance-reduction endpoint
would require prospective definition, exact executable/semantic scope and its
own statistical plan before evaluation.

## Provenance review

The raw audit was executed from an initially imported source version while a
host-only bootstrap block was edited on disk. Its final disk-source hash therefore
did not identify the imported version. This is a real provenance error, not an
inference-source change. The execution note preserves the raw artifact, reports
the discrepancy, and labels reconstructed source SHA rather than pretending it
was captured before launch. I requested the complete executed source snapshot;
it now exists at audit_snapshots/deadline_audit_screen_executed.py and its digest
matches the declared reconstruction. The bootstrap supplement separately hashes
the unchanged raw artifact. Independently verified original points/t intervals
and supplementary bootstraps are unaffected.

Accept the corrected, transparently reconstructed provenance for this diagnostic.
Do not claim the original hash capture was accurate, and keep running analysis
scripts unchanged in subsequent executions. Final manifest should include the
raw result, correction note, reconstructed executed source and supplement.
Frozen simulator/policy/configuration hashes remain untouched.

## Decision

Approve this as a scoped mathematical result plus independently checked negative/
noise mechanism evidence. All requested conditioning/guard/provenance corrections
are resolved. It does not defeat greedy, justify retuning/promoting unselected
policies, replace qualified reward, establish a causal allocation advantage or
prove PRNG independence. Continue the already registered frozen stages.
