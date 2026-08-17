# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Bounded in-memory runner for one approved beam review workflow."""

from __future__ import annotations

import hashlib
import json
import re
import threading
import time
from collections import OrderedDict
from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, cast

from structural_lib.core.result_contract import (
    CalculationStatus,
    EngineeringStatus,
    IntakeStatus,
    StructuralIssueV1,
    StructuralResultEnvelopeV2,
)
from structural_lib.services.beam_api import design_beam_is456
from structural_lib.services.evidence import (
    build_beam_evidence_envelope,
    build_beam_result_envelope,
)
from structural_lib.services.project_beam import (
    EffectiveDepthBasisV1,
    resolve_effective_depth_v1,
)
from structural_lib.services.workflow_catalog import (
    JsonScalar,
    get_workflow_catalog,
    get_workflow_input_defaults,
    validate_example_input,
)

__all__ = [
    "MAX_CACHED_RUNS",
    "MAX_DEFINITION_BYTES",
    "MAX_INPUT_BYTES",
    "MAX_OUTPUT_BYTES",
    "MAX_STEPS",
    "MAX_TIMEOUT_MS",
    "WORKFLOW_ID",
    "WORKFLOW_SCHEMA_VERSION",
    "WORKFLOW_VERSION",
    "WorkflowBusyError",
    "WorkflowDefinitionError",
    "WorkflowIdempotencyError",
    "WorkflowInputError",
    "WorkflowRunner",
    "get_beam_workflow_template_document",
    "serialize_beam_workflow_template",
    "validate_workflow_definition",
]

WORKFLOW_SCHEMA_VERSION = "1.0"
WORKFLOW_VERSION = "1.1.0"
WORKFLOW_ID = "is456.beam.review"
MAX_STEPS = 5
MAX_DEFINITION_BYTES = 16_384
MAX_INPUT_BYTES = 32_768
MAX_OUTPUT_BYTES = 262_144
MAX_TIMEOUT_MS = 2_000
MAX_CACHED_RUNS = 128
_RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
_STEP_CONTRACT = (
    ("input", "builtin.input.v1"),
    ("validate", "builtin.validate-beam.v1"),
    ("design", "is456.beam.design.v1"),
    ("review", "builtin.review-stop.v1"),
    ("export", "builtin.evidence-export.v1"),
)
_FORBIDDEN_DEFINITION_KEYS = frozenset(
    {"path", "file", "filename", "module", "import", "callable", "command", "url"}
)


class WorkflowDefinitionError(ValueError):
    """Raised when a workflow definition escapes the fixed template contract."""


class WorkflowInputError(ValueError):
    """Raised when input size, fields, units, or run identity are invalid."""


class WorkflowIdempotencyError(ValueError):
    """Raised when one run ID is reused for a different request."""


class WorkflowBusyError(RuntimeError):
    """Raised when the bounded in-memory concurrency quota is exhausted."""


@dataclass(frozen=True)
class _CachedRun:
    fingerprint: str
    result: dict[str, Any]


def _json_bytes(value: Any) -> bytes:
    try:
        encoded = json.dumps(
            value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise WorkflowDefinitionError(
            "Workflow payload must be JSON serializable"
        ) from exc
    return encoded


def _contains_forbidden_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key).lower() in _FORBIDDEN_DEFINITION_KEYS:
                return True
            if _contains_forbidden_key(item):
                return True
    elif isinstance(value, list):
        return any(_contains_forbidden_key(item) for item in value)
    return False


def get_beam_workflow_template_document() -> dict[str, Any]:
    """Return the only accepted ordered workflow definition."""
    return {
        "schema_version": WORKFLOW_SCHEMA_VERSION,
        "workflow_id": WORKFLOW_ID,
        "workflow_version": WORKFLOW_VERSION,
        "title": "Beam design with explicit review stop",
        "capability_id": "is456.beam.design",
        "steps": [
            {
                "step_id": step_id,
                "handler_id": handler_id,
                "position": position,
            }
            for position, (step_id, handler_id) in enumerate(_STEP_CONTRACT, start=1)
        ],
        "bindings": [
            {
                "source": "input.beam",
                "target": "design.request",
                "unit_contract": "catalog:is456.beam.design",
            },
            {
                "source": "design.result",
                "target": "review.evidence",
                "unit_contract": "fastapi.BeamDesignResponse.v2",
            },
        ],
        "limits": {
            "max_steps": MAX_STEPS,
            "max_definition_bytes": MAX_DEFINITION_BYTES,
            "max_input_bytes": MAX_INPUT_BYTES,
            "max_output_bytes": MAX_OUTPUT_BYTES,
            "max_timeout_ms": MAX_TIMEOUT_MS,
            "max_concurrency": 1,
            "max_project_members": 1,
            "max_batch_items": 1,
            "max_cached_runs": MAX_CACHED_RUNS,
        },
    }


def serialize_beam_workflow_template() -> str:
    """Return a deterministic save/export representation."""
    return _json_bytes(get_beam_workflow_template_document()).decode("utf-8")


def validate_workflow_definition(definition: Mapping[str, Any]) -> dict[str, Any]:
    """Validate exact identity, order, handlers, bindings, and bounded size."""
    if len(_json_bytes(definition)) > MAX_DEFINITION_BYTES:
        raise WorkflowDefinitionError("Workflow definition exceeds byte quota")
    if _contains_forbidden_key(definition):
        raise WorkflowDefinitionError(
            "Filesystem, import, command, and URL targets are forbidden"
        )
    expected = get_beam_workflow_template_document()
    if definition.get("schema_version") != WORKFLOW_SCHEMA_VERSION:
        raise WorkflowDefinitionError("Unsupported workflow schema version")
    if definition.get("workflow_id") != WORKFLOW_ID:
        raise WorkflowDefinitionError("Unknown workflow ID")
    if definition.get("workflow_version") != WORKFLOW_VERSION:
        raise WorkflowDefinitionError("Unsupported workflow version")
    if definition.get("capability_id") != "is456.beam.design":
        raise WorkflowDefinitionError("Unknown capability ID")

    steps = definition.get("steps")
    if not isinstance(steps, list) or len(steps) != MAX_STEPS:
        raise WorkflowDefinitionError(
            f"Workflow must contain exactly {MAX_STEPS} steps"
        )
    normalized_steps = []
    for position, ((step_id, handler_id), step) in enumerate(
        zip(_STEP_CONTRACT, steps, strict=True), start=1
    ):
        if not isinstance(step, Mapping):
            raise WorkflowDefinitionError("Workflow steps must be objects")
        normalized = {
            "step_id": step.get("step_id"),
            "handler_id": step.get("handler_id"),
            "position": step.get("position"),
        }
        if normalized != {
            "step_id": step_id,
            "handler_id": handler_id,
            "position": position,
        }:
            raise WorkflowDefinitionError(
                "Workflow step order or handler is not allowlisted"
            )
        normalized_steps.append(normalized)
    if definition.get("bindings") != expected["bindings"]:
        raise WorkflowDefinitionError(
            "Workflow bindings do not match the approved unit contract"
        )
    if definition.get("limits") != expected["limits"]:
        raise WorkflowDefinitionError(
            "Workflow quotas cannot be changed by a definition"
        )
    return deepcopy(expected)


def _normalize_inputs(values: Mapping[str, Any]) -> dict[str, float]:
    if len(_json_bytes(values)) > MAX_INPUT_BYTES:
        raise WorkflowInputError("Workflow input exceeds byte quota")
    capability = get_workflow_catalog().capabilities[0]
    defaults = get_workflow_input_defaults(capability)
    merged = {**defaults, **dict(values)}
    try:
        validate_example_input(
            capability,
            cast(dict[str, JsonScalar], merged),
        )
    except ValueError as exc:
        raise WorkflowInputError(str(exc)) from exc
    return {key: float(value) for key, value in merged.items()}


def _fingerprint(
    definition: Mapping[str, Any],
    inputs: Mapping[str, Any],
    review_acknowledged: bool,
    timeout_ms: int,
) -> str:
    return hashlib.sha256(
        _json_bytes(
            {
                "definition": definition,
                "inputs": inputs,
                "review_acknowledged": review_acknowledged,
                "timeout_ms": timeout_ms,
            }
        )
    ).hexdigest()


class WorkflowRunner:
    """One-process bounded runner with deterministic idempotency and cancellation."""

    def __init__(
        self,
        *,
        max_concurrency: int = 1,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if max_concurrency != 1:
            raise ValueError("The approved workflow runner concurrency is exactly 1")
        self._clock = clock
        self._lock = threading.Lock()
        self._active = 0
        self._active_run_ids: set[str] = set()
        self._cache: OrderedDict[str, _CachedRun] = OrderedDict()
        self._cancelled: set[str] = set()

    def cancel(self, run_id: str) -> bool:
        """Request cancellation only for a currently active run ID."""
        self._validate_run_id(run_id)
        with self._lock:
            if run_id not in self._active_run_ids:
                return False
            self._cancelled.add(run_id)
        return True

    def _validate_run_id(self, run_id: str) -> None:
        if _RUN_ID_PATTERN.fullmatch(run_id) is None:
            raise WorkflowInputError(
                "run_id must contain 1-64 letters, numbers, underscores, or hyphens"
            )

    def _is_cancelled(self, run_id: str) -> bool:
        with self._lock:
            return run_id in self._cancelled

    def _enter(self, run_id: str) -> None:
        with self._lock:
            if self._active >= 1:
                raise WorkflowBusyError("Workflow runner concurrency quota is busy")
            self._active += 1
            self._active_run_ids.add(run_id)

    def _leave(self, run_id: str) -> None:
        with self._lock:
            self._active -= 1
            self._active_run_ids.discard(run_id)
            self._cancelled.discard(run_id)

    def run(
        self,
        *,
        definition: Mapping[str, Any],
        inputs: Mapping[str, Any],
        run_id: str,
        review_acknowledged: bool = False,
        timeout_ms: int = 1_500,
    ) -> dict[str, Any]:
        """Run the fixed workflow or return a deterministic stop outcome."""
        self._validate_run_id(run_id)
        if not isinstance(timeout_ms, int) or isinstance(timeout_ms, bool):
            raise WorkflowInputError("timeout_ms must be an integer")
        if timeout_ms < 0 or timeout_ms > MAX_TIMEOUT_MS:
            raise WorkflowInputError(
                f"timeout_ms must be between 0 and {MAX_TIMEOUT_MS}"
            )
        normalized_definition = validate_workflow_definition(definition)
        normalized_inputs = _normalize_inputs(inputs)
        fingerprint = _fingerprint(
            normalized_definition,
            normalized_inputs,
            review_acknowledged,
            timeout_ms,
        )
        with self._lock:
            cached = self._cache.get(run_id)
        if cached is not None:
            if cached.fingerprint != fingerprint:
                raise WorkflowIdempotencyError(
                    "run_id was already used for a different workflow request"
                )
            replay = deepcopy(cached.result)
            replay["idempotent_replay"] = True
            return replay

        self._enter(run_id)
        try:
            started = self._clock()
            deadline = started + timeout_ms / 1000
            result = self._execute(
                run_id=run_id,
                inputs=normalized_inputs,
                review_acknowledged=review_acknowledged,
                deadline=deadline,
            )
            result["definition_hash"] = hashlib.sha256(
                _json_bytes(normalized_definition)
            ).hexdigest()
            result["input_hash"] = hashlib.sha256(
                _json_bytes(normalized_inputs)
            ).hexdigest()
            result["idempotent_replay"] = False
            if len(_json_bytes(result)) > MAX_OUTPUT_BYTES:
                raise WorkflowInputError("Workflow output exceeds byte quota")
            with self._lock:
                self._cache[run_id] = _CachedRun(fingerprint, deepcopy(result))
                self._cache.move_to_end(run_id)
                while len(self._cache) > MAX_CACHED_RUNS:
                    self._cache.popitem(last=False)
            return result
        finally:
            self._leave(run_id)

    def _stop_reason(self, run_id: str, deadline: float) -> str | None:
        if self._is_cancelled(run_id):
            return "CANCELLED"
        if self._clock() >= deadline:
            return "TIMED_OUT"
        return None

    def _execute(
        self,
        *,
        run_id: str,
        inputs: dict[str, float],
        review_acknowledged: bool,
        deadline: float,
    ) -> dict[str, Any]:
        steps: list[dict[str, Any]] = []
        stop = self._stop_reason(run_id, deadline)
        if stop:
            return self._stopped(run_id, stop, steps)
        steps.append({"step_id": "input", "status": "COMPLETED"})

        stop = self._stop_reason(run_id, deadline)
        if stop:
            return self._stopped(run_id, stop, steps)
        steps.append({"step_id": "validate", "status": "COMPLETED"})

        try:
            depth_resolution = resolve_effective_depth_v1(
                D_mm=inputs["depth"],
                d_mm=inputs.get("effective_depth"),
                effective_depth_basis=(
                    None
                    if inputs.get("effective_depth") is not None
                    else EffectiveDepthBasisV1(
                        clear_cover_mm=inputs["clear_cover"],
                        stirrup_diameter_mm=inputs["stirrup_dia_mm"],
                        tension_bar_diameter_mm=inputs["main_bar_dia_mm"],
                    )
                ),
            )
        except ValueError as exc:
            raise WorkflowInputError(str(exc)) from exc
        effective_depth = depth_resolution.d_mm
        d_dash_mm = (
            inputs["depth"] - effective_depth
            if depth_resolution.source == "DERIVED"
            else inputs["clear_cover"]
            + inputs["stirrup_dia_mm"]
            + inputs["main_bar_dia_mm"] / 2.0
        )
        design = design_beam_is456(
            units="IS456",
            b_mm=inputs["width"],
            D_mm=inputs["depth"],
            d_mm=inputs.get("effective_depth"),
            effective_depth_basis=depth_resolution.effective_depth_basis,
            mu_knm=inputs["moment"],
            vu_kn=inputs["shear"],
            fck_nmm2=inputs["fck"],
            fy_nmm2=inputs["fy"],
            d_dash_mm=d_dash_mm,
        )
        evidence = build_beam_evidence_envelope(
            inputs={
                "units": "IS456",
                "case_id": "CASE-1",
                "mu_knm": inputs["moment"],
                "vu_kn": inputs["shear"],
                "b_mm": inputs["width"],
                "D_mm": inputs["depth"],
                "d_mm": effective_depth,
                "fck_nmm2": inputs["fck"],
                "fy_nmm2": inputs["fy"],
                "d_dash_mm": d_dash_mm,
                "asv_mm2": 100.0,
            },
            is_ok=design.is_ok,
            governing_utilization=design.governing_utilization,
            utilizations=getattr(design, "utilizations", {}),
        )
        result_envelope = deepcopy(
            getattr(design, "result_envelope", None)
            or build_beam_result_envelope(
                is_ok=design.is_ok,
                evidence=evidence,
            ).to_dict()
        )
        design_payload = {
            "is_ok": bool(design.is_ok),
            "governing_utilization": float(design.governing_utilization),
            "ast_required_mm2": float(design.flexure.Ast_required),
            "remarks": str(design.remarks),
            "effective_depth_used": effective_depth,
            "effective_depth_basis": deepcopy(
                getattr(design, "effective_depth_resolution", None)
                or depth_resolution.to_dict()
            ),
            "result_envelope": result_envelope,
        }
        steps.append(
            {
                "step_id": "design",
                "status": "PASS" if design.is_ok else "FAIL",
                "output": design_payload,
            }
        )

        stop = self._stop_reason(run_id, deadline)
        if stop:
            return self._stopped(run_id, stop, steps)
        if not design.is_ok:
            steps.append(
                {
                    "step_id": "review",
                    "status": "STOPPED",
                    "reason": "UNSAFE_RESULT",
                }
            )
            return {
                "run_id": run_id,
                "workflow_id": WORKFLOW_ID,
                "status": "UNSAFE",
                "steps": steps,
                "export": None,
                "audit": {"review_stop": "UNSAFE_RESULT"},
                "result_envelope": result_envelope,
            }
        if not review_acknowledged:
            steps.append(
                {
                    "step_id": "review",
                    "status": "REVIEW_REQUIRED",
                    "reason": "USER_REVIEW_ACKNOWLEDGEMENT_REQUIRED",
                }
            )
            return {
                "run_id": run_id,
                "workflow_id": WORKFLOW_ID,
                "status": "REVIEW_REQUIRED",
                "steps": steps,
                "export": None,
                "audit": {"review_stop": "USER_REVIEW_ACKNOWLEDGEMENT_REQUIRED"},
                "result_envelope": result_envelope,
            }

        steps.append({"step_id": "review", "status": "ACKNOWLEDGED"})
        export = {
            "capability_id": "is456.beam.design",
            "status": "PASS",
            "qualified_review_required": True,
            "inputs": inputs,
            "result": design_payload,
            "result_envelope": result_envelope,
        }
        steps.append({"step_id": "export", "status": "COMPLETED"})
        return {
            "run_id": run_id,
            "workflow_id": WORKFLOW_ID,
            "status": "COMPLETED",
            "steps": steps,
            "export": export,
            "audit": {"review_stop": None},
            "result_envelope": result_envelope,
        }

    @staticmethod
    def _stopped(
        run_id: str, reason: str, steps: list[dict[str, Any]]
    ) -> dict[str, Any]:
        result_envelope = StructuralResultEnvelopeV2(
            intake_status=IntakeStatus.ACCEPTED,
            calculation_status=CalculationStatus.NOT_CALCULATED,
            engineering_status=EngineeringStatus.UNEVALUATED,
            issues=(
                StructuralIssueV1(
                    code=f"WORKFLOW_{reason}",
                    path="$.workflow",
                    message=f"Workflow stopped before calculation: {reason}.",
                ),
            ),
        ).to_dict()
        return {
            "run_id": run_id,
            "workflow_id": WORKFLOW_ID,
            "status": reason,
            "steps": steps,
            "export": None,
            "audit": {"review_stop": reason},
            "result_envelope": result_envelope,
        }
