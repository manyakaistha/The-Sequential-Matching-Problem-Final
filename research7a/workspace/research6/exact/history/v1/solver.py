"""Rational, finite acyclic MDP solver and explicit tiny-matching compiler.

No simulator imports, world generation, seed reads, fitting, or floating point.
The JSON MDP contains every reachable state, legal action and transition.
"""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product


def matchings(edges):
    """All matchings, including wait, by include/exclude edge recursion."""
    edges = tuple(sorted(tuple(e) for e in edges))
    def visit(k, used, chosen):
        if k == len(edges):
            yield chosen
            return
        yield from visit(k + 1, used, chosen)
        edge = edges[k]
        if not used.intersection(edge):
            yield from visit(k + 1, used.union(edge), chosen + (edge,))
    return tuple(visit(0, set(), ()))


def validate(mdp):
    states = mdp['states']
    assert mdp['initial'] in states
    for name, state in states.items():
        for action in state['actions'].values():
            assert action['transitions'], (name, 'empty transitions')
            assert sum((F(t['probability']) for t in action['transitions']), F(0)) == 1
            for t in action['transitions']:
                assert 0 < F(t['probability']) <= 1
                F(t['reward'])
                assert t['next'] in states
                assert states[t['next']]['rank'] > state['rank'], (name, t['next'])


def solve(mdp):
    """Backward Bellman induction; report every reachable action, including ties."""
    validate(mdp)
    values, actions, optimal = {}, {}, {}
    for name, state in sorted(mdp['states'].items(), key=lambda item: -item[1]['rank']):
        av = {a: sum((F(t['probability']) * (F(t['reward']) + values[t['next']])
                       for t in data['transitions']), F(0))
              for a, data in state['actions'].items()}
        values[name] = max(av.values(), default=F(0))
        actions[name] = av
        optimal[name] = sorted(a for a, v in av.items() if v == values[name])
    return {'value': str(values[mdp['initial']]),
            'initial_optimal_actions': optimal[mdp['initial']],
            'states': {s: {'value': str(values[s]), 'optimal_actions': optimal[s],
                           'action_values': {a: str(v) for a, v in actions[s].items()}}
                       for s in sorted(values)}}


def enumerate_policies(mdp, limit=100000):
    """Alternative exhaustive deterministic Markov-policy checker.

    Enumerates ALL policies of the supplied small model and evaluates each by
    recursive path expectation, without calling solve. This is a development
    cross-check, not an implementer-independent review. The critic must supply
    the independent checker required by TEST_SPEC A1.
    """
    validate(mdp)
    names = sorted(s for s, v in mdp['states'].items() if v['actions'])
    choices = [tuple(mdp['states'][s]['actions']) for s in names]
    count = 1
    for c in choices:
        count *= len(c)
    if count > limit:
        raise ValueError(f'{count} policies exceeds checker limit {limit}')
    best = {s: None for s in mdp['states']}
    action_best = {s: {} for s in mdp['states']}
    for selected in product(*choices):
        policy = dict(zip(names, selected))
        @lru_cache(None)
        def value(s):
            if s not in policy:
                return F(0)
            return sum((F(t['probability']) * (F(t['reward']) + value(t['next']))
                        for t in mdp['states'][s]['actions'][policy[s]]['transitions']), F(0))
        for s in mdp['states']:
            v = value(s)
            best[s] = v if best[s] is None else max(best[s], v)
            if s in policy:
                a = policy[s]
                action_best[s][a] = max(action_best[s].get(a, v), v)
    return {'policy_count': count, 'states': {s: {'value': str(best[s]),
            'action_values': {a: str(v) for a, v in action_best[s].items()}}
            for s in sorted(best)}}


def compile_matching(spec):
    """Expand known-calendar matching model to an explicit JSON MDP.

    Expected eventual reward q is booked once at assignment. Joint endpoint
    retirement is Bernoulli(p), observed by next decision day; nonretirement
    releases after d calendar days. Reward can be coupled as a subset of
    retirement because 0<=q<=p. Its conditional distribution is deliberately
    integrated out: additive reward and continuation need only its expectation.
    No hidden unknown parameters remain; all scheduled arrivals are public toy
    inputs. This is not the simulator's observation or delay process.
    """
    n, days = spec['n'], tuple(spec['action_days'])
    assert len(set(days)) == len(days) and tuple(sorted(days)) == days
    edges = {tuple(e['endpoints']): e for e in spec['edges']}
    assert len(edges) == len(spec['edges'])
    for edge, e in edges.items():
        assert len(edge) == 2 and edge[0] < edge[1] < n and edge[0] >= 0
        assert 0 <= F(e['q']) <= F(e['pause']) <= 1
        assert e['duration'] >= 1
    states, ids = {}, {}
    def expand(k, busy, retired, past):
        key = (k, busy, retired, past)
        if key in ids:
            return ids[key]
        name = f's{len(ids)}'
        ids[key] = name
        state = {'rank': k, 'state': {'decision_index': k, 'busy_until': list(busy),
                 'retired': list(retired), 'used_dyads': [list(e) for e in past]}, 'actions': {}}
        states[name] = state
        if k == len(days):
            return name
        day = days[k]
        state['state']['day'] = day
        legal = {edge: e for edge, e in edges.items()
                 if day in e['days'] and edge not in past
                 and not set(edge).intersection(retired)
                 and all(busy[i] <= day and spec['arrival'][i] <= day < spec['exit'][i]
                         for i in edge)}
        for matching in matchings(legal):
            action = ','.join(f'{i}-{j}' for i, j in matching) or 'wait'
            reward = sum((F(legal[e]['q']) for e in matching), F(0))
            transitions = []
            for flags in product((0, 1), repeat=len(matching)):
                prob, new_busy, new_retired = F(1), list(busy), set(retired)
                for edge, pause in zip(matching, flags):
                    e = legal[edge]
                    prob *= F(e['pause']) if pause else 1 - F(e['pause'])
                    if pause:
                        new_retired.update(edge)
                    else:
                        for i in edge:
                            new_busy[i] = day + e['duration']
                if not prob:
                    continue
                target = expand(k + 1, tuple(new_busy), tuple(sorted(new_retired)),
                                tuple(sorted(set(past).union(matching))))
                transitions.append({'probability': str(prob), 'reward': str(reward), 'next': target})
            state['actions'][action] = {'matching': [list(e) for e in matching], 'transitions': transitions}
        return name
    initial = expand(0, (0,) * n, (), ())
    return {'id': spec['id'], 'kind': 'explicit_acyclic_mdp', 'source_specification': spec,
            'initial': initial, 'states': states}


def check_lp_certificate(certificate):
    """Exact certificate for max c*x subject to A*x<=b, x>=0.

    Returns primal/dual objectives; equality certifies optimality. A feasible
    nonnegative dual alone supplies a bound even when primal differs.
    """
    A = [[F(v) for v in row] for row in certificate['A']]
    b, c, x, y = ([F(v) for v in certificate[k]] for k in ('b', 'c', 'primal', 'dual'))
    assert len(A) == len(b) == len(y)
    assert len(c) == len(x) and all(len(row) == len(c) for row in A)
    assert all(v >= 0 for v in x + y)
    assert all(sum(a * v for a, v in zip(row, x)) <= rhs for row, rhs in zip(A, b))
    assert all(sum(A[i][j] * y[i] for i in range(len(A))) >= c[j] for j in range(len(c)))
    primal, dual = sum(a * v for a, v in zip(c, x)), sum(a * v for a, v in zip(b, y))
    assert primal <= dual
    return {'primal': str(primal), 'dual': str(dual), 'exact_optimum': primal == dual}
