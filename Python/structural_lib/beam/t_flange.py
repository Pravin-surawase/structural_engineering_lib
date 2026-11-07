"""Source-bound flange participation and separately owned local slab steel.

This supplies the local flange provision for the selected T member. It is
not a whole-floor/slab product or approval of supporting beams/foundations.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

from structural_lib.codes.is456.beam.flanged_serviceability import (
    conservative_strip_shear,
    flange_strip_limits,
)
from structural_lib.codes.is456.beam.flexure import calculate_effective_flange_width
from structural_lib.core.data_types import BeamType

from .analysis import BeamLineRequest, solve_beam_line
from .bar_paths import BarPathOutput, BarPathRequest, BarPathRole, resolve_bar_paths
from .detailing import (
    BarSurface,
    DevelopmentLengthRequest,
    StressState,
    development_length,
)
from .flexure import (
    FlexuralCapacityRequest,
    FlexureCheckRequest,
    SectionKind,
    check_flexure,
    flexural_capacity,
)
from .reinforcement import (
    BarPosition,
    Face,
    ReinforcementGeometryRequest,
    evaluate_geometry,
)
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
from .t_member_basis import TBeamActionBasisRequest, _passed, check_t_action_basis

T_FLANGE_OPERATION = "is456.beam.t_flange_participation.check/v1"
T_FLANGE_REVISION = "is456-t-flange-physical-strip-e-v1"


@dataclass(frozen=True)
class TFlangeStripRequest:
    owner_id: str
    parent_geometry_revision_id: str
    reference: str
    nominal_cover_mm: float
    main_spacing_mm: float
    distribution_spacing_mm: float
    main_top_depth_mm: float
    main_bottom_depth_mm: float
    distribution_top_depth_mm: float
    distribution_bottom_depth_mm: float
    paths: BarPathRequest
    transverse_analysis: BeamLineRequest


@dataclass(frozen=True)
class TFlangeParticipationRequest:
    action_basis: TBeamActionBasisRequest
    adjacent_clear_distance_left_mm: float | None
    adjacent_clear_distance_right_mm: float | None
    integrally_cast: bool | None
    monolithic_reference: str | None
    slab_main_direction: str | None
    strip: TFlangeStripRequest | None


def _diag(code: str, field: str, message: str) -> Diagnostic:
    return Diagnostic(
        code,
        "error",
        message,
        T_FLANGE_OPERATION,
        field,
        "IS456-T-flange",
        "Supply the current monolithic/adjacency and actual separately owned flange-strip evidence.",
    )


def _box_distance(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    return math.sqrt(
        sum(
            max(a[2 * i] - b[2 * i + 1], b[2 * i] - a[2 * i + 1], 0) ** 2
            for i in range(3)
        )
    )


def check_t_flange_participation(
    request: TFlangeParticipationRequest,
) -> OperationResult:
    """Check one symmetric adjacent-beam flange and actual local strip proof.

    Flange strip bars remain slab-owned and receive no beam strength credit.
    Their eligible parallel bars are retained in a separate actual-y audit.
    """
    inputs = effective_inputs(request=request)
    provenance = Provenance(
        T_FLANGE_REVISION,
        T_FLANGE_REVISION,
        (
            "IS456:2000 through Amendment6;23.1.1/23.1.2; slab-main-perpendicular profile; Fig3 parallel-main trigger not applicable",
            "IS45626.3.3/26.4/26.5.2.1-2; actual slab-strip steel, two-face moment envelope and full tension development",
            "Two-span uniform static strip corroboration; not a whole-floor acceptance",
        ),
    )

    def hold(code: str, message: str) -> OperationResult:
        return not_evaluated_result(
            T_FLANGE_OPERATION,
            inputs,
            _diag(code, "request", message),
            provenance=provenance,
        )

    action = check_t_action_basis(request.action_basis)
    geometry = request.action_basis.geometry
    section = geometry.section
    strip = request.strip
    distances = (
        request.adjacent_clear_distance_left_mm,
        request.adjacent_clear_distance_right_mm,
    )
    if (
        strip is None
        or not request.monolithic_reference
        or request.integrally_cast is None
        or any(v is None for v in distances)
    ):
        return hold(
            "T_FLANGE.MISSING",
            "Monolithic, adjacent-beam and actual slab-strip evidence are required.",
        )
    if (
        not request.integrally_cast
        or request.slab_main_direction != "perpendicular_to_beam"
    ):
        return hold(
            "T_FLANGE.UNSUPPORTED",
            "Non-monolithic or parallel-main slab flanges require their own qualified interface/Fig3 profile.",
        )
    if not _passed(action):
        return hold(
            "T_FLANGE.ACTIONS",
            "Current physical action/span/depth evidence is required.",
        )
    left, right = distances
    assert left is not None and right is not None
    if (
        not all(math.isfinite(v) and v > 0 for v in (left, right))
        or not math.isclose(left, right, abs_tol=1e-8, rel_tol=0)
        or not math.isclose(
            section.web_left_from_flange_left_mm,
            (section.flange_width_physical_mm - section.web_width_mm) / 2,
            abs_tol=1e-8,
            rel_tol=0,
        )
    ):
        return hold(
            "T_FLANGE.ADJACENCY",
            "The selected symmetric T needs actual equal clear adjacent-beam distances and centred web.",
        )
    adjacency_cap = section.web_width_mm + (left + right) / 2
    if not math.isclose(
        adjacency_cap, section.flange_width_physical_mm, abs_tol=1e-8, rel_tol=0
    ):
        return hold(
            "T_FLANGE.PHYSICAL_WIDTH",
            "The owned physical flange strip must match the supplied half-clear adjacent-beam layout.",
        )
    effective = calculate_effective_flange_width(
        bw_mm=section.web_width_mm,
        span_mm=float(action.outputs["zero_moment_distance_mm"]),
        df_mm=section.flange_thickness_mm,
        flange_overhang_left_mm=left / 2,
        flange_overhang_right_mm=right / 2,
        beam_type=BeamType.FLANGED_T,
    )
    if (
        not strip.owner_id
        or not strip.reference
        or strip.parent_geometry_revision_id != section.geometry_revision_id
    ):
        return hold(
            "T_FLANGE.STRIP_IDENTITY",
            "The actual slab-strip owner/reference must bind the current T geometry.",
        )
    depths = (
        strip.main_top_depth_mm,
        strip.main_bottom_depth_mm,
        strip.distribution_top_depth_mm,
        strip.distribution_bottom_depth_mm,
    )
    if (
        not all(
            math.isfinite(y) and 0 < y < section.flange_thickness_mm for y in depths
        )
        or strip.main_top_depth_mm >= strip.main_bottom_depth_mm
        or strip.distribution_top_depth_mm >= strip.distribution_bottom_depth_mm
    ):
        return rejected_result(
            T_FLANGE_OPERATION,
            inputs,
            (
                _diag(
                    "T_FLANGE.STRIP_INPUT",
                    "strip",
                    "Actual ordered slab bar layers must lie within the flange thickness.",
                ),
            ),
            provenance=provenance,
        )
    path_request, analysis_request = strip.paths, strip.transverse_analysis
    full_length = geometry.paths.member_end_x_mm - geometry.paths.member_start_x_mm
    transverse_span = section.web_width_mm + left
    if (
        path_request.project_basis_id != geometry.paths.project_basis_id
        or path_request.member_id == geometry.member_id
        or path_request.section_width_mm != full_length
        or path_request.section_depth_mm != section.flange_thickness_mm
        or path_request.member_start_x_mm != -section.web_width_mm / 2
        or path_request.member_end_x_mm
        != 2 * transverse_span + section.web_width_mm / 2
    ):
        return hold(
            "T_FLANGE.STRIP_GEOMETRY",
            "The separate actual slab domain must span three adjacent webs and the full physical T length.",
        )
    paths = resolve_bar_paths(path_request)
    if not _passed(paths):
        return hold(
            "T_FLANGE.STRIP_PATHS",
            "Actual current fabricated slab-strip paths are required.",
        )
    primary = [
        seed
        for seed in path_request.paths
        if seed.role is BarPathRole.FLANGE_TRANSVERSE
    ]
    distribution = [
        seed
        for seed in path_request.paths
        if seed.role is BarPathRole.FLANGE_DISTRIBUTION
    ]
    if (
        not primary
        or not distribution
        or len(primary) + len(distribution) != len(path_request.paths)
    ):
        return hold(
            "T_FLANGE.STRIP_ROLES",
            "Every separate slab path needs an explicit transverse-main or parallel-distribution role.",
        )
    dimensions = (
        strip.nominal_cover_mm,
        strip.main_spacing_mm,
        strip.distribution_spacing_mm,
    )
    if not all(math.isfinite(v) and v > 0 for v in dimensions):
        return hold(
            "T_FLANGE.STRIP_INPUT", "Positive actual cover and pitches are required."
        )
    diagnostics = []
    main_diameter, distribution_diameter = (
        primary[0].diameter_mm,
        distribution[0].diameter_mm,
    )
    main_rows: dict[float, list[float]] = {
        strip.main_top_depth_mm: [],
        strip.main_bottom_depth_mm: [],
    }
    distribution_rows: dict[float, list[float]] = {
        strip.distribution_top_depth_mm: [],
        strip.distribution_bottom_depth_mm: [],
    }
    parallel_bars = []
    global_external_boxes = []
    for seed in path_request.paths:
        if len(seed.nodes) != 2 or seed.closed or seed.steel_grade_n_per_mm2 != 415:
            return hold(
                "T_FLANGE.STRIP_SHAPE",
                "This slab-strip profile needs actual straight uncoated Fe415 runs.",
            )
        a, b = (node.point for node in seed.nodes)
        radius = seed.diameter_mm / 2
        if any(
            not path_request.member_start_x_mm + strip.nominal_cover_mm + radius - 1e-8
            <= node.point.station_x_mm
            <= path_request.member_end_x_mm - strip.nominal_cover_mm - radius + 1e-8
            or not strip.nominal_cover_mm + radius - 1e-8
            <= node.point.section_x_from_left_mm
            <= full_length - strip.nominal_cover_mm - radius + 1e-8
            or not strip.nominal_cover_mm + radius - 1e-8
            <= node.point.section_y_from_top_mm
            <= section.flange_thickness_mm - strip.nominal_cover_mm - radius + 1e-8
            for node in seed.nodes
        ):
            diagnostics.append(
                _diag(
                    "T_FLANGE.STRIP_COVER",
                    seed.bar_id,
                    "The actual slab bar surface violates the declared physical slab cover.",
                )
            )
        if seed.role is BarPathRole.FLANGE_TRANSVERSE:
            if (
                seed.diameter_mm != main_diameter
                or a.section_y_from_top_mm not in main_rows
                or a.section_x_from_left_mm != b.section_x_from_left_mm
                or a.section_y_from_top_mm != b.section_y_from_top_mm
            ):
                return hold(
                    "T_FLANGE.MAIN_LAYOUT",
                    "Actual slab main bars must retain the supplied two faces and uniform transverse direction.",
                )
            if (
                min(a.station_x_mm, b.station_x_mm) > 0
                or max(a.station_x_mm, b.station_x_mm) < 2 * transverse_span
            ):
                diagnostics.append(
                    _diag(
                        "T_FLANGE.MAIN_EXTENT",
                        seed.bar_id,
                        "The supplied main slab runs do not cover both actual transverse spans.",
                    )
                )
            main_rows[a.section_y_from_top_mm].append(a.section_x_from_left_mm)
        else:
            if (
                seed.diameter_mm != distribution_diameter
                or a.section_y_from_top_mm not in distribution_rows
                or a.station_x_mm != b.station_x_mm
                or a.section_y_from_top_mm != b.section_y_from_top_mm
            ):
                return hold(
                    "T_FLANGE.DISTRIBUTION_LAYOUT",
                    "Actual slab distribution runs must retain their parallel direction and two physical layers.",
                )
            if (
                min(a.section_x_from_left_mm, b.section_x_from_left_mm)
                > strip.main_spacing_mm / 2
                or max(a.section_x_from_left_mm, b.section_x_from_left_mm)
                < full_length - strip.main_spacing_mm / 2
            ):
                diagnostics.append(
                    _diag(
                        "T_FLANGE.DISTRIBUTION_EXTENT",
                        seed.bar_id,
                        "The actual parallel distribution run does not cover the full owned T length.",
                    )
                )
            distribution_rows[a.section_y_from_top_mm].append(a.station_x_mm)
            global_x = (
                a.station_x_mm - transverse_span + section.flange_width_physical_mm / 2
            )
            if (
                radius + strip.nominal_cover_mm
                <= global_x
                <= section.flange_width_physical_mm - radius - strip.nominal_cover_mm
            ):
                parallel_bars.append(
                    BarPosition(
                        seed.bar_id,
                        seed.diameter_mm,
                        global_x,
                        a.section_y_from_top_mm,
                        Face.TOP,
                    )
                )
        # Explicit external-strip -> T global datum map for physical crossings.
        coordinates = [
            (
                point.section_x_from_left_mm + geometry.paths.member_start_x_mm,
                point.station_x_mm
                - transverse_span
                + section.flange_width_physical_mm / 2,
                point.section_y_from_top_mm,
            )
            for point in (a, b)
        ]
        box = tuple(
            value
            for i in range(3)
            for value in (
                min(p[i] for p in coordinates),
                max(p[i] for p in coordinates),
            )
        )
        global_external_boxes.append((seed.bar_id, radius, box))
    for index, (first_id, first_radius, first_box) in enumerate(global_external_boxes):
        for second_id, second_radius, second_box in global_external_boxes[index + 1 :]:
            # All admitted external runs are axis-aligned straight segments;
            # box distance is their exact minimum centreline distance.
            if (
                _box_distance(first_box, second_box)
                < first_radius + second_radius - 1e-8
            ):
                diagnostics.append(
                    _diag(
                        "T_FLANGE.SLAB_BAR_COLLISION",
                        f"{first_id},{second_id}",
                        "Actual slab main/distribution bar surfaces intersect.",
                    )
                )
    for rows, pitch, lo, hi in (
        (main_rows, strip.main_spacing_mm, 0.0, full_length),
        (distribution_rows, strip.distribution_spacing_mm, 0.0, 2 * transverse_span),
    ):
        for positions in rows.values():
            positions.sort()
            if (
                not positions
                or positions[0] > lo + pitch / 2 + 1e-8
                or positions[-1] < hi - pitch / 2 - 1e-8
                or any(
                    not math.isclose(b - a, pitch, abs_tol=1e-8, rel_tol=0)
                    for a, b in zip(positions, positions[1:], strict=False)
                )
            ):
                diagnostics.append(
                    _diag(
                        "T_FLANGE.STRIP_SPACING",
                        "paths",
                        "Actual supplied bar stations do not cover the declared slab region at the checked pitch.",
                    )
                )
    reference_width = 4 * strip.main_spacing_mm
    sample_positions = sorted(main_rows[strip.main_top_depth_mm])[:4]
    if len(sample_positions) != 4 or reference_width != 600:
        return hold(
            "T_FLANGE.UNSUPPORTED_STRIP",
            "The frozen local proof uses an actual four-bar,600mm repeating strip; other schemes need their own reference.",
        )
    sample_bars = tuple(
        BarPosition(
            next(
                seed.bar_id
                for seed in primary
                if seed.nodes[0].point.section_y_from_top_mm == y
                and seed.nodes[0].point.section_x_from_left_mm == x
            ),
            main_diameter,
            x,
            y,
            face,
        )
        for face, y in (
            (Face.TOP, strip.main_top_depth_mm),
            (Face.BOTTOM, strip.main_bottom_depth_mm),
        )
        for x in sorted(main_rows[y])[:4]
    )
    strip_geometry = evaluate_geometry(
        ReinforcementGeometryRequest(
            geometry.profile_id,
            reference_width,
            section.flange_thickness_mm,
            strip.nominal_cover_mm,
            0,
            25,
            sample_bars,
        )
    )
    strip_effective_depth = min(
        strip.main_bottom_depth_mm,
        section.flange_thickness_mm - strip.main_top_depth_mm,
    )
    limits = flange_strip_limits(section.flange_thickness_mm, strip_effective_depth)
    main_area_per_m = math.pi * main_diameter**2 / 4 * 1000 / strip.main_spacing_mm
    distribution_area_per_m = (
        math.pi * distribution_diameter**2 / 4 * 1000 / strip.distribution_spacing_mm
    )
    detail_pass = (
        main_area_per_m >= limits["minimum_area_per_m_each_direction_mm2"]
        and distribution_area_per_m >= limits["minimum_area_per_m_each_direction_mm2"]
        and strip.main_spacing_mm <= limits["maximum_main_spacing_mm"]
        and strip.distribution_spacing_mm <= limits["maximum_distribution_spacing_mm"]
        and max(main_diameter, distribution_diameter)
        <= limits["maximum_bar_diameter_mm"]
        and strip.nominal_cover_mm >= max(20, main_diameter, distribution_diameter)
    )
    loads = request.action_basis.loads
    assert loads is not None
    area_g = (
        section.flange_thickness_mm * loads.concrete_unit_weight_kn_per_m3 / 1000
        + loads.superimposed_permanent_load_n_per_mm
        * 1000
        / section.flange_width_physical_mm
    )
    area_q = loads.imposed_load_n_per_mm * 1000 / section.flange_width_physical_mm
    line_uls = (
        (
            area_g * loads.permanent_ultimate_factor
            + area_q * loads.imposed_ultimate_factor
        )
        * reference_width
        / 1000
    )
    envelope = line_uls * transverse_span**2 / 8 / 1e6
    # Corroborate the conservative both-sign envelope against an actual
    # continuous two-span linear solve, rather than labelling it a code factor.
    if (
        len(analysis_request.nodes) != 3
        or len(analysis_request.elements) != 2
        or tuple(n.x_mm for n in analysis_request.nodes)
        != (0, transverse_span, 2 * transverse_span)
        or any(
            not n.vertical_restraint
            or n.rotation_restraint
            or n.vertical_displacement_mm != 0
            or n.prescribed_rotation_rad != 0
            or n.nodal_force_n != 0
            or n.nodal_moment_nmm != 0
            for n in analysis_request.nodes
        )
        or analysis_request.point_loads
        or tuple((e.start_node_id, e.end_node_id) for e in analysis_request.elements)
        != tuple(
            (a.node_id, b.node_id)
            for a, b in zip(
                analysis_request.nodes, analysis_request.nodes[1:], strict=False
            )
        )
        or any(
            not math.isclose(
                e.uniform_load_n_per_mm, -line_uls, abs_tol=1e-10, rel_tol=0
            )
            or e.elastic_modulus_n_per_mm2 != 25000
            or not math.isclose(
                e.second_moment_mm4,
                reference_width * section.flange_thickness_mm**3 / 12,
                rel_tol=1e-12,
            )
            for e in analysis_request.elements
        )
    ):
        return hold(
            "T_FLANGE.STRIP_ACTIONS",
            "The separately owned strip needs its declared two actual continuous spans and physical-width-derived gravity actions.",
        )
    solved = solve_beam_line(analysis_request)
    if not (
        solved.execution == "completed"
        and solved.completeness == "complete_for_scope"
        and solved.freshness == "current"
        and not solved.diagnostics
    ):
        return hold(
            "T_FLANGE.STRIP_ANALYSIS",
            "A current qualifying supplied strip analysis is required.",
        )
    actual_moment = max(abs(row["m3_nmm"]) for row in solved.outputs["stations"]) / 1e6
    if actual_moment > envelope + 1e-8:
        diagnostics.append(
            _diag(
                "T_FLANGE.STRIP_ENVELOPE",
                "actions",
                "The conservative local envelope does not bound the actual two-span moments.",
            )
        )
    strengths = []
    for face in (Face.TOP, Face.BOTTOM):
        strip_capacity_request = FlexuralCapacityRequest(
            geometry.profile_id,
            SectionKind.RECTANGULAR,
            reference_width,
            section.flange_thickness_mm,
            25,
            415,
            sample_bars,
            face,
        )
        strengths.append(
            check_flexure(
                FlexureCheckRequest(
                    strip_capacity_request,
                    positive_design_moment_knm=(
                        envelope if face is Face.BOTTOM else None
                    ),
                    negative_design_moment_knm=-envelope if face is Face.TOP else None,
                )
            )
        )
    development = development_length(
        DevelopmentLengthRequest(
            geometry.profile_id,
            main_diameter,
            0.87 * 415,
            415,
            25,
            BarSurface.DEFORMED,
            StressState.TENSION,
        )
    )
    required_development = float(development.outputs["required_development_length_mm"])
    anchors = []
    for seed in primary:
        a, b = (node.point for node in seed.nodes)
        available_left = (
            transverse_span
            - section.web_width_mm / 2
            - min(a.station_x_mm, b.station_x_mm)
        )
        available_right = max(a.station_x_mm, b.station_x_mm) - (
            transverse_span + section.web_width_mm / 2
        )
        anchors.append(
            {
                "bar_id": seed.bar_id,
                "required_development_mm": required_development,
                "available_left_mm": available_left,
                "available_right_mm": available_right,
                "passed": min(available_left, available_right) >= required_development,
            }
        )
    # Existing rectangular shear data, without slab depth enhancement. This
    # local slab strip has no beam minimum-link obligation.
    tension_area = 4 * math.pi * main_diameter**2 / 4
    tau_v, tau_c = conservative_strip_shear(
        line_uls, transverse_span, reference_width, strip_effective_depth, tension_area
    )
    # Check actual 3D slab/web steel crossing clearance. Axis-aligned boxes
    # give a lower bound, including analytic subarc bounds for web link bends.
    from .t_section_geometry import _segment_boxes, _segment_station_bounds

    web_paths = resolve_bar_paths(geometry.paths).output_as(
        "reinforcement_schedule", BarPathOutput
    )
    crossing_min = math.inf
    for path in web_paths.paths:
        for segment in path.segments:
            station_bounds = _segment_station_bounds(segment)
            for xy in _segment_boxes(segment):
                web_box = (*station_bounds, *xy)
                for _, radius, external_box in global_external_boxes:
                    crossing_min = min(
                        crossing_min,
                        _box_distance(web_box, external_box)
                        - path.diameter_mm / 2
                        - radius,
                    )
    if crossing_min < -1e-8:
        return hold(
            "T_FLANGE.CROSSING_CERTIFICATE",
            "Actual slab/web steel lacks a nonintersection certificate; retain the supplied paths and revise or qualify the crossing detail.",
        )
    eligible = tuple(
        bar
        for bar in parallel_bars
        if abs(bar.x_from_left_mm - section.flange_width_physical_mm / 2)
        <= effective / 2
    )
    beam_section = FlexuralCapacityRequest(
        geometry.profile_id,
        SectionKind.T_BEAM,
        section.web_width_mm,
        section.depth_mm,
        25,
        415,
        geometry.bars,
        Face.BOTTOM,
        effective,
        section.flange_thickness_mm,
    )
    conservative_capacity = flexural_capacity(beam_section)
    actual_audit = flexural_capacity(
        replace(beam_section, bars=geometry.bars + eligible)
    )
    if not _passed(actual_audit) or float(
        actual_audit.outputs["capacity_knm"]
    ) + 1e-8 < float(conservative_capacity.outputs["capacity_knm"]):
        return hold(
            "T_FLANGE.PARALLEL_STEEL_AUDIT",
            "The actual-y eligible slab steel audit does not establish a ductile capacity at least as large as the uncredited web-only design resistance.",
        )
    checks_pass = (
        detail_pass
        and _passed(strip_geometry)
        and all(_passed(r) for r in strengths)
        and all(a["passed"] for a in anchors)
        and tau_v <= tau_c
    )
    if not checks_pass:
        diagnostics.append(
            _diag(
                "T_FLANGE.STRIP_PROVISION",
                "strip",
                "Actual local slab strength, cover, reinforcement minima/spacing, shear or full tension development fails.",
            )
        )
    outputs = {
        "section_id": section.section_id,
        "geometry_revision_id": section.geometry_revision_id,
        "reinforcement_revision_id": geometry.reinforcement_revision_id,
        "action_basis_result_id": action.result_id,
        "physical_flange_width_mm": section.flange_width_physical_mm,
        "effective_flange_width_mm": effective,
        "adjacent_width_cap_mm": adjacency_cap,
        "zero_moment_distance_mm": action.outputs["zero_moment_distance_mm"],
        "strip_owner_id": strip.owner_id,
        "strip_detail_revision_id": path_request.detail_revision_id,
        "slab_main_direction": request.slab_main_direction,
        "parallel_main_Fig3_applicability": "not_applicable",
        "strip_paths": paths,
        "strip_geometry": strip_geometry,
        "strip_analysis": solved,
        "strip_flexure": strengths,
        "strip_service_area_load_kn_per_m2": area_g + area_q,
        "strip_two_face_moment_envelope_knm": envelope,
        "strip_main_area_per_m_mm2": main_area_per_m,
        "strip_distribution_area_per_m_mm2": distribution_area_per_m,
        "strip_limits": limits,
        "strip_anchorages": anchors,
        "strip_shear_stress_nmm2": tau_v,
        "strip_concrete_shear_limit_nmm2": tau_c,
        "slab_web_crossing_clearance_lower_bound_mm": crossing_min,
        "parallel_slab_bars": tuple(parallel_bars),
        "eligible_parallel_slab_bars": eligible,
        "conservative_beam_only_capacity": conservative_capacity,
        "actual_parallel_steel_section_audit": actual_audit,
        "slab_steel_in_beam_BBS": False,
        "slab_steel_beam_strength_credit": False,
    }
    return completed_result(
        T_FLANGE_OPERATION,
        inputs,
        outputs,
        engineering=EngineeringState.FAIL if diagnostics else EngineeringState.PASS,
        diagnostics=diagnostics,
        provenance=provenance,
    )
