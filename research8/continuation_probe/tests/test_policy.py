"""Constructed public fixtures only; no sampled episodes or private worlds."""
import copy
import unittest
from unittest.mock import patch

from research8.continuation_probe import policy
from research8.w2.public_rules import SOFT
from research8.w2.protocol import sanitize_observation


def fixture(day=7):
    fields = dict(age_min=18, age_max=65, who_to_meet=['woman'],
                  relationship_structure='monogamous', smoking='no',
                  partner_smoking='any', has_children=False, partner_children='any',
                  wants_children='unsure', acceptable_zones=['zone_a'],
                  schedule=['weekend_day'])
    fields.update({k: 'same' for k in SOFT})
    members = []
    for ident in ['opaque Z', 'opaque A', 'opaque Y', 'opaque B', 'opaque X', 'opaque C']:
        f = copy.deepcopy(fields)
        if ident == 'opaque A':
            f.update({k: 'different' for k in SOFT})
        members.append(dict(member_id=ident, pool_id='public_pool', synthetic=True,
                            age=30, gender='woman', zone='zone_a', arrived_day=0,
                            fields=f, field_status={k: 'observed' for k in f},
                            field_observed_day={k: 0 for k in f},
                            source='declared_fixture', available=ident not in
                            ('opaque Y', 'opaque B')))
    intro = dict(introduction_id='public intro', user_a='opaque Y', user_b='opaque B',
                 assigned_day=day-7, response_deadline_day=day,
                 logging_policy='declared_fixture', propensity=None)
    event = dict(introduction_id='public intro', member_id='opaque Y',
                 event='introduction_response', value='no', missing_reason=None,
                 occurred_day=day-3, observed_day=day-3)
    request = dict(schema_version='1.0.0', phase='match', memory={}, state=dict(schema_version='1.0.0', synthetic=True,
                day=day, ask_budget_remaining=12, members=members,
                introductions=[intro], feedback=[event], ask_log=[]))
    assert sanitize_observation(request) == request
    return request


PARENT_PAIRS = [['opaque Z', 'opaque A'], ['opaque X', 'opaque C']]


class HoldTests(unittest.TestCase):
    def call(self, request, ident='Q6_return_hold', memory=None, fallback=False):
        observed = []

        def parent(req, cfg):
            observed.append((copy.deepcopy(req), cfg))
            policy.reference_adapter.LAST_STATUS = {'fallback': fallback,
                                                     'reason': 'fixture' if fallback else None}
            return ({'asks': [{'member_id': 'opaque Z', 'field': 'constraints'}],
                     'memory': {'q6': 1}} if req['phase'] == 'ask' else
                    {'pairs': copy.deepcopy(PARENT_PAIRS), 'memory': {'q6': 1}})

        with patch.object(policy.reference_adapter, 'decide', side_effect=parent):
            result = policy.decide(request, {'id': ident})
        return result, observed

    def test_trigger_and_no_future_forced_pair(self):
        req = fixture()
        original = copy.deepcopy(req)
        result, calls = self.call(req)
        self.assertEqual(result['pairs'], PARENT_PAIRS[1:])
        self.assertEqual(result['memory']['held'], PARENT_PAIRS[0])
        self.assertEqual(result['memory']['hold_events'][0]['alternative'], 'opaque Y')
        self.assertEqual(result['memory']['hold_events'][0]['new_score'], 7)
        self.assertEqual(result['memory']['hold_events'][0]['held_endpoint'], 'opaque Z')
        self.assertEqual(result['memory']['hold_events'][0]['target_day'], 8)
        self.assertEqual(calls[0][0]['memory'], {})
        self.assertEqual(req, original)
        req['state']['day'] += 1
        req['memory'] = result['memory']
        result2, calls2 = self.call(req)
        self.assertEqual(result2['pairs'], PARENT_PAIRS)
        self.assertEqual(calls2[0][0]['memory'], {'q6': 1})

    def test_no_released_negative_and_response_clock(self):
        for mode in ('yes', 'unreleased', 'early_assignment'):
            with self.subTest(mode=mode):
                req = fixture()
                if mode == 'yes':
                    req['state']['feedback'][0]['value'] = 'yes'
                elif mode == 'unreleased':
                    req['state']['feedback'][0]['observed_day'] = 8
                else:
                    req['state']['introductions'][0]['assigned_day'] = 1
                self.assertEqual(self.call(req)[0]['pairs'], PARENT_PAIRS)
        req = fixture()
        req['state']['feedback'][0].update(value=None, occurred_day=None,
                                          missing_reason='no_response', observed_day=7)
        self.assertEqual(self.call(req)[0]['pairs'], PARENT_PAIRS[1:])
        req['state']['feedback'][0]['observed_day'] = 3
        self.assertEqual(self.call(req)[0]['pairs'], PARENT_PAIRS)

    def test_no_improvement(self):
        req = fixture()
        req['state']['members'][1]['fields'].update({k: 'same' for k in SOFT})
        self.assertEqual(self.call(req)[0]['pairs'], PARENT_PAIRS)

    def test_day_59_never_holds(self):
        self.assertEqual(self.call(fixture(59))[0]['pairs'], PARENT_PAIRS)

    def test_repeat_and_latest_introduction(self):
        req = fixture(23)
        older = copy.deepcopy(req['state']['introductions'][0])
        older.update(introduction_id='older dyad', user_a='opaque Z',
                     user_b='opaque Y', assigned_day=0, response_deadline_day=7)
        req['state']['introductions'].append(older)
        # Also exhaust the other endpoint's alternative, independently of score.
        older = copy.deepcopy(older)
        older.update(introduction_id='older dyad 2', user_a='opaque A',
                     assigned_day=8, response_deadline_day=15)
        req['state']['introductions'].append(older)
        req['state']['members'][3]['fields'].update({k: 'unshared' for k in SOFT})
        self.assertEqual(self.call(req)[0]['pairs'], PARENT_PAIRS)
        req = fixture()
        latest = copy.deepcopy(req['state']['introductions'][0])
        latest.update(introduction_id='latest dyad', assigned_day=2,
                      response_deadline_day=9)
        req['state']['introductions'].append(latest)
        self.assertEqual(self.call(req)[0]['pairs'], PARENT_PAIRS)

    def test_once_per_actor_and_same_day(self):
        req = fixture()
        result, _ = self.call(req)
        req['memory'] = result['memory']
        self.assertEqual(self.call(req)[0]['pairs'], PARENT_PAIRS)
        req['state']['day'] = 15
        req['state']['introductions'][0]['assigned_day'] = 8
        req['state']['introductions'][0]['response_deadline_day'] = 15
        req['state']['feedback'][0].update(occurred_day=10, observed_day=10)
        self.assertEqual(self.call(req)[0]['pairs'], PARENT_PAIRS)

    def test_parent_and_ask_exact_delegation_and_status(self):
        req = fixture()
        req['memory'] = {'direct': 'parent memory'}
        result, calls = self.call(req, 'Q6_parent')
        self.assertEqual(result, {'pairs': PARENT_PAIRS, 'memory': {'q6': 1}})
        self.assertEqual(calls, [(req, {'id': 'Q6'})])
        req = fixture()
        req['phase'] = 'ask'
        self.assertEqual(self.call(req)[0]['asks'],
                         [{'member_id': 'opaque Z', 'field': 'constraints'}])
        with self.assertRaises(RuntimeError):
            self.call(req, fallback=True)
        self.assertTrue(policy.LAST_STATUS['fallback'])

    def test_contradictions_and_malformed_memory_preserve_parent(self):
        for name in ('date_happened', 'pause_after_mutual_interest', 'second_meeting_intention'):
            req = fixture()
            req['state']['feedback'].append(dict(introduction_id='public intro',
                member_id=None, event=name, value=False, observed_day=7, occurred_day=7))
            self.assertEqual(self.call(req)[0]['pairs'], PARENT_PAIRS)
        req = fixture()
        req['memory'] = {'held': ['bad']}
        self.assertEqual(self.call(req)[0]['pairs'], PARENT_PAIRS)


if __name__ == '__main__':
    unittest.main()
