# Stage A exact-model developer record

Owner: `/root/exact` (Astra/high). Named independent reviewer: director-assigned
Sol/high critic. CPU allowance: 300 seconds; no simulator worlds, seeds, fitting
or empirical confirmation authorized or used. Scope: `research6/exact/` and this
developer record, with director-authorized constructed artifacts under
`results/research6/stage_a_exact/` and `stage_a_exact_v2/`. Prior research and
results were read only and preserved.

**Outcome.** All 23 named rational models and 79 fixed additional graph/horizon
cases pass. The generated MDPs contain 2,231 states. The proposed renewal LP has
a valid conditional ideal-stream proof even for adaptive public histories;
using unconditional population coefficients after adaptive history selection
does not have that justification and admits exact counterexamples. No
full-simulator numerical bound or candidate policy superiority is established.

## Executed evidence and source amendment

Initial command `python3 -m research6.exact.run` created
`results/research6/stage_a_exact/20261011T041946.639650Z/`, with 0.434292 CPU seconds
reported by the runner. It registered model specifications and source hashes
before solution evaluation. Subsequent development made the public-history
conditioning example an executable rational type table, added focused tests,
and added the written proof. Consequently the live `run.py` no longer matched
that first registration. The reviewer identified the discrepancy; no original
output or manifest was rewritten.

The exact original four registered Python sources are retained under
`research6/exact/history/v1/`. Their bytes were checked against every original
registered hash. In particular original `run.py` was reconstructed by reversing
the known amendments and matched SHA256
`6c4edbe142187255440a70ac66b631f795256dd0106166ebaf1db3ca14ca41b8` exactly. This
restores reproducible source attribution; it does not claim those snapshots
were captured contemporaneously with the first execution.

The finalized command

```
python3 -m research6.exact.run --output-root results/research6/stage_a_exact_v2
```

created `results/research6/stage_a_exact_v2/20261011T042343.113219Z/`, reporting
0.497276 CPU seconds. Before solving, it saved source **bytes** under `source/`,
their hashes, the explicit specifications, and the registration. Its result
agrees with the initial mathematical values. `models.json` contains complete
explicit state/action/transition tables; `solutions.json` contains every
Bellman action value, the constructed validation checks, and exact LP
certificates. `summary.json` hashes the JSON evidence. Snapshots make later
source changes distinguishable without orphaning the registered source hash.

`python3 -m unittest research6.exact.test_exact` passed six tests in about
0.324 elapsed seconds as printed by unittest; test CPU was not separately
recorded. Tests check all named
values, exhaustive four-node matching enumeration by a different recursion,
rejection of invalid probability/cyclic models, final-day reward and no-repeat
behavior, every held-out Bellman action against full-policy enumeration, and
LP primal/dual feasibility including rejection of a false dual. The explicit
runner and tests together use well below the 300 CPU-second ceiling. Filesystem
reads and tool overhead were not centrally measured as CPU usage.

## Strongest case, criticism and resolution

The strongest constructive case is joint decision structure: complementarity
can give two individually worthless bundles positive joint value; collision
can make degree sums overstate introductions; and shared future alternatives
make additive continuation penalties double-count losses. Each is demonstrated
with exact rational values in a completely specified finite model.

The strongest opposing case is scope. Tiny examples do not measure the mass
of such opportunities in the simulator, and larger models expose different
feedback and latent-parameter structure. Degree, cardinality and throughput
proxies each have explicit losing cases. No new policy is admitted or promoted
by this record. Admission requires the director's fidelity and mechanism gates.

An A1 statement needs narrowing: no return of the exploratory pair does not
imply no learning value if a shared latent regime governs other later pairs.
The added no-return counterexample raises later choice value from 1/2 to 1.
The sound zero-value statement requires no later decision affected by the
observation. The proof and scope in `research6/exact/THEORY.md` preserve this
negative finding rather than forcing the requested conclusion.

The occupancy theorem relies on nonanticipation, conditionally independent
unused assignment streams, fixed latent parameters, and no gap between busy
occupancy and a later permanent pause. The shipped timing has the required
no-gap structure: pause by date+5, busy through date+6. Conditional on fixed
latents, adaptation to public history does not destroy fresh-stream
independence. Without that conditioning, the constructed duration-selection
example makes the naive expected-capacity sum 5/4 for a legal schedule whose
actual expected occupancy is 1. A corresponding reward example gives 1/2
actual expectation versus 1/4 from multiplying prior q by assignment rate.

The three tiny LPs have rational primal/dual certificates. Full-simulator
coefficient integration and outward numerical enclosures remain unimplemented;
floating quadrature and an LP objective alone cannot certify the proposed
simulator bound. Finite keyed pseudo-random generation is not a mathematical
proof of independent ideal streams. A conditional expected bound is not a
pathwise realized-reward bound.

## Reviewer handoff

The development policy enumerator is a different algorithm written by this
same developer, so it does not close the plan's independent-review gate. The
director reported that the critic's separate rational check agreed on 102
models, 2,231 states, 1,512 actions and LP certificates; that claim belongs to
the critic's own retained report. The final v2 source snapshot and proof still
require the independent reviewer's direct check and closure. This file makes
no independent-review approval on that reviewer's behalf.

The theorem and counterexamples are **proved under explicit ideal/reduced
assumptions**; toy solutions and rational LP certificates are **exact simplified
calculations**; connection to frequency of simulator opportunities is an
**unvalidated hypothesis**. There is no new empirical finding about policy
reward, no fitted model, and no full-simulator optimality claim.
