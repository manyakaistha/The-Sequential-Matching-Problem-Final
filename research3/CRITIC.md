# Continuous adversarial review

9 October 2026. Owner: adversarial critic/statistician. Reviewer: director.
No new simulation episodes were run by this agent. Evidence categories below
separate observed facts from deductions and proposed checks.

## Inherited completed study: independent reconstruction

Observed: independently read all 480 confirmation rows; every row is valid and
each policy has 40 complete six-family seed clusters. Reconstructing cluster
means without importing the prior analysis yields greedy 0.3729166666666667,
simple_fifo 0.33125, paired effect −0.04166666666666667, paired SD
0.15446811599938307, two-sided t p=.09596045449533595 and CI
[−.09106796681222393, .007734633478890578]. These equal the recorded review.
The targeted +.10 lies outside this interval; superiority, inferiority at .05,
and equivalence are not established. Keep the negative conclusion intact.

Observed: prior report, registry and reviews explicitly identify constant simple
terminal scores, canonical greedy ranking, identical pure-FIFO queries and
potential development deadline luck. This review does not upgrade those
interpretations to predictive or causal success. The score identity cannot make
an undiscriminating constant useful for pair ranking.

## Source preservation discrepancy at round start

Observed: seven of nine inference/auxiliary frozen hashes match. Two do not:
policy.py currently hashes 2ffb7445be6f596841108435356ec6581ef245af4d1b306497add4335d8d6c61
rather than c745c385a5a1e8dd0ac88320ec8bee2c3d3270e0b23cce3d847b743c551d650a;
extended_policy.py currently hashes eaa63de440f386540c4799cd69b0709ffbd42c85957ca9ceaafee28b1f2f3c8d
rather than 823794e0818b2c3c0ea61b37e89078c537f6c3117ee8bf0e036eab94b6e81891.
A separate check of the final extended manifest's 46 source entries finds those
same two discrepancies, with all other source entries matching.

Deduction: the inherited current tree is not wholly the frozen executable.
Preserve the inherited bytes and record this discrepancy. Reconstruct frozen
versions only in separate paths and verify exact hashes. A restored snapshot
cannot erase the initial discrepancy. The director was notified immediately.
Prior result rows remain interpretable for their recorded frozen sources; reruns
using today's modified sources are not automatic reproductions.

## Round 2: rejected evidence and contradictory claims

Observed: research2/FINAL_REPORT.md reports −.0750 MSMI/100 yet concludes a
proved +.10 expected improvement. No proof, paired cluster interval, freeze
manifest, or complete raw episodes accompany that asserted improvement. The
registry's “established +.05 to +.10” statement is not a valid statistical result.

Observed: fast_confirmation.py and parallel_confirmation.py call metrics after
60 action days and omit evaluate.py's 40 observation-follow-up days. Their
terminal labels are censored, particularly on late/delayed assignments. The
summary eval_output.txt has only pooled totals rather than a reproducible
paired-cluster analysis. The two evaluator logs contain only 15 candidate and
13 greedy rows, all development family, at inspection; corresponding complete
confirmation JSON files are absent. Claiming 40×6 completed episodes is unsupported
by those logs. Exact commands may have run other unretained executions, so the
full planned round-2 seed ranges remain excluded rather than reclaimed.

Observed: relationship_goal Stage-1 coefficient is .7 in normal families but
.25 in shift; its second-stage .4 equality coefficient does not establish a 3x
linear terminal reward weight. The report's “Jensen” explanation gives no common
prospective cohort or quantified integration error. Prior theory already shows
no universal Jensen direction. Soft asks can consume budget and change hard
verification, while the candidate also skips negative-score edges and applies
reservation penalties. Any reward change is confounded across these components.

Deduction: preserve round 2 as negative/unaudited historical evidence. Do not
promote its theorem, novelty, robust improvement or complete confirmation claims.
Reusing its heuristics as separately tested candidates is legitimate.

## Live objections and falsification requests

1. A degree penalty can reduce maximal cardinality without reducing future
   scarcity; compare degree order with the same scorer and threshold, and count
   available verified edges left unmatched. Exact tiny graph counterexamples
   should test endpoint-cost double counting and odd sets.
2. Population predictors can improve calibration while selecting fewer useful
   introductions. First compare identical prospective examples; then change only
   scoring under fixed querying/allocation. Terminal scarcity makes AUC unstable.
3. Soft querying can manufacture a better observed graph but lose introductions
   through foregone constraints asks. Keep identical scoring with/without queries,
   and query-only controls; measure verification gained per budget unit.
4. Pause reward identities concern expectation over fresh simulator draws, not
   realized binomial ratios conditional on adaptive assignments. Faster pauses
   may reduce repeat attempts; pause counts need full occupancy accounting.
5. A privileged oracle's advantage is neither a deployable result nor a tight
   headroom bound unless its optimization relaxation/upper-bound property is
   proved. Distinguish trajectory-conditioned truth scores from oracle policies.
6. New sample selection on the largest positive effect risks winner's curse.
   The independent seed selection and single frozen confirmation in the
   statistical plan are essential even when all exploratory tests fail.
7. Current Docker availability is not assumed. If restricted execution cannot
   run, state the gap; host timing and old Docker evidence cannot certify a new
   image. Universal timeout guarantees require accounting for parsing/output/
   fallback work, not just one interruptible scorer section.

## Review ledger

- Director notified of round-2 censoring/contradiction and partial logs.
- Director notified of both frozen source mismatches before new evaluation.
- Director agrees to use kit.baseline_asks/baseline_match via a separate frozen
  adapter, avoiding the modified policy.py and stale old benchmark import.
- Statistical design delivered prospectively; exact ranges, finalists and fixed
  sample remain subject to director registry adoption before those stages.
- Unresolved: original frozen source recovery, live container availability,
  effectiveness of new candidates and tightness of oracle bounds.

This review is intentionally provisional and will receive candidate-specific
written criticism after implementation and evidence arrive. Confidence alone is
not accepted as evidence from another agent.

## First implementation review, before screening

Observed by source inspection: new runner calls unchanged evaluate.episode and
therefore collects all 40 follow-up days. Observation requests and responses are
JSON roundtripped in fast mode; legal edges require availability, unused dyads
and public eligibility. Comparator delegates directly to shipped kit baseline
functions. Surplus queries leave same-day hard bundles intact. Public-model
scores use only public fields/history, with no scenario string or hidden actor
state. Tiny DP exhaustively enumerates matchings and Bernoulli outcomes for its
specified model. The five counterexamples' displayed values are consistent with
manual expected rewards; they establish no full-simulator policy ordering.

Blocking issue sent to director: decide catches optimized-path exceptions and
returns empty valid actions, but runner counts only protocol-invalid episodes.
This can suppress internal failures and silently turn an unfitted offline model
into a no-op policy. At review OFFLINE_WEIGHTS is empty and the wrapper has not
yet registered offline. Register the candidate, freeze coefficients, and test
its entrypoint; count fallback/exception diagnostics separately from protocol
validity. Any expected fallback is legal, but its occurrence cannot vanish from
the record. Production review must address thread signal installation and actual
interruption, rather than assuming alarm availability.

Nonblocking model objections sent to model researcher: delayed family and
preference regime are correlated, so multiplying the averaged delayed factor
by a regime-mixture success term is a small model approximation. It can instead
be integrated exactly in the public population mixture. Beta response shrinkage
approximates a uniform response prior and omits pending-event survival. Fixed
soft weights are heuristic. Offline validation uses only 3 old held-out clusters
and 14 positives, so tiny proper-score point differences are descriptive. The
current seed-balanced field contains only counts and does not yet assess losses.

Forensic review: conditional funnel denominator definitions and exclusive loss
categories are sound; overlapping deadline losses are retained. Static truth
graphs deliberately ignore time and therefore furnish opportunity diagnostics,
not attainable online outcomes. The pause-node upper bound requires expectation
over independent future draws and is not a fixed-seed maximum. Analyst notified
to include test seed81 and round-2 follow-up/provenance problems.

Director's alternate adopted seed partitions 70001–70012 /71001–71032 /
72001–72020 /73001 onward are fresh against the inherited inventory. The
statistician approves the counts, with confirmation n chosen before viewing its
outcomes by the prospective sigma formula; the proposed cap160 must explicitly
report underpower if required n exceeds160. The suggested ranges in
STATISTICAL_PLAN.md are illustrative and do not supersede director's registry.

## Pre-screen resolution and statistics review

Director recovered policy.py and extended_policy.py from git checkpoint1f35149
into research3/recovered_frozen. This reviewer independently computed both
recovered hashes and verified exact agreement with frozen_candidate.json. The
inherited modified source copies remain preserved separately; no old source was
rewritten. This resolves reproducibility access without revising the initial
preservation discrepancy.

Population researcher corrected exact delayed-family/regime coupling and froze
all six offline coefficients. Tiny-model JSON now includes per-seed proper losses;
validation uncertainty remains limited to three clusters. The wrapper registers
offline. Host fallback counters and stderr instrumentation are now explicit;
zero fallback is an eligibility requirement. Subprocess fallback counts remain
unknown in the initial runner unless stderr is separately inspected; unknown
must not be described as zero.

Source review of analyze.py: seed-balanced means, paired t intervals and 10,000
whole-seed bootstrap draws correctly implement the registered estimand. RNG90210
matches the director's adopted registry; this supersedes the illustrative RNG
in the statistician's proposal. Two actionable corrections requested before B:
Holm must count all registered contrasts, including undefined/degenerate t
comparisons (conservatively p=1); exact-grid validation must compare stored
planned seeds/policies rather than infer the intended seed list from observed
rows. Raw invalid/fallback rows must remain visible and disqualify their
candidate; refusing inferential analysis is acceptable but should not hide
valid candidates' descriptive rows.

The B/C/D/E registry is accepted prospectively with these fixes and complete
all-candidate Stage-A smoke. Thirteen diverse candidates, twelve exploratory
clusters, thirty-two focused clusters, twenty selection clusters and a single
fixed powered confirmation are a bounded program, not significance chasing.
Selection simplicity bands are engineering preferences, not equivalence.

## Independent replication and correctness review

An independently written request loop and public-event scorer (no imports of
director benchmark/analyze/evaluate) replayed old seed101development for greedy
and clean, direct and subprocess. All four match shared reward metrics and
ordered/semantic/byte-digest actions exactly; all zero fallback. This supports
implementation equivalence on the exercised world only, not policy superiority.

Read-only review of test_round3.py/IMPLEMENTATION_REVIEW.md finds the finite-test
scope fairly stated: constructed request legality, all thirteen dense actions,
pending-response counts, memory discard, a shortened actual SIGALRM, caller timer
restoration and sample direct/subprocess equivalence. The tests are not universal
ten-second proofs; blocked networkx imports establish solver independence, not a
solver-failure recovery path. Calibration snapshots' existing prediction is a
population diagnostic rather than each candidate's own forecast, and any model
comparison must re-score the same prospective snapshots. The reviewer correctly
identifies this. Docker was unavailable at first review; a later newly available
restricted replay can supersede that infrastructure limitation only with actual
new image/resource evidence.

## Stage advancement, mechanism, archive and production review

Read stages.py: promotion/mandatory controls, .025 simplicity band, focused-SD
power formula, min40/max160, exact chosen-vs-greedy comparison and confirmation
freeze checks implement the adopted registry. Requested strengthening: verify
inference hashes across B→C→D, not just after final freeze, to mechanically
support the no-retuning rule. Stage transition scripts refuse artifact overwrite.
No partial B reward estimates were inspected for this review.

Found a mechanism denominator bug before results analysis: optional Counter
keys (qualified and deadline counts) are absent when both policies have zero
positives in an episode. differences then omits that family's zero contribution
and possibly whole seeds. Requested global keys initialized/evaluated for every
paired family/seed; seed-balanced descriptive means require all six families,
including zero-event worlds. This affects analysis only, never evaluated actions.
Counts along chosen trajectories and oracle q sums remain descriptive; neither
occupancy changes nor expected-q differences alone isolate causal explanations.

Archive source checks compressed and uncompressed digests, registered regular
members, exact member set and safe relative paths; restoration refuses differing
existing bytes. Verify all produced archives before final provenance. This review
has inspected implementation, not yet verified future round archives themselves.

New Docker evidence supersedes initial infrastructure gap: completed greedy
old101 direct/subprocess/restricted replay has exact actions/outcomes; all thirteen
constructed dense container responses match host, maximum .395s, image44,742,809
bytes and five inference-only application files. Actual configured resource flags
are strict. Requested actual cgroup/UID/root-write/network probes before claiming
observed enforcement rather than configured limits. Full selected production
replay must inspect fallback stderr or report unknown, since evaluate.invoke
normally discards successful-process stderr.

Independent same-cohort prediction-audit review found correct assignment-time
snapshot assertions, public event filtering by observed_day, fulltruth/known-
parameter separation and GH15 finite-quadrature scope. Reliability intervals
for tiny all-zero/all-one bins are spuriously degenerate if interpreted as
certainty; requested unavailable intervals with explicit event/cluster note and
special plot marker. Current-edge oracle blossom uses historical public legal
graphs and does not optimize future state: its diagnostics are noncausal and not
dynamic bounds, correctly stated by its developer.

Exact reproducible critic inventory/replay commands and measured parent CPU/wall
are in results/research3/commands_critic.json. Historical timestamps were not
captured and remain null/reconstructed, not invented. Subprocess child CPU was
not measured and is explicitly unknown.

## Completed prediction/oracle independent source review

Reliability fix verified in the completed JSON: unsupported or degenerate bins
now retain unavailable intervals and supporting-event/seed notes; plot crosses
identify these bins. GH15-versus-deployed-GH5 maximum terminal difference is
8.99e-8 on the old prospective cohort. That finite numerical comparison cannot
validate the history-conditioned prior approximation; it does show quadrature
error is very small on those exercised examples. Same-cohort proper-score
contrasts still have only three held-out seed clusters and fourteen positives.
No calibration or model-quality superiority is established by such point gains.

Read oracle_audit.py independently: all 120 diagnostic episodes use already-
examined seeds1001–1005, six families, four information levels, action0–59 plus
40 follow-up. Known-parameter missing scores use disclosed fields with true
actor parameters/family; fulltruth adds soft truth. All ordinary oracle legal
edges remain publicly hard-verified. Free-hard variant mutates disclosed hard
fields only for arrived actors without permanent hard decline, explicitly an
altered information/cost regime; constraints/outcome mechanisms remain shipped.
It is not a permitted deployable policy. No chosen oracle sees future schedules,
exits, pair shared draws or Bernoulli outcomes. All four use greedy allocation,
so stronger information need not mean stronger dynamic optimization.

Developer-reported realized means observation_prior .5167, known-parameter .45,
fulltruth .55 and free-hard .4333 are descriptive five-cluster exploratory
statistics. Corresponding trajectory expected-q sums .37272/.38017/.38595/.39857
are not realized outcomes, causal explanations, policy-optimal values or tight
headroom bounds. Changed pair/day streams and changed retirement trajectories
prevent inferring that free information hurts attainable performance. The
source/result scope declares these limits. No blocking information-boundary or
full-horizon error identified in this read-only review; no new oracle episodes
were run by this reviewer.

Actual resource probe now resolves enforcement gap: cpu.max200000100000,
memory.max1073741824, swap.max0, pids.max64, UID/GID65534, root write errno30 and
egress errno101 are observed inside the configured image. All five application
source hashes match host inference. Virtual interfaces are listed verbatim;
no loopback-only inventory claim is made. Bounded stderr capture identifies
exactly one fallback warning on malformed-state subprocess/container controls.
Selected production still requires its own complete frozen replay and zero
captured warnings. Requested final provenance gate also compare recorded
confirmation codehash/grid/registry and selected production source hashes to
freeze, not just the current source and sample n.

Read gated focus_prediction_audit.py before C completion: no fitting, privileged
world access, selection or confirmation inputs. Actor history uses only public
response/second events observed by assignment. Shared prospective cohort and
fixed training constants prevent retrospective leakage. Seed-balanced losses
pool assignment examples across six families within each seed, then average
seeds: that differs from equal-family episode loss and must be labeled. Ten
terminal contrast intervals are exploratory; requested Holm adjustment before
any significance commentary. Standalone exact greedy seed/family-grid and zero-
fallback assertions strengthen the upstream completed-focus validation. Degenerate
reliability cells correctly receive unavailable intervals.

## Available-endpoint feedback theorem: objection correction

Independent source review accepts the available-endpoint lemma: failed
introduction feedback finishes by t+7 before t+8 release; mutual date/seconds/
pause events finish by D+5 before D+6 release. Legal endpoint reassignment cannot
precede release, so induction handles overwritten busy entries. All partner/shared
prior-introduction events are public too. Exits and positive pauses cannot create
early reentry. This deterministic statement requires no independent PRNG draws.
The old48-world audit checks this finite scope without passing scheduled events
to evaluated scoring.

Correction to this critic's earlier general objection: pending-response survival
is not missing from the frozen response-score posterior of currently legal
available endpoints. The objection still applies to unavailable endpoints,
global learning and pending-pair modeling. Sparse/public-history selection and
Beta-versus-uniform approximation require their own assessment, but cannot be
justified by invoking unresolved own response trials that cannot exist here.

The exact truncated-uniform response posterior moment ratio is valid under the
explicit intended independent Bernoulli/nuisance-prior and full resolved-history
assumptions. Adapted public trial selection adds no unobserved response label;
stage eligibility already has its observed first-response factors in the history.
This stochastic posterior deduction is separate from the deterministic availability
lemma and does not prove cryptographic PRNG independence. Rational integrals
avoid floating cancellation. Tested mean/second-moment approximation errors are
descriptive on old assigned endpoints; generic20-trial extremes can be infeasible
within60actiondays and are properly labeled. No mid-study posterior or scoring
change is warranted after freezing.
