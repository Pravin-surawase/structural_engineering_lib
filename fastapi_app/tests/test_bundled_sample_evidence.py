"""Reproducible software evidence for the bundled 153-beam acceptance sample."""

from __future__ import annotations

import math

import pytest

from fastapi_app.tests.conftest import unwrap


def _provided_area(ast_required: float) -> float:
    """Mirror the current UI's declared standard-bar selection policy."""
    for diameter in (12, 16, 20, 25, 32):
        bar_area = math.pi * (diameter / 2) ** 2
        count = math.ceil(ast_required / bar_area)
        if 2 <= count <= 8:
            return count * bar_area
    bar_area = math.pi * (25 / 2) ** 2
    return max(2, math.ceil(ast_required / bar_area)) * bar_area


def test_bundled_sample_boq_is_bound_to_dataset_and_calculation(client) -> None:
    sample = unwrap(client.get("/api/v1/import/sample"))
    assert sample["beam_count"] == 153
    assert all(
        beam["source_metadata"]
        == {
            "dataset_id": "bundled-etabs-beam-sample",
            "dataset_version": "etabs-csv-v1",
            "dataset_sha256": sample["dataset"]["dataset_sha256"],
            "source_record_identity": beam["source_id"],
            "sample_only": True,
            "calculation_basis_origins": {
                "fck_mpa": "assumed_sample",
                "fy_mpa": "assumed_sample",
                "cover_mm": "assumed_sample",
            },
            "qualified_review_required": True,
        }
        for beam in sample["beams"]
    )

    batch_payload = [
        {
            "schema_version": "project-beam-design/v1",
            "member_id": beam["id"],
            "b_mm": beam["width_mm"],
            "D_mm": beam["depth_mm"],
            "d_mm": beam["depth_mm"] - beam["cover_mm"] - 25,
            "mu_knm": beam["mu_knm"],
            "vu_kn": beam["vu_kn"],
            "fck_nmm2": beam["fck_mpa"],
            "fy_nmm2": beam["fy_mpa"],
            "source_metadata": {
                **beam["source_metadata"],
                "source_member_id": beam["id"],
                "effective_depth_basis": "explicit sample fixture",
            },
        }
        for beam in sample["beams"]
    ]
    design = unwrap(client.post("/api/v1/import/project-beams", json=batch_payload))
    assert (
        design["summary"]["total"],
        design["summary"]["passed"],
        design["summary"]["failed"],
    ) == (153, 153, 0)
    results = {
        member["member_id"]: member["calculation"] for member in design["members"]
    }

    boq_beams = []
    for beam in sample["beams"]:
        provided_area = _provided_area(results[beam["id"]]["flexure"]["ast_required"])
        steel_weight = provided_area * beam["span_mm"] * 7850 / 1e9
        boq_beams.append(
            {
                "beam_id": beam["id"],
                "story": beam["story"],
                "b_mm": beam["width_mm"],
                "D_mm": beam["depth_mm"],
                "span_mm": beam["span_mm"],
                "fck": beam["fck_mpa"],
                "steel_weight_kg": steel_weight,
            }
        )

    dataset = {
        key: sample["dataset"][key]
        for key in ("dataset_id", "dataset_version", "dataset_sha256")
    }
    boq = unwrap(
        client.post(
            "/api/v1/insights/project-boq",
            json={
                "project_name": "Bundled ETABS sample",
                "beams": boq_beams,
                "dataset": dataset,
            },
        )
    )

    assert boq["grand_total_steel_kg"] == pytest.approx(1932.27)
    assert boq["grand_total_concrete_m3"] == pytest.approx(48.7319)
    assert boq["evidence"]["dataset_sha256"] == (
        "b95a056c411eeaf4c714713dcf7edfa402ceadb2efdcfd4382f454cc82c5f43e"
    )
    assert len(boq["evidence"]["calculation_identity"]) == 64
    assert boq["evidence"]["qualified_review_required"] is True
