# Independent final mathematics and production review

8 October 2026. This is a read-only review of the existing inference source,
simulator, theory, frozen configuration and recorded verification artifacts. No
new rollout, evaluation seed, parameter change or inference edit was performed.
The only file owned by this review is this document.

## Opinion

No blocking mathematical error was found in the stated qualified-reward/positive-
pause theorem, pure-FIFO invariance proposition, odd-set example, logistic
approximation bound or finite rational dynamic benchmarks. Their conclusions
need the restrictions already stated in `EXTENDED_THEORY.md`. None proves an
optimal full-simulator policy or establishes an empirical superiority claim.

The six inference/simulator/evaluator hashes recorded in
`results/extended/frozen_candidate.json` match the files reviewed. The selected
configuration is `simple_fifo`, exactly `{"model":"simple"}` over the frozen
defaults: FIFO hard bundles, greedy allocation, no opportunity penalty, no
batching, no uncertainty penalty and no soft asks. The executable default remains
the integrated model and is a different candidate.

## Mathematical challenges resolved

**Pause identity.** In the ideal independent-draw interpretation of the shipped
transition mechanism, conditional on fixed family and preassignment history,
the date/feedback delays are independent of the event comprising mutual
acceptance, actual date and two positive second intentions. The assignment
indicator is measurable before those draws. Summing conditional expectations
therefore gives `E[N_Q]=c_f E[N_P]` even when previous qualification marks affect
later assignments. Standard `c_f=9/25`; delayed
`c_f=(9/25)(671/686)=6039/17150`. Both seconds arrive by date plus five and busy
release is date plus six; pause events therefore have disjoint endpoints under
legal actions. Hence `N_R=2N_P` pathwise after full follow-up, where `N_R` counts
positive-pause endpoints, not exits or the unused simulator `retired` set.
Scheduled outcomes are not cancelled by exits. All supported events of a day-59
assignment mature by day 97, before official evaluation.

Two stronger claims would be wrong and are correctly excluded: an exact realized
fixed-seed reward/pause ratio, and independent Binomial qualification marks
conditional on the final adaptively generated pause count. The rational adaptive
example in `theory.json` explicitly disproves an expected-ratio interpretation.
The seed-and-dyad hash feeding a deterministic PRNG is not a mathematical proof
of fresh independent random streams. The theorem states the intended stochastic
transition assumptions rather than silently claiming exact PRNG independence.
Pooling families requires family-specific weighted expectations.

**FIFO invariance.** An incomplete hard-constrained member cannot legally be
introduced, so its busy/positive-pause state cannot differ before its bundle
reveal. The incomplete queue's arrivals, exits, order and permanent-decline
pruning are therefore common to pure-FIFO policies with the same world and
budget. After a bundle all nondeclined hard fields are present and that member
leaves the queue permanently. Induction establishes identical schedules and
costs. `kit.baseline_asks`, the frozen FIFO path and its ask fallback implement
this queue on valid shipped requests. Soft budget spending, reordered members,
partial bundles and feedback-based priorities fall outside the proposition.
The proof establishes ask equality, not matching or reward equality.

**Nonseparable continuation and odd sets.** The AB/CD versus next-day AC example
correctly double-counts the same future alternative when edge losses are added.
The unit triangle has degree-relaxation value 3/2 versus matching value one;
the odd-set inequality repairs that example. A general-graph static dual needs
odd-set multipliers as well as node prices. Neither a static dual nor an exact
static matching makes dynamic continuation separable.

**Missing features and integration.** The global Taylor remainder bound is
`|E[sigmoid(Z)]-sigmoid(E[Z])| <= Var(Z)/(12 sqrt(3))` for finite variance.
There is no global Jensen sign. Enumerating independent missing equality
indicators is exact under the declared public soft-feature priors; it is not
the exact learned posterior after selection and shared history. Gaussian
quadrature and diagonal actor/tempered-regime updates remain approximations.
The fixed-grid numerical convergence audit supports quadrature accuracy on its
grid, not calibration or a universal error certificate. Reusing shared S and
goal equality through all four logits, and using response second moments,
corrects specific independence/mean-substitution mistakes without making the
posterior exact.

**Tiny MDP scope.** The five rational Bellman benchmarks exhaust legal current
matchings, including wait, with explicitly known schedules and next-step
retirement outcomes. Rational expected reward and regret values in `theory.json`
refer only to those finite simplified models. They omit the full simulator's
hidden schedules, questionnaire uncertainty and learned actor dependence.
Current blossom results are checked against enumeration; blossom alone is not
the dynamic optimum. The counterexamples challenge reductions and unrestricted
monotonicity, rather than every empirical reservation policy.

## Selected policy interpretation

The selected simple terminal estimate is a common smoothed aggregate rate for
all current dyads. It is positive and does not discriminate among edges. With
the selected configuration, normal allocation is therefore greedy in canonical
member-ID edge order. Updating that common rate does not change its ranking or
normal chosen pairs. The executable still computes integrated diagnostics and
updates actor memory before substituting the aggregate probabilities, so simple
decision behavior should not be confused with a fully stripped executable.

This is a meaningful simpler control against the baseline's visible-soft-equality
ranking. Any difference from greedy cannot be attributed to different pure-FIFO
hard asks under the proposition. It also cannot be attributed to terminal
probability discrimination by the selected score. Consequent availability,
dyad selection and stochastic outcomes can differ; attributing the reward
difference to a particular mechanism needs the separate controlled or empirical
evidence. Calibration of a constant forecast is a legitimate calibration test,
but does not demonstrate useful pair ranking.

## Production evidence and limits

`production.json` records the actual selected simple configuration. On already
examined development seed 1001, in-process, subprocess and restricted-container
actions have identical hashes and semantic outcomes. Container maximum call time
is 0.231712 seconds; peak serialized memory 152,643 bytes and request 631,222
bytes. The recorded image is 52,761,330 bytes. Effective limits are two CPU cores,
one GiB RAM, 64 PIDs, read-only root, no network and unprivileged UID. Its listed
application files exclude data and analysis artifacts. These are verification
results for the recorded image and episode, not every possible trajectory.

`stress_container_original.json` preserves a genuine original-default dense
request timeout. The guard patch retains the original source and records its
adoption in `production_guard_adoption.json`. The guarded source hash matches
`stress_final.json` and `stress_container_safe.json`. All twelve host stress
cases returned valid protocol, maximum wall time 7.104025 seconds; sampled RSS
maximum 100,237,312 bytes. All four recorded restricted-container cases returned
valid protocol, maximum wall time 7.194367 seconds. These constructed
observation-only stress cases are production tests, not performance episodes.
The host RSS statistic is sampled every 50 ms, not an exact peak.

The seven-second alarm interrupts optimized decision execution, including nested
solver work: `InvocationTimeout` inherits `BaseException` so the solver's
`except Exception` cannot swallow it. On interruption, the alarm is disabled
and an observation-only first-fit/FIFO fallback runs with reset memory. Actual
matching fallback rechecks observed eligibility, availability and used dyads;
hypothetical sampled hard fields never authorize introductions. The serialized
memory limit is strict, below one MiB, with an empty-memory legal fallback on
oversized/corrupt output. The subprocess protocol also caps request reads at
one MiB. Thread or missing-timer invocation falls back immediately.

The guard is not a universal proof of a ten-second wall-clock bound: JSON input
and output and the fallback itself run outside the seven-second optimized-path
alarm, and first-fit fallback has quadratic worst-case pair enumeration. For the
shipped 200-member workload the recorded stress evidence fits the ten-second
budget; arbitrary larger or adversarial inputs and slower machines are outside
that evidence. Deadline-sensitive query or solver work can also alter behavior
under resource scheduling. Equivalence is supported for the exercised replay,
not all environments. No inference change is recommended after freezing merely
to simplify this limitation.

`tests_final_policy.log` records all 28 policy and safety tests passing.
`tests_theory_review.log` records 19 independent policy tests and
`safety_tests.log` records nine guard tests. This review inspected their recorded
output without rerunning experiments. Unit checks, stress cases and the one
cross-execution replay establish complementary practical evidence; they do not
constitute formal process isolation of trusted Python or exhaustive production
verification.
