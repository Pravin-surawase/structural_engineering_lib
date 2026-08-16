"""Public-contract proof for the bounded symmetric combined-footing workflow."""

from __future__ import annotations

import dataclasses
import json
from dataclasses import FrozenInstanceError

import pytest

import structural_lib
import structural_lib.services as services
from structural_lib import api as compatibility_api
from structural_lib.codes.is456.combined_footing import (
    CombinedFootingActionInput,
    CombinedFootingAnalysisMethod,
    CombinedFootingContractError,
    CombinedFootingDesignDisposition,
    CombinedFootingDesignInput,
    CombinedFootingGeometryInput,
    CombinedFootingInput,
    CombinedFootingMaterialInput,
    CombinedFootingPressureModel,
    CombinedFootingReinforcementInput,
    CombinedFootingSupportingAreaBasis,
    CombinedFootingTransferInput,
)
from structural_lib.services import api as services_api


def _geometry() -> CombinedFootingGeometryInput:
    return CombinedFootingGeometryInput(
        footing_length_mm=6000.0,
        footing_width_mm=2500.0,
        overall_depth_mm=850.0,
        effective_depth_mm=750.0,
        column_side_mm=500.0,
        left_column_center_x_mm=1000.0,
        right_column_center_x_mm=5000.0,
        column_count=2,
        columns_identical=True,
        columns_square=True,
        columns_centered_across_width=True,
        foundation_on_soil=True,
        constant_depth=True,
        openings_present=False,
        pedestals_present=False,
        analysis_method=CombinedFootingAnalysisMethod.CONVENTIONAL_RIGID,
        pressure_model=CombinedFootingPressureModel.UNIFORM,
        rigid_footing_verified=True,
        rigidity_basis_reference="INDIA-2-COMBINED-HAND-01-RIGIDITY",
        geometry_basis_reference="INDIA-2-COMBINED-HAND-01-GEOMETRY",
    )


def _actions(
    **overrides: object,
) -> CombinedFootingActionInput:
    values: dict[str, object] = {
        "service_axial_load_each_kn": 900.0,
        "factored_axial_load_each_kn": 1350.0,
        "service_uniform_carrier_kn_per_m2": 25.0,
        "factored_uniform_carrier_kn_per_m2": 37.5,
        "allowable_gross_bearing_pressure_kn_per_m2": 150.0,
        "load_combination_approved": True,
        "bearing_and_settlement_approved": True,
        "pressure_uniformity_approved": True,
        "distributed_carrier_cancellation_approved": True,
        "column_moments_present": False,
        "horizontal_actions_present": False,
        "uplift_or_load_reversal_present": False,
        "load_basis_reference": "INDIA-2-COMBINED-HAND-01-LOAD",
        "bearing_settlement_basis_reference": ("INDIA-2-COMBINED-HAND-01-BEARING"),
        "cancellation_basis_reference": "INDIA-2-COMBINED-HAND-01-CANCELLATION",
    }
    values.update(overrides)
    return CombinedFootingActionInput(**values)  # type: ignore[arg-type]


def _reinforcement() -> CombinedFootingReinforcementInput:
    return CombinedFootingReinforcementInput(
        top_longitudinal_diameter_mm=16.0,
        top_longitudinal_spacing_mm=190.0,
        bottom_longitudinal_diameter_mm=16.0,
        bottom_longitudinal_spacing_mm=190.0,
        transverse_diameter_mm=12.0,
        transverse_spacing_mm=110.0,
        nominal_cover_mm=50.0,
        aggregate_size_mm=20.0,
        available_top_longitudinal_anchorage_each_end_mm=800.0,
        available_bottom_longitudinal_anchorage_each_end_mm=800.0,
        available_transverse_anchorage_each_edge_mm=800.0,
        straight_uncoated_deformed_bars=True,
        effective_depth_basis_approved=True,
        reinforcement_schedule_approved=True,
        detailing_basis_reference="INDIA-2-COMBINED-HAND-01-DETAILING",
    )


def _design_input(
    *,
    actions: CombinedFootingActionInput | None = None,
) -> CombinedFootingDesignInput:
    return CombinedFootingDesignInput(
        analysis=CombinedFootingInput(_geometry(), actions or _actions()),
        material=CombinedFootingMaterialInput(
            footing_concrete_grade_nmm2=30.0,
            column_concrete_grade_nmm2=30.0,
            steel_grade_nmm2=500.0,
            uncoated_deformed_bars=True,
            material_basis_reference="INDIA-2-COMBINED-HAND-01-MATERIAL",
        ),
        reinforcement=_reinforcement(),
        transfer=CombinedFootingTransferInput(
            effective_supporting_area_each_mm2=250000.0,
            effective_supporting_area_basis=(
                CombinedFootingSupportingAreaBasis.LARGEST_FRUSTUM_1V_2H
            ),
            effective_supporting_area_approved=True,
            dowel_count_each=4,
            dowel_diameter_mm=20.0,
            column_longitudinal_bar_diameter_mm=20.0,
            available_dowel_development_into_footing_mm=800.0,
            available_dowel_development_into_column_mm=800.0,
            uncoated_deformed_dowels=True,
            transfer_basis_reference="INDIA-2-COMBINED-HAND-01-TRANSFER",
        ),
    )


def _request(
    *,
    footing: CombinedFootingDesignInput | None = None,
    case_id: str = "INDIA-2-COMBINED-HAND-01",
    qualified_review_required: bool = True,
) -> services_api.SymmetricCombinedFootingDesignInput:
    return services_api.SymmetricCombinedFootingDesignInput(
        case_id=case_id,
        footing=footing or _design_input(),
        qualified_review_required=qualified_review_required,
    )


def test_combined_footing_has_one_canonical_public_function_and_types() -> None:
    assert (
        structural_lib.design_symmetric_combined_footing_is456
        is services_api.design_symmetric_combined_footing_is456
        is services.design_symmetric_combined_footing_is456
        is compatibility_api.design_symmetric_combined_footing_is456
    )
    for name in (
        "design_symmetric_combined_footing_is456",
        "SymmetricCombinedFootingDesignInput",
        "SymmetricCombinedFootingDesignProvenance",
        "SymmetricCombinedFootingDesignResult",
        "SymmetricCombinedFootingDesignStatus",
    ):
        assert name in services.__all__
        assert name in services_api.__all__
        assert name in compatibility_api.__all__
        assert name in structural_lib.__all__


def test_public_composition_matches_frozen_benchmark_and_is_serializable() -> None:
    result = structural_lib.design_symmetric_combined_footing_is456(_request())

    assert result.status is services_api.SymmetricCombinedFootingDesignStatus.PASS
    assert result.strength.disposition is CombinedFootingDesignDisposition.PASS
    assert result.strength.actions.gross_service_pressure_kn_per_m2 == pytest.approx(
        145.0
    )
    assert result.strength.actions.net_factored_structural_pressure_kn_per_m2 == (
        pytest.approx(180.0)
    )
    assert result.strength.top_longitudinal_flexure.factored_moment_kn_m == (
        pytest.approx(675.0)
    )
    assert result.strength.top_longitudinal_flexure.provided_steel_area_mm2 == (
        pytest.approx(2645.551708286142)
    )
    assert result.strength.punching[0].utilization == pytest.approx(0.208134572057151)
    assert result.strength.load_transfer[0].provided_transfer_steel_area_mm2 == (
        pytest.approx(1256.6370614359173)
    )
    assert result.is_safe_within_supported_scope is True
    assert result.qualified_review_required is True
    assert result.complete_engineering_design_approved is False
    json.dumps(dataclasses.asdict(result))


def test_public_workflow_preserves_all_caller_basis_and_source_boundaries() -> None:
    result = structural_lib.design_symmetric_combined_footing_is456(_request())
    provenance = result.provenance

    assert provenance.schema_version == "1.0"
    assert provenance.code_edition == "IS 456:2000 through Amendment 6"
    assert provenance.workflow == "design_symmetric_combined_footing_is456"
    assert provenance.case_id == "INDIA-2-COMBINED-HAND-01"
    assert provenance.benchmark_id == "INDIA-2-COMBINED-HAND-01"
    assert provenance.geometry_basis_reference.endswith("-GEOMETRY")
    assert provenance.rigidity_basis_reference.endswith("-RIGIDITY")
    assert provenance.load_basis_reference.endswith("-LOAD")
    assert provenance.bearing_settlement_basis_reference.endswith("-BEARING")
    assert provenance.cancellation_basis_reference.endswith("-CANCELLATION")
    assert provenance.material_basis_reference.endswith("-MATERIAL")
    assert provenance.detailing_basis_reference.endswith("-DETAILING")
    assert provenance.transfer_basis_reference.endswith("-TRANSFER")
    assert provenance.clause_refs == result.strength.clause_refs
    assert "IS456-PUBLIC-DISTRIBUTION-001" in provenance.source_refs
    assert any(
        item.startswith("IS456-2000-A5:sha256:") for item in provenance.source_refs
    )
    assert any(
        item.startswith("IS456-AMD6-2024:sha256:") for item in provenance.source_refs
    )
    assert "two identical square columns" in result.supported_case
    assert any("soil-structure-interaction" in item for item in result.held_cases)
    assert any("Strap footings" in item for item in result.held_cases)
    assert any("professional approval" in item for item in result.held_cases)


def test_valid_inadequacy_returns_public_fail_result() -> None:
    failing_footing = _design_input(
        actions=_actions(allowable_gross_bearing_pressure_kn_per_m2=140.0)
    )
    result = structural_lib.design_symmetric_combined_footing_is456(
        _request(footing=failing_footing)
    )

    assert result.status is services_api.SymmetricCombinedFootingDesignStatus.FAIL
    assert result.strength.disposition is CombinedFootingDesignDisposition.FAIL
    assert result.strength.actions.gross_service_bearing_within_allowable is False
    assert result.is_safe_within_supported_scope is False


def test_invalid_public_contract_fails_closed() -> None:
    with pytest.raises(CombinedFootingContractError, match="DesignInput"):
        services_api.design_symmetric_combined_footing_is456(object())  # type: ignore[arg-type]
    with pytest.raises(CombinedFootingContractError, match="case_id"):
        services_api.design_symmetric_combined_footing_is456(_request(case_id=" "))
    with pytest.raises(CombinedFootingContractError, match="footing"):
        services_api.design_symmetric_combined_footing_is456(
            services_api.SymmetricCombinedFootingDesignInput(
                case_id="BAD-NESTED-TYPE",
                footing=object(),  # type: ignore[arg-type]
                qualified_review_required=True,
            )
        )
    with pytest.raises(CombinedFootingContractError, match="qualified_review"):
        services_api.design_symmetric_combined_footing_is456(
            _request(qualified_review_required=False)
        )


def test_public_result_is_frozen_and_deterministic() -> None:
    first = structural_lib.design_symmetric_combined_footing_is456(_request())
    second = structural_lib.design_symmetric_combined_footing_is456(_request())

    assert first == second
    with pytest.raises(FrozenInstanceError):
        first.status = services_api.SymmetricCombinedFootingDesignStatus.FAIL  # type: ignore[misc]


def test_capability_and_semantic_truth_remain_held_until_combined_d() -> None:
    assert all(
        item.element != "combined_footing"
        for item in services_api.get_supported_is456_capabilities()
    )
    assert all(
        item.workflow != "design_symmetric_combined_footing_is456"
        for item in services_api.get_supported_is456_semantic_contract().workflows
    )
