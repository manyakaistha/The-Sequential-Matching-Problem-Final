# Round four primary-literature and novelty review

Reviewer: next-mechanisms researcher; named reviewer: statistician/director.
Question: are bundled acquisition, actor shrinkage or truncated-uniform response
updates broadly new? **The retrieved evidence does not support broad novelty.**
Three search calls and three page opens; no inference change or simulation.
Sources distinguish original papers, official mathematical documentation, and
our own simulator-specific deductions. This small review is not an exhaustive
priority search.

## Acquisition before the decision

Krause and Guestrin, *Optimal Value of Information in Graphical Models*, explicitly
study selecting expensive observations before an eventual decision, both as a
subset and as a conditional observation plan. Their abstract gives tractable
restricted-model results and hardness results for broader graphical models.
Thus choosing information for decision quality, rather than only entropy, is an
established idea. Our coordinated-goal policy is a fixed budget/timing heuristic;
it does not compute their optimal value of information and inherits no theorem
from their model. [Author paper, arXiv](https://arxiv.org/abs/1401.3474)

Chen and Krause, *Near-optimal Batch Mode Active Learning and Adaptive Submodular
Optimization* (ICML2013), is a closer title-level precedent for grouping
observations into batches. The publisher abstract concerns reducing labeling
effort through active learning. This review retrieved the publisher record,
not the full proof; it does not transfer an adaptive-submodular approximation
factor to our nonlearning same-day query heuristic. [Primary publisher record](https://proceedings.mlr.press/v28/chen13b.html)

Krause and Guestrin's *Near-optimal Nonmyopic Value of Information in Graphical
Models* also appeared in the primary author-hosted search record. Opening that
PDF timed out, so no detailed claim here relies on its theorem or proof. The
failed retrieval is preserved in the command ledger; it is not represented as
full-text review. [Author-hosted PDF](https://www.cs.cmu.edu/~guestrin/Publications/UAI2005/uai2005.pdf)

**Simulator-specific distinction:** one shipped ask batch legally discloses both
hard feasibility and goal on an available endpoint; the later match invocation
sees both. Previous surplus acquisition excluded endpoints not yet verified.
Coordinated acquisition sacrifices the fourth hard bundle to influence the first
pair choice of the other three. This is an implementation/timing contribution
to this benchmark, pending controlled reward evidence. It is not a new general
experimental-design principle. Budgeted information can help or harm through
occupancy and lost verification opportunities, so a positive information theorem
without the same costs/continuation model would not establish policy improvement.

## Actor shrinkage and Gaussian moment matching

Minka, *Expectation Propagation for approximate Bayesian inference* (UAI2001;
arXiv posting2013), describes approximate inference retaining expectations such
as mean and variance, and connects it to assumed-density filtering and belief
propagation. Retaining a Gaussian mean/variance after non-Gaussian evidence is
therefore established. Our actor update reweights five fixed Gaussian-prior
quadrature nodes with all included likelihoods and only then collapses to a
Gaussian; it is **not** EP's iterative site-consistency algorithm or a claim of
equivalent posterior accuracy. [Original-author paper record/abstract](https://arxiv.org/abs/1301.2294)

Hernández-Lobato and Adams, *Probabilistic Backpropagation for Scalable Learning
of Bayesian Neural Networks* (ICML2015), sections3/3.1 explicitly discuss
approximating a likelihood-reweighted Gaussian by matching its posterior mean
and variance, within assumed-density filtering. This is a useful concrete
computational precedent. Our policy is a tiny actor-bias model, not a neural
network, and its ignored regime/partner dependencies remain additional
approximations. Paper results on neural-network prediction do not validate
our terminal calibration. [Retrieved primary full PDF](https://proceedings.mlr.press/v37/hernandez-lobatoc15.pdf)

**Simulator-specific distinction:** current available endpoints have all prior
own-introduction feedback resolved under the shipped busy-release timings.
Hence explicit responding yes/no labels are usable without pending-label
imputation. The .7 acceptance-bias prior is given by the source, not fitted.
This motivates cheap shrinkage but neither makes the approximation exact nor
constitutes a new Bayesian-learning method.

## Truncated response posterior

NIST DLMF8.17.1 defines the incomplete beta integral
`B_x(a,b)=integral_0^x t^(a−1)(1−t)^(b−1)dt`. This official formula directly
expresses the finite-interval likelihood normalizer. [NIST official definition](https://dlmf.nist.gov/8.17.E1)

**Our deduction:** Uniform[.55,.98] prior plus observed Bernoulli successes/failures
gives density proportional to `r^s(1−r)^f` on that interval, i.e. a
Beta(s+1,f+1) kernel restricted and renormalized there. With
`Z(s,f)=B_.98(s+1,f+1)−B_.55(s+1,f+1)`, its kth moment is
`Z(s+k,f)/Z(s,f)`. This follows by Bayes multiplication and the cited integral;
the NIST page is not asserted to prove an adaptive-observation posterior theorem.
For integer counts, rational polynomial integration avoids floating cancellation.
None of these algebraic operations is a new general estimator. The useful
benchmark question is whether replacing a moment-matched Beta approximation
changes decisions or reward enough to justify the exact arithmetic.

## Generalization and unresolved novelty

Potential generalizable lesson: eligibility verification and preference
acquisition may complement each other when one decision observes a whole batch,
and public availability/release rules may simplify feedback censoring. These
require actual costs, legal simultaneous disclosures, stable latent actor
parameters and complete-event timing comparable to this simulator. The exact
uniform posterior requires the stated prior/support and ignorable observed trial
selection; a real population need not satisfy them. Broad novelty remains
unverified; a reproducible controlled benchmark result, positive or negative,
is the defensible contribution currently sought.
