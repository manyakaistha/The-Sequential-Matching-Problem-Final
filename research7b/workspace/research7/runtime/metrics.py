"""Event-based accounting matching kit.metrics and evaluate.episode."""
from collections import defaultdict
from typing import Any, Dict, List

from .interfaces import SOFT_FIELDS


def compute_run_metrics(introductions: List[Dict[str, Any]], ask_log: List[Dict[str, Any]],
                        *, feedback: List[Dict[str, Any]], arrived_members: List[Dict[str, Any]],
                        observed_day: int = 100, is_valid: bool = True,
                        validation_errors: List[str] = None) -> Dict[str, Any]:
    """Score released events with the evaluator's arrived-by-day-59 denominator.

    Feedback is required: introduction records contain no outcome labels.
    Inputs must be public records from the governing simulator; no worlds,
    hidden truth, seeds or future events are needed.
    """
    errors = list(validation_errors or [])
    arrived = {m['member_id']: m['arrived_day'] for m in arrived_members if m['arrived_day'] <= 59}
    events = defaultdict(list)
    for event in feedback:
        if event['observed_day'] <= observed_day:
            events[event['introduction_id']].append(event)
    mutual = dates = msmi = missing = pauses = 0
    first = {}
    for intro in introductions:
        for ident in (intro['user_a'], intro['user_b']):
            if ident not in arrived:
                raise ValueError('Introduced member is absent from arrived-by59 inventory')
            first[ident] = min(first.get(ident, intro['assigned_day']), intro['assigned_day'])
        es = events[intro['introduction_id']]
        rs = [e for e in es if e['event'] == 'introduction_response']
        mutual += len(rs) == 2 and all(e['value'] == 'yes' for e in rs)
        ds = [e for e in es if e['event'] == 'date_happened' and e['value'] is True]
        ss = [e for e in es if e['event'] == 'second_meeting_intention']
        qualified = bool(ds) and ds[0]['occurred_day'] - intro['assigned_day'] <= 30 and len(ss) == 2 and all(
            e['value'] == 'yes' and e['occurred_day'] - ds[0]['occurred_day'] <= 3 for e in ss)
        dates += bool(ds)
        msmi += qualified
        pauses += not qualified and any(e['event'] == 'pause_after_mutual_interest' and e['value'] is True for e in es)
        missing += sum(e.get('missing_reason') == 'no_response' for e in es)
    hard = soft = cost = 0
    for ask in ask_log:
        if ask['field'] == 'constraints':
            hard += 1
            cost += 3
        elif ask['field'] in SOFT_FIELDS:
            soft += 1
            cost += 1
        else:
            raise ValueError(f"Unknown governing ask field: {ask['field']}")
    denominator = max(1, len(arrived))
    return {
        'valid': is_valid and not errors, 'validation_errors': errors,
        'arrived_members': len(arrived), 'served_members': len(first),
        'unserved_members': len(arrived) - len(first), 'coverage': len(first) / denominator,
        'assignments': len(introductions), 'mutual_acceptances': mutual, 'dates': dates,
        'mutual_second_meeting_intention': msmi, 'missing_feedback': missing,
        'ask_cost': cost, 'msmi_per_100_arrived_members': 100 * msmi / denominator,
        'mutual_acceptances_per_100': 100 * mutual / denominator,
        'first_introduction_wait_days': sorted(first[i] - arrived[i] for i in first),
        'total_asks': len(ask_log), 'hard_asks': hard, 'soft_asks': soft,
        'unqualified_pause_count': pauses,
        'status': 'simulated_not_observed_product_performance',
    }
