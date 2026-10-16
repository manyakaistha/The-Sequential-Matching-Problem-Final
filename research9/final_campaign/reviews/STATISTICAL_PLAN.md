# Final bounded campaign — statistical contract recommendation

2026-10-15; author `/root/continuation_critic`, reviewer `/root`. Design only:
no fitting, extraction or simulation in this work order. This is the final
bounded attempt to improve Greedy; no win is guaranteed and failure ends it.

## Ordered stages and budgets

1. Preserve completed research and freeze this plan, feature/label schema,
   split commitments, portfolio, selection rule and endpoint implementation
   before new fitting/outcomes. All old96 seed groups remain development data.
   Deterministic hash order gives64 training,16 validation,16 development-test
   groups. Keep every family, arm, actor history and repeated introduction from
   a seed together. No split search. Existing aggregate inspection means the
   development-test split is not fresh confirmation.
2. Extract only audited public assignment-time records using streaming,
   one-cell-at-a-time archive reading and verified content identities. Fit one
   prespecified compact terminal/stage candidate using training groups only.
   No tuning sweep. Validation chooses admission, not a collection of winners.
   Use released mature labels, exact qualified date<=30 and both second
   intentions<=3, and censor unreleased outcomes rather than call them failures.
   Do not backfill future questionnaire values or future actor history.
3. Freeze at most four policies: C1 model-score greedy with unchanged Q6 asks;
   C2 C1 plus one fixed slack-soft batch rule; C3 C2 plus bounded fixed-score
   local repair; C4 continuation only if separately admitted joint reward/return,
   public-belief, boundary and tail gates already pass. Otherwise omit C4; do
   not invent its model to fill a slot. Keep no-continuation own parents.
4. Freeze eight validation seed groups by hash before fitting. Screen exactly
   8 groups×6 families×(admitted candidates+G/Q6/P), at most336 cells. Worlds
   are reused deliberately. Public policy inputs must never include host seed,
   family, arm identity, private world data or future calendars. Selection:
   highest mean paired qualified MSMI/100 advantage over G; ties within1e-12
   favor earlier C1/C2/C3/C4 order. Admit only a positive observed advantage,
   valid complete cells, no fallback and all implementation/model gates.
   Require no negative observed mean versus Q6/P as a conservative selection
   safeguard, not evidence of superiority. No extra seed or variant if none
   qualifies. Screen statistics are descriptive and selection-biased.
5. Evaluate the frozen selected model once on16 development-test groups for
   prediction only. Do not repair it after seeing those scores. Failure of the
   same prediction gate ends this campaign with no final contender. Do not add
   another policy screen or winner replacement. Freeze source/assets/configs,
   one selected policy and final analysis before final-seed outcome access.
6. Final: exactly96 fresh seed groups×6 families×selected/G/Q6/P=2,304 cells.
   At most7 cell workers globally; combined monitored worker-tree RSS<=8GiB;
   evidence budget15GiB with reserved overlap/audit transients. Full public
   captures, failed attempts and independent archive-aware audits are retained.
   Capacity failure stops dispatch and drains; it does not delete evidence.
   Earlier stages may stop for fixed invalidity/resource gates or no contender;
   final reward never changes the sample size. No optional stopping, sample
   extension, changed salts, threshold search or second final candidate.

## Prediction admission

IDs serve opaque within-episode history lookup only. Seed/family/arm are not
features. Features use assignment-time public values, explicit observed/declined/
not-asked masks and already released mature history. Response-stage marginals
must not be multiplied as independent endpoint probabilities; dyad conditional
stages and terminal calibration are checked explicitly. Public hard eligibility
remains exact and independent of imputed/learned scores.

Controls are training-only constant qualified probability and **a training-only
fixed-penalty logistic intercept+slope calibration of observed agreement count**.
The integer0..7 count is never itself used as a probability/log-loss input. If
P's expected-agreement surrogate is included, calibrate it likewise using
training only. Freeze penalty, feature scaling and clipping (e.g.1e-6) before
fitting; apply identical evaluation clipping to every control/model. Never fit
calibration on validation or test labels.

Require at least50 positive terminal training labels and20 each in validation
and development-test; otherwise no terminal-model claim or sample expansion.
For each held-out split require lower seed-weighted terminal log loss than both
controls and95% seed-bootstrap upper bounds of candidate-minus-control losses
below zero (one fixed bootstrap recipe). Also report Brier score, calibration
mean error (gate<=.01), a fixed five-bin reliability table with event counts,
and stage support/censoring. A log-loss win alone does not certify calibration
on unintroduced edges, a joint return model or policy value. Equal seed weights
and equal family/arm weights within seed prevent high-volume worlds dominating.

## Freshness and final inference

Review proposed final seeds against all seed-bearing registrations, reservations,
inventories and commits, including archived catalogs. A complete, hash-bound
index/proof that explicitly covers historical compressed scope can replace a
four-million-file scan. Document excluded/missing scope and reject freshness if
it cannot be resolved. A name-only search or omission of all results is
insufficient. Reserve final seeds before running; policy developers cannot use
final outcomes. Infrastructure preflight uses declared fixtures or development
worlds. Do not relabel any old seed fresh.

Primary endpoint: qualified introduction count×100/arrived-by59 members, full
released feedback through99. For each seed average the six family-specific
candidate-minus-control differences; **96**, not576 or2,304, is the inference
sample size. Report means, seed SD/SE, paired wins/ties/losses, two-sided95%
intervals and fixed one-sided superiority tests; no family/outlier exclusions.

Recommend a fixed hierarchical familywise-alpha.05 sequence: first C−G>0;
only if it rejects test C−Q6>0; only if that rejects test C−P>0. Each uses a
one-sided paired seed t-test at.05 and its corresponding95% lower bound. Stop
formal claims at the first failed gate; later contrasts remain descriptive.
Thus a Greedy win is a Greedy claim; a strongest-panel claim requires all three.
Predeclare this sequence rather than switch to Holm after outcomes. Handle zero
SD/degeneracy explicitly; do not fabricate infinite significance. Complete-grid
independent endpoint/statistics reconstruction must precede any final claim.

## What96 groups can resolve

Old audited contrasts supply planning assumptions, not a guarantee for new C.
Targeted/random soft versus G had seed SD.1581/.1533 MSMI/100. At n96, SE is
.01613/.01564; a true+.05 effect has approximate one-sided.05 normal power
93%/94%, and80%-power effects are about.040/.039. Contrasts versus Q6/P had
SD around.254–.283: power for+.05 falls to roughly61%–53% and80%-power effects
rise to.064–.072. Hierarchical later gates can only reduce joint panel power.
These approximations omit SD estimation and nonnormality; a new policy can have
larger variance. A null final result is inconclusive for smaller effects and
must not trigger expansion. No claim that this campaign closes every research,
production or mathematical gap is authorized.
