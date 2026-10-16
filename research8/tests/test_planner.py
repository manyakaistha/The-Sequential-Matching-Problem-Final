import unittest
from fractions import Fraction as F
from itertools import combinations

from research8.planner import (Actor, ArrivalEvent, ArrivalOutcome, Belief, Caps, EdgeLaw,
                              ExactPlanner, LimitExceeded, Model, ReturnOutcome, ScenarioState)


def law(day, pair, q, *, pause=None, return_day=None):
    p = q if pause is None else pause
    outcomes = []
    if q:
        outcomes.append(ReturnOutcome(q, (None, None), True))
    if p > q:
        outcomes.append(ReturnOutcome(p - q, (None, None), False))
    if p < 1:
        outcomes.append(ReturnOutcome(1 - p, (return_day or day + 8,) * 2, False))
    return EdgeLaw(day, pair, q, tuple(outcomes))


def actors(names='ABCD', **exits):
    return tuple(Actor(a, exits.get(a, 60)) for a in names)


class PlannerTests(unittest.TestCase):
    def test_return_law_reverses_hold(self):
        results = []
        for fast in [True, False]:
            outcomes = [ReturnOutcome(F(1, 5), (None, None), True),
                        ReturnOutcome(F(2, 5), (8, 8), False),
                        ReturnOutcome(F(2, 5), (8 if fast else 9,) * 2, False)]
            model = Model(actors(C=9), (EdgeLaw(0, ('A', 'B'), F(1, 5), tuple(outcomes)),
                                       law(8, ('A', 'C'), F(4, 5))),
                          (ArrivalEvent(8, (ArrivalOutcome(F(1), ('C',)),)),), end_day=8)
            planner = ExactPlanner(model)
            initial = ScenarioState(0, ('A', 'B', 'D'))
            decision = planner.solve(initial)
            self.assertEqual(dict(decision.action_values)[(('A', 'B'),)], F(21 if fast else 13, 25))
            self.assertEqual(dict(decision.action_values)[()], F(4, 5))
            self.assertEqual(decision.action, (('A', 'B'),) if fast else ())
            rollout = planner.evaluate_actions(initial, [(), (('A', 'B'),)], controller='greedy')
            self.assertEqual(rollout.value, decision.value)
            self.assertEqual(rollout.action, decision.action)
            results.append(decision.value)
        self.assertEqual(results, [F(21, 25), F(4, 5)])

    def test_future_arrival_is_not_known_before_action(self):
        for probability in [F(1, 2), F(1, 10)]:
            model = Model(actors(), (law(0, ('A', 'B'), F(1, 5), pause=F(1)),
                                     law(1, ('A', 'C'), F(4, 5))),
                          (ArrivalEvent(1, (ArrivalOutcome(probability, ('C',)),
                                             ArrivalOutcome(1 - probability))),), end_day=1)
            decision = ExactPlanner(model).solve(ScenarioState(0, ('A', 'B', 'D')))
            self.assertEqual(decision.value, max(F(1, 5), probability * F(4, 5)))
            self.assertEqual(decision.action, () if probability == F(1, 2) else (('A', 'B'),))

    def test_hidden_return_clock_oracle_trap(self):
        model = Model(actors(), (law(1, ('A', 'B'), F(3, 5), pause=F(1)),
                                 law(2, ('A', 'C'), F(1))), end_day=2)
        first = ScenarioState(1, tuple('ABCD'), (('C', 2),))
        second = ScenarioState(1, tuple('ABCD'), (('C', 3),))
        planner = ExactPlanner(model)
        self.assertEqual(planner.public_view(first), planner.public_view(second))
        # Whole belief max is .6. Averaging per-hidden-state maxima yields .8.
        belief = Belief(((F(1, 2), first), (F(1, 2), second)))
        decision = planner.solve(belief)
        self.assertEqual(decision.value, F(3, 5))
        self.assertEqual(decision.action, (('A', 'B'),))
        self.assertEqual(dict(decision.action_values)[()], F(1, 2))
        reverse = planner.solve(Belief(tuple(reversed(belief.particles))))
        self.assertEqual((decision.value, decision.action), (reverse.value, reverse.action))
        oracle = (planner.solve(first).value + planner.solve(second).value) / 2
        self.assertEqual(oracle, F(4, 5))

    def test_joint_shared_future_not_double_counted(self):
        model = Model(actors(), (law(0, ('A', 'B'), F(1, 2), pause=F(1)),
                                 law(0, ('C', 'D'), F(1, 2), pause=F(1)),
                                 law(1, ('A', 'C'), F(9, 10))), end_day=1)
        d = ExactPlanner(model).solve(ScenarioState(0, tuple('ABCD')))
        self.assertEqual(d.value, F(1))
        self.assertEqual(d.action, (('A', 'B'), ('C', 'D')))
        self.assertEqual(dict(d.action_values)[()], F(9, 10))

    def test_reuse_and_exhaustion(self):
        edges = tuple(law(day, pair, F(1, 10), return_day=day + 8)
                      for day in (0, 8, 16) for pair in combinations('ABC', 2))
        state = ScenarioState(0, tuple('ABCD'))
        d = ExactPlanner(Model(actors(), edges, end_day=16)).solve(state)
        self.assertEqual(d.value, F(271, 1000))
        ab = tuple(e for e in edges if e.endpoints == ('A', 'B'))
        self.assertEqual(ExactPlanner(Model(actors(), ab, end_day=16)).solve(state).value, F(1, 10))
        exhausted = ScenarioState(8, tuple('ABCD'), exhausted=(('A', 'B'),))
        self.assertNotIn((('A', 'B'),), ExactPlanner(Model(actors(), edges, end_day=16)).legal_actions(exhausted))

    def test_final_day_full_reward_static_and_greedy_trap(self):
        specs = [(('A', 'B'), F(9, 10)), (('C', 'D'), F(1, 20)),
                 (('A', 'D'), F(13, 20)), (('B', 'C'), F(13, 20))]
        planner = ExactPlanner(Model(actors(), tuple(law(59, pair, q) for pair, q in specs)))
        state = ScenarioState(59, tuple('ABCD'))
        decision = planner.solve(state)
        self.assertEqual(decision.value, F(13, 10))
        self.assertEqual(decision.action, (('A', 'D'), ('B', 'C')))
        greedy = planner.score_greedy(state)
        self.assertEqual(dict(decision.action_values)[greedy], F(19, 20))
        for future_steps in [0, 12, 59]:
            self.assertEqual(planner.evaluate_actions(state, planner.legal_actions(state),
                             future_steps=future_steps).value, F(13, 10))

    def test_all_sixty_four_graphs_match_independent_edge_subsets(self):
        pairs = tuple(combinations('ABCD', 2))
        for mask in range(64):
            present = tuple(p for i, p in enumerate(pairs) if mask & (1 << i))
            planner = ExactPlanner(Model(actors(), tuple(law(0, pair, F(1)) for pair in present), end_day=0))
            actual = set(planner.legal_actions(ScenarioState(0, tuple('ABCD'))))
            expected = set()
            for k in range(len(present) + 1):
                for subset in combinations(present, k):
                    flat = [a for pair in subset for a in pair]
                    if len(flat) == len(set(flat)):
                        expected.add(tuple(sorted(subset)))
            self.assertEqual(actual, expected)
        full = ExactPlanner(Model(actors('ABCDEFGH'), tuple(law(0, pair, F(1))
                                  for pair in combinations('ABCDEFGH', 2)), end_day=0))
        self.assertEqual(len(full.legal_actions(ScenarioState(0, tuple('ABCDEFGH')))), 764)

    def test_bounded_menu_legal_and_keeps_parent(self):
        names = 'ABCDEF'
        model = Model(actors(names), tuple(law(0, pair, F(1, 2))
                      for pair in combinations(names, 2)), end_day=0)
        planner = ExactPlanner(model)
        state = ScenarioState(0, tuple(names))
        menu = planner.bounded_action_menu(state)
        self.assertEqual(menu.reason, 'ok')
        self.assertLessEqual(len(menu.actions), 12)
        self.assertEqual(menu.actions[0], menu.parent)
        self.assertIn((), menu.actions)
        preserved = planner.evaluate_actions(state, menu.actions, tie_parent=menu.parent)
        self.assertEqual(preserved.action, menu.parent)
        self.assertTrue(set(menu.actions) <= set(planner.legal_actions(state)))

    def test_exact_dynamic_tie_retains_distinct_static_parent(self):
        model = Model(actors(), (law(0, ('A', 'B'), F(7, 10), pause=F(1)),
                                 law(0, ('A', 'C'), F(1, 2), pause=F(1)),
                                 law(0, ('B', 'D'), F(1, 2), pause=F(1)),
                                 law(1, ('C', 'D'), F(3, 10))), end_day=1)
        planner = ExactPlanner(model)
        state = ScenarioState(0, tuple('ABCD'))
        menu = planner.bounded_action_menu(state)
        self.assertEqual(menu.parent, (('A', 'C'), ('B', 'D')))
        self.assertNotEqual(menu.parent, planner.score_greedy(state))
        d = planner.evaluate_actions(state, menu.actions, tie_parent=menu.parent)
        self.assertEqual(d.value, F(1))
        self.assertEqual(d.action, menu.parent)

    def test_menu_overflow_fails_closed_and_outside_pairs_fixed(self):
        names = 'ABCDEFGH'
        dense = ExactPlanner(Model(actors(names), tuple(law(0, pair, F(1, 2))
                       for pair in combinations(names, 2)), end_day=0))
        state = ScenarioState(0, tuple(names))
        menu = dense.bounded_action_menu(state)
        self.assertEqual(menu.reason, 'region_overflow')
        self.assertEqual(menu.actions, (menu.parent,))
        specs = [(pair, F(1, 2)) for pair in combinations('ABCD', 2)]
        specs += [(('E', 'F'), F(1, 3)), (('G', 'H'), F(1, 3))]
        sparse = ExactPlanner(Model(actors(names), tuple(law(0, pair, q) for pair, q in specs), end_day=0))
        menu = sparse.bounded_action_menu(state)
        self.assertEqual(menu.reason, 'ok')
        for action in menu.actions:
            self.assertIn(('E', 'F'), action)
            self.assertIn(('G', 'H'), action)
            changed = {a for pair in set(action) ^ set(menu.parent) for a in pair}
            self.assertLessEqual(len(changed), 6)

    def test_greedy_tail_falsifier_and_static_myopic_repair(self):
        model = Model(actors(), (law(0, ('A', 'B'), F(7, 10), pause=F(1)),
                                 law(1, ('A', 'B'), F(3, 5), pause=F(1)),
                                 law(1, ('A', 'C'), F(1, 2), pause=F(1)),
                                 law(1, ('B', 'D'), F(1, 2), pause=F(1))), end_day=1)
        planner = ExactPlanner(model)
        state = ScenarioState(0, tuple('ABCD'))
        menu = planner.bounded_action_menu(state)
        greedy_tail = planner.evaluate_actions(state, menu.actions, controller='greedy', tie_parent=menu.parent)
        myopic_tail = planner.evaluate_actions(state, menu.actions, controller='myopic', tie_parent=menu.parent)
        self.assertEqual(greedy_tail.action, (('A', 'B'),))
        self.assertEqual(greedy_tail.value, F(7, 10))
        self.assertEqual(myopic_tail.action, ())
        self.assertEqual(myopic_tail.value, F(1))
        self.assertEqual(planner.solve(state).value, F(1))

    def test_even_static_max_weight_tail_misses_future_waiting(self):
        model = Model(actors(), (law(0, ('A', 'B'), F(1, 2), pause=F(1)),
                                 law(1, ('A', 'C'), F(2, 5), pause=F(1)),
                                 law(2, ('A', 'D'), F(9, 10), pause=F(1))), end_day=2)
        planner = ExactPlanner(model)
        state = ScenarioState(0, tuple('ABCD'))
        menu = planner.bounded_action_menu(state)
        approximate = planner.evaluate_actions(state, menu.actions, controller='myopic', tie_parent=menu.parent)
        oracle = planner.solve(state)
        self.assertEqual(approximate.action, (('A', 'B'),))
        self.assertEqual(oracle.action, ())
        true_action_value = planner.evaluate_actions(state, [approximate.action], controller='exact').value
        self.assertEqual(oracle.value - true_action_value, F(2, 5))
        coupled = planner.evaluate_actions(state, menu.actions, controller='exact', tie_parent=menu.parent)
        self.assertEqual(coupled.action, oracle.action)
        self.assertEqual(coupled.value, oracle.value)

    def test_previously_booked_pending_introduction_not_rewarded_again(self):
        for old_q in [F(1, 4), F(3, 4)]:
            model = Model(actors(), (law(0, ('A', 'B'), old_q),
                                     law(1, ('C', 'D'), F(3, 10))), end_day=1)
            state = ScenarioState(1, tuple('ABCD'), ready=(('A', 8), ('B', 8)),
                                  exhausted=(('A', 'B'),))
            d = ExactPlanner(model).solve(state)
            self.assertEqual(d.value, F(3, 10))
            self.assertEqual(d.action, (('C', 'D'),))

    def test_caps_and_invalid_inputs_fail_explicitly(self):
        m = Model(actors(), (law(0, ('A', 'B'), F(1, 5)),), end_day=1)
        with self.assertRaises(ValueError):
            ExactPlanner(m, Caps(max_states=100001))
        with self.assertRaises(LimitExceeded):
            ExactPlanner(m, Caps(max_states=1)).solve(ScenarioState(0, tuple('ABCD')))
        with self.assertRaises(ValueError):
            ExactPlanner(Model(actors(), (EdgeLaw(0, ('A', 'B'), F(1),
                       (ReturnOutcome(F(1), (8, 8), True),)),), end_day=0))
        with self.assertRaises(ValueError):
            ExactPlanner(Model(actors(), (EdgeLaw(0, ('A', 'B'), 0.5,
                       (ReturnOutcome(F(1), (None, None), False),)),), end_day=0))
        planner = ExactPlanner(m)
        with self.assertRaises(ValueError):
            planner.evaluate_actions(ScenarioState(0, tuple('ABCD')), [(('A', 'B'), ('A', 'B'))])
        with self.assertRaises(ValueError):
            planner.solve(Belief(((F(1, 2), ScenarioState(0, tuple('ABCD'))),
                                 (F(1, 2), ScenarioState(0, tuple('ABC'))))))


if __name__ == '__main__':
    unittest.main()
