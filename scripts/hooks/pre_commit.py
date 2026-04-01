#!/usr/bin/env python3
"""Pre-commit hooks — run before ai_commit.sh."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hooks import HookRunner


def check_no_force_flags(context: dict) -> tuple[bool, str]:
    """Reject commits with --force or --no-verify flags."""
    message = context.get("message", "")
    if "--force" in message or "--no-verify" in message:
        return False, "BLOCKED: --force/--no-verify flags detected"
    return True, "No force flags"


def check_commit_message_format(context: dict) -> tuple[bool, str]:
    """Validate conventional commit format: type(scope): description."""
    message = context.get("message", "")
    if not message:
        return True, "No message to validate"
    pattern = r"^(feat|fix|docs|refactor|test|chore|ci|perf|style|build)(\(.+\))?: .+"
    if not re.match(pattern, message):
        return (
            False,
            f"WARN: Commit message doesn't match conventional format: {message}",
        )
    return True, "Commit message format OK"


def check_no_stub_edits(context: dict) -> tuple[bool, str]:
    """Warn if editing the api.py stub instead of services/api.py."""
    files = context.get("files", [])
    for f in files:
        if f.endswith("structural_lib/api.py") and "services" not in f:
            return (
                False,
                "BLOCKED: Editing api.py stub — real code is in services/api.py",
            )
    return True, "No stub edits"


def register(runner: HookRunner) -> None:
    """Register all pre_commit hooks."""
    runner.register("pre_commit", check_no_force_flags, priority=10)
    runner.register("pre_commit", check_commit_message_format, priority=20)
    runner.register("pre_commit", check_no_stub_edits, priority=30)
