"""Bounded, process-local run storage with revision and concurrency guards."""

from __future__ import annotations

import secrets
import threading
import time
from dataclasses import dataclass
from typing import Any

from .engine import DemoEngine
from .settings import SETTINGS


class RunStoreError(Exception):
    status_code = 500
    code = "run_store_error"


class CapacityError(RunStoreError):
    status_code = 429
    code = "capacity"


class RunNotFound(RunStoreError):
    status_code = 404
    code = "unknown_run"


class RunExpired(RunStoreError):
    status_code = 410
    code = "expired_run"


class RevisionConflict(RunStoreError):
    status_code = 409
    code = "revision_conflict"


@dataclass(slots=True)
class StoredRun:
    run_id: str
    engine: DemoEngine


class RunStore:
    def __init__(self) -> None:
        self._runs: dict[str, StoredRun] = {}
        self._expired: set[str] = set()
        self._lock = threading.RLock()

    def _cleanup_locked(self) -> None:
        now = time.monotonic()
        expired: list[str] = []
        for run_id, stored in self._runs.items():
            age = now - stored.engine.created_at
            idle = now - stored.engine.last_used_at
            if age > SETTINGS.max_lifetime_seconds or idle > SETTINGS.run_ttl_seconds:
                expired.append(run_id)
        for run_id in expired:
            self._runs.pop(run_id, None)
            self._expired.add(run_id)
        if len(self._expired) > 256:
            self._expired = set(list(self._expired)[-128:])

    def create(self, preset: dict[str, Any], policy: str) -> StoredRun:
        with self._lock:
            self._cleanup_locked()
            if len(self._runs) >= SETTINGS.max_runs:
                raise CapacityError("The demo is at capacity; try again shortly.")
            run_id = secrets.token_urlsafe(18)
            while run_id in self._runs:
                run_id = secrets.token_urlsafe(18)
            stored = StoredRun(run_id, DemoEngine(preset, policy))
            self._runs[run_id] = stored
            return stored

    def get(self, run_id: str) -> StoredRun:
        with self._lock:
            self._cleanup_locked()
            if run_id in self._expired:
                raise RunExpired("This demonstration run has expired. Start a fresh run to continue.")
            stored = self._runs.get(run_id)
            if stored is None:
                raise RunNotFound("No active run exists for that identifier.")
            stored.engine.touch()
            return stored

    def delete(self, run_id: str) -> None:
        with self._lock:
            self._cleanup_locked()
            if run_id in self._expired:
                raise RunExpired("This demonstration run has expired.")
            if run_id not in self._runs:
                raise RunNotFound("No active run exists for that identifier.")
            self._runs.pop(run_id, None)

    def advance(self, run_id: str, expected_revision: int, steps: int, idempotency_key: str | None) -> dict[str, Any]:
        with self._lock:
            stored = self.get(run_id)
            engine = stored.engine
            if expected_revision != engine.revision:
                if idempotency_key and idempotency_key in engine.retained_advance_results:
                    return engine.retained_advance_results[idempotency_key]
                raise RevisionConflict(
                    f"Expected revision {expected_revision}, but the run is at revision {engine.revision}. Refresh the snapshot."
                )
            result = engine.advance_steps(steps)
            result["run_id"] = run_id
            result["expires_in_seconds"] = max(0, int(SETTINGS.run_ttl_seconds - (time.monotonic() - engine.last_used_at)))
            if idempotency_key:
                engine.retained_advance_results[idempotency_key] = result
                if len(engine.retained_advance_results) > 32:
                    oldest = next(iter(engine.retained_advance_results))
                    engine.retained_advance_results.pop(oldest, None)
            return result

    def active_count(self) -> int:
        with self._lock:
            self._cleanup_locked()
            return len(self._runs)


STORE = RunStore()
