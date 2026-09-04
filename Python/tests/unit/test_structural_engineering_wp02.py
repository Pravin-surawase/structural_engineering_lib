import pytest

from structural_lib.beam import (
    ActionBasis,
    BarPosition,
    ConcurrentActionRow,
    Face,
    FlexuralCapacityRequest,
    SectionKind,
    ShearAxis,
    ShearCapacityRequest,
    ShearCheckRequest,
    ShearDemand,
    TorsionCheckRequest,
    TransverseLink,
    check_shear,
    check_torsion,
    shear_capacity,
)


def _link(*, closed: bool = True, spacing_mm: float = 100) -> TransverseLink:
    return TransverseLink("L1", 8, 2, 2, spacing_mm, 415, closed, 230, 420)


def _capacity(
    axis: ShearAxis = ShearAxis.V2, link: TransverseLink | None = None
) -> ShearCapacityRequest:
    return ShearCapacityRequest(
        "IS456-WP02", axis, 300, 450, 25, 942.4777960769379, link or _link()
    )


def _bars() -> tuple[BarPosition, ...]:
    return (
        BarPosition("TL", 20, 60, 45, Face.TOP),
        BarPosition("TM", 20, 150, 45, Face.TOP),
        BarPosition("TR", 20, 240, 45, Face.TOP),
        BarPosition("BL", 20, 60, 450, Face.BOTTOM),
        BarPosition("BM", 20, 150, 450, Face.BOTTOM),
        BarPosition("BR", 20, 240, 450, Face.BOTTOM),
    )


def _flexure() -> FlexuralCapacityRequest:
    return FlexuralCapacityRequest(
        "IS456-WP02", SectionKind.RECTANGULAR, 300, 500, 25, 415, _bars(), Face.BOTTOM
    )


def _action(basis: ActionBasis = ActionBasis.STATIC_CONCURRENT) -> ConcurrentActionRow:
    return ConcurrentActionRow("R1", "S1", basis, 50, 0, 5, 0, 50, "analysis:one")


def test_shear_capacity_uses_actual_link_and_table_values() -> None:
    result = shear_capacity(_capacity())
    assert result.engineering == "pass"
    assert result.outputs["tau_c_n_per_mm2"] == pytest.approx(0.5534021442552741)
    assert result.outputs["tau_c_max_n_per_mm2"] == pytest.approx(3.1)
    assert result.outputs["link_area_mm2"] == pytest.approx(100.53096491487338)
    assert result.outputs["spacing_pass"] is True
    assert result.outputs["minimum_link_pass"] is True


def test_shear_check_handles_both_axes_and_station_signs() -> None:
    result = check_shear(
        ShearCheckRequest(
            (_capacity(ShearAxis.V2), _capacity(ShearAxis.V3)),
            (
                ShearDemand("S1", ShearAxis.V2, -100),
                ShearDemand("S1", ShearAxis.V3, 80),
            ),
        )
    )
    assert result.engineering == "pass"
    assert {check["axis"] for check in result.outputs["checks"]} == {"v2", "v3"}
    assert result.outputs["governing_utilization"] > 0


def test_missing_actual_link_is_not_evaluated() -> None:
    request = ShearCapacityRequest(
        "IS456-WP02", ShearAxis.V2, 300, 450, 25, 942.4777960769379, None
    )
    result = shear_capacity(request)
    assert result.execution == "completed"
    assert result.engineering == "not_evaluated"
    assert result.completeness == "partial"
    assert result.diagnostics[0].code == "REINFORCEMENT.REQUIRED"


def test_torsion_rejects_nonconcurrent_component_envelope() -> None:
    request = TorsionCheckRequest(
        "IS456-WP02",
        _action(ActionBasis.COMPONENT_ENVELOPE),
        _flexure(),
        _link(),
        ("TL", "TR", "BL", "BR"),
    )
    result = check_torsion(request)
    assert result.execution == "rejected_input"
    assert result.diagnostics[0].code == "ACTION.CONCURRENCY"


def test_torsion_does_not_ignore_minor_axis_interaction() -> None:
    action = ConcurrentActionRow(
        "R1", "S1", ActionBasis.STATIC_CONCURRENT, 50, 4, 5, 3, 50, "analysis:one"
    )
    request = TorsionCheckRequest(
        "IS456-WP02", action, _flexure(), _link(), ("TL", "TR", "BL", "BR")
    )
    result = check_torsion(request)
    assert result.applicability == "not_applicable"
    assert result.diagnostics[0].code == "PROFILE.UNSUPPORTED"


def test_torsion_checks_equivalent_actions_links_and_perimeter_bars() -> None:
    request = TorsionCheckRequest(
        "IS456-WP02", _action(), _flexure(), _link(), ("TL", "TR", "BL", "BR")
    )
    result = check_torsion(request)
    assert result.engineering == "pass"
    assert result.outputs["action_row_id"] == "R1"
    assert result.outputs["equivalent_shear_kn"] == pytest.approx(76.66666666666667)
    assert result.outputs["transverse_pass"] is True
    assert result.outputs["longitudinal_pass"] is True
    assert result.outputs["perimeter_pass"] is True


def test_open_link_is_completed_engineering_failure() -> None:
    request = TorsionCheckRequest(
        "IS456-WP02",
        _action(),
        _flexure(),
        _link(closed=False),
        ("TL", "TR", "BL", "BR"),
    )
    result = check_torsion(request)
    assert result.execution == "completed"
    assert result.engineering == "fail"
    assert result.diagnostics[0].code == "TORSION.CLOSED_LINK_REQUIRED"
