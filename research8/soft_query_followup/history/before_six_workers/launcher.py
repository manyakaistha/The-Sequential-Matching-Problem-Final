"""Enforced, write-once evidence campaign launcher.

A repository-wide lock serializes v2 coordinators and caps cell workers at three.
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

from .registration import ROOT, strict_json, verify_registration, write_once, file_sha256


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
              'run_p4_fast.py', 'soft_query_followup.v2.launcher']) and '--worker-cell' not in command):
            found.append(line.strip())
    if found:
        raise RuntimeError('Other known simulation coordinator(s) active: ' + '; '.join(found))


def proc_usage(pid):
    """Per-worker CPU/RSS plus child process CPU via ps, including policy children."""
    raw = subprocess.check_output(['ps', '-axo', 'pid=,ppid=,rss=,time='], text=True)
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
    verify_registration(reg)
    cell = next(c for c in reg['cells'] if c['cell_key'] == cell_key)
    _hard_limits(reg['resource_forecast'])
    result = Research8Runner(ROOT, reg, Path(output)).execute_cell(cell)
    return 0 if result.get('is_valid') and result.get('metrics', {}).get('valid') else 2


def run_experiment(registration_path, output_dir, workers=3):
    regpath, output = Path(registration_path).resolve(), Path(output_dir).resolve()
    reg = strict_json(regpath.read_text())
    verify_registration(reg)
    caps = reg['resource_forecast']
    if type(workers) is not int or not 1 <= workers <= min(3, caps['max_workers']):
        raise ValueError('worker count must be1..3')
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
            if strict_json(binding_path.read_text()) != binding:
                raise ValueError('output directory already bound to a different registration')
        else:
            if any(output.iterdir()):
                raise ValueError('new output directory must be empty')
            write_once(binding_path, binding)
        write_once(output / f'launch_{time.time_ns()}.json',
                   {'binding': binding, 'workers': workers, 'started_unix': time.time(),
                    'rss_enforcement': 'live worker+descendant aggregate RSS polled every0.1s',
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
            if row.get('registration_sha256') != reg['registration_sha256']:
                raise ValueError('existing commit registration mismatch')
            if not row.get('is_valid') or not row.get('metrics', {}).get('valid'):
                raise RuntimeError('invalid committed version; do not retry or omit it')
            present.add(key)
        queue = deque(c for c in reg['cells'] if c['cell_key'] not in present)
        pending = {}
        failure = None
        try:
            while queue or pending:
                check_disk(output, caps)
                # Hash checks before each dispatch batch prevent resuming/tampering
                # under another source identity; trusted workspace must stay frozen.
                verify_registration(reg)
                while queue and len(pending) < workers and failure is None:
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
                    cmd = [sys.executable, '-B', '-m', 'research8.soft_query_followup.v2.launcher',
                           '--registration', str(regpath), '--output', str(output),
                           '--worker-cell', cell['cell_key'], '--coordinator-lock-fd', str(lock.fileno())]
                    proc = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=stdout, stderr=stderr,
                                            start_new_session=True, pass_fds=(lock.fileno(),))
                    pending[proc.pid] = (proc, cell, time.monotonic(), stdout, stderr)
                for pid, (proc, cell, started, stdout, stderr) in list(pending.items()):
                    elapsed = time.monotonic() - started
                    if proc.poll() is None:
                        rss, cpu = proc_usage(pid)
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
                if failure:
                    raise RuntimeError(failure)
                time.sleep(.1)
        finally:
            for proc, _, _, stdout, stderr in pending.values():
                kill_worker(proc); stdout.close(); stderr.close()
        if set(expected) != present:
            raise RuntimeError('incomplete study')
        return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--registration', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--workers', type=int, default=3)
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
