"""Contract tests for the isolated concentric-footing FastAPI slice."""

from __future__ import annotations

from copy import deepcopy

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_app.routers.footing import router


def _app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


def _payload(*, detailing: bool = True) -> dict[str, object]:
    payload: dict[str, object] = {
        "case_id": "FOOT-C1-SQ-001",
        "service_axial_load_kN": 800.0,
        "service_load_combination_id": "SLS-GRAVITY-01",
        "service_load_basis": "includes_footing_self_weight_and_overburden",
        "service_load_origin": "provided",
        "factored_axial_load_kN": 1200.0,
        "factored_load_combination_id": "ULS-GRAVITY-01",
        "allowable_soil_pressure_kPa": 200.0,
        "allowable_soil_pressure_source_reference": "GEO-REPORT-001",
        "allowable_soil_pressure_origin": "verified",
        "allowable_soil_pressure_is_externally_approved": True,
        "footing_type": "ISOLATED_SQUARE",
        "column_L_mm": 400.0,
        "column_B_mm": 400.0,
        "minimum_overall_thickness_mm": 500.0,
        "maximum_overall_thickness_mm": 500.0,
        "thickness_increment_mm": 50.0,
        "effective_depth_offset_L_mm": 100.0,
        "effective_depth_offset_B_mm": 100.0,
        "footing_concrete_fck_nmm2": 25.0,
        "column_concrete_fck_nmm2": 25.0,
        "steel_fy_nmm2": 415.0,
        "effective_supporting_area_A1_mm2": 640000.0,
        "effective_supporting_area_basis": "largest_frustum_1v_2h",
        "effective_supporting_area_origin": "provided",
        "effective_supporting_area_is_approved": True,
        "dowel_count": 4,
        "dowel_diameter_mm": 20.0,
        "column_longitudinal_bar_diameter_mm": 20.0,
        "available_dowel_development_length_into_footing_mm": 1000.0,
        "available_dowel_development_length_into_column_mm": 1000.0,
    }
    if detailing:
        payload.update(
            {
                "nominal_cover_mm": 50.0,
                "cover_exposure_basis": "approved severe footing schedule",
                "cover_exposure_basis_is_approved": True,
                "nominal_max_aggregate_size_mm": 20.0,
                "lower_bottom_bar_direction": "L",
                "upper_bottom_bar_direction": "B",
                "permitted_bottom_bar_diameters_mm": [12, 16, 20, 25, 32],
                "footing_bottom_bar_type": "deformed",
            }
        )
    return payload


def test_concentric_footing_completed_benchmark_is_typed_pass():
    response = TestClient(_app()).post(
        "/api/v1/design/footing/isolated/concentric", json=_payload()
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert (
        data["status"]
        == data["calculation_status"]
        == data["detailing_status"]
        == "PASS"
    )
    assert data["one_way_shear_basis"] == "actual_provided_pt_final"
    assert data["one_way_shear"]["is_safe"] is True
    assert data["screening_pt_passed_to_one_way_shear_percent"] == {
        "L": 0.17111543963683395,
        "B": 0.17111543963683395,
    }
    assert data["pt_passed_to_one_way_shear_percent"] == {
        "L": 0.1837831702350029,
        "B": 0.1837831702350029,
    }
    assert all(
        item["provided_steel_area_mm2"] >= item["required_steel_area_mm2"]
        for item in data["reinforcement_demands"]
    )
    assert data["provenance"]["service_load_combination_id"] == "SLS-GRAVITY-01"
    assert data["provenance"]["source_ids"]
    assert data["exclusions"] and data["qualified_review_required"] is True


def test_concentric_footing_without_detailing_is_calculation_pass_and_hold():
    response = TestClient(_app()).post(
        "/api/v1/design/footing/isolated/concentric", json=_payload(detailing=False)
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["calculation_status"] == "PASS"
    assert data["detailing_status"] == data["status"] == "HOLD"
    assert data["one_way_shear_basis"] == "required_pt_screening"
    assert data["detailing"] is None
    assert data["detailing_hold_reason"]


def test_concentric_footing_transports_supported_bend_evidence():
    payload = _payload()
    payload.update(
        {
            "bottom_bar_end_arrangement": "bend_90",
            "bend_internal_radius_mm": 24.0,
            "extension_after_bend_mm": 144.0,
            "bend_geometry_source_reference": ("APPROVED-FOOTING-BEND-SCHEDULE-90"),
            "bend_geometry_source_is_approved": True,
        }
    )

    response = TestClient(_app()).post(
        "/api/v1/design/footing/isolated/concentric", json=payload
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "PASS"
    lower = data["detailing"]["lower"]
    assert lower["end_anchorage"]["arrangement"] == "bend_90"
    assert lower["end_anchorage"]["anchorage_is_adequate"] is True
    assert lower["end_anchorage"]["bounded_constructability_is_adequate"] is True
    assert lower["total_bar_length_mm"] > lower["straight_bar_length_mm"]


def test_concentric_footing_transports_unsupported_arrangement_hold():
    payload = _payload()
    payload["bottom_bar_end_arrangement"] = "bend_135"

    response = TestClient(_app()).post(
        "/api/v1/design/footing/isolated/concentric", json=payload
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["calculation_status"] == "PASS"
    assert data["detailing_status"] == data["status"] == "HOLD"
    assert "outside the supported" in data["detailing"]["reasons"][0]


def test_concentric_rectangular_wire_type_reaches_the_same_service_authority():
    payload = _payload(detailing=False)
    payload.update(
        {
            "case_id": "FOOT-C1-RECT-001",
            "service_axial_load_kN": 1000.0,
            "factored_axial_load_kN": 1500.0,
            "footing_type": "ISOLATED_RECTANGULAR",
            "column_B_mm": 300.0,
            "minimum_overall_thickness_mm": 600.0,
            "maximum_overall_thickness_mm": 700.0,
            "effective_depth_offset_L_mm": 80.0,
            "effective_depth_offset_B_mm": 80.0,
            "effective_supporting_area_A1_mm2": 480000.0,
            "dowel_count": 8,
            "dowel_diameter_mm": 25.0,
            "column_longitudinal_bar_diameter_mm": 25.0,
            "available_dowel_development_length_into_footing_mm": 1400.0,
            "available_dowel_development_length_into_column_mm": 1400.0,
        }
    )

    response = TestClient(_app()).post(
        "/api/v1/design/footing/isolated/concentric", json=payload
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert (data["bearing"]["L_mm"], data["bearing"]["B_mm"]) == (2600.0, 1950.0)
    assert data["provenance"]["allowable_soil_pressure_source_reference"] == (
        "GEO-REPORT-001"
    )


def test_concentric_footing_openapi_exposes_typed_path_and_success_schema():
    schema = _app().openapi()
    operation = schema["paths"]["/api/v1/design/footing/isolated/concentric"]["post"]

    assert operation["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("APIResponse_ConcentricIsolatedFootingResponse_")
    assert schema["components"]["schemas"]["ConcentricIsolatedFootingResponse"][
        "properties"
    ]["bearing"]
    assert schema["components"]["schemas"]["ConcentricIsolatedFootingResponse"][
        "properties"
    ]["detailing"]


def test_concentric_footing_rejects_unknown_and_nonfinite_values():
    client = TestClient(_app())
    extra = deepcopy(_payload())
    extra["not_a_contract_field"] = True
    assert (
        client.post(
            "/api/v1/design/footing/isolated/concentric", json=extra
        ).status_code
        == 422
    )

    nonfinite = deepcopy(_payload())
    nonfinite["service_axial_load_kN"] = "NaN"
    assert (
        client.post(
            "/api/v1/design/footing/isolated/concentric", json=nonfinite
        ).status_code
        == 422
    )


def test_concentric_footing_service_validation_uses_canonical_safe_envelope():
    invalid_range = deepcopy(_payload())
    invalid_range["maximum_overall_thickness_mm"] = 450.0

    response = TestClient(_app()).post(
        "/api/v1/design/footing/isolated/concentric", json=invalid_range
    )

    assert response.status_code == 422
    body = response.json()
    assert set(body) == {"success", "data", "error"}
    assert body["success"] is False and body["data"] is None
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["error"]["message"] == "Request validation failed"
    assert body["error"]["details"][0]["loc"] == ["body"]
    assert "maximum overall thickness" in body["error"]["details"][0]["msg"]


def test_main_app_mount_and_error_openapi_contract(client):
    response = client.post(
        "/api/v1/design/footing/isolated/concentric", json=_payload(detailing=False)
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "HOLD"

    invalid_requests = []
    invalid_dowel_count = deepcopy(_payload())
    invalid_dowel_count["dowel_count"] = True
    invalid_requests.append(invalid_dowel_count)
    invalid_footing_type = deepcopy(_payload())
    invalid_footing_type["footing_type"] = "COMBINED"
    invalid_requests.append(invalid_footing_type)
    missing_required_input = deepcopy(_payload())
    missing_required_input.pop("allowable_soil_pressure_source_reference")
    invalid_requests.append(missing_required_input)

    for invalid in invalid_requests:
        invalid_response = client.post(
            "/api/v1/design/footing/isolated/concentric", json=invalid
        )
        assert invalid_response.status_code == 422
        error = invalid_response.json()
        assert set(error) == {"success", "data", "error"}
        assert error["error"]["code"] == "REQUEST_VALIDATION_ERROR"

    operation = client.app.openapi()["paths"][
        "/api/v1/design/footing/isolated/concentric"
    ]["post"]
    assert operation["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("APIResponse_ConcentricIsolatedFootingResponse_")
    assert operation["responses"]["422"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/ProblemResponse"
    }
