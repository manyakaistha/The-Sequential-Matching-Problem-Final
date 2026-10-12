"""Package or restore unchanged raw research outputs with SHA256 verification."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results/extended'
INDEX = RESULTS / 'archive_index.json'


def stream_digest(stream):
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
        h.update(chunk)
    return h.hexdigest()


def digest(path):
    with path.open('rb') as stream:
        return stream_digest(stream)


def metadata(path):
    return dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size,
                sha256=digest(path))


def build():
    archives = []
    for directory in sorted(RESULTS.glob('*_traces')):
        files = sorted(p for p in directory.rglob('*') if p.is_file())
        target = directory.with_suffix('.tar.gz')
        with target.open('wb') as output, gzip.GzipFile(fileobj=output, mode='wb',
                                                       filename='', mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode='w|') as archive:
                for path in files:
                    info = archive.gettarinfo(str(path), arcname=str(path.relative_to(ROOT)))
                    info.mtime = 0
                    info.uid = info.gid = 0
                    info.uname = info.gname = ''
                    with path.open('rb') as source:
                        archive.addfile(info, source)
        archives.append(dict(kind='tar.gz', archive=metadata(target),
                             members=[metadata(p) for p in files]))
        print(target.name, target.stat().st_size, 'bytes', flush=True)
    for name in ('audit_development_calibration', 'audit_confirmation_calibration',
                 'audit_common_cohort_calibration'):
        source = RESULTS / (name + '.json')
        target = source.with_suffix('.json.gz')
        with source.open('rb') as stream, target.open('wb') as output:
            with gzip.GzipFile(fileobj=output, mode='wb', filename='', mtime=0) as gz:
                shutil.copyfileobj(stream, gz, 1024 * 1024)
        data = json.loads(source.read_text())
        rows = data.pop('assignment_rows')
        data['archived_assignment_row_count'] = len(rows)
        data['raw_assignment_archive'] = str(target.relative_to(ROOT))
        (RESULTS / (name + '.summary.json')).write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')
        archives.append(dict(kind='json.gz', archive=metadata(target), members=[metadata(source)]))
        print(target.name, target.stat().st_size, 'bytes', flush=True)
    INDEX.write_text(json.dumps(dict(scope='Lossless archives; raw paths and bytes are unchanged.',
                                    archives=archives), indent=2) + '\n')


def restore_or_verify(restore):
    index = json.loads(INDEX.read_text())
    checked = 0
    for item in index['archives']:
        archive = ROOT / item['archive']['path']
        assert digest(archive) == item['archive']['sha256'], str(archive)
        members = {row['path']: row for row in item['members']}
        if item['kind'] == 'json.gz':
            with gzip.open(archive, 'rb') as source:
                assert stream_digest(source) == next(iter(members.values()))['sha256'], str(archive)
        else:
            names = set()
            with tarfile.open(archive, 'r:gz') as source:
                for member in source:
                    assert member.name in members and member.isfile(), member.name
                    assert member.name not in names, member.name
                    names.add(member.name)
                    with source.extractfile(member) as stream:
                        assert stream_digest(stream) == members[member.name]['sha256'], member.name
            assert names == set(members), str(archive)
        if restore and item['kind'] == 'json.gz':
            name = next(iter(members))
            target = ROOT / name
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                with gzip.open(archive, 'rb') as source, target.open('wb') as output:
                    shutil.copyfileobj(source, output, 1024 * 1024)
        elif restore:
            with tarfile.open(archive, 'r:gz') as source:
                for member in source:
                    assert member.name in members and member.isfile(), member.name
                    target = (ROOT / member.name).resolve()
                    assert target.is_relative_to(ROOT), member.name
                    if not target.exists():
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with source.extractfile(member) as stream, target.open('wb') as output:
                            shutil.copyfileobj(stream, output, 1024 * 1024)
        for name, row in members.items():
            target = ROOT / name
            assert target.stat().st_size == row['bytes'] and digest(target) == row['sha256'], name
            checked += 1
    print('Verified', len(index['archives']), 'archives and', checked, 'unchanged raw files')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('build', 'restore', 'verify'))
    args = parser.parse_args()
    if args.action == 'build':
        build()
    else:
        restore_or_verify(args.action == 'restore')


if __name__ == '__main__':
    main()
