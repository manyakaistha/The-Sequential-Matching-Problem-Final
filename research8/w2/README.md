# B1 bounded continuation and public observation bridge

Status: implemented and independently accepted for **reduced development scope**. No simulator comparison, training fit, qualified-reward asset admission or production candidate admission.

## What changed

B1 chooses from the bounded legal matching menu at **each future public-belief epoch**, including future holds and exchanges. It no longer assumes that future decisions follow greedy or static matching. Joint hidden return branches are grouped by public observations before a shared action is selected. Maximum12 future daily epochs,2000 belief nodes,10000 cumulative support entries,50000 transitions and128 joint branches; any overflow discards the entire comparison and retains a validated current parent with no reported partial value. Optional .75-second cooperative wall guard; it is not a hard process-interruption guarantee.

`bounded.py` extends the frozen reduced core without changing its source/results. It fixes both known continuation counterexamples: the future competing-edge case returns1; the future waiting case holds through the early opportunities for9/10.

`public_adapter.py` implements literal `decide(request, config)` JSON contract. It rejects hidden/future field injection, preserves False and initial declines, derives arrivals from deduplicated public arrived_day histograms rather than available counts, validates every real matching, and carries bounded public memory. Its command-line entry point is:

```bash
python3 -m research8.w2.public_adapter < request.json
```

Public legality and G fallback helpers are vendored from the governing sources with provenance, so the candidate runtime imports no generator/simulator module. The default deployment entry point currently returns **unchanged legal G actions** because no public joint model asset has passed admission. Config/memory cannot bypass this gate with a calendar or an `admitted=True` flag.

`evaluate_projection` is a functioning **offline** public-observation integration seam. A fixture provider receives a deep copy of sanitized observations; the projected clock/availability/past dyads must agree with public history, current feasible edges must be represented, unresolved/outside neighbors fail closed, outside assignments cannot touch modeled actors, and the returned real matching is independently revalidated. It demonstrates a real public wire response that holds actors under a declared finite law; it is not a calibrated deployment bridge. Actual future IDs/timers are never supplied through public wire config or memory.

## Verification

Reproduce all35 tests (old21 plus new14):

```bash
python3 -m unittest research8.tests.test_planner research8.tests.test_query_packages research8.w2.tests.test_bounded research8.w2.tests.test_public_adapter -v
```

The final suite passed35 tests and reconstructed all27 registered grid cases. Grid has four actors, three opportunities on days0/1/2, and fixed Cartesian reward values. B1 matched the exact oracle on every case: zero first-action regret,19 waits. These are fully enumerated declared toy laws, not sampled simulator episodes or evidence of panel superiority.

Recorded performance on this host:

| Workload | Maximum observed seconds |
|---|---:|
| Bounded four-actor grid solve |0.001532|
| Public200-member G fallback, direct ask |0.005145|
| Public200-member G fallback, direct match |0.051612|
| Public200-member G fallback, cold-process ask |0.040148|
| Public200-member G fallback, cold-process match |0.102775|

Cold-process timing includes startup/import/parsing/action/serialization. All tested calls met the<1s target. This is **not active B1 planning on200 members** and not a universal worst-case timing certificate. Latest records and source hashes are in `results/validation_hardening.json`; the original `results/validation.json` and adapter snapshot `history/adapter_v1/` remain preserved; asset/runtime flags explicitly remain false for live candidate planning. Existing simulator10s hard cap remains separate.

To recompute in memory without overwriting closed artifacts:

```bash
python3 -c 'from research8.w2.run_validation import run; r=run(); print(r["max_grid_regret"], r["tested_runtime_gate_passed"])'
```

## Tail diagnostic and remaining gates

The separately registered day13 diagnostic preserves a negative result: todayAB reward1/2, futureAC day13 reward9/10, permanent absorption. B1's12-epoch horizon picksAB; full oracle waits. Full initial-action regret is2/5. Thus short-grid correctness does not certify the full60-day problem. `results/tail_diagnostic.json` records **tail gate NOT_CERTIFIED**.

Before an actual reward screen, the remaining concrete work is:

1. A public-data joint model for eventual qualified reward, pause, return/released feedback, anonymous arrival profiles and uncertain exits, with whole-world validation and independent admission. `model_asset_contract.json` spells out the provenance/schema/tests. No compatible model asset is currently available.
2. Extend or validate the observation-emission kernel for actual first/date/second-stage feedback and conditioned pending histories. The existing finite core observes availability only and uses declared toy exit calendars; these are explicit model limitations.
3. A continuation tail approximation/error control or supported-state gate that survives the day13 falsifier and longer-horizon sensitivities.
4. Active planner profiling on supported public200-member workloads and a frozen new seed/control registration before any reward campaign.

These gates require implementation/data and review, not another user permission request. No new reward campaign is launched merely because the G fallback is fast. No seeds, family labels, latent generator parameters, real exit/busy timers or future calendars are policy features. Prior research archives and W1 null/falsifier records are unchanged.

Independent review: `review.md`. Closed registration: `registration.json`. Official simulator episodes:0. Fits:0.
