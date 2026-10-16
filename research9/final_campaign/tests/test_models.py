"""Small synthetic unit fixtures; these are not research episodes or fitting."""
from copy import deepcopy
import json
import unittest

import numpy as np

from research9.final_campaign.features import (
    SOFT_FIELDS, feature_names, prepare_state, pair_features, batch_pair_features,
)
from research9.final_campaign.models import fit_logistic, predict


def fixture():
    def member(identity, age, value):
        return dict(member_id=identity, age=age, arrived_day=0,
                    fields={f: value for f in SOFT_FIELDS},
                    field_status={f: 'observed' for f in SOFT_FIELDS},
                    field_observed_day={f: 0 for f in SOFT_FIELDS})
    a, b = member('opaque_A', 24, 'one'), member('opaque_B', 31, 'two')
    state = dict(day=8, members=[a, b], introductions=[dict(
        introduction_id='prior', user_a=a['member_id'], user_b=b['member_id'], assigned_day=0)],
        feedback=[dict(introduction_id='prior', member_id=a['member_id'],
                       event='introduction_response', value='yes', observed_day=1)])
    return state, a, b


class PublicFeaturesTests(unittest.TestCase):
    def test_contract_symmetry_and_batch(self):
        state, a, b = fixture()
        x = pair_features(state, a, b)
        self.assertEqual(x.shape, (74,))
        self.assertEqual(len(feature_names()), len(set(feature_names())))
        np.testing.assert_array_equal(x, pair_features(state, b, a))
        np.testing.assert_array_equal(batch_pair_features(state, [(a, b)]), x[None, :])
        self.assertEqual(batch_pair_features(state, []).shape, (0, 74))
        self.assertTrue(np.isfinite(x).all())

    def test_id_renaming_member_and_feedback_permutation(self):
        state, a, b = fixture()
        expected = pair_features(state, a, b)
        state = deepcopy(state)
        rename = {'opaque_A': 'xyz_999', 'opaque_B': 'not_a_seed', 'prior': 'renamed_intro'}
        for m in state['members']:
            m['member_id'] = rename[m['member_id']]
        for intro in state['introductions']:
            for k in ('introduction_id', 'user_a', 'user_b'):
                intro[k] = rename[intro[k]]
        for e in state['feedback']:
            e['member_id'] = rename[e['member_id']]
            e['introduction_id'] = rename[e['introduction_id']]
        state['members'].reverse()
        state['feedback'].reverse()
        np.testing.assert_array_equal(expected, pair_features(state, *state['members']))

    def test_only_released_linked_prior_actor_feedback(self):
        state, a, b = fixture()
        expected = pair_features(state, a, b)
        state['introductions'].append(dict(introduction_id='current', user_a=a['member_id'],
                                          user_b=b['member_id'], assigned_day=state['day']))
        for intro, actor, day in [('prior', a['member_id'], 9),
                                  ('unknown', a['member_id'], 2),
                                  ('prior', 'outsider', 2),
                                  ('current', a['member_id'], 8)]:
            state['feedback'].append(dict(introduction_id=intro, member_id=actor,
                event='second_meeting_intention', value='no', observed_day=day))
        np.testing.assert_array_equal(expected, pair_features(state, a, b))
        names = feature_names()
        self.assertEqual(expected[names.index('introduction_response__yes_count__max')], 1)
        self.assertEqual(expected[names.index('introduction_response__yes_beta_rate__max')], 2/3)

    def test_private_keys_and_future_fields(self):
        state, a, b = fixture()
        expected = pair_features(state, a, b)
        state.update(seed=123, family='fake', variant='bad', world={'truth': 'private'})
        for m in (a, b):
            m.update(truth={'x': 1}, response_rate=0.00001, second_bias=999, seed=77)
        np.testing.assert_array_equal(expected, pair_features(state, a, b))
        a['field_observed_day'][SOFT_FIELDS[0]] = state['day'] + 1
        actual = pair_features(state, a, b)
        self.assertEqual(actual[2], 1)
        a['field_status'][SOFT_FIELDS[0]] = 'declined'
        a['field_observed_day'][SOFT_FIELDS[0]] = None
        actual = pair_features(state, a, b)
        self.assertEqual(actual[feature_names().index('soft_declined_max')], 1)

    def test_context_day_guard(self):
        state, a, b = fixture()
        context = prepare_state(state)
        state['day'] += 1
        with self.assertRaises(ValueError):
            pair_features(state, a, b, context)


class LogisticTests(unittest.TestCase):
    def test_finite_json_reproducible_and_calibrated_constant(self):
        X = np.zeros((20, 3))
        y = np.r_[np.ones(4), np.zeros(16)]
        model = fit_logistic(X, y, np.ones(20))
        self.assertEqual(json.loads(json.dumps(model, allow_nan=False)), model)
        self.assertEqual(fit_logistic(X, y), model)
        np.testing.assert_allclose(predict(model, X), .2, atol=1e-7)
        self.assertTrue(model['converged'])
        for labels in (np.zeros(20), np.ones(20)):
            p = predict(fit_logistic(X, labels), X)
            self.assertTrue(np.all((p > 0) & (p < 1)))

    def test_rare_labels_weighted_standardization_and_shapes(self):
        X = np.column_stack((np.arange(100), np.full(100, 9.)))
        y = np.zeros(100)
        y[-1] = 1
        weights = np.linspace(.1, 2, 100)
        model = fit_logistic(X, y, weights)
        self.assertAlmostEqual(model['mean'][0], np.average(X[:, 0], weights=weights))
        p = predict(model, X)
        self.assertEqual(p.shape, (100,))
        self.assertTrue(np.isfinite(p).all())
        self.assertGreater(p[-1], p[0])
        self.assertEqual(np.ndim(predict(model, X[0])), 0)
        with self.assertRaises(ValueError):
            predict(model, np.zeros((3, 9)))

    def test_malformed_prediction_asset_rejected(self):
        model = dict(mean=[0., 0.], scale=[1., 1.], coefficients=[.2, -.1], intercept=0.)
        for key, bad in (
                ('scale', [0., 1.]), ('scale', [-1., 1.]),
                ('scale', [float('nan'), 1.]), ('scale', [float('inf'), 1.]),
                ('scale', [1.]), ('mean', [0.]), ('coefficients', [.2]),
                ('coefficients', [[.2, -.1]]), ('mean', [float('nan'), 0.]),
                ('coefficients', [float('inf'), 0.]),
                ('intercept', float('inf')), ('intercept', float('nan')),
                ('intercept', [0.])):
            with self.subTest(key=key, bad=bad), self.assertRaises(ValueError):
                predict(dict(model, **{key: bad}), np.zeros((3, 2)))
        with self.assertRaises(ValueError):
            predict({}, np.zeros((3, 2)))
        np.testing.assert_allclose(predict(model, np.zeros((3, 2))), .5)

    def test_zero_weight_rows_have_no_effect_and_invalid_rejected(self):
        X = np.arange(20.).reshape(10, 2)
        y = np.arange(10) % 2
        first = fit_logistic(X, y)
        extended = fit_logistic(np.vstack((X, [1e8, 1e8])), np.r_[y, 1], np.r_[np.ones(10), 0])
        np.testing.assert_allclose(predict(first, X), predict(extended, X), atol=1e-10)
        for bad in ([-1] * 10, [0] * 10):
            with self.assertRaises(ValueError):
                fit_logistic(X, y, bad)


if __name__ == '__main__':
    unittest.main()
