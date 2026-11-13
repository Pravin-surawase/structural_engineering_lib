"""Compare signed fixed-compression rays and section properties."""

import json
from pathlib import Path

import pytest

from structural_lib.design.is456 import column

REFERENCE = json.loads(
    (
        Path(__file__).resolve().parents[3]
        / "docs/verification/library-029-sec02-column-interaction.json"
    ).read_text(encoding="utf-8")
)
CASES = REFERENCE["cases"]


@pytest.mark.parametrize("case", ("rectangle", "circle"))
def test_interaction_rays_and_properties(case):
    fixture = CASES[case]
    request = column.load_interaction_slice(json.dumps(fixture["request"]))
    result = column.check_interaction_slice(request)
    assert result.engineering_status.value == "PASS"
    assert result.calculation["member_acceptance"] == "NOT_EVALUATED"
    assert result.calculation["detailing_acceptance"] == "NOT_EVALUATED"
    for kind in ("gross", "transformed"):
        assert result.calculation[kind] == pytest.approx(
            fixture["properties"][kind], abs=1e-6
        )
    dense = column.check_interaction_slice(
        request.model_copy(update={"point_count": 16})
    )
    assert dense.engineering_status.value == "PASS"
    assert result.calculation["rays"] == dense.calculation["rays"][::2]
    tolerance = REFERENCE["tolerances"]
    for actual, expected in zip(
        result.calculation["rays"], fixture["rays"], strict=True
    ):
        assert actual["angle_deg"] == expected["angle_deg"]
        delta = (actual["normal_deg"] - expected["normal_deg"] + 180) % 360 - 180
        assert abs(delta) <= tolerance["angle_deg"]
        assert actual["xu_mm"] == pytest.approx(
            expected["xu_mm"], abs=tolerance["axis_mm"]
        )
        assert actual["p_kn"] == pytest.approx(request.pu_kn, abs=tolerance["axial_kn"])
        assert abs(actual["transverse_residual_knm"]) < 1e-7
        for field in ("mx_knm", "my_knm", "capacity_knm"):
            assert actual[field] == pytest.approx(
                expected[field], abs=tolerance["moment_knm"]
            )
    identity = result.to_dict()["envelope"]["result_identity"]["input_hash"]
    assert identity in column.render_interaction_slice_html(result)
    json.dumps(result.to_dict(), allow_nan=False)


def test_unresolved_compression_withholds_interaction_diagram():
    result = column.check_interaction_slice(
        column.load_interaction_slice(CASES["above_compression_domain"]["request"])
    )
    assert result.engineering_status.value == "HOLD"
    assert result.calculation["rays"] == []
    assert result.calculation["gross"]["area_mm2"] == 120000
    assert result.issues[0].code == "COLUMN.INTERACTION_DOMAIN_HELD"
