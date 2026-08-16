#!/usr/bin/env python3
"""Generate or validate the Alpha public API classification registry.

The registry covers all declared exports and every public-looking callable on
the supported root and service facades plus the retained compatibility module.
Names outside ``__all__`` are classified as internal so they cannot silently
become an undocumented public surface.
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT

DEFAULT_OUT = REPO_ROOT / "docs/reference/api-classification.json"
SURFACE_POLICY = (
    ("structural_lib", "preview"),
    ("structural_lib.services.api", "preview"),
    ("structural_lib.api", "compatibility"),
)


def _kind(value: object) -> str:
    if inspect.isclass(value):
        return "class"
    if inspect.isfunction(value) or inspect.isbuiltin(value):
        return "function"
    if inspect.ismodule(value):
        return "module"
    return "value"


def _build_surface(module_name: str, export_class: str) -> dict[str, Any]:
    module = importlib.import_module(module_name)
    declared = tuple(getattr(module, "__all__", ()))
    declared_set = set(declared)
    records: list[dict[str, Any]] = []

    missing = sorted(name for name in declared_set if not hasattr(module, name))
    if missing:
        raise RuntimeError(f"{module_name} declares missing exports: {missing}")

    for name in sorted(declared_set):
        value = getattr(module, name)
        records.append(
            {
                "name": name,
                "qualified_name": f"{module_name}.{name}",
                "kind": _kind(value),
                "classification": export_class,
                "declared_export": True,
                "defined_in": getattr(value, "__module__", module_name),
            }
        )

    for name, value in sorted(vars(module).items()):
        if name.startswith("_") or name in declared_set:
            continue
        if not (
            inspect.isclass(value)
            or inspect.isfunction(value)
            or inspect.isbuiltin(value)
        ):
            continue
        records.append(
            {
                "name": name,
                "qualified_name": f"{module_name}.{name}",
                "kind": _kind(value),
                "classification": "internal",
                "declared_export": False,
                "defined_in": getattr(value, "__module__", module_name),
            }
        )

    return {
        "module": module_name,
        "export_classification": export_class,
        "declared_export_count": len(declared_set),
        "classified_symbol_count": len(records),
        "symbols": sorted(records, key=lambda item: item["name"]),
    }


def build_registry() -> dict[str, Any]:
    sys.path.insert(0, str(REPO_ROOT / "Python"))
    from structural_lib import __version__

    surfaces = [
        _build_surface(module_name, export_class)
        for module_name, export_class in SURFACE_POLICY
    ]
    return {
        "schema_version": "1.0",
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "package_version": __version__,
        "release_channel": "alpha",
        "classifications": {
            "stable": "Reserved for a separately approved post-Alpha compatibility promise.",
            "preview": "Declared Alpha export; callable but subject to documented pre-1.0 change.",
            "compatibility": "Retained delegating facade; use the recommended root or service facade.",
            "internal": "Not declared in __all__; no public compatibility promise.",
        },
        "stable_exports": [],
        "internal_policy": "Every public-looking callable outside __all__ is tracked as internal.",
        "surfaces": surfaces,
    }


def _normalized(registry: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in registry.items() if key != "generated"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    expected = build_registry()
    if args.check:
        if not args.out.exists():
            print(f"ERROR: missing API classification registry: {args.out}")
            return 1
        actual = json.loads(args.out.read_text(encoding="utf-8"))
        if _normalized(actual) != _normalized(expected):
            print("ERROR: API classification registry is out of date.")
            print(
                "Run: ./scripts/python_runtime.sh scripts/generate_api_classification.py"
            )
            return 1
        print("API classification registry is current.")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote API classification registry to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
