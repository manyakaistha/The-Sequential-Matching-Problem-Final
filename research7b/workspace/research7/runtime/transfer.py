"""Bundle transfer packaging and safety verification according to MERGE_PROTOCOL.md."""

from dataclasses import dataclass
import hashlib
import json
import os
import stat
from pathlib import Path
import tarfile
from typing import Any, Dict, List, Optional, Set, Tuple
import zipfile


class TransferSecurityError(Exception):
    pass


class BundleTransferManager:
    """Creates and safely validates immutable research transfer bundles without path traversal or overlays."""

    @staticmethod
    def compute_sha256(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    @classmethod
    def generate_manifest(cls, bundle_dir: Path) -> Dict[str, Any]:
        """Generates bundle_manifest.json indexing every file in bundle_dir."""
        bundle_dir = Path(bundle_dir)
        files = []
        for p in sorted(bundle_dir.rglob("*")):
            if p.is_symlink():
                raise TransferSecurityError(f"Symlink forbidden in bundle: {p}")
            if p.is_file() and p.name not in {"bundle_manifest.json", "bundle_manifest.sha256"}:
                rel = p.relative_to(bundle_dir).as_posix()
                b = p.stat().st_size
                sha = cls.compute_sha256(p)
                files.append({"path": rel, "bytes": b, "sha256": sha})

        return {
            "schema_version": 1,
            "bundle_dir": bundle_dir.name,
            "file_count": len(files),
            "files": files,
        }

    @classmethod
    def inspect_archive_safety(
        cls,
        archive_path: Path,
        max_bytes: int = 10 * 1024 * 1024 * 1024,
    ) -> Tuple[bool, List[str]]:
        """Statically inspects a zip/tar archive for path traversal (..), absolute paths,

        symlink escapes, duplicate paths, and decompression bombs (T21).
        """
        archive_path = Path(archive_path)
        errors = []
        if not archive_path.is_file():
            return False, [f"Archive does not exist: {archive_path}"]

        seen_paths: Set[str] = set()
        total_uncompressed = 0

        if zipfile.is_zipfile(archive_path):
            with zipfile.ZipFile(archive_path, "r") as zf:
                for info in zf.infolist():
                    name = info.filename
                    if stat.S_ISLNK(info.external_attr >> 16):
                        errors.append(f"Unsafe link/symlink in archive: {name}")
                    if name.startswith("/") or name.startswith("\\"):
                        errors.append(f"Unsafe absolute path in archive: {name}")
                    parts = Path(name).parts
                    if ".." in parts:
                        errors.append(f"Unsafe path traversal (..) in archive: {name}")
                    if name in seen_paths:
                        errors.append(f"Duplicate path in archive: {name}")
                    seen_paths.add(name)
                    total_uncompressed += info.file_size
                    if total_uncompressed > max_bytes:
                        errors.append(f"Decompression bomb threshold exceeded: {total_uncompressed} > {max_bytes}")
                        break
        elif tarfile.is_tarfile(archive_path):
            with tarfile.open(archive_path, "r:*") as tf:
                for member in tf.getmembers():
                    name = member.name
                    if name.startswith("/") or name.startswith("\\"):
                        errors.append(f"Unsafe absolute path in archive: {name}")
                    if ".." in Path(name).parts:
                        errors.append(f"Unsafe path traversal (..) in archive: {name}")
                    if member.issym() or member.islnk():
                        errors.append(f"Unsafe link/symlink in archive: {name} -> {member.linkname}")
                    if name in seen_paths:
                        errors.append(f"Duplicate path in archive: {name}")
                    seen_paths.add(name)
                    total_uncompressed += member.size
                    if total_uncompressed > max_bytes:
                        errors.append(f"Decompression bomb threshold exceeded: {total_uncompressed} > {max_bytes}")
                        break
        else:
            errors.append("Unsupported archive format (expected .zip or .tar.*)")

        return len(errors) == 0, errors
