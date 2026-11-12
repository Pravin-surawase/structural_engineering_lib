"""Compose local positioned cage and biaxial checks at one supplied station."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, replace
from typing import Any

from structural_lib.codes.is456.column._common import _calculate_puz
from structural_lib.codes.is456.column._strain_compatibility import (
    COLUMN_SECTION_METHOD,
)
from structural_lib.codes.is456.column.axial import classify_column, effective_length
from structural_lib.codes.is456.column.detailing import check_longitudinal_limits
from structural_lib.codes.is456.column.positioned_biaxial import (
    PositionedColumnBar,
    positioned_biaxial_strength,
)
from structural_lib.codes.is456.column.positioned_cage import (
    PositionedCrossTie,
    PositionedTie,
    PositionedTiePath,
    check_positioned_cage,
)
from structural_lib.core.data_types import ColumnClassification, EndCondition
from structural_lib.core.result_contract import EngineeringStatus, StructuralIssueV1
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
)
from structural_lib.services.column_tied_member import _render_rectangular_section
from structural_lib.services.contracts.column_member import (
    PositionedRectangularColumnInputV1,
)

_WORKFLOW = "is456.column.positioned-rectangular-member-check/v1"
_STRENGTH = "IS 456:2000 Cl. 25.4, 38.1, 39.1, 39.5 and 39.6"


def check_positioned_rectangular_member(
    request: PositionedRectangularColumnInputV1,
) -> CanonicalFamilyResultV1[dict[str, Any]]:
    """Report independent strength and local restraint for the supplied cage."""
    require_request_type(request, PositionedRectangularColumnInputV1)
    geometry, actions = request.geometry, request.actions
    steel, materials = request.reinforcement, request.materials
    bars = tuple(PositionedColumnBar(**bar.model_dump()) for bar in steel.bars)
    area = sum(bar.area_mm2 for bar in bars)
    ratio, minimum_ok, maximum_ok, _ = check_longitudinal_limits(
        geometry.b_mm * geometry.D_mm, area
    )
    checks: list[dict[str, Any]] = []
    issues: list[StructuralIssueV1] = []

    def record(
        code: str, status: EngineeringStatus, path: str, message: str, **values: Any
    ) -> None:
        checks.append(
            {"code": code, "status": status, "path": path, "message": message, **values}
        )
        if status is not EngineeringStatus.PASS:
            issues.append(StructuralIssueV1(code, path, message))

    le = effective_length(
        geometry.unsupported_length_mm, EndCondition[geometry.end_condition]
    )
    short = all(
        classify_column(le, dimension) is ColumnClassification.SHORT
        for dimension in (geometry.D_mm, geometry.b_mm)
    )
    record(
        "COLUMN.SHORT_PROFILE",
        EngineeringStatus.PASS if short else EngineeringStatus.HOLD,
        "geometry",
        "Both effective-length ratios must be below 12.",
        effective_length_mm=le,
        slenderness_x=le / geometry.D_mm,
        slenderness_y=le / geometry.b_mm,
        source_reference="IS 456:2000 Cl. 25.1.2 and Cl. 25.2 Table 28",
    )
    materials_ok = materials.fck_nmm2 <= 60
    if not materials_ok:
        record(
            "COLUMN.CONCRETE_PROFILE",
            EngineeringStatus.HOLD,
            "materials",
            "This profile admits concrete grades up to M60.",
        )
    ratio_ok = minimum_ok and maximum_ok
    record(
        "COLUMN.LONGITUDINAL_RATIO",
        EngineeringStatus.PASS if ratio_ok else EngineeringStatus.FAIL,
        "reinforcement.bars",
        "Use the supported 0.8–4% longitudinal ratio.",
        actual=ratio,
        source_reference="IS 456:2000 Cl. 26.5.3.1 and supported analysis profile",
    )
    cage = {
        "bars": tuple({**asdict(bar), "area_mm2": bar.area_mm2} for bar in bars),
        "tie_centreline_width_mm": 0.0,
        "tie_centreline_depth_mm": 0.0,
        "supplied_steel_area_mm2": area,
        "steel_ratio": ratio,
    }
    paths: tuple[PositionedTiePath, ...] = ()
    tie = steel.tie
    if tie is None:
        record(
            "COLUMN.TIE_REQUIRED",
            EngineeringStatus.HOLD,
            "reinforcement.tie",
            "An actual perimeter hoop is required to check restraint.",
        )
    else:
        detail = check_positioned_cage(
            b_mm=geometry.b_mm,
            D_mm=geometry.D_mm,
            bars=bars,
            nominal_cover_mm=steel.nominal_cover_mm,
            required_cover_mm=steel.project_required_cover_mm,
            aggregate_size_mm=steel.aggregate_size_mm,
            required_hoop_bend_mm=steel.project_required_bend_radius_mm,
            required_link_bend_mm=steel.project_required_cross_tie_bend_radius_mm,
            hoop=PositionedTie(
                tie.tie_id,
                tie.diameter_mm,
                tie.internal_bend_radius_mm,
                tie.hook_angle_deg,
                tie.hook_tail_mm,
            ),
            hoop_closed=tie.closed,
            pitch_mm=tie.spacing_mm,
            cross_ties=tuple(
                PositionedCrossTie(**link.model_dump()) for link in steel.cross_ties
            ),
        )
        cage["tie_centreline_width_mm"] = detail.tie_centreline_width_mm
        cage["tie_centreline_depth_mm"] = detail.tie_centreline_depth_mm
        cage["tie_centreline_bend_radius_mm"] = (
            tie.internal_bend_radius_mm + tie.diameter_mm / 2
        )
        paths = detail.cross_ties
        for check in detail.checks:
            record(
                check.code,
                EngineeringStatus.PASS if check.passed else EngineeringStatus.FAIL,
                "reinforcement",
                check.code.removeprefix("COLUMN.").replace("_", " ").lower(),
                actual=check.actual,
                limit=check.limit,
                source_reference=check.source_reference,
            )
        if detail.unrestrained_ids:
            record(
                "COLUMN.CROSS_TIE_REQUIRED",
                EngineeringStatus.HOLD,
                "reinforcement.cross_ties",
                "Each outer intermediate bar needs a checked link.",
                unrestrained_ids=detail.unrestrained_ids,
            )

    restraint_checks = [
        check["status"] for check in checks if check["path"].startswith("reinforcement")
    ]
    restraint_status = (
        EngineeringStatus.FAIL
        if EngineeringStatus.FAIL in restraint_checks
        else (
            EngineeringStatus.HOLD
            if EngineeringStatus.HOLD in restraint_checks
            else EngineeringStatus.PASS
        )
    )
    strength = None
    strength_status = EngineeringStatus.HOLD
    if short and materials_ok and ratio_ok:
        puz = _calculate_puz(
            geometry.b_mm, geometry.D_mm, materials.fck_nmm2, materials.fy_nmm2, area
        )
        if actions.pu_kn >= puz:
            strength_status = EngineeringStatus.FAIL
            record(
                "COLUMN.AXIAL_LIMIT",
                strength_status,
                "actions.pu_kn",
                "The applied compression reaches the Cl. 39.6 axial limit.",
                actual=actions.pu_kn,
                limit=puz,
                source_reference=_STRENGTH,
            )
        else:
            strength = positioned_biaxial_strength(
                b_mm=geometry.b_mm,
                D_mm=geometry.D_mm,
                unsupported_length_mm=geometry.unsupported_length_mm,
                pu_kn=actions.pu_kn,
                mx_knm=actions.mx_knm,
                my_knm=actions.my_knm,
                fck_nmm2=materials.fck_nmm2,
                fy_nmm2=materials.fy_nmm2,
                bars=bars,
            )
            if strength is None:
                record(
                    "COLUMN.PM_BASIS",
                    EngineeringStatus.HOLD,
                    "actions",
                    "A unique converged section ray could not be established for all checks.",
                    source_reference=_STRENGTH,
                )
            else:
                strength_status = (
                    EngineeringStatus.PASS
                    if strength.governing_ratio <= 1
                    else EngineeringStatus.FAIL
                )
                record(
                    "COLUMN.PM_STRENGTH",
                    strength_status,
                    "actions",
                    "The supplied contour, equilibrium ray and separate minimum-eccentricity cases must pass.",
                    actual=strength.governing_ratio,
                    limit=1,
                    source_reference=_STRENGTH,
                )

    statuses = {check["status"] for check in checks} | {strength_status}
    status = (
        EngineeringStatus.FAIL
        if EngineeringStatus.FAIL in statuses
        else (
            EngineeringStatus.HOLD
            if EngineeringStatus.HOLD in statuses
            else EngineeringStatus.PASS
        )
    )
    calculation = {
        "scope": "Short braced positioned rectangle at one supplied station",
        "check_station_mm": actions.check_station_mm,
        "effective_length_mm": le,
        "cage": cage,
        "cross_ties": tuple(asdict(path) for path in paths),
        "section_quantities": {
            "longitudinal_count_by_diameter_mm": dict(
                Counter(f"{bar.diameter_mm:g}" for bar in bars)
            ),
            "perimeter_count_per_pitch": int(tie is not None),
            "cross_tie_count_per_pitch": len(steel.cross_ties),
        },
        "restraint_status": restraint_status,
        "strength_status": strength_status,
        "strength": asdict(strength) if strength is not None else None,
        "checks": checks,
    }
    result = canonical_family_result(
        request,
        calculation,
        workflow_id=_WORKFLOW,
        engineering_status=status,
        assumptions=(
            "Positive Mx compresses the top and positive My compresses the left.",
            "All longitudinal bars use the supplied common grade and their actual diameters and centres.",
            "The hoop and open links occupy separate transverse planes. The hoop closure follows the supplied local schedule.",
        ),
        limitations=(
            "One short braced section with aligned opposite-face open links.",
            "Section quantities and link paths do not determine member-wide fabrication, splices or joint anchorage.",
            "Section strength is reported independently of local restraint. The combined engineering status governs use.",
        ),
        provenance=(
            COLUMN_SECTION_METHOD,
            _STRENGTH,
            "IS 456:2000 Cl. 26.2.2.4(b), 26.3.2, 26.4 and 26.5.3.2 Fig. 9–10",
        ),
    )
    return replace(result, envelope=replace(result.envelope, issues=tuple(issues)))


def render_positioned_rectangular_member_html(
    result: CanonicalFamilyResultV1[dict[str, Any]],
) -> str:
    """Render a positioned member result and its checked paths."""
    request = result.request
    if result.workflow_id != _WORKFLOW or not isinstance(
        request, PositionedRectangularColumnInputV1
    ):
        raise TypeError("A positioned rectangular member result is required")
    return _render_rectangular_section(
        result,
        request.geometry,
        request.actions,
        capacity_keys=(
            "x_negative" if request.actions.mx_knm < 0 else "x_positive",
            "y_negative" if request.actions.my_knm < 0 else "y_positive",
        ),
    )
