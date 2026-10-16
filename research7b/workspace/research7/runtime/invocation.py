"""Exact byte invocations. Local modes are trusted and do not certify isolation."""
import contextlib
import io
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import tempfile
import time
from dataclasses import dataclass, field

LIMIT = 1024 * 1024

def raw_json(value):
    return json.dumps(value, allow_nan=False).encode('utf-8')

@dataclass
class InvocationResult:
    wire_response: bytes = b''
    stdout: bytes = b''
    stderr: bytes = b''
    elapsed_seconds: float = 0
    cpu_seconds: float = 0
    error: str = None
    policy_status: dict = field(default_factory=dict)

class TrustedInvocation:
    def __init__(self, decide, config):
        self.decide, self.config = decide, config

    def __call__(self, wire):
        out, err = io.StringIO(), io.StringIO()
        result = InvocationResult()
        start, cpu = time.monotonic(), time.process_time()
        previous_handler = signal.getsignal(signal.SIGALRM)
        previous_timer = signal.getitimer(signal.ITIMER_REAL)
        def deadline(signum, frame):
            raise TimeoutError('Trusted policy exceeded 10-second invocation limit')
        signal.signal(signal.SIGALRM, deadline)
        signal.setitimer(signal.ITIMER_REAL, min(10, previous_timer[0]) if previous_timer[0] else 10)
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                response = self.decide(json.loads(wire), json.loads(raw_json(self.config)))
            result.wire_response = raw_json(response)
        except BaseException as exc:
            result.error = type(exc).__name__ + ': ' + str(exc)
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous_handler)
            if previous_timer[0]:
                signal.setitimer(signal.ITIMER_REAL, max(0.000001, previous_timer[0]-(time.monotonic()-start)), previous_timer[1])
            module = __import__('sys').modules.get(self.decide.__module__)
            status = getattr(module, 'LAST_STATUS', {})
            result.policy_status = json.loads(raw_json(status))
        result.stdout, result.stderr = out.getvalue().encode(), err.getvalue().encode()
        result.elapsed_seconds, result.cpu_seconds = time.monotonic()-start, time.process_time()-cpu
        if result.elapsed_seconds > 10 or len(result.wire_response) > LIMIT or len(result.stdout) > LIMIT or len(result.stderr) > LIMIT:
            result.error = 'Invocation resource limit exceeded'
        if result.stdout:
            result.error = 'Unexpected stdout from in-process policy'
        return result

class SubprocessInvocation:
    def __init__(self, command, cwd, timeout=10):
        if not command or not all(isinstance(s, str) for s in command):
            raise ValueError('Registered command must be a string array')
        self.command, self.cwd, self.timeout = command, cwd, min(timeout, 10)

    def __call__(self, wire):
        result = InvocationResult()
        start = time.monotonic()
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        # RLIMIT_FSIZE bounds retained output; process group kill covers descendants.
        def limits():
            import resource
            resource.setrlimit(resource.RLIMIT_FSIZE, (LIMIT, LIMIT))
            resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
        workspace_dir = Path(__file__).resolve().parents[2]
        repo_root = Path(__file__).resolve().parents[4]
        existing_pp = os.environ.get('PYTHONPATH', '')
        pp_parts = [str(self.cwd), str(workspace_dir), str(repo_root)]
        if existing_pp:
            for p in existing_pp.split(os.pathsep):
                if p and p not in pp_parts:
                    pp_parts.append(p)
        env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1',
                   PYTHONPATH=os.pathsep.join(pp_parts))
        tmp_dir = workspace_dir / '.tmp'
        tmp_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=tmp_dir) as out, tempfile.TemporaryFile(dir=tmp_dir) as err:
            proc = None
            try:
                proc = subprocess.Popen(self.command, cwd=self.cwd, env=env, stdin=subprocess.PIPE,
                                        stdout=out, stderr=err, start_new_session=True, preexec_fn=limits)
                proc.communicate(wire, timeout=self.timeout)
                if proc.returncode:
                    result.error = f'Policy exit {proc.returncode}'
            except BaseException as exc:
                result.error = type(exc).__name__ + ': ' + str(exc)
            finally:
                if proc is not None:
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    proc.wait()
                out.seek(0); err.seek(0)
                result.stdout, result.stderr = out.read(), err.read()
                result.wire_response = result.stdout
        result.elapsed_seconds = time.monotonic()-start
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        result.cpu_seconds = after.ru_utime + after.ru_stime - usage.ru_utime - usage.ru_stime
        return result
