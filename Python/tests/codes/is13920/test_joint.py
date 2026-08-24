# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for the bounded IS 13920 SCWB directional-case contract."""

from __future__ import annotations

from typing import Any

import pytest

from structural_lib.codes.is13920.joint import (
    ColumnCapacityBasis,
    JointTopology,
    PrincipalPlane,
    ShakingDirection,
    check_scwb,
)


def _check(**overrides: Any):
    inputs: dict[str, Any] = {
        "column_top_capacity_knm": 200.0,
        "column_bottom_capacity_knm": 200.0,
        "beam_left_capacity_knm": 100.0,
        "beam_right_capacity_knm": 100.0,
        "topology": JointTopology.INTERIOR,
        "principal_plane": PrincipalPlane.X,
        "shaking_direction": ShakingDirection.POSITIVE,
        "column_capacity_direction": ShakingDirection.NEGATIVE,
        "column_top_factored_axial_load_kn": 850.0,
        "column_bottom_factored_axial_load_kn": 900.0,
        "column_capacity_basis": ColumnCapacityBasis.FACTORED_AXIAL_LOAD,
        "is_roof_joint": False,
        "is_flat_slab_system": False,
    }
    inputs.update(overrides)
    return check_scwb(**inputs)


class TestFixedIS13920Requirement:
    def test_g0_false_pass_benchmark_now_fails_at_1_4(self) -> None:
        result = _check(
            column_top_capacity_knm=125.0,
            column_bottom_capacity_knm=125.0,
        )

        assert result.factor == 1.4
        assert result.sum_column_capacity_knm == 250.0
        assert result.sum_beam_capacity_knm == 200.0
        assert result.required_column_capacity_knm == pytest.approx(280.0)
        assert result.ratio == pytest.approx(0.8928571428571429)
        assert result.is_satisfied is False
        assert result.errors[0].code == "E_SCWB_002"
        assert "1.4" in result.errors[0].message

    def test_exact_1_4_boundary_passes(self) -> None:
        result = _check(
            column_top_capacity_knm=140.0,
            column_bottom_capacity_knm=140.0,
        )

        assert result.is_satisfied is True
        assert result.ratio == pytest.approx(1.0)
        assert result.errors == ()

    def test_nonstandard_factor_override_is_not_part_of_contract(self) -> None:
        with pytest.raises(TypeError, match="unexpected keyword argument 'factor'"):
            _check(factor=1.0)

    def test_result_is_labeled_only_with_fixed_is13920_basis(self) -> None:
        result = _check()

        assert result.standard == "IS 13920:2016"
        assert "7.2.1-7.2.1.3" in result.source_reference
        assert result.factor == 1.4


class TestDirectionalAndAxialCapacityProvenance:
    @pytest.mark.parametrize(
        ("plane", "shaking", "column_direction"),
        [
            (PrincipalPlane.X, ShakingDirection.POSITIVE, ShakingDirection.NEGATIVE),
            (PrincipalPlane.X, ShakingDirection.NEGATIVE, ShakingDirection.POSITIVE),
            (PrincipalPlane.Y, ShakingDirection.POSITIVE, ShakingDirection.NEGATIVE),
            (PrincipalPlane.Y, ShakingDirection.NEGATIVE, ShakingDirection.POSITIVE),
        ],
    )
    def test_every_plane_direction_case_is_explicit(
        self,
        plane: PrincipalPlane,
        shaking: ShakingDirection,
        column_direction: ShakingDirection,
    ) -> None:
        result = _check(
            principal_plane=plane,
            shaking_direction=shaking,
            column_capacity_direction=column_direction,
        )

        assert result.principal_plane is plane
        assert result.shaking_direction is shaking
        assert result.beam_capacity_direction is shaking
        assert result.column_capacity_direction is column_direction
        assert result.assessment_scope == "ONE_PRINCIPAL_PLANE_ONE_SHAKING_DIRECTION"

    def test_column_capacity_direction_must_oppose_shaking(self) -> None:
        with pytest.raises(ValueError, match="must oppose"):
            _check(column_capacity_direction=ShakingDirection.POSITIVE)

    def test_factored_axial_load_basis_and_values_are_retained(self) -> None:
        result = _check(
            column_top_factored_axial_load_kn=812.5,
            column_bottom_factored_axial_load_kn=-125.0,
        )

        assert result.column_capacity_basis is ColumnCapacityBasis.FACTORED_AXIAL_LOAD
        assert result.column_top_factored_axial_load_kn == 812.5
        assert result.column_bottom_factored_axial_load_kn == -125.0

    @pytest.mark.parametrize(
        "field",
        [
            "column_top_factored_axial_load_kn",
            "column_bottom_factored_axial_load_kn",
        ],
    )
    def test_axial_load_basis_rejects_nonfinite_values(self, field: str) -> None:
        with pytest.raises(ValueError, match=field):
            _check(**{field: float("nan")})


class TestApplicability:
    def test_non_roof_beam_column_joint_is_explicitly_applicable(self) -> None:
        result = _check()
        assert result.applicability == "APPLICABLE_NON_ROOF_BEAM_COLUMN_JOINT"

    def test_roof_joint_waiver_cannot_be_reported_as_pass(self) -> None:
        with pytest.raises(ValueError, match="waived at roof joints"):
            _check(is_roof_joint=True)

    def test_flat_slab_exclusion_cannot_be_reported_as_pass(self) -> None:
        with pytest.raises(ValueError, match="not supported for flat-slab"):
            _check(is_flat_slab_system=True)

    @pytest.mark.parametrize("field", ["is_roof_joint", "is_flat_slab_system"])
    def test_applicability_flags_must_be_known_booleans(self, field: str) -> None:
        with pytest.raises(TypeError, match=field):
            _check(**{field: None})


class TestSupportedTopologies:
    def test_interior_joint_uses_both_beams(self) -> None:
        result = _check(
            beam_left_capacity_knm=90.0,
            beam_right_capacity_knm=110.0,
        )
        assert result.topology is JointTopology.INTERIOR
        assert result.sum_beam_capacity_knm == 200.0

    def test_left_exterior_joint_uses_only_left_beam(self) -> None:
        result = _check(
            topology=JointTopology.EXTERIOR_LEFT,
            beam_left_capacity_knm=120.0,
            beam_right_capacity_knm=None,
        )
        assert result.sum_beam_capacity_knm == 120.0

    def test_right_exterior_joint_uses_only_right_beam(self) -> None:
        result = _check(
            topology=JointTopology.EXTERIOR_RIGHT,
            beam_left_capacity_knm=None,
            beam_right_capacity_knm=130.0,
        )
        assert result.sum_beam_capacity_knm == 130.0

    @pytest.mark.parametrize(
        "overrides",
        [
            {"beam_right_capacity_knm": None},
            {
                "topology": JointTopology.EXTERIOR_LEFT,
                "beam_right_capacity_knm": 100.0,
            },
            {
                "topology": JointTopology.EXTERIOR_RIGHT,
                "beam_left_capacity_knm": 100.0,
                "beam_right_capacity_knm": None,
            },
        ],
    )
    def test_topology_and_present_beam_sides_must_agree(
        self,
        overrides: dict[str, Any],
    ) -> None:
        with pytest.raises(ValueError, match="topology"):
            _check(**overrides)


class TestValidationAndResultMethods:
    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("column_top_capacity_knm", 0.0),
            ("column_bottom_capacity_knm", -1.0),
            ("beam_left_capacity_knm", float("inf")),
        ],
    )
    def test_capacities_must_be_positive_and_finite(
        self,
        field: str,
        value: float,
    ) -> None:
        with pytest.raises(ValueError):
            _check(**{field: value})

    def test_to_dict_preserves_contract_fields(self) -> None:
        result_dict = _check().to_dict()

        assert result_dict["topology"] == "INTERIOR"
        assert result_dict["principal_plane"] == "X"
        assert result_dict["shaking_direction"] == "POSITIVE"
        assert result_dict["beam_capacity_direction"] == "POSITIVE"
        assert result_dict["column_capacity_direction"] == "NEGATIVE"
        assert result_dict["column_capacity_basis"] == "FACTORED_AXIAL_LOAD"
        assert result_dict["factor"] == 1.4
        assert result_dict["standard"] == "IS 13920:2016"
        assert result_dict["clause"] == result_dict["source_reference"]

    def test_summary_and_case_safety_are_directional(self) -> None:
        passing = _check()
        failing = _check(
            column_top_capacity_knm=100.0,
            column_bottom_capacity_knm=100.0,
        )

        assert passing.is_safe() is True
        assert "directional case" in passing.summary()
        assert "PASS" in passing.summary()
        assert failing.is_safe() is False
        assert "FAIL" in failing.summary()

    def test_result_is_frozen(self) -> None:
        result = _check()
        with pytest.raises(AttributeError):
            result.factor = 1.0  # type: ignore[misc]
