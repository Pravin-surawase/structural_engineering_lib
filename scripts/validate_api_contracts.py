#!/usr/bin/env python3
"""
API Contract Validator.

Validates FastAPI endpoints against their OpenAPI contracts to detect:
- Missing endpoints (breaking change)
- Changed response schemas (breaking change)
- Missing required fields (breaking change)
- Added optional fields (non-breaking)
- Changed HTTP methods (breaking change)

Usage:
    python scripts/validate_api_contracts.py              # Validate all
    python scripts/validate_api_contracts.py --save       # Save current as baseline
    python scripts/validate_api_contracts.py --diff       # Show detailed diff

Exit Codes:
    0: All contracts valid / no breaking changes
    1: Breaking changes detected
    2: Error validating contracts
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Baseline contract file location
BASELINE_PATH = Path(__file__).parent.parent / "fastapi_app" / "openapi_baseline.json"

# Add project root for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


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


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate FastAPI contracts for breaking changes"
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

    args = parser.parse_args()
    return validate_contracts(save=args.save, diff=args.diff)


if __name__ == "__main__":
    sys.exit(main())
