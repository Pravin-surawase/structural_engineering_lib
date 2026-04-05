# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for IS 13920:2016 Cl 7.2.1 — Strong Column Weak Beam (SCWB) check.

Functions under test:
    - check_scwb (Cl 7.2.1)

Test types:
    1. Unit tests — passing case (columns stronger)
    2. Unit tests — failing case (beams stronger)
    3. Boundary test — exactly at 1.1 ratio
    4. Input validation — zero/negative inputs
    5. Custom factor test
    6. Result methods — is_safe(), to_dict(), summary()
"""

from __future__ import annotations

import pytest

from structural_lib.codes.is13920.joint import check_scwb

# =============================================================================
# 1. Passing Case — Columns stronger than beams
# =============================================================================


class TestSCWBPass:
    """ΣMc ≥ 1.1 × ΣMb — check should pass."""

    def test_columns_clearly_stronger(self) -> None:
        """Columns well above the 1.1× threshold."""
        result = check_scwb(
            column_moments_top_knm=200.0,
            column_moments_bottom_knm=200.0,
            beam_moments_left_knm=150.0,
            beam_moments_right_knm=150.0,
        )
        # ΣMc = 400, ΣMb = 300, required = 330, ratio = 400/330 ≈ 1.212
        assert result.is_satisfied is True
        assert result.is_safe() is True
        assert result.sum_column_capacity_knm == pytest.approx(400.0)
        assert result.sum_beam_capacity_knm == pytest.approx(300.0)
        assert result.required_column_capacity_knm == pytest.approx(330.0)
        assert result.ratio == pytest.approx(400.0 / 330.0, rel=1e-6)
        assert len(result.errors) == 0

    def test_asymmetric_beams(self) -> None:
        """Different beam capacities on left and right."""
        result = check_scwb(
            column_moments_top_knm=250.0,
            column_moments_bottom_knm=250.0,
            beam_moments_left_knm=100.0,
            beam_moments_right_knm=200.0,
        )
        # ΣMc = 500, ΣMb = 300, required = 330
        assert result.is_satisfied is True
        assert result.ratio == pytest.approx(500.0 / 330.0, rel=1e-6)

    def test_asymmetric_columns(self) -> None:
        """Different column capacities top and bottom."""
        result = check_scwb(
            column_moments_top_knm=300.0,
            column_moments_bottom_knm=100.0,
            beam_moments_left_knm=150.0,
            beam_moments_right_knm=150.0,
        )
        # ΣMc = 400, ΣMb = 300, required = 330
        assert result.is_satisfied is True


# =============================================================================
# 2. Failing Case — Beams stronger than columns
# =============================================================================


class TestSCWBFail:
    """ΣMc < 1.1 × ΣMb — check should fail."""

    def test_beams_clearly_stronger(self) -> None:
        """Beams much stronger — obvious SCWB violation."""
        result = check_scwb(
            column_moments_top_knm=100.0,
            column_moments_bottom_knm=100.0,
            beam_moments_left_knm=200.0,
            beam_moments_right_knm=200.0,
        )
        # ΣMc = 200, ΣMb = 400, required = 440, ratio = 200/440 ≈ 0.455
        assert result.is_satisfied is False
        assert result.is_safe() is False
        assert result.ratio == pytest.approx(200.0 / 440.0, rel=1e-6)
        assert len(result.errors) == 1
        assert result.errors[0].code == "E_SCWB_002"

    def test_marginally_below_threshold(self) -> None:
        """Just barely below the 1.1× threshold."""
        # ΣMb = 200, required = 220, ΣMc = 219 < 220
        result = check_scwb(
            column_moments_top_knm=109.0,
            column_moments_bottom_knm=110.0,
            beam_moments_left_knm=100.0,
            beam_moments_right_knm=100.0,
        )
        # ΣMc = 219, required = 220
        assert result.is_satisfied is False


# =============================================================================
# 3. Boundary Case — Exactly at 1.1 ratio
# =============================================================================


class TestSCWBBoundary:
    """ΣMc = 1.1 × ΣMb exactly — should pass (≥ not >)."""

    def test_exactly_at_threshold(self) -> None:
        """Exactly at the 1.1 boundary — should satisfy the check."""
        # ΣMb = 200, required = 220, ΣMc = 220
        result = check_scwb(
            column_moments_top_knm=110.0,
            column_moments_bottom_knm=110.0,
            beam_moments_left_knm=100.0,
            beam_moments_right_knm=100.0,
        )
        assert result.is_satisfied is True
        assert result.ratio == pytest.approx(1.0, rel=1e-6)
        assert len(result.errors) == 0

    def test_marginally_above_threshold(self) -> None:
        """Just barely above the 1.1× threshold."""
        result = check_scwb(
            column_moments_top_knm=110.5,
            column_moments_bottom_knm=110.0,
            beam_moments_left_knm=100.0,
            beam_moments_right_knm=100.0,
        )
        # ΣMc = 220.5, required = 220
        assert result.is_satisfied is True


# =============================================================================
# 4. Input Validation — Zero/negative inputs
# =============================================================================


class TestSCWBValidation:
    """Zero and negative inputs should raise ValueError."""

    def test_zero_column_top(self) -> None:
        with pytest.raises(ValueError, match="column_moments_top_knm"):
            check_scwb(0.0, 100.0, 100.0, 100.0)

    def test_negative_column_bottom(self) -> None:
        with pytest.raises(ValueError, match="column_moments_bottom_knm"):
            check_scwb(100.0, -50.0, 100.0, 100.0)

    def test_zero_beam_left(self) -> None:
        with pytest.raises(ValueError, match="beam_moments_left_knm"):
            check_scwb(100.0, 100.0, 0.0, 100.0)

    def test_negative_beam_right(self) -> None:
        with pytest.raises(ValueError, match="beam_moments_right_knm"):
            check_scwb(100.0, 100.0, 100.0, -10.0)

    def test_zero_factor(self) -> None:
        with pytest.raises(ValueError, match="factor"):
            check_scwb(100.0, 100.0, 100.0, 100.0, factor=0.0)

    def test_negative_factor(self) -> None:
        with pytest.raises(ValueError, match="factor"):
            check_scwb(100.0, 100.0, 100.0, 100.0, factor=-1.0)


# =============================================================================
# 5. Custom Factor
# =============================================================================


class TestSCWBCustomFactor:
    """Use a non-default SCWB factor."""

    def test_factor_1_2(self) -> None:
        """Use factor=1.2 — stricter requirement."""
        # ΣMb = 200, required = 240, ΣMc = 250
        result = check_scwb(
            column_moments_top_knm=125.0,
            column_moments_bottom_knm=125.0,
            beam_moments_left_knm=100.0,
            beam_moments_right_knm=100.0,
            factor=1.2,
        )
        assert result.is_satisfied is True
        assert result.factor == 1.2
        assert result.required_column_capacity_knm == pytest.approx(240.0)

    def test_factor_1_0(self) -> None:
        """Use factor=1.0 — equal capacity check (non-standard)."""
        # ΣMb = 200, required = 200, ΣMc = 200
        result = check_scwb(
            column_moments_top_knm=100.0,
            column_moments_bottom_knm=100.0,
            beam_moments_left_knm=100.0,
            beam_moments_right_knm=100.0,
            factor=1.0,
        )
        assert result.is_satisfied is True
        assert result.ratio == pytest.approx(1.0, rel=1e-6)

    def test_factor_1_2_fail(self) -> None:
        """factor=1.2 causes failure that would pass with default 1.1."""
        # ΣMb = 200, required@1.1 = 220, required@1.2 = 240, ΣMc = 230
        result = check_scwb(
            column_moments_top_knm=115.0,
            column_moments_bottom_knm=115.0,
            beam_moments_left_knm=100.0,
            beam_moments_right_knm=100.0,
            factor=1.2,
        )
        assert result.is_satisfied is False
        # Same inputs with default factor should pass
        result_default = check_scwb(115.0, 115.0, 100.0, 100.0)
        assert result_default.is_satisfied is True


# =============================================================================
# 6. Result Methods
# =============================================================================


class TestSCWBResultMethods:
    """Test is_safe(), to_dict(), summary() methods."""

    def test_to_dict_keys(self) -> None:
        result = check_scwb(200.0, 200.0, 150.0, 150.0)
        d = result.to_dict()
        expected_keys = {
            "sum_column_capacity_knm",
            "sum_beam_capacity_knm",
            "required_column_capacity_knm",
            "ratio",
            "factor",
            "is_satisfied",
            "clause",
            "errors",
            "warnings",
        }
        assert set(d.keys()) == expected_keys

    def test_summary_contains_pass(self) -> None:
        result = check_scwb(200.0, 200.0, 150.0, 150.0)
        assert "PASS" in result.summary()

    def test_summary_contains_fail(self) -> None:
        result = check_scwb(100.0, 100.0, 200.0, 200.0)
        assert "FAIL" in result.summary()

    def test_clause_in_result(self) -> None:
        result = check_scwb(200.0, 200.0, 150.0, 150.0)
        assert "7.2.1" in result.clause

    def test_frozen_result(self) -> None:
        """SCWBResult is frozen — attributes cannot be changed."""
        result = check_scwb(200.0, 200.0, 150.0, 150.0)
        with pytest.raises(AttributeError):
            result.is_satisfied = False  # type: ignore[misc]
