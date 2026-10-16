"""Candidate Q1: Deterministic collision-aware hard query acquisition (light).

Evaluates exact maximum-cardinality matching over an optimistic possible graph
constructed from an 8-actor shortlist. Matching uses shipped baseline G.
"""

import copy
import itertools
from typing import Any, Dict, List, Set, Tuple
import networkx as nx

from kit import HARD, baseline_asks, baseline_match, eligibility

LAST_STATUS = {"fallback": False, "reason": None}


def get_query_eligible_actors(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    eligible = []
    for m in state.get('members', []):
        if not m.get('available'):
            continue
        statuses = m.get('field_status', {})
        # Must have at least one missing/unasked hard field (kit uses 'not_asked' or None)
        has_missing = any(statuses.get(k) in (None, 'not_asked', 'unasked', 'missing') or m.get('fields', {}).get(k) is None for k in HARD)
        # Must have NO hard-declined field
        has_declined = any(statuses.get(k) == 'declined' for k in HARD)
        if has_missing and not has_declined:
            eligible.append(m)
    return eligible


def get_verified_actors(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    verified = []
    for m in state.get('members', []):
        if not m.get('available'):
            continue
        statuses = m.get('field_status', {})
        all_observed = all(statuses.get(k) == 'observed' for k in HARD)
        has_declined = any(statuses.get(k) == 'declined' for k in HARD)
        if all_observed and not has_declined:
            verified.append(m)
    return verified


def decide_q1_asks(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    budget = state.get('ask_budget_remaining', 0)
    if budget < 3:
        return []

    past_dyads = {tuple(sorted((i['user_a'], i['user_b']))) for i in state.get('introductions', [])}

    query_eligible = get_query_eligible_actors(state)
    if not query_eligible:
        return []

    verified = get_verified_actors(state)
    query_set = {m['member_id']: m for m in query_eligible}
    verified_set = {m['member_id']: m for m in verified}

    all_candidates = {**verified_set, **query_set}
    incident_edges = {u_id: set() for u_id in query_set}

    for u_id, u in query_set.items():
        for v_id, v in all_candidates.items():
            if u_id >= v_id:
                continue
            pair = (u_id, v_id)
            if pair in past_dyads:
                continue
            el = eligibility(u, v)
            if el.get('status') == 'needs_clarification':
                incident_edges[u_id].add(v_id)
                if v_id in incident_edges:
                    incident_edges[v_id].add(u_id)

    # Rank query actors: descending degree, then arrival age (ascending arrived_day), then member_id
    def rank_key(m):
        m_id = m['member_id']
        deg = len(incident_edges.get(m_id, set()))
        return (-deg, m.get('arrived_day', 0), m_id)

    ranked_actors = sorted(query_eligible, key=rank_key)
    shortlist = ranked_actors[:8]

    k = min(4, budget // 3, len(shortlist))
    if k == 0:
        return []

    subsets = list(itertools.combinations(shortlist, k))

    # Identify FIFO subset (first k in arrival order with missing hard fields)
    fifo_sorted = sorted(query_eligible, key=lambda m: (m.get('arrived_day', 0), m['member_id']))
    fifo_subset = tuple(fifo_sorted[:k])

    best_subset = None
    best_cardinality = -1

    for s in subsets:
        active_subset_ids = set(verified_set.keys()) | {m['member_id'] for m in s}
        G = nx.Graph()
        G.add_nodes_from(active_subset_ids)
        for u_id in active_subset_ids:
            for v_id in active_subset_ids:
                if u_id >= v_id:
                    continue
                pair = (u_id, v_id)
                if pair in past_dyads:
                    continue
                el = eligibility(all_candidates[u_id], all_candidates[v_id])
                if el.get('status') in ('feasible', 'needs_clarification'):
                    G.add_edge(u_id, v_id)

        matching = nx.max_weight_matching(G, maxcardinality=True)
        card = len(matching)

        if card > best_cardinality:
            best_cardinality = card
            best_subset = s
        elif card == best_cardinality:
            # Deterministic tie-breaking: prefer FIFO, else oldest actor tuple
            if s == fifo_subset:
                best_subset = s
            elif best_subset != fifo_subset:
                s_key = tuple(sorted((m.get('arrived_day', 0), m['member_id']) for m in s))
                best_key = tuple(sorted((m.get('arrived_day', 0), m['member_id']) for m in best_subset))
                if s_key < best_key:
                    best_subset = s

    if best_subset is None:
        return []

    asks = [{'member_id': m['member_id'], 'field': 'constraints'} for m in best_subset]
    return asks


def decide(request: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
    global LAST_STATUS
    LAST_STATUS = {"fallback": False, "reason": None}
    phase = request.get('phase', 'ask')
    state = request.get('state', {})
    memory = request.get('memory')

    if phase == 'ask':
        try:
            asks = decide_q1_asks(state)
            return {"asks": asks, "memory": memory}
        except Exception as exc:
            LAST_STATUS = {"fallback": True, "reason": str(exc)}
            return {"asks": [], "memory": memory}
    else:
        # Match remains shipped G (greedy matching)
        pairs = baseline_match(state)
        return {"pairs": pairs, "memory": memory}
