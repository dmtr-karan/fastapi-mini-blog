"""Shared pytest fixtures for exercising the FastAPI app in isolation."""

import importlib
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture()
def client(monkeypatch, tmp_path):
    """Provide a test client that uses an isolated temporary working directory."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("FASTAPI_MINI_BLOG_SECRET_KEY", "test-secret")
    (tmp_path / "static").mkdir(exist_ok=True)

    for module_name in ["main", "database", "security", "models.post", "models.user"]:
        sys.modules.pop(module_name, None)

    main_module = importlib.import_module("main")
    with TestClient(main_module.app) as test_client:
        yield test_client
