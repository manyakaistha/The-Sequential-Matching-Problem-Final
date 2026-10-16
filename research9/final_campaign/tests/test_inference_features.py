"""Reference-equivalence tests on declared public fixtures, no simulator runs."""
from copy import deepcopy
from itertools import combinations
import unittest

import numpy as np

from research9.final_campaign import features, inference_features


def declared_state(count=24):
    fields = features.SOFT_FIELDS
    members = []
    for index in range(count):
        statuses, values, times = {}, {}, {}
        for j, name in enumerate(fields):
            status = ('observed', 'declined', 'not_asked', 'observed')[(index + j) % 4]
            statuses[name] = status
            values[name] = ('category_A', 'category_B', 'category_C')[(index + j) % 3] if status == 'observed' else None
            times[name] = (12 if (index + j) % 7 == 0 else 0) if status == 'observed' else None
        members.append(dict(member_id=f'opaque_actor_{index * 773}', age=20 + index % 40,
                            arrived_day=index % 10, fields=values, field_status=statuses,
                            field_observed_day=times))
    introductions, feedback = [], []
    for index in range(0, count - 1, 2):
        a, b = members[index:index + 2]
        intro_id = f'opaque_intro_{index}'
        introductions.append(dict(introduction_id=intro_id, user_a=a['member_id'],
                                  user_b=b['member_id'], assigned_day=0))
        for kind in ('introduction_response', 'second_meeting_intention'):
            for offset, member in enumerate((a, b)):
                feedback.append(dict(introduction_id=intro_id, member_id=member['member_id'],
                    event=kind, value=('yes', 'no', None)[(index + offset) % 3],
                    observed_day=11 if index % 6 == 0 else 7))
    return dict(day=10, members=members, introductions=introductions, feedback=feedback)


class InferenceFeaturesTests(unittest.TestCase):
    def assert_reference(self, state, pairs):
        context = features.prepare_state(state)
        expected = features.batch_pair_features(state, pairs, context)
        actual = inference_features.batch_pair_features(state, iter(pairs), context)
        self.assertEqual(actual.dtype, np.dtype('float64'))
        self.assertEqual(actual.shape, expected.shape)
        np.testing.assert_allclose(actual, expected, atol=1e-12, rtol=0)
        return actual

    def test_all_pairs_varied_statuses_future_releases_and_histories(self):
        state = declared_state()
        pairs = list(combinations(state['members'], 2))
        actual = self.assert_reference(state, pairs)
        swapped = self.assert_reference(state, [(b, a) for a, b in reversed(pairs)])
        np.testing.assert_array_equal(actual, swapped[::-1])

    def test_empty_single_actor_and_repeated_record_copies(self):
        for count in (0, 1, 2, 9):
            state = declared_state(count)
            self.assert_reference(state, list(combinations(state['members'], 2)))
        state = declared_state(2)
        a, b = state['members']
        self.assert_reference(state, [(a, b), (deepcopy(a), deepcopy(b)), (b, a)])

    def test_default_context_zero_histories_and_opaque_identifiers(self):
        state = declared_state(12)
        state['feedback'] = []
        for index, member in enumerate(state['members']):
            member['member_id'] = ('arbitrary', index)
        pairs = list(combinations(state['members'], 2))
        self.assert_reference(state, pairs)
        np.testing.assert_array_equal(
            inference_features.batch_pair_features(state, pairs),
            features.batch_pair_features(state, pairs))

    def test_stale_context_and_nonfinite_public_age_rejected(self):
        state = declared_state(2)
        pairs = [tuple(state['members'])]
        context = features.prepare_state(state)
        state['day'] += 1
        with self.assertRaises(ValueError):
            inference_features.batch_pair_features(state, pairs, context)
        state['members'][0]['age'] = float('nan')
        with self.assertRaises(ValueError):
            inference_features.batch_pair_features(state, pairs)


if __name__ == '__main__':
    unittest.main()
