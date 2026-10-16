# Independent public model/data review

2026-10-15; reviewer `/root/continuation_critic`, integrating reviewer `/root`.
Scope: features.py, models.py, dataset.py, their constructed tests, split and
campaign-plan interface. Read-only code; no old archive extraction, research
fitting, policy episodes or held-out outcome inspection. Allowance120 CPU
seconds/six minutes; synthetic unit checks only.

## Disposition before fitting

**Accept features/dataset for the frozen public-development extraction and
bounded training stage.** No assignment-time leakage or qualified-label
mismatch was found in the reviewed implementation. Asset validation must be
closed before policy deployment; prediction admission and production readiness
are separate. This receipt does not certify fitted models, calibration,
training/validation weighting, policy value, freshness or final launch.

The split must be checked by the trainer for64/16/16 disjoint unique seeds,
complete membership of the original96 and no arm/family crossing. The reviewed
modules do not enforce that themselves. Likewise stage masks and balanced
weights are caller responsibilities; train conditional models only on their
risk sets, never on the explicit zero placeholders outside those masks.

## Verified source behavior

- Features are74 finite symmetric public columns. IDs only join already
  released actor feedback; no seed, family, arm, private propensity or ID value
  becomes a predictor. All soft-field values require observed status and an
  observation day no later than assignment. Missingness is distinct from
  known disagreement. Initial declined/None fields correctly count as declined
  without inventing an observation timestamp.
- History is linked to prior public introductions and actual endpoint actors,
  deduplicated, and filtered by observed_day<=current day. Same-day assignments,
  future feedback and unlinked actors are excluded. Date/pause dyad events do
  not become actor response rows. Per-observation context reuse is appropriate;
  do not cache a context across different same-day requests with changed public
  history merely because its day matches.
- These history features use **all released responses**, including a response
  released before its introduction deadline. That is legal public information;
  it is not a mature-trials-only cohort. The beta-style ratios are descriptive
  released-feedback summaries, not calibrated actor response propensities:
  pending trials are absent from their denominator. Amend earlier mature-only
  wording before fitting rather than silently claim that stronger restriction.
- Dataset rows come from the actual post-query match request in actions.jsonl,
  never reconstructed final questionnaires. Features and opaque join metadata
  are separate. The source record is sanitized; exact pair/day joins match
  final introductions. Both action digest and original member hashes are
  checked. The6000-row cap is the correct conservative200/2×60 bound, rather
  than mistaking120 phase records for assignment capacity.
- Final labels pass the independent public chronology checker, then require
  mutual first acceptance, a happened date within30 days, and two affirmative
  second intentions within3 days. Funnel masks separate mutual and timely-date
  risk sets. Label totals reconcile to independently reconstructed qualified
  counts and committed metrics. The reader is specifically for completed old
  day99 captures; it is not a general immature/censored collector. Later use on
  partial captures must implement censoring, not reuse these all-mature masks.
- Each archive is rebound to its commit, immutable catalog and checkpoint in
  the completed2880-cell audit proof. The reader validates declared coverage,
  paths, regular-file types, lengths, compressed identity, every decompressed
  member hash, missing/extra members and trailing bytes. It never extracts the
  whole archive to disk. Only actions/final public JSON are interpreted; other
  evidence is streamed through hashing. Cells are bounded512MiB; final JSON
  and action-line bounds are explicit. Derived NPZ is fsynced and published
  exclusively, without replacing source evidence.
- Logistic fits use train-only weighted standardization, a fixed L2 penalty,
  stable sigmoid/logistic loss, finite checked inputs and a declared smoothed
  constant for single-class data. Failed optimization raises. Weight balancing,
  two-family selection and predictive scoring remain trainer responsibilities.

## Concrete outstanding production issue

models.predict currently validates X but trusts asset intercept, coefficient,
mean and scale arrays. A constructed zero-scale asset returned NaN rather than
raising; malformed dimensions can also broadcast or fail incidentally. Before
policy deployment require finite scalar intercept; finite one-dimensional
coefficient/mean/scale arrays of equal length; strictly positive scales; expected
feature contract; finite returned probabilities. Freeze/hash validated assets.
Any clipping used for log loss must be identical across controls and candidates
and frozen before evaluation. A valid training output is not a blanket validator
for arbitrary loaded assets. This defect does not contaminate extraction or
well-formed training, but it blocks production-admission of the current predictor.

## Practical gate amendment, before outcomes

The final user goal is to test a bounded best attempt against Greedy. A failed
proper-score gate need not logically forbid a model-based **ranking policy**:
selected logging lacks support for many alternatives, so prediction validation
and prospective policy value are different questions. The director may amend
the earlier hard-stop recommendation **before fitting/validation outcome
access** to retain finite predeclared ranking candidates after a failed
calibration/loss gate. Preserve that failure explicitly. No calibrated-q,
Bellman-value or joint-return claim follows; optional continuation remains
blocked unless its separate model/transition/tail gates pass.

Freeze exactly direct terminal ridge and conditional funnel as two model
families, fixed penalty/features/backoff and minimum-validation-terminal-loss
asset selection. This is two-family development selection, not an unbiased
validation certificate. Freeze the selected asset before the single16-group
development-test prediction evaluation; no repair, candidate substitution or
new model family after that test. If exploratory ranking remains eligible
regardless of predictive failure, say so now and rely on the already bounded
policy reward screen plus one fixed fresh final comparison for policy claims.
Numerical failure, leakage, invalid labels or protocol/resource failure remain
hard stops. No failed scientific gate is relabeled passed.

Training-only constant and **intercept+slope logistic-calibrated agreement** are
probability controls. Raw integer0..7 agreement is never log-loss input. P's
expected-agreement surrogate, if included, also needs training-only calibration.
Root adopted fixed one-sided alpha.05 hierarchy C−G→C−Q6→C−P; update remaining
Holm/hard-stop plan wording consistently before outcome access.

## Independent checks

All16 supplied model/dataset synthetic tests independently passed in0.280s
under a60-CPU-second guard. Additional public-label fixtures verified full
day59 eventual reward, date-lag30 accepted/31 rejected, and second-lag3
accepted/4 rejected. The malformed zero-scale asset failure above was separately
reproduced. Synthetic logistic tests fit constructed arrays only; no research
row, split outcome or model coefficient was accessed. More unit repetition is
unnecessary absent a code change; close the asset-validation defect and test
its malformed-asset boundaries before deployment.

## Separate final pre-fit training receipt

The subsequent train.py review closed the five bounded issues recorded in
train_seed_review.md: per-receipt NPZ/grid/metadata authentication, explicit
weighted Jeffreys constant, predictive-support counts as a probability gate,
zero-trial conditional backoff, and precise.975 bootstrap-endpoint labeling.
The immutable split has64/16/16 groups covering the original96 without crossing.
A metadata-only receipt check found every one of the2,880 cells has rows, so
current equal-cell weighting also equals equal seed/family/arm weighting.
No held-out labels, research rows, model coefficients or predictive scores were
read in that check. **GO for the single frozen two-family training execution**,
subject to its complete receipt/source checks. No fitting was performed by this
reviewer; trained assets/results still require post-fit provenance review.
