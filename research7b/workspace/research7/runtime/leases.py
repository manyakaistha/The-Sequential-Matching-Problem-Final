"""Cell lease management and concurrency control for Research 7 coordinator and workers."""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import uuid


class LeaseError(Exception):
    pass


@dataclass
class CellLease:
    cell_key: str
    host_id: str
    generation: int
    issued_at_utc: str
    expires_at_utc: str
    status: str  # "active", "committed", "revoked", "expired"
    lease_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, allow_nan=False)


class LeaseManager:
    """Coordinator-owned lease manager tracking cell leases, generations, and late duplicate quarantine."""

    MAX_SIMULATION_PROCESSES_GLOBAL = 3

    def __init__(self, leases_path: Path):
        self.leases_path = Path(leases_path)
        self.active_leases: Dict[str, CellLease] = {}
        self.committed_cells: Set[str] = set()
        self.revoked_leases: Dict[str, List[int]] = {}  # cell_key -> list of revoked generations
        self.quarantined_duplicates: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if not self.leases_path.exists():
            return
        with self.leases_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                lease = CellLease(**d)
                if lease.status == "committed":
                    self.committed_cells.add(lease.cell_key)
                    if lease.cell_key in self.active_leases:
                        del self.active_leases[lease.cell_key]
                elif lease.status == "active":
                    self.active_leases[lease.cell_key] = lease
                elif lease.status == "revoked":
                    self.revoked_leases.setdefault(lease.cell_key, []).append(lease.generation)
                    if lease.cell_key in self.active_leases and self.active_leases[lease.cell_key].generation == lease.generation:
                        del self.active_leases[lease.cell_key]

    def issue_lease(
        self,
        cell_key: str,
        host_id: str,
        duration_seconds: int = 3600,
    ) -> CellLease:
        """Issues an authoritative cell lease to host_id with generation increment."""
        if not isinstance(duration_seconds, int) or isinstance(duration_seconds, bool) or duration_seconds <= 0:
            raise LeaseError("Lease duration must be a positive integer")
        if cell_key in self.committed_cells:
            raise LeaseError(f"Cell {cell_key} has already been authoritatively committed; cannot re-lease")

        current_lease = self.active_leases.get(cell_key)
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()

        if current_lease and current_lease.status == "active":
            # Check if expired
            exp_dt = datetime.fromisoformat(current_lease.expires_at_utc)
            if now_dt < exp_dt:
                raise LeaseError(
                    f"Cell {cell_key} is currently actively leased to {current_lease.host_id} (gen {current_lease.generation})"
                )
            new_generation = current_lease.generation + 1
        else:
            past_gens = self.revoked_leases.get(cell_key, [])
            new_generation = (max(past_gens) + 1) if past_gens else 1

        exp_iso = datetime.fromtimestamp(now_dt.timestamp() + duration_seconds, timezone.utc).isoformat()
        lease = CellLease(
            cell_key=cell_key,
            host_id=host_id,
            generation=new_generation,
            issued_at_utc=now_iso,
            expires_at_utc=exp_iso,
            status="active",
            lease_id=f"LSE-{uuid.uuid4().hex[:8]}",
        )

        self.active_leases[cell_key] = lease
        self._append(lease)
        return lease

    def revoke_lease(self, cell_key: str, reason: str = "infrastructure_reassignment") -> Optional[CellLease]:
        """Revokes an active lease so it can be safely reassigned."""
        if cell_key not in self.active_leases:
            return None
        lease = self.active_leases.pop(cell_key)
        lease.status = "revoked"
        self.revoked_leases.setdefault(cell_key, []).append(lease.generation)
        self._append(lease)
        return lease

    def verify_lease_for_generation(self, cell_key: str, host_id: str, generation: int) -> bool:
        """Verifies that the worker holds an active lease for generation before starting world generation."""
        if cell_key in self.committed_cells:
            return False
        lease = self.active_leases.get(cell_key)
        if not lease or lease.status != "active":
            return False
        if lease.host_id != host_id or lease.generation != generation:
            return False
        now_dt = datetime.now(timezone.utc)
        exp_dt = datetime.fromisoformat(lease.expires_at_utc)
        return now_dt < exp_dt

    def commit_lease(
        self,
        cell_key: str,
        host_id: str,
        generation: int,
        attempt_id: str,
        metrics: Dict[str, Any],
    ) -> bool:
        """Atomically validates lease generation and commits cell.

        Quarantines late duplicates from expired or revoked generations.
        """
        if cell_key in self.committed_cells:
            # Duplicate commit detected! Quarantine it
            self.quarantined_duplicates.append({
                "cell_key": cell_key,
                "host_id": host_id,
                "generation": generation,
                "attempt_id": attempt_id,
                "reason": "late_duplicate_already_committed",
                "quarantined_at": datetime.now(timezone.utc).isoformat(),
            })
            self._persist_quarantine()
            return False

        revoked = self.revoked_leases.get(cell_key, [])
        if generation in revoked:
            self.quarantined_duplicates.append({
                "cell_key": cell_key,
                "host_id": host_id,
                "generation": generation,
                "attempt_id": attempt_id,
                "reason": "commit_attempt_under_revoked_generation",
                "quarantined_at": datetime.now(timezone.utc).isoformat(),
            })
            self._persist_quarantine()
            return False

        lease = self.active_leases.get(cell_key)
        if not self.verify_lease_for_generation(cell_key, host_id, generation):
            self.quarantined_duplicates.append({
                "cell_key": cell_key,
                "host_id": host_id,
                "generation": generation,
                "attempt_id": attempt_id,
                "reason": "lease_mismatch_or_expired",
                "quarantined_at": datetime.now(timezone.utc).isoformat(),
            })
            self._persist_quarantine()
            return False

        lease.status = "committed"
        self.committed_cells.add(cell_key)
        del self.active_leases[cell_key]
        self._append(lease)
        return True

    def _persist_quarantine(self):
        from .recorder import write_json
        path = self.leases_path.parent / 'quarantine'
        path.mkdir(exist_ok=True)
        write_json(path / (uuid.uuid4().hex + '.json'), self.quarantined_duplicates[-1])

    def _append(self, lease: CellLease):
        self.leases_path.parent.mkdir(parents=True, exist_ok=True)
        line = (lease.to_json() + "\n").encode("utf-8")
        with self.leases_path.open("ab") as stream:
            stream.write(line)
            stream.flush()
            os.fsync(stream.fileno())
