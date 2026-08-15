"""Public-contract proof for the composed simply supported deep-beam workflow."""

from __future__ import annotations

import dataclasses
import json

import pytest

import structural_lib
from structural_lib.codes.is456.deep_beam import (
    DeepBeamCheckStatus,
    DeepBeamContractError,
)
from structural_lib.services import api as services_api


def _benchmark_request(
    **overrides: object,
) -> services_api.SimplySupportedDeepBeamDesignInput:
    values: dict[str, object] = {
        "case_id": "INDIA-2-DEEP-HAND-01",
        "centre_to_centre_span_mm": 3000.0,
        "clear_span_mm": 2800.0,
        "overall_depth_mm": 2000.0,
        "beam_width_mm": 300.0,
        "concrete_grade_nmm2": 30.0,
        "steel_grade_nmm2": 500.0,
        "factored_positive_moment_knm": 900.0,
        "main_bar_count": 4,
        "main_bar_diameter_mm": 22.0,
        "furthest_main_bar_from_tension_face_mm": 250.0,
        "main_bars_continuous_between_supports": True,
        "main_bars_bundled": False,
        "main_bar_splices_present": False,
        "left_support_embedment_mm": 850.0,
        "right_support_embedment_mm": 850.0,
        "face_grid_count": 2,
        "vertical_side_bar_diameter_mm": 10.0,
        "vertical_side_bar_spacing_mm": 300.0,
        "horizontal_side_bar_diameter_mm": 10.0,
        "horizontal_side_bar_spacing_mm": 250.0,
        "geometry_basis_reference": "INDIA-2-DEEP-HAND-01-GEOMETRY",
        "bearing_nodal_zone_reference": "INDIA-2-DEEP-HAND-01-BEARING",
        "action_basis_reference": "INDIA-2-DEEP-HAND-01-ACTIONS",
        "reinforcement_basis_reference": "INDIA-2-DEEP-HAND-01-REINFORCEMENT",
        "support_type": "simply_supported",
        "solid_rectangular_section": True,
        "openings_present": False,
        "dapped_ends_present": False,
        "top_loaded": True,
        "hanging_action_required": False,
        "bearing_nodal_zone_verified": True,
    }
    values.update(overrides)
    return services_api.SimplySupportedDeepBeamDesignInput(**values)  # type: ignore[arg-type]


def test_deep_beam_has_one_canonical_public_function_and_types() -> None:
    assert (
        structural_lib.design_simply_supported_deep_beam_is456
        is services_api.design_simply_supported_deep_beam_is456
    )
    for name in (
        "design_simply_supported_deep_beam_is456",
        "SimplySupportedDeepBeamDesignInput",
        "SimplySupportedDeepBeamDesignProvenance",
        "SimplySupportedDeepBeamDesignResult",
    ):
        assert name in services_api.__all__
        assert name in structural_lib.__all__


def test_public_composition_matches_frozen_benchmark_and_is_serializable() -> None:
    result = structural_lib.design_simply_supported_deep_beam_is456(
        _benchmark_request()
    )

    assert result.status is DeepBeamCheckStatus.PASS
    assert result.reinforcement.geometry.effective_span_mm == pytest.approx(3000.0)
    assert result.reinforcement.geometry.lever_arm_mm == pytest.approx(1400.0)
    assert result.reinforcement.positive_tie.required_area_mm2 == pytest.approx(
        1477.832512315271, abs=1e-6
    )
    assert result.reinforcement.positive_tie.provided_area_mm2 == pytest.approx(
        1520.53084433746, abs=1e-6
    )
    assert result.reinforcement.anchorage.required_embedment_mm == pytest.approx(797.5)
    assert result.reinforcement.vertical_side_face.provided_area_mm2_per_m == (
        pytest.approx(523.598775598299, abs=1e-6)
    )
    assert result.reinforcement.horizontal_side_face.provided_area_mm2_per_m == (
        pytest.approx(628.318530717959, abs=1e-6)
    )
    assert result.shear_deemed_satisfied_within_clause_29_scope is True
    assert result.qualified_review_required is True
    assert result.complete_engineering_design_approved is False
    json.dumps(dataclasses.asdict(result))


def test_public_workflow_preserves_all_provenance_and_boundaries() -> None:
    result = structural_lib.design_simply_supported_deep_beam_is456(
        _benchmark_request()
    )

    assert result.provenance.workflow == "design_simply_supported_deep_beam_is456"
    assert result.provenance.benchmark_id == "INDIA-2-DEEP-HAND-01"
    assert result.provenance.action_generation_status.startswith("not_generated")
    assert result.provenance.bearing_nodal_zone_status.endswith("not_calculated")
    assert result.provenance.clause_refs == (
        "29",
        "29.1",
        "29.2",
        "29.3",
        "29.3.1",
        "29.3.4",
        "26.2.1",
        "26.2.1.1",
        "32.5",
        "32.5.1",
        "32.5.2",
    )
    assert "IS456-2000-A6" in result.provenance.source_refs
    assert "IS456-AMD3-DEEP-SIDEFACE" in result.provenance.source_refs
    assert "IS456-PUBLIC-DISTRIBUTION-001" in result.provenance.source_refs
    assert "NPTEL-RCD-DEEP-W7" in result.provenance.source_refs
    assert "simply supported" in result.supported_case
    assert any("bearing" in item for item in result.held_cases)
    assert any("strut-and-tie" in item for item in result.held_cases)
    assert any("IS 13920" in item for item in result.held_cases)


def test_valid_inadequate_inputs_return_composed_fail() -> None:
    tie_fail = structural_lib.design_simply_supported_deep_beam_is456(
        _benchmark_request(main_bar_count=3)
    )
    anchorage_fail = structural_lib.design_simply_supported_deep_beam_is456(
        _benchmark_request(left_support_embedment_mm=700.0)
    )

    assert tie_fail.reinforcement.positive_tie.status is DeepBeamCheckStatus.FAIL
    assert tie_fail.status is DeepBeamCheckStatus.FAIL
    assert tie_fail.shear_deemed_satisfied_within_clause_29_scope is False
    assert anchorage_fail.reinforcement.anchorage.status is DeepBeamCheckStatus.FAIL
    assert anchorage_fail.status is DeepBeamCheckStatus.FAIL


def test_invalid_public_contract_fails_closed() -> None:
    with pytest.raises(DeepBeamContractError, match="DesignInput"):
        services_api.design_simply_supported_deep_beam_is456(object())  # type: ignore[arg-type]
    with pytest.raises(DeepBeamContractError, match="case_id"):
        services_api.design_simply_supported_deep_beam_is456(
            _benchmark_request(case_id=" ")
        )
    with pytest.raises(DeepBeamContractError, match="support_type"):
        services_api.design_simply_supported_deep_beam_is456(
            _benchmark_request(support_type="continuous")
        )
    with pytest.raises(DeepBeamContractError, match="openings_present"):
        services_api.design_simply_supported_deep_beam_is456(
            _benchmark_request(openings_present=True)
        )
    with pytest.raises(DeepBeamContractError, match="bearing_nodal_zone_verified"):
        services_api.design_simply_supported_deep_beam_is456(
            _benchmark_request(bearing_nodal_zone_verified=False)
        )


def test_deep_beam_capability_and_semantic_contract_are_exact() -> None:
    capability = next(
        item
        for item in services_api.get_supported_is456_capabilities()
        if item.element == "deep_beam"
    )
    assert capability.public_workflows == ("design_simply_supported_deep_beam_is456",)
    assert "simply supported" in capability.supported_case
    assert any("bearing" in item for item in capability.held_cases)
    assert any("strut-and-tie" in item for item in capability.held_cases)
    assert capability.qualified_review_required is True

    contract = services_api.get_supported_is456_semantic_contract()
    workflow = next(
        item
        for item in contract.workflows
        if item.workflow == "design_simply_supported_deep_beam_is456"
    )
    field_names = {field.canonical_name for field in workflow.fields}
    assert {
        "request.factored_positive_moment_knm",
        "request.bearing_nodal_zone_verified",
        "reinforcement.geometry",
        "reinforcement.positive_tie",
        "reinforcement.anchorage",
        "reinforcement.status",
        "complete_engineering_design_approved",
    }.issubset(field_names)
    assert workflow.statuses[0].canonical_name == "status"
    assert any("professional" in item for item in workflow.statuses[0].limitations)
