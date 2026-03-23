#!/usr/bin/env python3
"""Scan codebase and sync stale numbers across documentation files.

Scans actual code to get current counts (tests, scripts, hooks, endpoints,
etc.) and updates documentation files that reference these numbers.

USAGE:
    python scripts/sync_numbers.py           # Scan + report (dry run)
    python scripts/sync_numbers.py --fix     # Scan + update files
    python scripts/sync_numbers.py --json    # Machine-readable output

Part of the "Simplify Agent Documentation Work" initiative (Session 91).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT, run_command
from _lib.output import StatusLine, print_json, print_summary


# ─── Targets ─────────────────────────────────────────────────────────────────

DOCS_TO_SYNC = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "llms.txt",
    REPO_ROOT / "CLAUDE.md",
    REPO_ROOT / ".github" / "copilot-instructions.md",
    REPO_ROOT / "docs" / "getting-started" / "agent-bootstrap.md",
]


# ─── Data ────────────────────────────────────────────────────────────────────

@dataclass
class Metrics:
    """Current codebase metrics from scanning."""

    test_count: int = 0
    script_count: int = 0
    hook_count: int = 0
    hook_file_count: int = 0
    endpoint_count: int = 0
    router_count: int = 0
    api_public_count: int = 0
    api_private_count: int = 0
    component_count: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "test_count": self.test_count,
            "script_count": self.script_count,
            "hook_count": self.hook_count,
            "hook_file_count": self.hook_file_count,
            "endpoint_count": self.endpoint_count,
            "router_count": self.router_count,
            "api_public_count": self.api_public_count,
            "api_private_count": self.api_private_count,
            "component_count": self.component_count,
        }


@dataclass
class Update:
    """A pending update to a documentation file."""

    file: Path
    line_num: int
    old_text: str
    new_text: str
    metric: str

    @property
    def file_rel(self) -> str:
        return str(self.file.relative_to(REPO_ROOT))


# ─── Scanners ────────────────────────────────────────────────────────────────

def scan_tests() -> int:
    """Count tests via pytest --co (collection only, fast)."""
    python_dir = REPO_ROOT / "Python"
    venv_python = REPO_ROOT / ".venv" / "bin" / "python"
    exe = str(venv_python) if venv_python.exists() else sys.executable

    result = run_command(
        [exe, "-m", "pytest", "tests/", "--co"],
        cwd=python_dir,
        timeout=60,
    )
    # Parse "3199 tests collected in 0.58s" from either stdout or stderr
    for output in (result.stdout or "", result.stderr or ""):
        for line in output.splitlines():
            match = re.search(r"(\d+)\s+tests?\s+collected", line)
            if match:
                return int(match.group(1))
    return 0


def scan_scripts() -> int:
    """Count .py and .sh scripts in scripts/ (top-level only)."""
    scripts_dir = REPO_ROOT / "scripts"
    count = 0
    for f in scripts_dir.iterdir():
        if f.is_file() and f.suffix in (".py", ".sh") and not f.name.startswith("__"):
            count += 1
    return count


def scan_hooks() -> tuple[int, int]:
    """Count exported hooks and hook files. Returns (hook_count, file_count)."""
    hooks_dir = REPO_ROOT / "react_app" / "src" / "hooks"
    if not hooks_dir.exists():
        return 0, 0

    hook_files = [f for f in hooks_dir.iterdir() if f.suffix == ".ts"]
    hook_count = 0
    for f in hook_files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        hook_count += len(re.findall(r"^export\s+function\s+use", content, re.MULTILINE))

    return hook_count, len(hook_files)


def scan_endpoints() -> tuple[int, int]:
    """Count API endpoints and router files. Returns (endpoint_count, router_count)."""
    routers_dir = REPO_ROOT / "fastapi_app" / "routers"
    if not routers_dir.exists():
        return 0, 0

    router_files = [
        f for f in routers_dir.iterdir()
        if f.suffix == ".py" and f.name not in ("__init__.py",)
    ]

    endpoint_count = 0
    for f in router_files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        endpoint_count += len(re.findall(
            r"@router\.(get|post|put|delete|patch|websocket)\b", content
        ))

    return endpoint_count, len(router_files)


def scan_api_functions() -> tuple[int, int]:
    """Count public and private functions in services/api.py. Returns (public, private)."""
    api_file = REPO_ROOT / "Python" / "structural_lib" / "services" / "api.py"
    if not api_file.exists():
        return 0, 0

    content = api_file.read_text(encoding="utf-8", errors="ignore")
    public = len(re.findall(r"^def (?!_)\w+", content, re.MULTILINE))
    private = len(re.findall(r"^def _\w+", content, re.MULTILINE))
    return public, private


def scan_components() -> int:
    """Count .tsx component files."""
    comp_dir = REPO_ROOT / "react_app" / "src" / "components"
    if not comp_dir.exists():
        return 0
    return len(list(comp_dir.rglob("*.tsx")))


def scan_all() -> Metrics:
    """Run all scanners and return current metrics."""
    m = Metrics()
    m.test_count = scan_tests()
    m.script_count = scan_scripts()
    m.hook_count, m.hook_file_count = scan_hooks()
    m.endpoint_count, m.router_count = scan_endpoints()
    m.api_public_count, m.api_private_count = scan_api_functions()
    m.component_count = scan_components()
    return m


# ─── Updaters ────────────────────────────────────────────────────────────────

# Each rule: (file_relative_path, regex_pattern, replacement_template, metric_name)
# The regex must have a capture group around the number to replace.
# The replacement_template uses {value} for the new number.

UpdateRule = tuple[str, str, str, str]


def get_update_rules() -> list[UpdateRule]:
    """Define all number-replacement rules across doc files.

    Each rule maps a regex pattern in a specific file to a metric.
    Patterns include enough context to avoid false matches.
    """
    return [
        # README.md — test count in "Quality" line
        ("README.md", r"Contract-tested APIs, (\d+) tests,", "Contract-tested APIs, {value} tests,", "test_count"),
        # README.md — test count in "Comprehensive Testing" line
        ("README.md", r"\*\*Comprehensive Testing:\*\* (\d+) tests,", "**Comprehensive Testing:** {value} tests,", "test_count"),
        # README.md — test count in Trust table
        ("README.md", r"\*\*Test Coverage\*\* \| (\d+) tests,", "**Test Coverage** | {value} tests,", "test_count"),
        # README.md — script count
        ("README.md", r"(\d+) automation scripts", "{value} automation scripts", "script_count"),
        # CLAUDE.md — router count in grep hint
        ("CLAUDE.md", r"FastAPI endpoints \((\d+) routers\)", "FastAPI endpoints ({value} routers)", "router_count"),
        # CLAUDE.md — function count hint
        ("CLAUDE.md", r"(\d+) public \+ (\d+) private helpers", "{public} public + {private} private helpers", "api_functions"),
        # copilot-instructions.md — router count
        (".github/copilot-instructions.md", r"FastAPI routes \((\d+) routers\)", "FastAPI routes ({value} routers)", "router_count"),
        # copilot-instructions.md — function count
        (".github/copilot-instructions.md", r"(\d+) public \+ (\d+) private helpers", "{public} public + {private} private helpers", "api_functions"),
        # llms.txt — endpoint count
        ("llms.txt", r"(\d+) endpoints across (\d+) routers", "{endpoints} endpoints across {routers} routers", "endpoint_router"),
        # agent-bootstrap.md — endpoint/router count
        ("docs/getting-started/agent-bootstrap.md", r"(\d+) endpoints across (\d+) routers", "{endpoints} endpoints across {routers} routers", "endpoint_router"),
        # agent-bootstrap.md — function count
        ("docs/getting-started/agent-bootstrap.md", r"(\d+) public functions \+ (\d+) private helpers", "{public} public functions + {private} private helpers", "api_functions"),
    ]


def find_updates(metrics: Metrics) -> list[Update]:
    """Compare current metrics against doc files and find needed updates."""
    updates: list[Update] = []

    for file_rel, pattern, template, metric_name in get_update_rules():
        filepath = REPO_ROOT / file_rel
        if not filepath.exists():
            continue

        lines = filepath.read_text(encoding="utf-8").splitlines()
        regex = re.compile(pattern)

        for i, line in enumerate(lines):
            match = regex.search(line)
            if not match:
                continue

            # Build replacement based on metric type
            if metric_name == "test_count":
                old_val = int(match.group(1))
                new_val = metrics.test_count
                if old_val == new_val:
                    continue
                new_text = line[:match.start()] + template.format(value=new_val) + line[match.end():]

            elif metric_name == "script_count":
                old_val = int(match.group(1))
                new_val = metrics.script_count
                if old_val == new_val:
                    continue
                new_text = line[:match.start()] + template.format(value=new_val) + line[match.end():]

            elif metric_name == "router_count":
                old_val = int(match.group(1))
                new_val = metrics.router_count
                if old_val == new_val:
                    continue
                new_text = line[:match.start()] + template.format(value=new_val) + line[match.end():]

            elif metric_name == "api_functions":
                old_pub = int(match.group(1))
                old_priv = int(match.group(2))
                if old_pub == metrics.api_public_count and old_priv == metrics.api_private_count:
                    continue
                replacement = template.format(
                    public=metrics.api_public_count,
                    private=metrics.api_private_count,
                )
                new_text = line[:match.start()] + replacement + line[match.end():]

            elif metric_name == "endpoint_router":
                old_ep = int(match.group(1))
                old_rt = int(match.group(2))
                if old_ep == metrics.endpoint_count and old_rt == metrics.router_count:
                    continue
                replacement = template.format(
                    endpoints=metrics.endpoint_count,
                    routers=metrics.router_count,
                )
                new_text = line[:match.start()] + replacement + line[match.end():]

            else:
                continue

            updates.append(Update(
                file=filepath,
                line_num=i + 1,
                old_text=line.strip(),
                new_text=new_text.strip(),
                metric=metric_name,
            ))

    return updates


def apply_updates(updates: list[Update]) -> int:
    """Apply pending updates to files. Returns number of files changed."""
    # Group by file
    by_file: dict[Path, list[Update]] = {}
    for u in updates:
        by_file.setdefault(u.file, []).append(u)

    changed = 0
    for filepath, file_updates in by_file.items():
        content = filepath.read_text(encoding="utf-8")
        for u in file_updates:
            if u.old_text in content:
                content = content.replace(u.old_text, u.new_text, 1)
        filepath.write_text(content, encoding="utf-8")
        changed += 1

    return changed


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="sync_numbers.py",
        description="Scan codebase and sync stale numbers across documentation files.",
    )
    parser.add_argument("--fix", action="store_true", help="Apply updates to files (default: dry run)")
    parser.add_argument("--json", action="store_true", help="Output metrics and updates as JSON")
    args = parser.parse_args()

    # Scan
    if not args.json:
        print("🔍 Scanning codebase...")
    metrics = scan_all()

    if args.json:
        updates = find_updates(metrics)
        result = {
            **metrics.as_dict(),
            "updates": [
                {"file": u.file_rel, "line": u.line_num, "metric": u.metric,
                 "old": u.old_text, "new": u.new_text}
                for u in updates
            ],
        }
        print_json(result)
        return 0

    # Report
    print()
    print("📊 Current Metrics:")
    print(f"  Tests:       {metrics.test_count}")
    print(f"  Scripts:     {metrics.script_count}")
    print(f"  Hooks:       {metrics.hook_count} (in {metrics.hook_file_count} files)")
    print(f"  Endpoints:   {metrics.endpoint_count} across {metrics.router_count} routers")
    print(f"  API funcs:   {metrics.api_public_count} public + {metrics.api_private_count} private")
    print(f"  Components:  {metrics.component_count}")
    print()

    # Find updates needed
    updates = find_updates(metrics)

    if not updates:
        StatusLine.ok("All numbers are up to date across documentation files")
        return 0

    print(f"📝 {len(updates)} update(s) needed:")
    for u in updates:
        print(f"  {u.file_rel}:{u.line_num} [{u.metric}]")
        print(f"    - {u.old_text}")
        print(f"    + {u.new_text}")
    print()

    if args.fix:
        changed = apply_updates(updates)
        StatusLine.ok(f"Updated {changed} file(s) with {len(updates)} change(s)")
    else:
        StatusLine.warn(f"{len(updates)} stale number(s) found. Run with --fix to update.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
