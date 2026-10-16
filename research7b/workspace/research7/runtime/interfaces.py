"""Public wire contract of the governing kit.py and evaluate.py."""
import copy
import json
from typing import Any, Dict, List, Set, Tuple

from kit import HARD, SOFT, VERSION, eligibility

HARD_FIELDS = set(HARD)
SOFT_FIELDS = set(SOFT)
ALL_KNOWN_FIELDS = HARD_FIELDS | SOFT_FIELDS
MAX_ASK_BUDGET = 12
HARD_BUNDLE_COST = 3
SOFT_FIELD_COST = 1
MEMORY_LIMIT_BYTES = 1024 * 1024


class PublicProtocolError(ValueError):
    """A request violates the governing public wire contract."""


def _keys(value, expected, label):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise PublicProtocolError(f'{label} must contain exactly {sorted(expected)}')


def _public_value(value):
    # Questionnaire answers are scalars or arrays of strings, never opaque maps.
    return (value is None or type(value) in (str, int, bool)
            or isinstance(value, list) and all(isinstance(x, str) for x in value))


def sanitize_observation(raw_obs: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the evaluator request and copy it without exposing simulator internals.

    Reject unknown keys at every structured boundary, rather than passing arbitrary
    nested dictionaries (including hidden member truth) to a policy.
    """
    _keys(raw_obs, {'schema_version', 'phase', 'state', 'memory'}, 'request')
    if raw_obs['schema_version'] != VERSION or raw_obs['phase'] not in ('ask', 'match'):
        raise PublicProtocolError('Unsupported version or phase')
    state = raw_obs['state']
    _keys(state, {'schema_version', 'synthetic', 'day', 'ask_budget_remaining',
                  'members', 'introductions', 'feedback', 'ask_log'}, 'state')
    if state['schema_version'] != VERSION or state['synthetic'] is not True:
        raise PublicProtocolError('Unsupported state version or synthetic flag')
    if type(state['day']) is not int or state['day'] < 0:
        raise PublicProtocolError('Invalid day')
    budget = state['ask_budget_remaining']
    if type(budget) is not int or not 0 <= budget <= MAX_ASK_BUDGET:
        raise PublicProtocolError('Invalid remaining ask budget')
    for key in ('members', 'introductions', 'feedback', 'ask_log'):
        if not isinstance(state[key], list):
            raise PublicProtocolError(f'{key} must be an array')
    ids = set()
    for member in state['members']:
        _keys(member, {'member_id', 'pool_id', 'synthetic', 'age', 'gender', 'zone',
                      'arrived_day', 'fields', 'field_status', 'field_observed_day',
                      'source', 'available'}, 'member')
        ident = member['member_id']
        if not isinstance(ident, str) or ident in ids:
            raise PublicProtocolError('Member IDs must be unique strings')
        ids.add(ident)
        for field_map in ('fields', 'field_status', 'field_observed_day'):
            _keys(member[field_map], ALL_KNOWN_FIELDS, field_map)
        if not all(_public_value(v) for v in member['fields'].values()):
            raise PublicProtocolError('Invalid public questionnaire value')
        if not all(v in ('observed', 'declined', 'not_asked') for v in member['field_status'].values()):
            raise PublicProtocolError('Invalid field status')
        if not all(v is None or type(v) is int for v in member['field_observed_day'].values()):
            raise PublicProtocolError('Invalid field observation day')
        if type(member['available']) is not bool or member['arrived_day'] > state['day']:
            raise PublicProtocolError('Invalid public member availability or arrival')
    for intro in state['introductions']:
        _keys(intro, {'introduction_id', 'user_a', 'user_b', 'assigned_day',
                      'response_deadline_day', 'logging_policy', 'propensity'}, 'introduction')
    for event in state['feedback']:
        keys = {'introduction_id', 'member_id', 'event', 'value', 'occurred_day', 'observed_day'}
        if isinstance(event, dict) and 'missing_reason' in event:
            keys.add('missing_reason')
        _keys(event, keys, 'feedback event')
        if not _public_value(event['value']):
            raise PublicProtocolError('Invalid feedback value')
        if event['observed_day'] > state['day']:
            raise PublicProtocolError('Unreleased future feedback')
    for ask in state['ask_log']:
        _keys(ask, {'member_id', 'field', 'observed_day', 'values', 'statuses'}, 'ask log')
        if ask['field'] not in {'constraints'} | SOFT_FIELDS:
            raise PublicProtocolError('Unknown ask-log field')
        fields = HARD_FIELDS if ask['field'] == 'constraints' else {ask['field']}
        _keys(ask['values'], fields, 'ask values')
        _keys(ask['statuses'], fields, 'ask statuses')
        if not all(_public_value(v) for v in ask['values'].values()):
            raise PublicProtocolError('Invalid ask value')
        if ask['observed_day'] > state['day']:
            raise PublicProtocolError('Unreleased future ask')
    ok, errors, _ = validate_policy_memory(raw_obs['memory'])
    if not ok:
        raise PublicProtocolError('; '.join(errors))
    try:
        # All public fields come from trusted observe(), but enforce strict JSON
        # so object references and non-finite payloads cannot cross the boundary.
        json.dumps(raw_obs, allow_nan=False)
    except (TypeError, ValueError, OverflowError) as exc:
        raise PublicProtocolError(f'Request is not strict JSON: {exc}') from exc
    return copy.deepcopy(raw_obs)


def validate_ask_batch(asks: Any, available_users: Set[str],
                       max_budget: int = MAX_ASK_BUDGET) -> Tuple[bool, List[str], int]:
    errors, seen, cost = [], set(), 0
    if not isinstance(asks, list):
        return False, ['Asks action must be an array'], 0
    for idx, ask in enumerate(asks):
        if (not isinstance(ask, dict) or set(ask) != {'member_id', 'field'}
                or not all(isinstance(v, str) for v in ask.values())):
            errors.append(f'Ask {idx}: expected exactly string member_id and field')
            continue
        ident, field = ask['member_id'], ask['field']
        if ident not in available_users:
            errors.append(f'Ask {idx}: unavailable member {ident}')
        if (ident, field) in seen:
            errors.append(f'Ask {idx}: duplicate ask')
        seen.add((ident, field))
        if field == 'constraints':
            cost += HARD_BUNDLE_COST
        elif field in SOFT_FIELDS:
            cost += SOFT_FIELD_COST
        else:
            errors.append(f'Ask {idx}: unknown field {field}')
    if cost > max_budget:
        errors.append(f'Ask cost {cost} exceeds remaining budget {max_budget}')
    return not errors, errors, cost


def validate_match_batch(pairs: Any, available_users: Set[str],
                         past_introductions: List[Dict[str, Any]],
                         members: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """Validate wire shape, allocation, history and public hard feasibility."""
    errors, seen = [], set()
    if not isinstance(pairs, list):
        return False, ['Pairs must be an array']
    past = {tuple(sorted((i['user_a'], i['user_b']))) for i in past_introductions}
    public = {m['member_id']: m for m in members}
    for idx, pair in enumerate(pairs):
        if not isinstance(pair, list) or len(pair) != 2 or not all(isinstance(v, str) for v in pair):
            errors.append(f'Pair {idx}: expected array of two strings')
            continue
        a, b = pair
        if a == b:
            errors.append(f'Pair {idx}: self-match')
        for ident in pair:
            if ident not in available_users or ident not in public or not public[ident]['available']:
                errors.append(f'Pair {idx}: unavailable member {ident}')
            if ident in seen:
                errors.append(f'Pair {idx}: overlapping allocation for {ident}')
            seen.add(ident)
        if tuple(sorted(pair)) in past:
            errors.append(f'Pair {idx}: repeat pair')
        if a in public and b in public and eligibility(public[a], public[b])['status'] != 'feasible':
            errors.append(f'Pair {idx}: hard constraint violation or missing constraint')
    return not errors, errors


def validate_policy_memory(memory: Any) -> Tuple[bool, List[str], int]:
    try:
        wire = json.dumps(memory, allow_nan=False).encode('utf-8')
    except (TypeError, ValueError, OverflowError) as exc:
        return False, [f'Memory is not strict JSON serializable: {exc}'], 0
    size = len(wire)
    errors = [f'Memory wire size {size} exceeds {MEMORY_LIMIT_BYTES} bytes limit'] if size > MEMORY_LIMIT_BYTES else []
    return not errors, errors, size
