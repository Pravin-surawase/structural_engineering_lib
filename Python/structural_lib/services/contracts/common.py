"""Common strict public-model and structured-issue translation contract."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import Any, ClassVar, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic import ValidationError as PydanticValidationError

from structural_lib.core.errors import InputContractError, InputIssueV1

__all__ = [
    "FieldContractV1",
    "StrictPublicModel",
    "ValidationDimension",
    "input_issues_from_details",
    "model_validate_or_error",
]


class ValidationDimension(StrEnum):
    """Closed vocabulary for advertised request-field validation."""

    TYPE_AND_FINITE_VALUE = "TYPE_AND_FINITE_VALUE"
    RANGE_AND_ZERO_POLICY = "RANGE_AND_ZERO_POLICY"
    UNIT_AND_QUANTITY = "UNIT_AND_QUANTITY"
    CODE_AND_MATERIAL_DOMAIN = "CODE_AND_MATERIAL_DOMAIN"
    CROSS_FIELD_RELATION = "CROSS_FIELD_RELATION"
    IDENTITY_AND_PROVENANCE = "IDENTITY_AND_PROVENANCE"
    ENUM_AND_TOPOLOGY = "ENUM_AND_TOPOLOGY"
    COLLECTION_CARDINALITY_AND_UNIQUENESS = "COLLECTION_CARDINALITY_AND_UNIQUENESS"
    DOWNSTREAM_CONSUMABILITY = "DOWNSTREAM_CONSUMABILITY"
    COMPATIBILITY_ALIAS_AND_MIGRATION_TARGET = (
        "COMPATIBILITY_ALIAS_AND_MIGRATION_TARGET"
    )


class FieldContractV1(BaseModel):
    """Machine-readable validation dimensions for one advertised field."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    path: str
    dimensions: tuple[ValidationDimension, ...]
    unit: str | None = None
    zero_allowed: bool | None = None
    compatibility_aliases: tuple[str, ...] = ()


class StrictPublicModel(BaseModel):
    """Base for immutable, non-coercing, finite public request models."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        str_strip_whitespace=True,
        allow_inf_nan=False,
        validate_default=True,
    )
    field_contracts: ClassVar[tuple[FieldContractV1, ...]] = ()


_ModelT = TypeVar("_ModelT", bound=StrictPublicModel)


def _safe_received(value: Any) -> Any:
    """Return bounded JSON-safe evidence without invoking arbitrary repr hooks."""

    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else str(value)
    if isinstance(value, (list, tuple)):
        return [_safe_received(item) for item in value[:10]]
    if isinstance(value, dict):
        return {
            str(key): _safe_received(item) for key, item in list(value.items())[:10]
        }
    return f"<{type(value).__name__}>"


def _issue_code(error_type: str) -> str:
    if error_type == "finite_number":
        return "INPUT_NOT_FINITE"
    if error_type in {"float_type", "int_type", "bool_type", "string_type"}:
        return "INPUT_TYPE_INVALID"
    if error_type == "extra_forbidden":
        return "EXTRA_FIELD_FORBIDDEN"
    if error_type == "missing":
        return "REQUIRED_FIELD_MISSING"
    if error_type in {"literal_error", "enum"}:
        return "ENUM_VALUE_INVALID"
    if error_type in {
        "greater_than",
        "greater_than_equal",
        "less_than",
        "less_than_equal",
    }:
        return "INPUT_OUT_OF_RANGE"
    if error_type in {"string_too_short", "string_pattern_mismatch"}:
        return "IDENTITY_INVALID"
    if error_type == "value_error":
        return "CROSS_FIELD_CONTRACT_INVALID"
    if error_type == "serviceability_scope_hold":
        return "SERVICEABILITY_SCOPE_HOLD"
    return "INPUT_CONTRACT_INVALID"


def _path(location: tuple[Any, ...]) -> str:
    return ".".join(str(part) for part in location) or "$"


def _allowed_values(context: dict[str, Any] | None) -> tuple[str, ...] | None:
    if not context:
        return None
    expected = context.get("expected")
    if not isinstance(expected, str):
        return None
    values = tuple(
        part.strip().strip("'")
        for part in expected.replace(" or ", ",").split(",")
        if part.strip()
    )
    return values or None


def issues_from_pydantic(error: PydanticValidationError) -> tuple[InputIssueV1, ...]:
    """Translate Pydantic internals into the stable library issue model."""

    return input_issues_from_details(error.errors(include_url=False))


def input_issues_from_details(
    details: Sequence[Mapping[str, Any]], *, drop_location_prefix: str | None = None
) -> tuple[InputIssueV1, ...]:
    """Translate Pydantic/FastAPI detail dictionaries into stable issues."""

    issues: list[InputIssueV1] = []
    for item in details:
        context = item.get("ctx")
        location = tuple(item.get("loc", ()))
        if drop_location_prefix and location[:1] == (drop_location_prefix,):
            location = location[1:]
        issues.append(
            InputIssueV1(
                code=_issue_code(str(item.get("type", ""))),
                path=_path(location),
                message=str(item.get("msg", "Invalid input.")),
                received=_safe_received(item.get("input")),
                constraint=(
                    str(context.get("error"))
                    if isinstance(context, dict) and context.get("error") is not None
                    else None
                ),
                allowed_values=_allowed_values(
                    context if isinstance(context, dict) else None
                ),
            )
        )
    return tuple(issues)


def model_validate_or_error(
    model: type[_ModelT], value: Any, *, path_prefix: str | None = None
) -> _ModelT:
    """Validate one public model without exposing raw Pydantic exceptions."""

    try:
        return model.model_validate(value)
    except PydanticValidationError as exc:
        issues = issues_from_pydantic(exc)
        if path_prefix:
            issues = tuple(
                InputIssueV1(
                    code=issue.code,
                    path=(
                        f"{path_prefix}.{issue.path}"
                        if issue.path != "$"
                        else path_prefix
                    ),
                    message=issue.message,
                    received=issue.received,
                    constraint=issue.constraint,
                    allowed_values=issue.allowed_values,
                    suggestion=issue.suggestion,
                )
                for issue in issues
            )
        raise InputContractError(issues) from None
