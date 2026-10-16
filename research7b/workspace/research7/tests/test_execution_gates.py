"""Adversarial execution safeguards; no generated worlds."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
import stat
import tempfile
import unittest
import zipfile
from research7.runtime.leases import LeaseManager, LeaseError
from research7.runtime.recorder import DurableRecorder
from research7.runtime.transfer import BundleTransferManager

class ExecutionGates(unittest.TestCase):
    def test_expired_commit_quarantined_after_reload(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'leases.jsonl'
            manager = LeaseManager(path)
            lease = manager.issue_lease('cell', 'mac-01')
            lease.expires_at_utc = (datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()
            manager._append(lease)
            restored = LeaseManager(path)
            self.assertFalse(restored.commit_lease('cell', 'mac-01', 1, 'late', {}))
            self.assertNotIn('cell', restored.committed_cells)
            self.assertEqual(len(restored.quarantined_duplicates), 1)

    def test_nonpositive_duration_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = LeaseManager(Path(temp)/'leases.jsonl')
            for duration in (-1, 0, True):
                with self.assertRaises(LeaseError):
                    manager.issue_lease('cell', 'mac-01', duration)

    def test_concurrent_commit_cannot_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            recorder = DurableRecorder(Path(temp))
            def commit(i):
                try:
                    logger = recorder.create_attempt_logger('cell')
                    logger.initialize({})
                    logger.finalize({'score': i})
                    recorder.write_commit('cell', logger.attempt_id, {}, {'score': i})
                    return i
                except FileExistsError:
                    return None
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(commit, (1,2)))
            winners = [x for x in results if x is not None]
            self.assertEqual(len(winners), 1)
            self.assertEqual(recorder.get_commit('cell')['metrics']['score'], winners[0])

    def test_zip_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'escape.zip'
            with zipfile.ZipFile(path,'w') as archive:
                entry = zipfile.ZipInfo('escape'); entry.create_system = 3
                entry.external_attr = (stat.S_IFLNK | 0o777) << 16
                archive.writestr(entry,'../../outside')
            ok, errors = BundleTransferManager.inspect_archive_safety(path)
            self.assertFalse(ok)
            self.assertTrue(any('symlink' in error for error in errors))

    def test_schema_boolean_does_not_admit_empty_grid(self):
        from research7.tests.test_registry import TestRegistry
        from research7.registry.validator import RegistrationValidator
        fixture = TestRegistry(); fixture.setUp()
        try:
            reg = fixture.valid_reg.copy()
            reg['execution_authorized'] = True
            reg['authorized_scope'] = 'P1_smoke'
            ok, errors = RegistrationValidator(fixture.root).validate_executable_readiness(reg)
            self.assertFalse(ok)
            self.assertTrue(any('grid is empty' in x for x in errors))
            self.assertTrue(any('Source missing or changed' in x for x in errors))
        finally:
            fixture.tearDown()

    def test_unsafe_source_path_rejected(self):
        from research7.tests.test_registry import TestRegistry
        from research7.registry.validator import RegistrationValidator
        fixture = TestRegistry(); fixture.setUp()
        try:
            reg = fixture.valid_reg.copy(); reg['source_manifest'] = {'../outside': 'bad'}
            ok, errors = RegistrationValidator(fixture.root).validate_executable_readiness(reg)
            self.assertFalse(ok)
            self.assertTrue(any('Unsafe source path' in x for x in errors))
        finally:
            fixture.tearDown()
