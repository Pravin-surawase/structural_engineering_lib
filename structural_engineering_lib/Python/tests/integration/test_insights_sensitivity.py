"""Comprehensive tests for sensitivity analysis module.

Tests cover:
- Determinism (same inputs → same outputs)
- Physical validation (beam theory expectations)
- Edge cases (zero utilization, high utilization, parameter bounds)
- Robustness scoring accuracy
- Normalized sensitivity coefficients
"""

from structural_lib.api import design_beam_is456
from structural_lib.insights import sensitivity_analysis


def _base_params():
    """Standard test beam with moderate utilization (~70-80%)."""
    return {
        "units": "IS456",
        "mu_knm": 120.0,
        "vu_kn": 80.0,
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }


def _low_util_params():
    """Beam with low utilization (~30-40%) - very robust."""
    return {
        "units": "IS456",
        "mu_knm": 50.0,
        "vu_kn": 30.0,
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }


def _high_util_params():
    """Beam with high utilization (~95%) - fragile."""
    return {
        "units": "IS456",
        "mu_knm": 180.0,
        "vu_kn": 120.0,
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }


# ==============================================================================
# Determinism Tests
# ==============================================================================


def test_sensitivity_deterministic():
    """Verify same inputs produce same outputs (no randomness)."""
    params = _base_params()
    s1, r1 = sensitivity_analysis(design_beam_is456, params, ["d_mm", "b_mm"])
    s2, r2 = sensitivity_analysis(design_beam_is456, params, ["d_mm", "b_mm"])

    assert s1 == s2
    assert r1 == r2


# ==============================================================================
# Physical Validation Tests (Beam Theory)
# ==============================================================================


def test_sensitivity_depth_more_critical_than_width():
    """Depth should be more effective than width for flexure (beam theory)."""
    params = _base_params()
    sensitivities, _ = sensitivity_analysis(design_beam_is456, params, ["d_mm", "b_mm"])

    by_param = {item.parameter: item for item in sensitivities}

    # Depth sensitivity should be larger (more effective)
    assert abs(by_param["d_mm"].sensitivity) > abs(by_param["b_mm"].sensitivity)

    # For a flexure-critical beam, depth should be ~2x more effective
    # (utilization ∝ 1/d² for flexure vs 1/b for area)
    assert abs(by_param["d_mm"].sensitivity) >= 1.5 * abs(by_param["b_mm"].sensitivity)


def test_sensitivity_strength_reduces_utilization():
    """Increasing concrete strength should reduce utilization.

    Note: fy sensitivity can be positive in some cases because when fy increases,
    Ast decreases proportionally, but if the design is compression-controlled or
    governed by other checks, the net effect on utilization can be complex.
    """
    params = _base_params()
    sensitivities, _ = sensitivity_analysis(
        design_beam_is456, params, ["fck_nmm2", "fy_nmm2"]
    )

    by_param = {item.parameter: item for item in sensitivities}

    # fck should have negative sensitivity (increase → decrease utilization)
    assert (
        by_param["fck_nmm2"].sensitivity < 0
    ), "fck increase should reduce utilization"

    # fy sensitivity depends on governing failure mode
    # Just verify it's computed (can be positive or negative)
    assert "fy_nmm2" in by_param


def test_sensitivity_dimensional_consistency():
    """Normalized sensitivities should be dimensionless and comparable."""
    params = _base_params()
    sensitivities, _ = sensitivity_analysis(
        design_beam_is456, params, ["d_mm", "fck_nmm2", "mu_knm"]
    )

    # All sensitivities should be dimensionless numbers
    for s in sensitivities:
        # Sensitivity is (ΔU/U) / (Δp/p) - dimensionless
        # Typical range: -5.0 to +5.0 for 10% perturbation
        assert -10.0 < s.sensitivity < 10.0, f"{s.parameter} sensitivity out of range"

        # Delta utilization should be proportional to sensitivity
        # For 10% perturbation: ΔU/U ≈ sensitivity × 0.10
        expected_relative_change = abs(s.sensitivity * 0.10)
        actual_relative_change = abs(s.delta_utilization / s.base_utilization)

        # Allow 1% tolerance for rounding
        assert abs(expected_relative_change - actual_relative_change) < 0.01


# ==============================================================================
# Edge Case Tests
# ==============================================================================


def test_sensitivity_low_utilization_beam():
    """Low utilization beam should have excellent robustness."""
    params = _low_util_params()
    sensitivities, robustness = sensitivity_analysis(
        design_beam_is456, params, ["d_mm", "b_mm", "fck_nmm2"]
    )

    # Should have sensitivities computed
    assert len(sensitivities) == 3

    # Robustness should be high (can tolerate large variations)
    assert robustness.score > 0.5, "Low utilization should be robust"
    assert robustness.rating in {"excellent", "good"}

    # Base utilization should be low
    assert robustness.base_utilization < 0.5


def test_sensitivity_high_utilization_beam():
    """High utilization beam should have poor robustness."""
    params = _high_util_params()
    sensitivities, robustness = sensitivity_analysis(
        design_beam_is456, params, ["d_mm", "b_mm", "fck_nmm2"]
    )

    # Should have sensitivities computed
    assert len(sensitivities) == 3

    # Robustness should be low (little margin to failure)
    assert robustness.score < 0.5, "High utilization should be fragile"

    # Base utilization should be high
    assert robustness.base_utilization > 0.8


def test_sensitivity_failing_design():
    """Design already failing (util > 1.0) should handle gracefully."""
    params = {
        "units": "IS456",
        "mu_knm": 300.0,  # Very high moment
        "vu_kn": 150.0,
        "b_mm": 230.0,  # Small section
        "D_mm": 400.0,
        "d_mm": 350.0,
        "fck_nmm2": 20.0,
        "fy_nmm2": 415.0,
    }

    sensitivities, robustness = sensitivity_analysis(
        design_beam_is456, params, ["d_mm", "b_mm"]
    )

    # Should still compute sensitivities
    assert len(sensitivities) == 2

    # Robustness should be poor (already failing)
    assert robustness.score <= 0.2, "Failing design should have poor robustness"
    assert robustness.rating == "poor"


def test_sensitivity_small_perturbation():
    """Small perturbation should still produce valid sensitivities."""
    params = _base_params()
    sensitivities, robustness = sensitivity_analysis(
        design_beam_is456,
        params,
        ["d_mm", "b_mm"],
        perturbation=0.01,  # 1% perturbation instead of 10%
    )

    # Should have sensitivities computed
    assert len(sensitivities) == 2

    # Sensitivities should still be in reasonable range
    # (normalized, so independent of perturbation size)
    for s in sensitivities:
        assert -10.0 < s.sensitivity < 10.0

    # Robustness should be valid
    assert 0.0 <= robustness.score <= 1.0


# ==============================================================================
# Robustness Scoring Tests
# ==============================================================================


def test_robustness_score_bounds():
    """Robustness score should always be in [0, 1] range."""
    params = _base_params()
    _, robustness = sensitivity_analysis(
        design_beam_is456, params, ["d_mm", "b_mm", "fck_nmm2", "fy_nmm2"]
    )

    assert 0.0 <= robustness.score <= 1.0
    assert robustness.rating in {"excellent", "good", "acceptable", "poor"}
    assert robustness.base_utilization > 0
    assert robustness.sensitivity_count == 4


def test_robustness_vulnerable_parameters():
    """Vulnerable parameters should be identified correctly."""
    params = _base_params()
    sensitivities, robustness = sensitivity_analysis(
        design_beam_is456, params, ["d_mm", "b_mm", "fck_nmm2", "fy_nmm2"]
    )

    # Should identify parameters with high/medium/critical impact
    assert len(robustness.vulnerable_parameters) > 0

    # All vulnerable parameters should be in sensitivity results
    all_params = {s.parameter for s in sensitivities}
    for param in robustness.vulnerable_parameters:
        assert param in all_params


def test_robustness_increases_with_margin():
    """More margin to failure should increase robustness score."""
    # Test three utilization levels with same parameters (scaled moment)
    base = _base_params()

    low_params = {**base, "mu_knm": 50.0}  # ~30% util
    mid_params = {**base, "mu_knm": 120.0}  # ~75% util
    high_params = {**base, "mu_knm": 180.0}  # ~95% util

    _, r_low = sensitivity_analysis(design_beam_is456, low_params, ["d_mm"])
    _, r_mid = sensitivity_analysis(design_beam_is456, mid_params, ["d_mm"])
    _, r_high = sensitivity_analysis(design_beam_is456, high_params, ["d_mm"])

    # Robustness should decrease as utilization increases
    # (low and mid might both be capped at 1.0, but high should be lower)
    assert r_low.score >= r_mid.score >= r_high.score
    assert r_high.score < r_mid.score or r_mid.base_utilization > 0.5


# ==============================================================================
# Golden Vector Validation (IS 456 Reference)
# ==============================================================================


def test_sensitivity_golden_vector_example1():
    """Validate against IS 456 SP:16 Example 1 (simply supported beam).

    Reference beam from SP:16-1980 (updated to IS 456:2000):
    - Span: 5000 mm
    - b = 300 mm, D = 500 mm, d = 450 mm
    - fck = 25 MPa, fy = 500 MPa
    - Mu = 140 kNm (factored)

    Expected behavior:
    - Depth sensitivity should be negative (increase d → decrease util)
    - |S_d| > |S_b| (depth more effective than width)
    - Robustness should be "good" (moderate loading)
    """
    params = {
        "units": "IS456",
        "mu_knm": 140.0,
        "vu_kn": 85.0,
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }

    sensitivities, robustness = sensitivity_analysis(
        design_beam_is456, params, ["d_mm", "b_mm", "fck_nmm2", "fy_nmm2"]
    )

    by_param = {s.parameter: s for s in sensitivities}

    # Physical expectations
    assert by_param["d_mm"].sensitivity < 0, "Depth increase should reduce utilization"
    assert (
        by_param["fck_nmm2"].sensitivity < 0
    ), "Concrete strength increase should help"

    # Depth should be most critical
    assert abs(by_param["d_mm"].sensitivity) > abs(by_param["b_mm"].sensitivity)

    # Robustness should be good (not overloaded, not underutilized)
    assert robustness.score >= 0.4, "Moderate loading should have acceptable robustness"
    assert robustness.base_utilization < 0.95, "Should not be near failure"


# ==============================================================================
# Impact Classification Tests
# ==============================================================================


def test_sensitivity_impact_classification():
    """Verify impact levels are assigned correctly."""
    params = _base_params()
    sensitivities, _ = sensitivity_analysis(
        design_beam_is456, params, ["d_mm", "b_mm", "fck_nmm2", "fy_nmm2"]
    )

    # All sensitivities should have valid impact classification
    valid_impacts = {"critical", "high", "medium", "low"}
    for s in sensitivities:
        assert s.impact in valid_impacts

    # Sorted by absolute sensitivity (highest first)
    abs_sensitivities = [abs(s.sensitivity) for s in sensitivities]
    assert abs_sensitivities == sorted(abs_sensitivities, reverse=True)


def test_sensitivity_depth_more_critical():
    """Legacy test - depth should be more critical than width."""
    params = _base_params()
    sensitivities, robustness = sensitivity_analysis(
        design_beam_is456, params, ["d_mm", "b_mm"]
    )
    assert robustness.score >= 0.0
    assert robustness.score <= 1.0

    by_param = {item.parameter: item for item in sensitivities}
    assert abs(by_param["d_mm"].sensitivity) >= abs(by_param["b_mm"].sensitivity)
