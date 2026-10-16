import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('archive_storage', Path(__file__).parents[1] / 'storage.py')
storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(storage)


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.attempt = self.root / 'attempts' / 'failed-01'
        self.attempt.mkdir(parents=True)
        self.data = {'nested/raw.bin': bytes(range(256)) * 500, 'commit.json': b'{"old":true}\n', '.partial': b'', 'trace.csv': b'1,2\n'}
        for name, data in self.data.items():
            p = self.attempt / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)

    def tearDown(self):
        self.temp.cleanup()

    def archive(self, **kwargs):
        return storage.archive_attempt(self.root, 'attempts/failed-01', **kwargs)

    def test_roundtrip_both_codecs_and_exact_original_hashes(self):
        for codec, level in [('zstd', 3), ('gzip', 6)]:
            with self.subTest(codec=codec):
                other = self.root / codec
                other.mkdir()
                import shutil
                shutil.copytree(self.attempt, other / 'attempt')
                expected = {name: hashlib.sha256(data).hexdigest() for name, data in self.data.items()}
                manifest = storage.archive_attempt(other, 'attempt', expected, codec, level, True)
                self.assertFalse((other / 'attempt').exists())
                storage.verify_archive(other, manifest)
                dest = self.root / ('restored-' + codec)
                storage.materialize_attempt(other, manifest, dest)
                self.assertEqual({p.relative_to(dest).as_posix(): p.read_bytes() for p in dest.rglob('*') if p.is_file()}, self.data)
                self.assertEqual(manifest, storage.archive_attempt(other, 'attempt', expected, remove_raw=True))
                objects = list((other / 'archive_manifests/objects').glob('*.json'))
                self.assertEqual(len(objects), 1)
                self.assertEqual(objects[0].stem, hashlib.sha256(objects[0].read_bytes()).hexdigest())

    def test_expected_mismatch_preserves_source(self):
        with self.assertRaises(ValueError):
            self.archive(expected_hashes={'commit.json': '0' * 64}, remove_raw=True)
        self.assertEqual((self.attempt / 'commit.json').read_bytes(), self.data['commit.json'])
        self.assertFalse(list((self.root / 'archives').glob('*.zst')))

    def test_corruption_blocks_delete(self):
        manifest = self.archive()
        archive = self.root / manifest['archive_relative_path']
        archive.write_bytes(archive.read_bytes()[:-7])
        with self.assertRaises(ValueError):
            self.archive(remove_raw=True)
        self.assertTrue(self.attempt.exists())

    def test_repeat_after_partial_raw_removal(self):
        manifest = self.archive()
        (self.attempt / 'nested/raw.bin').unlink()
        self.assertEqual(manifest, self.archive(remove_raw=True))
        self.assertFalse(self.attempt.exists())

    def test_changed_source_blocks_removal(self):
        self.archive()
        (self.attempt / 'trace.csv').write_bytes(b'new')
        with self.assertRaises(ValueError):
            self.archive(remove_raw=True)
        self.assertEqual((self.attempt / 'trace.csv').read_bytes(), b'new')

    def test_symlinks_and_traversal_rejected(self):
        for unsafe in ['../attempts/failed-01', '/tmp/x', 'attempts//failed-01', 'attempts/./failed-01']:
            with self.assertRaises(ValueError):
                storage.archive_attempt(self.root, unsafe)
        (self.attempt / 'link').symlink_to(self.attempt / 'trace.csv')
        with self.assertRaises(ValueError):
            self.archive(remove_raw=True)
        self.assertTrue((self.attempt / 'trace.csv').exists())

    def test_orphan_archive_can_be_recovered(self):
        manifest = self.archive()
        for p in (self.root / 'archive_manifests').glob('*.json'):
            p.unlink()
        self.assertEqual(manifest, self.archive())

    def test_materialize_rejects_existing_destination(self):
        manifest = self.archive()
        with self.assertRaises(FileExistsError):
            storage.materialize_attempt(self.root, manifest, self.attempt)
        self.assertEqual((self.attempt / 'commit.json').read_bytes(), self.data['commit.json'])

    def test_empty_attempt(self):
        empty = self.root / 'empty'
        empty.mkdir()
        manifest = storage.archive_attempt(self.root, 'empty', remove_raw=True)
        self.assertEqual(manifest['files'], {})
        self.assertFalse(empty.exists())
        storage.materialize_attempt(self.root, manifest, self.root / 'restored-empty')


if __name__ == '__main__':
    unittest.main()
