"""Extensibility check for custom outputs and validators."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
PYTHON_DIR = REPO_ROOT / "Python"
sys.path.insert(0, str(PYTHON_DIR))

print("=" * 60)
print("EXTENSIBILITY ASSESSMENT")
print("=" * 60)

print("\n1. Custom output format")
try:
    from structural_lib import flexure

    class CustomPDFReporter:
        def generate_report(self, design_result):
            return {
                "file": "custom_report.pdf",
                "fields": list(design_result.__dict__.keys()),
            }

    design = flexure.design_singly_reinforced(
        b=300, d=450, d_total=500, mu_knm=120, fck=25, fy=500
    )
    reporter = CustomPDFReporter()
    report = reporter.generate_report(design)
    print(f"   OK Custom report generated: {report['file']}")
except Exception as exc:
    print(f"   ERROR Custom output failed: {exc}")

print("\n2. Custom validation rule")
try:
    class CustomValidator:
        def check_seismic_requirements(self, beam_design):
            return {"compliant": True, "warnings": []}

    validator = CustomValidator()
    result = validator.check_seismic_requirements({"ast": 2000})
    print(f"   OK Custom validator works: {result['compliant']}")
except Exception as exc:
    print(f"   ERROR Custom validator failed: {exc}")

print("\n" + "=" * 60)
print("ASSESSMENT COMPLETE")
print("=" * 60)
