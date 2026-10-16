"""One episode = one (seed, law, arm). Trusted in-process policy; public state only.

Mirrors evaluate.episode semantics: 60 decision days (ask then match), 40 follow-up
days, MSMI per 100 members arrived by day 59, strict response shape and 1 MiB
memory/request limits, 10 s per-call limit. Adds host-only evaluation extras
(RB expectations, waiting/fairness rows, calibration rows, public ledger).
"""
import hashlib
import json
import time

import evaluate
import kit
from kit import HARD

from . import arms as A
from . import laws as L
from .fastsim import FastSimulator, LawSimulator
from .policies import model as M


def _digest_update(digest, phase, day, action):
    digest.update(json.dumps([phase, day, action], sort_keys=True).encode())


def _sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def run_episode(seed, law_name, arm, thetas, *, reference=False, keep_ledger=True):
    law = L.get(law_name)
    world = L.make_world(seed, law)
    world_sha = _sha(world)
    if reference:
        sim = kit.Simulator(world) if L.is_standard(law) else LawSimulator(world, law)
    else:
        sim = FastSimulator(world, law)
    del world
    meta = A.ARMS[arm]
    config = A.config_for(arm, law, thetas)
    fn = meta['fn']
    digest = hashlib.sha256()
    memory = None
    policy_seconds = max_call = 0.0
    own_pred, shadow = {}, {}
    x1_hist = None
    order = list(sim.members)
    index = {i: n for n, i in enumerate(order)}
    verified_day, wait_days, ever = {}, {}, set()
    error = None
    started = time.monotonic()
    try:
        for day in range(60):
            for phase in ('ask', 'match'):
                state = sim.observe()
                request = {'schema_version': kit.VERSION, 'phase': phase, 'state': state, 'memory': memory}
                if day == 59 and phase == 'match':
                    if len(json.dumps(request, allow_nan=False).encode()) > evaluate.LIMIT:
                        raise ValueError('Request exceeds 1 MiB')
                t0 = time.perf_counter()
                response = fn(request, config)
                elapsed = time.perf_counter() - t0
                policy_seconds += elapsed
                max_call = max(max_call, elapsed)
                if elapsed > 10:
                    raise ValueError('Policy exceeded 10-second invocation limit')
                response = evaluate.validate_response(evaluate.strict_json(json.dumps(response, allow_nan=False)), phase)
                memory = response['memory']
                action = response['asks' if phase == 'ask' else 'pairs']
                _digest_update(digest, phase, sim.day, action)
                if phase == 'ask':
                    sim.resolve_asks(action)
                    continue
                if not reference:
                    for m in state['members']:
                        i = m['member_id']
                        if i not in verified_day and all(m['fields'][k] is not None for k in HARD):
                            verified_day[i] = day
                        if m['available'] and i in verified_day and i not in ever:
                            wait_days[i] = wait_days.get(i, 0) + 1
                    if action:
                        if arm in A.PREDICTING:
                            own_pred.update({f'{day}|{k}': v for k, v in (memory.get('pred') or {}).items()})
                        for name in ('sim', 'emp'):
                            if name in thetas:
                                for k, v in M.predict_pairs(state, action, thetas[name]).items():
                                    shadow.setdefault(f'{day}|{k}', {})[name] = v
                        for a, b in action:
                            ever.update((a, b))
                sim.advance(action)
        if memory and 'x1_hist' in memory:
            x1_hist = memory['x1_hist']
        arrived = {i: m['arrived_day'] for i, m in sim.members.items() if m['arrived_day'] <= 59}
        for _ in range(40):
            sim.advance([])
    except Exception as exc:  # invalid episode is recorded, never dropped
        error = f'{type(exc).__name__}: {exc}'
    wall = time.monotonic() - started
    record = {'seed': seed, 'law': law_name, 'arm': arm, 'valid': error is None, 'error': error,
              'world_sha256': world_sha, 'action_sha256': digest.hexdigest(),
              'timing': {'wall': round(wall, 4), 'policy_seconds': round(policy_seconds, 4), 'max_call': round(max_call, 4)}}
    if error is not None:
        return record
    record['ask_log_sha256'] = _sha(sim.ask_log)
    base = sim.metrics()
    first = {}
    for intro in sim.introductions:
        for member in (intro['user_a'], intro['user_b']):
            first.setdefault(member, intro['assigned_day'])
    n = max(1, len(arrived))
    metrics = dict(base, arrived_members=len(arrived),
                   msmi_per_100_arrived_members=100 * base['mutual_second_meeting_intention'] / n,
                   dates_per_100=100 * base['dates'] / n,
                   mutual_acceptances_per_100=100 * base['mutual_acceptances'] / n,
                   served_members=len(first), unserved_members=len(arrived) - len(first),
                   coverage=len(first) / n,
                   hard_asks=sum(x['field'] == 'constraints' for x in sim.ask_log),
                   soft_asks=sum(x['field'] != 'constraints' for x in sim.ask_log))
    record['metrics'] = metrics
    if reference:
        return record
    exp = sim.expectations
    metrics.update(expected_mutual_per_100=100 * sum(e[0] for e in exp) / n,
                   expected_dates_per_100=100 * sum(e[1] for e in exp) / n,
                   expected_msmi_per_100=100 * sum(e[2] for e in exp) / n)
    outcomes = sim.intro_outcomes()
    intros = []
    for intro, e, o in zip(sim.introductions, exp, outcomes):
        key = f"{intro['assigned_day']}|{'|'.join(sorted((intro['user_a'], intro['user_b'])))}"
        intros.append([intro['assigned_day'], index[intro['user_a']], index[intro['user_b']],
                       round(e[0], 8), round(e[1], 8), round(e[2], 8), int(o[0]), int(o[1]), int(o[2]),
                       o[3], o[4], own_pred.get(key), shadow.get(key, {}).get('sim'), shadow.get(key, {}).get('emp')])
    counts, mutual_any, msmi_any = {}, set(), set()
    for intro, o in zip(sim.introductions, outcomes):
        for mbr in (intro['user_a'], intro['user_b']):
            counts[mbr] = counts.get(mbr, 0) + 1
            if o[0]:
                mutual_any.add(mbr)
            if o[2]:
                msmi_any.add(mbr)
    members = []
    for i, arr in arrived.items():
        m = sim.members[i]
        declined = any(m['field_status'][k] == 'declined' for k in HARD)
        complete0 = all(m['field_observed_day'][k] is not None and m['field_observed_day'][k] <= arr for k in HARD)
        members.append([index[i], arr, m['gender'], m['zone'], m['age'], int(complete0), int(declined),
                        verified_day.get(i), first.get(i), counts.get(i, 0), int(i in mutual_any),
                        int(i in msmi_any), wait_days.get(i, 0), int(m['exit_day'] < 60)])
    record['intros'] = intros
    record['members'] = members
    record['x1_hist'] = x1_hist
    if keep_ledger:
        record['ledger'] = {'introductions': sim.introductions, 'feedback': [e for e in sim.events if e['observed_day'] <= sim.day],
                            'ask_log': sim.ask_log, 'arrived': [[i, d] for i, d in arrived.items()]}
    return record

INTRO_COLUMNS = ['day', 'a', 'b', 'e_mutual', 'e_date', 'e_msmi', 'mutual', 'date', 'msmi', 'resp_a', 'resp_b',
                 'own_pred', 'shadow_sim', 'shadow_emp']
MEMBER_COLUMNS = ['idx', 'arrived', 'gender', 'zone', 'age', 'complete_at_arrival', 'declined_hard', 'verified_day',
                  'first_intro_day', 'n_intros', 'mutual_any', 'msmi_any', 'eligible_wait_days', 'early_exit']
