"""Request-to-public-library evidence for the new footing and slab consumers."""

from __future__ import annotations

import pytest


def _footing_load_transfer_payload(**overrides):
    payload = {
        "Pu_kN": 3000,
        "loaded_area_A2_mm2": 160000,
        "effective_supporting_area_A1_mm2": 640000,
        "effective_supporting_area_basis": "largest_frustum_1v_2h",
        "effective_supporting_area_is_approved": True,
        "supporting_concrete_fck_nmm2": 20,
        "supported_concrete_fck_nmm2": 25,
        "steel_fy_nmm2": 415,
        "dowel_count": 8,
        "dowel_diameter_mm": 25,
        "column_longitudinal_bar_diameter_mm": 32,
        "available_dowel_development_length_into_footing_mm": 1176,
        "available_dowel_development_length_into_supported_member_mm": 1010,
        "dowel_bar_type": "deformed",
    }
    payload.update(overrides)
    return payload


def _unwrap(response):
    body = response.json()
    assert body["success"] is True, body
    return body["data"]


def test_footing_load_transfer_endpoint_calls_supported_public_workflow(client):
    response = client.post(
        "/api/v1/design/footing/load-transfer",
        json=_footing_load_transfer_payload(),
    )

    assert response.status_code == 200
    data = _unwrap(response)
    assert data["governing_concrete_bearing_capacity_kN"] == 1800
    assert data["is_safe"] is True
    assert data["effective_supporting_area_basis"] == "largest_frustum_1v_2h"


@pytest.mark.parametrize("dowel_count", [6.8, True, 0])
def test_footing_load_transfer_endpoint_rejects_non_integral_or_invalid_count(
    client, dowel_count
):
    response = client.post(
        "/api/v1/design/footing/load-transfer",
        json=_footing_load_transfer_payload(dowel_count=dowel_count),
    )

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["error"]["details"]


def test_footing_load_transfer_endpoint_accepts_four_integral_dowels(client):
    response = client.post(
        "/api/v1/design/footing/load-transfer",
        json=_footing_load_transfer_payload(dowel_count=4),
    )

    assert response.status_code == 200
    assert _unwrap(response)["provided_bar_count"] == 4


def test_one_way_slab_endpoint_calls_supported_public_workflow(client):
    response = client.post(
        "/api/v1/design/slab/one-way",
        json={
            "short_effective_span_mm": 3000,
            "long_effective_span_mm": 7500,
            "thickness_mm": 150,
            "d_mm": 125,
            "factored_area_load_kn_per_m2": 10,
            "fck_n_per_mm2": 20,
            "fy_n_per_mm2": 415,
            "main_bar_diameter_mm": 10,
            "main_bar_spacing_mm": 250,
            "distribution_bar_diameter_mm": 8,
            "distribution_bar_spacing_mm": 250,
        },
    )

    assert response.status_code == 200
    data = _unwrap(response)
    assert data["flexure"]["factored_moment_knm"] == 11.25
    assert data["detailing"]["detailing_adequacy"] == "adequate"
    assert data["detailing"]["review_requirement"] == "qualified_review_required"


def test_one_way_slab_endpoint_rejects_two_way_geometry(client):
    response = client.post(
        "/api/v1/design/slab/one-way",
        json={
            "short_effective_span_mm": 3000,
            "long_effective_span_mm": 6000,
            "thickness_mm": 150,
            "d_mm": 125,
            "factored_area_load_kn_per_m2": 10,
            "fck_n_per_mm2": 20,
            "fy_n_per_mm2": 415,
            "main_bar_diameter_mm": 10,
            "main_bar_spacing_mm": 250,
            "distribution_bar_diameter_mm": 8,
            "distribution_bar_spacing_mm": 250,
        },
    )

    assert response.status_code == 422
    assert response.json()["success"] is False


def test_complete_one_way_slab_endpoint_serializes_composed_workflow_truth(client):
    response = client.post(
        "/api/v1/design/slab/one-way/complete",
        json={
            "short_effective_span_mm": 3000,
            "long_effective_span_mm": 7500,
            "thickness_mm": 150,
            "d_mm": 125,
            "factored_area_load_kn_per_m2": 10,
            "fck_n_per_mm2": 20,
            "fy_n_per_mm2": 415,
            "main_bar_diameter_mm": 10,
            "main_bar_spacing_mm": 250,
            "distribution_bar_diameter_mm": 8,
            "distribution_bar_spacing_mm": 250,
            "reviewed_base_span_depth_limit": 20,
            "reviewed_aggregate_modification_factor": 1.2,
            "serviceability_limit_source_reference": "IS456_CL23_REVIEWED",
            "serviceability_limit_source_is_approved": True,
            "qualified_serviceability_acceptance_reference": "review:B01-SLS",
            "qualified_serviceability_acceptance_acknowledged": True,
        },
    )
    assert response.status_code == 200, response.json()
    data = _unwrap(response)
    assert (
        data["reinforcement"]["flexure"]["status"]
        == "complete_workflow_checks_composed"
    )
    serialized_limitations = (
        data["reinforcement"]["flexure"]["limitations"]
        + data["reinforcement"]["detailing"]["limitations"]
    )
    assert not any("pending" in item.lower() for item in serialized_limitations)
    assert data["shear"]["status"] == "concrete_capacity_satisfied"
    assert data["serviceability"]["status"] == "satisfied_with_reviewed_limit"


def _continuous_slab_payload(**overrides):
    payload = {
        "short_effective_span_mm": 3000,
        "long_effective_span_mm": 7500,
        "thickness_mm": 140,
        "d_mm": 115,
        "factored_area_load_kn_per_m2": 14.25,
        "fck_n_per_mm2": 20,
        "fy_n_per_mm2": 415,
        "positive_moment_coefficient": 1 / 12,
        "negative_moment_coefficient": 1 / 10,
        "shear_coefficient": 0.4,
        "coefficient_source_reference": "NPTEL-L18-B02",
        "coefficient_source_is_approved": True,
        "qualified_coefficient_acceptance_reference": "review:B02",
        "qualified_coefficient_acceptance_acknowledged": True,
        "number_of_spans": 3,
        "maximum_span_variation_percent": 0,
        "uniform_cross_section_acknowledged": True,
        "substantially_uniform_load_acknowledged": True,
        "redistribution_applied": False,
        "positive_bar_diameter_mm": 8,
        "positive_bar_spacing_mm": 180,
        "negative_bar_diameter_mm": 10,
        "negative_bar_spacing_mm": 230,
        "distribution_bar_diameter_mm": 8,
        "distribution_bar_spacing_mm": 250,
        "reviewed_base_span_depth_limit": 23,
        "reviewed_aggregate_modification_factor": 1.18,
        "serviceability_limit_source_reference": "NPTEL-L18-B02-SLS",
        "serviceability_limit_source_is_approved": True,
        "qualified_serviceability_acceptance_reference": "review:B02-SLS",
        "qualified_serviceability_acceptance_acknowledged": True,
    }
    payload.update(overrides)
    return payload


def _two_way_slab_payload(**overrides):
    payload = {
        "x_effective_span_mm": 4000,
        "y_effective_span_mm": 6000,
        "thickness_mm": 160,
        "x_min_edge": "discontinuous",
        "x_max_edge": "continuous",
        "y_min_edge": "discontinuous",
        "y_max_edge": "continuous",
        "corner_lift_condition": "restrained",
        "support_topology_kind": "two_adjacent_edges_discontinuous",
        "alpha_x_negative": 0.075,
        "alpha_x_positive": 0.056,
        "alpha_y_negative": 0.047,
        "alpha_y_positive": 0.035,
        "coefficient_source_reference": "NPTEL-L19-B04",
        "coefficient_source_is_approved": True,
        "qualified_coefficient_acceptance_reference": "review:B04",
        "qualified_coefficient_acceptance_acknowledged": True,
        "factored_area_load_kn_per_m2": 15.5,
        "d_x_mm": 135,
        "d_y_mm": 125,
        "fck_n_per_mm2": 20,
        "fy_n_per_mm2": 415,
        "x_positive_bar_diameter_mm": 10,
        "x_positive_bar_spacing_mm": 200,
        "x_negative_bar_diameter_mm": 10,
        "x_negative_bar_spacing_mm": 200,
        "y_positive_bar_diameter_mm": 8,
        "y_positive_bar_spacing_mm": 200,
        "y_negative_bar_diameter_mm": 8,
        "y_negative_bar_spacing_mm": 200,
        "edge_strip_bar_diameter_mm": 8,
        "edge_strip_bar_spacing_mm": 250,
        "torsion_bar_diameter_mm": 8,
        "torsion_bar_spacing_mm": 200,
        "reviewed_base_span_depth_limit": 30,
        "reviewed_aggregate_modification_factor": 1,
        "serviceability_limit_source_reference": "NPTEL-L19-B04-SLS",
        "serviceability_limit_source_is_approved": True,
        "qualified_serviceability_acceptance_reference": "review:B04-SLS",
        "qualified_serviceability_acceptance_acknowledged": True,
    }
    payload.update(overrides)
    return payload


def test_continuous_one_way_slab_endpoint_returns_b02_actions(client):
    response = client.post(
        "/api/v1/design/slab/one-way/continuous",
        json=_continuous_slab_payload(),
    )
    assert response.status_code == 200, response.json()
    data = _unwrap(response)
    assert data["flexure"]["positive_midspan"][
        "factored_moment_knm_per_m"
    ] == pytest.approx(10.6875)
    assert data["flexure"]["negative_support"][
        "factored_moment_knm_per_m"
    ] == pytest.approx(12.825)
    assert data["flexure"]["coefficient_correctness_verified_by_library"] is False
    assert data["shear"]["punching_shear_disposition"].startswith("not_applicable")


def test_continuous_endpoint_rejects_redistribution_or_unapproved_source(client):
    for payload in (
        _continuous_slab_payload(redistribution_applied=True),
        _continuous_slab_payload(coefficient_source_is_approved=False),
    ):
        response = client.post("/api/v1/design/slab/one-way/continuous", json=payload)
        assert response.status_code == 422


def test_two_way_slab_panel_endpoint_returns_b04_topology_and_torsion(client):
    response = client.post(
        "/api/v1/design/slab/two-way/panel", json=_two_way_slab_payload()
    )
    assert response.status_code == 200, response.json()
    data = _unwrap(response)
    assert data["panel"]["x_negative"]["factored_moment_knm_per_m"] == pytest.approx(
        18.6
    )
    assert data["panel"]["y_positive"]["factored_moment_knm_per_m"] == pytest.approx(
        8.68
    )
    assert data["panel"]["corner_torsion"][0]["torsion_class"] == "full"
    assert data["panel"]["corner_torsion"][0]["zone_extent_from_each_edge_mm"] == 800
    assert data["panel"]["coefficient_correctness_verified_by_library"] is False


def test_two_way_endpoint_rejects_topology_coefficient_mismatch(client):
    response = client.post(
        "/api/v1/design/slab/two-way/panel",
        json=_two_way_slab_payload(support_topology_kind="four_edges_continuous"),
    )
    assert response.status_code == 422


def test_builtin_continuous_endpoint_resolves_tables_12_and_13(client):
    payload = _continuous_slab_payload()
    for field in (
        "factored_area_load_kn_per_m2",
        "positive_moment_coefficient",
        "negative_moment_coefficient",
        "shear_coefficient",
        "coefficient_source_reference",
        "coefficient_source_is_approved",
        "qualified_coefficient_acceptance_reference",
        "qualified_coefficient_acceptance_acknowledged",
    ):
        payload.pop(field)
    payload.update(
        {
            "factored_dead_and_fixed_imposed_load_kn_per_m2": 14.25,
            "factored_nonfixed_imposed_load_kn_per_m2": 0,
            "positive_location": "end_span_positive",
            "negative_location": "next_to_end_support_negative",
            "shear_location": "end_support",
        }
    )
    response = client.post(
        "/api/v1/design/slab/one-way/continuous/builtin", json=payload
    )
    assert response.status_code == 200, response.json()
    data = _unwrap(response)
    assert data["flexure"]["input"]["coefficients"]["table_id"] == "IS456_TABLE_12_13"
    assert data["flexure"]["coefficient_correctness_verified_by_library"] is True


def test_builtin_two_way_endpoint_resolves_table_26_case_4(client):
    payload = _two_way_slab_payload()
    for field in (
        "support_topology_kind",
        "alpha_x_negative",
        "alpha_x_positive",
        "alpha_y_negative",
        "alpha_y_positive",
        "coefficient_source_reference",
        "coefficient_source_is_approved",
        "qualified_coefficient_acceptance_reference",
        "qualified_coefficient_acceptance_acknowledged",
    ):
        payload.pop(field)
    response = client.post("/api/v1/design/slab/two-way/panel/builtin", json=payload)
    assert response.status_code == 200, response.json()
    data = _unwrap(response)
    coefficients = data["panel"]["input"]["coefficients"]
    assert coefficients["case_id"] == "table_26_case_4"
    assert coefficients["method"] == "built_in_exact"
    assert data["panel"]["coefficient_correctness_verified_by_library"] is True
    assert data["panel"]["serviceability_dependency"] == (
        "evaluated_by_composed_workflow_with_reviewed_limit_carrier"
    )
    assert not any(
        "built-in coefficient" in item.lower() for item in data["panel"]["held_scope"]
    )


def test_library_core_pydantic_422_uses_standard_envelope(client):
    response = client.post("/api/v1/design/slab/one-way", json={})

    assert response.status_code == 422
    body = response.json()
    assert set(body) == {"success", "data", "error"}
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["error"]["details"]
    assert body["error"]["details"][0]["loc"][0] == "body"


def test_existing_endpoint_pydantic_422_uses_same_envelope(client):
    response = client.post(
        "/api/v1/design/beam",
        json={"width": -100, "depth": 500, "moment": 150},
    )

    assert response.status_code == 422
    body = response.json()
    assert set(body) == {"success", "data", "error"}
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    locations = [detail["loc"] for detail in body["error"]["details"]]
    assert ["body", "width"] in locations


def test_openapi_documents_the_maintained_422_envelope(client):
    schema = client.get("/openapi.json").json()

    for path in (
        "/api/v1/design/slab/one-way",
        "/api/v1/design/beam",
    ):
        response_schema = schema["paths"][path]["post"]["responses"]["422"]
        assert response_schema["description"] == "Request validation failed"
        assert response_schema["content"]["application/json"]["schema"] == {
            "$ref": "#/components/schemas/ProblemResponse"
        }
