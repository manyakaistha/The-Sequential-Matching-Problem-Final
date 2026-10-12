"""Constructed graphs and observations only; no world generation or rollouts."""
import contextlib
import copy
import io
import itertools
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

from kit import HARD, SOFT, baseline_asks, baseline_match, eligibility
from research4.candidates import CANDIDATES, decision
from research6.policies import allocation, policy


def member(ident, schedule, soft='same'):
    fields = dict(age_min=18, age_max=65, who_to_meet=['woman'],
        relationship_structure='monogamous', smoking='no', partner_smoking='any',
        has_children=False, partner_children='any', wants_children='unsure',
        acceptable_zones=['zone_a'], schedule=schedule)
    fields.update({k: soft for k in SOFT})
    return dict(member_id=ident, pool_id='toy', age=30, gender='woman',
        zone='zone_a', arrived_day=0, available=True, fields=fields,
        field_status={k: 'observed' for k in fields})


def request():
    slots = ['weekday_evening', 'weekend_day', 'weekend_evening']
    members = [member('a', slots[:1], 'a'), member('b', slots[:2]),
               member('c', slots[1:]), member('d', slots[2:], 'd')]
    return {'phase': 'match', 'state': dict(day=0, members=members,
        introductions=[], feedback=[], ask_budget_remaining=12), 'memory': {}}


def exhaustive(scores):
    vertices = sorted({u for edge in scores for u in edge})
    def visit(remaining):
        if not remaining:
            return (0, 0)
        first, *rest = remaining
        choices = [visit(rest)]
        for other in rest:
            edge = tuple(sorted((first, other)))
            if edge in scores:
                count, score = visit([u for u in rest if u != other])
                choices.append((count+1, score+scores[edge]))
        return max(choices)
    return visit(vertices)


class AllocationTests(unittest.TestCase):
    def test_shipped_and_population_identity(self):
        req = request()
        for phase in ('ask', 'match'):
            req['phase'] = phase
            if phase == 'ask':
                for m in req['state']['members']:
                    m['fields']['age_min'] = None
                    m['field_status']['age_min'] = 'not_asked'
            expected = {'asks': baseline_asks(req['state']), 'memory': {}} if phase == 'ask' else {
                'pairs': baseline_match(req['state']), 'memory': {}}
            self.assertEqual(policy.decide(req, {'id': 'G'}), expected)
            self.assertEqual(policy.decide(req, {'id': 'P'}),
                             decision(req, CANDIDATES['population_control']))
        req = request()  # Nonempty allocation identity, not just missing-field case.
        self.assertEqual(policy.decide(req, {'id': 'G'}),
                         {'pairs': baseline_match(req['state']), 'memory': {}})
        self.assertEqual(policy.decide(req, {'id': 'P'}),
                         decision(req, CANDIDATES['population_control']))

    def test_length_three_trap_and_legality(self):
        req = request()
        self.assertEqual(baseline_match(req['state']), [['b', 'c']])
        for ident in ('N1', 'K'):
            self.assertEqual(policy.decide(req, {'id': ident})['pairs'], [['a', 'b'], ['c', 'd']])
        for ident in policy.CANDIDATES:
            result = policy.decide(req, {'id': ident})
            used = set()
            by_id = {m['member_id']: m for m in req['state']['members']}
            for a, b in result['pairs']:
                self.assertFalse(used.intersection((a, b)))
                self.assertEqual(eligibility(by_id[a], by_id[b])['status'], 'feasible')
                used.update((a, b))

    def test_exhaustive_cardinality_score_all_five_vertex_graphs(self):
        edges = list(itertools.combinations('abcde', 2))
        for mask in range(1 << len(edges)):
            scores = {edge: (index*3+mask) % 8 for index, edge in enumerate(edges)
                      if mask & (1 << index)}
            selected = allocation.cardinality_matching(scores)
            self.assertEqual((len(selected), sum(scores[e] for e in selected)), exhaustive(scores))

    def test_triangle_repeat_missing_and_unavailable(self):
        req = request()
        req['state']['members'] = [member(x, ['weekend_day']) for x in 'abc']
        for ident in policy.CANDIDATES:
            self.assertEqual(len(policy.decide(req, {'id': ident})['pairs']), 1)
        req['state']['introductions'] = [{'user_a': 'a', 'user_b': 'b'}]
        req['state']['members'][2]['available'] = False
        for ident in policy.CANDIDATES:
            self.assertEqual(policy.decide(req, {'id': ident})['pairs'], [])
        req['state']['introductions'] = []
        req['state']['members'][0]['fields']['age_min'] = None
        for ident in policy.CANDIDATES:
            self.assertEqual(policy.decide(req, {'id': ident})['pairs'], [])

    def test_tie_only_stability_and_json_immutability(self):
        scores = {('a', 'b'): 7, ('b', 'c'): 6, ('c', 'd'): 1}
        for day in range(60):
            self.assertEqual(allocation.stable_reranking(scores, day), [('a', 'b'), ('c', 'd')])
        tied = {e: 0 for e in itertools.combinations('abcdef', 2)}
        for block in range(8):
            first = allocation.stable_reranking(tied, block*8)
            for day in range(block*8, min(block*8+8, 60)):
                self.assertEqual(allocation.stable_reranking(tied, day), first)
        req = request()
        frozen = copy.deepcopy(req)
        cfg = {'id': 'N2'}
        for _ in range(2):
            policy.decide(req, cfg)
        self.assertEqual(req, frozen)
        self.assertEqual(cfg, {'id': 'N2'})

    def test_exception_and_deadline_fallback_and_malformed(self):
        req = request()
        for error in (RuntimeError('injected'), policy.Deadline()):
            with patch.object(allocation, 'action', side_effect=error), contextlib.redirect_stderr(io.StringIO()) as stderr:
                self.assertEqual(policy.decide(req, {'id': 'N1'}),
                                 {'pairs': baseline_match(req['state']), 'memory': {}})
                self.assertIn('fallback', stderr.getvalue())
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(policy.decide({'phase': 'ask'}), {'asks': [], 'memory': {}})

    def test_cli(self):
        req = request()
        result = subprocess.run([sys.executable, '-m', 'research6.policies.policy', '--candidate', 'N1'],
            input=json.dumps(req), text=True, capture_output=True, check=True, timeout=10)
        self.assertEqual(json.loads(result.stdout), policy.decide(req, {'id': 'N1'}))
        self.assertEqual(result.stderr, '')


if __name__ == '__main__':
    unittest.main()
