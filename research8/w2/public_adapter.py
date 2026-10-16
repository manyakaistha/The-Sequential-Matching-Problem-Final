"""Public wire bridge, with a fail-closed deployment entry point.

No calibrated public transition asset is admitted yet. decide therefore runs
validated unchanged G. evaluate_projection is an OFFLINE integration seam for
reviewed declared-model fixtures, never a way to inject calendars through wire
config or memory. It validates real legality again after modeled planning.
"""
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
import json
from typing import Callable

from .bounded import BoundedConfig, BoundedPlanner
from research8.planner import LimitExceeded
from .protocol import PublicProtocolError, sanitize_observation, validate_ask_batch, validate_match_batch
from .public_rules import HARD, baseline_asks, baseline_match, eligibility

LIMIT = 1024 * 1024
MEM_SCHEMA = 'B1-public-memory/v1'


def _wire_size(obj):
    return len(json.dumps(obj, allow_nan=False, separators=(',', ':')).encode())


def checked_request(request):
    if _wire_size(request) > LIMIT:
        raise PublicProtocolError('Request exceeds1MiB')
    result = sanitize_observation(request)
    state, day = result['state'], result['state']['day']
    if not 0 <= day <= 59 or len(state['members']) > 200:
        raise PublicProtocolError('Unsupported action day or population')
    members = {m['member_id']: m for m in state['members']}
    for m in members.values():
        if (m['synthetic'] is not True or any(type(m[k]) is not str or not m[k]
                for k in ('pool_id', 'gender', 'zone', 'source'))):
            raise PublicProtocolError('Invalid or nested member metadata')
        if type(m['arrived_day']) is not int or not 0 <= m['arrived_day'] <= day:
            raise PublicProtocolError('Invalid public arrival')
        if type(m['age']) is not int or not 0 <= m['age'] <= 120:
            raise PublicProtocolError('Invalid public age')
        for field, status in m['field_status'].items():
            value, observed = m['fields'][field], m['field_observed_day'][field]
            if observed is not None and (type(observed) is not int or not 0 <= observed <= day):
                raise PublicProtocolError('Future or invalid field observation')
            if status == 'not_asked' and (value is not None or observed is not None):
                raise PublicProtocolError('Unasked field has a disclosed value/time')
            if status == 'declined' and value is not None:
                raise PublicProtocolError('Declined field contradicts disclosure')
            if status == 'observed' and (value is None or observed is None):
                raise PublicProtocolError('Observed field lacks value/time')
    seen_intros = set()
    for intro in state['introductions']:
        if any(type(intro[k]) is not str or not intro[k]
               for k in ('introduction_id', 'user_a', 'user_b', 'logging_policy')):
            raise PublicProtocolError('Invalid or nested introduction metadata')
        propensity = intro['propensity']
        if propensity is not None and (type(propensity) not in (int, float) or not 0 <= propensity <= 1):
            raise PublicProtocolError('Invalid public propensity')
        if (intro['introduction_id'] in seen_intros or intro['user_a'] not in members
                or intro['user_b'] not in members or intro['user_a'] == intro['user_b']):
            raise PublicProtocolError('Invalid introduction identity/endpoints')
        seen_intros.add(intro['introduction_id'])
        if type(intro['assigned_day']) is not int or not 0 <= intro['assigned_day'] <= day:
            raise PublicProtocolError('Invalid introduction assignment')
        if intro['response_deadline_day'] != intro['assigned_day'] + 7:
            raise PublicProtocolError('Invalid public response deadline')
    for event in state['feedback']:
        if (type(event['event']) is not str or type(event['introduction_id']) is not str
                or (event['member_id'] is not None and type(event['member_id']) is not str)
                or (event.get('missing_reason') is not None and type(event['missing_reason']) is not str)):
            raise PublicProtocolError('Invalid or nested feedback metadata')
        observed = event['observed_day']
        if type(observed) is not int or not 0 <= observed <= day:
            raise PublicProtocolError('Invalid feedback release')
        occurred = event['occurred_day']
        if occurred is not None and (type(occurred) is not int or not 0 <= occurred <= observed):
            raise PublicProtocolError('Invalid feedback occurrence')
        if event['introduction_id'] not in seen_intros:
            raise PublicProtocolError('Feedback references unknown introduction')
        if event['member_id'] is not None and event['member_id'] not in members:
            raise PublicProtocolError('Feedback references unknown member')
    for ask in state['ask_log']:
        if any(value not in ('observed', 'declined', 'not_asked') for value in ask['statuses'].values()):
            raise PublicProtocolError('Invalid ask-log status')
        if ask['member_id'] not in members or type(ask['observed_day']) is not int or not 0 <= ask['observed_day'] <= day:
            raise PublicProtocolError('Invalid ask-log release')
    memory = result['memory']
    if memory is not None:
        expected = {'schema', 'last_day', 'arrival_counts', 'member_count', 'last_status'}
        if not isinstance(memory, dict) or set(memory) != expected or memory['schema'] != MEM_SCHEMA:
            raise PublicProtocolError('Unknown or private memory schema')
        if type(memory['last_day']) is not int or not 0 <= memory['last_day'] <= day:
            raise PublicProtocolError('Invalid memory day')
        if (not isinstance(memory['arrival_counts'], list) or len(memory['arrival_counts']) != memory['last_day'] + 1
                or any(type(n) is not int or n < 0 for n in memory['arrival_counts'])):
            raise PublicProtocolError('Invalid public arrival counters')
        if type(memory['member_count']) is not int or memory['member_count'] != sum(memory['arrival_counts']):
            raise PublicProtocolError('Invalid public member count')
        status = memory['last_status']
        if not isinstance(status, dict) or set(status) != {'mode', 'reason'} or any(type(v) is not str or len(v) > 240 for v in status.values()):
            raise PublicProtocolError('Invalid memory status')
    return result


def arrival_features(state):
    """All-arrived histogram, not available-pool change; zeros included.

    Rebuilding from deduplicated complete public members makes ask/match calls
    idempotent and never converts disappearance/busy status into arrival counts.
    """
    counts = Counter(m['arrived_day'] for m in state['members'])
    return {'arrival_counts': [counts.get(day, 0) for day in range(state['day'] + 1)],
            'member_count': len(state['members'])}


def _response(public, action, mode, reason):
    state, phase = public['state'], public['phase']
    available = {m['member_id'] for m in state['members'] if m['available']}
    if phase == 'ask':
        valid, errors, _ = validate_ask_batch(action, available, state['ask_budget_remaining'])
    else:
        valid, errors = validate_match_batch(action, available, state['introductions'], state['members'])
    if not valid:
        raise PublicProtocolError('Illegal real action: ' + ';'.join(errors))
    memory = dict(schema=MEM_SCHEMA, last_day=state['day'], **arrival_features(state),
                  last_status={'mode': mode, 'reason': reason[:240]})
    response = {'asks' if phase == 'ask' else 'pairs': action, 'memory': memory}
    if _wire_size(response) > LIMIT:
        raise PublicProtocolError('Response exceeds1MiB')
    return response


def _fallback(public, reason):
    state = public['state']
    action = baseline_asks(state) if public['phase'] == 'ask' else baseline_match(state)
    return _response(public, action, 'G_fallback', reason)


def decide(request, config=None):
    public = checked_request(request)
    config = {} if config is None else config
    if not isinstance(config, dict) or set(config) - {'id'} or config.get('id', 'B1') != 'B1':
        raise PublicProtocolError('No unreviewed model/config/calendar injection is allowed')
    # Admission of q/return/arrival/feedback/exit assets is a separate gate, not
    # a caller-supplied "admitted=True" bypass. No such receipt currently exists.
    return _fallback(public, 'public_joint_model_asset_not_admitted')


@dataclass(frozen=True)
class Projection:
    model: object
    prior: object
    actor_to_member: tuple[tuple[str, str], ...]
    outside_pairs: tuple[tuple[str, str], ...] = ()


def evaluate_projection(request, provider: Callable, config=BoundedConfig()):
    """OFFLINE public-adapter integration, including real-graph closure checks.

    Provider receives sanitized public input only. Its law is a declared
    assumption; this function is not the deployment decide entry point and
    supplies no asset provenance/calibration certificate.
    """
    public = checked_request(request)
    if public['phase'] != 'match':
        return _fallback(public, 'offline_projection_has_no_query_controller')
    projection = provider(deepcopy(public))
    if not isinstance(projection, Projection):
        raise PublicProtocolError('Provider must return a declared projection')
    planner = BoundedPlanner(projection.model, config)
    try:
        view = planner.public_view(projection.prior)
    except LimitExceeded:
        return _fallback(public, 'unsupported_projection_prior_cap')
    if view.day != public['state']['day']:
        raise PublicProtocolError('Projection clock differs from public day')
    mapping = dict(projection.actor_to_member)
    if len(mapping) != len(projection.actor_to_member) or len(set(mapping.values())) != len(mapping):
        raise PublicProtocolError('Projection mapping must be one-to-one')
    state = public['state']
    members = {m['member_id']: m for m in state['members']}
    if not set(view.arrived) <= set(mapping) or not set(mapping.values()) <= set(members):
        raise PublicProtocolError('Unseen/fake current projected member')
    for actor in view.arrived:
        if (actor in view.available) != members[mapping[actor]]['available']:
            raise PublicProtocolError('Projection contradicts observed availability')
    projected = {mapping[a] for a in view.arrived}
    past = {tuple(sorted((i['user_a'], i['user_b']))) for i in state['introductions']}
    reverse = {ident: actor for actor, ident in mapping.items()}
    for pair in past:
        if set(pair) <= projected:
            modeled_pair = tuple(sorted(reverse[ident] for ident in pair))
            if modeled_pair not in view.exhausted:
                raise PublicProtocolError('Projection omits a public exhausted dyad')
    if any(set(pair) & projected for pair in projection.outside_pairs):
        raise PublicProtocolError('Outside assignment touches a modeled actor')
    # No silently omitted unresolved current neighbors. This is conservative;
    # the current core has no future querying/pending-feedback/exit model.
    for actor in view.available:
        m = members[mapping[actor]]
        for other in members.values():
            if not other['available'] or other['member_id'] == m['member_id']:
                continue
            pair = tuple(sorted((m['member_id'], other['member_id'])))
            if pair in past:
                continue
            status = eligibility(m, other)['status']
            if status == 'needs_clarification':
                return _fallback(public, 'unsupported_unresolved_current_neighbor')
            if status == 'feasible' and other['member_id'] not in projected:
                return _fallback(public, 'unsupported_open_current_boundary')
    expected = set()
    for action in planner.legal_actions(projection.prior):
        for pair in action:
            real = tuple(sorted(mapping[a] for a in pair))
            if real in past or eligibility(members[real[0]], members[real[1]])['status'] != 'feasible':
                raise PublicProtocolError('Modeled current edge is not real eligible')
            expected.add(real)
    for a in view.available:
        for b in view.available:
            if a >= b:
                continue
            pair = tuple(sorted((mapping[a], mapping[b])))
            if pair not in past and eligibility(members[pair[0]], members[pair[1]])['status'] == 'feasible' and pair not in expected:
                return _fallback(public, 'unsupported_omitted_current_edge')
    result = planner.solve(projection.prior)
    if result.used_fallback:
        return _fallback(public, result.fallback_reason)
    pairs = [list(pair) for pair in projection.outside_pairs]
    pairs.extend([mapping[a], mapping[b]] for a, b in result.action)
    return _response(public, pairs, 'offline_declared_projection', 'bounded_future_waiting')


if __name__ == '__main__':
    import sys
    request = json.load(sys.stdin)
    print(json.dumps(decide(request), allow_nan=False))
