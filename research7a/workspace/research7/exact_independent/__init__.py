"""Independent exact reduced-model checker and rational history-tree DP.

Owned exclusively by 7a under Work Order WO02.
Does NOT import R6 or R7 developer solvers or simulator internals.
Supports verification of T02-T10 and T31.
"""

from research7.exact_independent.schema import (
    ReducedActor,
    ReducedEdge,
    ReducedModelSpec,
    ReducedState,
    ReducedAction,
    ReducedOutcome,
    CaseResult
)
from research7.exact_independent.solver import (
    vertex_recursive_enumeration,
    rational_history_tree_dp,
    enumerate_labelled_4vertex_graphs,
    verify_matching_legality
)
from research7.exact_independent.specifications import (
    get_all_test_specifications,
    run_exact_specification_check
)

__all__ = [
    'ReducedActor',
    'ReducedEdge',
    'ReducedModelSpec',
    'ReducedState',
    'ReducedAction',
    'ReducedOutcome',
    'CaseResult',
    'vertex_recursive_enumeration',
    'rational_history_tree_dp',
    'enumerate_labelled_4vertex_graphs',
    'verify_matching_legality',
    'get_all_test_specifications',
    'run_exact_specification_check'
]
