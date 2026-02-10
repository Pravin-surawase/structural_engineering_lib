"""Unified output formatting for scripts/.

Provides consistent JSON, table, and summary output across all validation
and audit scripts. Eliminates 26+ scripts each reimplementing JSON/table output.

Usage from any script in scripts/:
    from _lib.output import print_json, print_table, print_summary, StatusLine

    # JSON output
    print_json({"issues": [...], "summary": {...}})

    # Markdown-style table
    print_table(["File", "Line", "Issue"], rows)

    # Summary line with pass/fail
    print_summary("Architecture Check", passed=5, failed=2, warnings=1)

    # Status indicator
    StatusLine.ok("All checks passed")
    StatusLine.fail("2 violations found")
    StatusLine.warn("Deprecated pattern detected")
    StatusLine.skip("No files to check")
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from typing import Any, Sequence


def _serialize(obj: Any) -> Any:
    """Make objects JSON-serializable.

    Handles Path, dataclass, sets, and other common types.
    """
    if isinstance(obj, Path):
        return str(obj)
    if is_dataclass(obj) and not isinstance(obj, type):
        return asdict(obj)
    if isinstance(obj, set):
        return sorted(obj)
    if isinstance(obj, Exception):
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def print_json(data: Any, *, indent: int = 2, file: Any = None) -> None:
    """Print data as formatted JSON to stdout.

    Args:
        data: Any JSON-serializable data (dicts, lists, dataclasses, Paths).
        indent: JSON indentation (default 2).
        file: Output file object (default sys.stdout).
    """
    output = json.dumps(data, indent=indent, default=_serialize)
    print(output, file=file or sys.stdout)


def print_table(
    headers: Sequence[str],
    rows: Sequence[Sequence[str]],
    *,
    file: Any = None,
) -> None:
    """Print a markdown-style table.

    Args:
        headers: Column header strings.
        rows: List of row data (each row is a sequence of strings).
        file: Output file object (default sys.stdout).

    Example:
        print_table(["File", "Issues"], [["api.py", "3"], ["core.py", "0"]])
        # | File    | Issues |
        # |---------|--------|
        # | api.py  | 3      |
        # | core.py | 0      |
    """
    out = file or sys.stdout
    if not headers:
        return

    # Calculate column widths
    str_rows = [[str(cell) for cell in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in str_rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))

    # Print header
    header_line = "| " + " | ".join(h.ljust(w) for h, w in zip(headers, widths)) + " |"
    separator = "|-" + "-|-".join("-" * w for w in widths) + "-|"
    print(header_line, file=out)
    print(separator, file=out)

    # Print rows
    for row in str_rows:
        padded = []
        for i, w in enumerate(widths):
            cell = row[i] if i < len(row) else ""
            padded.append(cell.ljust(w))
        print("| " + " | ".join(padded) + " |", file=out)


def print_summary(
    title: str,
    *,
    passed: int = 0,
    failed: int = 0,
    warnings: int = 0,
    skipped: int = 0,
    file: Any = None,
) -> None:
    """Print a formatted summary line with counts.

    Args:
        title: Check/tool name.
        passed: Number of passing checks.
        failed: Number of failures.
        warnings: Number of warnings.
        skipped: Number of skipped items.
        file: Output file object.

    Example:
        print_summary("API Check", passed=5, failed=2, warnings=1)
        # ❌ API Check: 5 passed, 2 failed, 1 warning
    """
    out = file or sys.stdout
    parts = []
    if passed:
        parts.append(f"{passed} passed")
    if failed:
        parts.append(f"{failed} failed")
    if warnings:
        parts.append(f"{warnings} warning{'s' if warnings != 1 else ''}")
    if skipped:
        parts.append(f"{skipped} skipped")

    icon = "✅" if failed == 0 else "❌"
    detail = ", ".join(parts) if parts else "no items"
    print(f"{icon} {title}: {detail}", file=out)


@dataclass
class CheckResult:
    """Standardized result from a check/validation.

    Use this to collect results across multiple checks and then
    output them as JSON or table in a consistent format.
    """

    name: str
    passed: bool
    message: str = ""
    details: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON output."""
        d: dict[str, Any] = {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
        }
        if self.details:
            d["details"] = self.details
        return d


class StatusLine:
    """Print status indicator lines with consistent formatting.

    StatusLine.ok("All checks passed")     → ✅ All checks passed
    StatusLine.fail("2 violations found")  → ❌ 2 violations found
    StatusLine.warn("Deprecated pattern")  → ⚠️  Deprecated pattern
    StatusLine.skip("No files to check")   → ⏭️  No files to check
    StatusLine.info("Scanning 42 files")   → ℹ️  Scanning 42 files
    """

    @staticmethod
    def ok(msg: str, *, file: Any = None) -> None:
        """Print success status."""
        print(f"✅ {msg}", file=file or sys.stdout)

    @staticmethod
    def fail(msg: str, *, file: Any = None) -> None:
        """Print failure status."""
        print(f"❌ {msg}", file=file or sys.stderr)

    @staticmethod
    def warn(msg: str, *, file: Any = None) -> None:
        """Print warning status."""
        print(f"⚠️  {msg}", file=file or sys.stderr)

    @staticmethod
    def skip(msg: str, *, file: Any = None) -> None:
        """Print skipped status."""
        print(f"⏭️  {msg}", file=file or sys.stdout)

    @staticmethod
    def info(msg: str, *, file: Any = None) -> None:
        """Print info status."""
        print(f"ℹ️  {msg}", file=file or sys.stdout)
