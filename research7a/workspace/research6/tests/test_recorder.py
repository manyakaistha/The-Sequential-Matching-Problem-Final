"""Recorder failure retention and immutable commit checks, constructed worlds only."""
import gzip
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from research6 import recorder


class FakeSimulator:
    def __init__(self, world): self.day=0; self.introductions=[]
    def observe(self): return {'day':self.day}
    def resolve_asks(self, asks): pass
    def advance(self, pairs): self.day+=1
    def metrics(self): return {'mutual_second_meeting_intention':0,'arrived_members':200}
    def receive_feedback(self): return []


class RecorderTests(unittest.TestCase):
    def execute(self, root, decision):
        with patch.object(recorder,'generate',return_value={'schema_version':'1.0.0'}), \
             patch.object(recorder,'Simulator',FakeSimulator), \
             patch('research6.policies.policy.decide',side_effect=decision):
            return recorder.run_cell((str(root),{'policy':'G','seed':101,'family':'development'}, {'id':'G'},{}))

    def test_complete_chunks_and_no_overwrite(self):
        def decide(r,c): return {'asks' if r['phase']=='ask' else 'pairs':[], 'memory':{}}
        with tempfile.TemporaryDirectory() as temp:
            row=self.execute(temp,decide)
            self.assertTrue(row['valid']); self.assertEqual(row['invocation_count'],120)
            self.assertEqual(len(list((Path(row['attempt_path'])/'public').glob('*.request.json.gz'))),120)
            with self.assertRaises(FileExistsError): self.execute(temp,decide)
            self.assertEqual(len(list((Path(temp)/'attempts').glob('*/*/closed.json'))),2)

    def test_invalid_response_saved(self):
        def decide(r,c):
            print('captured stdout')
            import sys
            print('captured stderr',file=sys.stderr)
            return {'bad':True,'memory':{}}
        with tempfile.TemporaryDirectory() as temp:
            row=self.execute(temp,decide); self.assertFalse(row['valid'])
            path=Path(row['attempt_path'])/'public/001.response.json.gz'
            with gzip.open(path,'rt') as f: result=json.load(f)
            self.assertEqual(result['response']['bad'],True)
            self.assertIn('captured stdout',result['stdout_utf8'])
            self.assertIn('captured stderr',result['stderr_utf8'])
            self.assertTrue((Path(temp)/'commits/G_development_101.json').exists())

    def test_exception_streams_saved(self):
        def decide(r,c):
            print('before exception')
            raise RuntimeError('forced')
        with tempfile.TemporaryDirectory() as temp:
            row=self.execute(temp,decide); self.assertFalse(row['valid'])
            with gzip.open(Path(row['attempt_path'])/'public/001.inference_error.json.gz','rt') as f:
                result=json.load(f)
            self.assertIn('before exception',result['stdout_utf8'])
            self.assertIn('forced',result['error'])


if __name__=='__main__': unittest.main()
