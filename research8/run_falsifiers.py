"""Record closed development falsifiers; failed fidelity blocks admission."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

from research8.planner import Actor, EdgeLaw, ExactPlanner, Model, ReturnOutcome, ScenarioState


def law(day, pair, q):
    return EdgeLaw(day, pair, q, (ReturnOutcome(q, (None, None), True),
                                ReturnOutcome(1 - q, (None, None), False)))


def run():
    tests = [('future_static_matching', [(0, ('A', 'B'), F(7, 10)),
                                       (1, ('A', 'B'), F(3, 5)),
                                       (1, ('A', 'C'), F(1, 2)),
                                       (1, ('B', 'D'), F(1, 2))], 1),
             ('future_waiting', [(0, ('A', 'B'), F(1, 2)),
                                 (1, ('A', 'C'), F(2, 5)),
                                 (2, ('A', 'D'), F(9, 10))], 2)]
    rows = []
    for name, specs, end in tests:
        model = Model(tuple(Actor(a) for a in 'ABCD'), tuple(law(*s) for s in specs), end_day=end)
        planner = ExactPlanner(model)
        state = ScenarioState(0, tuple('ABCD'))
        oracle = planner.solve(state)
        menu = planner.bounded_action_menu(state)
        row = {'case': name, 'oracle_value': str(oracle.value), 'oracle_action': oracle.action}
        for controller in ('greedy', 'myopic', 'exact'):
            decision = planner.evaluate_actions(state, menu.actions, controller=controller, tie_parent=menu.parent)
            # True initial-action value follows an exact public-history tail:
            true_value = planner.evaluate_actions(state, [decision.action], controller='exact').value
            row[controller] = dict(action=decision.action, estimated_value=str(decision.value),
                                   true_first_action_value=str(true_value), regret=str(oracle.value - true_value))
        rows.append(row)
    assert rows[0]['greedy']['regret'] == '3/10'
    assert rows[0]['myopic']['regret'] == '0'
    assert rows[1]['myopic']['regret'] == '2/5'
    assert all(r['exact']['regret'] == '0' for r in rows)
    base = Path(__file__).parent
    return dict(status='falsifiers_reproduced', production_fidelity_gate='FAIL',
                gate='approximate first-action regret must be <=1/100 on declared fidelity cases',
                disposition='Do not admit greedy or myopic continuation prototype to reward screen',
                exact_belief_core='passes declared cases; not production-admitted',
                official_episodes=0, fits=0,
                source_sha256={p: hashlib.sha256((base / p).read_bytes()).hexdigest()
                               for p in ['planner.py', 'continuation_amendment.json', 'run_falsifiers.py']}, rows=rows)


if __name__ == '__main__':
    result = run()
    with (Path(__file__).parent / 'results' / 'falsifiers.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result, indent=2))
