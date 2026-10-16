"""Named world/simulator laws ("conditions") for the round-2 robustness grid.

A law is a JSON-able dict. The six standard families are laws with every override
empty; they must reproduce the frozen kit simulator bit-for-bit (certified in S0).
Stress laws perturb exactly one axis the judges named: arrival order/process,
preference weights, response conditions, or acceptance drift. World transforms use
their own hash streams (kit.rand_for) so the base world draws are unchanged.
"""
import copy

from kit import rand_for

FAMILIES = ('development', 'sparse', 'cold_start', 'delayed', 'shift', 'drift')
DEV_WEIGHTS = {'relationship_goal': .7, 'relationship_pace': .4, 'lifestyle': .25, 'conversations': .2}
SHIFT_WEIGHTS = {'relationship_goal': .25, 'relationship_pace': .8, 'lifestyle': -.25, 'conversations': .5}

DEFAULTS = {
    'base_family': 'development',
    'axis': 'standard',
    'order': None,              # None | 'arrival' | 'reverse_arrival'
    'arrivals': None,           # None | 'late_heavy' | 'waves'
    'response_range': None,     # None | [lo, hi] linear remap of U[.55,.98]
    'weights': None,            # None (family default) | dict | 'random'
    'drift': None,              # None (family default) | [[start_day, logit_offset], ...]
    'response_decay': None,     # None | [day, factor] applied to response rates of intros assigned >= day
    'date_prob': .78,
    'second_delay_max': 5,
    'extra_date_delay': None,   # None | [lo, hi] added to every date (on top of the delayed family)
}


def _law(name, **overrides):
    law = dict(DEFAULTS)
    law.update(overrides)
    law['name'] = name
    unknown = set(law) - set(DEFAULTS) - {'name'}
    if unknown:
        raise ValueError(f'unknown law keys {unknown}')
    return law


STANDARD = {f: _law(f, base_family=f) for f in FAMILIES}

STRESS = {
    # Arrival order / process (FIFO asks follow public list order).
    'A_sorted': _law('A_sorted', axis='arrival', order='arrival'),
    'A_reverse': _law('A_reverse', axis='arrival', order='reverse_arrival'),
    'A_late': _law('A_late', axis='arrival', arrivals='late_heavy'),
    'A_waves': _law('A_waves', axis='arrival', arrivals='waves'),
    # Preference weights.
    'W_half_shift': _law('W_half_shift', axis='weights',
                         weights={k: (DEV_WEIGHTS[k] + SHIFT_WEIGHTS[k]) / 2 for k in DEV_WEIGHTS}),
    'W_strong_shift': _law('W_strong_shift', axis='weights',
                           weights={'relationship_goal': 0.0, 'relationship_pace': 1.0,
                                    'lifestyle': -.5, 'conversations': .7}),
    'W_random': _law('W_random', axis='weights', weights='random'),
    'W_goal_zero': _law('W_goal_zero', axis='weights', weights=dict(DEV_WEIGHTS, relationship_goal=0.0)),
    # Response conditions.
    'R_low': _law('R_low', axis='response', response_range=[.35, .75]),
    'R_decay': _law('R_decay', axis='response', response_decay=[35, .7]),
    'R_date_low': _law('R_date_low', axis='response', date_prob=.6),
    'R_slow_second': _law('R_slow_second', axis='response', second_delay_max=8),
    # Acceptance drift (direction, timing, magnitude, reversal).
    'D_early': _law('D_early', axis='drift', drift=[[20, -.5]]),
    'D_strong': _law('D_strong', axis='drift', drift=[[35, -1.0]]),
    'D_positive': _law('D_positive', axis='drift', drift=[[35, .5]]),
    'D_reversal': _law('D_reversal', axis='drift', drift=[[20, -.75], [40, 0.0]]),
}

ALL = dict(STANDARD, **STRESS)


def get(name):
    return copy.deepcopy(ALL[name])


def is_standard(law):
    return all(law[k] == DEFAULTS[k] for k in DEFAULTS if k not in ('base_family', 'axis'))


def drift_schedule(law, variant):
    if law['drift'] is not None:
        return [tuple(x) for x in law['drift']]
    return [(35, -.5)] if variant == 'drift' else []


def drift_offset(schedule, day):
    value = 0.0
    for start, offset in schedule:
        if day >= start:
            value = offset
    return value


def weights_for(law, world):
    if law['weights'] is None:
        return SHIFT_WEIGHTS if world['variant'] == 'shift' else DEV_WEIGHTS
    if law['weights'] == 'random':
        r = rand_for(world['seed'], 'round2-law-weights', law['name'])
        return {k: round(r.uniform(-.5, 1.0), 6) for k in DEV_WEIGHTS}
    return dict(law['weights'])


def transform_world(world, law):
    """Apply world-level law transforms. Returns a new world; base draws are untouched."""
    world = copy.deepcopy(world)
    world['round2_law'] = law['name']
    members = world['members']
    for m in members:
        if law['arrivals'] is not None:
            r = rand_for(world['seed'], 'round2-law-arrival', law['name'], m['member_id'])
            if law['arrivals'] == 'late_heavy':
                arrival = 0 if r.random() < .4 else r.randint(1, 45)
            elif law['arrivals'] == 'waves':
                arrival = r.choice([0, 15, 30])
            else:
                raise ValueError('unknown arrivals law')
            m['arrived_day'] = arrival
            m['field_observed_day'] = {k: (arrival if v is not None else None) for k, v in m['fields'].items()}
        if law['response_range'] is not None:
            lo, hi = law['response_range']
            m['response_rate'] = lo + (m['response_rate'] - .55) / .43 * (hi - lo)
    if law['order'] == 'arrival':
        world['members'] = [m for _, m in sorted(enumerate(members), key=lambda x: (x[1]['arrived_day'], x[0]))]
    elif law['order'] == 'reverse_arrival':
        world['members'] = [m for _, m in sorted(enumerate(members), key=lambda x: (-x[1]['arrived_day'], x[0]))]
    elif law['order'] is not None:
        raise ValueError('unknown order law')
    return world


def make_world(seed, law):
    from kit import generate
    world = generate(seed=seed, n=200, pool_id='evaluation', variant=law['base_family'])
    return world if is_standard(law) else transform_world(world, law)
