"""Tests for SmartDesigner unified dashboard."""

import pytest

from structural_lib import beam_pipeline
from structural_lib.insights import (
    DashboardReport,
    SmartAnalysisSummary,
    SmartDesigner,
    quick_analysis,
)


def _base_params():
    """Standard beam parameters for testing."""
    return {
        "units": "IS456",
        "span_mm": 5000.0,
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
        "d_dash_mm": 50.0,
        "mu_knm": 120.0,
        "vu_kn": 85.0,
    }


def _run_pipeline(params):
    """Helper to run beam pipeline and get BeamDesignOutput."""
    return beam_pipeline.design_single_beam(
        units=params["units"],
        b_mm=params["b_mm"],
        D_mm=params["D_mm"],
        d_mm=params["d_mm"],
        cover_mm=params["D_mm"] - params["d_mm"],  # Calculate from D and d
        fck_nmm2=params["fck_nmm2"],
        fy_nmm2=params["fy_nmm2"],
        mu_knm=params["mu_knm"],
        vu_kn=params["vu_kn"],
        beam_id="test",
        story="TEST",
        span_mm=params["span_mm"],
        d_dash_mm=params.get("d_dash_mm", 50.0),
        asv_mm2=params.get("asv_mm2", 100.0),
    )


# =============================================================================
# SmartDesigner.analyze() Tests
# =============================================================================


def test_smart_designer_basic_analysis():
    """Test basic smart analysis with all features enabled."""
    params = _base_params()
    design = _run_pipeline(params)

    dashboard = SmartDesigner.analyze(
        design=design,
        span_mm=5000.0,
        mu_knm=120.0,
        vu_kn=85.0,
    )

    assert isinstance(dashboard, DashboardReport)
    assert isinstance(dashboard.summary, SmartAnalysisSummary)
    assert dashboard.cost is not None
    assert dashboard.suggestions is not None
    assert dashboard.sensitivity is not None
    assert dashboard.constructability is not None


def test_smart_designer_minimal_analysis():
    """Test analysis with only summary (all features disabled)."""
    params = _base_params()
    design = _run_pipeline(params)

    dashboard = SmartDesigner.analyze(
        design=design,
        span_mm=5000.0,
        mu_knm=120.0,
        vu_kn=85.0,
        include_cost=False,
        include_suggestions=False,
        include_sensitivity=False,
        include_constructability=False,
    )

    assert isinstance(dashboard, DashboardReport)
    assert dashboard.summary is not None
    assert dashboard.cost is None
    assert dashboard.suggestions is None
    assert dashboard.sensitivity is None
    assert dashboard.constructability is None


def test_smart_designer_selective_features():
    """Test analysis with selective feature inclusion."""
    params = _base_params()
    design = _run_pipeline(params)

    # Only cost and suggestions
    dashboard = SmartDesigner.analyze(
        design=design,
        span_mm=5000.0,
        mu_knm=120.0,
        vu_kn=85.0,
        include_cost=True,
        include_suggestions=True,
        include_sensitivity=False,
        include_constructability=False,
    )

    assert dashboard.cost is not None
    assert dashboard.suggestions is not None
    assert dashboard.sensitivity is None
    assert dashboard.constructability is None


def test_smart_designer_summary_structure():
    """Test summary structure and fields."""
    params = _base_params()
    design = _run_pipeline(params)

    dashboard = SmartDesigner.analyze(
        design=design, span_mm=5000.0, mu_knm=120.0, vu_kn=85.0
    )

    summary = dashboard.summary
    assert hasattr(summary, "design_status")
    assert summary.design_status in ["PASS", "WARNING", "FAIL"]
    assert 0.0 <= summary.safety_score <= 1.0
    assert 0.0 <= summary.cost_efficiency <= 1.0
    assert 0.0 <= summary.constructability <= 1.0
    assert 0.0 <= summary.robustness <= 1.0
    assert 0.0 <= summary.overall_score <= 1.0
    assert isinstance(summary.key_issues, list)
    assert isinstance(summary.quick_wins, list)


def test_smart_designer_cost_analysis():
    """Test cost analysis component."""
    params = _base_params()
    design = _run_pipeline(params)

    dashboard = SmartDesigner.analyze(
        design=design, span_mm=5000.0, mu_knm=120.0, vu_kn=85.0, include_cost=True
    )

    cost = dashboard.cost
    assert cost is not None
    assert cost.current_cost > 0
    assert cost.optimal_cost > 0
    assert cost.savings_percent >= 0
    assert isinstance(cost.alternatives, list)


def test_smart_designer_suggestions():
    """Test design suggestions component."""
    params = _base_params()
    design = _run_pipeline(params)

    dashboard = SmartDesigner.analyze(
        design=design,
        span_mm=5000.0,
        mu_knm=120.0,
        vu_kn=85.0,
        include_suggestions=True,
    )

    suggestions = dashboard.suggestions
    assert suggestions is not None
    assert suggestions.total_count >= 0
    assert suggestions.high_impact >= 0
    assert suggestions.medium_impact >= 0
    assert suggestions.low_impact >= 0
    assert (
        suggestions.total_count
        == suggestions.high_impact + suggestions.medium_impact + suggestions.low_impact
    )
    assert len(suggestions.top_3) <= 3


def test_smart_designer_sensitivity():
    """Test sensitivity analysis component."""
    params = _base_params()
    design = _run_pipeline(params)

    dashboard = SmartDesigner.analyze(
        design=design,
        span_mm=5000.0,
        mu_knm=120.0,
        vu_kn=85.0,
        include_sensitivity=True,
    )

    sensitivity = dashboard.sensitivity
    assert sensitivity is not None
    assert len(sensitivity.critical_parameters) > 0
    assert 0.0 <= sensitivity.robustness_score <= 1.0
    assert sensitivity.robustness_level in ["excellent", "good", "fair", "poor"]
    assert len(sensitivity.sensitivities) > 0


def test_smart_designer_constructability():
    """Test constructability assessment component."""
    params = _base_params()
    design = _run_pipeline(params)

    dashboard = SmartDesigner.analyze(
        design=design,
        span_mm=5000.0,
        mu_knm=120.0,
        vu_kn=85.0,
        include_constructability=True,
    )

    constructability = dashboard.constructability
    assert constructability is not None
    assert 0.0 <= constructability.score <= 1.0
    assert constructability.level in ["excellent", "good", "fair", "poor"]
    assert constructability.bar_complexity in [
        "very low",
        "low",
        "medium",
        "high",
    ]
    assert constructability.congestion_risk in [
        "very low",
        "low",
        "medium",
        "high",
    ]


def test_smart_designer_metadata():
    """Test metadata structure."""
    params = _base_params()
    design = _run_pipeline(params)

    dashboard = SmartDesigner.analyze(
        design=design, span_mm=5000.0, mu_knm=120.0, vu_kn=85.0
    )

    metadata = dashboard.metadata
    assert "timestamp" in metadata
    assert "library_version" in metadata
    assert "analysis_time_ms" in metadata
    assert metadata["analysis_time_ms"] > 0
    assert "included_analyses" in metadata
    assert "weights" in metadata


def test_smart_designer_custom_weights():
    """Test custom weight configuration."""
    params = _base_params()
    design = _run_pipeline(params)

    custom_weights = {
        "safety": 0.4,
        "cost": 0.3,
        "constructability": 0.2,
        "robustness": 0.1,
    }

    dashboard = SmartDesigner.analyze(
        design=design,
        span_mm=5000.0,
        mu_knm=120.0,
        vu_kn=85.0,
        weights=custom_weights,
    )

    assert dashboard.metadata["weights"] == custom_weights
    # Overall score should be weighted combination
    summary = dashboard.summary
    expected_score = (
        custom_weights["safety"] * summary.safety_score
        + custom_weights["cost"] * summary.cost_efficiency
        + custom_weights["constructability"] * summary.constructability
        + custom_weights["robustness"] * summary.robustness
    )
    assert abs(summary.overall_score - expected_score) < 0.01


def test_smart_designer_invalid_design():
    """Test error handling for invalid design."""
    params = _base_params()
    params["mu_knm"] = 1000.0  # Too high - will fail

    design = _run_pipeline(params)

    with pytest.raises(ValueError, match="No valid designs found"):
        SmartDesigner.analyze(design=design, span_mm=5000.0, mu_knm=1000.0, vu_kn=85.0)


# =============================================================================
# DashboardReport Output Tests
# =============================================================================


def test_dashboard_to_dict():
    """Test dashboard dictionary conversion."""
    params = _base_params()
    design = _run_pipeline(params)

    dashboard = SmartDesigner.analyze(
        design=design, span_mm=5000.0, mu_knm=120.0, vu_kn=85.0
    )

    data = dashboard.to_dict()
    assert isinstance(data, dict)
    assert "summary" in data
    assert "metadata" in data
    assert "cost" in data
    assert "suggestions" in data


def test_dashboard_to_json(tmp_path):
    """Test dashboard JSON export."""
    params = _base_params()
    design = _run_pipeline(params)

    dashboard = SmartDesigner.analyze(
        design=design, span_mm=5000.0, mu_knm=120.0, vu_kn=85.0
    )

    output_path = tmp_path / "dashboard.json"
    dashboard.to_json(str(output_path))

    assert output_path.exists()
    import json

    with output_path.open() as f:
        data = json.load(f)
    assert "summary" in data
    assert "metadata" in data


def test_dashboard_summary_text():
    """Test dashboard text summary generation."""
    params = _base_params()
    design = _run_pipeline(params)

    dashboard = SmartDesigner.analyze(
        design=design, span_mm=5000.0, mu_knm=120.0, vu_kn=85.0
    )

    text = dashboard.summary_text()
    assert isinstance(text, str)
    assert len(text) > 0
    assert "SMART DESIGN DASHBOARD" in text
    assert "Overall Score" in text
    assert "Safety" in text
    assert "Cost Efficiency" in text


def test_dashboard_summary_text_sections():
    """Test that text summary includes requested sections."""
    params = _base_params()
    design = _run_pipeline(params)

    dashboard = SmartDesigner.analyze(
        design=design,
        span_mm=5000.0,
        mu_knm=120.0,
        vu_kn=85.0,
        include_cost=True,
        include_suggestions=True,
        include_sensitivity=True,
        include_constructability=True,
    )

    text = dashboard.summary_text()
    assert "COST ANALYSIS" in text
    assert "DESIGN SUGGESTIONS" in text
    assert "SENSITIVITY ANALYSIS" in text
    assert "CONSTRUCTABILITY" in text


# =============================================================================
# quick_analysis() Tests
# =============================================================================


def test_quick_analysis():
    """Test quick_analysis helper function."""
    params = _base_params()
    design = _run_pipeline(params)

    text = quick_analysis(design, span_mm=5000.0, mu_knm=120.0, vu_kn=85.0)

    assert isinstance(text, str)
    assert len(text) > 0
    assert "SMART DESIGN DASHBOARD" in text
    # Quick analysis should include cost and suggestions, not sensitivity/constructability
    assert "COST ANALYSIS" in text
    assert "DESIGN SUGGESTIONS" in text


# =============================================================================
# Integration Tests
# =============================================================================


def test_smart_designer_deterministic():
    """Test that analysis produces deterministic results."""
    params = _base_params()
    design = _run_pipeline(params)

    dashboard1 = SmartDesigner.analyze(
        design=design, span_mm=5000.0, mu_knm=120.0, vu_kn=85.0
    )

    dashboard2 = SmartDesigner.analyze(
        design=design, span_mm=5000.0, mu_knm=120.0, vu_kn=85.0
    )

    # Summary scores should be identical
    assert dashboard1.summary.overall_score == dashboard2.summary.overall_score
    assert dashboard1.summary.safety_score == dashboard2.summary.safety_score

    # Cost should be identical
    if dashboard1.cost and dashboard2.cost:
        assert dashboard1.cost.current_cost == dashboard2.cost.current_cost
        assert dashboard1.cost.optimal_cost == dashboard2.cost.optimal_cost


def test_smart_designer_different_designs():
    """Test that different designs produce different analyses."""
    params1 = _base_params()
    design1 = _run_pipeline(params1)

    params2 = {**_base_params(), "b_mm": 350.0, "d_mm": 500.0, "D_mm": 550.0}
    design2 = _run_pipeline(params2)

    dashboard1 = SmartDesigner.analyze(
        design=design1, span_mm=5000.0, mu_knm=120.0, vu_kn=85.0
    )

    dashboard2 = SmartDesigner.analyze(
        design=design2, span_mm=5000.0, mu_knm=120.0, vu_kn=85.0
    )

    # Different designs should have different scores
    # (may not be true in all cases, but should be different for these specific cases)
    assert (
        dashboard1.summary.overall_score != dashboard2.summary.overall_score
        or dashboard1.cost.current_cost != dashboard2.cost.current_cost
    )


def test_smart_designer_large_span():
    """Test analysis with large span."""
    params = _base_params()
    params["mu_knm"] = 250.0
    params["d_mm"] = 600.0
    params["D_mm"] = 650.0
    params["span_mm"] = 8000.0
    params["vu_kn"] = 120.0
    design = _run_pipeline(params)

    dashboard = SmartDesigner.analyze(
        design=design, span_mm=8000.0, mu_knm=250.0, vu_kn=120.0
    )

    assert isinstance(dashboard, DashboardReport)
    assert dashboard.summary.design_status in ["PASS", "WARNING", "FAIL"]


def test_smart_designer_high_congestion():
    """Test constructability assessment for high congestion case."""
    params = _base_params()
    params["mu_knm"] = 180.0  # Higher moment -> more steel
    params["b_mm"] = 250.0  # Narrower section -> higher steel%
    design = _run_pipeline(params)

    dashboard = SmartDesigner.analyze(
        design=design,
        span_mm=5000.0,
        mu_knm=180.0,
        vu_kn=85.0,
        include_constructability=True,
    )

    # High steel percentage should result in lower constructability
    if dashboard.constructability:
        # Should detect congestion issues
        assert dashboard.constructability.score < 1.0
