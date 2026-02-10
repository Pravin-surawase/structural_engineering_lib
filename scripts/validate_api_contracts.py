#!/usr/bin/env python3
"""
API Contract Validator.

Validates FastAPI endpoints against their OpenAPI contracts to detect:
- Missing endpoints (breaking change)
- Changed response schemas (breaking change)
- Missing required fields (breaking change)
- Added optional fields (non-breaking)
- Changed HTTP methods (breaking change)

Also validates API functions for FastAPI compatibility (--schema mode,
absorbed from validate_fastapi_schema.py):
- Parameter type annotations
- Return type annotations
- JSON serializability
- Manifest comparison

Usage:
    python scripts/validate_api_contracts.py              # Validate contracts
    python scripts/validate_api_contracts.py --save       # Save current as baseline
    python scripts/validate_api_contracts.py --diff       # Show detailed diff
    python scripts/validate_api_contracts.py --schema     # Validate API schema/types
    python scripts/validate_api_contracts.py --schema --manifest  # Compare with manifest
    python scripts/validate_api_contracts.py --schema --generate  # Generate route stubs

Exit Codes:
    0: All contracts valid / no breaking changes
    1: Breaking changes detected or schema issues found
    2: Error validating contracts
"""

from __future__ import annotations

import argparse
import inspect
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, get_type_hints

# Baseline contract file location
BASELINE_PATH = Path(__file__).parent.parent / "fastapi_app" / "openapi_baseline.json"
MANIFEST_PATH = Path(__file__).parent.parent / "docs" / "reference" / "api-manifest.json"

# Add project root for imports
PROJECT_ROOT = Path(__file__).parent.parent
PYTHON_DIR = PROJECT_ROOT / "Python"
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PYTHON_DIR))


def get_current_openapi_schema() -> dict[str, Any]:
    """Get current OpenAPI schema from FastAPI app."""
    try:
        from fastapi_app.main import app

        return app.openapi()
    except Exception as e:
        print(f"Error getting OpenAPI schema: {e}", file=sys.stderr)
        sys.exit(2)


def extract_contract_signature(schema: dict[str, Any]) -> dict[str, Any]:
    """Extract contract-relevant parts of OpenAPI schema."""
    signature = {
        "version": schema.get("info", {}).get("version", "unknown"),
        "endpoints": {},
        "schemas": {},
    }

    # Extract paths (endpoints)
    for path, methods in schema.get("paths", {}).items():
        signature["endpoints"][path] = {}
        for method, details in methods.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                signature["endpoints"][path][method] = {
                    "summary": details.get("summary", ""),
                    "parameters": [
                        {
                            "name": p.get("name"),
                            "in": p.get("in"),
                            "required": p.get("required", False),
                        }
                        for p in details.get("parameters", [])
                    ],
                    "response_codes": list(details.get("responses", {}).keys()),
                    "request_body_required": (
                        details.get("requestBody", {}).get("required", False)
                        if details.get("requestBody")
                        else None
                    ),
                }

    # Extract schemas (for request/response validation)
    for name, schema_def in schema.get("components", {}).get("schemas", {}).items():
        required_fields = schema_def.get("required", [])
        properties = list(schema_def.get("properties", {}).keys())
        signature["schemas"][name] = {
            "required": sorted(required_fields),
            "properties": sorted(properties),
        }

    return signature


def compare_contracts(
    baseline: dict[str, Any], current: dict[str, Any]
) -> tuple[list[str], list[str], list[str]]:
    """Compare baseline and current contracts.

    Returns:
        Tuple of (breaking_changes, warnings, info)
    """
    breaking: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    baseline_endpoints = baseline.get("endpoints", {})
    current_endpoints = current.get("endpoints", {})

    # Check removed endpoints (breaking)
    for path, methods in baseline_endpoints.items():
        if path not in current_endpoints:
            breaking.append(f"REMOVED ENDPOINT: {path}")
        else:
            for method in methods:
                if method not in current_endpoints[path]:
                    breaking.append(f"REMOVED METHOD: {method.upper()} {path}")

    # Check new endpoints (non-breaking)
    for path, methods in current_endpoints.items():
        if path not in baseline_endpoints:
            info.append(f"NEW ENDPOINT: {path}")
        else:
            for method in methods:
                if method not in baseline_endpoints[path]:
                    info.append(f"NEW METHOD: {method.upper()} {path}")

    # Check schemas
    baseline_schemas = baseline.get("schemas", {})
    current_schemas = current.get("schemas", {})

    for name, base_def in baseline_schemas.items():
        if name not in current_schemas:
            warnings.append(f"REMOVED SCHEMA: {name}")
            continue

        curr_def = current_schemas[name]

        # Check removed required fields (breaking)
        for field in base_def.get("required", []):
            if field not in curr_def.get("required", []):
                breaking.append(f"REMOVED REQUIRED FIELD: {name}.{field}")

        # Check removed properties (breaking)
        for prop in base_def.get("properties", []):
            if prop not in curr_def.get("properties", []):
                breaking.append(f"REMOVED PROPERTY: {name}.{prop}")

        # Check new required fields (breaking - for request schemas)
        for field in curr_def.get("required", []):
            if field not in base_def.get("required", []):
                warnings.append(f"NEW REQUIRED FIELD: {name}.{field}")

        # Check new optional fields (non-breaking)
        for prop in curr_def.get("properties", []):
            if prop not in base_def.get("properties", []):
                info.append(f"NEW PROPERTY: {name}.{prop}")

    return breaking, warnings, info


def save_baseline(schema: dict[str, Any]) -> None:
    """Save current schema as baseline."""
    signature = extract_contract_signature(schema)
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(BASELINE_PATH, "w") as f:
        json.dump(signature, f, indent=2, sort_keys=True)
    print(f"Baseline saved to: {BASELINE_PATH}")


def load_baseline() -> dict[str, Any] | None:
    """Load baseline schema if exists."""
    if not BASELINE_PATH.exists():
        return None
    with open(BASELINE_PATH) as f:
        return json.load(f)


def print_comparison(
    breaking: list[str], warnings: list[str], info: list[str], verbose: bool = False
) -> None:
    """Print comparison results."""
    if breaking:
        print("\n❌ BREAKING CHANGES:")
        for item in breaking:
            print(f"   - {item}")

    if warnings:
        print("\n⚠️  WARNINGS:")
        for item in warnings:
            print(f"   - {item}")

    if verbose and info:
        print("\nℹ️  INFO (non-breaking):")
        for item in info:
            print(f"   - {item}")

    print()
    if breaking:
        print(f"❌ {len(breaking)} breaking changes detected")
    elif warnings:
        print(f"⚠️  {len(warnings)} warnings, no breaking changes")
    else:
        print("✅ No breaking changes detected")


def validate_contracts(save: bool = False, diff: bool = False) -> int:
    """Main validation logic."""
    print("API Contract Validator")
    print("=" * 40)

    # Get current schema
    current_schema = get_current_openapi_schema()
    current_sig = extract_contract_signature(current_schema)

    if save:
        save_baseline(current_schema)
        return 0

    # Load baseline
    baseline = load_baseline()
    if baseline is None:
        print("No baseline found. Creating initial baseline...")
        save_baseline(current_schema)
        print("Run again after making changes to detect breaking changes.")
        return 0

    # Compare
    breaking, warnings, info = compare_contracts(baseline, current_sig)
    print_comparison(breaking, warnings, info, verbose=diff)

    # Count endpoints
    total_endpoints = sum(
        len(methods) for methods in current_sig["endpoints"].values()
    )
    total_schemas = len(current_sig["schemas"])
    print(f"\nCurrent API: {total_endpoints} endpoints, {total_schemas} schemas")

    if breaking:
        return 1
    return 0


# ═══════════════════════════════════════════════════════════════════════════
# SCHEMA VALIDATION (absorbed from validate_fastapi_schema.py)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class APIFunction:
    """Represents a public API function."""
    name: str
    signature: str
    parameters: dict
    return_type: str
    docstring: str | None
    is_fastapi_compatible: bool
    issues: list[str]


@dataclass
class SchemaValidationResult:
    """Result of API schema validation."""
    total_functions: int
    compatible_count: int
    incompatible_count: int
    missing_types: int
    functions: list[APIFunction]
    issues: list[str]


def _load_api_module():
    """Load the structural_lib.api module."""
    try:
        from structural_lib import api
        return api
    except ImportError as e:
        print(f"❌ Cannot import structural_lib.api: {e}")
        print("   Ensure you're running from project root with .venv activated")
        sys.exit(1)


def _get_type_name(type_hint) -> str:
    """Convert type hint to string representation."""
    if type_hint is None:
        return "None"
    if hasattr(type_hint, "__name__"):
        return type_hint.__name__
    return str(type_hint).replace("typing.", "")


def _check_fastapi_compatibility(func) -> tuple[bool, list[str]]:
    """Check if a function is FastAPI-compatible."""
    issues = []
    sig = inspect.signature(func)
    for param_name, param in sig.parameters.items():
        if param.annotation is inspect.Parameter.empty:
            issues.append(f"Parameter '{param_name}' lacks type annotation")
    try:
        hints = get_type_hints(func)
        if "return" not in hints:
            issues.append("Missing return type annotation")
    except Exception:
        if sig.return_annotation is inspect.Parameter.empty:
            issues.append("Missing return type annotation")
    docstring = func.__doc__ or ""
    if "DataFrame" in docstring and "to_dict" not in docstring:
        issues.append("Returns DataFrame - ensure .to_dict() is called")
    return len(issues) == 0, issues


def _analyze_function(func) -> APIFunction:
    """Analyze a function for FastAPI compatibility."""
    sig = inspect.signature(func)
    params = {}
    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue
        param_type = (
            _get_type_name(param.annotation)
            if param.annotation is not inspect.Parameter.empty
            else "Any"
        )
        default = None if param.default is inspect.Parameter.empty else repr(param.default)
        params[param_name] = {"type": param_type, "default": default}
    return_type = (
        _get_type_name(sig.return_annotation)
        if sig.return_annotation is not inspect.Parameter.empty
        else "Any"
    )
    is_compatible, issues = _check_fastapi_compatibility(func)
    return APIFunction(
        name=func.__name__,
        signature=str(sig),
        parameters=params,
        return_type=return_type,
        docstring=inspect.getdoc(func),
        is_fastapi_compatible=is_compatible,
        issues=issues,
    )


def _get_public_functions(module) -> list:
    """Get all public functions from a module."""
    functions = []
    names = module.__all__ if hasattr(module, "__all__") else [
        n for n in dir(module) if not n.startswith("_")
    ]
    for name in names:
        obj = getattr(module, name, None)
        if obj is not None and callable(obj) and not isinstance(obj, type):
            functions.append(obj)
    return functions


def _validate_api_schema() -> SchemaValidationResult:
    """Validate all public API functions for FastAPI compatibility."""
    api = _load_api_module()
    functions = _get_public_functions(api)
    analyzed = []
    all_issues = []
    compatible_count = 0
    missing_types = 0
    for func in functions:
        result = _analyze_function(func)
        analyzed.append(result)
        if result.is_fastapi_compatible:
            compatible_count += 1
        else:
            all_issues.extend([f"{result.name}: {issue}" for issue in result.issues])
            if "type annotation" in str(result.issues):
                missing_types += 1
    return SchemaValidationResult(
        total_functions=len(analyzed),
        compatible_count=compatible_count,
        incompatible_count=len(analyzed) - compatible_count,
        missing_types=missing_types,
        functions=analyzed,
        issues=all_issues,
    )


def _generate_route_stubs(result: SchemaValidationResult) -> str:
    """Generate FastAPI route stubs for all API functions."""
    lines = [
        "# Auto-generated FastAPI routes for structural_lib",
        "# Generated by validate_api_contracts.py --schema --generate",
        "",
        "from fastapi import FastAPI, HTTPException",
        "from pydantic import BaseModel",
        "from structural_lib import api",
        "",
        "app = FastAPI(",
        '    title="Structural Engineering API",',
        '    description="IS 456 beam design and analysis",',
        '    version="0.19.0"',
        ")",
        "",
    ]
    for func in result.functions:
        if func.parameters:
            lines.append(f"class {func.name.title().replace('_', '')}Request(BaseModel):")
            for pname, pinfo in func.parameters.items():
                py_type = pinfo["type"]
                default = pinfo["default"]
                if default:
                    lines.append(f"    {pname}: {py_type} = {default}")
                else:
                    lines.append(f"    {pname}: {py_type}")
            lines.append("")
        endpoint = func.name.replace("_", "-")
        lines.append(f'@app.post("/api/{endpoint}")')
        lines.append(
            f"async def {func.name}(request: {func.name.title().replace('_', '')}Request):"
        )
        lines.append('    """')
        if func.docstring:
            lines.append(f"    {func.docstring.split(chr(10))[0]}")
        lines.append('    """')
        lines.append("    try:")
        params = ", ".join([f"{p}=request.{p}" for p in func.parameters.keys()])
        lines.append(f"        result = api.{func.name}({params})")
        lines.append(
            "        return result.to_dict() if hasattr(result, 'to_dict') else result"
        )
        lines.append("    except Exception as e:")
        lines.append("        raise HTTPException(status_code=400, detail=str(e))")
        lines.append("")
    return "\n".join(lines)


def _compare_with_manifest(result: SchemaValidationResult) -> list[str]:
    """Compare current API with manifest file."""
    issues = []
    if not MANIFEST_PATH.exists():
        issues.append(f"API manifest not found at {MANIFEST_PATH}")
        issues.append("Run: .venv/bin/python scripts/generate_api_manifest.py")
        return issues
    try:
        with open(MANIFEST_PATH) as f:
            manifest = json.load(f)
    except json.JSONDecodeError:
        issues.append("API manifest is not valid JSON")
        return issues
    manifest_names = set(manifest.get("functions", {}).keys())
    current_names = {f.name for f in result.functions}
    missing = current_names - manifest_names
    if missing:
        issues.append(f"Functions in API but not in manifest: {missing}")
    removed = manifest_names - current_names
    if removed:
        issues.append(f"Functions in manifest but not in API: {removed}")
    return issues


def _print_schema_report(result: SchemaValidationResult, verbose: bool = False):
    """Print schema validation report."""
    print("=" * 60)
    print("FastAPI Schema Validation Report")
    print("=" * 60)
    print()
    pct = (
        (result.compatible_count / result.total_functions * 100)
        if result.total_functions > 0
        else 0
    )
    print(f"Total API functions: {result.total_functions}")
    print(f"FastAPI compatible:  {result.compatible_count} ({pct:.1f}%)")
    print(f"Need attention:      {result.incompatible_count}")
    print(f"Missing types:       {result.missing_types}")
    print()
    if result.compatible_count == result.total_functions:
        print("✅ All functions are FastAPI-compatible!")
    else:
        print("⚠️  Some functions need type annotations for FastAPI:")
        for issue in result.issues[:10]:
            print(f"   • {issue}")
        if len(result.issues) > 10:
            print(f"   ... and {len(result.issues) - 10} more issues")
    if verbose:
        print()
        print("-" * 60)
        print("Function Details:")
        print("-" * 60)
        for func in result.functions:
            status = "✅" if func.is_fastapi_compatible else "⚠️"
            print(f"\n{status} {func.name}{func.signature}")
            print(f"   Return: {func.return_type}")
            if func.issues:
                for issue in func.issues:
                    print(f"   ⚠️  {issue}")


def validate_schema(
    generate: bool = False,
    manifest: bool = False,
    verbose: bool = False,
    output: Path | None = None,
) -> int:
    """Run schema validation (absorbed from validate_fastapi_schema.py)."""
    result = _validate_api_schema()
    _print_schema_report(result, verbose)

    if generate:
        routes = _generate_route_stubs(result)
        if output:
            output.write_text(routes)
            print(f"\n✅ Routes written to {output}")
        else:
            print("\n" + "=" * 60)
            print("Generated FastAPI Routes:")
            print("=" * 60)
            print(routes)

    if manifest:
        manifest_issues = _compare_with_manifest(result)
        if manifest_issues:
            print("\n" + "=" * 60)
            print("Manifest Comparison:")
            print("=" * 60)
            for issue in manifest_issues:
                print(f"⚠️  {issue}")

    return 1 if result.incompatible_count > 0 else 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate FastAPI contracts for breaking changes and API schema compatibility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/validate_api_contracts.py              # Contract check\n"
            "  python scripts/validate_api_contracts.py --save       # Save baseline\n"
            "  python scripts/validate_api_contracts.py --schema     # Schema validation\n"
            "  python scripts/validate_api_contracts.py --schema -v  # Verbose schema\n"
            "  python scripts/validate_api_contracts.py --schema --manifest\n"
            "  python scripts/validate_api_contracts.py --schema --generate\n"
        ),
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save current schema as baseline",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Show detailed diff including non-breaking changes",
    )
    # Schema validation flags (absorbed from validate_fastapi_schema.py)
    parser.add_argument(
        "--schema",
        action="store_true",
        help="Validate API functions for FastAPI compatibility (types, annotations)",
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate FastAPI route stubs (requires --schema)",
    )
    parser.add_argument(
        "--manifest",
        action="store_true",
        help="Compare with API manifest (requires --schema)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file for generated routes",
    )

    args = parser.parse_args()

    if args.schema:
        return validate_schema(
            generate=args.generate,
            manifest=args.manifest,
            verbose=args.verbose,
            output=args.output,
        )
    else:
        return validate_contracts(save=args.save, diff=args.diff)


if __name__ == "__main__":
    sys.exit(main())
