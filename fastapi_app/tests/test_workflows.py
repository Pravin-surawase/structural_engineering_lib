"""Transport gates for the explicitly activated bounded workflow runner."""

from __future__ import annotations

from copy import deepcopy
from threading import Event, Thread
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from fastapi_app.config import get_settings
from structural_lib.services.workflow_runner import (
    get_beam_workflow_template_document,
)

SAFE_INPUTS = {
    "width": 300.0,
    "depth": 500.0,
    "moment": 150.0,
    "shear": 75.0,
    "fck": 25.0,
    "fy": 500.0,
}


def _payload(run_id: str, **overrides):
    return {
        "definition": get_beam_workflow_template_document(),
        "inputs": SAFE_INPUTS,
        "run_id": run_id,
        **overrides,
    }


def test_template_is_read_only_but_execution_is_disabled_by_default(
    client: TestClient,
) -> None:
    settings = get_settings()
    previous = settings.workflow_runner_enabled
    settings.workflow_runner_enabled = False
    try:
        template = client.get("/api/v1/workflows/beam-template")
        run = client.post("/api/v1/workflows/run", json=_payload("disabled"))
    finally:
        settings.workflow_runner_enabled = previous

    assert template.status_code == 200
    assert template.json()["data"] == get_beam_workflow_template_document()
    assert run.status_code == 404
    assert run.json()["error"]["code"] == "WORKFLOW_RUNNER_DISABLED"


def test_enabled_transport_validates_runs_and_replays(client: TestClient) -> None:
    settings = get_settings()
    previous = settings.workflow_runner_enabled
    settings.workflow_runner_enabled = True
    try:
        validated = client.post(
            "/api/v1/workflows/validate",
            json={
                "definition": get_beam_workflow_template_document(),
                "inputs": SAFE_INPUTS,
            },
        )
        completed = client.post(
            "/api/v1/workflows/run",
            json=_payload("api-complete", review_acknowledged=True),
        )
        replay = client.post(
            "/api/v1/workflows/run",
            json=_payload("api-complete", review_acknowledged=True),
        )
    finally:
        settings.workflow_runner_enabled = previous

    assert validated.status_code == 200
    assert validated.json()["data"]["valid"] is True
    assert completed.status_code == 200
    assert completed.json()["data"]["status"] == "COMPLETED"
    assert replay.json()["data"]["idempotent_replay"] is True


def test_enabled_transport_stops_tampered_and_timed_out_runs(
    client: TestClient,
) -> None:
    settings = get_settings()
    previous = settings.workflow_runner_enabled
    settings.workflow_runner_enabled = True
    tampered = deepcopy(get_beam_workflow_template_document())
    tampered["steps"][2]["handler_id"] = "os.system"
    try:
        invalid = client.post(
            "/api/v1/workflows/run",
            json={**_payload("api-invalid"), "definition": tampered},
        )
        timed_out = client.post(
            "/api/v1/workflows/run",
            json=_payload("api-timeout", timeout_ms=0),
        )
    finally:
        settings.workflow_runner_enabled = previous

    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "WORKFLOW_VALIDATION_ERROR"
    assert timed_out.json()["data"]["status"] == "TIMED_OUT"


def test_enabled_transport_can_cancel_an_active_run(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entered = Event()
    release = Event()
    response_holder = {}

    def blocking_design(**_kwargs):
        entered.set()
        assert release.wait(timeout=2)
        return SimpleNamespace(
            is_ok=True,
            governing_utilization=0.5,
            flexure=SimpleNamespace(Ast_required=900.0),
            remarks=("PASS",),
        )

    monkeypatch.setattr(
        "structural_lib.services.workflow_runner.design_beam_is456",
        blocking_design,
    )
    settings = get_settings()
    previous = settings.workflow_runner_enabled
    settings.workflow_runner_enabled = True

    def execute() -> None:
        response_holder["response"] = client.post(
            "/api/v1/workflows/run", json=_payload("api-active-cancel")
        )

    worker = Thread(target=execute)
    try:
        worker.start()
        assert entered.wait(timeout=2)
        cancelled = client.post("/api/v1/workflows/runs/api-active-cancel/cancel")
        release.set()
        worker.join(timeout=2)
    finally:
        release.set()
        worker.join(timeout=2)
        settings.workflow_runner_enabled = previous

    assert cancelled.json()["data"]["cancellation_requested"] is True
    assert not worker.is_alive()
    assert response_holder["response"].json()["data"]["status"] == "CANCELLED"


def test_run_id_reuse_with_different_input_is_conflict(client: TestClient) -> None:
    settings = get_settings()
    previous = settings.workflow_runner_enabled
    settings.workflow_runner_enabled = True
    try:
        first = client.post("/api/v1/workflows/run", json=_payload("api-conflict"))
        conflict = client.post(
            "/api/v1/workflows/run",
            json={
                **_payload("api-conflict"),
                "inputs": {**SAFE_INPUTS, "moment": 160.0},
            },
        )
    finally:
        settings.workflow_runner_enabled = previous

    assert first.status_code == 200
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "WORKFLOW_IDEMPOTENCY_CONFLICT"
