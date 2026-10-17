# Sequential matching demo

This directory contains the FastAPI + Uvicorn service used by the public
walkthrough. It wraps the repository's `kit.Simulator` and `policy.decide`
directly, so the simulator remains the source of truth for eligibility,
clarification costs, delayed feedback and qualified mutual second-meeting
intention (MSMI).

All members, preferences and outcomes are synthetic. The service is a bounded,
single-process demonstration: runs live in memory, expire after inactivity, and
are lost when the process restarts. It is not a durable production matching
service or evidence of real relationship prediction.

## Local setup

From the repository root, use Python 3.10 or later (3.13 is used by Render):

```bash
python -m venv .venv-demo
. .venv-demo/bin/activate
python -m pip install -r demo/requirements-dev.txt
python -m uvicorn demo.app:app --host 0.0.0.0 --port 8787 --workers 1
```

Open <http://127.0.0.1:8787/>. The production command uses Render's `PORT`
environment variable; do not run more than one worker because the run store is
process-local.

## API and engine notes

- `GET /healthz` is a cheap liveness check.
- `/api/v1/config` lists the six fixed seed-101 public presets and three supplied controls.
- `POST /api/v1/runs` creates an opaque run identifier.
- `POST /api/v1/runs/{run_id}/advance` advances 1–4 phases with a required revision and optional idempotency key.
- `/events`, `/export` and the member inspection route expose only released public observations.

The engine performs ask → refreshed observation → match → day advance for each
decision day. Once day 60 is reached it submits empty introductions for the 40
follow-up days. The policy adapter receives a copied public state and explicit
memory; hidden truth, future arrivals, response propensities, exit days and
unreleased feedback never cross the adapter or browser boundary.

Environment settings are intentionally small and process-local:
`DEMO_MAX_RUNS` (default 8), `DEMO_RUN_TTL_SECONDS` (1200),
`DEMO_MAX_LIFETIME_SECONDS` (3600), `DEMO_MAX_EVENTS` (500) and
`DEMO_BUILD_VERSION`. No secrets or external services are required.

## Tests

Install the development requirements and run:

```bash
pytest -q demo/tests
```

The tests cover engine parity against the supplied simulator, public-state
privacy, API validation, idempotent revisions and concurrent advance guards.
