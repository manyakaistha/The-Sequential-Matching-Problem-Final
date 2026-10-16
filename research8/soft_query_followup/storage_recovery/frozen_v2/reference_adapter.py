"""Frozen Q6/P behavior; propagate fallback telemetry without changing actions."""
import copy
from research7b.workspace.research7.policies import references

LAST_STATUS = {'fallback': False, 'reason': None}


def decide(request, config):
    global LAST_STATUS
    response = references.decide(request, config)
    LAST_STATUS = copy.deepcopy(references.LAST_STATUS)
    return response
