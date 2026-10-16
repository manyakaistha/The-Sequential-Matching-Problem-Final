"""Execute the preregistered 144-case reduced development grid, never simulator worlds."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from time import perf_counter, process_time
import hashlib
import json

from research8.planner import (Actor, ArrivalEvent, ArrivalOutcome, EdgeLaw,
                              ExactPlanner, Model, ReturnOutcome, ScenarioState)


def edge(day, pair, q, return_day, absorbing=False):
    outcomes = [ReturnOutcome(q, (None, None), True)]
    if q < 1:
        outcomes.append(ReturnOutcome(1 - q, (None, None) if absorbing else (return_day,) * 2, False))
    return EdgeLaw(day, pair, q, tuple(outcomes))


def run():
    regpath = Path(__file__).with_name('registration.json')
    registration = json.loads(regpath.read_text())
    recipe = registration['reduced_grid']
    rows = []
    for today, future, arrival, mode in product(recipe['today_q'], recipe['future_q'],
                                               recipe['arrival_probability'], recipe['return_modes']):
        q, r, p = map(F, (today, future, arrival))
        outcomes = []
        if p:
            outcomes.append(ArrivalOutcome(p, ('C',)))
        if p < 1:
            outcomes.append(ArrivalOutcome(1 - p))
        model = Model(tuple(Actor(a, 9 if a == 'C' else 60) for a in 'ABCD'),
                      (edge(0, ('A', 'B'), q, 8 if mode == 'fast8' else 9,
                            absorbing=mode == 'absorbing'), edge(8, ('A', 'C'), r, 16)),
                      (ArrivalEvent(8, tuple(outcomes)),), end_day=8)
        planner = ExactPlanner(model)
        state = ScenarioState(0, ('A', 'B', 'D'))
        wall, cpu = perf_counter(), process_time()
        exact = planner.solve(state)
        elapsed, used_cpu = perf_counter() - wall, process_time() - cpu
        greedy = planner.evaluate_actions(state, [planner.score_greedy(state)])
        menu = planner.bounded_action_menu(state)
        rollout = planner.evaluate_actions(state, menu.actions, future_steps=12, tie_parent=menu.parent)
        zero = planner.evaluate_actions(state, menu.actions, future_steps=0, tie_parent=menu.parent)
        # Evaluate selected actions under full continuation; don't compare a
        # truncated value estimate directly to full-horizon expected reward.
        zero_full = planner.evaluate_actions(state, [zero.action])
        greedy_formula = q + ((1 - q) * p * r if mode == 'fast8' else 0)
        expected_optimum = max(greedy_formula, p * r)
        assert greedy.value == greedy_formula
        assert exact.value == expected_optimum
        assert rollout.value == exact.value
        assert exact.value >= greedy.value
        rows.append(dict(today_q=today, future_q=future, arrival_probability=arrival, mode=mode,
                         exact=str(exact.value), greedy=str(greedy.value), menu_rollout=str(rollout.value),
                         zero_horizon_full_value=str(zero_full.value),
                         greedy_regret=str(exact.value - greedy.value),
                         menu_regret=str(exact.value - rollout.value),
                         zero_horizon_regret=str(exact.value - zero_full.value),
                         held=not rollout.action, menu_actions=len(menu.actions),
                         states=exact.states, support_entries=exact.support_entries,
                         transitions=exact.transitions, elapsed_seconds=elapsed, cpu_seconds=used_cpu))
    assert len(rows) == recipe['cases'] == 144
    summary = dict(cases=len(rows), holds=sum(r['held'] for r in rows),
                   strict_model_improvements=sum(F(r['greedy_regret']) > 0 for r in rows),
                   mean_model_gain=str(sum((F(r['greedy_regret']) for r in rows), F(0)) / len(rows)),
                   max_menu_regret=str(max(F(r['menu_regret']) for r in rows)),
                   max_zero_horizon_regret=str(max(F(r['zero_horizon_regret']) for r in rows)),
                   max_states=max(r['states'] for r in rows),
                   max_support_entries=max(r['support_entries'] for r in rows),
                   max_transitions=max(r['transitions'] for r in rows),
                   max_toy_solve_seconds=max(r['elapsed_seconds'] for r in rows),
                   total_toy_solve_cpu_seconds=sum(r['cpu_seconds'] for r in rows))
    sources = {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
               for name in ('planner.py', 'query_packages.py', 'registration.json', 'run_reduced_grid.py')}
    return dict(status='passed', scope='declared reduced-model development grid only',
                source_sha256=sources, registration_sha256=hashlib.sha256(regpath.read_bytes()).hexdigest(),
                official_simulator_episodes=0, fits=0,
                limitations=['two sparse opportunities in four declared actors',
                             'exact declared probabilities and public toy exits, not learned beliefs',
                             'current-graph-only menu; pending/unresolved boundary not production-ready',
                             'toy solve timing is not200member invocation timing',
                             'no empirical MSMI/p100 superiority established'], summary=summary, rows=rows)


if __name__ == '__main__':
    result = run()
    target = Path(__file__).with_name('results') / 'reduced_grid.json'
    # Never overwrite a closed run; new code/config needs a new output identity.
    with target.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result['summary'], indent=2))
