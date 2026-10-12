"""Independent protocol/legality checks; existing seed101 and constructed requests."""
import copy, json, signal, subprocess, sys, time, unittest
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import evaluate
from kit import Simulator, generate, baseline_asks, baseline_match, HARD
from research3 import policy

class Correctness(unittest.TestCase):
    def state(self):return Simulator(generate(101,200,'evaluation')).observe()
    def request(self,phase='match',state=None):return dict(phase=phase,state=state or self.state(),memory=None,schema_version='1.0.0')
    def legal(self,req,cfg):
        response=policy.decide(req,cfg);evaluate.validate_response(response,req['phase'])
        sim=Simulator(generate(101,200,'evaluation'));sim.day=req['state']['day']
        sim.members={m['member_id']:dict(m,truth=m['fields'],exit_day=10000,response_rate=.7,bias=0.,second_bias=0.) for m in copy.deepcopy(req['state']['members'])}
        sim.past={tuple(sorted((i['user_a'],i['user_b']))) for i in req['state'].get('introductions',[])}
        for m in sim.members.values():
            if not m['available']:sim.busy[m['member_id']]=10000
        if req['phase']=='ask':sim.resolve_asks(response['asks'])
        else:sim.advance(response['pairs'])
        return response
    def test_shipped_greedy_exact(self):
        for phase in ('ask','match'):
            req=self.request(phase);r=policy.decide(req,{})
            self.assertEqual(r['asks' if phase=='ask' else 'pairs'],baseline_asks(req['state']) if phase=='ask' else baseline_match(req['state']))
    def test_all_candidate_actions_legal(self):
        for cfg in policy.CANDIDATES.values():
            for phase in ('ask','match'):self.legal(self.request(phase),cfg)
    def test_empty(self):
        s=self.state();s['members']=[]
        for cfg in policy.CANDIDATES.values():
            for phase in ('ask','match'):self.legal(self.request(phase,s),cfg)
    def test_permanent_declines(self):
        s=self.state()
        for m in s['members']:m['fields']['schedule']=None;m['field_status']['schedule']='declined'
        for cfg in policy.CANDIDATES.values():
            self.assertEqual(self.legal(self.request('ask',s),cfg)['asks'],[])
            self.assertEqual(self.legal(self.request('match',s),cfg)['pairs'],[])
    def test_exhausted_budget(self):
        s=self.state();s['ask_budget_remaining']=0
        for cfg in policy.CANDIDATES.values():self.assertEqual(policy.decide(self.request('ask',s),cfg)['asks'],[])
    def test_bad_memory_discarded(self):
        r=self.request();reference=policy.decide(r,{'mode':'response'})
        for mem in ('corrupt',[],{'users':'wrong'},None):
            r['memory']=mem;self.assertEqual(policy.decide(r,{'mode':'response'}),reference)
    def test_oversized_request(self):
        r=self.request();r['memory']='x'*(1024*1024+1)
        self.assertEqual(policy.decide(r),{'pairs':[],'memory':{}})
    def test_pending_feedback_is_not_failure(self):
        from research3.model_candidates import response_counts
        s=self.state();s['introductions']=[{'introduction_id':'pending','user_a':'a','user_b':'b','assigned_day':0}]
        self.assertEqual(dict(response_counts(s)),{})
        s['feedback']=[{'introduction_id':'pending','event':'introduction_response','member_id':'a','value':None,'missing_reason':'no_response'}]
        self.assertEqual(response_counts(s)['a'],[0,1])
    def test_solver_independence(self):
        # No candidate imports a general graph solver. Block any attempted import.
        import builtins
        imp=builtins.__import__
        def guarded(name,*args,**kw):
            if name.startswith('networkx'):raise ImportError('solver unavailable')
            return imp(name,*args,**kw)
        with patch('builtins.__import__',guarded):
            for cfg in policy.CANDIDATES.values():self.legal(self.request(),cfg)
    def test_actual_alarm_interruption(self):
        original=signal.setitimer
        def bounded(which,seconds,*args):return original(which,min(seconds,.025) if seconds else 0,*args)
        with patch.object(policy,'inner',side_effect=lambda *args:time.sleep(.1)),patch.object(policy.signal,'setitimer',side_effect=bounded):
            t=time.monotonic();r=policy.decide(self.request());self.assertLess(time.monotonic()-t,.09);self.assertEqual(r['pairs'],[])
    def test_subprocess_actions(self):
        for name in ('greedy','population','response','offline','goal_queries'):
            for phase in ('ask','match'):
                req=self.request(phase);direct=policy.decide(req,policy.CANDIDATES[name])
                actual,_=evaluate.invoke([sys.executable,'-m','research3.policy','--candidate',name],req)
                self.assertEqual(actual,direct)
    def test_outer_alarm_preserved(self):
        previous=signal.getsignal(signal.SIGALRM);timer=signal.getitimer(signal.ITIMER_REAL)
        try:
            signal.signal(signal.SIGALRM,lambda *_:None);signal.setitimer(signal.ITIMER_REAL,5)
            policy.decide(self.request())
            remaining=signal.getitimer(signal.ITIMER_REAL)[0]
            self.assertGreater(remaining,4)
        finally:
            signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous)
            if timer[0]:signal.setitimer(signal.ITIMER_REAL,*timer)

if __name__=='__main__':unittest.main(verbosity=2)
