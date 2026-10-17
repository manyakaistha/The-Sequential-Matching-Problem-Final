from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from demo.app import app


def test_two_same_revision_advances_cannot_double_apply():
    client = TestClient(app)
    run = client.post("/api/v1/runs", json={"preset_id": "public-101-development", "policy": "greedy"}).json()
    run_id = run["run_id"]

    def send():
        return client.post(f"/api/v1/runs/{run_id}/advance", json={"expected_revision": 0, "steps": 1})

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: send(), range(2)))
    assert sorted(response.status_code for response in responses) == [200, 409]
    current = client.get(f"/api/v1/runs/{run_id}").json()
    assert current["revision"] == 1
