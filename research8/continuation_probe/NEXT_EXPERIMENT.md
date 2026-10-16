# Cheapest next reward-model gate

Design only, 2026-10-15; author `/root/continuation_critic`, reviewer `/root`.
Allowance: 60 CPU seconds/four minutes. No extraction, fitting, episodes or new
seed claims are authorized by this document.

The seven-field Q6 agreement count is ordinal. Before expensive D1, ask whether
one small public model predicts **qualified eventual MSMI at assignment** better
than a fixed population prior. Accurate first-response prediction alone is not
this gate. The existing audited 2,880 episodes are development data, including
all 96 seed groups, six families and five arms; this is not confirmation.

## Freeze before touching labels

1. Commit a deterministic seed-group split: 64 training, 16 validation, 16 final
   development-test groups, using a fixed hash ordering of the registered seed
   list. Every family, arm, actor history and repeated introduction from a seed
   stays together. Seed serves splitting/cluster accounting only; neither seed,
   family/variant, arm label, introduction ID nor actor ID enters predictors.
   IDs are opaque within-episode history lookup keys. No new cross-arm actor
   memory is constructed. Freeze one baseline, one candidate, metrics and gates;
   do not search splits until scores improve. Existing prior inspection of these
   outcomes limits even this held-out score to development validation.
2. Use immutable public request/action/feedback captures under the existing
   archive-aware bounded reader. Materialize at most one cell; preserve original
   identities. Audit source/registration/world binding before any proposed
   extraction. Select introduced edges only, with the exact post-query,
   pre-assignment public masks, values, available flags, calendar/horizon and
   released history. No final questionnaire backfill or private-world joins.
3. Freeze a compact feature allowlist: disclosed soft equality/missingness,
   public age difference, public hard-verified attributes, time since arrival,
   and per-actor counts of **already mature released** prior responses. Include
   observed/declined/not-asked masks; missing is not disagreement. Pending trials
   remain pending. No whole-episode eventual totals, future availability, true
   exits, decoded IDs or hidden day35/family shortcut.

## One small model, explicit stage limits

Fit fixed-penalty logistic models without a tuning sweep. Start with actor-level
first-response/no-response and affirmative-given-response models; evaluate both
endpoints with seed-cluster uncertainty. Compare against training-only constant
priors and an agreement-count control calibrated using a fixed-penalty logistic
intercept and slope fitted on training groups only. Raw scores0–7 are never
treated as probabilities in log loss. If a population-score control is included,
freeze it in advance and calibrate it on training groups by the same rule.
Actor trials from one introduction
are dependent; do not multiply marginal probabilities and call the result
calibrated mutual acceptance.

For assignment-time qualified probability, fit dyad stages: mutual first
acceptance; happened date within30 days conditional on mutual acceptance; both
positive second intentions within3 days conditional on a timely happened date.
All stage predictors use assignment-time features. Their probability product
uses conditional stages, not endpoint independence; held-out terminal calibration
must still pass. If conditional-stage support is sparse, retain its training-only
constant rather than add personalization. A separate future feedback-conditioned
return model is deferred; these models do not supply occupancy transitions.

Freeze maturity rules: first responses mature at assigned+7; timely-date outcome
at assigned+30; timely-second outcome at date+3, counting only released evidence.
Use day99 follow-up and coherent public event chronology. Unknown/unreleased
outcomes are censored, never negative. Late positive responses and unqualified
pauses do not satisfy MSMI. Report stage denominators, censored rows and positive
counts by split; require at least50 positive terminal training examples and20
in validation before any terminal-model claim. Failure closes this fixed gate;
no sample expansion to meet counts.

## Decision and next step

Use equal seed weighting, with equal family/arm weighting within seed, and
seed-block resampling. Report terminal log loss, Brier score, calibration mean
error and a fixed five-bin reliability table; stage scores are secondary.
Admit only if validation improves terminal log loss versus constant and
agreement-only controls, its95% seed-bootstrap upper difference versus the
constant is below zero, and absolute calibration mean error is<=.01. After
freezing, evaluate once on the development-test groups; failure closes the
candidate without test-driven repairs.

Prediction on chosen edges is not policy value. Logging is deterministic and
selective; unintroduced alternatives may lack support/positivity. Do not claim
an off-policy causal improvement, score every alternative as validated, or
promote D1 from these proper scores. A later frozen policy requires separate
prospective evaluation and explicit joint reward/return-law admission.

If the hold smoke has zero triggers/intended replacements, close that rule and
consider this independent prediction gate; do not tune it into activity. If
active, audit exact next-day witness use and losses, then retain it as an
exploratory mechanism only. Either outcome leaves current reused data unsuitable
for fresh confirmation; neither automatically launches fitting or a larger run.
