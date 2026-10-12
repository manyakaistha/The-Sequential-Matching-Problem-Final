# Response posterior factorization at legal current edges

Owner: next-mechanisms researcher. Reviewer: statistics_review/director.
No inference source edits or simulator evaluations. This is a mathematical
result under an explicit stochastic interpretation, not a theorem that the
finite seeded PRNG output is statistically independent.

## Assumptions and scope

Interpret the public generator as drawing independent actor response propensities
`R_i ~ Uniform[a,b]`, with `a=.55,b=.98`, independently of actor acceptance and
second biases, hard/soft truth, scenario, arrivals/exits, initial disclosure and
decline draws. Conditional on these parameters, each scheduled introduction or
second submission uses a fresh independent Bernoulli(R_i) flag. The shared
dyadic effect, yes/no flags, delays and cancellation draws have the distributions
specified in kit.py and are independent of submission flags conditional on their
specified parameters. Dependence among nuisance parameters induced by public
history is allowed. Policies use only public history and independent policy
randomness; no private side channel, seed recovery or hidden-state action is used.

The exact seeded implementation uses deterministic pseudorandom generators, some
with keyed dyad/day streams. A proof of idealized conditional independence is
not a proof of statistical independence of every quantity when averaging a
finite family of seeds. The stochastic assumptions above are the model used for
the claimed Bayesian posterior, not an exploit of the implementation.

Let `H_d` be the entire public observation/action history through the observation
at day d: disclosed profile values/status/timestamps, arrivals, availability,
introductions, all received feedback and asks, and legal chosen actions. Let
`A_d` be the set of endpoints currently marked available. For `i in A_d`, let
`s_i,f_i` count its explicitly received introduction/second submission successes
and no-response flags respectively. A success means **any nonmissing answer**,
including yes and no; it does not mean acceptance or positive second intention.

## Theorem

Under these assumptions, the conditional distribution of response propensities
of currently available endpoints is

```
p((R_i)_{i in A_d} | H_d)
  = product_{i in A_d} [R_i^s_i (1−R_i)^f_i 1_[a,b](R_i) / Z(s_i,f_i)],
Z(s,f) = integral_a^b r^s(1−r)^f dr.
```

Moreover, this available-actor response vector is conditionally independent of
all remaining latent parameters given H_d. Those remaining parameters include
other actors' response propensities, biases, undisclosed soft values, scenario,
and past dyadic effects. It does not include the primitive uniform random
numbers thresholded to implement already conditioned Bernoulli flags, which
need not be independent of their thresholds after conditioning. Therefore for
a currently legal edge `(i,j)`,

`E[R_i² R_j² | H_d] = Z(s_i+2,f_i)/Z(s_i,f_i) × Z(s_j+2,f_j)/Z(s_j,f_j)`.

This proves the response factor **only**. The nuisance posterior is generally
not the fresh population prior, independent actor-Gaussian approximation or
independent regime mixture used by the deployed terminal scorer.

## Proof

First use the deterministic available-feedback lemma proved and independently
audited in research3/AVAILABLE_FEEDBACK_THEOREM.md. Every introduction incident
to an available endpoint has its complete event set already public: nonmutual
introductions release at assignment+8 after the latest day+7 response; mutual
ones release at date+6 after the latest date+5 second feedback. Legal endpoint
reuse cannot overwrite an unfinished interval. Thus no incident submission flag,
date/pause event or partner response remains censored for `i in A_d`.

Factor a realized complete incident introduction's probability by its generative
draws. Each member's explicit submission flag contributes R_i for a received
answer or `(1−R_i)` for explicit no response. Its responding yes/no value
contributes an acceptance or second-intention likelihood in nuisance variables;
conditional on the observed submission flag, that factor contains no further
R_i. An unused latent yes/no draw when a member fails to respond integrates to1.
Submission-time delay is drawn independently of R_i; conditional on its known
flag its observed timestamp likewise contributes only a nuisance factor.

A date is scheduled exactly after the **observed** two responding-yes
introduction outcomes. Second trials are created exactly after the observed date
happens. These stage-existence gates are deterministic functions of the earlier
observed labels, not additional Bernoulli(R_i) observations. Date cancellation,
date/feedback delays and observed pause after two positive answers contain no
additional R_i factor once all explicit submission flags and values are included.
Their probability can depend on nuisance parameters and earlier labels; that
dependence is retained in the nuisance likelihood rather than assumed absent.

All introductions not incident to any current available endpoint involve only
other actors' R values and nuisance parameters. Their completed or pending-event
likelihoods can be arbitrarily dependent among those other quantities. They
cannot introduce an R_i factor: if such an introduction were incident to i, the
complete-event lemma would already have placed it in the first group.

Conditioning on an adaptive policy's realized action sequence adds its public
history-dependent action probabilities. Those probabilities are fixed functions
of the conditioned public history (and integrated independent policy randomness),
not extra functions of latent R_i. Initial/asked fields and permanent declines
have priors/likelihoods independent of R_i. This remains true when the policy
chooses to ask a member because of that member's public response history.

Availability itself supplies no residual R_i information for these endpoints.
The current available predicate requires no exit, busy release reached, and no
observed positive pause. For all incident introductions their response values,
date/cancellation timestamps and possible pause are complete in H_d; hence the
busy/pause parts are fixed by those already conditioned observations. The
remaining no-exit/arrival restrictions involve nuisance variables independent
of R_i at generation. Historical availability observations, including before
feedback completion, are functions of already-accounted incident outcome/delay
variables and exogenous exits; after conditioning on the eventual complete
incident events they add restrictions to the nuisance factor only. They do not
create an uncounted submission flag. Exits do not erase scheduled feedback.

Consequently the full observed-history likelihood has form

`L(H_d|R,Theta) = [product_{i in A_d} R_i^s_i(1−R_i)^f_i] × G(H_d,Theta,R_notA)`.

R_i factors do not occur in G. Independent response priors then allow each
available R_i to be normalized separately by Z; all other integration/normalizing
constants belong to G. This gives the theorem and the product second moment. ∎

## Counterexample outside the available-endpoint scope

On day1 after an introduction, a member can be busy and have no response event
yet. If successful response delays are uniform1–7 and nonresponse becomes public
at day7, observing no event by day1 has likelihood

`P(no event through1 | R) = (1−R) + R*(6/7) = 1−R/7`.

There are zero explicit success/failure labels yet. The Uniform prior with
`s=f=0` is therefore **not** its current full-history response posterior. This
alone disproves extending the explicit-count result to arbitrary unavailable
actors. It does not assert that shipped busy duration reveals the mutually-
accepted gate before introduction response labels: the day+7 response maximum
precedes the earliest day+8 release, so that stronger example would be wrong.

An available actor cannot have this pending incident introduction under the
shipped timings, so the counterexample does not invalidate the theorem. Altering
busy release to assignment+1 or date+2 would invalidate its premise. An actor
sharing the same R-dependent latent prior with others, correlated response and
acceptance biases, or informative unreported events would also break the stated
factorization assumptions.

## Policy consequence and limits

Exact Uniform second moments on currently legal edges are the full-history
response posterior moments under the theorem's assumptions, rather than merely
a posterior ignoring pending evidence. Other actors' pending histories may help
infer scenario/bias/soft variables, but cannot change this available-actor
response factor after conditioning on its full resolved submission labels.
Learning actor acceptance/second bias or regime still requires the correct joint
nuisance posterior; pairwise shared effects, selection and missing-feature
posteriors do not disappear. Multiplying exact response factors by an approximate
fresh-prior full-funnel expectation remains an approximate terminal forecast.
No reward superiority, globally optimal policy or broad novelty follows.

This result is falsifiable by a legal shipped history having an available
endpoint with an unreceived scheduled incident event, by an R-dependent field/
exit/delay law omitted above, or by a remaining incident likelihood depending on
R after its explicit submission flags have been extracted. Independent review
must check these premises, not accept the conclusion from researcher confidence.
