import base64
import tempfile
import unittest
from research7.runtime.recorder import DurableRecorder, AttemptLogger
class RecoveryTests(unittest.TestCase):
    def test_pending_exact_immutable_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            r=DurableRecorder(d); log=r.create_attempt_logger('f'); log.initialize({})
            log.persist_request(1,0,'ask',b' {"x": 1} \n')
            self.assertEqual(r.reconcile()['attempts'][0]['state'],'interrupted')
            meta=log.record_step(1,0,'ask',b' \xff',b'\xfe',None,None,None,{},'', '',0,0)
            payload=AttemptLogger.read_segment(log.segments_dir/(meta.segment_id+'.bin'))
            self.assertEqual(base64.b64decode(payload['wire_response_base64']),b'\xfe')
            with self.assertRaises(FileExistsError): log.record_step(1,0,'ask',b'',b'',None,None,None,{},'','',0,0)
            log.finalize({'valid':False},is_valid=False); r.write_commit('f',log.attempt_id,{}, {'valid':False},False)
            with self.assertRaises(FileExistsError): r.write_commit('f',log.attempt_id,{}, {},False)
            (log.segments_dir/(meta.segment_id+'.bin')).write_bytes(b'corrupt')
            with self.assertRaises(ValueError): r.get_commit('f')
