#!/usr/bin/env python3
"""Collect a compact diagnostics bundle for debugging and support."""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def _run(cmd: list[str]) -> str:
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        return f"ERROR: {stderr}" if stderr else "ERROR: command failed"
    return result.stdout.strip()


def _tail(path: Path, lines: int) -> list[str]:
    if not path.exists():
        return ["(missing)"]
    try:
        content = path.read_text(errors="replace").splitlines()
    except Exception as exc:
        return [f"(error reading file: {exc})"]
    if lines <= 0:
        return ["(skipped)"]
    return content[-lines:] if content else ["(empty)"]


def _section(title: str, body: list[str]) -> list[str]:
    return [f"{title}", "-" * len(title), *body, ""]


def collect(lines: int) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    branch = _run(["git", "branch", "--show-current"])
    commit = _run(["git", "rev-parse", "--short", "HEAD"])
    status = _run(["git", "status", "--porcelain"])
    dirty = "clean" if status == "" else f"{len(status.splitlines())} change(s)"

    env_debug = os.getenv("DEBUG", "")
    venv = os.getenv("VIRTUAL_ENV", "")

    lines_out: list[str] = [
        "Diagnostics Report",
        "==================",
        f"Timestamp: {now}",
        f"Repo: {REPO_ROOT}",
        "",
    ]

    lines_out += _section(
        "Environment",
        [
            f"Python: {sys.version.split()[0]} ({sys.executable})",
            f"OS: {platform.platform()}",
            f"DEBUG: {env_debug or '(unset)'}",
            f"VIRTUAL_ENV: {venv or '(unset)'}",
        ],
    )

    lines_out += _section(
        "Git",
        [
            f"Branch: {branch}",
            f"Commit: {commit}",
            f"Working tree: {dirty}",
        ],
    )

    log_paths = [
        REPO_ROOT / "logs" / "git_workflow.log",
        REPO_ROOT / "logs" / "ci_monitor.log",
    ]
    for path in log_paths:
        lines_out += _section(
            f"Log tail: {path.relative_to(REPO_ROOT)}",
            _tail(path, lines),
        )

    return "\n".join(lines_out).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a diagnostics bundle.")
    parser.add_argument("--out", help="Write output to a file instead of stdout.")
    parser.add_argument(
        "--lines",
        type=int,
        default=80,
        help="Lines to include from each log file.",
    )
    args = parser.parse_args()

    report = collect(args.lines)
    if args.out:
        out_path = Path(args.out)
        out_path.write_text(report, encoding="utf-8")
        print(f"Wrote diagnostics bundle to {out_path}")
    else:
        print(report, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
