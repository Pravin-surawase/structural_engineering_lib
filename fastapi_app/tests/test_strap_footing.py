"""Contract tests for the bounded property-line strap-footing FastAPI slice."""

from __future__ import annotations

from copy import deepcopy

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_app.routers.strap_footing import router


def _app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


def _payload() -> dict[str, object]:
    return {
        "case_id": "INDIA-2-STRAP-HAND-01",
        "footing": {
            "analysis": {
                "geometry": {
                    "exterior_footing_length_mm": 2400.0,
                    "exterior_footing_width_mm": 2500.0,
                    "exterior_footing_depth_mm": 700.0,
                    "interior_footing_length_mm": 2500.0,
                    "interior_footing_width_mm": 3200.0,
                    "interior_footing_depth_mm": 700.0,
                    "exterior_column_side_mm": 500.0,
                    "interior_column_side_mm": 500.0,
                    "exterior_column_center_x_mm": 400.0,
                    "interior_column_center_x_mm": 6400.0,
                    "strap_width_mm": 500.0,
                    "strap_overall_depth_mm": 950.0,
                    "strap_effective_depth_mm": 850.0,
                    "footing_count": 2,
                    "column_count": 2,
                    "footings_rectangular": True,
                    "footings_parallel": True,
                    "footings_constant_depth": True,
                    "columns_square": True,
                    "columns_and_strap_share_centerline": True,
                    "interior_column_centered_on_footing": True,
                    "strap_straight_and_prismatic": True,
                    "strap_centered_across_footings": True,
                    "foundation_on_soil": True,
                    "strap_soil_contact": False,
                    "openings_present": False,
                    "pedestals_present": False,
                    "analysis_method": "rigid_equal_pressure",
                    "pressure_model": "equal_uniform_net",
                    "geometry_basis_reference": "INDIA-2-STRAP-HAND-01-GEOMETRY",
                    "rigidity_basis_reference": "INDIA-2-STRAP-HAND-01-RIGIDITY",
                    "strap_isolation_basis_reference": (
                        "INDIA-2-STRAP-HAND-01-ISOLATION"
                    ),
                },
                "actions": {
                    "service_exterior_column_load_kn": 1025.5625,
                    "service_interior_column_load_kn": 1741.4375,
                    "factored_exterior_column_load_kn": 1538.34375,
                    "factored_interior_column_load_kn": 2612.15625,
                    "service_clear_strap_line_load_kn_per_m": 12.0,
                    "factored_clear_strap_line_load_kn_per_m": 18.0,
                    "service_exterior_footing_carrier_kn_per_m2": 20.0,
                    "service_interior_footing_carrier_kn_per_m2": 20.0,
                    "factored_exterior_footing_carrier_kn_per_m2": 30.0,
                    "factored_interior_footing_carrier_kn_per_m2": 30.0,
                    "allowable_gross_bearing_pressure_kn_per_m2": 250.0,
                    "load_combination_approved": True,
                    "bearing_and_settlement_approved": True,
                    "equal_uniform_pressure_approved": True,
                    "footing_carrier_basis_approved": True,
                    "strap_line_load_basis_approved": True,
                    "load_pattern_compatible": True,
                    "column_moments_present": False,
                    "horizontal_actions_present": False,
                    "uplift_or_load_reversal_present": False,
                    "independently_factored_or_patterned_actions_present": False,
                    "load_basis_reference": "INDIA-2-STRAP-HAND-01-LOAD",
                    "bearing_settlement_basis_reference": (
                        "INDIA-2-STRAP-HAND-01-GEOTECH"
                    ),
                    "footing_carrier_basis_reference": (
                        "INDIA-2-STRAP-HAND-01-CARRIER"
                    ),
                    "strap_line_load_basis_reference": (
                        "INDIA-2-STRAP-HAND-01-LINE-LOAD"
                    ),
                    "load_pattern_basis_reference": ("INDIA-2-STRAP-HAND-01-PATTERN"),
                },
                "approvals": {
                    "exterior_footing_design_verified": True,
                    "interior_footing_design_verified": True,
                    "column_and_strap_transfer_verified": True,
                    "footing_reinforcement_and_anchorage_verified": True,
                    "supporting_areas_verified": True,
                    "construction_clearances_verified": True,
                    "exterior_footing_verification_reference": "EXT-FOOTING-01",
                    "interior_footing_verification_reference": "INT-FOOTING-01",
                    "transfer_verification_reference": "TRANSFER-01",
                    "construction_verification_reference": "CONSTRUCTION-01",
                },
            },
            "material": {
                "strap_concrete_grade_nmm2": 30.0,
                "steel_grade_nmm2": 500.0,
                "uncoated_deformed_bars": True,
                "material_basis_reference": "INDIA-2-STRAP-HAND-01-MATERIAL",
            },
            "reinforcement": {
                "top_bar_count": 6,
                "top_bar_diameter_mm": 25.0,
                "bottom_bar_count": 4,
                "bottom_bar_diameter_mm": 16.0,
                "side_face_bar_count_each_face": 4,
                "side_face_bar_diameter_mm": 12.0,
                "side_face_vertical_spacing_mm": 250.0,
                "stirrup_leg_count": 2,
                "stirrup_diameter_mm": 10.0,
                "stirrup_spacing_mm": 250.0,
                "nominal_cover_mm": 50.0,
                "required_nominal_cover_mm": 50.0,
                "maximum_aggregate_size_mm": 20.0,
                "available_top_anchorage_exterior_mm": 1200.0,
                "available_top_anchorage_interior_mm": 1200.0,
                "available_bottom_anchorage_exterior_mm": 1200.0,
                "available_bottom_anchorage_interior_mm": 1200.0,
                "vertical_closed_stirrups": True,
                "straight_anchorage": True,
                "bars_bundled": False,
                "bars_spliced": False,
                "bars_curtailed": False,
                "reinforcement_schedule_approved": True,
                "effective_depth_basis_approved": True,
                "durability_cover_basis_approved": True,
                "detailing_basis_reference": "INDIA-2-STRAP-HAND-01-DETAILING",
                "durability_basis_reference": "INDIA-2-STRAP-HAND-01-DURABILITY",
            },
        },
        "qualified_review_required": True,
    }


def test_strap_footing_benchmark_returns_typed_pass_with_provenance() -> None:
    response = TestClient(_app()).post(
        "/api/v1/design/strap-footing/property-line", json=_payload()
    )

    assert response.status_code == 200
    data = response.json()["data"]
    strength = data["strength"]
    assert data["status"] == "PASS"
    assert strength["actions"]["service"]["exterior_reaction_kn"] == pytest.approx(
        1200.0
    )
    assert strength["actions"]["service"]["interior_reaction_kn"] == pytest.approx(
        1600.0
    )
    assert strength["flexure"]["exact_flexural_steel_required_mm2"] == pytest.approx(
        2788.774499810215
    )
    assert strength["flexure"]["top_moment_capacity_kn_m"] == pytest.approx(
        961.337320139164
    )
    assert strength["shear"]["stirrup_carried_shear_required_kn"] == pytest.approx(
        19.6274979428445
    )
    assert data["provenance"]["workflow"] == (
        "design_property_line_strap_footing_is456"
    )
    assert data["provenance"]["strap_isolation_basis_reference"].endswith("-ISOLATION")
    assert data["qualified_review_required"] is True
    assert data["complete_engineering_design_approved"] is False


def test_strap_footing_rejects_unknown_nonfinite_and_held_scope() -> None:
    invalid_requests: list[dict[str, object]] = []

    extra = deepcopy(_payload())
    extra["not_a_contract_field"] = True
    invalid_requests.append(extra)
    nonfinite = deepcopy(_payload())
    nonfinite["footing"]["analysis"]["geometry"][  # type: ignore[index]
        "strap_overall_depth_mm"
    ] = "NaN"
    invalid_requests.append(nonfinite)
    soil_contact = deepcopy(_payload())
    soil_contact["footing"]["analysis"]["geometry"][  # type: ignore[index]
        "strap_soil_contact"
    ] = True
    invalid_requests.append(soil_contact)
    unapproved_transfer = deepcopy(_payload())
    unapproved_transfer["footing"]["analysis"]["approvals"][  # type: ignore[index]
        "column_and_strap_transfer_verified"
    ] = False
    invalid_requests.append(unapproved_transfer)
    non_boolean_review = deepcopy(_payload())
    non_boolean_review["qualified_review_required"] = 1
    invalid_requests.append(non_boolean_review)

    client = TestClient(_app())
    for invalid in invalid_requests:
        response = client.post(
            "/api/v1/design/strap-footing/property-line", json=invalid
        )
        assert response.status_code == 422


def test_strap_footing_service_validation_uses_safe_error_envelope() -> None:
    invalid = deepcopy(_payload())
    invalid["footing"]["analysis"]["geometry"][  # type: ignore[index]
        "strap_effective_depth_mm"
    ] = 950.0

    response = TestClient(_app()).post(
        "/api/v1/design/strap-footing/property-line", json=invalid
    )

    assert response.status_code == 422
    body = response.json()
    assert set(body) == {"success", "data", "error"}
    assert body["success"] is False and body["data"] is None
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["error"]["details"][0]["msg"] == (
        "strap_effective_depth_mm must be less than strap_overall_depth_mm"
    )


def test_strap_footing_valid_inadequacy_remains_json_safe_fail() -> None:
    inadequate = deepcopy(_payload())
    inadequate["footing"]["analysis"]["actions"][  # type: ignore[index]
        "allowable_gross_bearing_pressure_kn_per_m2"
    ] = 210.0

    response = TestClient(_app()).post(
        "/api/v1/design/strap-footing/property-line", json=inadequate
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert (
        data["strength"]["actions"]["gross_service_bearing_within_allowable"] is False
    )
    assert data["status"] == "FAIL"


def test_strap_footing_openapi_exposes_typed_success_schema() -> None:
    schema = _app().openapi()
    operation = schema["paths"]["/api/v1/design/strap-footing/property-line"]["post"]
    component_names = set(schema["components"]["schemas"])

    assert operation["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("APIResponse_PropertyLineStrapFootingResponse_")
    assert "StrapFootingDesignRequest" in component_names
    assert "StrapFootingDesignRequest-Input" not in component_names
    assert "StrapFootingDesignRequest-Output" not in component_names
    response_schema = schema["components"]["schemas"][
        "PropertyLineStrapFootingResponse"
    ]
    assert response_schema["properties"]["strength"]
    assert response_schema["properties"]["provenance"]


def test_strap_footing_is_mounted_in_main_app(client: TestClient) -> None:
    response = client.post(
        "/api/v1/design/strap-footing/property-line", json=_payload()
    )

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "PASS"
