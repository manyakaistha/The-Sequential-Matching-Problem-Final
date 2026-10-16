"""Arm registry: arm id -> (callable, static config, metadata).

meta.asks == 'G' marks arms whose asking must be byte-identical to the supplied
greedy (kit.baseline_asks); the audit verifies identical ask-log digests per world.
meta.prior names the theta file injected by the host (hash-bound in registrations).
"""
import policy as official
from research7b.workspace.research7.policies import references

from .policies import asking, model


def _official(mode):
    return lambda request, config: official.decide(request, mode)


ARMS = {
    # supplied baselines
    'G': dict(fn=_official('greedy'), config={}, asks='G', deployable=True, family='supplied'),
    'N': dict(fn=_official('no_asks'), config={}, asks='none', deployable=True, family='supplied'),
    'R': dict(fn=_official('random'), config={}, asks='G', deployable=True, family='supplied'),
    # frozen prior-round references (simulator-specific parameters inside)
    'P': dict(fn=references.decide, config={'id': 'P'}, asks='G', deployable=True, family='reference'),
    'Q6': dict(fn=references.decide, config={'id': 'Q6'}, asks='other', deployable=True, family='reference'),
    # ask-order probes, greedy matching fixed
    'G_arr': dict(fn=asking.decide_order, config={'order': 'arrival'}, asks='other', deployable=True, family='ask_order'),
    'G_lifo': dict(fn=asking.decide_order, config={'order': 'lifo'}, asks='other', deployable=True, family='ask_order'),
    'G_hash': dict(fn=asking.decide_order, config={'order': 'hashed'}, asks='other', deployable=True, family='ask_order'),
    'G_deg': dict(fn=asking.decide_order, config={'order': 'degree'}, asks='other', deployable=True, family='ask_order'),
    # parametric static scorer under three priors (Q2)
    'PS_sim': dict(fn=model.decide, config={'variant': 'PS'}, prior='sim', asks='G', deployable=True, family='model'),
    'PS_emp': dict(fn=model.decide, config={'variant': 'PS'}, prior='emp', asks='G', deployable=True, family='model'),
    'PS_flat': dict(fn=model.decide, config={'variant': 'PS'}, prior='flat', asks='G', deployable=True, family='model'),
    # N3_two acquisition under three hard-field priors (Q2); research6 sampler == Q6 control
    'N3e_r6': dict(fn=asking.decide_n3e, config={'sampler': 'research6'}, asks='other', deployable=True, family='acquisition'),
    'N3e_sim': dict(fn=asking.decide_n3e, config={}, prior='sim', asks='other', deployable=True, family='acquisition'),
    'N3e_emp': dict(fn=asking.decide_n3e, config={}, prior='emp', asks='other', deployable=True, family='acquisition'),
    'N3e_flat': dict(fn=asking.decide_n3e, config={}, prior='flat', asks='other', deployable=True, family='acquisition'),
    # small adaptive alternative and ablations (Q3)
    'X1_emp': dict(fn=model.decide, config={'variant': 'X1'}, prior='emp', asks='G', deployable=True, family='adaptive'),
    'X1_sim': dict(fn=model.decide, config={'variant': 'X1'}, prior='sim', asks='G', deployable=True, family='adaptive'),
    'X1_nocal_emp': dict(fn=model.decide, config={'variant': 'X1_nocal'}, prior='emp', asks='G', deployable=True, family='adaptive'),
    'X1_nolearn_emp': dict(fn=model.decide, config={'variant': 'X1_nolearn'}, prior='emp', asks='G', deployable=True, family='adaptive'),
    'X1_oracle': dict(fn=model.decide, config={'variant': 'X1_oracle'}, prior='sim', asks='G', deployable=False, family='adaptive'),
}

PREDICTING = {a for a, m in ARMS.items() if m['fn'] is model.decide}


def config_for(arm, law, thetas):
    meta = ARMS[arm]
    cfg = dict(meta['config'])
    if 'prior' in meta:
        cfg['theta'] = thetas[meta['prior']]
    if cfg.get('variant') == 'X1_oracle':
        from .laws import drift_schedule
        cfg['oracle_drift'] = [list(x) for x in drift_schedule(law, law['base_family'])]
    return cfg
