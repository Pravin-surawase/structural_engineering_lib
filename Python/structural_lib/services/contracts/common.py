"""Common strict public-model and structured-issue translation contract."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import Any, ClassVar, Literal, TypeVar, get_args, get_origin

from pydantic import BaseModel, ConfigDict, model_validator
from pydantic import ValidationError as PydanticValidationError

from structural_lib.core.errors import InputContractError, InputIssueV1

__all__ = [
    "FieldContractV1",
    "INPUT_ISSUE_CODES_V1",
    "StrictPublicModel",
    "ValidationDimension",
    "complete_field_contracts_from_schema",
    "input_issues_from_details",
    "model_validate_or_error",
    "schema_leaf_paths",
]


INPUT_ISSUE_CODES_V1 = (
    "INPUT_NOT_FINITE",
    "INPUT_TYPE_INVALID",
    "EXTRA_FIELD_FORBIDDEN",
    "REQUIRED_FIELD_MISSING",
    "ENUM_VALUE_INVALID",
    "INPUT_OUT_OF_RANGE",
    "IDENTITY_INVALID",
    "CROSS_FIELD_CONTRACT_INVALID",
    "SERVICEABILITY_SCOPE_HOLD",
    "INPUT_CONTRACT_INVALID",
)


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

    @model_validator(mode="before")
    @classmethod
    def reject_literal_boolean_coercion(cls, value: Any) -> Any:
        """Keep ``Literal[True/False]`` fields identity-strict at intake."""

        if not isinstance(value, Mapping):
            return value
        for name, field in cls.model_fields.items():
            annotation = field.annotation
            if get_origin(annotation) is not Literal:
                continue
            expected = get_args(annotation)
            if len(expected) != 1 or not isinstance(expected[0], bool):
                continue
            if name in value and value[name] is not expected[0]:
                raise ValueError(
                    f"{name} must be the exact boolean {str(expected[0]).lower()}"
                )
        return value


def _resolve_schema_node(
    node: Mapping[str, Any], root: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Resolve local references and the non-null branch of optional schemas."""

    current = node
    seen: set[str] = set()
    while "$ref" in current:
        reference = str(current["$ref"])
        if reference in seen or not reference.startswith("#/"):
            break
        seen.add(reference)
        resolved: Any = root
        for part in reference[2:].split("/"):
            resolved = resolved[part.replace("~1", "/").replace("~0", "~")]
        if not isinstance(resolved, Mapping):
            break
        current = resolved
    alternatives = current.get("anyOf")
    if isinstance(alternatives, list):
        non_null = [
            item
            for item in alternatives
            if isinstance(item, Mapping) and item.get("type") != "null"
        ]
        if len(non_null) == 1:
            return _resolve_schema_node(non_null[0], root)
    return current


def _schema_leaf_nodes(
    node: Mapping[str, Any],
    root: Mapping[str, Any],
    *,
    prefix: str = "",
) -> list[tuple[str, Mapping[str, Any]]]:
    current = _resolve_schema_node(node, root)
    properties = current.get("properties")
    if isinstance(properties, Mapping) and properties:
        leaves: list[tuple[str, Mapping[str, Any]]] = []
        for name, child in properties.items():
            if not isinstance(child, Mapping):
                continue
            path = f"{prefix}.{name}" if prefix else str(name)
            leaves.extend(_schema_leaf_nodes(child, root, prefix=path))
        return leaves
    return [(prefix or "$", current)]


def schema_leaf_paths(model: type[StrictPublicModel]) -> tuple[str, ...]:
    """Return deterministic validation-schema leaf paths for one request model."""

    schema = model.model_json_schema(mode="validation")
    return tuple(path for path, _node in _schema_leaf_nodes(schema, schema))


def _unit_for_path(path: str) -> str | None:
    lowered = path.lower()
    units = (
        ("_kn_per_m2", "kN/m2"),
        ("_kn_per_m", "kN/m"),
        ("_knm_per_m", "kN.m/m"),
        ("_nmm2", "N/mm2"),
        ("_mm3", "mm3"),
        ("_mm2", "mm2"),
        ("_mm", "mm"),
        ("_knm", "kN.m"),
        ("_kn", "kN"),
        ("_kpa", "kPa"),
        ("_percent", "%"),
    )
    for suffix, unit in units:
        if lowered.endswith(suffix):
            return unit
    return "dimensionless"


def _zero_allowed(node: Mapping[str, Any]) -> bool:
    minimum = node.get("minimum")
    exclusive_minimum = node.get("exclusiveMinimum")
    maximum = node.get("maximum")
    exclusive_maximum = node.get("exclusiveMaximum")
    if isinstance(exclusive_minimum, (int, float)):
        return exclusive_minimum < 0
    if isinstance(minimum, (int, float)):
        return minimum <= 0
    if isinstance(exclusive_maximum, (int, float)) and exclusive_maximum <= 0:
        return False
    if isinstance(maximum, (int, float)) and maximum < 0:
        return False
    return True


def complete_field_contracts_from_schema(
    model: type[StrictPublicModel],
    *,
    overrides: Sequence[FieldContractV1] = (),
) -> tuple[FieldContractV1, ...]:
    """Complete one strict request model's advertised field decisions.

    The schema remains the constraint authority. This function projects every
    leaf into the closed validation vocabulary and lets maintained hand-written
    records, such as the accepted B0 beam contracts, override richer paths.
    """

    schema = model.model_json_schema(mode="validation")
    records: dict[str, FieldContractV1] = {}
    for path, node in _schema_leaf_nodes(schema, schema):
        current = _resolve_schema_node(node, schema)
        schema_type = current.get("type")
        dimensions = [ValidationDimension.TYPE_AND_FINITE_VALUE]
        unit: str | None = None
        zero_allowed: bool | None = None

        if schema_type in {"integer", "number"}:
            dimensions.extend(
                (
                    ValidationDimension.RANGE_AND_ZERO_POLICY,
                    ValidationDimension.UNIT_AND_QUANTITY,
                )
            )
            unit = _unit_for_path(path)
            zero_allowed = _zero_allowed(current)

        lowered = path.lower()
        if schema_type == "string" or any(
            token in lowered
            for token in (
                "identity",
                "member_id",
                "case_id",
                "family_id",
                "story",
                "source",
                "reference",
                "review",
            )
        ):
            dimensions.append(ValidationDimension.IDENTITY_AND_PROVENANCE)

        if (
            "enum" in current
            or "const" in current
            or schema_type == "boolean"
            or any(
                token in lowered
                for token in (
                    "topology",
                    "condition",
                    "location",
                    "restraint",
                    "support",
                    "acknowledged",
                    "confirmed",
                    "approved",
                    "required",
                    "present",
                )
            )
        ):
            dimensions.append(ValidationDimension.ENUM_AND_TOPOLOGY)

        if any(
            token in lowered
            for token in (
                "material",
                "reinforcement",
                "concrete",
                "steel",
                "fck_",
                "fy_",
                "grade",
                "bar_",
            )
        ):
            dimensions.append(ValidationDimension.CODE_AND_MATERIAL_DOMAIN)

        if schema_type == "array" or "additionalProperties" in current:
            dimensions.append(ValidationDimension.COLLECTION_CARDINALITY_AND_UNIQUENESS)

        records[path] = FieldContractV1(
            path=path,
            dimensions=tuple(dict.fromkeys(dimensions)),
            unit=unit,
            zero_allowed=zero_allowed,
        )

    for contract in overrides:
        records[contract.path] = contract

    records["$"] = FieldContractV1(
        path="$",
        dimensions=(
            ValidationDimension.CROSS_FIELD_RELATION,
            ValidationDimension.DOWNSTREAM_CONSUMABILITY,
            ValidationDimension.COMPATIBILITY_ALIAS_AND_MIGRATION_TARGET,
        ),
    )
    return tuple(
        records[path] for path in sorted(records, key=lambda item: (item != "$", item))
    )


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
