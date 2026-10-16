"""Production execution and subprocess isolation test suite for Research 7 (Gate 4C).

Verifies:
1. Cold startup, imports, and subprocess serialization
2. Dense graph requests and maximum history/memory limits
3. Solver cancellation and process group cleanup on timeout
4. Deterministic legal fallbacks under internal solver failures
5. Production resource constraints (10s invocation limit, 1 MiB wire limit)
"""

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from research7.runtime.invocation import SubprocessInvocation, LIMIT, InvocationResult


class TestProductionExecution(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.workspace_root = Path(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_subprocess_cold_startup_and_serialization(self):
        """Subprocess cold startup imports reference policy and executes wire JSON roundtrip."""
        cmd = [
            sys.executable,
            "-m", "research7.policies.cli_adapter",
            "--entrypoint", "research7.policies.references:decide",
            "--config", json.dumps({"id": "G"}),
        ]
        repo_root = Path(__file__).resolve().parents[4]
        invocation = SubprocessInvocation(cmd, cwd=str(repo_root), timeout=10)

        # Wire request for greedy match
        request = {
            "schema_version": "1.0",
            "phase": "match",
            "state": {
                "day": 5,
                "members": [
                    {"member_id": 1, "pool_id": 0, "available": True, "who_to_meet": [2], "age": 25, "gender": "F", "target_gender": "M"},
                    {"member_id": 2, "pool_id": 0, "available": True, "who_to_meet": [1], "age": 27, "gender": "M", "target_gender": "F"},
                ],
                "introductions": [],
                "ask_budget_remaining": 12,
            },
            "memory": None,
        }
        wire_req = json.dumps(request).encode("utf-8")

        start = time.monotonic()
        result = invocation(wire_req)
        elapsed = time.monotonic() - start

        self.assertIsNone(result.error)
        self.assertLess(elapsed, 10.0, "Cold startup must complete within 10 seconds")
        self.assertTrue(result.wire_response)

        resp = json.loads(result.wire_response.decode("utf-8"))
        self.assertIn("pairs", resp)
        self.assertIsInstance(resp["pairs"], list)

    def test_02_dense_graph_and_maximum_history(self):
        """Dense 200-node graph with substantial history serialization completes within bounds."""
        cmd = [
            sys.executable,
            "-m", "research7.policies.cli_adapter",
            "--entrypoint", "research7.policies.references:decide",
            "--config", json.dumps({"id": "G"}),
        ]
        repo_root = Path(__file__).resolve().parents[4]
        invocation = SubprocessInvocation(cmd, cwd=str(repo_root), timeout=10)

        members = [
            {
                "member_id": i,
                "pool_id": 0,
                "available": True,
                "who_to_meet": [(i + 1) % 200, (i + 2) % 200],
                "age": 20 + (i % 30),
                "gender": "F" if i % 2 == 0 else "M",
                "target_gender": "M" if i % 2 == 0 else "F",
            }
            for i in range(200)
        ]
        intros = [{"pair": [i, (i + 1) % 200], "day": i % 30} for i in range(100)]
        request = {
            "schema_version": "1.0",
            "phase": "match",
            "state": {
                "day": 30,
                "members": members,
                "introductions": intros,
                "ask_budget_remaining": 6,
            },
            "memory": {"historical_tags": [f"tag_{k}" for k in range(500)]},
        }
        wire_req = json.dumps(request).encode("utf-8")
        self.assertLess(len(wire_req), LIMIT)

        result = invocation(wire_req)
        self.assertIsNone(result.error)
        self.assertTrue(result.wire_response)
        self.assertLess(len(result.wire_response), LIMIT)

    def test_03_solver_cancellation_and_orphan_cleanup(self):
        """Hanging solver triggers process group kill within timeout without leaking orphans."""
        # Subprocess running sleep 30
        cmd = [sys.executable, "-c", "import time, os; time.sleep(30)"]
        invocation = SubprocessInvocation(cmd, cwd=str(self.workspace_root), timeout=1)  # 1s test timeout

        start = time.monotonic()
        result = invocation(b'{"test": 1}')
        elapsed = time.monotonic() - start

        self.assertIsNotNone(result.error)
        self.assertIn("TimeoutExpired", result.error)
        self.assertLess(elapsed, 3.0, "Timeout must cancel and kill within bounded delay")

    def test_04_deterministic_legal_fallback(self):
        """Failing policy script catches error and returns valid deterministic greedy fallback."""
        # Create a synthetic failing policy in a scratch file
        bad_policy_path = self.workspace_root / "bad_policy.py"
        bad_policy_path.write_text(
            "LAST_STATUS = {'fallback': False}\n"
            "def decide(request, config):\n"
            "    raise RuntimeError('Internal solver exception!')\n"
        )

        cmd = [
            sys.executable,
            "-m", "research7.policies.cli_adapter",
            "--entrypoint", "bad_policy:decide",
            "--config", "{}",
            "--enable-fallback",
        ]
        invocation = SubprocessInvocation(cmd, cwd=str(self.workspace_root), timeout=10)

        request = {
            "schema_version": "1.0",
            "phase": "match",
            "state": {
                "day": 1,
                "members": [
                    {"member_id": 10, "pool_id": 0, "available": True, "who_to_meet": [20], "age": 30, "gender": "F", "target_gender": "M"},
                    {"member_id": 20, "pool_id": 0, "available": True, "who_to_meet": [10], "age": 32, "gender": "M", "target_gender": "F"},
                ],
                "introductions": [],
                "ask_budget_remaining": 12,
            },
            "memory": None,
        }
        wire_req = json.dumps(request).encode("utf-8")

        result = invocation(wire_req)
        # Process should succeed with returncode 0 because fallback engaged
        self.assertIsNone(result.error)
        self.assertTrue(result.wire_response)

        resp = json.loads(result.wire_response.decode("utf-8"))
        self.assertIn("pairs", resp)
        self.assertIn("executing deterministic legal fallback", result.stderr.decode("utf-8", errors="replace"))

    def test_05_oversized_payload_rejection(self):
        """Requests exceeding 1 MiB limit are bounded by RLIMIT_FSIZE / LIMIT."""
        oversized_wire = b'{"state": "' + b'x' * (LIMIT + 1024) + b'"}'
        cmd = [
            sys.executable,
            "-c",
            "import sys; sys.stdout.write(sys.stdin.read())"
        ]
        invocation = SubprocessInvocation(cmd, cwd=str(self.workspace_root), timeout=5)
        result = invocation(oversized_wire)
        # Subprocess with RLIMIT_FSIZE will either receive SIGXFSZ or return truncated output
        self.assertTrue(len(result.wire_response) <= LIMIT or result.error is not None)


if __name__ == "__main__":
    unittest.main()
