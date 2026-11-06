"""Public prescribed-column-section contract and independent case replay."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from structural_lib.design.is456 import column

ROOT = Path(__file__).resolve().parents[3]
REFERENCES = ROOT / "docs/verification"


@pytest.fixture
def section() -> dict:
    return {
        "b_mm": 230,
        "D_mm": 450,
        "xu_mm": 900,
        "fck_nmm2": 20,
        "fy_nmm2": 415,
        "layers": [
            {"depth_from_top_mm": 50, "count": 3, "diameter_mm": 16},
            {"depth_from_top_mm": 225, "count": 2, "diameter_mm": 16},
            {"depth_from_top_mm": 400, "count": 3, "diameter_mm": 16},
        ],
    }


def test_layered_section_example_replays_all_independent_targets(
    tmp_path: Path,
) -> None:
    example = ROOT / "Python/examples/layered_column_section.py"
    fixture = json.loads(
        (REFERENCES / "library-027-comparator-reference.json").read_text()
    )
    case = next(c for c in fixture["cases"] if c["id"] == "column_three_layers")
    boundary = json.loads(
        (REFERENCES / "library-027-column-section-boundary.json").read_text()
    )
    extension = json.loads(
        (REFERENCES / "library-027-column-section-extension.json").read_text()
    )
    completed = subprocess.run(
        [sys.executable, str(example)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    outcomes = json.loads(completed.stdout)
    assert outcomes.keys() == {
        "frozen_900mm",
        "full_depth_boundary",
        "partial_compression",
        "mixed_diameters",
    }
    for name, expected, tolerances in (
        (
            "frozen_900mm",
            case["expected"]["shared"],
            fixture["acceptance"]["absolute_tolerances"],
        ),
        ("full_depth_boundary", boundary["expected"], boundary["absolute_tolerances"]),
        *(
            (c["id"], c["expected"], extension["absolute_tolerances"])
            for c in extension["cases"]
        ),
    ):
        response = column.ColumnSectionResponseV1.model_validate_json(
            json.dumps(outcomes[name])
        )
        assert response.calculation_status == "COMPLETED"
        assert (
            response.member_acceptance
            == response.detailing_acceptance
            == "NOT_EVALUATED"
        )
        assert response.compression_face == "top"
        assert response.bending_axis == "centroidal_parallel_to_width"
        assert (
            response.method_revision_id
            == "IS456_FIG21_INTEGRATED_V1__STEEL_FIG23_GS115_V1"
        )
        for field, target in expected.items():
            actual = (
                response.request.xu_mm if field == "xu_mm" else getattr(response, field)
            )
            assert actual == pytest.approx(target, abs=tolerances[field], rel=0)
        assert response.axial_kn == pytest.approx(
            response.gross_concrete_axial_kn
            + sum(r.net_axial_kn for r in response.layers)
        )
        assert response.centroid_moment_knm == pytest.approx(
            response.gross_concrete_centroid_moment_knm
            + sum(r.centroid_moment_knm for r in response.layers)
        )
    assert outcomes["frozen_900mm"]["axial_kn"] > 1262.374193  # Comparator slice cap.
    for case in extension["cases"]:
        response = column.ColumnSectionResponseV1.model_validate_json(
            json.dumps(outcomes[case["id"]])
        )
        assert response.request == column.load_layered_section(case["inputs"])
        assert (
            column.load_layered_section(response.request.model_dump_json())
            == response.request
        )
        for group, expected in zip(
            response.layers, case["expected_groups"], strict=True
        ):
            for field, target in expected.items():
                assert getattr(group, field) == pytest.approx(
                    target, abs=extension["group_absolute_tolerances"][field], rel=0
                )


def test_layered_section_round_trips_and_approaches_full_depth_boundary(
    section,
) -> None:
    request = column.load_layered_section(section)
    assert column.load_layered_section(request.model_dump_json()) == request
    assert column.load_layered_section(request.model_dump_json().encode()) == request
    assert (
        column.ColumnSectionInputV1.model_json_schema()["additionalProperties"] is False
    )
    result = column.layered_section_response(request)
    assert (
        column.ColumnSectionResponseV1.model_validate_json(result.model_dump_json())
        == result
    )

    at = column.layered_section_response(
        column.load_layered_section({**section, "xu_mm": 450})
    )
    for delta in (-0.000001, 0.000001):
        near = column.layered_section_response(
            column.load_layered_section({**section, "xu_mm": 450 + delta})
        )
        assert near.far_face_strain * delta > 0
        assert near.axial_kn == pytest.approx(at.axial_kn, rel=0, abs=0.001)
        assert near.centroid_moment_knm == pytest.approx(
            at.centroid_moment_knm, rel=0, abs=0.001
        )


@pytest.mark.parametrize(
    ("changes", "code"),
    [
        ({"xu_mm": 0}, "INPUT_OUT_OF_RANGE"),
        ({"xu_mm": 5e-324}, "CROSS_FIELD_CONTRACT_INVALID"),
        ({"xu_mm": float("inf")}, "INPUT_NOT_FINITE"),
        ({"b_mm": 0}, "INPUT_OUT_OF_RANGE"),
        ({"fy_nmm2": 600}, "INPUT_OUT_OF_RANGE"),
        ({"layers": []}, "INPUT_CONTRACT_INVALID"),
        (
            {"layers": [{"depth_from_top_mm": 449, "count": 2, "diameter_mm": 16}]},
            "CROSS_FIELD_CONTRACT_INVALID",
        ),
        (
            {"layers": [{"depth_from_top_mm": 50, "count": 0, "diameter_mm": 16}]},
            "INPUT_OUT_OF_RANGE",
        ),
        (
            {"layers": [{"depth_from_top_mm": 50, "count": 2, "diameter_mm": 0}]},
            "INPUT_OUT_OF_RANGE",
        ),
        (
            {
                "layers": [
                    {"depth_from_top_mm": 50, "count": 8, "diameter_mm": 16},
                    {"depth_from_top_mm": 50, "count": 6, "diameter_mm": 20},
                ],
            },
            "CROSS_FIELD_CONTRACT_INVALID",
        ),
        (
            {"layers": [{"depth_from_top_mm": 50, "count": 15, "diameter_mm": 16}]},
            "CROSS_FIELD_CONTRACT_INVALID",
        ),
        ({"shape": "circular"}, "EXTRA_FIELD_FORBIDDEN"),
    ],
)
def test_layered_section_rejects_invalid_or_unsupported_inputs(
    section, changes, code
) -> None:
    with pytest.raises(column.InputContractError) as exc:
        column.load_layered_section({**section, **changes})
    assert code in {issue.code for issue in exc.value.issues}


def test_layered_section_loader_rejects_duplicate_json_and_untyped_calculation(
    section,
) -> None:
    with pytest.raises(column.InputContractError) as duplicate:
        column.load_layered_section('{"xu_mm":900,"xu_mm":450}')
    assert duplicate.value.issues[0].code == "DUPLICATE_JSON_KEY"
    with pytest.raises(column.InputContractError) as untyped:
        column.layered_section_response(section)
    assert untyped.value.issues[0].code == "INPUT_TYPE_INVALID"
