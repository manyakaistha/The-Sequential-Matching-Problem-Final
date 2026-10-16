"""Strict wire shape and memory checks, complemented by simulator boundary tests."""
import unittest
from research7.runtime.interfaces import validate_ask_batch, validate_policy_memory, MEMORY_LIMIT_BYTES


class RuntimeInterfaceTests(unittest.TestCase):
    def test_reject_invented_asks(self):
        for asks in ([[1,'hard_bundle']], [{'member_id':1,'field':'constraints'}],
                     [{'member_id':'a','field':'hard_bundle'}],
                     [{'member_id':'a','field':'constraints','cost':3}]):
            self.assertFalse(validate_ask_batch(asks,{'a'})[0])

    def test_memory(self):
        self.assertEqual(validate_policy_memory(None),(True,[],4))
        self.assertTrue(validate_policy_memory({'history':[1,2]})[0])
        for value in (float('nan'), {'x':set()}, {'x':'a'*(MEMORY_LIMIT_BYTES+1)}):
            self.assertFalse(validate_policy_memory(value)[0])
