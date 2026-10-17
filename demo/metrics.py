"""Public projections and metric calculations shared by the API and tests."""

from __future__ import annotations

import copy
from typing import Any

from kit import Simulator, eligibility


REASON_LABELS = {
    "same_member": "The two records refer to the same synthetic member.",
    "different_pool": "Members must belong to the same synthetic pool.",
    "underage": "Both members must be adults in the supplied contract.",
    "who_to_meet": "The other member's stated gender is outside this member's preference.",
    "age": "The other member is outside the stated age range.",
    "geography": "The other member's zone is outside the stated acceptable zones.",
    "smoking": "The smoking preference is not mutually compatible.",
    "children_present": "A children-related hard preference is not met.",
    "children_plans": "The members have conflicting explicit children plans.",
    "relationship_structure": "The relationship structures do not match in this kit.",
    "schedule": "The members have no overlapping available schedule slot.",
}


def reason_label(reason: str) -> str:
    return REASON_LABELS.get(reason, reason.replace("_", " ").capitalize())


def public_state(sim: Simulator) -> dict[str, Any]:
    """Return a deep-copied observation; hidden world fields never enter this object."""
    observed = sim.observe()
    # The reference simulator already omits truth, response propensity, bias and exit days.
    # Copy once more so a caller cannot mutate the engine through a response object.
    return copy.deepcopy(observed)


def pair_inspection(sim: Simulator, member_id: str) -> dict[str, Any] | None:
    state = public_state(sim)
    members = {member["member_id"]: member for member in state["members"]}
    selected = members.get(member_id)
    if selected is None:
        return None
    candidates: list[dict[str, Any]] = []
    past = {tuple(sorted((item["user_a"], item["user_b"]))) for item in state["introductions"]}
    for other in state["members"]:
        if other["member_id"] == member_id:
            continue
        result = eligibility(selected, other)
        pair = tuple(sorted((member_id, other["member_id"])))
        if pair in past:
            result = {"status": "infeasible", "reasons": ["already_introduced"], "missing": []}
        elif not selected["available"] or not other["available"]:
            result = {"status": "infeasible", "reasons": ["unavailable"], "missing": []}
        candidates.append(
            {
                "member_id": other["member_id"],
                "status": result["status"],
                "reasons": [reason_label(reason) for reason in result.get("reasons", [])],
                "missing": result.get("missing", []),
            }
        )
    candidates.sort(key=lambda item: (item["status"] != "feasible", item["status"] != "needs_clarification", item["member_id"]))
    return {"member_id": member_id, "candidates": candidates[:24]}


def metrics_snapshot(sim: Simulator) -> dict[str, Any]:
    raw = sim.metrics()
    arrived_ids = {member["member_id"] for member in sim.world["members"] if member["arrived_day"] <= 59}
    first_assignment: dict[str, int] = {}
    for intro in sim.introductions:
        for member_id in (intro["user_a"], intro["user_b"]):
            first_assignment.setdefault(member_id, intro["assigned_day"])
    waits = sorted(first_assignment[mid] - next(member["arrived_day"] for member in sim.world["members"] if member["member_id"] == mid)
                  for mid in first_assignment if mid in arrived_ids)
    served = len(first_assignment)
    denominator = max(1, len(arrived_ids))
    return {
        "assignments": int(raw["assignments"]),
        "mutual_acceptances": int(raw["mutual_acceptances"]),
        "dates": int(raw["dates"]),
        "mutual_second_meeting_intention": int(raw["mutual_second_meeting_intention"]),
        "missing_feedback": int(raw["missing_feedback"]),
        "ask_cost": int(raw["ask_cost"]),
        "arrived_members": len(arrived_ids),
        "served_members": served,
        "unserved_members": max(0, len(arrived_ids) - served),
        "coverage": served / denominator,
        "msmi_per_100_arrived_members": 100 * raw["mutual_second_meeting_intention"] / denominator,
        "mutual_acceptances_per_100": 100 * raw["mutual_acceptances"] / denominator,
        "first_introduction_wait_days": waits,
        "status": "final" if sim.day >= 100 else "provisional",
    }


def outcome_funnel(sim: Simulator) -> list[dict[str, Any]]:
    current = metrics_snapshot(sim)
    return [
        {"key": "assignments", "label": "Introductions assigned", "value": current["assignments"], "definition": "A valid, non-overlapping introduction selected by the policy."},
        {"key": "mutual_acceptances", "label": "Mutual acceptances", "value": current["mutual_acceptances"], "definition": "Both directional introduction responses were yes."},
        {"key": "dates", "label": "Dates occurred", "value": current["dates"], "definition": "The simulator recorded a first date after mutual acceptance."},
        {"key": "mutual_second_meeting_intention", "label": "Qualified MSMI", "value": current["mutual_second_meeting_intention"], "definition": "A date occurred within 30 days and both second-meeting yes responses arrived within 3 days."},
    ]


def action_payload(phase: str, day: int, asks: list[dict[str, Any]] | None = None,
                   pairs: list[list[str]] | None = None, ask_results: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"phase": phase, "day": day}
    if asks is not None:
        payload["asks"] = copy.deepcopy(asks)
    if pairs is not None:
        payload["pairs"] = copy.deepcopy(pairs)
    if ask_results is not None:
        payload["ask_results"] = copy.deepcopy(ask_results)
    return payload
