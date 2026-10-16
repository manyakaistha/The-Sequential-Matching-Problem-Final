"""Unit tests for Research 7 durable lossless recorder and exact wire round-trip (T17, T20)."""

import json
from pathlib import Path
import tempfile
import unittest

from research7.runtime.recorder import DurableRecorder, AttemptLogger


class TestRecorder(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.recorder = DurableRecorder(self.root)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_attempt_logging_and_wire_roundtrip_t17(self):
        cell_hash = "abc123cellhash"
        logger = self.recorder.create_attempt_logger(cell_hash)
        logger.initialize(
            cell_metadata={"seed": 700001, "family": "cold_start", "policy": "G"},
            initial_world={"schema_version": 1, "privileged_truth": "hidden_abc"},
        )

        # Verify started.json exists
        self.assertTrue(logger.started_path.exists())
        started_data = json.loads(logger.started_path.read_text(encoding="utf-8"))
        self.assertEqual(started_data["cell_key_hash"], cell_hash)

        # Record a step
        request_obj = {"schema_version": 1, "phase": "ask", "state": {"day": 0, "available_users": [1, 2]}}
        response_obj = {"asks": [[1, "interests"]], "memory": {"step": 0}}
        wire_req = json.dumps(request_obj, sort_keys=True).encode("utf-8")
        wire_resp = json.dumps(response_obj, sort_keys=True).encode("utf-8")

        meta = logger.record_step(
            sequence=1,
            day=0,
            phase="ask",
            wire_request=wire_req,
            wire_response=wire_resp,
            memory_before=None,
            memory_after={"step": 0},
            action=[[1, "interests"]],
            policy_status={"fallback": False, "reason": None},
            stdout_text="",
            stderr_text="",
            elapsed_seconds=0.012,
            cpu_seconds=0.010,
        )

        self.assertEqual(meta.sequence, 1)
        self.assertEqual(meta.phase, "ask")

        # Verify segment index
        self.assertTrue(logger.segment_index_path.exists())
        index_lines = logger.segment_index_path.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(index_lines), 1)
        idx_entry = json.loads(index_lines[0])
        self.assertEqual(idx_entry["segment_id"], meta.segment_id)
        self.assertEqual(idx_entry["sha256"], meta.sha256)

        # Exact wire round-trip test (T17)
        segment_path = logger.segments_dir / f"{meta.segment_id}.bin"
        self.assertTrue(segment_path.exists())
        recovered = AttemptLogger.read_segment(segment_path)
        self.assertEqual(recovered["wire_request_utf8"], wire_req.decode("utf-8"))
        self.assertEqual(recovered["wire_response_utf8"], wire_resp.decode("utf-8"))
        self.assertEqual(recovered["action"], [[1, "interests"]])
        self.assertEqual(recovered["memory_after"], {"step": 0})
        self.assertEqual(recovered["policy_status"]["fallback"], False)

        # Finalize
        logger.finalize(metrics={"msmi_per_100": 2.5, "valid": True}, is_valid=True)
        self.assertTrue(logger.outcomes_path.exists())
        self.assertTrue(logger.finished_path.exists())

    def test_durable_commit_and_no_overwrite_t20(self):
        cell_hash = "cell_commit_hash_1"
        logger = self.recorder.create_attempt_logger(cell_hash)
        logger.initialize({'cell': {'policy': 'G', 'seed': 700001}})
        logger.finalize({'msmi_per_100': 1.5, 'valid': True})
        target = self.recorder.write_commit(
            cell_key_hash=cell_hash,
            attempt_id=logger.attempt_id,
            cell_dict={"policy": "G", "seed": 700001},
            metrics={"msmi_per_100": 1.5, "valid": True},
            is_valid=True,
        )
        self.assertTrue(target.exists())

        # Second attempt to commit same cell hash must raise FileExistsError
        with self.assertRaises(FileExistsError):
            self.recorder.write_commit(
                cell_key_hash=cell_hash,
                attempt_id="att_2",
                cell_dict={"policy": "G", "seed": 700001},
                metrics={"msmi_per_100": 1.5, "valid": True},
                is_valid=True,
            )


if __name__ == "__main__":
    unittest.main()
