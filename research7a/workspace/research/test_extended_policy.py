"""Production and mathematical smoke tests; uses already examined seeds only."""
import copy
import json
import math
import subprocess
import sys
import unittest
from unittest import mock
from kit import Simulator,generate,HARD
from evaluate import validate_response
from extended_policy import decide,solve,DEFAULT
from research.terminal_model import predict_funnel,equality_probabilities,response_moments,user,update_memory,integrated


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.sim=Simulator(generate(101,35));self.state=self.sim.observe()
    def request(self,phase='match',state=None,memory=None):
        return dict(phase=phase,state=state or self.state,memory=memory)
    def test_empty_and_no_edges(self):
        state=copy.deepcopy(self.state);state['members']=[]
        for phase in ('ask','match'):
            r=decide(self.request(phase,state));validate_response(r,phase)
            self.assertEqual(r['asks' if phase=='ask' else 'pairs'],[])
    def test_exhausted_budget(self):
        state=copy.deepcopy(self.state);state['ask_budget_remaining']=0
        self.assertEqual(decide(self.request('ask',state))['asks'],[])
    def test_permanent_decline(self):
        state=copy.deepcopy(self.state)
        for member in state['members']: member['field_status'][HARD[0]]='declined'
        self.assertEqual(decide(self.request('ask',state))['asks'],[])
        self.assertEqual(decide(self.request('match',state))['pairs'],[])
    def test_malformed(self):
        for request in (None,[],{},dict(phase='oops'),dict(phase='ask',state={}),dict(phase='match',state=self.state,memory={'version':2,'users':[]})):
            response=decide(request)
            self.assertIn('memory',response)
    def test_nonfinite(self):
        self.assertEqual(decide(dict(phase='ask',state={'members':[]},memory={'x':float('nan')}))['memory'],{})
    def test_strict_memory(self):
        r=decide(self.request(memory={'version':2,'irrelevant':'x'*(1024*1024)}))
        self.assertLess(len(json.dumps(r['memory']).encode()),1024*1024)
    def test_solver_failure_fallback(self):
        edges=[(.4,('a','b')),(.2,('b','c'))]
        with mock.patch.dict(sys.modules,{'networkx':None}): self.assertEqual(solve(edges),[['a','b']])
    def test_solver_interrupt(self):
        import time
        try: import networkx
        except ImportError: self.skipTest('optional networkx unavailable')
        start=time.monotonic()
        with mock.patch.object(networkx,'max_weight_matching',side_effect=lambda *a,**k:time.sleep(1)):
            self.assertEqual(solve([(.4,('a','b'))],.015),[['a','b']])
        self.assertLess(time.monotonic()-start,.2)
    def test_no_hidden_import(self):
        # Static production call chain imports public eligibility/constants only.
        from pathlib import Path
        for path in ('extended_policy.py','research/terminal_model.py'):
            source=Path(path).read_text()
            self.assertNotIn("['truth']",source);self.assertNotIn('generate(',source);self.assertNotIn('Simulator(',source)
    def test_pending_not_negative(self):
        state=copy.deepcopy(self.state);state['feedback']=[]
        state['introductions']=[dict(introduction_id='pending',user_a='a',user_b='b',assigned_day=0)]
        memory=update_memory(state,None,DEFAULT)
        self.assertEqual(memory['users'],{})
    def test_response_moment_exact_prior(self):
        first,second=response_moments(user({},'x'))
        self.assertAlmostEqual(first,.765,places=12)
        self.assertAlmostEqual(second,(.55**2+.55*.98+.98**2)/3,places=12)
    def test_probability_nested(self):
        members=self.state['members']
        a,b=members[:2]
        p=predict_funnel(a,b,self.state,{},DEFAULT)
        sequence=[p[k] for k in ('both_response','both_accept_unconditional','date_unconditional','both_second_yes_unconditional','terminal')]
        self.assertTrue(all(0<=v<=1 for v in sequence))
        self.assertEqual(sequence,sorted(sequence,reverse=True))
        self.assertAlmostEqual(p['terminal']/p['pause'],p['deadline_conditional'])
    def test_independent_preserves_marginals(self):
        values=integrated((1.,0.,1.,0.),(0.,.49,0.,.25),(0.,.49,0.,.25),0,0,True)
        independent=integrated((1.,0.,1.,0.),(0.,.49,0.,.25),(0.,.49,0.,.25),0,0,False)
        self.assertAlmostEqual(values[0],independent[0],places=4)
        self.assertGreater(values[2],independent[2])
    def test_feature_enumeration_linearity(self):
        ua=ub=(0.,.49,0.,.25)
        uncertain=integrated((.5,0.,1.,0.),ua,ub,0,0,True)
        one=integrated((1.,0.,1.,0.),ua,ub,0,0,True);zero=integrated((0.,0.,1.,0.),ua,ub,0,0,True)
        for mix,a,b in zip(uncertain,one,zero): self.assertAlmostEqual(mix,.5*(a+b),places=12)
    def test_all_query_modes_legal(self):
        for mode in ('fifo','degree','entropy','random','value','two_query'):
            sim=Simulator(generate(101,35));state=sim.observe()
            r=decide(dict(phase='ask',state=state,memory=None),dict(asks=mode,query_candidates=5,query_samples=2))
            sim.resolve_asks(r['asks'])
            r=decide(dict(phase='match',state=sim.observe(),memory=r['memory']),dict(engine='blossom'))
            sim.advance(r['pairs'])
    def test_full_trajectory_memory_protocol(self):
        memory=None
        for _ in range(60):
            for phase in ('ask','match'):
                request=dict(phase=phase,state=self.sim.observe(),memory=memory)
                self.assertLess(len(json.dumps(request).encode()),1024*1024)
                response=decide(request);validate_response(response,phase);memory=response['memory']
                self.sim.resolve_asks(response['asks']) if phase=='ask' else self.sim.advance(response['pairs'])
        for _ in range(40): self.sim.advance([])
        self.assertEqual(self.sim.day,100)
    def test_subprocess_semantic(self):
        request=self.request('ask');expected=decide(copy.deepcopy(request))
        proc=subprocess.run([sys.executable,'extended_policy.py'],input=json.dumps(request),capture_output=True,text=True,timeout=10,check=True)
        self.assertEqual(json.loads(proc.stdout),expected)
    def test_malformed_subprocess(self):
        proc=subprocess.run([sys.executable,'extended_policy.py'],input='{',capture_output=True,text=True,timeout=10,check=True)
        self.assertEqual(json.loads(proc.stdout),{'pairs':[],'memory':{}})
    def test_legal_no_learning(self):
        initial=update_memory(self.state,None,DEFAULT)
        state=copy.deepcopy(self.state);state['feedback']=[dict(introduction_id='missing',member_id='a',event='introduction_response',value='yes')]
        result=update_memory(state,copy.deepcopy(initial),dict(DEFAULT,learning=False))
        self.assertEqual(initial,result)


if __name__=='__main__': unittest.main()
