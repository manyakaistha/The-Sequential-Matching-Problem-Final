"""Focused development tests. Independent reviewer ownership remains separate."""
import copy
import unittest
from fractions import Fraction as F
from itertools import combinations
from .solver import compile_matching, solve, matchings, validate, enumerate_policies, check_lp_certificate
from .specifications import build_specifications, market, edge


class ExactModelsTest(unittest.TestCase):
    def test_all_named_values_and_action_values(self):
        specs = build_specifications()
        for spec in specs['matching']+specs['information']:
            with self.subTest(model=spec['id']):
                mdp = compile_matching(spec) if 'n' in spec else spec
                answer = solve(mdp)
                self.assertEqual(answer['value'],spec['expected'])
                if spec.get('expected_first_action'):
                    self.assertIn(spec['expected_first_action'],answer['initial_optimal_actions'])

    def test_matchings_against_vertex_partition_enumeration(self):
        # Distinct recursion: select first remaining vertex, leave unmatched or
        # pair to one remaining neighbor. Exhaustive all 64 four-vertex graphs.
        def vertex_reference(vertices, edges):
            if not vertices:
                return {()}
            i,*rest = vertices
            result = vertex_reference(rest,edges)
            for j in rest:
                if (i,j) in edges:
                    result |= {tuple(sorted(((i,j),)+m)) for m in
                               vertex_reference([v for v in rest if v!=j],edges)}
            return result
        possible = list(combinations(range(4),2))
        for mask in range(64):
            edges = {e for i,e in enumerate(possible) if mask&(1<<i)}
            self.assertEqual(set(matchings(edges)),vertex_reference(list(range(4)),edges))

    def test_probability_validation_rejects_bad_mass_and_cycle(self):
        mdp = compile_matching(market('bad',2,[0],[edge(0,1,'1/3',[0])],0))
        bad = copy.deepcopy(mdp)
        bad['states']['s0']['actions']['0-1']['transitions'][0]['probability']='1'
        with self.assertRaises(AssertionError):
            validate(bad)
        bad = copy.deepcopy(mdp)
        bad['states']['s0']['actions']['wait']['transitions'][0]['next']='s0'
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_full_followup_and_no_repeat(self):
        spec=market('late',2,[59,60],[edge(0,1,'1/2',[59,60],duration=1)],'1/2')
        mdp=compile_matching(spec)
        answer=solve(mdp)
        self.assertEqual(answer['value'],'1/2')
        for t in mdp['states']['s0']['actions']['0-1']['transitions']:
            self.assertEqual(list(mdp['states'][t['next']]['actions']),['wait'])
        # Full follow-up preserves final assignment reward for every busy length.
        for duration in (1,8,1000):
            mdp=compile_matching(market('final',2,[59],[edge(0,1,'1/2',[59],duration=duration)],'1/2'))
            self.assertEqual(solve(mdp)['value'],'1/2')

    def test_held_out_every_bellman_action(self):
        for spec in build_specifications()['held_out_constructed_sweep']:
            with self.subTest(model=spec['id']):
                mdp=compile_matching(spec)
                answer, reference=solve(mdp),enumerate_policies(mdp)
                for state, row in reference['states'].items():
                    self.assertEqual(row['value'],answer['states'][state]['value'])
                    self.assertEqual(row['action_values'],answer['states'][state]['action_values'])

    def test_lp_certificates_and_wrong_dual_rejected(self):
        for cert in build_specifications()['lp_certificates'].values():
            self.assertTrue(check_lp_certificate(cert)['exact_optimum'])
        bad=copy.deepcopy(build_specifications()['lp_certificates']['two_day_renewal'])
        bad['dual']=['0','0']
        with self.assertRaises(AssertionError):
            check_lp_certificate(bad)


if __name__ == '__main__':
    unittest.main()
