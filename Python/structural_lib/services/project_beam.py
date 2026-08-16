# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Versioned, fail-closed project beam input and result contracts."""

from __future__ import annotations

import math
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real
from typing import Any

__all__ = [
    "PROJECT_BEAM_RESULT_SCHEMA_VERSION",
    "PROJECT_BEAM_SCHEMA_VERSION",
    "EffectiveDepthBasisV1",
    "ProjectBeamBatchResultV1",
    "ProjectBeamBatchSummaryV1",
    "ProjectBeamCalculationStatus",
    "ProjectBeamDesignInputV1",
    "ProjectBeamEngineeringStatus",
    "ProjectBeamInputIssueV1",
    "ProjectBeamInputValidationV1",
    "ProjectBeamIntakeStatus",
    "ProjectBeamMemberResultV1",
    "ProjectBeamOverallStatus",
    "validate_project_beam_design_input_v1",
]


PROJECT_BEAM_SCHEMA_VERSION = "project-beam-design/v1"
PROJECT_BEAM_RESULT_SCHEMA_VERSION = "project-beam-result/v1"
QUALIFIED_REVIEW_REQUIRED = "QUALIFIED_REVIEW_REQUIRED"


class ProjectBeamIntakeStatus(StrEnum):
    """Whether the complete project member input is accepted."""

    VALID = "VALID"
    BLOCKED = "BLOCKED"


class ProjectBeamCalculationStatus(StrEnum):
    """Whether calculation was attempted and completed."""

    NOT_EVALUATED = "NOT_EVALUATED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class ProjectBeamEngineeringStatus(StrEnum):
    """Engineering disposition of completed supported checks."""

    NOT_EVALUATED = "NOT_EVALUATED"
    PASS = "PASS"  # nosec B105 - engineering disposition, not a credential
    FAIL = "FAIL"
    HOLD = "HOLD"


class ProjectBeamOverallStatus(StrEnum):
    """Deterministic aggregate without professional-approval meaning."""

    BLOCKED = "BLOCKED"
    PASS = "PASS"  # nosec B105 - engineering disposition, not a credential
    FAIL = "FAIL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class EffectiveDepthBasisV1:
    """Complete, auditable basis for deriving beam effective depth."""

    clear_cover_mm: float
    stirrup_diameter_mm: float
    tension_bar_diameter_mm: float

    def derive_d_mm(self, D_mm: float) -> float:
        """Return ``D - cover - stirrup diameter - main-bar radius``."""

        return (
            D_mm
            - self.clear_cover_mm
            - self.stirrup_diameter_mm
            - self.tension_bar_diameter_mm / 2.0
        )

    def to_dict(self) -> dict[str, float]:
        return {
            "clear_cover_mm": self.clear_cover_mm,
            "stirrup_diameter_mm": self.stirrup_diameter_mm,
            "tension_bar_diameter_mm": self.tension_bar_diameter_mm,
        }


@dataclass(frozen=True)
class ProjectBeamDesignInputV1:
    """Canonical calculation-bearing project input with explicit units."""

    schema_version: str
    member_id: str
    b_mm: float
    D_mm: float
    mu_knm: float
    vu_kn: float
    fck_nmm2: float
    fy_nmm2: float
    d_mm: float | None = None
    effective_depth_basis: EffectiveDepthBasisV1 | None = None
    source_metadata: Mapping[str, Any] | None = None

    @property
    def resolved_d_mm(self) -> float:
        """Return the explicit or completely derived effective depth."""

        if self.d_mm is not None:
            return self.d_mm
        if self.effective_depth_basis is None:  # pragma: no cover - validator invariant
            raise ValueError("effective depth is unavailable")
        return self.effective_depth_basis.derive_d_mm(self.D_mm)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "schema_version": self.schema_version,
            "member_id": self.member_id,
            "b_mm": self.b_mm,
            "D_mm": self.D_mm,
            "mu_knm": self.mu_knm,
            "vu_kn": self.vu_kn,
            "fck_nmm2": self.fck_nmm2,
            "fy_nmm2": self.fy_nmm2,
        }
        if self.d_mm is not None:
            data["d_mm"] = self.d_mm
        elif self.effective_depth_basis is not None:
            data["effective_depth_basis"] = self.effective_depth_basis.to_dict()
        if self.source_metadata is not None:
            data["source_metadata"] = deepcopy(dict(self.source_metadata))
        return data


@dataclass(frozen=True)
class ProjectBeamInputIssueV1:
    """Stable machine issue plus a human-readable explanation."""

    code: str
    path: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass(frozen=True)
class ProjectBeamInputValidationV1:
    """Fail-closed parse result; ``value`` exists only without issues."""

    value: ProjectBeamDesignInputV1 | None
    issues: tuple[ProjectBeamInputIssueV1, ...]
    member_id_hint: str | None = None

    @property
    def is_valid(self) -> bool:
        return self.value is not None and not self.issues


@dataclass(frozen=True)
class ProjectBeamMemberResultV1:
    """One member's orthogonal intake, calculation, and engineering state."""

    index: int
    member_id: str | None
    intake_status: ProjectBeamIntakeStatus
    calculation_status: ProjectBeamCalculationStatus
    engineering_status: ProjectBeamEngineeringStatus
    overall_status: ProjectBeamOverallStatus
    issues: tuple[ProjectBeamInputIssueV1, ...] = ()
    input: ProjectBeamDesignInputV1 | None = None
    calculation: Mapping[str, Any] | None = None
    review_status: str = QUALIFIED_REVIEW_REQUIRED

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": PROJECT_BEAM_RESULT_SCHEMA_VERSION,
            "index": self.index,
            "member_id": self.member_id,
            "intake_status": self.intake_status.value,
            "calculation_status": self.calculation_status.value,
            "engineering_status": self.engineering_status.value,
            "review_status": self.review_status,
            "overall_status": self.overall_status.value,
            "qualified_review_required": True,
            "issues": [issue.to_dict() for issue in self.issues],
            "input": self.input.to_dict() if self.input is not None else None,
            "calculation": (
                deepcopy(dict(self.calculation))
                if self.calculation is not None
                else None
            ),
        }


@dataclass(frozen=True)
class ProjectBeamBatchSummaryV1:
    """Accounted service summary; zero evaluated members can never PASS."""

    total: int
    valid: int
    blocked: int
    evaluated: int
    passed: int
    failed: int
    held: int
    intake_status: ProjectBeamIntakeStatus
    calculation_status: ProjectBeamCalculationStatus
    engineering_status: ProjectBeamEngineeringStatus
    overall_status: ProjectBeamOverallStatus

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "valid": self.valid,
            "blocked": self.blocked,
            "evaluated": self.evaluated,
            "passed": self.passed,
            "failed": self.failed,
            "held": self.held,
            "intake_status": self.intake_status.value,
            "calculation_status": self.calculation_status.value,
            "engineering_status": self.engineering_status.value,
            "overall_status": self.overall_status.value,
            "qualified_review_required": True,
        }


@dataclass(frozen=True)
class ProjectBeamBatchResultV1:
    """Versioned strict project batch result."""

    members: tuple[ProjectBeamMemberResultV1, ...]
    summary: ProjectBeamBatchSummaryV1

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": PROJECT_BEAM_RESULT_SCHEMA_VERSION,
            "members": [member.to_dict() for member in self.members],
            "summary": self.summary.to_dict(),
        }


_TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "member_id",
        "b_mm",
        "D_mm",
        "d_mm",
        "effective_depth_basis",
        "mu_knm",
        "vu_kn",
        "fck_nmm2",
        "fy_nmm2",
        "source_metadata",
    }
)
_REQUIRED_FIELDS = (
    "schema_version",
    "member_id",
    "b_mm",
    "D_mm",
    "mu_knm",
    "vu_kn",
    "fck_nmm2",
    "fy_nmm2",
)
_DEPTH_BASIS_FIELDS = (
    "clear_cover_mm",
    "stirrup_diameter_mm",
    "tension_bar_diameter_mm",
)


def _issue(code: str, path: str, message: str) -> ProjectBeamInputIssueV1:
    return ProjectBeamInputIssueV1(code=code, path=path, message=message)


def _finite_number(
    values: Mapping[str, Any],
    field: str,
    issues: list[ProjectBeamInputIssueV1],
    *,
    path: str | None = None,
) -> float | None:
    value = values.get(field)
    issue_path = path or field
    if isinstance(value, bool) or not isinstance(value, Real):
        issues.append(
            _issue(
                "PROJECT_BEAM_INVALID_NUMBER",
                issue_path,
                "Value must be a JSON number; numeric strings are not accepted.",
            )
        )
        return None
    number = float(value)
    if not math.isfinite(number):
        issues.append(
            _issue(
                "PROJECT_BEAM_NON_FINITE",
                issue_path,
                "Value must be finite.",
            )
        )
        return None
    return number


def _range_issue(
    issues: list[ProjectBeamInputIssueV1],
    path: str,
    message: str,
    *,
    code: str = "PROJECT_BEAM_OUT_OF_RANGE",
) -> None:
    issues.append(_issue(code, path, message))


def _parse_effective_depth_basis(
    value: object,
    issues: list[ProjectBeamInputIssueV1],
) -> EffectiveDepthBasisV1 | None:
    if not isinstance(value, Mapping):
        issues.append(
            _issue(
                "PROJECT_BEAM_INVALID_OBJECT",
                "effective_depth_basis",
                "Effective-depth basis must be an object.",
            )
        )
        return None
    values = dict(value)
    for key in sorted(values, key=str):
        if not isinstance(key, str) or key not in _DEPTH_BASIS_FIELDS:
            issues.append(
                _issue(
                    "PROJECT_BEAM_UNKNOWN_FIELD",
                    f"effective_depth_basis.{key}",
                    "Field is not part of effective-depth basis v1.",
                )
            )
    for field in _DEPTH_BASIS_FIELDS:
        if field not in values:
            issues.append(
                _issue(
                    "PROJECT_BEAM_REQUIRED_FIELD",
                    f"effective_depth_basis.{field}",
                    "Required effective-depth value is missing.",
                )
            )
    if any(field not in values for field in _DEPTH_BASIS_FIELDS):
        return None
    numbers = {
        field: _finite_number(
            values,
            field,
            issues,
            path=f"effective_depth_basis.{field}",
        )
        for field in _DEPTH_BASIS_FIELDS
    }
    if any(value is None for value in numbers.values()):
        return None
    for field, number in numbers.items():
        if number is not None and number <= 0:
            _range_issue(
                issues,
                f"effective_depth_basis.{field}",
                "Effective-depth basis values must be positive.",
            )
    if any(number is not None and number <= 0 for number in numbers.values()):
        return None
    return EffectiveDepthBasisV1(
        clear_cover_mm=numbers["clear_cover_mm"],  # type: ignore[arg-type]
        stirrup_diameter_mm=numbers["stirrup_diameter_mm"],  # type: ignore[arg-type]
        tension_bar_diameter_mm=numbers["tension_bar_diameter_mm"],  # type: ignore[arg-type]
    )


def validate_project_beam_design_input_v1(
    payload: Mapping[str, Any] | ProjectBeamDesignInputV1,
) -> ProjectBeamInputValidationV1:
    """Validate one canonical project member without coercion or defaults."""

    if isinstance(payload, ProjectBeamDesignInputV1):
        values = payload.to_dict()
    elif isinstance(payload, Mapping):
        values = dict(payload)
    else:
        return ProjectBeamInputValidationV1(
            value=None,
            issues=(
                _issue(
                    "PROJECT_BEAM_INVALID_OBJECT",
                    "$",
                    "Project beam input must be an object.",
                ),
            ),
        )

    issues: list[ProjectBeamInputIssueV1] = []
    for key in sorted(values, key=str):
        if not isinstance(key, str) or key not in _TOP_LEVEL_FIELDS:
            issues.append(
                _issue(
                    "PROJECT_BEAM_UNKNOWN_FIELD",
                    str(key),
                    "Field is not part of project beam input v1.",
                )
            )
    for field in _REQUIRED_FIELDS:
        if field not in values:
            issues.append(
                _issue(
                    "PROJECT_BEAM_REQUIRED_FIELD",
                    field,
                    "Required project beam value is missing.",
                )
            )

    member_id_hint = (
        values.get("member_id")
        if isinstance(values.get("member_id"), str)
        and bool(values.get("member_id", "").strip())
        else None
    )
    schema_version = values.get("schema_version")
    if "schema_version" in values and schema_version != PROJECT_BEAM_SCHEMA_VERSION:
        issues.append(
            _issue(
                "PROJECT_BEAM_UNSUPPORTED_SCHEMA_VERSION",
                "schema_version",
                f"Expected {PROJECT_BEAM_SCHEMA_VERSION!r}.",
            )
        )
    member_id = values.get("member_id")
    if "member_id" in values and (
        not isinstance(member_id, str) or not member_id.strip()
    ):
        issues.append(
            _issue(
                "PROJECT_BEAM_INVALID_MEMBER_ID",
                "member_id",
                "Member identity must be a non-blank string.",
            )
        )

    numeric_fields = (
        "b_mm",
        "D_mm",
        "mu_knm",
        "vu_kn",
        "fck_nmm2",
        "fy_nmm2",
    )
    numbers = {
        field: _finite_number(values, field, issues)
        for field in numeric_fields
        if field in values
    }
    b_mm = numbers.get("b_mm")
    D_mm = numbers.get("D_mm")
    mu_knm = numbers.get("mu_knm")
    vu_kn = numbers.get("vu_kn")
    fck_nmm2 = numbers.get("fck_nmm2")
    fy_nmm2 = numbers.get("fy_nmm2")
    for field, number in (("b_mm", b_mm), ("D_mm", D_mm)):
        if number is not None and not 0 < number <= 5000:
            _range_issue(issues, field, "Section dimension must be > 0 and <= 5000 mm.")
    for field, number in (("mu_knm", mu_knm), ("vu_kn", vu_kn)):
        if number is not None and number < 0:
            _range_issue(
                issues, field, "Design action must be greater than or equal to zero."
            )
    if fck_nmm2 is not None and not 0 < fck_nmm2 <= 120:
        _range_issue(
            issues,
            "fck_nmm2",
            "Concrete strength must be > 0 and <= 120 N/mm2.",
        )
    if fy_nmm2 is not None and not 0 < fy_nmm2 <= 700:
        _range_issue(
            issues,
            "fy_nmm2",
            "Steel strength must be > 0 and <= 700 N/mm2.",
        )

    has_d = "d_mm" in values
    has_basis = "effective_depth_basis" in values
    d_mm: float | None = None
    depth_basis: EffectiveDepthBasisV1 | None = None
    if has_d and has_basis:
        issues.append(
            _issue(
                "PROJECT_BEAM_DEPTH_CONFLICT",
                "effective_depth_basis",
                "Supply d_mm or effective_depth_basis, not both.",
            )
        )
    elif not has_d and not has_basis:
        issues.append(
            _issue(
                "PROJECT_BEAM_REQUIRED_FIELD",
                "d_mm",
                "Supply d_mm or a complete effective_depth_basis.",
            )
        )
    elif has_d:
        d_mm = _finite_number(values, "d_mm", issues)
    else:
        depth_basis = _parse_effective_depth_basis(
            values.get("effective_depth_basis"), issues
        )

    resolved_d_mm = d_mm
    if resolved_d_mm is None and depth_basis is not None and D_mm is not None:
        resolved_d_mm = depth_basis.derive_d_mm(D_mm)
        if not math.isfinite(resolved_d_mm):
            issues.append(
                _issue(
                    "PROJECT_BEAM_NON_FINITE",
                    "effective_depth_basis",
                    "Derived effective depth must be finite.",
                )
            )
            resolved_d_mm = None
    if resolved_d_mm is not None and D_mm is not None:
        if not 0 < resolved_d_mm < D_mm or resolved_d_mm > 5000:
            _range_issue(
                issues,
                "d_mm" if has_d else "effective_depth_basis",
                "Effective depth must be > 0, <= 5000 mm, and less than D_mm.",
                code="PROJECT_BEAM_DEPTH_OUT_OF_RANGE",
            )

    source_metadata: Mapping[str, Any] | None = None
    if "source_metadata" in values:
        raw_metadata = values.get("source_metadata")
        if not isinstance(raw_metadata, Mapping):
            issues.append(
                _issue(
                    "PROJECT_BEAM_INVALID_SOURCE_METADATA",
                    "source_metadata",
                    "Source metadata must be a namespaced object.",
                )
            )
        elif any(not isinstance(key, str) or not key.strip() for key in raw_metadata):
            issues.append(
                _issue(
                    "PROJECT_BEAM_INVALID_SOURCE_METADATA",
                    "source_metadata",
                    "Source metadata namespace keys must be non-blank strings.",
                )
            )
        else:
            source_metadata = deepcopy(dict(raw_metadata))

    if issues:
        return ProjectBeamInputValidationV1(
            value=None,
            issues=tuple(issues),
            member_id_hint=member_id_hint,
        )

    return ProjectBeamInputValidationV1(
        value=ProjectBeamDesignInputV1(
            schema_version=PROJECT_BEAM_SCHEMA_VERSION,
            member_id=member_id.strip(),  # type: ignore[union-attr]
            b_mm=b_mm,  # type: ignore[arg-type]
            D_mm=D_mm,  # type: ignore[arg-type]
            d_mm=d_mm,
            effective_depth_basis=depth_basis,
            mu_knm=mu_knm,  # type: ignore[arg-type]
            vu_kn=vu_kn,  # type: ignore[arg-type]
            fck_nmm2=fck_nmm2,  # type: ignore[arg-type]
            fy_nmm2=fy_nmm2,  # type: ignore[arg-type]
            source_metadata=source_metadata,
        ),
        issues=(),
        member_id_hint=member_id.strip(),  # type: ignore[union-attr]
    )
