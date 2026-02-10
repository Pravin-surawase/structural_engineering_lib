#!/usr/bin/env python3
"""Generate or validate the public API manifest for structural_lib.api."""

from __future__ import annotations

import argparse
import inspect
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT
DEFAULT_OUT = REPO_ROOT / "docs/reference/api-manifest.json"


def _load_api():
    sys.path.insert(0, str(REPO_ROOT / "Python"))
    from structural_lib import api  # type: ignore

    return api


def _signature_for_class(cls: type) -> str:
    try:
        sig = inspect.signature(cls.__init__)
    except (TypeError, ValueError):
        return "()"
    params = list(sig.parameters.values())
    if params and params[0].name == "self":
        sig = sig.replace(parameters=params[1:])
    return str(sig)


def _signature_for_callable(obj: object) -> str:
    try:
        return str(inspect.signature(obj))
    except (TypeError, ValueError):
        return "(...)"


def _build_manifest() -> dict:
    api = _load_api()
    symbols: list[dict] = []

    for name in sorted(getattr(api, "__all__", [])):
        obj = getattr(api, name, None)
        if obj is None:
            continue
        if inspect.isclass(obj):
            kind = "class"
            signature = _signature_for_class(obj)
        elif inspect.isfunction(obj) or inspect.isbuiltin(obj):
            kind = "function"
            signature = _signature_for_callable(obj)
        else:
            kind = "value"
            signature = ""

        symbols.append(
            {
                "name": name,
                "kind": kind,
                "signature": signature,
            }
        )

    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "module": "structural_lib.api",
        "python": sys.version.split()[0],
        "count": len(symbols),
        "symbols": symbols,
    }


def _normalize(manifest: dict) -> dict:
    normalized = {
        key: value
        for key, value in manifest.items()
        if key not in {"generated", "python"}
    }
    symbols = normalized.get("symbols", [])
    normalized["symbols"] = sorted(symbols, key=lambda item: item.get("name", ""))
    return normalized


def _compare(expected: dict, actual: dict) -> list[str]:
    expected_map = {item["name"]: item for item in expected.get("symbols", [])}
    actual_map = {item["name"]: item for item in actual.get("symbols", [])}

    missing = sorted(set(expected_map) - set(actual_map))
    extra = sorted(set(actual_map) - set(expected_map))
    changed = [
        name
        for name in sorted(set(expected_map) & set(actual_map))
        if expected_map[name] != actual_map[name]
    ]

    messages = []
    if missing:
        messages.append("Missing symbols in manifest:")
        messages.extend(f"  - {name}" for name in missing)
    if extra:
        messages.append("Extra symbols in manifest:")
        messages.extend(f"  - {name}" for name in extra)
    if changed:
        messages.append("Signature or kind mismatch:")
        messages.extend(f"  - {name}" for name in changed)
    return messages


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate API manifest.")
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output path for the manifest JSON.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the manifest is up to date without writing.",
    )
    args = parser.parse_args()

    manifest = _build_manifest()
    expected = _normalize(manifest)
    if args.check:
        if not args.out.exists():
            print(f"ERROR: {args.out} not found. Run generate_api_manifest.py.")
            return 1
        actual = _normalize(json.loads(args.out.read_text(encoding="utf-8")))
        if expected != actual:
            print("ERROR: api manifest is out of date.")
            for line in _compare(expected, actual):
                print(line)
            print("Run: .venv/bin/python scripts/generate_api_manifest.py")
            return 1
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(manifest, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote API manifest to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
