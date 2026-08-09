"""Request-to-public-library evidence for the new footing and slab consumers."""

from __future__ import annotations


def _unwrap(response):
    body = response.json()
    assert body["success"] is True, body
    return body["data"]


def test_footing_load_transfer_endpoint_calls_supported_public_workflow(client):
    response = client.post(
        "/api/v1/design/footing/load-transfer",
        json={
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
        },
    )

    assert response.status_code == 200
    data = _unwrap(response)
    assert data["governing_concrete_bearing_capacity_kN"] == 1800
    assert data["is_safe"] is True
    assert data["effective_supporting_area_basis"] == "largest_frustum_1v_2h"


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
