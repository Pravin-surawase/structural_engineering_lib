"""Connect physical beam records, profile checks, and construction outputs.

Run against the current source build: python3 Python/examples/physical_member_workflow.py

This is a software composition example with a deliberately limited teaching
profile: geometry, positive flexure, and ordinary-frame seismic applicability.
It is not a complete building-design profile. Shear, torsion, serviceability,
anchorage, durability, and construction approval are outside this fixture.
The four straight longitudinal bars are a quantity fixture, not issued details.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, replace

from structural_lib import beam, construction, reporting


@dataclass(frozen=True)
class Workflow:
    """Retain actual results so callers can inspect every state and identity."""

    project: beam.OperationResult
    member: beam.OperationResult
    missing_member: beam.OperationResult
    stale_member: beam.OperationResult
    paths: beam.OperationResult
    bbs: beam.OperationResult
    quantities: beam.OperationResult
    cost: beam.OperationResult
    package: beam.OperationResult
    draft_package: beam.OperationResult


def require_complete(result: beam.OperationResult) -> None:
    """Stop at a failed/incomplete calculation before consuming its outputs."""
    if not (
        result.execution is beam.ExecutionState.COMPLETED
        and result.engineering is beam.EngineeringState.PASS
        and result.completeness is beam.CompletenessState.COMPLETE_FOR_SCOPE
        and result.freshness is beam.FreshnessState.CURRENT
    ):
        raise ValueError(result.to_dict())


def build_workflow() -> Workflow:
    """Run the same supplied physical bars through the existing pure owners."""
    profile_id, member_id, detail_revision = "teaching-profile", "B1", "detail-r1"
    bars = (
        beam.BarPosition("BOTTOM-1", 20, 50, 450, beam.Face.BOTTOM),
        beam.BarPosition("BOTTOM-2", 20, 250, 450, beam.Face.BOTTOM),
        beam.BarPosition("TOP-1", 20, 50, 50, beam.Face.TOP),
        beam.BarPosition("TOP-2", 20, 250, 50, beam.Face.TOP),
    )
    geometry_request = beam.ReinforcementGeometryRequest(
        profile_id=profile_id,
        width_mm=300,
        depth_mm=500,
        nominal_cover_mm=25,
        link_diameter_mm=8,
        minimum_clear_spacing_mm=25,
        bars=bars,
    )
    geometry = beam.evaluate_geometry(geometry_request)
    depth = beam.effective_depth(geometry_request, beam.Face.BOTTOM)
    flexure = beam.check_flexure(
        beam.FlexureCheckRequest(
            capacity=beam.FlexuralCapacityRequest(
                profile_id=profile_id,
                section_kind=beam.SectionKind.RECTANGULAR,
                web_width_mm=300,
                depth_mm=500,
                concrete_strength_n_per_mm2=25,
                steel_yield_strength_n_per_mm2=415,
                bars=bars,
                tension_face=beam.Face.BOTTOM,
            ),
            positive_design_moment_knm=50,
        )
    )
    seismic = beam.check_seismic_detailing(
        beam.SeismicDetailingCheckRequest(
            profile_id,
            beam.SeismicApplicability.ORDINARY_IS456,
        )
    )
    for result in (geometry, depth, flexure):
        require_complete(result)

    # The profile is explicit and frozen; leaf results never decide what checks
    # a real project requires. This limited teaching profile is not a default.
    checks = (("geometry", geometry), ("flexure", flexure), ("seismic", seismic))
    project_result = beam.create_beam_project(
        beam.BeamProjectRequest(
            project=beam.BeamProjectDefinition(
                "TEACHING", "Physical beam API example", "r1"
            ),
            unit_basis=beam.StructuralUnitBasis("mm", "N", "Nmm", "N/mm2"),
            code_data_revisions=tuple(
                beam.RevisionBinding(
                    name,
                    result.provenance.code_data_revision_id,
                    "; ".join(result.provenance.source_references),
                )
                for name, result in checks
            ),
            profile=beam.BeamDesignProfile(
                profile_id=profile_id,
                revision_id="profile-r1",
                design_code="IS 456:2000",
                seismic_design_profile=beam.SeismicDesignProfile.ORDINARY_IS456,
                check_rules=tuple(
                    beam.DesignCheckRule(
                        rule_id=name,
                        operation_semantic_id=result.operation_semantic_id,
                        scope=beam.CheckScope.MEMBER,
                        expected_applicability=(
                            beam.ApplicabilityState.NOT_APPLICABLE
                            if name == "seismic"
                            else beam.ApplicabilityState.APPLICABLE
                        ),
                        source_reference="Explicit teaching scope in this example",
                        code_data_binding_id=name,
                    )
                    for name, result in checks
                ),
                criteria=(beam.DesignCriterion("cover", 25, "mm", "Teaching fixture"),),
            ),
        )
    )
    require_complete(project_result)
    project = project_result.output_as("project", beam.BeamProject)
    bending = flexure.outputs["checks"][0]
    leaves = (
        beam.MemberLeafEvidence.from_result("geometry@B1", geometry),
        beam.MemberLeafEvidence.from_result(
            "flexure@B1",
            flexure,
            required_value=bending["demand_knm"],
            supplied_value=bending["capacity_knm"],
            unit="kNm",
            governing_utilization=bending["utilization"],
        ),
        beam.MemberLeafEvidence.from_result("seismic@B1", seismic),
    )
    member_request = beam.MemberDesignRequest(
        project=project,
        member_id=member_id,
        topology_revision_id="topology-r1",
        action_revision_id="actions-r1",
        reinforcement_revision_id=detail_revision,
        design_scope_revision_id="scope-r1",
        scope_instances=(),
        depth_iterations=(
            beam.EffectiveDepthIteration(
                iteration_number=1,
                reinforcement_revision_id=detail_revision,
                effective_depth_mm=depth.outputs["effective_depth_mm"],
                dependent_result_ids=(geometry.result_id, flexure.result_id),
                converged=True,
            ),
        ),
        leaf_results=leaves,
    )
    member = beam.design_member(member_request)
    require_complete(member)
    missing_member = beam.design_member(
        replace(member_request, leaf_results=leaves[:1] + leaves[2:])
    )
    stale_member = beam.design_member(
        replace(
            member_request,
            leaf_results=(
                leaves[0],
                replace(leaves[1], freshness=beam.FreshnessState.STALE),
                leaves[2],
            ),
        )
    )

    # Use the same physical coordinates and bar IDs. No area-to-bar inference.
    paths = beam.resolve_bar_paths(
        beam.BarPathRequest(
            profile_id=profile_id,
            project_basis_id=project.project_basis_id,
            criteria_revision_id=project.profile.revision_id,
            member_id=member_id,
            physical_span_id="SPAN-1",
            topology_revision_id="topology-r1",
            detail_revision_id=detail_revision,
            coordinate_system=beam.MemberLocalCoordinateSystem(
                "B1-local",
                "member_station_x",
                "section_x_from_left",
                "section_y_from_top",
            ),
            member_start_x_mm=0,
            member_end_x_mm=6000,
            section_width_mm=300,
            section_depth_mm=500,
            paths=tuple(
                beam.BarPathSeed(
                    bar_id=bar.bar_id,
                    bar_mark=bar.face.value,
                    layer=bar.layer,
                    role=(
                        beam.BarPathRole.BOTTOM_LONGITUDINAL
                        if bar.face is beam.Face.BOTTOM
                        else beam.BarPathRole.TOP_LONGITUDINAL
                    ),
                    diameter_mm=bar.diameter_mm,
                    steel_grade_n_per_mm2=415,
                    nodes=tuple(
                        beam.PathNode(
                            str(station),
                            beam.PathPoint(
                                station, bar.x_from_left_mm, bar.y_from_top_mm
                            ),
                        )
                        for station in (0, 6000)
                    ),
                )
                for bar in bars
            ),
            stock_lengths_mm=(12000,),
        )
    )
    require_complete(paths)
    schedule = paths.output_as("reinforcement_schedule", beam.BarPathOutput)
    schedule_binding = reporting.result_binding(paths, "reinforcement_schedule")
    bbs = construction.create_bbs(
        construction.BbsRequest(
            profile_id=profile_id,
            project_basis_id=project.project_basis_id,
            member_id=member_id,
            detail_revision_id=detail_revision,
            schedule_result_id=schedule_binding.result_id,
            schedule_output_payload_id=schedule_binding.output_payload_id,
            schedule=schedule,
            shape_convention=construction.ShapeConvention("centreline", "shape-r1"),
            stock_policy=construction.CuttingStockPolicy(
                "stock", "stock-r1", (12000,), 3, 500
            ),
            steel_density_kg_per_m3=7850,
        )
    )
    require_complete(bbs)
    bbs_binding = reporting.result_binding(bbs, "bbs")
    bbs_output = bbs.output_as("bbs", construction.BbsOutput)
    quantities = construction.calculate_construction_quantities(
        construction.ConstructionQuantityRequest(
            profile_id=profile_id,
            project_basis_id=project.project_basis_id,
            member_id=member_id,
            detail_revision_id=detail_revision,
            bbs_result_id=bbs_binding.result_id,
            bbs_output_payload_id=bbs_binding.output_payload_id,
            bbs=bbs_output,
            concrete_overlap_policy_id="isolated-prism-no-overlap",
            formwork_measurement_policy_id="soffit-and-two-sides",
            concrete_segments=(
                construction.ConcreteNetSegment(
                    "CONCRETE", member_id, "M25", "B1-volume", 300 * 500, 6000, False
                ),
            ),
            formwork_faces=tuple(
                construction.FormworkContactFace(
                    face_id=name,
                    member_id=member_id,
                    category=category,
                    ownership_id=f"B1-{name}",
                    gross_area_mm2=width * 6000,
                    measurement_state=construction.FormworkMeasurementState.INCLUDED,
                )
                for name, category, width in (
                    ("soffit", construction.FormworkFaceCategory.SOFFIT, 300),
                    ("left", construction.FormworkFaceCategory.SIDE_LEFT, 500),
                    ("right", construction.FormworkFaceCategory.SIDE_RIGHT, 500),
                )
            ),
        )
    )
    require_complete(quantities)
    quantity_output = quantities.output_as(
        "quantities", construction.ConstructionQuantityOutput
    )
    quantity_binding = reporting.result_binding(quantities, "quantities")
    cost = construction.estimate_construction_cost(
        construction.ConstructionCostRequest(
            profile_id=profile_id,
            project_basis_id=project.project_basis_id,
            member_id=member_id,
            detail_revision_id=detail_revision,
            quantity_result_id=quantity_binding.result_id,
            quantity_output_payload_id=quantity_binding.output_payload_id,
            quantities=quantity_output,
            rate_profile=construction.MeasuredRateProfile(
                profile_id="teaching-rates",
                revision_id="r1",
                currency="INR",
                valuation_date="2026-09-27",
                time_zone="Asia/Kolkata",
                geography="Synthetic fixture",
                source="Invented teaching rates, not market prices",
                scope=construction.HumanCostScope(
                    (
                        construction.CostCategory.MATERIAL,
                        construction.CostCategory.FORMWORK,
                    ),
                    (
                        construction.CostCategory.COUPLER,
                        construction.CostCategory.LABOUR,
                        construction.CostCategory.PLANT,
                    ),
                ),
                rates=tuple(
                    construction.CostRate(
                        name, category, basis, name, rate, "Synthetic teaching input"
                    )
                    for name, category, basis, rate in (
                        (
                            "steel",
                            construction.CostCategory.MATERIAL,
                            construction.CostBasis.STEEL_SCHEDULED_MASS_KG,
                            "50",
                        ),
                        (
                            "concrete",
                            construction.CostCategory.MATERIAL,
                            construction.CostBasis.CONCRETE_VOLUME_M3,
                            "6000",
                        ),
                        (
                            "formwork",
                            construction.CostCategory.FORMWORK,
                            construction.CostBasis.FORMWORK_AREA_M2,
                            "400",
                        ),
                    )
                ),
                waste_pricing_basis=construction.WastePricingBasis.SCHEDULED_STEEL,
                overhead_percent_decimal="0",
                tax_percent_decimal="0",
            ),
        )
    )
    require_complete(cost)
    cost_output = cost.output_as("cost", construction.ConstructionCostOutput)

    def package_for(member_result: beam.OperationResult) -> beam.OperationResult:
        member_output = member_result.output_as(
            "member_design", beam.MemberDesignOutput
        )
        traces = tuple(
            reporting.CalculationTrace(
                trace_id=f"trace-{item.expectation.leaf_id}",
                leaf_id=item.expectation.leaf_id,
                rule_reference="; ".join(checks[index][1].provenance.source_references),
                formula_reference=checks[index][1].provenance.method_revision_id,
                normalized_substitution=json.dumps(
                    checks[index][1].effective_inputs, sort_keys=True
                ),
                required_value=item.evidence.required_value if item.evidence else None,
                provided_value=item.evidence.supplied_value if item.evidence else None,
                selected_value=item.evidence.selected_value if item.evidence else None,
                unit=item.evidence.unit if item.evidence else None,
                utilization=(
                    item.evidence.governing_utilization if item.evidence else None
                ),
                governing=member_output.governing_leaf_id == item.expectation.leaf_id,
            )
            for index, item in enumerate(member_output.leaf_qualifications)
        )
        return reporting.create_calculation_package(
            reporting.CalculationPackageRequest(
                metadata=reporting.CalculationPackageMetadata(
                    "TEACHING",
                    "Physical beam API example",
                    "r1",
                    member_id,
                    "package-r1",
                    "python-structural-engineering-v1",
                    tuple(
                        binding.revision_id for binding in project.code_data_revisions
                    ),
                    "2026-09-27T00:00:00+00:00",
                ),
                package_profile=reporting.CalculationPackageProfile(
                    "teaching-package",
                    "r1",
                    "semantic-example",
                    tuple(item.leaf_id for item in member_output.expected_leaves),
                    (
                        "inputs",
                        "calculations",
                        "reinforcement",
                        "quantities",
                        "cost",
                        "drawings",
                        "signatures",
                    ),
                ),
                member_result=member_output,
                member_binding=reporting.result_binding(member_result, "member_design"),
                schedule=schedule,
                schedule_binding=schedule_binding,
                bbs=bbs_output,
                bbs_binding=bbs_binding,
                quantities=quantity_output,
                quantity_binding=quantity_binding,
                cost=cost_output,
                cost_binding=reporting.result_binding(cost, "cost"),
                assumptions=(
                    "Four supplied straight bars and a 300 x 500 x 6000 mm isolated prism.",
                ),
                traces=traces,
                drawings=(
                    reporting.DrawingView(
                        "schedule",
                        "bar_schedule",
                        detail_revision,
                        (
                            reporting.DrawingDatum(
                                "bar-count",
                                paths.result_id,
                                "Longitudinal bars",
                                str(len(bars)),
                            ),
                        ),
                    ),
                ),
                limitations=(
                    "Teaching scope only: geometry, flexure, ordinary seismic applicability.",
                    "No shear, serviceability, anchorage or complete building-design acceptance.",
                    "No file rendering, human review, or construction approval.",
                ),
                human_actions=(),
            )
        )

    package = package_for(member)
    require_complete(package)
    draft_package = package_for(stale_member)
    return Workflow(
        project_result,
        member,
        missing_member,
        stale_member,
        paths,
        bbs,
        quantities,
        cost,
        package,
        draft_package,
    )


def main() -> None:
    workflow = build_workflow()
    quantity = workflow.quantities.output_as(
        "quantities", construction.ConstructionQuantityOutput
    )
    package = workflow.package.output_as(
        "calculation_package", reporting.CalculationPackageOutput
    )
    draft = workflow.draft_package.output_as(
        "calculation_package", reporting.CalculationPackageOutput
    )
    assert math.isclose(quantity.steel_scheduled_mass_kg, 59.18760559, abs_tol=1e-8)
    assert math.isclose(quantity.concrete_volume_m3, 0.9)
    assert math.isclose(quantity.formwork_area_m2, 7.8)
    assert workflow.missing_member.completeness is beam.CompletenessState.PARTIAL
    assert any(
        item.code == "LEAF.MISSING" for item in workflow.missing_member.diagnostics
    )
    assert workflow.stale_member.freshness is beam.FreshnessState.STALE
    assert package.issue_state == "issue_ready" and not package.active_approval
    assert draft.issue_state == "draft" and not draft.active_approval
    print(
        json.dumps(
            {
                "scope": "teaching profile only; not complete building design",
                "member": workflow.member.engineering,
                "missing_member": workflow.missing_member.completeness,
                "stale_member": workflow.stale_member.freshness,
                "steel_kg": round(quantity.steel_scheduled_mass_kg, 6),
                "concrete_m3": quantity.concrete_volume_m3,
                "formwork_m2": quantity.formwork_area_m2,
                "package": package.issue_state,
                "stale_package": draft.issue_state,
                "human_approval": package.active_approval,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
