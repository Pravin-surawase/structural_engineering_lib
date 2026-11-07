"""Replay the frozen Packet D station correction through the public operation."""

import json
from dataclasses import replace
from pathlib import Path

import pytest

from structural_lib import beam

REFERENCE = json.loads(
    (
        Path(__file__).resolve().parents[3]
        / "docs/verification/library-027-torsion-station.json"
    ).read_text(encoding="utf-8")
)


def request(case):
    data = case["inputs"]
    bars = tuple(
        beam.BarPosition(name, data["longitudinal_diameter_mm"], x, y, face)
        for name, x, y, face in (
            ("TL", 50, 50, beam.Face.TOP),
            ("TR", 250, 50, beam.Face.TOP),
            ("BL", 50, 350, beam.Face.BOTTOM),
            ("BR", 250, 350, beam.Face.BOTTOM),
        )
    )
    links = data["link"]
    return beam.TorsionCheckRequest(
        "LIB-027-D-STATION",
        beam.ConcurrentActionRow(
            "ULS-1",
            "interior",
            beam.ActionBasis.STATIC_CONCURRENT,
            data["v2_kn"],
            0,
            data["torsion_knm"],
            0,
            data["m3_knm"],
            "independent-static-row",
        ),
        beam.FlexuralCapacityRequest(
            "LIB-027-D-STATION",
            beam.SectionKind.RECTANGULAR,
            data["b_mm"],
            data["D_mm"],
            25,
            415,
            bars,
            beam.Face.BOTTOM,
        ),
        beam.TransverseLink(
            "S8",
            links["diameter_mm"],
            2,
            2,
            links["spacing_mm"],
            415,
            True,
            links["centre_width_mm"],
            links["centre_depth_mm"],
        ),
        ("TL", "TR", "BL", "BR"),
    )


@pytest.mark.parametrize("case", REFERENCE["cases"], ids=lambda case: case["id"])
def test_station_uses_longitudinal_corner_centres(case):
    result = beam.check_torsion(request(case))
    assert result.engineering == case["engineering"]
    assert result.provenance.method_revision_id == "is456-torsion-check-wp02-v3"
    for field, expected in case["expected"].items():
        assert result.outputs[field] == pytest.approx(expected, abs=1e-9, rel=0)
    assert result.outputs["longitudinal_pass"] is True
    if case["engineering"] == "fail":
        assert result.outputs["transverse_pass"] is False
        assert {d.code for d in result.diagnostics} == {
            "TORSION.TRANSVERSE_REINFORCEMENT"
        }


def test_different_link_dimensions_do_not_change_the_corner_bar_equation():
    original = request(REFERENCE["cases"][0])
    changed = replace(
        original, link=replace(original.link, centre_width_mm=260, centre_depth_mm=360)
    )
    a, b = beam.check_torsion(original), beam.check_torsion(changed)
    assert (
        b.outputs["required_link_area_per_spacing_mm"]
        == a.outputs["required_link_area_per_spacing_mm"]
    )
    assert b.outputs["maximum_spacing_mm"] != a.outputs["maximum_spacing_mm"]


def test_unresolved_or_unaligned_corner_geometry_has_no_invented_capacity():
    original = request(REFERENCE["cases"][0])
    for changed in (
        replace(original, perimeter_bar_ids=("TL", "TR", "BL")),
        replace(
            original,
            flexural_capacity=replace(
                original.flexural_capacity,
                bars=tuple(
                    replace(bar, y_from_top_mm=60) if bar.bar_id == "TL" else bar
                    for bar in original.flexural_capacity.bars
                ),
            ),
        ),
    ):
        result = beam.check_torsion(changed)
        assert result.engineering == "not_evaluated"
        assert not result.outputs
        assert {d.code for d in result.diagnostics} == {
            "TORSION.CORNER_GEOMETRY_REQUIRED"
        }


@pytest.mark.parametrize("top_left_depth", (50, 60))
def test_zero_torsion_retains_the_existing_ordinary_check_method(top_left_depth):
    original = request(REFERENCE["cases"][0])
    result = beam.check_torsion(
        replace(
            original,
            action=replace(original.action, torsion_knm=0),
            flexural_capacity=replace(
                original.flexural_capacity,
                bars=tuple(
                    (
                        replace(bar, y_from_top_mm=top_left_depth)
                        if bar.bar_id == "TL"
                        else bar
                    )
                    for bar in original.flexural_capacity.bars
                ),
            ),
        )
    )
    assert result.engineering == "pass"
    assert result.provenance.method_revision_id == "is456-torsion-check-wp02-v2"
    assert "corner_width_mm" not in result.outputs
    assert result.outputs["equivalent_shear_kn"] == 60
    assert result.outputs["perimeter_pass"] is True


@pytest.mark.parametrize("moment", (15, -15))
def test_both_equivalent_bending_faces_use_the_same_concurrent_row(moment):
    original = request(REFERENCE["cases"][0])
    result = beam.check_torsion(
        replace(original, action=replace(original.action, m3_knm=moment))
    )
    assert result.engineering == "pass"
    assert result.outputs["primary_equivalent_moment_knm"] == pytest.approx(
        35.588235294117645
    )
    assert result.outputs["opposite_equivalent_moment_knm"] == pytest.approx(
        5.588235294117645
    )
