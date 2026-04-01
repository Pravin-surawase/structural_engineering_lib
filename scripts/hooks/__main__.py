#!/usr/bin/env python3
"""CLI for hook management.

Usage:
    python -m scripts.hooks list                    # List all registered hooks
    python -m scripts.hooks run pre_commit          # Run hooks for event (dry-run)
    python -m scripts.hooks test                    # Run all hooks as self-test
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure scripts/ is on sys.path for _lib imports
_SCRIPTS_DIR = str(Path(__file__).resolve().parent.parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from _lib.output import StatusLine  # noqa: E402
from hooks import VALID_EVENTS, HookRunner  # noqa: E402


def _get_runner() -> HookRunner:
    runner = HookRunner()
    runner.load_hooks()
    return runner


def cmd_list(args: argparse.Namespace) -> int:
    """List all registered hooks."""
    runner = _get_runner()
    hooks_map = runner.list_hooks()
    if not hooks_map:
        StatusLine.warn("No hooks registered")
        return 0

    for event, names in hooks_map.items():
        print(f"\n  {event}:")
        for name in names:
            print(f"    - {name}")
    print()
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """Run hooks for a given event with an empty context (dry-run)."""
    event = args.event
    if event not in VALID_EVENTS:
        StatusLine.fail(f"Unknown event: {event}. Valid: {sorted(VALID_EVENTS)}")
        return 1

    runner = _get_runner()
    context: dict = {}
    if args.message:
        context["message"] = args.message

    all_passed, results = runner.run(event, context)

    for r in results:
        fn = StatusLine.ok if r.passed else StatusLine.fail
        fn(f"[{r.hook_name}] {r.message}  ({r.duration_ms:.1f}ms)")

    if not results:
        StatusLine.skip(f"No hooks registered for {event}")

    summary = "PASSED" if all_passed else "FAILED"
    print(f"\n  {event}: {summary} ({len(results)} hook(s))\n")
    return 0 if all_passed else 1


def cmd_test(args: argparse.Namespace) -> int:
    """Run all hooks for all events as a self-test."""
    runner = _get_runner()
    total = 0
    failed = 0

    for event in sorted(VALID_EVENTS):
        all_passed, results = runner.run(event, {})
        for r in results:
            total += 1
            fn = StatusLine.ok if r.passed else StatusLine.fail
            fn(f"[{event}/{r.hook_name}] {r.message}")
            if not r.passed:
                failed += 1

    print(f"\n  Self-test: {total - failed}/{total} hooks passed\n")
    return 0 if failed == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="hooks",
        description="Hook framework CLI — list, run, and test lifecycle hooks.",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List all registered hooks")

    run_p = sub.add_parser("run", help="Run hooks for an event (dry-run)")
    run_p.add_argument("event", help=f"Event name: {sorted(VALID_EVENTS)}")
    run_p.add_argument(
        "--message", "-m", default="", help="Commit message (for pre_commit)"
    )

    sub.add_parser("test", help="Run all hooks as self-test")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return 0

    dispatch = {"list": cmd_list, "run": cmd_run, "test": cmd_test}
    return dispatch[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
