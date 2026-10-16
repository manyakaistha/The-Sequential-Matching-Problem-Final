"""Lossless regular-file attempt archives (empty directory metadata is omitted). Callers must stop writers before archiving/removal.

Only regular files are supported. Original commit records are never rewritten.
Archive verification streams bounded member sizes; extraction never uses extractall.
"""
from __future__ import annotations

import contextlib
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import tarfile
import tempfile

SCHEMA = "soft-query-attempt-archive-v1"
CHUNK = 1024 * 1024


def _rel(value):
    value = str(value)
    p = PurePosixPath(value)
    if not value or p.is_absolute() or '\\' in value or any(x in ('', '.', '..') for x in value.split('/')):
        raise ValueError(f"Unsafe relative path: {value!r}")
    return p.as_posix()


def _path(root, relative):
    root = Path(root).resolve()
    relative = _rel(relative)
    p = root
    for part in relative.split('/'):
        p = p / part
        if p.is_symlink():
            raise ValueError(f"Symlink forbidden: {p}")
    return p


def _hash_file(path):
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
    if not stat.S_ISREG(os.lstat(path).st_mode):
        raise ValueError(f'Not a regular file: {path}')
    fd = os.open(path, flags | getattr(os, 'O_NONBLOCK', 0))
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise ValueError(f"Not a regular file: {path}")
        digest = hashlib.sha256()
        size = 0
        while block := stream.read(CHUNK):
            digest.update(block)
            size += len(block)
        after = os.fstat(stream.fileno())
        if (before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError(f"Source changed during read: {path}")
    return {'sha256': digest.hexdigest(), 'bytes': size}


def _inventory(source):
    if not source.is_dir() or source.is_symlink():
        raise ValueError(f"Attempt must be a regular directory: {source}")
    result = {}
    for directory, dirs, names in os.walk(source, followlinks=False):
        for name in dirs:
            p = Path(directory) / name
            if p.is_symlink():
                raise ValueError(f"Symlink forbidden: {p}")
        for name in sorted(names):
            p = Path(directory) / name
            relative = _rel(p.relative_to(source).as_posix())
            if p.is_symlink():
                raise ValueError(f'Symlink forbidden: {p}')
            result[relative] = _hash_file(p)
    return dict(sorted(result.items()))


def _expected(files, expected):
    for name, value in (expected or {}).items():
        name = _rel(name)
        if name not in files:
            raise ValueError(f"Committed file missing: {name}")
        wanted = {'sha256': value} if isinstance(value, str) else value
        if any(files[name].get(k) != v for k, v in wanted.items() if k in ('sha256', 'bytes')):
            raise ValueError(f"Committed hash/length mismatch: {name}")


def _sync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _publish(temp, final):
    # Hard-link publication cannot overwrite another writer's committed artifact.
    os.link(temp, final)
    _sync_dir(final.parent)


def _json_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def _write_json_exclusive(path, value):
    data = _json_bytes(value)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Existing catalog differs: {path}")
        return
    fd, temp = tempfile.mkstemp(prefix='.catalog-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        _publish(temp, path)
    finally:
        Path(temp).unlink(missing_ok=True)


def _compression(stream, codec, level=None, writing=False):
    mode = 'wb' if writing else 'rb'
    if codec == 'gzip':
        return gzip.GzipFile(fileobj=stream, mode=mode, **({'compresslevel': level, 'mtime': 0} if writing else {}))
    if codec == 'zstd':
        from compression import zstd
        return zstd.ZstdFile(stream, mode=mode, **({'level': level} if writing else {}))
    raise ValueError(f"Unsupported codec: {codec}")


def _validate_manifest(manifest):
    if manifest.get('schema') != SCHEMA:
        raise ValueError('Unknown archive schema')
    _rel(manifest['original_relpath'])
    if not _rel(manifest['archive_relative_path']).startswith('archives/'):
        raise ValueError('Archive must be under archives/')
    if manifest['codec'] not in ('gzip', 'zstd'):
        raise ValueError('Unknown codec')
    for name, info in manifest['files'].items():
        _rel(name)
        if not isinstance(info['bytes'], int) or info['bytes'] < 0:
            raise ValueError('Invalid member size')
        if len(info['sha256']) != 64 or any(c not in '0123456789abcdef' for c in info['sha256']):
            raise ValueError('Invalid member hash')


class _BoundedReader:
    def __init__(self, stream, limit):
        self.stream, self.remaining = stream, limit

    def read(self, size=-1):
        request = self.remaining + 1 if size < 0 else min(size, self.remaining + 1)
        block = self.stream.read(request)
        self.remaining -= len(block)
        if self.remaining < 0:
            raise ValueError('Decompressed archive exceeds recorded size bound')
        return block


def _read_members(output, manifest, destination=None):
    _validate_manifest(manifest)
    archive = _path(output, manifest['archive_relative_path'])
    if _hash_file(archive) != {'sha256': manifest['archive_sha256'], 'bytes': manifest['archive_bytes']}:
        raise ValueError('Archive hash/length mismatch')
    seen = set()
    with archive.open('rb') as raw, _compression(raw, manifest['codec']) as compressed:
        limit = 32768 + sum(info['bytes'] + 8192 + len(name.encode()) * 2 for name, info in manifest['files'].items())
        bounded = _BoundedReader(compressed, limit)
        with tarfile.open(fileobj=bounded, mode='r|') as tar:
            for member in tar:
                name = _rel(member.name)
                if not member.isfile() or name in seen or name not in manifest['files']:
                    raise ValueError(f"Unexpected/unsafe archive member: {name}")
                info = manifest['files'][name]
                if member.size != info['bytes']:
                    raise ValueError(f"Member length mismatch: {name}")
                seen.add(name)
                target = None
                if destination is not None:
                    target_path = _path(destination, name)
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    target = target_path.open('xb')
                digest, size = hashlib.sha256(), 0
                with contextlib.ExitStack() as stack:
                    if target is not None:
                        stack.enter_context(target)
                    stream = stack.enter_context(tar.extractfile(member))
                    while block := stream.read(min(CHUNK, info['bytes'] - size + 1)):
                        size += len(block)
                        if size > info['bytes']:
                            raise ValueError('Oversized member')
                        digest.update(block)
                        if target is not None:
                            target.write(block)
                    if target is not None:
                        target.flush()
                        os.fsync(target.fileno())
                if size != info['bytes'] or digest.hexdigest() != info['sha256']:
                    raise ValueError(f"Member hash mismatch: {name}")
        # Require decompressor to consume its trailer and expose truncation errors.
        while block := bounded.read(CHUNK):
            if block.strip(b'\0'):
                raise ValueError('Nonzero trailing archive data')
    if seen != set(manifest['files']):
        raise ValueError('Archive members missing')
    return manifest


def verify_archive(output, manifest):
    """Verify physical archive checksum and every logical original file."""
    return _read_members(output, manifest)


def materialize_attempt(output, manifest, destination):
    """Materialize one attempt to a new directory; remove partial output on failure."""
    import shutil
    destination = Path(destination)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    # Reject caller-created symlink ancestors, permitting only macOS system aliases.
    for ancestor in destination.absolute().parents:
        if ancestor.is_symlink() and str(ancestor) not in ('/var', '/tmp', '/etc'):
            raise ValueError('Symlink destination ancestry')
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Resolve system aliases such as /var after checking caller-created ancestors.
    destination = destination.parent.resolve() / destination.name
    destination.mkdir()
    try:
        _read_members(output, manifest, destination)
        _sync_dir(destination)
    except BaseException:
        shutil.rmtree(destination)
        raise
    return destination


def _remove_raw(source, files):
    if not source.exists():
        return
    actual = _inventory(source)
    if any(name not in files or info != files[name] for name, info in actual.items()):
        raise ValueError('Raw source changed; refusing removal')
    for name, info in actual.items():
        p = _path(source, name)
        if _hash_file(p) != info:
            raise ValueError('Raw source changed during removal')
        p.unlink()
        _sync_dir(p.parent)
    for directory, dirs, names in os.walk(source, topdown=False):
        Path(directory).rmdir()
    _sync_dir(source.parent)


def archive_attempt(output, attempt_relative_path, expected_hashes=None, codec='zstd', level=3, remove_raw=False):
    """Archive a quiescent attempt and durably catalog it before optional deletion.

    Existing valid catalogs allow retries after partial or complete raw removal.
    expected_hashes maps paths within the attempt to hashes or {sha256, bytes}.
    """
    output = Path(output).resolve()
    relative = _rel(attempt_relative_path)
    if relative.split('/')[0] in ('archives', 'archive_manifests'):
        raise ValueError('Attempt cannot be inside storage metadata')
    source = _path(output, relative)
    key = hashlib.sha256(relative.encode()).hexdigest()
    archive_dir = _path(output, 'archives')
    catalog_dir = _path(output, 'archive_manifests')
    archive_dir.mkdir(parents=True, exist_ok=True)
    catalog_dir.mkdir(parents=True, exist_ok=True)
    objects = _path(output, 'archive_manifests/objects')
    objects.mkdir(exist_ok=True)
    catalog = catalog_dir / (key + '.json')
    with (catalog_dir / (key + '.lock')).open('a+b') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if catalog.exists():
            manifest = json.loads(catalog.read_text())
            if manifest['original_relpath'] != relative:
                raise ValueError('Catalog logical path mismatch')
            verify_archive(output, manifest)
            _expected(manifest['files'], expected_hashes)
            if source.exists():
                actual = _inventory(source)
                if any(name not in manifest['files'] or value != manifest['files'][name] for name, value in actual.items()):
                    raise ValueError('Source differs from archived attempt')
            if remove_raw:
                _remove_raw(source, manifest['files'])
            return manifest
        files = _inventory(source)
        _expected(files, expected_hashes)
        suffix = {'zstd': '.tar.zst', 'gzip': '.tar.gz'}.get(codec)
        if suffix is None:
            raise ValueError('Unsupported codec')
        archive = archive_dir / (key + suffix)
        if not archive.exists():
            fd, temp = tempfile.mkstemp(prefix='.archive-', dir=archive_dir)
            try:
                with os.fdopen(fd, 'wb') as raw:
                    with _compression(raw, codec, level, writing=True) as compressed:
                        with tarfile.open(fileobj=compressed, mode='w|', format=tarfile.PAX_FORMAT) as tar:
                            for name, info in files.items():
                                member = tarfile.TarInfo(name)
                                member.size = info['bytes']
                                member.mode = 0o600
                                with _path(source, name).open('rb') as stream:
                                    tar.addfile(member, stream)
                    raw.flush()
                    os.fsync(raw.fileno())
                if _inventory(source) != files:
                    raise ValueError('Source changed during archive creation')
                _publish(temp, archive)
            finally:
                Path(temp).unlink(missing_ok=True)
        physical = _hash_file(archive)
        manifest = {'schema': SCHEMA, 'original_relpath': relative, 'files': files,
                    'archive_relative_path': archive.relative_to(output).as_posix(),
                    'archive_sha256': physical['sha256'], 'archive_bytes': physical['bytes'],
                    'codec': codec, 'level': level}
        verify_archive(output, manifest)
        if _inventory(source) != files:
            raise ValueError('Source changed before catalog publication')
        object_hash = hashlib.sha256(_json_bytes(manifest)).hexdigest()
        _write_json_exclusive(objects / (object_hash + '.json'), manifest)
        _write_json_exclusive(catalog, manifest)
        if remove_raw:
            _remove_raw(source, files)
        return manifest
