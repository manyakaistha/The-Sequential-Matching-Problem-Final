"""Arm G_targeted_soft: Greedy hard batch + targeted eligible soft questions.

- Start with exact frozen Greedy hard-query batch (baseline_asks(state)).
- Calculate remaining budget after those hard queries.
- Fill remaining units with targeted eligible soft questions from candidate set C
  using the frozen priority and tie-breaking rules.
- After actual answers, use exact frozen Greedy matching (baseline_match(state)).
"""

from typing import Any, Dict
from kit import baseline_asks, baseline_match
from .targeting import select_targeted_soft_asks

LAST_STATUS: Dict[str, Any] = {"fallback": False, "reason": None}


def decide(request: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
    global LAST_STATUS
    LAST_STATUS = {"fallback": False, "reason": None}

    state = request["state"]
    memory = request.get("memory") or {}
    phase = request["phase"]

    if phase == "ask":
        hard_asks = baseline_asks(state)
        hard_cost = len(hard_asks) * 3
        current_budget = state.get("ask_budget_remaining", 12)
        remaining_budget = max(0, current_budget - hard_cost)

        soft_asks, soft_meta = select_targeted_soft_asks(state, remaining_budget)
        combined_asks = list(hard_asks) + list(soft_asks)

        # Record public telemetry in memory
        telemetry = memory.get("telemetry", {})
        day_str = str(state.get("day", 0))
        telemetry[day_str] = {
            "hard_asks_count": len(hard_asks),
            "soft_asks_count": len(soft_asks),
            "budget_remaining_after_hard": remaining_budget,
            "candidate_count": soft_meta.get("candidate_count", 0),
        }
        memory["telemetry"] = telemetry

        return {"asks": combined_asks, "memory": memory}

    elif phase == "match":
        pairs = baseline_match(state)
        return {"pairs": pairs, "memory": memory}

    else:
        raise ValueError(f"Unknown phase: {phase}")
