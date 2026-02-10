"""
Verification pack for insights module.

Tests insights functions against IS 456/SP:16 benchmark cases to ensure
accuracy and prevent regressions.

This module provides automated regression tests for:
- quick_precheck() - Heuristic validation against Table 23
- sensitivity_analysis() - Parameter sensitivity analysis
- calculate_constructability_score() - Construction ease assessment

Each test case is documented with IS 456/SP:16 references for traceability.
"""

import json
from pathlib import Path

import pytest

from structural_lib.services.api import design_beam_is456
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


def _load_cases():
    """Load benchmark cases from JSON file."""
    # Path to tests/data/ (two levels up from tests/integration/)
    path = Path(__file__).parent.parent / "data" / "insights_benchmark_cases.json"
    return json.loads(path.read_text())


def _create_detailing_from_spec(spec: dict) -> BeamDetailingResult:
    """Create BeamDetailingResult from JSON specification."""
    # Convert bar specs to BarArrangement objects
    top_bars = [
        BarArrangement(
            count=bar["count"],
            diameter=bar["diameter"],
            area_provided=bar["area_provided"],
            spacing=bar["spacing"],
            layers=bar["layers"],
        )
        for bar in spec["top_bars"]
    ]

    bottom_bars = [
        BarArrangement(
            count=bar["count"],
            diameter=bar["diameter"],
            area_provided=bar["area_provided"],
            spacing=bar["spacing"],
            layers=bar["layers"],
        )
        for bar in spec["bottom_bars"]
    ]

    stirrups = [
        StirrupArrangement(
            diameter=stir["diameter"],
            legs=stir["legs"],
            spacing=stir["spacing"],
            zone_length=stir["zone_length"],
        )
        for stir in spec["stirrups"]
    ]

    return BeamDetailingResult(
        beam_id=spec["beam_id"],
        story=spec["story"],
        b=spec["b"],
        D=spec["D"],
        span=spec["span"],
        cover=spec["cover"],
        top_bars=top_bars,
        bottom_bars=bottom_bars,
        stirrups=stirrups,
        ld_tension=spec["ld_tension"],
        ld_compression=spec["ld_compression"],
        lap_length=spec["lap_length"],
        is_valid=spec["is_valid"],
        remarks=spec["remarks"],
    )


# ==============================================================================
# Precheck Benchmark Tests
# ==============================================================================


@pytest.mark.parametrize(
    "case",
    [c for c in _load_cases()["cases"] if c["category"] == "precheck"],
    ids=lambda c: c["case_id"],
)
def test_precheck_benchmark(case):
    """Verify precheck against IS 456 benchmark cases."""
    result = quick_precheck(**case["inputs"])
    exp = case["expected"]

    # Risk level must match
    assert result.risk_level == exp["risk_level"], (
        f"Case {case['case_id']}: Expected risk {exp['risk_level']}, "
        f"got {result.risk_level}"
    )

    # Check warning count
    if "warning_count" in exp:
        assert len(result.warnings) == exp["warning_count"], (
            f"Case {case['case_id']}: Expected {exp['warning_count']} warnings, "
            f"got {len(result.warnings)}"
        )
    elif "warning_count_min" in exp:
        assert len(result.warnings) >= exp["warning_count_min"], (
            f"Case {case['case_id']}: Expected >= {exp['warning_count_min']} warnings, "
            f"got {len(result.warnings)}"
        )

    # Check for specific warning types
    if exp.get("has_deflection_warning"):
        assert any(
            w.type == "deflection_risk" for w in result.warnings
        ), f"Case {case['case_id']}: Expected deflection_risk warning"

    if exp.get("has_narrow_beam_warning"):
        assert any(
            w.type == "narrow_beam" for w in result.warnings
        ), f"Case {case['case_id']}: Expected narrow_beam warning"

    # Check recommended action if specified
    if "recommended_action" in exp:
        assert result.recommended_action == exp["recommended_action"], (
            f"Case {case['case_id']}: Expected action {exp['recommended_action']}, "
            f"got {result.recommended_action}"
        )


# ==============================================================================
# Sensitivity Analysis Benchmark Tests
# ==============================================================================


@pytest.mark.parametrize(
    "case",
    [c for c in _load_cases()["cases"] if c["category"] == "sensitivity"],
    ids=lambda c: c["case_id"],
)
def test_sensitivity_benchmark(case):
    """Verify sensitivity analysis against IS 456/SP:16 examples."""
    inputs = case["inputs"]
    sensitivities, robustness = sensitivity_analysis(
        design_beam_is456,
        inputs["base_params"],
        inputs["parameters_to_vary"],
        inputs.get("perturbation", 0.10),
    )

    exp = case["expected"]
    rob_exp = exp["robustness"]

    # Robustness score range check
    if "score_min" in rob_exp and "score_max" in rob_exp:
        assert rob_exp["score_min"] <= robustness.score <= rob_exp["score_max"], (
            f"Case {case['case_id']}: Robustness score {robustness.score:.3f} "
            f"not in range [{rob_exp['score_min']}, {rob_exp['score_max']}]"
        )

    # Robustness rating check
    if "rating" in rob_exp:
        assert robustness.rating == rob_exp["rating"], (
            f"Case {case['case_id']}: Expected rating {rob_exp['rating']}, "
            f"got {robustness.rating}"
        )
    elif "rating_options" in rob_exp:
        assert robustness.rating in rob_exp["rating_options"], (
            f"Case {case['case_id']}: Rating {robustness.rating} "
            f"not in {rob_exp['rating_options']}"
        )

    # Base utilization checks
    if "base_utilization_min" in rob_exp:
        assert robustness.base_utilization >= rob_exp["base_utilization_min"], (
            f"Case {case['case_id']}: Base util {robustness.base_utilization:.3f} "
            f"< {rob_exp['base_utilization_min']}"
        )

    if "base_utilization_max" in rob_exp:
        assert robustness.base_utilization <= rob_exp["base_utilization_max"], (
            f"Case {case['case_id']}: Base util {robustness.base_utilization:.3f} "
            f"> {rob_exp['base_utilization_max']}"
        )

    # Sensitivity parameter checks
    if "sensitivities" in exp:
        by_param = {s.parameter: s for s in sensitivities}

        for param, exp_sens in exp["sensitivities"].items():
            assert (
                param in by_param
            ), f"Case {case['case_id']}: Parameter {param} not in sensitivity results"

            actual = by_param[param]

            # Check sensitivity sign (physical validation)
            if "sensitivity_sign" in exp_sens:
                sign = exp_sens["sensitivity_sign"]
                if sign == "negative":
                    assert actual.sensitivity < 0, (
                        f"Case {case['case_id']}: {param} sensitivity should be negative, "
                        f"got {actual.sensitivity:.3f}"
                    )
                else:  # positive
                    assert actual.sensitivity > 0, (
                        f"Case {case['case_id']}: {param} sensitivity should be positive, "
                        f"got {actual.sensitivity:.3f}"
                    )

            # Check impact classification if specified
            if "impact" in exp_sens:
                assert actual.impact == exp_sens["impact"], (
                    f"Case {case['case_id']}: {param} expected impact {exp_sens['impact']}, "
                    f"got {actual.impact}"
                )


# ==============================================================================
# Constructability Benchmark Tests
# ==============================================================================


@pytest.mark.parametrize(
    "case",
    [c for c in _load_cases()["cases"] if c["category"] == "constructability"],
    ids=lambda c: c["case_id"],
)
def test_constructability_benchmark(case):
    """Verify constructability scoring against benchmark cases."""
    # Create design result
    design_params = case["inputs"]["design_params"]
    design = design_beam_is456(**design_params)

    # Create detailing from specification
    detailing = _create_detailing_from_spec(case["inputs"]["detailing"])

    result = calculate_constructability_score(design, detailing)
    exp = case["expected"]["constructability"]

    # Score range check
    if "score_min" in exp and "score_max" in exp:
        assert exp["score_min"] <= result.score <= exp["score_max"], (
            f"Case {case['case_id']}: Score {result.score:.1f} "
            f"not in range [{exp['score_min']}, {exp['score_max']}]"
        )
    elif "score_min" in exp:
        assert (
            result.score >= exp["score_min"]
        ), f"Case {case['case_id']}: Score {result.score:.1f} < {exp['score_min']}"
    elif "score_max" in exp:
        assert (
            result.score <= exp["score_max"]
        ), f"Case {case['case_id']}: Score {result.score:.1f} > {exp['score_max']}"

    # Rating check
    if "rating" in exp:
        assert result.rating == exp["rating"], (
            f"Case {case['case_id']}: Expected rating {exp['rating']}, "
            f"got {result.rating}"
        )
    elif "rating_options" in exp:
        assert result.rating in exp["rating_options"], (
            f"Case {case['case_id']}: Rating {result.rating} "
            f"not in {exp['rating_options']}"
        )

    # Factor-specific checks
    if exp.get("has_standard_sizes_bonus"):
        assert any(
            f.factor == "standard_sizes" and f.score > 0 for f in result.factors
        ), f"Case {case['case_id']}: Expected standard_sizes bonus"

    if exp.get("has_non_standard_penalty"):
        assert any(
            f.factor == "non_standard_sizes" and f.penalty < 0 for f in result.factors
        ), f"Case {case['case_id']}: Expected non_standard_sizes penalty"

    if exp.get("has_layer_penalty"):
        assert any(
            f.factor == "layers" and f.penalty < 0 for f in result.factors
        ), f"Case {case['case_id']}: Expected layers penalty"
