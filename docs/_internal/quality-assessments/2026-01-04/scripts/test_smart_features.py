"""Test smart/insights features."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
PYTHON_DIR = REPO_ROOT / "Python"
sys.path.insert(0, str(PYTHON_DIR))

from structural_lib import api, detailing
from structural_lib.insights import constructability, precheck, sensitivity

print("=" * 60)
print("SMART FEATURES ASSESSMENT")
print("=" * 60)

print("\n1. Precheck quick_precheck")
try:
    result = precheck.quick_precheck(
        span_mm=6000,
        b_mm=300,
        d_mm=500,
        D_mm=550,
        mu_knm=150,
        fck_nmm2=25,
        fy_nmm2=500,
    )
    print(f"   OK Risk Level: {result.risk_level}")
    print(f"   Warnings: {len(result.warnings)}")
    print(f"   Recommended action: {result.recommended_action}")
except Exception as exc:
    print(f"   ERROR Precheck failed: {exc}")

print("\n2. Sensitivity analysis")
try:
    base_params = {
        "units": "IS456",
        "mu_knm": 120,
        "vu_kn": 110,
        "b_mm": 300,
        "D_mm": 500,
        "d_mm": 450,
        "fck_nmm2": 25,
        "fy_nmm2": 500,
    }
    sens, robust = sensitivity.sensitivity_analysis(
        api.design_beam_is456,
        base_params,
        parameters_to_vary=["b_mm", "d_mm", "fck_nmm2"],
        perturbation=0.1,
    )
    print(f"   OK Sensitivity results: {len(sens)}")
    if sens:
        print(f"   Top parameter: {sens[0].parameter} (S={sens[0].sensitivity:.3f})")
    print(f"   Robustness: {robust.score:.2f} ({robust.rating})")
except Exception as exc:
    print(f"   ERROR Sensitivity failed: {exc}")

print("\n3. Constructability score")
try:
    design_result = api.design_beam_is456(
        units="IS456",
        mu_knm=120,
        vu_kn=110,
        b_mm=300,
        D_mm=500,
        d_mm=450,
        fck_nmm2=25,
        fy_nmm2=500,
    )
    detail = detailing.create_beam_detailing(
        beam_id="B1",
        story="L1",
        b=300,
        D=500,
        span=6000,
        cover=25,
        fck=25,
        fy=500,
        ast_start=design_result.flexure.ast_required,
        ast_mid=design_result.flexure.ast_required,
        ast_end=design_result.flexure.ast_required,
    )
    score = constructability.calculate_constructability_score(design_result, detail)
    print(f"   OK Score: {score.score:.1f} ({score.rating})")
    print(f"   Factors: {len(score.factors)}")
except Exception as exc:
    print(f"   ERROR Constructability failed: {exc}")

print("\n4. Additional smart features")
features_to_check = [
    "cost_optimization",
    "multi_objective_optimization",
    "ml_predictions",
    "design_suggestions",
    "failure_prediction",
    "code_compliance_ai",
]
for feature in features_to_check:
    if (
        hasattr(precheck, feature)
        or hasattr(sensitivity, feature)
        or hasattr(constructability, feature)
    ):
        print(f"   OK {feature} module found")
    else:
        print(f"   MISSING {feature} not implemented")

print("\n" + "=" * 60)
print("ASSESSMENT COMPLETE")
print("=" * 60)
