"""
Demo: Smart library features (Precheck + Sensitivity)

This demonstrates the new insights features:
1. Predictive validation (quick heuristic checks)
2. Sensitivity analysis (identify critical parameters)
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from structural_lib.api import design_beam_is456
from structural_lib.insights import quick_precheck, sensitivity_analysis
from structural_lib.errors import Severity


def format_precheck_report(result) -> str:
    """Format predictive check for display."""
    lines = []
    lines.append("=" * 60)
    lines.append("QUICK PRE-CHECK (Heuristic Validation)")
    lines.append("=" * 60)
    lines.append(f"Check time: {result.check_time_ms:.1f}ms")
    lines.append(f"Risk level: {result.risk_level}")
    lines.append(f"Recommendation: {result.recommended_action}")
    lines.append("")

    if not result.warnings:
        lines.append("✓ No issues detected - geometry looks reasonable")
    else:
        lines.append(f"Found {len(result.warnings)} potential issue(s):")
        lines.append("")
        for i, warning in enumerate(result.warnings, 1):
            severity_symbol = "!" if warning.severity == Severity.WARNING else "i"
            lines.append(
                f"{i}. {warning.type.replace('_', ' ').upper()} [{severity_symbol}]"
            )
            lines.append(f"   - Issue: {warning.message}")
            lines.append(f"   - Fix: {warning.suggestion}")
            lines.append(f"   - Basis: {warning.rule_basis}")
            lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


def format_sensitivity_report(sensitivities, robustness) -> str:
    """Format sensitivity analysis for display."""
    lines = []
    lines.append("=" * 60)
    lines.append("SENSITIVITY ANALYSIS")
    lines.append("=" * 60)
    lines.append("")

    if not sensitivities:
        lines.append("No sensitivity data available.")
        return "\n".join(lines)

    lines.append("Critical Parameters (ranked by impact):")
    lines.append("")

    for i, sens in enumerate(sensitivities[:5], 1):
        lines.append(f"{i}. {sens.parameter:<12} [{sens.impact.upper()}]")
        lines.append(
            f"   - +10% change: {sens.base_utilization:.1%} -> {sens.perturbed_utilization:.1%}"
        )
        lines.append(f"   - Sensitivity: {sens.sensitivity:.2f}")
        lines.append("")

    lines.append("-" * 60)
    lines.append("ROBUSTNESS ASSESSMENT")
    lines.append("-" * 60)
    lines.append(f"Score:  {robustness.score:.2f} ({robustness.rating.upper()})")

    if robustness.vulnerable_parameters:
        lines.append(f"Vulnerable to: {', '.join(robustness.vulnerable_parameters)}")

    lines.append("=" * 60)

    return "\n".join(lines)


def demo_predictive_validation():
    """Demo: Quick heuristic pre-checks."""
    print("\n" + "=" * 70)
    print("DEMO 1: PREDICTIVE VALIDATION (Heuristic Pre-Checks)")
    print("=" * 70)

    print("\nScenario A: Typical residential beam (should be fine)")
    print("-" * 70)
    result_a = quick_precheck(
        span_mm=5000,
        b_mm=230,
        d_mm=450,
        D_mm=500,
        mu_knm=120,
        fck_nmm2=25,
        fy_nmm2=500,
    )
    print(format_precheck_report(result_a))

    print("\nScenario B: Shallow beam (deflection risk)")
    print("-" * 70)
    result_b = quick_precheck(
        span_mm=6000,
        b_mm=230,
        d_mm=250,
        D_mm=300,
        mu_knm=180,
        fck_nmm2=25,
        fy_nmm2=500,
    )
    print(format_precheck_report(result_b))


def demo_sensitivity_analysis():
    """Demo: Sensitivity analysis with API design."""
    print("\n" + "=" * 70)
    print("DEMO 2: SENSITIVITY ANALYSIS (Critical Parameters)")
    print("=" * 70)

    base_params = {
        "units": "IS456",
        "mu_knm": 120,
        "vu_kn": 80,
        "b_mm": 230,
        "D_mm": 500,
        "d_mm": 450,
        "fck_nmm2": 25,
        "fy_nmm2": 500,
    }

    print("\nBase Design:")
    print(f"  Beam: {base_params['b_mm']}x{base_params['D_mm']} mm")
    print(f"  Mu: {base_params['mu_knm']} kN·m, Vu: {base_params['vu_kn']} kN")
    print(f"  Material: M{base_params['fck_nmm2']}, Fe{base_params['fy_nmm2']}")

    print("\nRunning sensitivity analysis (±10%)...")
    sensitivities, robustness = sensitivity_analysis(
        design_function=design_beam_is456,
        base_params=base_params,
        parameters_to_vary=["d_mm", "b_mm", "mu_knm"],
    )

    print("\n" + format_sensitivity_report(sensitivities, robustness))


def demo_combined_workflow():
    """Demo: Combined workflow (precheck -> design -> sensitivity)."""
    print("\n" + "=" * 70)
    print("DEMO 3: COMBINED WORKFLOW")
    print("=" * 70)

    design_params = {
        "span_mm": 5500,
        "b_mm": 300,
        "d_mm": 475,
        "D_mm": 525,
        "mu_knm": 150,
        "fck_nmm2": 30,
        "fy_nmm2": 500,
    }

    print("\nDesign Requirements:")
    for key, value in design_params.items():
        print(f"  {key}: {value}")

    print("\nSTEP 1: Quick Pre-Check")
    print("-" * 70)
    precheck = quick_precheck(**design_params)
    print(format_precheck_report(precheck))

    print("\nSTEP 2: Full Design Calculation")
    print("-" * 70)
    result = design_beam_is456(
        units="IS456",
        mu_knm=design_params["mu_knm"],
        vu_kn=120,
        b_mm=design_params["b_mm"],
        D_mm=design_params["D_mm"],
        d_mm=design_params["d_mm"],
        fck_nmm2=design_params["fck_nmm2"],
        fy_nmm2=design_params["fy_nmm2"],
    )

    print(f"  Status: {'SAFE' if result.is_ok else 'UNSAFE'}")
    print(f"  Ast required: {result.flexure.ast_required:.0f} mm²")
    print(f"  Utilization: {result.governing_utilization:.1%}")

    if result.is_ok:
        print("\nSTEP 3: Sensitivity Analysis")
        print("-" * 70)
        sensitivities, robustness = sensitivity_analysis(
            design_function=design_beam_is456,
            base_params={
                "units": "IS456",
                "mu_knm": design_params["mu_knm"],
                "vu_kn": 120,
                "b_mm": design_params["b_mm"],
                "D_mm": design_params["D_mm"],
                "d_mm": design_params["d_mm"],
                "fck_nmm2": design_params["fck_nmm2"],
                "fy_nmm2": design_params["fy_nmm2"],
            },
            parameters_to_vary=["d_mm", "b_mm", "mu_knm"],
        )
        print("\n" + format_sensitivity_report(sensitivities, robustness))


if __name__ == "__main__":
    print("\nSMART LIBRARY FEATURES DEMO")
    demo_predictive_validation()
    demo_sensitivity_analysis()
    demo_combined_workflow()
