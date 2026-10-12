"""Second-feedback timing intervention + deadline-integrated diagnostic.

No frozen source edits, new seeds, fitting or substituted primary policy reward.
Intervention replays use existing seed101; integrated audit reads completed rows.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
from kit import Simulator, generate
from research4.policy import CANDIDATES, decide
from research4 import policy as policy_module
from research3.analyze import interval

FAMILIES = ('development', 'sparse', 'cold_start', 'delayed', 'shift', 'drift')
PARENTS = {'coordinated_goal': 'goal_surplus_control', 'hard_priority': 'population_control',
           'response_uniform': 'response_beta_control', 'acceptance_shrinkage': 'response_uniform',
           'goal_surplus_control': 'population_control', 'response_beta_control': 'population_control'}


def counts(introductions, events):
    grouped = defaultdict(list)
    for event in events:
        grouped[event['introduction_id']].append(event)
    out = {'positive_pauses': 0, 'date_ontime_positive': 0, 'qualified': 0}
    for intro in introductions:
        es = grouped[intro['introduction_id']]
        date = [e for e in es if e['event'] == 'date_happened' and e['value'] is True]
        seconds = [e for e in es if e['event'] == 'second_meeting_intention']
        positive = len(seconds) == 2 and all(e['value'] == 'yes' for e in seconds)
        pauses = [e for e in es if e['event'] == 'pause_after_mutual_interest' and e['value'] is True]
        assert bool(pauses) == positive
        if positive:
            assert len(date) == 1
            out['positive_pauses'] += 1
            ontime = date[0]['occurred_day']-intro['assigned_day'] <= 30
            out['date_ontime_positive'] += ontime
            out['qualified'] += ontime and all(e['occurred_day']-date[0]['occurred_day'] <= 3 for e in seconds)
    return out


class TimingIntervention(Simulator):
    def __init__(self, world, lag):
        super().__init__(world)
        self.lag = lag

    def advance(self, pairs):
        old = len(self.events)
        super().advance(pairs)
        new = self.events[old:]
        dates = {e['introduction_id']: e['occurred_day'] for e in new if e['event'] == 'date_happened'}
        for event in new:
            if event['event'] == 'second_meeting_intention' and event['value'] is not None:
                event['occurred_day'] = event['observed_day'] = dates[event['introduction_id']]+self.lag
            elif event['event'] == 'pause_after_mutual_interest':
                event['occurred_day'] = event['observed_day'] = dates[event['introduction_id']]+self.lag
        # Busy release, date/acceptance/second flags and no-response reporting
        # at date+5 are untouched. No random draw is added or removed.


def replay(name, lag):
    simulator = TimingIntervention(generate(101, 200, 'evaluation', 'development'), lag)
    actions, availability = [], []
    initial = policy_module.FALLBACK_COUNT
    for _ in range(60):
        state = simulator.observe()
        availability.append([m['member_id'] for m in state['members'] if m['available']])
        request = json.loads(json.dumps({'phase': 'ask', 'state': state, 'memory': {}}))
        response = decide(request, CANDIDATES[name])
        simulator.resolve_asks(response['asks'])
        actions.append(['ask', simulator.day, response['asks']])
        request = json.loads(json.dumps({'phase': 'match', 'state': simulator.observe(), 'memory': {}}))
        response = decide(request, CANDIDATES[name])
        actions.append(['match', simulator.day, response['pairs']])
        simulator.advance(response['pairs'])
    for _ in range(40):
        simulator.advance([])
    metrics = simulator.metrics()
    stages = counts(simulator.introductions, simulator.receive_feedback())
    assert stages['qualified'] == metrics['mutual_second_meeting_intention']
    return {'policy': name, 'lag': lag, 'metrics': metrics, 'counts': stages,
            'fallback_count': policy_module.FALLBACK_COUNT-initial,
            'actions': actions, 'availability': availability,
            'introductions': simulator.introductions,
            'action_sha256': hashlib.sha256(json.dumps(actions, sort_keys=True).encode()).hexdigest()}


def interventions():
    started, results = time.process_time(), []
    for name in CANDIDATES:
        if time.process_time()-started > 55:
            raise RuntimeError('60CPU-second replay allowance nearly exhausted; no partial-success conclusion')
        fast, slow = replay(name, 1), replay(name, 5)
        assert fast['actions'] == slow['actions']
        assert fast['availability'] == slow['availability']
        assert fast['introductions'] == slow['introductions']
        assert fast['fallback_count'] == slow['fallback_count'] == 0
        assert fast['counts']['date_ontime_positive'] == slow['counts']['date_ontime_positive']
        assert fast['counts']['qualified'] == fast['counts']['date_ontime_positive']
        assert slow['counts']['qualified'] == 0
        results.append({'policy': name, 'byte_actions_equal': True, 'availability_equal': True,
                        'introduction_equal': True, 'fast': fast, 'slow': slow})
    return {'scope': 'Already-examined101 development; diagnostic alterations, not shipped reward evaluation',
            'seed': 101, 'variant': 'development', 'n_replays': len(results)*2,
            'cpu_seconds': time.process_time()-started, 'results': results}


def integrated(path):
    source = Path(path)
    data = json.loads(source.read_text())
    assert data.get('complete') is True
    seeds, policies = data['planned_seeds'], data['planned_policies']
    assert set(data['planned_variants']) == set(FAMILIES)
    assert len(data['episodes']) == len(seeds)*len(policies)*6
    assert all(r['valid'] and r['optimized_fallback_count'] == 0 for r in data['episodes'])
    assert {(r['seed'], r['variant'], r['policy']) for r in data['episodes']} == {(s, v, p) for s in seeds for v in FAMILIES for p in policies}
    rows, trace_hashes = [], {}
    for episode in data['episodes']:
        trace_path = Path(episode['trace'])
        trace = json.loads(trace_path.read_text())
        trace_hashes[str(trace_path)] = hashlib.sha256(trace_path.read_bytes()).hexdigest()
        stage = counts(trace['introductions'], trace['completed_feedback'])
        assert stage['qualified'] == episode['mutual_second_meeting_intention']
        score = 100*stage['qualified']/episode['arrived_members']
        proxy = 100*.36*stage['date_ontime_positive']/episode['arrived_members']
        assert abs(score-episode['msmi_per_100_arrived_members']) < 1e-12
        rows.append(dict(seed=episode['seed'], variant=episode['variant'], policy=episode['policy'],
                         arrived_members=episode['arrived_members'], counts=stage, actual_score=score,
                         deadline_integrated_proxy=proxy, actual_minus_proxy=score-proxy))
    by_key = {(r['seed'], r['variant'], r['policy']): r for r in rows}
    cluster = {p: {s: {metric: float(np.mean([by_key[(s, v, p)][metric] for v in FAMILIES]))
                       for metric in ('actual_score', 'deadline_integrated_proxy', 'actual_minus_proxy')}
                   for s in seeds} for p in policies}
    comparisons = [(p, 'greedy') for p in policies if p != 'greedy']
    comparisons += [(p, parent) for p, parent in PARENTS.items() if p in policies and parent in policies and parent != 'greedy']
    contrasts = {}
    for candidate, control in comparisons:
        contrasts[candidate+'_minus_'+control] = {metric: interval([cluster[candidate][s][metric]-cluster[control][s][metric] for s in seeds])
                                                 for metric in ('actual_score', 'deadline_integrated_proxy', 'actual_minus_proxy')}
    return {'input': str(source), 'input_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'trace_sha256': trace_hashes, 'n_seed_clusters': len(seeds), 'rows': rows,
            'policy_means': {p: {metric: float(np.mean([cluster[p][s][metric] for s in seeds])) for metric in cluster[p][seeds[0]]}
                             for p in policies}, 'contrasts': contrasts,
            'scope': 'Exploratory descriptive deadline-integrated trajectory proxy; registered primary unchanged; tCI/bootstrap seedclusters inherited analysis helper. Not inverse-propensity off-policy value or hidden oracle.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help='Complete screen or focused stage JSON')
    parser.add_argument('--interventions', action='store_true')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    target = Path(args.output)
    if target.exists():
        raise ValueError('refuse overwrite')
    start, cpu = datetime.now(timezone.utc).isoformat(), time.process_time()
    result = {'started_utc': start, 'command': sys.argv}
    if args.interventions:
        result['interventions'] = interventions()
    if args.input:
        result['deadline_integrated'] = integrated(args.input)
    if not args.interventions and not args.input:
        raise ValueError('specify intervention or completedinput')
    result.update(completed_utc=datetime.now(timezone.utc).isoformat(), cpu_seconds=time.process_time()-cpu,
                  source_sha256={p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
                                 for p in ('kit.py', 'research4/candidates.py', 'research4/policy.py', 'research4/deadline_audit.py')})
    target.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('deadline_integrated', 'interventions')}, indent=2))
    if 'deadline_integrated' in result:
        print(json.dumps(result['deadline_integrated']['policy_means'], indent=2))


if __name__ == '__main__':
    main()
