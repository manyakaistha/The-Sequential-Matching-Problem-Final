import copy
import json
from pathlib import Path
import signal
import subprocess
import sys
import time
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from evaluate import validate_response
from kit import HARD,Simulator,generate
import research_policy as rp

class PolicyTests(unittest.TestCase):
    def test_empty_and_exhausted_budget(self):
        state=dict(day=0,members=[],introductions=[],feedback=[],ask_log=[],ask_budget_remaining=0)
        for phase in ('ask','match'):
            result=rp.decide(dict(state=state,phase=phase,memory=None));validate_response(result,phase)
            self.assertEqual(result['asks' if phase=='ask' else 'pairs'],[])
    def test_permanent_declines_pruned(self):
        sim=Simulator(generate(907,30));state=sim.observe()
        for m in state['members']:m['field_status'][HARD[0]]='declined';m['fields'][HARD[0]]=None
        for phase in ('ask','match'):
            result=rp.decide(dict(state=state,phase=phase,memory=None))
            self.assertEqual(result['asks' if phase=='ask' else 'pairs'],[])
    def test_timeout_interrupts_and_restores_handler(self):
        import networkx as nx
        g=nx.Graph();g.add_edge('a','b',weight=1)
        before=signal.getsignal(signal.SIGALRM);start=time.perf_counter()
        with patch('networkx.max_weight_matching',side_effect=lambda *a,**k:time.sleep(2)):
            with self.assertRaises(rp.SolverTimeout):rp.bounded_solver(g)
        self.assertLess(time.perf_counter()-start,.9)
        self.assertEqual(signal.getsignal(signal.SIGALRM),before)
    def test_solver_exception_fallback_valid(self):
        sim=Simulator(generate(908,60));state=sim.observe();mem=rp.update(state,None,rp.DEFAULT)
        expected=rp.match_actions(state,copy.deepcopy(mem),dict(rp.DEFAULT,engine='greedy'))
        with patch('research_policy.bounded_solver',side_effect=rp.SolverTimeout):
            actual=rp.match_actions(state,copy.deepcopy(mem),rp.DEFAULT)
        self.assertEqual(actual,expected);sim.advance(actual)
    def test_official_action_validation_rollout(self):
        for variant in ('development','sparse','cold_start','delayed','shift','drift'):
            sim=Simulator(generate(907,60,'test',variant));memory=None
            for day in range(60):
                for phase in ('ask','match'):
                    result=rp.decide(dict(state=sim.observe(),phase=phase,memory=memory));validate_response(result,phase)
                    memory=json.loads(json.dumps(result['memory']))
                    self.assertLess(len(json.dumps(memory).encode()),1024*1024)
                    if phase=='ask':sim.resolve_asks(result['asks'])
                    else:sim.advance(result['pairs'])
    def test_malformed_json_cli(self):
        p=subprocess.run([sys.executable,'research_policy.py'],input='{bad',text=True,capture_output=True)
        self.assertEqual(p.returncode,0);self.assertEqual(json.loads(p.stdout),{'pairs':[],'memory':{}})
    def test_pending_not_counted_as_negative(self):
        state=dict(day=2,members=[],introductions=[dict(introduction_id='x',user_a='a',user_b='b',assigned_day=0)],feedback=[])
        mem=rp.update(state,None,rp.DEFAULT)
        self.assertEqual(mem['weights'],[-.25,.55,.5,0.,.3,-.15]);self.assertEqual(mem['users'],{})

if __name__=='__main__':unittest.main()
