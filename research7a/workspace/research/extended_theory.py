"""Exact rational toy dynamic programs and clearly labeled simulator calculations.
Not an optimizer of the full simulator; no evaluated policy imports this module.
"""
from dataclasses import dataclass, asdict
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from pathlib import Path
import argparse
import json
import math
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import networkx as nx
import numpy as np

@dataclass(frozen=True)
class Edge:
    u: int
    v: int
    reward: F
    retire: F = F(1)
    busy: int = 1
    start: int = 0
    end: int = 100

@dataclass(frozen=True)
class Instance:
    name: str
    horizon: int
    arrivals: tuple
    exits: tuple
    edges: tuple
    description: str


def matchings(edges):
    """All legal subsets, including wait; exponential by design, tiny instances only."""
    def rec(pos, used, selected):
        if pos == len(edges):
            yield tuple(selected)
            return
        yield from rec(pos + 1, used, selected)
        eid, e = edges[pos]
        if e.u not in used and e.v not in used:
            yield from rec(pos + 1, used | {e.u, e.v}, selected + [eid])
    return tuple(rec(0, set(), []))


class ExactModel:
    """Known toy arrivals, exits, rewards; retirement outcomes observed next day.
    Each assignment yields expected terminal reward q and jointly retires both
    endpoints with probability p>=q. Nonretired endpoints release after d days.
    The reward can be coupled as a subset of retirement (conditional q/p); only
    its expectation enters Bellman bookkeeping. Dyads cannot repeat.
    """
    def __init__(self, instance):
        self.i = instance
        for e in instance.edges:
            assert F(0) <= e.reward <= e.retire <= F(1)
        self.initial = (0, (0,) * len(instance.arrivals), 0, 0)

    def feasible(self, state):
        t, busy, retired, past = state
        return [(j, e) for j, e in enumerate(self.i.edges)
                if not past & (1 << j) and e.start <= t <= e.end
                and all(self.i.arrivals[u] <= t < self.i.exits[u]
                        and busy[u] <= t and not retired & (1 << u)
                        for u in (e.u, e.v))]

    def transitions(self, state, action):
        t, busy, retired, past = state
        for outcomes in product((False, True), repeat=len(action)):
            prob = F(1); newbusy = list(busy); newretired = retired; newpast = past
            for eid, retires in zip(action, outcomes):
                e = self.i.edges[eid]
                prob *= e.retire if retires else 1 - e.retire
                newpast |= 1 << eid
                for u in (e.u, e.v):
                    newbusy[u] = t + e.busy
                    if retires: newretired |= 1 << u
            if prob:
                yield prob, (t + 1, tuple(newbusy), newretired, newpast)

    def immediate(self, action):
        return sum((self.i.edges[e].reward for e in action), F(0))

    @lru_cache(None)
    def optimal(self, state):
        if state[0] >= self.i.horizon: return F(0), ()
        choices = matchings(self.feasible(state))
        scored = [(self.immediate(a) + sum((p * self.optimal(s)[0]
                   for p, s in self.transitions(state, a)), F(0)), a) for a in choices]
        return max(scored, key=lambda x: (x[0], tuple(-j for j in x[1])))

    def static_matching(self, state, weights=None):
        feasible = self.feasible(state)
        weights = weights or {j: e.reward for j, e in feasible}
        g = nx.Graph()
        g.add_weighted_edges_from((e.u, e.v, float(weights[j])) for j, e in feasible if weights.get(j, F(0)) > 0)
        pairs = {tuple(sorted(p)) for p in nx.max_weight_matching(g)}
        action = tuple(j for j, e in feasible if (e.u, e.v) in pairs)
        optimum = max(sum((weights.get(j, F(0)) for j in a), F(0)) for a in matchings(feasible))
        assert abs(float(sum((weights.get(j, F(0)) for j in action), F(0)) - optimum)) < 1e-12
        return action

    def static_value(self, state):
        if state[0] >= self.i.horizon: return F(0)
        return self.immediate(self.static_matching(state))

    def choose(self, state, policy):
        if policy == 'exact_dp': return self.optimal(state)[1]
        if policy == 'batching' and state[0] % 2 == 0: return ()
        if policy in ('blossom', 'batching'): return self.static_matching(state)
        feasible = self.feasible(state)
        if policy == 'greedy':
            used = set(); action = []
            for eid, e in sorted(feasible, key=lambda x: (-x[1].reward, x[0])):
                if not used.intersection((e.u, e.v)):
                    action.append(eid); used.update((e.u, e.v))
            return tuple(action)
        if policy == 'reservation':
            wait = self.static_value(next(self.transitions(state, ()))[1])
            adjusted = {}
            for eid, e in feasible:
                after = sum((p * self.static_value(s) for p, s in self.transitions(state, (eid,))), F(0))
                adjusted[eid] = e.reward - (wait - after)
            return self.static_matching(state, adjusted)
        raise ValueError(policy)

    @lru_cache(None)
    def evaluate(self, state, policy):
        if state[0] >= self.i.horizon: return F(0)
        a = self.choose(state, policy)
        return self.immediate(a) + sum((p * self.evaluate(s, policy)
                   for p, s in self.transitions(state, a)), F(0))

    def run(self):
        before = self.optimal.cache_info().currsize
        optimum = self.optimal(self.initial)[0]
        rows = {}
        for policy in ('exact_dp', 'greedy', 'blossom', 'batching', 'reservation'):
            value = self.evaluate(self.initial, policy)
            rows[policy] = dict(expected_reward=float(value), rational_reward=str(value),
                                regret=float(optimum - value), rational_regret=str(optimum - value),
                                initial_action=list(self.choose(self.initial, policy)))
        return dict(instance=asdict(self.i), policies=rows, dp_states=self.optimal.cache_info().currsize - before)


def instances():
    forever = (100,) * 4
    yield Instance('static_greedy_trap', 1, (0,) * 4, forever,
                   (Edge(0, 1, F(7, 10)), Edge(0, 2, F(3, 5)), Edge(1, 3, F(3, 5))),
                   'A highest-weight edge blocks two edges worth more in total.')
    yield Instance('known_future_arrivals', 2, (0, 0, 1, 1), forever,
                   (Edge(0, 1, F(3, 10)), Edge(0, 2, F(4, 5), start=1), Edge(1, 3, F(4, 5), start=1)),
                   'Immediate blossom consumes endpoints before deterministic high-value arrivals.')
    yield Instance('early_exit', 2, (0,) * 4, (1, 1, 100, 100),
                   (Edge(0, 1, F(4, 5)),), 'Waiting one day loses the only feasible assignment.')
    yield Instance('nonseparable_reservation', 2, (0,) * 4, forever,
                   (Edge(0, 1, F(1, 2), end=0), Edge(2, 3, F(1, 2), end=0), Edge(0, 2, F(9, 10), start=1)),
                   'Each separate endpoint removal destroys the same future edge; summing penalties double-counts its loss.')
    yield Instance('stochastic_repeated_members', 4, (0,) * 4, forever,
                   (Edge(0, 1, F(1, 5), F(2, 5), 1), Edge(0, 2, F(3, 10), F(1, 2), 2),
                    Edge(1, 3, F(3, 10), F(1, 2), 2), Edge(2, 3, F(1, 5), F(2, 5), 1),
                    Edge(0, 3, F(1, 10), F(1, 5), 1)),
                   'Nonretired members return; edge-specific busy times and dyad exhaustion affect continuation.')


def exact_delays():
    rows = {}
    for delayed in (False, True):
        support = list(product(range(1, 8), range(1, 8), range(1, 15), range(5, 13) if delayed else (0,)))
        date_delays = [max(a, b) + c + d for a, b, c, d in support]
        late = F(sum(d > 30 for d in date_delays), len(date_delays))
        rows['delayed' if delayed else 'standard'] = dict(mean_date_delay=str(F(sum(date_delays), len(date_delays))),
               late_date_probability=float(late), late_date_rational=str(late), on_time_feedback_probability=str(F(9, 25)),
               qualification_given_date_and_both_yes=float((1 - late) * F(9, 25)),
               latest_feedback_day_for_assignment_59=59 + max(date_delays) + 5)
    return rows


def sigmoid(x): return 1 / (1 + math.exp(-x))


def logistic_approximation():
    rows = []
    for regime, weights in [('development', (.7, .4, .25, .2)), ('shift', (.25, .8, -.25, .5))]:
        states = []
        for matches in product((False, True), repeat=4):
            mass = math.prod((1 / k if yes else 1 - 1 / k) for k, yes in zip((2, 3, 3, 4), matches))
            fit = sum(w * (1 if yes else -.5) for w, yes in zip(weights, matches))
            states.append((mass, fit))
        mean = sum(p * x for p, x in states)
        variance = sum(p * (x - mean) ** 2 for p, x in states)
        for intercept in (-2, -1, -.25, 0, 1, 2):
            exact = sum(p * sigmoid(intercept + x) for p, x in states)
            plugin = sigmoid(intercept + mean)
            rows.append(dict(regime=regime, intercept=intercept, exact_missing_feature_enumeration=exact,
                             logistic_of_expected_features=plugin, signed_error=plugin - exact,
                             absolute_error=abs(plugin - exact), second_derivative_error_bound=variance/(12*math.sqrt(3))))
    return rows


def shared_effect_audit():
    rows = []
    for nodes in (16, 32, 64):
        xs, ws = np.polynomial.hermite.hermgauss(nodes)
        ss = math.sqrt(2) * .45 * xs; ws = ws / math.sqrt(math.pi)
        a = np.array([sigmoid(-.25 + s) for s in ss]); b = np.array([sigmoid(.55 + s) for s in ss])
        c = np.array([sigmoid(.15 + s) for s in ss]); d = np.array([sigmoid(.65 + s) for s in ss])
        acceptance_joint = float(ws @ (a * b)); independent = float(ws @ a) * float(ws @ b)
        four_joint = float(ws @ (a * b * c * d))
        response_rate = F(153, 200)
        scale = .78 * float(response_rate ** 4)
        rows.append(dict(quadrature_nodes=nodes, acceptance_joint=acceptance_joint,
                         independent_marginal_product=independent, acceptance_dependence_gap=acceptance_joint-independent,
                         retirement_probability=scale*four_joint, qualified_probability_standard=scale*.36*four_joint,
                         four_factor_independence_approximation=scale*.36*float(ws@a)*float(ws@b)*float(ws@c)*float(ws@d)))
    return rows


def production_quadrature_audit():
    """Offline quadrature-only comparison; actor posterior model held fixed."""
    from research.terminal_model import integrated, REGIMES
    import hashlib
    source = Path('research/terminal_model.py').read_bytes()
    rows = []
    tests = [((.5, 1/3, 1/3, .25), (0., .49, 0., .25), (0., .49, 0., .25)),
             ((1., 1., 1., 1.), (-1., .49, .7, .25), (1., .49, -.7, .25)),
             ((0., 0., 0., 0.), (-2., .2, -1., .15), (.5, .6, 1., .3)),
             ((.5, 1/3, 1/3, .25), (-2.5, .49, 2.5, .25), (2.5, .49, -2.5, .25)),
             ((1., 0., 1., 0.), (-2.5, .001, -2.5, .001), (2.5, .001, 2.5, .001))]
    for case, (eq, ua, ub) in enumerate(tests):
        for regime in range(3):
            for day in (0, 40):
                estimates = {}
                for n in (32, 64):
                    xs, ws = np.polynomial.hermite.hermgauss(n)
                    xs = math.sqrt(2) * xs; ws = ws / math.sqrt(math.pi)
                    total = np.zeros(7)
                    uncertain = [j for j, p in enumerate(eq) if 0 < p < 1]
                    for bits in product((0., 1.), repeat=len(uncertain)):
                        truth = list(eq); mass = 1.
                        for j, bit in zip(uncertain, bits):
                            mass *= eq[j] if bit else 1-eq[j]; truth[j] = bit
                        wa = REGIMES[regime]
                        fit = -.25 + sum(w*(1 if yes else -.5) for w, yes in zip(wa[:4], truth)) + (wa[4] if day>=35 else 0)
                        sec = .15 + .4*truth[0]
                        def marginal(z, mean, variance):
                            zz = z + mean + .45*xs[:, None] + math.sqrt(variance)*xs[None, :]
                            return (1/(1+np.exp(-zz))) @ ws
                        pa=marginal(fit,ua[0],ua[1]); pb=marginal(fit,ub[0],ub[1])
                        sa=marginal(sec,ua[2],ua[3]); sb=marginal(sec,ub[2],ub[3])
                        for j, term in enumerate((pa,pb,pa*pb,sa*sb,pa*pb*sa*sb,sa,sb)):
                            total[j] += mass * (ws @ term)
                    estimates[n] = total
                five = np.array(integrated(eq, ua, ub, day, regime, True)[:7])
                ref = estimates[64]
                rows.append(dict(case=case, equal=eq, actor_a=ua, actor_b=ub, regime=regime, day=day,
                                 five_node=five.tolist(), reference_64_node=ref.tolist(),
                                 max_absolute_probability_error=float(np.max(np.abs(five-ref))),
                                 full_four_factor_relative_error=float((five[4]-ref[4])/ref[4]),
                                 reference_32_64_max_difference=float(np.max(np.abs(estimates[32]-ref)))))
    return dict(terminal_model_sha256=hashlib.sha256(source).hexdigest(), cases=rows,
                scope='Numerical quadrature error at fixed assumed actor posterior distributions, not model calibration.')


def controlled_query_benchmark():
    """Artificial observation-only two-node mechanism check, no experiment seeds."""
    import copy
    from extended_policy import decide, hard_distributions, DEFAULT
    from research.terminal_model import predict_funnel
    from kit import eligibility
    fields = dict(age_min=18, age_max=65, who_to_meet=['woman','man','non_binary'],
                  relationship_structure='monogamous', smoking='no', partner_smoking='any',
                  has_children=False, partner_children='any', wants_children='unsure',
                  acceptable_zones=['zone_a'], schedule=None,
                  relationship_goal='long_term',relationship_pace='steady',lifestyle='quiet',conversations='ideas')
    members = [dict(member_id='toy_'+name, pool_id='artificial_query', age=30, gender=gender,
                    zone='zone_a', available=True, arrived_day=0, fields=copy.deepcopy(fields),
                    field_status={k:('not_asked' if v is None else 'observed') for k,v in fields.items()})
               for name,gender in [('u','woman'),('v','man')]]
    state=dict(day=0,ask_budget_remaining=6,members=members,introductions=[],feedback=[],ask_log=[])
    configs=dict(DEFAULT,asks='two_query',query_candidates=2,query_samples=16)
    response=decide(dict(phase='ask',state=state,memory=None),configs)
    before=decide(dict(phase='match',state=state,memory=response['memory']),configs)['pairs']
    def reveal(names, declined=False):
        out=copy.deepcopy(state)
        for m in out['members']:
            if m['member_id'] in names and not (declined and m['member_id']=='toy_v'):
                m['fields']['schedule']=['weekend_day'];m['field_status']['schedule']='observed'
            elif declined and m['member_id']=='toy_v':
                m['field_status']['schedule']='declined'
        return out
    gains={}
    for names in ((),('toy_u',),('toy_v',),('toy_u','toy_v')):
        modified=reveal(names)
        gains[','.join(names) or 'empty']=int(eligibility(*modified['members'])['status']=='feasible')
    after=reveal([a['member_id'] for a in response['asks']])
    after_pairs=decide(dict(phase='match',state=after,memory=response['memory']),configs)['pairs']
    declined=reveal(('toy_u',),True)
    decline_asks=decide(dict(phase='ask',state=declined,memory=None),configs)['asks']
    decline_pairs=decide(dict(phase='match',state=declined,memory=None),configs)['pairs']
    distributions=hard_distributions(members[0])['schedule']
    # Exact rational mass under the same public subset prior, independent endpoints.
    rational=[(a,F(1,3) if len(a)==3 else F(1,9)) for a,_ in distributions]
    exact=sum((p*q for a,p in rational for b,q in rational if set(a)&set(b)),F(0))
    predicted_reward=predict_funnel(*members,state,{},configs)['terminal']
    assert gains=={'empty':0,'toy_u':0,'toy_v':0,'toy_u,toy_v':1}
    assert before==[] and len(after_pairs)==1 and decline_pairs==[] and decline_asks==[]
    return dict(scope='Artificial controlled observation-interface benchmark; not six-family empirical reward evidence.',
                observations=state,config=configs,selected_asks=response['asks'],before_pairs=before,after_pairs=after_pairs,
                deterministic_reveal_matching_values=gains,exact_public_schedule_compatibility_probability=str(exact),
                joint_query_expected_immediate_model_value=float(exact)*predicted_reward,
                singleton_query_expected_immediate_model_value=0.,model_edge_terminal_probability=predicted_reward,
                declined_schedule_asks=decline_asks,declined_schedule_pairs=decline_pairs)


def adaptive_pause_identity_audit():
    """Rational enumeration illustrates tower identity with endogenous assignments.
    Four disjoint endpoints: first pair always pauses. After observing whether its
    deadline mark qualified, introduce the second pair iff the first qualified.
    The second pair also always pauses and has an independent deadline mark.
    This is an artificial reduced model, not a simulator rollout.
    """
    rows = []
    for family, c in [('standard', F(9,25)), ('delayed', F(9,25)*F(671,686))]:
        paths = []
        for first_good in (False, True):
            p1 = c if first_good else 1-c
            if not first_good:
                paths.append((p1, 1, 0))
            else:
                for second_good in (False, True):
                    paths.append((p1*(c if second_good else 1-c), 2, 1+int(second_good)))
        pauses=sum((p*n for p,n,q in paths),F(0));qualified=sum((p*q for p,n,q in paths),F(0))
        realized_ratio_mean=sum((p*F(q,n) for p,n,q in paths),F(0))
        assert qualified == c*pauses
        assert realized_ratio_mean != c
        rows.append(dict(family=family,qualification_factor=str(c),expected_pauses=str(pauses),
                         expected_qualified=str(qualified),expected_paused_members=str(2*pauses),
                         identity_residual=str(qualified-c*pauses),expected_realized_qualified_per_pause=str(realized_ratio_mean),
                         expected_ratio_equals_factor=False,
                         paths=[dict(probability=str(p),pauses=n,qualified=q) for p,n,q in paths]))
    return dict(scope='Exact rational artificial reduced model: feedback-dependent assignment count. Not simulator outcomes.',cases=rows)


def counterexamples():
    return dict(query_complementarity={'F_empty':0,'F_u':0,'F_v':0,'F_uv':1,'marginal_v_empty':0,'marginal_v_given_u':1},
                general_graph_odd_set={'triangle_integer':1,'triangle_node_only_fractional':1.5,'missing_constraint':'x01+x02+x12<=1'},
                nonseparable_dynamic_loss={'future_edge_AC':.9,'loss_remove_AB':.9,'loss_remove_CD':.9,'loss_remove_both':.9},
                nonmonotone_reservation={'horizon':4,'current_edge_AB':.1,'future_edge_AC_day3':1,
                  'AC_arrival_probability_independent':.5,'cost_assign_AB_day0_busy2_no_retirement':0,
                  'cost_assign_AB_day1_busy2_no_retirement':0,
                  'cost_assign_AB_day2_busy2_no_retirement':.5,
                  'cost_assign_AB_day3_busy2_no_retirement':0,
                  'assumptions':'Constant busy duration two; no retirement, reward paid immediately, future AC available only day3. This counterexample refutes unrestricted monotonicity, not the stationary offer theorem.'},
                entropy_not_value={'unrelated_fair_coin_entropy_bits':1,'matching_value_change':0},
                disconnected_connectivity={'before_edges':[[0,1]],'after_edges':[[0,1],[2,3]],'vertices':[0,1,2,3,4],
                                           'lambda2_before':0,'lambda2_after':0,'maximum_matching_before':1,'maximum_matching_after':2})


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', default='results/extended/theory.json'); args = parser.parse_args()
    output = dict(scope='Exact rational finite toy MDPs; numerical quadrature is labeled separately. Not full-simulator optimality.',
                  exact_dynamic_benchmarks=[ExactModel(i).run() for i in instances()],
                  exact_simulator_delays=exact_delays(), missing_feature_approximation=logistic_approximation(),
                  numerical_shared_effect_audit=shared_effect_audit(), production_quadrature_audit=production_quadrature_audit(),
                  counterexamples=counterexamples(), controlled_query_benchmark=controlled_query_benchmark(),
                  adaptive_pause_identity_audit=adaptive_pause_identity_audit())
    target = Path(args.output); target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(output, indent=2, default=lambda x: str(x) if isinstance(x, F) else x, allow_nan=False) + '\n')
    for row in output['exact_dynamic_benchmarks']:
        print(row['instance']['name'], {p: r['rational_reward'] for p, r in row['policies'].items()})

if __name__ == '__main__': main()
