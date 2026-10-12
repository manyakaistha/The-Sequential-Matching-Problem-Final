"""Round-five recorder: full policy I/O plus separate privileged audit state.

Derived from sealed research4.benchmark; decision code remains unchanged.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import gzip
import traceback
import json
from pathlib import Path
import sys
import time
import evaluate
from kit import Simulator, generate
from research4.policy import CANDIDATES, decide
from research4 import policy as policy_module


def hashes():
    paths = ['kit.py', 'evaluate.py', 'research/terminal_model.py',
             'research3/policy.py', 'research3/model_candidates.py', 'research4/candidates.py', 'research4/policy.py', 'research4/benchmark.py']
    return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}


def run(job):
    name, seed, variant, trace_dir, execution = job
    if execution != 'in_process_json':
        raise ValueError('This full recorder is for registered in-process execution; use the independent replicator for subprocess checks')
    latencies, requests, snapshots, actions, sims, match_states, memories = [], [], [], [], [], [], []
    original = evaluate.invoke
    initial_fallbacks = policy_module.FALLBACK_COUNT
    if not trace_dir:
        raise ValueError('Full logging requires a trace directory')
    audit_root = Path(trace_dir).parent / (Path(trace_dir).name + '_full')
    audit_root.mkdir(parents=True, exist_ok=True)
    stem = f'{name}_{variant}_{seed}'
    public_path = audit_root / (stem + '.invocations.jsonl.gz')
    private_path = audit_root / (stem + '.privileged.jsonl.gz')
    public = gzip.open(public_path, 'xt', encoding='utf-8', compresslevel=1)
    private = gzip.open(private_path, 'xt', encoding='utf-8', compresslevel=1)
    def emit(stream, record):
        stream.write(json.dumps(record, allow_nan=False) + '\n')
        stream.flush()
    def diagnostic_repr(value):
        try:
            return repr(value)
        except Exception as error:
            return '<unrepresentable ' + type(value).__name__ + ': ' + type(error).__name__ + '>'
    def diagnostic_json(value):
        try:
            return json.dumps(value, default=diagnostic_repr)
        except Exception:
            return diagnostic_repr(value)
    sequence = 0
    def audit_state(sim):
        return {k: sorted(v) if isinstance(v, set) else v for k,v in vars(sim).items()}

    class Recorder(Simulator):
        def __init__(self, world):
            emit(private, {'kind':'initial_world', 'privileged':True, 'world':world})
            super().__init__(world)
            sims.append(self)
    def invoke(command, request, timeout=10):
        nonlocal sequence
        sequence += 1
        # Persist complete input before inference; disk I/O is outside policy timing.
        emit(public, {'kind':'request', 'sequence':sequence, 'command':command,
                      'timeout_seconds':timeout, 'request':request,
                      'utc':datetime.now(timezone.utc).isoformat()})
        response = None
        started = time.perf_counter()
        try:
            raw = json.dumps(request, allow_nan=False)
            requests.append(len(raw.encode()))
            if requests[-1] > evaluate.LIMIT:
                raise ValueError('oversized request')
            started = time.perf_counter()  # Same inference boundary as sealed round four.
            if execution == 'subprocess':
                response, elapsed = original(command, request, timeout)
            else:
                response = decide(evaluate.strict_json(raw), CANDIDATES[name])
                response = evaluate.validate_response(evaluate.strict_json(json.dumps(response, allow_nan=False)), request['phase'])
                elapsed = time.perf_counter() - started
            if elapsed > timeout or len(json.dumps(response['memory']).encode()) >= evaluate.LIMIT:
                raise ValueError('resource failure')
        except BaseException as error:
            emit(public, {'kind':'invocation_error', 'sequence':sequence,
                          'elapsed_seconds':time.perf_counter()-started,
                          'response_if_available_repr':diagnostic_repr(response),
                          'response_if_available_json':diagnostic_json(response),
                          'error_type':type(error).__name__, 'error':str(error),
                          'traceback':traceback.format_exc()})
            raise
        emit(public, {'kind':'response', 'sequence':sequence, 'response':response,
                      'elapsed_seconds':elapsed,
                      'utc':datetime.now(timezone.utc).isoformat()})
        memories.append(len(json.dumps(response['memory'], allow_nan=False).encode()))
        latencies.append(elapsed)
        key = 'asks' if request['phase'] == 'ask' else 'pairs'
        actions.append([request['phase'], request['state']['day'], response[key]])
        if trace_dir and key == 'pairs':
            if name == 'greedy':
                match_states.append({'day': request['state']['day'], 'state': {k:v for k,v in request['state'].items() if k != 'ask_log'}})
            by_id = {m['member_id']: m for m in request['state']['members']}
            for a, b in response[key]:
                snapshots.append({'user_a': a, 'user_b': b, 'assigned_day': request['state']['day'],
                                  'member_a': by_id[a], 'member_b': by_id[b],
                                  'prior_feedback': len(request['state']['feedback'])})
        return response, elapsed
    evaluate.invoke = invoke
    started = time.perf_counter()
    try:
        row = evaluate.episode(generate(seed, 200, 'evaluation', variant),
                               [sys.executable, '-m', 'research4.policy', '--candidate', name], simulator_class=Recorder)
    except Exception as error:
        row = {'valid': False, 'error': type(error).__name__ + ': ' + str(error)}
        emit(public, {'kind':'episode_error', 'error':row['error'], 'traceback':traceback.format_exc()})
    finally:
        evaluate.invoke = original
        try:
            if sims:
                emit(private, {'kind':'final_simulator_state', 'privileged':True,
                               'state':audit_state(sims[0])})
        finally:
            public.close()
            private.close()
    row.update(policy=name, seed=seed, variant=variant, configuration=CANDIDATES[name],
               execution=execution, wall_seconds=time.perf_counter()-started,
               inference_latencies=latencies, peak_request_bytes=max(requests, default=0),
               peak_memory_bytes=max(memories, default=0), invocation_count=len(latencies), failure_count=int(not row['valid']),
               optimized_fallback_count=policy_module.FALLBACK_COUNT-initial_fallbacks if execution=='in_process_json' else None)
    if trace_dir:
        sim = sims[0] if sims else None
        canonical = [[phase, day, sorted([sorted(a) if phase == 'match' else a for a in acts], key=lambda a: json.dumps(a, sort_keys=True))] for phase, day, acts in actions]
        trace = dict(policy=name, seed=seed, variant=variant, actions=actions,
                     assignment_snapshots=snapshots, match_states=match_states, introductions=sim.introductions if sim else [],
                     completed_feedback=sim.receive_feedback() if sim else [],
                     semantic_action_sha256=hashlib.sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest(),
                     boundary='Prospective observed features plus completed public events; no hidden world fields.')
        target = Path(trace_dir) / f'{name}_{variant}_{seed}.json'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(trace, allow_nan=False)+'\n')
        row.update(trace=str(target), semantic_action_sha256=trace['semantic_action_sha256'])
    row.update(full_invocation_log=str(public_path), privileged_audit_log=str(private_path),
               audit_files={str(p): {'bytes':p.stat().st_size, 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (public_path,private_path)})
    return row


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--policies', required=True)
    p.add_argument('--seeds', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--traces')
    p.add_argument('--resume-from')
    p.add_argument('--workers', type=int, default=3)
    p.add_argument('--execution', choices=['in_process_json', 'subprocess'], default='in_process_json')
    p.add_argument('--variants', default='all')
    args = p.parse_args()
    if not 1 <= args.workers <= 3:
        p.error('one to three research workers only')
    target = Path(args.output)
    if target.exists():
        raise ValueError('refuse to overwrite prior experiment')
    lo, hi = map(int, args.seeds.split(':')) if ':' in args.seeds else (int(args.seeds), int(args.seeds))
    variants = evaluate.VARIANTS if args.variants == 'all' else args.variants.split(',')
    names = args.policies.split(',')
    if not set(names) <= set(CANDIDATES) or not set(variants) <= set(evaluate.VARIANTS):
        raise ValueError('unknown candidate or variant')
    jobs = [(n, s, v, args.traces, args.execution) for s in range(lo, hi+1) for v in variants for n in names]
    metadata = dict(started_utc=datetime.now(timezone.utc).isoformat(), code_hashes=hashes(),
                    recorder_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    logging_schema='research5-full-v1', planned_episodes=len(jobs), planned_seeds=list(range(lo,hi+1)),
                    planned_policies=names, planned_variants=list(variants),
                    command=sys.argv, decision_days=60, follow_up_days=40)
    rows = []
    if args.resume_from:
        prior_path = Path(args.resume_from)
        prior = json.loads(prior_path.read_text())
        for key in ('code_hashes','planned_episodes','planned_seeds','planned_policies','planned_variants','decision_days','follow_up_days','logging_schema'):
            if prior[key] != metadata[key]:
                raise ValueError('Recovery metadata mismatch: ' + key)
        allowed = {(n,s,v) for n,s,v,_,_ in jobs}
        seen = set()
        archive = prior_path.parent
        for row in prior['episodes']:
            key = row['policy'],row['seed'],row['variant']
            if key not in allowed or key in seen:
                raise ValueError('Recovery unknown/duplicate cell')
            if row['configuration'] != CANDIDATES[row['policy']]:
                raise ValueError('Recovery configuration mismatch')
            seen.add(key)
            row['recorder_source_sha256'] = row.get('recorder_source_sha256', prior['recorder_sha256'])
            row['recovered_from'] = str(prior_path)
            for field in ('trace','full_invocation_log','privileged_audit_log'):
                original_path = Path(row[field])
                relocated = original_path if original_path.is_file() else archive / original_path.parent.name / original_path.name
                if not relocated.is_file():
                    raise ValueError('Missing archived evidence: ' + str(relocated))
                row[field] = str(relocated)
            shifted = {}
            for path, expected in row['audit_files'].items():
                moved = Path(path) if Path(path).is_file() else archive / Path(path).parent.name / Path(path).name
                if moved.stat().st_size != expected['bytes'] or hashlib.sha256(moved.read_bytes()).hexdigest() != expected['sha256']:
                    raise ValueError('Archived audit hash mismatch: ' + str(moved))
                shifted[str(moved)] = expected
            row['audit_files'] = shifted
            rows.append(row)
        jobs = [job for job in jobs if job[:3] not in seen]
        metadata['recovery'] = {'source_result':str(prior_path),
            'source_result_sha256':hashlib.sha256(prior_path.read_bytes()).hexdigest(),
            'original_metadata':{k:v for k,v in prior.items() if k != 'episodes'},
            'preserved_rows':len(rows), 'remaining_jobs':len(jobs),
            'scope':'All persisted rows retained, including failures; exact original sample. Uncommitted partial artifacts preserved in archive, missing cells recomputed.'}
    target.parent.mkdir(parents=True, exist_ok=True)
    def save():
        rows.sort(key=lambda r: (r['seed'], r['variant'], r['policy']))
        tmp = target.with_suffix('.tmp')
        tmp.write_text(json.dumps(dict(metadata, complete=len(rows)==metadata['planned_episodes'], episodes=rows), indent=2)+'\n')
        tmp.replace(target)
    save()
    started = time.perf_counter()
    recovered = len(rows)
    print(f"[START] {metadata['planned_episodes']:,} fixed episodes | {recovered} recovered | {len(jobs):,} remaining | {args.workers} workers", flush=True)
    print(f"[LOGGING] Episode summaries: {target}; full JSON logs: {Path(args.traces).name}_full/ (gzip)", flush=True)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(run, job) for job in jobs]):
            row = future.result()
            row['recorder_source_sha256'] = metadata['recorder_sha256']
            rows.append(row)
            save()
            count = len(rows); total = metadata['planned_episodes']
            elapsed = time.perf_counter()-started
            finished_here = count-recovered
            eta = elapsed * (total-count) / finished_here if finished_here else 0
            width = 28; filled = int(width*count/total)
            bar = '#' * filled + '-' * (width-filled)
            print(f"[PROGRESS] [{bar}] {count:,}/{total:,} ({100*count/total:.1f}%) | elapsed {elapsed/60:.1f}m | ETA {eta/60:.1f}m | logs saved", flush=True)
    save()
    print("[DONE] Fixed episode grid saved. Proceeding to registered analysis.", flush=True)


if __name__ == '__main__':
    main()
