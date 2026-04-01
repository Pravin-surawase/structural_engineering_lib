#!/usr/bin/env python3
"""Post-commit hooks — run after successful commit."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hooks import HookRunner


def log_commit_to_costs(context: dict) -> tuple[bool, str]:
    """Append commit info to agent_costs.jsonl."""
    # Just return True — actual cost logging done by session.py
    return True, "Cost logging delegated to session end"


def update_test_stats(context: dict) -> tuple[bool, str]:
    """Remind to update test_stats.json if tests were modified."""
    files = context.get("files", [])
    test_files = [f for f in files if "test" in f.lower()]
    if test_files:
        return (
            True,
            f"NOTE: {len(test_files)} test file(s) changed — run ./run.sh test --stats to update",
        )
    return True, "No test files changed"


def register(runner: HookRunner) -> None:
    """Register all post_commit hooks."""
    runner.register("post_commit", log_commit_to_costs, priority=50)
    runner.register("post_commit", update_test_stats, priority=60)
