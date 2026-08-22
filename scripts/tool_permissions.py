#!/usr/bin/env python3
"""Tool permission enforcement for agent operations.

Checks whether an agent is allowed to perform an operation based on
agent_registry.json permission_level and file_scope.

Usage as CLI:
    .venv/bin/python scripts/tool_permissions.py check --agent backend --op edit --path Python/structural_lib/api.py
    .venv/bin/python scripts/tool_permissions.py check --agent governance --op "project health" --mode=--fix

Usage as module:
    from tool_permissions import check_permission, check_file_scope
    result = check_permission("backend", "edit", "Python/structural_lib/api.py")
    print(result.allowed, result.reason)
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib.output import print_json  # noqa: E402
from _lib.utils import REPO_ROOT  # noqa: E402
from control_plane import (  # noqa: E402
    REGISTRY_PATH,
    ControlPlaneError,
    load_registry as load_control_registry,
    operation_map,
)

# ---------------------------------------------------------------------------
# Operation classifications
# ---------------------------------------------------------------------------

READ_OPS: set[str] = {
    "read",
    "search",
    "list",
    "find",
    "check",
    "validate",
    "discover",
    "show",
}

WRITE_OPS: set[str] = {
    "edit",
    "create",
    "modify",
    "write",
    "add",
    "update",
}

DANGER_OPS: set[str] = {
    "delete",
    "push",
    "merge",
    "force",
    "rm",
    "cleanup",
    "deploy",
}

# Minimum permission level required for each category (ordered low→high)
_PERMISSION_LEVELS = (
    "ReadOnly",
    "ReadOnlyTerminal",
    "WorkspaceWrite",
    "DangerFullAccess",
)

_LEVEL_FOR_CATEGORY: dict[str, str] = {
    "read": "ReadOnly",
    "write": "WorkspaceWrite",
    "danger": "DangerFullAccess",
}


def _op_category(operation: str) -> str:
    """Classify an operation string into read/write/danger."""
    op = operation.lower().strip()
    if op in READ_OPS:
        return "read"
    if op in WRITE_OPS:
        return "write"
    if op in DANGER_OPS:
        return "danger"
    # Unknown operations default to danger (fail-safe)
    return "danger"


def _level_rank(level: str) -> int:
    """Return numeric rank for a permission level (higher = more access)."""
    try:
        return _PERMISSION_LEVELS.index(level)
    except ValueError:
        return -1


# ---------------------------------------------------------------------------
# Registry loading
# ---------------------------------------------------------------------------

_REGISTRY_PATH = REPO_ROOT / "agents" / "agent_registry.json"


def _load_registry() -> list[dict]:
    """Load agents list from agent_registry.json."""
    try:
        with open(_REGISTRY_PATH) as f:
            data = json.load(f)
        return data.get("agents", [])
    except FileNotFoundError:
        print(f"WARNING: Agent registry not found at {_REGISTRY_PATH}", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"WARNING: Invalid JSON in agent registry: {e}", file=sys.stderr)
        return []


def _find_agent(agents: list[dict], name: str) -> dict | None:
    """Find agent entry by name (case-insensitive)."""
    name_lower = name.lower().strip()
    for agent in agents:
        if agent.get("name", "").lower() == name_lower:
            return agent
    return None


@lru_cache(maxsize=4)
def _load_cached_automation_tasks(
    modified_ns: int, size: int
) -> dict[str, dict]:
    """Load validated operation metadata for one exact registry file state."""
    del modified_ns, size
    try:
        return operation_map(load_control_registry())
    except ControlPlaneError:
        return {}


def _load_automation_tasks() -> dict[str, dict]:
    """Load operation metadata, revalidating only when registry bytes change."""
    try:
        stat = REGISTRY_PATH.stat()
    except OSError:
        return {}
    return _load_cached_automation_tasks(stat.st_mtime_ns, stat.st_size)


def resolve_required_permission(operation: str, *, mode: str | None = None) -> str:
    """Resolve the required level for an abstract op or declared script mode.

    Automation tasks must declare their default ``permission`` and any mutating
    ``permission_modes`` explicitly. Unknown tasks and modes fail closed.
    """
    normalized = operation.lower().strip()
    if mode is None and normalized in READ_OPS | WRITE_OPS | DANGER_OPS:
        return _LEVEL_FOR_CATEGORY[_op_category(normalized)]

    task = _load_automation_tasks().get(normalized)
    if not isinstance(task, dict):
        return "DangerFullAccess"

    default_level = task.get("permission")
    if default_level not in _PERMISSION_LEVELS:
        return "DangerFullAccess"
    if mode is None:
        return default_level

    modes = task.get("permission_modes", {})
    if not isinstance(modes, dict):
        return "DangerFullAccess"
    required = modes.get(mode.strip())
    return required if required in _PERMISSION_LEVELS else "DangerFullAccess"


def _is_declared_operation(operation: str, *, mode: str | None = None) -> bool:
    """Return whether an abstract operation or exact task/mode is declared."""
    normalized = operation.lower().strip()
    if mode is None and normalized in READ_OPS | WRITE_OPS | DANGER_OPS:
        return True

    task = _load_automation_tasks().get(normalized)
    if not isinstance(task, dict) or task.get("permission") not in _PERMISSION_LEVELS:
        return False
    if mode is None:
        return True

    modes = task.get("permission_modes", {})
    return (
        isinstance(modes, dict)
        and mode.strip() in modes
        and modes[mode.strip()] in _PERMISSION_LEVELS
    )


# ---------------------------------------------------------------------------
# Permission result
# ---------------------------------------------------------------------------


@dataclass
class PermissionResult:
    """Result of a permission check."""

    allowed: bool
    reason: str
    agent: str
    operation: str
    mode: str | None
    target_path: str | None
    permission_level: str
    required_level: str
    file_scope: str | None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def check_terminal_command(agent: str, command: str) -> bool:
    """Check if *command* is allowed for agent's terminal_allowlist.

    Returns True if the agent has no terminal_allowlist restriction (null/empty) OR
    if the command starts with any pattern in the allowlist.
    """
    agents = _load_registry()
    agent_data = _find_agent(agents, agent)
    if agent_data is None:
        return False

    allowlist = agent_data.get("terminal_allowlist", [])
    if not allowlist:
        return True  # No restriction

    # Check if command starts with any allowed pattern
    for pattern in allowlist:
        if command.strip().startswith(pattern):
            return True
    return False


def check_file_scope(agent: str, file_path: str) -> bool:
    """Check if *file_path* falls within the agent's file_scope glob.

    Returns True if the agent has no file_scope restriction (null) OR
    if the path matches the scope pattern.
    """
    agents = _load_registry()
    agent_data = _find_agent(agents, agent)
    if agent_data is None:
        return False

    scope = agent_data.get("file_scope")
    if scope is None:
        return True  # No restriction

    # Normalise to forward-slash relative paths
    normalized = file_path.replace("\\", "/").strip("/")
    return fnmatch.fnmatch(normalized, scope)


def check_permission(
    agent: str,
    operation: str,
    target_path: str | None = None,
    *,
    mode: str | None = None,
) -> PermissionResult:
    """Check whether *agent* may perform *operation* on *target_path*.

    Loads agent_registry.json, determines the agent's permission_level,
    classifies the operation, and checks file_scope when applicable.
    """
    agents = _load_registry()
    agent_data = _find_agent(agents, agent)
    required_level = resolve_required_permission(operation, mode=mode)

    if agent_data is None:
        return PermissionResult(
            allowed=False,
            reason=f"Agent '{agent}' not found in registry",
            agent=agent,
            operation=operation,
            mode=mode,
            target_path=target_path,
            permission_level="unknown",
            required_level=required_level,
            file_scope=None,
        )

    if not _is_declared_operation(operation, mode=mode):
        return PermissionResult(
            allowed=False,
            reason=(
                f"Operation '{operation}'"
                + (f" mode '{mode}'" if mode else "")
                + " has no explicit permission declaration"
            ),
            agent=agent,
            operation=operation,
            mode=mode,
            target_path=target_path,
            permission_level=agent_data.get("permission_level", "ReadOnly"),
            required_level=required_level,
            file_scope=agent_data.get("file_scope"),
        )

    perm_level: str = agent_data.get("permission_level", "ReadOnly")
    file_scope: str | None = agent_data.get("file_scope")

    # 1. Check permission level is sufficient
    if _level_rank(perm_level) < _level_rank(required_level):
        return PermissionResult(
            allowed=False,
            reason=(
                f"Agent '{agent}' has {perm_level} permission but "
                f"'{operation}' requires {required_level}"
            ),
            agent=agent,
            operation=operation,
            mode=mode,
            target_path=target_path,
            permission_level=perm_level,
            required_level=required_level,
            file_scope=file_scope,
        )

    # 2. For write/danger requirements with a target path, check file scope
    if (
        _level_rank(required_level) >= _level_rank("WorkspaceWrite")
        and target_path is not None
        and file_scope is not None
    ):
        normalized = target_path.replace("\\", "/").strip("/")
        if not fnmatch.fnmatch(normalized, file_scope):
            return PermissionResult(
                allowed=False,
                reason=(
                    f"Agent '{agent}' file scope is '{file_scope}' — "
                    f"path '{target_path}' is outside scope"
                ),
                agent=agent,
                operation=operation,
                mode=mode,
                target_path=target_path,
                permission_level=perm_level,
                required_level=required_level,
                file_scope=file_scope,
            )

    return PermissionResult(
        allowed=True,
        reason="Permitted",
        agent=agent,
        operation=operation,
        mode=mode,
        target_path=target_path,
        permission_level=perm_level,
        required_level=required_level,
        file_scope=file_scope,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check agent tool permissions against agent_registry.json",
    )
    sub = parser.add_subparsers(dest="command")

    # `check` subcommand
    check_p = sub.add_parser("check", help="Check a single permission")
    check_p.add_argument("--agent", required=True, help="Agent name")
    check_p.add_argument("--op", required=True, help="Operation (read/edit/delete/...)")
    check_p.add_argument("--mode", default=None, help="Exact declared task mode")
    check_p.add_argument("--path", default=None, help="Target file path")
    check_p.add_argument(
        "--json", action="store_true", dest="as_json", help="JSON output"
    )

    # Allow top-level flags as shorthand (no subcommand)
    parser.add_argument("--agent", default=None, help="Agent name")
    parser.add_argument("--op", default=None, help="Operation")
    parser.add_argument("--mode", default=None, help="Exact declared task mode")
    parser.add_argument("--path", default=None, help="Target file path")
    parser.add_argument(
        "--json", action="store_true", dest="as_json", help="JSON output"
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Support both `check --agent ...` and `--agent ...` forms
    agent = args.agent
    op = args.op
    mode = args.mode
    path = args.path
    as_json = args.as_json

    if not agent or not op:
        parser.print_help()
        return 1

    result = check_permission(agent, op, path, mode=mode)

    if as_json:
        print_json(
            {
                "allowed": result.allowed,
                "reason": result.reason,
                "agent": result.agent,
                "operation": result.operation,
                "mode": result.mode,
                "target_path": result.target_path,
                "permission_level": result.permission_level,
                "required_level": result.required_level,
                "file_scope": result.file_scope,
            }
        )
    else:
        icon = "✅" if result.allowed else "🚫"
        print(f"{icon} {result.agent} → {result.operation}", end="")
        if result.mode:
            print(f" {result.mode}", end="")
        if result.target_path:
            print(f" on {result.target_path}", end="")
        print(f"  [agent={result.permission_level}, required={result.required_level}]")
        if not result.allowed:
            print(f"   Reason: {result.reason}")

    return 0 if result.allowed else 2


if __name__ == "__main__":
    raise SystemExit(main())
