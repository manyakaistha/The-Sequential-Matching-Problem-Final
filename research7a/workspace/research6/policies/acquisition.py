"""N3 v1 fixed-work, public-only joint hard acquisition; actual matching is G.

Diagnostics are host-only pure data. No telemetry enters subsequent actions.
"""
import copy
import hashlib
import itertools
import random
import re
import time

from kit import GENDERS, HARD, SOFT, baseline_asks, baseline_match, eligibility

PARTICLES = 32
SHORTLIST = 8
SALT = 'research6-N3-joint4-v1'
GUARD_SECONDS = 6.0
ZONES = ['zone_a', 'zone_b', 'zone_c', 'zone_d']
SCHEDULE = ['weekday_evening', 'weekend_day', 'weekend_evening']
LAST_DIAGNOSTICS = {}


class WorkDeadline(Exception):
    pass


def _guard(start):
    if time.monotonic() - start >= GUARD_SECONDS:
        raise WorkDeadline('internal six-second guard')


def query_eligible(member):
    return (member['available'] and
            any(member['fields'][f] is None for f in HARD) and
            not any(member['field_status'][f] == 'declined' for f in HARD))


def sample_member(member, day, fifo_index, particle, salt=SALT):
    """A single member realization, reused for every incident edge and batch."""
    zone = member['zone']
    ordinary = zone in ZONES
    if not ordinary and not re.fullmatch(r'zone_(?:[0-9]|1[01])', zone):
        raise ValueError('unsupported public zone vocabulary')
    digest = hashlib.sha256(f'{salt}|{day}|{fifo_index}|{particle}'.encode()).digest()
    r = random.Random(int.from_bytes(digest[:16], 'big'))
    out = copy.deepcopy(member)
    f = out['fields']
    # Invoke only missing-field draws, preserving every disclosed value and False.
    for field in HARD:
        if f[field] is not None:
            continue
        if member['field_status'][field] == 'declined':
            raise ValueError('declined field cannot be imputed')
        if field == 'age_min':
            value = max(18, member['age'] - r.randint(3, 10))
        elif field == 'age_max':
            value = min(65, member['age'] + r.randint(3, 10))
        elif field == 'who_to_meet':
            value = r.sample(GENDERS, r.choices([1, 2, 3], [.7, .2, .1])[0])
        elif field == 'relationship_structure':
            value = r.choices(['monogamous', 'non_monogamous'], [.9, .1])[0]
        elif field == 'smoking':
            value = r.choices(['no', 'occasionally', 'yes'], [.75, .20, .05])[0]
        elif field == 'partner_smoking':
            value = r.choice(['no_smoking', 'any'])
        elif field == 'has_children':
            value = r.random() < .15
        elif field == 'partner_children':
            value = r.choice(['any', 'no_children'])
        elif field == 'wants_children':
            value = r.choice(['yes', 'no', 'unsure'])
        elif field == 'acceptable_zones':
            value = [zone]
            if ordinary and r.random() < .3:
                value = list(dict.fromkeys([zone, r.choice(ZONES)]))
        elif field == 'schedule':
            value = r.sample(SCHEDULE, r.randint(1, 3))
        f[field] = value
        out['field_status'][field] = 'observed'
    return out


def build_problem(state, batches_override=None):
    """Rank across verified and query-eligible neighbors; preserve G FIFO order."""
    members = state['members']
    if len(members) > 200:
        raise ValueError('member cap exceeded')
    eligible = [i for i, m in enumerate(members) if query_eligible(m)]
    k = min(4, state['ask_budget_remaining'] // 3, len(eligible))
    fifo = tuple(eligible[:k])
    past = {tuple(sorted((x['user_a'], x['user_b']))) for x in state['introductions']}
    verified = {i for i, m in enumerate(members) if m['available'] and
                all(m['fields'][f] is not None for f in HARD)}
    usable = verified | set(eligible)
    degrees = {i: [0, 0] for i in eligible}
    potential = []
    for i, j in itertools.combinations(sorted(usable), 2):
        a, b = members[i], members[j]
        pair = tuple(sorted((a['member_id'], b['member_id'])))
        if pair in past or eligibility(a, b)['status'] == 'infeasible':
            continue
        score = sum(a['fields'].get(f) is not None and
                    a['fields'].get(f) == b['fields'].get(f) for f in SOFT)
        potential.append((-score, pair, i, j))
        for actor, neighbor in ((i, j), (j, i)):
            if actor in degrees:
                degrees[actor][0 if neighbor in verified else 1] += 1
    ranked = sorted(eligible, key=lambda i: (-sum(degrees[i]), i, members[i]['member_id']))
    shortlist = ranked[:SHORTLIST]
    batches = sorted(set(itertools.combinations(sorted(shortlist), k)) | {fifo}) if k else [()]
    sampled = sorted(set(shortlist) | set(fifo))
    if batches_override is not None:
        batches = sorted(set(tuple(sorted(b)) for b in batches_override))
        if (not batches or len(batches) > 71 or
                any(len(b) != k or len(set(b)) != k or not set(b) <= set(eligible) for b in batches)):
            raise ValueError('invalid bounded fixed-k audit batches')
        sampled = sorted({i for b in batches for i in b})
        if len(sampled) > 12:
            raise ValueError('audit sampled actor cap exceeded')
    bits = {i: 1 << n for n, i in enumerate(sampled)}
    potential = [edge for edge in potential if all(i in verified or i in bits for i in edge[2:])]
    return dict(k=k, fifo=fifo, shortlist=shortlist, batches=batches, eligible=eligible,
                sampled=sampled, bits=bits, potential=sorted(potential),
                ranks=[dict(fifo_index=i, rank=n, one_bundle_degree=degrees[i][0],
                            two_bundle_degree=degrees[i][1], omitted=i not in shortlist)
                       for n, i in enumerate(ranked)])


def particle_edges(state, problem, draws):
    """G ordering with endpoint activation masks; verified edges need no redraw."""
    edges = []
    members, bits = state['members'], problem['bits']
    for neg_score, pair, i, j in problem['potential']:
        required = bits.get(i, 0) | bits.get(j, 0)
        if required and eligibility(draws.get(i, members[i]), draws.get(j, members[j]))['status'] != 'feasible':
            continue
        edges.append((required, (1 << i) | (1 << j), -neg_score, pair))
    return edges


def masked_match(edges, batch_mask, return_pairs=False):
    used = count = score = 0
    pairs = []
    for required, endpoints, value, pair in edges:
        if required & batch_mask != required or used & endpoints:
            continue
        used |= endpoints
        count += 1
        score += value
        if return_pairs:
            pairs.append(list(pair))
    return pairs if return_pairs else (count, score)


def _select(batches, fifo, totals):
    # FIFO wins equal modeled count/score; otherwise public FIFO tuple breaks ties.
    best = fifo
    for batch in batches:
        if totals[batch] > totals[best] or (totals[batch] == totals[best] and
                                          best != fifo and batch < best):
            best = batch
    return best


def evaluate_batches(state, batches, salt):
    """Offline fixed independent-stream audit; never used by deployed selection.

    Caller registers salt/batches before measuring. Returned gains must not be
    fitted or used to retune the deployed menu. Exactly 32 particles, <=71 batches.
    """
    if not isinstance(salt, str) or not salt or len(salt) > 256:
        raise ValueError('invalid audit salt')
    problem = build_problem(state, batches_override=batches)
    totals = {b: (0, 0) for b in problem['batches']}
    masks = {b: sum(problem['bits'][i] for i in b) for b in totals}
    started = time.monotonic()
    for particle in range(PARTICLES):
        _guard(started)
        draws = {i: sample_member(state['members'][i], state['day'], i, particle, salt)
                 for i in problem['sampled']}
        edges = particle_edges(state, problem, draws)
        for batch in totals:
            _guard(started)
            value = masked_match(edges, masks[batch])
            totals[batch] = tuple(a+b for a, b in zip(totals[batch], value))
    return {'salt': salt, 'particles': PARTICLES,
            'objectives': [{'batch': list(b), 'mean_count': c/PARTICLES,
                            'mean_soft_score': s/PARTICLES} for b, (c, s) in totals.items()]}


def action(request, config):
    global LAST_DIAGNOSTICS
    LAST_DIAGNOSTICS = {'fallback': False, 'reason': None, 'salt': SALT,
                        'particles': PARTICLES, 'shortlist_cap': SHORTLIST}
    state = request['state']
    if request['phase'] == 'match':
        return {'pairs': baseline_match(state), 'memory': {}}
    started = time.monotonic()
    try:
        problem = build_problem(state)
        LAST_DIAGNOSTICS.update({key: problem[key] for key in
                                ('k', 'fifo', 'shortlist', 'sampled', 'ranks')})
        LAST_DIAGNOSTICS['config'] = {'id': config['id'], 'salt': SALT,
                                     'particles': PARTICLES, 'shortlist': SHORTLIST}
        if problem['k'] == 0 or len(problem['ranks']) <= problem['k']:
            return {'asks': baseline_asks(state)[:problem['k']], 'memory': {}}
        if config['id'] == 'N3_fifo4':
            return {'asks': [{'member_id': state['members'][i]['member_id'], 'field': 'constraints'}
                             for i in problem['fifo']], 'memory': {}}
        if config['id'] == 'N3_two' and problem['k'] > 2:
            two_pairs = list(itertools.combinations(sorted(problem['shortlist']), 2))
            needed = problem['k'] - 2
            two_batches = []
            for a, b in two_pairs:
                filler = [x for x in problem['eligible'] if x not in (a, b)][:needed]
                two_batches.append(tuple(sorted((a, b) + tuple(filler))))
            batches_override = sorted(set(two_batches) | {problem['fifo']})
            problem = build_problem(state, batches_override=batches_override)
        totals = {batch: (0, 0) for batch in problem['batches']}
        masks = {batch: sum(problem['bits'][i] for i in batch) for batch in totals}
        recorded_draws = []
        scans = feasible_edges = 0
        LAST_DIAGNOSTICS['draws'] = recorded_draws
        work = {'particles': 0, 'batches': len(totals),
                'sampled_actors': len(problem['sampled']),
                'potential_pairs': len(problem['potential']),
                'feasible_particle_edges': 0, 'edge_scans': 0,
                'batch_particle_evaluations': 0}
        LAST_DIAGNOSTICS['work'] = work
        for particle in range(PARTICLES):
            _guard(started)
            draws = {i: sample_member(state['members'][i], state['day'], i, particle)
                     for i in problem['sampled']}
            recorded_draws.append({str(i): {f: draws[i]['fields'][f] for f in HARD}
                                   for i in problem['sampled']})
            edges = particle_edges(state, problem, draws)
            feasible_edges += len(edges)
            work['particles'] += 1
            work['feasible_particle_edges'] = feasible_edges
            for batch in totals:
                _guard(started)
                count, score = masked_match(edges, masks[batch])
                old_count, old_score = totals[batch]
                totals[batch] = (old_count + count, old_score + score)
                scans += len(edges)
                work['edge_scans'] = scans
                work['batch_particle_evaluations'] += 1
        chosen = _select(problem['batches'], problem['fifo'], totals)
        fifo_value = totals[problem['fifo']]
        LAST_DIAGNOSTICS.update(draws=recorded_draws,
            considered=[{'batch': list(b), 'mean_count': totals[b][0] / PARTICLES,
                         'mean_soft_score': totals[b][1] / PARTICLES} for b in totals],
            chosen=list(chosen), chosen_objective=[v / PARTICLES for v in totals[chosen]],
            fifo_objective=[v / PARTICLES for v in fifo_value],
            paired_difference=[(a-b) / PARTICLES for a, b in zip(totals[chosen], fifo_value)],
            work=work)
        _guard(started)
        return {'asks': [{'member_id': state['members'][i]['member_id'], 'field': 'constraints'}
                         for i in chosen], 'memory': {}}
    except Exception as error:
        LAST_DIAGNOSTICS.update(fallback=True, reason=type(error).__name__ + ': ' + str(error))
        return {'asks': baseline_asks(state), 'memory': {}}
    finally:
        LAST_DIAGNOSTICS['elapsed_seconds'] = time.monotonic() - started
