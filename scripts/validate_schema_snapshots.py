#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Schema Snapshot Validator.

Compares current Pydantic model schemas against stored snapshots to detect
unintended breaking changes. This is part of the contract testing strategy
for V3 migration.

Usage:
    python scripts/validate_schema_snapshots.py           # Validate
    python scripts/validate_schema_snapshots.py --update  # Update snapshots
    python scripts/validate_schema_snapshots.py --json    # JSON output

Exit codes:
    0 - Schemas match snapshots
    1 - Schema drift detected (breaking change)
    2 - Script error

Created: 2026-01-24 (Session 72)
Reference: docs/adr/0003-contract-testing-for-v3.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Add Python module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "Python"))

from structural_lib.core.models import (
    BeamDesignResult,
    BeamForces,
    BeamGeometry,
    DesignStatus,
    FrameType,
    Point3D,
    SectionProperties,
)

SNAPSHOT_FILE = Path(__file__).parent.parent / "Python/tests/integration/schema_snapshots.json"

MODELS = {
    "Point3D": Point3D,
    "SectionProperties": SectionProperties,
    "BeamGeometry": BeamGeometry,
    "BeamForces": BeamForces,
    "BeamDesignResult": BeamDesignResult,
}

ENUMS = {
    "DesignStatus": DesignStatus,
    "FrameType": FrameType,
}


def get_model_schema(model_class) -> dict[str, Any]:
    """Extract schema information from a Pydantic model."""
    schema = model_class.model_json_schema()

    required = set(schema.get("required", []))
    properties = set(schema.get("properties", {}).keys())

    # Get computed fields if they exist
    computed = set()
    if hasattr(model_class, "model_computed_fields"):
        computed = set(model_class.model_computed_fields.keys())

    return {
        "required": sorted(required),
        "properties": sorted(properties),
        "computed": sorted(computed) if computed else None,
    }


def get_enum_values(enum_class) -> list[str]:
    """Extract values from an enum."""
    return [e.value for e in enum_class]


def compare_schemas(
    current: dict[str, Any],
    snapshot: dict[str, Any],
    model_name: str
) -> list[str]:
    """Compare current schema against snapshot, return list of differences."""
    diffs = []

    # Check required fields
    current_required = set(current.get("required", []))
    snapshot_required = set(snapshot.get("required", []))

    added_required = current_required - snapshot_required
    removed_required = snapshot_required - current_required

    if added_required:
        diffs.append(f"{model_name}: New required fields: {added_required}")
    if removed_required:
        diffs.append(f"{model_name}: Removed required fields: {removed_required}")

    # Check all properties
    current_props = set(current.get("properties", []))
    snapshot_props = set(snapshot.get("properties", []))

    added_props = current_props - snapshot_props
    removed_props = snapshot_props - current_props

    if added_props:
        diffs.append(f"{model_name}: New properties: {added_props}")
    if removed_props:
        diffs.append(f"{model_name}: Removed properties: {removed_props}")

    return diffs


def validate_snapshots() -> tuple[bool, list[str], dict[str, Any]]:
    """Validate current schemas against snapshots.

    Returns:
        Tuple of (all_match, differences, current_schemas)
    """
    # Load snapshots
    if not SNAPSHOT_FILE.exists():
        return False, ["Snapshot file not found"], {}

    with open(SNAPSHOT_FILE) as f:
        snapshots = json.load(f)

    snapshot_models = snapshots.get("models", {})

    diffs = []
    current_schemas = {}

    # Check each model
    for name, model_class in MODELS.items():
        current = get_model_schema(model_class)
        current_schemas[name] = current

        if name not in snapshot_models:
            diffs.append(f"{name}: Not in snapshots (new model)")
            continue

        snapshot = snapshot_models[name]
        model_diffs = compare_schemas(current, snapshot, name)
        diffs.extend(model_diffs)

    # Check enums
    for name, enum_class in ENUMS.items():
        current_values = get_enum_values(enum_class)

        if name in snapshot_models:
            snapshot_values = snapshot_models[name].get("values", [])

            added = set(current_values) - set(snapshot_values)
            removed = set(snapshot_values) - set(current_values)

            if added:
                diffs.append(f"{name}: New enum values: {added}")
            if removed:
                diffs.append(f"{name}: Removed enum values: {removed}")

    return len(diffs) == 0, diffs, current_schemas


def update_snapshots(current_schemas: dict[str, Any]) -> None:
    """Update snapshot file with current schemas."""
    # Load existing to preserve metadata
    if SNAPSHOT_FILE.exists():
        with open(SNAPSHOT_FILE) as f:
            snapshots = json.load(f)
    else:
        snapshots = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "description": "Schema snapshots for API contract testing",
        }

    # Update generated date
    from datetime import datetime, timezone
    snapshots["generated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Update models
    models = {}
    for name, schema in current_schemas.items():
        models[name] = {k: v for k, v in schema.items() if v is not None}

    # Add enums
    for name, enum_class in ENUMS.items():
        models[name] = {"values": get_enum_values(enum_class)}

    snapshots["models"] = models

    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(snapshots, f, indent=2)

    print(f"✅ Updated {SNAPSHOT_FILE}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate API schema snapshots")
    parser.add_argument("--update", action="store_true", help="Update snapshots")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    all_match, diffs, current_schemas = validate_snapshots()

    if args.update:
        update_snapshots(current_schemas)
        return 0

    if args.json:
        result = {
            "match": all_match,
            "differences": diffs,
            "models_checked": len(MODELS),
            "enums_checked": len(ENUMS),
        }
        print(json.dumps(result, indent=2))
        return 0 if all_match else 1

    # Console output
    print("=" * 60)
    print("📊 Schema Snapshot Validation")
    print("=" * 60)
    print()

    print(f"Models checked: {len(MODELS)}")
    print(f"Enums checked: {len(ENUMS)}")
    print()

    if all_match:
        print("✅ All schemas match snapshots")
        print()
        print("No breaking changes detected.")
    else:
        print("🔴 Schema drift detected!")
        print()
        print("Differences:")
        for diff in diffs:
            print(f"  • {diff}")
        print()
        print("If these changes are intentional, run:")
        print("  python scripts/validate_schema_snapshots.py --update")

    return 0 if all_match else 1


if __name__ == "__main__":
    sys.exit(main())
