"""
Validate insights features against sample vectors.

This script exercises predictive validation and sensitivity analysis
with a few representative beam cases.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from structural_lib.api import design_beam_is456
from structural_lib.errors import Severity
from structural_lib.insights import quick_precheck, sensitivity_analysis


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


def validate_sample_vectors():
    """Test insights features against sample vectors."""

    print("\n" + "=" * 70)
    print("VALIDATION: Insights Features vs Sample Vectors")
    print("=" * 70)

    vectors = [
        {
            "id": "G1",
            "mu_knm": 80.0,
            "vu_kn": 60.0,
            "description": "Low moment - light steel",
        },
        {
            "id": "G2",
            "mu_knm": 120.0,
            "vu_kn": 200.0,
            "description": "Moderate moment - typical steel",
        },
        {
            "id": "G3",
            "mu_knm": 160.0,
            "vu_kn": 120.0,
            "description": "Higher moment - heavy steel",
        },
    ]

    common = {
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }

    span_mm = common["d_mm"] * 11

    for vec in vectors:
        print(f"\n{'-' * 70}")
        print(f"Vector {vec['id']}: {vec['description']}")
        print(f"Mu = {vec['mu_knm']} kN·m, Vu = {vec['vu_kn']} kN")
        print(f"{'-' * 70}")

        print("\n1) PREDICTIVE VALIDATION")
        precheck = quick_precheck(
            span_mm=span_mm,
            b_mm=common["b_mm"],
            d_mm=common["d_mm"],
            D_mm=common["D_mm"],
            mu_knm=vec["mu_knm"],
            fck_nmm2=common["fck_nmm2"],
            fy_nmm2=common["fy_nmm2"],
        )
        print(format_precheck_report(precheck))

        print("\n2) ACTUAL DESIGN RESULT")
        result = design_beam_is456(
            units="IS456",
            mu_knm=vec["mu_knm"],
            vu_kn=vec["vu_kn"],
            b_mm=common["b_mm"],
            D_mm=common["D_mm"],
            d_mm=common["d_mm"],
            fck_nmm2=common["fck_nmm2"],
            fy_nmm2=common["fy_nmm2"],
        )

        print(f"  Status: {'SAFE' if result.is_ok else 'UNSAFE'}")
        print(f"  Ast required: {result.flexure.ast_required:.1f} mm²")
        print(f"  Utilization: {result.governing_utilization:.1%}")

        if vec["id"] == "G2":
            print("\n3) SENSITIVITY ANALYSIS (G2 only)")
            sensitivities, robustness = sensitivity_analysis(
                design_function=design_beam_is456,
                base_params={
                    "units": "IS456",
                    "mu_knm": vec["mu_knm"],
                    "vu_kn": vec["vu_kn"],
                    "b_mm": common["b_mm"],
                    "D_mm": common["D_mm"],
                    "d_mm": common["d_mm"],
                    "fck_nmm2": common["fck_nmm2"],
                    "fy_nmm2": common["fy_nmm2"],
                },
                parameters_to_vary=["d_mm", "b_mm", "mu_knm"],
            )
            print("\nSensitivity Results:")
            for item in sensitivities:
                print(f"  {item.parameter}: {item.sensitivity:.2f} ({item.impact})")
            print(f"  Robustness: {robustness.score:.2f} ({robustness.rating})")

    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    validate_sample_vectors()
