"""Tests for cost optimization feature."""

from structural_lib.insights import optimize_beam_design
from structural_lib.services.costing import CostProfile, calculate_beam_cost
from structural_lib.services.optimization import optimize_beam_cost


def test_cost_profile_defaults():
    """Test default cost profile uses India CPWD 2023 rates."""
    profile = CostProfile()

    assert profile.currency == "INR"
    assert profile.concrete_costs[25] == 6700
    assert profile.steel_cost_per_kg == 72.0


def test_calculate_beam_cost_simple():
    """Test basic cost calculation."""
    profile = CostProfile()

    cost = calculate_beam_cost(
        b_mm=300,
        D_mm=450,
        span_mm=5000,
        ast_mm2=1500,
        fck_nmm2=25,
        steel_percentage=1.2,
        cost_profile=profile,
    )

    assert cost.total_cost > 0
    assert cost.concrete_cost > 0
    assert cost.steel_cost > 0
    assert cost.formwork_cost > 0


def test_optimize_beam_cost_residential():
    """Test optimization for typical residential beam."""
    result = optimize_beam_cost(span_mm=5000, mu_knm=120, vu_kn=80)

    assert result.optimal_candidate.is_valid
    assert result.optimal_candidate.cost_breakdown.total_cost > 0
    assert result.savings_percent > 0  # Should save vs conservative
    assert result.candidates_evaluated > 0


def test_optimize_beam_cost_heavy_commercial():
    """Test optimization for heavy commercial beam."""
    result = optimize_beam_cost(span_mm=8000, mu_knm=400, vu_kn=200)

    assert result.optimal_candidate.is_valid
    # Heavy beam should have larger section
    assert result.optimal_candidate.D_mm > 500


def test_cost_optimization_savings():
    """Verify cost optimization actually saves money."""
    result = optimize_beam_cost(span_mm=6000, mu_knm=180, vu_kn=100)

    # Should achieve some savings
    assert 5 <= result.savings_percent <= 25


def test_cost_optimization_alternatives():
    """Test that alternatives are provided."""
    result = optimize_beam_cost(span_mm=5000, mu_knm=120, vu_kn=80)

    assert len(result.alternatives) > 0
    # Alternatives should be more expensive than optimal
    for alt in result.alternatives:
        assert (
            alt.cost_breakdown.total_cost
            > result.optimal_candidate.cost_breakdown.total_cost
        )


def test_custom_cost_profile():
    """Test with custom regional costs."""
    custom_profile = CostProfile(
        concrete_costs={25: 7500, 30: 8000},
        steel_cost_per_kg=80,
        location_factor=1.2,  # 20% higher
    )

    result = optimize_beam_cost(
        span_mm=5000, mu_knm=120, vu_kn=80, cost_profile=custom_profile
    )

    # Should still find valid design
    assert result.optimal_candidate.is_valid
    # Cost should be higher due to higher rates
    assert result.optimal_candidate.cost_breakdown.total_cost > 10000


def test_api_function():
    """Test user-facing API function."""

    result = optimize_beam_design(span_mm=5000, mu_knm=120, vu_kn=80)

    assert result.optimal_candidate.is_valid
    assert result.savings_percent > 0
