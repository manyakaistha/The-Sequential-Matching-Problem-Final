# Independent Review of the Seven-Worker and Coordinator Dispatch Optimization Amendment

14 October 2026. Reviewer: Independent Reviewer (Sol high) / Statistical & Scientific Integrity.
Host: 10 physical cores, 16 GiB RAM, external APFS results drive.

## Summary of Amendment
Following the user's explicit directive ("use 7 workers as we still have some idel cpu. and ample ram") and authorization to apply Option 2 optimizations:
1. **Worker Capacity**: Simulator cell worker cap raised from 6 to 7 (`CAPS['max_workers'] = 7`). Agent delegation slots remain governed by AGENTS.md (at most 4 active slots; 3 child agents max).
2. **Coordinator Dispatch Optimization**: In `launcher.py`, `verify_registration(reg)` was relocated so that it executes immediately before dispatching new cells to available workers (`if queue and len(pending) < workers:`), rather than during every 100ms idle poll of the active worker wait loop. This eliminates continuous re-reading and SHA-256 hashing of registration and freshness files when all worker slots are saturated.
3. **Seed Inventory Scope**: In `registration.py`, `seed_inventory` excludes the historical `results/` run directory and temporary directories from recursive file matching. This eliminates 4.3 million `.json.gz` episode outputs from being recorded into `archives_not_decoded`, reducing the freshness audit artifact from 557 MB to ~2 KB.

## Verification
- Unit & Enforcement tests: 83 passed, 2 subtests passed in 17.87s.
- Guard test parametrization updated to verify that worker counts of 1..7 are accepted and counts >= 8 are rejected.
- Declared capture integration audit: Verified 100% parity and public event reconstruction.
- No simulator physics, candidate generation, or policy decision logic was modified.
