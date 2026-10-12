# Independent review of available-actor response factorization

10 October2026. Owner: statistics/theory critic; reviewer: director. Reviewed
RESPONSE_FACTORISATION.md, shipped availability/event-generation/observation code,
and the prior available-feedback proof. No simulator episodes, new seeds or
inference edits were needed. This review accepts the theorem under its stated
ideal stochastic assumptions, rather than treating developer confidence as proof.

## Verdict and proof check

**Accept the scoped factorization.** Let the conditioned full public history h
fix its available set A(h). For every i in A(h), every incident introduction's
submission flags and created-stage event set are completely observed. Extract
R_i for each explicit answering flag and1−R_i for each explicit no-response flag.
Their product is R_i^s_i(1−R_i)^f_i. Conditional on those flags, yes/no likelihoods,
response delays, date creation/cancellation, second-stage existence, pause and
busy-release events depend on nuisance quantities or already-fixed labels, not
an additional R_i draw. Integrating unobserved nuisance draws preserves that
factorization. Every pending introduction is nonincident to A(h), so its possibly
nonfactorized likelihood contains other response rates and nuisance variables,
but no available R_i.

Public-history-adaptive actions contribute probabilities determined by the
conditioned history and independent policy randomness. The likelihood is not
conditioned solely on the actor having been selected or remaining available:
it conditions on all the response labels and outcome/delay history that caused
that selection. Consequently adaptive sampling adds no residual R_i term.
Independent fixed Uniform priors then normalize each available factor separately
by Z(s_i,f_i), yielding mutual conditional independence of available rates and
independence from the remaining parameter vector. The separate nuisance posterior
can still be strongly dependent and different from its prior.

The moment identity E[R_i²R_j²|h]=Z(s_i+2,f_i)/Z(s_i,f_i) times
Z(s_j+2,f_j)/Z(s_j,f_j) follows. This is a full-public-history response factor
for available endpoints under this model, not merely a count approximation.
The prior1/(b−a) constants cancel in each posterior normalization.

## Attempts to falsify the claim

**Timing/hidden busy gate.** For a failed introduction, responses/no-response
labels finish by t+7 and busy release is t+8. For mutual acceptance, both intro
labels precede the date D; date/seconds/pause finish by D+5 and release is D+6.
Legal reassignment cannot overwrite unresolved busy intervals. An earlier public
unavailability observation can constrain hidden outcome/delay variables, but
those incident events are complete by the time the actor is currently available.
After extracting their flags it constrains nuisance variables only. The tempting
claim that ordinary busy release exposes mutual acceptance before both labels
is not valid with the shipped7/8 timing and is correctly rejected in the theorem.

**Second-stage selection.** A second response trial exists only after the
explicit mutual-yes intro gate and happened-date event. Counts must include
intro response flags as well as created second trials. With those earlier
labels conditioned, stage existence is deterministic; counting it again would
double-count the response likelihood. Nonresponding yes/no primitive draws can
be integrated out. Stage eligibility therefore supplies no missing factor.

**Partner pending history.** A prior partner might now be busy with another
actor and have unresolved feedback. That later introduction cannot involve the
currently available actor. It can update the partner's rate and shared nuisance
posterior, but cannot reinsert the available actor's rate into G after all of
its own incident flags have been extracted. A latent global preference regime
also belongs to G, and does not break factorization under the independent fixed
response prior. A global unknown response hyperparameter would break it and is
outside the specified model.

**Availability, pauses and exits.** Remaining available excludes an observed
positive pause and imposes arrival/no-exit/busy constraints. Given complete
incident outcomes, the first and third are restrictions on known labels/delays;
arrival and exits are nuisance draws independent of response rates. Events
continue after exits, so no response is silently censored by an exit. This does
not claim every unavailable actor's flags are complete: the current available
scope is essential.

**Unobserved event streams.** The supplied day1 counterexample is valid: for an
unavailable actor with uniform1–7 successful response delay and no event yet,
likelihood is1−R/7 despite zero explicit labels. Counts alone do not characterize
that actor's posterior. Earlier busy release, R-dependent delays/exits/disclosure,
correlated actor response/bias priors, shared response-rate hyperparameters,
informatively omitted event labels, or private-state policy actions would also
invalidate one of the proof premises. None is a shipped public mechanism under
the stated idealization.

## Required limits retained

Conditioning primitive uniforms on Bernoulli threshold outcomes can correlate
those primitive draws with R; the claimed independence is for the parameter
vector, not all past/future random outcomes. The theorem explicitly excludes
that overclaim. Actual seeded PRNG implementation does not itself establish
fresh statistical independence across its finite seed distribution, and the
proof is properly conditional on the independent-stream interpretation.

The terminal scorer still approximates posterior soft values, actor acceptance/
second biases, regime dependence and selection. Exact response moments do not
make its joint funnel expectation exact or calibrated. The acceptance-shrinkage
posterior is separately approximate. No optimal matching, reward improvement,
program-wide superiority, or broad literature novelty follows from factorization.
Available-actor rates being independent of nuisance parameters also does not
make nuisance parameters independent of each other.

No blocking correction requested. Preserve the explicit full-history, complete
incident-event, fixed-independent-prior and ideal-stream qualifiers in any final
report. Predictive and reward value remain subject to the registered experiments.
