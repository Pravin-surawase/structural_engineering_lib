"""Contract tests for the bounded regular interior flat-slab FastAPI slice."""

from __future__ import annotations

from copy import deepcopy

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_app.routers.flat_slab import router


def _app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


def _direction() -> dict[str, object]:
    return {
        "column_strip_negative_bars": {"diameter_mm": 12.0, "spacing_mm": 160.0},
        "column_strip_positive_bars": {"diameter_mm": 10.0, "spacing_mm": 200.0},
        "middle_strip_negative_bars": {"diameter_mm": 10.0, "spacing_mm": 200.0},
        "middle_strip_positive_bars": {"diameter_mm": 10.0, "spacing_mm": 200.0},
        "support_top_extension_from_face_mm": 1650.0,
    }


def _payload() -> dict[str, object]:
    return {
        "case_id": "INDIA-2-FLAT-HAND-01",
        "geometry": {
            "centre_to_centre_span_x_mm": 6000.0,
            "centre_to_centre_span_y_mm": 6000.0,
            "continuous_span_count_x": 3,
            "continuous_span_count_y": 3,
            "column_width_x_mm": 500.0,
            "column_width_y_mm": 500.0,
            "overall_depth_mm": 300.0,
            "conservative_effective_depth_mm": 260.0,
            "analysis_method": "direct_design",
            "panel_location": "interior",
            "all_spans_equal_x": True,
            "all_spans_equal_y": True,
            "columns_offset_from_grid": False,
            "solid_slab": True,
            "drop_present": False,
            "column_head_present": False,
            "marginal_beam_or_wall_present": False,
            "openings_present": False,
            "geometry_basis_reference": "INDIA-2-FLAT-HAND-01-GEOMETRY",
        },
        "material": {
            "concrete_grade_nmm2": 30,
            "steel_grade_nmm2": 500,
            "uncoated_deformed_bars": True,
            "material_basis_reference": "INDIA-2-FLAT-HAND-01-MATERIAL",
        },
        "gravity_load": {
            "service_dead_load_kn_per_m2": 9.0,
            "service_live_load_kn_per_m2": 4.0,
            "factored_uniform_load_kn_per_m2": 19.5,
            "self_weight_included": True,
            "identical_full_loading_on_represented_panels": True,
            "patterned_loading_required": False,
            "unbalanced_or_lateral_moment_transfer_present": False,
            "load_combination_approved": True,
            "load_basis_reference": "INDIA-2-FLAT-HAND-01-LOAD",
        },
        "x": _direction(),
        "y": _direction(),
        "factored_support_reaction_kn": 702.0,
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


def test_flat_slab_benchmark_returns_typed_pass_with_provenance() -> None:
    response = TestClient(_app()).post(
        "/api/v1/design/flat-slab/regular-interior", json=_payload()
    )

    assert response.status_code == 200
    data = response.json()["data"]
    reinforcement = data["reinforcement"]
    assert data["status"] == "PASS"
    assert reinforcement["geometry_x"]["governing_clear_span_mm"] == 5500.0
    assert reinforcement["moments_x"]["total_static_moment_knm"] == pytest.approx(
        442.40625
    )
    assert reinforcement["x"]["column_strip_negative"][
        "ast_required_total_mm2"
    ] == pytest.approx(1993.0759957303314)
    assert reinforcement["x_serviceability"]["utilization"] == pytest.approx(
        0.9861932938856016
    )
    assert data["punching"]["punching_shear_force_kn"] == pytest.approx(690.7368)
    assert data["punching"]["no_reinforcement_utilization"] == pytest.approx(
        0.6382120901359107
    )
    assert data["provenance"]["workflow"] == ("design_regular_interior_flat_slab_is456")
    assert data["qualified_review_required"] is True
    assert data["complete_engineering_design_approved"] is False


def test_flat_slab_rejects_unknown_nonfinite_and_unsupported_scope() -> None:
    invalid_requests: list[dict[str, object]] = []

    extra = deepcopy(_payload())
    extra["not_a_contract_field"] = True
    invalid_requests.append(extra)
    nonfinite = deepcopy(_payload())
    nonfinite["factored_support_reaction_kn"] = "NaN"
    invalid_requests.append(nonfinite)
    opening = deepcopy(_payload())
    opening["geometry"]["openings_present"] = True  # type: ignore[index]
    invalid_requests.append(opening)
    moment_transfer = deepcopy(_payload())
    moment_transfer["gravity_load"][  # type: ignore[index]
        "unbalanced_or_lateral_moment_transfer_present"
    ] = True
    invalid_requests.append(moment_transfer)
    non_boolean_review = deepcopy(_payload())
    non_boolean_review["qualified_review_required"] = 1
    invalid_requests.append(non_boolean_review)

    client = TestClient(_app())
    for invalid in invalid_requests:
        response = client.post(
            "/api/v1/design/flat-slab/regular-interior", json=invalid
        )
        assert response.status_code == 422


def test_flat_slab_service_validation_uses_safe_error_envelope() -> None:
    invalid = deepcopy(_payload())
    invalid["factored_support_reaction_kn"] = 701.0

    response = TestClient(_app()).post(
        "/api/v1/design/flat-slab/regular-interior", json=invalid
    )

    assert response.status_code == 422
    body = response.json()
    assert set(body) == {"success", "data", "error"}
    assert body["success"] is False and body["data"] is None
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["error"]["details"][0]["msg"] == (
        "factored_support_reaction_kn must match the uniform tributary reaction "
        "for the frozen equal-panel topology"
    )


def test_flat_slab_valid_inadequacy_remains_json_safe_fail() -> None:
    inadequate = deepcopy(_payload())
    inadequate["x"]["column_strip_negative_bars"][  # type: ignore[index]
        "spacing_mm"
    ] = 200.0

    response = TestClient(_app()).post(
        "/api/v1/design/flat-slab/regular-interior", json=inadequate
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["reinforcement"]["x"]["column_strip_negative"]["is_adequate"] is False
    assert data["status"] == "FAIL"


def test_flat_slab_openapi_exposes_typed_success_schema() -> None:
    schema = _app().openapi()
    operation = schema["paths"]["/api/v1/design/flat-slab/regular-interior"]["post"]

    assert operation["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("APIResponse_RegularInteriorFlatSlabResponse_")
    response_schema = schema["components"]["schemas"]["RegularInteriorFlatSlabResponse"]
    assert response_schema["properties"]["reinforcement"]
    assert response_schema["properties"]["punching"]
    assert response_schema["properties"]["provenance"]


def test_flat_slab_is_mounted_in_main_app(client: TestClient) -> None:
    response = client.post("/api/v1/design/flat-slab/regular-interior", json=_payload())

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "PASS"
