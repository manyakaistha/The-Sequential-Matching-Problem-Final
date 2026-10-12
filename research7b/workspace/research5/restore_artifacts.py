"""Verify archives without raw originals; restore through symlink-refusing dirfds.

Use a trusted archive_index.json and final manifest. No extraction can overwrite
an existing file. The destination root itself and every traversed child directory
and file are opened with O_NOFOLLOW. No safety claim against arbitrary concurrent
filesystem tampering or a compromised operating system is made.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tarfile

from research5.archive_results import safe, sha


def hash_stream(stream):
    digest = hashlib.sha256()
    size = 0
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        digest.update(block); size += len(block)
    return size, digest.hexdigest()


def verify_archives(index):
    count = 0
    for record in index['archives']:
        assert sha(record['path']) == record['sha256']
        expected = {r['path']: r for r in record['members']}
        assert len(expected) == len(record['members'])
        seen = set()
        with tarfile.open(record['path'], 'r:*') as archive:
            for member in archive:
                safe(member.name)
                assert member.isfile() and member.name in expected and member.name not in seen
                seen.add(member.name)
                with archive.extractfile(member) as stream:
                    size, digest = hash_stream(stream)
                assert size == expected[member.name]['bytes'] and digest == expected[member.name]['sha256']
                count += 1
        assert seen == set(expected)
    return count


def write_member(root_fd, relative, stream, expected):
    """All directory opens are relative to trusted fds, with symlinks refused."""
    parts = safe(relative).parts
    parent = os.dup(root_fd)
    try:
        for component in parts[:-1]:
            try:
                os.mkdir(component, dir_fd=parent)
            except FileExistsError:
                pass
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            os.close(parent); parent = child
        leaf = parts[-1]
        try:
            fd = os.open(leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600, dir_fd=parent)
        except FileExistsError:
            fd = os.open(leaf, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
            with os.fdopen(fd, 'rb') as existing:
                size, digest = hash_stream(existing)
            assert size == expected['bytes'] and digest == expected['sha256'], 'Existing differing bytes'
            return False
        with os.fdopen(fd, 'wb') as output:
            digest = hashlib.sha256(); size = 0
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                output.write(block); digest.update(block); size += len(block)
        assert size == expected['bytes'] and digest.hexdigest() == expected['sha256']
        return True
    finally:
        os.close(parent)


def restore(index, destination, only=None):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    root_fd = os.open(destination, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    restored = 0
    try:
        for record in index['archives']:
            expected = {r['path']: r for r in record['members']}
            assert len(expected) == len(record['members'])
            wanted = set(expected) if only is None else set(expected) & only
            if not wanted:
                continue
            assert sha(record['path']) == record['sha256']
            seen = set()
            with tarfile.open(record['path'], 'r:*') as archive:
                for member in archive:
                    safe(member.name)
                    assert member.isfile() and member.name in expected and member.name not in seen
                    seen.add(member.name)
                    if member.name in wanted:
                        with archive.extractfile(member) as stream:
                            restored += write_member(root_fd, member.name, stream, expected[member.name])
                    if only is not None and wanted <= seen:
                        break
            assert wanted <= seen if only is not None else seen == set(expected)
    finally:
        os.close(root_fd)
    return restored


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('verify', 'restore'))
    parser.add_argument('--index', default='results/research5/archive_index.json')
    parser.add_argument('--destination', default='.')
    args = parser.parse_args()
    index = json.loads(Path(args.index).read_text())
    if args.action == 'verify':
        print('Verified archive-only members:', verify_archives(index))
    else:
        print('Restored missing files:', restore(index, args.destination))


if __name__ == '__main__':
    main()
