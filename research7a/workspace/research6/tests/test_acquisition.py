"""Constructed public fixtures only; no world generation, fitting or episodes."""
import copy
import itertools
import json
import subprocess
import sys
import time
import unittest
from collections import Counter
from unittest.mock import patch

from kit import HARD, SOFT, baseline_asks, baseline_match, eligibility
from research6.policies import acquisition as acq
from research6.tests.test_allocation import member


def request(n=10, missing='schedule', budget=12):
    members = [member(f'm{i:03}', acq.SCHEDULE) for i in range(n)]
    for m in members:
        if missing:
            m['fields'][missing] = None
            m['field_status'][missing] = 'not_asked'
    return {'phase': 'ask', 'state': {'members': members, 'day': 0,
        'ask_budget_remaining': budget, 'introductions': [], 'feedback': []}, 'memory': {}}


class AcquisitionTests(unittest.TestCase):
    def test_source_probabilities_clipping_false_and_sparse(self):
        m = member('x', acq.SCHEDULE)
        m['age'] = 21
        for f in HARD:
            m['fields'][f] = None
            m['field_status'][f] = 'not_asked'
        draws = [acq.sample_member(m, 1, 0, p)['fields'] for p in range(8000)]
        def rate(field, value):
            return sum(d[field] == value for d in draws) / len(draws)
        self.assertAlmostEqual(rate('age_min', 18), 1.)
        self.assertAlmostEqual(rate('relationship_structure', 'monogamous'), .9, delta=.02)
        self.assertAlmostEqual(rate('has_children', True), .15, delta=.02)
        self.assertAlmostEqual(rate('smoking', 'no'), .75, delta=.02)
        self.assertAlmostEqual(rate('smoking', 'occasionally'), .2, delta=.02)
        self.assertAlmostEqual(rate('smoking', 'yes'), .05, delta=.015)
        for field, values in [('partner_smoking', ['no_smoking', 'any']),
                              ('partner_children', ['any', 'no_children']),
                              ('wants_children', ['yes', 'no', 'unsure'])]:
            for v in values:
                self.assertAlmostEqual(rate(field, v), 1/len(values), delta=.02)
        self.assertAlmostEqual(sum(len(d['acceptable_zones']) == 1 for d in draws)/8000, .775, delta=.02)
        for zone in acq.ZONES[1:]:
            self.assertAlmostEqual(sum(d['acceptable_zones'] == ['zone_a', zone] for d in draws)/8000, .075, delta=.015)
        for length, prob in [(1, .7), (2, .2), (3, .1)]:
            self.assertAlmostEqual(sum(len(d['who_to_meet']) == length for d in draws)/8000, prob, delta=.02)
        for length in (1, 2, 3):
            self.assertAlmostEqual(sum(len(d['schedule']) == length for d in draws)/8000, 1/3, delta=.02)
        # Clipping multiplicity: age 24, lower endpoint 18 corresponds to R=6..10.
        m['age'] = 24
        lower = Counter(acq.sample_member(m, 2, 1, p)['fields']['age_min'] for p in range(1600))
        self.assertAlmostEqual(lower[18]/1600, 5/8, delta=.04)
        m['age'] = 60
        upper = Counter(acq.sample_member(m, 2, 1, p)['fields']['age_max'] for p in range(1600))
        self.assertAlmostEqual(upper[65]/1600, 6/8, delta=.04)
        m['fields']['has_children'] = False
        m['field_status']['has_children'] = 'observed'
        m['zone'] = 'zone_11'
        self.assertIs(acq.sample_member(m, 0, 1, 0)['fields']['has_children'], False)
        self.assertEqual(acq.sample_member(m, 0, 1, 0)['fields']['acceptable_zones'], ['zone_11'])
        m['field_status']['smoking'] = 'declined'
        with self.assertRaises(ValueError):
            acq.sample_member(m, 0, 1, 0)

    def test_masked_graph_is_literal_g_all_batches_and_shared_draws(self):
        req = request(10)
        req['state']['members'][8]['fields']['schedule'] = ['weekend_day']
        req['state']['members'][9]['available'] = False
        for i, m in enumerate(req['state']['members']):
            for j, f in enumerate(SOFT):
                m['fields'][f] = None if (i+j) % 5 == 0 else str((i+j) % 3)
        req['state']['introductions'] = [{'user_a': 'm000', 'user_b': 'm001'}]
        problem = acq.build_problem(req['state'])
        for p in range(3):
            draws = {i: acq.sample_member(req['state']['members'][i], 0, i, p) for i in problem['sampled']}
            frozen = copy.deepcopy(draws)
            edges = acq.particle_edges(req['state'], problem, draws)
            for batch in problem['batches']:
                hypothetical = copy.deepcopy(req['state'])
                for i in batch:
                    hypothetical['members'][i] = draws[i]
                mask = sum(problem['bits'][i] for i in batch)
                pairs = acq.masked_match(edges, mask, True)
                self.assertEqual(pairs, baseline_match(hypothetical))
                score = sum(sum(hypothetical['members'][int(a[1:])]['fields'].get(f) is not None and
                                    hypothetical['members'][int(a[1:])]['fields'].get(f) ==
                                    hypothetical['members'][int(b[1:])]['fields'].get(f) for f in SOFT)
                            for a, b in pairs)
                self.assertEqual(acq.masked_match(edges, mask), (len(pairs), score))
            self.assertEqual(draws, frozen)

    def test_budget_fifo_declines_and_public_only(self):
        for budget in range(13):
            req = request(budget=budget)
            req['state']['members'][0]['field_status']['schedule'] = 'declined'
            before = copy.deepcopy(req)
            response = acq.action(req, {'id': 'N3'})
            self.assertEqual(len(response['asks']), min(4, budget//3, 9))
            self.assertEqual(len({a['member_id'] for a in response['asks']}), len(response['asks']))
            self.assertTrue(all(a['field'] == 'constraints' and a['member_id'] != 'm000' for a in response['asks']))
            self.assertEqual(req, before)
            self.assertEqual(response['memory'], {})
        req = request()
        action = acq.action(req, {'id': 'N3'})
        objective = copy.deepcopy(acq.LAST_DIAGNOSTICS['chosen_objective'])
        req['seed'] = -999
        req['state']['family'] = 'hidden'
        for m in req['state']['members']:
            m['truth'] = {f: 'perturbation' for f in HARD}
        self.assertEqual(acq.action(req, {'id': 'N3'}), action)
        self.assertEqual(acq.LAST_DIAGNOSTICS['chosen_objective'], objective)
        self.assertIn(acq.LAST_DIAGNOSTICS['fifo'], [tuple(x['batch']) for x in acq.LAST_DIAGNOSTICS['considered']])
        self.assertEqual(acq._select([(0, 1), (2, 3)], (0, 1), {(0, 1): (2, 7), (2, 3): (2, 7)}), (0, 1))
        self.assertEqual(acq._select([(1, 2), (3, 4), (0, 5)], (0, 5),
                                    {(1, 2): (3, 7), (3, 4): (3, 7), (0, 5): (2, 7)}), (1, 2))
        report = acq.evaluate_batches(req['state'], [(0, 1, 2, 3), (4, 5, 6, 7)], 'registered-audit-stream')
        self.assertEqual(report, acq.evaluate_batches(req['state'], [(0, 1, 2, 3), (4, 5, 6, 7)], 'registered-audit-stream'))
        self.assertEqual(report['particles'], 32)

    def test_complementarity_collision_and_changed_query_set(self):
        # Two incomplete endpoints are jointly necessary; edge collision limits value.
        edges = [(3, 3, 7, ('a', 'b')), (5, 5, 7, ('a', 'c'))]
        self.assertEqual(acq.masked_match(edges, 1), (0, 0))
        self.assertEqual(acq.masked_match(edges, 3), (1, 7))
        self.assertEqual(acq.masked_match(edges, 7), (1, 7))
        req = request(8)
        for m in req['state']['members'][:4]:
            m['fields']['who_to_meet'] = ['man']
        action = acq.action(req, {'id': 'N3'})
        self.assertNotEqual(action['asks'], baseline_asks(req['state']))
        self.assertGreater(acq.LAST_DIAGNOSTICS['paired_difference'][0], 0)
        self.assertTrue(all(x['two_bundle_degree'] > 0 for x in acq.LAST_DIAGNOSTICS['ranks'][0:4]))

    def test_guard_error_actual_matching_and_history_invariant(self):
        req = request()
        for injected in (acq.WorkDeadline('test'), RuntimeError('test')):
            with patch.object(acq, '_guard', side_effect=injected):
                self.assertEqual(acq.action(req, {'id': 'N3'})['asks'], baseline_asks(req['state']))
                self.assertTrue(acq.LAST_DIAGNOSTICS['fallback'])
        with patch.object(acq, 'GUARD_SECONDS', 0):
            acq.action(req, {'id': 'N3'})
            self.assertIn('WorkDeadline', acq.LAST_DIAGNOSTICS['reason'])
        req['state']['members'][0]['zone'] = 'unsupported'
        acq.action(req, {'id': 'N3'})
        self.assertIn('unsupported', acq.LAST_DIAGNOSTICS['reason'])
        req = request(6, missing=None)
        req['phase'] = 'match'
        self.assertEqual(acq.action(req, {'id': 'N3'})['pairs'], baseline_match(req['state']))
        # Legal introduction requires all hard fields; monotone disclosure cannot
        # produce an incomplete actor after a legal introduction.
        a, b = req['state']['members'][:2]
        for field in HARD:
            incomplete = copy.deepcopy(a)
            incomplete['fields'][field] = None
            self.assertNotEqual(eligibility(incomplete, b)['status'], 'feasible')
        self.assertEqual(acq.LAST_DIAGNOSTICS.get('draws'), None)  # reset on match

    def test_fresh_process_replay_and_dense_full_work(self):
        req = request()
        expected = acq.action(req, {'id': 'N3'})
        script = 'import json,sys; from research6.policies.acquisition import action; print(json.dumps(action(json.load(sys.stdin), {"id":"N3"})))'
        for _ in range(2):
            proc = subprocess.run([sys.executable, '-c', script], input=json.dumps(req),
                capture_output=True, text=True, check=True, timeout=10)
            self.assertEqual(json.loads(proc.stdout), expected)
        req = request(200, missing=None)
        for m in req['state']['members'][:12]:
            m['fields']['age_min'] = None
            m['field_status']['age_min'] = 'not_asked'
        for m in req['state']['members'][:4]:
            m['fields']['who_to_meet'] = ['man']
        # Keep all incident edges feasible under every radius; FIFO outside
        # shortlist is exercised separately by ranking against low-degree actors.
        start = time.monotonic()
        acq.action(req, {'id': 'N3'})
        elapsed = time.monotonic() - start
        diag = acq.LAST_DIAGNOSTICS
        self.assertFalse(diag['fallback'], diag)
        self.assertEqual(diag['work']['particles'], 32)
        self.assertEqual(diag['work']['batches'], 71)
        self.assertEqual(diag['work']['sampled_actors'], 12)
        self.assertGreater(diag['work']['edge_scans'], 40_000_000)
        self.assertLess(elapsed, 6.)
        self.assertLess(len(json.dumps(expected['memory']).encode()), 65536)
        print(f'N3 constructed dense full work: {elapsed:.3f}s; {diag["work"]}')


if __name__ == '__main__':
    unittest.main()
