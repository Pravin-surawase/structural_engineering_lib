"""Feature completeness check using actual module functions."""

import importlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
PYTHON_DIR = REPO_ROOT / "Python"
sys.path.insert(0, str(PYTHON_DIR))

print("=" * 60)
print("FEATURE COMPLETENESS ASSESSMENT")
print("=" * 60)

features_by_area = {
    "Flexure": [
        (
            "Singly reinforced beams",
            "structural_lib.flexure",
            "design_singly_reinforced",
        ),
        (
            "Doubly reinforced beams",
            "structural_lib.flexure",
            "design_doubly_reinforced",
        ),
        ("Flanged beams (T/L)", "structural_lib.flexure", "design_flanged_beam"),
        ("Limiting moment", "structural_lib.flexure", "calculate_mu_lim"),
        ("Ast required", "structural_lib.flexure", "calculate_ast_required"),
    ],
    "Shear": [
        ("Shear design", "structural_lib.shear", "design_shear"),
        ("Shear stress", "structural_lib.shear", "calculate_tv"),
    ],
    "Detailing": [
        (
            "Development length",
            "structural_lib.detailing",
            "calculate_development_length",
        ),
        ("Lap length", "structural_lib.detailing", "calculate_lap_length"),
        ("Bar spacing", "structural_lib.detailing", "calculate_bar_spacing"),
        ("Min spacing check", "structural_lib.detailing", "check_min_spacing"),
        (
            "Side-face reinforcement",
            "structural_lib.detailing",
            "check_side_face_reinforcement",
        ),
        ("Create beam detailing", "structural_lib.detailing", "create_beam_detailing"),
    ],
    "Serviceability": [
        (
            "Deflection span/depth",
            "structural_lib.serviceability",
            "check_deflection_span_depth",
        ),
        ("Crack width", "structural_lib.serviceability", "check_crack_width"),
        (
            "Level B deflection",
            "structural_lib.serviceability",
            "check_deflection_level_b",
        ),
    ],
    "Compliance": [
        ("Compliance case", "structural_lib.compliance", "check_compliance_case"),
        ("Compliance report", "structural_lib.compliance", "check_compliance_report"),
    ],
}

for area, items in features_by_area.items():
    print(f"\n{area.upper()}")
    print("-" * 40)
    for label, module_name, func_name in items:
        try:
            module = importlib.import_module(module_name)
            getattr(module, func_name)
            print(f"   OK {label}")
        except Exception:
            print(f"   MISSING {label}")

print("\nCurrently Out of Scope (not implemented):")
out_of_scope = [
    "Column design",
    "Slab design (one-way)",
    "Slab design (two-way)",
    "Punching shear",
    "Torsion design",
    "Shear wall design",
    "Foundation design",
    "Seismic design",
    "Wind load calculations",
    "Multi-span beams",
]
for feature in out_of_scope:
    print(f"   MISSING {feature}")

print("\n" + "=" * 60)
print("ASSESSMENT COMPLETE")
print("=" * 60)
