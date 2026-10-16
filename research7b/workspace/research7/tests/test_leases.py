"""Unit tests for Research 7 cell leases and duplicate quarantine (T26)."""

from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from research7.runtime.leases import LeaseManager, LeaseError


class TestLeases(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.leases_file = self.root / "leases.jsonl"
        self.mgr = LeaseManager(self.leases_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_issue_lease_and_verify(self):
        cell_key = "r7:B0:700001:cold_start:G:hash1:hash2:hash3"
        lease = self.mgr.issue_lease(cell_key, "mac-01", duration_seconds=3600)
        self.assertEqual(lease.cell_key, cell_key)
        self.assertEqual(lease.host_id, "mac-01")
        self.assertEqual(lease.generation, 1)

        # Verification passes
        self.assertTrue(self.mgr.verify_lease_for_generation(cell_key, "mac-01", 1))
        # Wrong host fails
        self.assertFalse(self.mgr.verify_lease_for_generation(cell_key, "7a", 1))
        # Wrong generation fails
        self.assertFalse(self.mgr.verify_lease_for_generation(cell_key, "mac-01", 2))

    def test_reissue_active_lease_rejected(self):
        cell_key = "cell_1"
        self.mgr.issue_lease(cell_key, "mac-01", duration_seconds=3600)
        with self.assertRaises(LeaseError) as ctx:
            self.mgr.issue_lease(cell_key, "7a", duration_seconds=3600)
        self.assertIn("actively leased", str(ctx.exception))

    def test_revocation_and_generation_increment(self):
        cell_key = "cell_2"
        lease1 = self.mgr.issue_lease(cell_key, "mac-01", duration_seconds=3600)
        self.assertEqual(lease1.generation, 1)

        rev = self.mgr.revoke_lease(cell_key, reason="test_reassignment")
        self.assertIsNotNone(rev)

        # Old worker cannot commit under revoked generation
        committed = self.mgr.commit_lease(cell_key, "mac-01", 1, "attempt_old", {})
        self.assertFalse(committed)
        self.assertEqual(len(self.mgr.quarantined_duplicates), 1)
        self.assertEqual(
            self.mgr.quarantined_duplicates[0]["reason"], "commit_attempt_under_revoked_generation"
        )

        # New lease gets incremented generation 2
        lease2 = self.mgr.issue_lease(cell_key, "7a", duration_seconds=3600)
        self.assertEqual(lease2.generation, 2)
        self.assertTrue(self.mgr.verify_lease_for_generation(cell_key, "7a", 2))

    def test_commit_and_duplicate_quarantine_t26(self):
        cell_key = "cell_3"
        lease = self.mgr.issue_lease(cell_key, "mac-01", duration_seconds=3600)

        # Valid commit
        committed = self.mgr.commit_lease(cell_key, "mac-01", 1, "attempt_valid", {"score": 10.0})
        self.assertTrue(committed)

        # Re-commit of same cell must be quarantined, never overwrite or double count
        dup_commit = self.mgr.commit_lease(cell_key, "mac-01", 1, "attempt_late_dup", {"score": 10.0})
        self.assertFalse(dup_commit)
        self.assertTrue(any(q["reason"] == "late_duplicate_already_committed" for q in self.mgr.quarantined_duplicates))


if __name__ == "__main__":
    unittest.main()
