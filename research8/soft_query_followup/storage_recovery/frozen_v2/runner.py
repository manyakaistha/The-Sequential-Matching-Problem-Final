"""Auditable research runner. Policies are trusted code, not hostile submissions.

World truth exists only in host memory. Cold children receive public observations
and policy configuration. OS limits constrain resources but do not sandbox paths.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import time
import uuid

from kit import Simulator, VERSION, baseline_asks, baseline_match, generate
from research8.w2.protocol import (PublicProtocolError, sanitize_observation,
                                  validate_ask_batch, validate_match_batch,
                                  validate_policy_memory)
from research8.soft_query_trial.policies.targeting import build_legal_graph, extract_candidate_set
from .invoke import invoke_policy, strict_loads
from .metrics import compute_run_metrics


def raw_json(value):
    # Preserve the frozen action digest's standard json separators.
    return json.dumps(value, allow_nan=False, sort_keys=True).encode('utf-8')


def _write(path, value):
    with Path(path).open('xb') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False).encode() + b'\n')
        stream.flush()
        os.fsync(stream.fileno())


def _append(path, value):
    with Path(path).open('ab') as stream:
        stream.write(raw_json(value) + b'\n')
        stream.flush()
        os.fsync(stream.fileno())


def _sync_directory(path):
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _cpu():
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    return time.process_time() + children.ru_utime + children.ru_stime


class Research8Runner:
    def __init__(self, workspace_root, registration, output_dir):
        self.workspace_root = Path(workspace_root).resolve()
        self.registration = copy.deepcopy(registration)
        self.output_dir = Path(output_dir).resolve()
        self.commits_dir = self.output_dir / 'commits'
        self.attempts_dir = self.output_dir / 'attempts'
        self.commits_dir.mkdir(parents=True, exist_ok=True)
        self.attempts_dir.mkdir(parents=True, exist_ok=True)

    def execute_cell(self, cell):
        from .registration import verify_registration
        verify_registration(self.registration, self.workspace_root)
        if cell not in self.registration['cells']:
            raise ValueError('cell is not registered')
        key = cell['cell_key']
        if not isinstance(key, str) or not key or Path(key).name != key or key in ('.', '..'):
            raise ValueError('unsafe cell key')
        registration_hash = self.registration['registration_sha256']
        commit_file = self.commits_dir / f'{key}.json'
        if commit_file.exists():
            record = strict_loads(commit_file.read_text())
            if record['registration_sha256'] != registration_hash or record['cell'] != cell:
                raise ValueError('existing commit registration/cell mismatch')
            relative = Path(record['attempt_relative_path'])
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('unsafe existing attempt path')
            attempt_path = self.output_dir / relative
            if not attempt_path.resolve().is_relative_to(self.attempts_dir.resolve()) or attempt_path.is_symlink():
                raise ValueError('unsafe existing attempt path')
            for name, digest in record['artifact_hashes'].items():
                if Path(name).name != name or (attempt_path / name).is_symlink():
                    raise ValueError('unsafe existing artifact path')
                if hashlib.sha256((attempt_path / name).read_bytes()).hexdigest() != digest:
                    raise ValueError('existing commit artifact mismatch')
            return record
        limits = self.registration['resource_forecast']
        reserve = limits['free_reserve_gib_min'] * 1024**3
        if shutil.disk_usage(self.output_dir).free < reserve:
            raise RuntimeError('free disk reserve below registered minimum')
        attempt_id = uuid.uuid4().hex
        attempt_dir = self.attempts_dir / key / attempt_id
        attempt_dir.mkdir(parents=True, exist_ok=False)
        streams = ('responses.jsonl', 'requests.jsonl', 'actions.jsonl', 'invocations.jsonl', 'query_answers.jsonl',
                   'daily_telemetry.jsonl', 'released_feedback.jsonl', 'event_log.jsonl')
        for name in streams:
            with (attempt_dir / name).open('xb') as stream:
                stream.flush()
                os.fsync(stream.fileno())
        started, cpu_start = time.monotonic(), _cpu()
        deadline = started + limits['max_attempt_wall_seconds']
        sequence, world_hash, memory = 0, None, None
        digest = hashlib.sha256()
        invocation_times, fallback_count, seen_feedback = [], 0, set()
        final_public, error = None, None
        _append(attempt_dir / 'event_log.jsonl', {'event': 'attempt_started', 'attempt_id': attempt_id})

        def check_limits():
            if time.monotonic() >= deadline:
                raise RuntimeError('attempt wall limit exceeded')
            if _cpu() - cpu_start > limits['max_attempt_cpu_seconds']:
                raise RuntimeError('attempt combined parent/child CPU limit exceeded')
            if shutil.disk_usage(self.output_dir).free < reserve:
                raise RuntimeError('free disk reserve below registered minimum')

        def release(state):
            for event in state['feedback']:
                identity = raw_json(event)
                if identity not in seen_feedback:
                    seen_feedback.add(identity)
                    _append(attempt_dir / 'released_feedback.jsonl', event)

        try:
            world = generate(seed=cell['seed'], n=200, pool_id='evaluation', variant=cell['family'])
            world_hash = hashlib.sha256(raw_json(world)).hexdigest()
            sim = Simulator(world)
            del world
            spec = self.registration['policies'][cell['policy_id']]
            for day in range(60):
                daily = None
                for phase in ('ask', 'match'):
                    check_limits()
                    sequence += 1
                    request = sanitize_observation({'schema_version': VERSION, 'phase': phase,
                                                    'state': sim.observe(), 'memory': copy.deepcopy(memory)})
                    state = request['state']
                    release(state)
                    _append(attempt_dir / 'requests.jsonl', {'sequence': sequence, 'day': day,
                                                              'phase': phase, 'request': request})
                    call_start = time.monotonic()
                    try:
                        envelope = invoke_policy(self.workspace_root, spec['entrypoint'], spec.get('config', {}), request,
                            timeout_seconds=min(limits['invocation_wall_seconds'], deadline-time.monotonic()),
                            wire_limit_bytes=limits['wire_limit_bytes'],
                            cpu_seconds=min(limits['invocation_wall_seconds'], max(.01, limits['max_attempt_cpu_seconds']-(_cpu()-cpu_start))),
                            rss_gib=limits['max_rss_gib'])
                    except Exception as exc:
                        elapsed = time.monotonic() - call_start
                        invocation_times.append(elapsed)
                        fallback_count += bool(getattr(exc, 'telemetry', {}).get('fallback'))
                        _append(attempt_dir / 'invocations.jsonl', {'sequence': sequence, 'day': day, 'phase': phase,
                            'telemetry': dict(getattr(exc, 'telemetry', {}), elapsed_seconds=elapsed), 'error': str(exc),
                            'stdout': getattr(exc, 'stdout', ''), 'stderr': getattr(exc, 'stderr', '')})
                        raise
                    elapsed = time.monotonic() - call_start
                    invocation_times.append(elapsed)
                    envelope['telemetry']['function_elapsed_seconds'] = envelope['telemetry'].get('elapsed_seconds')
                    envelope['telemetry']['elapsed_seconds'] = elapsed
                    envelope['telemetry']['cold_elapsed_seconds'] = elapsed
                    fallback_count += bool(envelope['telemetry'].get('fallback'))
                    _append(attempt_dir / 'invocations.jsonl', {'sequence': sequence, 'day': day, 'phase': phase,
                                                               'telemetry': envelope['telemetry']})
                    response = envelope['response']
                    _append(attempt_dir / 'responses.jsonl', {'sequence': sequence, 'day': day, 'phase': phase, 'response': response})
                    if elapsed > limits['invocation_wall_seconds']:
                        raise PublicProtocolError('cold invocation exceeds registered wall limit')
                    expected = {'memory', 'asks' if phase == 'ask' else 'pairs'}
                    if set(response) != expected:
                        raise PublicProtocolError('policy response keys do not match phase')
                    valid_memory, errors, _ = validate_policy_memory(response['memory'])
                    if not valid_memory:
                        raise PublicProtocolError('; '.join(errors))
                    available = {m['member_id'] for m in state['members'] if m['available']}
                    if phase == 'ask':
                        action = response['asks']
                        ok, errors, cost = validate_ask_batch(action, available, state['ask_budget_remaining'])
                        if not ok:
                            raise PublicProtocolError('; '.join(errors))
                        members, neighbors, _ = build_legal_graph(state)
                        candidates = extract_candidate_set(members, neighbors)
                        hard_count = sum(a['field'] == 'constraints' for a in action)
                        daily = {'day': day, 'hard_asks_count': hard_count,
                                 'soft_asks_count': len(action)-hard_count,
                                 'budget_remaining_after_hard': state['ask_budget_remaining']-hard_count*3,
                                 'candidate_count': len(candidates),
                                 'candidates': [candidates[k] for k in sorted(candidates)],
                                 'baseline_preanswer_pairs': baseline_match(state)}
                        answers = sim.resolve_asks(action)
                        _append(attempt_dir / 'query_answers.jsonl', {'sequence': sequence, 'day': day, 'answers': answers})
                    else:
                        action = response['pairs']
                        ok, errors = validate_match_batch(action, available, state['introductions'], state['members'])
                        if not ok:
                            raise PublicProtocolError('; '.join(errors))
                        daily['actual_postanswer_pairs'] = copy.deepcopy(action)
                        pre = {tuple(sorted(p)) for p in daily['baseline_preanswer_pairs']}
                        post = {tuple(sorted(p)) for p in action}
                        daily['match_changed'] = pre != post
                        daily['changed_pair_count'] = len(pre.symmetric_difference(post))
                        _append(attempt_dir / 'daily_telemetry.jsonl', daily)
                        sim.advance(action)
                    digest.update(raw_json([phase, day, action]))
                    memory = copy.deepcopy(response['memory'])
                    _append(attempt_dir / 'actions.jsonl', {'sequence': sequence, 'day': day, 'phase': phase,
                                                           'request': request, 'response': response, 'elapsed_seconds': elapsed})
                    check_limits()
            arrived = copy.deepcopy(sim.observe()['members'])
            _write(attempt_dir / 'arrived_by59.json', arrived)
            while sim.day < 99:
                check_limits()
                release(sim.observe())
                sim.advance([])
            snapshot = sim.observe()
            release(snapshot)
            final_public = {'members': snapshot['members'], 'introductions': snapshot['introductions'],
                            'feedback': snapshot['feedback'], 'ask_log': snapshot['ask_log'],
                            'observed_day_cutoff': 99, 'final_day': 100}
            sim.advance([])
            if sim.day != 100 or sequence != 120:
                raise PublicProtocolError('horizon mismatch')
            _write(attempt_dir / 'final_public.json', final_public)
            metrics = compute_run_metrics(final_public['introductions'], final_public['ask_log'],
                feedback=final_public['feedback'], arrived_members=arrived, observed_day=99,
                is_valid=True, validation_errors=[])
            check_limits()
        except Exception as exc:
            error = f'{type(exc).__name__}: {exc}'
            metrics = {'valid': False, 'error': error}
        valid = error is None
        status = {'status': 'completed' if valid else 'failed', 'is_valid': valid,
                  'error': error, 'sequence': sequence, 'attempt_id': attempt_id}
        _append(attempt_dir / 'event_log.jsonl', dict(status, event='attempt_finished'))
        _write(attempt_dir / 'status.json', status)
        _sync_directory(attempt_dir)
        hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(attempt_dir.iterdir()) if p.is_file()}
        record = {'cell': copy.deepcopy(cell), 'registration_sha256': registration_hash,
                  'source_sha256': copy.deepcopy(self.registration['source_manifest']),
                  'attempt_id': attempt_id, 'attempt_relative_path': str(attempt_dir.relative_to(self.output_dir)),
                  'artifact_hashes': hashes, 'world_sha256': world_hash,
                  'action_sha256': digest.hexdigest(), 'metrics': metrics, 'is_valid': valid, 'error': error,
                  'wall_seconds': time.monotonic()-started, 'cpu_seconds': _cpu()-cpu_start,
                  'invocation_count': len(invocation_times), 'invocation_seconds_total': sum(invocation_times),
                  'invocation_seconds_max': max(invocation_times, default=0), 'fallback_count': fallback_count,
                  'rss_raw': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  'rss_units': 'bytes' if os.uname().sysname == 'Darwin' else 'KiB'}
        # Exclusive creation makes a completed or failed cell immutable; retries require a new registration cell.
        temporary = self.commits_dir / ('.' + key + '.' + attempt_id + '.tmp')
        _write(temporary, record)
        try:
            os.link(temporary, commit_file)
        finally:
            temporary.unlink()
        _sync_directory(self.commits_dir)
        return record
