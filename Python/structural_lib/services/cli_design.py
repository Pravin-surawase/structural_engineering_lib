# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Strict, lossless intake and compatibility output for the advertised design CLI."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from structural_lib.core.data_types import CrackWidthParams, DeflectionParams

from . import beam_pipeline
from .batch import validate_project_beam_batch_v1
from .import_ledger import ImportFieldAction, ImportStatus
from .imports import parse_single_csv_lossless
from .project_beam import PROJECT_BEAM_SCHEMA_VERSION

CLI_DESIGN_INPUT_SCHEMA_VERSION = "cli-beam-design-input/v1"
CLI_DESIGN_OUTPUT_SCHEMA_VERSION = beam_pipeline.SCHEMA_VERSION


@dataclass(frozen=True)
class CLIDesignIssueV1:
    """Stable blocked-intake diagnostic."""

    code: str
    path: str
    message: str


class CLIDesignBlockedError(ValueError):
    """Raised before calculation when any CLI project input is unsafe."""

    def __init__(self, issues: list[CLIDesignIssueV1] | tuple[CLIDesignIssueV1, ...]):
        self.issues = tuple(issues)
        codes = ", ".join(sorted({issue.code for issue in self.issues}))
        super().__init__(f"CLI design input blocked: {codes or 'unknown input error'}")


@dataclass(frozen=True)
class CLIDesignRecordV1:
    """Complete CLI record plus the canonical strict calculation payload."""

    beam_id: str
    story: str
    b: float
    D: float
    d: float
    span: float
    cover: float
    fck: float
    fy: float
    Mu: float
    Vu: float
    stirrup_dia: float
    stirrup_spacing: float
    project_payload: dict[str, Any]


@dataclass(frozen=True)
class CLIDesignIntakeV1:
    """Accounted input records and immutable source identity."""

    source_sha256: str
    source_rows: int
    records: tuple[CLIDesignRecordV1, ...]


_ALIASES: dict[str, tuple[str, ...]] = {
    "member_id": ("member_id", "beam_id", "BeamID"),
    "story": ("story", "Story"),
    "b_mm": ("b_mm", "b", "b (mm)"),
    "D_mm": ("D_mm", "D", "D (mm)"),
    "d_mm": ("d_mm", "d", "d (mm)", "eff_d", "effective_depth_mm"),
    "span_mm": ("span_mm", "span", "Span", "Span (mm)"),
    "clear_cover_mm": ("clear_cover_mm", "cover_mm", "cover", "Cover"),
    "fck_nmm2": ("fck_nmm2", "fck", "Fck"),
    "fy_nmm2": ("fy_nmm2", "fy", "Fy"),
    "mu_knm": ("mu_knm", "Mu", "mu"),
    "vu_kn": ("vu_kn", "Vu", "vu"),
    "stirrup_diameter_mm": (
        "stirrup_diameter_mm",
        "stirrup_dia_mm",
        "stirrup_dia",
        "Stirrup_Dia",
    ),
    "stirrup_spacing_mm": (
        "stirrup_spacing_mm",
        "stirrup_spacing",
        "Stirrup_Spacing",
    ),
    "tension_bar_diameter_mm": (
        "tension_bar_diameter_mm",
        "main_bar_dia_mm",
        "bar_dia_mm",
    ),
}
_ALIAS_TO_FIELD = {
    alias: field for field, aliases in _ALIASES.items() for alias in aliases
}
_CSV_FIELD_MAP = {
    "beam_id": "member_id",
    "story": "story",
    "width_mm": "b_mm",
    "depth_mm": "D_mm",
    "eff_depth_mm": "d_mm",
    "span_mm": "span_mm",
    "cover_mm": "clear_cover_mm",
    "fck_mpa": "fck_nmm2",
    "fy_mpa": "fy_nmm2",
    "mu_knm": "mu_knm",
    "vu_kn": "vu_kn",
    "stirrup_diameter_mm": "stirrup_diameter_mm",
    "stirrup_spacing_mm": "stirrup_spacing_mm",
    "tension_bar_diameter_mm": "tension_bar_diameter_mm",
}
_REQUIRED_FIELDS = (
    "member_id",
    "story",
    "b_mm",
    "D_mm",
    "span_mm",
    "clear_cover_mm",
    "fck_nmm2",
    "fy_nmm2",
    "mu_knm",
    "vu_kn",
    "stirrup_diameter_mm",
    "stirrup_spacing_mm",
)
_NUMERIC_FIELDS = frozenset(_REQUIRED_FIELDS[2:]) | {
    "d_mm",
    "tension_bar_diameter_mm",
}


def _issue(code: str, path: str, message: str) -> CLIDesignIssueV1:
    return CLIDesignIssueV1(code=code, path=path, message=message)


def _normalize_json_record(
    raw: dict[str, Any], *, path: str
) -> tuple[dict[str, Any], list[CLIDesignIssueV1]]:
    normalized: dict[str, Any] = {}
    issues: list[CLIDesignIssueV1] = []
    for key, value in raw.items():
        canonical = _ALIAS_TO_FIELD.get(key)
        if canonical is None:
            issues.append(
                _issue(
                    "CLI_DESIGN_UNKNOWN_FIELD",
                    f"{path}.{key}",
                    "Field is not part of CLI beam design input v1.",
                )
            )
            continue
        if canonical in normalized:
            issues.append(
                _issue(
                    "CLI_DESIGN_ALIAS_CONFLICT",
                    f"{path}.{canonical}",
                    "Multiple aliases supplied one field; no precedence is applied.",
                )
            )
            continue
        normalized[canonical] = value
    return normalized, issues


def _finite_number(
    values: dict[str, Any],
    field: str,
    *,
    path: str,
    issues: list[CLIDesignIssueV1],
) -> float | None:
    value = values.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        issues.append(
            _issue(
                "CLI_DESIGN_INVALID_NUMBER",
                f"{path}.{field}",
                "Value must be a JSON/CSV number; numeric strings are not accepted in JSON.",
            )
        )
        return None
    number = float(value)
    if not math.isfinite(number):
        issues.append(
            _issue(
                "CLI_DESIGN_NON_FINITE",
                f"{path}.{field}",
                "Value must be finite.",
            )
        )
        return None
    return number


def _build_record(
    values: dict[str, Any],
    *,
    path: str,
    source_sha256: str,
    source_row_number: int,
) -> tuple[CLIDesignRecordV1 | None, list[CLIDesignIssueV1]]:
    issues: list[CLIDesignIssueV1] = []
    for field in _REQUIRED_FIELDS:
        if field not in values:
            issues.append(
                _issue(
                    "CLI_DESIGN_REQUIRED_FIELD",
                    f"{path}.{field}",
                    "Required CLI design value is missing.",
                )
            )

    member_id = values.get("member_id")
    story = values.get("story")
    for field, value in (("member_id", member_id), ("story", story)):
        if field in values and (not isinstance(value, str) or not value.strip()):
            issues.append(
                _issue(
                    "CLI_DESIGN_INVALID_IDENTITY",
                    f"{path}.{field}",
                    "Identity values must be non-blank strings.",
                )
            )

    numbers = {
        field: _finite_number(values, field, path=path, issues=issues)
        for field in _NUMERIC_FIELDS
        if field in values
    }
    for field in (
        "b_mm",
        "D_mm",
        "span_mm",
        "clear_cover_mm",
        "fck_nmm2",
        "fy_nmm2",
        "stirrup_diameter_mm",
        "stirrup_spacing_mm",
        "tension_bar_diameter_mm",
    ):
        number = numbers.get(field)
        if number is not None and number <= 0:
            issues.append(
                _issue(
                    "CLI_DESIGN_OUT_OF_RANGE",
                    f"{path}.{field}",
                    "Value must be greater than zero.",
                )
            )

    has_d = "d_mm" in values
    has_bar = "tension_bar_diameter_mm" in values
    if has_d and has_bar:
        issues.append(
            _issue(
                "CLI_DESIGN_CONFLICTING_DEPTH_BASIS",
                f"{path}.d_mm",
                "Supply explicit d_mm or a complete derivation basis, not both.",
            )
        )
    elif not has_d and not has_bar:
        issues.append(
            _issue(
                "CLI_DESIGN_REQUIRED_DEPTH_BASIS",
                f"{path}.d_mm",
                "Supply d_mm or tension_bar_diameter_mm with explicit cover and stirrup diameter.",
            )
        )

    if issues:
        return None, issues

    assert isinstance(member_id, str) and isinstance(story, str)
    b_mm = numbers["b_mm"]
    D_mm = numbers["D_mm"]
    span_mm = numbers["span_mm"]
    clear_cover_mm = numbers["clear_cover_mm"]
    fck_nmm2 = numbers["fck_nmm2"]
    fy_nmm2 = numbers["fy_nmm2"]
    mu_knm = numbers["mu_knm"]
    vu_kn = numbers["vu_kn"]
    stirrup_diameter_mm = numbers["stirrup_diameter_mm"]
    stirrup_spacing_mm = numbers["stirrup_spacing_mm"]
    assert b_mm is not None
    assert D_mm is not None
    assert span_mm is not None
    assert clear_cover_mm is not None
    assert fck_nmm2 is not None
    assert fy_nmm2 is not None
    assert mu_knm is not None
    assert vu_kn is not None
    assert stirrup_diameter_mm is not None
    assert stirrup_spacing_mm is not None
    project_payload: dict[str, Any] = {
        "schema_version": PROJECT_BEAM_SCHEMA_VERSION,
        "member_id": f"{story.strip()}/{member_id.strip()}",
        "b_mm": b_mm,
        "D_mm": D_mm,
        "mu_knm": mu_knm,
        "vu_kn": vu_kn,
        "fck_nmm2": fck_nmm2,
        "fy_nmm2": fy_nmm2,
        "source_metadata": {
            "input_artifact_sha256": source_sha256,
            "source_row_number": source_row_number,
        },
    }
    if has_d:
        project_payload["d_mm"] = numbers["d_mm"]
        resolved_d = numbers["d_mm"]
    else:
        tension_bar_diameter_mm = numbers["tension_bar_diameter_mm"]
        assert tension_bar_diameter_mm is not None
        project_payload["effective_depth_basis"] = {
            "clear_cover_mm": clear_cover_mm,
            "stirrup_diameter_mm": stirrup_diameter_mm,
            "tension_bar_diameter_mm": tension_bar_diameter_mm,
        }
        resolved_d = (
            D_mm - clear_cover_mm - stirrup_diameter_mm - tension_bar_diameter_mm / 2.0
        )
    assert resolved_d is not None
    return (
        CLIDesignRecordV1(
            beam_id=member_id.strip(),
            story=story.strip(),
            b=b_mm,
            D=D_mm,
            d=resolved_d,
            span=span_mm,
            cover=clear_cover_mm,
            fck=fck_nmm2,
            fy=fy_nmm2,
            Mu=mu_knm,
            Vu=vu_kn,
            stirrup_dia=stirrup_diameter_mm,
            stirrup_spacing=stirrup_spacing_mm,
            project_payload=project_payload,
        ),
        [],
    )


def _load_csv(path: Path, *, input_format: str) -> CLIDesignIntakeV1:
    result = parse_single_csv_lossless(path, format_hint=input_format)
    if result.status is ImportStatus.BLOCKED:
        raise CLIDesignBlockedError(
            [
                _issue(issue.code.value, issue.path, issue.message)
                for issue in result.issues
            ]
        )

    issues: list[CLIDesignIssueV1] = []
    records: list[CLIDesignRecordV1] = []
    source_sha256 = result.ledger.geometry_artifact.sha256
    for row in result.ledger.rows:
        values: dict[str, Any] = {}
        for field in row.fields:
            if field.canonical_field is None:
                issues.append(
                    _issue(
                        "CLI_DESIGN_UNKNOWN_FIELD",
                        f"rows[{row.source_row_number}].{field.raw_header}",
                        "Every CLI input field must belong to the versioned contract.",
                    )
                )
                continue
            cli_field = _CSV_FIELD_MAP.get(field.canonical_field)
            if cli_field is None:
                issues.append(
                    _issue(
                        "CLI_DESIGN_UNACCOUNTED_FIELD",
                        f"rows[{row.source_row_number}].{field.raw_header}",
                        "Recognized import field is not consumed by CLI design v1.",
                    )
                )
                continue
            if field.action is not ImportFieldAction.NORMALIZED:
                issues.append(
                    _issue(
                        "CLI_DESIGN_REJECTED_FIELD",
                        f"rows[{row.source_row_number}].{field.raw_header}",
                        "Field was not safely normalized.",
                    )
                )
                continue
            values[cli_field] = field.parsed_value
        record, record_issues = _build_record(
            values,
            path=f"rows[{row.source_row_number}]",
            source_sha256=source_sha256,
            source_row_number=row.source_row_number,
        )
        issues.extend(record_issues)
        if record is not None:
            records.append(record)
    if issues:
        raise CLIDesignBlockedError(issues)
    return CLIDesignIntakeV1(
        source_sha256=source_sha256,
        source_rows=result.ledger.totals.source_rows,
        records=tuple(records),
    )


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"Non-finite JSON number {value!r} is not accepted")


def _load_json(path: Path) -> CLIDesignIntakeV1:
    raw = path.read_bytes()
    duplicate_paths: list[str] = []

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                duplicate_paths.append(key)
            value[key] = item
        return value

    try:
        payload = json.loads(
            raw.decode("utf-8-sig"),
            object_pairs_hook=reject_duplicates,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise CLIDesignBlockedError(
            [_issue("CLI_DESIGN_MALFORMED_JSON", "$", str(exc))]
        ) from exc
    if duplicate_paths:
        raise CLIDesignBlockedError(
            [
                _issue(
                    "CLI_DESIGN_DUPLICATE_JSON_KEY",
                    key,
                    "Duplicate JSON keys are not accepted.",
                )
                for key in duplicate_paths
            ]
        )
    if not isinstance(payload, dict):
        raise CLIDesignBlockedError(
            [_issue("CLI_DESIGN_INVALID_ENVELOPE", "$", "Expected a JSON object.")]
        )
    unknown_top = sorted(set(payload) - {"schema_version", "beams"})
    issues = [
        _issue(
            "CLI_DESIGN_UNKNOWN_FIELD",
            key,
            "Top-level field is not part of CLI beam design input v1.",
        )
        for key in unknown_top
    ]
    if payload.get("schema_version") != CLI_DESIGN_INPUT_SCHEMA_VERSION:
        issues.append(
            _issue(
                "CLI_DESIGN_UNSUPPORTED_SCHEMA_VERSION",
                "schema_version",
                f"Expected {CLI_DESIGN_INPUT_SCHEMA_VERSION!r}.",
            )
        )
    rows = payload.get("beams")
    if not isinstance(rows, list) or not rows:
        issues.append(
            _issue(
                "CLI_DESIGN_EMPTY_PROJECT",
                "beams",
                "A non-empty beams array is required.",
            )
        )
        rows = []

    source_sha256 = hashlib.sha256(raw).hexdigest()
    records: list[CLIDesignRecordV1] = []
    for index, raw_record in enumerate(rows):
        path_label = f"beams[{index}]"
        if not isinstance(raw_record, dict):
            issues.append(
                _issue(
                    "CLI_DESIGN_INVALID_RECORD",
                    path_label,
                    "Each beam record must be an object.",
                )
            )
            continue
        values, normalization_issues = _normalize_json_record(
            raw_record, path=path_label
        )
        issues.extend(normalization_issues)
        record, record_issues = _build_record(
            values,
            path=path_label,
            source_sha256=source_sha256,
            source_row_number=index + 1,
        )
        issues.extend(record_issues)
        if record is not None:
            records.append(record)
    if issues:
        raise CLIDesignBlockedError(issues)
    return CLIDesignIntakeV1(
        source_sha256=source_sha256,
        source_rows=len(rows),
        records=tuple(records),
    )


def load_cli_design_input_v1(
    path: Path | str, *, input_format: str = "generic"
) -> CLIDesignIntakeV1:
    """Load every source record without defaults, row loss, or field loss."""

    input_path = Path(path)
    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        return _load_csv(input_path, input_format=input_format)
    if suffix == ".json":
        return _load_json(input_path)
    raise CLIDesignBlockedError(
        [
            _issue(
                "CLI_DESIGN_UNSUPPORTED_FORMAT",
                "input",
                f"Unsupported input extension {suffix!r}; expected .csv or .json.",
            )
        ]
    )


def design_cli_project_v1(
    records: tuple[CLIDesignRecordV1, ...],
    *,
    include_deflection: bool = False,
    support_condition: str = "simply_supported",
    crack_width_params: CrackWidthParams | None = None,
) -> beam_pipeline.MultiBeamOutput:
    """Validate the whole project, then calculate into the retained beams envelope."""

    validations = validate_project_beam_batch_v1(
        [record.project_payload for record in records]
    )
    blocked_issues: list[CLIDesignIssueV1] = []
    for index, validation in enumerate(validations):
        for issue in validation.issues:
            blocked_issues.append(
                _issue(issue.code, f"beams[{index}].{issue.path}", issue.message)
            )
    if blocked_issues:
        raise CLIDesignBlockedError(blocked_issues)

    results: list[beam_pipeline.BeamDesignOutput] = []
    for record, validation in zip(records, validations, strict=True):
        assert validation.value is not None
        deflection_params = None
        if include_deflection:
            deflection_params = DeflectionParams(
                span_mm=record.span,
                d_mm=validation.value.resolved_d_mm,
                support_condition=support_condition,
            )
        asv_mm2 = 3.14159 * (record.stirrup_dia / 2.0) ** 2 * 2.0
        results.append(
            beam_pipeline.design_single_beam(
                units="IS456",
                beam_id=record.beam_id,
                story=record.story,
                b_mm=validation.value.b_mm,
                D_mm=validation.value.D_mm,
                d_mm=validation.value.resolved_d_mm,
                span_mm=record.span,
                cover_mm=record.cover,
                fck_nmm2=validation.value.fck_nmm2,
                fy_nmm2=validation.value.fy_nmm2,
                mu_knm=validation.value.mu_knm,
                vu_kn=validation.value.vu_kn,
                case_id=f"{record.story}_{record.beam_id}",
                d_dash_mm=record.cover,
                asv_mm2=asv_mm2,
                include_detailing=True,
                stirrup_dia_mm=record.stirrup_dia,
                stirrup_spacing_start_mm=record.stirrup_spacing,
                stirrup_spacing_mid_mm=record.stirrup_spacing * 1.33,
                stirrup_spacing_end_mm=record.stirrup_spacing,
                deflection_params=deflection_params,
                crack_width_params=crack_width_params,
            )
        )
    return beam_pipeline.MultiBeamOutput(
        schema_version=CLI_DESIGN_OUTPUT_SCHEMA_VERSION,
        code="IS456",
        units="IS456",
        beams=results,
        summary={
            "total_beams": len(results),
            "passed": sum(1 for result in results if result.is_ok),
            "failed": sum(1 for result in results if not result.is_ok),
        },
    )


__all__ = [
    "CLI_DESIGN_INPUT_SCHEMA_VERSION",
    "CLI_DESIGN_OUTPUT_SCHEMA_VERSION",
    "CLIDesignBlockedError",
    "CLIDesignIntakeV1",
    "CLIDesignIssueV1",
    "CLIDesignRecordV1",
    "design_cli_project_v1",
    "load_cli_design_input_v1",
]
