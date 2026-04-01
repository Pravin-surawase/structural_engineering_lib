#!/usr/bin/env python3
"""Pre-route hooks — run before prompt_router routes a task."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hooks import HookRunner

# Agents with read-only permission level
_READONLY_AGENTS = frozenset(
    {
        "orchestrator",
        "structural-engineer",
        "reviewer",
        "security",
        "library-expert",
        "ui-designer",
    }
)

_WRITE_KEYWORDS = frozenset(
    {
        "create",
        "write",
        "edit",
        "delete",
        "modify",
        "add",
        "remove",
    }
)


def check_agent_permission(context: dict) -> tuple[bool, str]:
    """Check if the requesting agent has permission for the operation type."""
    agent = context.get("agent", "")
    query = context.get("query", "")

    if agent in _READONLY_AGENTS:
        query_lower = query.lower()
        for kw in _WRITE_KEYWORDS:
            if kw in query_lower:
                return (
                    True,
                    f"INFO: ReadOnly agent '{agent}' routing to write operation — will be delegated",
                )

    return True, "Permission check passed"


def register(runner: HookRunner) -> None:
    """Register all pre_route hooks."""
    runner.register("pre_route", check_agent_permission, priority=10)
