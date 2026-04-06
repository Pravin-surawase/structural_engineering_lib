#!/usr/bin/env python3
"""Check OpenAPI spec for drift against baseline.

Compares the live FastAPI OpenAPI spec against the committed baseline
in ``fastapi_app/openapi_baseline.json``.  Exits 0 when they match,
exits 1 when drift is detected.

Usage:
    python scripts/check_openapi_drift.py           # Check only
    python scripts/check_openapi_drift.py --update   # Update baseline
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "fastapi_app" / "openapi_baseline.json"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Keys to ignore during comparison (version bumps are expected)
IGNORED_KEYS: set[tuple[str, ...]] = {("info", "version")}


def _strip_ignored(obj: Any, path: tuple[str, ...] = ()) -> Any:
    """Return a deep copy of *obj* with ignored key-paths removed."""
    if isinstance(obj, dict):
        return {
            k: _strip_ignored(v, path + (k,))
            for k, v in obj.items()
            if path + (k,) not in IGNORED_KEYS
        }
    if isinstance(obj, list):
        return [_strip_ignored(v, path) for v in obj]
    return obj


def _collect_diffs(
    baseline: Any,
    current: Any,
    path: str = "",
    diffs: list[str] | None = None,
) -> list[str]:
    """Recursively collect human-readable diff lines between two objects."""
    if diffs is None:
        diffs = []

    if type(baseline) is not type(current):
        diffs.append(
            f"  {path or '<root>'}: type changed {type(baseline).__name__} -> {type(current).__name__}"
        )
        return diffs

    if isinstance(baseline, dict):
        all_keys = sorted(set(baseline) | set(current))
        for key in all_keys:
            child_path = f"{path}.{key}" if path else key
            if key not in current:
                diffs.append(f"  REMOVED  {child_path}")
            elif key not in baseline:
                diffs.append(f"  ADDED    {child_path}")
            else:
                _collect_diffs(baseline[key], current[key], child_path, diffs)
    elif isinstance(baseline, list):
        if len(baseline) != len(current):
            diffs.append(f"  {path}: list length {len(baseline)} -> {len(current)}")
        for i, (b, c) in enumerate(zip(baseline, current)):
            _collect_diffs(b, c, f"{path}[{i}]", diffs)
        # Extra items in current
        for i in range(len(baseline), len(current)):
            diffs.append(f"  ADDED    {path}[{i}]")
    else:
        if baseline != current:
            # Truncate long values for readability
            b_repr = (
                repr(baseline)
                if len(repr(baseline)) < 80
                else repr(baseline)[:77] + "..."
            )
            c_repr = (
                repr(current) if len(repr(current)) < 80 else repr(current)[:77] + "..."
            )
            diffs.append(f"  CHANGED  {path}: {b_repr} -> {c_repr}")

    return diffs


def _normalise(obj: Any) -> str:
    """Serialise to a canonical JSON string (sorted keys, consistent indent)."""
    return json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------


def get_current_spec() -> dict[str, Any]:
    """Import the FastAPI app and return its OpenAPI schema."""
    # Ensure the repo root is on sys.path so ``fastapi_app`` is importable.
    repo_str = str(ROOT)
    if repo_str not in sys.path:
        sys.path.insert(0, repo_str)

    from fastapi_app.main import app  # type: ignore[import-untyped]

    spec: dict[str, Any] = app.openapi()
    return json.loads(json.dumps(spec, sort_keys=True))  # normalise


def load_baseline() -> dict[str, Any]:
    """Load the committed baseline spec."""
    if not BASELINE_PATH.exists():
        print(f"❌ Baseline not found: {BASELINE_PATH}")
        sys.exit(2)
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


def update_baseline(spec: dict[str, Any]) -> None:
    """Write *spec* as the new baseline."""
    BASELINE_PATH.write_text(
        json.dumps(spec, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"✅ Baseline updated: {BASELINE_PATH}")


def check_drift() -> bool:
    """Return True when baseline matches the live spec (no drift)."""
    baseline_raw = load_baseline()
    current_raw = get_current_spec()

    baseline = _strip_ignored(baseline_raw)
    current = _strip_ignored(current_raw)

    if _normalise(baseline) == _normalise(current):
        return True

    # Drift detected – produce a useful report
    print("❌ OpenAPI baseline drift detected!\n")

    # Section-level summary
    for section in ("paths", "components", "tags", "info"):
        b_section = baseline.get(section)  # type: ignore[union-attr]
        c_section = current.get(section)  # type: ignore[union-attr]
        if _normalise(b_section) != _normalise(c_section):
            print(f"  Section '{section}' differs")

    # Detailed diffs
    diffs = _collect_diffs(baseline, current)
    if diffs:
        print(f"\nDetails ({len(diffs)} difference{'s' if len(diffs) != 1 else ''}):")
        for line in diffs[:40]:
            print(line)
        if len(diffs) > 40:
            print(f"  … and {len(diffs) - 40} more")

    print("\nTo update the baseline run:")
    print("  python scripts/check_openapi_drift.py --update")
    return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    if "--update" in sys.argv:
        spec = get_current_spec()
        update_baseline(spec)
        return

    ok = check_drift()
    if ok:
        print("✅ OpenAPI spec matches baseline — no drift")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
