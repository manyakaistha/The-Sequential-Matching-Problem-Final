"""Bounded cold-process transport; no adversarial filesystem/network sandbox."""
import json
import math
import os
from pathlib import Path
import resource
import selectors
import signal
import subprocess
import sys
import tempfile
import time


def strict_loads(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    def constant(value):
        raise ValueError('nonfinite JSON value: ' + value)
    return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)


class InvocationError(RuntimeError):
    def __init__(self, message, stdout=b'', stderr=b'', telemetry=None):
        super().__init__(message)
        self.stdout = stdout.decode('utf-8', 'replace')
        self.stderr = stderr.decode('utf-8', 'replace')
        self.telemetry = telemetry or {}


def invoke_policy(workspace_root, entrypoint, config, request, *, timeout_seconds=10,
                  wire_limit_bytes=1048576, cpu_seconds=10, rss_gib=4):
    data = json.dumps({'request': request, 'config': config}, allow_nan=False).encode()
    if len(data) > wire_limit_bytes:
        raise InvocationError('request exceeds wire limit')
    if timeout_seconds <= 0:
        raise InvocationError('attempt wall deadline reached')
    required = ('RLIMIT_CPU', 'RLIMIT_AS', 'RLIMIT_FSIZE')
    if any(not hasattr(resource, name) for name in required):
        raise InvocationError('required OS resource guard unsupported')
    def guard():
        resource.setrlimit(resource.RLIMIT_CPU, (max(1, math.ceil(cpu_seconds)), max(1, math.ceil(cpu_seconds))))
        if sys.platform != 'darwin':
            resource.setrlimit(resource.RLIMIT_AS, (int(rss_gib * 1024**3), int(rss_gib * 1024**3)))
        resource.setrlimit(resource.RLIMIT_FSIZE, (wire_limit_bytes, wire_limit_bytes))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    started = time.monotonic()
    stdout, stderr = bytearray(), bytearray()
    enforcement = {'cpu': 'RLIMIT_CPU', 'address_space': 'unsupported on macOS' if sys.platform == 'darwin' else 'RLIMIT_AS (virtual address space; not RSS)',
                   'rss': 'live ps RSS monitor/process-group kill (direct child)' ,
                   'file_size': 'RLIMIT_FSIZE', 'wall': 'parent deadline/process-group kill',
                   'wire': 'bounded pipes', 'sandbox': 'none (trusted source only)'}
    temporary_root = Path(workspace_root).resolve() / 'research8' / 'continuation_probe' / '.policy_tmp'
    temporary_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='r8_policy_', dir=temporary_root) as cwd:
        command = [sys.executable, '-I', '-B', '-X', f'pycache_prefix={cwd}/pycache', str(Path(__file__).with_name('policy_cli.py').resolve()),
                   str(Path(workspace_root).resolve()), entrypoint, str(wire_limit_bytes)]
        try:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, cwd=cwd, env={'PATH': os.defpath, 'LANG': 'C.UTF-8', 'PYTHONPYCACHEPREFIX': f'{cwd}/pycache', 'PYTHONDONTWRITEBYTECODE': '1'},
                                       start_new_session=True, preexec_fn=guard)
        except (OSError, subprocess.SubprocessError) as exc:
            raise InvocationError(f'required process/resource guard failed: {exc}', telemetry={'enforcement': enforcement}) from exc
        selector = selectors.DefaultSelector()
        for stream in (process.stdin, process.stdout, process.stderr):
            os.set_blocking(stream.fileno(), False)
        selector.register(process.stdin, selectors.EVENT_WRITE, 'stdin')
        selector.register(process.stdout, selectors.EVENT_READ, 'stdout')
        selector.register(process.stderr, selectors.EVENT_READ, 'stderr')
        offset, failure, last_rss_check, peak_rss_kib = 0, None, 0, 0
        try:
            while selector.get_map():
                if time.monotonic() - last_rss_check >= .1 and process.poll() is None:
                    last_rss_check = time.monotonic()
                    try:
                        measurement = subprocess.run(['/bin/ps', '-o', 'rss=', '-p', str(process.pid)],
                                                     capture_output=True, timeout=min(.5, max(.01, timeout_seconds-(time.monotonic()-started))), env={'PATH': os.defpath})
                    except (OSError, subprocess.TimeoutExpired):
                        failure = 'required live RSS monitor unavailable'
                        break
                    if measurement.returncode == 0 and measurement.stdout.strip():
                        peak_rss_kib = max(peak_rss_kib, int(measurement.stdout.strip()))
                        if peak_rss_kib > rss_gib * 1024**2:
                            failure = 'policy RSS limit exceeded'
                            break
                    elif process.poll() is None:
                        failure = 'required live RSS monitor unavailable'
                        break
                remaining = timeout_seconds - (time.monotonic() - started)
                if remaining <= 0:
                    failure = 'policy hard wall timeout'
                    break
                for key, _ in selector.select(min(.1, remaining)):
                    stream, name = key.fileobj, key.data
                    if name == 'stdin':
                        try:
                            offset += os.write(stream.fileno(), data[offset:offset + 65536])
                        except BrokenPipeError:
                            offset = len(data)
                        if offset == len(data):
                            selector.unregister(stream)
                            stream.close()
                    else:
                        chunk = os.read(stream.fileno(), 65536)
                        if not chunk:
                            selector.unregister(stream)
                            stream.close()
                            continue
                        target = stdout if name == 'stdout' else stderr
                        space = wire_limit_bytes - len(stdout) - len(stderr)
                        target.extend(chunk[:max(0, space)])
                        if len(chunk) > space:
                            failure = 'policy stdout/stderr exceeds combined wire limit'
                            break
                if failure:
                    break
            if failure:
                os.killpg(process.pid, signal.SIGKILL)
            try:
                code = process.wait(timeout=max(.01, timeout_seconds - (time.monotonic() - started)))
            except subprocess.TimeoutExpired:
                failure = 'policy hard wall timeout'
                os.killpg(process.pid, signal.SIGKILL)
                code = process.wait()
            if time.monotonic() - started > timeout_seconds:
                failure = failure or 'policy hard wall timeout'
            telemetry = {'transport_elapsed_seconds': time.monotonic() - started, 'exit_code': code,
                         'fallback': False, 'reason': failure, 'enforcement': enforcement, 'peak_rss_kib': peak_rss_kib}
            if failure or code:
                raise InvocationError(failure or f'policy exited {code}', stdout, stderr, telemetry)
            try:
                envelope = strict_loads(stdout)
                if set(envelope) != {'response', 'telemetry'} or not isinstance(envelope['response'], dict):
                    raise ValueError('invalid response envelope')
                if not isinstance(envelope['telemetry'], dict):
                    raise ValueError('invalid telemetry envelope')
                # Strictly reject NaN, Infinity and non-JSON response values.
                json.dumps(envelope, allow_nan=False)
                envelope['telemetry'].update(telemetry)
                envelope['telemetry']['fallback'] = bool(strict_loads(stdout)['telemetry'].get('fallback'))
                envelope['telemetry']['stderr'] = stderr.decode('utf-8', 'replace')
                if envelope['telemetry']['fallback']:
                    telemetry['fallback'] = True
                    telemetry['reason'] = envelope['telemetry'].get('reason')
                    raise ValueError('policy fallback is not authorized')
                return envelope
            except (ValueError, TypeError) as exc:
                raise InvocationError(f'invalid policy output: {exc}', stdout, stderr, telemetry) from exc
        finally:
            selector.close()
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
            for stream in (process.stdin, process.stdout, process.stderr):
                if not stream.closed:
                    stream.close()
