"""Tests for rebar optimization functions.

Session 34 (Jan 23, 2026): Phase 2 - Testing extracted optimization functions.

These tests verify:
- calculate_constructability_score: Scoring algorithm
- suggest_optimal_rebar: Rebar selection optimization
"""

from __future__ import annotations

import pytest

from structural_lib.optimization import (
    ConstructabilityResult,
    RebarOptimizationResult,
    calculate_constructability_score,
    suggest_optimal_rebar,
)


class TestConstructabilityScore:
    """Tests for calculate_constructability_score function."""

    def test_high_constructability_few_bars(self):
        """Few bars should score higher."""
        result = calculate_constructability_score(
            bottom_bars=[(16, 3)],
            top_bars=[(12, 2)],
            stirrup_spacing_mm=200,
            b_mm=300,
        )
        assert isinstance(result, ConstructabilityResult)
        assert result.score >= 60  # Few bars + wide stirrups + single layer
        assert "Few bars" in result.notes

    def test_low_constructability_many_bars(self):
        """Many bars should score lower."""
        result = calculate_constructability_score(
            bottom_bars=[(16, 6), (16, 4)],  # 10 bars, 2 layers
            top_bars=[(12, 2)],
            stirrup_spacing_mm=75,  # Very tight
            b_mm=300,
        )
        assert result.score < 40
        assert "Multi-layer" in result.notes

    def test_uniform_diameter_bonus(self):
        """Same diameter throughout should get bonus."""
        result = calculate_constructability_score(
            bottom_bars=[(16, 4)],
            top_bars=[(16, 2)],  # Same as bottom
            stirrup_spacing_mm=150,
            b_mm=300,
        )
        assert "Uniform dia" in result.notes or "Same as top" in result.notes

    def test_wide_stirrup_spacing_bonus(self):
        """Wide stirrup spacing should get bonus."""
        result_wide = calculate_constructability_score(
            bottom_bars=[(16, 4)],
            top_bars=[(12, 2)],
            stirrup_spacing_mm=200,
            b_mm=300,
        )
        result_tight = calculate_constructability_score(
            bottom_bars=[(16, 4)],
            top_bars=[(12, 2)],
            stirrup_spacing_mm=80,
            b_mm=300,
        )
        assert result_wide.score > result_tight.score

    def test_to_dict_serializable(self):
        """Result should be JSON-serializable."""
        result = calculate_constructability_score(
            bottom_bars=[(16, 4)],
            top_bars=[(12, 2)],
            stirrup_spacing_mm=150,
            b_mm=300,
        )
        d = result.to_dict()
        assert isinstance(d, dict)
        assert "score" in d
        assert "summary" in d
        assert "notes" in d
        assert isinstance(d["notes"], list)

    def test_score_capped_at_100(self):
        """Score should not exceed 100."""
        result = calculate_constructability_score(
            bottom_bars=[(16, 2)],  # Very few bars
            top_bars=[(16, 2)],  # Same diameter
            stirrup_spacing_mm=250,  # Wide
            b_mm=400,  # Good spacing
        )
        assert result.score <= 100


class TestSuggestOptimalRebar:
    """Tests for suggest_optimal_rebar function."""

    def test_nominal_case(self):
        """Standard beam should return valid result."""
        result = suggest_optimal_rebar(
            b_mm=300,
            D_mm=450,
            mu_knm=80,
            vu_kn=60,
            fck=25,
            fy=500,
            cover_mm=40,
        )
        assert result is not None
        assert isinstance(result, RebarOptimizationResult)
        assert result.bottom_layer1_count >= 2
        assert result.bottom_layer1_dia in [10, 12, 16, 20, 25, 32]
        assert result.stirrup_dia in [8, 10, 12]
        assert result.stirrup_spacing > 0

    def test_high_moment_needs_more_steel(self):
        """High moment should result in more/larger bars."""
        result_low = suggest_optimal_rebar(
            b_mm=300,
            D_mm=450,
            mu_knm=50,
            vu_kn=30,
        )
        result_high = suggest_optimal_rebar(
            b_mm=300,
            D_mm=450,
            mu_knm=200,
            vu_kn=80,
        )
        assert result_low is not None
        assert result_high is not None
        # High moment should have more steel
        ast_low = result_low.ast_provided_mm2
        ast_high = result_high.ast_provided_mm2
        assert ast_high > ast_low

    def test_high_shear_tighter_stirrups(self):
        """High shear should result in tighter stirrup spacing."""
        result_low = suggest_optimal_rebar(
            b_mm=300,
            D_mm=450,
            mu_knm=80,
            vu_kn=30,
        )
        result_high = suggest_optimal_rebar(
            b_mm=300,
            D_mm=450,
            mu_knm=80,
            vu_kn=150,
        )
        assert result_low is not None
        assert result_high is not None
        # High shear should have smaller spacing or larger stirrup
        assert (
            result_high.stirrup_spacing <= result_low.stirrup_spacing
            or result_high.stirrup_dia >= result_low.stirrup_dia
        )

    def test_invalid_depth_returns_none(self):
        """Zero or negative effective depth should return None."""
        result = suggest_optimal_rebar(
            b_mm=300,
            D_mm=50,  # Too small
            mu_knm=80,
            vu_kn=60,
            cover_mm=60,  # Cover > depth
        )
        assert result is None

    def test_custom_bar_diameters(self):
        """Custom bar diameter list should be used."""
        result = suggest_optimal_rebar(
            b_mm=300,
            D_mm=450,
            mu_knm=80,
            vu_kn=60,
            bar_diameters=[12, 16],  # Limited options
        )
        assert result is not None
        assert result.bottom_layer1_dia in [12, 16]

    def test_custom_stirrup_options(self):
        """Custom stirrup options should be used."""
        result = suggest_optimal_rebar(
            b_mm=300,
            D_mm=450,
            mu_knm=80,
            vu_kn=60,
            stirrup_diameters=[10, 12],
            stirrup_spacings=[125, 175],
        )
        assert result is not None
        assert result.stirrup_dia in [10, 12]
        assert result.stirrup_spacing in [125, 175]

    def test_to_dict_serializable(self):
        """Result should be JSON-serializable."""
        result = suggest_optimal_rebar(
            b_mm=300,
            D_mm=450,
            mu_knm=80,
            vu_kn=60,
        )
        assert result is not None
        d = result.to_dict()
        assert isinstance(d, dict)
        assert "bottom_layer1_dia" in d
        assert "stirrup_spacing" in d
        assert "constructability_score" in d

    def test_to_session_state_dict(self):
        """Session state format should work for Streamlit."""
        result = suggest_optimal_rebar(
            b_mm=300,
            D_mm=450,
            mu_knm=80,
            vu_kn=60,
        )
        assert result is not None
        d = result.to_session_state_dict()
        assert "bottom_layer1_dia" in d
        assert "bottom_layer1_count" in d
        assert "stirrup_dia" in d
        assert "stirrup_spacing" in d
        # Should NOT have derived fields
        assert "ast_provided_mm2" not in d

    def test_minimum_steel_enforced(self):
        """Very low moment should still meet minimum steel."""
        result = suggest_optimal_rebar(
            b_mm=300,
            D_mm=450,
            mu_knm=10,
            vu_kn=10,  # Very low loads
        )
        assert result is not None
        # Should have at least 2 bars
        assert result.bottom_layer1_count >= 2

    def test_two_layer_for_heavy_reinforcement(self):
        """Heavy moment should use two layers if needed."""
        result = suggest_optimal_rebar(
            b_mm=200,  # Narrow beam
            D_mm=450,
            mu_knm=250,  # High moment
            vu_kn=100,
        )
        # For narrow beam with high moment, may need 2 layers
        if result is not None:
            assert result.ast_required_mm2 > 0

    def test_constructability_score_included(self):
        """Result should include constructability score."""
        result = suggest_optimal_rebar(
            b_mm=300,
            D_mm=450,
            mu_knm=80,
            vu_kn=60,
        )
        assert result is not None
        assert 0 <= result.constructability_score <= 100


class TestOptimizationIntegration:
    """Integration tests for optimization functions."""

    def test_constructability_matches_result(self):
        """Constructability score in result should match direct calculation."""
        result = suggest_optimal_rebar(
            b_mm=300,
            D_mm=450,
            mu_knm=80,
            vu_kn=60,
        )
        assert result is not None

        # Calculate independently
        direct_score = calculate_constructability_score(
            bottom_bars=[
                (result.bottom_layer1_dia, result.bottom_layer1_count),
                (result.bottom_layer2_dia, result.bottom_layer2_count),
            ],
            top_bars=[(result.top_dia, result.top_count)],
            stirrup_spacing_mm=result.stirrup_spacing,
            b_mm=300,
        )

        assert result.constructability_score == direct_score.score
