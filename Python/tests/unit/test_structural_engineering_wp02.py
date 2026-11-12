from dataclasses import replace

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
                ShearDemand("S2", ShearAxis.V2, 50),
                ShearDemand("S1", ShearAxis.V3, 80),
            ),
        )
    )
    assert result.engineering == "pass"
    assert {check["axis"] for check in result.outputs["checks"]} == {"v2", "v3"}
    assert result.outputs["governing_utilization"] > 0
    checks = result.outputs["checks"]
    assert checks[0]["capacity_result_id"] == checks[1]["capacity_result_id"]
    assert checks[0]["capacity_result_id"] != checks[2]["capacity_result_id"]
    assert [check["signed_demand_kn"] for check in checks] == [-100, 50, 80]


def _unsupported_capacity(axis: ShearAxis, kind: str) -> ShearCapacityRequest:
    if kind == "concrete":
        return replace(_capacity(axis), concrete_strength_n_per_mm2=45)
    return replace(
        _capacity(axis),
        link=replace(_link(), steel_yield_strength_n_per_mm2=550),
    )


@pytest.mark.parametrize("axis", tuple(ShearAxis))
@pytest.mark.parametrize("kind", ("concrete", "link_grade"))
def test_unsupported_shear_batch_preserves_capacity_scope_state(axis, kind) -> None:
    capacity = _unsupported_capacity(axis, kind)
    producer = shear_capacity(capacity)
    batch = check_shear(ShearCheckRequest((capacity,), (ShearDemand("S1", axis, 50),)))
    for result in (producer, batch):
        assert result.execution == "completed"
        assert result.applicability == "not_applicable"
        assert result.engineering == "not_evaluated"
        assert result.completeness == "complete_for_scope"
        assert result.freshness == "current"
        assert result.outputs == {}
        assert result.diagnostics[0].code == "PROFILE.UNSUPPORTED"
    assert batch.diagnostics == producer.diagnostics


@pytest.mark.parametrize("unsupported_axis", tuple(ShearAxis))
@pytest.mark.parametrize("kind", ("concrete", "link_grade"))
@pytest.mark.parametrize("companion", ("pass", "fail", "missing_link", "rejected"))
@pytest.mark.parametrize("reverse", (False, True))
def test_mixed_shear_capacity_precedence(
    unsupported_axis, kind, companion, reverse
) -> None:
    unsupported = _unsupported_capacity(unsupported_axis, kind)
    other_axis = ShearAxis.V3 if unsupported_axis is ShearAxis.V2 else ShearAxis.V2
    other = _capacity(other_axis)
    if companion == "fail":
        other = replace(other, link=_link(spacing_mm=400))
    elif companion == "missing_link":
        other = replace(other, link=None)
    elif companion == "rejected":
        other = replace(other, resisting_width_mm=-1)
    producer = shear_capacity(other)
    assert (
        producer.engineering
        == {
            "pass": "pass",
            "fail": "fail",
            "missing_link": "not_evaluated",
            "rejected": "not_evaluated",
        }[companion]
    )
    capacities = (other, unsupported) if reverse else (unsupported, other)
    result = check_shear(
        ShearCheckRequest(
            capacities,
            (ShearDemand("S1", ShearAxis.V2, 50), ShearDemand("S1", ShearAxis.V3, 50)),
        )
    )
    rejected = companion == "rejected"
    assert result.execution == ("rejected_input" if rejected else "completed")
    assert result.applicability == ("unknown" if rejected else "not_applicable")
    assert result.completeness == ("partial" if rejected else "complete_for_scope")
    assert result.engineering == "not_evaluated"
    assert result.outputs == {}
    assert result.diagnostics == (
        producer.diagnostics if rejected else shear_capacity(unsupported).diagnostics
    )


@pytest.mark.parametrize("kind", ("concrete", "link_grade"))
def test_invalid_shear_demand_precedes_unsupported_scope(kind) -> None:
    result = check_shear(
        ShearCheckRequest(
            (_unsupported_capacity(ShearAxis.V2, kind),),
            (ShearDemand("", ShearAxis.V2, 50),),
        )
    )
    assert result.execution == "rejected_input"
    assert result.applicability == "unknown"
    assert result.engineering == "not_evaluated"
    assert result.completeness == "partial"
    assert result.diagnostics[0].code == "INPUT.RANGE"


@pytest.mark.parametrize("unsupported", (False, True))
@pytest.mark.parametrize("missing", ("link", "axis"))
def test_shear_missing_evidence_holds_unless_scope_is_known_unsupported(
    unsupported, missing
) -> None:
    capacity = _capacity()
    if unsupported:
        capacity = _unsupported_capacity(ShearAxis.V2, "concrete")
    if missing == "link":
        capacity = replace(capacity, link=None)
    axis = ShearAxis.V3 if missing == "axis" else ShearAxis.V2
    result = check_shear(ShearCheckRequest((capacity,), (ShearDemand("S1", axis, 50),)))
    assert result.execution == "completed"
    assert result.applicability == ("not_applicable" if unsupported else "unknown")
    assert result.completeness == ("complete_for_scope" if unsupported else "partial")
    assert result.engineering == "not_evaluated"
    assert result.outputs == {}
    expected_code = (
        "PROFILE.UNSUPPORTED"
        if unsupported
        else (
            "REINFORCEMENT.REQUIRED" if missing == "link" else "SHEAR.CAPACITY_MISSING"
        )
    )
    assert result.diagnostics[0].code == expected_code


def test_evaluated_shear_failure_remains_complete_fail() -> None:
    result = check_shear(
        ShearCheckRequest((_capacity(),), (ShearDemand("S1", ShearAxis.V2, 1000),))
    )
    assert result.execution == "completed"
    assert result.applicability == "applicable"
    assert result.engineering == "fail"
    assert result.completeness == "complete_for_scope"
    assert result.outputs["checks"][0]["engineering"] == "fail"
    assert result.diagnostics[0].code == "SHEAR.FAIL"


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


@pytest.mark.parametrize("sign", (-1, 1))
@pytest.mark.parametrize("torsion", (0, 5, 50))
def test_opposite_tension_steel_is_checked_only_when_equivalent_moment_exists(
    sign, torsion
) -> None:
    active = Face.BOTTOM if sign > 0 else Face.TOP
    bars = tuple(
        replace(bar, diameter_mm=8) if bar.face is not active else bar
        for bar in _bars()
    )
    result = check_torsion(
        TorsionCheckRequest(
            "IS456-WP02",
            replace(_action(), m3_knm=sign * 50, torsion_knm=torsion),
            replace(_flexure(), bars=bars),
            _link(),
            ("TL", "TR", "BL", "BR"),
        )
    )
    assert result.execution == "completed"
    assert result.outputs["longitudinal_pass"] is (torsion < 50)
    assert result.engineering == ("pass" if torsion < 50 else "fail")
