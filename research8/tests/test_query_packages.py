import unittest
from fractions import Fraction as F
from itertools import product

from research8.query_packages import (AnswerScenario, QueryLimitError, QueryModel,
                                     QueryModelError, choose_package, evaluate_package)


class QueryTests(unittest.TestCase):
    def test_soft_displaces_hard_under_actual_twelve_units(self):
        edges = (('A', 'B'), ('A', 'C'), ('D', 'E'), ('F', 'G'))
        queries = (('A', 'goal'), ('D', 'constraints'), ('E', 'constraints'),
                   ('F', 'constraints'), ('G', 'constraints'))
        scenarios = tuple(AnswerScenario(F(1, 2), tuple((a, True) for a in 'DEFG'),
                             ((('A', 'goal'), answer),),
                             tuple(zip(edges, (ab, ac, F(4, 5), F(2, 5)))))
                          for answer, ab, ac in [('x', F(1), F(0)), ('y', F(0), F(1))])
        model = QueryModel(tuple('ABCDEFGH'), tuple('ABC'), scenarios, queries, edges)
        self.assertEqual(evaluate_package(model, queries[1:]), F(17, 10))
        selected = choose_package(model)
        self.assertEqual(selected.value, F(9, 5))
        self.assertEqual(selected.package, (('A', 'goal'), ('D', 'constraints'), ('E', 'constraints')))
        self.assertEqual(evaluate_package(model, ()), F(1, 2))

    def test_hidden_profile_not_oracle_without_query(self):
        edges = (('A', 'B'), ('A', 'C'))
        scenarios = (AnswerScenario(F(1, 2), (), ((('A', 'goal'), 'x'),),
                                    tuple(zip(edges, (F(1), F(0))))),
                     AnswerScenario(F(1, 2), (), ((('A', 'goal'), 'y'),),
                                    tuple(zip(edges, (F(0), F(1))))))
        model = QueryModel(tuple('ABCD'), tuple('ABC'), scenarios, (('A', 'goal'),), edges)
        self.assertEqual(evaluate_package(model, ()), F(1, 2))
        self.assertEqual(evaluate_package(model, (('A', 'goal'),)), F(1))
        self.assertEqual(choose_package(model).value, F(1))

    def test_hard_complement_and_soft_cannot_legalize(self):
        scenarios = (AnswerScenario(F(1), (('A', True), ('B', True)),
                                    ((('A', 'goal'), 'x'),), ((('A', 'B'), F(1)),)),)
        queries = (('A', 'constraints'), ('B', 'constraints'), ('A', 'goal'))
        model = QueryModel(tuple('ABCD'), (), scenarios, queries, (('A', 'B'),))
        for package in [(), (queries[0],), (queries[1],), (queries[2],), (queries[0], queries[2])]:
            self.assertEqual(evaluate_package(model, package), 0)
        self.assertEqual(evaluate_package(model, queries[:2]), 1)
        self.assertEqual(choose_package(model).package, tuple(sorted(queries[:2])))

    def test_decline_and_observed_false_are_not_truthy(self):
        for answer in [False, None]:
            s = AnswerScenario(F(1), (('B', answer),), (), ((('A', 'B'), F(1)),))
            m = QueryModel(tuple('ABCD'), ('A',), (s,), (('B', 'constraints'),), (('A', 'B'),))
            self.assertEqual(evaluate_package(m, m.queries), 0)
            self.assertEqual(choose_package(m).package, ())

    def test_collision_joint_scenarios(self):
        # Verified A,B,C; uncertain U1,U2 collide on A, V1,V2 reach B,C.
        actors = ('A', 'B', 'C', 'U1', 'U2', 'V1', 'V2')
        edges = (('A', 'U1'), ('A', 'U2'), ('B', 'V1'), ('C', 'V2'))
        qs = tuple((a, 'constraints') for a in ('U1', 'U2', 'V1', 'V2'))
        probs = (F(4, 5), F(4, 5), F(7, 10), F(7, 10))
        scenarios = []
        for bits in product((False, True), repeat=4):
            p = F(1)
            for bit, yes in zip(bits, probs):
                p *= yes if bit else 1 - yes
            scenarios.append(AnswerScenario(p, tuple(zip(('U1', 'U2', 'V1', 'V2'), bits)),
                                            (), tuple((e, F(1)) for e in edges)))
        m = QueryModel(actors, tuple('ABC'), tuple(scenarios), qs, edges, budget=6)
        self.assertEqual(evaluate_package(m, qs[:2]), F(24, 25))
        self.assertEqual(evaluate_package(m, qs[2:]), F(7, 5))
        # Mixed high-probability+distinct wins1.5, a needed whole-menu check.
        self.assertEqual(choose_package(m).value, F(3, 2))

    def test_cap_invalid_package_and_probability(self):
        s = AnswerScenario(F(1), (('A', True), ('B', True)), (), ((('A', 'B'), F(1)),))
        m = QueryModel(tuple('ABCD'), (), (s,), (('A', 'constraints'), ('B', 'constraints')),
                       (('A', 'B'),), max_packages=1)
        with self.assertRaises(QueryLimitError):
            choose_package(m)
        with self.assertRaises(QueryModelError):
            evaluate_package(m, (m.queries[0], m.queries[0]))
        with self.assertRaises(QueryModelError):
            QueryModel(('', 'B', 'C', 'D'), (), (s,), m.queries, m.edges)
        with self.assertRaises(QueryLimitError):
            QueryModel(tuple('ABCD'), (), (s,), m.queries, m.edges, max_scenarios=True)
        with self.assertRaises(QueryModelError):
            QueryModel(tuple('ABCD'), (), (AnswerScenario(F(1, 2), s.hard, (), s.rewards),),
                       m.queries, m.edges)

    def test_every_eight_actor_hard_package(self):
        actors = tuple('ABCDEFGH')
        edges = (('A', 'B'), ('C', 'D'), ('E', 'F'), ('G', 'H'))
        s = AnswerScenario(F(1), tuple((a, True) for a in actors), (),
                           tuple(zip(edges, (F(1), F(4, 5), F(3, 5), F(2, 5)))))
        m = QueryModel(actors, (), (s,), tuple((a, 'constraints') for a in actors), edges)
        decision = choose_package(m)
        self.assertEqual(decision.value, F(9, 5))
        self.assertEqual(len(decision.values), 163)
        self.assertEqual(decision.package, tuple((a, 'constraints') for a in 'ABCD'))


if __name__ == '__main__':
    unittest.main()
