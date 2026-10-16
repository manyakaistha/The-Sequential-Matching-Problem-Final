"""Ask-order variants with the supplied greedy matching held fixed (Q1 arrival-order probes),
and N3_two acquisition with an injectable hard-field prior (Q2 prior probe).
"""
import hashlib
import itertools
import random
import time

from kit import GENDERS, HARD, baseline_asks, baseline_match

from research6.policies import acquisition as acq

ZONES = ['zone_a', 'zone_b', 'zone_c', 'zone_d']
SCHEDULE = ['weekday_evening', 'weekend_day', 'weekend_evening']


def _eligible(state):
    return [(n, m) for n, m in enumerate(state['members']) if m['available']
            and any(m['fields'][k] is None for k in HARD)
            and not any(m['field_status'][k] == 'declined' for k in HARD)]


def ordered_asks(state, order):
    rows = _eligible(state)
    if order == 'arrival':
        rows.sort(key=lambda x: (x[1]['arrived_day'], x[0]))
    elif order == 'lifo':
        rows.sort(key=lambda x: (-x[1]['arrived_day'], x[0]))
    elif order == 'hashed':
        rows.sort(key=lambda x: (hashlib.sha256(f"r2-ask|{state['day']}|{x[1]['member_id']}".encode()).hexdigest(), x[0]))
    else:
        raise ValueError('unknown ask order')
    return [{'member_id': m['member_id'], 'field': 'constraints'} for _, m in rows[:state['ask_budget_remaining'] // 3]]


def decide_order(request, config):
    state = request['state']
    if request['phase'] == 'ask':
        if config['order'] == 'degree':
            from research4.candidates import choose_asks
            return {'asks': choose_asks(state, 'hard_priority'), 'memory': {}}
        return {'asks': ordered_asks(state, config['order']), 'memory': {}}
    return {'pairs': baseline_match(state), 'memory': {}}


# ------------------------------------------------------------------ N3e
def theta_sampler(hard):
    """Member realisation sampler with explicit hard-field priors (same seeding scheme as N3)."""
    def choose(r, table):
        values = list(table)
        return r.choices(values, [table[v] for v in values])[0]

    def sample(member, day, fifo_index, particle, salt=acq.SALT):
        digest = hashlib.sha256(f'{salt}|{day}|{fifo_index}|{particle}'.encode()).digest()
        r = random.Random(int.from_bytes(digest[:16], 'big'))
        out = {k: (v if not isinstance(v, dict) else dict(v)) for k, v in member.items()}
        f = out['fields'] = {k: (v[:] if isinstance(v, list) else v) for k, v in member['fields'].items()}
        status = out['field_status'] = dict(member['field_status'])
        zone = member['zone']
        for field in HARD:
            if f[field] is not None:
                continue
            if status[field] == 'declined':
                raise ValueError('declined field cannot be imputed')
            if field == 'age_min':
                value = max(18, member['age'] - int(choose(r, hard['age_min_offset'])))
            elif field == 'age_max':
                value = min(65, member['age'] + int(choose(r, hard['age_max_offset'])))
            elif field == 'who_to_meet':
                size = int(choose(r, hard['who_to_meet_size']))
                pool, value = dict(hard['gender_inclusion']), []
                for _ in range(min(size, len(pool))):
                    g = choose(r, pool)
                    value.append(g)
                    pool.pop(g)
            elif field == 'has_children':
                value = r.random() < hard['has_children']
            elif field == 'acceptable_zones':
                value = [zone]
                if zone in ZONES and r.random() < hard['extra_zone']:
                    value = list(dict.fromkeys([zone, choose(r, hard['extra_zone_choice'])]))
            elif field == 'schedule':
                size = int(choose(r, hard['schedule_size']))
                value = r.sample(SCHEDULE, size)
            else:
                value = choose(r, hard[field])
            f[field] = value
            status[field] = 'observed'
        return out
    return sample


def n3_two_asks(state, sampler):
    """research6 N3_two selection with the particle sampler injected; FIFO fallback."""
    started = time.monotonic()
    try:
        problem = acq.build_problem(state)
        if problem['k'] == 0 or len(problem['ranks']) <= problem['k']:
            return baseline_asks(state)[:problem['k']]
        if problem['k'] > 2:
            needed = problem['k'] - 2
            two = []
            for a, b in itertools.combinations(sorted(problem['shortlist']), 2):
                filler = [x for x in problem['eligible'] if x not in (a, b)][:needed]
                two.append(tuple(sorted((a, b) + tuple(filler))))
            problem = acq.build_problem(state, batches_override=sorted(set(two) | {problem['fifo']}))
        totals = {batch: (0, 0) for batch in problem['batches']}
        masks = {batch: sum(problem['bits'][i] for i in batch) for batch in totals}
        for particle in range(acq.PARTICLES):
            acq._guard(started)
            draws = {i: sampler(state['members'][i], state['day'], i, particle) for i in problem['sampled']}
            edges = acq.particle_edges(state, problem, draws)
            for batch in totals:
                count, score = acq.masked_match(edges, masks[batch])
                c0, s0 = totals[batch]
                totals[batch] = (c0 + count, s0 + score)
        chosen = acq._select(problem['batches'], problem['fifo'], totals)
        return [{'member_id': state['members'][i]['member_id'], 'field': 'constraints'} for i in chosen]
    except Exception:
        return baseline_asks(state)


def decide_n3e(request, config):
    state = request['state']
    if request['phase'] == 'match':
        return {'pairs': baseline_match(state), 'memory': {}}
    sampler = acq.sample_member if config.get('sampler') == 'research6' else theta_sampler(config['theta']['hard'])
    return {'asks': n3_two_asks(state, sampler), 'memory': {}}
