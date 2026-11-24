# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Pravin Surawase
"""SLAB-01 public regression cases for the frozen continuous strip inputs."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from structural_lib.codes.is456.slab.models import SlabContractError
from structural_lib.design.is456 import slab
from structural_lib.services.slab_api import (
    ContinuousOneWaySlabDesignResult,
    design_continuous_one_way_slab_is456,
)

pytestmark = pytest.mark.repo_only

_CASES = json.loads(
    (
        Path(__file__).resolve().parents[3]
        / "docs/verification/library-0311-s1-continuous-slab.json"
    ).read_text(encoding="utf-8")
)
_BUILT_IN = _CASES["built_in"]
_SUPPLIED = _CASES["supplied_coefficients"]
_TOLERANCES = _CASES["candidate_comparison"]["tolerances"]
_ACTION_TOLERANCE = _TOLERANCES[
    "moment_shear_stress_percentage_and_dimensionless_absolute"
]


def _approx(expected: float, absolute_tolerance: float = _ACTION_TOLERANCE):
    return pytest.approx(expected, abs=absolute_tolerance, rel=_TOLERANCES["relative"])


def _assert_frozen_calculation(
    result: ContinuousOneWaySlabDesignResult, case: dict, width_mm: int
) -> None:
    flexure = result.flexure
    context = f"{case['id']} at {width_mm} mm"
    assert flexure.input.geometry.strip_width_mm == width_mm, context
    assert flexure.line_load_kn_per_m == _approx(
        case["physical_line_load_kn_per_m_by_width_mm"][str(width_mm)]
    ), context

    expected = case["expected_at_each_width"]
    quantities = {
        "shear_kn_per_m": flexure.factored_shear_kn_per_m,
        "shear_stress_n_per_mm2": result.shear.tau_v_n_per_mm2,
        "shear_tension_steel_percent": result.shear.tension_steel_percentage,
        "actual_span_depth_ratio": result.serviceability.actual_span_depth_ratio,
        "reviewed_modified_span_depth_limit": (
            result.serviceability.reviewed_modified_span_depth_limit
        ),
    }
    for region, action, steel in (
        ("positive", flexure.positive_midspan, result.positive_reinforcement),
        ("negative", flexure.negative_support, result.negative_reinforcement),
    ):
        assert steel.area_passed is expected[f"{region}_area_passed"], context
        quantities.update(
            {
                f"{region}_moment_knm_per_m": action.factored_moment_knm_per_m,
                f"{region}_limiting_moment_knm_per_m": action.limiting_moment_knm_per_m,
                f"{region}_action_steel_mm2_per_m": action.ast_required_mm2_per_m,
                f"{region}_governing_steel_mm2_per_m": steel.governing_required_mm2_per_m,
                f"{region}_provided_steel_mm2_per_m": steel.provided_mm2_per_m,
            }
        )
        assert steel.required_for_moment_mm2_per_m == _approx(
            expected[f"{region}_action_steel_mm2_per_m"],
            _TOLERANCES["steel_area_mm2_per_m_absolute"],
        ), context
    assert result.serviceability.is_satisfied is expected["serviceability_satisfied"]

    for name, value in quantities.items():
        tolerance = (
            _TOLERANCES["steel_area_mm2_per_m_absolute"]
            if name.endswith("_mm2_per_m")
            else _ACTION_TOLERANCE
        )
        assert value == _approx(expected[name], tolerance), f"{context}: {name}"


@pytest.mark.parametrize("case", _BUILT_IN["cases"], ids=lambda case: case["id"])
def test_continuous_slab_public_result_is_invariant_to_strip_width(case) -> None:
    payload = deepcopy(_BUILT_IN["cookbook_base"]["request"])
    for group, overrides in case["request_overrides"].items():
        payload[group].update(overrides)
    provenance = _BUILT_IN["expected_provenance"]

    for width_mm in case["widths_mm"]:
        payload["geometry"]["strip_width_mm"] = width_mm
        request = slab.load_continuous_one_way_json(json.dumps(payload))
        result = slab.design_continuous_one_way(request)
        assert request.geometry.strip_width_mm == width_mm
        assert result.envelope.intake_status.value == "VALID"
        assert result.envelope.calculation_status.value == "COMPLETED"
        assert (
            result.engineering_status.value
            == case["expected_at_each_width"]["engineering_status"]
        ), f"{case['id']} at {width_mm} mm"
        json.dumps(result.to_dict(), allow_nan=False)
        calculation = result.calculation
        assert calculation.flexure.coefficient_correctness_verified_by_library is True
        coefficients = calculation.flexure.input.coefficients
        assert coefficients.method.value == provenance["method"]
        assert coefficients.table_id == provenance["table_id"]
        assert coefficients.case_id == provenance["case_id"]
        _assert_frozen_calculation(calculation, case, width_mm)

        if width_mm == case["widths_mm"][0]:
            reference = calculation
        assert calculation.shear == reference.shear
        assert calculation.serviceability == reference.serviceability


def test_continuous_slab_supplied_coefficients_are_invariant_to_strip_width() -> None:
    case = _SUPPLIED
    kwargs = {**case["base_kwargs"], **case["kwargs_overrides"]}
    provenance = case["expected_provenance"]
    for width_mm in case["widths_mm"]:
        result = design_continuous_one_way_slab_is456(**kwargs, strip_width_mm=width_mm)
        assert result.flexure.coefficient_correctness_verified_by_library is False
        coefficients = result.flexure.input.coefficients
        assert coefficients.source_reference == provenance["source_reference"]
        assert (
            coefficients.qualified_acceptance_reference
            == provenance["qualified_acceptance_reference"]
        )
        _assert_frozen_calculation(result, case, width_mm)

        if width_mm == case["widths_mm"][0]:
            reference = result
        assert result.shear == reference.shear
        assert result.serviceability == reference.serviceability


def test_continuous_slab_capacity_diagnostic_reports_physical_strip_totals() -> None:
    case = _CASES["capacity_diagnostic_control"]
    kwargs = {**_SUPPLIED["base_kwargs"], **case["kwargs_overrides"]}
    with pytest.raises(SlabContractError, match="exceeds singly reinforced") as caught:
        design_continuous_one_way_slab_is456(**kwargs)

    expected = case["expected"]
    failure = caught.value.result
    assert failure.governing_region == expected["governing_region"]
    assert (
        failure.result_envelope.engineering_status.value
        == expected["engineering_status"]
    )
    assert failure.result_envelope.issues[0].code == expected["issue_code"]
    assert failure.factored_moment_knm == _approx(expected["factored_moment_knm"])
    assert failure.limiting_moment_knm == _approx(expected["limiting_moment_knm"])
