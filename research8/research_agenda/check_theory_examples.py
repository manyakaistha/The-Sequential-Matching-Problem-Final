"""Independent rational arithmetic for declared examples; not simulator evidence.

All future opportunity laws below are specified toy assumptions, not observed
future calendars. No simulator, model assets, seeds or external packages used.
"""
from fractions import Fraction as F
from functools import lru_cache
import json
import math


def stopping_value(opportunities):
    """One reusable-until-accepted actor, absorbing assignment, disposable partners.

    Each day's (probability, reward) opportunity is observed before match/hold.
    Days are independent; all probabilities and rewards are declared public.
    """
    v = F(0)
    for day in reversed(opportunities):
        assert sum(p for p, _ in day) == 1
        v = sum(p * max(q, v) for p, q in day)
    return v


def run():
    rows = []
    # Four actors: AB=.6, AC=BD=.4, no other edges, final action day.
    assert F(2, 5) + F(2, 5) > F(3, 5)
    rows.append(dict(case='static_exchange', greedy='3/5', maximum_weight='4/5',
                     assumptions='true q; final day; distinct feasible edges; no continuation'))
    # AB today, AC tomorrow, AD day2; all assignments absorb endpoints.
    schedule = [((F(1), q),) for q in (F(1, 2), F(2, 5), F(9, 10))]
    oracle = stopping_value(schedule)
    one_step_g = max(F(1, 2), F(2, 5))
    hold_two_then_g = F(9, 10)
    assert oracle == hold_two_then_g == F(9, 10) and one_step_g == F(1, 2)
    rows.append(dict(case='coordinated_wait', exact=str(oracle),
                     full_horizon_one_step_g=str(one_step_g),
                     library_with_two_day_hold=str(hold_two_then_g)))
    # Existing day13 horizon falsifier, independently reconstructed.
    schedule = [((F(1), F(1, 2)),)] + [((F(1), F(0)),)] * 12 + [((F(1), F(9, 10)),)]
    assert stopping_value(schedule) == F(9, 10)
    assert stopping_value(schedule[:13]) == F(1, 2)
    rows.append(dict(case='day13', horizon12='1/2', full_horizon='9/10'))
    # Wait value = survival * chance of usable arrival * offered reward.
    for p, expected in [(F(1, 2), 'match'), (F(9, 10), 'wait')]:
        wait = F(4, 5) * p * F(9, 10)
        action = 'wait' if wait > F(1, 2) else 'match'
        assert action == expected
        rows.append(dict(case='arrival_risk', arrival_probability=str(p),
                         survival='4/5', wait_value=str(wait), today='1/2', action=action))
    # Two missing hard bundles cost6; individually no feasible edge, jointly q=.8.
    values = {(): F(0), ('A',): F(0), ('B',): F(0), ('A', 'B'): F(4, 5)}
    assert values[('A', 'B')] - values[('A',)] > values[('B',)] - values[()]
    rows.append(dict(case='hard_query_complementarity', individual_gain='0', joint_gain='4/5', cost=6))
    # Two held actors cannot both consume the same future partner C.
    solo = F(4, 5)
    joint = F(4, 5)
    assert solo + solo > joint
    rows.append(dict(case='shared_future_partner', sum_independent_values='8/5', joint_value='4/5'))
    # A fixed 8-policy menu, 64 iid trajectories, conditional paired range[-50,50].
    radius = 100 * math.sqrt(math.log(2 * 8 / .01) / (2 * 64))
    assert radius > 20
    return dict(status='constructed_checks_passed', official_episodes=0, fits=0,
                rows=rows, illustration_hoeffding_radius_msmi_per100=radius,
                warning='Toy arithmetic validates examples only; no learned-model or simulator superiority.')


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
