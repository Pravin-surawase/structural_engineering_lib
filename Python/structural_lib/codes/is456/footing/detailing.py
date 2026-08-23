# SPDX-License-Identifier: MIT
"""Maintained bottom-reinforcement detailing for concentric isolated footings.

The bounded case is a square or rectangular, uniform-depth footing under a
concentric factored column load.  This module consumes an accepted Cl. 34.4
load-transfer receipt and does not redesign its dowels.  Flexural demand is
recomputed at the physical bar centrelines through :func:`footing_flexure`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

from structural_lib.codes.is456.beam.detailing import (
    calculate_development_length,
    evaluate_tension_bar_anchorage_v1,
)
from structural_lib.codes.is456.footing.flexure import footing_flexure
from structural_lib.codes.is456.footing.load_transfer import (
    AMENDMENT_6_SOURCE_ID,
    IS456_CONSOLIDATED_SOURCE_ID,
    LoadTransferResult,
)
from structural_lib.codes.is456.footing.one_way_shear import footing_one_way_shear
from structural_lib.codes.is456.traceability import clause
from structural_lib.core.data_types import FootingOneWayShearResult
from structural_lib.core.errors import StructuralLibError

__all__ = [
    "FootingDetailingResult",
    "FootingDirectionDetail",
    "FootingEndAnchorageDetailV1",
    "FootingDowelScheduleLink",
    "FootingReinforcementZone",
    "detail_isolated_footing_bottom_steel",
]

_DIAMETERS = (10, 12, 16, 20, 25, 32)
_FCK = (20, 25, 30, 35, 40, 45, 50)
_CONTRACT_VERSION = "FOOT-ISO-DETAILING-P3-V1"
_SUPPORTED_CASE = "concentric_uniform_depth_isolated_square_or_rectangular_footing"
_LOAD_TRANSFER_SUPPORTED_CASE = (
    "concentric_isolated_square_or_rectangular_footing_with_dowels"
)
_SOURCE_IDS = (IS456_CONSOLIDATED_SOURCE_ID, AMENDMENT_6_SOURCE_ID)
_CLAUSE_REFS = (
    "34.2.3.1",
    "34.3",
    "34.3.1",
    "34.5.1",
    "26.5.2.1",
    "26.5.2.2",
    "26.3.2",
    "26.3.3(b)",
    "26.4",
    "26.2.1",
    "26.2.2.1",
    "34.4",
)
_EXCLUSIONS = (
    "Eccentric, partial-contact and biaxial pressure cases are excluded.",
    "Combined, strap, raft and pile foundation systems are excluded.",
    "Settlement, soil-capacity derivation and soil-structure interaction are excluded.",
    "Sliding, lateral load, uplift, overturning and seismic approval are excluded.",
    "Edge/corner punching and stepped, sloped or arbitrary geometry are excluded.",
    "Only straight, 90-degree bend and standard U-hook bottom-bar end arrangements are evaluated.",
    "Other bends, mechanical anchorage, curtailment, laps, bar-to-bar collision modelling, coordinates and bar-bending schedules are excluded.",
)
_UNITS = {
    "length": "mm",
    "area": "mm2",
    "moment": "kNm",
    "stress": "N/mm2",
    "force": "kN",
}


@dataclass(frozen=True)
class FootingReinforcementZone:
    """One buildable distribution zone without duplicated boundary bars."""

    zone: Literal["full_width", "central_band", "outer_band_each"]
    width_mm: float
    required_area_mm2: float
    provided_area_mm2: float
    bar_count: int
    spacing_mm: float
    clear_spacing_mm: float


@dataclass(frozen=True)
class FootingEndAnchorageDetailV1:
    """Symmetric end-anchorage and physical-fit evidence for one bar direction."""

    arrangement: Literal["straight", "bend_90", "u_hook_180"]
    arrangement_was_explicit: bool
    required_development_length_mm: float
    available_straight_length_mm: float
    anchorage_value_mm: float
    total_available_development_length_mm: float
    shortfall_mm: float
    utilization_ratio: float
    anchorage_is_adequate: bool
    bend_angle_degrees: int | None
    internal_bend_radius_mm: float | None
    centreline_bend_radius_mm: float | None
    extension_after_bend_mm: float | None
    bend_arc_length_mm: float
    vertical_envelope_required_mm: float
    vertical_envelope_available_mm: float
    return_extension_available_mm: float | None
    geometry_fits: bool
    bounded_constructability_is_adequate: bool
    geometry_source_reference: str | None
    geometry_source_is_approved: bool
    clause_refs: tuple[str, ...]
    source_ids: tuple[str, ...]


@dataclass(frozen=True)
class FootingDirectionDetail:
    """Selected straight-bar schedule for one orthogonal footing direction.

    For a central-band layout, ``spacing_mm`` is the largest scheduled zone
    spacing and ``clear_spacing_mm`` is the smallest clear zone spacing.  The
    exact central and outer spacings are retained in ``zones``.
    """

    direction: Literal["L", "B"]
    layer: Literal["lower", "upper"]
    layout: Literal["uniform", "central_band"]
    diameter_mm: int
    physical_effective_depth_mm: float
    analysis_effective_depth_mm: float
    Mu_kNm: float
    flexure_result_area_mm2: float
    analysis_screening_area_mm2: float
    minimum_area_mm2: float
    required_area_mm2: float
    provided_area_mm2: float
    bar_count: int
    spacing_mm: float
    clear_spacing_mm: float
    max_spacing_mm: float
    minimum_clear_spacing_mm: float
    max_diameter_mm: float
    development_length_mm: float
    development_length_unrounded_mm: float
    straight_anchorage_available_each_end_mm: float
    straight_bar_length_mm: float
    total_bar_length_mm: float
    end_anchorage: FootingEndAnchorageDetailV1
    zones: tuple[FootingReinforcementZone, ...]


@dataclass(frozen=True)
class FootingDowelScheduleLink:
    """Immutable linkage to the accepted Cl. 34.4 dowel schedule."""

    bar_count: int
    diameter_mm: float
    required_area_mm2: float
    provided_area_mm2: float
    required_development_length_into_footing_mm: float
    available_development_length_into_footing_mm: float
    required_development_length_into_supported_member_mm: float
    available_development_length_into_supported_member_mm: float
    is_safe: bool
    source_ids: tuple[str, ...]


@dataclass(frozen=True)
class FootingDetailingResult:
    """Fail-closed result for the bounded B2 detailing contract."""

    status: Literal["PASS", "FAIL", "HOLD"]
    qualified_review_required: bool
    reasons: tuple[str, ...]
    contract_version: str
    supported_case: str
    exclusions: tuple[str, ...]
    units: dict[str, str]
    source_ids: tuple[str, ...]
    clause_refs: tuple[str, ...]
    lower_direction: Literal["L", "B"]
    upper_direction: Literal["L", "B"]
    lower: FootingDirectionDetail | None
    upper: FootingDirectionDetail | None
    actual_provided_pt_percent: dict[str, float]
    final_one_way_shear: FootingOneWayShearResult | None
    dowel_schedule_link: FootingDowelScheduleLink
    accepted_load_transfer: LoadTransferResult


def _area(phi_mm: float) -> float:
    return math.pi * phi_mm * phi_mm / 4.0


def _valid_positive(**values: float) -> bool:
    return all(
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value > 0
        for value in values.values()
    )


def _dowel_link(receipt: LoadTransferResult) -> FootingDowelScheduleLink:
    return FootingDowelScheduleLink(
        bar_count=receipt.provided_bar_count,
        diameter_mm=receipt.provided_dowel_diameter_mm,
        required_area_mm2=receipt.required_transfer_steel_area_mm2,
        provided_area_mm2=receipt.provided_transfer_steel_area_mm2,
        required_development_length_into_footing_mm=(
            receipt.required_dowel_development_length_into_footing_mm
        ),
        available_development_length_into_footing_mm=(
            receipt.available_dowel_development_length_into_footing_mm
        ),
        required_development_length_into_supported_member_mm=(
            receipt.required_dowel_development_length_into_supported_member_mm
        ),
        available_development_length_into_supported_member_mm=(
            receipt.available_dowel_development_length_into_supported_member_mm
        ),
        is_safe=receipt.is_safe,
        source_ids=receipt.source_ids,
    )


def _result(
    status: Literal["PASS", "FAIL", "HOLD"],
    reason: str,
    receipt: LoadTransferResult,
    lower_direction: Literal["L", "B"],
    upper_direction: Literal["L", "B"],
    *,
    lower: FootingDirectionDetail | None = None,
    upper: FootingDirectionDetail | None = None,
    actual_provided_pt_percent: dict[str, float] | None = None,
    final_one_way_shear: FootingOneWayShearResult | None = None,
) -> FootingDetailingResult:
    return FootingDetailingResult(
        status=status,
        qualified_review_required=True,
        reasons=(reason,),
        contract_version=_CONTRACT_VERSION,
        supported_case=_SUPPORTED_CASE,
        exclusions=_EXCLUSIONS,
        units=dict(_UNITS),
        source_ids=_SOURCE_IDS,
        clause_refs=_CLAUSE_REFS,
        lower_direction=lower_direction,
        upper_direction=upper_direction,
        lower=lower,
        upper=upper,
        actual_provided_pt_percent=(
            {} if actual_provided_pt_percent is None else actual_provided_pt_percent
        ),
        final_one_way_shear=final_one_way_shear,
        dowel_schedule_link=_dowel_link(receipt),
        accepted_load_transfer=receipt,
    )


def _uniform_zone(
    *,
    distribution_width_mm: float,
    cover_mm: float,
    phi_mm: int,
    required_area_mm2: float,
    max_spacing_mm: float,
    minimum_clear_spacing_mm: float,
) -> tuple[FootingReinforcementZone, ...] | None:
    centre_span_mm = distribution_width_mm - 2 * cover_mm - phi_mm
    if centre_span_mm <= 0:
        return None
    area_count = math.ceil(required_area_mm2 / _area(phi_mm))
    spacing_count = math.ceil(centre_span_mm / max_spacing_mm) + 1
    count = max(2, area_count, spacing_count)
    spacing_mm = centre_span_mm / (count - 1)
    clear_spacing_mm = spacing_mm - phi_mm
    if clear_spacing_mm + 1e-9 < minimum_clear_spacing_mm:
        return None
    return (
        FootingReinforcementZone(
            zone="full_width",
            width_mm=distribution_width_mm,
            required_area_mm2=required_area_mm2,
            provided_area_mm2=count * _area(phi_mm),
            bar_count=count,
            spacing_mm=spacing_mm,
            clear_spacing_mm=clear_spacing_mm,
        ),
    )


def _central_band_zones(
    *,
    long_dimension_mm: float,
    short_dimension_mm: float,
    cover_mm: float,
    phi_mm: int,
    required_area_mm2: float,
    max_spacing_mm: float,
    minimum_clear_spacing_mm: float,
) -> tuple[FootingReinforcementZone, ...] | None:
    beta = long_dimension_mm / short_dimension_mm
    central_fraction = 2.0 / (beta + 1.0)
    central_required_mm2 = required_area_mm2 * central_fraction
    outer_required_each_mm2 = required_area_mm2 * (1.0 - central_fraction) / 2.0

    # The central-band boundary bars belong to the central zone.  Each outer
    # count excludes that shared boundary, preventing duplicate physical bars.
    edge_centre_mm = cover_mm + phi_mm / 2.0
    outer_centre_span_mm = (
        long_dimension_mm - short_dimension_mm
    ) / 2.0 - edge_centre_mm
    if outer_centre_span_mm <= 0:
        return None

    central_count = max(
        2,
        math.ceil(central_required_mm2 / _area(phi_mm)),
        math.ceil(short_dimension_mm / max_spacing_mm) + 1,
    )
    outer_count_each = max(
        1,
        math.ceil(outer_required_each_mm2 / _area(phi_mm)),
        math.ceil(outer_centre_span_mm / max_spacing_mm),
    )
    central_spacing_mm = short_dimension_mm / (central_count - 1)
    outer_spacing_mm = outer_centre_span_mm / outer_count_each
    central_clear_mm = central_spacing_mm - phi_mm
    outer_clear_mm = outer_spacing_mm - phi_mm
    if min(central_clear_mm, outer_clear_mm) + 1e-9 < minimum_clear_spacing_mm:
        return None

    return (
        FootingReinforcementZone(
            zone="central_band",
            width_mm=short_dimension_mm,
            required_area_mm2=central_required_mm2,
            provided_area_mm2=central_count * _area(phi_mm),
            bar_count=central_count,
            spacing_mm=central_spacing_mm,
            clear_spacing_mm=central_clear_mm,
        ),
        FootingReinforcementZone(
            zone="outer_band_each",
            width_mm=(long_dimension_mm - short_dimension_mm) / 2.0,
            required_area_mm2=outer_required_each_mm2,
            provided_area_mm2=outer_count_each * _area(phi_mm),
            bar_count=outer_count_each,
            spacing_mm=outer_spacing_mm,
            clear_spacing_mm=outer_clear_mm,
        ),
    )


def _end_anchorage_detail(
    *,
    arrangement: Literal["straight", "bend_90", "u_hook_180"],
    arrangement_was_explicit: bool,
    run_mm: float,
    column_parallel_mm: float,
    d_mm: float,
    nominal_cover_mm: float,
    phi_mm: int,
    fck: float,
    fy: float,
    bar_type: Literal["plain", "deformed"],
    internal_bend_radius_mm: float | None,
    extension_after_bend_mm: float | None,
    geometry_source_reference: str | None,
    geometry_source_is_approved: bool,
) -> tuple[FootingEndAnchorageDetailV1, float]:
    edge_axis_available_mm = (
        (run_mm - column_parallel_mm) / 2.0 - nominal_cover_mm - phi_mm / 2.0
    )
    if arrangement == "straight":
        straight_available_mm = max(0.0, edge_axis_available_mm)
        evaluated = evaluate_tension_bar_anchorage_v1(
            bar_dia=phi_mm,
            fck=fck,
            fy=fy,
            available_straight_length_mm=straight_available_mm,
            arrangement="straight",
            bar_type=bar_type,
        )
        geometry_fits = edge_axis_available_mm >= 0.0
        total_bar_length_mm = run_mm - 2.0 * nominal_cover_mm
        return (
            FootingEndAnchorageDetailV1(
                arrangement="straight",
                arrangement_was_explicit=arrangement_was_explicit,
                required_development_length_mm=(
                    evaluated.required_development_length_mm
                ),
                available_straight_length_mm=straight_available_mm,
                anchorage_value_mm=evaluated.anchorage_value_mm,
                total_available_development_length_mm=(
                    evaluated.total_available_development_length_mm
                ),
                shortfall_mm=evaluated.shortfall_mm,
                utilization_ratio=evaluated.utilization_ratio,
                anchorage_is_adequate=evaluated.is_adequate,
                bend_angle_degrees=None,
                internal_bend_radius_mm=None,
                centreline_bend_radius_mm=None,
                extension_after_bend_mm=None,
                bend_arc_length_mm=0.0,
                vertical_envelope_required_mm=0.0,
                vertical_envelope_available_mm=max(
                    0.0, d_mm - nominal_cover_mm - phi_mm / 2.0
                ),
                return_extension_available_mm=None,
                geometry_fits=geometry_fits,
                bounded_constructability_is_adequate=geometry_fits,
                geometry_source_reference=None,
                geometry_source_is_approved=False,
                clause_refs=evaluated.clause_refs,
                source_ids=_SOURCE_IDS,
            ),
            total_bar_length_mm,
        )

    assert internal_bend_radius_mm is not None
    assert extension_after_bend_mm is not None
    centreline_radius_mm = internal_bend_radius_mm + phi_mm / 2.0
    raw_straight_to_tangent_mm = edge_axis_available_mm - centreline_radius_mm
    straight_to_tangent_mm = max(0.0, raw_straight_to_tangent_mm)
    evaluated = evaluate_tension_bar_anchorage_v1(
        bar_dia=phi_mm,
        fck=fck,
        fy=fy,
        available_straight_length_mm=straight_to_tangent_mm,
        arrangement=arrangement,
        bar_type=bar_type,
    )
    vertical_available_mm = max(0.0, d_mm - nominal_cover_mm - phi_mm / 2.0)
    if arrangement == "bend_90":
        angle_degrees = 90
        bend_arc_length_mm = math.pi * centreline_radius_mm / 2.0
        vertical_required_mm = centreline_radius_mm + extension_after_bend_mm
        return_available_mm = None
        return_fits = True
    else:
        angle_degrees = 180
        bend_arc_length_mm = math.pi * centreline_radius_mm
        vertical_required_mm = 2.0 * centreline_radius_mm
        return_available_mm = max(0.0, edge_axis_available_mm)
        return_fits = extension_after_bend_mm <= return_available_mm + 1e-9
    geometry_fits = (
        raw_straight_to_tangent_mm >= -1e-9
        and vertical_required_mm <= vertical_available_mm + 1e-9
        and return_fits
    )
    straight_between_tangents_mm = max(
        0.0,
        run_mm - 2.0 * (nominal_cover_mm + phi_mm / 2.0 + centreline_radius_mm),
    )
    total_bar_length_mm = straight_between_tangents_mm + 2.0 * (
        bend_arc_length_mm + extension_after_bend_mm
    )
    return (
        FootingEndAnchorageDetailV1(
            arrangement=arrangement,
            arrangement_was_explicit=arrangement_was_explicit,
            required_development_length_mm=evaluated.required_development_length_mm,
            available_straight_length_mm=straight_to_tangent_mm,
            anchorage_value_mm=evaluated.anchorage_value_mm,
            total_available_development_length_mm=(
                evaluated.total_available_development_length_mm
            ),
            shortfall_mm=evaluated.shortfall_mm,
            utilization_ratio=evaluated.utilization_ratio,
            anchorage_is_adequate=evaluated.is_adequate,
            bend_angle_degrees=angle_degrees,
            internal_bend_radius_mm=internal_bend_radius_mm,
            centreline_bend_radius_mm=centreline_radius_mm,
            extension_after_bend_mm=extension_after_bend_mm,
            bend_arc_length_mm=bend_arc_length_mm,
            vertical_envelope_required_mm=vertical_required_mm,
            vertical_envelope_available_mm=vertical_available_mm,
            return_extension_available_mm=return_available_mm,
            geometry_fits=geometry_fits,
            bounded_constructability_is_adequate=(
                geometry_fits and geometry_source_is_approved
            ),
            geometry_source_reference=geometry_source_reference,
            geometry_source_is_approved=geometry_source_is_approved,
            clause_refs=evaluated.clause_refs,
            source_ids=_SOURCE_IDS,
        ),
        total_bar_length_mm,
    )


@clause(
    "34.2.3.1",
    "34.2.4.1",
    "34.3",
    "26.5.2.1",
    "26.3.2",
    "26.3.3",
    "26.2.1",
    "26.2.2.1",
    "34.4",
)
def detail_isolated_footing_bottom_steel(
    *,
    Pu_kN: float,
    L_mm: float,
    B_mm: float,
    column_L_mm: float,
    column_B_mm: float,
    D_mm: float,
    analysis_d_L_mm: float,
    analysis_d_B_mm: float,
    fck: float,
    fy: float,
    nominal_cover_mm: float,
    exposure_basis: str,
    exposure_is_approved: bool,
    aggregate_size_mm: float,
    lower_direction: Literal["L", "B"],
    upper_direction: Literal["L", "B"],
    permitted_diameters_mm: tuple[int, ...],
    bar_type: Literal["plain", "deformed"],
    load_transfer_result: LoadTransferResult,
    bottom_bar_end_arrangement: (
        Literal["straight", "bend_90", "u_hook_180", "bend_135", "mechanical"] | None
    ) = None,
    bend_internal_radius_mm: float | None = None,
    extension_after_bend_mm: float | None = None,
    bend_geometry_source_reference: str | None = None,
    bend_geometry_source_is_approved: bool = False,
) -> FootingDetailingResult:
    """Select two orthogonal full-length bottom-bar layers and end anchorage.

    Service pressure/SBC is not calculated here.  Missing engineering approval
    and unsupported arrangements return ``HOLD``. A complete but inadequate
    anchorage or physical-fit basis returns ``FAIL``. Missing arrangement input
    retains the legacy straight-bar behavior: adequate straight bars may pass,
    while an arrangement choice needed to close anchorage remains ``HOLD``.
    """
    if (
        load_transfer_result.supported_case != _LOAD_TRANSFER_SUPPORTED_CASE
        or not set(_SOURCE_IDS).issubset(load_transfer_result.source_ids)
        or not math.isclose(load_transfer_result.Pu_kN, Pu_kN, abs_tol=1e-9)
        or not math.isclose(
            load_transfer_result.loaded_area_A2_mm2,
            column_L_mm * column_B_mm,
            abs_tol=1e-6,
        )
    ):
        return _result(
            "HOLD",
            "Load-transfer receipt is stale or inconsistent with the detailing request.",
            load_transfer_result,
            lower_direction,
            upper_direction,
        )
    if not load_transfer_result.is_safe:
        return _result(
            "FAIL",
            "Accepted load-transfer result is unsafe; its dowels are retained and not redesigned.",
            load_transfer_result,
            lower_direction,
            upper_direction,
        )
    if not exposure_is_approved or not exposure_basis.strip():
        return _result(
            "HOLD",
            "An explicit approved exposure and cover basis is required.",
            load_transfer_result,
            lower_direction,
            upper_direction,
        )
    supported_material_pair = (fy == 250 and bar_type == "plain") or (
        fy in (415, 500) and bar_type == "deformed"
    )
    if fck not in _FCK or not supported_material_pair:
        return _result(
            "HOLD",
            "Material grade and bar-type pairing is outside this bounded detailing case.",
            load_transfer_result,
            lower_direction,
            upper_direction,
        )
    if {lower_direction, upper_direction} != {"L", "B"}:
        return _result(
            "HOLD",
            "Two orthogonal ordered bottom layers are required.",
            load_transfer_result,
            lower_direction,
            upper_direction,
        )
    if not permitted_diameters_mm or any(
        diameter not in _DIAMETERS for diameter in permitted_diameters_mm
    ):
        return _result(
            "HOLD",
            "Permitted diameters must be drawn from the bounded footing schedule.",
            load_transfer_result,
            lower_direction,
            upper_direction,
        )
    if bottom_bar_end_arrangement in {"bend_135", "mechanical"}:
        return _result(
            "HOLD",
            "The requested bottom-bar end arrangement is outside the supported straight, 90-degree bend and standard U-hook contract.",
            load_transfer_result,
            lower_direction,
            upper_direction,
        )
    arrangement: Literal["straight", "bend_90", "u_hook_180"]
    if bottom_bar_end_arrangement is None:
        arrangement = "straight"
    elif bottom_bar_end_arrangement == "straight":
        arrangement = "straight"
    elif bottom_bar_end_arrangement == "bend_90":
        arrangement = "bend_90"
    elif bottom_bar_end_arrangement == "u_hook_180":
        arrangement = "u_hook_180"
    else:  # pragma: no cover - defensive runtime typing boundary
        return _result(
            "HOLD",
            "The requested bottom-bar end arrangement is unsupported.",
            load_transfer_result,
            lower_direction,
            upper_direction,
        )
    arrangement_was_explicit = bottom_bar_end_arrangement is not None
    geometry_values = (
        bend_internal_radius_mm,
        extension_after_bend_mm,
        bend_geometry_source_reference,
    )
    if arrangement == "straight" and (
        any(value is not None for value in geometry_values)
        or bend_geometry_source_is_approved
    ):
        return _result(
            "HOLD",
            "Straight end anchorage must not carry a bend geometry basis.",
            load_transfer_result,
            lower_direction,
            upper_direction,
        )
    if arrangement != "straight" and (
        bend_internal_radius_mm is None
        or extension_after_bend_mm is None
        or not isinstance(bend_geometry_source_reference, str)
        or not bend_geometry_source_reference.strip()
        or not bend_geometry_source_is_approved
    ):
        return _result(
            "HOLD",
            "A complete approved bend radius, extension and geometry source reference are required for a bent or hooked arrangement.",
            load_transfer_result,
            lower_direction,
            upper_direction,
        )
    if arrangement != "straight":
        assert bend_internal_radius_mm is not None
        assert extension_after_bend_mm is not None
        if not _valid_positive(
            bend_internal_radius_mm=bend_internal_radius_mm,
            extension_after_bend_mm=extension_after_bend_mm,
        ):
            return _result(
                "FAIL",
                "Bend internal radius and extension must be finite positive dimensions.",
                load_transfer_result,
                lower_direction,
                upper_direction,
            )
    if (
        not _valid_positive(
            Pu_kN=Pu_kN,
            L_mm=L_mm,
            B_mm=B_mm,
            column_L_mm=column_L_mm,
            column_B_mm=column_B_mm,
            D_mm=D_mm,
            analysis_d_L_mm=analysis_d_L_mm,
            analysis_d_B_mm=analysis_d_B_mm,
            nominal_cover_mm=nominal_cover_mm,
            aggregate_size_mm=aggregate_size_mm,
        )
        or column_L_mm >= L_mm
        or column_B_mm >= B_mm
    ):
        return _result(
            "FAIL",
            "Plan, column, depth, cover, aggregate and analysis-depth inputs must be physically valid.",
            load_transfer_result,
            lower_direction,
            upper_direction,
        )
    if not math.isclose(
        analysis_d_L_mm,
        analysis_d_B_mm,
        rel_tol=0.0,
        abs_tol=1e-9,
    ):
        return _result(
            "HOLD",
            "A common maintained analysis depth is required for the current one-way-shear core.",
            load_transfer_result,
            lower_direction,
            upper_direction,
        )
    try:
        analysis_flexure = footing_flexure(
            Pu_kN,
            L_mm,
            B_mm,
            analysis_d_L_mm,
            column_L_mm,
            column_B_mm,
            fck,
            fy,
            overall_thickness_mm=D_mm,
        )
    except StructuralLibError:
        return _result(
            "FAIL",
            "The maintained analysis-depth flexural demand could not be satisfied.",
            load_transfer_result,
            lower_direction,
            upper_direction,
        )
    analysis_demands = {
        "L": analysis_flexure.Ast_L_mm2,
        "B": analysis_flexure.Ast_B_mm2,
    }

    candidates: list[
        tuple[
            tuple[float, int, int, tuple[int, int]],
            FootingDirectionDetail,
            FootingDirectionDetail,
            FootingOneWayShearResult,
            dict[str, float],
        ]
    ] = []
    implicit_arrangement_choice_required = False
    numeric_failure_found = False
    provided_pt_shear_failure_found = False
    failed_end_candidates: list[
        tuple[
            tuple[float, int, int, tuple[int, int]],
            FootingDirectionDetail,
            FootingDirectionDetail,
            bool,
            bool,
        ]
    ] = []

    for lower_phi in sorted(set(permitted_diameters_mm)):
        for upper_phi in sorted(set(permitted_diameters_mm)):
            phis = {lower_direction: lower_phi, upper_direction: upper_phi}
            depths = {
                lower_direction: D_mm - nominal_cover_mm - lower_phi / 2.0,
                upper_direction: D_mm - nominal_cover_mm - lower_phi - upper_phi / 2.0,
            }
            if (
                depths["L"] + 1e-9 < analysis_d_L_mm
                or depths["B"] + 1e-9 < analysis_d_B_mm
            ):
                numeric_failure_found = True
                continue
            try:
                flex_l = footing_flexure(
                    Pu_kN,
                    L_mm,
                    B_mm,
                    depths["L"],
                    column_L_mm,
                    column_B_mm,
                    fck,
                    fy,
                    overall_thickness_mm=D_mm,
                )
                flex_b = footing_flexure(
                    Pu_kN,
                    L_mm,
                    B_mm,
                    depths["B"],
                    column_L_mm,
                    column_B_mm,
                    fck,
                    fy,
                    overall_thickness_mm=D_mm,
                )
            except StructuralLibError:
                numeric_failure_found = True
                continue

            demands = {
                "L": (flex_l.Mu_L_kNm, flex_l.Ast_L_mm2),
                "B": (flex_b.Mu_B_kNm, flex_b.Ast_B_mm2),
            }
            details: dict[Literal["L", "B"], FootingDirectionDetail] = {}
            pair_anchorage_failure = False
            pair_geometry_failure = False
            pair_numeric_failure = False

            for direction in ("L", "B"):
                typed_direction: Literal["L", "B"] = direction
                phi = phis[typed_direction]
                d_mm = depths[typed_direction]
                run_mm, distribution_width_mm, column_parallel_mm = (
                    (L_mm, B_mm, column_L_mm)
                    if typed_direction == "L"
                    else (B_mm, L_mm, column_B_mm)
                )
                if nominal_cover_mm + 1e-9 < max(50.0, float(phi)):
                    pair_numeric_failure = True
                    break
                if phi > D_mm / 8.0 + 1e-9:
                    pair_numeric_failure = True
                    break

                Mu_kNm, flexure_area_mm2 = demands[typed_direction]
                minimum_area_mm2 = (
                    (0.0015 if fy == 250 else 0.0012) * distribution_width_mm * D_mm
                )
                analysis_screening_area_mm2 = analysis_demands[typed_direction]
                required_area_mm2 = max(
                    flexure_area_mm2,
                    analysis_screening_area_mm2,
                    minimum_area_mm2,
                )
                max_spacing_mm = min(3.0 * d_mm, 300.0)
                minimum_clear_spacing_mm = max(
                    float(phi), aggregate_size_mm + 5.0, 25.0
                )

                is_rectangular_short_direction = abs(L_mm - B_mm) > 1e-9 and (
                    (typed_direction == "L" and L_mm < B_mm)
                    or (typed_direction == "B" and B_mm < L_mm)
                )
                if is_rectangular_short_direction:
                    zones = _central_band_zones(
                        long_dimension_mm=max(L_mm, B_mm),
                        short_dimension_mm=min(L_mm, B_mm),
                        cover_mm=nominal_cover_mm,
                        phi_mm=phi,
                        required_area_mm2=required_area_mm2,
                        max_spacing_mm=max_spacing_mm,
                        minimum_clear_spacing_mm=minimum_clear_spacing_mm,
                    )
                    layout: Literal["uniform", "central_band"] = "central_band"
                else:
                    zones = _uniform_zone(
                        distribution_width_mm=distribution_width_mm,
                        cover_mm=nominal_cover_mm,
                        phi_mm=phi,
                        required_area_mm2=required_area_mm2,
                        max_spacing_mm=max_spacing_mm,
                        minimum_clear_spacing_mm=minimum_clear_spacing_mm,
                    )
                    layout = "uniform"
                if zones is None:
                    pair_numeric_failure = True
                    break

                end_anchorage, total_bar_length_mm = _end_anchorage_detail(
                    arrangement=arrangement,
                    arrangement_was_explicit=arrangement_was_explicit,
                    run_mm=run_mm,
                    column_parallel_mm=column_parallel_mm,
                    d_mm=d_mm,
                    nominal_cover_mm=nominal_cover_mm,
                    phi_mm=phi,
                    fck=fck,
                    fy=fy,
                    bar_type=bar_type,
                    internal_bend_radius_mm=bend_internal_radius_mm,
                    extension_after_bend_mm=extension_after_bend_mm,
                    geometry_source_reference=bend_geometry_source_reference,
                    geometry_source_is_approved=bend_geometry_source_is_approved,
                )
                ld_mm = calculate_development_length(phi, fck, fy, bar_type)
                if not end_anchorage.anchorage_is_adequate:
                    pair_anchorage_failure = True
                if not end_anchorage.bounded_constructability_is_adequate:
                    pair_geometry_failure = True

                bar_count = sum(
                    zone.bar_count * (2 if zone.zone == "outer_band_each" else 1)
                    for zone in zones
                )
                provided_area_mm2 = sum(
                    zone.provided_area_mm2
                    * (2 if zone.zone == "outer_band_each" else 1)
                    for zone in zones
                )
                details[typed_direction] = FootingDirectionDetail(
                    direction=typed_direction,
                    layer=("lower" if typed_direction == lower_direction else "upper"),
                    layout=layout,
                    diameter_mm=phi,
                    physical_effective_depth_mm=d_mm,
                    analysis_effective_depth_mm=(
                        analysis_d_L_mm if typed_direction == "L" else analysis_d_B_mm
                    ),
                    Mu_kNm=Mu_kNm,
                    flexure_result_area_mm2=flexure_area_mm2,
                    analysis_screening_area_mm2=analysis_screening_area_mm2,
                    minimum_area_mm2=minimum_area_mm2,
                    required_area_mm2=required_area_mm2,
                    provided_area_mm2=provided_area_mm2,
                    bar_count=bar_count,
                    spacing_mm=max(zone.spacing_mm for zone in zones),
                    clear_spacing_mm=min(zone.clear_spacing_mm for zone in zones),
                    max_spacing_mm=max_spacing_mm,
                    minimum_clear_spacing_mm=minimum_clear_spacing_mm,
                    max_diameter_mm=D_mm / 8.0,
                    development_length_mm=ld_mm,
                    development_length_unrounded_mm=(
                        end_anchorage.required_development_length_mm
                    ),
                    straight_anchorage_available_each_end_mm=(
                        end_anchorage.available_straight_length_mm
                    ),
                    straight_bar_length_mm=(
                        total_bar_length_mm
                        - 2.0
                        * (
                            end_anchorage.bend_arc_length_mm
                            + (end_anchorage.extension_after_bend_mm or 0.0)
                        )
                    ),
                    total_bar_length_mm=total_bar_length_mm,
                    end_anchorage=end_anchorage,
                    zones=zones,
                )

            if pair_numeric_failure:
                numeric_failure_found = True
                continue
            if len(details) != 2:
                numeric_failure_found = True
                continue
            pair = (lower_phi, upper_phi)
            sort_key = (
                details["L"].provided_area_mm2 + details["B"].provided_area_mm2,
                details["L"].bar_count + details["B"].bar_count,
                max(pair),
                pair,
            )
            if pair_anchorage_failure or pair_geometry_failure:
                failed_end_candidates.append(
                    (
                        sort_key,
                        details["L"],
                        details["B"],
                        pair_anchorage_failure,
                        pair_geometry_failure,
                    )
                )
                if pair_anchorage_failure:
                    if not arrangement_was_explicit:
                        implicit_arrangement_choice_required = True
                continue

            l_detail = details["L"]
            b_detail = details["B"]
            actual_provided_pt_percent = {
                "L": l_detail.provided_area_mm2 / (B_mm * analysis_d_L_mm) * 100.0,
                "B": b_detail.provided_area_mm2 / (L_mm * analysis_d_B_mm) * 100.0,
            }
            try:
                final_one_way_shear = footing_one_way_shear(
                    Pu_kN=Pu_kN,
                    L_mm=L_mm,
                    B_mm=B_mm,
                    d_mm=analysis_d_L_mm,
                    a_mm=column_L_mm,
                    b_mm=column_B_mm,
                    fck=fck,
                    pt_L_percent=actual_provided_pt_percent["L"],
                    pt_B_percent=actual_provided_pt_percent["B"],
                )
            except StructuralLibError:
                numeric_failure_found = True
                continue
            if not final_one_way_shear.is_safe:
                provided_pt_shear_failure_found = True
                continue
            candidates.append(
                (
                    sort_key,
                    l_detail,
                    b_detail,
                    final_one_way_shear,
                    actual_provided_pt_percent,
                )
            )

    if not candidates:
        failed_l: FootingDirectionDetail | None = None
        failed_b: FootingDirectionDetail | None = None
        selected_anchorage_failure = False
        selected_geometry_failure = False
        if failed_end_candidates:
            (
                _,
                failed_l,
                failed_b,
                selected_anchorage_failure,
                selected_geometry_failure,
            ) = min(failed_end_candidates, key=lambda candidate: candidate[0])
        failed_lower = failed_l if lower_direction == "L" else failed_b
        failed_upper = failed_b if upper_direction == "B" else failed_l
        if implicit_arrangement_choice_required:
            return _result(
                "HOLD",
                "A numerically feasible bar grid needs an explicit supported end arrangement to close anchorage.",
                load_transfer_result,
                lower_direction,
                upper_direction,
                lower=failed_lower,
                upper=failed_upper,
            )
        if selected_geometry_failure:
            failure_reason = (
                "No permitted schedule fits the approved bend/hook radius, "
                "extension and available footing envelope."
            )
        elif selected_anchorage_failure:
            failure_reason = (
                "No permitted schedule provides the exact required development "
                "length with the selected end arrangement."
            )
        elif provided_pt_shear_failure_found:
            failure_reason = (
                "No permitted buildable schedule passes one-way shear using its "
                "actual provided directional reinforcement percentages."
            )
        elif numeric_failure_found:
            failure_reason = (
                "No permitted straight-bar arrangement satisfies physical depth, "
                "cover, spacing and diameter checks."
            )
        else:
            failure_reason = "No maintained detailing candidate was available."
        return _result(
            "FAIL",
            failure_reason,
            load_transfer_result,
            lower_direction,
            upper_direction,
            lower=failed_lower,
            upper=failed_upper,
        )

    (
        _,
        l_detail,
        b_detail,
        final_one_way_shear,
        actual_provided_pt_percent,
    ) = min(candidates, key=lambda candidate: candidate[0])
    return _result(
        "PASS",
        "All maintained bounded detailing checks pass; qualified structural-engineering review remains required.",
        load_transfer_result,
        lower_direction,
        upper_direction,
        lower=l_detail if lower_direction == "L" else b_detail,
        upper=b_detail if upper_direction == "B" else l_detail,
        actual_provided_pt_percent=actual_provided_pt_percent,
        final_one_way_shear=final_one_way_shear,
    )
