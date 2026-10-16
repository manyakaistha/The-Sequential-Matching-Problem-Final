"""Exact nonadaptive query choice in a finite public toy answer model.

Scenario answers are hypotheses, not observed truth. Indistinguishable revealed
answer branches are merged before the matching controller acts. No simulator or
legacy probability assets are imported. This is not a production policy adapter.
"""
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Optional

F = Fraction
Pair = tuple[str, str]
Query = tuple[str, str]


class QueryModelError(ValueError):
    pass


class QueryLimitError(RuntimeError):
    pass


@dataclass(frozen=True)
class AnswerScenario:
    probability: F
    hard: tuple[tuple[str, Optional[bool]], ...]
    soft: tuple[tuple[Query, str], ...]
    rewards: tuple[tuple[Pair, F], ...]


@dataclass(frozen=True)
class QueryModel:
    actors: tuple[str, ...]
    verified: tuple[str, ...]
    scenarios: tuple[AnswerScenario, ...]
    queries: tuple[Query, ...]
    edges: tuple[Pair, ...]
    budget: int = 12
    max_packages: int = 4096
    max_scenarios: int = 64

    def __post_init__(self):
        actors = set(self.actors)
        if (not 1 <= len(actors) <= 8 or len(actors) != len(self.actors)
                or any(type(a) is not str or not a for a in self.actors)):
            raise QueryModelError('Require one to eight distinct actors')
        if not set(self.verified) <= actors or len(set(self.verified)) != len(self.verified):
            raise QueryModelError('Invalid verified actors')
        if type(self.budget) is not int or not 0 <= self.budget <= 12:
            raise QueryModelError('Budget must be an integer in [0,12]')
        if (type(self.max_scenarios) is not int or
                not 0 < len(self.scenarios) <= self.max_scenarios <= 64):
            raise QueryLimitError('Scenario cap exceeded or invalid')
        if type(self.max_packages) is not int or not 1 <= self.max_packages <= 4096:
            raise QueryLimitError('Package cap must be in [1,4096]')
        if len(self.queries) > 12 or len(set(self.queries)) != len(self.queries):
            raise QueryLimitError('Require at most12 distinct query actions')
        for actor, field in self.queries:
            if actor not in actors or not isinstance(field, str) or not field:
                raise QueryModelError('Unknown actor or empty field')
            if field == 'constraints' and actor in self.verified:
                raise QueryModelError('Hard ask on already verified actor')
        if len(set(self.edges)) != len(self.edges):
            raise QueryModelError('Duplicate edges')
        if any(len(pair) != 2 or pair[0] >= pair[1] or not set(pair) <= actors for pair in self.edges):
            raise QueryModelError('Edges must be canonical distinct known actors')
        if sum((s.probability for s in self.scenarios), F(0)) != 1:
            raise QueryModelError('Scenario probabilities must sum to1')
        for s in self.scenarios:
            if not isinstance(s.probability, F) or s.probability <= 0:
                raise QueryModelError('Require positive rational probabilities')
            h, soft, rewards = dict(s.hard), dict(s.soft), dict(s.rewards)
            if len(h) != len(s.hard) or len(soft) != len(s.soft) or len(rewards) != len(s.rewards):
                raise QueryModelError('Duplicate scenario keys')
            if not set(h) <= actors or any(v is not None and type(v) is not bool for v in h.values()):
                raise QueryModelError('Hard answers must be True, False or decline None')
            if any(a in h and h[a] is not True for a in self.verified):
                raise QueryModelError('Modeled hard answer contradicts known verification')
            if any(k[0] not in actors or not isinstance(v, str) for k, v in soft.items()):
                raise QueryModelError('Invalid soft answers')
            if set(rewards) != set(self.edges) or any(not isinstance(q, F) or not 0 <= q <= 1 for q in rewards.values()):
                raise QueryModelError('Every edge needs a rational probability in [0,1]')
            for actor, field in self.queries:
                if field == 'constraints' and actor not in h:
                    raise QueryModelError('Missing modeled hard answer')
                if field != 'constraints' and (actor, field) not in soft:
                    raise QueryModelError('Missing modeled soft answer')


@dataclass(frozen=True)
class PackageDecision:
    package: tuple[Query, ...]
    value: F
    values: tuple[tuple[tuple[Query, ...], F], ...]


def matching_value(edges: tuple[tuple[Pair, F], ...]) -> F:
    """Exhaustive exact terminal controller; zero/negative weights may be omitted."""
    if not edges:
        return F(0)
    (u, v), q = edges[0]
    rest = tuple(e for e in edges[1:] if not ({u, v} & set(e[0])))
    return max(matching_value(edges[1:]), q + matching_value(rest))


def package_cost(package: tuple[Query, ...]) -> int:
    return sum(3 if field == 'constraints' else 1 for _, field in package)


def evaluate_package(model: QueryModel, package: tuple[Query, ...]) -> F:
    if len(set(package)) != len(package) or not set(package) <= set(model.queries):
        raise QueryModelError('Invalid query package')
    if package_cost(package) > model.budget:
        raise QueryModelError('Package exceeds daily nonadaptive budget')
    groups = {}
    for s in model.scenarios:
        hard, soft = dict(s.hard), dict(s.soft)
        disclosed = tuple((query, hard[query[0]] if query[1] == 'constraints' else soft[query])
                          for query in sorted(package))
        groups.setdefault(disclosed, []).append(s)
    expected = F(0)
    for disclosed, branches in groups.items():
        mass = sum((s.probability for s in branches), F(0))
        verified = set(model.verified)
        verified.update(query[0] for query, answer in disclosed
                        if query[1] == 'constraints' and answer is True)
        # A controller sees only disclosed answers. Integrate all still-hidden
        # rewards first; maximizing per scenario would be an oracle.
        weights = tuple((pair, sum((s.probability * dict(s.rewards)[pair] for s in branches), F(0)) / mass)
                        for pair in model.edges if set(pair) <= verified)
        expected += mass * matching_value(weights)
    return expected


def choose_package(model: QueryModel) -> PackageDecision:
    actions = tuple(sorted(model.queries))
    values = []
    for k in range(len(actions) + 1):
        for package in combinations(actions, k):
            if package_cost(package) > model.budget:
                continue
            if len(values) >= model.max_packages:
                raise QueryLimitError('Package cap exceeded; no partial optimum returned')
            values.append((package, evaluate_package(model, package)))
    # Ties prefer less cost, then canonical package; no selection salt search.
    package, value = min(values, key=lambda item: (-item[1], package_cost(item[0]), item[0]))
    return PackageDecision(package, value, tuple(values))
