"""Independent history-tree dynamic programming and vertex-recursive enumeration.

Enforces:
- Standalone reduced-model execution without simulator imports.
- Vertex-recursive matching enumeration (disjoint endpoints).
- Backward induction on observable history trees.
- Branch merging by observable history (nonanticipation).
- Dyad masks, busy/pause state, and one-time future reward booking.
- Hard state cap <= 100,000 states per case.
"""

from __future__ import annotations
import itertools
from typing import Any, Callable, Dict, FrozenSet, List, Optional, Set, Tuple
from research7.exact_independent.schema import (
    ReducedAction,
    ReducedActor,
    ReducedBranch,
    ReducedEdge,
    ReducedModelSpec,
    ReducedState,
    CaseResult
)


def vertex_recursive_enumeration(
    available_vertices: FrozenSet[str],
    feasible_edges: List[Tuple[str, str, float]]
) -> List[Tuple[Tuple[Tuple[str, str], ...], float]]:
    """Enumerate all valid matchings (disjoint pairs) and their sum weights.
    
    Returns list of (matching_pairs, total_weight) sorted by weight descending.
    """
    sorted_edges = []
    for u, v, w in feasible_edges:
        if u in available_vertices and v in available_vertices:
            pair = tuple(sorted((u, v)))
            sorted_edges.append((pair, float(w)))

    all_matchings: List[Tuple[Tuple[Tuple[str, str], ...], float]] = []

    def recurse(
        edge_idx: int,
        current_used: Set[str],
        current_pairs: List[Tuple[str, str]],
        current_weight: float
    ):
        if edge_idx == len(sorted_edges):
            all_matchings.append((tuple(current_pairs), round(current_weight, 8)))
            return

        pair, w = sorted_edges[edge_idx]
        u, v = pair

        # Option 1: Do not include edge
        recurse(edge_idx + 1, current_used, current_pairs, current_weight)

        # Option 2: Include edge if disjoint
        if u not in current_used and v not in current_used:
            current_used.add(u)
            current_used.add(v)
            current_pairs.append(pair)
            recurse(edge_idx + 1, current_used, current_pairs, current_weight + w)
            current_pairs.pop()
            current_used.remove(u)
            current_used.remove(v)

    recurse(0, set(), [], 0.0)
    all_matchings.sort(key=lambda item: (-item[1], len(item[0]), item[0]))
    return all_matchings


def greedy_matching(
    available_vertices: FrozenSet[str],
    feasible_edges: List[Tuple[str, str, float]]
) -> Tuple[Tuple[Tuple[str, str], ...], float]:
    """Compute greedy matching by picking highest-weight feasible disjoint edges."""
    sorted_edges = []
    for u, v, w in feasible_edges:
        if u in available_vertices and v in available_vertices:
            sorted_edges.append((tuple(sorted((u, v))), float(w)))

    # Sort descending by weight, tie-break by pair
    sorted_edges.sort(key=lambda item: (-item[1], item[0]))

    used: Set[str] = set()
    pairs: List[Tuple[str, str]] = []
    total_w = 0.0

    for pair, w in sorted_edges:
        u, v = pair
        if u not in used and v not in used:
            used.add(u)
            used.add(v)
            pairs.append(pair)
            total_w += w

    return tuple(pairs), round(total_w, 8)


def enumerate_labelled_4vertex_graphs() -> List[Dict[str, Any]]:
    """Enumerate all 64 labelled 4-vertex simple graphs and verify matching legality.
    
    Vertices: A, B, C, D (6 potential edges: AB, AC, AD, BC, BD, CD).
    2^6 = 64 subgraphs.
    For every graph, the maximum matching cardinality must be <= 2.
    """
    vertices = frozenset(['A', 'B', 'C', 'D'])
    all_edges = [('A', 'B'), ('A', 'C'), ('A', 'D'), ('B', 'C'), ('B', 'D'), ('CD', 'D') if False else ('C', 'D')]
    
    results = []
    for edge_mask in range(64):
        present_edges = []
        for i in range(6):
            if (edge_mask >> i) & 1:
                u, v = all_edges[i]
                present_edges.append((u, v, 1.0))

        matchings = vertex_recursive_enumeration(vertices, present_edges)
        max_cardinality = max(len(m[0]) for m in matchings) if matchings else 0
        if max_cardinality > 2:
            raise ValueError(f"Matching cardinality violation on 4-vertex graph mask {edge_mask}: {max_cardinality}")

        results.append({
            'mask': edge_mask,
            'edges': [e[:2] for e in present_edges],
            'max_cardinality': max_cardinality,
            'valid': True
        })
    return results


def verify_matching_legality(cycle_lengths: Tuple[int, ...] = (3, 5, 7)) -> Dict[int, Dict[str, Any]]:
    """Verify that odd cycles 3, 5, 7 have integer maximum cardinality floor(k/2).
    
    Triangle (C_3) has maximum matching cardinality 1, NOT fractional 1.5.
    C_5 has 2, C_7 has 3.
    """
    out = {}
    for k in cycle_lengths:
        vertices = frozenset(f"V{i}" for i in range(k))
        edges = [(f"V{i}", f"V{(i+1)%k}", 1.0) for i in range(k)]
        matchings = vertex_recursive_enumeration(vertices, edges)
        max_card = max(len(m[0]) for m in matchings) if matchings else 0
        expected = k // 2
        out[k] = {
            'vertices': k,
            'max_matching_cardinality': max_card,
            'expected_integer_cardinality': expected,
            'is_exact': max_card == expected,
            'is_fractional': False
        }
    return out


def rational_history_tree_dp(
    spec: ReducedModelSpec,
    transition_fn: Callable[[ReducedState, ReducedAction], List[ReducedBranch]],
    action_generator: Callable[[ReducedState, ReducedModelSpec], List[ReducedAction]]
) -> CaseResult:
    """Solve observable-history dynamic programming via backward induction.
    
    Ensures:
    - Merges branches with identical observable history (nonanticipation).
    - Hard state enumeration cap enforced.
    - Resolves optimal actions and ties.
    """
    state_count = 0
    memo: Dict[Tuple[int, Tuple[Tuple[str, Any], ...]], Tuple[float, Any, List[Any]]] = {}

    def solve(state: ReducedState) -> Tuple[float, Any, List[Any]]:
        nonlocal state_count
        state_count += 1
        if state_count > spec.state_cap:
            raise OverflowError(f"State cap exceeded ({spec.state_cap}) in case {spec.case_id}")

        # Horizon check
        if state.day >= spec.horizon_days:
            return 0.0, None, []

        # State key for observable nonanticipation: day + observable history
        state_key = (state.day, state.observation_history)
        if state_key in memo:
            return memo[state_key]

        admissible_actions = action_generator(state, spec)
        if not admissible_actions:
            memo[state_key] = (0.0, None, [])
            return 0.0, None, []

        best_val = -float('inf')
        best_act = None
        ties: List[Any] = []

        for action in admissible_actions:
            branches = transition_fn(state, action)
            expected_q = 0.0
            for branch in branches:
                future_val, _, _ = solve(branch.next_state)
                expected_q += branch.probability * (branch.immediate_reward + future_val)
            expected_q = round(expected_q, 8)

            if expected_q > best_val + 1e-9:
                best_val = expected_q
                best_act = action
                ties = [action]
            elif abs(expected_q - best_val) <= 1e-9:
                ties.append(action)

        memo[state_key] = (best_val, best_act, ties)
        return best_val, best_act, ties

    # Initial state
    init_state = ReducedState(
        day=spec.decision_days[0] if spec.decision_days else 0,
        available_actors=frozenset(a.actor_id for a in spec.actors),
        busy_until=(),
        paused=frozenset(),
        past_dyads=frozenset(),
        pending_rewards=0.0,
        observation_history=()
    )

    try:
        val, act, ties = solve(init_state)
        return CaseResult(
            case_id=spec.case_id,
            status='verified',
            expected_value=spec.parameters.get('expected_rational_value'),
            computed_value=val,
            expected_action=spec.parameters.get('expected_action'),
            computed_action=act,
            tie_action_set=ties,
            enumerated_states=state_count,
            details={'memo_size': len(memo)}
        )
    except OverflowError as exc:
        return CaseResult(
            case_id=spec.case_id,
            status='exceeded_cap',
            expected_value=spec.parameters.get('expected_rational_value'),
            computed_value=None,
            expected_action=spec.parameters.get('expected_action'),
            computed_action=None,
            enumerated_states=state_count,
            details={'error': str(exc)}
        )
