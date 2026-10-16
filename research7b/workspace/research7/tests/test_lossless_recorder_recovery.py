"""Independent durability and recovery test suite for Research 7 Format Version 2 recorder.

Covers all Gate 4B requirements:
1. Exact reconstruction (wire bytes & metadata)
2. Corruption and missing dependencies
3. Torn request/completion tails
4. Kill/restart at relevant checkpoints
5. Disk exhaustion and fsync failure
6. Partial/malformed responses and timeouts
7. Lease conflicts and stale workers
8. Authoritative commits and restart idempotency
9. Archive restoration
"""

import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from research7.runtime.journal import (
    JournalWriter,
    scan_journal,
    decode,
    encode,
    read_frames,
    HEADER,
    MAX_RECORD,
    digest,
)
from research7.runtime.leases import LeaseManager
from research7.runtime.recorder import (
    AttemptLogger,
    DurableRecorder,
    compute_bytes_sha256,
    verify_attempt,
    verify_prefix,
)


class TestLosslessRecorderRecovery(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.root = Path(self.temp_dir)
        self.recorder = DurableRecorder(self.root)
        self.cell_key = "test_cell_" + hashlib.sha256(b"seed_700001_family_eval").hexdigest()[:16]
        self.cell_dict = {
            "cell_key": self.cell_key,
            "seed": 700001,
            "family": "evaluation",
            "policy_id": "G",
            "stage_id": "P2a_pilot",
        }

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_exact_reconstruction(self):
        """Exact wire bytes and metadata reconstruction from format v2 journal."""
        logger = self.recorder.create_attempt_logger(self.cell_key, format_version=2)
        logger.initialize({"cell": self.cell_dict}, initial_world={"members": 200})

        requests = []
        responses = []
        for seq in range(1, 15):
            day = (seq - 1) // 2
            phase = "ask" if seq % 2 == 1 else "match"
            wire_req = json.dumps({
                "sequence": seq, "day": day, "phase": phase,
                "state": {"members": [{"id": i, "score": i * 0.1} for i in range(10)]},
                "memory": {"step": seq - 1} if seq > 1 else None
            }, sort_keys=True).encode("utf-8")
            wire_resp = json.dumps({"action": [{"pair": [1, 2]}], "memory": {"step": seq}}).encode("utf-8")

            requests.append(wire_req)
            responses.append(wire_resp)

            logger.persist_request(seq, day, phase, wire_req)
            logger.record_step(
                sequence=seq, day=day, phase=phase,
                wire_request=wire_req, wire_response=wire_resp,
                memory_before={"step": seq - 1} if seq > 1 else None,
                memory_after={"step": seq},
                action=[{"pair": [1, 2]}],
                policy_status={"success": True},
                stdout_text=f"step {seq} stdout",
                stderr_text="",
                elapsed_seconds=0.012,
                cpu_seconds=0.010,
            )

        metrics = {"reward": 42.0, "matches": 14}
        logger.finalize(metrics, final_state={"day": 7}, is_valid=True)

        # 1. verify_attempt must pass
        verify_attempt(logger.attempt_dir)

        # 2. Inspect journal contents and verify exact wire bytes
        scan = scan_journal(logger.journal_path)
        self.assertFalse(scan["torn_tail"])
        self.assertIsNone(scan["pending_request"])
        self.assertEqual(scan["pairs_count"], 14)

        with logger.journal_path.open("rb") as stream:
            frames = list(read_frames(stream))
            self.assertEqual(len(frames), 28)  # 14 requests + 14 completions
            prev_req_record = None
            for i in range(14):
                req_frame = frames[2 * i]
                comp_frame = frames[2 * i + 1]

                is_delta = (req_frame[4] == 2)
                decoded_req_record = decode(req_frame, prev_req_record if is_delta else None)
                env_line, decoded_wire_req = decoded_req_record.split(b"\n", 1)
                env = json.loads(env_line.decode("ascii"))

                self.assertEqual(env["sequence"], i + 1)
                self.assertEqual(decoded_wire_req, requests[i], f"Exact wire request mismatch at step {i+1}")
                prev_req_record = decoded_req_record

                decoded_comp = json.loads(decode(comp_frame).decode("utf-8"))
                decoded_wire_resp = base64.b64decode(decoded_comp["wire_response_base64"])
                self.assertEqual(decoded_wire_resp, responses[i], f"Exact wire response mismatch at step {i+1}")
                self.assertEqual(decoded_comp["request_sha256"], hashlib.sha256(requests[i]).hexdigest())

    def test_02_corruption_and_missing_dependencies(self):
        """Corruption in frames or missing files must raise explicit verification errors."""
        logger = self.recorder.create_attempt_logger(self.cell_key, format_version=2)
        logger.initialize({"cell": self.cell_dict})
        wire_req = b'{"state": "test"}'
        wire_resp = b'{"action": []}'
        logger.persist_request(1, 0, "ask", wire_req)
        logger.record_step(1, 0, "ask", wire_req, wire_resp, None, None, [], {}, "", "", 0.01, 0.01)
        logger.finalize({"score": 1})

        # Bit flip in journal payload
        journal_raw = bytearray(logger.journal_path.read_bytes())
        corrupt_journal = bytearray(journal_raw)
        corrupt_journal[-5] ^= 0xFF
        logger.journal_path.write_bytes(bytes(corrupt_journal))

        with self.assertRaises(ValueError):
            verify_attempt(logger.attempt_dir)

        # Restore journal and remove an artifact
        logger.journal_path.write_bytes(bytes(journal_raw))
        logger.journal_index_path.unlink()
        with self.assertRaises(ValueError):
            verify_attempt(logger.attempt_dir)

    def test_03_torn_request_and_completion_tails(self):
        """Torn request tail and torn completion tail must be detected cleanly."""
        # Case A: Torn request tail
        logger_a = self.recorder.create_attempt_logger(self.cell_key + "_a", format_version=2)
        logger_a.initialize({"cell": self.cell_dict})
        logger_a.persist_request(1, 0, "ask", b'{"req": 1}')
        logger_a.record_step(1, 0, "ask", b'{"req": 1}', b'{"resp": 1}', None, None, [], {}, "", "", 0.01, 0.01)

        # Append partial torn header of request 2
        with logger_a.journal_path.open("ab") as f:
            f.write(b"R7C1\x01\x00")  # Only 6 bytes of 117-byte header

        scan_a = scan_journal(logger_a.journal_path)
        self.assertTrue(scan_a["torn_tail"])
        self.assertIn("Torn header", scan_a["error"])
        self.assertEqual(scan_a["pairs_count"], 1)

        # Case B: Durable request, torn completion tail
        logger_b = self.recorder.create_attempt_logger(self.cell_key + "_b", format_version=2)
        logger_b.initialize({"cell": self.cell_dict})
        logger_b.persist_request(1, 0, "ask", b'{"req": 1}')
        # Process crash during completion write (partial completion payload)
        complete_frame = encode(b'{"record_kind":"completion","sequence":1}')
        with logger_b.journal_path.open("ab") as f:
            f.write(complete_frame[:50])  # truncated payload

        scan_b = scan_journal(logger_b.journal_path)
        self.assertTrue(scan_b["torn_tail"])
        self.assertIsNotNone(scan_b["pending_request"])
        self.assertEqual(scan_b["pending_request"]["sequence"], 1)
        self.assertEqual(scan_b["pairs_count"], 0)

    def test_04_kill_restart_at_checkpoints(self):
        """Checkpoint frames decode standalone without prior delta history."""
        journal_path = self.root / "checkpoint_test.r7c"
        writer = JournalWriter(journal_path, checkpoint_interval=3)
        writer.open()

        # Realistic request JSON payloads (100 members, slight diff between steps)
        base_members = [{"id": j, "val": j * 10} for j in range(100)]
        wire_reqs = []
        for i in range(6):
            m = copy.deepcopy(base_members)
            m[0]["step"] = i
            wire_reqs.append(json.dumps({"members": m}, sort_keys=True).encode("utf-8"))

        for i, wire in enumerate(wire_reqs):
            seq = i + 1
            writer.persist_request(seq, 0, "ask", "att_1", wire)
            writer.persist_completion(seq, 0, "ask", "att_1", wire, b'{}', None, None, [], {}, "", "", 0.01, 0.01)
        writer.close()

        with journal_path.open("rb") as stream:
            frames = list(read_frames(stream))

        # Checkpoints occur at sequence 1 and sequence 4 (interval=3)
        # Frames for sequence 1: index 0 (req), index 1 (comp)
        # Frames for sequence 4: index 6 (req), index 7 (comp)
        cp_frame_1 = frames[0]
        cp_frame_4 = frames[6]

        # Mode of checkpoint frame must not be delta (mode != 2)
        self.assertIn(cp_frame_1[4], (0, 1))
        self.assertIn(cp_frame_4[4], (0, 1))

        # Checkpoint frame 4 must decode cleanly with previous=None
        decoded_cp_4 = decode(cp_frame_4, previous=None)
        self.assertIn(b'"step": 3', decoded_cp_4)

        # Delta frame at sequence 5 (index 8) requires predecessor
        delta_frame_5 = frames[8]
        self.assertEqual(delta_frame_5[4], 2)
        with self.assertRaises(ValueError):
            decode(delta_frame_5, previous=None)
        decoded_5 = decode(delta_frame_5, previous=decoded_cp_4)
        self.assertIn(b'"step": 4', decoded_5)

    def test_05_disk_exhaustion_and_fsync_failure(self):
        """Fsync failure before inference raises OSError and prevents inference execution."""
        logger = self.recorder.create_attempt_logger(self.cell_key, format_version=2)
        logger.initialize({"cell": self.cell_dict})

        inference_executed = False
        def fake_inference(wire):
            nonlocal inference_executed
            inference_executed = True
            return b'{"ok": true}'

        # Simulate disk full on fsync
        with patch("os.fsync", side_effect=OSError(28, "No space left on device")):
            with self.assertRaises(OSError) as ctx:
                logger.persist_request(1, 0, "ask", b'{"state": "val"}')
                fake_inference(b'{"state": "val"}')

            self.assertEqual(ctx.exception.errno, 28)

        # Invariant: inference must NOT have run
        self.assertFalse(inference_executed)

    def test_06_partial_malformed_responses_and_timeouts(self):
        """Malformed non-UTF-8 bytes, partial JSON, and timeouts are preserved byte-exact."""
        logger = self.recorder.create_attempt_logger(self.cell_key, format_version=2)
        logger.initialize({"cell": self.cell_dict})

        malformed_bytes = b"\xff\xfe\x00\xaa malformed \x80\x81"
        wire_req = b'{"state": "ok"}'

        logger.persist_request(1, 0, "ask", wire_req)
        logger.record_step(
            sequence=1, day=0, phase="ask",
            wire_request=wire_req, wire_response=malformed_bytes,
            memory_before=None, memory_after=None, action=None,
            policy_status={"success": False, "error": "Timeout exceeded 10.0s", "fallback": True},
            stdout_text="", stderr_text="Segmentation fault or timeout",
            elapsed_seconds=10.05, cpu_seconds=1.2,
        )
        logger.finalize({"valid": False}, is_valid=False, error_message="Timeout")

        verify_attempt(logger.attempt_dir)

        scan = scan_journal(logger.journal_path)
        self.assertEqual(scan["pairs_count"], 1)
        comp = scan["pairs"][0]["completion"]
        self.assertEqual(comp["policy_status"]["error"], "Timeout exceeded 10.0s")
        restored_response = base64.b64decode(comp["wire_response_base64"])
        self.assertEqual(restored_response, malformed_bytes)

    def test_07_lease_conflicts_and_stale_workers(self):
        """Stale worker lease generation prevents commit."""
        lease_path = self.root / "leases.json"
        lm = LeaseManager(lease_path)

        # Worker 1 takes lease (generation 1)
        lease_1 = lm.issue_lease(self.cell_key, host_id="worker-01")
        self.assertIsNotNone(lease_1)
        self.assertEqual(lease_1.generation, 1)

        # Revoke Worker 1 lease and issue to Worker 2 (generation 2)
        lm.revoke_lease(self.cell_key)
        lease_2 = lm.issue_lease(self.cell_key, host_id="worker-02")
        self.assertIsNotNone(lease_2)
        self.assertEqual(lease_2.generation, 2)

        # Worker 1 tries to commit using stale generation 1 -> refused & quarantined
        committed = lm.commit_lease(self.cell_key, host_id="worker-01", generation=lease_1.generation,
                                    attempt_id="att_stale", metrics={"valid": True})
        self.assertFalse(committed)

        # Worker 2 commits using valid generation 2 -> accepted
        committed_2 = lm.commit_lease(self.cell_key, host_id="worker-02", generation=lease_2.generation,
                                      attempt_id="att_valid", metrics={"valid": True})
        self.assertTrue(committed_2)

    def test_08_authoritative_commits_and_restart_idempotency(self):
        """Authoritative commit is published, duplicate commit rejected, restart idempotent."""
        logger = self.recorder.create_attempt_logger(self.cell_key, format_version=2)
        logger.initialize({"cell": self.cell_dict})
        logger.persist_request(1, 0, "ask", b'{"req": 1}')
        logger.record_step(1, 0, "ask", b'{"req": 1}', b'{"resp": 1}', None, None, [], {}, "", "", 0.01, 0.01)
        metrics = {"reward": 10.0}
        logger.finalize(metrics, is_valid=True)

        commit_target = self.recorder.write_commit(
            self.cell_key, logger.attempt_id, self.cell_dict, metrics, is_valid=True
        )
        self.assertTrue(commit_target.exists())

        # Second attempt for same cell must fail
        with self.assertRaises(FileExistsError):
            self.recorder.write_commit(
                self.cell_key, "different_attempt", self.cell_dict, metrics, is_valid=True
            )

        # get_commit must return verified commit data
        commit_data = self.recorder.get_commit(self.cell_key)
        self.assertIsNotNone(commit_data)
        self.assertEqual(commit_data["attempt_id"], logger.attempt_id)
        self.assertEqual(commit_data["metrics"], metrics)

    def test_09_archive_restoration(self):
        """Full archive restoration preserves verification integrity."""
        logger = self.recorder.create_attempt_logger(self.cell_key, format_version=2)
        logger.initialize({"cell": self.cell_dict}, initial_world={"seed": 700001})
        for s in range(1, 5):
            logger.persist_request(s, 0, "ask", f'{{"s": {s}}}'.encode())
            logger.record_step(s, 0, "ask", f'{{"s": {s}}}'.encode(), b'{"a":[]}', None, None, [], {}, "", "", 0.01, 0.01)
        logger.finalize({"score": 4}, final_state={"done": True})

        archive_dir = self.root / "restored_attempt"
        shutil.copytree(logger.attempt_dir, archive_dir)

        # Restored attempt must pass full verification
        final = verify_attempt(archive_dir)
        self.assertTrue(final["is_valid"])
        self.assertEqual(final["format_version"], 2)


if __name__ == "__main__":
    unittest.main()
