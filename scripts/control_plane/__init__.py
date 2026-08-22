#!/usr/bin/env python3
"""Canonical control-plane registry loader and validator.

When to use: Load operation discovery, permissions, aliases, executable targets,
or the temporary ``automation-map.json`` compatibility projection.
"""

from __future__ import annotations

import json
import shlex
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
REGISTRY_PATH = SCRIPTS_DIR / "control-plane.json"
SCHEMA_PATH = SCRIPTS_DIR / "control-plane.schema.json"
LEGACY_PATH = SCRIPTS_DIR / "automation-map.json"
PERMISSION_LEVELS = (
    "ReadOnly",
    "ReadOnlyTerminal",
    "WorkspaceWrite",
    "DangerFullAccess",
)
SCRIPT_EXTENSIONS = {".py", ".sh"}


class ControlPlaneError(ValueError):
    """Raised when the canonical registry is unavailable or invalid."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ControlPlaneError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys
        )
    except FileNotFoundError as exc:
        raise ControlPlaneError(f"registry file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ControlPlaneError(f"invalid JSON in {path}: {exc}") from exc
    except OSError as exc:
        raise ControlPlaneError(f"cannot read {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ControlPlaneError(f"expected a JSON object in {path}")
    return data


def _schema_errors(data: dict[str, Any], schema_path: Path) -> list[str]:
    schema = _read_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"schema:{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: "
        f"{error.message}"
        for error in sorted(
            validator.iter_errors(data),
            key=lambda item: tuple(str(part) for part in item.path),
        )
    ]


def operation_map(
    registry: dict[str, Any], *, active_only: bool = False
) -> dict[str, dict[str, Any]]:
    """Return operation metadata, optionally excluding deprecated aliases."""
    operations = registry.get("operations", {})
    if not isinstance(operations, dict):
        return {}
    if not active_only:
        return operations
    return {
        name: info
        for name, info in operations.items()
        if isinstance(info, dict) and info.get("status") == "active"
    }


def get_operation(
    name: str, registry: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    """Resolve an exact operation name or alias, case-insensitively."""
    loaded = registry if registry is not None else load_registry()
    normalized = name.lower().strip()
    operations = operation_map(loaded)
    direct = operations.get(normalized)
    if isinstance(direct, dict):
        return direct
    for info in operations.values():
        aliases = {str(alias).lower() for alias in info.get("aliases", [])}
        if normalized in aliases:
            return info
    return None


def operation_name_for_alias(
    alias: str, registry: dict[str, Any] | None = None
) -> str | None:
    """Return the active operation owning an alias."""
    loaded = registry if registry is not None else load_registry()
    normalized = alias.lower().strip()
    for name, info in operation_map(loaded, active_only=True).items():
        if normalized in {str(item).lower() for item in info.get("aliases", [])}:
            return name
    return None


def _resolve_local_target(cwd: str, token: str) -> Path | None:
    if "<" in token or ">" in token:
        return None
    if not (token.startswith("./") or token.startswith("../")):
        if not (
            token.startswith("scripts/") and token.endswith(tuple(SCRIPT_EXTENSIONS))
        ):
            return None
    return (REPO_ROOT / cwd / token).resolve()


def command_targets(registry: dict[str, Any]) -> dict[str, set[Path]]:
    """Return local executable/script targets referenced by each operation."""
    result: dict[str, set[Path]] = {}
    for name, info in operation_map(registry).items():
        targets: set[Path] = set()
        for step in info.get("command", {}).get("steps", []):
            cwd = str(step.get("cwd", "."))
            for token in step.get("argv", []):
                target = _resolve_local_target(cwd, str(token))
                if target is not None:
                    targets.add(target)
        result[name] = targets
    return result


def top_level_scripts() -> set[str]:
    """Return active top-level Python and shell scripts on disk."""
    return {
        path.name
        for path in SCRIPTS_DIR.iterdir()
        if path.is_file()
        and path.suffix in SCRIPT_EXTENSIONS
        and not path.name.startswith(".")
    }


def referenced_top_level_scripts(registry: dict[str, Any]) -> set[str]:
    """Return top-level scripts reached by structured operation commands."""
    return {
        target.name
        for targets in command_targets(registry).values()
        for target in targets
        if target.parent == SCRIPTS_DIR
    }


def semantic_errors(data: dict[str, Any]) -> list[str]:
    """Validate invariants that JSON Schema cannot express."""
    errors: list[str] = []
    operations = operation_map(data)
    operation_names = set(operations)
    active_names = {
        name for name, info in operations.items() if info.get("status") == "active"
    }
    alias_owners: dict[str, str] = {}

    for name, info in operations.items():
        if name != name.lower().strip():
            errors.append(f"operation:{name}: name must be normalized lowercase")
        for alias in info.get("aliases", []):
            normalized = str(alias).lower().strip()
            if normalized != alias:
                errors.append(f"operation:{name}: alias must be normalized: {alias}")
            if normalized in operation_names and normalized != name:
                errors.append(
                    f"operation:{name}: alias collides with operation: {normalized}"
                )
            owner = alias_owners.get(normalized)
            if owner is not None and owner != name:
                errors.append(
                    f"operation:{name}: alias '{normalized}' already belongs to {owner}"
                )
            alias_owners[normalized] = name

        if info.get("status") == "deprecated":
            replacement = info.get("replacement")
            if replacement not in active_names:
                errors.append(
                    f"operation:{name}: replacement is not an active operation: {replacement}"
                )

        command = info.get("command", {})
        display = str(command.get("display", ""))
        steps = command.get("steps", [])
        expected_tokens: list[str] = []
        previous_cwd: str | None = None
        for step in steps:
            cwd = str(step.get("cwd", "."))
            if cwd != "." and cwd != previous_cwd:
                expected_tokens.extend(["cd", cwd, "&&"])
            expected_tokens.extend(str(token) for token in step.get("argv", []))
            expected_tokens.append("&&")
            previous_cwd = cwd
        if expected_tokens:
            expected_tokens.pop()
        try:
            display_tokens = shlex.split(display)
        except ValueError as exc:
            errors.append(f"operation:{name}: invalid display command: {exc}")
        else:
            if display_tokens != expected_tokens:
                errors.append(
                    f"operation:{name}: display command differs from structured steps"
                )

    for name, targets in command_targets(data).items():
        for target in sorted(targets):
            try:
                target.relative_to(REPO_ROOT)
            except ValueError:
                errors.append(f"operation:{name}: target escapes repository: {target}")
                continue
            if not target.exists():
                errors.append(f"operation:{name}: missing command target: {target}")

    actual = top_level_scripts()
    referenced = referenced_top_level_scripts(data)
    for missing in sorted(actual - referenced):
        errors.append(
            f"coverage: top-level script is not registered: scripts/{missing}"
        )
    for phantom in sorted(referenced - actual):
        errors.append(f"coverage: registered script is not on disk: scripts/{phantom}")
    return errors


def validate_registry_data(
    data: dict[str, Any], *, schema_path: Path = SCHEMA_PATH
) -> list[str]:
    """Return all schema and semantic errors for registry data."""
    errors = _schema_errors(data, schema_path)
    if not errors:
        errors.extend(semantic_errors(data))
    return errors


def load_registry(
    path: Path = REGISTRY_PATH,
    *,
    schema_path: Path = SCHEMA_PATH,
    validate: bool = True,
) -> dict[str, Any]:
    """Load the canonical registry and fail closed on invalid content."""
    data = _read_json(path)
    if validate:
        errors = validate_registry_data(data, schema_path=schema_path)
        if errors:
            raise ControlPlaneError("invalid control plane:\n- " + "\n- ".join(errors))
    return data


def legacy_tasks(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Project canonical operations into the temporary legacy task shape."""
    result: dict[str, dict[str, Any]] = {}
    field_order = (
        "group",
        "description",
        "permission",
        "permission_modes",
        "options",
        "aliases",
        "never_use",
        "context_docs",
        "agent",
        "prereq",
        "replacement",
    )
    for name, operation in operation_map(registry).items():
        task: dict[str, Any] = {
            "script": operation["command"]["display"],
        }
        for field in field_order:
            if field in operation:
                task[field] = operation[field]
        if operation["status"] == "deprecated":
            task["deprecated"] = True
        result[name] = task
    return result


def legacy_projection(registry: dict[str, Any]) -> dict[str, Any]:
    """Build the deterministic compatibility projection."""
    actual = top_level_scripts()
    referenced = referenced_top_level_scripts(registry)
    return {
        "_comment": (
            "GENERATED compatibility projection from scripts/control-plane.json; "
            "do not edit directly"
        ),
        "_usage": "Use ./run.sh find <query> or ./run.sh control find <query>",
        "_source": "scripts/control-plane.json",
        "_coverage": f"{len(referenced)}/{len(actual)} top-level scripts registered",
        "tasks": legacy_tasks(registry),
    }


def canonical_json(data: dict[str, Any]) -> str:
    """Serialize registry/projection content deterministically."""
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def legacy_is_current(
    registry: dict[str, Any], *, legacy_path: Path = LEGACY_PATH
) -> bool:
    """Return whether the checked-in compatibility projection is exact."""
    try:
        current = legacy_path.read_text(encoding="utf-8")
    except OSError:
        return False
    return current == canonical_json(legacy_projection(registry))
