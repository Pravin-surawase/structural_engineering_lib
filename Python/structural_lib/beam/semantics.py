"""Portable semantic result, diagnostic, provenance, and identity primitives.

These types are independent from Excel, ETABS, HTTP, and rendering. Every
public operation reports the PF4 result dimensions separately and binds its
result to unit-normalized effective engineering inputs.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any

CANONICALIZATION_VERSION = "pf4-canonical-json-v1"
RESULT_SCHEMA_VERSION = "structural-operation-result/v1"


class ExecutionState(StrEnum):
    COMPLETED = "completed"
    REJECTED_INPUT = "rejected_input"
    NOT_RUN = "not_run"
    SOFTWARE_ERROR = "software_error"
    CANCELLED = "cancelled"


class ApplicabilityState(StrEnum):
    APPLICABLE = "applicable"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class EngineeringState(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    NOT_EVALUATED = "not_evaluated"


class CompletenessState(StrEnum):
    COMPLETE_FOR_SCOPE = "complete_for_scope"
    PARTIAL = "partial"


class FreshnessState(StrEnum):
    CURRENT = "current"
    STALE = "stale"
    UNBOUND = "unbound"


class ApprovalState(StrEnum):
    UNREVIEWED = "unreviewed"
    CHECKED = "checked"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Diagnostic:
    code: str
    severity: str
    message: str
    operation_semantic_id: str
    field_or_location: str | None = None
    source: str = "operation"
    remediation: str | None = None


@dataclass(frozen=True)
class EffectiveValue:
    value: Any
    state: str = "supplied"
    origin: str = "caller"
    dependencies: tuple[str, ...] = ()
    rule: str | None = None


@dataclass(frozen=True)
class Provenance:
    code_data_revision_id: str
    method_revision_id: str
    source_references: tuple[str, ...]


@dataclass(frozen=True)
class OperationResult:
    schema_version: str
    operation_semantic_id: str
    execution: ExecutionState
    applicability: ApplicabilityState
    engineering: EngineeringState
    completeness: CompletenessState
    freshness: FreshnessState
    approval: ApprovalState
    effective_inputs: Mapping[str, Any]
    outputs: Mapping[str, Any]
    diagnostics: tuple[Diagnostic, ...]
    provenance: Provenance
    normalized_input_id: str
    calculation_id: str
    result_id: str

    def to_dict(self) -> dict[str, Any]:
        return plain(asdict(self))


def plain(value: Any) -> Any:
    """Convert semantic records to finite JSON-compatible values."""

    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [plain(item) for item in value]
    if hasattr(value, "__dataclass_fields__"):
        return plain(asdict(value))
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Canonical engineering values must be finite")
        if value == 0:
            return 0
        if value.is_integer() and abs(value) <= 9_007_199_254_740_991:
            return int(value)
    return value


def canonical_json_bytes(value: Any) -> bytes:
    """Return PF4 canonical UTF-8 JSON for already normalized units."""

    return json.dumps(
        plain(value),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def semantic_hash(kind: str, value: Any) -> str:
    digest = hashlib.sha256(canonical_json_bytes(value)).hexdigest()
    return f"{kind}:{CANONICALIZATION_VERSION}:{digest}"


def effective_inputs(**values: Any) -> dict[str, dict[str, Any]]:
    """Wrap effective engineering values with state and origin."""

    return {
        key: plain(
            value if isinstance(value, EffectiveValue) else EffectiveValue(value)
        )
        for key, value in values.items()
    }


def _result(
    operation_semantic_id: str,
    inputs: Mapping[str, Any],
    outputs: Mapping[str, Any],
    *,
    execution: ExecutionState,
    applicability: ApplicabilityState,
    engineering: EngineeringState,
    completeness: CompletenessState,
    freshness: FreshnessState,
    diagnostics: Iterable[Diagnostic],
    provenance: Provenance,
    engine_build: str,
) -> OperationResult:
    diagnostic_items = tuple(diagnostics)
    normalized_id = semantic_hash("normalized_input_id", inputs)
    calculation_id = ""
    if execution is ExecutionState.COMPLETED:
        calculation_id = semantic_hash(
            "calculation_id",
            {
                "code_data_revision_id": provenance.code_data_revision_id,
                "engine_build": engine_build,
                "normalized_input_id": normalized_id,
                "operation_semantic_id": operation_semantic_id,
            },
        )
    semantic_outcome = {
        "applicability": applicability,
        "calculation_id": calculation_id,
        "completeness": completeness,
        "diagnostics": diagnostic_items,
        "engineering": engineering,
        "execution": execution,
        "freshness": freshness,
        "outputs": outputs,
    }
    return OperationResult(
        schema_version=RESULT_SCHEMA_VERSION,
        operation_semantic_id=operation_semantic_id,
        execution=execution,
        applicability=applicability,
        engineering=engineering,
        completeness=completeness,
        freshness=freshness,
        approval=ApprovalState.UNREVIEWED,
        effective_inputs=plain(inputs),
        outputs=plain(outputs),
        diagnostics=diagnostic_items,
        provenance=provenance,
        normalized_input_id=normalized_id,
        calculation_id=calculation_id,
        result_id=semantic_hash("result_id", semantic_outcome),
    )


def completed_result(
    operation_semantic_id: str,
    inputs: Mapping[str, Any],
    outputs: Mapping[str, Any],
    *,
    engineering: EngineeringState = EngineeringState.PASS,
    diagnostics: Iterable[Diagnostic] = (),
    provenance: Provenance,
    engine_build: str = "python-structural-engineering-v1",
) -> OperationResult:
    return _result(
        operation_semantic_id,
        inputs,
        outputs,
        execution=ExecutionState.COMPLETED,
        applicability=ApplicabilityState.APPLICABLE,
        engineering=engineering,
        completeness=CompletenessState.COMPLETE_FOR_SCOPE,
        freshness=FreshnessState.CURRENT,
        diagnostics=diagnostics,
        provenance=provenance,
        engine_build=engine_build,
    )


def rejected_result(
    operation_semantic_id: str,
    raw_inputs: Mapping[str, Any],
    diagnostics: Iterable[Diagnostic],
    *,
    provenance: Provenance,
) -> OperationResult:
    return _result(
        operation_semantic_id,
        raw_inputs,
        {},
        execution=ExecutionState.REJECTED_INPUT,
        applicability=ApplicabilityState.UNKNOWN,
        engineering=EngineeringState.NOT_EVALUATED,
        completeness=CompletenessState.PARTIAL,
        freshness=FreshnessState.UNBOUND,
        diagnostics=diagnostics,
        provenance=provenance,
        engine_build="python-structural-engineering-v1",
    )


def not_applicable_result(
    operation_semantic_id: str,
    inputs: Mapping[str, Any],
    diagnostic: Diagnostic,
    *,
    provenance: Provenance,
) -> OperationResult:
    return _result(
        operation_semantic_id,
        inputs,
        {},
        execution=ExecutionState.COMPLETED,
        applicability=ApplicabilityState.NOT_APPLICABLE,
        engineering=EngineeringState.NOT_EVALUATED,
        completeness=CompletenessState.COMPLETE_FOR_SCOPE,
        freshness=FreshnessState.CURRENT,
        diagnostics=(diagnostic,),
        provenance=provenance,
        engine_build="python-structural-engineering-v1",
    )


def not_evaluated_result(
    operation_semantic_id: str,
    inputs: Mapping[str, Any],
    diagnostic: Diagnostic,
    *,
    provenance: Provenance,
) -> OperationResult:
    """Return a completed but incomplete result for missing required evidence."""

    return _result(
        operation_semantic_id,
        inputs,
        {},
        execution=ExecutionState.COMPLETED,
        applicability=ApplicabilityState.UNKNOWN,
        engineering=EngineeringState.NOT_EVALUATED,
        completeness=CompletenessState.PARTIAL,
        freshness=FreshnessState.CURRENT,
        diagnostics=(diagnostic,),
        provenance=provenance,
        engine_build="python-structural-engineering-v1",
    )


def partial_result(
    operation_semantic_id: str,
    inputs: Mapping[str, Any],
    outputs: Mapping[str, Any],
    diagnostics: Iterable[Diagnostic],
    *,
    provenance: Provenance,
    freshness: FreshnessState = FreshnessState.CURRENT,
) -> OperationResult:
    """Return an applicable partial result while retaining evaluated evidence."""

    return _result(
        operation_semantic_id,
        inputs,
        outputs,
        execution=ExecutionState.COMPLETED,
        applicability=ApplicabilityState.APPLICABLE,
        engineering=EngineeringState.NOT_EVALUATED,
        completeness=CompletenessState.PARTIAL,
        freshness=freshness,
        diagnostics=diagnostics,
        provenance=provenance,
        engine_build="python-structural-engineering-v1",
    )


__all__ = [
    "ApprovalState",
    "ApplicabilityState",
    "CompletenessState",
    "Diagnostic",
    "EffectiveValue",
    "EngineeringState",
    "ExecutionState",
    "FreshnessState",
    "OperationResult",
    "Provenance",
    "canonical_json_bytes",
    "completed_result",
    "effective_inputs",
    "not_applicable_result",
    "not_evaluated_result",
    "partial_result",
    "plain",
    "rejected_result",
    "semantic_hash",
]
