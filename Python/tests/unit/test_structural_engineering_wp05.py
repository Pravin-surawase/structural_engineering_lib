from dataclasses import replace

import pytest

from structural_lib.beam import (
    AnchorageCheckRequest,
    AnchorageDirection,
    AnchorageLocation,
    AnchoragePath,
    BarSurface,
    BeamEnd,
    CircularObstacle,
    CurtailmentDetail,
    DependentJointCheck,
    DevelopmentLengthRequest,
    LapCurtailmentCheckRequest,
    LinkCage,
    LongitudinalBarPath,
    PlacementOpening,
    QualifiedCheckReference,
    ReinforcementArrangementCheckRequest,
    ReinforcementRole,
    SeismicAnchorageCheck,
    SeismicApplicability,
    SeismicBeamContext,
    SeismicDetailingCheckRequest,
    SeismicLinkZone,
    SimpleSupportAnchorageEvidence,
    SpliceDetail,
    SpliceKind,
    StationSteelDemand,
    StationZone,
    StressState,
    check_anchorage,
    check_laps_and_curtailment,
    check_reinforcement_arrangement,
    check_seismic_detailing,
    development_length,
)
from structural_lib.beam.semantics import (
    ApplicabilityState,
    CompletenessState,
    EngineeringState,
    ExecutionState,
    FreshnessState,
)


def _development(
    *,
    surface: BarSurface = BarSurface.DEFORMED,
    stress_state: StressState = StressState.TENSION,
    bundle_size: int = 1,
) -> DevelopmentLengthRequest:
    return DevelopmentLengthRequest(
        "IS456-WP05",
        20,
        0.87 * 415,
        415,
        20,
        surface,
        stress_state,
        bundle_size,
    )


def _qualified(operation: str = "qualified.operation/v1") -> QualifiedCheckReference:
    return QualifiedCheckReference(
        operation,
        f"result:{operation}",
        ExecutionState.COMPLETED,
        ApplicabilityState.APPLICABLE,
        EngineeringState.PASS,
        CompletenessState.COMPLETE_FOR_SCOPE,
        FreshnessState.CURRENT,
    )


def _bar(
    bar_id: str,
    role: ReinforcementRole,
    x_mm: float,
    y_mm: float,
    *,
    diameter_mm: float = 20,
    layer: int = 1,
    start_mm: float = 0,
    end_mm: float = 6000,
) -> LongitudinalBarPath:
    return LongitudinalBarPath(
        bar_id,
        f"MARK-{bar_id}",
        role,
        diameter_mm,
        layer,
        x_mm,
        y_mm,
        start_mm,
        end_mm,
        0.87 * 415,
    )


def test_development_length_reports_all_modifiers_and_amendment_6_epoxy() -> None:
    deformed = development_length(_development())
    epoxy = development_length(
        _development(surface=BarSurface.FUSION_BONDED_EPOXY_DEFORMED)
    )
    compression = development_length(
        _development(stress_state=StressState.COMPRESSION)
    )
    bundle = development_length(_development(bundle_size=4))

    assert deformed.outputs["design_bond_stress_n_per_mm2"] == pytest.approx(1.92)
    assert deformed.outputs["required_development_length_mm"] == pytest.approx(
        940.234375
    )
    assert epoxy.outputs["required_development_length_mm"] == pytest.approx(
        1175.29296875
    )
    assert compression.outputs["required_development_length_mm"] == pytest.approx(
        752.1875
    )
    assert bundle.outputs["required_development_length_mm"] == pytest.approx(
        940.234375 * 1.33
    )


def test_development_length_rejects_stress_above_bounded_profile() -> None:
    request = _development()
    result = development_length(
        DevelopmentLengthRequest(
            request.profile_id,
            request.bar_diameter_mm,
            0.9 * request.steel_yield_strength_n_per_mm2,
            request.steel_yield_strength_n_per_mm2,
            request.concrete_grade_n_per_mm2,
            request.bar_surface,
            request.stress_state,
        )
    )

    assert result.execution == "rejected_input"
    assert result.diagnostics[0].code == "STRESS.OUTSIDE_PROFILE"


def test_simple_support_anchorage_uses_moment_over_shear_plus_lo() -> None:
    result = check_anchorage(
        AnchorageCheckRequest(
            "IS456-WP05",
            "B1",
            "reinforcement:R1",
            (
                AnchoragePath(
                    "B1-BOT-1",
                    "right-support-face",
                    AnchorageLocation.SIMPLE_SUPPORT,
                    AnchorageDirection.INCREASING_X,
                    0,
                    6000,
                    5800,
                    "SUP-R",
                    5800,
                    5900,
                    (),
                    None,
                    _development(),
                    SimpleSupportAnchorageEvidence(
                        85_000_000,
                        100_000,
                        ("action:ULS-right",),
                    ),
                ),
            ),
        )
    )

    check = result.outputs["checks"][0]
    assert result.engineering == "pass"
    assert check["moment_shear_contribution_mm"] == pytest.approx(850)
    assert check["anchorage_beyond_support_centre_mm"] == pytest.approx(100)
    assert check["available_for_criterion_mm"] == pytest.approx(950)


def test_anchorage_rejects_support_centreline_as_face() -> None:
    result = check_anchorage(
        AnchorageCheckRequest(
            "IS456-WP05",
            "B1",
            "reinforcement:R1",
            (
                AnchoragePath(
                    "B1-BOT-1",
                    "wrong-centreline-section",
                    AnchorageLocation.CONTINUOUS_SUPPORT,
                    AnchorageDirection.INCREASING_X,
                    0,
                    6000,
                    5900,
                    "SUP-R",
                    5800,
                    5900,
                    (),
                    None,
                    _development(),
                ),
            ),
        )
    )

    assert result.execution == "rejected_input"
    assert result.diagnostics[0].code == "SUPPORT.FACE_REQUIRED"


def _lap_curtailment_request(
    *,
    splice_start_mm: float = 2500,
    splice_end_mm: float = 3500,
) -> LapCurtailmentCheckRequest:
    bars = (
        _bar("B1", ReinforcementRole.BOTTOM_LONGITUDINAL, 60, 440),
        _bar("B2", ReinforcementRole.BOTTOM_LONGITUDINAL, 150, 440),
        _bar(
            "B3",
            ReinforcementRole.BOTTOM_LONGITUDINAL,
            240,
            440,
            end_mm=5000,
        ),
    )
    return LapCurtailmentCheckRequest(
        "IS456-WP05",
        "B1",
        "SPAN-1",
        "demand:R1",
        "reinforcement:R1",
        0,
        6000,
        450,
        20,
        415,
        BarSurface.DEFORMED,
        bars,
        (
            StationSteelDemand(
                "D-4000",
                4000,
                ReinforcementRole.BOTTOM_LONGITUDINAL,
                600,
                80_000,
                120_000,
                "action:ULS-4000",
            ),
        ),
        (
            SpliceDetail(
                "SP-1",
                SpliceKind.LAP,
                ("B1", "B2"),
                splice_start_mm,
                splice_end_mm,
                StressState.TENSION,
                False,
                50,
                "STAGGER-A",
            ),
        ),
        (
            CurtailmentDetail(
                "CUT-1",
                "B3",
                4000,
                5000,
                AnchorageDirection.INCREASING_X,
                "D-4000",
                600,
                ("B1", "B2"),
                _qualified("is456.beam.anchorage.check/v1"),
                _qualified("is456.beam.shear.check/v1"),
                True,
                _qualified("is456.beam.shear.check/v1"),
            ),
        ),
        (StationZone("NO-LAP-END", 0, 1000),),
    )


def test_lap_and_curtailment_checks_actual_schedule_and_demand() -> None:
    result = check_laps_and_curtailment(_lap_curtailment_request())

    assert result.engineering == "pass"
    splice = result.outputs["splice_checks"][0]
    cutoff = result.outputs["curtailment_checks"][0]
    assert splice["required_length_mm"] == pytest.approx(940.234375)
    assert splice["actual_length_mm"] == 1000
    assert cutoff["actual_extension_mm"] == 1000
    assert cutoff["continuing_area_mm2"] == pytest.approx(628.3185307179587)
    assert cutoff["action_row_id"] == "action:ULS-4000"


def test_lap_in_prohibited_zone_is_completed_failure() -> None:
    result = check_laps_and_curtailment(
        _lap_curtailment_request(splice_start_mm=200, splice_end_mm=1200)
    )

    assert result.execution == "completed"
    assert result.engineering == "fail"
    assert result.outputs["splice_checks"][0]["zone_allowed"] is False


def test_curtailment_rejects_unrelated_passing_result_as_evidence() -> None:
    request = _lap_curtailment_request()
    cutoff = request.curtailments[0]
    result = check_laps_and_curtailment(
        LapCurtailmentCheckRequest(
            request.profile_id,
            request.member_id,
            request.physical_span_id,
            request.demand_revision_id,
            request.reinforcement_revision_id,
            request.member_start_x_mm,
            request.member_end_x_mm,
            request.effective_depth_mm,
            request.concrete_grade_n_per_mm2,
            request.steel_yield_strength_n_per_mm2,
            request.bar_surface,
            request.bars,
            request.demands,
            request.splices,
            (
                CurtailmentDetail(
                    cutoff.cutoff_id,
                    cutoff.bar_id,
                    cutoff.theoretical_cutoff_x_mm,
                    cutoff.actual_end_x_mm,
                    cutoff.direction,
                    cutoff.demand_station_id,
                    cutoff.required_extension_mm,
                    cutoff.continuing_bar_ids,
                    _qualified("is456.beam.flexure.check/v1"),
                    cutoff.shear_cutoff_check,
                    cutoff.extra_links_required,
                    cutoff.extra_links_check,
                ),
            ),
            request.prohibited_splice_zones,
        )
    )

    assert result.engineering == "fail"
    assert result.outputs["curtailment_checks"][0]["anchorage_ok"] is False


def test_qualified_coupler_allows_large_bar_and_extra_links_are_conditional() -> None:
    request = _lap_curtailment_request()
    large_bars = tuple(
        replace(bar, diameter_mm=40)
        if bar.bar_id in {"B1", "B2"}
        else bar
        for bar in request.bars
    )
    coupler = replace(
        request.splices[0],
        kind=SpliceKind.QUALIFIED_COUPLER,
        coupler_qualification_reference="coupler:qualification:R1",
        installation_reference="coupler:installation:R1",
    )
    cutoff = replace(
        request.curtailments[0],
        extra_links_required=False,
        extra_links_check=None,
    )
    result = check_laps_and_curtailment(
        replace(
            request,
            bars=large_bars,
            splices=(coupler,),
            curtailments=(cutoff,),
        )
    )

    assert result.engineering == "pass"
    assert result.outputs["splice_checks"][0]["required_length_mm"] is None
    assert result.outputs["splice_checks"][0][
        "lap_permitted_for_diameter"
    ] is True
    assert result.outputs["curtailment_checks"][0]["extra_links_ok"] is True


def _seismic_context() -> SeismicBeamContext:
    bars = (
        _bar("T1", ReinforcementRole.TOP_LONGITUDINAL, 60, 60),
        _bar("T2", ReinforcementRole.TOP_LONGITUDINAL, 240, 60),
        _bar("B1", ReinforcementRole.BOTTOM_LONGITUDINAL, 60, 440),
        _bar("B2", ReinforcementRole.BOTTOM_LONGITUDINAL, 240, 440),
    )
    return SeismicBeamContext(
        "SMRF-1",
        "seismic:R1",
        "B1",
        "SPAN-1",
        "J-L",
        "J-R",
        200,
        5800,
        300,
        500,
        450,
        30,
        415,
        bars,
        (
            SeismicLinkZone("L-END", 200, 1100, 100, 10, True, 135, 50),
            SeismicLinkZone("R-END", 4900, 5800, 100, 10, True, 135, 50),
        ),
        (),
        60_000,
        20_000,
        100_000_000,
        100_000_000,
        100_000_000,
        100_000_000,
        100_000,
        _qualified("is456.beam.shear.check/v1"),
        tuple(
            SeismicAnchorageCheck(
                beam_end,
                role,
                replace(
                    _qualified("is456.beam.anchorage.check/v1"),
                    result_id=f"result:anchorage:{beam_end.value}:{role.value}",
                ),
            )
            for beam_end in (BeamEnd.LEFT, BeamEnd.RIGHT)
            for role in (
                ReinforcementRole.TOP_LONGITUDINAL,
                ReinforcementRole.BOTTOM_LONGITUDINAL,
            )
        ),
        (
            DependentJointCheck("J-L", _qualified("joint:left")),
            DependentJointCheck("J-R", _qualified("joint:right")),
        ),
    )


def test_seismic_detailing_uses_actual_reinforcement_and_capacity_shear() -> None:
    result = check_seismic_detailing(
        SeismicDetailingCheckRequest(
            "IS13920-WP05",
            SeismicApplicability.IS13920_2016,
            _seismic_context(),
        )
    )

    assert result.engineering == "pass"
    assert result.outputs["continuous_top_bar_ids"] == ["T1", "T2"]
    assert result.outputs["continuous_bottom_bar_ids"] == ["B1", "B2"]
    assert result.outputs["governing_shear_n"] == pytest.approx(70_000)
    assert len(result.outputs["steel_face_checks"]) == 4


def test_geometry_only_seismic_input_is_not_evaluated() -> None:
    result = check_seismic_detailing(
        SeismicDetailingCheckRequest(
            "IS13920-WP05",
            SeismicApplicability.IS13920_2016,
            None,
        )
    )

    assert result.execution == "completed"
    assert result.engineering == "not_evaluated"
    assert result.completeness == "partial"


def test_seismic_detailing_requires_anchorage_operation_identity() -> None:
    context = _seismic_context()
    wrong_context = replace(
        context,
        anchorage_checks=tuple(
            replace(
                binding,
                check=_qualified("is456.beam.flexure.check/v1"),
            )
            for binding in context.anchorage_checks
        ),
    )
    wrong = check_seismic_detailing(
        SeismicDetailingCheckRequest(
            "IS13920-WP05",
            SeismicApplicability.IS13920_2016,
            wrong_context,
        )
    )
    assert wrong.engineering == "fail"
    assert any(
        item["rule_id"] == "ANCHORAGE_RESULTS" and not item["passed"]
        for item in wrong.outputs["rule_checks"]
    )


def test_seismic_detailing_rejects_duplicate_dependency_bindings() -> None:
    context = _seismic_context()
    duplicate_face = replace(
        context,
        anchorage_checks=(
            context.anchorage_checks[0],
            context.anchorage_checks[0],
            *context.anchorage_checks[2:],
        ),
    )
    duplicate_joint = replace(
        context,
        dependent_joint_checks=(
            context.dependent_joint_checks[0],
            context.dependent_joint_checks[0],
        ),
    )

    for malformed in (duplicate_face, duplicate_joint):
        result = check_seismic_detailing(
            SeismicDetailingCheckRequest(
                "IS13920-WP05",
                SeismicApplicability.IS13920_2016,
                malformed,
            )
        )
        assert result.execution == "rejected_input"
        assert result.diagnostics[0].code == "DEPENDENCY.BINDING_INVALID"


def _arrangement_request(
    *,
    top_second_x_mm: float = 240,
    obstacles: tuple[CircularObstacle, ...] = (),
) -> ReinforcementArrangementCheckRequest:
    return ReinforcementArrangementCheckRequest(
        "IS456-WP05",
        "B1",
        "SPAN-1@MID",
        "reinforcement:R1",
        300,
        500,
        25,
        20,
        (
            _bar(
                "T1",
                ReinforcementRole.TOP_LONGITUDINAL,
                60,
                60,
                diameter_mm=16,
            ),
            _bar(
                "T2",
                ReinforcementRole.TOP_LONGITUDINAL,
                top_second_x_mm,
                60,
                diameter_mm=16,
            ),
            _bar(
                "B1",
                ReinforcementRole.BOTTOM_LONGITUDINAL,
                60,
                440,
                diameter_mm=16,
            ),
            _bar(
                "B2",
                ReinforcementRole.BOTTOM_LONGITUDINAL,
                240,
                440,
                diameter_mm=16,
            ),
        ),
        (LinkCage("L1", 8, 29, 271, 29, 471, 16, True),),
        (
            ReinforcementRole.TOP_LONGITUDINAL,
            ReinforcementRole.BOTTOM_LONGITUDINAL,
        ),
        10,
        obstacles,
        PlacementOpening("PO-1", 260, 460, "sequence:R1"),
        True,
    )


def test_full_arrangement_checks_surfaces_spacing_centroids_and_placement() -> None:
    result = check_reinforcement_arrangement(_arrangement_request())

    assert result.engineering == "pass"
    assert result.outputs["link_checks"][0]["surface_covers_mm"] == {
        "left": 25,
        "right": 25,
        "top": 25,
        "bottom": 25,
    }
    assert len(result.outputs["horizontal_clearance_checks"]) == 2
    centroids = {
        item["role"]: item for item in result.outputs["role_centroids"]
    }
    assert centroids["top_longitudinal"]["centroid_y_from_top_mm"] == pytest.approx(60)
    assert centroids["bottom_longitudinal"][
        "centroid_y_from_top_mm"
    ] == pytest.approx(440)
    assert result.outputs["placement_check"]["passed"] is True


def test_tension_layer_only_cannot_qualify_full_arrangement() -> None:
    request = _arrangement_request()
    result = check_reinforcement_arrangement(
        ReinforcementArrangementCheckRequest(
            request.profile_id,
            request.member_id,
            request.station_id,
            request.reinforcement_revision_id,
            request.section_width_mm,
            request.section_depth_mm,
            request.nominal_cover_mm,
            request.maximum_aggregate_size_mm,
            request.bars[:2],
            request.links,
            (ReinforcementRole.TOP_LONGITUDINAL,),
            request.vertical_alignment_tolerance_mm,
        )
    )

    assert result.engineering == "not_evaluated"
    assert result.completeness == "partial"


def test_arrangement_obstacle_clash_is_completed_failure() -> None:
    result = check_reinforcement_arrangement(
        _arrangement_request(
            obstacles=(CircularObstacle("COUPLER", 60, 60, 20, 5),)
        )
    )

    assert result.execution == "completed"
    assert result.engineering == "fail"
    assert result.outputs["obstacle_checks"][0]["passed"] is False


def test_arrangement_orders_face_relative_layers_by_physical_y() -> None:
    request = _arrangement_request()
    extra_bottom = (
        _bar(
            "B3",
            ReinforcementRole.BOTTOM_LONGITUDINAL,
            60,
            400,
            diameter_mm=16,
            layer=2,
        ),
        _bar(
            "B4",
            ReinforcementRole.BOTTOM_LONGITUDINAL,
            240,
            400,
            diameter_mm=16,
            layer=2,
        ),
    )
    result = check_reinforcement_arrangement(
        replace(request, bars=(*request.bars, *extra_bottom))
    )

    layer_gap = next(
        item
        for item in result.outputs["vertical_clearance_checks"]
        if item["kind"] == "physical_layer_gap"
    )
    assert result.engineering == "pass"
    assert layer_gap["upper_layer"] == 2
    assert layer_gap["lower_layer"] == 1
    assert layer_gap["actual_clear_mm"] == pytest.approx(24)


def test_arrangement_checks_obstacles_against_link_segments() -> None:
    result = check_reinforcement_arrangement(
        _arrangement_request(
            obstacles=(CircularObstacle("SLEEVE", 150, 29, 10, 0),)
        )
    )

    assert result.engineering == "fail"
    assert any(
        item["reinforcement_kind"] == "link_segment" and not item["passed"]
        for item in result.outputs["obstacle_checks"]
    )
