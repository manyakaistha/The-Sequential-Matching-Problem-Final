"""Observation-only round-four policy. Public mechanisms only; no file reads."""
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
from research4.candidates import CANDIDATES, decision



def inner(request, cfg):
    return decision(request, cfg)


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
        print('round4 fallback: '+type(error).__name__, file=sys.stderr)
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
