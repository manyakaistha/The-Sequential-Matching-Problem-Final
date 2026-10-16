"""Prior parameter sets (theta). 'sim' transcribes simulator literals; 'flat' is uninformative.
'emp' is produced by fit_priors.py from observable training data only and stored as
priors/emp.json (hash-registered before any study that uses it).
"""
import json
from pathlib import Path

from .oracle_value import date_within_probability

HERE = Path(__file__).resolve().parent / 'priors'


def _uniform(values):
    return {str(v): 1 / len(values) for v in values}


def sim_theta():
    m, v = (.55 + .98) / 2, (.98 - .55) ** 2 / 12
    total = m * (1 - m) / v - 1
    return {
        'name': 'sim', 'source': 'transcribed from kit.py generate/_prob/advance literals',
        'soft_equal_prob': {'relationship_goal': 1 / 2, 'relationship_pace': 1 / 3, 'lifestyle': 1 / 3,
                            'conversations': 1 / 4},
        'accept': {'intercept': -.25, 'bias_sd': .7, 'shared_sd': .45,
                   'weights': {'relationship_goal': .7, 'relationship_pace': .4, 'lifestyle': .25, 'conversations': .2}},
        'response': {'alpha': m * total, 'beta': (1 - m) * total},
        'date': {'p_happen': .78, 'p_within30': 5 / 6 + date_within_probability(True, None, None) / 6},
        'second': {'intercept': .15, 'goal_coef': .4, 'bias_sd': .5, 'p_on_time': 3 / 5},
        'hard': {
            'age_min_offset': _uniform(range(3, 11)), 'age_max_offset': _uniform(range(3, 11)),
            'who_to_meet_size': {'1': .7, '2': .2, '3': .1},
            'gender_inclusion': _uniform(['woman', 'man', 'non_binary']),
            'relationship_structure': {'monogamous': .9, 'non_monogamous': .1},
            'smoking': {'no': .75, 'occasionally': .2, 'yes': .05},
            'partner_smoking': _uniform(['no_smoking', 'any']),
            'has_children': .15,
            'partner_children': _uniform(['any', 'no_children']),
            'wants_children': _uniform(['yes', 'no', 'unsure']),
            'extra_zone': .3, 'extra_zone_choice': _uniform(['zone_a', 'zone_b', 'zone_c', 'zone_d']),
            'schedule_size': _uniform([1, 2, 3]),
        },
    }


def flat_theta():
    return {
        'name': 'flat', 'source': 'uninformative negative control',
        'soft_equal_prob': {'relationship_goal': .5, 'relationship_pace': .5, 'lifestyle': .5, 'conversations': .5},
        'accept': {'intercept': 0.0, 'bias_sd': 0.0, 'shared_sd': 0.0,
                   'weights': {'relationship_goal': 0.0, 'relationship_pace': 0.0, 'lifestyle': 0.0, 'conversations': 0.0}},
        'response': {'alpha': 1.0, 'beta': 1.0},
        'date': {'p_happen': .5, 'p_within30': 1.0},
        'second': {'intercept': 0.0, 'goal_coef': 0.0, 'bias_sd': 0.0, 'p_on_time': .5},
        'hard': {
            'age_min_offset': _uniform(range(1, 16)), 'age_max_offset': _uniform(range(1, 16)),
            'who_to_meet_size': _uniform([1, 2, 3]),
            'gender_inclusion': _uniform(['woman', 'man', 'non_binary']),
            'relationship_structure': _uniform(['monogamous', 'non_monogamous']),
            'smoking': _uniform(['no', 'occasionally', 'yes']),
            'partner_smoking': _uniform(['no_smoking', 'any']),
            'has_children': .5,
            'partner_children': _uniform(['any', 'no_children']),
            'wants_children': _uniform(['yes', 'no', 'unsure']),
            'extra_zone': .5, 'extra_zone_choice': _uniform(['zone_a', 'zone_b', 'zone_c', 'zone_d']),
            'schedule_size': _uniform([1, 2, 3]),
        },
    }


def write_builtin():
    HERE.mkdir(exist_ok=True)
    for theta in (sim_theta(), flat_theta()):
        path = HERE / f"{theta['name']}.json"
        data = json.dumps(theta, indent=2, sort_keys=True) + '\n'
        if path.exists() and path.read_text() != data:
            raise RuntimeError(f'{path} differs from builtin; refusing to overwrite')
        path.write_text(data)


def load(name):
    return json.loads((HERE / f'{name}.json').read_text())
