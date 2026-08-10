"""Bounded-runner tests for the approved beam workflow only."""

from __future__ import annotations

from copy import deepcopy
from threading import Event, Thread
from types import SimpleNamespace

import pytest

from structural_lib.services.workflow_runner import (
    WorkflowBusyError,
    WorkflowDefinitionError,
    WorkflowIdempotencyError,
    WorkflowInputError,
    WorkflowRunner,
    get_beam_workflow_template_document,
    serialize_beam_workflow_template,
    validate_workflow_definition,
)

SAFE_INPUTS = {
    "width": 300.0,
    "depth": 500.0,
    "moment": 150.0,
    "shear": 75.0,
    "fck": 25.0,
    "fy": 500.0,
}


def test_template_is_deterministic_and_exactly_allowlisted() -> None:
    template = get_beam_workflow_template_document()

    assert validate_workflow_definition(template) == template
    assert serialize_beam_workflow_template() == serialize_beam_workflow_template()
    assert [step["step_id"] for step in template["steps"]] == [
        "input",
        "validate",
        "design",
        "review",
        "export",
    ]


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda item: item["steps"][2].update(handler_id="os.system"), "allowlisted"),
        (lambda item: item.update(path="/tmp/run.py"), "forbidden"),
        (lambda item: item["steps"].reverse(), "allowlisted"),
        (lambda item: item["limits"].update(max_steps=99), "cannot be changed"),
    ],
)
def test_tampered_definition_cannot_execute(mutation, message: str) -> None:
    definition = deepcopy(get_beam_workflow_template_document())
    mutation(definition)

    with pytest.raises(WorkflowDefinitionError, match=message):
        validate_workflow_definition(definition)


def test_safe_run_stops_for_review_then_completes_with_acknowledgement() -> None:
    runner = WorkflowRunner()
    definition = get_beam_workflow_template_document()

    held = runner.run(
        definition=definition,
        inputs=SAFE_INPUTS,
        run_id="safe-held",
    )
    completed = runner.run(
        definition=definition,
        inputs=SAFE_INPUTS,
        run_id="safe-completed",
        review_acknowledged=True,
    )

    assert held["status"] == "REVIEW_REQUIRED"
    assert held["export"] is None
    assert completed["status"] == "COMPLETED"
    assert completed["export"]["status"] == "PASS"
    assert completed["export"]["qualified_review_required"] is True


def test_unsafe_run_stops_before_export() -> None:
    runner = WorkflowRunner()
    unsafe = {**SAFE_INPUTS, "moment": 2_000.0, "depth": 250.0}

    result = runner.run(
        definition=get_beam_workflow_template_document(),
        inputs=unsafe,
        run_id="unsafe",
        review_acknowledged=True,
    )

    assert result["status"] == "UNSAFE"
    assert result["export"] is None
    assert result["steps"][-1]["reason"] == "UNSAFE_RESULT"


def test_timeout_and_idempotency_are_deterministic() -> None:
    template = get_beam_workflow_template_document()
    runner = WorkflowRunner()
    timed_out = runner.run(
        definition=template,
        inputs=SAFE_INPUTS,
        run_id="timed-out",
        timeout_ms=0,
    )
    first = runner.run(
        definition=template,
        inputs=SAFE_INPUTS,
        run_id="repeat",
    )
    replay = runner.run(
        definition=template,
        inputs=SAFE_INPUTS,
        run_id="repeat",
    )

    assert timed_out["status"] == "TIMED_OUT"
    assert first["idempotent_replay"] is False
    assert replay["idempotent_replay"] is True
    with pytest.raises(WorkflowIdempotencyError, match="different"):
        runner.run(
            definition=template,
            inputs={**SAFE_INPUTS, "moment": 160.0},
            run_id="repeat",
        )


def test_active_run_can_be_cancelled_and_concurrency_stays_bounded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entered = Event()
    release = Event()
    result: dict[str, object] = {}

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
    runner = WorkflowRunner()
    template = get_beam_workflow_template_document()

    def execute() -> None:
        result.update(
            runner.run(definition=template, inputs=SAFE_INPUTS, run_id="active-run")
        )

    worker = Thread(target=execute)
    worker.start()
    assert entered.wait(timeout=2)
    assert runner.cancel("unknown-run") is False
    assert runner.cancel("active-run") is True
    with pytest.raises(WorkflowBusyError, match="concurrency quota"):
        runner.run(definition=template, inputs=SAFE_INPUTS, run_id="second-run")
    release.set()
    worker.join(timeout=2)

    assert not worker.is_alive()
    assert result["status"] == "CANCELLED"
    assert result["export"] is None


def test_invalid_run_identity_and_oversized_input_fail_closed() -> None:
    runner = WorkflowRunner()
    template = get_beam_workflow_template_document()

    with pytest.raises(WorkflowInputError, match="run_id"):
        runner.run(definition=template, inputs=SAFE_INPUTS, run_id="../escape")
    with pytest.raises(WorkflowInputError, match="byte quota"):
        runner.run(
            definition=template,
            inputs={**SAFE_INPUTS, "payload": "x" * 40_000},
            run_id="oversized",
        )
