#!/usr/bin/env python3
"""Inspect and validate the canonical repository control plane.

When to use: Validate operation metadata, search registered commands, inspect
permissions, or verify/regenerate the temporary automation-map projection.
"""

from __future__ import annotations

import argparse
import json
import sys
from difflib import get_close_matches
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from control_plane import (  # noqa: E402
    LEGACY_PATH,
    ControlPlaneError,
    canonical_json,
    legacy_is_current,
    legacy_projection,
    load_registry,
    operation_map,
    referenced_top_level_scripts,
    top_level_scripts,
)


def _find(query: str, registry: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    active = operation_map(registry, active_only=True)
    normalized = query.lower().strip()
    if normalized in active:
        return [(normalized, active[normalized])]
    matches = []
    for name, info in active.items():
        aliases = [str(alias).lower() for alias in info.get("aliases", [])]
        haystack = f"{name} {info.get('description', '')}".lower()
        if normalized in haystack or any(normalized in alias for alias in aliases):
            matches.append((name, info))
    if matches:
        return matches
    close = get_close_matches(normalized, list(active), n=3, cutoff=0.4)
    return [(name, active[name]) for name in close]


def _print_operation(name: str, info: dict[str, Any]) -> None:
    print(f"{name} [{info['group']}]")
    print(f"  {info['description']}")
    print(f"  command: {info['command']['display']}")
    print(f"  permission: {info['permission']}")
    if info.get("permission_modes"):
        modes = ", ".join(
            f"{mode}={level}" for mode, level in info["permission_modes"].items()
        )
        print(f"  modes: {modes}")
    if info.get("aliases"):
        print(f"  aliases: {', '.join(info['aliases'])}")


def _cmd_validate(args: argparse.Namespace) -> int:
    try:
        registry = load_registry()
    except ControlPlaneError as exc:
        if args.json:
            print(json.dumps({"status": "fail", "errors": str(exc).splitlines()}))
        else:
            print(f"ERROR: {exc}")
        return 1
    errors = []
    if not legacy_is_current(registry):
        errors.append(
            "scripts/automation-map.json is not the exact generated projection"
        )
    result = {
        "status": "fail" if errors else "pass",
        "schema_version": registry["schema_version"],
        "operations": len(operation_map(registry)),
        "active_operations": len(operation_map(registry, active_only=True)),
        "top_level_scripts": len(top_level_scripts()),
        "registered_top_level_scripts": len(referenced_top_level_scripts(registry)),
        "legacy_projection_current": not errors,
        "errors": errors,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    elif errors:
        print("Control plane: FAIL")
        for error in errors:
            print(f"- {error}")
    else:
        print(
            "Control plane: PASS "
            f"({result['active_operations']} active operations; "
            f"{result['registered_top_level_scripts']}/{result['top_level_scripts']} scripts)"
        )
    return 1 if errors else 0


def _cmd_export(args: argparse.Namespace) -> int:
    try:
        registry = load_registry()
    except ControlPlaneError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    content = canonical_json(legacy_projection(registry))
    if args.write:
        LEGACY_PATH.write_text(content, encoding="utf-8", newline="\n")
        print(f"Wrote {LEGACY_PATH}")
        return 0
    if legacy_is_current(registry):
        print("automation-map.json projection is current")
        return 0
    print("automation-map.json projection differs", file=sys.stderr)
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="Validate registry and projection")
    validate.add_argument("--json", action="store_true")
    validate.set_defaults(handler=_cmd_validate)

    find = sub.add_parser("find", help="Find active operations")
    find.add_argument("query")
    find.add_argument("--json", action="store_true")

    listing = sub.add_parser("list", help="List active operations")
    listing.add_argument("--group")
    listing.add_argument("--json", action="store_true")

    stats = sub.add_parser("stats", help="Show registry counts")
    stats.add_argument("--json", action="store_true")

    export = sub.add_parser(
        "export-legacy", help="Check or write automation-map compatibility projection"
    )
    export.add_argument("--write", action="store_true")
    export.set_defaults(handler=_cmd_export)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if hasattr(args, "handler"):
        return args.handler(args)
    try:
        registry = load_registry()
    except ControlPlaneError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.command == "find":
        matches = _find(args.query, registry)
        if args.json:
            print(
                json.dumps([{"name": name, **info} for name, info in matches], indent=2)
            )
        else:
            for name, info in matches:
                _print_operation(name, info)
        return 0 if matches else 1

    active = operation_map(registry, active_only=True)
    if args.command == "list":
        selected = {
            name: info
            for name, info in active.items()
            if not args.group or info["group"].lower() == args.group.lower()
        }
        if args.json:
            print(json.dumps(selected, indent=2))
        else:
            for name, info in selected.items():
                _print_operation(name, info)
        return 0

    permissions: dict[str, int] = {}
    groups: dict[str, int] = {}
    aliases = 0
    for info in active.values():
        permissions[info["permission"]] = permissions.get(info["permission"], 0) + 1
        groups[info["group"]] = groups.get(info["group"], 0) + 1
        aliases += len(info.get("aliases", []))
    result = {
        "operations": len(operation_map(registry)),
        "active_operations": len(active),
        "deprecated_operations": len(operation_map(registry)) - len(active),
        "groups": groups,
        "permissions": permissions,
        "aliases": aliases,
        "top_level_scripts": len(top_level_scripts()),
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
