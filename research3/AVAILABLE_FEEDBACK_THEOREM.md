# Available endpoints have no unresolved own-introduction feedback

Exact source lemma, independent replay and response-posterior diagnostic. Researcher owns this document/audit; adversarial critic reviews it. Frozen evaluated models and registry are unchanged.

## Deterministic source lemma

**Lemma.** In any history produced by legal calls to shipped `Simulator.advance`, at any public observation day d, if member i has `available=true`, every event scheduled by every prior introduction involving i has `observed_day<=d` and is included in that observation's feedback. This includes its partner's introduction/second feedback and shared date/pause events, not merely i's own response events. No independent-random-stream or probabilistic assumption is required.

**Proof.** For an introduction at t without mutual acceptance, the only scheduled events are its two introduction responses. Both have observation day at most t+7, including explicit no-response at t+7. Both endpoints are busy until t+8 (`kit.py` lines158–167), strictly after all scheduled feedback.

For mutual acceptance, both introduction responses precede the date, since date day is their maximum sampled response day plus a strictly positive offset. Delayed-family extra offsets are also positive. A date event is observed on its date day D. If cancelled, there are no second-intention events. If the date happens, every second-intention event is observed by D+5, including explicit no-response. Any positive-pause event is observed at the maximum event observation day, also at most D+5. Both endpoints stay busy until D+6 (lines168–188), strictly after every scheduled event.

An endpoint cannot legally receive its next introduction before its busy release: `advance` checks public availability before assignment (line149). Thus all events of each earlier introduction have already been observed before any later legal introduction involving that endpoint. This induction avoids an error from looking only at the currently overwritten `busy` dictionary. For the most recent introduction, an available endpoint must have reached its release day by the availability predicate (lines97–100), again after every scheduled feedback day. A positive pause only makes the endpoint permanently unavailable; an exit similarly cannot create an earlier reentry. An endpoint with no prior introduction has no such events. Finally, `receive_feedback` returns all events with observation day at most d (lines110–111). Therefore all prior-introduction events are public when i is available. ∎

The lemma remains valid after exogenous exits because exits do not reopen endpoints or cancel scheduled feedback. It does not identify why unavailable endpoints are unavailable and does not say the whole market has no pending feedback. It also does not expose future date/busy-release times before availability returns.

**Counterexample to an extension.** At assignment day0, a member is unavailable on day1 while its introduction response can still be pending until day7. Therefore the lemma cannot justify ignoring pending-survival evidence when modeling unavailable members, global regime parameters, pending-pair values or history-adaptive query timing. Changing busy release to t+1 without changing response delays, or D+2 with second feedback up to D+5, would invalidate it. Arbitrary malformed externally supplied observations or histories that bypass legal simulator calls are outside scope.

**Policy consequence.** The frozen response score ranks only currently legal edges, whose endpoints must be available. Every prior response/second trial involving those endpoints is resolved; there is no pending-response survival contribution to their propensity posterior at that invocation. The earlier general objection that response scoring omitted pending survival is therefore inapplicable on these legal current edges under the shipped simulator. Population/prior selection errors, Beta-prior approximation and calibration still need assessment. Public global learning can involve unavailable endpoints with pending events and is a different problem. This correction is a clarification of assumptions, not a mid-study model change or post hoc policy improvement.

## Independent old-world replay

`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m research3.available_feedback_audit` reconstructed all48 old greedy worlds, seeds1001–1008 across six families, and replayed recorded ask/match actions. It verified exact introduction lists against raw traces. At every match invocation, it checked all publicly available endpoints against the offline scheduled-event list. This private list was used solely to test the lemma, never to choose an evaluated policy action or learn a model.

458,829 available endpoint invocations and290,606 prior-introduction event checks had zero unresolved-event violations. These repeated checks are exhaustive for those48 trajectories, not independent statistical trials or a replacement for the source proof. There were7134 assigned-endpoint examples, exactly twice3567 old common-cohort assignments. Runtime was8.22 CPU seconds. Source/trace hashes and individual episode counts are preserved in `available_feedback.json`.

## Exact uniform response posterior

This separate deduction uses the intended stochastic generative assumptions: an actor's fixed R is Uniform[a,b] with a=.55,b=.98, response/second-submission flags are independent Bernoulli(R) draws conditional on R, and assignments/stage eligibility adapt only to public history and independent policy randomization. These assumptions concern the probabilistic interpretation; the deterministic PRNG implementation does not itself prove fresh independent streams.

For s observed responses and f explicit no-responses, including introduction and second submissions, the response likelihood is R^s(1−R)^f. Adapted trial selection does not add an unobserved response label. Second trials exist only after observed introduction success/date, whose response flags already contribute to s; acceptance/second-yes/date factors contain no further R conditional on those observed submission flags. With independent prior nuisance parameters and full resolved public history, the R factor remains separate. Available endpoints have no unresolved own trials by the lemma, so no pending-survival factor is missing for this current-edge propensity score.

Define Z(s,f)=integral_a^b r^s(1−r)^f dr. Then

`E[R^k | s,f] = Z(s+k,f) / Z(s,f)`.

Equivalently, these are incomplete-beta integral ratios, or finite polynomial integrals. The audit computes them exactly as rational numbers by expanding `(1−r)^f`; no floating cancellation enters those integrals. Only displayed numbers are converted to floats. Exact moments do not imply the rest of the terminal model is exact or calibrated.

The frozen Beta prior matches the uniform mean and variance: alpha8.16055164954, beta2.50683612764. Hence it matches prior first/second moments, and one-trial posterior means. After finite observations, the truncated-uniform posterior is generally not that conjugate Beta posterior, and second moments can already differ after one trial.

On7134 old assigned-endpoint examples, the absolute Beta-minus-uniform mean error averaged.002670 and second-moment error.004894. The largest observed count-cell second-moment discrepancy was.046730: s=1,f=4, only two assigned-endpoint examples, exact second moment.403161 versus Beta.356430. Histories ranged from0 through8 observed submission trials. These are cohort-weighted approximation diagnostics, not measured policy reward loss.

A generic count grid s+f<=20 yields larger worst cases (max absolute mean discrepancy.304356 and second moment.248825 at20 consecutive failures). That deliberately broad algebraic grid includes histories impossible during the shipped60-day action horizon; it is not a production-state frequency/headroom claim. Legal introductions are at least8 days apart, so any endpoint available for an action day d can have at most floor(d/8) prior introductions and at most twice that many submission trials; moreover no-response-only histories yield no second stage. The actual replay counts are the relevant tested examples. No prior or fitted score was replaced after freeze.

## Review and unresolved scope

Critic independently reviewed the source timing/induction, complete-event boundary, adapted response-likelihood factorization and first-trial moment statement; no blocking objection was found. The prior pending-survival objection is explicitly corrected for legal available endpoints, while remaining for unavailable/global models. The source proof is deterministic and specific to shipped release/observation rules. The exact posterior formula is mathematical under explicit stochastic/ignorable-observation assumptions. The replay is finite implementation evidence. The Beta error is a descriptive numerical comparison. None establishes higher reward, a new optimal policy or a PRNG independence theorem. A future preregistered control could compare the exact truncated-uniform moments with the frozen Beta approximation, but this round's policy configuration remains untouched.
