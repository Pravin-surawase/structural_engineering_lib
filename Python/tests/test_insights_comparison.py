"""Tests for comparison module (multi-design comparison, cost-aware sensitivity)."""

import pytest

from structural_lib.api import design_beam_is456
from structural_lib.insights import (
    ComparisonResult,
    CostProfile,
    CostSensitivityResult,
    DesignAlternative,
    compare_designs,
    cost_aware_sensitivity,
)


def _base_params():
    """Standard beam parameters for testing."""
    return {
        "units": "IS456",
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
        "d_dash_mm": 50.0,
        "mu_knm": 120.0,
        "vu_kn": 85.0,
    }


def _cost_profile():
    """Standard cost profile for testing."""
    return CostProfile()  # Use defaults


# =============================================================================
# Design Comparison Tests
# =============================================================================


def test_compare_two_designs():
    """Compare two design alternatives."""
    params1 = _base_params()
    result1 = design_beam_is456(**params1)
    alt1 = DesignAlternative(
        name="Option A: 300x450",
        parameters=params1,
        result=result1,
        cost=15000.0,
    )

    params2 = {**_base_params(), "b_mm": 350.0, "d_mm": 400.0}
    result2 = design_beam_is456(**params2)
    alt2 = DesignAlternative(
        name="Option B: 350x400",
        parameters=params2,
        result=result2,
        cost=16000.0,
    )

    comparison = compare_designs([alt1, alt2])

    assert isinstance(comparison, ComparisonResult)
    assert len(comparison.alternatives) == 2
    assert len(comparison.metrics) == 2
    assert len(comparison.ranking) == 2
    assert 0 <= comparison.best_alternative_idx < 2

    # Best design should have highest overall score
    best_idx = comparison.best_alternative_idx
    best_score = comparison.metrics[best_idx].overall_score
    for idx, metrics in enumerate(comparison.metrics):
        if idx != best_idx:
            assert best_score >= metrics.overall_score


def test_compare_three_designs():
    """Compare three design alternatives."""
    params1 = _base_params()
    params2 = {**_base_params(), "b_mm": 350.0}
    params3 = {**_base_params(), "d_mm": 500.0}

    result1 = design_beam_is456(**params1)
    result2 = design_beam_is456(**params2)
    result3 = design_beam_is456(**params3)

    alternatives = [
        DesignAlternative("A", params1, result1, cost=15000.0),
        DesignAlternative("B", params2, result2, cost=15500.0),
        DesignAlternative("C", params3, result3, cost=16200.0),
    ]

    comparison = compare_designs(alternatives)

    assert len(comparison.alternatives) == 3
    assert len(comparison.metrics) == 3
    assert len(comparison.ranking) == 3
    # Ranking should be valid indices
    assert set(comparison.ranking) == {0, 1, 2}


def test_compare_designs_empty_list():
    """Empty alternatives list should raise ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        compare_designs([])


def test_compare_designs_invalid_weights():
    """Weights not summing to 1.0 should raise ValueError."""
    params = _base_params()
    result = design_beam_is456(**params)
    alt = DesignAlternative("Test", params, result)

    with pytest.raises(ValueError, match="must sum to 1.0"):
        compare_designs(
            [alt],
            cost_weight=0.5,
            safety_weight=0.3,  # Sum = 0.9, not 1.0
            constructability_weight=0.1,
            robustness_weight=0.0,
        )


def test_comparison_metrics_structure():
    """Verify ComparisonMetrics structure."""
    params = _base_params()
    result = design_beam_is456(**params)
    alt = DesignAlternative("Test", params, result, cost=15000.0)

    comparison = compare_designs([alt])
    metrics = comparison.metrics[0]

    # All metrics should be in 0.0-1.0 range
    assert 0.0 <= metrics.structural_safety <= 1.0
    assert 0.0 <= metrics.cost_efficiency <= 1.0
    assert 0.0 <= metrics.constructability <= 1.0
    assert 0.0 <= metrics.robustness <= 1.0
    assert 0.0 <= metrics.overall_score <= 1.0

    # Weights should be stored
    assert "cost" in metrics.weights
    assert "safety" in metrics.weights
    assert "constructability" in metrics.weights
    assert "robustness" in metrics.weights


def test_comparison_without_cost():
    """Compare designs without cost data."""
    params1 = _base_params()
    params2 = {**_base_params(), "b_mm": 350.0}

    result1 = design_beam_is456(**params1)
    result2 = design_beam_is456(**params2)

    alt1 = DesignAlternative("A", params1, result1)  # No cost
    alt2 = DesignAlternative("B", params2, result2)  # No cost

    comparison = compare_designs([alt1, alt2])

    # Should still work with neutral cost efficiency
    assert comparison.metrics[0].cost_efficiency == 0.5
    assert comparison.metrics[1].cost_efficiency == 0.5


def test_comparison_ranking_order():
    """Ranking should be sorted by overall score (best first)."""
    # Create designs with different utilizations
    params1 = {**_base_params(), "mu_knm": 100.0}  # Lower util = higher safety
    params2 = {**_base_params(), "mu_knm": 150.0}  # Higher util = lower safety

    result1 = design_beam_is456(**params1)
    result2 = design_beam_is456(**params2)

    alt1 = DesignAlternative("Low Load", params1, result1, cost=14000.0)
    alt2 = DesignAlternative("High Load", params2, result2, cost=14000.0)

    comparison = compare_designs([alt1, alt2])

    # First in ranking should have highest score
    first_idx = comparison.ranking[0]
    second_idx = comparison.ranking[1]
    assert (
        comparison.metrics[first_idx].overall_score
        >= comparison.metrics[second_idx].overall_score
    )


# =============================================================================
# Cost-Aware Sensitivity Tests
# =============================================================================


def test_cost_aware_sensitivity_basic():
    """Basic cost-aware sensitivity analysis."""
    params = _base_params()
    costs = _cost_profile()

    results, base_cost = cost_aware_sensitivity(
        design_beam_is456, params, costs, parameters_to_vary=["d_mm", "b_mm"]
    )

    assert isinstance(results, list)
    assert len(results) == 2
    assert isinstance(base_cost, float)
    assert base_cost > 0

    for result in results:
        assert isinstance(result, CostSensitivityResult)
        assert result.parameter in ["d_mm", "b_mm"]
        assert isinstance(result.sensitivity, float)
        assert isinstance(result.cost_impact_per_percent, float)
        assert isinstance(result.cost_sensitivity, float)
        assert len(result.recommendation) > 0


def test_cost_sensitivity_has_structural_sensitivity():
    """Cost sensitivity should include structural sensitivity."""
    params = _base_params()
    costs = _cost_profile()

    results, _ = cost_aware_sensitivity(
        design_beam_is456, params, costs, parameters_to_vary=["d_mm"]
    )

    result = results[0]
    # Structural sensitivity should be negative (increasing depth helps)
    assert result.sensitivity < 0
    assert result.impact in ["critical", "high", "medium", "low"]


def test_cost_sensitivity_impact_classification():
    """Cost sensitivity should classify impact correctly."""
    params = _base_params()
    costs = _cost_profile()

    results, _ = cost_aware_sensitivity(
        design_beam_is456,
        params,
        costs,
        parameters_to_vary=["d_mm", "b_mm", "fck_nmm2"],
    )

    # All should have valid impact classification
    impacts = {r.impact for r in results}
    assert impacts.issubset({"critical", "high", "medium", "low"})


def test_cost_sensitivity_recommendation_format():
    """Recommendations should be clear strings."""
    params = _base_params()
    costs = _cost_profile()

    results, _ = cost_aware_sensitivity(
        design_beam_is456, params, costs, parameters_to_vary=["d_mm"]
    )

    rec = results[0].recommendation
    assert isinstance(rec, str)
    assert len(rec) > 10  # Should be meaningful
    # Should mention impact level
    assert any(word in rec.upper() for word in ["CRITICAL", "HIGH", "MEDIUM", "LOW"])


def test_cost_sensitivity_deterministic():
    """Same inputs should give same cost sensitivity."""
    params = _base_params()
    costs = _cost_profile()

    results1, cost1 = cost_aware_sensitivity(
        design_beam_is456, params, costs, parameters_to_vary=["d_mm"]
    )
    results2, cost2 = cost_aware_sensitivity(
        design_beam_is456, params, costs, parameters_to_vary=["d_mm"]
    )

    assert cost1 == cost2
    assert results1[0].sensitivity == results2[0].sensitivity
    assert results1[0].cost_sensitivity == results2[0].cost_sensitivity
    assert results1[0].recommendation == results2[0].recommendation


def test_cost_sensitivity_with_all_parameters():
    """Test with all default parameters."""
    params = _base_params()
    costs = _cost_profile()

    # Don't specify parameters_to_vary - should use all numeric params
    results, base_cost = cost_aware_sensitivity(design_beam_is456, params, costs)

    assert len(results) > 0
    assert base_cost > 0

    # Should include key structural parameters
    param_names = {r.parameter for r in results}
    assert "d_mm" in param_names
    assert "b_mm" in param_names


def test_cost_sensitivity_cost_increases_with_dimensions():
    """Cost should increase when dimensions increase."""
    params = _base_params()
    costs = _cost_profile()

    results, base_cost = cost_aware_sensitivity(
        design_beam_is456, params, costs, parameters_to_vary=["D_mm", "b_mm"]
    )

    # Both D_mm and b_mm should increase cost when increased
    for result in results:
        if result.parameter in ["D_mm", "b_mm"]:
            # Cost sensitivity should be positive (more dimension = more cost)
            assert result.cost_sensitivity > 0
            assert result.cost_impact_per_percent > 0


# =============================================================================
# Integration Tests
# =============================================================================


def test_comparison_with_cost_sensitivity():
    """Integration: Compare designs and analyze cost sensitivity."""
    params1 = _base_params()
    params2 = {**_base_params(), "b_mm": 350.0}

    result1 = design_beam_is456(**params1)
    result2 = design_beam_is456(**params2)

    costs = _cost_profile()

    # Compare designs
    alt1 = DesignAlternative("A", params1, result1, cost=15000.0)
    alt2 = DesignAlternative("B", params2, result2, cost=16000.0)
    comparison = compare_designs([alt1, alt2])

    # Analyze sensitivity for best design
    best_idx = comparison.best_alternative_idx
    best_params = comparison.alternatives[best_idx].parameters

    sens_results, _ = cost_aware_sensitivity(
        design_beam_is456, best_params, costs, parameters_to_vary=["d_mm", "b_mm"]
    )

    # Should have results
    assert len(sens_results) == 2
    assert all(isinstance(r, CostSensitivityResult) for r in sens_results)


def test_comparison_identifies_trade_offs():
    """Comparison should identify trade-offs between designs."""
    # Create designs with clear trade-offs
    params1 = {**_base_params(), "mu_knm": 100.0}  # Safer but may be over-designed
    params2 = {**_base_params(), "mu_knm": 140.0}  # More utilized but cheaper?

    result1 = design_beam_is456(**params1)
    result2 = design_beam_is456(**params2)

    alt1 = DesignAlternative("Conservative", params1, result1, cost=15500.0)
    alt2 = DesignAlternative("Economical", params2, result2, cost=15000.0)

    comparison = compare_designs([alt1, alt2])

    # Should have some trade-offs identified
    assert isinstance(comparison.trade_offs, list)
    # Trade-offs list may be empty or populated depending on metrics
    # Just verify it's a valid list of strings
    for trade_off in comparison.trade_offs:
        assert isinstance(trade_off, str)
        assert len(trade_off) > 0


# =============================================================================
# Edge Cases
# =============================================================================


def test_comparison_single_design():
    """Compare single design (degenerate case)."""
    params = _base_params()
    result = design_beam_is456(**params)
    alt = DesignAlternative("Only Option", params, result, cost=15000.0)

    comparison = compare_designs([alt])

    assert len(comparison.alternatives) == 1
    assert comparison.best_alternative_idx == 0
    assert len(comparison.ranking) == 1
    assert comparison.ranking[0] == 0


def test_cost_sensitivity_zero_perturbation_raises():
    """Zero perturbation should raise ValueError."""
    params = _base_params()
    costs = _cost_profile()

    # This should be caught by sensitivity_analysis
    with pytest.raises(ValueError, match="perturbation must be > 0"):
        cost_aware_sensitivity(
            design_beam_is456,
            params,
            costs,
            parameters_to_vary=["d_mm"],
            perturbation=0.0,
        )


def test_comparison_custom_weights():
    """Compare with custom weight priorities."""
    params1 = _base_params()
    params2 = {**_base_params(), "b_mm": 350.0}

    result1 = design_beam_is456(**params1)
    result2 = design_beam_is456(**params2)

    alt1 = DesignAlternative("A", params1, result1, cost=15000.0)
    alt2 = DesignAlternative("B", params2, result2, cost=14000.0)

    # Prioritize cost heavily
    comparison_cost = compare_designs(
        [alt1, alt2],
        cost_weight=0.7,
        safety_weight=0.2,
        constructability_weight=0.05,
        robustness_weight=0.05,
    )

    # Prioritize safety heavily
    comparison_safety = compare_designs(
        [alt1, alt2],
        cost_weight=0.1,
        safety_weight=0.7,
        constructability_weight=0.1,
        robustness_weight=0.1,
    )

    # Rankings might differ based on weights
    # Just verify both are valid
    assert 0 <= comparison_cost.best_alternative_idx < 2
    assert 0 <= comparison_safety.best_alternative_idx < 2
