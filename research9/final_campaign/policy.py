"""Finite learned-policy portfolio; public approximations, never Bellman claims.

Soft VOI uses empirical disclosed answers and immediate matching value only.
Continuation assumes survival of currently available actors and models only
public rejection-clock returns; no anonymous arrivals or hidden calendars.
All work caps are deterministic. The host enforces the runtime deadline.
"""
from __future__ import annotations

import copy
import hashlib
import itertools
import json
from pathlib import Path
import random

import numpy as np

from research8.continuation_probe.policy import _return_candidates
from research8.soft_query_followup.v2 import reference_adapter
from research8.w2.public_rules import HARD, SOFT, eligibility
from . import features, models
from .inference_features import batch_pair_features

LAST_STATUS = {'fallback': False, 'reason': None}
IDS = ('model_greedy', 'model_soft', 'model_repair', 'model_continuation')
EPS = 1e-12


def _asset(config):
    path = Path(config['model_path'])
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != config['model_sha256']:
        raise ValueError('model asset hash mismatch')
    asset = json.loads(raw)
    if (asset.get('schema') != 'final-model-asset-v1'
            or asset.get('feature_names') != features.feature_names()
            or asset.get('kind') not in ('direct', 'funnel')
            or len(asset.get('models', [])) != (1 if asset.get('kind') == 'direct' else 3)):
        raise ValueError('model asset contract mismatch')
    for model in asset['models']:
        for key in ('mean', 'scale', 'coefficients'):
            a = np.asarray(model.get(key), dtype=float)
            if a.shape != (74,) or not np.isfinite(a).all():
                raise ValueError('invalid model vector')
        if np.any(np.asarray(model['scale']) <= 0) or not np.isfinite(model['intercept']):
            raise ValueError('invalid model scaling/intercept')
    return asset


def _predict(asset, matrix):
    q = np.ones(len(matrix))
    for model in asset['models']:
        p = np.asarray(models.predict(model, matrix))
        if p.shape != q.shape or not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
            raise ValueError('invalid model probability vector')
        q *= p
    return q


def _graph(state, asset, context=None, actors=None, extra_past=()):
    members = state['members'] if actors is None else actors
    available = [m for m in members if m['available']]
    past = {frozenset((i['user_a'], i['user_b'])) for i in state['introductions']}
    past.update(frozenset(p) for p in extra_past)
    pairs = [(a, b) for a, b in itertools.combinations(available, 2)
             if frozenset((a['member_id'], b['member_id'])) not in past
             and eligibility(a, b)['status'] == 'feasible']
    values = _predict(asset, batch_pair_features(state, pairs, context))
    return {(a['member_id'], b['member_id']): float(q)
            for (a, b), q in zip(pairs, values)}


def _greedy(graph):
    # Stable graph insertion order is public member order; IDs are lookup keys.
    used, matching = set(), []
    for edge in sorted(graph, key=lambda e: -graph[e]):
        if not used.intersection(edge):
            matching.append(edge)
            used.update(edge)
    return matching


def _value(matching, graph):
    return sum(graph[e] for e in matching)


def _repair(graph):
    """At most two passes and 2000 total exchange probes; ties retain parent."""
    matching = _greedy(graph)
    lookup = {frozenset(edge): edge for edge in graph}
    probes = 0
    for _ in range(2):
        used = set(itertools.chain.from_iterable(matching))
        actors = list(dict.fromkeys(itertools.chain.from_iterable(graph)))
        free = [a for a in actors if a not in used]
        best = None
        for i, edge in enumerate(matching):
            a, b = edge
            for u, v in itertools.combinations(free, 2):
                for proposed in (((a, u), (b, v)), ((a, v), (b, u))):
                    probes += 1
                    keys = [lookup.get(frozenset(e)) for e in proposed]
                    if all(k is not None for k in keys):
                        gain = _value(keys, graph) - graph[edge]
                        if gain > EPS and (best is None or gain > best[0] + EPS):
                            best = (gain, (i,), keys)
                    if probes >= 2000:
                        break
                if probes >= 2000:
                    break
            if probes >= 2000:
                break
        if probes < 2000:
            for i, j in itertools.combinations(range(len(matching)), 2):
                a, b = matching[i]
                c, d = matching[j]
                for proposed in (((a, c), (b, d)), ((a, d), (b, c))):
                    probes += 1
                    keys = [lookup.get(frozenset(e)) for e in proposed]
                    if all(k is not None for k in keys):
                        gain = _value(keys, graph) - graph[matching[i]] - graph[matching[j]]
                        if gain > EPS and (best is None or gain > best[0] + EPS):
                            best = (gain, (i, j), keys)
                    if probes >= 2000:
                        break
                if probes >= 2000:
                    break
        if best is None:
            break
        _, removed, added = best
        matching = [e for i, e in enumerate(matching) if i not in removed] + added
        if probes >= 2000:
            break
    return matching


def _soft_asks(state, parent_asks, asset, repair=False):
    budget = state['ask_budget_remaining'] - sum(3 if a['field'] == 'constraints' else 1
                                                for a in parent_asks)
    if budget <= 0:
        return []
    context = features.prepare_state(state)
    graph = _graph(state, asset, context)
    controller = _repair if repair else _greedy
    base = _value(controller(graph), graph)
    by_id = {m['member_id']: m for m in state['members']}
    neighbors = {ident: [] for ident in by_id}
    for a, b in graph:
        neighbors[a].append(b)
        neighbors[b].append(a)
    candidates = []
    parent_keys = {(a['member_id'], a['field']) for a in parent_asks}
    for order, member in enumerate(state['members']):
        actor = member['member_id']
        if not member['available'] or not neighbors[actor]:
            continue
        for field_order, field in enumerate(SOFT):
            if (member['fields'].get(field) is None
                    and member['field_status'].get(field) == 'not_asked'
                    and (actor, field) not in parent_keys
                    and any(by_id[n]['fields'].get(field) is not None
                            for n in neighbors[actor])):
                candidates.append((-len(neighbors[actor]), order, field_order, actor, field))
    ranked = []
    for _, order, field_order, actor, field in sorted(candidates)[:8]:
        frequencies = {}
        for member in state['members']:
            value = member['fields'].get(field)
            if value is not None and member['field_status'].get(field) == 'observed':
                frequencies[value] = frequencies.get(value, 0) + 1
        if not frequencies:
            continue
        if len(frequencies) > 8:
            # Work cap is explicit; never truncate the empirical answer law.
            continue
        expected = 0.
        actor_member = by_id[actor]
        affected = [e for e in graph if actor in e]
        for answer, count in frequencies.items():
            changed = copy.deepcopy(actor_member)
            changed['fields'][field] = answer
            changed['field_status'][field] = 'observed'
            changed['field_observed_day'][field] = state['day']
            pairs = [(changed if a == actor else by_id[a],
                      changed if b == actor else by_id[b]) for a, b in affected]
            altered = dict(graph)
            altered.update(zip(affected, map(float, _predict(asset,
                batch_pair_features(state, pairs, context)))))
            expected += count / sum(frequencies.values()) * _value(controller(altered), altered)
        gain = max(0., expected - base)
        ranked.append((-gain, order, field_order, {'member_id': actor, 'field': field}))
    return [r[3] for r in sorted(ranked, key=lambda r: r[:3])[:min(8, budget)]]


def _memory(raw):
    if raw == {} or raw is None:
        return {'parent_memory': {}, 'held': [], 'return_yes': 0, 'return_no': 0,
                'expected_day': None, 'expected_ids': []}
    value = copy.deepcopy(raw)
    if (not isinstance(value, dict) or not isinstance(value.get('parent_memory'), dict)
            or not isinstance(value.get('held'), list) or len(value['held']) > 200
            or len(set(value['held'])) != len(value['held'])
            or not all(isinstance(x, str) for x in value['held'])
            or any(type(value.get(k)) is not int or value[k] < 0
                   for k in ('return_yes', 'return_no'))
            or value.get('expected_day') is not None and type(value['expected_day']) is not int
            or not isinstance(value.get('expected_ids'), list)
            or len(value['expected_ids']) > 8
            or not all(isinstance(x, str) for x in value['expected_ids'])):
        raise ValueError('invalid campaign policy memory')
    return value


def _update_returns(state, memory):
    if memory['expected_day'] is not None and memory['expected_day'] <= state['day']:
        if memory['expected_day'] == state['day']:
            available = {m['member_id'] for m in state['members'] if m['available']}
            memory['return_yes'] += sum(i in available for i in memory['expected_ids'])
            memory['return_no'] += sum(i not in available for i in memory['expected_ids'])
        memory['expected_day'], memory['expected_ids'] = None, []


def _continuation(state, matching, graph, asset, memory):
    if state['day'] == 59:
        return matching
    returns, _ = _return_candidates(state)
    returns = returns[:8]
    memory['expected_day'] = state['day'] + 1
    memory['expected_ids'] = [m['member_id'] for m in returns]
    if not returns:
        return matching
    p = (memory['return_yes'] + 1) / (memory['return_yes'] + memory['return_no'] + 2)
    tomorrow = copy.deepcopy(state)
    tomorrow['day'] += 1
    # Evaluate each possible edge once; scenarios only select actors and edges.
    actors = [copy.deepcopy(m) for m in state['members'] if m['available'] or m in returns]
    for member in actors:
        member['available'] = True
    future = _graph(tomorrow, asset, features.prepare_state(tomorrow), actors)
    rng = random.Random(913700 + state['day'])
    scenarios = [{m['member_id'] for m in returns if rng.random() < p} for _ in range(16)]
    now_ids = {m['member_id'] for m in state['members'] if m['available']}

    def objective(action):
        busy = set(itertools.chain.from_iterable(action))
        exhausted = {frozenset(e) for e in action}
        value = _value(action, graph)
        for returned in scenarios:
            pool = (now_ids - busy) | returned
            allowed = {e: q for e, q in future.items()
                       if e[0] in pool and e[1] in pool and frozenset(e) not in exhausted}
            value += _value(_greedy(allowed), allowed) / 16
        return value

    best, best_value = matching, objective(matching)
    held = set(memory['held'])
    for index in sorted(range(len(matching)), key=lambda i: (graph[matching[i]], i))[:5]:
        edge = matching[index]
        if held.intersection(edge):
            continue
        action = [e for i, e in enumerate(matching) if i != index]
        value = objective(action)
        if value > best_value + EPS:
            best, best_value = action, value
    if best is not matching:
        omitted = next(e for e in matching if e not in best)
        memory['held'].extend(omitted)
    return best


def decide(request, config):
    global LAST_STATUS
    LAST_STATUS = {'fallback': False, 'reason': None}
    ident = config['id']
    if ident not in IDS:
        raise ValueError('unknown campaign policy')
    state = request['state']
    if len(state['members']) > 200:
        raise ValueError('campaign policy supports at most 200 actors')
    memory = _memory(request.get('memory', {}))
    _update_returns(state, memory)
    parent_request = copy.deepcopy(request)
    parent_request['memory'] = memory['parent_memory']
    if request['phase'] == 'ask':
        response = reference_adapter.decide(parent_request, {'id': 'Q6'})
        LAST_STATUS = copy.deepcopy(reference_adapter.LAST_STATUS)
        if LAST_STATUS.get('fallback'):
            raise RuntimeError('frozen Q6 fallback')
        memory['parent_memory'] = response['memory']
        asks = copy.deepcopy(response['asks'])
        if ident != 'model_greedy':
            asks += _soft_asks(state, asks, _asset(config), ident == 'model_repair')
        return {'asks': asks, 'memory': memory}
    asset = _asset(config)
    graph = _graph(state, asset, features.prepare_state(state))
    matching = _repair(graph) if ident == 'model_repair' else _greedy(graph)
    if ident == 'model_continuation':
        matching = _continuation(state, matching, graph, asset, memory)
    return {'pairs': [list(e) for e in matching], 'memory': memory}
