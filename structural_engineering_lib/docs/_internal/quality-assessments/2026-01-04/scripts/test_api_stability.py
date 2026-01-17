"""Test if API is stable and usable for platform development."""

import inspect
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
PYTHON_DIR = REPO_ROOT / "Python"
sys.path.insert(0, str(PYTHON_DIR))

from structural_lib import compliance, detailing, flexure, serviceability, shear

print("=" * 60)
print("PLATFORM API ASSESSMENT")
print("=" * 60)

modules = [
    ("flexure", flexure),
    ("shear", shear),
    ("detailing", detailing),
    ("compliance", compliance),
    ("serviceability", serviceability),
]

for name, module in modules:
    print(f"\n{name.upper()} MODULE")
    print("-" * 40)

    public_funcs = [
        f for f in dir(module) if not f.startswith("_") and callable(getattr(module, f))
    ]

    print(f"Public functions: {len(public_funcs)}")

    for func_name in public_funcs[:5]:
        func = getattr(module, func_name)
        sig = inspect.signature(func)

        has_doc = func.__doc__ is not None and len(func.__doc__) > 10
        has_types = any(
            p.annotation != inspect.Parameter.empty
            for p in sig.parameters.values()
        )
        has_return_type = sig.return_annotation != inspect.Signature.empty

        status = "OK" if (has_doc and has_types and has_return_type) else "WARN" if has_doc else "FAIL"

        print(f"  {status} {func_name}()")
        if not has_doc:
            print("      Missing docstring")
        if not has_types:
            print("      Missing type hints")
        if not has_return_type:
            print("      Missing return type")

print("\n" + "=" * 60)
print("EXTENSIBILITY CHECK")
print("=" * 60)

print("\n1. Can developers import and use functions?")
try:
    from structural_lib.flexure import design_singly_reinforced

    result = design_singly_reinforced(
        b=300, d=450, d_total=500, mu_knm=120, fck=25, fy=500
    )
    print("   OK Basic import and usage works")
except Exception as exc:
    print(f"   ERROR Import failed: {exc}")

print("\n2. Are data structures accessible?")
try:
    print(f"   Result type: {type(result)}")
    print(f"   Fields: {list(result.__dict__.keys())}")
    print("   OK Data structures accessible")
except Exception as exc:
    print(f"   ERROR Data access failed: {exc}")

print("\n3. Can developers build on top?")
try:
    def my_custom_beam_designer(span, load, fck=25, fy=500):
        """Example of building on the platform."""
        from structural_lib.flexure import design_singly_reinforced

        mu = load * span**2 / 8 / 1_000_000  # kNmm -> kNm
        b = 300
        d = max(450, span / 15)
        D = d + 50

        result = design_singly_reinforced(
            b=b, d=d, d_total=D, mu_knm=mu, fck=fck, fy=fy
        )
        result.span = span
        result.load = load
        return result

    _ = my_custom_beam_designer(span=5000, load=20)
    print("   OK Custom wrapper works - platform is extensible")
except Exception as exc:
    print(f"   ERROR Extensibility test failed: {exc}")

print("\n" + "=" * 60)
print("ASSESSMENT COMPLETE")
print("=" * 60)
