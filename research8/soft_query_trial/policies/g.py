"""Arm G: Frozen Greedy Benchmark.

- Hard asks: exact kit.baseline_asks(state)
- Matching: exact kit.baseline_match(state)
- No added soft queries.
"""

from typing import Any, Dict
from kit import baseline_asks, baseline_match

LAST_STATUS: Dict[str, Any] = {"fallback": False, "reason": None}


def decide(request: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
    global LAST_STATUS
    LAST_STATUS = {"fallback": False, "reason": None}

    state = request["state"]
    memory = request.get("memory") or {}
    phase = request["phase"]

    if phase == "ask":
        hard_asks = baseline_asks(state)
        # Record public telemetry in memory
        telemetry = memory.get("telemetry", {})
        day_str = str(state.get("day", 0))
        telemetry[day_str] = {
            "hard_asks_count": len(hard_asks),
            "soft_asks_count": 0,
            "budget_remaining_after_hard": state.get("ask_budget_remaining", 12) - len(hard_asks) * 3,
        }
        memory["telemetry"] = telemetry
        return {"asks": hard_asks, "memory": memory}

    elif phase == "match":
        pairs = baseline_match(state)
        return {"pairs": pairs, "memory": memory}

    else:
        raise ValueError(f"Unknown phase: {phase}")
