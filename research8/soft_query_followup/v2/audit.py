"""Independent closure audit using only public captures, never world.json.

The audit deliberately does not import the production metrics or analysis code.
Public protocol validators check action legality; endpoint reconstruction is local.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

from research8.w2.protocol import (sanitize_observation, validate_ask_batch,
                                 validate_match_batch, validate_policy_memory)
from research8.w2.public_rules import SOFT, VERSION


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _decode(raw):
    def invalid(value):
        raise ValueError('Nonfinite JSON number: ' + value)
    def unique(items):
        result = {}
        for key, value in items:
            _require(key not in result, 'Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(raw, parse_constant=invalid, object_pairs_hook=unique)


def _json(path):
    return _decode(path.read_text())


def _lines(path):
    rows = []
    for line in path.read_text().splitlines():
        _require(bool(line.strip()), 'Empty stream record')
        rows.append(_decode(line))
    return rows


def _safe(base, name):
    relative = Path(name)
    _require(isinstance(name, str) and name and not relative.is_absolute()
             and '..' not in relative.parts, 'Unsafe artifact path')
    path = base / relative
    _require(not base.is_symlink(), 'Symlink artifact root')
    cursor = base
    for part in relative.parts:
        cursor = cursor / part
        _require(not cursor.is_symlink(), 'Symlink artifact path')
    _require(path.resolve().is_relative_to(base.resolve()), 'Escaping artifact path')
    return path


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(value):
    return json.dumps(value, sort_keys=True, allow_nan=False)


def reconstruct_public(public):
    """Validate exact public schemas, chronology, then independently recount."""
    _require(set(public) == {'members', 'introductions', 'feedback', 'ask_log',
                             'observed_day_cutoff', 'final_day'}, 'Final public schema')
    _require(public['observed_day_cutoff'] == 99 and public['final_day'] == 100,
             'Final horizon mismatch')
    _require(type(public['observed_day_cutoff']) is int and type(public['final_day']) is int,
             'Final horizon types')
    state = dict(schema_version=VERSION, synthetic=True, day=100,
                 ask_budget_remaining=12,
                 **{k: public[k] for k in ('members', 'introductions', 'feedback', 'ask_log')})
    sanitize_observation(dict(schema_version=VERSION, phase='match', state=state, memory=None))
    members = {}
    for m in public['members']:
        _require(type(m['arrived_day']) is int and 0 <= m['arrived_day'] <= 100,
                 'Invalid arrival day')
        _require(m['synthetic'] is True and type(m['pool_id']) is str
                 and type(m['source']) is str and type(m['age']) is int
                 and type(m['gender']) is str and type(m['zone']) is str,
                 'Invalid public member metadata')
        members[m['member_id']] = m['arrived_day']
    denominator = {k: v for k, v in members.items() if v <= 59}
    intros, pairs, first = {}, set(), {}
    for i in public['introductions']:
        ident, a, b, day = i['introduction_id'], i['user_a'], i['user_b'], i['assigned_day']
        _require(type(ident) is str and ident not in intros and type(a) is str
                 and type(b) is str and a != b and tuple(sorted((a, b))) not in pairs,
                 'Duplicate introduction/pair or invalid endpoints')
        _require(type(day) is int and 0 <= day <= 59 and a in denominator
                 and b in denominator and max(members[a], members[b]) <= day,
                 'Introduction chronology/inventory mismatch')
        _require(type(i['response_deadline_day']) is int and i['response_deadline_day'] >= day
                 and type(i['logging_policy']) is str
                 and (i['propensity'] is None or type(i['propensity']) in (int, float)
                      and 0 <= i['propensity'] <= 1), 'Invalid introduction metadata')
        intros[ident] = i
        pairs.add(tuple(sorted((a, b))))
        for actor in (a, b):
            first[actor] = min(first.get(actor, day), day)
    events, event_keys = defaultdict(list), set()
    for e in public['feedback']:
        _require(e['introduction_id'] in intros, 'Orphan feedback')
        intro = intros[e['introduction_id']]
        name, actor, value = e['event'], e['member_id'], e['value']
        _require(name in {'introduction_response', 'date_happened',
                          'second_meeting_intention', 'pause_after_mutual_interest'},
                 'Unknown feedback event')
        key = (e['introduction_id'], name, actor)
        _require(key not in event_keys, 'Duplicate/conflicting feedback')
        event_keys.add(key)
        _require(type(e['observed_day']) is int
                 and intro['assigned_day'] <= e['observed_day'] <= 99,
                 'Unreleased/out-of-horizon feedback')
        occurred = e['occurred_day']
        _require(occurred is None or type(occurred) is int
                 and intro['assigned_day'] <= occurred <= e['observed_day'],
                 'Feedback occurrence chronology')
        if name in {'introduction_response', 'second_meeting_intention'}:
            _require(actor in (intro['user_a'], intro['user_b'])
                     and (value is None or type(value) is str and value in {'yes', 'no'}),
                     'Invalid endpoint feedback')
            _require((value is None and occurred is None and e.get('missing_reason') == 'no_response')
                     or (value is not None and occurred is not None and e.get('missing_reason') is None),
                     'Invalid response/missingness chronology')
        else:
            _require(actor is None and type(value) is bool and occurred is not None
                     and e.get('missing_reason') is None, 'Invalid dyad feedback')
        events[e['introduction_id']].append(e)
    mutual = dates = qualified = pauses = missing = 0
    for ident, intro in intros.items():
        rows = events[ident]
        endpoints = {intro['user_a'], intro['user_b']}
        rs = [e for e in rows if e['event'] == 'introduction_response']
        accepted = (len(rs) == 2 and {e['member_id'] for e in rs} == endpoints
                    and all(e['value'] == 'yes' for e in rs))
        mutual += accepted
        ds = [e for e in rows if e['event'] == 'date_happened']
        ss = [e for e in rows if e['event'] == 'second_meeting_intention']
        _require(not ds or accepted, 'Date without mutual acceptance')
        _require(not ds or ds[0]['occurred_day'] >= max(e['occurred_day'] for e in rs),
                 'Date before acceptance')
        happened = bool(ds) and ds[0]['value'] is True
        _require(not ss or happened, 'Second intention without happened date')
        _require(not ss or all(e['occurred_day'] is None
                              or e['occurred_day'] >= ds[0]['occurred_day'] for e in ss),
                 'Second intention before date')
        dates += happened
        good = (accepted and happened
                and 0 <= ds[0]['occurred_day'] - intro['assigned_day'] <= 30
                and len(ss) == 2 and {e['member_id'] for e in ss} == endpoints
                and all(e['value'] == 'yes' and e['occurred_day'] is not None
                        and 0 <= e['occurred_day'] - ds[0]['occurred_day'] <= 3 for e in ss))
        qualified += good
        pauses += not good and any(e['event'] == 'pause_after_mutual_interest'
                                  and e['value'] is True for e in rows)
        missing += sum(e.get('missing_reason') == 'no_response' for e in rows)
    hard = soft = 0
    for ask in public['ask_log']:
        _require(ask['member_id'] in denominator and type(ask['observed_day']) is int
                 and members[ask['member_id']] <= ask['observed_day'] <= 59,
                 'Ask chronology/inventory mismatch')
        _require(all(v in {'observed', 'declined'} for v in ask['statuses'].values()),
                 'Invalid answer status')
        hard += ask['field'] == 'constraints'
        soft += ask['field'] in SOFT
    n = len(denominator)
    return dict(valid=True, validation_errors=[], arrived_members=n,
                served_members=len(first), unserved_members=n-len(first),
                coverage=len(first)/n if n else 0.0, assignments=len(intros),
                mutual_acceptances=mutual, dates=dates,
                mutual_second_meeting_intention=qualified, missing_feedback=missing,
                ask_cost=3*hard+soft, msmi_per_100_arrived_members=100.0*qualified/n if n else 0.0,
                mutual_acceptances_per_100=100.0*mutual/n if n else 0.0,
                first_introduction_wait_days=sorted(first[k]-members[k] for k in first),
                total_asks=len(public['ask_log']), hard_asks=hard, soft_asks=soft,
                unqualified_pause_count=pauses, status='simulated_not_observed_product_performance')


def _audit_stream(attempt, public, invocation_limit=10):
    actions = _lines(attempt / 'actions.jsonl')
    _require(len(actions) == 120, 'Expected 120 action records')
    requests = _lines(attempt / 'requests.jsonl')
    responses = _lines(attempt / 'responses.jsonl')
    invocations = _lines(attempt / 'invocations.jsonl')
    _require(len(requests) == len(responses) == len(invocations) == 120,
             'Incomplete request/response/invocation streams')
    executed_asks, executed_pairs, daily = [], [], {}
    previous_memory = None
    digest = hashlib.sha256()
    for index, row in enumerate(actions):
        _require(set(row) == {'sequence', 'day', 'phase', 'request', 'response', 'elapsed_seconds'},
                 'Action record schema')
        day, phase = divmod(index, 2)[0], ('ask', 'match')[index % 2]
        _require(type(row['sequence']) is int and type(row['day']) is int
                 and row['sequence'] == index+1 and row['day'] == day and row['phase'] == phase,
                 'Action sequence/horizon mismatch')
        base = dict(sequence=index+1, day=day, phase=phase)
        _require(requests[index] == dict(base, request=row['request']), 'Request stream mismatch')
        _require(responses[index] == dict(base, response=row['response']), 'Response stream mismatch')
        invocation = invocations[index]
        _require(set(invocation) == {'sequence', 'day', 'phase', 'telemetry'}
                 and all(invocation[k] == v for k, v in base.items()), 'Invocation stream schema/sequence')
        timing = invocation['telemetry']
        _require(isinstance(timing, dict) and timing.get('fallback') is False,
                 'Invocation fallback detected')
        _require(type(timing.get('elapsed_seconds')) in (int, float)
                 and 0 <= timing['elapsed_seconds'] <= invocation_limit, 'Policy function timing violation')
        _require(type(timing.get('transport_elapsed_seconds')) in (int, float)
                 and 0 <= timing['transport_elapsed_seconds'] <= invocation_limit,
                 'Transport invocation timing violation')
        _require(type(row['elapsed_seconds']) in (int, float)
                 and 0 <= row['elapsed_seconds'] <= invocation_limit,
                 'Invocation timing violation')
        if 'cold_elapsed_seconds' in timing:
            _require(timing['cold_elapsed_seconds'] == row['elapsed_seconds'], 'Cold elapsed capture mismatch')
        req = sanitize_observation(row['request'])
        state, response = req['state'], row['response']
        _require(req['memory'] == previous_memory, 'Policy memory continuity mismatch')
        _require(req['phase'] == phase and state['day'] == day, 'Request capture day mismatch')
        visible = {m['member_id']: m for m in state['members']}
        expected_visible = {m['member_id']: m for m in public['members'] if m['arrived_day'] <= day}
        _require(set(visible) == set(expected_visible), 'Incomplete public member capture')
        for ident, member in visible.items():
            for key in ('member_id', 'pool_id', 'synthetic', 'age', 'gender', 'zone', 'arrived_day', 'source'):
                _require(member[key] == expected_visible[ident][key], 'Public member metadata mismatch')
            _require(all(v is None or type(v) is int and 0 <= v <= day
                         for v in member['field_observed_day'].values()), 'Future questionnaire release')
        _require(isinstance(response, dict) and set(response) == ({'asks', 'memory'} if phase == 'ask'
                                                                else {'pairs', 'memory'}), 'Response schema')
        ok, errs, _ = validate_policy_memory(response['memory'])
        _require(ok, 'Invalid response memory: '+str(errs))
        previous_memory = response['memory']
        available = {m['member_id'] for m in state['members'] if m['available']}
        if phase == 'ask':
            action = response['asks']
            _require(state['ask_budget_remaining'] == 12, 'Daily ask budget did not reset')
            ok, errs, cost = validate_ask_batch(action, available, state['ask_budget_remaining'])
            remaining_budget = 12-cost
            hard = sum(a['field'] == 'constraints' for a in action)
            daily[day] = dict(hard_asks_count=hard, soft_asks_count=len(action)-hard,
                              budget_remaining_after_hard=state['ask_budget_remaining']-3*hard)
            executed_asks.extend((day, a['member_id'], a['field']) for a in action)
        else:
            action = response['pairs']
            _require(state['ask_budget_remaining'] == remaining_budget, 'Post-answer budget mismatch')
            ok, errs = validate_match_batch(action, available, state['introductions'], state['members'])
            daily[day]['actual_postanswer_pairs'] = action
            executed_pairs.extend((day, tuple(sorted(p))) for p in action)
        _require(ok, 'Illegal action: '+str(errs))
        digest.update(json.dumps([phase, day, action], allow_nan=False, sort_keys=True).encode())
        # Captures must contain exact cumulative records already publicly released.
        for key in ('introductions', 'feedback', 'ask_log'):
            _require(all(_canonical(r) in {_canonical(x) for x in public[key]} for r in state[key]),
                     'Request contains record absent from final public artifact')
        expected_intros = [i for i in public['introductions'] if i['assigned_day'] < day]
        expected_feedback = [e for e in public['feedback'] if e['observed_day'] <= day]
        expected_asks = [a for a in public['ask_log'] if a['observed_day'] < day
                         or phase == 'match' and a['observed_day'] == day]
        for key, expected in [('introductions', expected_intros), ('feedback', expected_feedback),
                              ('ask_log', expected_asks)]:
            _require(Counter(map(_canonical, state[key])) == Counter(map(_canonical, expected)),
                     'Incomplete/noncausal public request '+key)
    _require(Counter(executed_asks) == Counter((a['observed_day'], a['member_id'], a['field'])
                                              for a in public['ask_log']), 'Executed ask mismatch')
    _require(Counter(executed_pairs) == Counter((i['assigned_day'], tuple(sorted((i['user_a'], i['user_b']))))
                                               for i in public['introductions']), 'Executed match mismatch')
    if (attempt / 'query_answers.jsonl').exists():
        answers = _lines(attempt / 'query_answers.jsonl')
        _require(len(answers) == 60, 'Answer stream incomplete')
        for day, row in enumerate(answers):
            _require(set(row) == {'day', 'sequence', 'answers'} and row['day'] == day
                     and row['sequence'] == day*2+1, 'Answer stream sequence/schema')
            _require(row['answers'] == [a for a in public['ask_log'] if a['observed_day'] == day],
                     'Answer stream mismatch')
    if (attempt / 'daily_telemetry.jsonl').exists():
        telemetry = _lines(attempt / 'daily_telemetry.jsonl')
        _require(len(telemetry) == 60, 'Daily telemetry incomplete')
        for day, row in enumerate(telemetry):
            _require(row['day'] == day, 'Daily telemetry sequence')
            for key, value in daily[day].items():
                _require(row[key] == value, 'Daily telemetry mismatch '+key)
            baseline = {tuple(sorted(p)) for p in row['baseline_preanswer_pairs']}
            actual = {tuple(sorted(p)) for p in row['actual_postanswer_pairs']}
            _require(row['match_changed'] == (baseline != actual)
                     and row['changed_pair_count'] == len(baseline ^ actual), 'Pair-change telemetry mismatch')
            _require(row['candidate_count'] == len(row['candidates']), 'Candidate telemetry mismatch')
    if (attempt / 'released_feedback.jsonl').exists():
        _require(Counter(map(_canonical, _lines(attempt / 'released_feedback.jsonl')))
                 == Counter(map(_canonical, public['feedback'])), 'Released feedback stream mismatch')
    return digest.hexdigest()


def audit_run(output, registration_path):
    output, registration_path = Path(output), Path(registration_path)
    reg = _json(registration_path)
    if reg.get('schema_version') == 'R8-evidence-v2':
        # Public-event reconstruction remains independent of the main metrics.
        # Actual campaigns must additionally pass the production freeze contract.
        from .registration import verify_registration
        verify_registration(reg)
    digest_payload = {k: v for k, v in reg.items() if k != 'registration_sha256'}
    registration_digest = hashlib.sha256(json.dumps(digest_payload, sort_keys=True,
                                                     indent=2, allow_nan=False).encode()).hexdigest()
    _require(reg.get('registration_sha256') == registration_digest, 'Invalid registration self digest')
    expected = {}
    for cell in reg['cells']:
        _require(cell['cell_key'] not in expected, 'Duplicate registered cell')
        expected[cell['cell_key']] = cell
    _require(bool(expected), 'Empty registered grid')
    if {'ordered_seed_list', 'families', 'policy_ids', 'stage_id'} <= set(reg):
        import itertools
        grid = [dict(stage_id=reg['stage_id'], seed=s, family=f, policy_id=p,
                     cell_key=f"{reg['stage_id']}_{s}_{f}_{p}")
                for s, f, p in itertools.product(reg['ordered_seed_list'], reg['families'], reg['policy_ids'])]
        _require(reg['cells'] == grid and reg['total_cells'] == len(grid), 'Registered grid metadata mismatch')
    commits, worlds, denoms, sources = {}, defaultdict(set), defaultdict(set), set()
    for path in sorted((output / 'commits').glob('*.json')):
        _require(not path.is_symlink(), 'Symlink commit')
        row = _json(path)
        cell = row['cell']
        key = cell['cell_key']
        _require(key in expected and key not in commits and cell == expected[key], 'Unexpected/duplicate cell metadata')
        _require(path.stem == key, 'Commit filename/cell mismatch')
        _require(row['is_valid'] is True and row['metrics']['valid'] is True
                 and row.get('error') is None, 'Invalid cell commit')
        _require(row['registration_sha256'] == registration_digest, 'Registration digest mismatch')
        _require(row['source_sha256'] == reg['source_manifest'] and bool(row['source_sha256']),
                 'Registered source digest mismatch')
        sources.add(_canonical(row['source_sha256']))
        attempt = _safe(output, row['attempt_relative_path'])
        _require(attempt.is_dir(), 'Missing attempt directory')
        hashes = row['artifact_hashes']
        required_files = {'actions.jsonl', 'final_public.json', 'requests.jsonl', 'responses.jsonl',
                          'invocations.jsonl', 'query_answers.jsonl', 'daily_telemetry.jsonl',
                          'released_feedback.jsonl', 'event_log.jsonl', 'status.json', 'arrived_by59.json'}
        _require(isinstance(hashes, dict) and required_files <= set(hashes),
                 'Required artifact hashes missing')
        descendants = list(attempt.rglob('*'))
        _require(all(not p.is_symlink() for p in descendants), 'Symlink attempt artifact')
        actual_files = {str(p.relative_to(attempt)) for p in descendants if p.is_file()}
        _require(actual_files == set(hashes), 'Artifact hash coverage mismatch')
        for name, digest in hashes.items():
            artifact = _safe(attempt, name)
            _require(artifact.is_file() and _sha(artifact) == digest, 'Artifact hash mismatch: '+name)
        public = _json(attempt / 'final_public.json')
        status = _json(attempt / 'status.json')
        expected_status = dict(status='completed', is_valid=True, error=None,
                               sequence=120, attempt_id=row['attempt_id'])
        _require(status == expected_status, 'Terminal status mismatch')
        event_log = _lines(attempt / 'event_log.jsonl')
        _require(event_log == [dict(event='attempt_started', attempt_id=row['attempt_id']),
                               dict(expected_status, event='attempt_finished')], 'Lifecycle event log mismatch')
        inventory = _json(attempt / 'arrived_by59.json')
        _require(isinstance(inventory, list), 'Arrival inventory schema')
        sanitize_observation(dict(schema_version=VERSION, phase='match', memory=None,
                                  state=dict(schema_version=VERSION, synthetic=True, day=60,
                                             ask_budget_remaining=12, members=inventory,
                                             introductions=[], feedback=[], ask_log=[])))
        _require({m['member_id']: m['arrived_day'] for m in inventory}
                 == {m['member_id']: m['arrived_day'] for m in public['members'] if m['arrived_day'] <= 59}
                 and len(inventory) == len({m['member_id'] for m in inventory}), 'Public arrival inventory mismatch')
        metrics = reconstruct_public(public)
        for metric, value in metrics.items():
            _require(metric in row['metrics'] and row['metrics'][metric] == value,
                     'Independent metric mismatch: '+metric)
        limit = reg.get('resource_forecast', {}).get('invocation_wall_seconds', 10)
        _require(0 < limit <= 10, 'Invalid registered invocation limit')
        _require(_audit_stream(attempt, public, limit) == row['action_sha256'], 'Action digest mismatch')
        actions = _lines(attempt / 'actions.jsonl')
        elapsed = [a['elapsed_seconds'] for a in actions]
        _require(row['invocation_count'] == 120 and row['fallback_count'] == 0
                 and row['invocation_seconds_total'] == sum(elapsed)
                 and row['invocation_seconds_max'] == max(elapsed), 'Invocation aggregate mismatch')
        group = (cell['seed'], cell['family'])
        _require(isinstance(row['world_sha256'], str) and len(row['world_sha256']) == 64,
                 'Missing world identity digest')
        worlds[group].add(row['world_sha256'])
        denoms[group].add(metrics['arrived_members'])
        commits[key] = row
    _require(set(commits) == set(expected), 'Incomplete registered grid')
    _require(len(sources) <= 1, 'Source digest mismatch across cells')
    _require(all(len(v) == 1 for v in worlds.values()), 'Common world mismatch')
    _require(all(len(v) == 1 for v in denoms.values()), 'Common denominator mismatch')
    return dict(status='passed', verified_cells=len(commits), expected_cells=len(expected),
                all_valid=True, world_parity_verified=True, denominator_parity_verified=True,
                public_event_reconstruction_verified=True, private_world_read=False)


def audit_run_closure(commits_dir, registration_path):
    return audit_run(Path(commits_dir).parent, registration_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--registration', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        result = audit_run(args.output, args.registration)
    except Exception as exc:
        print(json.dumps(dict(status='failed', error=f'{type(exc).__name__}: {exc}')))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
