"""Physical section checks against separately generated source-derived vectors."""

import json
from pathlib import Path

import pytest

from structural_lib import beam as b

REFERENCE = json.loads(
    (
        Path(__file__).resolve().parents[3]
        / "contracts/structural-engineering/conformance/wp01-per-bar-vectors.json"
    ).read_text(encoding="utf-8")
)


@pytest.mark.parametrize("vector", REFERENCE["vectors"], ids=lambda v: v["id"])
def test_per_bar_section_matches_independent_reference(vector):
    data = dict(vector["input"])
    data["section_kind"] = b.SectionKind(data["section_kind"])
    data["tension_face"] = b.Face(data["tension_face"])
    data["bars"] = tuple(
        b.BarPosition(**{**bar, "face": b.Face(bar["face"])}) for bar in data["bars"]
    )
    request = b.FlexuralCapacityRequest(**data)
    result = b.flexural_capacity(request)
    expected, actual = vector["expected"], result.outputs
    assert result.execution == "completed"
    assert result.engineering == expected["engineering"]
    assert result.provenance.method_revision_id == "is456-flexural-capacity-wp01-v3"
    assert actual["equilibrium_neutral_axis_depth_mm"] == pytest.approx(
        expected["neutral_axis_depth_mm"], abs=1e-7, rel=0
    )
    assert actual["capacity_knm"] == pytest.approx(
        expected["capacity_knm"], abs=1e-7, rel=0
    )
    assert abs(actual["force_residual_n"]) < 1e-6
    assert (
        actual["capacity_neutral_axis_depth_mm"]
        == actual["equilibrium_neutral_axis_depth_mm"]
    )
    assert actual["maximum_tension_strain"] == pytest.approx(
        expected["maximum_tension_strain"], abs=1e-12
    )
    assert actual["minimum_tension_strain"] == expected["minimum_tension_strain"]
    assert len(actual["bar_responses"]) == len(expected["bar_responses"])
    for bar, reference in zip(
        actual["bar_responses"], expected["bar_responses"], strict=True
    ):
        assert bar["bar_id"] == reference["bar_id"]
        for field in (
            "depth_from_compression_face_mm",
            "area_mm2",
            "strain",
            "steel_stress_n_per_mm2",
            "displaced_concrete_stress_n_per_mm2",
            "net_force_n",
        ):
            assert bar[field] == pytest.approx(reference[field], abs=1e-6, rel=0), field
    if result.engineering == "fail":
        # A low demand cannot turn insufficient ductility into an acceptable beam.
        demands = (
            {"positive_design_moment_knm": 1}
            if request.tension_face is b.Face.BOTTOM
            else {"negative_design_moment_knm": -1}
        )
        assert (
            b.check_flexure(b.FlexureCheckRequest(request, **demands)).engineering
            == "fail"
        )


def test_reference_exercises_mixed_stress_ranges_and_reversed_bar_stress():
    by_id = {v["id"]: v for v in REFERENCE["vectors"]}
    rows = {
        row["bar_id"]: row
        for row in by_id["fe415-bottom25-bottom"]["expected"]["bar_responses"]
    }
    assert (
        rows["B3"]["steel_stress_n_per_mm2"] > -415 / 1.15
    )  # inner tension steel below plateau
    assert rows["B1"]["steel_stress_n_per_mm2"] == -415 / 1.15
    assert rows["T1"]["strain"] > 0.002
    assert rows["T3"]["strain"] < 0.8 * (415 / 1.15) / 200000
    assert any(
        row["bar_id"].startswith("T") and row["steel_stress_n_per_mm2"] < 0
        for vector in REFERENCE["vectors"]
        if vector["input"]["tension_face"] == "bottom"
        for row in vector["expected"]["bar_responses"]
    )
    comparison = REFERENCE["design_block_comparison"]
    assert -0.3 < comparison["difference_percent"] < 0
