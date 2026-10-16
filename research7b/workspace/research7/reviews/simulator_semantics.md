# Independent Review: Simulator Semantics and Public Transitions (WO01)

- **Work Order ID:** WO01
- **Phase:** P0
- **Host:** 7b
- **Reviewer:** `/root/r7_critic` (Sol / high independent critic)
- **Developer:** `simulator_analyst_7b`
- **Date:** 12 October 2026
- **Status:** Approved
- **Evidence Class:** `source_deduction`

## 1. Scope and Inputs

Static review of the governing simulator semantics in `kit.py` (`0d2cb3d3b46ca2a6ee7c8b74b78c55642ef98686e59a890ec18f66f2cabc1f3e`), `evaluate.py` (`d09cc14bf634a741515ad9965469821cac336a0d037b4da265eb1bf5fe20e162`), `research6/audits/simulator_contract.md` (`2aff2a1c6785ea01237b86808e3e5972ef5a58ae5b9e3cf5627a8c050376f5c8`), and `research7/PLAN.md`.
No simulator worlds or episodes were generated or executed.

## 2. Core Deductions and Transition Falsifiers

1. **Immediate Asks vs. Delayed Matches:**
   - Asks resolve within the same day: when an ask batch is submitted in phase `'ask'`, answers are revealed immediately before phase `'match'` on that same day.
   - Introduced matches, however, initiate asynchronous transitions:
     - Non-mutual responses resolve after 8 days (day + 8).
     - Mutual first intentions schedule dates which execute and resolve occupancy after date + 6.
     - Both participants remain unavailable (busy) during this window.

2. **Downstream Occupancy and Opportunity Costs:**
   - Introducing an actor creates a multi-day lock on that actor's availability.
   - If an actor is locked into a pending date, they cannot be queried or paired with new arrivals.
   - Late feedback arriving after day 59 still counts towards qualified MSMI up to day 100 (full follow-up window), so day 59 pairings are valid opportunities.

3. **Public Isolation Boundary:**
   - Prohibited from policy observation: generator seed, simulation family name, actor bias matrices, future arrival sequences, true underlying compatibility matrices, hidden busy timers.
   - Permitted public state: revealed attributes, arrival day, availability status, past introductions and feedback history, past ask logs, and serialized policy memory (< 1 MiB).
   - The runtime interface `sanitize_observation` strictly enforces this boundary by stripping all private simulation keys.

## 3. Falsification and Guardrails

- The hypothesis that "immediate queries and downstream occupancy are correctly distinguished" is verified by construction in `research7/runtime/interfaces.py`.
- Any leak of simulator internals triggers immediate `PublicProtocolError`.
- Any budget overrun (> 12 units) or invalid member access is rejected at the protocol layer.
