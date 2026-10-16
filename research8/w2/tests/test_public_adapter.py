from copy import deepcopy
import json
import sys
import unittest
from research8.w2.public_adapter import checked_request,decide,evaluate_projection,arrival_features
from research8.w2.protocol import PublicProtocolError
from research8.w2.tests.fixtures import request,waiting_projection


class AdapterTests(unittest.TestCase):
    def test_G_fallback_exact_and_public_only(self):
        # Host comparison only; candidate runtime imports no kit/simulator.
        from kit import baseline_asks,baseline_match
        for phase in ['ask','match']:
            raw=request(20,phase,unknown=8)
            out=decide(raw)
            key='asks' if phase=='ask' else 'pairs'
            expected=baseline_asks(raw['state']) if phase=='ask' else baseline_match(raw['state'])
            self.assertEqual(out[key],expected)
            self.assertEqual(set(out),{key,'memory'})
            self.assertEqual(out['memory']['last_status']['mode'],'G_fallback')
            self.assertEqual(out['memory']['arrival_counts'],[20])

    def test_offline_declared_model_bridge_can_hold_and_revalidates(self):
        raw=request()
        out=evaluate_projection(raw,waiting_projection)
        self.assertEqual(out['pairs'],[])
        self.assertEqual(out['memory']['last_status']['mode'],'offline_declared_projection')
        self.assertEqual(raw['memory'],None)

    def test_unknown_neighbor_blocks_projection(self):
        raw=request(5)
        out=evaluate_projection(raw,waiting_projection)
        self.assertEqual(out['memory']['last_status']['reason'],'unsupported_open_current_boundary')
        raw['state']['members'][-1]['fields']['age_min']=None
        raw['state']['members'][-1]['field_status']['age_min']='not_asked'
        raw['state']['members'][-1]['field_observed_day']['age_min']=None
        out=evaluate_projection(raw,waiting_projection)
        self.assertEqual(out['memory']['last_status']['reason'],'unsupported_unresolved_current_neighbor')

    def test_reject_hidden_future_memory_and_config_injection(self):
        for key in ['truth','exit_day','busy_until','response_rate']:
            raw=request();raw['state']['members'][0][key]=0
            with self.assertRaises(PublicProtocolError):decide(raw)
        raw=request();raw['state']['seed']=1000001
        with self.assertRaises(PublicProtocolError):decide(raw)
        raw=request();raw['memory']={'ready':[['A',8]]}
        with self.assertRaises(PublicProtocolError):decide(raw)
        with self.assertRaises(PublicProtocolError):decide(request(),{'model':{'future_arrivals':[]}})
        raw=request();raw['state']['members'][0]['field_observed_day']['age_min']=1
        with self.assertRaises(PublicProtocolError):decide(raw)
        raw=request();raw['state']['members'][0]['field_status']['age_min']='not_asked'
        with self.assertRaises(PublicProtocolError):decide(raw)

    def test_counts_idempotent_across_phases_and_unavailable(self):
        raw=request(4,day=2)
        raw['state']['members'][0]['arrived_day']=2
        a=decide(raw)
        raw['phase']='ask';raw['memory']=a['memory'];raw['state']['members'][0]['available']=False
        b=decide(raw)
        self.assertEqual(a['memory']['arrival_counts'],[3,0,1])
        self.assertEqual(a['memory']['arrival_counts'],b['memory']['arrival_counts'])
        self.assertEqual(a['memory']['member_count'],b['memory']['member_count'])

    def test_projection_cannot_mutate_public_boundary_or_clock(self):
        from dataclasses import replace
        raw=request()
        def mutating(public):
            public['state']['members'][0]['fields']['age_min']=80
            return waiting_projection(public)
        out=evaluate_projection(raw,mutating)
        self.assertEqual(out['pairs'],[])
        self.assertEqual(raw['state']['members'][0]['fields']['age_min'],18)
        def wrong_day(public):
            p=waiting_projection(public)
            return replace(p,prior=replace(p.prior,day=1))
        with self.assertRaises(PublicProtocolError):evaluate_projection(raw,wrong_day)
        def outside_touch(public):
            p=waiting_projection(public)
            return replace(p,outside_pairs=(('m_000','m_001'),))
        with self.assertRaises(PublicProtocolError):evaluate_projection(raw,outside_touch)
        raw['state']['introductions']=[dict(introduction_id='old',user_a='m_000',user_b='m_001',assigned_day=0,response_deadline_day=7,logging_policy='test',propensity=None)]
        with self.assertRaises(PublicProtocolError):evaluate_projection(raw,waiting_projection)

    def test_metadata_cannot_hide_private_maps(self):
        for key in ['source','pool_id','gender','zone']:
            raw=request();raw['state']['members'][0][key]={'truth':{'seed':10}}
            with self.assertRaises(PublicProtocolError):decide(raw)

    def test_projection_prior_cap_returns_valid_G(self):
        from dataclasses import replace
        from fractions import Fraction as F
        from research8.planner import Belief
        from research8.w2.bounded import BoundedConfig
        def provider(public):
            p=waiting_projection(public)
            return replace(p,prior=Belief(((F(1,2),p.prior),(F(1,2),p.prior))))
        out=evaluate_projection(request(),provider,BoundedConfig(max_joint_branches=1))
        self.assertEqual(out['memory']['last_status']['mode'],'G_fallback')
        self.assertEqual(out['memory']['last_status']['reason'],'unsupported_projection_prior_cap')

    def test_large_public_state_and_declined_hard(self):
        raw=request(200,'ask',unknown=20)
        m=raw['state']['members'][0];m['field_status']['age_min']='declined';m['field_observed_day']['age_min']=None
        out=decide(raw)
        self.assertEqual(len(out['asks']),4)
        self.assertNotIn(m['member_id'],[a['member_id'] for a in out['asks']])
        self.assertLess(len(json.dumps(out).encode()),1024**2)
        raw['state']['members'].append(deepcopy(raw['state']['members'][-1]))
        with self.assertRaises(PublicProtocolError):decide(raw)


if __name__=='__main__':unittest.main()
