"""Explicit typed calls for beam analysis, serviceability and detailing.

Run: python3 Python/examples/beam_checks_workflow.py

Each fixture declares its own input basis. Service components/strain and station
steel demand below are supplied teaching inputs, not inferred from the beam-line
solver. These bounded checks do not establish complete-member acceptance.
"""

from __future__ import annotations

import json
from dataclasses import replace

from structural_lib import beam as b


def run_checks() -> dict[str, b.OperationResult]:
    profile = "explicit-checks-example"
    bars = tuple(
        b.BarPosition(name, 20, x, y, face)
        for name, x, y, face in (
            ("B1", 50, 450, b.Face.BOTTOM),
            ("B2", 250, 450, b.Face.BOTTOM),
            ("T1", 50, 50, b.Face.TOP),
            ("T2", 250, 50, b.Face.TOP),
        )
    )
    axes = b.LocalAxes(
        "local-123", b.Vector3(1, 0, 0), b.Vector3(0, 1, 0), b.Vector3(0, 0, 1)
    )
    results: dict[str, b.OperationResult] = {}
    results["topology"] = b.define_beam_topology(
        b.BeamTopologyRequest(
            "B1",
            axes,
            (
                b.PhysicalSupport("A", 0, -200, 200),
                b.PhysicalSupport("B", 6000, 5800, 6200),
            ),
            (
                b.PhysicalSpan(
                    "S1", "A", "B", 450, (b.SectionRegion("R1", "300x500", 0, 6000),)
                ),
            ),
            (b.AnalysisElementMapping("E1", "S1", 0, 6000),),
        )
    )
    results["analysis"] = b.solve_beam_line(
        b.BeamLineRequest(
            model_id="teaching-line",
            load_case_id="SLS-illustration",
            nodes=(b.BeamNode("A", 0, True, False), b.BeamNode("B", 6000, True, False)),
            elements=(b.BeamElement("E1", "S1", "A", "B", 25_000, 3_125_000_000, -10),),
            station_intervals=12,
        )
    )
    # Preserve a real solver station as a source row; normalization is not a
    # strength check and does not turn this service case into an ultimate case.
    midspan = results["analysis"].outputs["stations"][6]
    results["actions"] = b.normalize_action_snapshot(
        b.RawActionSnapshot(
            source_id="python-beam-line",
            model_id="teaching-line",
            analysis_epoch_id=results["analysis"].calculation_id,
            result_epoch_id=results["analysis"].result_id,
            force_unit=b.ForceUnit.N,
            moment_unit=b.MomentUnit.N_MM,
            station_unit=b.LengthUnit.MM,
            local_axes=(axes,),
            rows=(
                b.RawActionRow(
                    source_row_id="E1-midspan",
                    member_id="B1",
                    physical_span_id="S1",
                    object_id="B1",
                    analysis_element_id="E1",
                    axis_id=axes.axis_id,
                    object_station=midspan["x_mm"],
                    element_station=midspan["distance_from_start_mm"],
                    load_case_id="SLS-illustration",
                    step_type="static",
                    step_number=None,
                    concurrency=b.ActionConcurrency.STATIC_CONCURRENT,
                    p=0,
                    v2=midspan["v2_n"],
                    v3=0,
                    t=0,
                    m2=0,
                    m3=midspan["m3_nmm"],
                ),
            ),
        )
    )
    geometry = b.ReinforcementGeometryRequest(profile, 300, 500, 25, 8, 25, bars)
    results["geometry"] = b.evaluate_geometry(geometry)
    results["depth"] = b.effective_depth(geometry, b.Face.BOTTOM)
    capacity = b.FlexuralCapacityRequest(
        profile, b.SectionKind.RECTANGULAR, 300, 500, 25, 415, bars, b.Face.BOTTOM
    )
    results["flexure"] = b.check_flexure(
        b.FlexureCheckRequest(capacity, positive_design_moment_knm=50)
    )
    link = b.TransverseLink("L8", 8, 2, 2, 150, 415, True, 242, 442)
    results["shear"] = b.check_shear(
        b.ShearCheckRequest(
            capacities=(
                b.ShearCapacityRequest(
                    profile,
                    b.ShearAxis.V2,
                    300,
                    450,
                    25,
                    sum(
                        float(b.bar_area(bar.diameter_mm).outputs["area_mm2"])
                        for bar in bars
                        if bar.face is b.Face.BOTTOM
                    ),
                    link,
                ),
            ),
            demands=(b.ShearDemand("ULS-station", b.ShearAxis.V2, 60),),
        )
    )
    results["torsion"] = b.check_torsion(
        b.TorsionCheckRequest(
            profile,
            b.ConcurrentActionRow(
                "ULS-row",
                "ULS-station",
                b.ActionBasis.STATIC_CONCURRENT,
                60,
                0,
                5,
                0,
                50,
                "declared-teaching-actions",
            ),
            capacity,
            link,
            tuple(bar.bar_id for bar in bars),
        )
    )

    total_limit = b.DeflectionLimitRequest(
        profile, 6000, b.DeflectionCriterion.TOTAL_FINAL
    )
    finishes_limit = b.DeflectionLimitRequest(
        profile, 6000, b.DeflectionCriterion.AFTER_FINISHES
    )
    results["deflection_limit"] = b.deflection_limit(total_limit)
    results["screening"] = b.check_deflection(
        b.DeflectionCheckRequest(
            profile,
            b.DeflectionMethod.SPAN_DEPTH_SCREENING,
            screening=b.DeflectionScreeningBasis(
                6000,
                450,
                b.SupportCondition.SIMPLY_SUPPORTED,
                1,
                1,
                1,
                "teaching-span",
                "explicit-unenhanced-factors",
            ),
        )
    )
    # Externally supplied illustrative components. AO09 aggregates these; it
    # does not derive creep, shrinkage or cracking evidence from an elastic run.
    components = b.CalculatedDeflectionBasis(
        service_action_snapshot_id="teaching-service-components",
        total_service_action_row_ids=("total",),
        sustained_service_action_row_ids=("sustained",),
        analysis_result_id="external-component-fixture",
        reinforcement_revision_id="detail-r1",
        effective_span_mm=6000,
        instantaneous_total_deflection_mm=8,
        instantaneous_sustained_deflection_mm=5,
        creep_multiplier=1.2,
        shrinkage_deflection_mm=1,
        finish_installation_age_days=90,
        deflection_at_finish_installation_mm=4,
        age_at_loading_days=28,
        assessment_age_days=1853,
        sustained_duration_days=1825,
        relative_humidity_percent=60,
        notional_size_mm=150,
        stiffness_method="supplied-teaching-component",
        cracking_method="supplied-teaching-component",
        creep_method="supplied-teaching-multiplier",
        shrinkage_method="supplied-teaching-component",
    )
    deflection = b.DeflectionCheckRequest(
        profile,
        b.DeflectionMethod.CALCULATED_COMPONENTS,
        calculated=components,
        total_limit=total_limit,
        after_finishes_limit=finishes_limit,
    )
    results["calculated_deflection"] = b.check_deflection(deflection)
    results["missing_history"] = b.check_deflection(
        replace(
            deflection, calculated=replace(components, sustained_duration_days=None)
        )
    )
    crack_limit = b.CrackWidthLimitRequest(profile, b.ExposureClass.MODERATE, False)
    results["crack_limit"] = b.crack_width_limit(crack_limit)
    crack = b.CrackWidthCheckRequest(
        profile_id=profile,
        member_id="B1",
        station_id="SLS-midspan",
        service_action_row_id="supplied-SLS-row",
        reinforcement_revision_id="detail-r1",
        section_width_mm=300,
        section_depth_mm=500,
        neutral_axis_depth_from_compression_face_mm=150,
        tension_face=b.Face.BOTTOM,
        bars=bars,
        surface_point_x_from_left_mm=150,
        service_steel_stress_n_per_mm2=200,
        steel_yield_strength_n_per_mm2=415,
        steel_modulus_n_per_mm2=200_000,
        mean_strain_at_tension_surface=0.0006,
        limit=crack_limit,
    )
    results["crack_width"] = b.check_crack_width(crack)
    results["missing_strain"] = b.check_crack_width(
        replace(crack, mean_strain_at_tension_surface=None)
    )

    development = b.DevelopmentLengthRequest(
        profile, 20, 0.87 * 415, 415, 25, b.BarSurface.DEFORMED, b.StressState.TENSION
    )
    results["development"] = b.development_length(development)
    results["anchorage"] = b.check_anchorage(
        b.AnchorageCheckRequest(
            profile,
            "B1",
            "detail-r1",
            (
                b.AnchoragePath(
                    bar_id="B1",
                    critical_section_id="teaching-discontinuity",
                    location=b.AnchorageLocation.DISCONTINUITY,
                    direction=b.AnchorageDirection.INCREASING_X,
                    path_start_x_mm=0,
                    path_end_x_mm=6000,
                    critical_section_x_mm=5000,
                    support_id=None,
                    support_near_face_x_mm=None,
                    support_centre_x_mm=None,
                    bends=(),
                    bend_schedule_reference=None,
                    development=development,
                ),
            ),
        )
    )
    paths = tuple(
        b.LongitudinalBarPath(
            bar.bar_id,
            bar.bar_id,
            (
                b.ReinforcementRole.BOTTOM_LONGITUDINAL
                if bar.face is b.Face.BOTTOM
                else b.ReinforcementRole.TOP_LONGITUDINAL
            ),
            bar.diameter_mm,
            bar.layer,
            bar.x_from_left_mm,
            bar.y_from_top_mm,
            0,
            6000,
            0.87 * 415,
        )
        for bar in bars
    )
    results["continuity"] = b.check_laps_and_curtailment(
        b.LapCurtailmentCheckRequest(
            profile_id=profile,
            member_id="B1",
            physical_span_id="S1",
            demand_revision_id="teaching-500mm2",
            reinforcement_revision_id="detail-r1",
            member_start_x_mm=0,
            member_end_x_mm=6000,
            effective_depth_mm=450,
            concrete_grade_n_per_mm2=25,
            steel_yield_strength_n_per_mm2=415,
            bar_surface=b.BarSurface.DEFORMED,
            bars=paths,
            demands=(
                b.StationSteelDemand(
                    "midspan",
                    3000,
                    b.ReinforcementRole.BOTTOM_LONGITUDINAL,
                    500,
                    60_000,
                    results["shear"].outputs["checks"][0]["capacity_kn"] * 1000,
                    "declared-demand",
                ),
            ),
            # One of two bottom bar lines is lapped (50%) over a declared 1 m zone.
            # The other bottom line and both top lines remain continuous.
            splices=(
                b.SpliceDetail(
                    splice_id="bottom-lap-1",
                    kind=b.SpliceKind.LAP,
                    bar_ids=("B1",),
                    start_x_mm=2000,
                    end_x_mm=3000,
                    stress_state=b.StressState.TENSION,
                    direct_tension=False,
                    percentage_spliced_at_section=50,
                    stagger_group="A",
                ),
            ),
            curtailments=(),
        )
    )
    results["arrangement"] = b.check_reinforcement_arrangement(
        b.ReinforcementArrangementCheckRequest(
            profile_id=profile,
            member_id="B1",
            station_id="midspan",
            reinforcement_revision_id="detail-r1",
            section_width_mm=300,
            section_depth_mm=500,
            nominal_cover_mm=25,
            maximum_aggregate_size_mm=20,
            bars=paths,
            links=(b.LinkCage("L8", 8, 29, 271, 29, 471, 16, True),),
            required_roles=(
                b.ReinforcementRole.BOTTOM_LONGITUDINAL,
                b.ReinforcementRole.TOP_LONGITUDINAL,
            ),
            vertical_alignment_tolerance_mm=1,
        )
    )
    results["ordinary_seismic"] = b.check_seismic_detailing(
        b.SeismicDetailingCheckRequest(profile, b.SeismicApplicability.ORDINARY_IS456)
    )
    results["missing_seismic_context"] = b.check_seismic_detailing(
        b.SeismicDetailingCheckRequest(profile, b.SeismicApplicability.IS13920_2016)
    )
    return results


def main() -> None:
    results = run_checks()
    not_evaluated = {
        "analysis",
        "missing_history",
        "missing_strain",
        "ordinary_seismic",
        "missing_seismic_context",
    }
    for name, result in results.items():
        expected = (
            b.EngineeringState.NOT_EVALUATED
            if name in not_evaluated
            else b.EngineeringState.PASS
        )
        assert result.execution is b.ExecutionState.COMPLETED, name
        assert result.engineering is expected, (
            name,
            result.engineering,
            [item.code for item in result.diagnostics],
        )
    assert results["analysis"].outputs["stations"][6]["m3_nmm"] == 45_000_000
    assert results["actions"].outputs["rows"][0]["m3_nmm"] == 45_000_000
    assert (
        results["screening"].outputs["result_kind"]
        == "screening_not_calculated_displacement"
    )
    assert results["calculated_deflection"].outputs["total_final_deflection_mm"] == 15
    assert (
        results["ordinary_seismic"].applicability is b.ApplicabilityState.NOT_APPLICABLE
    )
    print(
        json.dumps(
            {
                name: {
                    "execution": result.execution,
                    "engineering": result.engineering,
                    "applicability": result.applicability,
                    "diagnostics": [item.code for item in result.diagnostics],
                }
                for name, result in results.items()
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
