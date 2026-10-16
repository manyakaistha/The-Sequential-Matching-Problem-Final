"""Exact tiny planning in a declared finite public Markov matching model.

This is a count-reward research oracle, not a simulator policy. Arrivals are
observed at the start of each day. Joint occupancy clocks remain hidden; only
current availability is observed. Belief branches with the same public history
share one continuation decision. No unrevealed outcome is passed to a controller. Qualified
reward is booked as q once, including on the final action day. Permanent pause
may occur without qualified reward, but qualified reward requires both pauses.
Arrival events on different days and joint outcomes of vertex-disjoint edges
are independent by declaration. Arbitrary correlated hidden arrival scenarios,
response releases, and the simulator's complete observation law are not modeled.
Declared exit days and future edge laws are toy-model assumptions, never an
adapter for private simulator calendars. Asymmetric None/day outcomes describe
a general reduced resource law, not source-exact pair-pause behavior.
"""

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Optional

Pair = tuple[str, str]
Action = tuple[Pair, ...]


def _rational(value, name):
    if type(value) is int:
        return Fraction(value)
    if isinstance(value, Fraction):
        return value
    raise ValueError(f"{name} must be an integer or Fraction, not float")


def _day(value, name):
    if type(value) is not int or not 0 <= value <= 10000:
        raise ValueError(f"{name} must be an absolute nonnegative calendar day <=10000")


def canonical_pair(pair):
    if len(pair) != 2 or any(type(x) is not str or not x for x in pair):
        raise ValueError("a pair needs two nonempty opaque actor names")
    if pair[0] == pair[1]:
        raise ValueError("self-pair")
    return tuple(sorted(pair))


@dataclass(frozen=True)
class Actor:
    name: str
    exit_day: int = 60  # exclusive; declared public on arrival


@dataclass(frozen=True)
class ReturnOutcome:
    probability: Fraction
    returns: tuple[Optional[int], Optional[int]]
    qualified: bool


@dataclass(frozen=True)
class EdgeLaw:
    day: int
    endpoints: Pair
    q: Fraction
    outcomes: tuple[ReturnOutcome, ...]


@dataclass(frozen=True)
class ArrivalOutcome:
    probability: Fraction
    actors: tuple[str, ...] = ()


@dataclass(frozen=True)
class ArrivalEvent:
    day: int
    outcomes: tuple[ArrivalOutcome, ...]


@dataclass(frozen=True)
class Model:
    """Declared public toy law with hidden occupancy outcomes, not perfect information.

    Probabilities, exclusive exit days and day-indexed edge laws are assumptions
    known to the planner. Future arrival realizations and occupancy clocks are
    not observed until the reduced public availability history distinguishes
    them. This declaration contains no population fit or simulator state.
    """
    actors: tuple[Actor, ...]
    edges: tuple[EdgeLaw, ...]
    arrival_events: tuple[ArrivalEvent, ...] = ()
    end_day: int = 59


@dataclass(frozen=True)
class ScenarioState:
    """INTERNAL model state AFTER this day's arrival event.

    Missing ready entries mean ready now. None means hidden permanent pause.
    Exhausted pairs cannot be introduced again. Arrived actors remain recorded
    after departure. No previously booked reward is included in this state.
    An initial prior is supplied conditional on its observed arrival history;
    full reachability from every earlier calendar event is not reconstructed.
    """
    day: int
    arrived: tuple[str, ...]
    ready: tuple[tuple[str, Optional[int]], ...] = ()
    exhausted: tuple[Pair, ...] = ()


# Compatibility name for a deterministic initial prior; never a controller view.
PublicState = ScenarioState


@dataclass(frozen=True)
class PublicView:
    day: int
    arrived: tuple[str, ...]
    available: tuple[str, ...]
    exhausted: tuple[Pair, ...]


@dataclass(frozen=True)
class Belief:
    """Finite rational posterior over internal clocks, sharing one public view."""
    particles: tuple[tuple[Fraction, ScenarioState], ...]


@dataclass(frozen=True)
class Caps:
    max_states: int = 100000
    max_transitions: int = 1000000
    max_joint_branches: int = 4096
    max_edge_outcomes: int = 16
    max_arrival_outcomes: int = 32
    max_support_entries: int = 200000


class LimitExceeded(RuntimeError):
    """The requested calculation exceeded its declared work allowance."""


@dataclass(frozen=True)
class Decision:
    value: Fraction
    action: Action
    action_values: tuple[tuple[Action, Fraction], ...]
    states: int
    transitions: int
    support_entries: int


@dataclass(frozen=True)
class Menu:
    actions: tuple[Action, ...]
    parent: Action
    reason: str


class ExactPlanner:
    def __init__(self, model: Model, caps: Caps = Caps()):
        self.model, self.caps = model, caps
        hard_limits = vars(Caps())
        for name, value in vars(caps).items():
            if type(value) is not int or not 0 < value <= hard_limits[name]:
                raise ValueError(f"{name} must be positive integer <={hard_limits[name]}")
        _day(model.end_day, "end_day")
        if model.end_day > 59:
            raise ValueError("action horizon must end no later than day59")
        if not 4 <= len(model.actors) <= 8:
            raise ValueError("exact core requires 4 through 8 declared actors")
        self.actors = {}
        for actor in model.actors:
            if type(actor.name) is not str or not actor.name or actor.name in self.actors:
                raise ValueError("actor names must be unique nonempty opaque strings")
            _day(actor.exit_day, "exit_day")
            self.actors[actor.name] = actor
        self.edges = {}
        for edge in model.edges:
            _day(edge.day, "edge day")
            pair = canonical_pair(edge.endpoints)
            if pair != edge.endpoints or not set(pair) <= self.actors.keys():
                raise ValueError("edge endpoints must be canonical declared actor names")
            if edge.day > model.end_day or (edge.day, pair) in self.edges:
                raise ValueError("duplicate or out-of-horizon edge law")
            q = _rational(edge.q, "q")
            if not 0 <= q <= 1:
                raise ValueError("q outside [0,1]")
            self._probabilities(edge.outcomes, caps.max_edge_outcomes)
            qualified = Fraction(0)
            for outcome in edge.outcomes:
                if type(outcome.qualified) is not bool or len(outcome.returns) != 2:
                    raise ValueError("joint outcome requires boolean qualification and two returns")
                for day in outcome.returns:
                    if day is not None:
                        _day(day, "return day")
                        if day <= edge.day:
                            raise ValueError("returns must be after assignment day")
                if outcome.qualified:
                    if outcome.returns != (None, None):
                        raise ValueError("qualified reward requires permanent pause for both endpoints")
                    qualified += _rational(outcome.probability, "probability")
            if q != qualified:
                raise ValueError("q inconsistent with joint qualified/pause law")
            self.edges[edge.day, pair] = edge
        self.arrivals = {}
        actor_event_days = {}
        for event in model.arrival_events:
            _day(event.day, "arrival day")
            if event.day > model.end_day or event.day in self.arrivals:
                raise ValueError("duplicate or out-of-horizon arrival event")
            self._probabilities(event.outcomes, caps.max_arrival_outcomes)
            for outcome in event.outcomes:
                if len(set(outcome.actors)) != len(outcome.actors):
                    raise ValueError("duplicate arrival within outcome")
                for name in outcome.actors:
                    if name not in self.actors or self.actors[name].exit_day <= event.day:
                        raise ValueError("arrival requires declared actor alive on arrival day")
                    if name in actor_event_days and actor_event_days[name] != event.day:
                        raise ValueError("each actor may have one uncertain arrival day only")
                    actor_event_days[name] = event.day
            self.arrivals[event.day] = event
        self._reset()

    @staticmethod
    def _probabilities(outcomes, cap):
        if not outcomes or len(outcomes) > cap:
            raise ValueError("empty or oversized outcome support")
        probabilities = [_rational(o.probability, "probability") for o in outcomes]
        if any(p <= 0 for p in probabilities) or sum(probabilities) != 1:
            raise ValueError("outcome probabilities must be positive and sum exactly to one")

    def _reset(self):
        self._cache = {}
        self._states = self._transitions = 0
        self._support_entries = 0

    def _state(self, state):
        _day(state.day, "state day")
        if state.day > self.model.end_day:
            raise ValueError("decision state is after the action horizon")
        arrived = tuple(sorted(state.arrived))
        if len(set(arrived)) != len(arrived) or not set(arrived) <= self.actors.keys():
            raise ValueError("arrived names must be unique declared actors")
        ready = dict(state.ready)
        if len(ready) != len(state.ready) or not set(ready) <= set(arrived):
            raise ValueError("ready entries must be unique arrived actors")
        for day in ready.values():
            if day is not None:
                _day(day, "ready day")
        exhausted = tuple(sorted(canonical_pair(p) for p in state.exhausted))
        if len(set(exhausted)) != len(exhausted) or any(not set(p) <= set(arrived) for p in exhausted):
            raise ValueError("exhausted pairs must be unique arrived dyads")
        # Past ready clocks are interchangeable; normalization improves caching.
        ready = tuple(sorted((a, d) for a, d in ready.items() if d is None or d > state.day))
        for event in self.model.arrival_events:
            if event.day > state.day and any(set(o.actors) & set(arrived) for o in event.outcomes):
                raise ValueError("already arrived actor appears in a future arrival event")
        return PublicState(state.day, arrived, ready, exhausted)

    def available(self, state):
        if isinstance(state, PublicView):
            return self.public_view(state).available
        if isinstance(state, Belief):
            return self.public_view(state).available
        state = self._state(state)
        ready = dict(state.ready)
        return tuple(a for a in state.arrived if self.actors[a].exit_day > state.day
                     and ready.get(a, state.day) is not None
                     and ready.get(a, state.day) <= state.day)

    def public_view(self, state):
        if isinstance(state, PublicView):
            if len(set(state.available)) != len(state.available) or not set(state.available) <= set(state.arrived):
                raise ValueError("public available actors must be unique arrived actors")
            unavailable = set(state.arrived) - set(state.available)
            normalized = self._state(ScenarioState(state.day, state.arrived,
                                                   tuple((a, None) for a in unavailable), state.exhausted))
            if any(self.actors[a].exit_day <= state.day for a in state.available):
                raise ValueError("public available actor has already exited")
            return PublicView(normalized.day, normalized.arrived, tuple(sorted(state.available)), normalized.exhausted)
        if isinstance(state, Belief):
            state = self._belief(state).particles[0][1]
        else:
            state = self._state(state)
        return PublicView(state.day, state.arrived, self.available(state), state.exhausted)

    def _belief(self, belief):
        if isinstance(belief, ScenarioState):
            belief = Belief(((Fraction(1), belief),))
        if not isinstance(belief, Belief) or not belief.particles:
            raise ValueError("a nonempty declared finite belief is required")
        if len(belief.particles) > self.caps.max_joint_branches:
            raise LimitExceeded("belief support cap exceeded")
        merged, view = {}, None
        for probability, state in belief.particles:
            probability = _rational(probability, "belief probability")
            if probability <= 0:
                raise ValueError("belief probabilities must be positive")
            state = self._state(state)
            observed = self.public_view(state)
            if view is not None and observed != view:
                raise ValueError("belief particles must share the same current public observation")
            view = observed
            merged[state] = merged.get(state, Fraction(0)) + probability
        if sum(merged.values()) != 1:
            raise ValueError("belief probabilities must sum exactly to one")
        return Belief(tuple((p, s) for s, p in sorted(merged.items(), key=lambda item: repr(item[0]))))

    def legal_actions(self, state):
        """All whole vertex-disjoint actions, including empty (764 on K8)."""
        state = self.public_view(state)
        available = self.available(state)
        exhausted = set(state.exhausted)
        def visit(remaining):
            if not remaining:
                yield ()
                return
            first, tail = remaining[0], remaining[1:]
            yield from visit(tail)
            for index, other in enumerate(tail):
                pair = (first, other)
                if pair in exhausted or (state.day, pair) not in self.edges:
                    continue
                for rest in visit(tail[:index] + tail[index + 1:]):
                    yield tuple(sorted((pair,) + rest))
        return tuple(sorted(visit(available)))

    def score_greedy(self, state):
        state = self.public_view(state)
        available, exhausted = set(self.available(state)), set(state.exhausted)
        menu = [e for (day, pair), e in self.edges.items() if day == state.day
                and set(pair) <= available and pair not in exhausted and e.q > 0]
        used, chosen = set(), []
        for edge in sorted(menu, key=lambda e: (-e.q, e.endpoints)):
            if not set(edge.endpoints) & used:
                chosen.append(edge.endpoints)
                used.update(edge.endpoints)
        return tuple(sorted(chosen))

    def _tick(self):
        self._transitions += 1
        if self._transitions > self.caps.max_transitions:
            raise LimitExceeded("transition cap exceeded")

    def _next_states(self, state, action):
        laws = [self.edges[state.day, pair] for pair in action]
        event = self.arrivals.get(state.day + 1)
        arrivals = event.outcomes if event else (ArrivalOutcome(Fraction(1)),)
        count = len(arrivals)
        for law in laws:
            count *= len(law.outcomes)
        if count > self.caps.max_joint_branches:
            raise LimitExceeded("joint branch cap exceeded")
        for outcomes in product(*(law.outcomes for law in laws)):
            ready, probability = dict(state.ready), Fraction(1)
            for pair, outcome in zip(action, outcomes):
                probability *= outcome.probability
                ready.update(zip(pair, outcome.returns))
            for arrival in arrivals:
                self._tick()
                new = PublicState(state.day + 1, tuple(sorted(state.arrived + arrival.actors)),
                                  tuple(sorted(ready.items())), tuple(sorted(state.exhausted + action)))
                yield probability * arrival.probability, self._state(new)

    def _q_value(self, belief, action, stop, controller):
        day = belief.particles[0][1].day
        reward = sum((self.edges[day, pair].q for pair in action), Fraction(0))
        if day >= stop:
            return reward
        # Partition before choosing a continuation: never maximize each latent
        # outcome separately. Bayes normalization carries hidden-clock beliefs.
        groups = {}
        for prior_probability, state in belief.particles:
            for probability, new in self._next_states(state, action):
                view = self.public_view(new)
                group = groups.setdefault(view, {})
                group[new] = group.get(new, Fraction(0)) + prior_probability * probability
        continuation = Fraction(0)
        for group in groups.values():
            mass = sum(group.values())
            posterior = self._belief(Belief(tuple((p / mass, s) for s, p in group.items())))
            continuation += mass * self._value(posterior, stop, controller)
        return reward + continuation

    def _value(self, belief, stop, controller):
        key = (belief, stop, controller)
        if key in self._cache:
            return self._cache[key]
        self._states += 1
        if self._states > self.caps.max_states:
            raise LimitExceeded("state cap exceeded")
        self._support_entries += len(belief.particles)
        if self._support_entries > self.caps.max_support_entries:
            raise LimitExceeded("cumulative belief support cap exceeded")
        if controller == "exact":
            value = max(self._q_value(belief, action, stop, controller) for action in self.legal_actions(belief))
        else:
            value = self._q_value(belief, self.score_greedy(self.public_view(belief)), stop, controller)
        self._cache[key] = value
        return value

    def solve(self, state):
        """Optimal expected introduction count under the declared public model."""
        return self.evaluate_actions(state, self.legal_actions(state), controller="exact")

    def bounded_action_menu(self, state, *, parent="max_reward"):
        return bounded_action_menu(self, state, parent=parent)

    def evaluate_actions(self, state, actions, *, future_steps=None, controller="greedy", tie_parent=None):
        """Fixed-first-action comparison, followed by one common public controller.

        future_steps counts FUTURE decision epochs; zero retains today's full q.
        Every branch retains all actors, occupancy and consumed dyads. This is
        exact enumeration under a bounded model, not sampled simulator evidence.
        tie_parent preserves the explicitly supplied control on exact ties;
        it must be legal and included in actions. Default ties prefer greedy.
        """
        state = self._belief(state)
        day = state.particles[0][1].day
        if controller not in ("exact", "greedy"):
            raise ValueError("controller must be exact or greedy")
        if future_steps is None:
            stop = self.model.end_day
        elif type(future_steps) is not int or future_steps < 0 or future_steps > 59:
            raise ValueError("future_steps must be an integer in [0,59]")
        else:
            stop = min(self.model.end_day, day + future_steps)
        legal, unique = set(self.legal_actions(state)), []
        for action in actions:
            canonical = tuple(sorted(canonical_pair(pair) for pair in action))
            if canonical not in legal:
                raise ValueError("first action is not a legal whole matching")
            if canonical not in unique:
                unique.append(canonical)
        if not unique:
            raise ValueError("first-action menu is empty")
        if tie_parent is None:
            parent = self.score_greedy(state)
        else:
            parent = tuple(sorted(canonical_pair(pair) for pair in tie_parent))
            if parent not in legal or parent not in unique:
                raise ValueError("tie_parent must be legal and included in the first-action menu")
        self._reset()
        self._states = 1
        self._support_entries = len(state.particles)
        if self._support_entries > self.caps.max_support_entries:
            raise LimitExceeded("cumulative belief support cap exceeded")
        values = tuple((action, self._q_value(state, action, stop, controller)) for action in unique)
        best = max(value for _, value in values)
        tied = [action for action, value in values if value == best]
        chosen = parent if parent in tied else min(tied)
        return Decision(best, chosen, values, self._states, self._transitions, self._support_entries)


def bounded_action_menu(planner, state, *, parent="max_reward"):
    """At most twelve complete actions on a closed current-graph region.

    This reduced menu inspects only presently available legal edges. It has no
    unresolved-hard, latent future, or pending-return boundary representation;
    it is not the full proposed D1 production menu. Region/boundary overflow
    returns the parent alone rather than clipping a graph. Outside parent pairs
    remain fixed. Each changed endpoint, including a broken partner, counts
    toward the six-actor cap. Immediate reward ranks the bounded candidates;
    no claim of exhaustive dynamic search follows from this menu.
    """
    view = planner.public_view(state)
    legal = planner.legal_actions(view)
    greedy = planner.score_greedy(view)
    def reward(action):
        return sum((planner.edges[view.day, pair].q for pair in action), Fraction(0))
    if parent == "greedy":
        baseline = greedy
    elif parent == "max_reward":
        best = max(map(reward, legal))
        tied = tuple(action for action in legal if reward(action) == best)
        baseline = greedy if greedy in tied else min(tied)
    elif isinstance(parent, (tuple, list)):
        baseline = tuple(sorted(canonical_pair(pair) for pair in parent))
        if baseline not in legal:
            raise ValueError("explicit menu parent must be a legal whole matching")
    else:
        raise ValueError("parent must be max_reward, greedy, or an explicit legal action")
    if not baseline:
        return Menu((baseline,), baseline, "empty_parent")
    neighbors = {a: set() for a in view.available}
    for (day, pair) in planner.edges:
        if day == view.day and pair not in view.exhausted and set(pair) <= set(view.available):
            a, b = pair
            neighbors[a].add(b)
            neighbors[b].add(a)
    if len(view.available) <= 6:
        region, boundary = set(view.available), set()
    else:
        # Seed the parent edge with the most alternative legal neighbors.
        seed = min(baseline, key=lambda pair: (
            -len((neighbors[pair[0]] | neighbors[pair[1]]) - set(pair)), pair))
        seeded = set(seed)
        remaining = [pair for pair in baseline if pair != seed]
        for _ in range(2):
            adjacent = [pair for pair in remaining if any(
                neighbors[a] & seeded for a in pair)]
            if not adjacent:
                break
            pair = min(adjacent, key=lambda candidate: (-reward((candidate,)), candidate))
            seeded.update(pair)
            remaining.remove(pair)
        region = set(seeded)
        frontier = list(seeded)
        while frontier:
            actor = frontier.pop()
            for neighbor in neighbors[actor] - region:
                region.add(neighbor)
                frontier.append(neighbor)
        boundary = region - seeded
    if len(region) > 6:
        return Menu((baseline,), baseline, "region_overflow")
    if len(boundary) > 6:
        return Menu((baseline,), baseline, "boundary_overflow")
    # Full incident closure ensures no baseline edge straddles the boundary.
    outside = tuple(pair for pair in baseline if not set(pair) & region)
    if any(bool(set(pair) & region) and not set(pair) <= region for pair in baseline):
        return Menu((baseline,), baseline, "open_parent_boundary")
    baseline_set = set(baseline)
    def fits(action):
        if tuple(pair for pair in action if not set(pair) & region) != outside:
            return False
        if any(set(pair) & region and not set(pair) <= region for pair in action):
            return False
        changed = set().union(*(set(pair) for pair in set(action) ^ baseline_set))
        return len(changed) <= 6
    fitting = tuple(action for action in legal if fits(action))
    actions = [baseline]
    def add(action):
        if action not in actions and len(actions) < 12:
            actions.append(action)
    if greedy in fitting:
        add(greedy)
    exchanges = [action for action in fitting if set(action) - baseline_set]
    exchanges.sort(key=lambda action: (-reward(action), len(set(action) ^ baseline_set), action))
    for action in exchanges[:4]:
        add(action)
    deletions = [action for action in fitting if action != baseline and set(action) <= baseline_set]
    deletions.sort(key=lambda action: (len(baseline_set - set(action)), -reward(action), action))
    for action in deletions[:4]:
        add(action)
    add(outside)  # Empty local replacement preserves every outside parent pair.
    if len(actions) < 12:
        for action in exchanges[4:]:
            if action not in actions:
                add(action)
                break
    return Menu(tuple(actions), baseline, "ok")
