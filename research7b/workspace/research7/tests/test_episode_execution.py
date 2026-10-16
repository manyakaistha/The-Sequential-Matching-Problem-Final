"""Constructed empty worlds, never research seed generation."""
import tempfile
import unittest
from kit import VERSION
from research7.runtime.invocation import TrustedInvocation, InvocationResult
from research7.runtime.recorder import DurableRecorder
from research7.runtime.runner import run_episode

class EpisodeTests(unittest.TestCase):
    def test_full_horizon_memory(self):
        seen=[]
        def decide(request,config):
            seen.append((request['phase'],request['state']['day'],request['memory']))
            return {('asks' if request['phase']=='ask' else 'pairs'):[], 'memory':len(seen)}
        with tempfile.TemporaryDirectory() as d:
            log=DurableRecorder(d).create_attempt_logger('fixture'); log.initialize({})
            row=run_episode(log,{'seed':0,'family':'development'},TrustedInvocation(decide,{}),
                world_factory=lambda *args:{'schema_version':VERSION,'seed':0,'variant':'development','members':[]})
            self.assertTrue(row['valid'],row); self.assertEqual(row['invocation_count'],120)
            self.assertEqual(row['final_day'],100); self.assertEqual(seen[:2],[('ask',0,None),('match',0,1)])
    def test_invalid_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            r=DurableRecorder(d); log=r.create_attempt_logger('fixture'); log.initialize({})
            row=run_episode(log,{'seed':0,'family':'development'},lambda wire:InvocationResult(wire_response=b'\xff'),
                world_factory=lambda *args:{'schema_version':VERSION,'seed':0,'variant':'development','members':[]})
            self.assertFalse(row['valid']); self.assertEqual(row['invocation_count'],1)
            r.write_commit('fixture',log.attempt_id,{},row,False,row['error']); self.assertFalse(r.get_commit('fixture')['is_valid'])
