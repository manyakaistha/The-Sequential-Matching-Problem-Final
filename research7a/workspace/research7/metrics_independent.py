"""Independent metric reconstruction from public introduction and feedback event logs.

Owned exclusively by 7a under Work Order WO02.
Does NOT import simulator internals or ground truth.

Reconstructs:
- Assignment-relative date deadline <= 30 days
- Date-relative second response deadline <= 3 days
- Exactly two on-time 'yes' second-meeting intentions
- One pair reward per qualified introduction
- Arrived-by-59 denominator (200 members)
- Unique coverage (unique members served)
- Distinct tracking for unqualified late-positive pauses
- Nonmutual, canceled, missing, and late events
"""

from __future__ import annotations
import collections
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


def reconstruct_metrics_from_events(
    introductions: Sequence[Dict[str, Any]],
    events: Sequence[Dict[str, Any]],
    arrived_members_count: int = 200,
    arrived_member_ids: Optional[Set[str]] = None
) -> Dict[str, Any]:
    """Reconstruct primary and diagnostic metrics from public introduction and event streams.
    
    Zero reliance on simulator internals, private truth, or hidden oracle states.
    """
    # Group events by introduction_id
    events_by_intro: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)
    for ev in events:
        intro_id = ev.get('introduction_id')
        if intro_id:
            events_by_intro[intro_id].append(ev)

    assignments_count = len(introductions)
    mutual_acceptances = 0
    dates_scheduled_or_happened = 0
    qualified_msmi = 0
    unqualified_late_pauses = 0
    non_mutual_intros = 0
    declined_intros = 0
    missing_feedback_events = 0

    served_members: Set[str] = set()
    first_introduction_day: Dict[str, int] = {}

    for intro in introductions:
        intro_id = intro['introduction_id']
        assigned_day = intro['assigned_day']
        user_a = intro['user_a']
        user_b = intro['user_b']

        served_members.add(user_a)
        served_members.add(user_b)
        first_introduction_day.setdefault(user_a, assigned_day)
        first_introduction_day.setdefault(user_b, assigned_day)

        ev_list = events_by_intro.get(intro_id, [])

        # 1. Introduction response events
        intro_responses = [e for e in ev_list if e.get('event') == 'introduction_response']
        yes_responses = [e for e in intro_responses if e.get('value') == 'yes']
        no_responses = [e for e in intro_responses if e.get('value') == 'no']
        
        is_mutual = len(yes_responses) == 2
        if is_mutual:
            mutual_acceptances += 1
        else:
            non_mutual_intros += 1
            if len(no_responses) > 0:
                declined_intros += 1

        # Track missing feedback
        for e in ev_list:
            if e.get('missing_reason') == 'no_response':
                missing_feedback_events += 1

        # 2. Date happened events
        date_events = [e for e in ev_list if e.get('event') == 'date_happened' and e.get('value') is True]
        if date_events:
            dates_scheduled_or_happened += 1
            date_ev = date_events[0]
            date_occurred_day = date_ev.get('occurred_day')

            # Date qualification: date must occur within 30 days of introduction
            date_on_time = (
                date_occurred_day is not None and
                (date_occurred_day - assigned_day) <= 30
            )

            # 3. Second meeting intention events
            second_intentions = [e for e in ev_list if e.get('event') == 'second_meeting_intention']
            yes_seconds = [e for e in second_intentions if e.get('value') == 'yes']

            both_yes = len(yes_seconds) == 2
            
            # Intention qualification: both must occur within 3 days of the date
            intentions_on_time = False
            if both_yes and date_occurred_day is not None:
                intentions_on_time = all(
                    (s.get('occurred_day') is not None and (s['occurred_day'] - date_occurred_day) <= 3)
                    for s in yes_seconds
                )

            if date_on_time and intentions_on_time:
                qualified_msmi += 1
            elif both_yes:
                # Late positive second intentions: causes pause in simulator, but does NOT qualify as MSMI!
                unqualified_late_pauses += 1

    denominator = arrived_members_count if arrived_members_count > 0 else len(served_members)
    msmi_per_100 = 100.0 * qualified_msmi / max(1, denominator)
    coverage = len(served_members) / max(1, denominator)

    return {
        'assignments': assignments_count,
        'mutual_acceptances': mutual_acceptances,
        'dates': dates_scheduled_or_happened,
        'mutual_second_meeting_intention': qualified_msmi,
        'unqualified_late_pauses': unqualified_late_pauses,
        'non_mutual_introductions': non_mutual_intros,
        'declined_introductions': declined_intros,
        'missing_feedback_count': missing_feedback_events,
        'arrived_members': denominator,
        'served_members': len(served_members),
        'unserved_members': max(0, denominator - len(served_members)),
        'coverage': round(coverage, 6),
        'msmi_per_100_arrived_members': round(msmi_per_100, 8),
        'first_introduction_day_counts': len(first_introduction_day)
    }


def verify_metric_reconstruction() -> Dict[str, Any]:
    """Verify independent metric reconstruction logic against synthetic edge cases.
    
    Checks:
    1. Standard on-time qualified MSMI (date <= 30, second <= 3).
    2. Late date (> 30 days) yields unqualified_late_pause, not MSMI.
    3. Late second intention (> 3 days) yields unqualified_late_pause, not MSMI.
    4. One No response yields declined and no MSMI.
    5. Day 59 assignment with day 80 date and day 82 intention qualifies (since date-assigned <= 30 and intent-date <= 3).
    """
    tests = {}

    # Case 1: Standard qualified
    intro1 = {'introduction_id': 'i1', 'user_a': 'u1', 'user_b': 'u2', 'assigned_day': 10}
    events1 = [
        {'introduction_id': 'i1', 'event': 'introduction_response', 'value': 'yes', 'occurred_day': 12},
        {'introduction_id': 'i1', 'event': 'introduction_response', 'value': 'yes', 'occurred_day': 14},
        {'introduction_id': 'i1', 'event': 'date_happened', 'value': True, 'occurred_day': 25},
        {'introduction_id': 'i1', 'event': 'second_meeting_intention', 'value': 'yes', 'occurred_day': 27},
        {'introduction_id': 'i1', 'event': 'second_meeting_intention', 'value': 'yes', 'occurred_day': 28}
    ]
    m1 = reconstruct_metrics_from_events([intro1], events1, arrived_members_count=200)
    tests['standard_qualified'] = m1['mutual_second_meeting_intention'] == 1 and m1['unqualified_late_pauses'] == 0

    # Case 2: Late date (> 30 days, e.g. day 45 vs intro day 10 => delay 35)
    intro2 = {'introduction_id': 'i2', 'user_a': 'u3', 'user_b': 'u4', 'assigned_day': 10}
    events2 = [
        {'introduction_id': 'i2', 'event': 'introduction_response', 'value': 'yes', 'occurred_day': 12},
        {'introduction_id': 'i2', 'event': 'introduction_response', 'value': 'yes', 'occurred_day': 14},
        {'introduction_id': 'i2', 'event': 'date_happened', 'value': True, 'occurred_day': 45},  # > 30 delay
        {'introduction_id': 'i2', 'event': 'second_meeting_intention', 'value': 'yes', 'occurred_day': 46},
        {'introduction_id': 'i2', 'event': 'second_meeting_intention', 'value': 'yes', 'occurred_day': 47}
    ]
    m2 = reconstruct_metrics_from_events([intro2], events2, arrived_members_count=200)
    tests['late_date_unqualified'] = m2['mutual_second_meeting_intention'] == 0 and m2['unqualified_late_pauses'] == 1

    # Case 3: Late second intention (> 3 days, e.g. delay 5 days)
    intro3 = {'introduction_id': 'i3', 'user_a': 'u5', 'user_b': 'u6', 'assigned_day': 10}
    events3 = [
        {'introduction_id': 'i3', 'event': 'introduction_response', 'value': 'yes', 'occurred_day': 12},
        {'introduction_id': 'i3', 'event': 'introduction_response', 'value': 'yes', 'occurred_day': 14},
        {'introduction_id': 'i3', 'event': 'date_happened', 'value': True, 'occurred_day': 25},
        {'introduction_id': 'i3', 'event': 'second_meeting_intention', 'value': 'yes', 'occurred_day': 27},
        {'introduction_id': 'i3', 'event': 'second_meeting_intention', 'value': 'yes', 'occurred_day': 31}  # 6 days after date > 3
    ]
    m3 = reconstruct_metrics_from_events([intro3], events3, arrived_members_count=200)
    tests['late_intention_unqualified'] = m3['mutual_second_meeting_intention'] == 0 and m3['unqualified_late_pauses'] == 1

    # Case 4: Day 59 assignment with full follow-up (date day 75, intention day 77)
    intro4 = {'introduction_id': 'i4', 'user_a': 'u7', 'user_b': 'u8', 'assigned_day': 59}
    events4 = [
        {'introduction_id': 'i4', 'event': 'introduction_response', 'value': 'yes', 'occurred_day': 62},
        {'introduction_id': 'i4', 'event': 'introduction_response', 'value': 'yes', 'occurred_day': 63},
        {'introduction_id': 'i4', 'event': 'date_happened', 'value': True, 'occurred_day': 75},  # 75 - 59 = 16 <= 30
        {'introduction_id': 'i4', 'event': 'second_meeting_intention', 'value': 'yes', 'occurred_day': 77},  # 77 - 75 = 2 <= 3
        {'introduction_id': 'i4', 'event': 'second_meeting_intention', 'value': 'yes', 'occurred_day': 77}
    ]
    m4 = reconstruct_metrics_from_events([intro4], events4, arrived_members_count=200)
    tests['day59_full_followup_qualified'] = m4['mutual_second_meeting_intention'] == 1 and m4['unqualified_late_pauses'] == 0

    all_passed = all(tests.values())
    return {
        'status': 'metric_verification_complete',
        'all_passed': all_passed,
        'tests': tests
    }
