"""Candidate A1: Terminal-value general-graph allocation (light inference).

Solves unrestricted maximum weight matching on the exact legal general graph
with maxcardinality=False. Edge weights quantized deterministically at 1e-6.
Pre-computes legal score-greedy action as an instant interrupt fallback and own parent.
Asks use baseline FIFO.
"""

import copy
import itertools
from typing import Any, Dict, List, Optional, Set, Tuple
import networkx as nx

from kit import SOFT, baseline_asks, eligibility

LAST_STATUS = {"fallback": False, "reason": None}


def compute_pair_score(a: Dict[str, Any], b: Dict[str, Any], day: int = 0, weight_model: Optional[str] = "population") -> float:
    """Computes pair ranking score from observed fields."""
    if weight_model == "population":
        try:
            from research3.model_candidates import population
            q, _ = population(a, b, day)
            return float(q)
        except Exception:
            pass
    # Standard fallback / soft score model: count of matching observed soft fields in [0, 4]
    return float(sum(
        a.get('fields', {}).get(k) is not None and
        a.get('fields', {}).get(k) == b.get('fields', {}).get(k)
        for k in SOFT
    ))


def get_feasible_edges(state: Dict[str, Any], weight_model: Optional[str] = "population") -> Dict[Tuple[int, int], float]:
    """Extracts all legally feasible edges among available actors with deterministic weights."""
    active = [m for m in state.get('members', []) if m.get('available')]
    past = {
        tuple(sorted((i['user_a'], i['user_b'])))
        for i in state.get('introductions', [])
    }
    day = state.get('day', 0)
    edges = {}
    for a, b in itertools.combinations(active, 2):
        pair = tuple(sorted((a['member_id'], b['member_id'])))
        if pair not in past and eligibility(a, b).get('status') == 'feasible':
            edges[pair] = compute_pair_score(a, b, day=day, weight_model=weight_model)
    return edges


def score_greedy_match(scores: Dict[Tuple[int, int], float]) -> List[Tuple[int, int]]:
    """Deterministic score-greedy matching (own parent and interrupt fallback)."""
    # Sort descending by score, tie-breaking by lexicographical node IDs
    sorted_pairs = sorted(scores.keys(), key=lambda p: (-scores[p], p[0], p[1]))
    used = set()
    pairs = []
    for u, v in sorted_pairs:
        if u not in used and v not in used:
            used.add(u)
            used.add(v)
            pairs.append((u, v))
    return sorted(pairs)


def decide_a1_match(state: Dict[str, Any], config: Dict[str, Any] = None) -> Tuple[List[List[int]], Dict[str, Any]]:
    """Unrestricted maximum weight general-graph matching with quantized weights."""
    weight_model = config.get('weight_model') if config else None
    scores = get_feasible_edges(state, weight_model)
    if not scores:
        return [], {"solver": "empty", "edges": 0}

    # Precompute deterministic score-greedy fallback
    fallback_matching = score_greedy_match(scores)

    # Build NetworkX graph with quantized integer weights
    G = nx.Graph()
    for (u, v), weight in sorted(scores.items()):
        quantized = int(round(weight * 1_000_000))
        G.add_edge(u, v, weight=quantized, raw_weight=weight)

    try:
        # Solve maximum weight matching with maxcardinality=False
        # Solves each connected component independently
        raw_matching = nx.max_weight_matching(G, maxcardinality=False, weight='weight')
        chosen_pairs = sorted(tuple(sorted(p)) for p in raw_matching)
        return [list(p) for p in chosen_pairs], {"solver": "max_weight_matching", "edges": len(scores)}
    except Exception as exc:
        # Fall back cleanly to score-greedy
        return [list(p) for p in fallback_matching], {"solver": "greedy_fallback", "error": str(exc)}


def decide(request: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
    global LAST_STATUS
    LAST_STATUS = {"fallback": False, "reason": None}
    phase = request.get('phase', 'ask')
    state = request.get('state', {})
    memory = request.get('memory')

    if phase == 'ask':
        # Baseline FIFO asks
        asks = baseline_asks(state)
        return {"asks": asks, "memory": memory}
    else:
        try:
            pairs, info = decide_a1_match(state, config)
            LAST_STATUS = {"fallback": (info.get("solver") == "greedy_fallback"), "info": info}
            return {"pairs": pairs, "memory": memory}
        except Exception as exc:
            LAST_STATUS = {"fallback": True, "reason": str(exc)}
            from kit import baseline_match
            return {"pairs": baseline_match(state), "memory": memory}
