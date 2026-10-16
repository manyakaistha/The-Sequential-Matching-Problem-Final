"""Adapters to the six unchanged reference policies, using public requests only."""
import copy
import policy as official
from research6.policies import policy as round6

LAST_STATUS = {'fallback': False, 'reason': None}


def decide(request, config):
    global LAST_STATUS
    ident = config['id']
    LAST_STATUS = {'fallback': False, 'reason': None}
    if ident in ('G', 'N', 'R'):
        return official.decide(request, {'G': 'greedy', 'N': 'no_asks', 'R': 'random'}[ident])
    if ident not in ('P', 'K', 'Q6'):
        raise ValueError('Unknown frozen reference')
    result = round6.decide(request, {'id': {'P': 'P', 'K': 'K', 'Q6': 'N3_two'}[ident]})
    LAST_STATUS = copy.deepcopy(round6.LAST_STATUS)
    return result
