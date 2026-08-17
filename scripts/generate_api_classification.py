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
_ADVANCED_MODULE_PREFIXES = (
    "structural_lib.services.audit",
    "structural_lib.services.calculation_report",
    "structural_lib.services.costing",
    "structural_lib.services.multi_objective_optimizer",
)
_HOLD_MODULE_PREFIXES = (
    "structural_lib.services.etabs_import",
    "structural_lib.visualization",
    "structural_lib.codes.is456.load_analysis",
)
_CANONICAL_TASK_EXPORTS = frozenset({"design_beam_is456"})
_CANONICAL_SUPPORT_EXPORTS = frozenset(
    {"EffectiveDepthBasisV1", "EffectiveDepthResolutionV1"}
)


def _kind(value: object) -> str:
    if inspect.isclass(value):
        return "class"
    if inspect.isfunction(value) or inspect.isbuiltin(value):
        return "function"
    if inspect.ismodule(value):
        return "module"
    return "value"


def _claim_disposition(
    *,
    module_name: str,
    name: str,
    defined_in: str,
    declared_export: bool,
    canonical_task_exports: set[str],
    capability_bound_exports: set[str],
) -> str:
    if not declared_export:
        return "internal"
    if module_name == "structural_lib.api":
        return "compatibility"
    if name in canonical_task_exports:
        return "canonical"
    if name in _CANONICAL_SUPPORT_EXPORTS:
        return "canonical"
    if defined_in.startswith(_HOLD_MODULE_PREFIXES):
        return "hold"
    if defined_in.startswith(_ADVANCED_MODULE_PREFIXES):
        return "advanced"
    if name in capability_bound_exports:
        return "advanced"
    return "compatibility"


def _build_surface(
    module_name: str,
    export_class: str,
    canonical_task_exports: set[str],
    capability_bound_exports: set[str],
) -> dict[str, Any]:
    module = importlib.import_module(module_name)
    declared = tuple(getattr(module, "__all__", ()))
    declared_set = set(declared)
    records: list[dict[str, Any]] = []

    missing = sorted(name for name in declared_set if not hasattr(module, name))
    if missing:
        raise RuntimeError(f"{module_name} declares missing exports: {missing}")

    for name in sorted(declared_set):
        value = getattr(module, name)
        defined_in = getattr(value, "__module__", module_name)
        records.append(
            {
                "name": name,
                "qualified_name": f"{module_name}.{name}",
                "kind": _kind(value),
                "classification": export_class,
                "declared_export": True,
                "defined_in": defined_in,
                "claim_disposition": _claim_disposition(
                    module_name=module_name,
                    name=name,
                    defined_in=defined_in,
                    declared_export=True,
                    canonical_task_exports=canonical_task_exports,
                    capability_bound_exports=capability_bound_exports,
                ),
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
        defined_in = getattr(value, "__module__", module_name)
        records.append(
            {
                "name": name,
                "qualified_name": f"{module_name}.{name}",
                "kind": _kind(value),
                "classification": "internal",
                "declared_export": False,
                "defined_in": defined_in,
                "claim_disposition": "internal",
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
    from structural_lib.services.capabilities import get_supported_is456_capabilities

    capability_bound_exports = {
        workflow
        for capability in get_supported_is456_capabilities()
        for workflow in capability.public_workflows
    }
    canonical_task_exports = set(_CANONICAL_TASK_EXPORTS)
    missing_authority = canonical_task_exports - capability_bound_exports
    if missing_authority:
        raise RuntimeError(
            "Canonical task exports are absent from capability authority: "
            + ", ".join(sorted(missing_authority))
        )

    surfaces = [
        _build_surface(
            module_name,
            export_class,
            canonical_task_exports,
            capability_bound_exports,
        )
        for module_name, export_class in SURFACE_POLICY
    ]
    return {
        "schema_version": "2.0",
        "claim_surface_matrix_schema_version": "claim-surface-matrix/v1",
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "package_version": __version__,
        "release_channel": "alpha",
        "classifications": {
            "stable": "Reserved for a separately approved post-Alpha compatibility promise.",
            "preview": "Declared Alpha export; callable but subject to documented pre-1.0 change.",
            "compatibility": "Retained delegating facade; use the recommended root or service facade.",
            "internal": "Not declared in __all__; no public compatibility promise.",
        },
        "claim_dispositions": {
            "canonical": "Bounded task workflow listed by the capability authority.",
            "advanced": "Maintained specialist tool outside the small task API.",
            "compatibility": "Retained public surface without a canonical task claim.",
            "hold": "Callable preview surface that cannot support its broader advertised use until its named gate passes.",
            "internal": "Undeclared implementation detail.",
        },
        "canonical_task_exports": sorted(canonical_task_exports),
        "canonical_support_exports": sorted(_CANONICAL_SUPPORT_EXPORTS),
        "advanced_capability_exports": sorted(
            capability_bound_exports - canonical_task_exports
        ),
        "artifact_boundaries": {
            "wheel": ["structural_lib Python API", "structural_lib CLI"],
            "exact_head_application": ["FastAPI", "React"],
            "repository_clients": ["clients/python", "clients/typescript"],
            "not_in_wheel": ["fastapi_app", "react_app", "clients"],
        },
        "canonical_reference_journey": {
            "task_id": "design_beam_is456",
            "input_contract": "project-beam-design/v1",
            "effective_depth_contract": "effective-depth-basis/v1",
            "result_contract": "structural-result-envelope/v2",
            "problem_contract": "structural-problem/v1",
            "surfaces": [
                {
                    "surface": "python_root",
                    "locator": "structural_lib.design_beam_is456",
                    "artifact": "wheel",
                    "disposition": "canonical",
                },
                {
                    "surface": "python_service",
                    "locator": "structural_lib.services.api.design_beam_is456",
                    "artifact": "wheel",
                    "disposition": "canonical",
                },
                {
                    "surface": "python_compatibility",
                    "locator": "structural_lib.api.design_beam_is456",
                    "artifact": "wheel",
                    "disposition": "compatibility",
                },
                {
                    "surface": "cli",
                    "locator": "python -m structural_lib design",
                    "artifact": "wheel",
                    "disposition": "canonical",
                },
                {
                    "surface": "rest",
                    "locator": "POST /api/v1/design/beam",
                    "artifact": "exact_head_application",
                    "disposition": "canonical",
                },
                {
                    "surface": "workflow",
                    "locator": "is456.beam.review@1.1.0",
                    "artifact": "exact_head_application",
                    "disposition": "canonical",
                    "activation": "feature_gated",
                },
                {
                    "surface": "react_manual",
                    "locator": "/workbench/quick/manual",
                    "artifact": "exact_head_application",
                    "disposition": "canonical",
                },
                {
                    "surface": "react_catalog",
                    "locator": "/workbench/quick",
                    "artifact": "exact_head_application",
                    "disposition": "canonical",
                    "activation": "feature_gated",
                },
            ],
            "compatibility_holds": [
                {
                    "surface": "websocket_design",
                    "locator": "/ws/design/{session_id}",
                    "condition": "missing structural-result-envelope/v2",
                    "outcome": "HOLD",
                }
            ],
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
