"""Independent endpoint counterexamples; no simulator episodes or policy imports."""
import copy
import unittest

from research8.soft_query_followup.v2.metrics import compute_run_metrics


def fixture():
    intro = dict(introduction_id='i', user_a='a', user_b='b', assigned_day=59,
                 response_deadline_day=66, logging_policy='test', propensity=None)
    def event(name, member, value, occurred, observed):
        return dict(introduction_id='i', member_id=member, event=name, value=value,
                    occurred_day=occurred, observed_day=observed)
    events = [event('introduction_response', 'a', 'yes', 60, 60),
              event('introduction_response', 'b', 'yes', 61, 61),
              event('date_happened', None, True, 89, 89),
              event('second_meeting_intention', 'a', 'yes', 92, 99),
              event('second_meeting_intention', 'b', 'yes', 92, 99)]
    inventory = [dict(member_id='a', arrived_day=0), dict(member_id='b', arrived_day=59),
                 dict(member_id='c', arrived_day=60)]
    return [intro], events, inventory


class EndpointAdversarialTests(unittest.TestCase):
    def result(self, events=None, intros=None, inventory=None):
        base_intros, base_events, base_inventory = fixture()
        return compute_run_metrics(base_intros if intros is None else intros, [],
                                   feedback=base_events if events is None else events,
                                   arrived_members=base_inventory if inventory is None else inventory,
                                   observed_day=99)

    def assert_no_reward(self, events):
        try:
            result = self.result(events=events)
        except ValueError:
            return
        self.assertEqual(result['mutual_second_meeting_intention'], 0)

    def test_inclusive_timing_and_release_boundaries_and_single_dyad(self):
        result = self.result()
        self.assertEqual(result['mutual_second_meeting_intention'], 1)
        self.assertEqual(result['arrived_members'], 2)
        self.assertEqual(result['msmi_per_100_arrived_members'], 50.0)

    def test_day100_release_never_qualifies(self):
        _, events, _ = fixture()
        events[-1]['observed_day'] = 100
        self.assert_no_reward(events)

    def test_distinct_second_participants_required(self):
        _, events, _ = fixture()
        events[-1]['member_id'] = 'a'
        self.assert_no_reward(events)

    def test_distinct_first_participants_required(self):
        _, events, _ = fixture()
        events[1]['member_id'] = 'a'
        self.assert_no_reward(events)

    def test_mutual_first_acceptance_required(self):
        _, events, _ = fixture()
        events[0]['value'] = 'no'
        self.assert_no_reward(events)

    def test_date_before_assignment_never_qualifies(self):
        _, events, _ = fixture()
        events[2]['occurred_day'] = 58
        events[3]['occurred_day'] = events[4]['occurred_day'] = 58
        self.assert_no_reward(events)

    def test_second_before_date_never_qualifies(self):
        _, events, _ = fixture()
        events[-1]['occurred_day'] = 88
        self.assert_no_reward(events)

    def test_first_response_before_assignment_never_qualifies(self):
        _, events, _ = fixture()
        events[0]['occurred_day'] = 58
        self.assert_no_reward(events)

    def test_occurrence_after_release_never_qualifies(self):
        _, events, _ = fixture()
        events[0]['observed_day'] = 59
        self.assert_no_reward(events)

    def test_date_before_mutual_acceptance_never_qualifies(self):
        _, events, _ = fixture()
        events[2]['occurred_day'] = events[2]['observed_day'] = 60
        events[3]['occurred_day'] = events[4]['occurred_day'] = 62
        self.assert_no_reward(events)

    def test_yes_with_no_response_reason_never_qualifies(self):
        _, events, _ = fixture()
        events[-1]['missing_reason'] = 'no_response'
        self.assert_no_reward(events)

    def test_conflicting_dates_never_qualify(self):
        _, events, _ = fixture()
        conflict = copy.deepcopy(events[2])
        conflict['value'] = False
        events.append(conflict)
        self.assert_no_reward(events)

    def test_orphan_event_rejected(self):
        _, events, _ = fixture()
        orphan = copy.deepcopy(events[0])
        orphan['introduction_id'] = 'orphan'
        events.append(orphan)
        with self.assertRaises(ValueError):
            self.result(events=events)

    def test_duplicate_late_inventory_id_rejected(self):
        _, _, inventory = fixture()
        inventory.append(copy.deepcopy(inventory[-1]))
        with self.assertRaises(ValueError):
            self.result(inventory=inventory)


if __name__ == '__main__':
    unittest.main()
