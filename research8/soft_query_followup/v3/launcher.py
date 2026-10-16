"""Enforced, write-once evidence campaign launcher.

A shared v2/v3 lease caps participating simulation workers at seven.
Storage continuation preserves the original fixed experiment and all old commits.
It cannot control unrelated launchers that do not participate in this protocol;
preflight detects known old launch commands, and the testing prompt requires an
operator check for other simulators on either machine before starting.
"""
import argparse
from collections import deque
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import time

from research8.soft_query_followup.v2.registration import ROOT, strict_json, write_once, file_sha256
from .continuation import verify_continuation, verify_commit_identity
from .storage import archive_attempt, verify_archive


def check_disk(output, caps):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    for path, floor, label in [(output, caps['free_reserve_gib_min'], 'results drive'),
                               (Path('/'), caps['boot_free_reserve_gib_min'], 'boot drive')]:
        free = shutil.disk_usage(path).free / 2**30
        if free < floor:
            raise RuntimeError(f'{label} free space {free:.3f}GiB below registered {floor}GiB')


def known_other_simulators():
    raw = subprocess.check_output(['ps', '-axo', 'pid=,command='], text=True)
    me = os.getpid()
    found = []
    for line in raw.splitlines():
        bits = line.strip().split(None, 1)
        if len(bits) != 2 or int(bits[0]) == me:
            continue
        command = bits[1]
        if ('python' in command and any(token in command for token in
             ['soft_query_trial/runtime/launcher.py', 'soft_query_trial.runtime.launcher',
              'run_p4_fast.py', 'soft_query_followup.v2.launcher', 'soft_query_followup.v3.launcher']) and '--worker-cell' not in command):
            found.append(line.strip())
    if found:
        raise RuntimeError('Other known simulation coordinator(s) active: ' + '; '.join(found))


def proc_usage(pid, snapshot=None):
    """Per-worker CPU/RSS plus child process CPU via ps, including policy children."""
    raw = snapshot if snapshot is not None else subprocess.check_output(['ps', '-axo', 'pid=,ppid=,rss=,time='], text=True)
    rows = {}
    for line in raw.splitlines():
        parts = line.split()
        if len(parts) != 4: continue
        try:
            actor, parent, rss = map(int, parts[:3])
            components = parts[3].split(':')
            seconds = sum(float(value) * 60**i for i, value in enumerate(reversed(components)))
            rows[actor] = (parent, rss * 1024, seconds)
        except ValueError:
            continue
    descendants = {pid}
    while True:
        add = {p for p, (parent, _, _) in rows.items() if parent in descendants}
        if add.issubset(descendants): break
        descendants.update(add)
    # Worker CPU excludes reaped children; runner adds cumulative child CPU and
    # enforces exact total. ps monitor bounds live aggregate RSS and wall time.
    return (sum(rows[p][1] for p in descendants if p in rows),
            sum(rows[p][2] for p in descendants if p in rows))


def kill_worker(proc):
    # Policy subprocesses create sessions of their own. Collect descendants
    # before killing the parent so their ancestry is not lost on reparenting.
    rows = {}
    try:
        raw = subprocess.check_output(['ps', '-axo', 'pid=,ppid='], text=True)
        rows = {int(a): int(b) for a, b in (line.split() for line in raw.splitlines() if len(line.split()) == 2)}
    except (OSError, subprocess.SubprocessError, ValueError):
        pass
    descendants = {proc.pid}
    while True:
        add = {pid for pid, parent in rows.items() if parent in descendants}
        if add.issubset(descendants): break
        descendants.update(add)
    for pid in descendants - {proc.pid}:
        try: os.killpg(pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            try: os.kill(pid, signal.SIGKILL)
            except ProcessLookupError: pass
    try: os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError: pass
    proc.wait()


def _hard_limits(caps):
    resource.setrlimit(resource.RLIMIT_CPU, (math.ceil(caps['max_attempt_cpu_seconds']),) * 2)
    # Aggregate RSS monitored by parent; process AS is separately limited where
    # supported. No RLIMIT_RSS claim (it is often unenforced on Unix).
    if hasattr(resource, 'RLIMIT_AS') and sys.platform != 'darwin':
        limit = int(caps['max_rss_gib'] * 2**30)
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))


def worker_main(registration_path, output, cell_key, coordinator_lock_fd=None):
    if coordinator_lock_fd is None:
        raise ValueError('workers must be launched by the locked coordinator')
    try:
        expected_lock = (ROOT / 'research8/soft_query_followup/v2/.simulation.lock').stat()
        actual_lock = os.fstat(coordinator_lock_fd)
        if (expected_lock.st_dev, expected_lock.st_ino) != (actual_lock.st_dev, actual_lock.st_ino):
            raise ValueError('worker inherited an unrelated lock')
        fcntl.flock(coordinator_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (OSError, ValueError) as error:
        raise ValueError('worker missing live coordinator lease') from error
    from .runner import Research8Runner
    reg = strict_json(Path(registration_path).read_text())
    verify_continuation(reg,output=Path(output))
    cell = next(c for c in reg['cells'] if c['cell_key'] == cell_key)
    _hard_limits(reg['resource_forecast'])
    result = Research8Runner(ROOT, reg, Path(output)).execute_cell(cell)
    return 0 if result.get('is_valid') and result.get('metrics', {}).get('valid') else 2


def validate_worker_count(workers, caps):
    if type(workers) is not int or not 1 <= workers <= min(7, caps['max_workers']):
        raise ValueError('worker count must be1..7')


def check_combined_rss(rss_bytes, caps):
    if rss_bytes > caps['max_total_worker_rss_gib'] * 2**30:
        raise RuntimeError('combined simulation worker RSS cap exceeded')




def evidence_bytes(output):
    return sum(p.stat().st_size for p in Path(output).rglob('*') if p.is_file())


def storage_dispatch_allowed(output, reg, *, pending_count):
    # Each raw attempt is bounded at512MiB. Reserve raw+archive duplication,
    # codec framing and one external audit staging slot; never delete evidence
    # to meet budget and never shrink the fixed statistical grid.
    used=evidence_bytes(output)
    reserve=pending_count * (1100*2**20) + reg['storage']['audit_transient_max_bytes']
    return used+reserve <= reg['storage']['max_evidence_bytes']


def run_experiment(registration_path, output_dir, workers=7):
    regpath, output = Path(registration_path).resolve(), Path(output_dir).resolve()
    reg = strict_json(regpath.read_text())
    original=verify_continuation(reg,output=output)
    caps = reg['resource_forecast']
    validate_worker_count(workers, caps)
    check_disk(output, caps)
    lockpath = ROOT / 'research8/soft_query_followup/v2/.simulation.lock'
    with lockpath.open('a') as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: raise RuntimeError('Another v2 coordinator holds the repository simulation lock')
        known_other_simulators()
        binding_path = output / 'run_binding.json'
        binding = {'registration_sha256': reg['registration_sha256'], 'stage_id': reg['stage_id'],
                   'registration_file_sha256': file_sha256(regpath)}
        if binding_path.exists():
            existing_binding = strict_json(binding_path.read_text())
            if existing_binding.get('registration_sha256') == reg['original_registration_sha256']:
                expected_original_binding = {
                    'registration_sha256': reg['original_registration_sha256'],
                    'stage_id': reg['stage_id'],
                    'registration_file_sha256': reg['original_registration_file_sha256'],
                }
                if existing_binding != expected_original_binding:
                    raise ValueError('original output directory binding changed')
                continued=output/'continuation_binding.json'
                if continued.exists():
                    if strict_json(continued.read_text()) != binding:raise ValueError('different continuation already bound')
                else:write_once(continued,binding)
            elif existing_binding != binding:
                raise ValueError('output directory binding changed')
        else:
            if any(output.iterdir()):
                raise ValueError('new output directory must be empty')
            write_once(binding_path, binding)
        write_once(output / f'launch_{time.time_ns()}.json',
                   {'binding': binding, 'workers': workers, 'started_unix': time.time(),
                    'rss_enforcement': 'live worker+descendant aggregate RSS polled every0.1s',
                    'storage_codec':'zstd3-lossless','storage_cap_bytes':15*2**30,
                    'filesystem_sandbox': False})
        commits = output / 'commits'
        commits.mkdir(exist_ok=True)
        expected = {c['cell_key']: c for c in reg['cells']}
        present = set()
        for path in commits.glob('*.json'):
            row = strict_json(path.read_text())
            key = row['cell']['cell_key']
            if key not in expected or row['cell'] != expected[key] or key in present:
                raise ValueError('unexpected/mismatched/duplicate existing committed cell')
            verify_commit_identity(output,row,reg,original)
            archived=archive_attempt(output,row['attempt_relative_path'],row['artifact_hashes'],remove_raw=True)
            if {k:v['sha256'] for k,v in archived['files'].items()} != row['artifact_hashes']:
                raise ValueError('retained archive coverage mismatch')
            if not row.get('is_valid') or not row.get('metrics', {}).get('valid'):
                raise RuntimeError('invalid committed version; do not retry or omit it')
            present.add(key)
        queue = deque(c for c in reg['cells'] if c['cell_key'] not in present)
        pending = {}
        failure = None
        try:
            while queue or pending:
                check_disk(output, caps)
                if queue and len(pending) < workers and failure is None and not (output/'DRAIN_REQUESTED').exists():
                    # Hash checks before each dispatch batch prevent resuming/tampering
                    # under another source identity; trusted workspace must stay frozen.
                    verify_continuation(reg,output=Path(output))
                    while queue and len(pending) < workers and failure is None:
                        if not storage_dispatch_allowed(output,reg,pending_count=len(pending)+1):break
                        cell = queue.popleft()
                        logs = output / 'worker_logs'
                        logs.mkdir(exist_ok=True)
                        attempt_log_prefix = cell['cell_key'] + '_' + str(time.time_ns())
                        stdout = (logs / (attempt_log_prefix + '.stdout')).open('xb')
                        stderr = (logs / (attempt_log_prefix + '.stderr')).open('xb')
                        env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'),
                               'PYTHONPATH': str(ROOT), 'PYTHONDONTWRITEBYTECODE': '1',
                               'TMPDIR': str(output), 'HOME': str(output),
                               'PYTHONPYCACHEPREFIX': str(output / 'empty_import_cache')}
                        cmd = [sys.executable, '-B', '-m', 'research8.soft_query_followup.v3.launcher',
                               '--registration', str(regpath), '--output', str(output),
                               '--worker-cell', cell['cell_key'], '--coordinator-lock-fd', str(lock.fileno())]
                        proc = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=stdout, stderr=stderr,
                                                start_new_session=True, pass_fds=(lock.fileno(),))
                        pending[proc.pid] = (proc, cell, time.monotonic(), stdout, stderr)
                combined_rss = 0
                process_snapshot=subprocess.check_output(['ps','-axo','pid=,ppid=,rss=,time='],text=True) if pending else ''
                for pid, (proc, cell, started, stdout, stderr) in list(pending.items()):
                    elapsed = time.monotonic() - started
                    if proc.poll() is None:
                        rss, cpu = proc_usage(pid,process_snapshot)
                        combined_rss += rss
                        if (elapsed > caps['max_attempt_wall_seconds'] or rss > caps['max_rss_gib'] * 2**30
                                or cpu > caps['max_attempt_cpu_seconds']):
                            kill_worker(proc)
                            failure = 'hard attempt resource cap exceeded: ' + cell['cell_key']
                    if proc.poll() is not None:
                        stdout.close(); stderr.close(); del pending[pid]
                        path = commits / (cell['cell_key'] + '.json')
                        if proc.returncode != 0 or not path.exists():
                            failure = failure or 'worker failed or missing durable commit: ' + cell['cell_key']
                            write_once(output / f'failure_{cell["cell_key"]}_{time.time_ns()}.json',
                                       {'cell': cell, 'returncode': proc.returncode, 'reason': failure,
                                        'registration_sha256': reg['registration_sha256']})
                        else:
                            row = strict_json(path.read_text())
                            if row['cell'] != cell or row.get('registration_sha256') != reg['registration_sha256'] or not row['is_valid']:
                                failure = 'invalid committed cell: ' + cell['cell_key']
                            else:
                                present.add(cell['cell_key'])
                                print(f'{len(present)}/{len(expected)} durable valid cells', flush=True)
                check_combined_rss(combined_rss, caps)
                if failure:
                    raise RuntimeError(failure)
                if (output/'DRAIN_REQUESTED').exists():
                    queue.clear()
                    if not pending:break
                if queue and not pending and not storage_dispatch_allowed(output,reg,pending_count=1):
                    raise RuntimeError('15GiB evidence budget exhausted; preserved all data')
                time.sleep(.1)
        finally:
            for proc, _, _, stdout, stderr in pending.values():
                kill_worker(proc); stdout.close(); stderr.close()
        if set(expected) != present:
            if (output/'DRAIN_REQUESTED').exists():
                print('Graceful drain complete; original fixed grid retained for resume',flush=True)
                return 0
            raise RuntimeError('incomplete study')
        print('Fixed grid complete; running archive-aware independent audit',flush=True)
        from .audit import audit_campaign
        proof=audit_campaign(output,ROOT/reg['original_registration_path'],regpath)
        write_once(output/'final_public_event_audit.json',proof)
        return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--registration', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--workers', type=int, default=7)
    p.add_argument('--worker-cell', help=argparse.SUPPRESS)
    p.add_argument('--coordinator-lock-fd', type=int, help=argparse.SUPPRESS)
    args = p.parse_args()
    try:
        if args.worker_cell:
            return worker_main(args.registration, args.output, args.worker_cell, args.coordinator_lock_fd)
        return run_experiment(args.registration, args.output, args.workers)
    except Exception as error:
        print(f'{type(error).__name__}: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
