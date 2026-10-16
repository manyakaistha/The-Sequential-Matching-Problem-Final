"""Exact fixture arithmetic only; no planner, simulator, fitting, or hidden inputs."""
from fractions import Fraction as F
from itertools import combinations
import json


def best_matching(edges):
    """Independent exhaustive weighted matching for tiny rational graphs."""
    if not edges:
        return F(0)
    (u, v), weight = edges[0]
    skipped = best_matching(edges[1:])
    rest = [e for e in edges[1:] if not ({u, v} & set(e[0]))]
    return max(skipped, weight + best_matching(rest))


def subsets(items):
    for k in range(len(items) + 1):
        yield from combinations(items, k)


def check():
    results = {}
    fast = F(1, 5) + F(4, 5) * F(4, 5)
    slow = F(1, 5) + F(2, 5) * F(4, 5)
    assert fast == F(21, 25) > F(4, 5) > slow == F(13, 25)
    assert F(1, 2) * F(4, 5) > F(1, 5) > F(1, 10) * F(4, 5)
    results['return_fast_slow_hold'] = [str(fast), str(slow), '4/5']
    assert F(1, 2) + F(1, 2) > F(9, 10)
    reuse = sum(F(9, 10) ** k * F(1, 10) for k in range(3))
    assert reuse == F(271, 1000)
    results['reuse'] = str(reuse)
    edges = [(('A', 'B'), F(9, 10)), (('C', 'D'), F(1, 20)),
             (('A', 'D'), F(13, 20)), (('B', 'C'), F(13, 20))]
    assert best_matching(edges) == F(13, 10)
    results['terminal_matching'] = str(best_matching(edges))
    assert 1 - F(1, 5) ** 2 == F(24, 25) < F(7, 5)
    # Four disjoint pairs; each actor needs cost3 hard verification.
    hard_edges = [(('A', 'B'), F(1)), (('C', 'D'), F(4, 5)),
                  (('E', 'F'), F(3, 5)), (('G', 'H'), F(2, 5))]
    packages = []
    for actors in subsets(tuple('ABCDEFGH')):
        if 3 * len(actors) <= 12:
            selected = set(actors)
            value = sum((q for pair, q in hard_edges if set(pair) <= selected), F(0))
            packages.append((value, ''.join(actors)))
    assert max(packages)[0] == F(9, 5)
    results['hard_package_optimum'] = str(max(packages)[0])
    # Eight actors: triangle ABC, pairs DE/FG, isolated H.
    # 'soft_A' is one public answer; all other actions are constraints bundles.
    actions = ('soft_A', 'D', 'E', 'F', 'G')
    evaluated = []
    for package in subsets(actions):
        p = set(package)
        cost = sum(1 if a == 'soft_A' else 3 for a in p)
        if cost > 12:
            continue
        value = F(1) if 'soft_A' in p else F(1, 2)
        if {'D', 'E'} <= p:
            value += F(4, 5)
        if {'F', 'G'} <= p:
            value += F(2, 5)
        evaluated.append((value, cost, sorted(p)))
    optimum = max(x[0] for x in evaluated)
    all_hard = next(x[0] for x in evaluated if set(x[2]) == set('DEFG'))
    assert optimum == F(9, 5) > all_hard == F(17, 10)
    winners = [p for value, _, p in evaluated if value == optimum]
    assert all({'soft_A', 'D', 'E'} <= set(p) for p in winners)
    results['soft_hard_budget12'] = {'soft_optimum': str(optimum), 'all_hard': str(all_hard)}
    assert F(4, 5) * F(1, 4) == F(1, 5)
    results['future_query_threshold_scaled_budget'] = '1/4'
    return {'status': 'passed', 'scope': 'exact reduced arithmetic only; no production policy tests',
            'results': results}


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
