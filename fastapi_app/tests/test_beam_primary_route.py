"""Focused FastAPI contract tests for the primary IS 456 beam route."""

import pytest
from fastapi import status

from fastapi_app.tests.conftest import unwrap
from structural_lib.services.api import design_beam_is456
from structural_lib.services.project_beam import EffectiveDepthBasisV1


@pytest.fixture
def ordinary_payload() -> dict[str, float]:
    return {
        "width": 300.0,
        "depth": 500.0,
        "moment": 150.0,
        "shear": 75.0,
        "fck": 25.0,
        "fy": 500.0,
        "clear_cover": 25.0,
        "stirrup_dia_mm": 8.0,
        "main_bar_dia_mm": 20.0,
    }


@pytest.mark.parametrize(
    "field",
    [
        "width",
        "depth",
        "moment",
        "shear",
        "fck",
        "fy",
        "clear_cover",
        "stirrup_dia_mm",
        "main_bar_dia_mm",
    ],
)
def test_v1_beam_requires_every_calculation_bearing_field(
    client, ordinary_payload, field
) -> None:
    payload = dict(ordinary_payload)
    del payload[field]

    response = client.post("/api/v1/design/beam", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert field in str(response.json()["error"]["details"])


@pytest.mark.parametrize(
    "field,value",
    [
        ("width", "300"),
        ("moment", True),
        ("include_serviceability", "false"),
    ],
)
def test_v1_beam_rejects_coerced_numeric_and_boolean_values(
    client, ordinary_payload, field, value
) -> None:
    response = client.post(
        "/api/v1/design/beam", json={**ordinary_payload, field: value}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    details = response.json()["error"]["details"]
    assert any(item["loc"][-1] == field for item in details)


def test_v1_beam_rejects_unknown_engineering_fields(client, ordinary_payload) -> None:
    response = client.post(
        "/api/v1/design/beam",
        json={**ordinary_payload, "unexpected_engineering_field": 999},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    details = response.json()["error"]["details"]
    assert details[0]["type"] == "extra_forbidden"
    assert details[0]["loc"][-1] == "unexpected_engineering_field"


def test_v1_beam_rejects_unconsumed_reinforcement_layers(
    client, ordinary_payload
) -> None:
    response = client.post(
        "/api/v1/design/beam",
        json={
            **ordinary_payload,
            "rebar_layers": [{"layer": 1, "bar_count": 3, "bar_dia_mm": 20.0}],
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert "REBAR_LAYERS_SCOPE_HOLD" in str(response.json()["error"]["details"])


def test_v1_beam_accepts_ordinary_integers_and_complete_derivation_basis(
    client,
) -> None:
    response = client.post(
        "/api/v1/design/beam",
        json={
            "width": 300,
            "depth": 500,
            "moment": 150,
            "shear": 75,
            "fck": 25,
            "fy": 500,
            "clear_cover": 25,
            "stirrup_dia_mm": 8,
            "main_bar_dia_mm": 20,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    data = unwrap(response)
    assert data["effective_depth_used"] == pytest.approx(457.0)
    assert data["effective_depth_basis"]["source"] == "DERIVED"


def test_zero_torsion_preserves_primary_route_contract(
    client, ordinary_payload
) -> None:
    implicit = unwrap(client.post("/api/v1/design/beam", json=ordinary_payload))
    explicit = unwrap(
        client.post("/api/v1/design/beam", json={**ordinary_payload, "torsion": 0.0})
    )

    for field in ("success", "flexure", "shear", "ast_total", "asc_total"):
        assert explicit[field] == implicit[field]
    assert explicit["combined_actions"] is None
    assert explicit["torsion"] is None
    assert explicit["holds"] == []
    assert not any("Closed stirrups" in item for item in explicit["warnings"])
    assert explicit["effective_depth_used"] == 457.0
    assert explicit["effective_depth_basis"]["source"] == "DERIVED"
    assert explicit["result_envelope"]["engineering_status"] == "PASS"


def test_safe_torsion_is_integrated_into_primary_demands(
    client, ordinary_payload
) -> None:
    zero = unwrap(client.post("/api/v1/design/beam", json=ordinary_payload))
    response = client.post(
        "/api/v1/design/beam", json={**ordinary_payload, "torsion": 10.0}
    )

    assert response.status_code == status.HTTP_200_OK
    data = unwrap(response)
    assert data["success"] is True
    assert data["combined_actions"] == pytest.approx(
        {
            "mu_knm": 150.0,
            "vu_kn": 75.0,
            "tu_knm": 10.0,
            "me_knm": 165.68627450980392,
            "ve_kn": 128.33333333333334,
        }
    )
    assert data["ast_total"] > zero["ast_total"]
    assert data["shear"]["tau_v"] == pytest.approx(
        data["combined_actions"]["ve_kn"] * 1000 / (300.0 * 457.0)
    )
    assert data["shear"]["asv_required"] == data["torsion"]["asv_total"]
    assert data["torsion"]["requires_closed_stirrups"] is True
    assert data["torsion"]["source"] == "IS 456:2000"
    assert data["torsion"]["al_torsion"] > 0
    assert data["torsion"]["clause_refs"]["Me"] == "IS 456 Cl 41.4.2"
    assert data["evidence"]["support_status"] == "SUPPORTED"
    assert data["evidence"]["artifact_schema_version"] == "3.1"
    assert (
        data["evidence"]["normalized_input_hash"]
        != zero["evidence"]["normalized_input_hash"]
    )
    assert data["holds"] == []


def test_unsafe_torsion_fails_primary_result(client) -> None:
    response = client.post(
        "/api/v1/design/beam",
        json={
            "width": 200.0,
            "depth": 400.0,
            "effective_depth": 350.0,
            "moment": 300.0,
            "shear": 200.0,
            "torsion": 100.0,
            "fck": 20.0,
            "fy": 500.0,
            "clear_cover": 40.0,
            "stirrup_dia_mm": 8.0,
            "main_bar_dia_mm": 20.0,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True
    data = unwrap(response)
    assert data["success"] is False
    assert data["result_envelope"]["engineering_status"] == "FAIL"
    assert data["result_envelope"]["overall_status"] == "FAIL"
    assert data["evidence"]["status"] == "FAIL"
    assert data["evidence"]["exact_utilization"] is None
    assert data["evidence"]["utilization_disposition"] == "UNBOUNDED_FAILURE"
    assert data["torsion"]["is_safe"] is False
    assert any(error["code"] == "E_TORSION_001" for error in data["torsion"]["errors"])


def test_out_of_scope_primary_torsion_is_an_explicit_hold(
    client, ordinary_payload
) -> None:
    response = client.post(
        "/api/v1/design/beam",
        json={**ordinary_payload, "torsion": 10.0, "fck": 50.0},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "TORSION_SCOPE_HOLD" in str(response.json()["error"]["details"])


def test_serviceability_true_forwards_and_false_opts_out(
    client, ordinary_payload
) -> None:
    serviceability = {
        "span_mm": 5000.0,
        "support_condition": "simply_supported",
        "crack_width_params": {
            "exposure_class": "moderate",
            "acr_mm": 40.0,
            "cmin_mm": 25.0,
            "h_mm": 500.0,
            "x_mm": 150.0,
            "fs_service_nmm2": 180.0,
        },
    }
    enabled = unwrap(
        client.post(
            "/api/v1/design/beam",
            json={
                **ordinary_payload,
                **serviceability,
                "include_serviceability": True,
            },
        )
    )
    disabled = unwrap(
        client.post(
            "/api/v1/design/beam",
            json={
                **ordinary_payload,
                **serviceability,
                "include_serviceability": False,
            },
        )
    )

    assert enabled["deflection_check"]["is_ok"] is True
    assert enabled["crack_width_check"]["is_ok"] is True
    assert enabled["evidence"]["support_status"] == "SUPPORTED"
    assert (
        enabled["evidence"]["normalized_input_hash"]
        != disabled["evidence"]["normalized_input_hash"]
    )
    assert enabled["holds"] == []
    assert disabled["deflection_check"] is None
    assert disabled["crack_width_check"] is None
    assert disabled["evidence"] is not None


def test_unsupported_serviceability_exposure_is_rejected(
    client, ordinary_payload
) -> None:
    response = client.post(
        "/api/v1/design/beam",
        json={
            **ordinary_payload,
            "include_serviceability": True,
            "span_mm": 5000.0,
            "support_condition": "simply_supported",
            "crack_width_params": {
                "exposure_class": "extreme",
                "acr_mm": 40.0,
                "cmin_mm": 25.0,
                "h_mm": 500.0,
                "x_mm": 150.0,
                "fs_service_nmm2": 180.0,
            },
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert "exposure_class" in str(response.json()["error"]["details"])


def test_combined_report_binds_current_identity_and_exports_governing_results(
    client, ordinary_payload
) -> None:
    design = unwrap(
        client.post(
            "/api/v1/design/beam",
            json={**ordinary_payload, "torsion": 10.0},
        )
    )
    payload = {
        **ordinary_payload,
        "beam_id": "B-TORSION",
        "torsion": 10.0,
        "calculation_identity": design["evidence"]["calculation_identity"],
        "format": "json",
    }

    response = client.post("/api/v1/export/report", json=payload)
    assert response.status_code == status.HTTP_200_OK
    report = response.json()
    assert report["evidence"]["calculation_identity"] == payload["calculation_identity"]
    assert report["summary"]["combined_actions"]["tu_knm"] == 10.0
    assert report["summary"]["torsion"]["requires_closed_stirrups"] is True
    assert report["summary"]["torsion"]["asv_total_mm2_per_mm"] > 0


def test_stale_report_and_combined_bbs_dxf_fail_closed(
    client, ordinary_payload
) -> None:
    stale = client.post(
        "/api/v1/export/report",
        json={
            **ordinary_payload,
            "beam_id": "B-STALE",
            "calculation_identity": "0" * 64,
            "format": "json",
        },
    )
    assert stale.status_code == status.HTTP_409_CONFLICT
    assert "STALE_CALCULATION_IDENTITY" in str(stale.json()["error"])

    export_payload = {
        "beam_id": "B-COMBINED",
        "width": ordinary_payload["width"],
        "depth": ordinary_payload["depth"],
        "span_length": 5000.0,
        "clear_cover": ordinary_payload["clear_cover"],
        "fck": ordinary_payload["fck"],
        "fy": ordinary_payload["fy"],
        "ast_required": 900.0,
        "moment": ordinary_payload["moment"],
        "shear": ordinary_payload["shear"],
        "torsion": 10.0,
    }
    for endpoint in ("bbs", "dxf"):
        blocked = client.post(f"/api/v1/export/{endpoint}", json=export_payload)
        assert blocked.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "EXPORT_SCOPE_HOLD" in str(blocked.json())


@pytest.mark.parametrize(
    "serviceability",
    [
        {"include_serviceability": True},
        {
            "include_serviceability": True,
            "span_mm": 5000.0,
            "support_condition": "unsupported",
        },
    ],
)
def test_serviceability_missing_or_invalid_inputs_are_explicit(
    client, ordinary_payload, serviceability
) -> None:
    response = client.post(
        "/api/v1/design/beam", json={**ordinary_payload, **serviceability}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["error"]["code"] == "REQUEST_VALIDATION_ERROR"


def test_primary_shear_quantity_is_asv_per_spacing(client, ordinary_payload) -> None:
    data = unwrap(client.post("/api/v1/design/beam", json=ordinary_payload))
    shear = data["shear"]
    expected = (
        (shear["tau_v"] - shear["tau_c"])
        * ordinary_payload["width"]
        / (0.87 * ordinary_payload["fy"])
    )

    assert shear["asv_required"] == pytest.approx(expected)
    assert shear["asv_required"] == pytest.approx(0.010375739761108373)
    assert shear["asv_required_unit"] == "mm²/mm"


def test_depth_boundary_matches_the_canonical_failure_vector(client) -> None:
    response = client.post(
        "/api/v1/design/beam",
        json={
            "width": 300.0,
            "depth": 500.0,
            "clear_cover": 40.0,
            "stirrup_dia_mm": 8.0,
            "main_bar_dia_mm": 18.0,
            "moment": 150.0,
            "shear": 420.0,
            "fck": 25.0,
            "fy": 500.0,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True
    data = unwrap(response)
    assert data["effective_depth_used"] == 443.0
    assert data["effective_depth_basis"]["source"] == "DERIVED"
    assert data["success"] is False
    assert data["utilization_ratio"] == pytest.approx(1.01944, rel=1e-4)
    assert data["result_envelope"]["engineering_status"] == "FAIL"
    direct = design_beam_is456(
        units="IS456",
        case_id="CASE-1",
        b_mm=300.0,
        D_mm=500.0,
        d_mm=None,
        effective_depth_basis=EffectiveDepthBasisV1(40.0, 8.0, 18.0),
        d_dash_mm=57.0,
        mu_knm=150.0,
        vu_kn=420.0,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
        cover_mm=40.0,
        stirrup_dia_mm=8.0,
    )
    assert data["result_envelope"] == direct.result_envelope


def test_explicit_effective_depth_is_not_combined_with_adapter_basis(client) -> None:
    response = client.post(
        "/api/v1/design/beam",
        json={
            "width": 300.0,
            "depth": 500.0,
            "effective_depth": 450.0,
            "clear_cover": 40.0,
            "stirrup_dia_mm": 8.0,
            "main_bar_dia_mm": 18.0,
            "moment": 100.0,
            "shear": 75.0,
            "fck": 25.0,
            "fy": 500.0,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    resolution = unwrap(response)["effective_depth_basis"]
    assert resolution["source"] == "EXPLICIT"
    assert resolution["d_mm"] == 450.0
    assert resolution["effective_depth_basis"] is None


def test_separate_torsion_endpoint_contract_is_unchanged(client) -> None:
    response = client.post(
        "/api/v1/design/beam/torsion",
        json={
            "width": 300.0,
            "depth": 500.0,
            "torsion": 10.0,
            "moment": 150.0,
            "shear": 100.0,
            "fck": 25.0,
            "fy": 500.0,
            "clear_cover": 40.0,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    data = unwrap(response)
    assert set(data) == {
        "success",
        "message",
        "tu_knm",
        "vu_kn",
        "mu_knm",
        "ve_kn",
        "me_knm",
        "tv_equiv",
        "tc",
        "tc_max",
        "asv_torsion",
        "asv_shear",
        "asv_total",
        "stirrup_spacing",
        "al_torsion",
        "is_safe",
        "requires_closed_stirrups",
        "warnings",
    }
