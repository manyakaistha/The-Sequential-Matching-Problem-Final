"""Append-only delegation ledger and global slot tracking for Research 7."""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import uuid


class DelegationError(Exception):
    pass


@dataclass
class DelegationRecord:
    task_id: str
    phase: str
    role_profile: str
    task_kind: str
    developer: str
    named_reviewer: str
    exclusive_ownership: List[str]
    input_paths: List[str]
    concrete_input_hashes: Dict[str, str]
    provider: str
    model: str
    effort: str
    cpu_seconds_allowance: int
    status: str
    created_at_utc: str
    closed_at_utc: Optional[str] = None
    outcome: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, allow_nan=False)


class DelegationManager:
    """Enforces global 4-slot ledger (root + max 3 children), developer/reviewer separation,

    and explicit model routing before recording to delegations.jsonl.
    """

    MAX_GLOBAL_SLOTS = 4
    MAX_CHILDREN = 3
    ALLOWED_EFFORTS = {"low", "medium", "high"}

    def __init__(self, ledger_path: Path, routing_profiles_path: Optional[Path] = None):
        self.ledger_path = Path(ledger_path)
        self.routing_profiles_path = (
            Path(routing_profiles_path)
            if routing_profiles_path
            else self.ledger_path.parent / "routing_profiles.json"
        )
        self.active_slots: Dict[str, DelegationRecord] = {}
        self._load_active()

    def _load_active(self):
        if not self.ledger_path.exists():
            return
        with self.ledger_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                rec = DelegationRecord(**d)
                if rec.status == "active":
                    self.active_slots[rec.task_id] = rec
                elif rec.task_id in self.active_slots and rec.status in {"completed", "failed", "revoked"}:
                    del self.active_slots[rec.task_id]

    def validate_delegation(
        self,
        task_id: str,
        developer: str,
        named_reviewer: str,
        effort: str,
        exclusive_ownership: List[str],
        concrete_input_hashes: Dict[str, str],
        input_paths: List[str],
    ) -> List[str]:
        errors = []

        # Global slot limit check: root occupies 1 slot, children at most 3
        if len(self.active_slots) >= self.MAX_CHILDREN:
            errors.append(
                f"Global slot limit reached: {len(self.active_slots)} children currently active (max {self.MAX_CHILDREN}, total {self.MAX_GLOBAL_SLOTS} including root)"
            )

        # Developer / reviewer separation
        if developer == named_reviewer:
            errors.append(
                f"Developer/reviewer separation violation: developer '{developer}' cannot be reviewer '{named_reviewer}'"
            )

        # Effort validation
        if effort not in self.ALLOWED_EFFORTS:
            errors.append(f"Invalid effort '{effort}'. Allowed efforts are: {sorted(list(self.ALLOWED_EFFORTS))}")

        # Input hashes validation
        for inp in input_paths:
            if inp not in concrete_input_hashes or not concrete_input_hashes[inp]:
                errors.append(f"Missing concrete input hash for '{inp}'")

        # Exclusive ownership conflicts with currently active tasks
        current_owned: Set[str] = set()
        for active_rec in self.active_slots.values():
            current_owned.update(active_rec.exclusive_ownership)
        conflicts = set(exclusive_ownership) & current_owned
        if conflicts:
            errors.append(f"Exclusive ownership collision with active tasks: {sorted(list(conflicts))}")

        return errors

    def register_delegation(
        self,
        task_id: str,
        phase: str,
        role_profile: str,
        task_kind: str,
        developer: str,
        named_reviewer: str,
        exclusive_ownership: List[str],
        input_paths: List[str],
        concrete_input_hashes: Dict[str, str],
        provider: str,
        model: str,
        effort: str,
        cpu_seconds_allowance: int,
    ) -> DelegationRecord:
        errors = self.validate_delegation(
            task_id=task_id,
            developer=developer,
            named_reviewer=named_reviewer,
            effort=effort,
            exclusive_ownership=exclusive_ownership,
            concrete_input_hashes=concrete_input_hashes,
            input_paths=input_paths,
        )
        if errors:
            raise DelegationError(f"Delegation rejected: {'; '.join(errors)}")

        rec = DelegationRecord(
            task_id=task_id,
            phase=phase,
            role_profile=role_profile,
            task_kind=task_kind,
            developer=developer,
            named_reviewer=named_reviewer,
            exclusive_ownership=exclusive_ownership,
            input_paths=input_paths,
            concrete_input_hashes=concrete_input_hashes,
            provider=provider,
            model=model,
            effort=effort,
            cpu_seconds_allowance=cpu_seconds_allowance,
            status="active",
            created_at_utc=datetime.now(timezone.utc).isoformat(),
        )

        self.active_slots[task_id] = rec
        self._append_record(rec)
        return rec

    def close_delegation(self, task_id: str, outcome: str, status: str = "completed"):
        if task_id not in self.active_slots:
            raise DelegationError(f"Task {task_id} is not currently active")
        rec = self.active_slots.pop(task_id)
        rec.status = status
        rec.outcome = outcome
        rec.closed_at_utc = datetime.now(timezone.utc).isoformat()
        self._append_record(rec)

    def _append_record(self, record: DelegationRecord):
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        line = (record.to_json() + "\n").encode("utf-8")
        with self.ledger_path.open("ab") as stream:
            stream.write(line)
            stream.flush()
            os.fsync(stream.fileno())
