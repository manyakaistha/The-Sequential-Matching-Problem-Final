"""Independent archive boundary counterexamples; no simulator/world access."""
import copy
import gzip
import hashlib
import io
from pathlib import Path
import tarfile
import tempfile
import unittest

from research8.soft_query_followup.v3 import storage


class ArchiveAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='r8-v3-critic-')
        self.root = Path(self.temp.name).resolve()
        self.relative = 'attempts/cell/attempt'
        self.source = self.root / self.relative
        self.source.mkdir(parents=True)
        (self.source / 'capture.jsonl').write_bytes(b'{"public": true}\n' * 12)
        (self.source / 'empty').write_bytes(b'')
        self.original = {p.name: p.read_bytes() for p in self.source.iterdir()}
        self.expected = {name: hashlib.sha256(value).hexdigest() for name, value in self.original.items()}

    def tearDown(self):
        self.temp.cleanup()

    def archive(self):
        return storage.archive_attempt(self.root, self.relative, self.expected,
                                       codec='gzip', level=6)

    def replace_archive(self, manifest, members):
        archive = self.root / manifest['archive_relative_path']
        with archive.open('wb') as raw:
            with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode='w|') as tar:
                    for member, body in members:
                        tar.addfile(member, io.BytesIO(body) if member.isfile() else None)
        value = copy.deepcopy(manifest)
        value['archive_bytes'] = archive.stat().st_size
        value['archive_sha256'] = hashlib.sha256(archive.read_bytes()).hexdigest()
        return value

    def test_original_byte_roundtrip_including_empty_file(self):
        manifest = self.archive()
        storage.archive_attempt(self.root, self.relative, self.expected,
                                codec='gzip', level=6, remove_raw=True)
        self.assertFalse(self.source.exists())
        restored = storage.materialize_attempt(self.root, manifest, self.root / 'restored')
        self.assertEqual({p.name: p.read_bytes() for p in restored.iterdir()}, self.original)
        self.assertEqual({k: v['sha256'] for k, v in manifest['files'].items()}, self.expected)

    def test_corrupt_archive_never_deletes_original_bytes(self):
        manifest = self.archive()
        archive = self.root / manifest['archive_relative_path']
        content = bytearray(archive.read_bytes())
        content[len(content)//2] ^= 1
        archive.write_bytes(content)
        with self.assertRaises(ValueError):
            storage.archive_attempt(self.root, self.relative, self.expected,
                                    codec='gzip', level=6, remove_raw=True)
        self.assertEqual((self.source / 'capture.jsonl').read_bytes(), self.original['capture.jsonl'])

    def test_changed_or_extra_raw_file_refuses_deletion(self):
        self.archive()
        (self.source / 'new-evidence').write_bytes(b'preserve me')
        with self.assertRaises(ValueError):
            storage.archive_attempt(self.root, self.relative, self.expected,
                                    codec='gzip', level=6, remove_raw=True)
        self.assertTrue((self.source / 'new-evidence').exists())
        self.assertTrue((self.source / 'capture.jsonl').exists())

    def test_partial_raw_removal_can_resume_from_verified_archive(self):
        manifest = self.archive()
        (self.source / 'empty').unlink()
        repeated = storage.archive_attempt(self.root, self.relative, self.expected,
                                           codec='gzip', level=6, remove_raw=True)
        self.assertEqual(repeated, manifest)
        self.assertFalse(self.source.exists())
        storage.verify_archive(self.root, repeated)

    def test_source_symlink_is_rejected_without_touching_target(self):
        outside = self.root / 'outside'
        outside.write_bytes(b'keep')
        (self.source / 'linked').symlink_to(outside)
        with self.assertRaises((ValueError, OSError)):
            self.archive()
        self.assertEqual(outside.read_bytes(), b'keep')

    def test_relative_path_escape_is_rejected(self):
        for unsafe in ('../attempt', '/attempt', 'attempts/../attempt', 'attempts//attempt', 'attempts/./attempt'):
            with self.subTest(unsafe=unsafe), self.assertRaises(ValueError):
                storage.archive_attempt(self.root, unsafe, codec='gzip', level=6)

    def test_tar_path_escape_and_link_and_duplicate_fail_closed(self):
        manifest = self.archive()
        regular = tarfile.TarInfo('capture.jsonl')
        regular.size = len(self.original['capture.jsonl'])
        empty = tarfile.TarInfo('empty')
        for special in ('traversal', 'symlink', 'duplicate'):
            with self.subTest(special=special):
                extra = tarfile.TarInfo('../escaped' if special == 'traversal' else 'capture.jsonl')
                if special == 'symlink':
                    extra.type = tarfile.SYMTYPE
                    extra.linkname = '../escaped'
                bad = self.replace_archive(manifest, [(regular, self.original['capture.jsonl']),
                                                     (empty, b''), (extra, b'')])
                with self.assertRaises(ValueError):
                    storage.materialize_attempt(self.root, bad, self.root / 'bad-extraction')
                self.assertFalse((self.root / 'bad-extraction').exists())
                self.assertFalse((self.root / 'escaped').exists())

    def test_truncated_archive_refuses_verification_even_when_physical_hash_matches(self):
        manifest = self.archive()
        archive = self.root / manifest['archive_relative_path']
        content = archive.read_bytes()[:-5]
        archive.write_bytes(content)
        modified = copy.deepcopy(manifest)
        modified['archive_bytes'] = len(content)
        modified['archive_sha256'] = hashlib.sha256(content).hexdigest()
        with self.assertRaises((EOFError, OSError, ValueError)):
            storage.verify_archive(self.root, modified)

    def test_materialize_refuses_symlink_destination_ancestor(self):
        manifest = self.archive()
        actual = self.root / 'actual'
        actual.mkdir()
        (self.root / 'linked-dir').symlink_to(actual, target_is_directory=True)
        with self.assertRaises(ValueError):
            storage.materialize_attempt(self.root, manifest, self.root / 'linked-dir' / 'new')
        self.assertFalse((actual / 'new').exists())


if __name__ == '__main__':
    unittest.main()
