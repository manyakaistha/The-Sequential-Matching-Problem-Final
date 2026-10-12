"""Audit every committed invocation without executing a policy or fitting a model.

Privileged initial worlds are confined to this offline transition audit. No new
worlds or evaluated actions are generated. All policy inputs are checked against
the public observation reconstructed from preceding saved actions.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import resource
import time

from kit import Simulator

ROOT = Path('results/research5')


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def audit(row):
    start = time.process_time()
    for path, expected in row['audit_files'].items():
        assert Path(path).stat().st_size == expected['bytes'], path
        assert sha(path) == expected['sha256'], path
    with gzip.open(row['privileged_audit_log'], 'rt') as stream:
        private = [json.loads(line) for line in stream]
    assert len(private) == 2
    assert [r['kind'] for r in private] == ['initial_world', 'final_simulator_state']
    assert all(r['privileged'] is True for r in private)
    world = private[0]['world']
    assert world['seed'] == row['seed'] and world['variant'] == row['variant']
    assert len(world['members']) == 200
    sim = Simulator(world)
    actions, snapshots, match_states, latencies = [], [], [], []
    memory = None
    peak_request = peak_memory = 0
    digest = hashlib.sha256()
    with gzip.open(row['full_invocation_log'], 'rt') as stream:
        for seq in range(1, 121):
            incoming = json.loads(next(stream))
            outgoing = json.loads(next(stream))
            assert incoming['kind'] == 'request' and outgoing['kind'] == 'response'
            assert incoming['sequence'] == outgoing['sequence'] == seq
            phase = 'ask' if seq % 2 else 'match'
            request = incoming['request']
            assert request['phase'] == phase and request['state']['day'] == (seq - 1) // 2
            assert request['state'] == sim.observe(), 'Observation/history discrepancy'
            assert request['memory'] == memory
            assert set(request) == {'schema_version', 'phase', 'state', 'memory'}
            assert request['schema_version'] == world['schema_version']
            assert incoming['timeout_seconds'] == 10
            assert incoming['command'][-2:] == ['--candidate', row['policy']]
            request_size = len(json.dumps(request, allow_nan=False).encode())
            assert request_size <= 1048576
            peak_request = max(peak_request, request_size)
            response = outgoing['response']
            key = 'asks' if phase == 'ask' else 'pairs'
            assert set(response) == {key, 'memory'} and isinstance(response[key], list)
            memory = response['memory']
            size = len(json.dumps(memory, allow_nan=False).encode())
            assert size < 1048576
            peak_memory = max(peak_memory, size)
            assert 0 <= outgoing['elapsed_seconds'] < 10
            latencies.append(outgoing['elapsed_seconds'])
            act = response[key]
            actions.append([phase, sim.day, act])
            digest.update(json.dumps([phase, sim.day, act], sort_keys=True).encode())
            if phase == 'ask':
                sim.resolve_asks(act)
            else:
                if row['policy'] == 'greedy':
                    match_states.append({'day': sim.day,
                        'state': {k: v for k, v in request['state'].items() if k != 'ask_log'}})
                by_id = {m['member_id']: m for m in request['state']['members']}
                for a, b in act:
                    snapshots.append({'user_a': a, 'user_b': b, 'assigned_day': sim.day,
                        'member_a': by_id[a], 'member_b': by_id[b],
                        'prior_feedback': len(request['state']['feedback'])})
                sim.advance(act)
        assert next(stream, None) is None, 'Extra invocation/error record'
    assert sim.day == 60
    for _ in range(40):
        sim.advance([])
    assert sim.day == 100
    final = {k: sorted(v) if isinstance(v, set) else v for k, v in vars(sim).items()}
    assert json.loads(json.dumps(final)) == private[1]['state'], 'Final simulator state discrepancy'
    assert peak_request == row['peak_request_bytes'] and peak_memory == row['peak_memory_bytes']
    assert latencies == row['inference_latencies'] and len(latencies) == row['invocation_count']
    assert digest.hexdigest() == row['action_sha256']
    canonical = [[phase, day, sorted([sorted(a) if phase == 'match' else a for a in acts],
                 key=lambda a: json.dumps(a, sort_keys=True))] for phase, day, acts in actions]
    semantic = hashlib.sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest()
    assert semantic == row['semantic_action_sha256']
    trace = json.loads(Path(row['trace']).read_text())
    assert trace['actions'] == actions and trace['assignment_snapshots'] == snapshots
    assert trace['match_states'] == match_states
    assert trace['introductions'] == sim.introductions
    assert trace['completed_feedback'] == sim.receive_feedback()
    assert trace['semantic_action_sha256'] == semantic
    assert (trace['policy'], trace['seed'], trace['variant']) == (row['policy'], row['seed'], row['variant'])
    # Independent grouping and public-label qualification; do not call metrics().
    events = {}
    for event in sim.receive_feedback():
        events.setdefault(event['introduction_id'], []).append(event)
    counts = Counter(assignments=len(sim.introductions), ask_cost=sim.asks_total)
    for intro in sim.introductions:
        es = events[intro['introduction_id']]
        first = [e for e in es if e['event'] == 'introduction_response']
        assert len(first) == 2
        both_response = all(e['value'] is not None for e in first)
        counts['both_first_response'] += both_response
        counts['first_nonresponse_dyads'] += not both_response
        mutual = all(e['value'] == 'yes' for e in first)
        counts['first_rejection_dyads'] += both_response and not mutual
        counts['mutual_acceptances'] += mutual
        ds = [e for e in es if e['event'] == 'date_happened']
        if not mutual:
            assert not ds
            continue
        assert len(ds) == 1
        counts['date_cancellations'] += ds[0]['value'] is False
        if not ds[0]['value']:
            continue
        counts['dates'] += 1
        ss = [e for e in es if e['event'] == 'second_meeting_intention']
        assert len(ss) == 2
        both_second = all(e['value'] is not None for e in ss)
        counts['both_second_response'] += both_second
        counts['second_nonresponse_dyads'] += not both_second
        positive = all(e['value'] == 'yes' for e in ss)
        counts['negative_second_dyads'] += both_second and not positive
        if positive:
            counts['positive_pause_dyads'] += 1
            qdate = ds[0]['occurred_day'] - intro['assigned_day'] <= 30
            qseconds = all(e['occurred_day'] - ds[0]['occurred_day'] <= 3 for e in ss)
            counts['date_deadline_loss'] += not qdate
            counts['feedback_deadline_loss_given_date_qualified'] += qdate and not qseconds
            counts['mutual_second_meeting_intention'] += qdate and qseconds
    counts['arrived_members'] = sum(m['arrived_day'] <= 59 for m in sim.members.values())
    counts['served_members'] = len({u for intro in sim.introductions for u in (intro['user_a'], intro['user_b'])})
    for key in ('assignments', 'ask_cost', 'mutual_acceptances', 'dates',
                'mutual_second_meeting_intention', 'arrived_members', 'served_members'):
        assert counts[key] == row[key], (key, counts[key], row[key])
    assert row['msmi_per_100_arrived_members'] == 100 * counts['mutual_second_meeting_intention'] / counts['arrived_members']
    return {'policy': row['policy'], 'seed': row['seed'], 'variant': row['variant'],
            'valid': True, 'invocations': 120, 'counts': dict(counts),
            'trace_sha256': sha(row['trace']), 'cpu_seconds': time.process_time() - start}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=6)
    args = parser.parse_args()
    assert 1 <= args.workers <= 6
    target = ROOT / 'log_checks.json'
    assert not target.exists(), 'Refuse audit overwrite'
    data = json.loads((ROOT / 'confirmation.json').read_text())
    assert data['complete'] and len(data['episodes']) == 5160
    started = time.perf_counter()
    cpu = resource.getrusage(resource.RUSAGE_CHILDREN)
    rows, errors = [], []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs = {pool.submit(audit, row): (row['policy'], row['seed'], row['variant']) for row in data['episodes']}
        for future in as_completed(jobs):
            try:
                rows.append(future.result())
            except Exception as error:
                errors.append({'cell': jobs[future], 'error': type(error).__name__ + ': ' + str(error)})
            if (len(rows) + len(errors)) % 100 == 0:
                print(f'Log audit {len(rows)+len(errors)}/5160; errors={len(errors)}', flush=True)
    end = resource.getrusage(resource.RUSAGE_CHILDREN)
    totals = {policy: dict(sum((Counter(r['counts']) for r in rows if r['policy'] == policy), Counter()))
              for policy in ('greedy', 'population_control')}
    result = {'started_scope': 'All committed policy inputs, outputs, public transitions, privileged final states and prospective traces; no policy inference or newly generated worlds.',
              'source_sha256': sha(__file__), 'confirmation_sha256': sha(ROOT / 'confirmation.json'),
              'completed_utc': datetime.now(timezone.utc).isoformat(), 'valid': len(rows) == 5160 and not errors,
              'checked_episodes': len(rows), 'checked_invocations': sum(r['invocations'] for r in rows),
              'errors': errors, 'rows': rows, 'totals': totals,
              'wall_seconds': time.perf_counter()-started,
              'child_cpu_seconds': end.ru_utime+end.ru_stime-cpu.ru_utime-cpu.ru_stime}
    target.write_text(json.dumps(result, indent=2) + '\n')
    print('All log checks passed:', result['valid'], flush=True)
    if not result['valid']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
