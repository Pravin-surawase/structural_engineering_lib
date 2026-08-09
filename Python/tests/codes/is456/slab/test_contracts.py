# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Exact P6 contract tests for solid rectangular slab classification."""

from __future__ import annotations

import math

import pytest

from structural_lib.codes.is456.slab import (
    SlabClassification,
    SlabContractError,
    SlabScopeStatus,
    SolidRectangularSlabGeometry,
    classify_solid_rectangular_slab,
)
from structural_lib.codes.is456.traceability import get_clause_refs


def test_geometry_normalizes_axis_neutral_effective_spans() -> None:
    geometry = SolidRectangularSlabGeometry(
        span_a_effective_mm=6000,
        span_b_effective_mm=3000,
        thickness_mm=150,
        strip_width_mm=1000,
    )

    assert geometry.short_effective_span_mm == 3000.0
    assert geometry.long_effective_span_mm == 6000.0
    assert geometry.span_order_was_normalized is True
    assert geometry.strip_width_mm == 1000.0


def test_exact_ratio_boundary_two_is_two_way() -> None:
    result = classify_solid_rectangular_slab(
        SolidRectangularSlabGeometry(3000, 6000, 150)
    )

    assert result.span_ratio_ly_lx == 2.0
    assert result.classification is SlabClassification.TWO_WAY
    assert result.scope_status is SlabScopeStatus.SUPPORTED
    assert result.is_supported is True


def test_ratio_above_two_is_one_way() -> None:
    result = classify_solid_rectangular_slab(
        SolidRectangularSlabGeometry(3000, 6000.3, 150)
    )

    assert result.span_ratio_ly_lx > 2.0
    assert result.classification is SlabClassification.ONE_WAY


def test_ratio_below_two_is_two_way() -> None:
    result = classify_solid_rectangular_slab(
        SolidRectangularSlabGeometry(4000, 6000, 175)
    )

    assert result.span_ratio_ly_lx == 1.5
    assert result.classification is SlabClassification.TWO_WAY


def test_result_records_contract_assumptions_and_source_ids() -> None:
    result = classify_solid_rectangular_slab(
        SolidRectangularSlabGeometry(6000, 3000, 150)
    )

    assert any("normalized" in assumption.lower() for assumption in result.assumptions)
    assert any(
        "no support condition" in assumption.lower()
        for assumption in result.assumptions
    )
    assert result.source_refs == (
        "IS 456:2000 (consolidated through Amd. 5), Cl. 24.1",
        "IS 456:2000 (consolidated through Amd. 5), Cl. 24.3",
    )
    assert get_clause_refs(classify_solid_rectangular_slab) == ["24.1", "24.3"]


@pytest.mark.parametrize(
    ("field_name", "value", "message"),
    [
        ("span_a_effective_mm", 0, "positive"),
        ("span_b_effective_mm", -1, "positive"),
        ("thickness_mm", math.inf, "finite"),
        ("thickness_mm", math.nan, "finite"),
        ("strip_width_mm", 0, "positive"),
        ("strip_width_mm", "1000", "real value"),
    ],
)
def test_nonpositive_nonfinite_or_non_numeric_geometry_fails_closed(
    field_name: str, value: object, message: str
) -> None:
    values: dict[str, object] = {
        "span_a_effective_mm": 3000,
        "span_b_effective_mm": 6000,
        "thickness_mm": 150,
        "strip_width_mm": None,
    }
    values[field_name] = value

    with pytest.raises(SlabContractError, match=message):
        SolidRectangularSlabGeometry(**values)  # type: ignore[arg-type]


def test_classifier_rejects_any_geometry_outside_supported_contract() -> None:
    with pytest.raises(SlabContractError, match="SolidRectangularSlabGeometry"):
        classify_solid_rectangular_slab(object())  # type: ignore[arg-type]


def test_geometry_is_frozen() -> None:
    geometry = SolidRectangularSlabGeometry(3000, 6000, 150)

    with pytest.raises(AttributeError):
        geometry.thickness_mm = 175  # type: ignore[misc]
