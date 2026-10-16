import unittest
from fractions import Fraction as F
from unittest.mock import patch
from research8.planner import Actor, Belief, EdgeLaw, ExactPlanner, Model, ReturnOutcome, ScenarioState
from research8.w2.bounded import BoundedConfig, BoundedPlanner
from research8.w2.tests.fixtures import absorbing


class BoundedTests(unittest.TestCase):
    def test_future_waiting_and_static_matching_falsifiers(self):
        for edges,end,expected in [
            ((absorbing(0,('A','B'),F(1,2)),absorbing(1,('A','C'),F(2,5)),absorbing(2,('A','D'),F(9,10))),2,F(9,10)),
            ((absorbing(0,('A','B'),F(7,10)),absorbing(1,('A','B'),F(3,5)),absorbing(1,('A','C'),F(1,2)),absorbing(1,('B','D'),F(1,2))),1,F(1))]:
            model=Model(tuple(Actor(a) for a in 'ABCD'),edges,end_day=end)
            state=ScenarioState(0,tuple('ABCD'))
            result=BoundedPlanner(model).solve(state)
            self.assertFalse(result.used_fallback)
            self.assertEqual((result.action,result.value),((),expected))
            self.assertEqual(result.value,ExactPlanner(model).solve(state).value)

    def test_hidden_clock_and_public_menu(self):
        model=Model(tuple(Actor(a) for a in 'ABCD'),
                    (absorbing(1,('A','B'),F(3,5)),absorbing(2,('A','C'),F(1))),end_day=2)
        prior=Belief(((F(1,2),ScenarioState(1,tuple('ABCD'),(('C',2),))),
                      (F(1,2),ScenarioState(1,tuple('ABCD'),(('C',3),)))))
        result=BoundedPlanner(model).solve(prior)
        self.assertEqual(result.value,F(3,5))
        self.assertEqual(result.action,(('A','B'),))
        reverse=BoundedPlanner(model).solve(Belief(tuple(reversed(prior.particles))))
        self.assertEqual((result.value,result.action),(reverse.value,reverse.action))

    def test_each_limit_discards_partial_comparison(self):
        model=Model(tuple(Actor(a) for a in 'ABCD'),(absorbing(0,('A','B'),F(1,2)),),end_day=1)
        state=ScenarioState(0,tuple('ABCD'))
        for setting in ['max_states','max_support_entries','max_transitions','max_joint_branches']:
            result=BoundedPlanner(model,BoundedConfig(**{setting:1})).solve(state)
            self.assertTrue(result.used_fallback,setting)
            self.assertEqual(result.action,(('A','B'),))
            self.assertIsNone(result.value)
            self.assertEqual(result.action_values,())
        with patch('research8.w2.bounded.monotonic',side_effect=[0,1,1,1,1]):
            result=BoundedPlanner(model,BoundedConfig(wall_seconds=.01)).solve(state)
        self.assertTrue(result.used_fallback)
        self.assertIsNone(result.value)

    def test_oversized_prior_still_requires_lawful_common_view(self):
        model=Model(tuple(Actor(a) for a in 'ABCD'),(absorbing(0,('A','B'),F(1,2)),),end_day=0)
        state=ScenarioState(0,tuple('ABCD'))
        prior=Belief(tuple((F(1,129),state) for _ in range(129)))
        result=BoundedPlanner(model).solve(prior)
        self.assertTrue(result.used_fallback)
        with self.assertRaises(ValueError):
            BoundedPlanner(model).solve(Belief(prior.particles[:-1]))
        mixed=Belief(prior.particles[:-1]+((F(1,129),ScenarioState(0,tuple('ABC'))),))
        with self.assertRaises(ValueError):BoundedPlanner(model).solve(mixed)

    def test_final_day_reward_and_horizon_limits(self):
        model=Model(tuple(Actor(a) for a in 'ABCD'),(absorbing(59,('A','B'),F(9,10)),))
        for h in [0,12]:
            result=BoundedPlanner(model,BoundedConfig(future_steps=h)).solve(ScenarioState(59,tuple('ABCD')))
            self.assertEqual(result.value,F(9,10));self.assertEqual(result.transitions,0)
        with self.assertRaises(ValueError):BoundedConfig(future_steps=13)
        with self.assertRaises(ValueError):BoundedConfig(max_states=2001)


if __name__=='__main__':unittest.main()
