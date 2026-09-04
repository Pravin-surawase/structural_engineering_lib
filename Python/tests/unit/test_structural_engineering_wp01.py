import hashlib
import math

import pytest

from structural_lib.beam import (
    BarPosition,
    Face,
    FlexuralCapacityRequest,
    FlexureCheckRequest,
    ReinforcementGeometryRequest,
    SectionKind,
    bar_area,
    check_flexure,
    effective_depth,
    evaluate_geometry,
    flexural_capacity,
    mass_per_length,
)
from structural_lib.beam.semantics import canonical_json_bytes


def _bars() -> tuple[BarPosition, ...]:
    return (
        BarPosition("T1", 16, 75, 42, Face.TOP),
        BarPosition("T2", 16, 225, 42, Face.TOP),
        BarPosition("B1", 20, 65, 450, Face.BOTTOM),
        BarPosition("B2", 20, 150, 450, Face.BOTTOM),
        BarPosition("B3", 20, 235, 450, Face.BOTTOM),
    )


def _geometry(
    bars: tuple[BarPosition, ...] | None = None,
) -> ReinforcementGeometryRequest:
    return ReinforcementGeometryRequest(
        "IS456-WP01", 300, 500, 25, 8, 25, bars or _bars()
    )


def _capacity(
    section: SectionKind = SectionKind.RECTANGULAR, **changes: object
) -> FlexuralCapacityRequest:
    values: dict[str, object] = {
        "profile_id": "IS456-WP01",
        "section_kind": section,
        "web_width_mm": 300,
        "depth_mm": 500,
        "concrete_strength_n_per_mm2": 25,
        "steel_yield_strength_n_per_mm2": 415,
        "bars": _bars(),
        "tension_face": Face.BOTTOM,
        "flange_width_mm": 800 if section is not SectionKind.RECTANGULAR else None,
        "flange_thickness_mm": 100 if section is not SectionKind.RECTANGULAR else None,
    }
    values.update(changes)
    return FlexuralCapacityRequest(**values)  # type: ignore[arg-type]


def test_canonical_bytes_are_sorted_finite_and_stable() -> None:
    value = {"z": 16.0, "a": [1.25, -0.0], "face": Face.BOTTOM}
    expected = b'{"a":[1.25,0],"face":"bottom","z":16}'
    assert canonical_json_bytes(value) == expected
    assert hashlib.sha256(expected).hexdigest() == (
        "4c31e47356c8c9c60fc679f4e07ab31094749fbd68e66d20a7d2b4604a0337ae"
    )


def test_foundation_values_retain_effective_inputs_units_and_identity() -> None:
    area = bar_area(16)
    mass = mass_per_length(16, 7850)
    assert area.outputs["area_mm2"] == math.pi * 16**2 / 4
    assert mass.outputs["mass_kg_per_m"] == area.outputs["area_mm2"] * 7850 / 1e6
    assert mass.effective_inputs["density_kg_per_m3"]["value"] == 7850
    assert area.normalized_input_id.startswith(
        "normalized_input_id:pf4-canonical-json-v1:"
    )
    assert bar_area(16).calculation_id == area.calculation_id


def test_invalid_foundation_value_is_rejected_input() -> None:
    result = bar_area(0)
    assert result.execution == "rejected_input"
    assert result.engineering == "not_evaluated"
    assert result.diagnostics[0].code == "INPUT.RANGE"


def test_geometry_uses_actual_multilayer_coordinates_and_reports_spacing() -> None:
    bars = _bars() + (
        BarPosition("B4", 16, 110, 405, Face.BOTTOM, layer=2),
        BarPosition("B5", 16, 190, 405, Face.BOTTOM, layer=2),
    )
    result = evaluate_geometry(_geometry(bars))
    bottom = result.outputs["faces"]["bottom"]
    expected_y = sum(
        math.pi * bar.diameter_mm**2 / 4 * bar.y_from_top_mm
        for bar in bars
        if bar.face is Face.BOTTOM
    ) / sum(
        math.pi * bar.diameter_mm**2 / 4 for bar in bars if bar.face is Face.BOTTOM
    )
    assert bottom["effective_depth_mm"] == expected_y
    assert result.outputs["bar_count"] == 7
    assert result.engineering == "pass"
    depth = effective_depth(_geometry(bars), Face.BOTTOM)
    assert depth.outputs["bar_ids"] == ["B1", "B2", "B3", "B4", "B5"]


def test_geometry_overlap_is_an_engineering_failure() -> None:
    bars = (
        BarPosition("B1", 20, 100, 450, Face.BOTTOM),
        BarPosition("B2", 20, 110, 450, Face.BOTTOM),
    )
    result = evaluate_geometry(_geometry(bars))
    assert result.execution == "completed"
    assert result.engineering == "fail"
    assert any(item.code == "GEOMETRY.SPACING" for item in result.diagnostics)


def test_rectangular_singly_and_doubly_reinforced_capacity() -> None:
    singly = flexural_capacity(
        _capacity(bars=tuple(bar for bar in _bars() if bar.face is Face.BOTTOM))
    )
    doubly = flexural_capacity(_capacity())
    assert singly.engineering == "pass"
    assert doubly.engineering == "pass"
    assert doubly.outputs["compression_steel_area_mm2"] > 0
    assert doubly.outputs["capacity_knm"] > singly.outputs["capacity_knm"]


def test_independent_rectangular_capacity_vector() -> None:
    bars = (
        BarPosition("B1", 20, 80, 450, Face.BOTTOM),
        BarPosition("B2", 20, 220, 450, Face.BOTTOM),
    )
    result = flexural_capacity(_capacity(bars=bars))
    assert result.outputs["capacity_knm"] == pytest.approx(94.07913916844615)
    assert result.outputs["equilibrium_neutral_axis_depth_mm"] == pytest.approx(
        84.02015019100702
    )


def test_flanged_positive_uses_flange_and_negative_uses_web() -> None:
    request = _capacity(SectionKind.T_BEAM)
    positive = flexural_capacity(request)
    negative = flexural_capacity(
        FlexuralCapacityRequest(**{**request.__dict__, "tension_face": Face.TOP})
    )
    assert positive.outputs["uses_compression_flange"] is True
    assert negative.outputs["uses_compression_flange"] is False
    assert positive.outputs["capacity_knm"] > negative.outputs["capacity_knm"]


def test_flexure_checks_both_signs_against_physical_faces() -> None:
    result = check_flexure(FlexureCheckRequest(_capacity(), 100, -50))
    assert result.execution == "completed"
    assert [check["tension_face"] for check in result.outputs["checks"]] == [
        "bottom",
        "top",
    ]
    assert result.outputs["governing_utilization"] > 0


def test_axial_interaction_is_explicitly_not_applicable() -> None:
    result = flexural_capacity(_capacity(axial_force_kn=10))
    assert result.execution == "completed"
    assert result.applicability == "not_applicable"
    assert result.completeness == "complete_for_scope"
    assert result.engineering == "not_evaluated"
    assert result.diagnostics[0].code == "PROFILE.UNSUPPORTED"
