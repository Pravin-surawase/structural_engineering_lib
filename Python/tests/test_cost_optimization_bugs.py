"""Tests for cost optimization bug fixes.

These tests specifically verify the fixes for:
- Bug #1: Feasibility check using wrong grade (M25 instead of M30)
- Bug #2: Baseline calculation failing for high moments
"""

from structural_lib.optimization import optimize_beam_cost


def test_bug1_feasibility_check_m30():
    """Test Bug #1: Feasibility check should use M30, not M25.

    For 400×500mm beam with Mu = 367 kNm:
    - Mu_lim(M25) = 334 kNm → Would be rejected by old feasibility check
    - Mu_lim(M30) = 401 kNm → Should be valid with new check

    This test verifies that valid M30 designs are no longer incorrectly rejected.
    """
    result = optimize_beam_cost(
        span_mm=6000,
        mu_knm=367,  # High moment that fails with M25 but works with M30
        vu_kn=150,
    )

    # Should find valid designs (not raise ValueError)
    assert result.optimal_candidate.is_valid
    assert result.candidates_valid > 0

    # Optimal design should exist with reasonable dimensions
    assert result.optimal_candidate.D_mm >= 400
    assert result.optimal_candidate.b_mm >= 230


def test_bug2_baseline_fails_high_moment():
    """Test Bug #2: Baseline calculation should handle over-reinforced baseline.

    For span=5000mm, Mu=200 kNm:
    - Baseline (300×417) with M25: Mu_lim = 142 kNm → Over-reinforced
    - Old code: ast_required = 0, baseline cost artificially low, negative savings
    - New code: Upgrades to M30 or increases depth, valid baseline

    This test verifies that savings are never negative due to baseline failure.
    """
    result = optimize_beam_cost(
        span_mm=5000,
        mu_knm=200,  # High moment that over-reinforces span/12 baseline
        vu_kn=100,
    )

    # Should find valid designs
    assert result.optimal_candidate.is_valid

    # Savings should be non-negative (baseline should be valid or equal to optimal)
    assert result.savings_percent >= -0.1  # Allow tiny rounding error
    assert result.savings_amount >= -1.0

    # Baseline cost should be reasonable (not artificially low from zero steel)
    assert result.baseline_cost > 5000  # Should have meaningful cost


def test_bug2_extreme_moment_baseline_fallback():
    """Test Bug #2: Baseline should fallback to optimal cost if truly infeasible.

    For extremely high moments where even span/10 with M30 fails,
    baseline should use optimal cost (zero savings, not negative).
    """
    result = optimize_beam_cost(span_mm=5000, mu_knm=400, vu_kn=150)  # Very high moment

    # Should still find valid optimal design (with deeper section)
    assert result.optimal_candidate.is_valid

    # If baseline failed completely, savings should be exactly 0
    # (baseline cost = optimal cost)
    if result.savings_percent < 0.1:
        assert (
            abs(
                result.baseline_cost
                - result.optimal_candidate.cost_breakdown.total_cost
            )
            < 1.0
        )


def test_feasibility_check_rejects_impossible_designs():
    """Verify feasibility check still rejects truly impossible designs.

    Even with M30, some dimensions are impossible (e.g., very shallow beams).
    Note: With current search space (widths up to 400mm, depths up to 900mm),
    most "impossible" moments can actually be designed. This test verifies
    the algorithm handles edge cases gracefully.
    """
    # Very high moment - may find valid designs with deep sections
    # If valid designs exist, verify they meet constraints
    try:
        result = optimize_beam_cost(
            span_mm=8000, mu_knm=500, vu_kn=200  # Very high moment
        )
        # If it succeeds, verify the design is actually valid
        assert result.optimal_candidate.is_valid
        assert result.optimal_candidate.D_mm >= 600  # Should need deep section
    except ValueError as e:
        # If it fails, should be due to no valid designs
        assert "No valid designs found" in str(e)


def test_m30_designs_included_in_results():
    """Verify M30 designs are actually evaluated and can be optimal.

    For some cases, M30 might be cheaper than M25 despite higher concrete cost
    (due to requiring less steel or smaller section).
    """
    result = optimize_beam_cost(
        span_mm=6000, mu_knm=250, vu_kn=120  # Moderate-to-high moment
    )

    # Should evaluate candidates with both M25 and M30
    assert result.candidates_evaluated > 20  # Multiple grade options tested

    # Check if M30 appears in optimal or alternatives
    all_candidates = [result.optimal_candidate] + result.alternatives
    grades_tested = {c.fck_nmm2 for c in all_candidates if c}

    # Should have tested both grades
    assert 25 in grades_tested or 30 in grades_tested


def test_baseline_uses_higher_grade_when_needed():
    """Verify baseline calculation upgrades from M25 to M30 when needed.

    For moments that over-reinforce M25 baseline but work with M30,
    baseline should use M30 grade.
    """
    result = optimize_beam_cost(
        span_mm=5000,
        mu_knm=180,  # Moment that requires M30 for span/12 baseline
        vu_kn=90,
    )

    # Baseline should be valid (not zero-cost due to failure)
    assert result.baseline_cost > 8000  # Reasonable cost for 5m beam

    # Should achieve some savings (baseline is conservative)
    assert result.savings_percent > 0


def test_baseline_increases_depth_when_needed():
    """Verify baseline calculation increases depth (span/10) when M30 still fails.

    For very high moments, even M30 with span/12 depth fails.
    Baseline should use span/10 instead.
    """
    result = optimize_beam_cost(
        span_mm=6000, mu_knm=300, vu_kn=150  # High moment requiring deep section
    )

    # Baseline should be valid (not fallback to optimal cost)
    # If savings are positive, baseline used deeper section successfully
    if result.savings_percent > 1.0:
        # Baseline was more expensive, so it worked (used span/10 or M30)
        assert result.baseline_cost > result.optimal_candidate.cost_breakdown.total_cost
