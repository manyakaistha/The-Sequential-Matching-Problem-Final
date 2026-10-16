# Independent training and seed-method review

2026-10-15; `/root/continuation_critic`, reviewer of integration `/root`.
Read-only train.py, TRAINING_PROTOCOL.md, split metadata and bounded historical
seed inventory; no actual research row/outcome extraction, fitting or episodes.
Allowance90 CPU seconds/five minutes.

## Training receipt: fixes required before fitting

The core modeling design is consistent: fixed direct/funnel families, train-only
standardization/calibrated agreement control, inherited unconditional cell
weights on conditional risk sets, minimum-support stage backoff, validation-only
family choice, and only the selected family evaluated on development-test.
The code reports terminal losses/calibration and selected-family gate failures
rather than treating all-stage prediction wins as policy proof. It preserves
one immutable asset and report. Five bounded issues were returned to the director:

1. **Rebind derived input.** NPZ file count and extractor source hashes alone
   do not authenticate dataset contents or the exact Cartesian grid. Before
   fitting, validate each immutable extraction receipt's source identity,
   output path/hash/length, cell identity and metadata; require exact2880
   seed/family/arm cells, metadata/group_seed consistency and the correct
   feature contract. Validate64/16/16 unique disjoint split groups, exact
   original96-seed coverage and the frozen split identity. Do not silently
   ignore rows outside split masks. Extraction receipts already contain the
   required bindings; a large raw-history walk is unnecessary.
2. **Constant prior mismatch.** fit_logistic with zero feature columns still
   optimizes its unpenalized intercept to the weighted MLE in a mixed-class
   sample. This is not the protocol's Jeffreys-smoothed constant. Construct
   the declared weighted-smoothed constant explicitly, with its normalization
   fixed; retain the independently fitted intercept+slope agreement control.
3. **Support gate versus ranking exception.** An early assertion on held-out
   positive counts aborts fitting even though predictive-support failure is
   predeclared to disable probability/D admission while retaining exploratory
   A/B/C ranking. Put those counts into the probability gate; retain hard
   stops for invalid data, leakage, numerical failure and protocol violations.
   Preserve every failed support condition explicitly, without more data.
4. **Empty conditional cohort.** np.average on an empty risk set raises before
   the declared low-support backoff. Freeze a zero-trial smoothed constant
   (e.g.1/2) or an explicit no-model rule before fitting. Never discover and
   improvise its prior from held-out outcomes.
5. **Bootstrap label.** The implemented.975 percentile is the upper endpoint
   of a two-sided95% percentile interval, more conservative than a one-sided
   95% bound. Label it precisely and retain the fixed rule. There is no need
   to loosen it after seeing scores.

Current equal-cell weights imply equal seed/family/arm influence when every
cell contains rows. If any complete cell has zero assignments, prediction loss
there is undefined: disclose empty cells and either freeze an explicit
observed-edge estimand with equal per-seed averaging, or verify no empty cells
before asserting exact equal seed weights. Conditional-stage fits correctly
inherit original row weights rather than renormalizing each selected cell.
Bootstrap draws must operate on seed loss summaries, as the current code does.

The training code can compute predictions for both assets on unlabeled feature
matrices, but only the chosen family's development-test metrics may influence
reports/gates. No family replacement, refit or split repair after those scores.
Validation-selected losses are development evidence, not an unbiased certificate.
Code/source/protocol hashes must be frozen again after these pre-fit repairs;
old extraction hashes and source captures remain untouched.

## Final seed-method decision

**Accept independent prospective random draws under explicit historical-scope
limits.** A convenient small consecutive range lacks universal nonreuse evidence
because deleted/private/archive history is unresolved. That does not require an
unbounded search when a new independent randomized design makes overlap
negligible and the limits are honestly disclosed.

Generate exactly96 unique seeds uniformly from[2^127,2^128), using independent
cryptographic draws, before final outcomes. Preserve the first draw/reservation
ledger, algorithm, time and hashes; do not outcome-search or range-search.
Resampling is allowed only for duplicate draws or documented visible prior
reservation/use, recording every rejected draw and reason. Keep the draw
independent of model/policy performance. Reserve once and never silently replace
seeds following errors or outcomes. Verify all downstream code preserves full
Python integers: no float, JavaScript Number or NumPy int64 narrowing. The
simulator/hashed introduction RNG must receive the exact recorded seed.

Check all feasibly indexed repository-visible registrations, reservations,
commits and compressed catalogs, including existing provenance digests. State
omissions explicitly; do not remove old raw directories from the claimed scope
or pretend an index certifies history it never covered. The bounded inventory's
unresolved125 deleted seed-bearing items, private/external runs and uninspected
payloads remain unresolved; a high-number draw does not prove those never existed.

For any fixed unseen set of B earlier seeds independent of the new draw,
P(any prior overlap)<=96B/2^127 by the union bound (using all B is conservative
when only some lie in the sampling range). For illustrative B=10^12 the bound
is about5.65×10^-25. This is conditional arithmetic, **not** a certified count
of old history. Uniqueness rejection removes within-campaign duplicate clusters;
visible-overlap exclusions must be fixed/recorded and are independent of outcomes.

Describe the set as “prospectively independently randomized seeds, with
repository-visible nonoverlap; universal historical nonuse remains unverified.”
This supports a statistically separate prospective confirmation experiment under
ordinary seeded-simulator assumptions and negligible disclosed collision risk.
It is not a universal freshness certificate. The source/asset freeze, fixed96
clusters, hierarchy, complete audit and no outcome-based replacement remain
mandatory; a random-seed method does not waive any other campaign gate.
