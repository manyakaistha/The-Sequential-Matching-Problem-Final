from __future__ import annotations

from fastapi.testclient import TestClient

from demo.app import app


def test_health_config_and_public_run_flow():
    client = TestClient(app)
    assert client.get("/healthz").json()["status"] == "ok"
    config = client.get("/api/v1/config").json()
    assert len(config["presets"]) == 6
    assert {item["id"] for item in config["policies"]} == {"greedy", "no_asks", "random"}

    created = client.post("/api/v1/runs", json={"preset_id": "public-101-development", "policy": "greedy"})
    assert created.status_code == 201
    run = created.json()
    run_id = run["run_id"]
    assert run["phase"] == "ask"
    assert run["state"]["synthetic"] is True

    advanced = client.post(f"/api/v1/runs/{run_id}/advance", json={"expected_revision": 0, "steps": 1, "idempotency_key": "api-test-000001"})
    assert advanced.status_code == 200
    assert advanced.json()["run_id"] == run_id
    assert advanced.json()["phase"] == "match"

    retry = client.post(f"/api/v1/runs/{run_id}/advance", json={"expected_revision": 0, "steps": 1, "idempotency_key": "api-test-000001"})
    assert retry.status_code == 200
    assert retry.json()["revision"] == 1

    events = client.get(f"/api/v1/runs/{run_id}/events?after=0&limit=10")
    assert events.status_code == 200
    assert events.json()["events"][0]["event_type"] == "policy_action"
    export = client.get(f"/api/v1/runs/{run_id}/export")
    assert export.status_code == 200
    assert export.json()["synthetic"] is True
    assert "truth" not in export.text

    assert client.delete(f"/api/v1/runs/{run_id}").status_code == 204
    assert client.get(f"/api/v1/runs/{run_id}").status_code == 404


def test_invalid_input_unknown_preset_and_stale_revision():
    client = TestClient(app)
    invalid = client.post("/api/v1/runs", json={"preset_id": "not-public", "policy": "greedy"})
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "invalid_transition"
    malformed = client.post("/api/v1/runs", json={"preset_id": "public-101-development", "policy": "greedy", "extra": True})
    assert malformed.status_code == 422
    run = client.post("/api/v1/runs", json={"preset_id": "public-101-development", "policy": "greedy"}).json()
    run_id = run["run_id"]
    assert client.post(f"/api/v1/runs/{run_id}/advance", json={"expected_revision": 5, "steps": 1}).status_code == 409


def test_failed_transition_is_transactional(monkeypatch):
    import demo.engine as engine_module

    client = TestClient(app)
    run = client.post("/api/v1/runs", json={"preset_id": "public-101-development", "policy": "greedy"}).json()
    run_id = run["run_id"]
    monkeypatch.setattr(engine_module, "decide", lambda request, mode: {"pairs": [["missing-a", "missing-b"]], "memory": None} if request["phase"] == "match" else {"asks": [], "memory": None})
    # First call is an ask phase and succeeds; the second invalid match must not move the day.
    first = client.post(f"/api/v1/runs/{run_id}/advance", json={"expected_revision": 0, "steps": 1})
    assert first.status_code == 200
    failed = client.post(f"/api/v1/runs/{run_id}/advance", json={"expected_revision": 1, "steps": 1})
    assert failed.status_code == 422
    unchanged = client.get(f"/api/v1/runs/{run_id}").json()
    assert unchanged["revision"] == 1
    assert unchanged["day"] == 0
    assert unchanged["phase"] == "match"
