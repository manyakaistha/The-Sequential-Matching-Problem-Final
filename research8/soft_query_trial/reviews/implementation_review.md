# Independent Implementation & Observation-Scope Review: Research 8 Soft Query Trial

**Date:** 2026-10-14  
**Scope:** Review of `research8/soft_query_trial/policies/`, `targeting.py`, `metrics.py`, `runner.py`, `launcher.py`, and `test_policies.py`.  
**Disposition:** **APPROVED FOR FROZEN REGISTRATION & EXECUTION GATE**.

---

## 1. Compliance with Experiment Mandate

1. **Policy Arm Isolation:**
   - **Arm `G`:** Calls `kit.baseline_asks(state)` and `kit.baseline_match(state)`. No added soft queries. Exactly identical to frozen Greedy reference.
   - **Arm `G_random_soft`:** Preserves exact `baseline_asks(state)`. Computes remaining budget `12 - len(hard_asks) * 3`. Randomly samples from candidate set $\mathcal{C}$ without replacement using deterministic policy salt `research8_g_random_soft_v1` and public `day`. Uses exact `baseline_match(state)` post-answers.
   - **Arm `G_targeted_soft`:** Preserves exact `baseline_asks(state)`. Fills remaining budget with targeted questions from candidate set $\mathcal{C}$ using the registered priority and tie-breaking rules. Uses exact `baseline_match(state)` post-answers.

2. **Candidate Set Parity ($\mathcal{C}$):**
   - Both random and targeted filling sample from the exact same candidate set $\mathcal{C}$:
     $$\mathcal{C} = \{(u, k) : u \in V_{\text{available}}, k \in \text{SOFT}, \text{status}(u, k) = \text{'not\_asked'}, \text{fields}(u, k) = \text{None}, n_{\text{obs}}(u, k) \ge 1\}$$
   - Direct comparison opportunity ($n_{\text{obs}} \ge 1$) is strictly required for both arms.
   - Questions for observed or declined fields are strictly excluded.
   - Boolean `False` is not treated as missing.

3. **No Displacement of Hard Bundles:**
   - Hard queries are always computed first and placed at the beginning of the returned query array.
   - Soft query count is bounded by `max(0, ask_budget_remaining - len(hard_asks) * 3)`.
   - If 4 hard bundles are selected (cost 12), soft budget is 0.

4. **Public Observation & Sandbox Integrity:**
   - Decisions consume only sanitized public observation dicts (`state['members']`, `state['introductions']`, `state['day']`, `state['ask_budget_remaining']`).
   - No simulator seed, family variant, latent truth vector, response propensity, exit day, or arrival schedule enters policy inputs.
   - Member identifiers are treated strictly as opaque string keys for tie-breaking.

5. **Metric Layer Correction:**
   - Endpoint is verified:
     $$Y = 100 \times \frac{\text{qualified\_introductions}}{\text{arrived\_members\_by\_day59}}$$
   - Each qualifying dyad is counted once. The factor-of-two reporting inflation from historical P4 is eliminated.
   - Unit of statistical inference is the seed cluster ($D_s = \frac{1}{6} \sum_f \Delta_{s, f}$), analyzing 24 seed clusters across the 6 families.

6. **Process & Resource Guard:**
   - Simulator worker processes are strictly capped at 3 (`max_workers = 3`).
   - Cached directory sizing prevents coordinator scheduling freezes.

---

## 2. Test Suite & Fixture Coverage

The test suite in `research8/soft_query_trial/tests/test_policies.py` implements all 17 specification conditions and 6 tiny fixtures:
- Fixture 1: Isolated node $\to$ 0 soft queries.
- Fixture 2: One informative neighbor $\to$ creates eligible candidate.
- Fixture 3: Two neighbors with conflicting answers $\to$ Priority 1 over Priority 2.
- Fixture 4: Revealed soft answer flips Greedy edge selection.
- Fixture 5: Single legal edge $\to$ revealed answer does not change match.
- Fixture 6: 4 hard bundles (cost 12) $\to$ 0 soft queries.

**Conclusion:** The implementation is certified correct, fail-closed, and compliant with all governing research protocols.
