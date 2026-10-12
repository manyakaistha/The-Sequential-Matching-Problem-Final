"""Full evaluator episodes with observation JSON roundtrips and prospective traces."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
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
    latencies, requests, snapshots, actions, sims, match_states = [], [], [], [], [], []
    original = evaluate.invoke
    initial_fallbacks = policy_module.FALLBACK_COUNT
    class Recorder(Simulator):
        def __init__(self, world):
            super().__init__(world)
            sims.append(self)
    def invoke(command, request, timeout=10):
        raw = json.dumps(request, allow_nan=False)
        requests.append(len(raw.encode()))
        if requests[-1] > evaluate.LIMIT:
            raise ValueError('oversized request')
        started = time.perf_counter()
        if execution == 'subprocess':
            response, elapsed = original(command, request, timeout)
        else:
            response = decide(evaluate.strict_json(raw), CANDIDATES[name])
            response = evaluate.validate_response(evaluate.strict_json(json.dumps(response, allow_nan=False)), request['phase'])
            elapsed = time.perf_counter() - started
        if elapsed > timeout or len(json.dumps(response['memory']).encode()) >= evaluate.LIMIT:
            raise ValueError('resource failure')
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
    finally:
        evaluate.invoke = original
    row.update(policy=name, seed=seed, variant=variant, configuration=CANDIDATES[name],
               execution=execution, wall_seconds=time.perf_counter()-started,
               inference_latencies=latencies, peak_request_bytes=max(requests, default=0),
               peak_memory_bytes=2, invocation_count=len(latencies), failure_count=int(not row['valid']),
               optimized_fallback_count=policy_module.FALLBACK_COUNT-initial_fallbacks if execution=='in_process_json' else None)
    if trace_dir:
        sim = sims[0]
        canonical = [[phase, day, sorted([sorted(a) if phase == 'match' else a for a in acts], key=lambda a: json.dumps(a, sort_keys=True))] for phase, day, acts in actions]
        trace = dict(policy=name, seed=seed, variant=variant, actions=actions,
                     assignment_snapshots=snapshots, match_states=match_states, introductions=sim.introductions,
                     completed_feedback=sim.receive_feedback(),
                     semantic_action_sha256=hashlib.sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest(),
                     boundary='Prospective observed features plus completed public events; no hidden world fields.')
        target = Path(trace_dir) / f'{name}_{variant}_{seed}.json'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(trace, allow_nan=False)+'\n')
        row.update(trace=str(target), semantic_action_sha256=trace['semantic_action_sha256'])
    return row


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--policies', required=True)
    p.add_argument('--seeds', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--traces')
    p.add_argument('--workers', type=int, default=2)
    p.add_argument('--execution', choices=['in_process_json', 'subprocess'], default='in_process_json')
    p.add_argument('--variants', default='all')
    args = p.parse_args()
    if not 1 <= args.workers <= 2:
        p.error('one or two workers only')
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
                    planned_episodes=len(jobs), planned_seeds=list(range(lo,hi+1)),
                    planned_policies=names, planned_variants=list(variants),
                    command=sys.argv, decision_days=60, follow_up_days=40)
    rows = []
    target.parent.mkdir(parents=True, exist_ok=True)
    def save():
        rows.sort(key=lambda r: (r['seed'], r['variant'], r['policy']))
        tmp = target.with_suffix('.tmp')
        tmp.write_text(json.dumps(dict(metadata, complete=len(rows)==len(jobs), episodes=rows), indent=2)+'\n')
        tmp.replace(target)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(run, job) for job in jobs]):
            row = future.result()
            rows.append(row)
            save()
            print(row['policy'], row['seed'], row['variant'], row.get('mutual_second_meeting_intention'), row['valid'], flush=True)
    save()


if __name__ == '__main__':
    main()
