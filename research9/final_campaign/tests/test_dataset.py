"""Constructed public records only; no simulator, fitting or campaign reads."""
import copy
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from research9.final_campaign import dataset as ds
from research9.final_campaign import features
from research8.soft_query_followup.v3 import storage
from research8.w2.public_rules import HARD, SOFT, VERSION


def member(ident):
    fields = HARD + SOFT
    return dict(member_id=ident, pool_id='p', synthetic=True, age=30, gender='x', zone='z', arrived_day=0, source='fixture', available=True, fields={f: None for f in fields}, field_status={f: 'not_asked' for f in fields}, field_observed_day={f: None for f in fields})


def intro(ident, a, b, day=0):
    return dict(introduction_id=ident, user_a=a, user_b=b, assigned_day=day, response_deadline_day=day+7, logging_policy='fixture', propensity=None)


def event(ident, actor, name, value, day):
    return dict(introduction_id=ident, member_id=actor, event=name, value=value, occurred_day=day, observed_day=day)


def public_fixture():
    intros = [intro('i0', 'a', 'b'), intro('i1', 'c', 'd'), intro('i2', 'e', 'f')]
    feedback = []
    for i, a, b in [('i0', 'a', 'b'), ('i1', 'c', 'd')]:
        feedback += [event(i, actor, 'introduction_response', 'yes', 1) for actor in (a,b)]
        feedback += [event(i, None, 'date_happened', True, 5)]
        feedback += [event(i, actor, 'second_meeting_intention', 'yes', 7 if i == 'i0' else 9) for actor in (a,b)]
    feedback += [event('i2', 'e', 'introduction_response', 'no', 1), event('i2', 'f', 'introduction_response', 'yes', 1)]
    return dict(members=[member(c) for c in 'abcdef'], introductions=intros, feedback=feedback, ask_log=[], observed_day_cutoff=99, final_day=100)


def action_bytes():
    actions = []
    for seq in range(1,121):
        day, phase = (seq-1)//2, ('ask','match')[(seq-1)%2]
        state = dict(schema_version=VERSION, synthetic=True, day=day, ask_budget_remaining=12, members=[member(c) for c in 'abcdef'], introductions=[], feedback=[], ask_log=[])
        # Only the captured first match request exposes this answer. Final public
        # values differ, so rebuilding from final questionnaire data would leak.
        if phase == 'match' and day == 0:
            state['members'][0]['fields']['relationship_goal'] = 'long_term'
            state['members'][0]['field_status']['relationship_goal'] = 'observed'
            state['members'][0]['field_observed_day']['relationship_goal'] = 0
        request = dict(schema_version=VERSION, phase=phase, state=state, memory=None)
        response = dict(memory=None, **({'pairs': [['a','b'], ['c','d'], ['e','f']] if day == 0 else []} if phase == 'match' else {'asks': []}))
        actions.append(dict(sequence=seq, phase=phase, day=day, request=request, response=response))
    return b''.join(json.dumps(a).encode()+b'\n' for a in actions)


class DatasetTests(unittest.TestCase):
    def test_labels_and_stage_risk_sets(self):
        labels, metrics = ds.public_labels(public_fixture())
        good, late, refused = [labels[(0, tuple(p))] for p in [('a','b'), ('c','d'), ('e','f')]]
        self.assertEqual(metrics['mutual_second_meeting_intention'], 1)
        self.assertEqual((good['y_terminal'], late['y_terminal'], refused['y_terminal']), (1,0,0))
        self.assertTrue(late['mask_second_given_timelydate'])
        self.assertFalse(refused['mask_date_given_first'])
        self.assertFalse(refused['mask_second_given_timelydate'])

    def test_final_horizon_and_future_events_fail(self):
        public = public_fixture()
        public['observed_day_cutoff'] = 98
        with self.assertRaisesRegex(ValueError, 'horizon'):
            ds.public_labels(public)
        public = public_fixture()
        public['feedback'][0]['observed_day'] = 100
        with self.assertRaises(ValueError):
            ds.public_labels(public)

    def test_exact_assignment_request_features(self):
        seen = []
        class Spy:
            feature_names = staticmethod(lambda: ['answer_known'])
            prepare_state = staticmethod(lambda s: None)
            @staticmethod
            def pair_features(state,a,b,context=None):
                seen.append((state['day'], a['member_id'], a['fields']['relationship_goal']))
                return np.asarray([a['fields']['relationship_goal'] == 'long_term'])
        rows, action_hash = ds._action_rows(io.BytesIO(action_bytes()), Spy)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]['X'].tolist(), [1])
        self.assertEqual(seen[0], (0,'a','long_term'))
        self.assertEqual(len(action_hash),64)
        self.assertEqual(len(rows[0]['request_sha256']),64)

    def test_real_feature_api_and_future_soft_mask(self):
        rows, _ = ds._action_rows(io.BytesIO(action_bytes()), features)
        self.assertEqual(rows[0]['X'].shape, (len(features.feature_names()),))
        state = json.loads(action_bytes().splitlines()[1])['request']['state']
        future = copy.deepcopy(state)
        future['members'][0]['field_observed_day']['relationship_goal'] = 10
        hidden = copy.deepcopy(future)
        hidden['members'][0]['fields']['relationship_goal'] = None
        np.testing.assert_array_equal(features.pair_features(future, *future['members'][:2]), features.pair_features(hidden, *hidden['members'][:2]))

    def test_action_extra_or_missing_lines_fail(self):
        for value in (action_bytes()+b'{}\n', b'\n'.join(action_bytes().splitlines()[:-1])+b'\n'):
            with self.assertRaises(ValueError):
                ds._action_rows(io.BytesIO(value), features)

    def test_stream_archive_checks_all_members_and_never_extracts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            attempt = root/'attempts/cell/a'
            attempt.mkdir(parents=True)
            (attempt/'actions.jsonl').write_bytes(action_bytes())
            (attempt/'final_public.json').write_text(json.dumps(public_fixture()))
            (attempt/'opaque.bin').write_bytes(b'not JSON: never interpreted')
            manifest = storage.archive_attempt(root, 'attempts/cell/a')
            with patch.object(tarfile.TarFile, 'extractall', side_effect=AssertionError('disk extraction forbidden')):
                rows, public, _ = ds._stream_cell(root, manifest, features)
            self.assertEqual(len(rows),3)
            self.assertEqual(public['final_day'],100)
            altered = copy.deepcopy(manifest)
            altered['files']['opaque.bin']['sha256'] = 'a'*64
            with self.assertRaisesRegex(ValueError,'Member hash'):
                ds._stream_cell(root, altered, features)

    def test_checkpoint_binds_commit_catalog_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root/'commits').mkdir()
            attempt = root/'attempts/cell/a'
            attempt.mkdir(parents=True)
            (attempt/'final_public.json').write_bytes(b'{}')
            manifest = storage.archive_attempt(root, 'attempts/cell/a')
            row = dict(is_valid=True, metrics=dict(valid=True), error=None,
                       cell=dict(cell_key='cell'), attempt_relative_path='attempts/cell/a',
                       artifact_hashes={k:v['sha256'] for k,v in manifest['files'].items()},
                       registration_sha256='a'*64)
            commit = root/'commits/cell.json'
            commit.write_text(json.dumps(row))
            proof_path = root/'proof.json'
            proof_path.write_bytes(b'proof fixture')
            proof = dict(sources={}, registration={}, implementation={})
            catalog = storage._path(root, 'archive_manifests/' + hashlib.sha256(b'attempts/cell/a').hexdigest() + '.json')
            binding = dict(commit=storage._hash_file(commit), sources={}, registration={},
                           cell_registration_sha256='a'*64, implementation={},
                           evidence=dict(kind='archive', catalog=storage._hash_file(catalog),
                                         archive=storage._hash_file(root/manifest['archive_relative_path'])))
            record = dict(cell_key='cell', binding=binding, result=dict(status='passed'))
            record['payload_sha256'] = ds.digest(record)
            (root/'checkpoints').mkdir()
            checkpoint = root/'checkpoints'/ (ds.digest(binding)+'.json')
            checkpoint.write_text(json.dumps(record))
            index = {'cell':storage._hash_file(checkpoint)['sha256']}
            with patch.object(ds, '_proof', return_value=(proof,index)):
                _, got, _ = ds._verified_manifest(root,commit,proof_path)
                self.assertEqual(got,manifest)
                row['registration_sha256'] = 'b'*64
                commit.write_text(json.dumps(row))
                with self.assertRaises((ValueError,FileNotFoundError)):
                    ds._verified_manifest(root,commit,proof_path)

    def test_archive_links_and_traversal_fail(self):
        for name, kind in [('../evil',tarfile.REGTYPE), ('safe',tarfile.SYMTYPE)]:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                (root/'archives').mkdir()
                archive = root/'archives/bad.tar'
                with tarfile.open(archive,'w') as tar:
                    info = tarfile.TarInfo(name)
                    info.type = kind
                    info.linkname = '/tmp/evil'
                    tar.addfile(info, io.BytesIO())
                manifest = dict(archive_relative_path='archives/bad.tar', codec='test', files={'safe':dict(bytes=0, sha256=hashlib.sha256(b'').hexdigest())})
                with patch.object(storage, '_compression', side_effect=lambda stream,codec: stream):
                    with self.assertRaises(ValueError):
                        ds._stream_cell(root, manifest, features)


if __name__ == '__main__':
    unittest.main()
