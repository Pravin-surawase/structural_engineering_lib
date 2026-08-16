"""Public-contract proof for the composed regular interior flat-slab workflow."""

from __future__ import annotations

import dataclasses
import json
from dataclasses import replace

import pytest

import structural_lib
from structural_lib.codes.is456.flat_slab import (
    FlatSlabAnalysisMethod,
    FlatSlabContractError,
    FlatSlabDirectionDetailingInput,
    FlatSlabGravityLoad,
    FlatSlabGridGeometry,
    FlatSlabMaterial,
    FlatSlabPanelInput,
    FlatSlabPanelLocation,
    FlatSlabPunchingStatus,
)
from structural_lib.codes.is456.slab.detailing import ProvidedSlabBars
from structural_lib.services import api as services_api


def _panel(
    *,
    dead_load: float = 9.0,
    live_load: float = 4.0,
    factored_load: float = 19.5,
) -> FlatSlabPanelInput:
    return FlatSlabPanelInput(
        geometry=FlatSlabGridGeometry(
            centre_to_centre_span_x_mm=6000.0,
            centre_to_centre_span_y_mm=6000.0,
            continuous_span_count_x=3,
            continuous_span_count_y=3,
            column_width_x_mm=500.0,
            column_width_y_mm=500.0,
            overall_depth_mm=300.0,
            conservative_effective_depth_mm=260.0,
            analysis_method=FlatSlabAnalysisMethod.DIRECT_DESIGN,
            panel_location=FlatSlabPanelLocation.INTERIOR,
            all_spans_equal_x=True,
            all_spans_equal_y=True,
            columns_offset_from_grid=False,
            solid_slab=True,
            drop_present=False,
            column_head_present=False,
            marginal_beam_or_wall_present=False,
            openings_present=False,
            geometry_basis_reference="INDIA-2-FLAT-HAND-01-GEOMETRY",
        ),
        material=FlatSlabMaterial(
            concrete_grade_nmm2=30.0,
            steel_grade_nmm2=500.0,
            uncoated_deformed_bars=True,
            material_basis_reference="INDIA-2-FLAT-HAND-01-MATERIAL",
        ),
        gravity_load=FlatSlabGravityLoad(
            service_dead_load_kn_per_m2=dead_load,
            service_live_load_kn_per_m2=live_load,
            factored_uniform_load_kn_per_m2=factored_load,
            self_weight_included=True,
            identical_full_loading_on_represented_panels=True,
            patterned_loading_required=False,
            unbalanced_or_lateral_moment_transfer_present=False,
            load_combination_approved=True,
            load_basis_reference="INDIA-2-FLAT-HAND-01-LOAD",
        ),
    )


def _direction() -> FlatSlabDirectionDetailingInput:
    return FlatSlabDirectionDetailingInput(
        column_strip_negative_bars=ProvidedSlabBars(12.0, 160.0),
        column_strip_positive_bars=ProvidedSlabBars(10.0, 200.0),
        middle_strip_negative_bars=ProvidedSlabBars(10.0, 200.0),
        middle_strip_positive_bars=ProvidedSlabBars(10.0, 200.0),
        support_top_extension_from_face_mm=1650.0,
    )


def _request(
    *,
    panel: FlatSlabPanelInput | None = None,
    **overrides: object,
) -> services_api.RegularInteriorFlatSlabDesignInput:
    selected_panel = panel or _panel()
    values: dict[str, object] = {
        "case_id": "INDIA-2-FLAT-HAND-01",
        "panel": selected_panel,
        "x": _direction(),
        "y": _direction(),
        "factored_support_reaction_kn": (
            selected_panel.gravity_load.factored_uniform_load_kn_per_m2 * 36.0
        ),
        "straight_bars_only": True,
        "all_bottom_bars_continuous": True,
        "splices_present": False,
        "serviceability_acceptance_acknowledged": True,
        "centred_concentric_reaction": True,
        "full_critical_perimeter_available": True,
        "no_punching_reinforcement_provided": True,
        "qualified_review_required": True,
        "detailing_basis_reference": "INDIA-2-FLAT-HAND-01-DETAILING",
        "serviceability_acceptance_reference": ("INDIA-2-FLAT-G0-REVIEWED-SPAN-DEPTH"),
        "support_reaction_basis_reference": "INDIA-2-FLAT-HAND-01-REACTION",
        "punching_basis_reference": "INDIA-2-FLAT-HAND-01-PUNCHING",
    }
    values.update(overrides)
    return services_api.RegularInteriorFlatSlabDesignInput(**values)  # type: ignore[arg-type]


def test_flat_slab_has_one_canonical_public_function_and_types() -> None:
    assert (
        structural_lib.design_regular_interior_flat_slab_is456
        is services_api.design_regular_interior_flat_slab_is456
    )
    for name in (
        "design_regular_interior_flat_slab_is456",
        "RegularInteriorFlatSlabDesignInput",
        "RegularInteriorFlatSlabDesignProvenance",
        "RegularInteriorFlatSlabDesignResult",
        "RegularInteriorFlatSlabDesignStatus",
    ):
        assert name in services_api.__all__
        assert name in structural_lib.__all__


def test_public_composition_matches_frozen_benchmark_and_is_serializable() -> None:
    result = structural_lib.design_regular_interior_flat_slab_is456(_request())

    assert result.status is services_api.RegularInteriorFlatSlabDesignStatus.PASS
    assert result.reinforcement.moments.x.total_static_moment_knm == pytest.approx(
        442.40625
    )
    assert result.reinforcement.x.column_strip_negative.ast_required_total_mm2 == (
        pytest.approx(1993.0759957303314)
    )
    assert result.reinforcement.x_serviceability.utilization == pytest.approx(
        0.9861932938856016
    )
    assert result.punching.punching_shear_force_kn == pytest.approx(690.7368)
    assert result.punching.no_reinforcement_utilization == pytest.approx(
        0.6382120901359107
    )
    assert result.punching.status is (
        FlatSlabPunchingStatus.SAFE_WITHOUT_PUNCHING_REINFORCEMENT
    )
    assert result.qualified_review_required is True
    assert result.complete_engineering_design_approved is False
    json.dumps(dataclasses.asdict(result))


def test_public_workflow_preserves_provenance_and_held_boundaries() -> None:
    result = structural_lib.design_regular_interior_flat_slab_is456(_request())

    assert result.provenance.workflow == "design_regular_interior_flat_slab_is456"
    assert result.provenance.benchmark_id == "INDIA-2-FLAT-HAND-01"
    assert result.provenance.action_generation_status.startswith("not_generated")
    assert result.provenance.support_reaction_status.startswith("caller_supplied")
    assert "31.4.2.2" in result.provenance.clause_refs
    assert "31.6.3.2" in result.provenance.clause_refs
    assert "Figure 16" in result.provenance.clause_refs
    assert "IS456-2000-A6" in result.provenance.source_refs
    assert "IS456-PUBLIC-DISTRIBUTION-001" in result.provenance.source_refs
    assert "square interior" in result.supported_case
    assert any("Equivalent-frame" in item for item in result.held_cases)
    assert any("Punching reinforcement" in item for item in result.held_cases)
    assert any("professional" in item for item in result.held_cases)


def test_valid_inadequacy_returns_composed_fail() -> None:
    direction = _direction()
    inadequate_direction = replace(
        direction,
        column_strip_negative_bars=ProvidedSlabBars(12.0, 200.0),
    )
    reinforcement_fail = structural_lib.design_regular_interior_flat_slab_is456(
        _request(x=inadequate_direction)
    )
    high_load_panel = _panel(
        dead_load=16.0,
        live_load=5.0,
        factored_load=31.5,
    )
    punching_fail = structural_lib.design_regular_interior_flat_slab_is456(
        _request(panel=high_load_panel)
    )

    assert reinforcement_fail.status is (
        services_api.RegularInteriorFlatSlabDesignStatus.FAIL
    )
    assert punching_fail.punching.status is (
        FlatSlabPunchingStatus.PUNCHING_REINFORCEMENT_OR_REDESIGN_REQUIRED
    )
    assert punching_fail.status is services_api.RegularInteriorFlatSlabDesignStatus.FAIL


def test_invalid_public_contract_fails_closed() -> None:
    with pytest.raises(FlatSlabContractError, match="DesignInput"):
        services_api.design_regular_interior_flat_slab_is456(object())  # type: ignore[arg-type]
    with pytest.raises(FlatSlabContractError, match="case_id"):
        services_api.design_regular_interior_flat_slab_is456(_request(case_id=" "))
    with pytest.raises(FlatSlabContractError, match="straight_bars_only"):
        services_api.design_regular_interior_flat_slab_is456(
            _request(straight_bars_only=False)
        )
    with pytest.raises(FlatSlabContractError, match="uniform tributary reaction"):
        services_api.design_regular_interior_flat_slab_is456(
            _request(factored_support_reaction_kn=701.0)
        )
    with pytest.raises(FlatSlabContractError, match="qualified_review_required"):
        services_api.design_regular_interior_flat_slab_is456(
            _request(qualified_review_required=False)
        )


def test_flat_slab_capability_and_semantic_contract_are_exact() -> None:
    capability = next(
        item
        for item in services_api.get_supported_is456_capabilities()
        if item.element == "flat_slab"
    )
    assert capability.public_workflows == ("design_regular_interior_flat_slab_is456",)
    assert "square interior" in capability.supported_case
    assert any("Equivalent-frame" in item for item in capability.held_cases)
    assert any("Punching reinforcement" in item for item in capability.held_cases)
    assert capability.qualified_review_required is True

    contract = services_api.get_supported_is456_semantic_contract()
    workflow = next(
        item
        for item in contract.workflows
        if item.workflow == "design_regular_interior_flat_slab_is456"
    )
    field_names = {field.canonical_name for field in workflow.fields}
    assert {
        "request.panel.geometry",
        "request.panel.gravity_load.factored_uniform_load_kn_per_m2",
        "request.factored_support_reaction_kn",
        "reinforcement.moments",
        "reinforcement.x",
        "reinforcement.y",
        "punching.status",
        "complete_engineering_design_approved",
    }.issubset(field_names)
    assert workflow.statuses[0].canonical_name == "status"
    assert any("professional" in item for item in workflow.statuses[0].limitations)
