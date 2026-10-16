"""Arm G_random_soft: Greedy hard batch + random eligible soft questions.

- Start with exact frozen Greedy hard-query batch (baseline_asks(state)).
- Calculate remaining budget after those hard queries.
- Fill remaining units with randomly selected eligible soft questions from candidate set C.
- After actual answers, use exact frozen Greedy matching (baseline_match(state)).
"""

from typing import Any, Dict
from kit import baseline_asks, baseline_match
from .targeting import select_random_soft_asks, RANDOM_POLICY_SALT

LAST_STATUS: Dict[str, Any] = {"fallback": False, "reason": None}


def decide(request: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
    global LAST_STATUS
    LAST_STATUS = {"fallback": False, "reason": None}

    config = config or {}
    salt = config.get("salt", RANDOM_POLICY_SALT)

    state = request["state"]
    memory = request.get("memory") or {}
    phase = request["phase"]

    if phase == "ask":
        hard_asks = baseline_asks(state)
        hard_cost = len(hard_asks) * 3
        current_budget = state.get("ask_budget_remaining", 12)
        remaining_budget = max(0, current_budget - hard_cost)

        soft_asks, soft_meta = select_random_soft_asks(state, remaining_budget, salt=salt)
        combined_asks = list(hard_asks) + list(soft_asks)

        # Record public telemetry in memory
        telemetry = memory.get("telemetry", {})
        day_str = str(state.get("day", 0))
        telemetry[day_str] = {
            "hard_asks_count": len(hard_asks),
            "soft_asks_count": len(soft_asks),
            "budget_remaining_after_hard": remaining_budget,
            "candidate_count": soft_meta.get("candidate_count", 0),
            "rng_recipe": soft_meta.get("rng_recipe"),
        }
        memory["telemetry"] = telemetry

        return {"asks": combined_asks, "memory": memory}

    elif phase == "match":
        pairs = baseline_match(state)
        return {"pairs": pairs, "memory": memory}

    else:
        raise ValueError(f"Unknown phase: {phase}")
