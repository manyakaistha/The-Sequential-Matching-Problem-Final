"""Independent reduced-model data contracts and case representations.

Pure Python stdlib, zero simulator or developer solver dependencies.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, List, Optional, Tuple, Union
import json


@dataclass(frozen=True)
class ReducedActor:
    actor_id: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    response_rate: float = 1.0
    bias: float = 0.0
    type_prior: Optional[Dict[str, float]] = None


@dataclass(frozen=True)
class ReducedEdge:
    user_a: str
    user_b: str
    q: float  # Base qualified expectation
    p: float = 1.0  # Return probability
    weight: float = 1.0  # Static weight or instant value


@dataclass(frozen=True)
class ReducedState:
    day: int
    available_actors: FrozenSet[str]
    busy_until: Tuple[Tuple[str, int], ...] = ()
    paused: FrozenSet[str] = frozenset()
    past_dyads: FrozenSet[Tuple[str, str]] = frozenset()
    pending_rewards: float = 0.0
    observation_history: Tuple[Tuple[str, Any], ...] = ()

    def is_available(self, actor: str) -> bool:
        if actor in self.paused:
            return False
        if actor not in self.available_actors:
            return False
        for a, until in self.busy_until:
            if a == actor and until > self.day:
                return False
        return True

    def get_available_set(self) -> FrozenSet[str]:
        busy_map = dict(self.busy_until)
        return frozenset(
            a for a in self.available_actors
            if a not in self.paused and busy_map.get(a, -1) <= self.day
        )


@dataclass(frozen=True)
class ReducedAction:
    ask_batch: Tuple[Tuple[str, str], ...] = ()
    matching_pairs: Tuple[Tuple[str, str], ...] = ()


@dataclass(frozen=True)
class ReducedBranch:
    probability: float
    next_state: ReducedState
    immediate_reward: float = 0.0
    observable_reveal: Tuple[Tuple[str, Any], ...] = ()


ReducedOutcome = ReducedBranch


@dataclass
class ReducedModelSpec:
    case_id: str
    description: str
    actors: List[ReducedActor]
    edges: List[ReducedEdge]
    horizon_days: int
    decision_days: List[int]
    ask_budget_per_day: int = 12
    bundle_cost: int = 3
    soft_cost: int = 1
    state_cap: int = 100000
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CaseResult:
    case_id: str
    status: str  # 'verified', 'skipped', 'exceeded_cap', 'counterexample'
    expected_value: Any
    computed_value: Any
    expected_action: Any
    computed_action: Any
    tie_action_set: List[Any] = field(default_factory=list)
    enumerated_states: int = 0
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'case_id': self.case_id,
            'status': self.status,
            'expected_value': self.expected_value,
            'computed_value': self.computed_value,
            'expected_action': self.expected_action,
            'computed_action': self.computed_action,
            'tie_action_set': self.tie_action_set,
            'enumerated_states': self.enumerated_states,
            'details': self.details
        }
