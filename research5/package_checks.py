"""Final verification gate. Never modifies frozen registration or prior studies."""
from datetime import datetime, timezone
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import time

from research5.launch import verify_registration
from research5.run_test import check

ROOT = Path('results/research5')
_HASH_CACHE = {}


def sha(path):
    path = Path(path)
    stat = path.stat()
    signature = (stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)
    cached = _HASH_CACHE.get(str(path))
    if cached and cached[0] == signature:
        return cached[1]
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    final = path.stat()
    assert signature == (final.st_ino, final.st_size, final.st_mtime_ns, final.st_ctime_ns), 'File changed during hashing'
    result = digest.hexdigest()
    _HASH_CACHE[str(path)] = (signature, result)
    return result


def load(name):
    return json.loads((ROOT / (name + '.json')).read_text())


def source_checks(record):
    for path, digest in record.get('source_hashes', {}).items():
        assert sha(path) == digest, path


def validate():
    if sys.flags.optimize:
        raise RuntimeError('Verification must run with assertions enabled')
    verify_registration()
    design = check()
    data, official = load('confirmation'), load('analysis')
    independent, replay = load('independent_statistics'), load('independent_verification')
    world, logs = load('world_checks'), load('log_checks')
    archives, archive_checks = load('archive_index'), load('archive_build_checks')
    security = load('restore_security_checks')
    execution = load('execution')
    assert execution['status'] == 'completed' and execution['returncode'] == 0
    assert execution['design_sha256'] == sha(ROOT / 'design.json') == official['design_sha256']
    expected = {(p, s, v) for p in design['policies'] for s in design['seeds'] for v in design['families']}
    found = [(r['policy'], r['seed'], r['variant']) for r in data['episodes']]
    assert len(found) == len(expected) == 5160 and set(found) == expected and data['complete']
    assert data['code_hashes'] == design['frozen_inherited_hashes']
    assert data['recorder_sha256'] == design['setup_source_hashes']['research5/benchmark.py']
    permitted_recorders = {design['setup_source_hashes']['research5/benchmark.py']} | set(design['recovery']['prior_recorder_sha256s'])
    for row in data['episodes']:
        assert row['recorder_source_sha256'] in permitted_recorders
        assert row['valid'] and row['failure_count'] == row['optimized_fallback_count'] == 0
        assert row['invocation_count'] == 120 and row['arrived_members'] == 200
        assert row['configuration'] == (design['configuration'] if row['policy'] == design['candidate'] else {'match': 'greedy', 'ask': 'fifo'})
    assert independent['adjusted98_75']['n'] == 430 and independent['invalid_failures_fallbacks'] == 0
    assert independent['superiority'] == official['superiority']
    assert all(abs(a-b) < 1e-12 for a, b in zip(independent['adjusted98_75']['ci'], official['adjusted_ci98_75']))
    assert all(v < 1e-12 for v in independent['official_max_abs_errors'].values())
    source_checks(independent)
    assert replay['complete_registered_verification_grid'] and replay['episodes'] == 48 and replay['invocations'] == 5760
    assert replay['all_valid_zero_fallback'] and replay['all_ordered_semantic_actions_digests_shared_metrics_equal']
    assert replay['reference_sha256'] == sha(ROOT / 'confirmation.json')
    required_replays = {(p, s, v, mode) for p in design['policies'] for s in (90001, 90002)
                        for v in design['families'] for mode in ('direct', 'subprocess')}
    actual_replays = []
    for name in ('independent_replay_direct', 'independent_replay_subprocess'):
        record = load(name); source_checks(record)
        assert record['complete'] and record['source_bytes_unchanged']
        assert record['reference_sha256'] == sha(ROOT / 'confirmation.json')
        assert record['source_hashes'] == record['source_hashes_after']
        for row in record['episodes']:
            actual_replays.append((row['policy'], row['seed'], row['variant'], row['execution']))
            assert row['valid'] and row['fallback_count'] == 0 and not row['metric_differences']
            assert all(row[k] for k in ('ordered_actions_equal', 'semantic_actions_equal', 'byte_digest_match', 'semantic_digest_match'))
    assert len(actual_replays) == 48 and set(actual_replays) == required_replays
    assert world['complete'] and world['pass'] and world['committed_rows_processed'] == 5160
    assert world['paired_seed_family_cells'] == world['generator_calls'] == 2580 and not world['failures']
    source_checks(world)
    assert logs['valid'] and logs['checked_episodes'] == 5160 and logs['checked_invocations'] == 619200 and not logs['errors']
    log_cells = [(r['policy'], r['seed'], r['variant']) for r in logs['rows']]
    assert len(log_cells) == 5160 and set(log_cells) == expected
    assert logs['source_sha256'] == sha('research5/verify_logs.py')
    assert logs['confirmation_sha256'] == sha(ROOT / 'confirmation.json')
    for policy in design['policies']:
        for key, count in independent['totals'][policy].items():
            assert logs['totals'][policy][key] == count
    assert archive_checks['valid'] and archive_checks['index_sha256'] == sha(ROOT / 'archive_index.json')
    assert archive_checks['source_sha256'] == sha('research5/archive_results.py')
    assert archive_checks['different_existing_refused'] and archive_checks['identical_existing_skipped']
    archived = {m['path']: m for archive in archives['archives'] for m in archive['members']}
    assert len(archived) == archive_checks['verified_members']
    all_raw = {str(p) for pattern in ('*_traces', '*_traces_full') for directory in ROOT.rglob(pattern) if directory.is_dir() for p in directory.rglob('*') if p.is_file()}
    assert set(archived) == all_raw
    for path, expected_record in archived.items():
        assert Path(path).stat().st_size == expected_record['bytes'] and sha(path) == expected_record['sha256']
    for record in archives['archives']:
        assert Path(record['path']).stat().st_size == record['bytes'] and sha(record['path']) == record['sha256']
    for row in data['episodes']:
        assert all(row[k] in archived for k in ('trace', 'full_invocation_log', 'privileged_audit_log'))
        for path, digest in row['audit_files'].items():
            assert archived[path]['sha256'] == digest['sha256'] and archived[path]['bytes'] == digest['bytes']
    assert security['valid']; source_checks(security)
    production = load('production_selected')
    assert production['valid'] and not production['prepare_only'] and all(production['equivalence'].values())
    assert len(production['rows']) == 3 and {r['execution'] for r in production['rows']} == {'direct', 'subprocess', 'container'}
    source_checks(production)
    for row in production['rows']:
        assert row['valid'] and row['candidate'] == design['candidate'] and len(row['calls']) == 120
        assert row['captured_fallback_warning_count'] == 0
        if row['execution'] == 'direct':
            assert row['optimized_fallback_count'] == 0
        for call in row['calls']:
            assert call['seconds'] < 10 and call['memory_bytes'] < 1048576 and call['request_bytes'] <= 1048576
    probe = production['resource_probe']['probe']; limits = probe['cgroups']
    quota, period = map(int, limits['cpu.max'].split())
    assert 0 < quota / period <= 2 and 0 < int(limits['memory.max']) <= 1073741824
    assert int(limits['memory.swap.max']) == 0 and 0 < int(limits['pids.max']) <= 64
    assert probe['uid'] == probe['gid'] == 65534 and probe['root_write_errno'] == 30 and probe['egress_errno'] == 101
    assert production['image']['below_documented_2GiB'] and 0 < production['image']['size_bytes'] < 2*1073741824
    app_sources = {'kit.py','research/terminal_model.py','research3/__init__.py','research3/policy.py','research3/model_candidates.py','research4/__init__.py','research4/policy.py','research4/candidates.py'}
    assert set(probe['source_hashes']) == set(production['resource_probe']['host_source_hashes']) == app_sources
    for path in app_sources:
        assert sha(path) == probe['source_hashes'][path] == production['resource_probe']['host_source_hashes'][path] == production['source_hashes'][path]
    metrics = {'assignments','mutual_acceptances','dates','mutual_second_meeting_intention','missing_feedback','ask_cost','arrived_members','msmi_per_100_arrived_members','status','valid','served_members','unserved_members','coverage','mutual_acceptances_per_100','first_introduction_wait_days','action_sha256','semantic_action_sha256'}
    for metric in metrics:
        assert all(row[metric] == production['rows'][0][metric] for row in production['rows'])
    critic = load('critic_checks')
    assert critic['full_grid_cells'] == critic['valid_committed_rows'] == 5160
    assert critic['failures_committed'] == critic['fallbacks_committed'] == 0
    assert Counter(row['recorder_source_sha256'] for row in data['episodes']) == critic['recorders'] == independent['recorder_attribution']
    anchors = {design['recovery']['archive_manifest']: design['recovery']['archive_manifest_sha256']}
    for recovery in critic['recovery']:
        prior_design = json.loads((Path(recovery['archive'])/'design.json').read_text())
        if prior_design.get('recovery'):
            old = prior_design['recovery']
            anchors[old['archive_manifest']] = old['archive_manifest_sha256']
            assert sha(Path(old['archive'])/'design.json') == old['prior_design_sha256']
    for recovery in critic['recovery']:
        assert recovery['all_saved_scientific_rows_identical_final'] and recovery['run_function_ast_unchanged']
        manifest_path = str(Path(recovery['archive'])/'archive_manifest.json')
        assert sha(manifest_path) == anchors[manifest_path]
        for path, expected_record in json.loads(Path(manifest_path).read_text())['files'].items():
            assert Path(path).stat().st_size == expected_record['bytes'] and sha(path) == expected_record['sha256']
    preserved = {}
    exceptions = json.loads(Path('results/research4/inherited_manifest_exceptions.json').read_text())
    allowed = {r['path']: r['current_sha256'] for r in exceptions['exceptions']}
    for manifest_path in ('results/research4/manifest.json', 'results/research3/manifest.json', 'results/research3/inherited_manifest.json'):
        prior = json.loads(Path(manifest_path).read_text())
        for path, record in prior['files'].items():
            digest = sha(path)
            assert digest == record['sha256'] or digest == allowed.get(path), path
        preserved[manifest_path] = len(prior['files'])
    for name in ('FINAL_REPORT', 'REPRODUCTION', 'FINAL_REVIEW', 'RESULT_REPLICATION', 'PRODUCTION_REVIEW',
                 'ARCHIVE_AUDIT_REVIEW', 'WORLD_REVIEW', 'PACKAGE_REVIEW'):
        assert (Path('research5') / (name + '.md')).is_file(), name
    return {'valid': True, 'fixed_episode_count': 5160, 'seed_clusters': 430, 'checked_policy_calls': 619200,
            'independent_replays': 48, 'production_calls': 360, 'archive_members': len(archived),
            'superiority': official['superiority'], 'preserved_prior_file_counts': preserved,
            'interrupted_attempts': 'Preserved separately; not certified failure-free. See FINAL_REVIEW.md.',
            'scope': 'Complete fixed-grid verification, finite tested production scope and lossless archival integrity; no universal timeout guarantee or proof of historical timestamps.'}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--seal', action='store_true'); args = parser.parse_args()
    started, cpu = time.perf_counter(), time.process_time()
    report = validate()
    if args.seal:
        target = ROOT / 'manifest.json'; assert not target.exists(), 'Refuse final manifest overwrite'
        files = [p for base in (Path('research5'), ROOT) for p in base.rglob('*')
                 if p.is_file() and '__pycache__' not in p.parts and p != target and p != ROOT/'package_gate.json']
        mapping = {str(p): {'bytes': p.stat().st_size, 'sha256': sha(p)} for p in sorted(files)}
        report.update(completed_utc=datetime.now(timezone.utc).isoformat(),
                      gate_wall_seconds=time.perf_counter()-started,
                      gate_cpu_seconds=time.process_time()-cpu,
                      compute_scope='Includes validation/preservation and manifest input hashing; excludes final small JSON writes.')
        log = ROOT / 'package_gate.json'
        log.write_text(json.dumps(report, indent=2)+'\n')
        mapping[str(log)] = {'bytes': log.stat().st_size, 'sha256': sha(log)}
        manifest = {'completed': True, 'completed_utc': report['completed_utc'],
                    'registration_design_sha256': sha(ROOT/'design.json'), 'superiority': report['superiority'],
                    'verification': report, 'python': sys.version, 'platform': platform.platform(), 'files': mapping,
                    'scope': 'Frozen byte consistency, not tamper-proof historical provenance; interrupted attempts retained.'}
        target.write_text(json.dumps(manifest, indent=2)+'\n')
        print('Research5 verification sealed:', len(mapping), 'files; superiority:', report['superiority'])
    else:
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
