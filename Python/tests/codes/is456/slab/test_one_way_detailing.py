# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Exact P8 tests for one-way slab provided-reinforcement detailing."""

from __future__ import annotations

from dataclasses import replace

import pytest

from structural_lib.codes.is456.slab.models import (
    SlabContractError,
    SolidRectangularSlabGeometry,
)
from structural_lib.codes.is456.slab.one_way import (
    OneWaySlabFlexureInput,
    design_simply_supported_one_way_slab_flexure,
)
from structural_lib.codes.is456.slab.one_way_detailing import (
    DetailingAdequacyStatus,
    OneWaySlabDetailingInput,
    OneWaySlabReviewRequirement,
    OneWaySlabServiceabilityStatus,
    check_simply_supported_one_way_slab_detailing,
)
from structural_lib.codes.is456.traceability import get_clause_refs


def _p7_result(*, short_span_mm: float = 3000.0, d_mm: float = 125.0):
    return design_simply_supported_one_way_slab_flexure(
        OneWaySlabFlexureInput(
            geometry=SolidRectangularSlabGeometry(short_span_mm, 7500, 150, 1000),
            d_mm=d_mm,
            factored_area_load_kn_per_m2=10,
            fck_n_per_mm2=20,
            fy_n_per_mm2=415,
        )
    )


def _benchmark_input(**kwargs: float) -> OneWaySlabDetailingInput:
    values: dict[str, object] = {
        "flexure_result": _p7_result(),
        "main_bar_diameter_mm": 10,
        "main_bar_spacing_mm": 250,
        "distribution_bar_diameter_mm": 8,
        "distribution_bar_spacing_mm": 250,
    }
    values.update(kwargs)
    return OneWaySlabDetailingInput(**values)  # type: ignore[arg-type]


def test_independent_benchmark_checks_provided_reinforcement_and_review_boundary() -> (
    None
):
    """10 mm at 250 provides 314.159 mm2/m; 8 mm at 250 provides 201.062 mm2/m."""
    result = check_simply_supported_one_way_slab_detailing(_benchmark_input())

    assert result.minimum_reinforcement_ratio == pytest.approx(0.0012)
    assert result.minimum_reinforcement_mm2 == pytest.approx(180.0)
    assert result.main_reinforcement_required_mm2 == pytest.approx(260.7266304)
    assert result.distribution_reinforcement_required_mm2 == pytest.approx(180.0)
    assert result.main_reinforcement_provided_mm2 == pytest.approx(314.1592654)
    assert result.distribution_reinforcement_provided_mm2 == pytest.approx(201.0619298)
    assert result.maximum_bar_diameter_mm == pytest.approx(18.75)
    assert result.maximum_main_spacing_mm == pytest.approx(300.0)
    assert result.maximum_distribution_spacing_mm == pytest.approx(450.0)
    assert result.basic_span_to_depth_ratio == pytest.approx(24.0)
    assert result.detailing_adequacy is DetailingAdequacyStatus.ADEQUATE
    assert (
        result.serviceability_status
        is OneWaySlabServiceabilityStatus.QUALIFIED_REVIEW_REQUIRED
    )
    assert (
        result.review_requirement
        is OneWaySlabReviewRequirement.QUALIFIED_REVIEW_REQUIRED
    )
    assert all(check.passed for check in result.governing_checks)


def test_basic_span_to_depth_boundary_at_twenty_is_satisfied() -> None:
    result = check_simply_supported_one_way_slab_detailing(
        OneWaySlabDetailingInput(
            flexure_result=_p7_result(short_span_mm=2500, d_mm=125),
            main_bar_diameter_mm=10,
            main_bar_spacing_mm=250,
            distribution_bar_diameter_mm=8,
            distribution_bar_spacing_mm=250,
        )
    )

    assert result.basic_span_to_depth_ratio == pytest.approx(20.0)
    assert (
        result.serviceability_status
        is OneWaySlabServiceabilityStatus.BASIC_RATIO_SATISFIED
    )
    assert (
        result.review_requirement
        is OneWaySlabReviewRequirement.NO_QUALIFIED_REVIEW_REQUIRED
    )


@pytest.mark.parametrize(
    ("fy_n_per_mm2", "expected_ratio"), [(250, 0.0015), (500, 0.0012)]
)
def test_minimum_reinforcement_ratio_uses_supported_steel_grade(
    fy_n_per_mm2: float, expected_ratio: float
) -> None:
    flexure = design_simply_supported_one_way_slab_flexure(
        OneWaySlabFlexureInput(
            geometry=SolidRectangularSlabGeometry(3000, 7500, 150, 1000),
            d_mm=125,
            factored_area_load_kn_per_m2=10,
            fck_n_per_mm2=20,
            fy_n_per_mm2=fy_n_per_mm2,
        )
    )
    result = check_simply_supported_one_way_slab_detailing(
        OneWaySlabDetailingInput(flexure, 12, 200, 10, 300)
    )

    assert result.minimum_reinforcement_ratio == pytest.approx(expected_ratio)
    assert result.minimum_reinforcement_mm2 == pytest.approx(expected_ratio * 150_000)


@pytest.mark.parametrize(
    ("kwargs", "failed_check"),
    [
        ({"main_bar_spacing_mm": 400}, "P8-MAIN-STEEL-01"),
        ({"distribution_bar_spacing_mm": 300}, "P8-DIST-STEEL-01"),
        ({"main_bar_diameter_mm": 20}, "P8-MAIN-DIA-01"),
        ({"distribution_bar_diameter_mm": 20}, "P8-DIST-DIA-01"),
        ({"main_bar_spacing_mm": 301}, "P8-MAIN-SPACING-01"),
        ({"distribution_bar_spacing_mm": 451}, "P8-DIST-SPACING-01"),
    ],
)
def test_provided_steel_spacing_and_diameter_failure_boundaries(
    kwargs: dict[str, float], failed_check: str
) -> None:
    result = check_simply_supported_one_way_slab_detailing(_benchmark_input(**kwargs))

    assert result.detailing_adequacy is DetailingAdequacyStatus.INADEQUATE
    checks = {check.check_id: check for check in result.governing_checks}
    assert checks[failed_check].passed is False


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"main_bar_diameter_mm": 0}, "positive"),
        ({"main_bar_spacing_mm": float("inf")}, "finite"),
        ({"distribution_bar_diameter_mm": float("nan")}, "finite"),
        ({"distribution_bar_spacing_mm": 0}, "positive"),
    ],
)
def test_nonfinite_or_nonpositive_provided_bars_fail_closed(
    kwargs: dict[str, float], message: str
) -> None:
    with pytest.raises(SlabContractError, match=message):
        _benchmark_input(**kwargs)


def test_wrong_p7_status_and_inconsistent_geometry_fail_closed() -> None:
    flexure = _p7_result()
    wrong_status = replace(flexure, status=object())
    with pytest.raises(SlabContractError, match="status"):
        OneWaySlabDetailingInput(wrong_status, 10, 250, 8, 250)  # type: ignore[arg-type]

    inconsistent_geometry = replace(flexure, effective_short_span_mm=3001)
    with pytest.raises(SlabContractError, match="inconsistent effective short-span"):
        check_simply_supported_one_way_slab_detailing(
            OneWaySlabDetailingInput(inconsistent_geometry, 10, 250, 8, 250)
        )


def test_nonfinite_retained_p7_value_fails_closed() -> None:
    nonfinite_flexure = replace(_p7_result(), ast_required_mm2=float("inf"))

    with pytest.raises(SlabContractError, match="ast_required_mm2 must be finite"):
        check_simply_supported_one_way_slab_detailing(
            OneWaySlabDetailingInput(nonfinite_flexure, 10, 250, 8, 250)
        )


def test_unsupported_p7_steel_grade_fails_closed() -> None:
    flexure = _p7_result()
    object.__setattr__(flexure.input, "fy_n_per_mm2", 400.0)

    with pytest.raises(SlabContractError, match="P8 supported grades"):
        check_simply_supported_one_way_slab_detailing(
            OneWaySlabDetailingInput(flexure, 10, 250, 8, 250)
        )


def test_p8_traceability_and_limits_are_explicit() -> None:
    result = check_simply_supported_one_way_slab_detailing(_benchmark_input())

    assert get_clause_refs(check_simply_supported_one_way_slab_detailing) == [
        "24.1",
        "26.3.3",
        "26.5.2.1",
    ]
    assert any("964e2705" in source for source in result.source_refs)
    assert any("4fc24999" in source for source in result.source_refs)
    assert any(
        "AMENDMENT-6-SLAB-CHANGE: none" in source for source in result.source_refs
    )
    assert any("deflection modification factors" in item for item in result.limitations)
