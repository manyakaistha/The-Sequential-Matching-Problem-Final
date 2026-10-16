"""Unit tests for Research 7 bundle transfer safety and manifest validation (T21)."""

from pathlib import Path
import tempfile
import unittest
import zipfile

from research7.runtime.transfer import BundleTransferManager


class TestTransfer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_safe_archive(self):
        zip_path = self.root / "clean.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("data/sample.json", '{"hello": "world"}')
            zf.writestr("manifest.json", "{}")

        ok, errors = BundleTransferManager.inspect_archive_safety(zip_path)
        self.assertTrue(ok, f"Expected clean archive to pass, got: {errors}")

    def test_unsafe_path_traversal_rejected_t21(self):
        zip_path = self.root / "traversal.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("normal.txt", "fine")
            zf.writestr("../escaped.txt", "malicious payload")

        ok, errors = BundleTransferManager.inspect_archive_safety(zip_path)
        self.assertFalse(ok)
        self.assertTrue(any("path traversal" in e for e in errors))

    def test_unsafe_absolute_path_rejected_t21(self):
        zip_path = self.root / "absolute.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("/etc/evil.conf", "bad")

        ok, errors = BundleTransferManager.inspect_archive_safety(zip_path)
        self.assertFalse(ok)
        self.assertTrue(any("absolute path" in e for e in errors))

    def test_generate_manifest(self):
        bundle_dir = self.root / "my_bundle"
        bundle_dir.mkdir()
        (bundle_dir / "file1.txt").write_text("hello 1", encoding="utf-8")
        (bundle_dir / "sub").mkdir()
        (bundle_dir / "sub" / "file2.txt").write_text("hello 2", encoding="utf-8")

        manifest = BundleTransferManager.generate_manifest(bundle_dir)
        self.assertEqual(manifest["file_count"], 2)
        paths = {f["path"] for f in manifest["files"]}
        self.assertEqual(paths, {"file1.txt", "sub/file2.txt"})


if __name__ == "__main__":
    unittest.main()
