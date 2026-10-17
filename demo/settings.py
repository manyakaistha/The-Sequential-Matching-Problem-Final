"""Runtime settings for the small, single-process public demo."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _int_env(name: str, default: int, *, minimum: int = 0, maximum: int | None = None) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = int(raw)
    except ValueError as exc:  # pragma: no cover - exercised through startup validation
        raise ValueError(f"{name} must be an integer") from exc
    if value < minimum or (maximum is not None and value > maximum):
        limit = f" and <= {maximum}" if maximum is not None else ""
        raise ValueError(f"{name} must be >= {minimum}{limit}")
    return value


@dataclass(frozen=True, slots=True)
class Settings:
    app_env: str = "development"
    max_runs: int = 8
    run_ttl_seconds: int = 1200
    max_lifetime_seconds: int = 3600
    max_events: int = 500
    max_export_bytes: int = 1_500_000
    build_version: str = "demo-1.0.0"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_env=os.getenv("APP_ENV", "development"),
            max_runs=_int_env("DEMO_MAX_RUNS", 8, minimum=1, maximum=32),
            run_ttl_seconds=_int_env("DEMO_RUN_TTL_SECONDS", 1200, minimum=60, maximum=86_400),
            max_lifetime_seconds=_int_env("DEMO_MAX_LIFETIME_SECONDS", 3600, minimum=300, maximum=172_800),
            max_events=_int_env("DEMO_MAX_EVENTS", 500, minimum=50, maximum=5_000),
            max_export_bytes=_int_env("DEMO_MAX_EXPORT_BYTES", 1_500_000, minimum=100_000, maximum=10_000_000),
            build_version=os.getenv("DEMO_BUILD_VERSION", "demo-1.0.0"),
        )


SETTINGS = Settings.from_env()
