from dataclasses import replace
from math import pi

import pytest

from structural_lib.beam import (
    BarMarkSummary,
    BarPathOutput,
    BarPathRole,
    CompletenessState,
    EffectiveDepthIteration,
    EngineeringState,
    ExecutionState,
    FreshnessState,
    MemberLeafEvidence,
    MemberLeafExpectation,
    MemberLeafQualification,
    MemberLocalCoordinateSystem,
    PathPoint,
    PathSegmentKind,
    ResolvedBarPath,
    ResolvedPathSegment,
)
from structural_lib.beam.member import MemberDesignOutput
from structural_lib.beam.project import CheckScope
from structural_lib.beam.semantics import ApplicabilityState, semantic_hash
from structural_lib.construction import (
    BbsOutput,
    BbsRequest,
    ConcreteNetSegment,
    ConstructionCostOutput,
    ConstructionCostRequest,
    ConstructionQuantityOutput,
    ConstructionQuantityRequest,
    CostBasis,
    CostCategory,
    CostRate,
    CuttingStockPolicy,
    FormworkContactFace,
    FormworkFaceCategory,
    FormworkMeasurementState,
    HumanCostScope,
    LinkPlacementZone,
    MeasuredRateProfile,
    ShapeConvention,
    SpliceKind,
    SpliceRecord,
    WastePricingBasis,
    calculate_construction_quantities,
    create_bbs,
    estimate_construction_cost,
)
from structural_lib.construction.contracts import WasteLedger
from structural_lib.reporting import (
    CalculationPackageMetadata,
    CalculationPackageProfile,
    CalculationPackageRequest,
    CalculationTrace,
    DrawingDatum,
    DrawingView,
    HumanAction,
    HumanActionKind,
    ResultBinding,
    create_calculation_package,
)


def _axes() -> MemberLocalCoordinateSystem:
    return MemberLocalCoordinateSystem(
        "B1-local",
        "member_station_x",
        "section_x_from_left",
        "section_y_from_top",
    )


def _straight_path(
    bar_id: str,
    mark: str,
    length_mm: float,
    *,
    station_x_mm: float = 0,
    section_y_mm: float = 50,
    diameter_mm: float = 20,
    role: BarPathRole = BarPathRole.TOP_LONGITUDINAL,
    splice_ids: tuple[str, ...] = (),
) -> ResolvedBarPath:
    start = PathPoint(station_x_mm, 50, section_y_mm)
    end = (
        PathPoint(station_x_mm + length_mm, 50, section_y_mm)
        if role is not BarPathRole.TRANSVERSE_LINK
        else PathPoint(station_x_mm, 50 + length_mm, section_y_mm)
    )
    segment = ResolvedPathSegment(
        f"{bar_id}:001",
        PathSegmentKind.TANGENT_STRAIGHT,
        start,
        end,
        length_mm,
    )
    return ResolvedBarPath(
        bar_id,
        mark,
        role,
        1,
        diameter_mm,
        415,
        1,
        False,
        (f"{bar_id}:N1", f"{bar_id}:N2"),
        (segment,),
        length_mm,
        12000,
        (),
        splice_ids,
    )


def _schedule(*paths: ResolvedBarPath) -> BarPathOutput:
    marks = []
    for mark in sorted({item.bar_mark for item in paths}):
        marked = [item for item in paths if item.bar_mark == mark]
        first = marked[0]
        marks.append(
            BarMarkSummary(
                mark,
                first.role,
                first.diameter_mm,
                first.steel_grade_n_per_mm2,
                first.bundle_size,
                first.closed,
                tuple(item.bar_id for item in marked),
                len(marked),
                first.developed_centreline_length_mm,
                first.compatible_stock_length_mm,
            )
        )
    return BarPathOutput(
        "PROFILE-1",
        "project-basis-1",
        "criteria-r1",
        "B1",
        "SPAN-1",
        "topology-r1",
        "detail-r1",
        _axes(),
        paths,
        tuple(marks),
        True,
    )


def _bbs_request(schedule: BarPathOutput, **changes: object) -> BbsRequest:
    values = {
        "profile_id": "PROFILE-1",
        "project_basis_id": "project-basis-1",
        "member_id": "B1",
        "detail_revision_id": "detail-r1",
        "schedule_result_id": "schedule-result-1",
        "schedule_output_payload_id": semantic_hash("output_payload_id", schedule),
        "schedule": schedule,
        "shape_convention": ShapeConvention("IS2502", "shape-r1"),
        "stock_policy": CuttingStockPolicy(
            "STOCK-POLICY",
            "cut-r1",
            (6000, 9000, 12000),
            0,
            500,
        ),
        "steel_density_kg_per_m3": 7850,
    }
    values.update(changes)
    return BbsRequest(**values)


def _typed_bbs(result: object) -> BbsOutput:
    request = result  # keeps type checker diagnostics local to this test helper
    assert isinstance(request, BbsOutput)
    return request


def test_bbs_and_quantity_independent_reference_fixture() -> None:
    schedule = _schedule(
        *(
            _straight_path(f"BAR-{index}", "M1", 6000, section_y_mm=40 + index * 20)
            for index in range(1, 5)
        )
    )
    bbs_result = create_bbs(_bbs_request(schedule))
    bbs_data = bbs_result.outputs["bbs"]
    assert bbs_data["scheduled_steel_mass_kg"] == pytest.approx(59.18760559)

    bbs = BbsOutput(
        "PROFILE-1",
        "project-basis-1",
        "B1",
        "detail-r1",
        "schedule-result-1",
        "shape-r1",
        "cut-r1",
        (),
        (),
        (),
        (),
        24000,
        24000,
        0,
        0,
        0,
        bbs_data["scheduled_steel_mass_kg"],
        bbs_data["purchased_stock_mass_kg"],
        "heuristic_first_fit_decreasing",
        True,
    )
    # Preserve the actual schedule rows used by AO04.
    bbs = replace(bbs, rows=tuple(_bbs_rows_from_mapping(bbs_data["rows"])))
    quantity = calculate_construction_quantities(
        ConstructionQuantityRequest(
            "PROFILE-1",
            "project-basis-1",
            "B1",
            "detail-r1",
            "bbs-result-1",
            semantic_hash("output_payload_id", bbs),
            bbs,
            "beam-owns-net-prism-v1",
            "contact-face-v1",
            (ConcreteNetSegment("C1", "B1", "M25", "VOL-B1", 300 * 500, 6000, False),),
            (
                FormworkContactFace("F-S", "B1", FormworkFaceCategory.SOFFIT, "FACE-S", 300 * 6000, FormworkMeasurementState.INCLUDED),
                FormworkContactFace("F-L", "B1", FormworkFaceCategory.SIDE_LEFT, "FACE-L", 500 * 6000, FormworkMeasurementState.INCLUDED),
                FormworkContactFace("F-R", "B1", FormworkFaceCategory.SIDE_RIGHT, "FACE-R", 500 * 6000, FormworkMeasurementState.INCLUDED),
            ),
        )
    )

    assert quantity.outputs["quantities"]["steel_scheduled_mass_kg"] == pytest.approx(59.18760559)
    assert quantity.outputs["quantities"]["concrete_volume_m3"] == pytest.approx(0.9)
    assert quantity.outputs["quantities"]["formwork_area_m2"] == pytest.approx(7.8)
    assert quantity.outputs["quantities"]["direct_cost"] is None


def _bbs_rows_from_mapping(rows: list[dict[str, object]]) -> list[object]:
    from structural_lib.construction.contracts import BbsRow, ShapeDimension

    return [
        BbsRow(
            row["bar_mark"],
            BarPathRole(row["role"]),
            row["diameter_mm"],
            row["steel_grade_n_per_mm2"],
            row["bundle_size"],
            row["placement_count"],
            row["scheduled_bar_count"],
            row["shape_code"],
            tuple(
                ShapeDimension(
                    item["dimension_id"],
                    item["segment_kind"],
                    item["centreline_length_mm"],
                    item["bend_radius_mm"],
                    item["bend_angle_degrees"],
                )
                for item in row["dimensions"]
            ),
            row["centreline_developed_length_each_mm"],
            row["fabrication_cut_length_each_mm"],
            row["scheduled_cut_length_mm"],
            row["theoretical_mass_kg"],
            tuple(row["source_path_ids"]),
            tuple(row["splice_ids"]),
        )
        for row in rows
    ]


def test_bend_centreline_and_cut_lengths_are_separate_fields() -> None:
    diameter = 16.0
    centreline_radius = 32 + diameter / 2
    arc = centreline_radius * pi / 2
    segments = (
        ResolvedPathSegment("B1:001", PathSegmentKind.TANGENT_STRAIGHT, PathPoint(0, 50, 50), PathPoint(100, 50, 50), 100),
        ResolvedPathSegment("B1:002", PathSegmentKind.BEND_ARC, PathPoint(100, 50, 50), PathPoint(100, 50, 150), arc, PathPoint(60, 50, 90), centreline_radius, 90),
        ResolvedPathSegment("B1:003", PathSegmentKind.TANGENT_STRAIGHT, PathPoint(100, 50, 150), PathPoint(100, 50, 250), 100),
    )
    path = ResolvedBarPath("B1", "M16", BarPathRole.TOP_LONGITUDINAL, 1, diameter, 415, 1, False, ("N1", "N2", "N3"), segments, 200 + arc, 6000, (), ())
    result = create_bbs(_bbs_request(_schedule(path)))
    row = result.outputs["bbs"]["rows"][0]

    assert row["dimensions"][1]["centreline_length_mm"] == pytest.approx(62.83185307)
    assert row["centreline_developed_length_each_mm"] == pytest.approx(200 + arc)
    assert row["fabrication_cut_length_each_mm"] == pytest.approx(200 + arc)


def test_cutting_plan_separates_kerf_reusable_offcut_and_waste() -> None:
    schedule = _schedule(
        _straight_path("B1", "M1", 5000),
        _straight_path("B2", "M1", 5000, section_y_mm=80),
    )
    result = create_bbs(
        _bbs_request(
            schedule,
            stock_policy=CuttingStockPolicy("P", "r1", (9000,), 3, 500),
        )
    )
    output = result.outputs["bbs"]

    assert len(output["stock_pieces"]) == 2
    assert output["kerf_length_mm"] == pytest.approx(6)
    assert output["reusable_offcut_length_mm"] == pytest.approx(7994)
    assert output["waste_length_mm"] == 0
    assert output["stock_length_mm"] == pytest.approx(
        output["scheduled_cut_length_mm"]
        + output["kerf_length_mm"]
        + output["reusable_offcut_length_mm"]
        + output["waste_length_mm"]
    )
    assert output["allocation_optimality"] == "heuristic_first_fit_decreasing"


def test_link_zone_boundary_has_one_owner_and_matches_physical_paths() -> None:
    paths = tuple(
        _straight_path(
            f"L-{station}",
            "L1",
            200,
            station_x_mm=station,
            diameter_mm=8,
            role=BarPathRole.TRANSVERSE_LINK,
        )
        for station in (0, 100, 200)
    )
    zones = (
        LinkPlacementZone("Z1", "L1", 0, 100, 100, True, True),
        LinkPlacementZone("Z2", "L1", 100, 200, 100, False, True),
    )
    result = create_bbs(_bbs_request(_schedule(*paths), link_zones=zones))

    assert [item["stations_x_mm"] for item in result.outputs["bbs"]["link_zones"]] == [[0, 100], [200]]
    duplicated = create_bbs(
        _bbs_request(
            _schedule(*paths),
            link_zones=(zones[0], replace(zones[1], include_start=True)),
        )
    )
    assert duplicated.diagnostics[0].code == "BBS.LINK_BOUNDARY_DUPLICATE"

    missing = create_bbs(_bbs_request(_schedule(*paths)))
    assert missing.diagnostics[0].code == "BBS.LINK_ZONE_REQUIRED"


def test_bbs_rejects_detached_payload_and_inconsistent_mark_summary() -> None:
    schedule = _schedule(
        _straight_path("B1", "M1", 6000),
        _straight_path("B2", "M1", 6000, section_y_mm=80),
    )
    detached = create_bbs(
        _bbs_request(schedule, schedule_output_payload_id="output_payload_id:wrong")
    )
    bad_summary = replace(schedule.marks[0], count=1)
    inconsistent_schedule = replace(schedule, marks=(bad_summary,))
    inconsistent = create_bbs(_bbs_request(inconsistent_schedule))

    assert detached.diagnostics[0].code == "BBS.SCHEDULE_BINDING"
    assert inconsistent.diagnostics[0].code == "BBS.SCHEDULE_RECONCILIATION"


def test_lap_and_coupler_are_explicit_without_added_cut_length() -> None:
    path = _straight_path("B1", "M1", 6000, splice_ids=("S-LAP", "S-COUPLER"))
    result = create_bbs(
        _bbs_request(
            _schedule(path),
            splice_records=(
                SpliceRecord("S-LAP", SpliceKind.LAP, 2500, "lap-check-1"),
                SpliceRecord("S-COUPLER", SpliceKind.COUPLER, 5000, "coupler-cert-1", 1),
            ),
        )
    )
    output = result.outputs["bbs"]

    assert output["scheduled_cut_length_mm"] == 6000
    assert output["couplers"][0]["count"] == 1
    assert output["rows"][0]["splice_ids"] == ["S-COUPLER", "S-LAP"]


def _quantity_output() -> ConstructionQuantityOutput:
    return ConstructionQuantityOutput(
        "PROFILE-1",
        "project-basis-1",
        "B1",
        "detail-r1",
        "bbs-result-1",
        "concrete-policy-r1",
        "formwork-policy-r1",
        (),
        (),
        (),
        WasteLedger(3, 500, 20),
        10,
        12,
        2,
        3,
        1,
    )


def _rate_profile(**changes: object) -> MeasuredRateProfile:
    values = {
        "profile_id": "RATES-1",
        "revision_id": "rates-r1",
        "currency": "INR",
        "valuation_date": "2026-09-04",
        "time_zone": "Asia/Calcutta",
        "geography": "Pune, Maharashtra",
        "source": "project quotation set Q-17",
        "scope": HumanCostScope(
            (CostCategory.MATERIAL, CostCategory.FORMWORK),
            (CostCategory.COUPLER, CostCategory.LABOUR, CostCategory.PLANT),
        ),
        "rates": (
            CostRate("steel", CostCategory.MATERIAL, CostBasis.STEEL_SCHEDULED_MASS_KG, "reinforcement", "5", "Q-17 steel"),
            CostRate("concrete", CostCategory.MATERIAL, CostBasis.CONCRETE_VOLUME_M3, "M25 concrete", "100", "Q-17 concrete"),
            CostRate("formwork", CostCategory.FORMWORK, CostBasis.FORMWORK_AREA_M2, "beam formwork", "10", "Q-17 formwork"),
        ),
        "waste_pricing_basis": WastePricingBasis.SCHEDULED_STEEL,
        "overhead_percent_decimal": "10",
        "tax_percent_decimal": "18",
    }
    values.update(changes)
    return MeasuredRateProfile(**values)


def test_dated_itemized_cost_uses_decimal_arithmetic_and_explicit_scope() -> None:
    result = estimate_construction_cost(
        ConstructionCostRequest(
            "PROFILE-1",
            "project-basis-1",
            "B1",
            "detail-r1",
            "quantity-result-1",
            semantic_hash("output_payload_id", _quantity_output()),
            _quantity_output(),
            _rate_profile(),
        )
    )
    output = result.outputs["cost"]

    assert output["direct_subtotal_decimal"] == "280.00"
    assert output["overhead_decimal"] == "28.00"
    assert output["pre_tax_total_decimal"] == "308.00"
    assert output["tax_decimal"] == "55.44"
    assert output["total_decimal"] == "363.44"
    assert {item["source_quantity_result_id"] for item in output["lines"]} == {"quantity-result-1"}


def test_cost_rejects_incomplete_identity_and_double_priced_waste() -> None:
    quantities = _quantity_output()
    request = ConstructionCostRequest("PROFILE-1", "project-basis-1", "B1", "detail-r1", "quantity-result-1", semantic_hash("output_payload_id", quantities), quantities, _rate_profile())
    missing_geography = estimate_construction_cost(replace(request, rate_profile=replace(request.rate_profile, geography="")))
    stock_rate = replace(request.rate_profile.rates[0], basis=CostBasis.STEEL_STOCK_MASS_KG)
    double_count = estimate_construction_cost(replace(request, rate_profile=replace(request.rate_profile, rates=(stock_rate, *request.rate_profile.rates[1:]))))
    cross_project = estimate_construction_cost(
        replace(
            request,
            quantities=replace(quantities, project_basis_id="other-project"),
            quantity_output_payload_id=semantic_hash(
                "output_payload_id",
                replace(quantities, project_basis_id="other-project"),
            ),
        )
    )

    assert missing_geography.diagnostics[0].code == "COST.IDENTITY"
    assert double_count.diagnostics[0].code == "COST.WASTE_DOUBLE_COUNT"
    assert cross_project.diagnostics[0].code == "COST.QUANTITY_STALE"


def test_cost_displayed_lines_reconcile_after_currency_rounding() -> None:
    quantities = replace(
        _quantity_output(),
        steel_scheduled_mass_kg=1,
        concrete_volume_m3=1,
        formwork_area_m2=0,
    )
    profile = replace(
        _rate_profile(),
        scope=HumanCostScope(
            (CostCategory.MATERIAL,),
            (
                CostCategory.FORMWORK,
                CostCategory.COUPLER,
                CostCategory.LABOUR,
                CostCategory.PLANT,
            ),
        ),
        rates=(
            CostRate("a", CostCategory.MATERIAL, CostBasis.STEEL_SCHEDULED_MASS_KG, "steel", "0.005", "rate-a"),
            CostRate("b", CostCategory.MATERIAL, CostBasis.CONCRETE_VOLUME_M3, "concrete", "0.005", "rate-b"),
        ),
        overhead_percent_decimal="0",
        tax_percent_decimal="0",
    )
    result = estimate_construction_cost(
        ConstructionCostRequest(
            "PROFILE-1",
            "project-basis-1",
            "B1",
            "detail-r1",
            "quantity-result-1",
            semantic_hash("output_payload_id", quantities),
            quantities,
            profile,
        )
    )
    output = result.outputs["cost"]

    assert [item["amount_decimal"] for item in output["lines"]] == ["0.00", "0.00"]
    assert output["direct_subtotal_decimal"] == "0.00"


def _binding(
    operation: str,
    result_id: str,
    payload: object,
    *,
    freshness: FreshnessState = FreshnessState.CURRENT,
) -> ResultBinding:
    return ResultBinding(operation, result_id, f"input:{result_id}", f"calculation:{result_id}", ExecutionState.COMPLETED, ApplicabilityState.APPLICABLE, EngineeringState.PASS, CompletenessState.COMPLETE_FOR_SCOPE, freshness, semantic_hash("output_payload_id", payload))


def _member_output() -> MemberDesignOutput:
    expectation = MemberLeafExpectation("flexure@B1", "flexure", "is456.beam.flexure.check/v1", "B1", CheckScope.MEMBER, ApplicabilityState.APPLICABLE, "is456-r1")
    evidence = MemberLeafEvidence("flexure@B1", expectation.operation_semantic_id, "leaf-result-1", ExecutionState.COMPLETED, ApplicabilityState.APPLICABLE, EngineeringState.PASS, CompletenessState.COMPLETE_FOR_SCOPE, FreshnessState.CURRENT, "is456-r1", "flexure-r1", "input:leaf", "calculation:leaf", 100, 120, 120, "kNm", 0.8333333333)
    iteration = EffectiveDepthIteration(1, "reinforcement-r1", 450, (evidence.result_id,), True)
    return MemberDesignOutput("project-basis-1", "profile-r1", "B1", "topology-r1", "actions-r1", "reinforcement-r1", "scope-r1", (expectation,), (MemberLeafQualification(expectation, evidence, True, ()),), (iteration,), expectation.leaf_id, evidence.result_id, evidence.governing_utilization, True)


def _package_request() -> CalculationPackageRequest:
    schedule = _schedule(_straight_path("B1", "M1", 6000))
    bbs = BbsOutput("PROFILE-1", "project-basis-1", "B1", "detail-r1", "schedule-result-1", "shape-r1", "cut-r1", (), (), (), (), 6000, 6000, 0, 0, 0, 14.7969014, 14.7969014, "heuristic_first_fit_decreasing", True)
    quantities = _quantity_output()
    member = _member_output()
    return CalculationPackageRequest(
        CalculationPackageMetadata("PROJECT-1", "Office", "project-r1", "B1", "package-r1", "engine-1", ("is456-r1", "rebar-r1"), "2026-09-04T10:00:00+05:30"),
        CalculationPackageProfile("CALC-PROFILE", "calc-profile-r1", "beam-template-r1", ("flexure@B1",), ("inputs", "calculations", "reinforcement", "quantities", "drawings", "signatures")),
        member,
        _binding("is456.beam_member.design/v1", "member-result-1", member),
        schedule,
        _binding("structural.reinforcement_paths.resolve/v1", "schedule-result-1", schedule),
        bbs,
        _binding("structural.bbs.create/v1", "bbs-result-1", bbs),
        quantities,
        _binding("structural.construction_quantities.calculate/v1", "quantity-result-1", quantities),
        None,
        None,
        ("Loads are supplied at the stated design revision.",),
        (CalculationTrace("TRACE-1", "flexure@B1", "IS456-flexure", "rectangular-flexure-v1", "Mu=100 kNm; capacity=120 kNm", 100, 120, 120, "kNm", 0.8333333333, True),),
        (DrawingView("ELEV-1", "beam_elevation", "detail-r1", (DrawingDatum("D1", "B1", "bar mark", "M1"),)),),
        ("Valid for the declared ordinary beam profile.",),
        (HumanAction("ACT-1", "PE-123", "A. Engineer", "structural engineer", HumanActionKind.PREPARED, "2026-09-04T10:30:00+05:30", "B1", "member-result-1"),),
    )


def test_calculation_package_is_replayable_and_keeps_real_human_actions() -> None:
    result = create_calculation_package(_package_request())
    output = result.outputs["calculation_package"]

    assert result.completeness == "complete_for_scope"
    assert output["issue_state"] == "issue_ready"
    assert output["active_approval"] is False
    assert output["leaves"][0]["result_id"] == "leaf-result-1"
    assert output["human_actions"][0]["actor_id"] == "PE-123"
    assert output["calculation_package_id"].startswith("calculation_package_id:pf4-canonical-json-v1:")
    assert {item["section_id"] for item in output["render_sections"]} == {"inputs", "calculations", "reinforcement", "quantities", "drawings", "signatures"}


def test_stale_package_is_visible_draft_and_cannot_activate_approval() -> None:
    request = _package_request()
    approved = replace(request.human_actions[0], action=HumanActionKind.APPROVED)
    result = create_calculation_package(
        replace(
            request,
            member_binding=replace(request.member_binding, freshness=FreshnessState.STALE),
            human_actions=(approved,),
        )
    )
    output = result.outputs["calculation_package"]

    assert result.completeness == "partial"
    assert result.freshness == "stale"
    assert output["issue_state"] == "draft"
    assert output["active_approval"] is False
    assert result.diagnostics[0].code == "PACKAGE.EVIDENCE_INCOMPLETE"


def test_package_rejects_detached_payload_and_changed_trace_values() -> None:
    request = _package_request()
    detached = create_calculation_package(
        replace(
            request,
            member_binding=replace(
                request.member_binding,
                output_payload_id="output_payload_id:wrong",
            ),
        )
    )
    changed_trace = replace(request.traces[0], provided_value=999)
    mismatched = create_calculation_package(
        replace(request, traces=(changed_trace,))
    )

    assert detached.diagnostics[0].code == "PACKAGE.PAYLOAD_BINDING"
    assert mismatched.diagnostics[0].code == "PACKAGE.TRACE_VALUE"


def test_package_rejects_cost_from_another_project_basis() -> None:
    request = _package_request()
    cost = ConstructionCostOutput(
        "PROFILE-1",
        "other-project",
        "B1",
        "detail-r1",
        request.quantity_binding.result_id,
        "RATES-1",
        "rates-r1",
        "INR",
        "2026-09-04",
        "Pune, Maharashtra",
        "project quotation Q-17",
        (),
        (),
        tuple(CostCategory),
        "0.00",
        "0.00",
        "0.00",
        "0.00",
        "0.00",
    )
    result = create_calculation_package(
        replace(
            request,
            cost=cost,
            cost_binding=_binding(
                "structural.construction_cost.estimate/v1",
                "cost-result-1",
                cost,
            ),
        )
    )

    assert result.diagnostics[0].code == "PACKAGE.IDENTITY_CONFLICT"


def test_approval_uses_absolute_time_and_requires_passing_bindings() -> None:
    request = _package_request()
    prepared = replace(
        request.human_actions[0],
        action_id="ACT-PREPARED",
        recorded_at_utc="2026-09-04T12:00:00+05:30",
    )
    approved = replace(
        prepared,
        action_id="ACT-APPROVED",
        action=HumanActionKind.APPROVED,
        recorded_at_utc="2026-09-04T07:00:00Z",
    )
    current = create_calculation_package(
        replace(request, human_actions=(prepared, approved))
    )
    failed_dependency = create_calculation_package(
        replace(
            request,
            bbs_binding=replace(
                request.bbs_binding,
                engineering=EngineeringState.FAIL,
            ),
            human_actions=(approved,),
        )
    )

    assert current.outputs["calculation_package"]["active_approval"] is True
    assert failed_dependency.outputs["calculation_package"]["issue_state"] == "draft"
    assert (
        failed_dependency.outputs["calculation_package"]["active_approval"] is False
    )
