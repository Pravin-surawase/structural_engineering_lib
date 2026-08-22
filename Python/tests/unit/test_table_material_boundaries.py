"""Fail-closed boundaries for lower-level IS 456 table and material routes."""

from __future__ import annotations

import math
from collections.abc import Callable

import pytest

from structural_lib import materials as compatibility_materials
from structural_lib import tables as compatibility_tables
from structural_lib.codes.is456 import IS456Code, materials, tables

INVALID_NUMERIC_INPUTS = (
    True,
    "25",
    complex(25, 0),
    float("nan"),
    float("inf"),
    float("-inf"),
)


@pytest.mark.parametrize("value", INVALID_NUMERIC_INPUTS)
@pytest.mark.parametrize(
    "call",
    (
        lambda value: tables.get_tc_value(value, 1.0),
        lambda value: tables.get_tc_value(25.0, value),
        tables.get_tc_max_value,
        materials.get_xu_max_d,
        materials.get_ec,
        materials.get_fcr,
        lambda value: materials.get_steel_stress(value, 415.0),
        lambda value: materials.get_steel_stress(0.002, value),
    ),
)
def test_canonical_helpers_reject_non_finite_or_non_real_inputs(
    call: Callable[[object], float], value: object
) -> None:
    with pytest.raises(ValueError, match=r"finite.*real"):
        call(value)


@pytest.mark.parametrize(
    "call",
    (
        lambda: tables.get_tc_value(14.99, 1.0),
        lambda: tables.get_tc_value(40.01, 1.0),
        lambda: tables.get_tc_value(25.0, 0.149),
        lambda: tables.get_tc_value(25.0, 3.001),
        lambda: tables.get_tc_max_value(14.99),
        lambda: tables.get_tc_max_value(40.01),
        lambda: materials.get_xu_max_d(249.99),
        lambda: materials.get_xu_max_d(550.01),
        lambda: materials.get_ec(14.99),
        lambda: materials.get_ec(80.01),
        lambda: materials.get_fcr(14.99),
        lambda: materials.get_fcr(80.01),
        lambda: materials.get_steel_stress(0.002, 249.99),
        lambda: materials.get_steel_stress(0.002, 550.01),
    ),
)
def test_canonical_helpers_reject_unsupported_domains(
    call: Callable[[], float],
) -> None:
    with pytest.raises(ValueError, match="must be between"):
        call()


def test_compatibility_exports_and_is456_delegates_share_boundaries() -> None:
    code = IS456Code()
    invalid_calls = (
        lambda: compatibility_tables.get_tc_value(float("nan"), 1.0),
        lambda: compatibility_tables.get_tc_max_value(True),
        lambda: compatibility_materials.get_ec(True),
        lambda: compatibility_materials.get_fcr(float("inf")),
        lambda: compatibility_materials.get_xu_max_d(700.0),
        lambda: compatibility_materials.get_steel_stress(True, 415.0),
        lambda: code.get_tau_c(float("nan"), 1.0),
        lambda: code.get_tau_c_max(True),
    )

    for call in invalid_calls:
        with pytest.raises(ValueError):
            call()


def test_is456_design_strength_methods_share_material_domains() -> None:
    code = IS456Code()
    invalid_calls = (
        lambda: code.get_design_strength_concrete(True),
        lambda: code.get_design_strength_concrete(float("nan")),
        lambda: code.get_design_strength_concrete(10.0),
        lambda: code.get_design_strength_steel(True),
        lambda: code.get_design_strength_steel(float("inf")),
        lambda: code.get_design_strength_steel(700.0),
    )

    for call in invalid_calls:
        with pytest.raises(ValueError):
            call()


def test_valid_boundaries_and_benchmarks_are_unchanged() -> None:
    assert tables.get_tc_value(15.0, 0.15) == pytest.approx(0.28)
    assert tables.get_tc_value(40.0, 3.0) == pytest.approx(1.01)
    assert tables.get_tc_max_value(15.0) == pytest.approx(2.5)
    assert tables.get_tc_max_value(40.0) == pytest.approx(4.0)
    assert materials.get_xu_max_d(250.0) == pytest.approx(0.53)
    assert materials.get_xu_max_d(550.0) == pytest.approx(700 / (1100 + 0.87 * 550))
    assert materials.get_ec(80.0) == pytest.approx(5000 * math.sqrt(80))
    assert materials.get_fcr(15.0) == pytest.approx(0.7 * math.sqrt(15))
    assert materials.get_steel_stress(0.01, 300.0) == pytest.approx(0.87 * 300)


def test_internal_derived_reinforcement_uses_nearest_table_row() -> None:
    assert tables._get_tc_value_for_derived_reinforcement(20.0, 0.0) == pytest.approx(
        0.28
    )
    assert tables._get_tc_value_for_derived_reinforcement(20.0, 5.0) == pytest.approx(
        0.82
    )
