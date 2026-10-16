"""Public-event endpoints for the day-59 assignment/day-99 release horizon."""
from collections import defaultdict

from research8.w2.public_rules import SOFT


def compute_run_metrics(introductions, ask_log, *, feedback, arrived_members,
                        observed_day=100, is_valid=True, validation_errors=None):
    errors = list(validation_errors or [])
    cutoff = min(observed_day, 99)
    arrived, member_ids = {}, set()
    for member in arrived_members:
        ident, day = member['member_id'], member['arrived_day']
        if ident in member_ids:
            raise ValueError('Duplicate member ID')
        member_ids.add(ident)
        if day <= 59:
            arrived[ident] = day
    events = defaultdict(list)
    for event in feedback:
        if event['observed_day'] <= cutoff:
            events[event['introduction_id']].append(event)
    seen_ids, seen_pairs, first = set(), set(), {}
    mutual = dates = qualified = missing = pauses = 0
    for intro in introductions:
        ident = intro['introduction_id']
        endpoints = {intro['user_a'], intro['user_b']}
        pair = tuple(sorted(endpoints))
        if len(endpoints) != 2 or ident in seen_ids or pair in seen_pairs:
            raise ValueError('Duplicate introduction ID/pair or self introduction')
        if not 0 <= intro['assigned_day'] <= 59:
            raise ValueError('Introduction outside assignment horizon')
        seen_ids.add(ident)
        seen_pairs.add(pair)
        for member in endpoints:
            if member not in arrived or arrived[member] > intro['assigned_day']:
                raise ValueError('Introduction member absent or not yet arrived')
            first[member] = min(first.get(member, intro['assigned_day']), intro['assigned_day'])
        es = events[ident]
        event_keys = set()
        for event in es:
            name, actor = event['event'], event['member_id']
            key = (name, actor)
            if key in event_keys or name not in {'introduction_response', 'date_happened',
                                                'second_meeting_intention', 'pause_after_mutual_interest'}:
                raise ValueError('Duplicate/conflicting or unknown feedback event')
            event_keys.add(key)
            if name in {'introduction_response', 'second_meeting_intention'} and actor not in endpoints:
                raise ValueError('Invalid feedback endpoint')
            if name in {'introduction_response', 'second_meeting_intention'}:
                value, occurred = event['value'], event['occurred_day']
                if not ((value is None and occurred is None and event.get('missing_reason') == 'no_response')
                        or (value in ('yes', 'no') and type(value) is str and occurred is not None
                            and event.get('missing_reason') is None)):
                    raise ValueError('Invalid response missingness')
            if name in {'date_happened', 'pause_after_mutual_interest'} and actor is not None:
                raise ValueError('Invalid dyad event endpoint')
            occurrence = event['occurred_day']
            release = event['observed_day']
            if type(release) is not int or release < intro['assigned_day'] or (occurrence is not None
                    and (type(occurrence) is not int or not intro['assigned_day'] <= occurrence <= release)):
                raise ValueError('Invalid event chronology')
        def positive_endpoints(name, start=None, window=None):
            rows = [e for e in es if e['event'] == name]
            return (len(rows) == 2 and {e['member_id'] for e in rows} == endpoints
                    and all(e['value'] == 'yes' and type(e['occurred_day']) is int
                            and (start is None or 0 <= e['occurred_day'] - start <= window)
                            for e in rows))
        accepted = positive_endpoints('introduction_response')
        mutual += int(accepted)
        ds = [e for e in es if e['event'] == 'date_happened' and e['value'] is True]
        if ds and (not accepted or ds[0]['occurred_day'] < max(
                e['occurred_day'] for e in es if e['event'] == 'introduction_response')):
            raise ValueError('Date before mutual acceptance')
        dates += int(bool(ds))
        good = accepted and any(type(e['occurred_day']) is int
                               and 0 <= e['occurred_day'] - intro['assigned_day'] <= 30
                               and positive_endpoints('second_meeting_intention', e['occurred_day'], 3)
                               for e in ds)
        qualified += int(good)
        pauses += int(not good and any(e['event'] == 'pause_after_mutual_interest'
                                      and e['value'] is True for e in es))
        missing += sum(e.get('missing_reason') == 'no_response' for e in es)
    if set(events) - seen_ids:
        raise ValueError('Feedback references unknown introduction')
    hard = soft = 0
    for ask in ask_log:
        if ask['field'] == 'constraints':
            hard += 1
        elif ask['field'] in SOFT:
            soft += 1
        else:
            raise ValueError('Unknown governing ask field')
    denominator = len(arrived)
    return dict(valid=is_valid and not errors, validation_errors=errors,
                arrived_members=denominator, served_members=len(first),
                unserved_members=denominator-len(first),
                coverage=len(first)/denominator if denominator else 0.0,
                assignments=len(introductions), mutual_acceptances=mutual, dates=dates,
                mutual_second_meeting_intention=qualified, missing_feedback=missing,
                ask_cost=3*hard+soft,
                msmi_per_100_arrived_members=100.0*qualified/denominator if denominator else 0.0,
                mutual_acceptances_per_100=100.0*mutual/denominator if denominator else 0.0,
                first_introduction_wait_days=sorted(first[i]-arrived[i] for i in first),
                total_asks=len(ask_log), hard_asks=hard, soft_asks=soft,
                unqualified_pause_count=pauses,
                status='simulated_not_observed_product_performance')
