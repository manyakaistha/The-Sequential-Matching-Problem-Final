# Independent round-four candidate review

10 October2026. Production reviewer; named reviewers: director and statistician.
Concrete question: do eight configurations produce legal observation-only queries
and matches, and does the response posterior compute its specified public model?
Falsifiable hypothesis: no protocol or arithmetic violation on supported test
states. Exclusive owned files: this document and test_candidates.py. Candidate
source was read-only; reviewed SHA256
`f9f3bf1ef5d949a17c58a1b8abac76e82a84228a97c143fe3b29a403e7e5096c`.
Allowance60CPU seconds; three small suite runs took less than3 measured wall
seconds total, CPU not instrumented. No fresh simulator seeds or training were
generated. Reviewed existing seed101 observations and constructed public states.

## Observed checks

`python3 -m unittest -v research4.test_candidates` passes7 tests (final run0.757
seconds). All eight configurations satisfy response shape, endpoint availability,
budget, duplicate-query exclusion and declined-query exclusion. Matching checks
verify hard feasibility, endpoint-disjointness and dyad nonrepeat. A ten-endpoint
fully feasible constructed state produces5pairs per configuration; excluding one
endpoint yields4pairs, while a prior completed dyad cannot repeat. Thus tests do
exercise nonempty matching, rather than relying only on an initially unverified
pool. Empty pools, exhausted budget and hard/soft permanent declines produce
appropriate empty actions. Greedy-control actions exactly equal shipped baseline.

Coordinated querying is accepted by actual Simulator.resolve_asks: four eligible
hard-unknown members at budget12 produce three constraints bundles and three goal
queries to the same selected members. Both hard and goal statuses become observed
in that batch, consuming exactly12units. This is a legal public mechanism. It
does not prove those endpoints subsequently have partners or that the strategy
increases reward. With only three hard candidates, the surplus control also has
three units left; coordination creates a tradeoff when a fourth candidate exists.

Uniform-response E[R²] matches an independently expressed rational polynomial
integral at (successes,failures)=(0,0),(7,7),(7,0),(0,7), including exact prior
moment. Values stay within[.55²,.98²]; successes raise and failures lower the
moment. The tested arithmetic is exact before conversion to float. Finite horizon
bounds and rational integration avoid cancellation from floating polynomial sums;
this review does not establish all-cache-shape latency bounds.

Acceptance likelihood is finite and strictly between0and1 for extreme observed
equalities, missing-feature mixtures, biases−2,0,+2 and days0,35,59. One uncertain
Bernoulli feature is explicitly marginalized before sigmoid: probability at
equality prior.5 equals the mean of the two deterministic feature probabilities.
It is not sigmoid of expected fit. Own yes/no public introduction responses move
actor posterior means in the expected directions; variance remains finite and
nonnegative. Pending events and explicit nonresponse do not create acceptance
labels. Response-propensity counts separately use received response/nonresponse
events, including later-stage responses, consistent with the reused public
response propensity.

## Deductions and approximations

Matching uses the independently reviewed round3 legal-edge generator, observation
members and public event histories. No seed, hidden truth, world labels, files or
network are used by candidates. Current observed features may revise compatibility
of earlier introductions; this is available information at current invocation,
not assignment-time retrospective leakage in the evaluated policy.

The acceptance updater is an approximate actor posterior. Five-node Gaussian
quadrature, moment-matched Gaussian collapse, independent regime mixing across
trials, ignored partner/shared-effect posterior conditioning and default second-
intention actor priors are explicit approximations. It only models own yes/no
conditional on response; independence of latent response propensity and own
acceptance bias is inherited from the public generator. Current-feature-only
compatibility excludes unavailable future disclosures. The hard-priority completion
weight omits several unknown constraints and approximates cross-zone completion;
it is a ranking proxy, never a substitute for verified legal matching.

No correctness blocker was found in this tested scope. Candidate arithmetic and
query legality do not establish calibration, reward gain or novelty. Serious
promotion still needs registered seed-cluster comparisons and own-architecture
controls. The director must supply JSON/request/memory validation, interrupting
deadline guard and legal fallback as candidates.py documents. Container parity,
restricted-resource enforcement and actual deadline tests for that new wrapper
are future production obligations; round3 deployment evidence cannot automatically
certify an altered round4 wrapper.
