"""Test current visualization capabilities."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
PYTHON_DIR = REPO_ROOT / "Python"
sys.path.insert(0, str(PYTHON_DIR))

print("=" * 60)
print("VISUAL CAPABILITIES ASSESSMENT")
print("=" * 60)

print("\n1. Checking for visualization modules...")
modules_to_check = ["matplotlib", "plotly", "seaborn", "PIL"]
for module in modules_to_check:
    try:
        __import__(module)
        mod = sys.modules[module]
        version = getattr(mod, "__version__", "unknown")
        print(f"   OK {module} available ({version})")
    except ImportError:
        print(f"   MISSING {module} not installed")

print("\n2. Checking structural_lib for plotting functions...")
try:
    from structural_lib import flexure, insights, report, report_svg, shear

    modules = [
        ("flexure", flexure),
        ("shear", shear),
        (
            "insights.precheck",
            insights.precheck if hasattr(insights, "precheck") else None,
        ),
        ("report", report),
        ("report_svg", report_svg),
    ]

    for name, module in modules:
        if module is None:
            continue
        funcs = [
            f
            for f in dir(module)
            if "plot" in f.lower() or "visual" in f.lower() or "chart" in f.lower()
        ]
        if funcs:
            print(f"   OK {name} has visualization-related functions: {funcs}")
        else:
            print(f"   NONE {name} has no visualization functions")

except Exception as exc:
    print(f"   ERROR checking structural_lib: {exc}")

print("\n3. Attempting to generate sample visualization...")
try:
    import matplotlib.pyplot as plt

    from structural_lib import flexure

    result = flexure.design_singly_reinforced(
        b=300, d=450, d_total=500, mu_knm=120, fck=25, fy=500
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    labels = ["Mu (kNm)", "Ast Req (mm^2)"]
    values = [120, result.ast_required]

    ax.bar(labels, values, color=["#1f77b4", "#ff7f0e"])
    ax.set_ylabel("Value")
    ax.set_title("Sample Beam Design Results")
    ax.grid(axis="y", alpha=0.3)

    output_path = (
        Path(__file__).resolve().parents[1] / "outputs" / "test_basic_visual.png"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    print(f"   OK Generated {output_path}")

except Exception as exc:
    print(f"   ERROR Could not generate visualization: {exc}")

print("\n" + "=" * 60)
print("ASSESSMENT COMPLETE")
print("=" * 60)
