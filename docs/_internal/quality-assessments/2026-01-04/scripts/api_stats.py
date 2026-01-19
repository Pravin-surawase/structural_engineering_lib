"""Compute API doc/type-hint coverage for core modules."""

import inspect
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
PYTHON_DIR = REPO_ROOT / "Python"
sys.path.insert(0, str(PYTHON_DIR))

from structural_lib import compliance, detailing, flexure, serviceability, shear

modules = [flexure, shear, detailing, compliance, serviceability]

for module in modules:
    funcs = [
        obj
        for name, obj in inspect.getmembers(module, inspect.isfunction)
        if obj.__module__ == module.__name__ and not name.startswith("_")
    ]
    if not funcs:
        print(f"{module.__name__}: no public functions")
        continue

    doc_count = 0
    typed_count = 0
    return_typed = 0
    for func in funcs:
        has_doc = func.__doc__ is not None and len(func.__doc__) > 10
        sig = inspect.signature(func)
        has_param_types = any(
            p.annotation != inspect.Parameter.empty for p in sig.parameters.values()
        )
        has_return = sig.return_annotation != inspect.Signature.empty
        if has_doc:
            doc_count += 1
        if has_param_types:
            typed_count += 1
        if has_return:
            return_typed += 1

    total = len(funcs)
    print(
        f"{module.__name__}: {total} funcs, docstrings {doc_count}/{total}, "
        f"param types {typed_count}/{total}, return types {return_typed}/{total}"
    )
