"""Bounded transport fixtures; these tests do not generate simulator cells."""
import json
from pathlib import Path
import time

import pytest

from research8.soft_query_followup.v2.invoke import InvocationError, invoke_policy, strict_loads
from research8.soft_query_followup.v2.runner import raw_json


def fixture_source(tmp_path, body):
    package = tmp_path / 'research8' / 'soft_query_followup' / 'v2'
    package.mkdir(parents=True)
    for directory in (package, package.parent, package.parent.parent):
        (directory / '__init__.py').write_text('')
    (package / 'fixture.py').write_text(body)
    return tmp_path, 'research8.soft_query_followup.v2.fixture:decide'


def call(root, entrypoint, **kwargs):
    return invoke_policy(root, entrypoint, {}, {'phase': 'ask', 'state': {}, 'memory': None}, **kwargs)


def test_cold_process_memory_and_minimal_environment(tmp_path):
    root, entry = fixture_source(tmp_path, '''import os
calls = 0
def decide(request, config):
    global calls
    calls += 1
    assert "HOME" not in os.environ
    assert "seed" not in request
    return {"asks": [], "memory": {"calls": calls}}
''')
    assert call(root, entry)['response']['memory']['calls'] == 1
    assert call(root, entry)['response']['memory']['calls'] == 1


def test_hard_timeout(tmp_path):
    root, entry = fixture_source(tmp_path, 'import time\ndef decide(request, config):\n    time.sleep(5)\n')
    start = time.monotonic()
    with pytest.raises(InvocationError, match='wall timeout'):
        call(root, entry, timeout_seconds=.2)
    assert time.monotonic() - start < 2


def test_combined_output_is_bounded(tmp_path):
    root, entry = fixture_source(tmp_path, 'import sys\ndef decide(request, config):\n    sys.stderr.write("x" * 100000)\n    return {"asks": [], "memory": None}\n')
    with pytest.raises(InvocationError) as caught:
        call(root, entry, wire_limit_bytes=4096)
    assert len(caught.value.stdout.encode()) + len(caught.value.stderr.encode()) <= 4096


def test_policy_exception_has_no_fallback(tmp_path):
    root, entry = fixture_source(tmp_path, 'def decide(request, config):\n    raise ValueError("fixture failure")\n')
    with pytest.raises(InvocationError) as caught:
        call(root, entry)
    assert not caught.value.telemetry['fallback']
    assert 'fixture failure' in caught.value.stderr


def test_fallback_status_is_rejected(tmp_path):
    root, entry = fixture_source(tmp_path, 'LAST_STATUS={"fallback": True,"reason":"test"}\ndef decide(request, config):\n    return {"asks": [], "memory": None}\n')
    with pytest.raises(InvocationError, match='fallback'):
        call(root, entry)


@pytest.mark.parametrize('data', ['{"a": 1, "a": 2}', '{"x": NaN}', '{"x": Infinity}'])
def test_strict_json(data):
    with pytest.raises(ValueError):
        strict_loads(data)


def test_digest_is_frozen_standard_json():
    value = ['ask', 4, [{'member_id': 'syn_a', 'field': 'constraints'}]]
    assert raw_json(value) == json.dumps(value, sort_keys=True).encode()


def test_runner_horizon_public_closure_and_immutable_reuse(tmp_path, monkeypatch):
    from research8.soft_query_followup.v2 import runner, registration
    monkeypatch.setattr(registration, 'verify_registration', lambda *args: True)
    monkeypatch.setattr(runner, 'generate', lambda **kwargs: {'members': []})
    class FixtureSimulator:
        def __init__(self, world):
            self.day = 0
        def observe(self):
            feedback = []
            if self.day >= 99:
                feedback.append({'introduction_id': 'fixture', 'member_id': None,
                    'event': 'date_happened', 'value': False, 'occurred_day': 99, 'observed_day': 99})
            if self.day >= 100:
                feedback.append({'introduction_id': 'fixture', 'member_id': None,
                    'event': 'date_happened', 'value': False, 'occurred_day': 100, 'observed_day': 100})
            return {'schema_version': '1.0.0', 'synthetic': True, 'day': self.day,
                    'ask_budget_remaining': 12, 'members': [], 'introductions': [],
                    'feedback': feedback, 'ask_log': []}
        def resolve_asks(self, asks):
            assert self.day < 60
            return []
        def advance(self, pairs):
            assert self.day < 60 or pairs == []
            self.day += 1
    monkeypatch.setattr(runner, 'Simulator', FixtureSimulator)
    monkeypatch.setattr(runner, 'invoke_policy', lambda root, entry, config, request, **kwargs:
        {'response': {'asks' if request['phase'] == 'ask' else 'pairs': [], 'memory': None},
         'telemetry': {'fallback': False}})
    monkeypatch.setattr(runner, 'compute_run_metrics', lambda *args, **kwargs:
        {'valid': True, 'observed_day': kwargs['observed_day']})
    cell = {'cell_key': 'fixture_G', 'seed': 1, 'family': 'development', 'policy_id': 'G'}
    reg = {'cells': [cell], 'registration_sha256': 'fixture', 'source_manifest': {},
           'policies': {'G': {'entrypoint': 'unused:decide', 'config': {}}},
           'resource_forecast': dict(registration.CAPS, free_reserve_gib_min=.00001)}
    executor = runner.Research8Runner(tmp_path, reg, tmp_path/'output')
    record = executor.execute_cell(cell)
    assert record['is_valid']
    assert record['invocation_count'] == 120
    attempt = tmp_path/'output'/record['attempt_relative_path']
    public = json.loads((attempt/'final_public.json').read_text())
    assert public['final_day'] == 100 and public['observed_day_cutoff'] == 99
    assert [event['observed_day'] for event in public['feedback']] == [99]
    assert not (attempt/'world.json').exists()
    assert len((attempt/'actions.jsonl').read_text().splitlines()) == 120
    assert len((attempt/'query_answers.jsonl').read_text().splitlines()) == 60
    monkeypatch.setattr(runner, 'generate', lambda **kwargs: (_ for _ in ()).throw(AssertionError('retry')))
    assert executor.execute_cell(cell) == record
    (attempt/'status.json').write_text('{}')
    with pytest.raises(ValueError, match='artifact mismatch'):
        executor.execute_cell(cell)
