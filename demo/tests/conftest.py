from __future__ import annotations

import pytest

from demo.app import app
from demo.sessions import STORE


@pytest.fixture(autouse=True)
def clean_store():
    # Tests share the process-local store with the app, so release each run.
    run_ids = list(STORE._runs)  # noqa: SLF001 - test fixture intentionally drains the bounded store
    for run_id in run_ids:
        STORE._runs.pop(run_id, None)  # noqa: SLF001
    STORE._expired.clear()  # noqa: SLF001
    yield
    for run_id in list(STORE._runs):  # noqa: SLF001
        STORE._runs.pop(run_id, None)  # noqa: SLF001
