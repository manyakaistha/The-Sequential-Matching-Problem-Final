"""Lossless invocation chunks, separate audit state, immutable attempt commits."""
import contextlib
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import resource
import sys
import time
import traceback
import uuid

import evaluate
from kit import Simulator, generate


def raw_json(value):
    return json.dumps(value, allow_nan=False).encode('utf-8')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write_new(path, value):
    path = Path(path)
    with path.open('xb') as stream:
        stream.write(raw_json(value) + b'\n')
        stream.flush()
        os.fsync(stream.fileno())


def chunk(path, value):
    # Each invocation is independently decompressible; a crash cannot corrupt others.
    with Path(path).open('xb') as stream:
        with gzip.GzipFile(fileobj=stream, mode='wb', compresslevel=1, mtime=0) as zipped:
            zipped.write(raw_json(value) + b'\n')
        stream.flush()
        os.fsync(stream.fileno())


def run_cell(job):
    from research6.policies import policy as policy_module
    decide = policy_module.decide
    root, cell, cfg, sources = job
    root = Path(root)
    for source, expected in sources.items():
        if sha(source) != expected:
            raise ValueError('worker source mismatch: '+source)
    ident = f"{cell['policy']}_{cell['family']}_{cell['seed']}"
    attempt_id = uuid.uuid4().hex
    attempt = root / 'attempts' / ident / attempt_id
    public = attempt / 'public'
    private = attempt / 'privileged'
    public.mkdir(parents=True, exist_ok=False)
    private.mkdir()
    started = time.monotonic()
    cpu_start = time.process_time()
    write_new(attempt / 'started.json', dict(cell=cell, attempt_id=attempt_id, pid=os.getpid(), sources=sources,
                                             execution='in_process_json', config=cfg, started_unix=time.time()))
    sim = None
    initial_hash = None
    memory = None
    digest = hashlib.sha256()
    timings = []
    requests = []
    memory_sizes = []
    actions = []
    fallbacks = 0
    sequence = 0
    try:
        world = generate(cell['seed'], 200, 'evaluation', cell['family'])
        initial_hash = hashlib.sha256(raw_json(world)).hexdigest()
        chunk(private / 'initial.json.gz', {'world':world,'privileged':True})
        sim = Simulator(world)
        for day in range(60):
            for phase in ('ask', 'match'):
                sequence += 1
                request = {'schema_version': world['schema_version'], 'phase': phase,
                           'state': sim.observe(), 'memory': memory}
                wire = raw_json(request)
                prefix = f'{sequence:03d}'
                chunk(public / (prefix + '.request.json.gz'), {'sequence': sequence,
                      'wire_utf8': wire.decode(), 'request': request, 'memory_before_utf8': raw_json(memory).decode(),
                      'pid': os.getpid(), 'unix': time.time()})
                if len(wire) > evaluate.LIMIT:
                    raise ValueError('request exceeds protocol limit')
                err = io.StringIO()
                stdout = io.StringIO()
                call_start = time.monotonic()
                call_cpu = time.process_time()
                response = None
                policy_module.LAST_STATUS = {'fallback':False, 'reason':None}
                status = dict(policy_module.LAST_STATUS)
                try:
                    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(stdout):
                        try:
                            response = decide(evaluate.strict_json(wire), cfg)
                        finally:
                            status = dict(policy_module.LAST_STATUS)
                            fallbacks += int(status.get('fallback') is True)
                    output = raw_json(response)
                except BaseException as error:
                    chunk(public / (prefix + '.inference_error.json.gz'), {
                        'sequence':sequence, 'response_repr':repr(response), 'stdout_utf8':stdout.getvalue(),
                        'stderr_utf8':err.getvalue(), 'elapsed_seconds':time.monotonic()-call_start,
                        'cpu_seconds':time.process_time()-call_cpu, 'policy_status':status, 'error':repr(error),
                        'traceback':traceback.format_exc()})
                    raise
                elapsed = time.monotonic() - call_start
                key = 'asks' if phase == 'ask' else 'pairs'
                # Retain returned bytes and captured output before validation can reject them.
                chunk(public / (prefix + '.response.json.gz'), {'sequence': sequence,
                      'wire_utf8': output.decode(), 'response': response,
                      'stderr_utf8': err.getvalue(), 'stdout_utf8':stdout.getvalue(),
                      'wire_scope':'serialized in-process return; captured stdout recorded separately',
                      'execution': 'in_process_json', 'policy_status':status, 'elapsed_seconds': elapsed,
                      'cpu_seconds': time.process_time()-call_cpu,
                      'peak_rss_process_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == 'darwin' else 1024),
                      'request_bytes':len(wire), 'response_bytes':len(output), 'unix':time.time()})
                evaluate.validate_response(evaluate.strict_json(output), phase)
                memory_wire = raw_json(response['memory'])
                chunk(public / (prefix + '.validated.json.gz'), {'sequence':sequence,
                       'memory_after_utf8':memory_wire.decode(), 'memory_bytes':len(memory_wire)})
                if elapsed > 10 or len(memory_wire) >= evaluate.LIMIT or len(output) > evaluate.LIMIT:
                    raise ValueError('invocation resource limit')
                action = response[key]
                memory = response['memory']
                timings.append(elapsed)
                requests.append(len(wire))
                memory_sizes.append(len(memory_wire))
                actions.append([phase, day, action])
                digest.update(json.dumps([phase, day, action], sort_keys=True, allow_nan=False).encode())
                if phase == 'ask':
                    sim.resolve_asks(action)
                else:
                    sim.advance(action)
        for _ in range(40):
            sim.advance([])
        if sim.day != 100 or sequence != 120:
            raise ValueError('horizon/call mismatch')
        row = sim.metrics()
        served = {i for introduction in sim.introductions for i in (introduction['user_a'], introduction['user_b'])}
        row.update(valid=True, coverage=len(served)/200, served_members=len(served))
    except BaseException as error:
        chunk(public / 'error.json.gz', {'sequence': sequence, 'error_type': type(error).__name__,
              'error':str(error), 'traceback':traceback.format_exc(), 'unix':time.time()})
        row = {'valid': False, 'error':type(error).__name__+': '+str(error)}
    chunk(private / 'final.json.gz', {'privileged':True, 'state':{k:sorted(v) if isinstance(v,set) else v for k,v in vars(sim).items()} if sim else None})
    chunk(public / 'outcomes.json.gz', {'introductions':sim.introductions if sim else [],'feedback':sim.receive_feedback() if sim else [],
                                       'actions':actions,'final_day':sim.day if sim else None})
    row.update(**cell, attempt_id=attempt_id, attempt_path=str(attempt), config=cfg, source_hashes=sources,
               world_sha256=initial_hash, action_sha256=digest.hexdigest(), invocation_count=len(timings),
               attempted_invocations=sequence, fallback_count=fallbacks, wall_seconds=time.monotonic()-started,
               cpu_seconds=time.process_time()-cpu_start, inference_latencies=timings,
               peak_request_bytes=max(requests,default=0), peak_memory_bytes=max(memory_sizes,default=0))
    files = {str(path.relative_to(attempt)): {'bytes':path.stat().st_size,'sha256':sha(path)}
             for path in sorted(attempt.rglob('*')) if path.is_file()}
    row['files'] = files
    write_new(attempt / 'closed.json', row)
    # Atomic authoritative commit; no overwrite, including invalid committed episodes.
    commit = root / 'commits' / (ident+'.json')
    commit.parent.mkdir(exist_ok=True)
    temporary = attempt / 'commit.json'
    write_new(temporary, row)
    os.link(temporary, commit)
    return row
