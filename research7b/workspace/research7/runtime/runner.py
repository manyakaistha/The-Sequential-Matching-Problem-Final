"""Registered execution runner interface for Research 7."""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from .interfaces import (
    sanitize_observation,
    validate_ask_batch,
    validate_match_batch,
    validate_policy_memory,
    PublicProtocolError,
)
from .leases import CellLease, LeaseManager
from .metrics import compute_run_metrics
from .recorder import DurableRecorder, AttemptLogger


class RunnerBlockerError(Exception):
    """Raised when an empirical run is blocked by status, uncertified freshness, or unverified registration."""
    pass


class RegisteredRunner:
    """The Research 7 execution runner.

    Strictly refuses execution if registration is in planning_only status, freshness is uncertified,
    or execution is unauthorized.
    """

    def __init__(
        self,
        workspace_root: Path,
        registration_dict: Dict[str, Any],
        recorder: DurableRecorder,
        lease_manager: LeaseManager,
        host_id: str = "mac-01",
    ):
        self.workspace_root = Path(workspace_root)
        self.registration = registration_dict
        self.recorder = recorder
        self.lease_manager = lease_manager
        self.host_id = host_id
        self._cached_cells_by_key = {c.get('cell_key'): c for c in self.registration.get('cells', []) if isinstance(c, dict)}
        self._readiness_blockers = None

    def check_execution_blockers(self, cell_dict: Dict[str, Any]) -> List[str]:
        """Preflight check: verifies all prerequisites before allowing any simulation step."""
        if self._readiness_blockers is None:
            from research7.registry.validator import RegistrationValidator
            _, self._readiness_blockers = RegistrationValidator(self.workspace_root).validate_executable_readiness(self.registration)
        blockers = list(self._readiness_blockers)
        ck = cell_dict.get("cell_key")
        if ck not in self._cached_cells_by_key or self._cached_cells_by_key[ck] != cell_dict:
            blockers.append("Cell is not an exact member of the frozen grid.")

        # 1. Registration status check
        status = self.registration.get("status")
        if status != "frozen_execution_registration":
            blockers.append(
                f"Registration status is '{status}'. Must be 'frozen_execution_registration' to execute."
            )

        # 2. Seed freshness check
        if not self.registration.get("seed_freshness_certified"):
            blockers.append(
                "Seed freshness is uncertified. Coordinator must audit all archives before execution."
            )

        # 3. Execution authorization check
        if not self.registration.get("execution_authorized"):
            blockers.append(
                "Execution unauthorized: planning package is not research execution authority."
            )

        # 4. Source hash verification
        governing = self.registration.get("governing_simulator", {})
        kit_file = self.workspace_root / "kit.py"
        if kit_file.exists():
            actual_kit_sha = hashlib.sha256(kit_file.read_bytes()).hexdigest()
            if actual_kit_sha != governing.get("kit_sha256"):
                blockers.append(f"Simulator kit.py hash mismatch: expected {governing.get('kit_sha256')}, got {actual_kit_sha}")
        else:
            blockers.append("kit.py not found in workspace")

        # 5. Policy registration check
        policy_id = cell_dict.get("policy_id")
        registered_policies = self.registration.get("policies", {})
        if policy_id not in registered_policies:
            blockers.append(f"Policy '{policy_id}' is not in registered policies: {list(registered_policies.keys())}")

        return blockers

    def execute_cell_guarded(
        self,
        cell_dict: Dict[str, Any],
        policy_decide_fn: Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]],
        policy_config: Dict[str, Any],
        active_lease: CellLease,
    ) -> Dict[str, Any]:
        """Guarded execution of a single registered cell.

        Fails immediately with RunnerBlockerError if any blockers exist.
        """
        blockers = self.check_execution_blockers(cell_dict)
        if blockers:
            raise RunnerBlockerError(f"Runner blocked by unfulfilled prerequisites:\n" + "\n".join(f" - {b}" for b in blockers))

        # Verify lease active for this host and generation
        cell_key = cell_dict.get("cell_key", "")
        if not self.lease_manager.verify_lease_for_generation(cell_key, self.host_id, active_lease.generation):
            raise RunnerBlockerError(f"Worker {self.host_id} does not hold a valid active lease for cell {cell_key}")

        from .invocation import TrustedInvocation, raw_json
        import importlib
        spec = self.registration['policies'][cell_dict['policy_id']]
        if policy_config != spec.get('config'):
            raise RunnerBlockerError('Policy configuration differs from registration')
        module, name = spec['entrypoint'].split(':')
        frozen_decide = getattr(importlib.import_module(module), name)
        if policy_decide_fn is not frozen_decide:
            raise RunnerBlockerError('Policy function differs from frozen entrypoint')
        mode = spec.get('execution_mode', 'trusted_inprocess')
        if mode == 'trusted_inprocess' and (cell_dict['stage_id'] != 'P1_smoke' or cell_dict['policy_id'] not in {'G','N','R','P','K','Q6'}):
            raise RunnerBlockerError('Trusted in-process mode admitted only for reference smoke')
        if mode == 'trusted_inprocess':
            invocation = TrustedInvocation(frozen_decide, policy_config)
        elif mode == 'subprocess_json':
            from .invocation import SubprocessInvocation
            invocation = SubprocessInvocation(spec['command'], self.workspace_root)
        else:
            raise RunnerBlockerError('Unsupported execution mode; no container admission implemented')
        if self.recorder.get_commit(cell_key) is not None:
            raise RunnerBlockerError('Cell already has an authoritative commit')
        logger = self.recorder.create_attempt_logger(cell_key)
        logger.initialize({'cell': cell_dict, 'lease': active_lease.to_dict(), 'execution_mode': mode})
        row = run_episode(logger, cell_dict, invocation, resource_limits=self.registration["resource_forecast"])
        self.lease_manager._load()
        if not self.lease_manager.verify_lease_for_generation(cell_key, self.host_id, active_lease.generation):
            raise RunnerBlockerError('Lease expired or revoked before commit; finalized attempt retained')
        self.recorder.write_commit(cell_key, logger.attempt_id, cell_dict, row, row['valid'], row.get('error'))
        if not self.lease_manager.commit_lease(cell_key, self.host_id, active_lease.generation, logger.attempt_id, row):
            raise RunnerBlockerError('Lease commit refused; coordinator reconciliation required')
        return row


def run_episode(logger, cell, invocation, *, world_factory=None, simulator_class=None, resource_limits=None):
    """Official horizon; injected factories are exclusively for constructed tests."""
    from kit import generate, Simulator, VERSION
    import evaluate
    import traceback
    from .invocation import raw_json, LIMIT
    world_factory = world_factory or generate
    simulator_class = simulator_class or Simulator
    sim = None
    memory = None
    sequence = 0
    start, cpu = time.monotonic(), time.process_time()
    import resource
    children_start = resource.getrusage(resource.RUSAGE_CHILDREN)
    child_cpu_start = children_start.ru_utime + children_start.ru_stime
    inference_seconds = 0
    digest = hashlib.sha256()
    row = {}
    world_sha256 = None
    fallback_count = 0
    try:
        world = world_factory(cell['seed'], 200, 'evaluation', cell['family'])
        world_sha256 = hashlib.sha256(raw_json(world)).hexdigest()
        logger.record_world(world)
        sim = simulator_class(world)
        for day in range(60):
            for phase in ('ask', 'match'):
                if resource_limits:
                    import resource, sys, shutil
                    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == 'darwin' else 1024)
                    child_usage=resource.getrusage(resource.RUSAGE_CHILDREN)
                    total_cpu=time.process_time()-cpu+child_usage.ru_utime+child_usage.ru_stime-child_cpu_start
                    if total_cpu+10 > resource_limits.get('max_attempt_cpu_seconds',90):
                        raise PublicProtocolError('Attempt CPU reservation reached')
                    if rss > max(0,resource_limits['max_rss_gib']-1)*1024**3/2:
                        raise PublicProtocolError('Per-worker RSS guard reached')
                    size = sum(p.stat().st_size for p in logger.attempt_dir.rglob('*') if p.is_file())
                    if size > resource_limits.get('max_attempt_output_bytes',32*1024**2):
                        raise PublicProtocolError('Attempt storage guard reached')
                    if shutil.disk_usage(logger.attempt_dir).free < resource_limits['free_reserve_gib_min']*1024**3:
                        raise PublicProtocolError('Free reserve reached')
                sequence += 1
                request = {'schema_version': VERSION, 'phase': phase, 'state': sim.observe(), 'memory': memory}
                wire = raw_json(request)
                logger.persist_request(sequence, day, phase, wire)
                if len(wire) > LIMIT:
                    raise PublicProtocolError('Request exceeds 1 MiB')
                sanitize_observation(request)
                result = invocation(wire)
                # Raw bytes retained before decode or validation, including malformed UTF-8.
                logger.record_step(sequence, day, phase, wire, result.wire_response, memory, None, None,
                                   dict(result.policy_status, error=result.error),
                                   __import__('base64').b64encode(result.stdout).decode(),
                                   __import__('base64').b64encode(result.stderr).decode(),
                                   result.elapsed_seconds, result.cpu_seconds)
                fallback_count += int(result.policy_status.get("fallback") is True)
                inference_seconds += result.elapsed_seconds
                if result.error:
                    raise PublicProtocolError(result.error)
                if result.elapsed_seconds > 10 or len(result.wire_response) > LIMIT:
                    raise PublicProtocolError('Invocation resource limit')
                response = evaluate.validate_response(evaluate.strict_json(result.wire_response.decode('utf-8')), phase)
                state = request['state']
                available = {m['member_id'] for m in state['members'] if m['available']}
                action = response['asks' if phase == 'ask' else 'pairs']
                if phase == 'ask':
                    ok, errors, _ = validate_ask_batch(action, available, state['ask_budget_remaining'])
                else:
                    ok, errors = validate_match_batch(action, available, state['introductions'], state['members'])
                if not ok:
                    raise PublicProtocolError('; '.join(errors))
                memory = response['memory']
                digest.update(json.dumps([phase,day,action],sort_keys=True).encode())
                if phase == 'ask': sim.resolve_asks(action)
                else: sim.advance(action)
        arrived = sim.observe()['members']
        for _ in range(40): sim.advance([])
        if sim.day != 100 or sequence != 120: raise PublicProtocolError('Horizon mismatch')
        row = compute_run_metrics(sim.introductions, sim.ask_log, feedback=sim.receive_feedback(), arrived_members=arrived)
        row['valid'] = True
    except BaseException as exc:
        row = {'valid': False, 'error': type(exc).__name__ + ': ' + str(exc)}
        logger._write_atomic_json(logger.public_dir/'error.json', {'sequence':sequence,'error':row['error'],'traceback':traceback.format_exc()})
    import sys
    row.update(world_sha256=world_sha256, fallback_count=fallback_count, peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024),
               evidence_bytes_before_final=sum(p.stat().st_size for p in logger.attempt_dir.rglob('*') if p.is_file()),
               attempt_id=logger.attempt_id, invocation_count=len(logger.segments), attempted_invocations=sequence,
               action_sha256=digest.hexdigest(), inference_seconds=inference_seconds,
               wall_seconds=time.monotonic()-start, cpu_seconds=time.process_time()-cpu + resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime + resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime-child_cpu_start,
               final_day=sim.day if sim else None)
    final = {k:sorted(v) if isinstance(v,set) else v for k,v in vars(sim).items()} if sim else None
    logger.finalize(row, final, row['valid'], row.get('error'))
    return row
