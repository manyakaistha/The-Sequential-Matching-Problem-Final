"""Independent constructed-only review; never generates a simulator world."""
import contextlib
import copy
import gzip
import io
import itertools
import json
from pathlib import Path
import signal
import tempfile
import time
import unittest
from unittest.mock import patch

from kit import baseline_asks, baseline_match
from research4.candidates import CANDIDATES, decision
from research6 import recorder, orchestrator
from research6.policies import allocation, policy
from research6.tests.test_allocation import member, request, exhaustive
from research6.tests.test_recorder import FakeSimulator


class IndependentContracts(unittest.TestCase):
    def test_exact_baseline_identity_constructed_requests(self):
        for phase, budget, missing, declined in itertools.product(('ask', 'match'), (0, 2, 3, 12), (False, True), (False, True)):
            r = request(); r['phase'] = phase; r['state']['ask_budget_remaining'] = budget
            for m in r['state']['members']:
                if missing: m['fields']['age_min'] = None
                if declined: m['field_status']['age_min'] = 'declined'
            r['state']['introductions'] = [{'user_a': 'a', 'user_b': 'b'}]
            key = 'asks' if phase == 'ask' else 'pairs'
            shipped = baseline_asks if phase == 'ask' else baseline_match
            self.assertEqual(policy.decide(r, {'id': 'G'}), {key: shipped(r['state']), 'memory': {}})
            self.assertEqual(policy.decide(r, {'id': 'P'}), decision(r, dict(CANDIDATES['population_control'])))

    def test_n1_lexicographic_monotonicity_all_five_vertex_graphs(self):
        edges = list(itertools.combinations('abcde', 2))
        for mask in range(1024):
            scores = {e: (mask + i*5) % 8 for i, e in enumerate(edges) if mask & (1 << i)}
            used = set(); initial = []
            for edge in sorted(scores, key=lambda e: (-scores[e], e)):
                if not used.intersection(edge): initial.append(edge); used.update(edge)
            repaired = allocation.local_repair(initial, scores)
            self.assertGreaterEqual((len(repaired), sum(scores[e] for e in repaired)), (len(initial), sum(scores[e] for e in initial)))
            flat = [u for pair in repaired for u in pair]
            self.assertEqual(len(flat), len(set(flat)))
            self.assertTrue(all(e in scores for e in repaired))
            optimum = allocation.cardinality_matching(scores)
            self.assertEqual((len(optimum), sum(scores[e] for e in optimum)), exhaustive(scores))

    def test_n2_exact_tie_precedence_and_request_order_independence(self):
        r = request(); r['state']['members'] = [member(c, ['weekend_day']) for c in 'abcdef']
        for day in range(60):
            r['state']['day'] = day
            scores = allocation.scored_edges(r['state'])
            out = allocation.stable_reranking(scores, day)
            for i, chosen in enumerate(out):
                used = {u for e in out[:i] for u in e}
                feasible = [e for e in scores if not used.intersection(e)]
                self.assertEqual(scores[chosen], max(scores[e] for e in feasible))
            reverse = copy.deepcopy(r); reverse['state']['members'].reverse()
            self.assertEqual(policy.decide(r, {'id': 'N2'}), policy.decide(reverse, {'id': 'N2'}))

    def test_actual_timer_survives_broad_exception_handler(self):
        def expensive(*args):
            try:
                while True: time.sleep(.05)
            except Exception:
                return {'pairs': [], 'memory': {}}
        began = time.monotonic()
        with patch.object(allocation, 'action', side_effect=expensive), contextlib.redirect_stderr(io.StringIO()) as err:
            out = policy.decide(request(), {'id': 'N1'})
        elapsed = time.monotonic()-began
        self.assertEqual(out, {'pairs': baseline_match(request()['state']), 'memory': {}})
        self.assertIn('Deadline', err.getvalue())
        self.assertGreaterEqual(elapsed, 6.5); self.assertLess(elapsed, 9)
        self.assertEqual(signal.getitimer(signal.ITIMER_REAL)[0], 0)

    def run_fake(self, root, fn):
        with patch.object(recorder, 'generate', return_value={'schema_version': '1.0.0'}), patch.object(recorder, 'Simulator', FakeSimulator), patch('research6.policies.policy.decide', side_effect=fn):
            return recorder.run_cell((str(root), {'policy':'G','seed':101,'family':'development'}, {'id':'G'}, {'research6/tests/test_independent_contract.py':recorder.sha(__file__)}))

    def test_nonfinite_return_keeps_error_streams_failure_commit_resume(self):
        def fn(r, c):
            import sys
            print('before nonfinite'); print('error bytes before nonfinite', file=sys.stderr)
            return {'asks': [], 'memory': float('nan')}
        with tempfile.TemporaryDirectory() as temp:
            row = self.run_fake(temp, fn)
            self.assertFalse(row['valid']); self.assertEqual(row['attempted_invocations'], 1)
            with gzip.open(Path(row['attempt_path'])/'public/001.inference_error.json.gz', 'rt') as f: event=json.load(f)
            self.assertIn('before nonfinite', event['stdout_utf8'])
            self.assertIn('error bytes before nonfinite', event['stderr_utf8'])
            committed = json.loads((Path(temp)/'commits/G_development_101.json').read_text())
            orchestrator.verify_commit(committed, row['source_hashes'], {'id':'G'})
            self.assertEqual(committed['attempt_id'], row['attempt_id'])
            with self.assertRaises(ValueError): orchestrator.verify_commit(committed, row['source_hashes'], {'id':'N1'})
            with self.assertRaises(ValueError): orchestrator.verify_commit(committed, {'research6/tests/test_independent_contract.py':'changed'})

    def test_setup_failure_commits_without_world_generation(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(recorder, 'generate', side_effect=RuntimeError('constructed setup failure')):
                row = recorder.run_cell((temp, {'policy':'G','seed':101,'family':'development'}, {'id':'G'}, {}))
            self.assertFalse(row['valid']); self.assertEqual(row['attempted_invocations'], 0)
            self.assertIsNone(row['world_sha256'])
            self.assertTrue((Path(temp)/'commits/G_development_101.json').exists())
            with gzip.open(Path(row['attempt_path'])/'privileged/final.json.gz', 'rt') as f:
                self.assertIsNone(json.load(f)['state'])
            orchestrator.verify_commit(row, {}, {'id':'G'})

    def test_invalid_invocation_retains_fallback_count(self):
        for failure in ('shape', 'nonfinite', 'exception'):
            with self.subTest(failure=failure):
                def fn(r, c):
                    policy.LAST_STATUS = {'fallback': True, 'reason': 'Deadline'}
                    if failure == 'exception': raise RuntimeError('after fallback')
                    if failure == 'nonfinite': return {'asks': [], 'memory': float('nan')}
                    return {'bad': True, 'memory': {}}
                with tempfile.TemporaryDirectory() as temp:
                    row=self.run_fake(temp, fn)
                    self.assertFalse(row['valid'])
                    self.assertEqual(row['fallback_count'], 1, 'failed invocations must retain fallback telemetry')
                    suffix='response' if failure == 'shape' else 'inference_error'
                    with gzip.open(Path(row['attempt_path'])/f'public/001.{suffix}.json.gz', 'rt') as f:
                        self.assertEqual(json.load(f)['policy_status'], {'fallback': True, 'reason':'Deadline'})

    def test_stderr_fallback_text_is_not_telemetry(self):
        def fn(r, c):
            import sys
            print('research6 fallback: diagnostic example', file=sys.stderr)
            return {'asks' if r['phase']=='ask' else 'pairs':[], 'memory':{}}
        with tempfile.TemporaryDirectory() as temp:
            row=self.run_fake(temp, fn)
            self.assertTrue(row['valid']); self.assertEqual(row['fallback_count'], 0)
            with gzip.open(Path(row['attempt_path'])/'public/001.response.json.gz', 'rt') as f:
                event=json.load(f)
            self.assertIn('fallback', event['stderr_utf8'])
            self.assertEqual(event['policy_status'], {'fallback':False, 'reason':None})

    def test_wrapper_and_recorder_clear_prior_fallback_status(self):
        with contextlib.redirect_stderr(io.StringIO()):
            policy.decide({'phase':'ask'})
        self.assertEqual(policy.LAST_STATUS, {'fallback':True, 'reason':'KeyError'})
        policy.decide(request(), {'id':'G'})
        self.assertEqual(policy.LAST_STATUS, {'fallback':False, 'reason':None})
        calls=0
        def fn(r, c):
            nonlocal calls
            calls += 1
            if calls == 1: policy.LAST_STATUS={'fallback':True, 'reason':'constructed'}
            else: self.assertEqual(policy.LAST_STATUS, {'fallback':False, 'reason':None})
            return {'asks' if r['phase']=='ask' else 'pairs':[], 'memory':{}}
        with tempfile.TemporaryDirectory() as temp:
            row=self.run_fake(temp, fn)
            self.assertTrue(row['valid']); self.assertEqual(row['fallback_count'], 1)
            self.assertEqual(calls,120)

    def test_registration_rejects_policy_config_identity_mismatch(self):
        design = {'cells':[{'policy':'N1','seed':101,'family':'development'}],
            'configs':{'N1':{'id':'G'}}, 'sources':{}, 'stage':'smoke',
            'resource_forecast':{'main_cpu_seconds':1,'fit_cpu_seconds':0},
            'reviews':[{'passed':True,'path':'review','sha256':'digest'}], 'seed_inventory_sha256':'digest'}
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'design.json'; path.write_text(json.dumps(design))
            with patch.object(orchestrator, 'sources', return_value={}), patch.object(orchestrator,'sha',return_value='digest'):
                with self.assertRaises(ValueError): orchestrator.load_design(path)


if __name__ == '__main__': unittest.main()
