"""Production amendment tests; deliberately separate from frozen efficacy tests."""
import copy
import importlib
import os
import threading
import time
import unittest
from unittest import mock
safe=importlib.import_module('extended_policy' if os.environ.get('EXTENDED_SAFETY_TEST_TARGET')=='actual' else 'research.extended_policy_safe')
from research.extended_stress import request
from kit import Simulator,generate,HARD
frozen=importlib.import_module('research.extended_policy_development' if os.environ.get('EXTENDED_SAFETY_TEST_TARGET')=='actual' else 'extended_policy').decide


class SafetyTests(unittest.TestCase):
    def test_arithmetic_memory(self):
        r=request(n=4);r['memory']['date_counts']=[0.,0.]
        out=safe.decide(r);self.assertEqual(out['memory'],{});self.assertEqual(len(out['pairs']),2)
    def test_zero_actor_precision(self):
        r=request(n=4);r['memory']['users']['stress_0000'][3]=0.
        out=safe.decide(r);self.assertEqual(out['memory'],{});self.assertEqual(len(out['pairs']),2)
    def test_global_timer(self):
        r=request(n=20)
        with mock.patch.object(safe,'INVOCATION_SECONDS',.02),mock.patch.object(safe,'predict_funnel',side_effect=lambda *a,**k:time.sleep(1)):
            start=time.monotonic();out=safe.decide(r)
            self.assertLess(time.monotonic()-start,.15);self.assertEqual(len(out['pairs']),10);self.assertEqual(out['memory'],{})
    def test_nested_solver_deadline(self):
        import networkx
        r=request(n=6,diverse=False)
        with mock.patch.object(safe,'INVOCATION_SECONDS',.02),mock.patch.object(networkx,'max_weight_matching',side_effect=lambda *a,**k:time.sleep(1)):
            start=time.monotonic();out=safe.decide(r,{'engine':'blossom'})
            self.assertLess(time.monotonic()-start,.15);self.assertEqual(out['memory'],{})
    def test_missing_signal(self):
        r=request(n=6)
        with mock.patch.object(safe.signal,'setitimer',None):
            del safe.signal.setitimer
            out=safe.decide(r);self.assertEqual(len(out['pairs']),3);self.assertEqual(out['memory'],{})
    def test_thread_no_signal_fallback(self):
        rows=[];errors=[]
        def run():
            try: rows.append(safe.decide(request(n=6)))
            except BaseException as e: errors.append(str(e))
        thread=threading.Thread(target=run);thread.start();thread.join(timeout=2)
        self.assertEqual(errors,[]);self.assertEqual(len(rows[0]['pairs']),3);self.assertEqual(rows[0]['memory'],{})
    def test_normal_equivalence(self):
        sim=Simulator(generate(1001,35));a=None;b=None
        for _ in range(60):
            for phase in ('ask','match'):
                r=dict(phase=phase,state=sim.observe(),memory=a);x=frozen(copy.deepcopy(r))
                r['memory']=b;y=safe.decide(r);self.assertEqual(x,y);a=x['memory'];b=y['memory']
                sim.resolve_asks(x['asks']) if phase=='ask' else sim.advance(x['pairs'])
    def test_ask_fallback(self):
        r=request(n=20,incomplete=10);r['phase']='ask'
        with mock.patch.object(safe,'INVOCATION_SECONDS',.02),mock.patch.object(safe,'ask_actions',side_effect=lambda *a,**k:time.sleep(1)):
            out=safe.decide(r);self.assertEqual(len(out['asks']),4);self.assertEqual(out['memory'],{})
        r['state']['members'][0]['field_status'][HARD[0]]='declined'
        out=safe.fallback(r);self.assertNotIn('stress_0000',[a['member_id'] for a in out['asks']])
        r['state']['ask_budget_remaining']=0;self.assertEqual(safe.fallback(r)['asks'],[])
    def test_past_and_unavailable_fallback(self):
        r=request(n=6);r['state']['members'][0]['available']=False
        r['state']['introductions']=[dict(user_a='stress_0001',user_b='stress_0002')]
        out=safe.fallback(r);pairs={tuple(p) for p in out['pairs']}
        self.assertNotIn(('stress_0001','stress_0002'),pairs)
        self.assertTrue(all('stress_0000' not in p for p in pairs))


if __name__=='__main__': unittest.main()
