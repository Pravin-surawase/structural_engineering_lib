# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Strict project beam design plus a delegating legacy batch surface."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from copy import deepcopy
from typing import Any

from . import api
from .evidence import build_beam_evidence_envelope
from .project_beam import (
    PROJECT_BEAM_SCHEMA_VERSION,
    ProjectBeamBatchResultV1,
    ProjectBeamBatchSummaryV1,
    ProjectBeamCalculationStatus,
    ProjectBeamDesignInputV1,
    ProjectBeamEngineeringStatus,
    ProjectBeamInputIssueV1,
    ProjectBeamInputValidationV1,
    ProjectBeamIntakeStatus,
    ProjectBeamMemberResultV1,
    ProjectBeamOverallStatus,
    validate_project_beam_design_input_v1,
)

__all__ = [
    "design_beams",
    "design_beams_iter",
    "design_project_beams_iter_v1",
    "design_project_beams_v1",
    "validate_project_beam_batch_v1",
]


_LEGACY_ALIAS_GROUPS: dict[str, tuple[str, ...]] = {
    "member_id": ("member_id", "id", "beam_id", "beamId"),
    "b_mm": ("b_mm", "width", "width_mm", "b"),
    "D_mm": ("D_mm", "depth", "depth_mm", "D"),
    "d_mm": ("d_mm", "d", "effective_depth_mm"),
    "mu_knm": ("mu_knm", "moment", "Mu"),
    "vu_kn": ("vu_kn", "shear", "Vu"),
    "fck_nmm2": ("fck_nmm2", "fck", "fck_mpa"),
    "fy_nmm2": ("fy_nmm2", "fy", "fy_mpa"),
}
_LEGACY_DEPTH_COMPONENTS: dict[str, tuple[str, ...]] = {
    "clear_cover_mm": ("clear_cover_mm", "cover_mm", "cover"),
    "stirrup_diameter_mm": (
        "stirrup_diameter_mm",
        "stirrup_dia_mm",
    ),
    "tension_bar_diameter_mm": (
        "tension_bar_diameter_mm",
        "bar_dia_mm",
        "main_bar_dia_mm",
    ),
}
_LEGACY_DIRECT_FIELDS = frozenset(
    {
        "schema_version",
        "effective_depth_basis",
        "source_metadata",
    }
)
_LEGACY_KNOWN_FIELDS = (
    frozenset(
        field
        for fields in (
            *_LEGACY_ALIAS_GROUPS.values(),
            *_LEGACY_DEPTH_COMPONENTS.values(),
        )
        for field in fields
    )
    | _LEGACY_DIRECT_FIELDS
)


def _issue(code: str, path: str, message: str) -> ProjectBeamInputIssueV1:
    return ProjectBeamInputIssueV1(code=code, path=path, message=message)


def _coerce_params(beam: Any) -> dict[str, Any]:
    if isinstance(beam, ProjectBeamDesignInputV1):
        return beam.to_dict()
    if isinstance(beam, Mapping):
        return dict(beam)
    if hasattr(beam, "model_dump"):
        dumped = beam.model_dump()
        if isinstance(dumped, Mapping):
            return dict(dumped)
    if hasattr(beam, "dict"):
        dumped = beam.dict()
        if isinstance(dumped, Mapping):
            return dict(dumped)
    try:
        return dict(vars(beam))
    except (TypeError, ValueError):
        return {}


def _alias_value(
    params: Mapping[str, Any],
    canonical_field: str,
    aliases: tuple[str, ...],
    issues: list[ProjectBeamInputIssueV1],
) -> tuple[bool, Any]:
    present = [(alias, params[alias]) for alias in aliases if alias in params]
    if not present:
        return False, None
    first_value = present[0][1]
    if any(value != first_value for _, value in present[1:]):
        issues.append(
            _issue(
                "PROJECT_BEAM_ALIAS_CONFLICT",
                canonical_field,
                "Conflicting compatibility aliases were supplied; no precedence is applied.",
            )
        )
    return True, first_value


def _normalize_legacy_beam(
    beam: Any,
) -> tuple[dict[str, Any], tuple[ProjectBeamInputIssueV1, ...]]:
    """Map known aliases without filling any calculation-bearing value."""

    params = _coerce_params(beam)
    issues: list[ProjectBeamInputIssueV1] = []
    canonical: dict[str, Any] = {
        "schema_version": params.get("schema_version", PROJECT_BEAM_SCHEMA_VERSION)
    }
    for canonical_field, aliases in _LEGACY_ALIAS_GROUPS.items():
        present, value = _alias_value(params, canonical_field, aliases, issues)
        if present:
            canonical[canonical_field] = value

    if "source_metadata" in params:
        canonical["source_metadata"] = params["source_metadata"]
    if "effective_depth_basis" in params:
        canonical["effective_depth_basis"] = params["effective_depth_basis"]

    depth_components: dict[str, Any] = {}
    for canonical_field, aliases in _LEGACY_DEPTH_COMPONENTS.items():
        present, value = _alias_value(params, canonical_field, aliases, issues)
        if present:
            depth_components[canonical_field] = value
    if depth_components:
        if "effective_depth_basis" in canonical:
            issues.append(
                _issue(
                    "PROJECT_BEAM_ALIAS_CONFLICT",
                    "effective_depth_basis",
                    "Supply one effective-depth basis representation.",
                )
            )
        else:
            canonical["effective_depth_basis"] = depth_components

    for key in params:
        if key not in _LEGACY_KNOWN_FIELDS:
            canonical[key] = params[key]
    return canonical, tuple(issues)


def _with_issues(
    validation: ProjectBeamInputValidationV1,
    additional: tuple[ProjectBeamInputIssueV1, ...],
) -> ProjectBeamInputValidationV1:
    if not additional:
        return validation
    return ProjectBeamInputValidationV1(
        value=None,
        issues=validation.issues + additional,
        member_id_hint=(
            validation.value.member_id
            if validation.value is not None
            else validation.member_id_hint
        ),
    )


def _validate_batch(
    payloads: Sequence[Mapping[str, Any] | ProjectBeamDesignInputV1],
    additional_issues: Sequence[tuple[ProjectBeamInputIssueV1, ...]] | None = None,
) -> list[ProjectBeamInputValidationV1]:
    validations = [
        validate_project_beam_design_input_v1(payload) for payload in payloads
    ]
    if additional_issues is not None:
        validations = [
            _with_issues(validation, extra)
            for validation, extra in zip(validations, additional_issues, strict=True)
        ]

    member_ids = [
        (
            validation.value.member_id
            if validation.value is not None
            else validation.member_id_hint
        )
        for validation in validations
    ]
    counts = Counter(member_id for member_id in member_ids if member_id is not None)
    duplicate_ids = {member_id for member_id, count in counts.items() if count > 1}
    if not duplicate_ids:
        return validations

    duplicate_issue = {
        member_id: _issue(
            "PROJECT_BEAM_DUPLICATE_MEMBER_ID",
            "member_id",
            f"Member identity {member_id!r} occurs more than once in the batch.",
        )
        for member_id in duplicate_ids
    }
    blocked: list[ProjectBeamInputValidationV1] = []
    for validation, member_id in zip(validations, member_ids, strict=True):
        if member_id not in duplicate_ids:
            blocked.append(validation)
            continue
        assert member_id is not None  # narrowed by membership in set[str]
        blocked.append(
            ProjectBeamInputValidationV1(
                value=None,
                issues=validation.issues + (duplicate_issue[member_id],),
                member_id_hint=member_id,
            )
        )
    return blocked


def _calculation_payload(
    beam: ProjectBeamDesignInputV1,
    *,
    units: str,
) -> dict[str, Any]:
    d_mm = beam.resolved_d_mm
    result = api.design_beam_is456(
        units=units,
        case_id=beam.member_id,
        b_mm=beam.b_mm,
        D_mm=beam.D_mm,
        d_mm=d_mm,
        mu_knm=beam.mu_knm,
        vu_kn=beam.vu_kn,
        fck_nmm2=beam.fck_nmm2,
        fy_nmm2=beam.fy_nmm2,
    )
    evidence = build_beam_evidence_envelope(
        inputs={
            "units": units,
            "case_id": beam.member_id,
            "mu_knm": beam.mu_knm,
            "vu_kn": beam.vu_kn,
            "b_mm": beam.b_mm,
            "D_mm": beam.D_mm,
            "d_mm": d_mm,
            "fck_nmm2": beam.fck_nmm2,
            "fy_nmm2": beam.fy_nmm2,
            "d_dash_mm": 50.0,
            "asv_mm2": 100.0,
        },
        is_ok=result.is_ok,
        governing_utilization=result.governing_utilization,
        utilizations=result.utilizations,
        source_metadata=beam.source_metadata,
    )
    is_safe = result.is_ok
    return {
        "design_succeeded": True,
        "is_safe": is_safe,
        "status": "PASS" if is_safe else "FAIL",
        "flexure": {
            "ast_required": result.flexure.Ast_required,
            "asc_required": result.flexure.Asc_required,
            "mu_lim": result.flexure.Mu_lim,
            "xu": result.flexure.xu,
            "is_safe": result.flexure.is_safe,
        },
        "shear": (
            {
                "tau_v": result.shear.tau_v,
                "tau_c": result.shear.tau_c,
                "tau_c_max": result.shear.tau_c_max,
                "vus": result.shear.Vus,
                "stirrup_spacing": result.shear.spacing,
                "is_safe": result.shear.is_safe,
            }
            if result.shear
            else None
        ),
        "utilization_ratio": result.governing_utilization,
        "utilizations": dict(result.utilizations),
        "failed_checks": list(result.failed_checks),
        "remarks": result.remarks,
        "evidence": evidence,
    }


def _blocked_member(
    validation: ProjectBeamInputValidationV1,
    index: int,
) -> ProjectBeamMemberResultV1:
    return ProjectBeamMemberResultV1(
        index=index,
        member_id=validation.member_id_hint,
        intake_status=ProjectBeamIntakeStatus.BLOCKED,
        calculation_status=ProjectBeamCalculationStatus.NOT_EVALUATED,
        engineering_status=ProjectBeamEngineeringStatus.NOT_EVALUATED,
        overall_status=ProjectBeamOverallStatus.BLOCKED,
        issues=validation.issues,
    )


def _calculated_member(
    beam: ProjectBeamDesignInputV1,
    index: int,
    *,
    units: str,
) -> ProjectBeamMemberResultV1:
    try:
        calculation = _calculation_payload(beam, units=units)
    except Exception:  # Public result deliberately excludes raw exception text.
        issue = _issue(
            "PROJECT_BEAM_CALCULATION_ERROR",
            "$",
            "Calculation could not be completed for the validated member.",
        )
        return ProjectBeamMemberResultV1(
            index=index,
            member_id=beam.member_id,
            input=beam,
            intake_status=ProjectBeamIntakeStatus.VALID,
            calculation_status=ProjectBeamCalculationStatus.ERROR,
            engineering_status=ProjectBeamEngineeringStatus.HOLD,
            overall_status=ProjectBeamOverallStatus.HOLD,
            issues=(issue,),
        )

    engineering_status = (
        ProjectBeamEngineeringStatus.PASS
        if calculation["is_safe"]
        else ProjectBeamEngineeringStatus.FAIL
    )
    overall_status = (
        ProjectBeamOverallStatus.PASS
        if calculation["is_safe"]
        else ProjectBeamOverallStatus.FAIL
    )
    return ProjectBeamMemberResultV1(
        index=index,
        member_id=beam.member_id,
        input=beam,
        intake_status=ProjectBeamIntakeStatus.VALID,
        calculation_status=ProjectBeamCalculationStatus.COMPLETED,
        engineering_status=engineering_status,
        overall_status=overall_status,
        calculation=calculation,
    )


def _summarize(
    members: tuple[ProjectBeamMemberResultV1, ...],
) -> ProjectBeamBatchSummaryV1:
    total = len(members)
    valid = sum(
        member.intake_status is ProjectBeamIntakeStatus.VALID for member in members
    )
    blocked = total - valid
    evaluated = sum(
        member.calculation_status is ProjectBeamCalculationStatus.COMPLETED
        for member in members
    )
    calculation_errors = sum(
        member.calculation_status is ProjectBeamCalculationStatus.ERROR
        for member in members
    )
    passed = sum(
        member.engineering_status is ProjectBeamEngineeringStatus.PASS
        for member in members
    )
    failed = sum(
        member.engineering_status is ProjectBeamEngineeringStatus.FAIL
        for member in members
    )
    held = sum(
        member.engineering_status is ProjectBeamEngineeringStatus.HOLD
        for member in members
    )
    intake_status = (
        ProjectBeamIntakeStatus.VALID
        if total > 0 and blocked == 0
        else ProjectBeamIntakeStatus.BLOCKED
    )
    if calculation_errors:
        calculation_status = ProjectBeamCalculationStatus.ERROR
    elif evaluated:
        calculation_status = ProjectBeamCalculationStatus.COMPLETED
    else:
        calculation_status = ProjectBeamCalculationStatus.NOT_EVALUATED
    if evaluated == 0:
        engineering_status = (
            ProjectBeamEngineeringStatus.HOLD
            if held
            else ProjectBeamEngineeringStatus.NOT_EVALUATED
        )
    elif failed:
        engineering_status = ProjectBeamEngineeringStatus.FAIL
    elif held:
        engineering_status = ProjectBeamEngineeringStatus.HOLD
    else:
        engineering_status = ProjectBeamEngineeringStatus.PASS

    if intake_status is ProjectBeamIntakeStatus.BLOCKED:
        overall_status = ProjectBeamOverallStatus.BLOCKED
    elif calculation_status is ProjectBeamCalculationStatus.ERROR or held:
        overall_status = ProjectBeamOverallStatus.HOLD
    elif engineering_status is ProjectBeamEngineeringStatus.FAIL:
        overall_status = ProjectBeamOverallStatus.FAIL
    elif engineering_status is ProjectBeamEngineeringStatus.PASS and evaluated > 0:
        overall_status = ProjectBeamOverallStatus.PASS
    else:  # pragma: no cover - state table exhaustiveness
        overall_status = ProjectBeamOverallStatus.HOLD

    return ProjectBeamBatchSummaryV1(
        total=total,
        valid=valid,
        blocked=blocked,
        evaluated=evaluated,
        passed=passed,
        failed=failed,
        held=held,
        intake_status=intake_status,
        calculation_status=calculation_status,
        engineering_status=engineering_status,
        overall_status=overall_status,
    )


def _prepare_validations(
    payloads: Sequence[Mapping[str, Any] | ProjectBeamDesignInputV1],
    *,
    units: str,
    additional_issues: Sequence[tuple[ProjectBeamInputIssueV1, ...]] | None = None,
) -> list[ProjectBeamInputValidationV1]:
    validations = _validate_batch(payloads, additional_issues)
    if units != "IS456":
        units_issue = (
            _issue(
                "PROJECT_BEAM_UNSUPPORTED_UNITS",
                "units",
                "The project beam v1 service accepts explicit IS456 units only.",
            ),
        )
        validations = [
            _with_issues(validation, units_issue) for validation in validations
        ]
    return validations


def _iter_validated_members(
    validations: Sequence[ProjectBeamInputValidationV1],
    *,
    units: str,
) -> Iterable[ProjectBeamMemberResultV1]:
    """Calculate accepted members only as their result is requested."""

    for index, validation in enumerate(validations):
        yield (
            _blocked_member(validation, index)
            if validation.value is None
            else _calculated_member(validation.value, index, units=units)
        )


def _design_project_batch(
    payloads: Sequence[Mapping[str, Any] | ProjectBeamDesignInputV1],
    *,
    units: str,
    additional_issues: Sequence[tuple[ProjectBeamInputIssueV1, ...]] | None = None,
) -> ProjectBeamBatchResultV1:
    validations = _prepare_validations(
        payloads,
        units=units,
        additional_issues=additional_issues,
    )
    members = tuple(_iter_validated_members(validations, units=units))
    return ProjectBeamBatchResultV1(members=members, summary=_summarize(members))


def design_project_beams_v1(
    beams: Iterable[Mapping[str, Any] | ProjectBeamDesignInputV1],
    *,
    units: str = "IS456",
) -> ProjectBeamBatchResultV1:
    """Validate the complete batch, then calculate only accepted unique members."""

    return _design_project_batch(list(beams), units=units)


def validate_project_beam_batch_v1(
    beams: Iterable[Mapping[str, Any] | ProjectBeamDesignInputV1],
    *,
    units: str = "IS456",
) -> tuple[ProjectBeamInputValidationV1, ...]:
    """Validate a complete project batch without calling calculation functions."""

    return tuple(_prepare_validations(list(beams), units=units))


def design_project_beams_iter_v1(
    beams: Iterable[Mapping[str, Any] | ProjectBeamDesignInputV1],
    *,
    units: str = "IS456",
) -> Iterable[ProjectBeamMemberResultV1]:
    """Yield strict member results after whole-batch identity validation."""

    validations = _prepare_validations(list(beams), units=units)
    return _iter_validated_members(validations, units=units)


def _prepare_legacy_validations(
    beams: Iterable[Any],
    *,
    units: str,
) -> list[ProjectBeamInputValidationV1]:
    payloads: list[dict[str, Any]] = []
    additional_issues: list[tuple[ProjectBeamInputIssueV1, ...]] = []
    for beam in beams:
        payload, issues = _normalize_legacy_beam(beam)
        payloads.append(payload)
        additional_issues.append(issues)
    return _prepare_validations(
        payloads,
        units=units,
        additional_issues=additional_issues,
    )


def _design_legacy_batch(
    beams: Iterable[Any],
    *,
    units: str,
) -> ProjectBeamBatchResultV1:
    validations = _prepare_legacy_validations(beams, units=units)
    members = tuple(_iter_validated_members(validations, units=units))
    return ProjectBeamBatchResultV1(
        members=members,
        summary=_summarize(members),
    )


def _legacy_outcome(member: ProjectBeamMemberResultV1) -> dict[str, Any]:
    if member.calculation_status is ProjectBeamCalculationStatus.COMPLETED:
        calculation = deepcopy(dict(member.calculation or {}))
        data = {
            "beam_id": member.member_id,
            "index": member.index,
            "input": member.input.to_dict() if member.input is not None else None,
            "intake_status": member.intake_status.value,
            "calculation_status": member.calculation_status.value,
            "engineering_status": member.engineering_status.value,
            "review_status": member.review_status,
            "overall_status": member.overall_status.value,
            **calculation,
        }
        return {"success": True, "data": data}

    issues = [issue.to_dict() for issue in member.issues]
    first_issue = member.issues[0] if member.issues else None
    return {
        "success": False,
        "error": {
            "beam_id": member.member_id,
            "index": member.index,
            "code": first_issue.code if first_issue else "PROJECT_BEAM_BLOCKED",
            "message": first_issue.message if first_issue else "Project beam blocked.",
            "issues": issues,
            "intake_status": member.intake_status.value,
            "calculation_status": member.calculation_status.value,
            "engineering_status": member.engineering_status.value,
            "overall_status": member.overall_status.value,
        },
    }


def design_beams_iter(
    beams: Iterable[Any],
    *,
    units: str = "IS456",
) -> Iterable[dict[str, Any]]:
    """Compatibility surface that delegates to the strict project contract."""

    validations = _prepare_legacy_validations(beams, units=units)
    return (
        _legacy_outcome(member)
        for member in _iter_validated_members(validations, units=units)
    )


def design_beams(
    beams: Iterable[Any],
    *,
    units: str = "IS456",
) -> dict[str, Any]:
    """Return the legacy shape without restoring unsafe defaults or precedence."""

    batch_result = _design_legacy_batch(beams, units=units)
    outcomes = [_legacy_outcome(member) for member in batch_result.members]
    results = [outcome["data"] for outcome in outcomes if outcome["success"]]
    errors = [outcome["error"] for outcome in outcomes if not outcome["success"]]
    summary = batch_result.summary.to_dict()
    return {
        "results": results,
        "errors": errors,
        "summary": {
            **summary,
            "status": summary["overall_status"],
            "is_safe": summary["overall_status"] == "PASS",
        },
    }
