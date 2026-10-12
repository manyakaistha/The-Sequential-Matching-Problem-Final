# Independent model-routing implementation review

Reviewer: `/root/routing_review`, routed as `gpt-6.1-sol` / `medium`; accountable reviewer: `/root`. Scope: `AGENTS.md`, `research6/agent_routing.json`, `research6/agent_router.py`, and the role contract in `research6/ORCHESTRATION.md`. All other project files remained read-only. Checks used constructed work orders and in-memory configuration copies; no model API calls, simulations, seed worlds, training, fitting, or experiment launches occurred.

## Observed checks

The initial checked-in routes correctly map all 16 task categories: discovery/reading/mechanical checks to Luna low, structured extraction/indexing to Luna medium, bounded implementation/review to Sol medium, simulator/predictive/statistical/production/adversarial work to Sol high, and demanding proof/planning to Astra high. Every constructed default payload includes explicit model, effort, and `fork_turns="none"`. The actual collaboration tool schema supports that override combination; a full-history fork would not.

Constructed Python and CLI checks passed:

- All 16 default category payloads and all five declared escalation edges.
- Twenty blank, whitespace, missing, or non-string required evidence fields rejected.
- Fourteen invalid task/name/slot/budget/escalation cases rejected, including unapproved escalation, missing reason, and an unpaired reason.
- Root-counted active counts 1, 2, and 3 accepted; 0, 4, 5, booleans, and nonintegers rejected.
- CLI produces valid JSON for a permitted work order; occupied slots and omitted-root count return argparse exit 2 with specific diagnostics.

The initial configuration validator rejected effort above high but accepted three policy-drift counterexamples in memory: discovery reassigned to Astra, the Luna low profile reassigned to Sol, and that profile's effort changed to high. This was reported immediately to the director and corrected by the director's contract-validation patch.

The final patch fixes exact profile/model/effort pairs, all 16 category/default mappings, director Sol/high intent, escalation adjacency, and the single-escalation policy value. The full payload/guard/CLI suite above passed again. Fourteen additional in-memory policy-drift variants were rejected: the three original counterexamples, xhigh, director low, extra profile, extra category, missing category, direct Luna-to-Astra escalation, escalation cap two, full-history fork, five global slots, silent substitution, and child spawning.

**Verdict: pass for the reviewed delegation-helper scope; no remaining blocking finding.** The hypothesis holds for the checked-in contract and tested invalid work orders/configuration variants. This is bounded verification, not proof against every malformed input or a live scheduling test. Missing/malformed required work-order evidence means empty or non-string fields here; substantive evidence adequacy remains a reviewer obligation.

## Operational limits

This helper prepares one payload; it does not spawn agents or schedule experiments. `active_agents` is a caller-supplied count, not a live scheduler observation or atomic slot reservation. The director must count root plus all active workers immediately before spawning and handle actual tool-level capacity/model availability failures without silent substitution.

The helper validates an allowed initial-to-escalated route and writes its reason into the work order. It has no task history or persistent ledger; the director owns enforcing at most one escalation across repeated work orders. The router likewise cannot verify the truth, adequacy, or provenance of nonempty evidence descriptions, exclusive ownership, or reviewer independence.

CPU allowances and suggested response lengths are work-order guidance, not measured or enforced runtime limits. Requested reasoning effort is not a token cap. `followup_task` does not change an agent's model or effort; reuse must match the original assignment and ownership. The existing root cannot be retuned by this helper. Keeping a critic engaged and enforcing role separation remain director responsibilities.

The documents honestly distinguish current live delegation policy from the proposed round-six experiment runner. These checks establish payload/configuration behavior only; they establish no scientific improvement or production runner readiness.
