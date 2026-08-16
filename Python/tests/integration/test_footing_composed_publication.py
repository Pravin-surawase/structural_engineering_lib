# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Public-contract proof for the composed concentric isolated-footing route."""

from __future__ import annotations

import dataclasses
import json

import pytest

import structural_lib
from structural_lib.core.data_types import FootingType
from structural_lib.services import api as services_api


def _benchmark_request() -> services_api.ConcentricIsolatedFootingInput:
    return services_api.ConcentricIsolatedFootingInput(
        case_id="FOOT-INDIA-1C-SQ-001",
        service_axial_load_kN=800.0,
        service_load_combination_id="SLS-GRAVITY-01",
        service_load_basis="includes_footing_self_weight_and_overburden",
        service_load_origin="provided",
        factored_axial_load_kN=1_200.0,
        factored_load_combination_id="ULS-GRAVITY-01",
        allowable_soil_pressure_kPa=200.0,
        allowable_soil_pressure_source_reference="GEO-REPORT-001",
        allowable_soil_pressure_origin="verified",
        allowable_soil_pressure_is_externally_approved=True,
        footing_type=FootingType.ISOLATED_SQUARE,
        column_L_mm=400.0,
        column_B_mm=400.0,
        minimum_overall_thickness_mm=500.0,
        maximum_overall_thickness_mm=500.0,
        thickness_increment_mm=50.0,
        effective_depth_offset_L_mm=100.0,
        effective_depth_offset_B_mm=100.0,
        footing_concrete_fck_nmm2=25.0,
        column_concrete_fck_nmm2=25.0,
        steel_fy_nmm2=415.0,
        effective_supporting_area_A1_mm2=640_000.0,
        effective_supporting_area_basis="largest_frustum_1v_2h",
        effective_supporting_area_origin="provided",
        effective_supporting_area_is_approved=True,
        dowel_count=4,
        dowel_diameter_mm=20.0,
        column_longitudinal_bar_diameter_mm=20.0,
        available_dowel_development_length_into_footing_mm=1_000.0,
        available_dowel_development_length_into_column_mm=1_000.0,
        nominal_cover_mm=50.0,
        cover_exposure_basis="approved severe footing schedule",
        cover_exposure_basis_is_approved=True,
        nominal_max_aggregate_size_mm=20.0,
        lower_bottom_bar_direction="L",
        upper_bottom_bar_direction="B",
        permitted_bottom_bar_diameters_mm=(12, 16, 20, 25, 32),
        footing_bottom_bar_type="deformed",
    )


def test_composed_footing_has_one_canonical_public_function_and_types() -> None:
    assert (
        structural_lib.design_concentric_isolated_footing_is456
        is services_api.design_concentric_isolated_footing_is456
    )
    for name in (
        "design_concentric_isolated_footing_is456",
        "ConcentricIsolatedFootingInput",
        "ConcentricIsolatedFootingResult",
        "FootingDepthCandidate",
        "FootingDirectionalReinforcementDemand",
        "FootingProvenance",
    ):
        assert name in services_api.__all__
        assert name in structural_lib.__all__


def test_public_composition_matches_accepted_square_benchmark() -> None:
    result = structural_lib.design_concentric_isolated_footing_is456(
        _benchmark_request()
    )

    assert (
        result.status == result.calculation_status == result.detailing_status == "PASS"
    )
    assert result.bearing.L_mm == result.bearing.B_mm == 2_000.0
    assert result.selected_overall_thickness_mm == 500.0
    assert result.flexure is not None
    assert result.flexure.Mu_L_kNm == result.flexure.Mu_B_kNm == pytest.approx(192.0)
    assert result.one_way_shear is not None
    assert result.one_way_shear_basis == "actual_provided_pt_final"
    assert result.one_way_shear.utilization_ratio == pytest.approx(0.95648558)
    assert result.punching is not None
    assert result.punching.utilization_ratio == pytest.approx(0.63)
    assert result.load_transfer.provided_transfer_steel_area_mm2 == pytest.approx(
        1_256.6371
    )
    assert result.qualified_review_required is True
    json.dumps(dataclasses.asdict(result))


def test_capability_claims_composition_and_retains_eccentric_foundation_holds() -> None:
    footing = next(
        item
        for item in services_api.get_supported_is456_capabilities()
        if item.element == "isolated_footing"
    )
    request_fields = {field.name for field in dataclasses.fields(_benchmark_request())}

    assert "design_concentric_isolated_footing_is456" in footing.public_workflows
    assert "uniform trial thickness" in footing.supported_case
    assert "service-load sizing" in footing.supported_case
    assert "provided-bar detailing" in footing.supported_case
    assert "eccentric_moment_kNm" not in request_fields
    assert any("Eccentric loading" in item for item in footing.held_cases)
    assert any("Combined, strap, raft" in item for item in footing.held_cases)
