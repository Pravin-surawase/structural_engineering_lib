"""LIB-PRO-007-P6 REST parity for the frozen ETABS and gravity vectors."""

from __future__ import annotations

from fastapi_app.tests.conftest import unwrap
from structural_lib import (
    get_gravity_workflow_example_document_v1,
    get_gravity_workflow_example_request_v1,
    run_gravity_workflow_with_book_v1,
)
from structural_lib.services.batch import design_project_beams_v1

SNAPSHOT_SHA256 = "a82d927d347108f56aa3fcdd559c1aa45ba8d87673cb3feec61a03d5eadbf4f8"


def _p5_request(
    *,
    unique_name: str,
    source_member_id: str,
    D_mm: float,
    mu_knm: float,
    vu_kn: float,
) -> dict[str, object]:
    return {
        "schema_version": "project-beam-design/v1",
        "member_id": f"etabs:P5-TRIAL-HALL:{unique_name}",
        "b_mm": 300.0,
        "D_mm": D_mm,
        "mu_knm": mu_knm,
        "vu_kn": vu_kn,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
        "effective_depth_basis": {
            "clear_cover_mm": 40.0,
            "stirrup_diameter_mm": 8.0,
            "tension_bar_diameter_mm": 20.0,
        },
        "source_metadata": {
            "source_system": "ETABS_EXPORTED_FILES",
            "project_id": "P5-TRIAL-HALL",
            "export_id": "P5-EXPORT-001",
            "snapshot_sha256": SNAPSHOT_SHA256,
            "source_unique_name": unique_name,
            "source_member_id": source_member_id,
        },
    }


def _p5_requests() -> list[dict[str, object]]:
    return [
        _p5_request(
            unique_name="101",
            source_member_id="B1_L1",
            D_mm=500.0,
            mu_knm=150.0,
            vu_kn=75.0,
        ),
        _p5_request(
            unique_name="102",
            source_member_id="B2_L1",
            D_mm=550.0,
            mu_knm=130.0,
            vu_kn=65.0,
        ),
    ]


def test_p5_canonical_request_has_identical_python_and_rest_result_identity(
    client,
) -> None:
    requests = _p5_requests()
    python_members = [
        member.to_dict() for member in design_project_beams_v1(requests).members
    ]

    response = client.post("/api/v1/import/project-beams", json=requests)

    assert response.status_code == 200
    rest_members = unwrap(response)["members"]
    assert len(rest_members) == len(python_members) == 2
    for rest_member, python_member in zip(rest_members, python_members, strict=True):
        assert rest_member["input"] == python_member["input"]
        assert rest_member["overall_status"] == python_member["overall_status"]
        assert rest_member["issues"] == python_member["issues"]
        assert (
            rest_member["result_envelope"]["result_identity"]
            == python_member["result_envelope"]["result_identity"]
        )
        assert (
            rest_member["calculation"]["evidence"]["source_metadata"]["snapshot_sha256"]
            == SNAPSHOT_SHA256
        )


def test_maintained_gravity_example_has_identical_python_and_rest_identity(
    client,
) -> None:
    request = get_gravity_workflow_example_request_v1()
    python_bundle = run_gravity_workflow_with_book_v1(request).model_dump(mode="json")

    response = client.post(
        "/api/v1/building-gravity/v1/run",
        json=get_gravity_workflow_example_document_v1(),
    )

    assert response.status_code == 200
    rest_bundle = unwrap(response)
    python_workflow = python_bundle["workflow_result"]
    rest_workflow = rest_bundle["workflow_result"]
    assert (
        rest_workflow["workflow_result_hash"] == python_workflow["workflow_result_hash"]
    )
    assert (
        rest_workflow["result_envelope"]["overall_status"]
        == python_workflow["result_envelope"]["overall_status"]
    )
    assert (
        rest_workflow["result_envelope"]["issues"]
        == python_workflow["result_envelope"]["issues"]
    )
    assert (
        rest_bundle["calculation_book"]["workflow_result_hash"]
        == rest_workflow["workflow_result_hash"]
    )
