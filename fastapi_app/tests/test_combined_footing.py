"""Contract tests for the bounded symmetric combined-footing FastAPI slice."""

from __future__ import annotations

from copy import deepcopy

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_app.routers.combined_footing import router


def _app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


def _payload() -> dict[str, object]:
    return {
        "case_id": "INDIA-2-COMBINED-HAND-01",
        "footing": {
            "analysis": {
                "geometry": {
                    "footing_length_mm": 6000.0,
                    "footing_width_mm": 2500.0,
                    "overall_depth_mm": 850.0,
                    "effective_depth_mm": 750.0,
                    "column_side_mm": 500.0,
                    "left_column_center_x_mm": 1000.0,
                    "right_column_center_x_mm": 5000.0,
                    "column_count": 2,
                    "columns_identical": True,
                    "columns_square": True,
                    "columns_centered_across_width": True,
                    "foundation_on_soil": True,
                    "constant_depth": True,
                    "openings_present": False,
                    "pedestals_present": False,
                    "analysis_method": "conventional_rigid",
                    "pressure_model": "uniform",
                    "rigid_footing_verified": True,
                    "rigidity_basis_reference": ("INDIA-2-COMBINED-HAND-01-RIGIDITY"),
                    "geometry_basis_reference": ("INDIA-2-COMBINED-HAND-01-GEOMETRY"),
                },
                "actions": {
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
                    "bearing_settlement_basis_reference": (
                        "INDIA-2-COMBINED-HAND-01-BEARING"
                    ),
                    "cancellation_basis_reference": (
                        "INDIA-2-COMBINED-HAND-01-CANCELLATION"
                    ),
                },
            },
            "material": {
                "footing_concrete_grade_nmm2": 30,
                "column_concrete_grade_nmm2": 30,
                "steel_grade_nmm2": 500,
                "uncoated_deformed_bars": True,
                "material_basis_reference": "INDIA-2-COMBINED-HAND-01-MATERIAL",
            },
            "reinforcement": {
                "top_longitudinal_diameter_mm": 16,
                "top_longitudinal_spacing_mm": 190.0,
                "bottom_longitudinal_diameter_mm": 16,
                "bottom_longitudinal_spacing_mm": 190.0,
                "transverse_diameter_mm": 12,
                "transverse_spacing_mm": 110.0,
                "nominal_cover_mm": 50.0,
                "aggregate_size_mm": 20.0,
                "available_top_longitudinal_anchorage_each_end_mm": 800.0,
                "available_bottom_longitudinal_anchorage_each_end_mm": 800.0,
                "available_transverse_anchorage_each_edge_mm": 800.0,
                "straight_uncoated_deformed_bars": True,
                "effective_depth_basis_approved": True,
                "reinforcement_schedule_approved": True,
                "detailing_basis_reference": ("INDIA-2-COMBINED-HAND-01-DETAILING"),
            },
            "transfer": {
                "effective_supporting_area_each_mm2": 250000.0,
                "effective_supporting_area_basis": "largest_frustum_1v_2h",
                "effective_supporting_area_approved": True,
                "dowel_count_each": 4,
                "dowel_diameter_mm": 20,
                "column_longitudinal_bar_diameter_mm": 20,
                "available_dowel_development_into_footing_mm": 800.0,
                "available_dowel_development_into_column_mm": 800.0,
                "uncoated_deformed_dowels": True,
                "transfer_basis_reference": "INDIA-2-COMBINED-HAND-01-TRANSFER",
            },
        },
        "qualified_review_required": True,
    }


def test_combined_footing_benchmark_returns_typed_pass_with_provenance() -> None:
    response = TestClient(_app()).post(
        "/api/v1/design/combined-footing/symmetric", json=_payload()
    )

    assert response.status_code == 200
    data = response.json()["data"]
    strength = data["strength"]
    assert data["status"] == "PASS"
    assert strength["actions"]["gross_service_pressure_kn_per_m2"] == 145.0
    assert strength["actions"][
        "net_factored_structural_pressure_kn_per_m2"
    ] == pytest.approx(180.0)
    assert strength["top_longitudinal_flexure"][
        "factored_moment_kn_m"
    ] == pytest.approx(675.0)
    assert strength["punching"][0]["utilization"] == pytest.approx(0.208134572057151)
    assert strength["load_transfer"][0][
        "provided_transfer_steel_area_mm2"
    ] == pytest.approx(1256.6370614359173)
    assert data["provenance"]["workflow"] == ("design_symmetric_combined_footing_is456")
    assert data["provenance"]["geometry_basis_reference"].endswith("-GEOMETRY")
    assert data["qualified_review_required"] is True
    assert data["complete_engineering_design_approved"] is False


def test_combined_footing_rejects_unknown_nonfinite_and_held_scope() -> None:
    invalid_requests: list[dict[str, object]] = []

    extra = deepcopy(_payload())
    extra["not_a_contract_field"] = True
    invalid_requests.append(extra)
    nonfinite = deepcopy(_payload())
    nonfinite["footing"]["analysis"]["geometry"][  # type: ignore[index]
        "overall_depth_mm"
    ] = "NaN"
    invalid_requests.append(nonfinite)
    opening = deepcopy(_payload())
    opening["footing"]["analysis"]["geometry"][  # type: ignore[index]
        "openings_present"
    ] = True
    invalid_requests.append(opening)
    unapproved_soil = deepcopy(_payload())
    unapproved_soil["footing"]["analysis"]["actions"][  # type: ignore[index]
        "bearing_and_settlement_approved"
    ] = False
    invalid_requests.append(unapproved_soil)
    non_boolean_review = deepcopy(_payload())
    non_boolean_review["qualified_review_required"] = 1
    invalid_requests.append(non_boolean_review)

    client = TestClient(_app())
    for invalid in invalid_requests:
        response = client.post(
            "/api/v1/design/combined-footing/symmetric", json=invalid
        )
        assert response.status_code == 422


def test_combined_footing_service_validation_uses_safe_error_envelope() -> None:
    invalid = deepcopy(_payload())
    invalid["footing"]["analysis"]["geometry"][  # type: ignore[index]
        "right_column_center_x_mm"
    ] = 4900.0

    response = TestClient(_app()).post(
        "/api/v1/design/combined-footing/symmetric", json=invalid
    )

    assert response.status_code == 422
    body = response.json()
    assert set(body) == {"success", "data", "error"}
    assert body["success"] is False and body["data"] is None
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["error"]["details"][0]["msg"] == (
        "column positions must provide equal longitudinal end projections"
    )


def test_combined_footing_valid_inadequacy_remains_json_safe_fail() -> None:
    inadequate = deepcopy(_payload())
    inadequate["footing"]["analysis"]["actions"][  # type: ignore[index]
        "allowable_gross_bearing_pressure_kn_per_m2"
    ] = 140.0

    response = TestClient(_app()).post(
        "/api/v1/design/combined-footing/symmetric", json=inadequate
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert (
        data["strength"]["actions"]["gross_service_bearing_within_allowable"] is False
    )
    assert data["status"] == "FAIL"


def test_combined_footing_openapi_exposes_typed_success_schema() -> None:
    schema = _app().openapi()
    operation = schema["paths"]["/api/v1/design/combined-footing/symmetric"]["post"]

    assert operation["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("APIResponse_SymmetricCombinedFootingResponse_")
    response_schema = schema["components"]["schemas"][
        "SymmetricCombinedFootingResponse"
    ]
    assert response_schema["properties"]["strength"]
    assert response_schema["properties"]["provenance"]


def test_combined_footing_is_mounted_in_main_app(client: TestClient) -> None:
    response = client.post("/api/v1/design/combined-footing/symmetric", json=_payload())

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "PASS"
