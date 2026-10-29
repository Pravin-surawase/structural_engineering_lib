"""S3 calculation quantities and admission semantics across maintained wires."""

import json
from dataclasses import replace

import pytest
from jsonschema import Draft202012Validator

from fastapi_app.beam_projection import project_beam_design_result
from fastapi_app.routers.websocket import beam_design_websocket_schema_v1
from fastapi_app.tests.conftest import unwrap
from fastapi_app.tests.test_websocket import _design_params, _ws_path
from structural_lib.services.batch import design_project_beams_v1
from structural_lib.services.beam_api import design_beam_is456


@pytest.mark.parametrize(
    "moment,shear,status", [(150, 75, "PASS"), (150, 300, "FAIL"), (2000, 75, "FAIL")]
)
def test_http_websocket_share_actual_quantities_depth_status_and_identity(
    client, moment, shear, status
):
    params = _design_params(cover=25, moment=moment, shear=shear)
    http_params = {**params, "clear_cover": params["cover"]}
    del http_params["cover"]
    http = unwrap(client.post("/api/v1/design/beam", json=http_params))
    with client.websocket_connect(_ws_path("s3-parity")) as ws:
        ws.send_json({"type": "design_beam", "params": params})
        message = ws.receive_json()
    assert message["type"] == "design_result"
    schema = beam_design_websocket_schema_v1()
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(message)
    actual = message["data"]
    for name in (
        "flexure",
        "shear",
        "result_envelope",
        "effective_depth_basis",
        "governing_utilization",
        "unavailable_utilizations",
    ):
        assert actual[name] == http[name]
    assert actual["result_envelope"]["engineering_status"] == status
    assert (
        actual["evidence"]["calculation_identity"]
        == http["evidence"]["calculation_identity"]
    )
    assert actual["shear"]["asv_required_unit"] == "mm²/mm"
    if moment == 150 and shear == 75:
        assert actual["shear"]["asv_required"] == pytest.approx(0.01037573975765039)
    if moment == 2000:
        assert actual["governing_utilization"] is None
        assert actual["unavailable_utilizations"]
    json.dumps(actual, allow_nan=False)


def test_uncapped_finite_quantity_is_preserved_by_compatibility_projection():
    result = design_beam_is456(
        units="IS456",
        b_mm=300,
        D_mm=500,
        d_mm=450,
        mu_knm=150,
        vu_kn=75,
        fck_nmm2=25,
        fy_nmm2=500,
    )
    result = replace(result, governing_utilization=3.25)
    response = project_beam_design_result(result, evidence_inputs=result.design_inputs)
    assert response.utilization_ratio == 2.0
    assert response.governing_utilization == 3.25


@pytest.mark.parametrize(
    "update",
    [
        {"torsion": 100},
        {"effective_depth": 200},
        {"moment": True},
        {"cover": 25, "clear_cover": 40},
    ],
)
def test_ws_rejects_inputs_that_would_change_or_corrupt_the_basis(client, update):
    with client.websocket_connect(_ws_path("s3-invalid")) as ws:
        ws.send_json({"type": "design_beam", "params": _design_params(**update)})
        error = ws.receive_json()
        assert error["type"] == "error"
        assert error["error"]["code"] == "INPUT_CONTRACT_INVALID"
        ws.send_json({"type": "ping"})
        assert ws.receive_json()["type"] == "pong"


@pytest.mark.parametrize(
    "raw,code",
    [
        (
            '{"type":"design_beam","params":{"moment":150,"moment":100}}',
            "DUPLICATE_JSON_KEY",
        ),
        ('{"type":"design_beam","params":{"moment":NaN}}', "INPUT_NOT_FINITE"),
        ("[]", "INPUT_TYPE_INVALID"),
        ("{", "INPUT_JSON_INVALID"),
    ],
)
def test_invalid_json_does_not_discard_actions_or_break_the_connection(
    client, raw, code
):
    with client.websocket_connect(_ws_path("s3-json")) as ws:
        ws.send_text(raw)
        error = ws.receive_json()
        assert error["type"] == "error"
        assert any(
            issue["code"] == code for issue in error["error"]["details"]["issues"]
        )
        ws.send_json({"type": "ping"})
        assert ws.receive_json()["type"] == "pong"


def test_ws_legacy_numeric_strings_and_cover_alias_are_declared_and_supported(client):
    params = {k: str(v) for k, v in _design_params().items()}
    params["clear_cover"] = params.pop("cover")
    params["length"] = "4000"
    message = {"type": "design_beam", "params": params}
    Draft202012Validator(beam_design_websocket_schema_v1()).validate(message)
    with client.websocket_connect(_ws_path("s3-alias")) as ws:
        ws.send_json(message)
        assert ws.receive_json()["type"] == "design_result"


def test_overloaded_batch_is_strict_json_on_service_stream_and_polling(client):
    beam = dict(
        schema_version="project-beam-design/v1",
        member_id="B1",
        b_mm=300,
        D_mm=500,
        d_mm=450,
        mu_knm=2000,
        vu_kn=75,
        fck_nmm2=25,
        fy_nmm2=500,
    )
    result = design_project_beams_v1([beam], units="IS456").to_dict()
    json.dumps(result, allow_nan=False)
    calculation = result["members"][0]["calculation"]
    assert calculation["utilization_ratio"] is None
    assert calculation["unavailable_utilizations"]
    response = client.post("/stream/batch-design", json=[beam])
    data_lines = [
        line[5:].strip()
        for line in response.text.splitlines()
        if line.startswith("data:")
    ]
    events = [
        json.loads(
            line,
            parse_constant=lambda value: pytest.fail(f"Invalid JSON constant {value}"),
        )
        for line in data_lines
    ]
    member = next(event for event in events if event.get("beam_id") == "B1")
    assert member["status"] == "FAIL"
    assert member["governing_utilization"] is None
    job_id = next(event["job_id"] for event in events if "job_id" in event)
    polling = client.get(f"/stream/job/{job_id}")
    assert polling.status_code == 200
    json.dumps(polling.json(), allow_nan=False)


def test_dashboard_preserves_unknown_and_observed_uncapped_ratios(client):
    endpoint = "/api/v1/insights/dashboard"
    missing = unwrap(
        client.post(
            endpoint,
            json={
                "results": [{"beam_id": "B1", "is_valid": False, "utilization": None}]
            },
        )
    )
    assert missing["failed"] == 1
    assert missing["avg_utilization"] is None
    observed = unwrap(
        client.post(
            endpoint,
            json={
                "results": [
                    {"beam_id": "B1", "is_valid": False, "utilization": None},
                    {"beam_id": "B2", "utilization": 3.25},
                ]
            },
        )
    )
    assert observed["avg_utilization"] == observed["max_utilization"] == 3.25
    zero = unwrap(
        client.post(
            endpoint,
            json={
                "results": [
                    {"beam_id": "B1", "utilization": 0},
                    {"beam_id": "B2", "utilization": 1},
                ]
            },
        )
    )
    assert zero["avg_utilization"] == 0.5
    assert zero["min_utilization"] == 0
