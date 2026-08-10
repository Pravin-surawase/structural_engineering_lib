# SPDX-License-Identifier: MIT
# ruff: noqa: N815
"""Bounded orchestration for concentric isolated footings (IS 456:2000)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

from structural_lib.codes.is456.footing.bearing import size_footing
from structural_lib.codes.is456.footing.flexure import footing_flexure
from structural_lib.codes.is456.footing.load_transfer import (
    LoadTransferResult,
    check_isolated_footing_load_transfer,
)
from structural_lib.codes.is456.footing.one_way_shear import footing_one_way_shear
from structural_lib.codes.is456.footing.punching_shear import footing_punching_shear
from structural_lib.core.data_types import (
    FootingBearingResult,
    FootingFlexureResult,
    FootingOneWayShearResult,
    FootingPunchingResult,
    FootingType,
)
from structural_lib.core.errors import StructuralLibError, ValidationError

__all__ = [
    "ConcentricIsolatedFootingInput",
    "ConcentricIsolatedFootingResult",
    "FootingDepthCandidate",
    "FootingDirectionalReinforcementDemand",
    "FootingProvenance",
    "design_concentric_isolated_footing_is456",
]


_A1_BASIS = "largest_frustum_1v_2h"
_SERVICE_LOAD_BASIS = "includes_footing_self_weight_and_overburden"
_SUPPORTED_CASE = "concentric_centred_isolated_square_or_rectangular_footing"
_DETAILING_HOLD_REASON = (
    "PROVIDED_REBAR_LAYOUT_AND_DETAILING_NOT_SUPPORTED: required directional "
    "steel is reported, but bar selection, spacing, anchorage and a buildable "
    "layout require a separate maintained detailing check."
)
_EXCLUSIONS = (
    "Eccentric, partial-contact and moment-transfer cases are excluded.",
    "Combined, strap, raft and pile foundations are excluded.",
    "Settlement and allowable-soil-pressure derivation are excluded.",
    "Lateral, sliding, uplift and global-overturning checks are excluded.",
    "Edge/corner punching and stepped, sloped or arbitrary geometry are excluded.",
)


@dataclass(frozen=True)
class ConcentricIsolatedFootingInput:
    """Explicit inputs for the sole supported B1 footing workflow.

    Service and factored axial actions are independent submitted inputs.  The
    service action must already include footing self-weight and overburden.
    Allowable soil pressure is an externally accepted engineering input; this
    service neither derives SBC nor checks settlement.
    """

    case_id: str
    service_axial_load_kN: float
    service_load_combination_id: str
    service_load_basis: Literal["includes_footing_self_weight_and_overburden"]
    factored_axial_load_kN: float
    factored_load_combination_id: str
    allowable_soil_pressure_kPa: float
    allowable_soil_pressure_source_reference: str
    allowable_soil_pressure_is_externally_approved: bool
    footing_type: FootingType
    column_L_mm: float
    column_B_mm: float
    minimum_overall_thickness_mm: float
    maximum_overall_thickness_mm: float
    thickness_increment_mm: float
    effective_depth_offset_L_mm: float
    effective_depth_offset_B_mm: float
    footing_concrete_fck_nmm2: float
    column_concrete_fck_nmm2: float
    steel_fy_nmm2: float
    effective_supporting_area_A1_mm2: float
    effective_supporting_area_basis: Literal["largest_frustum_1v_2h"]
    effective_supporting_area_is_approved: bool
    dowel_count: int
    dowel_diameter_mm: float
    column_longitudinal_bar_diameter_mm: float
    available_dowel_development_length_into_footing_mm: float
    available_dowel_development_length_into_column_mm: float
    dowel_bar_type: Literal["deformed", "plain"] = "deformed"


@dataclass(frozen=True)
class FootingDepthCandidate:
    """Structural evidence for one deterministic thickness candidate."""

    overall_thickness_mm: float
    effective_depth_L_mm: float
    effective_depth_B_mm: float
    structural_status: Literal["PASS", "FAIL", "HOLD"]
    one_way_shear_utilization: float | None
    punching_shear_utilization: float | None
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class FootingDirectionalReinforcementDemand:
    """Required flexural steel evidence; this is not a provided-bar layout."""

    direction: Literal["L", "B"]
    effective_depth_mm: float
    moment_kNm: float
    required_steel_area_mm2: float
    required_steel_percent: float
    central_band_fraction: float | None
    detailing_status: Literal["HOLD"] = "HOLD"


@dataclass(frozen=True)
class FootingProvenance:
    """Input and calculation identities needed to interpret a B1 result."""

    schema_version: str
    code_edition: str
    units: dict[str, str]
    service_load_combination_id: str
    service_load_basis: str
    factored_load_combination_id: str
    allowable_soil_pressure_source_reference: str
    allowable_soil_pressure_role: str
    loaded_area_A2_basis: str
    effective_supporting_area_basis: str
    core_function_ids: tuple[str, ...]
    clause_bases: dict[str, str]
    source_ids: tuple[str, ...]
    qualified_review_requirement: str


@dataclass(frozen=True)
class ConcentricIsolatedFootingResult:
    """Bounded calculation evidence with fail-closed aggregate statuses."""

    case_id: str
    status: Literal["PASS", "FAIL", "HOLD"]
    calculation_status: Literal["PASS", "FAIL", "NOT_EVALUATED"]
    detailing_status: Literal["HOLD"]
    detailing_hold_reason: str
    qualified_review_required: bool
    supported_case: str
    exclusions: tuple[str, ...]
    service_axial_load_kN: float
    factored_axial_load_kN: float
    selected_overall_thickness_mm: float | None
    selected_effective_depth_L_mm: float | None
    selected_effective_depth_B_mm: float | None
    depth_candidates: tuple[FootingDepthCandidate, ...]
    bearing: FootingBearingResult
    flexure: FootingFlexureResult | None
    one_way_shear: FootingOneWayShearResult | None
    punching: FootingPunchingResult | None
    load_transfer: LoadTransferResult
    reinforcement_demands: tuple[FootingDirectionalReinforcementDemand, ...]
    pt_passed_to_one_way_shear_percent: dict[str, float]
    failed_checks: tuple[str, ...]
    hold_reasons: tuple[str, ...]
    provenance: FootingProvenance

    @property
    def is_ok(self) -> bool:
        """True only for an unheld aggregate PASS result."""
        return self.status == "PASS"

    @property
    def calculations_are_safe(self) -> bool:
        """Report only whether all represented calculation checks passed."""
        return self.calculation_status == "PASS"


def _require_positive_finite(name: str, value: object) -> None:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value <= 0
    ):
        raise ValidationError(
            f"{name} must be a finite positive value",
            details={name: value},
        )


def _require_non_empty(name: str, value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{name} must be a non-empty string")


def _validate_request(request: ConcentricIsolatedFootingInput) -> None:
    for name in (
        "case_id",
        "service_load_combination_id",
        "factored_load_combination_id",
        "allowable_soil_pressure_source_reference",
    ):
        _require_non_empty(name, getattr(request, name))
    for name in (
        "service_axial_load_kN",
        "factored_axial_load_kN",
        "allowable_soil_pressure_kPa",
        "column_L_mm",
        "column_B_mm",
        "minimum_overall_thickness_mm",
        "maximum_overall_thickness_mm",
        "thickness_increment_mm",
        "effective_depth_offset_L_mm",
        "effective_depth_offset_B_mm",
        "footing_concrete_fck_nmm2",
        "column_concrete_fck_nmm2",
        "steel_fy_nmm2",
        "effective_supporting_area_A1_mm2",
        "dowel_diameter_mm",
        "column_longitudinal_bar_diameter_mm",
        "available_dowel_development_length_into_footing_mm",
        "available_dowel_development_length_into_column_mm",
    ):
        _require_positive_finite(name, getattr(request, name))
    if request.footing_type not in {
        FootingType.ISOLATED_SQUARE,
        FootingType.ISOLATED_RECTANGULAR,
    }:
        raise ValidationError(
            "Only isolated square or rectangular footings are supported"
        )
    if request.service_load_basis != _SERVICE_LOAD_BASIS:
        raise ValidationError(
            "service load must explicitly include footing self-weight and overburden",
            details={"required_service_load_basis": _SERVICE_LOAD_BASIS},
        )
    if request.allowable_soil_pressure_is_externally_approved is not True:
        raise ValidationError(
            "allowable soil pressure must be externally established and approved; "
            "this service does not derive SBC or check settlement"
        )
    if request.effective_supporting_area_basis != _A1_BASIS:
        raise ValidationError(
            "effective A1 must use the approved largest-frustum 1V:2H basis"
        )
    if request.effective_supporting_area_is_approved is not True:
        raise ValidationError(
            "effective A1 geometry must be approved; footing plan area is not A1"
        )
    if request.minimum_overall_thickness_mm < 150.0:
        raise ValidationError(
            "minimum overall thickness must be at least 150 mm",
            clause_ref="Cl. 34.1",
        )
    if request.maximum_overall_thickness_mm < request.minimum_overall_thickness_mm:
        raise ValidationError("maximum overall thickness must not be below the minimum")
    if request.minimum_overall_thickness_mm <= max(
        request.effective_depth_offset_L_mm,
        request.effective_depth_offset_B_mm,
    ):
        raise ValidationError(
            "effective-depth offsets must leave a positive depth at the minimum thickness"
        )


def _depth_values(
    request: ConcentricIsolatedFootingInput,
) -> tuple[tuple[float, float, float], ...]:
    count = math.floor(
        (request.maximum_overall_thickness_mm - request.minimum_overall_thickness_mm)
        / request.thickness_increment_mm
        + 1e-12
    )
    return tuple(
        (
            request.minimum_overall_thickness_mm
            + index * request.thickness_increment_mm,
            request.minimum_overall_thickness_mm
            + index * request.thickness_increment_mm
            - request.effective_depth_offset_L_mm,
            request.minimum_overall_thickness_mm
            + index * request.thickness_increment_mm
            - request.effective_depth_offset_B_mm,
        )
        for index in range(count + 1)
    )


def _provenance(
    request: ConcentricIsolatedFootingInput,
    load_transfer: LoadTransferResult,
) -> FootingProvenance:
    return FootingProvenance(
        schema_version="footing.isolated.concentric/v1",
        code_edition="IS 456:2000",
        units={
            "force": "kN",
            "length": "mm",
            "stress": "N/mm2",
            "soil_pressure": "kPa",
            "area": "mm2",
        },
        service_load_combination_id=request.service_load_combination_id,
        service_load_basis=request.service_load_basis,
        factored_load_combination_id=request.factored_load_combination_id,
        allowable_soil_pressure_source_reference=(
            request.allowable_soil_pressure_source_reference
        ),
        allowable_soil_pressure_role=(
            "Externally supplied allowable pressure; no SBC derivation or settlement "
            "approval is performed."
        ),
        loaded_area_A2_basis=(
            "Centred rectangular column footprint: column_L_mm * column_B_mm."
        ),
        effective_supporting_area_basis=request.effective_supporting_area_basis,
        core_function_ids=(
            "structural_lib.codes.is456.footing.bearing.size_footing",
            "structural_lib.codes.is456.footing.flexure.footing_flexure",
            "structural_lib.codes.is456.footing.one_way_shear.footing_one_way_shear",
            "structural_lib.codes.is456.footing.punching_shear.footing_punching_shear",
            "structural_lib.codes.is456.footing.load_transfer."
            "check_isolated_footing_load_transfer",
        ),
        clause_bases={
            "plan_sizing": "Cl. 34.1; service action and external allowable pressure",
            "flexure": (
                "Cl. 34.2.3.1 and Cl. 34.3.1; factored axial action and "
                "rectangular-footing central-band distribution"
            ),
            "one_way_shear": (
                "Cl. 34.2.4.1(a) and IS 456 Table 19; factored axial action "
                "using directional required pt as a conservative screening input "
                "pending provided detailing"
            ),
            "punching": "Cl. 31.6.1 and Cl. 34.2.4.1(b); factored axial action",
            "load_transfer": "Cl. 34.4/34.4.1-34.4.3 and Cl. 26.2.1",
        },
        source_ids=load_transfer.source_ids,
        qualified_review_requirement=(
            "Bounded software calculation evidence only; qualified structural-"
            "engineering review is required."
        ),
    )


def _reinforcement_demands(
    flexure: FootingFlexureResult | None,
    d_l_mm: float | None,
    d_b_mm: float | None,
    footing_l_mm: float,
    footing_b_mm: float,
) -> tuple[FootingDirectionalReinforcementDemand, ...]:
    if flexure is None or d_l_mm is None or d_b_mm is None:
        return ()
    is_rectangular = not math.isclose(
        footing_l_mm,
        footing_b_mm,
        rel_tol=0.0,
        abs_tol=1.0,
    )
    short_direction = "B" if footing_b_mm < footing_l_mm else "L"
    return (
        FootingDirectionalReinforcementDemand(
            direction="L",
            effective_depth_mm=d_l_mm,
            moment_kNm=flexure.Mu_L_kNm,
            required_steel_area_mm2=flexure.Ast_L_mm2,
            required_steel_percent=flexure.pt_L_percent,
            central_band_fraction=(
                flexure.central_band_fraction
                if is_rectangular and short_direction == "L"
                else None
            ),
        ),
        FootingDirectionalReinforcementDemand(
            direction="B",
            effective_depth_mm=d_b_mm,
            moment_kNm=flexure.Mu_B_kNm,
            required_steel_area_mm2=flexure.Ast_B_mm2,
            required_steel_percent=flexure.pt_B_percent,
            central_band_fraction=(
                flexure.central_band_fraction
                if is_rectangular and short_direction == "B"
                else None
            ),
        ),
    )


def design_concentric_isolated_footing_is456(
    request: ConcentricIsolatedFootingInput,
) -> ConcentricIsolatedFootingResult:
    """Size and check the bounded concentric isolated-footing case.

    The first uniform-thickness candidate passing flexure, one-way shear and
    punching is selected.  Differing directional depths return ``HOLD`` because
    the maintained shear/punching core accepts one effective depth; no hidden
    averaging or minimum-depth substitution is made.
    """
    if not isinstance(request, ConcentricIsolatedFootingInput):
        raise TypeError("request must be a ConcentricIsolatedFootingInput")
    _validate_request(request)

    bearing = size_footing(
        P_service_kN=request.service_axial_load_kN,
        q_safe_kPa=request.allowable_soil_pressure_kPa,
        a_mm=request.column_L_mm,
        b_mm=request.column_B_mm,
        M_service_kNm=0.0,
        footing_type=request.footing_type,
    )
    load_transfer = check_isolated_footing_load_transfer(
        Pu_kN=request.factored_axial_load_kN,
        loaded_area_A2_mm2=request.column_L_mm * request.column_B_mm,
        effective_supporting_area_A1_mm2=(request.effective_supporting_area_A1_mm2),
        effective_supporting_area_basis=request.effective_supporting_area_basis,
        effective_supporting_area_is_approved=(
            request.effective_supporting_area_is_approved
        ),
        supporting_concrete_fck_nmm2=request.footing_concrete_fck_nmm2,
        supported_concrete_fck_nmm2=request.column_concrete_fck_nmm2,
        steel_fy_nmm2=request.steel_fy_nmm2,
        dowel_count=request.dowel_count,
        dowel_diameter_mm=request.dowel_diameter_mm,
        column_longitudinal_bar_diameter_mm=(
            request.column_longitudinal_bar_diameter_mm
        ),
        available_dowel_development_length_into_footing_mm=(
            request.available_dowel_development_length_into_footing_mm
        ),
        available_dowel_development_length_into_supported_member_mm=(
            request.available_dowel_development_length_into_column_mm
        ),
        dowel_bar_type=request.dowel_bar_type,
    )
    provenance = _provenance(request, load_transfer)
    depth_values = _depth_values(request)

    if not math.isclose(
        request.effective_depth_offset_L_mm,
        request.effective_depth_offset_B_mm,
        rel_tol=0.0,
        abs_tol=1e-9,
    ):
        held_candidates = tuple(
            FootingDepthCandidate(
                overall_thickness_mm=overall,
                effective_depth_L_mm=d_l,
                effective_depth_B_mm=d_b,
                structural_status="HOLD",
                one_way_shear_utilization=None,
                punching_shear_utilization=None,
                reasons=("DIRECTIONAL_EFFECTIVE_DEPTH_NOT_SUPPORTED_BY_CURRENT_CORE",),
            )
            for overall, d_l, d_b in depth_values
        )
        return ConcentricIsolatedFootingResult(
            case_id=request.case_id,
            status="HOLD",
            calculation_status="NOT_EVALUATED",
            detailing_status="HOLD",
            detailing_hold_reason=_DETAILING_HOLD_REASON,
            qualified_review_required=True,
            supported_case=_SUPPORTED_CASE,
            exclusions=_EXCLUSIONS,
            service_axial_load_kN=request.service_axial_load_kN,
            factored_axial_load_kN=request.factored_axial_load_kN,
            selected_overall_thickness_mm=None,
            selected_effective_depth_L_mm=None,
            selected_effective_depth_B_mm=None,
            depth_candidates=held_candidates,
            bearing=bearing,
            flexure=None,
            one_way_shear=None,
            punching=None,
            load_transfer=load_transfer,
            reinforcement_demands=(),
            pt_passed_to_one_way_shear_percent={},
            failed_checks=(),
            hold_reasons=(
                "DIRECTIONAL_EFFECTIVE_DEPTH_NOT_SUPPORTED_BY_CURRENT_CORE",
                _DETAILING_HOLD_REASON,
            ),
            provenance=provenance,
        )

    candidates: list[FootingDepthCandidate] = []
    selected_overall: float | None = None
    selected_d_l: float | None = None
    selected_d_b: float | None = None
    selected_flexure: FootingFlexureResult | None = None
    selected_one_way: FootingOneWayShearResult | None = None
    selected_punching: FootingPunchingResult | None = None

    for overall, d_l, d_b in depth_values:
        reasons: list[str] = []
        try:
            flexure = footing_flexure(
                Pu_kN=request.factored_axial_load_kN,
                L_mm=bearing.L_mm,
                B_mm=bearing.B_mm,
                d_mm=d_l,
                a_mm=request.column_L_mm,
                b_mm=request.column_B_mm,
                fck=request.footing_concrete_fck_nmm2,
                fy=request.steel_fy_nmm2,
                overall_thickness_mm=overall,
            )
            one_way = footing_one_way_shear(
                Pu_kN=request.factored_axial_load_kN,
                L_mm=bearing.L_mm,
                B_mm=bearing.B_mm,
                d_mm=d_l,
                a_mm=request.column_L_mm,
                b_mm=request.column_B_mm,
                fck=request.footing_concrete_fck_nmm2,
                pt_L_percent=flexure.pt_L_percent,
                pt_B_percent=flexure.pt_B_percent,
            )
            punching = footing_punching_shear(
                Pu_kN=request.factored_axial_load_kN,
                L_mm=bearing.L_mm,
                B_mm=bearing.B_mm,
                d_mm=d_l,
                a_mm=request.column_L_mm,
                b_mm=request.column_B_mm,
                fck=request.footing_concrete_fck_nmm2,
            )
        except StructuralLibError as exc:
            candidates.append(
                FootingDepthCandidate(
                    overall_thickness_mm=overall,
                    effective_depth_L_mm=d_l,
                    effective_depth_B_mm=d_b,
                    structural_status="FAIL",
                    one_way_shear_utilization=None,
                    punching_shear_utilization=None,
                    reasons=(str(exc),),
                )
            )
            continue

        if not flexure.is_safe:
            reasons.append("flexure")
        if not one_way.is_safe:
            reasons.append("one_way_shear")
        if not punching.is_safe:
            reasons.append("punching")
        structural_status: Literal["PASS", "FAIL", "HOLD"] = (
            "PASS" if not reasons else "FAIL"
        )
        candidates.append(
            FootingDepthCandidate(
                overall_thickness_mm=overall,
                effective_depth_L_mm=d_l,
                effective_depth_B_mm=d_b,
                structural_status=structural_status,
                one_way_shear_utilization=one_way.utilization_ratio,
                punching_shear_utilization=punching.utilization_ratio,
                reasons=tuple(reasons),
            )
        )
        if structural_status == "PASS":
            selected_overall = overall
            selected_d_l = d_l
            selected_d_b = d_b
            selected_flexure = flexure
            selected_one_way = one_way
            selected_punching = punching
            break

    failed_checks: list[str] = []
    if not bearing.is_safe:
        failed_checks.append("bearing")
    if selected_overall is None:
        failed_checks.append("depth_selection")
    if not load_transfer.is_safe:
        failed_checks.append("load_transfer")
    calculation_status: Literal["PASS", "FAIL", "NOT_EVALUATED"] = (
        "PASS" if not failed_checks else "FAIL"
    )
    status: Literal["PASS", "FAIL", "HOLD"] = (
        "FAIL" if calculation_status == "FAIL" else "HOLD"
    )
    reinforcement_demands = _reinforcement_demands(
        selected_flexure,
        selected_d_l,
        selected_d_b,
        bearing.L_mm,
        bearing.B_mm,
    )
    return ConcentricIsolatedFootingResult(
        case_id=request.case_id,
        status=status,
        calculation_status=calculation_status,
        detailing_status="HOLD",
        detailing_hold_reason=_DETAILING_HOLD_REASON,
        qualified_review_required=True,
        supported_case=_SUPPORTED_CASE,
        exclusions=_EXCLUSIONS,
        service_axial_load_kN=request.service_axial_load_kN,
        factored_axial_load_kN=request.factored_axial_load_kN,
        selected_overall_thickness_mm=selected_overall,
        selected_effective_depth_L_mm=selected_d_l,
        selected_effective_depth_B_mm=selected_d_b,
        depth_candidates=tuple(candidates),
        bearing=bearing,
        flexure=selected_flexure,
        one_way_shear=selected_one_way,
        punching=selected_punching,
        load_transfer=load_transfer,
        reinforcement_demands=reinforcement_demands,
        pt_passed_to_one_way_shear_percent=(
            {
                "L": selected_flexure.pt_L_percent,
                "B": selected_flexure.pt_B_percent,
            }
            if selected_flexure is not None
            else {}
        ),
        failed_checks=tuple(failed_checks),
        hold_reasons=(_DETAILING_HOLD_REASON,) if status == "HOLD" else (),
        provenance=provenance,
    )
