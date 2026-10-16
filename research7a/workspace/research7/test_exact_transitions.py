"""Adversarial constructed checks for the independent rational belief engine."""
import unittest
from dataclasses import replace
from fractions import Fraction as F
from research7.exact_independent.models import Actor, Edge, State, TemporalModel, law
from research7.exact_independent.solver import BeliefSolver, vertex_recursive_enumeration
from research7.exact_independent.specifications import run_exact_specification_check


class HiddenGuess:
    """Hidden bit never revealed; posterior remains balanced at next decision."""
    initial=[(F(1,2),(0,False)),(F(1,2),(0,True))]
    def observe(self,s): return s[0]
    def terminal(self,s): return s[0]==2
    def actions(self,s): return ('advance',) if s[0]==0 else ('false','true')
    def transition(self,s,a):
        reward=F(int((a=='true')==s[1])) if s[0]==1 else F(0)
        return [(F(1),(s[0]+1,s[1]),reward)]


class ExactTransitions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=run_exact_specification_check()

    def test_all_constructed_assertions(self):
        for name,case in self.report['case_ledger'].items():
            with self.subTest(case=name):
                self.assertTrue(case['verified'],case['checks'])
                self.assertTrue(all(case['checks'].values()))

    def test_full_reachable_traces_and_bellman_values(self):
        for case in self.report['case_ledger'].values():
            for name,run in case['runs'].items():
                self.assertLessEqual(run['enumerated_states']+run['support_states'],100000)
                for node in run['nodes']:
                    self.assertEqual(sum(p for p,_ in node['belief']),1)
                    if not node['actions']:
                        self.assertEqual(node['value'],0)
                        continue
                    for a in node['actions']:
                        self.assertIsInstance(a['value'],F)
                        self.assertEqual(sum(b['mass'] for b in a['branches']),1)
                        self.assertEqual(sum(o['probability'] for o in a['outcomes']),1)
                        value=a['immediate']+sum(o['probability']*run['nodes'][o['child']]['value'] for o in a['outcomes'])
                        self.assertEqual(a['value'],value)
                    self.assertEqual(node['value'],max(a['value'] for a in node['actions']))
                    self.assertEqual(set(node['ties']),{a['action'] for a in node['actions'] if a['value']==node['value']})

    def test_nonanticipation_not_first_hidden_state(self):
        result=BeliefSolver(HiddenGuess()).solve()
        self.assertEqual(result['value'],F(1,2))
        decision=result['nodes'][1]
        self.assertEqual(set(decision['ties']),{'true','false'})
        self.assertEqual(len(decision['belief']),2)
        # Reverse hidden support order: result and all action values unchanged.
        m=HiddenGuess();m.initial=list(reversed(m.initial))
        self.assertEqual(BeliefSolver(m).solve()['value'],F(1,2))

    def test_hidden_dependent_menu_rejected(self):
        class Bad(HiddenGuess):
            def actions(self,s): return (str(s[1]),)
        with self.assertRaisesRegex(ValueError,'hidden state'):
            BeliefSolver(Bad()).solve()

    def test_mask_busy_pause_repeat_overlap_and_queries(self):
        edges=[Edge(a,b,(0,8),law(F(1,2))) for a,b in (('A','B'),('A','C'),('C','D'))]
        m=TemporalModel((0,8),[Actor(a) for a in 'ABCD'],edges)
        s=State(phase='match',verified=frozenset('ABCD'),used=frozenset({('A','B')}),
                busy=(('C',8),),paused=frozenset({'D'}))
        self.assertEqual(m.actions(s),[('match',())])
        for bad in [('match',(('A','B'),)),('match',(('A','C'),)),
                    ('match',(('A','B'),('A','C')))]:
            with self.assertRaises(ValueError): list(m.transition(s,bad))
        returned=replace(s,epoch=1,busy=(),paused=frozenset())
        self.assertIn(('match',(('A','C'),)),m.actions(returned))
        self.assertNotIn(('match',(('A','B'),)),m.actions(returned))
        q=TemporalModel((0,),[Actor(a,known=False) for a in 'ABCDE'],[],12)
        unknown=q.initial[0][1]
        self.assertEqual(len(q.actions(unknown)),31) # Every size <=4 subset, no filler asks.
        for invalid in [('ask',('A','A')),('ask',tuple('ABCDE'))]:
            with self.assertRaises(ValueError): list(q.transition(unknown,invalid))
        self.assertNotIn(('ask',('A',)),q.actions(replace(unknown,busy=(('A',8),))))

    def test_private_timers_and_pending_expectation_are_masked(self):
        m=TemporalModel((0,8),[Actor('A'),Actor('B')],[Edge('A','B',(8,),law(F(1)))])
        first=State(verified=frozenset('AB'),busy=(('A',8),),pending=(('old',F(1,4)),))
        second=replace(first,busy=(('A',16),),pending=(('old',F(3,4)),))
        self.assertEqual(m.observe(first),m.observe(second))
        m.initial=[(F(1,2),first),(F(1,2),second)]
        self.assertEqual(BeliefSolver(m).solve()['value'],F(1,2))

    def test_reject_float_invalid_probability_and_enforce_cap(self):
        with self.assertRaises(TypeError): vertex_recursive_enumeration(frozenset('AB'),[('A','B',0.5)])
        class Bad(HiddenGuess):
            def transition(self,s,a): return [(F(1,2),(s[0]+1,s[1]),F(0))]
        with self.assertRaises(ValueError): BeliefSolver(Bad()).solve()
        with self.assertRaises(OverflowError): BeliefSolver(HiddenGuess(),state_cap=2).solve()
        with self.assertRaises(ValueError): BeliefSolver(HiddenGuess(),state_cap=100001)


if __name__=='__main__':
    unittest.main()
