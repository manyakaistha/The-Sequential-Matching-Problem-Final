# Independent fresh-test design review

Prepared, **not executed**, 10 October 2026. Owner: empirical statistician/adversarial reviewer; named reviewer: director. Accept the fixed design for execution under its stated assumptions, not as evidence that the policy defeats greedy. No new simulator world, policy invocation or empirical episode was generated during this review. No sealed round-four file was edited.

## Hypothesis, multiplicity and power

The unchanged frozen population_control-versus-shipped-greedy comparison is well defined. The primary unit is the six-family mean paired difference for each independent seed; the 5,160 episodes are not 5,160 independent clusters. Previous 56 E clusters are excluded from the new primary. Previous outcomes inform variance/cost, not fitting or pooled salvage.

The finite family contains four valid primary comparisons and uses common two-sided alpha .0125 / 98.75% intervals for any new family-level claim. This is Bonferroni-valid for those four tests without requiring independence between them. Historical reports remain preserved; their original .05/.016667 gates cannot be mixed with the new .0125 gate and described as a .05 family rule. The registry explicitly fixes this distinction. This is not an anytime-valid or unlimited-research-round guarantee.

Independently calculated noncentral-t positive-tail rejection power, assuming normally distributed independent cluster differences, agrees with the registration:

| Fixed n | Power if true gain .05 and SD .26 |
|---|---:|
| 389 | .8997148441 |
| 390 | .9005724289 |
| 430 | .9299681381 |

Thus minimum n390 and ceil(1.10×390)=430 are correct. The SD .26 exceeds both observed C .252618 and E .227585, but finite past estimates do not guarantee the future variance. Distribution shift/heavier tails, smaller true effect and correlated nominally distinct seeds can reduce actual power. The retained sensitivity table matters; the 93% figure is model power, not a simulator guarantee.

The design powers rejecting **zero** when truth is +.05. It does not power proving a gain above +.05 when truth is exactly +.05. The latter requires the separately declared adjusted lower bound >.05. A positive point estimate or nominal-only interval does not pass the superiority gate. The full fixed sample, no peeking, no extension, no substitution, no retuning and no pooling rules prevent significance-driven sample expansion. A nonsignificant result does not establish equivalence.

## Freshness and immutable scope

The proposal is exactly seeds 90001–90430, all six families, two policies. Independently checked design/preflight shows zero intersection with the recorded blocked inventory, including the inherited guard and all round-four actual/planned/reserved blocks. This is repository-recorded freshness, not proof against unknown external examination. No proposed world was created to assess freshness.

Registered design SHA256 at review is:

`1a4e1b3cee790ee87ccdb4704ed294622ccc51f130181813ffc98dd060202ee6`

The design is a trusted immutable registration and must remain unchanged. Its whole-file SHA should be checked against this review/preparation record before launch; the preflight uses design.json as its source of expected hashes and does not self-authenticate every design field by hashing the file against an external anchor. Do not alter alpha, family, sample or configuration and then treat the changed file as the same registered test.

Frozen host simulator/evaluator/recorder/inference hashes, deployed initializer hashes, new setup source hashes, reused research3/analyze.py hash, registry hash and prior sealed manifest hash are checked. NumPy/SciPy versions are checked. The review identified the initially unbound analysis helper; the director corrected it before preparation. An explicit all-family command and full 60-action-plus-40-follow-up metadata checks are present. This review checks the frozen bytes now; a source hash does not independently prove semantic correctness by itself.

## Independent runner and analyzer checks

I read prepare.py, run_test.py, analyze.py, the reused analysis helper and registry. `run_test --check` passed without episodes. Mocked inherited hash alteration and mocked analysis-helper hash alteration each failed preflight; these mocked calls did not modify files.

Using a temporary directory and deliberately fabricated public result rows, I exercised the analyzer's full 430-cluster/5,160-row grid. The fabricated nonzero effect produced the expected adjusted gates. Duplicate-cell, missing-cell, invalid-episode and fallback-episode fixtures were each refused. This isolated analyzer/grid logic by mocking only the design preflight; it does not test real-world action quality or represent a simulated result. Temporary fixtures were deleted. Synthetic audit consumed 2.591813 process CPU seconds; other preflight/power checks were subsecond, within the 60-CPU-second review allowance.

The inherited analysis helper validates completeness, uniqueness, exact paired six-family cells, valid status, failure/fallback counts and seed plan before computing uncertainty. The new wrapper separately checks invocation count, 200-member denominator, score identity, horizon metadata and frozen comparison. Complete-grid inference uses a paired seed t statistic and whole-seed bootstrap sensitivity; bootstrap cannot replace the primary gate. Zero-variance edge cases are conservatively not declared superiority by this implementation.

The runner refuses prior or partial outputs and records actual OS child CPU, full command, status and wall time. It preserves a failed run rather than replacing bad seeds. No automatic missing-job recovery exists. Any future deterministic recovery needs a separate reviewed protocol retaining the original fixed sample and all failures; it cannot expand the test until significance. Two simulation workers are separate from the policy's per-invocation resource cap.

## Criticism, cost and final-claim conditions

This is a larger fresh replication of an existing uncertain hypothesis, not a new candidate search. A prior positive point estimate can still regress. Reusing the same simulator and inference source makes statistical replication distinct from independent implementation replication. Matched seed streams do not make changed dyads share all outcome draws, and no causal interpretation follows from descriptive chosen trajectories alone.

Historical cost extrapolation gives approximately 6,769 wall seconds, 13,471 OS CPU seconds, 56.7 GB raw traces and 3.1 GB compressed traces, excluding analysis/replay/archive overhead. Nonlinear I/O, workers, host load and trace compression can change cost. The free-space guard adds a 30% raw margin; it is not a universal storage guarantee. No external paid spend is registered.

Before any final superiority claim, the registry requires independent full-cluster/count/statistical reconstruction, 48 selected/baseline direct/subprocess replays on the specified two completed seeds, restricted-container/source/resource rechecks, lossless archive verification, written review and a new provenance manifest. A provisional positive analysis is not the completed reviewed result. No additional confirmation is authorized by this design regardless of outcome.

No current scientific blocker remains. The setup is ready; it contains no confirmation evidence. Preserve the sealed prior studies and the registered design, and execute only the entire fixed test when the director/user initiates it.
