"""Simulators for round 2.

* LawSimulator: the *reference* implementation. A minimal subclass of the frozen
  kit.Simulator whose only edits insert law parameters; with a standard law every
  inserted value equals the kit literal, so it is kit itself.
* FastSimulator: an infrastructure-only optimisation (incremental availability,
  pause/busy indices, no deepcopy of immutable history). It must reproduce the
  reference exactly: identical observations, RNG consumption, errors, events and
  metrics. certify.py checks this on every law before any science cell runs.

Neither simulator ever exposes truth/bias/response_rate/exit_day to policies.
"""
import hashlib
import math

import kit
from kit import HARD, SOFT, VERSION, eligibility, rand_for

from . import laws as L
from .oracle_value import oracle_expectations

_MEMBER_KEYS = ('member_id', 'pool_id', 'synthetic', 'age', 'gender', 'zone', 'arrived_day',
                'fields', 'field_status', 'field_observed_day', 'source')


def _law_params(world, law):
    if law is not None:
        return law
    variant = world['variant']
    return L.get(variant) if variant in L.STANDARD else dict(L.DEFAULTS, name=variant, base_family=variant)


class LawSimulator(kit.Simulator):
    """Reference: kit.Simulator with law parameters substituted for literals."""

    def __init__(self, world, law=None):
        super().__init__(world)
        self.law = _law_params(world, law)
        self.law_weights = L.weights_for(self.law, self.world)
        self.law_schedule = L.drift_schedule(self.law, self.world['variant'])

    def _rate(self, actor):
        decay = self.law['response_decay']
        return actor['response_rate'] * (decay[1] if decay and self.day >= decay[0] else 1.0)

    def _prob(self, a, b, shared):
        f, g = a['truth'], b['truth']
        fit = sum(w * (1 if f[k] == g[k] else -.5) for k, w in self.law_weights.items())
        drift = L.drift_offset(self.law_schedule, self.day)
        z = -.25 + a['bias'] + fit + shared + drift
        return 1 / (1 + math.exp(-z))

    def advance(self, pairs):
        # Verbatim kit.advance except the marked law substitutions.
        used = set()
        for pair in pairs:
            if len(pair) != 2: raise ValueError('pair length')
            a, b = pair
            if a not in self.members or b not in self.members: raise ValueError('unknown member')
            if a in used or b in used: raise ValueError('overlapping allocation')
            used.update(pair)
            if not all(self.available(self.members[i]) for i in pair): raise ValueError('unavailable member')
            if tuple(sorted(pair)) in self.past: raise ValueError('repeat pair')
            if eligibility(self.members[a], self.members[b])['status'] != 'feasible': raise ValueError('hard constraint violation or missing constraint')
        law = self.law
        for a, b in sorted([sorted(p) for p in pairs]):
            self.past.add((a, b)); ma, mb = self.members[a], self.members[b]
            r = rand_for(self.world['seed'], a, b, self.day)
            mid = 'intro_' + hashlib.sha256(f'{a}|{b}|{self.day}'.encode()).hexdigest()[:24]
            self.introductions.append({'introduction_id': mid, 'user_a': a, 'user_b': b, 'assigned_day': self.day, 'response_deadline_day': self.day + 7, 'logging_policy': 'baseline_or_submitted_policy', 'propensity': None})
            shared = r.gauss(0, .45); responded = []; accept = []; response_days = []
            for actor, other in ((ma, mb), (mb, ma)):
                responded.append(r.random() < self._rate(actor))                      # LAW: response decay
                accept.append(r.random() < self._prob(actor, other, shared))
                delay = r.randint(1, 7); response_days.append(self.day + delay)
                self.events.append({'introduction_id': mid, 'member_id': actor['member_id'], 'event': 'introduction_response',
                                    'value': ('yes' if accept[-1] else 'no') if responded[-1] else None,
                                    'missing_reason': None if responded[-1] else 'no_response',
                                    'occurred_day': self.day + delay if responded[-1] else None,
                                    'observed_day': self.day + delay if responded[-1] else self.day + 7})
            for i in (a, b): self.busy[i] = self.day + 8
            if all(responded) and all(accept):
                date_day = max(response_days) + r.randint(1, 14)
                if self.world['variant'] == 'delayed': date_day += r.randint(5, 12)
                if law['extra_date_delay'] is not None: date_day += r.randint(*law['extra_date_delay'])  # LAW
                happened = r.random() < law['date_prob']                               # LAW (.78)
                self.events.append({'introduction_id': mid, 'member_id': None, 'event': 'date_happened',
                                    'value': happened, 'occurred_day': date_day, 'observed_day': date_day})
                seconds = []; on_time = []
                for i in (a, b): self.busy[i] = date_day + 6
                if happened:
                    for actor, other in ((ma, mb), (mb, ma)):
                        answer = r.random() < self._rate(actor); delay = r.randint(1, law['second_delay_max'])  # LAW
                        p = 1 / (1 + math.exp(-(.15 + actor['second_bias'] + shared + .4 * (actor['truth']['relationship_goal'] == other['truth']['relationship_goal']))))
                        yes = r.random() < p; seconds.append(answer and yes); on_time.append(delay <= 3)
                        self.events.append({'introduction_id': mid, 'member_id': actor['member_id'], 'event': 'second_meeting_intention',
                                            'value': ('yes' if yes else 'no') if answer else None, 'missing_reason': None if answer else 'no_response',
                                            'occurred_day': date_day + delay if answer else None, 'observed_day': date_day + delay if answer else date_day + 5})
                    if all(seconds):
                        retire_day = max(e['observed_day'] for e in self.events if e['introduction_id'] == mid)
                        self.events.append({'introduction_id': mid, 'member_id': None, 'event': 'pause_after_mutual_interest', 'value': True,
                                            'occurred_day': retire_day, 'observed_day': retire_day})
        self.day += 1; self.ask_spent = 0


def _copy_fields(fields):
    return {k: (v[:] if isinstance(v, list) else v) for k, v in fields.items()}


def _copy_ask(entry):
    return {'member_id': entry['member_id'], 'field': entry['field'], 'observed_day': entry['observed_day'],
            'values': _copy_fields(entry['values']), 'statuses': dict(entry['statuses'])}


class FastSimulator:
    """Optimised, behaviour-identical law simulator with host-only RB oracle."""

    def __init__(self, world, law=None):
        import copy
        self.world = copy.deepcopy(world)
        self.law = _law_params(self.world, law)
        self.variant = self.world['variant']
        self.seed = self.world['seed']
        self.members = {m['member_id']: m for m in self.world['members']}
        self.order = list(self.members)
        self.index = {i: n for n, i in enumerate(self.order)}
        self.day = 0
        self.busy, self.paused_from = {}, {}
        self.past, self.introductions, self.events = set(), [], []
        self.events_by_intro = {}
        self.ask_spent = self.asks_total = 0
        self.ask_log = []
        self.weights = L.weights_for(self.law, self.world)
        self.schedule = L.drift_schedule(self.law, self.variant)
        self.expectations = []          # host-only, aligned with self.introductions
        self.pause_count = 0

    # --- public state -------------------------------------------------------
    def _available_id(self, i):
        m = self.members[i]
        return (m['arrived_day'] <= self.day < m['exit_day'] and self.paused_from.get(i, 10**9) > self.day
                and self.busy.get(i, -1) <= self.day)

    def available(self, m):
        return self._available_id(m['member_id'])

    def observe(self):
        day = self.day
        visible = []
        for i in self.order:
            m = self.members[i]
            if m['arrived_day'] > day:
                continue
            visible.append({'member_id': i, 'pool_id': m['pool_id'], 'synthetic': m['synthetic'], 'age': m['age'],
                            'gender': m['gender'], 'zone': m['zone'], 'arrived_day': m['arrived_day'],
                            'fields': _copy_fields(m['fields']), 'field_status': dict(m['field_status']),
                            'field_observed_day': dict(m['field_observed_day']), 'source': m['source'],
                            'available': self._available_id(i)})
        return {'schema_version': VERSION, 'synthetic': True, 'day': day, 'ask_budget_remaining': 12 - self.ask_spent,
                'members': visible, 'introductions': [dict(x) for x in self.introductions],
                'feedback': [dict(e) for e in self.events if e['observed_day'] <= day],
                'ask_log': [_copy_ask(x) for x in self.ask_log]}

    # --- actions ------------------------------------------------------------
    def resolve_asks(self, asks):
        cost = 0; seen = set()
        for a in asks:
            ident = a['member_id']; field = a['field']
            if ident not in self.members or not self._available_id(ident): raise ValueError('ask member unavailable')
            if field not in ['constraints'] + SOFT: raise ValueError('unknown ask field')
            if (ident, field) in seen: raise ValueError('duplicate ask')
            seen.add((ident, field)); cost += 3 if field == 'constraints' else 1
        if cost + self.ask_spent > 12: raise ValueError('ask budget exceeded')
        self.ask_spent += cost; self.asks_total += cost; out = []
        for a in asks:
            m = self.members[a['member_id']]; keys = HARD if a['field'] == 'constraints' else [a['field']]
            for k in keys:
                if m['field_status'][k] != 'declined':
                    v = m['truth'][k]
                    m['fields'][k] = v[:] if isinstance(v, list) else v
                    m['field_status'][k] = 'observed'; m['field_observed_day'][k] = self.day
            out.append({'member_id': a['member_id'], 'field': a['field'], 'observed_day': self.day,
                        'values': {k: (m['fields'][k][:] if isinstance(m['fields'][k], list) else m['fields'][k]) for k in keys},
                        'statuses': {k: m['field_status'][k] for k in keys}})
        self.ask_log.extend(_copy_ask(x) for x in out)
        return out

    def _rate(self, actor):
        decay = self.law['response_decay']
        return actor['response_rate'] * (decay[1] if decay and self.day >= decay[0] else 1.0)

    def _event(self, mid, event):
        self.events.append(event)
        self.events_by_intro.setdefault(mid, []).append(event)

    def advance(self, pairs):
        used = set()
        for pair in pairs:
            if len(pair) != 2: raise ValueError('pair length')
            a, b = pair
            if a not in self.members or b not in self.members: raise ValueError('unknown member')
            if a in used or b in used: raise ValueError('overlapping allocation')
            used.update(pair)
            if not all(self._available_id(i) for i in pair): raise ValueError('unavailable member')
            if tuple(sorted(pair)) in self.past: raise ValueError('repeat pair')
            if eligibility(self.members[a], self.members[b])['status'] != 'feasible': raise ValueError('hard constraint violation or missing constraint')
        law, day = self.law, self.day
        drift = L.drift_offset(self.schedule, day)
        decay = law['response_decay']
        factor = decay[1] if decay and day >= decay[0] else 1.0
        for a, b in sorted([sorted(p) for p in pairs]):
            self.past.add((a, b)); ma, mb = self.members[a], self.members[b]
            r = rand_for(self.seed, a, b, day)
            mid = 'intro_' + hashlib.sha256(f'{a}|{b}|{day}'.encode()).hexdigest()[:24]
            self.introductions.append({'introduction_id': mid, 'user_a': a, 'user_b': b, 'assigned_day': day, 'response_deadline_day': day + 7, 'logging_policy': 'baseline_or_submitted_policy', 'propensity': None})
            self.expectations.append(oracle_expectations(
                ma, mb, day, weights=self.weights, drift_offset=drift, rate_factor=factor,
                date_prob=law['date_prob'], second_delay_max=law['second_delay_max'],
                delayed=self.variant == 'delayed', extra_delay=law['extra_date_delay']))
            shared = r.gauss(0, .45); responded = []; accept = []; response_days = []
            for actor, other in ((ma, mb), (mb, ma)):
                responded.append(r.random() < actor['response_rate'] * factor)
                f, g = actor['truth'], other['truth']
                fit = sum(w * (1 if f[k] == g[k] else -.5) for k, w in self.weights.items())
                p = 1 / (1 + math.exp(-(-.25 + actor['bias'] + fit + shared + drift)))
                accept.append(r.random() < p)
                delay = r.randint(1, 7); response_days.append(day + delay)
                self._event(mid, {'introduction_id': mid, 'member_id': actor['member_id'], 'event': 'introduction_response',
                                  'value': ('yes' if accept[-1] else 'no') if responded[-1] else None,
                                  'missing_reason': None if responded[-1] else 'no_response',
                                  'occurred_day': day + delay if responded[-1] else None,
                                  'observed_day': day + delay if responded[-1] else day + 7})
            for i in (a, b): self.busy[i] = day + 8
            if all(responded) and all(accept):
                date_day = max(response_days) + r.randint(1, 14)
                if self.variant == 'delayed': date_day += r.randint(5, 12)
                if law['extra_date_delay'] is not None: date_day += r.randint(*law['extra_date_delay'])
                happened = r.random() < law['date_prob']
                self._event(mid, {'introduction_id': mid, 'member_id': None, 'event': 'date_happened',
                                  'value': happened, 'occurred_day': date_day, 'observed_day': date_day})
                seconds = []
                for i in (a, b): self.busy[i] = date_day + 6
                if happened:
                    for actor, other in ((ma, mb), (mb, ma)):
                        answer = r.random() < actor['response_rate'] * factor; delay = r.randint(1, law['second_delay_max'])
                        p = 1 / (1 + math.exp(-(.15 + actor['second_bias'] + shared + .4 * (actor['truth']['relationship_goal'] == other['truth']['relationship_goal']))))
                        yes = r.random() < p; seconds.append(answer and yes)
                        self._event(mid, {'introduction_id': mid, 'member_id': actor['member_id'], 'event': 'second_meeting_intention',
                                          'value': ('yes' if yes else 'no') if answer else None, 'missing_reason': None if answer else 'no_response',
                                          'occurred_day': date_day + delay if answer else None, 'observed_day': date_day + delay if answer else date_day + 5})
                    if all(seconds):
                        retire_day = max(e['observed_day'] for e in self.events_by_intro[mid])
                        self._event(mid, {'introduction_id': mid, 'member_id': None, 'event': 'pause_after_mutual_interest', 'value': True,
                                          'occurred_day': retire_day, 'observed_day': retire_day})
                        for i in (a, b):
                            self.paused_from[i] = min(self.paused_from.get(i, 10**9), retire_day)
        self.day += 1; self.ask_spent = 0

    # --- outcomes (host only) ----------------------------------------------
    def intro_outcomes(self):
        """Per introduction: (mutual, date, msmi, yes_a, yes_b) exactly as kit.metrics counts them."""
        out = []
        for intro in self.introductions:
            es = [e for e in self.events_by_intro.get(intro['introduction_id'], ()) if e['observed_day'] <= self.day]
            rs = [e for e in es if e['event'] == 'introduction_response']
            mutual = len(rs) == 2 and all(e['value'] == 'yes' for e in rs)
            ds = [e for e in es if e['event'] == 'date_happened' and e['value'] is True]
            ss = [e for e in es if e['event'] == 'second_meeting_intention']
            msmi = bool(ds) and ds[0]['occurred_day'] - intro['assigned_day'] <= 30 and len(ss) == 2 and all(
                e['value'] == 'yes' and e['occurred_day'] - ds[0]['occurred_day'] <= 3 for e in ss)
            ya = next((e['value'] for e in rs if e['member_id'] == intro['user_a']), None)
            yb = next((e['value'] for e in rs if e['member_id'] == intro['user_b']), None)
            out.append((bool(mutual), bool(ds), bool(msmi), ya, yb))
        return out

    def metrics(self):
        """kit.Simulator.metrics() semantics, computed from indices."""
        mutual = dates = msmi = missing = 0
        for intro, (mu, da, ms, _, _) in zip(self.introductions, self.intro_outcomes()):
            mutual += mu; dates += da; msmi += ms
            missing += sum(e.get('missing_reason') == 'no_response'
                           for e in self.events_by_intro.get(intro['introduction_id'], ()) if e['observed_day'] <= self.day)
        denominator = sum(m['arrived_day'] <= self.day for m in self.members.values())
        return {'assignments': len(self.introductions), 'mutual_acceptances': mutual, 'dates': dates,
                'mutual_second_meeting_intention': msmi, 'missing_feedback': missing, 'ask_cost': self.asks_total,
                'arrived_members': denominator, 'msmi_per_100_arrived_members': 100 * msmi / max(1, denominator),
                'status': 'simulated_not_observed_product_performance'}
