# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Source-bound tests for the bounded IS 13920 beam requirements contract."""

from __future__ import annotations

from typing import Any

import pytest

from structural_lib.codes.is456.traceability import get_clause_refs
from structural_lib.codes.is13920.beam import (
    calculate_confinement_spacing,
    check_beam_ductility,
    check_geometry,
    get_max_tension_steel_percentage,
    get_min_tension_steel_percentage,
)


def _check(**overrides: Any):
    inputs: dict[str, Any] = {
        "b": 250.0,
        "D": 500.0,
        "d": 450.0,
        "fck": 25.0,
        "fy": 500.0,
        "min_long_bar_dia": 12.0,
    }
    inputs.update(overrides)
    return check_beam_ductility(**inputs)


class TestAcceptedAmendmentChain:
    def test_g0_independent_benchmark_uses_six_bar_diameters(self) -> None:
        result = _check()

        assert result.min_pt == pytest.approx(0.24)
        assert result.max_pt == pytest.approx(2.5)
        assert result.confinement_spacing == pytest.approx(72.0)
        assert result.source_reference == (
            "IS 13920:2016 First Revision with Amendment 1 (2017) "
            "and Amendment 2 (2020)"
        )

    def test_each_close_link_limit_can_govern(self) -> None:
        assert calculate_confinement_spacing(200.0, 20.0) == 50.0
        assert calculate_confinement_spacing(600.0, 12.0) == 72.0
        assert calculate_confinement_spacing(600.0, 20.0) == 100.0


class TestStrictGeometryBoundary:
    def test_exact_width_depth_ratio_of_0_3_fails(self) -> None:
        valid, message, errors = check_geometry(300.0, 1000.0)

        assert valid is False
        assert "must be > 0.3" in message
        assert errors[0].code == "E_DUCTILE_002"
        assert errors[0].clause == "IS 13920 Cl. 6.1.1"

    def test_ratio_strictly_above_0_3_passes(self) -> None:
        valid, message, errors = check_geometry(300.000001, 1000.0)

        assert valid is True
        assert message == "OK"
        assert errors == []

    def test_minimum_width_is_200_mm_under_clause_6_1_2(self) -> None:
        valid, _, errors = check_geometry(199.999, 500.0)

        assert valid is False
        assert errors[0].code == "E_DUCTILE_001"
        assert errors[0].clause == "IS 13920 Cl. 6.1.2"
        assert check_geometry(200.0, 500.0)[0] is True


class TestFiniteIntake:
    @pytest.mark.parametrize(
        "field",
        ["b", "D", "d", "fck", "fy", "min_long_bar_dia"],
    )
    @pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
    def test_composed_contract_rejects_every_nonfinite_input(
        self, field: str, value: float
    ) -> None:
        result = _check(**{field: value})

        assert result.is_geometry_valid is False
        assert result.min_pt == 0.0
        assert result.max_pt == 0.0
        assert result.confinement_spacing == 0.0
        assert result.errors[0].code == "E_INPUT_017"
        assert any(error.field == field for error in result.errors)
        assert result.compliance_status == "NOT_EVALUATED_NO_PROVIDED_REINFORCEMENT"

    @pytest.mark.parametrize(
        ("function", "args"),
        [
            (get_min_tension_steel_percentage, (float("nan"), 500.0)),
            (get_min_tension_steel_percentage, (25.0, float("inf"))),
            (calculate_confinement_spacing, (float("nan"), 12.0)),
            (calculate_confinement_spacing, (450.0, float("inf"))),
        ],
    )
    def test_direct_requirement_calculators_reject_nonfinite_inputs(
        self, function: Any, args: tuple[float, float]
    ) -> None:
        with pytest.raises(ValueError):
            function(*args)


class TestRequirementVersusComplianceTruth:
    def test_result_does_not_claim_reinforcement_compliance(self) -> None:
        result = _check()

        assert result.is_geometry_valid is True
        assert result.result_kind == "REQUIREMENTS_WITH_GEOMETRY_CHECK"
        assert result.compliance_status == ("NOT_EVALUATED_NO_PROVIDED_REINFORCEMENT")
        assert "not evaluated" in result.remarks
        assert "Compliant" not in result.remarks

    def test_clause_and_standard_provenance_are_exact(self) -> None:
        result = _check()

        assert result.standard == "IS 13920:2016"
        assert result.clause_refs == (
            "6.1.1",
            "6.1.2",
            "6.2.1(b)",
            "6.2.2",
            "6.3.5",
        )
        assert get_clause_refs(check_geometry) == ["6.1.1", "6.1.2"]
        assert get_clause_refs(get_min_tension_steel_percentage) == ["6.2.1(b)"]
        assert get_clause_refs(get_max_tension_steel_percentage) == ["6.2.2"]
        assert get_clause_refs(calculate_confinement_spacing) == ["6.3.5"]
        assert get_clause_refs(check_beam_ductility) == list(result.clause_refs)
