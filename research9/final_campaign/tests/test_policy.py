"""Constructed fixture checks only; no sampled matching episodes."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from research8.continuation_probe.tests.test_policy import fixture
from research8.w2.protocol import validate_ask_batch, validate_match_batch
from research9.final_campaign import features, policy


def constant_model(p=.2):
    return {'mean': [0.] * 74, 'scale': [1.] * 74,
            'coefficients': [0.] * 74, 'intercept': float(np.log(p / (1-p)))}


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'frozen.json'
        self.asset = {'schema': 'final-model-asset-v1', 'feature_names': features.feature_names(),
                      'kind': 'direct', 'models': [constant_model()]}
        self.freeze()

    def tearDown(self):
        self.temp.cleanup()

    def freeze(self):
        raw = json.dumps(self.asset).encode()
        self.path.write_bytes(raw)
        self.config = {'id': 'model_greedy', 'model_path': str(self.path),
                       'model_sha256': hashlib.sha256(raw).hexdigest()}

    def test_all_arms_return_legal_matching_and_do_not_mutate(self):
        for arm in policy.IDS:
            request = fixture()
            original = copy.deepcopy(request)
            config = dict(self.config, id=arm)
            result = policy.decide(request, config)
            state = request['state']
            ok, errors = validate_match_batch(result['pairs'],
                {m['member_id'] for m in state['members'] if m['available']},
                state['introductions'], state['members'])
            self.assertTrue(ok, errors)
            self.assertEqual(request, original)
            self.assertEqual(len(set(sum(result['pairs'], []))), 2 * len(result['pairs']))

    def test_greedy_and_repair_ties_retain_parent(self):
        graph = {('a', 'b'): .4, ('c', 'd'): .4, ('a', 'c'): .4, ('b', 'd'): .4}
        self.assertEqual(policy._greedy(graph), [('a', 'b'), ('c', 'd')])
        self.assertEqual(policy._repair(graph), policy._greedy(graph))

    def test_repair_exchanges_increase_whole_matching_value(self):
        one = {('a', 'b'): .8, ('a', 'c'): .6, ('b', 'd'): .6}
        self.assertEqual(set(policy._repair(one)), {('a', 'c'), ('b', 'd')})
        two = {('a', 'b'): .9, ('c', 'd'): .1, ('a', 'c'): .7, ('b', 'd'): .7}
        self.assertGreater(policy._value(policy._repair(two), two),
                           policy._value(policy._greedy(two), two))

    def test_day_59_continuation_is_immediate_matching(self):
        request = fixture(59)
        direct = policy.decide(request, self.config)
        continuation = policy.decide(request, dict(self.config, id='model_continuation'))
        self.assertEqual(continuation['pairs'], direct['pairs'])
        self.assertEqual(continuation['memory']['held'], [])

    def test_soft_batch_slack_cost_bound_and_parent_isolation(self):
        request = fixture()
        request['phase'] = 'ask'
        for member in request['state']['members']:
            if member['available']:
                for field in features.SOFT_FIELDS[:3]:
                    member['fields'][field] = None
                    member['field_status'][field] = 'not_asked'
                    member['field_observed_day'][field] = None
        # Retain one verified available comparison actor with known answers.
        reference = request['state']['members'][-1]
        reference.update(copy.deepcopy(fixture()['state']['members'][-1]))
        calls = []

        def parent(req, config):
            calls.append((copy.deepcopy(req['memory']), config))
            policy.reference_adapter.LAST_STATUS = {'fallback': False, 'reason': None}
            return {'asks': [{'member_id': 'opaque Z', 'field': 'constraints'}],
                    'memory': {'frozen_parent': 1}}

        with patch.object(policy.reference_adapter, 'decide', side_effect=parent):
            result = policy.decide(request, dict(self.config, id='model_soft'))
            request['memory'] = result['memory']
            policy.decide(request, dict(self.config, id='model_soft'))
        self.assertEqual(calls, [({}, {'id': 'Q6'}), ({'frozen_parent': 1}, {'id': 'Q6'})])
        self.assertEqual(result['asks'][0]['field'], 'constraints')
        self.assertEqual(len(result['asks']) - 1, 8)
        ok, errors, cost = validate_ask_batch(result['asks'],
            {m['member_id'] for m in request['state']['members'] if m['available']}, 12)
        self.assertTrue(ok, errors)
        self.assertEqual(cost, 11)

    def test_no_soft_queries_displace_full_parent_budget(self):
        request = fixture()
        asks = [{'member_id': str(i), 'field': 'constraints'} for i in range(4)]
        with patch.object(policy, '_graph', side_effect=AssertionError('unnecessary work')):
            self.assertEqual(policy._soft_asks(request['state'], asks, self.asset), [])

    def test_asset_integrity_and_probability_product_shape(self):
        matrix = np.zeros((3, 74))
        self.assertTrue(np.allclose(policy._predict(self.asset, matrix), .2))
        self.asset.update(kind='funnel', models=[constant_model(.5)] * 3)
        self.freeze()
        loaded = policy._asset(self.config)
        self.assertTrue(np.allclose(policy._predict(loaded, matrix), .125))
        self.path.write_text('{}')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            policy._asset(self.config)
        with patch.object(policy.models, 'predict', return_value=np.array([.1])):
            with self.assertRaisesRegex(ValueError, 'probability vector'):
                policy._predict(self.asset, matrix)

    def test_empirical_return_updates_once_and_no_private_fields(self):
        request = fixture()
        memory = policy._memory({})
        memory.update(expected_day=7, expected_ids=['opaque Z', 'opaque Y'])
        policy._update_returns(request['state'], memory)
        policy._update_returns(request['state'], memory)
        self.assertEqual((memory['return_yes'], memory['return_no']), (1, 1))
        self.assertIsNone(memory['expected_day'])

    def test_parent_fallback_is_never_hidden(self):
        request = fixture()
        request['phase'] = 'ask'
        def parent(req, cfg):
            policy.reference_adapter.LAST_STATUS = {'fallback': True, 'reason': 'test'}
            return {'asks': [], 'memory': {}}
        with patch.object(policy.reference_adapter, 'decide', side_effect=parent):
            with self.assertRaisesRegex(RuntimeError, 'Q6 fallback'):
                policy.decide(request, self.config)
        self.assertTrue(policy.LAST_STATUS['fallback'])


if __name__ == '__main__':
    unittest.main()
