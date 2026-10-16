"""Constructed temporal matching model, independent of production simulator.

Queries are nonadaptive batches; answers refresh before matching. Full eventual
reward is booked at assignment. Outcome branches determine future occupancy.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F
from itertools import combinations, product
from research7.exact_independent.solver import vertex_recursive_enumeration, rational


@dataclass(frozen=True)
class Actor:
    name: str
    arrival: int = 0
    departure: int = 1000
    known: bool = True


@dataclass(frozen=True)
class Outcome:
    probability: F
    reward: F
    pause: bool = False
    delay_a: int = 8
    delay_b: int = 8
    label: str = 'return'


@dataclass(frozen=True)
class Edge:
    a: str
    b: str
    days: tuple
    outcomes: tuple


@dataclass(frozen=True)
class State:
    epoch: int = 0
    phase: str = 'ask'
    verified: frozenset = frozenset()
    failed: frozenset = frozenset()
    used: frozenset = frozenset()
    busy: tuple = ()
    paused: frozenset = frozenset()
    latent: tuple = ()
    events: tuple = ()
    pending: tuple = ()  # Already booked (identity, expectation); never added by transitions.


class TemporalModel:
    def __init__(self, days, actors, edges, budgets=0, initial=None):
        self.days, self.actors, self.edges = tuple(days), tuple(actors), tuple(edges)
        self.budgets = (budgets,) * len(days) if isinstance(budgets, int) else tuple(budgets)
        if len(self.budgets) != len(days):
            raise ValueError('budget/day mismatch')
        self.initial = initial or [(F(1), State(verified=frozenset(a.name for a in actors if a.known)))]

    def terminal(self, s):
        return s.epoch == len(self.days)

    def day(self, s):
        return self.days[s.epoch] if not self.terminal(s) else self.days[-1] + 1

    def available(self, s):
        day, busy, hidden = self.day(s), dict(s.busy), dict(s.latent)
        return frozenset(a.name for a in self.actors if a.arrival <= day < a.departure
                         and hidden.get('present:' + a.name, True)
                         and a.name not in s.paused and busy.get(a.name, -1) <= day)

    def observe(self, s):
        # Arrival is public when reached, never before. Latent answer types absent.
        arrived = frozenset(a.name for a in self.actors if a.arrival <= self.day(s)
                            and dict(s.latent).get('present:' + a.name, True))
        return (s.epoch, s.phase, self.available(s), s.verified & arrived, s.failed & arrived,
                s.used, s.events, tuple(identity for identity, _ in s.pending))

    def actions(self, s):
        if self.terminal(s):
            return ()
        available = self.available(s)
        if s.phase == 'ask':
            candidates = sorted(available - s.verified - s.failed)
            return [('ask', batch) for r in range(min(len(candidates), self.budgets[s.epoch] // 3) + 1)
                    for batch in combinations(candidates, r)]
        eligible = []
        for edge in self.edges:
            pair = tuple(sorted((edge.a, edge.b)))
            if self.day(s) in edge.days and pair not in s.used and set(pair) <= available & s.verified:
                eligible.append((*pair, F(0)))
        return [('match', m) for m, _ in vertex_recursive_enumeration(available, eligible)]

    def transition(self, s, action):
        if action not in self.actions(s):
            raise ValueError('illegal query/matching action')
        if action[0] == 'ask':
            hidden = dict(s.latent)
            yes = frozenset(a for a in action[1] if hidden.get('answer:' + a, True))
            no = frozenset(action[1]) - yes
            yield F(1), replace(s, phase='match', verified=s.verified | yes, failed=s.failed | no), F(0)
            return
        edge_map = {tuple(sorted((e.a, e.b))): e for e in self.edges if self.day(s) in e.days}
        laws = [edge_map[p].outcomes for p in action[1]]
        for outcomes in product(*laws):
            probability, reward = F(1), F(0)
            busy, paused, events = dict(s.busy), set(s.paused), []
            for pair, outcome in zip(action[1], outcomes):
                probability *= rational(outcome.probability)
                reward += rational(outcome.reward)
                if outcome.pause:
                    paused.update(pair)
                else:
                    edge = edge_map[pair]
                    busy[edge.a] = self.day(s) + outcome.delay_a
                    busy[edge.b] = self.day(s) + outcome.delay_b
                # This reduced model releases outcomes by the next epoch. The
                # pending-feedback case is separate and does not use this law.
                events.append((pair, outcome.label))
            child = replace(s, epoch=s.epoch + 1, phase='ask', used=s.used | frozenset(action[1]),
                            busy=tuple(sorted(busy.items())), paused=frozenset(paused), events=tuple(events))
            yield probability, child, reward


def law(q, p=None, delay=8):
    q, p = rational(q), rational(q if p is None else p)
    if not 0 <= q <= p <= 1:
        raise ValueError('require 0 <= qualified <= pause <= 1')
    return tuple(o for o in (Outcome(q, F(1), True, label='qualified_pause'),
                            Outcome(p-q, F(0), True, label='late_unqualified_pause'),
                            Outcome(1-p, F(0), False, delay, delay, 'nonpause_return')) if o.probability)
