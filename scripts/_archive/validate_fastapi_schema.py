#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
FastAPI Schema Validation Script (V3 Preparation)
==================================================

Validates that FastAPI routes match the structural_lib API surface.
This script is designed to catch API mismatches BEFORE runtime.

Usage:
    python scripts/validate_fastapi_schema.py                 # Validate all APIs
    python scripts/validate_fastapi_schema.py --generate      # Generate route stubs
    python scripts/validate_fastapi_schema.py --manifest      # Compare with API manifest
    python scripts/validate_fastapi_schema.py --verbose       # Detailed output

Exit Codes:
    0 - All validations passed
    1 - Validation errors found
    2 - Missing API coverage

V3 Context:
    This script prepares for the React + FastAPI migration by:
    1. Validating that all public library APIs can be wrapped
    2. Checking type annotations are FastAPI-compatible
    3. Generating OpenAPI-compatible route skeletons
    4. Ensuring response models are JSON-serializable

Author: AI Agent (V3 Foundation Session)
Created: 2026-01-24
"""

from __future__ import annotations

import argparse
import inspect
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import get_type_hints

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
PYTHON_DIR = PROJECT_ROOT / "Python"
MANIFEST_PATH = PROJECT_ROOT / "docs" / "reference" / "api-manifest.json"

# Add Python directory to path
sys.path.insert(0, str(PYTHON_DIR))


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
class ValidationResult:
    """Result of API validation."""
    total_functions: int
    compatible_count: int
    incompatible_count: int
    missing_types: int
    functions: list[APIFunction]
    issues: list[str]


def load_api_module():
    """Load the structural_lib.api module."""
    try:
        from structural_lib import api
        return api
    except ImportError as e:
        print(f"❌ Cannot import structural_lib.services.api: {e}")
        print("   Ensure you're running from project root with .venv activated")
        sys.exit(1)


def get_type_name(type_hint) -> str:
    """Convert type hint to string representation."""
    if type_hint is None:
        return "None"
    if hasattr(type_hint, "__name__"):
        return type_hint.__name__
    return str(type_hint).replace("typing.", "")


def check_fastapi_compatibility(func) -> tuple[bool, list[str]]:
    """
    Check if a function is FastAPI-compatible.

    FastAPI requirements:
    1. All parameters should have type annotations
    2. Return type should be annotated
    3. Complex types should be serializable
    """
    issues = []
    sig = inspect.signature(func)

    # Check parameter annotations
    for param_name, param in sig.parameters.items():
        if param.annotation is inspect.Parameter.empty:
            issues.append(f"Parameter '{param_name}' lacks type annotation")

    # Check return type annotation
    try:
        hints = get_type_hints(func)
        if "return" not in hints:
            issues.append("Missing return type annotation")
    except Exception:
        # get_type_hints can fail on some complex types
        if sig.return_annotation is inspect.Parameter.empty:
            issues.append("Missing return type annotation")

    # Check for non-serializable types (basic check)
    docstring = func.__doc__ or ""
    if "DataFrame" in docstring and "to_dict" not in docstring:
        issues.append("Returns DataFrame - ensure .to_dict() is called")

    return len(issues) == 0, issues


def analyze_function(func) -> APIFunction:
    """Analyze a function for FastAPI compatibility."""
    sig = inspect.signature(func)

    # Extract parameters
    params = {}
    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue
        param_type = get_type_name(param.annotation) if param.annotation is not inspect.Parameter.empty else "Any"
        default = None if param.default is inspect.Parameter.empty else repr(param.default)
        params[param_name] = {"type": param_type, "default": default}

    # Get return type
    return_type = get_type_name(sig.return_annotation) if sig.return_annotation is not inspect.Parameter.empty else "Any"

    # Check compatibility
    is_compatible, issues = check_fastapi_compatibility(func)

    return APIFunction(
        name=func.__name__,
        signature=str(sig),
        parameters=params,
        return_type=return_type,
        docstring=inspect.getdoc(func),
        is_fastapi_compatible=is_compatible,
        issues=issues
    )


def get_public_functions(module) -> list:
    """Get all public functions from a module."""
    functions = []

    # Check __all__ if defined
    if hasattr(module, "__all__"):
        names = module.__all__
    else:
        names = [name for name in dir(module) if not name.startswith("_")]

    for name in names:
        obj = getattr(module, name, None)
        if obj is None:
            continue
        if callable(obj) and not isinstance(obj, type):
            functions.append(obj)

    return functions


def validate_api() -> ValidationResult:
    """Validate all public API functions for FastAPI compatibility."""
    api = load_api_module()
    functions = get_public_functions(api)

    analyzed = []
    all_issues = []
    compatible_count = 0
    missing_types = 0

    for func in functions:
        result = analyze_function(func)
        analyzed.append(result)

        if result.is_fastapi_compatible:
            compatible_count += 1
        else:
            all_issues.extend([f"{result.name}: {issue}" for issue in result.issues])
            if "type annotation" in str(result.issues):
                missing_types += 1

    return ValidationResult(
        total_functions=len(analyzed),
        compatible_count=compatible_count,
        incompatible_count=len(analyzed) - compatible_count,
        missing_types=missing_types,
        functions=analyzed,
        issues=all_issues
    )


def generate_route_stubs(result: ValidationResult) -> str:
    """Generate FastAPI route stubs for all API functions."""
    lines = [
        "# Auto-generated FastAPI routes for structural_lib",
        "# Generated by validate_fastapi_schema.py",
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
        # Generate request model if needed
        if func.parameters:
            lines.append(f"class {func.name.title().replace('_', '')}Request(BaseModel):")
            for param_name, param_info in func.parameters.items():
                py_type = param_info["type"]
                default = param_info["default"]
                if default:
                    lines.append(f"    {param_name}: {py_type} = {default}")
                else:
                    lines.append(f"    {param_name}: {py_type}")
            lines.append("")

        # Generate route
        endpoint = func.name.replace("_", "-")
        lines.append(f'@app.post("/api/{endpoint}")')
        lines.append(f"async def {func.name}(request: {func.name.title().replace('_', '')}Request):")
        lines.append(f'    """')
        if func.docstring:
            lines.append(f"    {func.docstring.split(chr(10))[0]}")
        lines.append(f'    """')
        lines.append(f"    try:")
        params = ", ".join([f"{p}=request.{p}" for p in func.parameters.keys()])
        lines.append(f"        result = api.{func.name}({params})")
        lines.append(f"        return result.to_dict() if hasattr(result, 'to_dict') else result")
        lines.append(f"    except Exception as e:")
        lines.append(f'        raise HTTPException(status_code=400, detail=str(e))')
        lines.append("")

    return "\n".join(lines)


def compare_with_manifest(result: ValidationResult) -> list[str]:
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

    # Check for missing in manifest
    missing = current_names - manifest_names
    if missing:
        issues.append(f"Functions in API but not in manifest: {missing}")

    # Check for removed from API
    removed = manifest_names - current_names
    if removed:
        issues.append(f"Functions in manifest but not in API: {removed}")

    return issues


def print_report(result: ValidationResult, verbose: bool = False):
    """Print validation report."""
    print("=" * 60)
    print("FastAPI Schema Validation Report")
    print("=" * 60)
    print()

    # Summary
    pct = (result.compatible_count / result.total_functions * 100) if result.total_functions > 0 else 0
    print(f"Total API functions: {result.total_functions}")
    print(f"FastAPI compatible:  {result.compatible_count} ({pct:.1f}%)")
    print(f"Need attention:      {result.incompatible_count}")
    print(f"Missing types:       {result.missing_types}")
    print()

    # Compatibility status
    if result.compatible_count == result.total_functions:
        print("✅ All functions are FastAPI-compatible!")
    else:
        print("⚠️  Some functions need type annotations for FastAPI:")
        for issue in result.issues[:10]:  # Limit output
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


def main():
    parser = argparse.ArgumentParser(
        description="Validate API for FastAPI compatibility (V3 preparation)"
    )
    parser.add_argument("--generate", action="store_true",
                       help="Generate FastAPI route stubs")
    parser.add_argument("--manifest", action="store_true",
                       help="Compare with API manifest")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--output", "-o", type=Path,
                       help="Output file for generated routes")

    args = parser.parse_args()

    # Run validation
    result = validate_api()

    # Print report
    print_report(result, args.verbose)

    # Generate routes if requested
    if args.generate:
        routes = generate_route_stubs(result)
        if args.output:
            args.output.write_text(routes)
            print(f"\n✅ Routes written to {args.output}")
        else:
            print("\n" + "=" * 60)
            print("Generated FastAPI Routes:")
            print("=" * 60)
            print(routes)

    # Compare with manifest if requested
    if args.manifest:
        manifest_issues = compare_with_manifest(result)
        if manifest_issues:
            print("\n" + "=" * 60)
            print("Manifest Comparison:")
            print("=" * 60)
            for issue in manifest_issues:
                print(f"⚠️  {issue}")

    # Exit code
    if result.incompatible_count > 0:
        sys.exit(1)
    return 0


if __name__ == "__main__":
    main()
