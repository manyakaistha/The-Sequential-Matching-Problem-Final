# R8 W2 independent review

Reviewer: `/root/w2_critic`; director integrates. Date: 2026-10-14.
Scope: bounded finite continuation and a public-observation adapter. No simulator
episodes, fitting, promotion or confirmation are part of this review. The review
owns this new file only; completed W1 artifacts remain unchanged.

## B1 disposition

**Accepted for reduced finite-model correctness, subject to the stated menu and
horizon restrictions.** B1 searches the bounded whole-action menu at each future
public belief epoch. It does not merely use a static optimal allocator as its
tail. The inherited transition routine first groups successors by PublicView,
normalizes each posterior, and only then calls the bounded maximization. The
menu receives a PublicView without ready clocks. Internal posterior clocks are
used to compute observation probabilities, rather than select separately
optimized hidden-scenario actions.

The completed bounded comparison either returns rational action values for its
finite menu/horizon or returns the validated current parent with value=None and
empty action_values. State, cumulative support, transition and joint-branch caps
cannot expose a partial optimum. A future region overflow aborts the entire
comparison. Explicit current parents are checked against the full legal matching
domain, and exact value ties preserve that parent.

One draft defect was found and fixed: an oversized initial belief originally
triggered its branch cap before validating later particles' public observations
or total probability, using only the first particle to define fallback legality.
The final implementation scans at most 10,000 input particles, validates positive
rational probabilities, total one, and a common public observation, then allows
the search cap to return the parent. Larger raw inputs are validation errors.
This scan does not pass hidden clocks to the action menu.

## Independent checks

Read-only Python checks used exact Fraction arithmetic and a 90 CPU-second
resource guard. They verified:

* The AB=1/2, AC=2/5, AD=9/10 three-day witness returns wait with value 9/10.
  Instrumented future menu calls occur at days 1 and 2 and receive PublicView
  only. Future waiting is therefore present in this tested construction.
* Starting a day earlier than the hidden-clock choice, an equally weighted
  unavailable-C prior with return days 2 and 3 gives lawful value 3/5; optimizing
  those hidden scenarios separately would give 4/5. Reversing prior order leaves
  the value unchanged. This independently exercises successor grouping before
  a future max, not just grouping at the root.
* Setting each of max_states, max_support_entries, max_transitions and
  max_joint_branches to one produces a parent-only fallback, with no value and
  no partial action_values. A mocked expired wall guard has the same behavior.
* A dense future K8 graph causes day-1 region overflow after another root branch
  can be evaluated; the final result discards all partial comparisons and keeps
  the original AB parent.
* Malformed oversized priors with mismatched observations, total probability
  two or zero-probability entries raise ValueError. A valid oversized raw prior
  falls back on its support cap.
* Day 59 with H=0 and H=12 books the full 9/10 reward and performs no successor
  transition. This verifies eventual reward accounting, not global optimality
  of a restricted final-day menu.

The existing 21 tests independently passed in 0.033 seconds. This is a unit-test
timing, not a 200-member invocation benchmark. AST comparison independently
confirmed that vendored eligibility, baseline_asks and baseline_match match the
governing kit.py functions exactly.

Reviewed B1 SHA256:
`694328acee494938bf2c0325a0bd3a7ca1c9e6ddaa7114d12c73cd819dcf1be1`.
Unchanged exact-core SHA256:
`49d1332459c09be381b86f070c5238f580ea8305530d16de09ccfd95d5834153`.

## Limits and concrete public-model bridge

B1 still uses 4--8 declared actors, at most twelve future decision epochs and
the existing current-graph local menu. It does not implement the full D1 pending
or unresolved-hard boundary. Zero terminal value after truncation can favor
early commitment; successful reduced witnesses do not certify full-horizon
regret. The wall guard is cooperative: it accounts from solve entry but checks
after bounded public validation/menu work and during search. It is not a hard
process interruption or worst-case subsecond proof.

The governing public request contains arrived_day, public profile values and
statuses, current availability, introductions, released feedback and ask logs.
It does not contain true exit_day, busy clocks, hidden member traits or future
arrival identities. An unavailable member is not proof of permanent absorption.
The finite engine observes availability only and has declared deterministic exit
calendars; these limits must remain explicit until a richer law is validated.

A smallest useful frozen public-model asset contract is:

1. A versioned manifest with asset ID, content/source hashes, public feature
   allowlist, frozen fit recipe, public-log provenance, disjoint whole-world
   training/validation split commitments and independent admission receipt.
2. A joint edge law connecting qualified reward, pause/return outcomes and
   public feedback-release emissions. Pending-state support is conditioned on
   the complete released history and current availability, including survival
   without a released event. Reward probability and absorption probability
   are distinct; late positive pause need not qualify as timely reward.
3. Joint future-arrival/profile support derived from admitted public arrival
   histories. Future actor names are synthetic placeholders associated with
   sampled public profile/status outcomes, never unreleased real member IDs.
   Any independence or finite-support assumptions are declared and tested.
4. Runtime validation of positive normalized probability support, compatible
   public observations, reachability assumptions, support/resource ceilings and
   reward/return consistency. Public hard eligibility remains a separate exact
   check on both endpoints; an imputed or soft answer cannot verify it.

A manifest signature or caller-supplied admitted=true flag is not calibration.
Model/data provenance, probability/observation calibration, conditioned pending
history coverage and transition correctness require independent evidence. The
current wave can supply public parsing, legal action validation and a working G
fallback immediately; absent or unsupported assets should select G rather than
invent probabilities or prevent ordinary public decisions. Request memory or
config must not bypass asset admission with ready clocks or private calendars.

## Adapter receipt

**Accepted for public parsing, validated unchanged G deployment behavior and an
offline declared-law integration seam.** The adapter is deliberately not a
calibrated production B1 controller. It derives an all-arrived histogram from
public arrived_day records and includes zero-arrival days. Ask and match calls
are idempotent; unavailable members are not counted as departures or negative
arrivals. Current G actions are revalidated against public availability, hard
eligibility, prior introductions, whole-matching and ask-budget constraints.

Independent checks rejected private member keys (truth, exit_day, busy, ready),
future arrival/field observation records and contradictory hard status/value
records. Wire config and memory cannot inject ready clocks or model calendars.
A real-source compatibility defect was found and fixed: kit.py legitimately
uses declined fields with value=None and field_observed_day=None. The adapter
now accepts that record while preserving the decline and withholding the actor
from hard verification/matching. Its regression passed.

The offline provider receives a deep copy of the sanitized public request.
Projection checks require the same public clock, one-to-one real-member mapping,
observed availability, public introduced dyads retained as exhausted, and outside
assignments disjoint from projected actors. Unresolved/open current boundaries
and omitted real eligible current edges select G. Final projected actions are
revalidated against the real public graph. A capped prior at the earlier public
view normalization gate also selects G; its new regression passed. These checks
validate a declared-law fixture seam, not conditioned real-feedback fidelity,
uncertain exits or model asset calibration.

## Closed validation reconstruction and final receipt

The reviewer independently reconstructed the closed validation JSON without
importing the director's runner or analysis helper. All 27 registered Cartesian
keys are unique and complete. Because all three opportunities share A and every
introduction absorbs the pair, the exact value is max(today, middle, future).
For the recorded current action, true first-action value is today if AB is
introduced and max(middle, future) if it waits. Every expected value, oracle
value and regret matches these formulas. All 27 first-action regrets are zero;
19 choose wait. Recorded state/support/transition counters respect the caps.
This is a deterministic finite construction, not independent simulator samples
or a statistical claim about a population reward effect.

The recorded timing aggregates reconstruct exactly. The 200-member benchmark
tests the public adapter executing **G fallback**, with ten direct calls and
three fresh subprocess calls for each of ask and match. The largest recorded
fresh-process invocation is 0.093421 seconds, below the one-second target on the
reported host. Full subprocess startup/import/JSON costs are included. This
does not measure active B1 planning on a 200-member graph, arbitrary pending
histories, Docker restrictions or a worst-case bound. A four-actor offline
projection is timed separately. The benchmark's active_planning=false and
live_model_asset_admitted=false labels are correct.

The final independent guarded test run passed **34 tests in 0.058 seconds**
(21 existing and 13 W2 tests). Each frozen source hash in validation.json matches
the current file, and the old exact-core hash remains unchanged. The reviewer
did not rerun or overwrite the closed grid/benchmark artifact.

Reviewed public adapter SHA256:
`5d153751e3fb0a88df9e32b143db4e46922241d646b41cc1a323f5666d85714d`.
Closed validation artifact SHA256:
`f07000875bb52ccb9f0a90aed937af9985b5e993b822beafb03bc007a912a380`.

The finite-horizon limitation remains a real gate: analytically, certain
absorption with AB reward 1/2 on day 0 and AC reward 9/10 only on day 13 makes
H=12 value the hold branch at zero, choose AB, and lose 2/5 against the full
declared horizon. This deduction motivates the director's separate registered
tail diagnostic; it is not another committed grid result in this receipt.

Final disposition: reduced B1 continuation and the public/G/offline fixture
adapter are accepted in their stated development scope. Production joint-model
asset admission, full feedback/uncertain-exit transition fidelity, tail-error
control and active full-population runtime remain unclosed. No fitting, official
simulator episode, superiority result or reward-screen admission follows from
this review. The authorized development has concrete working artifacts and a
public fallback; no further permission question is required to report them.

## Separately closed tail diagnostic

The director subsequently committed the separately registered day-13 diagnostic.
Independent receipt inspection confirms H=12 chooses AB with value 1/2, the full
declared horizon chooses hold with value 9/10, and full first-action regret is
2/5. The registration hash matches. The recorded NOT_CERTIFIED tail gate and
production_admitted=false correctly preserve this negative evidence; the
short-grid pass is not a full-horizon certificate. No new simulator sample or
extra unit run was needed to reconstruct this exact arithmetic.

Tail diagnostic SHA256:
`9b02b04851de049990d7c5a859e176014093a32994cb949343fc0a0edaf6f268`.
Tail registration SHA256:
`7d6e6e6336c3f7790fd14d4a6a7bfa8b76c568c6f466d46a525a192773ff5a72`.

## Metadata hardening amendment receipt

The director identified a separate public-shape loophole: previously unchecked
source/pool/gender/zone, introduction logging and feedback metadata could hold
nested maps despite occupying nominally public keys. The new checked_request
requires scalar member metadata, scalar introduction identifiers/logging policy,
numeric-or-null propensity, scalar feedback identifiers/event/missing reason,
and allowed ask-log statuses. The new private-map regression passes. Structured
unknown keys and forbidden calendars still fail before reaching the provider;
legitimate initial declined records remain supported.

This is a registered source change after the original receipt. The original
adapter, adapter tests and validation runner were preserved in
history/adapter_v1. Independent review verified every historical manifest hash,
the unchanged original validation artifact hash above and all current hashes in
the new validation_hardening.json. The latest adapter hash below supersedes the
old adapter identity for the current source; the earlier receipt continues to
identify the historical source and its untouched original result.

The reviewer independently ran all **35 tests in 0.056 seconds**, under a
60 CPU-second resource limit. The suite includes the existing four search-cap
failures and wallguard fallback tests, and the new metadata test. Independent
Fraction reconstruction again confirms all 27 unique registered cases, exact
expected/oracle values, parent ties and zero first-action regret; resource
counters remain within their limits. Timing maxima and counts reconstruct from
the latest raw timing arrays. The largest recorded fresh-process invocation is
now **0.102775 seconds**, still below the target for the same constructed
200-member **G fallback** workload. This justified rerun follows the source
change and writes a separate artifact; it does not overwrite the original
benchmark, increase a statistical reward sample or demonstrate active
200-member B1 planning.

Current adapter SHA256:
`f08dd4d535f0e71966704bfb6c9ce1f2ec8f5af5f6bd7ffacce2d621a4ebf853`.
Latest hardening validation SHA256:
`d3fc1df6b6556d676073092d07cfd1f08d47655c812375a5a36128d7dc46728f`.
Hardening registration SHA256:
`3993662e88ead99d5dbbfcda4bfe4444ee7973098a6db11737992d6507d4312c`.

Amendment disposition: accepted in the same restricted development scope.
Production assets, full feedback/exit fidelity, demonstrated tail-error control
and active full-population runtime remain unclosed. The explicit tail failure
is material evidence against extrapolating the short construction's fidelity
pass. No official episode, fit or reward-screen admission was added.
