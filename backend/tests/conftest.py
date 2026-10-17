import os
import tempfile

import pytest

# Point the app at a throwaway data dir *before* app modules are imported,
# so tests never touch your real database or uploads.
os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="meetings-test-")

from fastapi.testclient import TestClient  # noqa: E402

from app import pipeline  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(pipeline, "FAKE_STEP_SECONDS", 0)
    with TestClient(app) as c:
        yield c
