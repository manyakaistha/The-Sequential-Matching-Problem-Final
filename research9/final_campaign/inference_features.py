"""Vectorized inference for the frozen 74-column public feature contract.

The reference training extractor remains features.py. This implementation only
caches per-call actor values and broadcasts public pair indices; it introduces
no additional covariates or persistent state.
"""
from __future__ import annotations

import numpy as np

from .features import SOFT_FIELDS, _soft, feature_names, prepare_state


def batch_pair_features(state: dict, pairs, context: dict | None = None) -> np.ndarray:
    """Return the reference feature matrix for member-dict pairs as float64."""
    context = prepare_state(state) if context is None else context
    day = state['day']
    if context['day'] != day:
        raise ValueError('Feature context belongs to a different assignment day')
    # Object identity only deduplicates records within this call. Opaque member
    # IDs are used exclusively by the reference public-history join below.
    actors, positions, indices = [], {}, []
    for a, b in pairs:
        pair_indices = []
        for member in (a, b):
            identity = id(member)
            index = positions.get(identity)
            if index is None:
                index = len(actors)
                positions[identity] = index
                actors.append(member)
            pair_indices.append(index)
        indices.append(pair_indices)
    if not indices:
        return np.empty((0, len(feature_names())), dtype=np.float64)
    indices = np.asarray(indices, dtype=np.intp)
    left, right = indices[:, 0], indices[:, 1]
    soft = [_soft(member, day) for member in actors]
    values = np.asarray([item[0] for item in soft], dtype=object)
    known = np.asarray([[value is not None for value in item[0]] for item in soft])
    declined = np.asarray([item[1] for item in soft], dtype=np.float64)
    known_rate = known.sum(axis=1) / len(SOFT_FIELDS)
    ages = np.asarray([float(member['age']) for member in actors])
    tenure = np.asarray([float(day - member['arrived_day']) for member in actors])
    empty_history = np.array([[0., 0., 0., 0., .5, .5]] * 2)
    history = np.stack([context['histories'].get(member['member_id'], empty_history)
                        for member in actors])

    out = np.empty((len(indices), len(feature_names())), dtype=np.float64)
    ak, bk = known[left], known[right]
    both = ak & bk
    equal = values[left] == values[right]
    flags = out[:, :28].reshape(-1, len(SOFT_FIELDS), 4)
    flags[:, :, 0] = both & equal
    flags[:, :, 1] = both & ~equal
    flags[:, :, 2] = ak != bk
    flags[:, :, 3] = ~ak & ~bk
    out[:, 28] = np.minimum(declined[left], declined[right])
    out[:, 29] = np.maximum(declined[left], declined[right])
    out[:, 30] = np.minimum(known_rate[left], known_rate[right])
    out[:, 31] = np.maximum(known_rate[left], known_rate[right])
    out[:, 32] = np.abs(ages[left] - ages[right])
    out[:, 33] = day / 59.0
    out[:, 34] = np.minimum(tenure[left], tenure[right])
    out[:, 35] = np.maximum(tenure[left], tenure[right])
    out[:, 36] = np.minimum(ages[left], ages[right])
    out[:, 37] = np.maximum(ages[left], ages[right])
    histories = out[:, 38:].reshape(-1, 2, 6, 3)
    ah, bh = history[left], history[right]
    histories[:, :, :, 0] = np.minimum(ah, bh)
    histories[:, :, :, 1] = np.maximum(ah, bh)
    histories[:, :, :, 2] = (ah + bh) / 2
    if not np.isfinite(out).all():
        raise ValueError('Nonfinite public pair feature')
    return out
