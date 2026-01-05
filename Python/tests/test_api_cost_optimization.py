"""Integration tests for api.optimize_beam_cost() function.

These tests verify the API layer correctly orchestrates cost optimization
and returns properly formatted results.
"""

import pytest
from structural_lib import api


def test_api_optimize_beam_cost_basic():
    """Test basic cost optimization via API."""
    result = api.optimize_beam_cost(
        units="IS456",
        span_mm=5000,
        mu_knm=120,
        vu_kn=80,
        cover_mm=40,
    )

    # Check structure
    assert "optimal_design" in result
    assert "alternatives" in result
    assert "baseline_cost" in result
    assert "savings_amount" in result
    assert "savings_percent" in result
    assert "metadata" in result

    # Check optimal design has required fields
    opt = result["optimal_design"]
    assert "b_mm" in opt
    assert "D_mm" in opt
    assert "d_mm" in opt
    assert "fck_nmm2" in opt
    assert "fy_nmm2" in opt
    assert "cost_breakdown" in opt

    # Check cost breakdown
    cost = opt["cost_breakdown"]
    assert "total_cost" in cost
    assert "concrete_cost" in cost
    assert "steel_cost" in cost
    assert "formwork_cost" in cost
    assert "currency" in cost
    assert cost["currency"] == "INR"

    # Check metadata
    meta = result["metadata"]
    assert "candidates_evaluated" in meta
    assert "candidates_valid" in meta
    assert "computation_time_sec" in meta
    assert meta["candidates_evaluated"] > 0


def test_api_optimize_beam_cost_alternatives():
    """Test that alternatives are returned and valid."""
    result = api.optimize_beam_cost(
        units="IS456",
        span_mm=6000,
        mu_knm=150,
        vu_kn=100,
        cover_mm=40,
    )

    alternatives = result["alternatives"]
    assert len(alternatives) <= 3  # Should return up to 3 alternatives

    # Each alternative should have complete structure
    for alt in alternatives:
        if alt:  # Some may be None if fewer than 3 alternatives exist
            assert "b_mm" in alt
            assert "D_mm" in alt
            assert "cost_breakdown" in alt
            assert alt["cost_breakdown"]["total_cost"] > 0


def test_api_optimize_beam_cost_savings_calculation():
    """Test that savings are calculated correctly."""
    result = api.optimize_beam_cost(
        units="IS456",
        span_mm=5000,
        mu_knm=120,
        vu_kn=80,
        cover_mm=40,
    )

    optimal_cost = result["optimal_design"]["cost_breakdown"]["total_cost"]
    baseline_cost = result["baseline_cost"]
    savings_amount = result["savings_amount"]
    savings_percent = result["savings_percent"]

    # Verify savings calculation
    assert pytest.approx(savings_amount, rel=0.01) == baseline_cost - optimal_cost
    assert (
        pytest.approx(savings_percent, rel=0.1)
        == (savings_amount / baseline_cost) * 100
    )

    # Optimal should be cheaper than or equal to baseline
    assert optimal_cost <= baseline_cost


def test_api_optimize_beam_cost_small_span():
    """Test optimization with small span."""
    result = api.optimize_beam_cost(
        units="IS456",
        span_mm=3000,
        mu_knm=50,
        vu_kn=40,
        cover_mm=25,
    )

    opt = result["optimal_design"]
    assert opt["b_mm"] >= 200  # Minimum width
    assert opt["d_mm"] > 0
    assert opt["D_mm"] > opt["d_mm"]  # Overall depth > effective depth


def test_api_optimize_beam_cost_large_moment():
    """Test optimization with large moment."""
    result = api.optimize_beam_cost(
        units="IS456",
        span_mm=8000,
        mu_knm=400,
        vu_kn=150,
        cover_mm=40,
    )

    opt = result["optimal_design"]
    # Should produce a valid design
    assert opt["cost_breakdown"]["total_cost"] > 0
    # Higher grade likely needed
    assert opt["fck_nmm2"] in [25, 30]


def test_api_optimize_beam_cost_custom_cover():
    """Test optimization with custom cover."""
    result_25 = api.optimize_beam_cost(
        units="IS456",
        span_mm=5000,
        mu_knm=120,
        vu_kn=80,
        cover_mm=25,
    )

    result_50 = api.optimize_beam_cost(
        units="IS456",
        span_mm=5000,
        mu_knm=120,
        vu_kn=80,
        cover_mm=50,
    )

    # Higher cover should result in higher cost (deeper beam needed)
    cost_25 = result_25["optimal_design"]["cost_breakdown"]["total_cost"]
    cost_50 = result_50["optimal_design"]["cost_breakdown"]["total_cost"]
    assert cost_50 >= cost_25
