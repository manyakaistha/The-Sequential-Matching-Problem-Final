"""Lossless archives for every raw trace/log, including interrupted attempts.

Already compressed full logs use plain tar; public JSON traces use fast gzip.
Verification streams every member and exercises non-overwriting restoration.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import resource
import tarfile
import tempfile
import time

ROOT = Path('results/research5')


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def build_group(job):
    name, files, compressed = job
    target = ROOT / ('raw_' + name + ('.tar.gz' if compressed else '.tar'))
    assert not target.exists(), 'Refuse archive overwrite'
    records = [{'path': str(p), 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in files]
    mode = 'w:gz' if compressed else 'w'
    kwargs = {'compresslevel': 1} if compressed else {}
    with tarfile.open(target, mode, **kwargs) as archive:
        for path in files:
            archive.add(path, arcname=str(path), recursive=False)
    return {'path': str(target), 'bytes': target.stat().st_size,
            'sha256': sha(target), 'members': records}


def safe(path):
    path = Path(path)
    assert not path.is_absolute() and '..' not in path.parts
    assert path.parts[:2] == ('results', 'research5')
    return path


def restore(index, destination, only=None):
    """Restore under destination, refusing mismatched existing bytes."""
    destination = Path(destination)
    count = 0
    for record in index['archives']:
        expected = {r['path']: r for r in record['members']}
        wanted = set(expected) if only is None else set(expected) & only
        if not wanted:
            continue
        assert sha(record['path']) == record['sha256']
        seen = set()
        with tarfile.open(record['path'], 'r:*') as archive:
            for member in archive:
                assert member.isfile() and member.name in expected and member.name not in seen
                path = safe(member.name)
                seen.add(member.name)
                if only is not None and member.name not in only:
                    continue
                target = destination / path
                expected_record = expected[member.name]
                if target.exists():
                    assert sha(target) == expected_record['sha256'], 'Existing differing bytes: ' + str(target)
                    if only is not None and wanted <= seen:
                        break
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as source, target.open('xb') as output:
                    for block in iter(lambda: source.read(1024 * 1024), b''):
                        output.write(block)
                assert target.stat().st_size == expected_record['bytes'] and sha(target) == expected_record['sha256']
                count += 1
                if only is not None and wanted <= seen:
                    break
        assert wanted <= seen if only is not None else seen == set(expected)
    return count


def verify_group(record):
    assert sha(record['path']) == record['sha256']
    expected = {r['path']: r for r in record['members']}
    seen = set()
    with tarfile.open(record['path'], 'r:*') as archive:
        for member in archive:
            assert member.isfile() and member.name in expected and member.name not in seen
            safe(member.name)
            seen.add(member.name)
            digest = hashlib.sha256()
            size = 0
            with archive.extractfile(member) as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(block); size += len(block)
            r = expected[member.name]
            assert size == r['bytes'] and digest.hexdigest() == r['sha256']
            assert Path(member.name).stat().st_size == r['bytes'] and sha(member.name) == r['sha256']
    assert seen == set(expected)
    return len(seen)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('build', 'verify', 'restore'))
    parser.add_argument('--destination', default='.')
    args = parser.parse_args()
    index_path = ROOT / 'archive_index.json'
    start = time.perf_counter()
    cpu_start = resource.getrusage(resource.RUSAGE_CHILDREN)
    own_start = time.process_time()
    if args.action == 'build':
        assert not index_path.exists()
        trace_files, log_files = set(), set()
        for directory in ROOT.rglob('*_traces'):
            if directory.is_dir():
                trace_files.update(p for p in directory.rglob('*') if p.is_file())
        for directory in ROOT.rglob('*_traces_full'):
            if directory.is_dir():
                log_files.update(p for p in directory.rglob('*') if p.is_file())
        jobs = [(policy, sorted(p for p in trace_files if p.name.startswith(policy+'_')), True)
                for policy in ('greedy', 'population_control')]
        others = sorted(p for p in trace_files if not any(p.name.startswith(n+'_') for n in ('greedy', 'population_control')))
        if others:
            jobs.append(('other_traces', others, True))
        with ProcessPoolExecutor(max_workers=2) as pool:
            records = list(pool.map(build_group, jobs))
        records.append(build_group(('full_logs', sorted(log_files), False)))
        index = {'format': 'repository-relative regular tar members; gzip for JSON, plain tar for existing gzip logs',
                 'archives': records, 'source_sha256': sha(__file__),
                 'scope': 'All raw public traces/full logs including uncommitted interrupted files; original bytes retained.'}
        index_path.write_text(json.dumps(index, indent=2)+'\n')
        print('Built', len(records), 'lossless archives', flush=True)
    else:
        index = json.loads(index_path.read_text())
    if args.action == 'restore':
        print('Restored', restore(index, args.destination), 'missing files; differing existing bytes never overwritten')
        return
    with ProcessPoolExecutor(max_workers=2) as pool:
        count = sum(pool.map(verify_group, index['archives']))
    # Extract first member of each archive; test existing-byte and corrupt-byte behavior.
    # Full streaming verification above covers every member, not just these samples.
    selected = {r['members'][0]['path'] for r in index['archives'] if r['members']}
    with tempfile.TemporaryDirectory() as temp:
        extracted = restore(index, temp, selected)
        assert extracted == len(selected)
        assert restore(index, temp, selected) == 0
        chosen = sorted(selected)[0]
        damaged = Path(temp) / chosen
        damaged.write_bytes(b'deliberately differing restoration fixture')
        try:
            restore(index, temp, selected)
        except AssertionError as error:
            assert 'Existing differing bytes' in str(error)
        else:
            raise AssertionError('Restoration overwrote mismatched file')
    cpu_end = resource.getrusage(resource.RUSAGE_CHILDREN)
    report = {'valid': True, 'archives': len(index['archives']), 'verified_members': count,
              'sample_restored_files': extracted, 'identical_existing_skipped': True,
              'different_existing_refused': True, 'original_files_retained': True,
              'completed_utc': datetime.now(timezone.utc).isoformat(),
              'source_sha256': sha(__file__), 'index_sha256': sha(index_path),
              'wall_seconds': time.perf_counter()-start, 'own_cpu_seconds': time.process_time()-own_start,
              'child_cpu_seconds': cpu_end.ru_utime+cpu_end.ru_stime-cpu_start.ru_utime-cpu_start.ru_stime}
    target = ROOT / ('archive_build_checks.json' if args.action == 'build' else 'archive_rechecks.json')
    assert not target.exists(), 'Refuse archive check overwrite'
    target.write_text(json.dumps(report, indent=2)+'\n')
    print('Verified', count, 'members; restoration and non-overwrite checks passed', flush=True)


if __name__ == '__main__':
    main()
