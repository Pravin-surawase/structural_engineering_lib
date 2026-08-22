#!/usr/bin/env python3
"""Validate and query small canonical repository context.

When to use: At task orientation or before opening a broad source/docs area.
The command reads live worktree paths on demand and never writes projections.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = SCRIPT_DIR / "context-manifest.json"
SKIP_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}
GENERIC_INDEX_NAMES = {"index.json", "index.md"}
LEGACY_DOCS_INDEX = "docs/docs-index.json"

sys.path.insert(0, str(SCRIPT_DIR))
from control_plane import (  # noqa: E402
    ControlPlaneError,
    load_registry,
    operation_map,
)


class ContextManifestError(ValueError):
    """Raised when the context manifest or its repository binding is invalid."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContextManifestError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _read_manifest(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object
        )
    except OSError as exc:
        raise ContextManifestError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ContextManifestError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ContextManifestError("manifest root must be an object")
    return data


def _relative_path(value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ContextManifestError(f"{label} must be a non-empty string")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or "\\" in value:
        raise ContextManifestError(f"{label} must stay inside the repository: {value}")
    return path


def _string_list(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        suffix = "" if allow_empty else " and must not be empty"
        raise ContextManifestError(f"{label} must be a list{suffix}")
    if any(not isinstance(item, str) or not item for item in value):
        raise ContextManifestError(f"{label} entries must be non-empty strings")
    if len(value) != len(set(value)):
        raise ContextManifestError(f"{label} entries must be unique")
    return value


def _tracked_paths(root: Path) -> set[str]:
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        result = None
    if result is not None and result.returncode == 0:
        tracked = {line for line in result.stdout.splitlines() if line}
        try:
            deleted = subprocess.run(
                ["git", "-C", str(root), "ls-files", "--deleted"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ContextManifestError(
                "cannot determine deleted repository paths"
            ) from exc
        if deleted.returncode == 0:
            tracked.difference_update(deleted.stdout.splitlines())
        return tracked
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and not any(part in SKIP_PARTS for part in path.parts)
    }


def _strict_fields(value: dict[str, Any], expected: set[str], label: str) -> None:
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing:
        raise ContextManifestError(f"{label} missing fields: {', '.join(missing)}")
    if extra:
        raise ContextManifestError(f"{label} unknown fields: {', '.join(extra)}")


def validate_manifest(
    data: dict[str, Any],
    *,
    root: Path = REPO_ROOT,
    tracked_paths: set[str] | None = None,
    registry: dict[str, Any] | None = None,
) -> None:
    """Validate shape, paths, control-plane references, and index retirement."""
    _strict_fields(
        data,
        {
            "schema_version",
            "description",
            "summary_policy",
            "authorities",
            "retained_indexes",
            "areas",
        },
        "manifest",
    )
    if data["schema_version"] != 1:
        raise ContextManifestError("schema_version must be 1")
    if not isinstance(data["description"], str) or not data["description"]:
        raise ContextManifestError("description must be a non-empty string")

    policy = data["summary_policy"]
    if not isinstance(policy, dict):
        raise ContextManifestError("summary_policy must be an object")
    _strict_fields(
        policy,
        {"source", "default_file_limit", "generated_folder_indexes"},
        "summary_policy",
    )
    if policy["source"] != "live-worktree-files":
        raise ContextManifestError("summary_policy.source must be live-worktree-files")
    if policy["generated_folder_indexes"] != "retired":
        raise ContextManifestError(
            "summary_policy.generated_folder_indexes must be retired"
        )
    limit = policy["default_file_limit"]
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
        raise ContextManifestError(
            "default_file_limit must be an integer from 1 to 100"
        )

    authorities = data["authorities"]
    if not isinstance(authorities, dict) or not authorities:
        raise ContextManifestError("authorities must be a non-empty object")
    for name, info in authorities.items():
        if not isinstance(info, dict):
            raise ContextManifestError(f"authority:{name} must be an object")
        _strict_fields(info, {"path", "description"}, f"authority:{name}")
        authority_path = _relative_path(info["path"], f"authority:{name}.path")
        if not (root / authority_path).is_file():
            raise ContextManifestError(
                f"authority:{name}.path does not exist: {authority_path.as_posix()}"
            )
        if not isinstance(info["description"], str) or not info["description"]:
            raise ContextManifestError(
                f"authority:{name}.description must be a non-empty string"
            )

    retained = data["retained_indexes"]
    if not isinstance(retained, dict) or not retained:
        raise ContextManifestError("retained_indexes must be a non-empty object")
    retained_paths: set[str] = set()
    for path_text, info in retained.items():
        path = _relative_path(path_text, "retained index path")
        retained_paths.add(path.as_posix())
        if not (root / path).is_file():
            raise ContextManifestError(
                f"retained index does not exist: {path.as_posix()}"
            )
        if not isinstance(info, dict):
            raise ContextManifestError(f"retained index:{path_text} must be an object")
        _strict_fields(info, {"kind", "owner", "reason"}, f"retained index:{path_text}")
        if any(not isinstance(info[key], str) or not info[key] for key in info):
            raise ContextManifestError(
                f"retained index:{path_text} fields must be non-empty strings"
            )

    try:
        registry = registry or load_registry()
    except ControlPlaneError as exc:
        raise ContextManifestError(f"control plane is invalid: {exc}") from exc
    operations = operation_map(registry)
    active_operations = {
        name for name, info in operations.items() if info.get("status") == "active"
    }

    areas = data["areas"]
    if not isinstance(areas, dict) or not areas:
        raise ContextManifestError("areas must be a non-empty object")
    for name, info in areas.items():
        if not isinstance(info, dict):
            raise ContextManifestError(f"area:{name} must be an object")
        _strict_fields(
            info,
            {"description", "roots", "read_first", "operations"},
            f"area:{name}",
        )
        if not isinstance(info["description"], str) or not info["description"]:
            raise ContextManifestError(
                f"area:{name}.description must be a non-empty string"
            )
        for root_text in _string_list(info["roots"], f"area:{name}.roots"):
            area_root = _relative_path(root_text, f"area:{name}.root")
            if not (root / area_root).is_dir():
                raise ContextManifestError(
                    f"area:{name}.root does not exist: {area_root.as_posix()}"
                )
        for first_text in _string_list(info["read_first"], f"area:{name}.read_first"):
            first = _relative_path(first_text, f"area:{name}.read_first path")
            if not (root / first).is_file():
                raise ContextManifestError(
                    f"area:{name}.read_first does not exist: {first.as_posix()}"
                )
        for operation in _string_list(
            info["operations"], f"area:{name}.operations", allow_empty=True
        ):
            if operation not in active_operations:
                raise ContextManifestError(
                    f"area:{name}.operation is not active: {operation}"
                )

    tracked = tracked_paths if tracked_paths is not None else _tracked_paths(root)
    generic = {
        path
        for path in tracked
        if Path(path).name in GENERIC_INDEX_NAMES or path == LEGACY_DOCS_INDEX
    }
    unexpected = sorted(generic - retained_paths)
    if unexpected:
        raise ContextManifestError(
            "generic generated indexes are retired; unexpected tracked paths: "
            + ", ".join(unexpected)
        )


def load_manifest(
    path: Path = MANIFEST_PATH, *, root: Path = REPO_ROOT
) -> dict[str, Any]:
    data = _read_manifest(path)
    validate_manifest(data, root=root)
    return data


def _worktree_files(root: Path, relative_root: Path) -> list[Path]:
    target = (root / relative_root).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise ContextManifestError(
            f"summary target escapes repository: {relative_root.as_posix()}"
        ) from exc
    if not target.is_dir():
        raise ContextManifestError(
            f"summary target is not a directory: {relative_root.as_posix()}"
        )
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                "--",
                relative_root.as_posix(),
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        result = None
    if result is not None and result.returncode == 0:
        candidates = [root / line for line in result.stdout.splitlines() if line]
    else:
        candidates = list(target.rglob("*"))
    return sorted(
        path
        for path in candidates
        if path.is_file()
        and not any(part in SKIP_PARTS for part in path.relative_to(root).parts)
    )


def summarize_roots(
    roots: Iterable[str], *, repository_root: Path = REPO_ROOT, limit: int = 30
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for root_text in roots:
        relative_root = _relative_path(root_text, "summary root")
        files = _worktree_files(repository_root, relative_root)
        extension_counts = Counter(path.suffix.lower() or "<none>" for path in files)
        target = (repository_root / relative_root).resolve()
        child_counts: Counter[str] = Counter()
        for path in files:
            relative = path.relative_to(target)
            child_counts[relative.parts[0] if len(relative.parts) > 1 else "."] += 1
        summaries.append(
            {
                "root": relative_root.as_posix(),
                "file_count": len(files),
                "extensions": dict(sorted(extension_counts.items())),
                "top_level": dict(sorted(child_counts.items())),
                "files": [
                    path.relative_to(repository_root).as_posix()
                    for path in files[:limit]
                ],
                "truncated": len(files) > limit,
            }
        )
    return summaries


def _resolve_summary_target(
    manifest: dict[str, Any], target: str, root: Path
) -> tuple[str, list[str]]:
    if target in manifest["areas"]:
        return target, manifest["areas"][target]["roots"]
    path = _relative_path(target, "summary target")
    if not (root / path).is_dir():
        raise ContextManifestError(f"unknown area or directory: {target}")
    return target, [path.as_posix()]


def _print_summary(label: str, summaries: list[dict[str, Any]]) -> None:
    print(f"Context summary: {label}")
    for summary in summaries:
        print(f"\n{summary['root']}: {summary['file_count']} live files")
        extensions = ", ".join(
            f"{name}={count}" for name, count in summary["extensions"].items()
        )
        print(f"  extensions: {extensions or 'none'}")
        children = ", ".join(
            f"{name}={count}" for name, count in summary["top_level"].items()
        )
        print(f"  top-level: {children or 'none'}")
        for path in summary["files"]:
            print(f"  - {path}")
        if summary["truncated"]:
            print("  - ... use --limit to change the bounded file preview")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and query live repository context without generated indexes"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "validate", help="Validate manifest, paths, and index retirement"
    )
    list_parser = subparsers.add_parser("list", help="List canonical context areas")
    list_parser.add_argument("--json", action="store_true")
    show_parser = subparsers.add_parser("show", help="Show one context area")
    show_parser.add_argument("area")
    show_parser.add_argument("--json", action="store_true")
    summary_parser = subparsers.add_parser(
        "summary", help="Summarize live files for an area or repository directory"
    )
    summary_parser.add_argument("target")
    summary_parser.add_argument("--limit", type=int)
    summary_parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = load_manifest()
        if args.command == "validate":
            print(
                "PASS context manifest: "
                f"{len(manifest['areas'])} areas, "
                f"{len(manifest['authorities'])} authorities, "
                f"{len(manifest['retained_indexes'])} retained index-named surfaces, "
                "0 generated folder indexes"
            )
            return 0
        if args.command == "list":
            areas = manifest["areas"]
            if args.json:
                print(json.dumps(areas, indent=2, sort_keys=True))
            else:
                for name, info in areas.items():
                    print(f"{name}: {info['description']}")
            return 0
        if args.command == "show":
            area = manifest["areas"].get(args.area)
            if area is None:
                raise ContextManifestError(f"unknown context area: {args.area}")
            if args.json:
                print(json.dumps({"name": args.area, **area}, indent=2))
            else:
                print(f"{args.area}: {area['description']}")
                print("roots:")
                for path in area["roots"]:
                    print(f"  - {path}")
                print("read first:")
                for path in area["read_first"]:
                    print(f"  - {path}")
                print("operations:")
                operations = operation_map(load_registry())
                for name in area["operations"]:
                    print(f"  - {name}: {operations[name]['command']['display']}")
            return 0
        label, roots = _resolve_summary_target(manifest, args.target, REPO_ROOT)
        limit = args.limit or manifest["summary_policy"]["default_file_limit"]
        if not 1 <= limit <= 500:
            raise ContextManifestError("--limit must be from 1 to 500")
        summaries = summarize_roots(roots, limit=limit)
        payload = {"target": label, "summaries": summaries}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _print_summary(label, summaries)
        return 0
    except ContextManifestError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
