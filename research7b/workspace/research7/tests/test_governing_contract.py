"""Constructed governing simulator boundaries; no generated worlds or policy episodes."""
import copy
import unittest

from kit import HARD, SOFT, Simulator, VERSION
from evaluate import VARIANTS, validate_response
from research7.registry.schema import EXPECTED_SIX_FAMILIES
from research7.runtime.interfaces import sanitize_observation, PublicProtocolError, validate_ask_batch, validate_match_batch
from research7.runtime.metrics import compute_run_metrics


def member(ident):
    hard = dict(age_min=18, age_max=60, who_to_meet=['woman'], relationship_structure='monogamous',
                smoking='no', partner_smoking='any', has_children=False, partner_children='any',
                wants_children='unsure', acceptable_zones=['a'], schedule=['evening'])
    fields = dict(hard, **{k: 'test' for k in SOFT})
    return dict(member_id=ident, pool_id='test', synthetic=True, age=30, gender='woman', zone='a',
                arrived_day=0, fields=fields, field_status={k:'observed' for k in fields},
                field_observed_day={k:0 for k in fields}, source='constructed', available=True,
                truth=copy.deepcopy(fields), exit_day=10000)


def sim():
    # Directly constructed two-member state, not kit.generate or an empirical episode.
    return Simulator({'members':[member('a'),member('b')]})


class GoverningContract(unittest.TestCase):
    def test_families(self):
        self.assertEqual(EXPECTED_SIX_FAMILIES, list(VARIANTS))

    def test_observe_boundary_and_copy(self):
        s = sim()
        raw = dict(schema_version=VERSION, phase='ask', state=s.observe(), memory=None)
        clean = sanitize_observation(raw)
        self.assertEqual(clean, raw)
        clean['state']['members'][0]['fields']['age_min'] = 99
        self.assertEqual(raw['state']['members'][0]['fields']['age_min'],18)
        for location in ('state','member','fields','nested_value','introduction','feedback','ask'):
            bad = copy.deepcopy(raw)
            state = bad['state']
            if location == 'state': state['seed'] = 1
            elif location == 'member': state['members'][0]['truth'] = {}
            elif location == 'fields': state['members'][0]['fields']['truth'] = {}
            elif location == 'nested_value': state['members'][0]['fields']['age_min']={'truth':{}}
            elif location == 'introduction': state['introductions']=[{'truth':{}}]
            elif location == 'feedback': state['feedback']=[{'truth':{}}]
            else: state['ask_log']=[{'truth':{}}]
            with self.subTest(location=location), self.assertRaises(PublicProtocolError):
                sanitize_observation(bad)

    def test_asks_match_simulator_legality(self):
        cases = [([{'member_id':'a','field':'constraints'}], True),
                 ([{'member_id':'a','field':SOFT[0]}], True),
                 ([{'member_id':'a','field':'age_min'}], False),
                 ([{'member_id':'a','field':'constraints'}]*2, False),
                 ([{'member_id':'unknown','field':SOFT[0]}], False)]
        for asks, expected in cases:
            with self.subTest(asks=asks):
                s = sim()
                ok, _, cost = validate_ask_batch(asks, {'a','b'})
                self.assertEqual(ok, expected)
                if expected:
                    validate_response({'asks':asks,'memory':None},'ask')
                    s.resolve_asks(asks)
                    self.assertEqual(cost,s.asks_total)
                else:
                    with self.assertRaises(ValueError): s.resolve_asks(asks)
        self.assertFalse(validate_ask_batch([{'member_id':'a','field':'constraints'}], {'a'},2)[0])

    def test_match_rejects_missing_hard_and_history(self):
        state = sim().observe()
        self.assertTrue(validate_match_batch([['a','b']], {'a','b'}, [],state['members'])[0])
        validate_response({'pairs':[['a','b']], 'memory':None},'match')
        for pairs in ([['a','a']], [['a','b'],['b','a']], [[1,2]], [('a','b')]):
            self.assertFalse(validate_match_batch(pairs, {'a','b'}, [],state['members'])[0])
        self.assertFalse(validate_match_batch([['b','a']], {'a','b'},[{'user_a':'a','user_b':'b'}],state['members'])[0])
        state['members'][0]['fields']['schedule']=None
        self.assertFalse(validate_match_batch([['a','b']], {'a','b'}, [],state['members'])[0])

    def test_metrics_equal_governing_timing_boundaries(self):
        for date_delay,second_delay,expected in ((30,3,1),(31,3,0),(30,4,0)):
            with self.subTest(date_delay=date_delay,second_delay=second_delay):
                s=sim(); s.day=100
                s.introductions=[dict(introduction_id='i',user_a='a',user_b='b',assigned_day=0)]
                def event(kind,value,day,ident=None):
                    return dict(introduction_id='i',member_id=ident,event=kind,value=value,
                                occurred_day=day,observed_day=day)
                s.events=[event('introduction_response','yes',1,'a'),event('introduction_response','yes',1,'b'),
                          event('date_happened',True,date_delay),
                          event('second_meeting_intention','yes',date_delay+second_delay,'a'),
                          event('second_meeting_intention','yes',date_delay+second_delay,'b'),
                          event('pause_after_mutual_interest',True,date_delay+second_delay)]
                s.asks_total=4
                ours=compute_run_metrics(s.introductions,[{'field':'constraints'},{'field':SOFT[0]}],
                                         feedback=s.receive_feedback(), arrived_members=s.observe()['members'])
                for key,value in s.metrics().items():
                    self.assertEqual(ours[key],value,(key,ours,s.metrics()))
                self.assertEqual(ours['mutual_second_meeting_intention'],expected)
                self.assertEqual(ours['unqualified_pause_count'],1-expected)
                hidden=compute_run_metrics(s.introductions,[],feedback=s.events,arrived_members=s.observe()['members'],observed_day=0)
                self.assertEqual(hidden['mutual_second_meeting_intention'],0)

    def test_arrived59_and_missing_feedback(self):
        s=sim(); s.day=100
        s.introductions=[dict(introduction_id='i',user_a='a',user_b='b',assigned_day=0)]
        feedback=[dict(introduction_id='i',event='introduction_response',value=None,
                       missing_reason='no_response',observed_day=7,occurred_day=None)]
        arrivals=s.observe()['members']+[dict(member_id='late',arrived_day=60)]
        row=compute_run_metrics(s.introductions,[],feedback=feedback,arrived_members=arrivals)
        self.assertEqual(row['arrived_members'],2)
        self.assertEqual(row['missing_feedback'],1)
        self.assertEqual(row['coverage'],1)
        self.assertEqual(row['mutual_second_meeting_intention'],0)
