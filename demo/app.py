"""FastAPI application for the sequential reciprocal-matching walkthrough."""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .engine import PRESETS, SUPPORTED_POLICIES, config_payload
from .schemas import (
    AdvanceRequest,
    ConfigResponse,
    EventsResponse,
    ResearchSummaryResponse,
    RunCreate,
    RunResponse,
)
from .sessions import RunNotFound, RunStoreError, STORE
from .settings import SETTINGS


ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = Path(__file__).resolve().parent / "static"
CPU_SLOT = asyncio.Semaphore(1)

app = FastAPI(
    title="Sequential reciprocal matching demo",
    description="A synthetic, executable illustration of the retained Greedy policy.",
    version=SETTINGS.build_version,
    docs_url=None,
    redoc_url=None,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def error_payload(code: str, message: str, *, details: Any | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        body["details"] = details
    return {"error": body}


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content=error_payload("invalid_input", "The request did not match the public API contract.", details=exc.errors()))


@app.exception_handler(RunStoreError)
async def run_store_error(_: Request, exc: RunStoreError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=error_payload(exc.code, str(exc)))


@app.exception_handler(ValueError)
async def value_error(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=422, content=error_payload("invalid_transition", str(exc)))


@app.exception_handler(Exception)
async def unexpected_error(_: Request, exc: Exception) -> JSONResponse:  # pragma: no cover - defensive production boundary
    # Do not return simulator internals or a traceback to a public visitor.
    return JSONResponse(status_code=500, content=error_payload("server_error", "The demo could not complete that bounded transition."))


@app.middleware("http")
async def request_size_limit(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > 100_000:
                return JSONResponse(status_code=413, content=error_payload("request_too_large", "Request bodies are limited to 100 KB."))
        except ValueError:
            return JSONResponse(status_code=400, content=error_payload("invalid_content_length", "Invalid Content-Length header."))
    return await call_next(request)


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/healthz", include_in_schema=False)
async def healthz() -> dict[str, Any]:
    return {"status": "ok", "service": "sequential-matching-demo", "version": SETTINGS.build_version}


@app.get("/api/v1/config", response_model=ConfigResponse)
async def config() -> dict[str, Any]:
    return config_payload()


def _run_response(run_id: str) -> dict[str, Any]:
    stored = STORE.get(run_id)
    result = stored.engine.view(run_id)
    result["expires_in_seconds"] = max(0, int(SETTINGS.run_ttl_seconds - (time.monotonic() - stored.engine.last_used_at)))
    return result


@app.post("/api/v1/runs", response_model=RunResponse, status_code=status.HTTP_201_CREATED)
async def create_run(body: RunCreate) -> dict[str, Any]:
    preset = PRESETS.get(body.preset_id)
    if preset is None:
        raise ValueError("Choose one of the documented public presets.")
    if body.policy not in SUPPORTED_POLICIES:
        raise ValueError("Choose one of the supplied policy controls.")
    stored = STORE.create(preset, body.policy)
    result = stored.engine.view(stored.run_id)
    result["expires_in_seconds"] = SETTINGS.run_ttl_seconds
    return result


@app.get("/api/v1/runs/{run_id}", response_model=RunResponse)
async def get_run(run_id: str) -> dict[str, Any]:
    stored = STORE.get(run_id)
    result = stored.engine.view(run_id)
    result["expires_in_seconds"] = max(0, int(SETTINGS.run_ttl_seconds - (time.monotonic() - stored.engine.last_used_at)))
    return result


@app.post("/api/v1/runs/{run_id}/advance", response_model=RunResponse)
async def advance_run(run_id: str, body: AdvanceRequest) -> dict[str, Any]:
    async with CPU_SLOT:
        return await asyncio.to_thread(STORE.advance, run_id, body.expected_revision, body.steps, body.idempotency_key)


@app.get("/api/v1/runs/{run_id}/events", response_model=EventsResponse)
async def events(
    run_id: str,
    after: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> dict[str, Any]:
    stored = STORE.get(run_id)
    rows, next_cursor, has_more = stored.engine.events_after(after, limit)
    return {"run_id": run_id, "events": rows, "next_cursor": next_cursor, "has_more": has_more}


@app.get("/api/v1/runs/{run_id}/export")
async def export_run(run_id: str) -> JSONResponse:
    stored = STORE.get(run_id)
    payload = stored.engine.export(run_id)
    encoded = json.dumps(payload, separators=(",", ":"), allow_nan=False).encode("utf-8")
    if len(encoded) > SETTINGS.max_export_bytes:
        return JSONResponse(status_code=413, content=error_payload("export_too_large", "This run's public export exceeded the bounded download size."))
    return JSONResponse(content=payload, headers={"Content-Disposition": f'attachment; filename="sequential-matching-{run_id}.json"'})


@app.get("/api/v1/runs/{run_id}/members/{member_id}/inspection")
async def inspect_member(run_id: str, member_id: str) -> dict[str, Any]:
    stored = STORE.get(run_id)
    result = stored.engine.inspect_member(member_id)
    if result is None:
        raise RunNotFound("That synthetic member is not visible in this run.")
    return result


@app.delete("/api/v1/runs/{run_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_run(run_id: str) -> None:
    STORE.delete(run_id)


@app.get("/api/v1/research-summary", response_model=ResearchSummaryResponse)
async def research_summary() -> dict[str, Any]:
    source = ROOT / "final_report" / "data" / "historical_baselines.json"
    try:
        data = json.loads(source.read_text())
    except (OSError, json.JSONDecodeError):
        data = {}
    return {
        "synthetic": True,
        "source": "final_report/data/historical_baselines.json",
        "note": "Historical aggregate context only; this single episode is not statistical evidence.",
        "controls": data,
    }
