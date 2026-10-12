"""Constructed rational examples fixed before any solution evaluation."""
from fractions import Fraction as F
from itertools import combinations, product
from .solver import compile_matching, matchings


def edge(i, j, q, days, pause=None, duration=8):
    return {'endpoints': [i, j], 'q': str(F(q)), 'pause': str(F(q if pause is None else pause)),
            'duration': duration, 'days': list(days)}


def market(name, n, days, edges, expected, first=None, arrival=None, exit=None):
    return {'id': name, 'n': n, 'action_days': list(days), 'edges': edges,
            'arrival': arrival or [0] * n, 'exit': exit or [100] * n,
            'expected': str(F(expected)), 'expected_first_action': first,
            'information': 'All edge probabilities, action days and arrival/exit schedules are known toy inputs.',
            'reward_bookkeeping': 'Expected eventual reward booked once at assignment; full follow-up assumed.'}


def matching_specs():
    path = [edge(0, 1, '1/10', [0]), edge(1, 2, '11/100', [0]), edge(2, 3, '1/10', [0])]
    specs = [market('local_cardinality_repair', 4, [0], path, '1/5', '0-1,2-3'),
             market('cardinality_reward_reversal', 4, [0], [edge(0,1,'9/10',[0]),
                    edge(0,2,'1/10',[0]),edge(1,3,'1/10',[0])], '9/10', '0-1'),
             market('odd_triangle', 3, [0], [edge(i,j,1,[0]) for i,j in combinations(range(3),2)], 1),
             market('known_return_reservation', 4, [0,1], [edge(0,1,'11/100',[0]),
                    edge(1,3,'1/10',[0]),edge(0,2,'1/10',[1])], '1/5', '1-3', arrival=[0,0,1,0]),
             market('known_return_removed', 4, [0,1], [edge(0,1,'11/100',[0]),
                    edge(1,3,'1/10',[0])], '11/100', '0-1'),
             market('repeat_opportunities', 3, [0,8,16],
                    [edge(i,j,'1/10',[0,8,16]) for i,j in combinations(range(3),2)], '271/1000'),
             market('repeat_short_horizon', 3, [0],
                    [edge(i,j,'1/10',[0]) for i,j in combinations(range(3),2)], '1/10'),
             market('nonseparable_alternatives', 4, [0,1], [edge(0,1,'1/2',[0],1),
                    edge(2,3,'1/2',[0],1),edge(0,2,'9/10',[1],1)], 1, '0-1,2-3'),
             market('last_action_day', 4, [59], [edge(0,1,'1/5',[59]),edge(2,3,'1/10',[59])],
                    '3/10', '0-1,2-3'),
             market('single_introduction_no_learning', 2, [0,1], [edge(0,1,'1/2',[0],1)], '1/2', '0-1'),
             market('inherited_throughput_last_day', 3, [59], [edge(0,1,'1/5',[59],duration=8),
                    edge(0,2,'3/10',[59],duration=20)], '3/10', '0-2'),
             market('inherited_waiting_future_arrival', 3, [0,1], [edge(0,1,'1/10',[0]),
                    edge(0,2,'9/10',[1])], '9/10', 'wait', arrival=[0,0,1]),
             market('inherited_retry_option', 3, [0,1], [edge(0,1,'1/5',[0],duration=1),
                    edge(0,2,'4/5',[1],duration=1)], '21/25', '0-1'),
             market('inherited_static_greedy_trap', 4, [0], [edge(0,1,'7/10',[0],1),
                    edge(0,2,'3/5',[0],1),edge(1,3,'3/5',[0],1)], '6/5', '0-2,1-3'),
             market('inherited_known_future_arrivals', 4, [0,1], [edge(0,1,'3/10',[0,1],1),
                    edge(0,2,'4/5',[1],1),edge(1,3,'4/5',[1],1)], '8/5', 'wait', arrival=[0,0,1,1]),
             market('inherited_early_exit', 4, [0,1], [edge(0,1,'4/5',[0,1],1)], '4/5', '0-1', exit=[1,1,100,100]),
             market('inherited_stochastic_returning', 4, [0,1,2,3], [
                    edge(0,1,'1/5',range(4),'2/5',1),edge(0,2,'3/10',range(4),'1/2',2),
                    edge(1,3,'3/10',range(4),'1/2',2),edge(2,3,'1/5',range(4),'2/5',1),
                    edge(0,3,'1/10',range(4),'1/5',1)], '709/1000'),
             market('pause_not_qualified_penalty', 4, [0,1], [edge(0,1,'1/10',[0],1,1),
                    edge(0,2,'1/10',[0],'1/10',1),edge(0,3,1,[1],1,1)], 1),
             market('renewal_certificate_toy', 3, [0,1], [edge(0,1,'1/2',[0],duration=1),
                    edge(0,2,'1/2',[1],duration=1)], '3/4', '0-1')]
    return specs


def transition(probability, reward=0, target='terminal'):
    return {'probability': str(F(probability)), 'reward': str(F(reward)), 'next': target}


def simple(name, actions, extra=None, expected=None, information='Fully specified constructed information experiment.'):
    states = {'initial': {'rank': 0, 'actions': {a: {'transitions': t} for a,t in actions.items()}},
              'terminal': {'rank': 10, 'actions': {}}}
    states.update(extra or {})
    return {'id': name, 'kind':'explicit_acyclic_mdp', 'information': information,
            'expected': str(F(expected)) if expected is not None else None,
            'initial':'initial', 'states':states}


def information_specs():
    complement = simple('complementary_verification', {a:[transition(1,reward)] for a,reward in
                         [('empty',0),('bundle_A',0),('bundle_B',0),('bundle_A_and_B',1)]}, expected=1,
                         information='Only AB feasible; neither endpoint verified; each bundle deterministically verifies its endpoint. Values are immediate maximum matching counts, with no query cost subtraction.')
    collision_actions = {}
    for name, q, pairs in [('shared',F(4,5),[(0,2),(1,2)]), ('distinct',F(7,10),[(0,2),(1,3)])]:
        transitions = []
        for flags in product((0,1), repeat=2):
            present = [e for e,flag in zip(pairs, flags) if flag]
            probability = q**sum(flags)*(1-q)**(2-sum(flags))
            transitions.append(transition(probability, max(map(len, matchings(present)))))
        collision_actions[name] = transitions
    collision = simple('collision_distinct_partners', collision_actions, expected='7/5',
                       information='Two independent Bernoulli candidate-partner edges revealed by each batch; matching chosen after reveal. Shared batch p=4/5, distinct p=7/10.')
    soft = simple('soft_value_hard_cost', {
            'no_information':[transition(1,'1/2')],
            'reveal_free':[transition('1/2',target='high'),transition('1/2',target='low')],
            'reveal_displaces_hard':[transition('1/2','-1/4','high'),transition('1/2','-1/4','low')]},
            extra={s:{'rank':1,'actions':{'AB':{'transitions':[transition(1,q)]},
                                         'AC':{'transitions':[transition(1,'1/2')]}}}
                   for s,q in [('high','9/10'),('low','1/10')]}, expected='7/10',
            information='AB state is high/low equiprobably; reveal exposes state before choosing AB/AC. Forgone disjoint hard opportunity is represented by additive cost 1/4.')
    no_return = simple('no_return_can_still_have_learning', {
            'skip_experiment':[transition(1,target='unknown')],
            'introduce_informative_disjoint_pair':[transition('1/2',target='type_0'),transition('1/2',target='type_1')]},
            extra={s:{'rank':1,'actions':{a:{'transitions':[transition(1,q)]} for a,q in choices}}
                   for s,choices in [('unknown',[('choice_B','1/2'),('choice_C','1/2')]),
                                     ('type_0',[('choice_B',1),('choice_C',0)]),
                                     ('type_1',[('choice_B',0),('choice_C',1)])]}, expected=1,
            information='One fair shared regime controls later alternatives B/C. An earlier disjoint pair retires without reward but publicly reveals regime; its endpoints never return. Other endpoints remain. No-return alone does not imply zero learning value.')
    return [complement, collision, soft, no_return]


def sweep_specs():
    """Deterministic constructed hold-out grid; not simulator seeds or fitted cases."""
    specs = []
    # All 64 labelled simple graphs on four vertices, including empty components.
    possible = list(combinations(range(4),2))
    for mask in range(64):
        selected = [e for i,e in enumerate(possible) if mask & (1 << i)]
        specs.append(market(f'graph4_{mask:02d}',4,[0],[edge(i,j,'1/3',[0]) for i,j in selected],0))
        specs[-1].pop('expected')
    for length in (3,5,7):
        pairs = [(i,i+1) for i in range(length-1)]+[(0,length-1)]
        specs.append(market(f'odd_cycle_{length}',length,[0],[edge(i,j,1,[0]) for i,j in pairs],length//2))
    # Changed horizons with zero, certain and intermediate success; no-repeat.
    for horizon in (0,1,2,3):
        for q in ('0','1/3','1'):
            specs.append(market(f'horizon_{horizon}_q_{q.replace("/","_")}',3,list(range(horizon)),
                [edge(0,1,q,range(horizon),duration=1),edge(0,2,q,range(horizon),duration=1)],0))
            specs[-1].pop('expected')
    return specs


def lp_certificates():
    return {
        'triangle_degree_relaxation': {'A':[[1,1,0],[1,0,1],[0,1,1]],'b':[1,1,1],
            'c':[1,1,1],'primal':['1/2']*3,'dual':['1/2']*3},
        'triangle_odd_set': {'A':[[1,1,0],[1,0,1],[0,1,1],[1,1,1]],'b':[1,1,1,1],
            'c':[1,1,1],'primal':[1,0,0],'dual':[0,0,0,1]},
        'two_day_renewal': {'A':[[1,0],['1/2',1]],'b':[1,1],
            'c':['1/2','1/2'],'primal':[1,'1/2'],'dual':['1/4','1/2']}}


def build_specifications():
    return {'schema_version':1, 'scope':'Constructed exact reduced models only; no simulator worlds, seeds or empirical policy claims.',
            'matching':matching_specs(), 'information':information_specs(),
            'held_out_constructed_sweep':sweep_specs(), 'lp_certificates':lp_certificates(),
            'inherited_nonmonotone_occupancy':{'action_days':[0,1,2,3], 'duration':2,
                 'future_partner_day':3,'future_reward':'1','arrival_probability':'1/2',
                 'expected_costs':['0','0','1/2','0'],
                 'scope':'Isolated current AB introduction, no retirement; independent future AC opportunity only on day 3. Reward not required to be a subset of retirement.'}}
