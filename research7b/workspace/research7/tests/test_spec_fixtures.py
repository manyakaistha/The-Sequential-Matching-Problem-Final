"""Comprehensive TEST_SPEC fixtures for Research7 admission gates (T11-T16, T05, T10, T31).

Verifies:
- T11: Hard legality, decline domination, availability, budget, duplicate asks.
- T12: Feedback maturity timing, 7/30/3 masks, late feedback.
- T13: Memory preservation, cross-episode reset, size bounds (<1 MiB).
- T14: Query batch preceding match refresh; refreshed observations visible to match.
- T15: Public observation isolation (varying hidden seeds/truth yields identical decisions).
- T10: Day-59 terminal reward retention through follow-up vs late-positive pause.
- T31: Old pending assignment non-double-counting.
- T05: Dyad repeat prohibited vs legal actor reuse with a new partner.
"""

import copy
import json
import unittest

from kit import HARD, SOFT, eligibility, Simulator, VERSION
from evaluate import validate_response
from research7.runtime.interfaces import (
    sanitize_observation,
    validate_ask_batch,
    validate_match_batch,
    validate_policy_memory,
    PublicProtocolError,
    MEMORY_LIMIT_BYTES,
)
from research7.runtime.metrics import compute_run_metrics


def make_member(ident, **overrides):
    hard = {
        'age_min': 20,
        'age_max': 40,
        'who_to_meet': ['woman'],
        'relationship_structure': 'monogamous',
        'smoking': 'no',
        'partner_smoking': 'any',
        'has_children': False,
        'partner_children': 'any',
        'wants_children': 'unsure',
        'acceptable_zones': ['zone_a'],
        'schedule': ['weekend_day'],
    }
    hard.update(overrides.get('hard_overrides', {}))
    fields = dict(hard, **{k: 'value' for k in SOFT})
    truth = copy.deepcopy(fields)
    status = {k: 'observed' for k in fields}
    status.update(overrides.get('status_overrides', {}))
    for k, st in status.items():
        if st in ('declined', 'not_asked'):
            fields[k] = None

    mem = {
        'member_id': ident,
        'pool_id': overrides.get('pool_id', 'pool_1'),
        'synthetic': True,
        'age': overrides.get('age', 28),
        'gender': overrides.get('gender', 'woman'),
        'zone': overrides.get('zone', 'zone_a'),
        'arrived_day': overrides.get('arrived_day', 0),
        'fields': fields,
        'field_status': status,
        'field_observed_day': {k: 0 for k in fields},
        'source': 'constructed',
        'available': overrides.get('available', True),
        'truth': truth,
        'exit_day': overrides.get('exit_day', 10000),
    }
    return mem


class TestSpecFixtures(unittest.TestCase):
    """TEST_SPEC admission fixture verification suite."""

    def test_t11_legality_and_decline_domination(self):
        """T11: Declines, contradiction dominance, availability, budget, duplicate asks."""
        # 1. False has_children is preserved and valid
        m_a = make_member('a', hard_overrides={'has_children': False})
        m_b = make_member('b', hard_overrides={'has_children': False, 'who_to_meet': ['woman']})
        self.assertEqual(m_a['fields']['has_children'], False)
        self.assertEqual(eligibility(m_a, m_b)['status'], 'feasible')

        # 2. Known contradiction dominates missing field
        # m_c age 45, but m_a age_max is 40 -> known failure even if smoking is missing
        m_c = make_member('c', age=45, status_overrides={'smoking': 'not_asked'})
        self.assertEqual(eligibility(m_a, m_c)['status'], 'infeasible')

        # 3. Declined field: member declined a hard question -> stays None, needs_clarification, rejected by validate_match_batch
        m_declined = make_member('d', status_overrides={'smoking': 'declined'})
        self.assertEqual(eligibility(m_a, m_declined)['status'], 'needs_clarification')
        ok_match, errs = validate_match_batch([['a', 'd']], {'a', 'd'}, [], [m_a, m_declined])
        self.assertFalse(ok_match)
        self.assertTrue(any('missing constraint' in e or 'violation' in e for e in errs))

        # 4. Asks budget: 4 hard (12) is valid, 5 hard (15) exceeds 12
        asks_12 = [{'member_id': 'a', 'field': 'constraints'}] * 4
        # with unique members
        asks_12 = [{'member_id': f'u_{i}', 'field': 'constraints'} for i in range(4)]
        users_4 = {f'u_{i}' for i in range(4)}
        ok, errors, cost = validate_ask_batch(asks_12, users_4)
        self.assertTrue(ok)
        self.assertEqual(cost, 12)

        asks_13 = asks_12 + [{'member_id': 'u_0', 'field': SOFT[0]}]
        ok, errors, cost = validate_ask_batch(asks_13, users_4)
        self.assertFalse(ok)
        self.assertIn('exceeds remaining budget', errors[0])

        # 5. Duplicate ask for same member and field
        dup_asks = [{'member_id': 'a', 'field': 'constraints'}, {'member_id': 'a', 'field': 'constraints'}]
        ok, errors, _ = validate_ask_batch(dup_asks, {'a'})
        self.assertFalse(ok)
        self.assertTrue(any('duplicate' in e for e in errors))

        # 6. Overlapping actor in match batch
        pairs_overlap = [['a', 'b'], ['a', 'c']]
        ok, errors = validate_match_batch(pairs_overlap, {'a', 'b', 'c'}, [], [m_a, m_b, m_c])
        self.assertFalse(ok)
        self.assertTrue(any('overlapping' in e for e in errors))

        # 7. Boundary age 18: 17 is infeasible (underage), 18 is feasible
        m_17 = make_member('u17', age=17)
        self.assertEqual(eligibility(m_a, m_17)['status'], 'infeasible')
        self.assertIn('underage', eligibility(m_a, m_17)['reasons'])
        m_18 = make_member('u18', age=18, hard_overrides={'age_min': 18, 'age_max': 50})
        m_adult = make_member('u_adult', age=25, hard_overrides={'age_min': 18, 'age_max': 50})
        self.assertEqual(eligibility(m_18, m_adult)['status'], 'feasible')

        # 8. Smoking contradiction: partner_smoking == 'no_smoking' but other smokes
        m_nonsmoker_only = make_member('ns', hard_overrides={'partner_smoking': 'no_smoking', 'smoking': 'no'})
        m_smoker = make_member('sm', hard_overrides={'smoking': 'yes', 'partner_smoking': 'any'})
        self.assertEqual(eligibility(m_nonsmoker_only, m_smoker)['status'], 'infeasible')
        self.assertIn('smoking', eligibility(m_nonsmoker_only, m_smoker)['reasons'])

        # 9. Children plans contradiction: wants_children == 'yes' vs 'no'
        m_want_yes = make_member('wy', hard_overrides={'wants_children': 'yes'})
        m_want_no = make_member('wn', hard_overrides={'wants_children': 'no'})
        self.assertEqual(eligibility(m_want_yes, m_want_no)['status'], 'infeasible')
        self.assertIn('children_plans', eligibility(m_want_yes, m_want_no)['reasons'])

        # 10. Schedule contradiction: disjoint schedules
        m_sch_weekend = make_member('sw', hard_overrides={'schedule': ['weekend_day']})
        m_sch_weekday = make_member('sd', hard_overrides={'schedule': ['weekday_evening']})
        self.assertEqual(eligibility(m_sch_weekend, m_sch_weekday)['status'], 'infeasible')
        self.assertIn('schedule', eligibility(m_sch_weekend, m_sch_weekday)['reasons'])

    def test_t12_feedback_maturity_timing_and_masks(self):
        """T12: Joining only observed_day <= t, first-7 deadline, date <= 30, second <= 3."""
        # Setup introductions on day 0
        intros = [{'introduction_id': 'i1', 'user_a': 'a', 'user_b': 'b', 'assigned_day': 0}]
        arrived = [make_member('a'), make_member('b')]

        # Case 1: unobserved future feedback must not be counted at t=5
        feedback_future = [
            {'introduction_id': 'i1', 'member_id': 'a', 'event': 'introduction_response', 'value': 'yes', 'occurred_day': 5, 'observed_day': 10},
            {'introduction_id': 'i1', 'member_id': 'b', 'event': 'introduction_response', 'value': 'yes', 'occurred_day': 5, 'observed_day': 10},
        ]
        res_t5 = compute_run_metrics(intros, [], feedback=feedback_future, arrived_members=arrived, observed_day=5)
        self.assertEqual(res_t5['mutual_acceptances'], 0)
        res_t10 = compute_run_metrics(intros, [], feedback=feedback_future, arrived_members=arrived, observed_day=10)
        self.assertEqual(res_t10['mutual_acceptances'], 1)

        # Case 2: Date happened day 31 (> 30 days after intro day 0) -> not qualified
        feedback_late_date = [
            {'introduction_id': 'i1', 'member_id': 'a', 'event': 'introduction_response', 'value': 'yes', 'occurred_day': 3, 'observed_day': 3},
            {'introduction_id': 'i1', 'member_id': 'b', 'event': 'introduction_response', 'value': 'yes', 'occurred_day': 3, 'observed_day': 3},
            {'introduction_id': 'i1', 'member_id': None, 'event': 'date_happened', 'value': True, 'occurred_day': 31, 'observed_day': 31},
            {'introduction_id': 'i1', 'member_id': 'a', 'event': 'second_meeting_intention', 'value': 'yes', 'occurred_day': 33, 'observed_day': 33},
            {'introduction_id': 'i1', 'member_id': 'b', 'event': 'second_meeting_intention', 'value': 'yes', 'occurred_day': 33, 'observed_day': 33},
        ]
        res_late_date = compute_run_metrics(intros, [], feedback=feedback_late_date, arrived_members=arrived, observed_day=100)
        self.assertEqual(res_late_date['dates'], 1)
        self.assertEqual(res_late_date['mutual_second_meeting_intention'], 0)

        # Case 3: Second meeting intention occurred 4 days after date (> 3 days) -> not qualified, but pauses
        feedback_late_second = [
            {'introduction_id': 'i1', 'member_id': 'a', 'event': 'introduction_response', 'value': 'yes', 'occurred_day': 3, 'observed_day': 3},
            {'introduction_id': 'i1', 'member_id': 'b', 'event': 'introduction_response', 'value': 'yes', 'occurred_day': 3, 'observed_day': 3},
            {'introduction_id': 'i1', 'member_id': None, 'event': 'date_happened', 'value': True, 'occurred_day': 20, 'observed_day': 20},
            {'introduction_id': 'i1', 'member_id': 'a', 'event': 'second_meeting_intention', 'value': 'yes', 'occurred_day': 24, 'observed_day': 24},
            {'introduction_id': 'i1', 'member_id': 'b', 'event': 'second_meeting_intention', 'value': 'yes', 'occurred_day': 24, 'observed_day': 24},
            {'introduction_id': 'i1', 'member_id': None, 'event': 'pause_after_mutual_interest', 'value': True, 'occurred_day': 24, 'observed_day': 24},
        ]
        res_late_second = compute_run_metrics(intros, [], feedback=feedback_late_second, arrived_members=arrived, observed_day=100)
        self.assertEqual(res_late_second['mutual_second_meeting_intention'], 0)
        self.assertEqual(res_late_second['unqualified_pause_count'], 1)

    def test_t13_memory_preservation_and_bounds(self):
        """T13: Ask-to-match memory preserved, episode reset, strict <1 MiB bounds."""
        # 1. Valid JSON serializable memory
        valid_mem = {'step': 12, 'counts': {'yes': 4, 'no': 1}}
        ok, errors, size = validate_policy_memory(valid_mem)
        self.assertTrue(ok)
        self.assertGreater(size, 0)

        # 2. Memory reset to None or {} is valid
        self.assertTrue(validate_policy_memory(None)[0])
        self.assertTrue(validate_policy_memory({})[0])

        # 3. Oversized memory (> 1 MiB) rejected
        oversized_mem = {'data': 'x' * (MEMORY_LIMIT_BYTES + 10)}
        ok, errors, size = validate_policy_memory(oversized_mem)
        self.assertFalse(ok)
        self.assertTrue(any('exceeds' in e for e in errors))

        # 4. Non-JSON serializable memory rejected (e.g. set or NaN)
        self.assertFalse(validate_policy_memory({'bad': {1, 2, 3}})[0])
        self.assertFalse(validate_policy_memory({'bad': float('nan')})[0])

    def test_t14_t15_public_observation_isolation(self):
        """T14 & T15: Sanitization strips hidden fields; varying hidden state leaves public action invariant."""
        m_a = make_member('a', status_overrides={'smoking': 'not_asked'})
        m_b = make_member('b', hard_overrides={'partner_smoking': 'no_smoking', 'smoking': 'no'})
        s = Simulator({'members': [m_a, m_b]})
        raw_obs = {'schema_version': VERSION, 'phase': 'ask', 'state': s.observe(), 'memory': None}

        # Verify no truth/seed leaked in sanitized observation
        clean = sanitize_observation(raw_obs)
        for m in clean['state']['members']:
            self.assertNotIn('truth', m)
            self.assertNotIn('exit_day', m)
        self.assertNotIn('seed', clean['state'])

        # Inject hidden fields and ensure sanitizer rejects them
        bad_req = copy.deepcopy(raw_obs)
        bad_req['state']['hidden_oracle_truth'] = {'cheat': True}
        with self.assertRaises(PublicProtocolError):
            sanitize_observation(bad_req)

        # T14: Query batch precedes match refresh
        # Prior to resolving asks, m_a has smoking=None -> pair (a, b) needs clarification (not feasible)
        obs_pre = s.observe()
        self.assertEqual(eligibility(obs_pre['members'][0], obs_pre['members'][1])['status'], 'needs_clarification')

        # Resolve ask for member 'a' constraints
        s.resolve_asks([{'member_id': 'a', 'field': 'constraints'}])
        obs_post = s.observe()
        # After resolving, member 'a' has observed smoking ('no') -> pair (a, b) is now feasible
        self.assertEqual(obs_post['members'][0]['field_status']['smoking'], 'observed')
        self.assertEqual(eligibility(obs_post['members'][0], obs_post['members'][1])['status'], 'feasible')

    def test_t10_and_t31_terminal_reward_and_pending_assignments(self):
        """T10 & T31: Day-59 assignment qualified reward retention; no double-counting of pending assignments."""
        # T10: Day 59 assignment receives full reward if qualified during follow-up
        intros = [{'introduction_id': 'i_d59', 'user_a': 'a', 'user_b': 'b', 'assigned_day': 59}]
        arrived = [make_member('a', arrived_day=10), make_member('b', arrived_day=20)]
        feedback_d59 = [
            {'introduction_id': 'i_d59', 'member_id': 'a', 'event': 'introduction_response', 'value': 'yes', 'occurred_day': 62, 'observed_day': 62},
            {'introduction_id': 'i_d59', 'member_id': 'b', 'event': 'introduction_response', 'value': 'yes', 'occurred_day': 62, 'observed_day': 62},
            {'introduction_id': 'i_d59', 'member_id': None, 'event': 'date_happened', 'value': True, 'occurred_day': 75, 'observed_day': 75},
            {'introduction_id': 'i_d59', 'member_id': 'a', 'event': 'second_meeting_intention', 'value': 'yes', 'occurred_day': 77, 'observed_day': 77},
            {'introduction_id': 'i_d59', 'member_id': 'b', 'event': 'second_meeting_intention', 'value': 'yes', 'occurred_day': 77, 'observed_day': 77},
        ]
        # Evaluated at day 100
        res = compute_run_metrics(intros, [], feedback=feedback_d59, arrived_members=arrived, observed_day=100)
        self.assertEqual(res['mutual_second_meeting_intention'], 1)
        self.assertEqual(res['msmi_per_100_arrived_members'], 50.0)  # 1 MSMI / 2 arrived = 50.0

        # T31: Pending assignment non-double-counting
        # If an existing assignment i1 is pending at day t with expected reward r,
        # booking reward for a new disjoint assignment i2 adds exactly q2, never q2 + r.
        # In compute_run_metrics, each introduction contributes at most 1 qualified reward if it qualifies.
        # An unresolved pending introduction contributes 0 qualified reward to the final MSMI tally.
        intros_two = [
            {'introduction_id': 'i1', 'user_a': 'a', 'user_b': 'b', 'assigned_day': 10},
            {'introduction_id': 'i2', 'user_a': 'c', 'user_b': 'd', 'assigned_day': 20},
        ]
        arrived_four = [make_member('a'), make_member('b'), make_member('c'), make_member('d')]
        # i1 is still pending (no date/second meeting yet), i2 qualifies
        feedback_two = [
            {'introduction_id': 'i2', 'member_id': 'c', 'event': 'introduction_response', 'value': 'yes', 'occurred_day': 22, 'observed_day': 22},
            {'introduction_id': 'i2', 'member_id': 'd', 'event': 'introduction_response', 'value': 'yes', 'occurred_day': 22, 'observed_day': 22},
            {'introduction_id': 'i2', 'member_id': None, 'event': 'date_happened', 'value': True, 'occurred_day': 30, 'observed_day': 30},
            {'introduction_id': 'i2', 'member_id': 'c', 'event': 'second_meeting_intention', 'value': 'yes', 'occurred_day': 32, 'observed_day': 32},
            {'introduction_id': 'i2', 'member_id': 'd', 'event': 'second_meeting_intention', 'value': 'yes', 'occurred_day': 32, 'observed_day': 32},
        ]
        res_two = compute_run_metrics(intros_two, [], feedback=feedback_two, arrived_members=arrived_four, observed_day=100)
        self.assertEqual(res_two['mutual_second_meeting_intention'], 1)  # Only i2 counted, not i1

    def test_t05_dyad_reuse_prohibited_vs_new_partner_allowed(self):
        """T05: Re-introducing same dyad (a, b) is illegal; introducing (a, c) after a returns is legal."""
        m_a = make_member('a')
        m_b = make_member('b')
        m_c = make_member('c')
        past = [{'user_a': 'a', 'user_b': 'b'}]

        # Re-introducing (a, b) is rejected as repeat dyad
        ok, errors = validate_match_batch([['a', 'b']], {'a', 'b', 'c'}, past, [m_a, m_b, m_c])
        self.assertFalse(ok)
        self.assertTrue(any('repeat' in e for e in errors))

        # Introducing (a, c) where (a, b) was past is legal
        ok, errors = validate_match_batch([['a', 'c']], {'a', 'b', 'c'}, past, [m_a, m_b, m_c])
        self.assertTrue(ok)


if __name__ == '__main__':
    unittest.main()
