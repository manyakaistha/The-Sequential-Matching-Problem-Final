"""Independent rational matching and finite public-history belief enumeration.

No simulator/policy imports. A node is a posterior over *all* hidden states
consistent with the complete action/observation history, never its first member.
"""
from collections import defaultdict
from fractions import Fraction as F
from itertools import combinations
from time import process_time


def rational(x):
    if isinstance(x, float):
        raise TypeError('Exact model inputs must be integers or Fractions, not floats')
    return F(x)


def vertex_recursive_enumeration(available_vertices, feasible_edges):
    edges = {}
    for u, v, w in feasible_edges:
        if u == v:
            raise ValueError('self edge')
        if u in available_vertices and v in available_vertices:
            pair = tuple(sorted((u, v)))
            if pair in edges:
                raise ValueError('duplicate edge')
            edges[pair] = rational(w)

    def walk(vertices):
        if not vertices:
            return [((), F(0))]
        u = min(vertices)
        rest = vertices - {u}
        out = walk(rest)
        for v in sorted(rest):
            pair = tuple(sorted((u, v)))
            if pair in edges:
                out += [(tuple(sorted((pair,) + m)), edges[pair] + value)
                        for m, value in walk(rest - {v})]
        return out
    return sorted(walk(frozenset(available_vertices)), key=lambda x: (-x[1], x[0]))


def greedy_matching(vertices, edges):
    used, pairs, total = set(), [], F(0)
    for u, v, w in sorted(edges, key=lambda x: (-rational(x[2]), tuple(sorted(x[:2])))):
        if u in vertices and v in vertices and u not in used and v not in used:
            pairs.append(tuple(sorted((u, v))))
            used.update((u, v))
            total += rational(w)
    return tuple(sorted(pairs)), total


def enumerate_labelled_4vertex_graphs():
    vertices = frozenset('ABCD')
    pairs = list(combinations(sorted(vertices), 2))
    out = []
    for mask in range(64):
        edges = [(*e, F(1)) for i, e in enumerate(pairs) if mask & (1 << i)]
        enumerated = vertex_recursive_enumeration(vertices, edges)
        # Separate subset reference, with equality of *all* legal action sets.
        reference = set()
        for r in range(len(edges) + 1):
            for subset in combinations(edges, r):
                flat = [u for e in subset for u in e[:2]]
                if len(flat) == len(set(flat)):
                    reference.add(tuple(sorted(e[:2] for e in subset)))
        actual = {m for m, _ in enumerated}
        assert actual == reference
        out.append(dict(mask=mask, edges=[e[:2] for e in edges],
                        matchings=enumerated, max_cardinality=len(enumerated[0][0]),
                        valid=actual == reference))
    return out


def verify_matching_legality(cycle_lengths=(3, 5, 7)):
    out = {}
    for k in cycle_lengths:
        vs = frozenset('V' + str(i) for i in range(k))
        edges = [('V' + str(i), 'V' + str((i + 1) % k), F(1)) for i in range(k)]
        maximum = max(len(m) for m, _ in vertex_recursive_enumeration(vs, edges))
        out[k] = dict(max_matching_cardinality=maximum, expected_integer_cardinality=k // 2,
                      is_exact=maximum == k // 2, is_fractional=False)
    return out


class BeliefSolver:
    """Finite acyclic model protocol: initial, observe, terminal, actions, transition.

    transition(state, action) returns (probability, next_state, booked_reward).
    Hidden support action menus must be identical; intersection would conceal a
    hidden-dependent legality bug. Reward is NOT automatically observed. State
    observations must explicitly include released feedback/availability.
    """
    def __init__(self, model, state_cap=100000, cpu_seconds=300):
        if not 0 < state_cap <= 100000 or not 0 < cpu_seconds <= 300:
            raise ValueError('hard enumeration allowance exceeded')
        self.model, self.cap, self.cpu_cap = model, state_cap, cpu_seconds
        self.nodes = []
        self.transitions = 0
        self.support_states = 0
        self.started = process_time()

    def check_cap(self):
        if len(self.nodes) + self.support_states > self.cap:
            raise OverflowError('enumerated belief plus support state cap exceeded')
        if process_time() - self.started > self.cpu_cap:
            raise TimeoutError('constructed solver CPU cap exceeded')

    def solve(self):
        initial = [(rational(p), s) for p, s in self.model.initial if p]
        if sum(p for p, _ in initial) != 1 or any(p < 0 for p, _ in initial):
            raise ValueError('initial probability must sum to one')
        observations = {self.model.observe(s) for _, s in initial}
        if len(observations) != 1:
            raise ValueError('initial public observation must be fixed')
        value, root = self._node(initial, (('initial', next(iter(observations))),))
        return dict(value=value, root=root, nodes=self.nodes, enumerated_states=len(self.nodes),
                    support_states=self.support_states, enumerated_transitions=self.transitions,
                    cpu_seconds=process_time() - self.started, state_cap=self.cap)

    def _node(self, belief, history):
        combined = defaultdict(F)
        for p, state in belief:
            combined[state] += p
        belief = sorted(((p, s) for s, p in combined.items() if p), key=lambda x: repr(x[1]))
        assert sum(p for p, _ in belief) == 1
        terminal = {self.model.terminal(s) for _, s in belief}
        if len(terminal) != 1:
            raise ValueError('hidden-dependent horizon')
        node_id = len(self.nodes)
        self.support_states += len(belief)
        row = dict(id=node_id, history=history, belief=belief, actions=[], ties=[], value=F(0))
        self.nodes.append(row)
        self.check_cap()
        if next(iter(terminal)):
            return F(0), node_id
        menus = [tuple(sorted(set(self.model.actions(s)), key=repr)) for _, s in belief]
        if any(menu != menus[0] for menu in menus):
            raise ValueError('action menu depends on hidden state within one public history')
        if not menus[0]:
            raise ValueError('nonterminal node must provide at least wait')
        best = None
        for action in menus[0]:
            grouped = defaultdict(list)
            immediate = F(0)
            branches_ledger = []
            for prior, state in belief:
                branches = list(self.model.transition(state, action))
                if sum(rational(b[0]) for b in branches) != 1:
                    raise ValueError('transition probabilities must sum to one')
                for probability, child, reward in branches:
                    probability, reward = rational(probability), rational(reward)
                    if probability < 0:
                        raise ValueError('negative branch probability')
                    if not probability:
                        continue
                    mass = prior * probability
                    observed = self.model.observe(child)
                    grouped[observed].append((mass, child))
                    immediate += mass * reward
                    branches_ledger.append(dict(mass=mass, reward=reward, observation=observed,
                                                next_state=child))
                    self.transitions += 1
            value, outcomes = immediate, []
            for observed, weighted in sorted(grouped.items(), key=lambda x: repr(x[0])):
                mass = sum(p for p, _ in weighted)
                child_value, child_id = self._node([(p / mass, s) for p, s in weighted],
                                                   history + ((action, observed),))
                value += mass * child_value
                outcomes.append(dict(probability=mass, child=child_id))
            row['actions'].append(dict(action=action, value=value, immediate=immediate,
                                       outcomes=outcomes, branches=branches_ledger))
            if best is None or value > best:
                best, row['ties'] = value, [action]
            elif value == best:
                row['ties'].append(action)
            self.check_cap()
        row['value'] = best
        return best, node_id


def rational_history_tree_dp(spec, transition_fn=None, action_generator=None):
    """New API accepts an explicit belief model; unsafe callback API is rejected."""
    if transition_fn is not None or action_generator is not None:
        raise TypeError('legacy single-state callbacks cannot certify public beliefs; use BeliefSolver model')
    return BeliefSolver(spec).solve()
