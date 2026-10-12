"""Observation-only round-three policy. Public mechanisms only; no file reads."""
import argparse
import hashlib
import itertools
import json
import signal
import sys
import time
from kit import HARD, baseline_asks, baseline_match, eligibility

LIMIT = 1024 * 1024
FALLBACK_COUNT = 0  # Host-only instrumentation; never an inference input.
CANDIDATES = {
    'greedy': {},
    'clean': {'mode': 'clean'},
    'goal': {'mode': 'goal'},
    'canonical': {'mode': 'canonical'},
    'random_order': {'mode': 'random'},
    'public_weight': {'mode': 'public_weight'},
    'population': {'mode': 'population'},
    'scarce': {'mode': 'scarce'},
    'response': {'mode': 'response'},
    'throughput': {'mode': 'throughput'},
    'offline': {'mode': 'offline'},
    'goal_queries': {'mode': 'public_weight', 'soft': 'goal'},
    'four_queries': {'mode': 'population', 'soft': 'four'},
}


def legal_edges(state):
    active = [m for m in state['members'] if m.get('available')]
    past = {tuple(sorted((i['user_a'], i['user_b']))) for i in state['introductions']}
    return [tuple(sorted((a['member_id'], b['member_id'])))
            for a, b in itertools.combinations(active, 2)
            if tuple(sorted((a['member_id'], b['member_id']))) not in past
            and eligibility(a, b)['status'] == 'feasible']


def asks(state, cfg):
    out = baseline_asks(state)
    budget = state['ask_budget_remaining'] - 3 * len(out)
    if not cfg.get('soft') or budget <= 0:
        return out
    edges = legal_edges(state)
    degree = {}
    for p in edges:
        for u in p:
            degree[u] = degree.get(u, 0) + 1
    fields = ('relationship_goal',) if cfg['soft'] == 'goal' else (
        'relationship_goal', 'relationship_pace', 'conversations', 'lifestyle')
    # Surplus only: no hard bundle is displaced. Rank by current legal exposure.
    eligible = sorted([m for m in state['members'] if m['member_id'] in degree],
                      key=lambda m: (-degree[m['member_id']], m['member_id']))
    for field in fields:
        for m in eligible:
            if budget <= 0:
                return out
            if m['fields'].get(field) is None and m['field_status'].get(field) != 'declined':
                out.append({'member_id': m['member_id'], 'field': field})
                budget -= 1
    return out


def inner(request, cfg):
    state = request['state']
    if request['phase'] == 'ask':
        return {'asks': asks(state, cfg), 'memory': {}}
    mode = cfg.get('mode', 'greedy')
    if mode == 'greedy':
        return {'pairs': baseline_match(state), 'memory': {}}
    edges = legal_edges(state)
    members = {m['member_id']: m for m in state['members']}
    if mode in ('clean', 'goal', 'canonical', 'random'):
        fields = ('relationship_goal',) if mode == 'goal' else (
            'relationship_goal', 'relationship_pace', 'lifestyle', 'conversations')
        def score(pair):
            if mode == 'canonical':
                return 1
            if mode == 'random':
                return int.from_bytes(hashlib.sha256((str(state['day'])+'|'+ '|'.join(pair)).encode()).digest()[:8], 'big')
            a, b = (members[i] for i in pair)
            return 1 + sum(a['fields'].get(k) is not None and
                           a['fields'].get(k) == b['fields'].get(k) for k in fields)
        ranked = [(score(p), p) for p in edges]
    else:
        from research3.model_candidates import score_edges
        ranked = score_edges(state, edges, mode)
    used, pairs = set(), []
    for score, pair in sorted(ranked, key=lambda row: (-row[0], row[1])):
        if score > 0 and not used.intersection(pair):
            used.update(pair)
            pairs.append(list(pair))
    return {'pairs': sorted(pairs), 'memory': {}}


class Deadline(BaseException):
    pass


def decide(request, config=None):
    global FALLBACK_COUNT
    cfg = config or {}
    key = 'asks' if isinstance(request, dict) and request.get('phase') == 'ask' else 'pairs'
    empty = {key: [], 'memory': {}}
    previous = None
    installed = False
    old_timer = (0., 0.)
    started = time.monotonic()
    try:
        if not isinstance(request, dict) or request.get('phase') not in ('ask', 'match'):
            return empty
        if len(json.dumps(request, allow_nan=False).encode()) > LIMIT:
            return empty
        # Invocation-only guard; malformed supplied memory is discarded by design.
        previous = signal.getsignal(signal.SIGALRM)
        old_timer = signal.getitimer(signal.ITIMER_REAL)
        signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(Deadline()))
        installed = True
        signal.setitimer(signal.ITIMER_REAL, min(7., old_timer[0]) if old_timer[0] else 7.)
        return inner(request, cfg)
    except (Deadline, ValueError, TypeError, KeyError, AttributeError, IndexError, ArithmeticError) as error:
        FALLBACK_COUNT += 1
        print('round3 fallback: '+type(error).__name__, file=sys.stderr)
        return empty
    finally:
        if installed:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous)
            if old_timer[0]:
                signal.setitimer(signal.ITIMER_REAL, max(.001, old_timer[0]-(time.monotonic()-started)), old_timer[1])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--candidate', default='greedy', choices=CANDIDATES)
    p.add_argument('--baseline', default='greedy')
    args = p.parse_args()
    request = {}
    try:
        raw = sys.stdin.buffer.read(LIMIT + 1)
        if len(raw) > LIMIT:
            raise ValueError('oversized request')
        request = json.loads(raw, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
    except (ValueError, UnicodeError):
        pass
    print(json.dumps(decide(request, CANDIDATES[args.candidate]), allow_nan=False))


if __name__ == '__main__':
    main()
