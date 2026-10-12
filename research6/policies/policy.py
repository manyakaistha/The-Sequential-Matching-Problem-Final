"""JSON-only entrypoint with seven-second interruption and shipped fallback."""
import argparse
import json
import signal
import sys
import time

from kit import HARD, baseline_asks, baseline_match
from . import allocation

LIMIT = 1024 * 1024
CANDIDATES = ('G', 'P', 'K', 'N1', 'N2', 'N3', 'N3_fifo4', 'N3_two')
# Host-only per-invocation telemetry; never read by candidate action selection.
LAST_STATUS = {'fallback': False, 'reason': None}


class Deadline(BaseException):
    pass


def validate_request(request):
    if not isinstance(request, dict) or request.get('phase') not in ('ask', 'match'):
        raise ValueError('invalid request phase')
    state = request['state']
    if not isinstance(state, dict):
        raise ValueError('invalid state')
    if type(state['day']) is not int or not 0 <= state['day'] < 60:
        raise ValueError('invalid day')
    if type(state['ask_budget_remaining']) is not int or not 0 <= state['ask_budget_remaining'] <= 12:
        raise ValueError('invalid ask budget')
    members = state['members']
    if not isinstance(members, list) or len(members) > 200:
        raise ValueError('invalid member count')
    ids = set()
    for member in members:
        ident = member['member_id']
        if not isinstance(ident, str) or not ident or ident in ids:
            raise ValueError('invalid member ID')
        ids.add(ident)
        if (type(member['available']) is not bool or
                type(member['age']) is not int or
                not all(isinstance(member[k], str) for k in ('pool_id', 'gender', 'zone')) or
                not isinstance(member['fields'], dict) or
                not isinstance(member['field_status'], dict)):
            raise ValueError('invalid member shape')
        fields = member['fields']
        for field in HARD:
            value = fields[field]
            if member['field_status'][field] not in ('observed', 'declined', 'not_asked'):
                raise ValueError('invalid field status')
            if value is None:
                continue
            if field in ('age_min', 'age_max'):
                valid = type(value) is int
            elif field in ('who_to_meet', 'acceptable_zones', 'schedule'):
                valid = isinstance(value, list) and all(isinstance(x, str) for x in value)
            elif field == 'has_children':
                valid = type(value) is bool
            else:
                valid = isinstance(value, str)
            if not valid:
                raise ValueError('invalid hard field')
    if not isinstance(state['introductions'], list):
        raise ValueError('invalid introductions')
    for intro in state['introductions']:
        if intro['user_a'] not in ids or intro['user_b'] not in ids:
            raise ValueError('invalid introduction endpoint')


def _baseline(request):
    key = 'asks' if request['phase'] == 'ask' else 'pairs'
    function = baseline_asks if key == 'asks' else baseline_match
    return {key: function(request['state']), 'memory': {}}


def decide(request, config=None):
    global LAST_STATUS
    LAST_STATUS = {'fallback': False, 'reason': None}
    key = 'asks' if isinstance(request, dict) and request.get('phase') == 'ask' else 'pairs'
    empty = {key: [], 'memory': {}}
    valid = False
    installed = False
    started = time.monotonic()
    old_timer = (0., 0.)
    previous = None
    try:
        # Clone inputs through strict JSON; no input or configuration is mutated.
        raw = json.dumps(request, allow_nan=False)
        if len(raw.encode('utf-8')) > LIMIT:
            raise ValueError('oversized request')
        request = json.loads(raw)
        validate_request(request)
        valid = True
        cfg = json.loads(json.dumps(config or {'id': 'G'}, allow_nan=False))
        if cfg.get('id') not in CANDIDATES:
            raise ValueError('unknown candidate')
        previous = signal.getsignal(signal.SIGALRM)
        old_timer = signal.getitimer(signal.ITIMER_REAL)
        signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(Deadline()))
        installed = True
        signal.setitimer(signal.ITIMER_REAL, min(7., old_timer[0]) if old_timer[0] else 7.)
        return allocation.action(request, cfg)
    except (Deadline, Exception) as error:
        LAST_STATUS = {'fallback': True, 'reason': type(error).__name__}
        # Stop candidate timer before the bounded shipped fallback is rebuilt.
        if installed:
            signal.setitimer(signal.ITIMER_REAL, 0)
        print('research6 fallback: '+type(error).__name__, file=sys.stderr)
        return _baseline(request) if valid else empty
    finally:
        if installed:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous)
            if old_timer[0]:
                signal.setitimer(signal.ITIMER_REAL,
                    max(.001, old_timer[0]-(time.monotonic()-started)), old_timer[1])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', choices=CANDIDATES, default='G')
    args = parser.parse_args()
    request = {}
    try:
        raw = sys.stdin.buffer.read(LIMIT + 1)
        if len(raw) > LIMIT:
            raise ValueError('oversized request')
        request = json.loads(raw, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
    except (ValueError, UnicodeError):
        print('research6 malformed JSON', file=sys.stderr)
    print(json.dumps(decide(request, {'id': args.candidate}), allow_nan=False))


if __name__ == '__main__':
    main()
