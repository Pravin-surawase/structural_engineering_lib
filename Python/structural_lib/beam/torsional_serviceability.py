"""Bound, short-term torsion and time-dependent flexural service evidence.

This ordinary demonstration admits transient equilibrium torsion, not sustained
torsion, arbitrary histories, or absolute supporting-system displacement.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from structural_lib.codes.is456.beam.torsion_serviceability import (
    cracked_service_section,
    lampert_cracked_stiffness,
    shrinkage_upper_bound,
    uniform_flexural_deflection,
    wsm_torsion_row,
)

from .analysis import ACTION_NORMALIZE_OPERATION
from .physical_torsion import (
    ClosedLinkDetailRequest,
    TorsionSupportTransferRequest,
    check_closed_link_detail,
    check_torsion_support_transfer,
)
from .reinforcement import Face
from .semantics import (
    Diagnostic,
    EngineeringState,
    OperationResult,
    Provenance,
    completed_result,
    effective_inputs,
    not_evaluated_result,
    rejected_result,
)
from .serviceability import (
    CalculatedDeflectionBasis,
    CrackWidthCheckRequest,
    CrackWidthLimitRequest,
    DeflectionCheckRequest,
    DeflectionCriterion,
    DeflectionLimitRequest,
    DeflectionMethod,
    ExposureClass,
    check_crack_width,
    check_deflection,
)

TORSIONAL_SERVICEABILITY_OPERATION = "is456.beam.torsional_serviceability.check/v1"
TORSIONAL_SERVICEABILITY_REVISION = "is456-bruun-transient-torsion-d3-v1"


@dataclass(frozen=True)
class TorsionServiceHistory:
    permanent_load_n_per_mm: float
    permanent_eccentricity_mm: float
    imposed_load_n_per_mm: float
    imposed_eccentricity_mm: float
    ultimate_load_factor: float
    age_at_permanent_loading_days: float
    finish_installation_age_days: float
    assessment_age_days: float
    imposed_application_age_days: float | None
    imposed_assessment_age_days: float | None
    relative_humidity_percent: float
    imposed_load_is_transient: bool
    shrinkage_is_uniform: bool
    temperature_effects_applicable: bool
    receiver_end_boundary: str
    reference: str


@dataclass(frozen=True)
class TorsionalServiceabilityRequest:
    profile_id: str
    member_id: str
    reinforcement_revision_id: str
    support_transfer: TorsionSupportTransferRequest
    closed_links: ClosedLinkDetailRequest
    service_actions: OperationResult
    permanent_actions: OperationResult
    history: TorsionServiceHistory | None
    edge_offset_from_section_centre_mm: float


def _diagnostic(code: str, message: str) -> Diagnostic:
    return Diagnostic(
        code,
        "error",
        message,
        TORSIONAL_SERVICEABILITY_OPERATION,
        "service_basis",
        "LIB-027-D3",
        "Supply the named current service/model evidence and rerun the member.",
    )


def _passed(result: OperationResult) -> bool:
    return (
        result.execution == "completed"
        and result.engineering == "pass"
        and result.freshness == "current"
        and result.completeness == "complete_for_scope"
    )


def _history_gap(history: TorsionServiceHistory | None) -> str | None:
    if history is None or not history.reference:
        return "An explicit load decomposition, time history and model reference are required."
    if not history.imposed_load_is_transient:
        return "The cracked torsion model does not qualify sustained imposed torque."
    if (
        not math.isfinite(history.permanent_eccentricity_mm)
        or history.permanent_eccentricity_mm != 0
    ):
        return "Nonzero permanent torque requires an independently qualified torsional creep method."
    if (
        history.imposed_application_age_days is None
        or history.imposed_assessment_age_days is None
        or not math.isfinite(history.imposed_application_age_days)
        or not math.isfinite(history.imposed_assessment_age_days)
        or history.imposed_application_age_days < history.finish_installation_age_days
        or history.imposed_application_age_days != history.imposed_assessment_age_days
        or history.imposed_assessment_age_days != history.assessment_age_days
    ):
        return "This torsion model requires an explicit immediate Q assessment at application, after finishes; finite-duration sustained effects are unqualified."
    if (
        history.age_at_permanent_loading_days != 28
        or not history.shrinkage_is_uniform
        or history.temperature_effects_applicable
    ):
        return "This time basis admits 28-day permanent loading and uniform shrinkage without applicable thermal actions."
    if history.receiver_end_boundary != "identical_pinned_receivers_zero_settlement":
        return "The same-edge chord needs the declared identical receiver boundary, not an assumed rigid primary support."
    return None


def _receiver_symmetry(request: TorsionSupportTransferRequest) -> bool:
    if len(request.supports) != 2:
        return False
    first, second = request.supports
    return (
        first.receiver_section == second.receiver_section
        and first.receiver_links == second.receiver_links
        and tuple(
            (p.receiver_station_mm, p.upward_reaction_kn) for p in first.bearing_lines
        )
        == tuple(
            (p.receiver_station_mm, p.upward_reaction_kn) for p in second.bearing_lines
        )
        and first.receiver_analysis.nodes == second.receiver_analysis.nodes
        and first.receiver_analysis.elements == second.receiver_analysis.elements
        and first.receiver_analysis.point_loads == second.receiver_analysis.point_loads
        and first.receiver_topology.local_axes.e1
        == second.receiver_topology.local_axes.e1
        and first.receiver_topology.local_axes.e2
        == second.receiver_topology.local_axes.e2
        and first.receiver_topology.local_axes.e3
        == second.receiver_topology.local_axes.e3
        and all(
            n.vertical_restraint
            and not n.rotation_restraint
            and n.vertical_displacement_mm == 0
            for support in request.supports
            for n in support.receiver_analysis.nodes
        )
    )


def _action_gap(
    snapshot: OperationResult,
    request: TorsionalServiceabilityRequest,
    load: float,
    torque_intensity: float,
    span: float,
) -> str | None:
    if (
        not _passed(snapshot)
        or snapshot.operation_semantic_id != ACTION_NORMALIZE_OPERATION
    ):
        return "Current complete normalized actions are required for each separate load case."
    rows = snapshot.outputs.get("rows", ())
    stations = {r["object_station_mm"] for r in rows}
    section = request.support_transfer.primary_section
    offset = (
        abs(torque_intensity / load)
        * (1 + section.depth_mm / section.web_width_mm)
        / 1.7
        if load
        else 0.0
    )
    for critical in (0.0, span / 2, span, span / 2 - offset, span / 2 + offset):
        if not any(
            math.isclose(x, critical, abs_tol=1e-8, rel_tol=0) for x in stations
        ):
            return "Service rows omit an end, midspan or exact concurrent equivalent-moment peak."
    if len({r["load_case_id"] for r in rows}) != 1:
        return "Each snapshot must contain one concurrent service load case."
    for row in rows:
        x = row["object_station_mm"]
        expected = (
            load * (span / 2 - x),
            load * x * (span - x) / 2,
            torque_intensity * (span / 2 - x),
        )
        actual = (row["v2_n"], row["m3_nmm"], row["t_nmm"])
        if (
            row["member_id"] != request.member_id
            or row["axis_id"]
            != request.support_transfer.primary_topology.local_axes.axis_id
            or row["concurrency"] != "static_concurrent"
            or not 0 <= x <= span
            or any(row[key] != 0 for key in ("p_n", "v3_n", "m2_nmm"))
            or not all(
                math.isclose(a, e, abs_tol=1e-6, rel_tol=1e-12)
                for a, e in zip(actual, expected, strict=True)
            )
        ):
            return "Actions must reconstruct the declared unfactored component loads on the same member and axes."
    return None


def _profile_gap(request: TorsionalServiceabilityRequest) -> str | None:
    transfer = request.support_transfer
    section = transfer.primary_section
    bars = section.bars
    arrangement = request.closed_links.arrangement
    if (
        request.profile_id != transfer.profile_id
        or request.member_id != transfer.member_id
        or request.reinforcement_revision_id != transfer.reinforcement_revision_id
        or section.concrete_strength_n_per_mm2 != 25
        or section.steel_yield_strength_n_per_mm2 != 415
        or len(bars) != 4
        or len(transfer.primary_topology.spans) != 1
        or len(transfer.primary_topology.spans[0].section_regions) != 1
        or request.closed_links.paths != transfer.primary_paths
        or request.closed_links.link.steel_yield_strength_n_per_mm2 != 415
        or request.closed_links.link.legs_v2 != 2
        or request.closed_links.link.legs_v3 != 2
    ):
        return "The named ordinary M25/Fe415 four-corner two-leg physical profile is required."
    xs, ys = sorted({p.x_from_left_mm for p in bars}), sorted(
        {p.y_from_top_mm for p in bars}
    )
    if (
        len(xs) != 2
        or len(ys) != 2
        or {(p.x_from_left_mm, p.y_from_top_mm) for p in bars}
        != {(x, y) for x in xs for y in ys}
        or len({p.diameter_mm for p in bars}) != 1
        or not math.isclose(sum(xs), section.web_width_mm, abs_tol=1e-8)
        or not math.isclose(sum(ys), section.depth_mm, abs_tol=1e-8)
        or {p.bar_id for p in arrangement.bars} != {p.bar_id for p in bars}
    ):
        return "Equal symmetric four-corner bars are required for the two-face service model."
    return None


def _deflection_result(
    request: TorsionalServiceabilityRequest,
    *,
    span: float,
    code_span: float,
    initial: float,
    permanent: float,
    creep: float,
    shrinkage: float,
    edge: float,
) -> OperationResult:
    history = request.history
    assert history is not None
    section = request.support_transfer.primary_section
    rows = request.service_actions.outputs["rows"]
    permanent_rows = request.permanent_actions.outputs["rows"]
    return check_deflection(
        DeflectionCheckRequest(
            request.profile_id,
            DeflectionMethod.CALCULATED_COMPONENTS,
            calculated=CalculatedDeflectionBasis(
                request.service_actions.result_id,
                tuple(r["row_id"] for r in rows),
                tuple(r["row_id"] for r in permanent_rows),
                request.service_actions.calculation_id,
                request.reinforcement_revision_id,
                code_span,
                initial + edge,
                permanent,
                creep / permanent,
                shrinkage,
                history.finish_installation_age_days,
                permanent,
                history.age_at_permanent_loading_days,
                history.assessment_age_days,
                history.assessment_age_days - history.age_at_permanent_loading_days,
                history.relative_humidity_percent,
                section.web_width_mm
                * section.depth_mm
                / (section.web_width_mm + section.depth_mm),
                f"Fully cracked actual-bar Icr; conservative {span:g}mm analysis span; transient Lampert edge displacement",
                "Zero tension-stiffening credit; same physical edge support chord",
                "IS456 C4: re-solved permanent section at Ec/(1+1.6); ultimate creep upper bound",
                "IS456 C3: single-face equivalent ignores beneficial compression steel; all shrinkage counted after finishes",
            ),
            total_limit=DeflectionLimitRequest(
                request.profile_id, code_span, DeflectionCriterion.TOTAL_FINAL
            ),
            after_finishes_limit=DeflectionLimitRequest(
                request.profile_id, code_span, DeflectionCriterion.AFTER_FINISHES
            ),
        )
    )


def check_torsional_serviceability(
    request: TorsionalServiceabilityRequest,
) -> OperationResult:
    """Qualify the explicit transient-torsion service profile and bound leaves.

    Deflection is relative to the same physical edge support chord. Receiver
    end supports are modeled pinned at zero settlement; this is an explicit
    demonstration boundary, not evidence about a real foundation. Equal
    receiver models preserve equal support rotations, which cancel in the
    chord-relative twist. Missing or changed boundary evidence retains HOLD.
    """
    op = TORSIONAL_SERVICEABILITY_OPERATION
    inputs = effective_inputs(request=request)
    provenance = Provenance(
        TORSIONAL_SERVICEABILITY_REVISION,
        TORSIONAL_SERVICEABILITY_REVISION,
        (
            "IS456:2000 through Amendment6; 6.2.3-6.2.5,23.2,AnnexC,AnnexF; AnnexB5/B6,Tables21/22/24",
            "Bruun/Kuan/Bentz2020 DOI10.14359/51728290; Eq3 and worked example pp53,60: cubic corner area",
            "Transient equilibrium torsion; indirect AnnexB stress/detail crack control, not torsional crack width",
        ),
    )
    gap = _history_gap(request.history) or _profile_gap(request)
    if gap:
        return not_evaluated_result(
            op, inputs, _diagnostic("SLS.BASIS_UNQUALIFIED", gap), provenance=provenance
        )
    history = request.history
    assert history is not None
    numbers = (
        history.permanent_load_n_per_mm,
        history.imposed_load_n_per_mm,
        history.imposed_eccentricity_mm,
        history.permanent_eccentricity_mm,
        history.ultimate_load_factor,
        history.finish_installation_age_days,
        history.assessment_age_days,
        history.relative_humidity_percent,
        request.edge_offset_from_section_centre_mm,
    )
    if (
        not all(math.isfinite(x) for x in numbers)
        or history.permanent_load_n_per_mm <= 0
        or history.imposed_load_n_per_mm < 0
        or history.ultimate_load_factor <= 1
        or not 28 <= history.finish_installation_age_days < history.assessment_age_days
        or not 0 < history.relative_humidity_percent <= 100
    ):
        return rejected_result(
            op,
            inputs,
            (
                _diagnostic(
                    "SLS.INPUT",
                    "Finite loads, chronological history and material environment are required.",
                ),
            ),
            provenance=provenance,
        )
    transfer = request.support_transfer
    section = transfer.primary_section
    b, D = section.web_width_mm, section.depth_mm
    if (
        abs(request.edge_offset_from_section_centre_mm) > b / 2
        or abs(history.imposed_eccentricity_mm) > b / 2
    ):
        return rejected_result(
            op,
            inputs,
            (
                _diagnostic(
                    "SLS.PHYSICAL_POINT",
                    "The declared load line and checked edge must lie on the actual section.",
                ),
            ),
            provenance=provenance,
        )
    physical = check_torsion_support_transfer(transfer)
    hooks = check_closed_link_detail(request.closed_links)
    if not _passed(physical) or not _passed(hooks):
        return not_evaluated_result(
            op,
            inputs,
            _diagnostic(
                "SLS.PHYSICAL_EVIDENCE",
                "Current support transfer and actual hook/cage evidence are required.",
            ),
            provenance=provenance,
        )
    if not _receiver_symmetry(transfer):
        return not_evaluated_result(
            op,
            inputs,
            _diagnostic(
                "SLS.SUPPORT_DATUM",
                "The declared common-rotation receiver model is not symmetric.",
            ),
            provenance=provenance,
        )
    supports = sorted(transfer.primary_topology.supports, key=lambda s: s.centre_x_mm)
    span = supports[-1].centre_x_mm - supports[0].centre_x_mm
    if (
        supports[0].centre_x_mm != 0
        or request.closed_links.required_start_mm > 0
        or request.closed_links.required_end_mm < span
    ):
        return not_evaluated_result(
            op,
            inputs,
            _diagnostic(
                "SLS.PHYSICAL_SCOPE",
                "The one-span model and actual links must cover the whole service member.",
            ),
            provenance=provenance,
        )
    total_load = history.permanent_load_n_per_mm + history.imposed_load_n_per_mm
    torque_intensity = history.imposed_load_n_per_mm * history.imposed_eccentricity_mm
    snapshots = (
        (request.service_actions, total_load, torque_intensity),
        (request.permanent_actions, history.permanent_load_n_per_mm, 0.0),
        (
            transfer.action_snapshot,
            total_load * history.ultimate_load_factor,
            torque_intensity * history.ultimate_load_factor,
        ),
    )
    for snapshot, load, torque in snapshots:
        gap = _action_gap(snapshot, request, load, torque, span)
        if gap:
            return not_evaluated_result(
                op,
                inputs,
                _diagnostic("SLS.ACTION_BINDING", gap),
                provenance=provenance,
            )
    if len({snap.outputs["rows"][0]["load_case_id"] for snap, _, _ in snapshots}) != 3:
        return rejected_result(
            op,
            inputs,
            (
                _diagnostic(
                    "SLS.CASE_IDENTITY",
                    "ULS, total service and permanent cases must retain distinct identities.",
                ),
            ),
            provenance=provenance,
        )
    bars = section.bars
    ys = sorted({bar.y_from_top_mm for bar in bars})
    xs = sorted({bar.x_from_left_mm for bar in bars})
    area = math.pi * bars[0].diameter_mm ** 2 / 4
    layers = ((ys[0], 2 * area), (ys[1], 2 * area))
    ec, es = 25000.0, 200000.0
    axis, inertia = cracked_service_section(b, D, layers, ec, es)
    long_axis, long_inertia = cracked_service_section(b, D, layers, ec / 2.6, es)
    initial = uniform_flexural_deflection(total_load, span, ec, inertia)
    permanent = uniform_flexural_deflection(
        history.permanent_load_n_per_mm, span, ec, inertia
    )
    permanent_long = uniform_flexural_deflection(
        history.permanent_load_n_per_mm, span, ec / 2.6, long_inertia
    )
    try:
        shrinkage = shrinkage_upper_bound(2 * area, b, ys[1], D, span, 0.0003)
    except ValueError as exc:
        return not_evaluated_result(
            op,
            inputs,
            _diagnostic("SLS.SHRINKAGE_DOMAIN", str(exc)),
            provenance=provenance,
        )
    link = request.closed_links.link
    corner_area = (xs[1] - xs[0]) * (ys[1] - ys[0])
    corner_perimeter = 2 * (xs[1] - xs[0] + ys[1] - ys[0])
    longitudinal_ratio = 4 * area / (b * D)
    link_leg_area = math.pi * link.diameter_mm**2 / 4
    transverse_ratio = (
        link_leg_area
        * 2
        * (link.centre_width_mm + link.centre_depth_mm)
        / (b * D * link.spacing_mm)
    )
    stiffness = lampert_cracked_stiffness(
        es, corner_area, corner_perimeter, longitudinal_ratio, transverse_ratio
    )
    twist = torque_intensity * span**2 / (8 * stiffness)
    edge = abs(request.edge_offset_from_section_centre_mm * twist)
    code_span = min(
        supports[1].left_face_x_mm - supports[0].right_face_x_mm + ys[1], span
    )
    deflection = _deflection_result(
        request,
        span=span,
        code_span=code_span,
        initial=initial,
        permanent=permanent,
        creep=permanent_long - permanent,
        shrinkage=shrinkage,
        edge=edge,
    )
    rows = request.service_actions.outputs["rows"]
    governing = max(rows, key=lambda r: abs(r["m3_nmm"]))
    curvature = abs(governing["m3_nmm"]) / (ec * inertia)
    steel_stress = es * curvature * (ys[1] - axis)
    crack = check_crack_width(
        CrackWidthCheckRequest(
            request.profile_id,
            request.member_id,
            f"SLS-{governing['object_station_mm']}",
            governing["row_id"],
            request.reinforcement_revision_id,
            b,
            D,
            axis,
            Face.BOTTOM,
            bars,
            b / 2,
            steel_stress,
            415,
            es,
            curvature * (D - axis),
            CrackWidthLimitRequest(request.profile_id, ExposureClass.MILD, False),
        )
    )
    wsm_rows = []
    for row in rows:
        stresses = wsm_torsion_row(
            b_mm=b,
            D_mm=D,
            d_mm=ys[1],
            corner_b_mm=xs[1] - xs[0],
            corner_d_mm=ys[1] - ys[0],
            face_area_mm2=2 * area,
            link_area_mm2=2 * link_leg_area,
            link_spacing_mm=link.spacing_mm,
            moment_nmm=row["m3_nmm"],
            shear_n=row["v2_n"],
            torque_nmm=row["t_nmm"],
        )
        passed = (
            max(
                stresses["primary_tension_stress_nmm2"],
                stresses["opposite_tension_stress_nmm2"],
                stresses["torsion_link_stress_nmm2"],
                stresses["full_equivalent_shear_link_stress_nmm2"],
            )
            <= 230
            and stresses["compression_stress_nmm2"] <= 8.5
            and stresses["equivalent_shear_stress_nmm2"] <= 1.9
        )
        wsm_rows.append(
            {
                "source_row_id": row["row_id"],
                "station_mm": row["object_station_mm"],
                "passed": passed,
                **stresses,
            }
        )
    # The sustained state remains in the source's proportional-creep stress
    # domain, fck/3 (Cl6.2.5); transient Q carries no creep contribution.
    creep_stress = max(
        history.permanent_load_n_per_mm * span**2 / 8 * axis / inertia,
        history.permanent_load_n_per_mm * span**2 / 8 * long_axis / long_inertia,
    )
    if creep_stress > 25 / 3:
        return not_evaluated_result(
            op,
            inputs,
            _diagnostic(
                "SLS.CREEP_STRESS_DOMAIN",
                "Concrete stress exceeds the qualified proportional-creep domain.",
            ),
            provenance=provenance,
        )
    passed = all(row["passed"] for row in wsm_rows) and deflection.engineering == "pass"
    outputs = {
        "service_action_snapshot_id": request.service_actions.result_id,
        "permanent_action_snapshot_id": request.permanent_actions.result_id,
        "reinforcement_revision_id": request.reinforcement_revision_id,
        "support_transfer_result_id": physical.result_id,
        "closed_link_result_id": hooks.result_id,
        "deformation_datum": "same_physical_edge_support_chord; identical pinned-ended receiver models, zero settlement",
        "support_model_boundary_reference": history.reference,
        "analysis_span_mm": span,
        "code_effective_span_mm": code_span,
        "short_term_neutral_axis_mm": axis,
        "short_term_cracked_inertia_mm4": inertia,
        "long_term_neutral_axis_mm": long_axis,
        "long_term_cracked_inertia_mm4": long_inertia,
        "bottom_steel_stress_nmm2": steel_stress,
        "elastic_tension_surface_strain": curvature * (D - axis),
        "lampert_stiffness_nmm2": stiffness,
        "longitudinal_ratio": longitudinal_ratio,
        "transverse_ratio": transverse_ratio,
        "midspan_relative_twist_rad": twist,
        "edge_torsional_displacement_mm": edge,
        "indirect_torsional_crack_control": "IS456_ANNEX_B_SERVICE_STRESS_AND_ACTUAL_DETAIL",
        "torsional_crack_width_mm": None,
        "wsm_rows": wsm_rows,
        "deflection": deflection.to_dict(),
        "flexural_crack": crack.to_dict(),
        "passed": passed,
    }
    return completed_result(
        op,
        inputs,
        outputs,
        engineering=EngineeringState.PASS if passed else EngineeringState.FAIL,
        diagnostics=(
            ()
            if passed
            else (
                _diagnostic(
                    "SLS.LIMIT_EXCEEDED",
                    "Combined edge deflection or indirect Annex-B stress/detail criteria fail.",
                ),
            )
        ),
        provenance=provenance,
    )
