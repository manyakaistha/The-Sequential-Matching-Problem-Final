"""Execution runner for Research 8 soft query trial."""

import copy
import hashlib
import importlib
import json
import os
from pathlib import Path
import resource
import time
from typing import Any, Callable, Dict, List, Optional

from kit import Simulator, VERSION, generate
from research7b.workspace.research7.runtime.interfaces import (
    sanitize_observation,
    validate_ask_batch,
    validate_match_batch,
    validate_policy_memory,
    PublicProtocolError,
)
from .metrics import compute_run_metrics


def raw_json(val: Any) -> bytes:
    return json.dumps(val, allow_nan=False, sort_keys=True).encode("utf-8")


class Research8Runner:
    """Execution runner for Research 8 cells."""

    def __init__(self, workspace_root: Path, registration: Dict[str, Any], output_dir: Path):
        self.workspace_root = Path(workspace_root)
        self.registration = registration
        self.output_dir = Path(output_dir)
        self.commits_dir = self.output_dir / "commits"
        self.attempts_dir = self.output_dir / "attempts"
        self.commits_dir.mkdir(parents=True, exist_ok=True)
        self.attempts_dir.mkdir(parents=True, exist_ok=True)

    def execute_cell(self, cell: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single registered cell."""
        policy_id = cell["policy_id"]
        policy_spec = self.registration["policies"][policy_id]
        module_name, func_name = policy_spec["entrypoint"].split(":")
        mod = importlib.import_module(module_name)
        decide_fn = getattr(mod, func_name)
        policy_config = policy_spec.get("config", {})

        cell_key = cell["cell_key"]
        commit_file = self.commits_dir / f"{cell_key}.json"
        if commit_file.exists():
            return json.loads(commit_file.read_text())

        attempt_id = f"att_{int(time.time()*1000)}_{os.getpid()}"
        attempt_dir = self.attempts_dir / policy_id / f"{cell['seed']}_{cell['family']}" / attempt_id
        attempt_dir.mkdir(parents=True, exist_ok=True)

        start_time = time.monotonic()
        start_cpu = time.process_time()

        sim = None
        memory = None
        sequence = 0
        world_sha256 = None
        action_digest = hashlib.sha256()

        try:
            # Generate world
            world = generate(seed=cell["seed"], n=200, pool_id="evaluation", variant=cell["family"])
            world_sha256 = hashlib.sha256(raw_json(world)).hexdigest()
            (attempt_dir / "world.json").write_bytes(raw_json(world))

            sim = Simulator(world)

            for day in range(60):
                for phase in ("ask", "match"):
                    sequence += 1
                    request = {
                        "schema_version": VERSION,
                        "phase": phase,
                        "state": sim.observe(),
                        "memory": copy.deepcopy(memory),
                    }
                    sanitized_req = sanitize_observation(request)

                    # Invoke policy
                    t0 = time.monotonic()
                    response = decide_fn(sanitized_req, policy_config)
                    elapsed = time.monotonic() - t0

                    if elapsed > 10.0:
                        raise PublicProtocolError("Policy exceeded 10-second invocation limit")

                    state = sanitized_req["state"]
                    available_users = {m["member_id"] for m in state["members"] if m.get("available")}

                    if phase == "ask":
                        asks = response.get("asks", [])
                        ok, errs, cost = validate_ask_batch(asks, available_users, state["ask_budget_remaining"])
                        if not ok:
                            raise PublicProtocolError(f"Invalid ask batch: {'; '.join(errs)}")
                        sim.resolve_asks(asks)
                        action_digest.update(raw_json([phase, day, asks]))
                    else:
                        pairs = response.get("pairs", [])
                        ok, errs = validate_match_batch(pairs, available_users, state["introductions"], state["members"])
                        if not ok:
                            raise PublicProtocolError(f"Invalid match batch: {'; '.join(errs)}")
                        sim.advance(pairs)
                        action_digest.update(raw_json([phase, day, pairs]))

                    memory = response.get("memory")
                    ok_mem, mem_errs, _ = validate_policy_memory(memory)
                    if not ok_mem:
                        raise PublicProtocolError(f"Invalid policy memory: {'; '.join(mem_errs)}")

            # Follow-up days 60..99
            arrived_inventory = sim.observe()["members"]
            for _ in range(40):
                sim.advance([])

            if sim.day != 100 or sequence != 120:
                raise PublicProtocolError(f"Horizon mismatch: day={sim.day}, sequence={sequence}")

            metrics = compute_run_metrics(
                sim.introductions,
                sim.ask_log,
                feedback=sim.receive_feedback(),
                arrived_members=arrived_inventory,
                observed_day=100,
            )
            is_valid = True
            error_msg = None

        except Exception as exc:
            metrics = {"valid": False, "msmi_per_100_arrived_members": 0.0, "error": str(exc)}
            is_valid = False
            error_msg = f"{type(exc).__name__}: {str(exc)}"

        wall_seconds = time.monotonic() - start_time
        cpu_seconds = time.process_time() - start_cpu

        record = {
            "cell": cell,
            "metrics": metrics,
            "world_sha256": world_sha256,
            "action_sha256": action_digest.hexdigest(),
            "is_valid": is_valid,
            "error": error_msg,
            "wall_seconds": wall_seconds,
            "cpu_seconds": cpu_seconds,
            "attempt_id": attempt_id,
        }

        # Write atomic commit
        tmp_commit = commit_file.with_suffix(".tmp")
        tmp_commit.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        tmp_commit.replace(commit_file)

        return record
