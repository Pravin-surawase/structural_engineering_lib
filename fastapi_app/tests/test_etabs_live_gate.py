"""G0 startup, route, peer, and scope gates for live ETABS access."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess  # nosec B404 - fixed interpreter command in isolated startup test
import sys
import time

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from fastapi_app.auth import create_access_token, require_loopback_request
from fastapi_app.auth import ALGORITHM, SECRET_KEY
from fastapi_app.etabs_live_policy import (
    ETABS_OPERATION_POLICIES_V1,
    ETABSOperationClass,
)
from fastapi_app.main import app as default_app
from fastapi_app.routers import etabs_bridge
from structural_lib.services import etabs_live_bridge as etabs_live_service
import jwt
from structural_lib.services.etabs_live_bridge import (
    ETABSConnectionV1,
    ETABSModelIdentityV1,
)

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_VALID_SECRET = "etabs-live-test-secret-0123456789-abcdef"  # nosec B105
_CONNECT_PATH = "/api/v1/etabs-bridge/v1/connect"
_PILOT_PATH = "/api/v1/etabs-bridge/v1/beam-pilot"


def _token(*scopes: str) -> str:
    return create_access_token(
        {"sub": "g0-test-user", "email": "g0@example.com", "scopes": list(scopes)}
    )


def _read_app(*, enforce_loopback: bool = True) -> FastAPI:
    test_app = FastAPI()
    if not enforce_loopback:
        test_app.dependency_overrides[require_loopback_request] = lambda: None
    test_app.include_router(etabs_bridge.live_read_router, prefix="/api/v1")
    return test_app


def _connection() -> ETABSConnectionV1:
    return ETABSConnectionV1(
        library_version="0.24.0",
        library_content_identity="a" * 64,
        model=ETABSModelIdentityV1(
            model_name="approved-copy.edb",
            model_path=r"C:\models\approved-copy.edb",
            etabs_version="ETABS 22",
            etabs_version_number=22.0,
        ),
    )


def _fail_if_com_is_called():
    raise AssertionError("COM boundary must not be called before the G0 gate passes")


def test_server_owned_operation_classification_is_complete():
    classifications = {
        policy.path: (policy.operation_class, policy.required_scope)
        for policy in ETABS_OPERATION_POLICIES_V1
    }

    assert classifications == {
        "/api/v1/etabs-bridge/v1/status": (ETABSOperationClass.OFFLINE, None),
        "/api/v1/etabs-bridge/v1/beam-demand": (
            ETABSOperationClass.OFFLINE,
            None,
        ),
        "/api/v1/etabs-bridge/v1/connect": (
            ETABSOperationClass.LIVE_READ,
            "etabs:live:read",
        ),
        "/api/v1/etabs-bridge/v1/beam-baseline/preflight": (
            ETABSOperationClass.LIVE_READ,
            "etabs:live:read",
        ),
        "/api/v1/etabs-bridge/v1/beam-baseline": (
            ETABSOperationClass.LIVE_READ,
            "etabs:live:read",
        ),
        "/api/v1/etabs-bridge/v1/result-catalogue": (
            ETABSOperationClass.LIVE_READ,
            "etabs:live:read",
        ),
        "/api/v1/etabs-bridge/v1/beam-pilot": (
            ETABSOperationClass.LIVE_MUTATION,
            "etabs:live:mutate",
        ),
    }


def test_offline_status_cannot_construct_com_session(monkeypatch):
    class COMConstructionTripwire:
        def __init__(self):
            _fail_if_com_is_called()

    monkeypatch.setattr(
        etabs_live_service, "_ComtypesETABSSession", COMConstructionTripwire
    )

    with TestClient(default_app) as client:
        response = client.get("/api/v1/etabs-bridge/v1/status")

    assert response.status_code == 200, response.text


def test_default_disabled_live_route_cannot_reach_com(monkeypatch):
    monkeypatch.setattr(etabs_bridge, "connect_etabs_v1", _fail_if_com_is_called)

    with TestClient(default_app) as client:
        response = client.post(_CONNECT_PATH)

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("authorization", "expected_status"),
    [
        (None, 401),
        ("Bearer invalid-token", 401),
        (f"Bearer {_token('design')}", 403),
    ],
)
def test_read_gate_rejects_missing_invalid_or_wrong_scope_before_com(
    monkeypatch, authorization, expected_status
):
    monkeypatch.setattr(etabs_bridge, "connect_etabs_v1", _fail_if_com_is_called)
    headers = {"Authorization": authorization} if authorization else {}

    with TestClient(_read_app(enforce_loopback=False)) as client:
        response = client.post(_CONNECT_PATH, headers=headers)

    assert response.status_code == expected_status


def test_read_gate_rejects_signed_malformed_claims_before_com(monkeypatch):
    monkeypatch.setattr(etabs_bridge, "connect_etabs_v1", _fail_if_com_is_called)
    malformed = jwt.encode(
        {
            "sub": "malformed-user",
            "scopes": "etabs:live:read",
            "exp": time.time() + 300,
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    with TestClient(_read_app(enforce_loopback=False)) as client:
        response = client.post(
            _CONNECT_PATH,
            headers={"Authorization": f"Bearer {malformed}"},
        )

    assert response.status_code == 401


def test_read_gate_rejects_non_loopback_peer_before_com(monkeypatch):
    monkeypatch.setattr(etabs_bridge, "connect_etabs_v1", _fail_if_com_is_called)

    with TestClient(_read_app(), client=("192.0.2.10", 50000)) as remote_client:
        response = remote_client.post(
            _CONNECT_PATH,
            headers={"Authorization": f"Bearer {_token('etabs:live:read')}"},
        )

    assert response.status_code == 403
    assert "loopback" in response.json()["detail"].lower()


def test_read_gate_allows_scoped_loopback_request(monkeypatch):
    monkeypatch.setattr(etabs_bridge, "connect_etabs_v1", _connection)

    with TestClient(_read_app(), client=("127.0.0.1", 50000)) as local_client:
        response = local_client.post(
            _CONNECT_PATH,
            headers={"Authorization": f"Bearer {_token('etabs:live:read')}"},
        )

    assert response.status_code == 200, response.text
    assert response.json()["data"]["model"]["model_name"] == "approved-copy.edb"


@pytest.mark.parametrize("mutation_enabled", [False, True])
def test_secured_startup_mounts_only_enabled_live_classes(mutation_enabled):
    environment = os.environ.copy()
    environment.update(
        {
            "ENVIRONMENT": "development",
            "HOST": "127.0.0.1",
            "AUTH_ENABLED": "true",
            "JWT_SECRET_KEY": _VALID_SECRET,
            "ETABS_LIVE_BRIDGE_ENABLED": "true",
            "ETABS_LIVE_MUTATION_ENABLED": str(mutation_enabled).lower(),
            "RATE_LIMIT_ENABLED": "false",
            "PYTHONWARNINGS": "ignore",
        }
    )
    script = (
        "import json; "
        "from fastapi_app.main import app; "
        "from fastapi.testclient import TestClient; "
        "from fastapi_app.auth import create_access_token; "
        "schema=app.openapi(); "
        "client=TestClient(app, client=('127.0.0.1', 50000)); "
        "wrong=create_access_token({'sub':'wrong','scopes':['design']}); "
        f"invalid=client.post('{_CONNECT_PATH}', headers={{'Authorization':'Bearer invalid'}}); "
        f"wrong_scope=client.post('{_CONNECT_PATH}', headers={{'Authorization':'Bearer '+wrong}}); "
        "print(json.dumps({"
        "'paths': sorted(schema['paths']), "
        "'schemes': schema.get('components', {}).get('securitySchemes', {}), "
        f"'read_security': schema['paths']['{_CONNECT_PATH}']['post'].get('security'), "
        "'invalid_status': invalid.status_code, "
        "'wrong_scope_status': wrong_scope.status_code, "
        "'policy': app.state.etabs_live_route_policy.model_dump(mode='json')"
        "}))"
    )
    result = subprocess.run(  # nosec B603 - fixed interpreter and repository script
        [sys.executable, "-c", script],
        cwd=_REPOSITORY_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert _CONNECT_PATH in payload["paths"]
    assert (_PILOT_PATH in payload["paths"]) is mutation_enabled
    assert "HTTPBearer" in payload["schemes"]
    assert {"HTTPBearer": []} in payload["read_security"]
    assert payload["invalid_status"] == 401
    assert payload["wrong_scope_status"] == 403
    assert payload["policy"]["live_bridge_enabled"] is True
    assert payload["policy"]["live_mutation_enabled"] is mutation_enabled
