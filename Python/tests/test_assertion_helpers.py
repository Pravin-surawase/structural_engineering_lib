# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for the IS 456 test assertion helpers."""

import pytest

from tests.helpers.is456_assertions import (
    assert_capacity_exceeds_demand,
    assert_dimensions_positive,
    assert_spacing_valid,
)


class TestAssertCapacityExceedsDemand:
    def test_capacity_greater_passes(self):
        assert_capacity_exceeds_demand(100.0, 80.0)

    def test_capacity_equal_passes(self):
        assert_capacity_exceeds_demand(100.0, 100.0)

    def test_capacity_less_fails(self):
        with pytest.raises(AssertionError, match="Capacity.*< Demand"):
            assert_capacity_exceeds_demand(80.0, 100.0)

    def test_label_in_message(self):
        with pytest.raises(AssertionError, match="beam B1"):
            assert_capacity_exceeds_demand(50.0, 100.0, label="beam B1")

    def test_utilization_ratio_in_message(self):
        with pytest.raises(AssertionError, match="1.250"):
            assert_capacity_exceeds_demand(80.0, 100.0)


class TestAssertSpacingValid:
    def test_valid_spacing(self):
        assert_spacing_valid(150.0, 450.0)  # max = min(337.5, 300) = 300

    def test_spacing_at_limit(self):
        assert_spacing_valid(300.0, 450.0)

    def test_spacing_exceeds_300_fails(self):
        with pytest.raises(AssertionError, match="Cl. 26.5.1.5"):
            assert_spacing_valid(350.0, 450.0)

    def test_spacing_exceeds_075d_fails(self):
        with pytest.raises(AssertionError, match="Cl. 26.5.1.5"):
            assert_spacing_valid(200.0, 250.0)  # max = min(187.5, 300) = 187.5

    def test_zero_spacing_fails(self):
        with pytest.raises(AssertionError, match="must be > 0"):
            assert_spacing_valid(0, 450.0)

    def test_negative_spacing_fails(self):
        with pytest.raises(AssertionError, match="must be > 0"):
            assert_spacing_valid(-10, 450.0)

    def test_label_in_message(self):
        with pytest.raises(AssertionError, match="stirrup"):
            assert_spacing_valid(350.0, 450.0, label="stirrup")


class TestAssertDimensionsPositive:
    def test_all_positive_passes(self):
        assert_dimensions_positive(b=300, d=450, D=500)

    def test_zero_fails(self):
        with pytest.raises(AssertionError, match="'b'.*must be > 0"):
            assert_dimensions_positive(b=0, d=450)

    def test_negative_fails(self):
        with pytest.raises(AssertionError, match="'d'.*must be > 0"):
            assert_dimensions_positive(b=300, d=-10)

    def test_single_dim(self):
        assert_dimensions_positive(width=250)

    def test_single_dim_negative(self):
        with pytest.raises(AssertionError, match="'width'"):
            assert_dimensions_positive(width=-5)
