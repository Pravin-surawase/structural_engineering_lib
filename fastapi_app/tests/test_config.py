"""Tests for safe, environment-configurable FastAPI settings."""

import os
from pathlib import Path
import subprocess  # nosec B404 - fixed interpreter command in isolated startup test
import sys

import pytest
from pydantic import ValidationError

from fastapi_app.config import Settings

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_VALID_PRODUCTION_SECRET = (  # nosec B105 - non-sensitive test fixture
    "production-secret-0123456789-abcdef"
)
_DEFAULT_DEVELOPMENT_SECRET = (  # nosec B105 - documented public placeholder
    "dev-secret-key-change-in-production"
)


def _import_main_with_environment(
    **environment: str,
) -> subprocess.CompletedProcess[str]:
    """Import the ASGI app in a clean interpreter with explicit settings."""
    child_environment = os.environ.copy()
    child_environment.update(environment)
    return subprocess.run(  # nosec B603 - argv and cwd are repository constants
        [sys.executable, "-c", "from fastapi_app.main import app"],
        cwd=_REPOSITORY_ROOT,
        env=child_environment,
        capture_output=True,
        text=True,
        check=False,
    )


def test_server_host_is_private_by_default_and_environment_configurable(monkeypatch):
    """Local startup stays private unless a deploy environment opts in."""
    monkeypatch.delenv("HOST", raising=False)
    assert Settings(_env_file=None).host == "127.0.0.1"

    monkeypatch.setenv("HOST", "192.0.2.10")
    assert Settings(_env_file=None).host == "192.0.2.10"


def test_development_defaults_remain_unauthenticated(monkeypatch):
    """Local development and test startup retain the existing defaults."""
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("AUTH_ENABLED", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)

    settings = Settings(_env_file=None)

    assert settings.environment == "development"
    assert settings.auth_enabled is False
    assert settings.etabs_live_bridge_enabled is False
    assert settings.etabs_live_mutation_enabled is False


def test_etabs_mutation_requires_live_bridge(monkeypatch):
    monkeypatch.setenv("ETABS_LIVE_BRIDGE_ENABLED", "false")
    monkeypatch.setenv("ETABS_LIVE_MUTATION_ENABLED", "true")

    with pytest.raises(ValidationError, match="requires ETABS_LIVE_BRIDGE_ENABLED"):
        Settings(_env_file=None)


def test_etabs_live_bridge_requires_loopback_bind(monkeypatch):
    monkeypatch.setenv(
        "HOST", "0.0.0.0"  # nosec B104 - unsafe bind is the rejection fixture
    )
    monkeypatch.setenv("ETABS_LIVE_BRIDGE_ENABLED", "true")
    monkeypatch.setenv("AUTH_ENABLED", "true")
    monkeypatch.setenv("JWT_SECRET_KEY", _VALID_PRODUCTION_SECRET)

    with pytest.raises(ValidationError, match="requires HOST.*loopback"):
        Settings(_env_file=None)


def test_etabs_live_bridge_requires_authentication(monkeypatch):
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("ETABS_LIVE_BRIDGE_ENABLED", "true")
    monkeypatch.setenv("AUTH_ENABLED", "false")
    monkeypatch.setenv("JWT_SECRET_KEY", _VALID_PRODUCTION_SECRET)

    with pytest.raises(ValidationError, match="AUTH_ENABLED=true is required"):
        Settings(_env_file=None)


def test_etabs_live_bridge_requires_non_default_secret(monkeypatch):
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("ETABS_LIVE_BRIDGE_ENABLED", "true")
    monkeypatch.setenv("AUTH_ENABLED", "true")
    monkeypatch.setenv("JWT_SECRET_KEY", _DEFAULT_DEVELOPMENT_SECRET)

    with pytest.raises(ValidationError, match="JWT_SECRET_KEY must be non-default"):
        Settings(_env_file=None)


def test_etabs_live_bridge_accepts_secured_loopback_profile(monkeypatch):
    monkeypatch.setenv("HOST", "::1")
    monkeypatch.setenv("ETABS_LIVE_BRIDGE_ENABLED", "true")
    monkeypatch.setenv("ETABS_LIVE_MUTATION_ENABLED", "true")
    monkeypatch.setenv("AUTH_ENABLED", "true")
    monkeypatch.setenv("JWT_SECRET_KEY", _VALID_PRODUCTION_SECRET)

    settings = Settings(_env_file=None)

    assert settings.etabs_live_route_policy.live_bridge_enabled is True
    assert settings.etabs_live_route_policy.live_mutation_enabled is True


def test_production_requires_authentication(monkeypatch):
    """Production-like profiles must not serve public endpoints."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_ENABLED", "false")
    monkeypatch.setenv("JWT_SECRET_KEY", _VALID_PRODUCTION_SECRET)

    with pytest.raises(ValidationError, match="AUTH_ENABLED=true is required"):
        Settings(_env_file=None)


def test_production_app_import_refuses_disabled_authentication():
    """The ASGI application fails before serving with production auth disabled."""
    result = _import_main_with_environment(
        ENVIRONMENT="production",
        AUTH_ENABLED="false",
        JWT_SECRET_KEY=_VALID_PRODUCTION_SECRET,
    )

    assert result.returncode != 0
    assert "AUTH_ENABLED=true is required" in result.stderr


@pytest.mark.parametrize(
    "secret",
    ["", "short-production-secret", "change-me-in-production", "dev-secret"],
)
def test_production_rejects_empty_or_placeholder_jwt_secret(monkeypatch, secret):
    """Production auth cannot be enabled with the supplied development secret."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_ENABLED", "true")
    monkeypatch.setenv("JWT_SECRET_KEY", secret)

    with pytest.raises(ValidationError, match="JWT_SECRET_KEY must be non-default"):
        Settings(_env_file=None)


def test_production_accepts_authentication_with_non_default_secret(monkeypatch):
    """A configured production profile remains valid."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_ENABLED", "true")
    monkeypatch.setenv("JWT_SECRET_KEY", _VALID_PRODUCTION_SECRET)

    settings = Settings(_env_file=None)

    assert settings.auth_enabled is True


def test_production_app_import_allows_valid_authentication_setup():
    """A configured production ASGI application can start."""
    result = _import_main_with_environment(
        ENVIRONMENT="production",
        AUTH_ENABLED="true",
        JWT_SECRET_KEY=_VALID_PRODUCTION_SECRET,
    )

    assert result.returncode == 0, result.stderr


def test_development_app_import_keeps_current_local_startup_behavior():
    """The local profile still imports with development authentication defaults."""
    result = _import_main_with_environment(
        ENVIRONMENT="development",
        AUTH_ENABLED="false",
        JWT_SECRET_KEY=_DEFAULT_DEVELOPMENT_SECRET,
    )

    assert result.returncode == 0, result.stderr
