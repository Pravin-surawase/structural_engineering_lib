#!/usr/bin/env python3
"""Compatibility bridge from retired folder indexes to live context summaries.

When to use: Only for an older caller that still invokes the former index
generator. Generic committed folder indexes were retired by MAINT-012B; this
bridge is read-only and points callers to ./run.sh context.
"""

from __future__ import annotations

import argparse
import sys

from repo_context import main as context_main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deprecated read-only bridge to live repository context"
    )
    parser.add_argument("folder", nargs="?")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--json-only", action="store_true")
    parser.add_argument("--md-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-new-index", action="store_true")
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(
        "DEPRECATED: committed folder indexes are retired; "
        "use ./run.sh context. No files will be written."
    )
    if args.allow_new_index or args.json_only or args.md_only:
        print(
            "ERROR: index creation/output flags are no longer supported; "
            "use ./run.sh context summary <area-or-folder>",
            file=sys.stderr,
        )
        return 2
    if args.check:
        return context_main(["validate"])
    if not args.folder and not args.all:
        build_parser().print_help()
        return 0
    target = "repository" if args.all else str(args.folder)
    return context_main(["summary", target])


if __name__ == "__main__":
    raise SystemExit(main())
