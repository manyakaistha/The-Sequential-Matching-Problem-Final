"""Independent tiny protocol checks: examined seed101 and synthetic public states."""
import copy
import math
import unittest
from fractions import Fraction

import evaluate
from kit import HARD, Simulator, generate, baseline_asks, baseline_match, eligibility
from research4 import candidates as c


class CandidateChecks(unittest.TestCase):
    def state(self):
        return Simulator(generate(101, 200, 'evaluation')).observe()

    def legal(self, state, cfg, phase):
        response = c.decision(dict(phase=phase, state=state, memory=None), cfg)
        evaluate.validate_response(response, phase)
        members = {m['member_id']: m for m in state['members']}
        if phase == 'ask':
            seen = set()
            cost = 0
            for ask in response['asks']:
                ident, field = ask['member_id'], ask['field']
                self.assertTrue(members[ident]['available'])
                self.assertNotIn((ident, field), seen)
                seen.add((ident, field))
                cost += 3 if field == 'constraints' else 1
                if field == 'constraints':
                    self.assertFalse(any(members[ident]['field_status'][k] == 'declined' for k in HARD))
                else:
                    self.assertNotEqual(members[ident]['field_status'][field], 'declined')
            self.assertLessEqual(cost, state['ask_budget_remaining'])
        else:
            used = set()
            past = {tuple(sorted((i['user_a'], i['user_b']))) for i in state['introductions']}
            for pair in response['pairs']:
                self.assertFalse(used.intersection(pair))
                used.update(pair)
                self.assertNotIn(tuple(sorted(pair)), past)
                self.assertTrue(all(members[i]['available'] for i in pair))
                self.assertEqual(eligibility(*(members[i] for i in pair))['status'], 'feasible')
        return response

    def test_all_configs_protocol(self):
        for cfg in c.CANDIDATES.values():
            for phase in ('ask', 'match'):
                self.legal(self.state(), cfg, phase)

    def test_greedy_control_exact(self):
        s = self.state()
        self.assertEqual(c.decision({'phase': 'ask', 'state': s})['asks'], baseline_asks(s))
        self.assertEqual(c.decision({'phase': 'match', 'state': s})['pairs'], baseline_match(s))

    def test_feasible_repeat_and_busy_matching(self):
        s = self.state(); s['members'] = s['members'][:10]
        fields = dict(age_min=18, age_max=65, who_to_meet=['man'],
                      relationship_structure='monogamous', smoking='no',
                      partner_smoking='any', has_children=False,
                      partner_children='any', wants_children='unsure',
                      acceptable_zones=['zone_a'], schedule=['weekend_day'])
        for m in s['members']:
            m.update(age=30, gender='man', zone='zone_a', available=True)
            m['fields'].update(fields)
            for k in HARD: m['field_status'][k] = 'observed'
        for cfg in c.CANDIDATES.values():
            self.assertEqual(len(self.legal(s, cfg, 'match')['pairs']), 5)
        a, b = [m['member_id'] for m in s['members'][:2]]
        s['introductions'] = [{'introduction_id': 'finished', 'user_a': a, 'user_b': b, 'assigned_day': 0}]
        s['feedback'] = [{'introduction_id': 'finished', 'member_id': a, 'event': 'introduction_response', 'value': 'yes'},
                         {'introduction_id': 'finished', 'member_id': b, 'event': 'introduction_response', 'value': 'no'}]
        for cfg in c.CANDIDATES.values():
            self.assertEqual(len(self.legal(s, cfg, 'match')['pairs']), 5)
        s['members'][0]['available'] = False
        for cfg in c.CANDIDATES.values():
            self.assertEqual(len(self.legal(s, cfg, 'match')['pairs']), 4)

    def test_empty_exhausted_declined(self):
        for cfg in c.CANDIDATES.values():
            empty = self.state(); empty['members'] = []
            for phase in ('ask', 'match'):
                self.assertEqual(self.legal(empty, cfg, phase)['asks' if phase == 'ask' else 'pairs'], [])
            s = self.state(); s['ask_budget_remaining'] = 0
            self.assertEqual(self.legal(s, cfg, 'ask')['asks'], [])
            s = self.state()
            for m in s['members']:
                m['fields']['schedule'] = None; m['field_status']['schedule'] = 'declined'
                m['fields']['relationship_goal'] = None; m['field_status']['relationship_goal'] = 'declined'
            self.assertEqual(self.legal(s, cfg, 'ask')['asks'], [])
            self.assertEqual(self.legal(s, cfg, 'match')['pairs'], [])

    def test_coordinated_same_batch_resolves(self):
        sim = Simulator(generate(101, 200, 'evaluation'))
        s = sim.observe()
        # Keep four arrived actors; make unknown hard fields answerable.
        s['members'] = [m for m in s['members'] if m['available']][:4]
        self.assertEqual(len(s['members']), 4)
        for m in s['members']:
            actual = sim.members[m['member_id']]
            for k in HARD:
                actual['fields'][k] = m['fields'][k] = None
                actual['field_status'][k] = m['field_status'][k] = 'unobserved'
            actual['fields']['relationship_goal'] = m['fields']['relationship_goal'] = None
            actual['field_status']['relationship_goal'] = m['field_status']['relationship_goal'] = 'unobserved'
        asks = self.legal(s, c.CANDIDATES['coordinated_goal'], 'ask')['asks']
        hard = {a['member_id'] for a in asks if a['field'] == 'constraints'}
        soft = {a['member_id'] for a in asks if a['field'] == 'relationship_goal'}
        self.assertEqual(len(hard), 3); self.assertEqual(hard, soft)
        sim.resolve_asks(asks)
        observed = {m['member_id']: m for m in sim.observe()['members']}
        self.assertEqual(sim.ask_spent, 12)
        for ident in hard:
            self.assertTrue(all(observed[ident]['field_status'][k] == 'observed' for k in HARD))
            self.assertEqual(observed[ident]['field_status']['relationship_goal'], 'observed')

    def test_uniform_second_exact(self):
        a, b = Fraction(55, 100), Fraction(98, 100)
        self.assertAlmostEqual(c.uniform_second(0, 0), float((a*a+a*b+b*b)/3), places=15)
        # Independent polynomial integration of the specified truncated prior.
        import math
        def z(s, f):
            return sum(((-1)**j*math.comb(f, j)*(b**(s+j+1)-a**(s+j+1))/(s+j+1)
                        for j in range(f+1)), Fraction(0))
        for s, f in ((7, 7), (7, 0), (0, 7)):
            value = c.uniform_second(s, f)
            self.assertEqual(value, float(z(s+2, f)/z(s, f)))
            self.assertTrue(float(a*a) < value < float(b*b))
        self.assertGreater(c.uniform_second(7, 0), c.uniform_second(0, 0))
        self.assertLess(c.uniform_second(0, 7), c.uniform_second(0, 0))

    def test_acceptance_public_likelihood_and_posterior(self):
        for equal in ((0., 0., 0., 0.), (1., 1., 1., 1.), (.2, .5, .25, 1.)):
            for bias in (-2., 0., 2.):
                for day in (0, 35, 59):
                    p = c.acceptance_likelihood(equal, bias, day)
                    self.assertTrue(math.isfinite(p) and 0 < p < 1)
        # Marginalize the Bernoulli feature itself, before sigmoid expectation.
        unknown = c.acceptance_likelihood((.5, 0., 0., 0.), 0., 0)
        endpoints = (c.acceptance_likelihood((0., 0., 0., 0.), 0., 0) +
                     c.acceptance_likelihood((1., 0., 0., 0.), 0., 0))/2
        self.assertAlmostEqual(unknown, endpoints, places=14)
        s = self.state(); a, b = s['members'][:2]
        s['introductions'] = [{'introduction_id': 'observed', 'user_a': a['member_id'], 'user_b': b['member_id'], 'assigned_day': 0}]
        self.assertEqual(c.acceptance_posteriors(s), {})
        for label, sign in (('yes', 1), ('no', -1)):
            s['feedback'] = [{'introduction_id': 'observed', 'member_id': a['member_id'], 'event': 'introduction_response', 'value': label}]
            mean, variance, second, second_var = c.acceptance_posteriors(s)[a['member_id']]
            self.assertGreater(sign*mean, 0)
            self.assertTrue(math.isfinite(variance) and variance >= 0)
            self.assertEqual((second, second_var), (0., .25))
        s['feedback'][0]['value'] = None
        self.assertEqual(c.acceptance_posteriors(s), {})


if __name__ == '__main__':
    unittest.main(verbosity=2)
