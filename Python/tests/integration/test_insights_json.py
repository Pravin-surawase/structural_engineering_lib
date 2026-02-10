"""Tests for JSON serialization of insights types.

Tests verify that all insights dataclasses can be converted to JSON-serializable
dictionaries for CLI output and API integration.
"""

import json

from structural_lib.api import design_beam_is456
from structural_lib.detailing import (
    BarArrangement,
    BeamDetailingResult,
    StirrupArrangement,
)
from structural_lib.insights import (
    calculate_constructability_score,
    quick_precheck,
    sensitivity_analysis,
)


def test_precheck_to_dict():
    """Verify PredictiveCheckResult.to_dict() produces valid JSON."""
    result = quick_precheck(
        span_mm=5000.0,
        b_mm=300.0,
        d_mm=450.0,
        D_mm=500.0,
        mu_knm=120.0,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
    )

    # Convert to dict
    data = result.to_dict()

    # Verify structure
    assert "check_time_ms" in data
    assert "risk_level" in data
    assert "warnings" in data
    assert "recommended_action" in data
    assert "heuristics_version" in data

    # Verify JSON serializable
    json_str = json.dumps(data)
    assert len(json_str) > 0

    # Verify round-trip
    parsed = json.loads(json_str)
    assert parsed["risk_level"] == data["risk_level"]
    assert isinstance(parsed["warnings"], list)


def test_sensitivity_to_dict():
    """Verify SensitivityResult.to_dict() produces valid JSON."""
    params = {
        "units": "IS456",
        "mu_knm": 120.0,
        "vu_kn": 80.0,
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }

    sensitivities, _ = sensitivity_analysis(design_beam_is456, params, ["d_mm", "b_mm"])

    # Convert to list of dicts
    data = [s.to_dict() for s in sensitivities]

    # Verify structure
    assert len(data) == 2
    for item in data:
        assert "parameter" in item
        assert "base_value" in item
        assert "perturbed_value" in item
        assert "base_utilization" in item
        assert "perturbed_utilization" in item
        assert "delta_utilization" in item
        assert "sensitivity" in item
        assert "impact" in item

    # Verify JSON serializable
    json_str = json.dumps(data)
    assert len(json_str) > 0

    # Verify round-trip
    parsed = json.loads(json_str)
    assert len(parsed) == 2
    assert parsed[0]["parameter"] in {"d_mm", "b_mm"}


def test_robustness_to_dict():
    """Verify RobustnessScore.to_dict() produces valid JSON."""
    params = {
        "units": "IS456",
        "mu_knm": 120.0,
        "vu_kn": 80.0,
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }

    _, robustness = sensitivity_analysis(design_beam_is456, params, ["d_mm", "b_mm"])

    # Convert to dict
    data = robustness.to_dict()

    # Verify structure
    assert "score" in data
    assert "rating" in data
    assert "vulnerable_parameters" in data
    assert "base_utilization" in data
    assert "sensitivity_count" in data

    # Verify JSON serializable
    json_str = json.dumps(data)
    assert len(json_str) > 0

    # Verify round-trip
    parsed = json.loads(json_str)
    assert parsed["rating"] in {"excellent", "good", "acceptable", "poor"}
    assert isinstance(parsed["vulnerable_parameters"], list)


def test_constructability_to_dict():
    """Verify ConstructabilityScore.to_dict() produces valid JSON."""
    # Get design result
    params = {
        "units": "IS456",
        "mu_knm": 120.0,
        "vu_kn": 80.0,
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }
    design = design_beam_is456(**params)

    # Create detailing
    bars = [
        BarArrangement(
            count=3,
            diameter=16.0,
            area_provided=603.0,
            spacing=140.0,
            layers=1,
        )
        for _ in range(3)
    ]
    stirrups = [
        StirrupArrangement(
            diameter=8.0,
            legs=2,
            spacing=150.0,
            zone_length=1500.0,
        )
        for _ in range(3)
    ]
    detailing = BeamDetailingResult(
        beam_id="B1",
        story="L1",
        b=300.0,
        D=500.0,
        span=5000.0,
        cover=40.0,
        top_bars=bars,
        bottom_bars=bars,
        stirrups=stirrups,
        ld_tension=0.0,
        ld_compression=0.0,
        lap_length=0.0,
        is_valid=True,
        remarks="",
    )

    # Calculate constructability
    result = calculate_constructability_score(design, detailing)

    # Convert to dict
    data = result.to_dict()

    # Verify structure
    assert "score" in data
    assert "rating" in data
    assert "factors" in data
    assert "overall_message" in data
    assert "version" in data

    # Verify factors structure
    assert isinstance(data["factors"], list)
    for factor in data["factors"]:
        assert "factor" in factor
        assert "score" in factor
        assert "penalty" in factor
        assert "message" in factor
        assert "recommendation" in factor

    # Verify JSON serializable
    json_str = json.dumps(data)
    assert len(json_str) > 0

    # Verify round-trip
    parsed = json.loads(json_str)
    assert parsed["rating"] in {"excellent", "good", "acceptable", "poor"}
    assert 0.0 <= parsed["score"] <= 100.0


def test_heuristic_warning_to_dict():
    """Verify HeuristicWarning.to_dict() handles enum conversion."""
    from structural_lib.core.errors import Severity
    from structural_lib.insights.types import HeuristicWarning

    warning = HeuristicWarning(
        type="depth",
        severity=Severity.WARNING,
        message="Depth is low",
        suggestion="Increase depth",
        rule_basis="IS 456 Cl. 23.2",
    )

    # Convert to dict
    data = warning.to_dict()

    # Verify structure
    assert "type" in data
    assert "severity" in data
    assert "message" in data
    assert "suggestion" in data
    assert "rule_basis" in data

    # Verify enum is converted to string
    assert isinstance(data["severity"], str)
    assert data["severity"] == "warning"

    # Verify JSON serializable
    json_str = json.dumps(data)
    assert len(json_str) > 0


def test_all_insights_json_serializable():
    """Integration test: verify complete insights workflow produces valid JSON."""
    params = {
        "units": "IS456",
        "mu_knm": 120.0,
        "vu_kn": 80.0,
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }

    # Run all insights
    precheck = quick_precheck(
        span_mm=5000.0,
        b_mm=params["b_mm"],
        d_mm=params["d_mm"],
        D_mm=params["D_mm"],
        mu_knm=params["mu_knm"],
        fck_nmm2=params["fck_nmm2"],
        fy_nmm2=params["fy_nmm2"],
    )

    design = design_beam_is456(**params)

    sensitivities, robustness = sensitivity_analysis(
        design_beam_is456, params, ["d_mm", "b_mm", "fck_nmm2"]
    )

    # Mock detailing
    bars = [
        BarArrangement(
            count=3, diameter=16.0, area_provided=603.0, spacing=140.0, layers=1
        )
        for _ in range(3)
    ]
    stirrups = [
        StirrupArrangement(diameter=8.0, legs=2, spacing=150.0, zone_length=1500.0)
        for _ in range(3)
    ]
    detailing = BeamDetailingResult(
        beam_id="B1",
        story="L1",
        b=300.0,
        D=500.0,
        span=5000.0,
        cover=40.0,
        top_bars=bars,
        bottom_bars=bars,
        stirrups=stirrups,
        ld_tension=0.0,
        ld_compression=0.0,
        lap_length=0.0,
        is_valid=True,
        remarks="",
    )

    constructability = calculate_constructability_score(design, detailing)

    # Convert all to JSON
    insights_data = {
        "precheck": precheck.to_dict(),
        "sensitivities": [s.to_dict() for s in sensitivities],
        "robustness": robustness.to_dict(),
        "constructability": constructability.to_dict(),
    }

    # Verify complete JSON is serializable
    json_str = json.dumps(insights_data, indent=2)
    assert len(json_str) > 0

    # Verify round-trip
    parsed = json.loads(json_str)
    assert "precheck" in parsed
    assert "sensitivities" in parsed
    assert "robustness" in parsed
    assert "constructability" in parsed

    # Verify sizes are reasonable (not empty)
    assert len(json_str) > 1000  # Should be >1KB for complete insights
