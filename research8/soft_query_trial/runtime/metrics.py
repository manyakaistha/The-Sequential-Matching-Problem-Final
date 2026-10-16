"""Event-based metric computation for Research 8 soft query trial.

Strictly implements the corrected metric layer:
- Endpoint: Y = 100 * qualified_introductions / arrived_members_by_day59
- Each qualifying dyad is counted ONCE (no factor-of-two inflation).
- Denominator is strictly arrived members with arrived_day <= 59.
- Qualification:
    1. Mutual first acceptance (both introduction_response == 'yes')
    2. Date happened within 30 days of introduction (date_happened occurred_day - assigned_day <= 30)
    3. Both second intentions positive within 3 days of date (second_meeting_intention occurred_day - date_occurred_day <= 3)
    4. Required feedback released by evaluation cutoff (observed_day <= observed_day_cutoff).
"""

from collections import defaultdict
from typing import Any, Dict, List

from research8.soft_query_trial.policies.targeting import SOFT_FIELDS


def compute_run_metrics(
    introductions: List[Dict[str, Any]],
    ask_log: List[Dict[str, Any]],
    *,
    feedback: List[Dict[str, Any]],
    arrived_members: List[Dict[str, Any]],
    observed_day: int = 100,
    is_valid: bool = True,
    validation_errors: List[str] = None,
) -> Dict[str, Any]:
    errors = list(validation_errors or [])
    arrived = {m["member_id"]: m["arrived_day"] for m in arrived_members if m.get("arrived_day", 0) <= 59}

    events = defaultdict(list)
    for event in feedback:
        if event.get("observed_day", 0) <= observed_day:
            events[event["introduction_id"]].append(event)

    mutual = dates = msmi = missing = pauses = 0
    first_intro_day = {}

    for intro in introductions:
        intro_id = intro["introduction_id"]
        for ident in (intro["user_a"], intro["user_b"]):
            if ident not in arrived:
                raise ValueError(f"Introduced member {ident} absent from arrived-by-59 inventory")
            first_intro_day[ident] = min(first_intro_day.get(ident, intro["assigned_day"]), intro["assigned_day"])

        es = events[intro_id]
        rs = [e for e in es if e.get("event") == "introduction_response"]
        is_mutual = len(rs) == 2 and all(e.get("value") == "yes" for e in rs)
        mutual += int(is_mutual)

        ds = [e for e in es if e.get("event") == "date_happened" and e.get("value") is True]
        date_happened = bool(ds)
        dates += int(date_happened)

        ss = [e for e in es if e.get("event") == "second_meeting_intention"]
        qualified = (
            date_happened
            and (ds[0]["occurred_day"] - intro["assigned_day"] <= 30)
            and len(ss) == 2
            and all(e.get("value") == "yes" and (e["occurred_day"] - ds[0]["occurred_day"] <= 3) for e in ss)
        )
        msmi += int(qualified)

        pauses += int(
            not qualified
            and any(e.get("event") == "pause_after_mutual_interest" and e.get("value") is True for e in es)
        )
        missing += sum(e.get("missing_reason") == "no_response" for e in es)

    hard_asks = soft_asks = ask_cost = 0
    for ask in ask_log:
        field = ask.get("field")
        if field == "constraints":
            hard_asks += 1
            ask_cost += 3
        elif field in SOFT_FIELDS:
            soft_asks += 1
            ask_cost += 1
        else:
            raise ValueError(f"Unknown governing ask field: {field}")

    denominator = max(1, len(arrived))
    msmi_per_100 = 100.0 * msmi / denominator
    mutual_per_100 = 100.0 * mutual / denominator

    return {
        "valid": is_valid and not errors,
        "validation_errors": errors,
        "arrived_members": len(arrived),
        "served_members": len(first_intro_day),
        "unserved_members": len(arrived) - len(first_intro_day),
        "coverage": len(first_intro_day) / denominator,
        "assignments": len(introductions),
        "mutual_acceptances": mutual,
        "dates": dates,
        "mutual_second_meeting_intention": msmi,
        "missing_feedback": missing,
        "ask_cost": ask_cost,
        "msmi_per_100_arrived_members": msmi_per_100,
        "mutual_acceptances_per_100": mutual_per_100,
        "first_introduction_wait_days": sorted(first_intro_day[i] - arrived[i] for i in first_intro_day),
        "total_asks": len(ask_log),
        "hard_asks": hard_asks,
        "soft_asks": soft_asks,
        "unqualified_pause_count": pauses,
        "status": "simulated_not_observed_product_performance",
    }
