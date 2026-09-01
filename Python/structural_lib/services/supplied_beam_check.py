"""Canonical V2 supplied-reinforcement beam check."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any, Literal

from structural_lib.core.result_contract import (
    CalculationStatus,
    EngineeringStatus,
    IntakeStatus,
    ResultIdentityV1,
    StructuralIssueV1,
    StructuralResultEnvelopeV2,
)
from structural_lib.core.version import get_runtime_version
from structural_lib.services.beam_api import check_beam_is456
from structural_lib.services.beam_reinforcement import (
    BeamReinforcementEvaluationV1,
    LongitudinalBarLayersV1,
    evaluate_supplied_beam_reinforcement_v1,
)
from structural_lib.services.contracts.beam_supplied_check import (
    BEAM_SUPPLIED_CHECK_SCHEMA_VERSION,
    BeamSuppliedCheckRequestV2,
)

__all__ = [
    "BEAM_SUPPLIED_CHECK_RESULT_SCHEMA_VERSION",
    "BeamSuppliedCheckResultV2",
    "BeamSuppliedShearEvaluationV2",
    "check_supplied_beam_v2",
]


BEAM_SUPPLIED_CHECK_RESULT_SCHEMA_VERSION = "beam-supplied-check-result/v2"
BeamSuppliedTerminalStatus = Literal["PASS", "FAIL", "HOLD", "ERROR"]


def _layer_centroid_from_face_mm(
    arrangement: LongitudinalBarLayersV1,
    *,
    cover_mm: float,
    stirrup_diameter_mm: float,
) -> float:
    centres = [cover_mm + stirrup_diameter_mm + arrangement.diameter_mm / 2.0]
    for spacing in arrangement.vertical_center_spacings_mm:
        centres.append(centres[-1] + spacing)
    return (
        math.fsum(
            count * centre
            for count, centre in zip(arrangement.bars_per_layer, centres, strict=True)
        )
        / arrangement.count
    )


def _input_hash(request: BeamSuppliedCheckRequestV2) -> str:
    payload = json.dumps(
        request.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class BeamSuppliedShearEvaluationV2:
    """Check the exact stirrup area and spacing against the calculated demand."""

    status: Literal["PASS", "FAIL"]
    required_vus_kn: float
    concrete_capacity_kn: float
    provided_stirrup_capacity_kn: float
    total_capacity_kn: float
    provided_asv_mm2: float
    provided_spacing_mm: float
    maximum_permitted_spacing_mm: float
    spacing_is_adequate: bool
    capacity_is_adequate: bool
    section_shear_is_adequate: bool
    utilization: float
    issues: tuple[dict[str, str], ...]

    def to_dict(self) -> dict[str, Any]:
        """Return the versioned JSON-safe shear-check payload."""

        return {
            "schema_version": "beam-supplied-shear-check/v2",
            "status": self.status,
            "required_Vus_kn": self.required_vus_kn,
            "concrete_capacity_kn": self.concrete_capacity_kn,
            "provided_stirrup_capacity_kn": self.provided_stirrup_capacity_kn,
            "total_capacity_kn": self.total_capacity_kn,
            "provided_asv_mm2": self.provided_asv_mm2,
            "provided_spacing_mm": self.provided_spacing_mm,
            "maximum_permitted_spacing_mm": self.maximum_permitted_spacing_mm,
            "spacing_is_adequate": self.spacing_is_adequate,
            "capacity_is_adequate": self.capacity_is_adequate,
            "section_shear_is_adequate": self.section_shear_is_adequate,
            "utilization": self.utilization,
            "issues": list(self.issues),
            "clause_refs": {
                "shear_strength": "IS 456:2000 Cl 40",
                "stirrup_design": "IS 456:2000 Cl 40.4",
                "maximum_spacing": "IS 456:2000 Cl 26.5.1.5",
                "minimum_shear_reinforcement": "IS 456:2000 Cl 26.5.1.6",
            },
        }


@dataclass(frozen=True)
class BeamSuppliedCheckResultV2:
    """One terminal, correlated result for the V2 supplied-beam check."""

    correlation_id: str
    status: BeamSuppliedTerminalStatus
    request: BeamSuppliedCheckRequestV2
    effective_depth_resolution: dict[str, Any]
    d_dash_used_mm: float
    longitudinal: BeamReinforcementEvaluationV1
    shear: BeamSuppliedShearEvaluationV2
    result_envelope: StructuralResultEnvelopeV2
    limitations: tuple[str, ...]
    schema_version: str = BEAM_SUPPLIED_CHECK_RESULT_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        """Return the stable Python/REST/WebSocket representation."""

        return {
            "schema_version": self.schema_version,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "identity": self.request.identity.model_dump(mode="json"),
            "primary_tension_face": self.request.actions.primary_tension_face,
            "request": self.request.model_dump(mode="json"),
            "effective_depth_resolution": self.effective_depth_resolution,
            "d_dash_used_mm": self.d_dash_used_mm,
            "longitudinal": self.longitudinal.to_dict(),
            "shear": self.shear.to_dict(),
            "result_envelope": self.result_envelope.to_dict(),
            "limitations": list(self.limitations),
        }


def _evaluate_shear(
    request: BeamSuppliedCheckRequestV2,
    *,
    d_mm: float,
    shear_result: Any,
) -> BeamSuppliedShearEvaluationV2:
    reinforcement = request.reinforcement
    fy_design_nmm2 = min(request.materials.fy_transverse_nmm2, 415.0)
    provided_capacity_kn = (
        0.87
        * fy_design_nmm2
        * reinforcement.asv_mm2
        * d_mm
        / (reinforcement.stirrup_spacing_mm * 1000.0)
    )
    concrete_capacity_kn = shear_result.tau_c * request.section.b_mm * d_mm / 1000.0
    total_capacity_kn = concrete_capacity_kn + provided_capacity_kn
    required_spacing_mm = float(shear_result.spacing)
    spacing_ok = (
        shear_result.is_safe
        and required_spacing_mm > 0
        and reinforcement.stirrup_spacing_mm <= required_spacing_mm + 1e-9
    )
    capacity_ok = shear_result.Vus <= provided_capacity_kn + 1e-9
    section_ok = bool(shear_result.is_safe)
    issues: list[dict[str, str]] = []
    if not section_ok:
        issues.append(
            {
                "code": "BEAM_SECTION_SHEAR_CAPACITY_EXCEEDED",
                "path": "actions.vu_kn",
                "message": "The section exceeds the maintained concrete shear-stress limit.",
            }
        )
    if not spacing_ok:
        issues.append(
            {
                "code": "BEAM_STIRRUP_SPACING_INADEQUATE",
                "path": "reinforcement.stirrup_spacing_mm",
                "message": "The supplied stirrup spacing exceeds the calculated maximum.",
            }
        )
    if not capacity_ok:
        issues.append(
            {
                "code": "BEAM_STIRRUP_CAPACITY_INADEQUATE",
                "path": "reinforcement",
                "message": "The supplied stirrup area and spacing do not provide the required Vus.",
            }
        )
    status: Literal["PASS", "FAIL"] = (
        "PASS" if section_ok and spacing_ok and capacity_ok else "FAIL"
    )
    utilization = (
        request.actions.vu_kn / total_capacity_kn
        if total_capacity_kn > 0
        else float("inf")
    )
    return BeamSuppliedShearEvaluationV2(
        status=status,
        required_vus_kn=float(shear_result.Vus),
        concrete_capacity_kn=concrete_capacity_kn,
        provided_stirrup_capacity_kn=provided_capacity_kn,
        total_capacity_kn=total_capacity_kn,
        provided_asv_mm2=reinforcement.asv_mm2,
        provided_spacing_mm=reinforcement.stirrup_spacing_mm,
        maximum_permitted_spacing_mm=required_spacing_mm,
        spacing_is_adequate=spacing_ok,
        capacity_is_adequate=capacity_ok,
        section_shear_is_adequate=section_ok,
        utilization=utilization,
        issues=tuple(issues),
    )


def check_supplied_beam_v2(
    request: BeamSuppliedCheckRequestV2,
) -> BeamSuppliedCheckResultV2:
    """Check exact supplied bars and stirrups for one factored beam case.

    The operation derives no private cover offset. Effective depth comes from
    exactly one explicit V2 section basis, while actual bar-layer centroids are
    independently recomputed and compared by the accepted reinforcement
    evaluator. A software ``PASS`` remains subject to qualified review.
    """

    if not isinstance(request, BeamSuppliedCheckRequestV2):
        raise TypeError("request must be BeamSuppliedCheckRequestV2")
    depth_resolution = request.section.resolve_effective_depth()
    reinforcement = request.reinforcement
    supplied = reinforcement.to_service()
    compression_centroid_mm = _layer_centroid_from_face_mm(
        supplied.compression_or_hanger,
        cover_mm=reinforcement.clear_cover_mm,
        stirrup_diameter_mm=reinforcement.stirrup_diameter_mm,
    )
    report = check_beam_is456(
        units="IS456",
        cases=[
            {
                "case_id": request.identity.case_id,
                "mu_knm": request.actions.mu_knm,
                "vu_kn": request.actions.vu_kn,
                "ast_mm2_for_shear": supplied.tension.area_provided_mm2,
                "fy_transverse_nmm2": request.materials.fy_transverse_nmm2,
            }
        ],
        b_mm=request.section.b_mm,
        D_mm=request.section.D_mm,
        d_mm=depth_resolution.d_mm,
        fck_nmm2=request.materials.fck_nmm2,
        fy_nmm2=request.materials.fy_nmm2,
        d_dash_mm=compression_centroid_mm,
        asv_mm2=reinforcement.asv_mm2,
    )
    if len(report.cases) != 1:
        raise RuntimeError("supplied beam check did not return exactly one case")
    calculation = report.cases[0]
    support = request.support
    longitudinal = evaluate_supplied_beam_reinforcement_v1(
        ast_required_mm2=calculation.flexure.Ast_required,
        asc_required_mm2=calculation.flexure.Asc_required,
        b_mm=request.section.b_mm,
        D_mm=request.section.D_mm,
        d_design_mm=depth_resolution.d_mm,
        d_dash_design_mm=compression_centroid_mm,
        cover_mm=reinforcement.clear_cover_mm,
        stirrup_dia_mm=reinforcement.stirrup_diameter_mm,
        fck_nmm2=request.materials.fck_nmm2,
        fy_nmm2=request.materials.fy_nmm2,
        vu_kn=request.actions.vu_kn,
        support_width_start_mm=support.start_width_mm if support is not None else None,
        support_width_end_mm=support.end_width_mm if support is not None else None,
        support_width_source_reference=(
            support.source_reference if support is not None else None
        ),
        selection=request.selection.to_service(),
        supplied=supplied,
    )
    shear = _evaluate_shear(
        request, d_mm=depth_resolution.d_mm, shear_result=calculation.shear
    )

    status: BeamSuppliedTerminalStatus
    if longitudinal.status == "HOLD":
        status = "HOLD"
    elif longitudinal.status == "FAIL" or shear.status == "FAIL":
        status = "FAIL"
    else:
        status = "PASS"
    engineering_status = EngineeringStatus(status)
    issues = tuple(
        StructuralIssueV1(
            code=issue["code"],
            path=issue.get("path", "reinforcement"),
            message=issue["message"],
        )
        for issue in (*longitudinal.issues, *shear.issues)
    )
    envelope = StructuralResultEnvelopeV2(
        intake_status=(
            IntakeStatus.PARTIAL if status == "HOLD" else IntakeStatus.VALID
        ),
        calculation_status=CalculationStatus.COMPLETED,
        engineering_status=engineering_status,
        issues=issues,
        result_identity=ResultIdentityV1(
            contract_version=BEAM_SUPPLIED_CHECK_SCHEMA_VERSION,
            library_version=get_runtime_version(),
            input_hash=_input_hash(request),
            calculation_identity="is456-supplied-rectangular-beam-check/v2",
        ),
    )
    return BeamSuppliedCheckResultV2(
        correlation_id=request.correlation_id,
        status=status,
        request=request,
        effective_depth_resolution=depth_resolution.to_dict(),
        d_dash_used_mm=compression_centroid_mm,
        longitudinal=longitudinal,
        shear=shear,
        result_envelope=envelope,
        limitations=(
            "One ordinary solid rectangular beam and one factored action case only.",
            "Torsion, serviceability, seismic capacity design, curtailment, laps, and construction sequencing are outside this check.",
            "A software PASS is not professional approval; qualified review remains required.",
        ),
    )
