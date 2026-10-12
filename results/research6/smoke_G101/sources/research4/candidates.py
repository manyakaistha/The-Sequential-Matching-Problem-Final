"""Small observation-only round-four mechanisms and architecture controls.

The director supplies request validation, interruption and legal fallback guards.
No seed, private world, files, network, or serialized actor parameters are read.
"""
from fractions import Fraction
from functools import lru_cache
from math import comb
from itertools import product
from kit import HARD, baseline_asks, baseline_match, eligibility
from research3.policy import legal_edges
from research3.model_candidates import population, response_counts, response_second
from research.terminal_model import (NODES, WEIGHTS, REGIMES, sigmoid,
                                     equality_probabilities, integrated)

CANDIDATES = {
    'greedy': {'match': 'greedy', 'ask': 'fifo'},
    'population_control': {'match': 'population', 'ask': 'fifo'},
    'goal_surplus_control': {'match': 'population', 'ask': 'goal_surplus'},
    'coordinated_goal': {'match': 'population', 'ask': 'coordinated_goal'},
    'hard_priority': {'match': 'population', 'ask': 'hard_priority'},
    'response_beta_control': {'match': 'response_beta', 'ask': 'fifo'},
    'response_uniform': {'match': 'response_uniform', 'ask': 'fifo'},
    'acceptance_shrinkage': {'match': 'acceptance_shrinkage', 'ask': 'fifo'},
}


@lru_cache(maxsize=4096)
def acceptance_likelihood(equal, bias, day):
    """Marginal own yes probability; enumerate missing equality/shared effect."""
    unknown = [i for i, p in enumerate(equal) if 0 < p < 1]
    value = 0.
    for bits in product((0., 1.), repeat=len(unknown)):
        eq, mass = list(equal), 1.
        for i, bit in zip(unknown, bits):
            mass *= equal[i] if bit else 1-equal[i]
            eq[i] = bit
        for regime, weight in zip(REGIMES, (4/6, 1/6, 1/6)):
            fit = -.25+sum(w*(1 if e else -.5) for w, e in zip(regime[:4], eq))
            fit += regime[4] if day >= 35 else 0.
            value += mass*weight*sum(w*sigmoid(fit+bias+.45*x)
                                    for x, w in zip(NODES, WEIGHTS))
    return value


def acceptance_posteriors(state):
    """Five-point prior-weighted posterior, then moment-matched Gaussian.

    Publicly disclosed current fields can inform past compatibility now. No field
    disclosed after this invocation is accessed. Regimes are independently mixed
    per trial; partner responses/shared-effect posterior are not conditioned on.
    These deliberate approximations need prospective calibration tests.
    """
    members = {m['member_id']: m for m in state['members']}
    intros = {i['introduction_id']: i for i in state.get('introductions', ())}
    masses = {}
    for event in state.get('feedback', ()):
        if event.get('event') != 'introduction_response' or event.get('value') not in ('yes', 'no'):
            continue
        intro = intros.get(event.get('introduction_id'))
        ident = event.get('member_id')
        if not intro or ident not in members:
            continue
        other = intro['user_b'] if ident == intro['user_a'] else intro['user_a']
        if other not in members:
            continue
        equal = equality_probabilities(members[ident], members[other])
        row = masses.setdefault(ident, list(WEIGHTS))
        for j, x in enumerate(NODES):
            p = acceptance_likelihood(equal, .7*x, intro['assigned_day'])
            row[j] *= p if event['value'] == 'yes' else 1-p
    result = {}
    for ident, row in masses.items():
        total = sum(row)
        mean = sum(w*.7*x for w, x in zip(row, NODES))/total
        variance = max(0., sum(w*(.7*x-mean)**2 for w, x in zip(row, NODES))/total)
        result[ident] = (round(mean, 5), round(variance, 5), 0., .25)
    return result


def personalized_population(a, b, day, actors):
    equal = equality_probabilities(a, b)
    ua, ub = (actors.get(m['member_id'], (0., .49, 0., .25)) for m in (a, b))
    values = [integrated(equal, ua, ub, day, regime)[4] for regime in range(3)]
    joint = ((3+671/686)/6)*values[0]+values[1]/6+values[2]/6
    second = (.55**2+.55*.98+.98**2)/3
    return .78*.36*second**2*joint


@lru_cache(maxsize=512)
def uniform_second(successes, failures):
    """Exact rational integral ratio for R~Uniform[55/100,98/100]."""
    if not (0 <= successes <= 120 and 0 <= failures <= 120):
        raise ValueError('response history outside supported public horizon')
    low, high = Fraction(55, 100), Fraction(98, 100)
    def integral(power):
        return sum(((-1)**j * comb(failures, j) *
                    (high**(power+j+1)-low**(power+j+1))/(power+j+1)
                    for j in range(failures+1)), Fraction(0))
    return float(integral(successes+2)/integral(successes))


def hard_candidates(state):
    return [m for m in state['members'] if m.get('available') and
            any(m['fields'].get(k) is None for k in HARD) and
            not any(m['field_status'].get(k) == 'declined' for k in HARD)]


def potential_weight(a, b):
    """Explicit approximate completion probability from public demographics.

    Partial observed failures are exact pruning. Unknown age bounds use the exact
    generator radius distribution. Unknown gender inclusion has prior 7/15.
    Cross-zone completion is a conservative proxy, NOT an exact joint posterior.
    Remaining hard constraints are intentionally omitted, not imputed legal.
    """
    if eligibility(a, b)['status'] == 'infeasible':
        return 0.
    probability = 1.
    ordinary_zones = {'zone_a', 'zone_b', 'zone_c', 'zone_d'}
    for x, y in ((a, b), (b, a)):
        difference = y['age'] - x['age']
        required = 'age_max' if difference >= 0 else 'age_min'
        if x['fields'].get(required) is None:
            probability *= max(0, 11-max(3, abs(difference)))/8
        if x['fields'].get('who_to_meet') is None:
            probability *= 7/15
        if x['fields'].get('acceptable_zones') is None and x['zone'] != y['zone']:
            # Added zone is UNIFORM, unlike the member's own-zone draw. The
            # unconditional six-family mixture includes 1/6 sparse with no extra.
            probability *= .3/4*(5/6) if y['zone'] in ordinary_zones else 0.
    return probability


def prioritized_hard(state):
    candidates = hard_candidates(state)
    active = [m for m in state['members'] if m.get('available') and
              not any(m['field_status'].get(k) == 'declined' for k in HARD)]
    verified = {m['member_id'] for m in active
                if all(m['fields'].get(k) is not None for k in HARD)}
    past = {tuple(sorted((i['user_a'], i['user_b'])))
            for i in state.get('introductions', ())}
    def value(a):
        immediate = potential = 0.
        for b in active:
            if a['member_id'] == b['member_id'] or tuple(sorted((a['member_id'], b['member_id']))) in past:
                continue
            weight = potential_weight(a, b)
            potential += weight
            if b['member_id'] in verified:
                immediate += weight
        # Explicit priority: one-bundle opportunities, then two-bundle prospects.
        return (-immediate, -potential, a['arrived_day'], a['member_id'])
    return sorted(candidates, key=value)


def choose_asks(state, mode):
    budget = state['ask_budget_remaining']
    if mode == 'hard_priority':
        return [{'member_id': m['member_id'], 'field': 'constraints'}
                for m in prioritized_hard(state)[:budget//3]]
    fifo = baseline_asks(state)
    if mode == 'fifo':
        return fifo
    if mode == 'coordinated_goal':
        # Reserve three units only when at least three hard candidates compete.
        # The control instead spends those units on a fourth hard bundle.
        selected = fifo[:3] if len(fifo) >= 3 and budget >= 12 else fifo
    elif mode == 'goal_surplus':
        selected = fifo
    else:
        raise ValueError('unknown acquisition mode')
    left = budget - 3*len(selected)
    if left <= 0:
        return selected
    active = {m['member_id']: m for m in state['members'] if m.get('available')}
    newly = {row['member_id'] for row in selected}
    degree = {}
    for pair in legal_edges(state):
        for ident in pair:
            degree[ident] = degree.get(ident, 0)+1
    eligible = [m for ident, m in active.items()
                if (ident in degree or (mode == 'coordinated_goal' and ident in newly))
                and m['fields'].get('relationship_goal') is None
                and m['field_status'].get('relationship_goal') != 'declined']
    # Newly verified endpoints have never had a legal introduction. Revealing
    # their goal before first use is the targeted mechanism, not entropy.
    eligible.sort(key=lambda m: (m['member_id'] not in newly,
                                 -degree.get(m['member_id'], 0), m['member_id']))
    return selected + [{'member_id': m['member_id'], 'field': 'relationship_goal'}
                       for m in eligible[:left]]


def decision(request, config=None):
    config = config or CANDIDATES['greedy']
    state = request['state']
    if request['phase'] == 'ask':
        return {'asks': choose_asks(state, config.get('ask', 'fifo')), 'memory': {}}
    mode = config.get('match', 'greedy')
    if mode == 'greedy':
        return {'pairs': baseline_match(state), 'memory': {}}
    by_id = {m['member_id']: m for m in state['members']}
    personalized = mode == 'acceptance_shrinkage'
    counts = response_counts(state) if mode.startswith('response_') or personalized else {}
    actors = acceptance_posteriors(state) if personalized else {}
    prior_second = (.55**2 + .55*.98 + .98**2)/3
    ranked = []
    for pair in legal_edges(state):
        score = (personalized_population(by_id[pair[0]], by_id[pair[1]], state['day'], actors)
                 if personalized else population(by_id[pair[0]], by_id[pair[1]], state['day'])[0])
        if mode.startswith('response_') or personalized:
            moment = response_second if mode == 'response_beta' else lambda c: uniform_second(*c)
            score *= moment(counts.get(pair[0], (0, 0)))*moment(counts.get(pair[1], (0, 0)))/prior_second**2
        elif mode != 'population':
            raise ValueError('unknown matching mode')
        ranked.append((score, pair))
    used, pairs = set(), []
    for _, pair in sorted(ranked, key=lambda row: (-row[0], row[1])):
        if not used.intersection(pair):
            pairs.append(list(pair)); used.update(pair)
    return {'pairs': sorted(pairs), 'memory': {}}


decide = decision
