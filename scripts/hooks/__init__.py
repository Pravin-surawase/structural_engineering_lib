#!/usr/bin/env python3
"""
Hook framework for pre/post execution hooks.

Hooks are registered by event name and run in order.
Each hook is a callable that receives a context dict and returns (proceed: bool, message: str).

Events:
  pre_commit     — Before ai_commit.sh stages/commits
  post_commit    — After successful commit
  pre_route      — Before prompt_router routes a task
  pre_file_write — Before file edits in structural_lib
  post_test      — After pytest run completes

Usage:
    from hooks import HookRunner
    runner = HookRunner()
    runner.load_hooks()
    proceed, messages = runner.run("pre_commit", {"files": ["api.py"], "message": "feat: X"})
"""

from __future__ import annotations

import importlib
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

# Ensure scripts/ is on sys.path for _lib imports
_SCRIPTS_DIR = str(Path(__file__).resolve().parent.parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from _lib.output import StatusLine  # noqa: E402
from _lib.utils import REPO_ROOT  # noqa: E402

# Valid event names
VALID_EVENTS = frozenset(
    {
        "pre_commit",
        "post_commit",
        "pre_route",
        "pre_file_write",
        "post_test",
    }
)

# Hook modules to auto-discover (basenames without .py)
_HOOK_MODULES = ("pre_commit", "post_commit", "pre_route")


@dataclass
class HookResult:
    """Result from a single hook execution."""

    hook_name: str
    passed: bool
    message: str
    duration_ms: float


@dataclass
class _RegisteredHook:
    """Internal: a hook function with its metadata."""

    event: str
    fn: Callable[[dict[str, Any]], tuple[bool, str]]
    priority: int
    name: str


class HookRunner:
    """Registry and executor for lifecycle hooks."""

    def __init__(self) -> None:
        self._hooks: dict[str, list[_RegisteredHook]] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        event: str,
        hook_fn: Callable[[dict[str, Any]], tuple[bool, str]],
        priority: int = 50,
    ) -> None:
        """Register a hook function for *event*.

        Lower *priority* values run first.
        """
        if event not in VALID_EVENTS:
            raise ValueError(
                f"Unknown event {event!r}. Valid events: {sorted(VALID_EVENTS)}"
            )
        entry = _RegisteredHook(
            event=event,
            fn=hook_fn,
            priority=priority,
            name=hook_fn.__name__,
        )
        self._hooks.setdefault(event, []).append(entry)
        # Keep sorted by priority
        self._hooks[event].sort(key=lambda h: h.priority)

    # ------------------------------------------------------------------
    # Auto-discovery
    # ------------------------------------------------------------------

    def load_hooks(self) -> None:
        """Auto-discover and load all hook modules from scripts/hooks/."""
        hooks_dir = Path(__file__).resolve().parent
        for mod_name in _HOOK_MODULES:
            mod_path = hooks_dir / f"{mod_name}.py"
            if not mod_path.exists():
                StatusLine.warn(f"Hook module not found: {mod_path.name}")
                continue
            try:
                # Import as scripts.hooks.<mod_name> or directly
                spec_name = f"scripts.hooks.{mod_name}"
                if spec_name in sys.modules:
                    mod = sys.modules[spec_name]
                else:
                    spec = importlib.util.spec_from_file_location(spec_name, mod_path)
                    if spec is None or spec.loader is None:
                        StatusLine.warn(f"Cannot load hook module: {mod_name}")
                        continue
                    mod = importlib.util.module_from_spec(spec)
                    sys.modules[spec_name] = mod
                    spec.loader.exec_module(mod)

                # Each module must expose register(runner)
                register_fn = getattr(mod, "register", None)
                if register_fn is None:
                    StatusLine.warn(
                        f"Hook module {mod_name} has no register() function"
                    )
                    continue
                register_fn(self)
            except Exception as exc:
                StatusLine.fail(f"Error loading hook module {mod_name}: {exc}")

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run(
        self, event: str, context: dict[str, Any] | None = None
    ) -> tuple[bool, list[HookResult]]:
        """Run all hooks registered for *event*.

        Returns (all_passed, list_of_HookResult).
        Individual hook exceptions are caught and reported as failures.
        """
        if event not in VALID_EVENTS:
            raise ValueError(
                f"Unknown event {event!r}. Valid events: {sorted(VALID_EVENTS)}"
            )
        context = context or {}
        results: list[HookResult] = []
        all_passed = True

        for hook in self._hooks.get(event, []):
            t0 = time.monotonic()
            try:
                passed, message = hook.fn(context)
            except Exception as exc:
                passed = False
                message = f"EXCEPTION in {hook.name}: {exc}"
            duration_ms = (time.monotonic() - t0) * 1000.0

            results.append(
                HookResult(
                    hook_name=hook.name,
                    passed=passed,
                    message=message,
                    duration_ms=round(duration_ms, 2),
                )
            )
            if not passed:
                all_passed = False

        return all_passed, results

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def list_hooks(self) -> dict[str, list[str]]:
        """Return registered hook names grouped by event."""
        return {
            event: [h.name for h in hooks]
            for event, hooks in sorted(self._hooks.items())
        }
