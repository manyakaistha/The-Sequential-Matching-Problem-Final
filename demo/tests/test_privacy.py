from __future__ import annotations

from fastapi.testclient import TestClient

from demo.app import app


def test_member_inspection_and_export_only_use_public_fields():
    client = TestClient(app)
    run = client.post("/api/v1/runs", json={"preset_id": "public-101-cold-start", "policy": "no_asks"}).json()
    run_id = run["run_id"]
    member_id = run["state"]["members"][0]["member_id"]
    inspection = client.get(f"/api/v1/runs/{run_id}/members/{member_id}/inspection")
    assert inspection.status_code == 200
    assert "truth" not in inspection.text
    assert "response_rate" not in inspection.text
    export = client.get(f"/api/v1/runs/{run_id}/export")
    assert "exit_day" not in export.text
    assert "future" not in export.text.lower()
