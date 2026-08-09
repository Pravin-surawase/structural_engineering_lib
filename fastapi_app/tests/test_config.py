"""Tests for safe, environment-configurable FastAPI settings."""

from fastapi_app.config import Settings


def test_server_host_is_private_by_default_and_environment_configurable(monkeypatch):
    """Local startup stays private unless a deploy environment opts in."""
    monkeypatch.delenv("HOST", raising=False)
    assert Settings(_env_file=None).host == "127.0.0.1"

    monkeypatch.setenv("HOST", "192.0.2.10")
    assert Settings(_env_file=None).host == "192.0.2.10"
