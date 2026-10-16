"""Unit test suite for round-2 components: simulators, laws, oracles, policies, and episode runner."""
import copy
import hashlib
import json
import unittest

import kit
from research9.round2 import laws as L
from research9.round2 import oracle_value as OV
from research9.round2 import fastsim as FS
from research9.round2 import priors as P
from research9.round2 import arms as A
from research9.round2 import episode as EP


class TestRound2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        P.write_builtin()
        cls.thetas = {
            'sim': P.load('sim'),
            'flat': P.load('flat'),
            'emp': P.load('emp'),
        }

    def test_01_laws_definition(self):
        self.assertEqual(len(L.FAMILIES), 6)
        self.assertIn('A_sorted', L.STRESS)
        self.assertIn('W_half_shift', L.STRESS)
        self.assertIn('R_low', L.STRESS)
        self.assertIn('D_early', L.STRESS)
        for name, law in L.ALL.items():
            self.assertEqual(law['name'], name)
            self.assertIn(law['base_family'], L.FAMILIES)

    def test_02_oracle_values(self):
        nodes, weights = OV.gauss_hermite_normal(40)
        self.assertEqual(len(nodes), 40)
        self.assertEqual(len(weights), 40)
        self.assertAlmostEqual(sum(weights), 1.0, places=7)

        # Standard date probability
        p_std = OV.date_within_probability(False, None, None)
        self.assertAlmostEqual(p_std, 1.0, places=5)
        p_del = OV.date_within_probability(True, None, None)
        self.assertGreater(p_del, 0.90)
        self.assertLess(p_del, 1.0)

    def test_03_fastsim_equivalence_on_standard_families(self):
        seed = 4000002
        for fam in ('development', 'delayed', 'shift', 'drift'):
            w = kit.generate(seed, 200, 'evaluation', fam)
            sim_kit = kit.Simulator(copy.deepcopy(w))
            sim_fast = FS.FastSimulator(copy.deepcopy(w))
            
            for _ in range(30):
                sa = sim_kit.observe()
                sb = sim_fast.observe()
                self.assertEqual(len(sa['members']), len(sb['members']))
                self.assertEqual(sa['day'], sb['day'])
                self.assertEqual(sa['ask_budget_remaining'], sb['ask_budget_remaining'])
                
                asks = kit.baseline_asks(sa)
                sim_kit.resolve_asks(asks)
                sim_fast.resolve_asks(asks)
                
                pairs = kit.baseline_match(sim_kit.observe())
                sim_kit.advance(pairs)
                sim_fast.advance(pairs)
                
            for _ in range(40):
                sim_kit.advance([])
                sim_fast.advance([])
                
            m_kit = sim_kit.metrics()
            m_fast = sim_fast.metrics()
            self.assertEqual(m_kit['assignments'], m_fast['assignments'])
            self.assertEqual(m_kit['mutual_acceptances'], m_fast['mutual_acceptances'])
            self.assertEqual(m_kit['dates'], m_fast['dates'])
            self.assertEqual(m_kit['mutual_second_meeting_intention'], m_fast['mutual_second_meeting_intention'])

    def test_04_policies_smoke(self):
        seed = 4000003
        w = kit.generate(seed, 200, 'evaluation', 'development')
        sim = FS.FastSimulator(w)
        state = sim.observe()
        
        # Test PS_emp
        req_ask = {'schema_version': kit.VERSION, 'phase': 'ask', 'state': state, 'memory': {}}
        res_ask = A.ARMS['PS_emp']['fn'](req_ask, A.config_for('PS_emp', L.get('development'), self.thetas))
        self.assertIn('asks', res_ask)
        
        req_match = {'schema_version': kit.VERSION, 'phase': 'match', 'state': state, 'memory': {}}
        res_match = A.ARMS['PS_emp']['fn'](req_match, A.config_for('PS_emp', L.get('development'), self.thetas))
        self.assertIn('pairs', res_match)
        self.assertIn('memory', res_match)
        self.assertIn('pred', res_match['memory'])

        # Test X1_emp
        res_x1_match = A.ARMS['X1_emp']['fn'](req_match, A.config_for('X1_emp', L.get('development'), self.thetas))
        self.assertIn('pairs', res_x1_match)
        self.assertIn('memory', res_x1_match)

    def test_05_episode_runner(self):
        seed = 4000004
        # Test running 1 episode of G
        rec_g = EP.run_episode(seed, 'development', 'G', self.thetas, keep_ledger=False)
        self.assertTrue(rec_g['valid'])
        self.assertIn('metrics', rec_g)
        self.assertIn('intros', rec_g)
        self.assertIn('members', rec_g)

        # Test running 1 episode of X1_emp on drift
        rec_x1 = EP.run_episode(seed, 'drift', 'X1_emp', self.thetas, keep_ledger=False)
        self.assertTrue(rec_x1['valid'])
        self.assertIn('metrics', rec_x1)


if __name__ == '__main__':
    unittest.main()
