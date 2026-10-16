"""Fixed, symmetric features of the public assignment-time observation.

IDs are used only to join released actor feedback to public introductions. No
population, variant, latent propensity, or identifier value enters the vector.
"""
from __future__ import annotations

import numpy as np

SOFT_FIELDS = (
    'relationship_goal', 'relationship_pace', 'lifestyle', 'conversations',
    'emotional_availability', 'space_for_relationship', 'relocate',
)
_HISTORY_KINDS = ('introduction_response', 'second_meeting_intention')
_HISTORY_STATS = ('yes_count', 'no_count', 'nonresponse_count', 'released_count',
                  'response_beta_rate', 'yes_beta_rate')


def feature_names() -> list[str]:
    """Return a fresh copy of the immutable ordered feature contract (74 columns)."""
    names = [f'{field}__{kind}' for field in SOFT_FIELDS
             for kind in ('equal_known', 'mismatch_known', 'one_missing', 'both_missing')]
    names += ['soft_declined_min', 'soft_declined_max', 'soft_known_rate_min',
              'soft_known_rate_max', 'age_gap', 'day_fraction', 'tenure_min',
              'tenure_max', 'age_min', 'age_max']
    names += [f'{kind}__{stat}__{agg}' for kind in _HISTORY_KINDS
              for stat in _HISTORY_STATS for agg in ('min', 'max', 'mean')]
    return names


def prepare_state(state: dict) -> dict:
    """Aggregate only actor feedback actually released by the assignment day.

    Same-day assignments are excluded: they cannot have feedback when this
    day's batch is selected. A member must be an endpoint of the referenced
    public introduction. Pair-level date/pause events do not become actor data.
    """
    day = state['day']
    intros = {i['introduction_id']: i for i in state.get('introductions', [])
              if i['assigned_day'] < day}
    counts = {}
    seen = set()
    for event in state.get('feedback', []):
        kind = event.get('event')
        observed = event.get('observed_day')
        intro = intros.get(event.get('introduction_id'))
        actor = event.get('member_id')
        if (kind not in _HISTORY_KINDS or intro is None
                or not isinstance(observed, (int, float)) or not 0 <= observed <= day
                or actor not in (intro['user_a'], intro['user_b'])):
            continue
        identity = (event['introduction_id'], actor, kind)
        if identity in seen:
            raise ValueError('Duplicate released actor feedback')
        seen.add(identity)
        value = event.get('value')
        if value not in ('yes', 'no', None):
            raise ValueError('Unknown released actor response')
        bucket = counts.setdefault(actor, np.zeros((2, 3), dtype=float))
        bucket[_HISTORY_KINDS.index(kind), {'yes': 0, 'no': 1, None: 2}[value]] += 1
    histories = {}
    for actor, values in counts.items():
        total = values.sum(axis=1)
        answered = values[:, :2].sum(axis=1)
        histories[actor] = np.column_stack((values, total,
            (answered + 1) / (total + 2), (values[:, 0] + 1) / (answered + 2)))
    return {'day': day, 'histories': histories}


def _soft(member: dict, day: int):
    fields = member.get('fields', {})
    statuses = member.get('field_status', {})
    times = member.get('field_observed_day', {})
    values, declined = [], 0
    for field in SOFT_FIELDS:
        status, observed = statuses.get(field), times.get(field)
        released = isinstance(observed, (int, float)) and 0 <= observed <= day
        values.append(fields.get(field) if status == 'observed' and released else None)
        # Initial public declines have no observation timestamp in kit.py.
        declined += status == 'declined'
    return values, float(declined)


def pair_features(state: dict, a: dict, b: dict, context: dict | None = None) -> np.ndarray:
    """74 finite float features, invariant to endpoint order and opaque IDs."""
    context = prepare_state(state) if context is None else context
    day = state['day']
    if context['day'] != day:
        raise ValueError('Feature context belongs to a different assignment day')
    av, ad = _soft(a, day)
    bv, bd = _soft(b, day)
    out = []
    for x, y in zip(av, bv):
        both = x is not None and y is not None
        out.extend((float(both and x == y), float(both and x != y),
                    float((x is None) != (y is None)), float(x is None and y is None)))
    ak = sum(v is not None for v in av) / len(SOFT_FIELDS)
    bk = sum(v is not None for v in bv) / len(SOFT_FIELDS)
    ages = (float(a['age']), float(b['age']))
    tenures = (float(day - a['arrived_day']), float(day - b['arrived_day']))
    out.extend((min(ad, bd), max(ad, bd), min(ak, bk), max(ak, bk),
                abs(ages[0] - ages[1]), day / 59.0, min(tenures), max(tenures),
                min(ages), max(ages)))
    empty = np.array([[0., 0., 0., 0., .5, .5]] * 2)
    ah = context['histories'].get(a['member_id'], empty)
    bh = context['histories'].get(b['member_id'], empty)
    for kind in range(2):
        for stat in range(6):
            x, y = ah[kind, stat], bh[kind, stat]
            out.extend((min(x, y), max(x, y), (x + y) / 2))
    result = np.asarray(out, dtype=float)
    if not np.isfinite(result).all():
        raise ValueError('Nonfinite public pair feature')
    return result


def batch_pair_features(state: dict, pairs, context: dict | None = None) -> np.ndarray:
    """Extract pairs of member dicts, aggregating feedback just once per state."""
    context = prepare_state(state) if context is None else context
    rows = [pair_features(state, a, b, context) for a, b in pairs]
    return np.stack(rows) if rows else np.empty((0, len(feature_names())), dtype=float)
