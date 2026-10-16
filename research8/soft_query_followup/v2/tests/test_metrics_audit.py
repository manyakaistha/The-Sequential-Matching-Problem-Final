"""Constructed artifacts only: these tests never generate or run a world."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from research8.soft_query_followup.v2.metrics import compute_run_metrics
from research8.soft_query_followup.v2.audit import audit_run, reconstruct_public
from research8.w2.public_rules import VERSION


class AuditTests(unittest.TestCase):
    def _closure(self, directory):
        output = Path(directory)
        (output / 'commits').mkdir()
        attempt = output / 'attempts' / 'cell' / 'fixture'
        attempt.mkdir(parents=True)
        cell = dict(cell_key='cell', seed=1, family='development', policy_id='G', stage_id='fixture')
        registration = output / 'registration.json'
        reg = dict(cells=[cell], source_manifest={'fixture.py': 'a'*64})
        reg['registration_sha256'] = hashlib.sha256(json.dumps(reg, sort_keys=True, indent=2).encode()).hexdigest()
        registration.write_text(json.dumps(reg))
        public = dict(members=[], introductions=[], feedback=[], ask_log=[],
                      observed_day_cutoff=99, final_day=100)
        (attempt / 'final_public.json').write_text(json.dumps(public))
        actions = []
        action_digest = hashlib.sha256()
        for sequence in range(1, 121):
            day, phase = (sequence-1)//2, ('ask', 'match')[(sequence-1)%2]
            state = dict(schema_version=VERSION, synthetic=True, day=day,
                         ask_budget_remaining=12, members=[], introductions=[], feedback=[], ask_log=[])
            request = dict(schema_version=VERSION, phase=phase, state=state, memory=None)
            response = dict(memory=None, **{('asks' if phase == 'ask' else 'pairs'): []})
            actions.append(dict(sequence=sequence, day=day, phase=phase,
                                request=request, response=response, elapsed_seconds=0.01))
            action_digest.update(json.dumps([phase, day, []], sort_keys=True).encode())
        (attempt / 'actions.jsonl').write_text(''.join(json.dumps(a)+'\n' for a in actions))
        def stream(name, rows):
            (attempt / name).write_text(''.join(json.dumps(a)+'\n' for a in rows))
        stream('requests.jsonl', [{k: a[k] for k in ('sequence', 'day', 'phase', 'request')} for a in actions])
        stream('responses.jsonl', [{k: a[k] for k in ('sequence', 'day', 'phase', 'response')} for a in actions])
        stream('invocations.jsonl', [dict(sequence=a['sequence'], day=a['day'], phase=a['phase'],
                                           telemetry=dict(fallback=False, elapsed_seconds=0.01,
                                                          transport_elapsed_seconds=0.01)) for a in actions])
        stream('query_answers.jsonl', [dict(day=d, sequence=2*d+1, answers=[]) for d in range(60)])
        stream('daily_telemetry.jsonl', [dict(day=d, hard_asks_count=0, soft_asks_count=0,
                                               budget_remaining_after_hard=12, candidate_count=0,
                                               candidates=[], baseline_preanswer_pairs=[], actual_postanswer_pairs=[],
                                               match_changed=False, changed_pair_count=0) for d in range(60)])
        stream('released_feedback.jsonl', [])
        status = dict(status='completed', is_valid=True, error=None, sequence=120, attempt_id='fixture')
        (attempt / 'status.json').write_text(json.dumps(status))
        (attempt / 'arrived_by59.json').write_text('[]')
        stream('event_log.jsonl', [dict(event='attempt_started', attempt_id='fixture'),
                                    dict(status, event='attempt_finished')])
        metrics = compute_run_metrics([], [], feedback=[], arrived_members=[])
        row = dict(cell=cell, metrics=metrics, is_valid=True, error=None,
                   attempt_relative_path='attempts/cell/fixture',
                   registration_sha256=reg['registration_sha256'], attempt_id='fixture',
                   source_sha256={'fixture.py': 'a'*64}, world_sha256='b'*64,
                   action_sha256=action_digest.hexdigest(), artifact_hashes={},
                   invocation_count=120, fallback_count=0, invocation_seconds_total=sum([.01]*120),
                   invocation_seconds_max=.01)
        self._commit(output, attempt, row)
        return output, registration, attempt, row

    def _commit(self, output, attempt, row):
        row['artifact_hashes'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in attempt.iterdir() if p.is_file()}
        (output / 'commits' / 'cell.json').write_text(json.dumps(row))

    def test_complete_empty_constructed_capture(self):
        with tempfile.TemporaryDirectory() as tmp:
            output, reg, _, _ = self._closure(tmp)
            result = audit_run(output, reg)
            self.assertEqual(result['verified_cells'], 1)
            self.assertFalse(result['private_world_read'])

    def test_wrong_metric_rejected_after_valid_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            output, reg, attempt, row = self._closure(tmp)
            row['metrics']['arrived_members'] = 1
            self._commit(output, attempt, row)
            with self.assertRaisesRegex(ValueError, 'metric mismatch'):
                audit_run(output, reg)

    def test_missing_action_rejected_even_when_rehashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            output, reg, attempt, row = self._closure(tmp)
            path = attempt / 'actions.jsonl'
            path.write_text('\n'.join(path.read_text().splitlines()[:-1])+'\n')
            self._commit(output, attempt, row)
            with self.assertRaisesRegex(ValueError, '120 action'):
                audit_run(output, reg)

    def test_hidden_final_field_rejected(self):
        public = dict(members=[], introductions=[], feedback=[], ask_log=[],
                      observed_day_cutoff=99, final_day=100, truth={})
        with self.assertRaisesRegex(ValueError, 'schema'):
            reconstruct_public(public)

    def test_hash_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            output, reg, attempt, _ = self._closure(tmp)
            with (attempt / 'actions.jsonl').open('a') as stream:
                stream.write('{}\n')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                audit_run(output, reg)

    def test_traversal_and_symlink_rejected(self):
        for mode in ('traversal', 'symlink'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                output, reg, attempt, row = self._closure(tmp)
                if mode == 'traversal':
                    row['attempt_relative_path'] = '../elsewhere'
                else:
                    target = attempt / 'final_public.json'
                    backup = output / 'fixture.json'
                    target.rename(backup)
                    target.symlink_to(backup)
                self._commit(output, attempt, row)
                with self.assertRaisesRegex(ValueError, 'Unsafe|Symlink'):
                    audit_run(output, reg)

    def test_zero_denominator(self):
        metrics = compute_run_metrics([], [], feedback=[], arrived_members=[])
        self.assertEqual(metrics['coverage'], 0)
        self.assertEqual(metrics['msmi_per_100_arrived_members'], 0)

    def test_deleted_telemetry_cannot_be_rehashed_away(self):
        with tempfile.TemporaryDirectory() as tmp:
            output, reg, attempt, row = self._closure(tmp)
            (attempt / 'invocations.jsonl').unlink()
            self._commit(output, attempt, row)
            with self.assertRaisesRegex(ValueError, 'Required artifact hashes'):
                audit_run(output, reg)

    def test_source_manifest_must_match_registration(self):
        with tempfile.TemporaryDirectory() as tmp:
            output, reg, attempt, row = self._closure(tmp)
            row['source_sha256'] = {'fixture.py': 'c'*64}
            self._commit(output, attempt, row)
            with self.assertRaisesRegex(ValueError, 'source digest'):
                audit_run(output, reg)

    def test_duplicate_stream_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            output, reg, attempt, row = self._closure(tmp)
            path = attempt / 'actions.jsonl'
            lines = path.read_text().splitlines()
            lines[0] = lines[0].replace('"sequence": 1', '"sequence": 1, "sequence": 1')
            path.write_text('\n'.join(lines)+'\n')
            self._commit(output, attempt, row)
            with self.assertRaisesRegex(ValueError, 'Duplicate JSON key'):
                audit_run(output, reg)

    def test_memory_chain_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            output, reg, attempt, row = self._closure(tmp)
            for name, field in [('actions.jsonl', 'request'), ('requests.jsonl', 'request')]:
                path = attempt / name
                records = [json.loads(line) for line in path.read_text().splitlines()]
                records[1][field]['memory'] = {'injected': True}
                path.write_text(''.join(json.dumps(r)+'\n' for r in records))
            self._commit(output, attempt, row)
            with self.assertRaisesRegex(ValueError, 'memory continuity'):
                audit_run(output, reg)


if __name__ == '__main__':
    unittest.main()
