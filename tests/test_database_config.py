"""Unit tests for database configuration behavior."""

import importlib
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture()
def reloaded_database_module(monkeypatch, tmp_path):
    """Import a fresh database module instance for each test."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    for module_name in ["database", "main", "security", "models.post", "models.user"]:
        sys.modules.pop(module_name, None)

    sys.modules.pop("main", None)
    importlib.invalidate_caches()
    module = importlib.import_module("database")
    yield module
    sys.modules.pop("database", None)


def test_uses_default_sqlite_url_when_database_url_is_absent(reloaded_database_module):
    assert reloaded_database_module.DATABASE_URL == "sqlite:///data.db"


def test_uses_explicit_database_url_when_present(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///custom.db")

    for module_name in ["database", "main", "security", "models.post", "models.user"]:
        sys.modules.pop(module_name, None)

    importlib.invalidate_caches()
    database_module = importlib.import_module("database")

    assert database_module.DATABASE_URL == "sqlite:///custom.db"
    sys.modules.pop("database", None)


def test_sqlite_engine_uses_check_same_thread_false(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    for module_name in ["database", "main", "security", "models.post", "models.user"]:
        sys.modules.pop(module_name, None)

    importlib.invalidate_caches()
    with patch("sqlalchemy.create_engine") as create_engine:
        importlib.import_module("database")

    create_engine.assert_called_once()
    _, kwargs = create_engine.call_args
    assert kwargs["connect_args"] == {"check_same_thread": False}


def test_non_sqlite_engine_does_not_receive_sqlite_connect_args(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")

    for module_name in ["database", "main", "security", "models.post", "models.user"]:
        sys.modules.pop(module_name, None)

    importlib.invalidate_caches()

    with patch("databases.Database") as database_cls, patch("sqlalchemy.create_engine") as create_engine:
        database_cls.return_value = object()
        importlib.import_module("database")

    create_engine.assert_called_once()
    _, kwargs = create_engine.call_args
    assert kwargs["connect_args"] == {}
