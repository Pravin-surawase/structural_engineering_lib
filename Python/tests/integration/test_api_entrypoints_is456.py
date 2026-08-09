"""Integrated public-entrypoint checks for the supported IS 456 RC core."""

from __future__ import annotations

import pytest

import structural_lib
from structural_lib import api
from structural_lib.services import api as services_api

PUBLIC_COMPLETION_SYMBOLS = (
    "calculate_development_length",
    "check_anchorage_at_simple_support",
    "check_isolated_footing_load_transfer",
    "design_one_way_slab_is456",
    "design_two_way_slab_is456",
    "get_supported_is456_capability_document",
    "get_supported_is456_capabilities",
    "get_supported_is456_semantic_contract",
)


def test_completion_symbols_have_one_canonical_service_facade_and_compatibility_paths():
    for name in PUBLIC_COMPLETION_SYMBOLS:
        canonical = getattr(services_api, name)
        assert name in services_api.__all__
        assert getattr(api, name) is canonical
        assert getattr(structural_lib, name) is canonical
        assert name in structural_lib.__all__


def test_development_length_service_adapter_matches_transport_contract():
    result = services_api.calculate_development_length(
        bar_diameter=16,
        fck=25,
        fy=500,
        bar_type="deformed",
    )

    assert result == pytest.approx({"tau_bd": 2.24, "ld": 777.0})


def test_one_way_public_workflow_matches_independent_packet_benchmark():
    result = services_api.design_one_way_slab_is456(
        short_effective_span_mm=3000,
        long_effective_span_mm=7500,
        thickness_mm=150,
        d_mm=125,
        factored_area_load_kn_per_m2=10,
        fck_n_per_mm2=20,
        fy_n_per_mm2=415,
        main_bar_diameter_mm=10,
        main_bar_spacing_mm=250,
        distribution_bar_diameter_mm=8,
        distribution_bar_spacing_mm=250,
    )

    assert result.flexure.factored_moment_knm == pytest.approx(11.25)
    assert result.flexure.ast_required_mm2 == pytest.approx(260.7266304)
    assert result.is_detailing_adequate is True
    assert result.detailing.review_requirement.value == "qualified_review_required"


def test_two_way_public_workflow_matches_independent_packet_benchmark():
    result = services_api.design_two_way_slab_is456(
        short_effective_span_mm=4000,
        long_effective_span_mm=6000,
        thickness_mm=180,
        alpha_x=0.08,
        alpha_y=0.06,
        coefficient_source_reference="qualified-external-sheet:table-row-14",
        coefficient_source_is_approved=True,
        qualified_coefficient_acceptance_reference="engineer-review:two-way-panel-1",
        qualified_coefficient_acceptance_acknowledged=True,
        is_interior_solid_rectangular_panel=True,
        all_four_edges_continuous=True,
        factored_area_load_kn_per_m2=10,
        d_x_mm=150,
        d_y_mm=140,
        fck_n_per_mm2=20,
        fy_n_per_mm2=415,
    )

    assert result.x_direction.factored_moment_knm == pytest.approx(12.8)
    assert result.y_direction.factored_moment_knm == pytest.approx(9.6)
    assert result.x_direction.ast_required_mm2 == pytest.approx(244.7591, abs=1e-4)
    assert result.y_direction.ast_required_mm2 == pytest.approx(195.6828, abs=1e-4)
    assert result.bounded_flexure_computation_supported is True
    assert result.coefficient_review_status.value == "review_required"
    assert result.qualified_acceptance_recorded is True
    assert result.coefficient_correctness_verified_by_library is False
    assert result.complete_engineering_design_approved is False


@pytest.mark.parametrize(
    ("is_interior", "all_four_continuous"),
    [(False, True), (True, False)],
)
def test_two_way_public_workflow_rejects_unsupported_panel_configuration(
    is_interior, all_four_continuous
):
    with pytest.raises(ValueError):
        services_api.design_two_way_slab_is456(
            short_effective_span_mm=4000,
            long_effective_span_mm=6000,
            thickness_mm=180,
            alpha_x=0.08,
            alpha_y=0.06,
            coefficient_source_reference="qualified-external-sheet:table-row-14",
            coefficient_source_is_approved=True,
            qualified_coefficient_acceptance_reference="engineer-review:two-way-panel-1",
            qualified_coefficient_acceptance_acknowledged=True,
            is_interior_solid_rectangular_panel=is_interior,
            all_four_edges_continuous=all_four_continuous,
            factored_area_load_kn_per_m2=10,
            d_x_mm=150,
            d_y_mm=140,
            fck_n_per_mm2=20,
            fy_n_per_mm2=415,
        )


def test_capability_registry_names_every_supported_core_element():
    capabilities = services_api.get_supported_is456_capabilities()

    assert tuple(item.element for item in capabilities) == (
        "beam",
        "column",
        "isolated_footing",
        "solid_slab",
    )
    assert all(item.qualified_review_required for item in capabilities)
    assert all(item.public_workflows for item in capabilities)
    slab_capability = next(
        item for item in capabilities if item.element == "solid_slab"
    )
    assert "externally accepted coefficient, flexure-only supported case" in (
        slab_capability.supported_case
    )


def test_capability_document_is_json_native_and_preserves_review_boundaries():
    document = services_api.get_supported_is456_capability_document()

    assert document["schema_version"] == "1.0"
    assert document["code_edition"] == "IS 456:2000"
    assert [item["capability_id"] for item in document["capabilities"]] == [
        "beam",
        "column",
        "isolated_footing",
        "solid_slab",
    ]
    assert all(
        item["capability_id"] == item["element"]
        and item["qualified_review_required"]
        and isinstance(item["held_cases"], list)
        for item in document["capabilities"]
    )
    assert isinstance(document["semantic_contract"]["workflows"], list)
