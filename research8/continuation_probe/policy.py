"""D1_min: experimental ordinal-score hold, not a calibrated dynamic planner.

The public rejection clock implies a possible next-day return conditional on
survival. Private departure, competing matches and lost current opportunities
can make the hold harmful. No future match is forced or probability estimated.
"""
import copy

from research8.soft_query_followup.v2 import reference_adapter
from research8.w2.public_rules import SOFT, eligibility

LAST_STATUS = {'fallback': False, 'reason': None}


def _score(a, b):
    return sum(a['fields'].get(k) is not None
               and a['fields'].get(k) == b['fields'].get(k) for k in SOFT)


def _memory(value):
    """Reject malformed hold history; never pass wrapper state to Q6."""
    fresh = {'parent_memory': {}, 'held': [], 'hold_events': []}
    if value == {} or value is None:
        return fresh, True
    if not isinstance(value, dict):
        return fresh, False
    parent = value.get('parent_memory', {})
    fresh['parent_memory'] = copy.deepcopy(parent) if isinstance(parent, dict) else {}
    held, events = value.get('held'), value.get('hold_events')
    if (not isinstance(parent, dict) or not isinstance(held, list)
            or len(held) > 200 or not all(isinstance(x, str) for x in held)
            or len(set(held)) != len(held) or not isinstance(events, list)
            or len(events) > 100):
        return fresh, False
    endpoints = []
    for event in events:
        if (not isinstance(event, dict) or type(event.get('day')) is not int
                or not 0 <= event['day'] < 59
                or not isinstance(event.get('endpoints'), list)
                or len(event['endpoints']) != 2
                or not all(isinstance(x, str) for x in event['endpoints'])
                or len(set(event['endpoints'])) != 2
                or not isinstance(event.get('alternative'), str)
                or event.get('held_endpoint') not in event['endpoints']
                or type(event.get('target_day')) is not int
                or event['target_day'] != event['day'] + 1
                or type(event.get('old_score')) is not int
                or type(event.get('new_score')) is not int
                or not 0 <= event['old_score'] < event['new_score'] <= 7
                or event.get('public_reason') != 'latest_nonmutual_assignment_plus_8'):
            return fresh, False
        endpoints.extend(event['endpoints'])
    if (len(set(endpoints)) != len(endpoints) or set(endpoints) != set(held)
            or len({e['day'] for e in events}) != len(events)
            or len(set(held) | {e['alternative'] for e in events}) > 200):
        return fresh, False
    return copy.deepcopy(value), True


def _return_candidates(state):
    """Index cumulative public history once, then inspect at most 200 actors."""
    today = state['day']
    latest, ambiguous = {}, set()
    past = set()
    for intro in state['introductions']:
        a, b, day = intro['user_a'], intro['user_b'], intro['assigned_day']
        past.add(frozenset((a, b)))
        if type(day) is not int or day > today:
            continue
        for actor in (a, b):
            if actor not in latest or day > latest[actor]['assigned_day']:
                latest[actor] = intro
                ambiguous.discard(actor)
            elif day == latest[actor]['assigned_day']:
                ambiguous.add(actor)
    released, paused = {}, set()
    intro_by_id = {i['introduction_id']: i for i in state['introductions']}
    for event in state.get('feedback', []):
        observed = event.get('observed_day')
        if type(observed) is not int or observed > today:
            continue
        ident = event.get('introduction_id')
        released.setdefault(ident, []).append(event)
        if event.get('event') == 'pause_after_mutual_interest' and ident in intro_by_id:
            intro = intro_by_id[ident]
            paused.update((intro['user_a'], intro['user_b']))
    candidates = []
    for member in state['members']:
        actor = member['member_id']
        intro = latest.get(actor)
        if (member['available'] or actor in paused or actor in ambiguous
                or intro is None or intro['assigned_day'] + 8 != today + 1
                or intro.get('response_deadline_day') != intro['assigned_day'] + 7):
            continue
        events = released.get(intro['introduction_id'], [])
        if any(e.get('event') in ('date_happened', 'second_meeting_intention',
                                   'pause_after_mutual_interest') for e in events):
            continue
        negative = False
        for event in events:
            if (event.get('event') != 'introduction_response'
                    or event.get('member_id') not in (intro['user_a'], intro['user_b'])
                    or event['observed_day'] < intro['assigned_day']):
                continue
            occurred = event.get('occurred_day')
            if event.get('value') == 'no' and (type(occurred) is int
                    and intro['assigned_day'] <= occurred <= event['observed_day']
                    and event.get('missing_reason') is None):
                negative = True
            if (event.get('value') is None and occurred is None
                    and event.get('missing_reason') == 'no_response'
                    and event['observed_day'] == intro['response_deadline_day']):
                negative = True
        if negative:
            candidates.append(member)
    return candidates, past


def decide(request, config):
    """Delegate Q6 exactly; optionally omit one current parent pair per day."""
    global LAST_STATUS
    LAST_STATUS = {'fallback': False, 'reason': None}
    if config['id'] not in ('Q6_parent', 'Q6_return_hold'):
        raise ValueError('unknown continuation probe configuration')
    hold = config['id'] == 'Q6_return_hold'
    memory, valid_memory = _memory(request.get('memory', {})) if hold else ({}, True)
    parent_request = copy.deepcopy(request) if hold else request
    if hold:
        parent_request['memory'] = memory['parent_memory']
    response = reference_adapter.decide(parent_request, {'id': 'Q6'})
    LAST_STATUS = copy.deepcopy(reference_adapter.LAST_STATUS)
    if LAST_STATUS.get('fallback'):
        raise RuntimeError('frozen Q6 parent fallback: ' + str(LAST_STATUS.get('reason')))
    if not hold:
        return response
    response = copy.deepcopy(response)
    memory['parent_memory'] = response['memory']
    response['memory'] = memory
    state = request['state']
    today = state['day']
    if (request['phase'] != 'match' or today == 59 or not valid_memory
            or any(e['day'] >= today for e in memory['hold_events'])):
        return response
    if len(state['members']) > 200:
        raise ValueError('hold probe supports at most 200 public actors')
    members = {m['member_id']: m for m in state['members']}
    candidates, past = _return_candidates(state)
    held = set(memory['held'])
    best = None
    for index, pair in enumerate(response['pairs']):
        if held.intersection(pair):
            continue
        old = _score(members[pair[0]], members[pair[1]])
        for position, actor in enumerate(pair):
            for order, candidate in enumerate(candidates):
                other = candidate['member_id']
                if (other in pair or other in held
                        or frozenset((actor, other)) in past
                        or eligibility(members[actor], candidate)['status'] != 'feasible'):
                    continue
                new = _score(members[actor], candidate)
                key = (-(new - old), index, position, order)
                if new > old and (best is None or key < best[0]):
                    best = (key, index, list(pair), actor, other, old, new)
    if best is not None:
        _, index, pair, actor, alternative, old, new = best
        response['pairs'].pop(index)
        memory['held'].extend(pair)
        memory['hold_events'].append({
            'day': today, 'endpoints': pair, 'alternative': alternative,
            'held_endpoint': actor, 'target_day': today + 1,
            'old_score': old, 'new_score': new,
            'public_reason': 'latest_nonmutual_assignment_plus_8',
        })
    return response
