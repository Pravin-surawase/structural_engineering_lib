#!/usr/bin/env python3
"""Unified check orchestrator — runs all validation scripts in parallel.

When to use: When you want a single command to validate the entire codebase.
Called by `./run.sh check` or directly.

USAGE:
    python scripts/check_all.py                      # Run ALL checks
    python scripts/check_all.py --quick              # Fast subset (<30s)
    python scripts/check_all.py --category api       # One category only
    python scripts/check_all.py --fix                # Auto-fix what's possible
    python scripts/check_all.py --json               # Machine-readable output
    python scripts/check_all.py --list               # Show categories and scripts
    python scripts/check_all.py --changed            # Only categories for changed files
    python scripts/check_all.py --pre-commit         # Run pre-commit hooks

Exit Codes:
    0: All checks passed (or warnings only)
    1: One or more checks failed
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from concurrent.futures import as_completed
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT
from _lib.output import StatusLine, print_json

VENV_PYTHON = str(REPO_ROOT / ".venv" / "bin" / "python")
SCRIPTS_DIR = REPO_ROOT / "scripts"

# Detect sensible default workers based on system
_default_workers = min(4, max(1, (os.cpu_count() or 2)))

# ── Check Registry ─────────────────────────────────────────────────────────


@dataclass
class Check:
    """Definition of a single validation check."""

    name: str
    cmd: list[str]
    timeout: int = 60
    fix_cmd: list[str] | None = None  # command to run with --fix


@dataclass
class Category:
    """A group of related checks."""

    name: str
    label: str
    checks: list[Check]
    description: str = ""


def _py(script: str, *args: str) -> list[str]:
    """Build a Python script command."""
    return [VENV_PYTHON, str(SCRIPTS_DIR / script), *args]


def _sh(script: str, *args: str) -> list[str]:
    """Build a shell script command."""
    return ["bash", str(SCRIPTS_DIR / script), *args]


# Category definitions — the source of truth for what gets checked.
# Each check must be: fast (<60s), idempotent, exit 0 on success.
CATEGORIES: list[Category] = [
    Category(
        name="api",
        label="API",
        description="API contracts, manifest, endpoint validation",
        checks=[
            Check("API validation", _py("check_api.py", "--all")),
            Check("API contracts", _py("validate_api_contracts.py")),
            Check(
                "API manifest", _py("generate_api_manifest.py", "--check"), timeout=30
            ),
        ],
    ),
    Category(
        name="docs",
        label="Docs",
        description="Links, doc versions, metadata, tasks format",
        checks=[
            Check(
                "Doc validation",
                _py("check_docs.py", "--all"),
                fix_cmd=_py("check_docs.py", "--all", "--fix"),
            ),
            Check("Broken links", _py("check_links.py")),
            Check("Doc versions", _py("check_doc_versions.py")),
            Check("CLI reference", _py("check_cli_reference.py")),
            Check("Tasks format", _py("check_tasks_format.py")),
            Check("Brief length", _py("check_next_session_brief_length.py")),
            Check("Scripts index", _py("check_scripts_index.py")),
        ],
    ),
    Category(
        name="arch",
        label="Architecture",
        description="Layer boundaries, circular imports, import validation",
        checks=[
            Check(
                "Architecture boundaries",
                _py("check_architecture_boundaries.py"),
                timeout=90,
            ),
            Check("Circular imports", _py("check_circular_imports.py"), timeout=90),
            Check("Import validation", _py("validate_imports.py")),
        ],
    ),
    Category(
        name="governance",
        label="Governance",
        description="Governance rules, repo hygiene, Python version, schemas",
        checks=[
            Check("Governance rules", _py("check_governance.py", "--full")),
            Check("Repo hygiene", _py("check_repo_hygiene.py")),
            Check("Python version", _py("check_python_version.py")),
            Check("Schema snapshots", _py("validate_schema_snapshots.py"), timeout=90),
        ],
    ),
    Category(
        name="fastapi",
        label="FastAPI",
        description="FastAPI issues, Docker config, OpenAPI snapshot",
        checks=[
            Check("FastAPI issues", _py("check_fastapi_issues.py")),
            Check("Docker config", _py("check_docker_config.py")),
            Check("OpenAPI snapshot", _py("check_openapi_snapshot.py")),
        ],
    ),
    Category(
        name="git",
        label="Git",
        description="Git state, unfinished merges, version consistency, script budget",
        checks=[
            Check("Git state", _sh("validate_git_state.sh")),
            Check("Unfinished merge", _sh("check_unfinished_merge.sh")),
            Check("Version consistency", _sh("check_version_consistency.sh")),
            Check("Script line budget", _py("check_git_script_budget.py")),
        ],
    ),
    Category(
        name="stale",
        label="Stale Refs",
        description="Stale script references, instruction drift, bootstrap freshness",
        checks=[
            Check("Script references", _py("validate_script_refs.py")),
            Check("Instruction drift", _py("check_instruction_drift.py")),
            Check("Bootstrap freshness", _py("check_bootstrap_freshness.py")),
        ],
    ),
    Category(
        name="code",
        label="Code Quality",
        description="Type annotations",
        checks=[
            Check("Type annotations", _py("check_type_annotations.py"), timeout=90),
        ],
    ),
]

# Quick checks — a curated fast subset
QUICK_CHECKS: dict[str, list[str]] = {
    "docs": ["Broken links", "Doc versions", "Brief length"],
    "arch": ["Import validation"],
    "governance": ["Repo hygiene"],
    "git": ["Git state", "Unfinished merge"],
    "stale": ["Script references"],
}

# File path patterns → categories for --changed mode
_PATH_TO_CATEGORIES: list[tuple[str, list[str]]] = [
    ("Python/structural_lib/services/api", ["api"]),
    ("Python/structural_lib/", ["arch", "code"]),
    ("fastapi_app/", ["api", "fastapi"]),
    ("docs/", ["docs", "stale"]),
    ("scripts/", ["stale", "governance"]),
    ("react_app/", []),  # No script-based checks for React yet
    (".pre-commit", ["governance"]),
    ("docker-compose", ["fastapi"]),
    ("Dockerfile", ["fastapi"]),
    ("pyproject.toml", ["governance", "arch"]),
]


def _detect_changed_categories() -> set[str]:
    """Detect which categories to run based on git diff."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            # Fallback: diff against working tree
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                timeout=10,
            )
    except Exception:
        return set()  # On error, return empty (caller falls back to all)

    changed_files = result.stdout.strip().splitlines()
    if not changed_files:
        return set()

    categories: set[str] = set()
    # Always run git checks
    categories.add("git")

    for filepath in changed_files:
        for pattern, cats in _PATH_TO_CATEGORIES:
            if filepath.startswith(pattern):
                categories.update(cats)
                break

    return categories


def _run_pre_commit(fix: bool = False) -> int:
    """Run pre-commit hooks and return exit code."""
    cmd = ["pre-commit", "run", "--all-files"]
    if fix:
        # pre-commit auto-fixes by default for formatters
        pass

    print("🔍 Running pre-commit hooks...")
    try:
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            timeout=300,
        )
        return result.returncode
    except FileNotFoundError:
        print("  ❌ pre-commit not installed. Run: pip install pre-commit")
        return 1
    except subprocess.TimeoutExpired:
        print("  ⏱️  pre-commit timed out after 300s")
        return 1


# ── Runner ─────────────────────────────────────────────────────────────────


@dataclass
class CheckResult:
    """Result of running a single check."""

    name: str
    category: str
    passed: bool
    exit_code: int
    duration: float
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    error: str = ""


def _run_check(check: Check, category_name: str, use_fix: bool = False) -> CheckResult:
    """Run a single check and return the result."""
    cmd = check.fix_cmd if (use_fix and check.fix_cmd) else check.cmd
    start = time.monotonic()

    try:
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=check.timeout,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        elapsed = time.monotonic() - start

        return CheckResult(
            name=check.name,
            category=category_name,
            passed=(result.returncode == 0),
            exit_code=result.returncode,
            duration=elapsed,
            stdout=result.stdout,
            stderr=result.stderr,
        )
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start
        return CheckResult(
            name=check.name,
            category=category_name,
            passed=False,
            exit_code=-1,
            duration=elapsed,
            timed_out=True,
            error=f"Timed out after {check.timeout}s",
        )
    except FileNotFoundError as e:
        elapsed = time.monotonic() - start
        return CheckResult(
            name=check.name,
            category=category_name,
            passed=False,
            exit_code=-1,
            duration=elapsed,
            error=f"Script not found: {e}",
        )
    except Exception as e:
        elapsed = time.monotonic() - start
        return CheckResult(
            name=check.name,
            category=category_name,
            passed=False,
            exit_code=-1,
            duration=elapsed,
            error=str(e),
        )


def _collect_checks(
    category_filter: str | None,
    quick: bool,
    changed_categories: set[str] | None = None,
) -> list[tuple[Check, str]]:
    """Collect checks to run based on filters."""
    checks: list[tuple[Check, str]] = []

    for cat in CATEGORIES:
        # Category filter
        if category_filter and cat.name != category_filter:
            continue

        # Changed-file filter
        if changed_categories is not None and cat.name not in changed_categories:
            continue

        if quick:
            # Only run checks named in QUICK_CHECKS for this category
            allowed = QUICK_CHECKS.get(cat.name, [])
            if not allowed:
                continue
            for check in cat.checks:
                if check.name in allowed:
                    checks.append((check, cat.name))
        else:
            for check in cat.checks:
                checks.append((check, cat.name))

    return checks


# ── Output ─────────────────────────────────────────────────────────────────


def _format_duration(seconds: float) -> str:
    """Format seconds into human-readable duration."""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    return f"{seconds:.1f}s"


def _print_results_table(results: list[CheckResult]) -> None:
    """Print a category-grouped results table."""
    # Group by category
    by_category: dict[str, list[CheckResult]] = {}
    for r in results:
        by_category.setdefault(r.category, []).append(r)

    # Find category label for display
    cat_labels = {cat.name: cat.label for cat in CATEGORIES}

    print()
    print("━━━ Check Report ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    total_passed = 0
    total_failed = 0
    total_timeout = 0
    fixable = 0

    for cat_name in [c.name for c in CATEGORIES]:
        cat_results = by_category.get(cat_name, [])
        if not cat_results:
            continue

        label = cat_labels.get(cat_name, cat_name)
        passed = sum(1 for r in cat_results if r.passed)
        failed = len(cat_results) - passed
        timed_out = sum(1 for r in cat_results if r.timed_out)

        total_passed += passed
        total_failed += failed
        total_timeout += timed_out

        if failed == 0:
            icon = "✅"
            detail = f"{passed}/{len(cat_results)} passed"
        elif timed_out > 0:
            icon = "⏱️ "
            detail = f"{passed}/{len(cat_results)} passed ({timed_out} timed out)"
        else:
            icon = "❌"
            detail = f"{passed}/{len(cat_results)} passed ({failed} failed)"

        # Calculate total time for category
        cat_time = sum(r.duration for r in cat_results)
        time_str = _format_duration(cat_time)

        print(f"  {label:15s} {icon} {detail:30s} {time_str:>8s}")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    total = total_passed + total_failed
    total_time = sum(r.duration for r in results)

    if total_failed == 0:
        print(
            f"  ✅ Total: {total_passed}/{total} passed  ({_format_duration(total_time)})"
        )
    else:
        print(
            f"  ❌ Total: {total_passed}/{total} passed, {total_failed} failed  ({_format_duration(total_time)})"
        )

    # Count fixable checks
    for cat in CATEGORIES:
        for check in cat.checks:
            if check.fix_cmd:
                for r in results:
                    if r.name == check.name and not r.passed:
                        fixable += 1

    if fixable > 0:
        print(f"  💡 Auto-fixable: {fixable} (run with --fix)")

    print()

    # Print details for failed checks
    failed_results = [r for r in results if not r.passed]
    if failed_results:
        print("━━━ Failed Check Details ━━━━━━━━━━━━━━━━━━━━━━━")
        for r in failed_results:
            label = cat_labels.get(r.category, r.category)
            print(f"\n  ❌ {r.name} [{label}]")
            if r.timed_out:
                print(f"     Timed out after {r.duration:.0f}s")
            elif r.error:
                print(f"     Error: {r.error}")
            else:
                # Show last few lines of output (most relevant)
                output = (r.stdout + r.stderr).strip()
                if output:
                    lines = output.splitlines()
                    # Show up to last 10 lines
                    show_lines = lines[-10:]
                    for line in show_lines:
                        print(f"     {line}")
                    if len(lines) > 10:
                        print(f"     ... ({len(lines) - 10} more lines)")
        print()


def _print_json_results(results: list[CheckResult]) -> None:
    """Print results as JSON."""
    output = {
        "total": len(results),
        "passed": sum(1 for r in results if r.passed),
        "failed": sum(1 for r in results if not r.passed),
        "duration": round(sum(r.duration for r in results), 2),
        "categories": {},
        "checks": [],
    }

    # Group by category
    for r in results:
        if r.category not in output["categories"]:
            output["categories"][r.category] = {"passed": 0, "failed": 0, "duration": 0}
        cat = output["categories"][r.category]
        if r.passed:
            cat["passed"] += 1
        else:
            cat["failed"] += 1
        cat["duration"] = round(cat["duration"] + r.duration, 2)

        output["checks"].append(
            {
                "name": r.name,
                "category": r.category,
                "passed": r.passed,
                "exit_code": r.exit_code,
                "duration": round(r.duration, 2),
                "timed_out": r.timed_out,
                "error": r.error or None,
            }
        )

    print_json(output)


def _print_list() -> None:
    """Print available categories and their checks."""
    print("━━━ Available Check Categories ━━━━━━━━━━━━━━━━━")
    print()
    for cat in CATEGORIES:
        quick_names = QUICK_CHECKS.get(cat.name, [])
        quick_tag = " (has --quick subset)" if quick_names else ""
        print(f"  {cat.label:15s} ({cat.name}){quick_tag}")
        if cat.description:
            print(f"  {' ' * 15} {cat.description}")
        for check in cat.checks:
            is_quick = "⚡" if check.name in quick_names else " "
            fix_tag = " [fixable]" if check.fix_cmd else ""
            print(f"    {is_quick} {check.name}{fix_tag}")
        print()

    total = sum(len(cat.checks) for cat in CATEGORIES)
    quick_total = sum(len(v) for v in QUICK_CHECKS.values())
    print(f"  Total: {total} checks across {len(CATEGORIES)} categories")
    print(f"  Quick: {quick_total} checks (⚡ marked above)")
    print()


# ── Main ───────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="check_all.py",
        description="Run all validation checks in parallel, grouped by category.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/check_all.py                    # Run all checks\n"
            "  python scripts/check_all.py --quick            # Fast subset\n"
            "  python scripts/check_all.py --category api     # API checks only\n"
            "  python scripts/check_all.py --changed          # Only categories for changed files\n"
            "  python scripts/check_all.py --pre-commit       # Run pre-commit hooks\n"
            "  python scripts/check_all.py --fix              # Auto-fix issues\n"
            "  python scripts/check_all.py --json             # CI output\n"
            "  python scripts/check_all.py --list             # Show categories\n"
        ),
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run fast subset of checks (<30s)",
    )
    parser.add_argument(
        "--category",
        "-c",
        type=str,
        default=None,
        choices=[cat.name for cat in CATEGORIES],
        help="Run checks for a specific category only",
    )
    parser.add_argument(
        "--changed",
        action="store_true",
        help="Only run checks for categories affected by recent file changes",
    )
    parser.add_argument(
        "--pre-commit",
        action="store_true",
        help="Run pre-commit hooks (black, ruff, mypy, isort, bandit)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix issues where possible",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Machine-readable JSON output",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Show available categories and checks",
    )
    parser.add_argument(
        "--serial",
        action="store_true",
        help="Run checks serially instead of in parallel (for debugging)",
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=_default_workers,
        help=f"Number of parallel workers (default: {_default_workers})",
    )

    args = parser.parse_args()

    if args.list:
        _print_list()
        return 0

    # Handle --pre-commit mode
    if args.pre_commit:
        return _run_pre_commit(fix=args.fix)

    # Detect changed categories if --changed
    changed_cats = None
    if args.changed:
        changed_cats = _detect_changed_categories()
        if not changed_cats:
            if not args.json:
                print("✅ No changes detected — nothing to check")
            return 0

    # Collect checks to run
    checks = _collect_checks(args.category, args.quick, changed_cats)

    if not checks:
        if args.category:
            StatusLine.warn(f"No checks found for category: {args.category}")
        else:
            StatusLine.warn("No checks to run")
        return 0

    if not args.json:
        if args.changed and changed_cats:
            mode = f"changed: {', '.join(sorted(changed_cats))}"
        elif args.quick:
            mode = "quick"
        elif args.category:
            mode = f"category: {args.category}"
        else:
            mode = "all"
        fix_tag = " (fix mode)" if args.fix else ""
        print(f"🔍 Running {len(checks)} check(s) [{mode}]{fix_tag}...")

    # Run checks
    results: list[CheckResult] = []
    start_time = time.monotonic()

    if args.serial or len(checks) == 1:
        # Serial execution
        for check, cat_name in checks:
            if not args.json:
                print(f"  ▸ {check.name}...", end="", flush=True)
            result = _run_check(check, cat_name, use_fix=args.fix)
            results.append(result)
            if not args.json:
                icon = "✅" if result.passed else ("⏱️ " if result.timed_out else "❌")
                print(f" {icon} ({_format_duration(result.duration)})")
    else:
        # Parallel execution with ThreadPoolExecutor
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {}
            for check, cat_name in checks:
                future = executor.submit(_run_check, check, cat_name, args.fix)
                futures[future] = (check, cat_name)

            aggregate_timeout = min(sum(c.timeout for c, _ in checks), 900)
            try:
                for future in as_completed(futures, timeout=aggregate_timeout):
                    result = future.result()
                    results.append(result)
                    if not args.json:
                        icon = (
                            "✅"
                            if result.passed
                            else ("⏱️ " if result.timed_out else "❌")
                        )
                        print(
                            f"  {icon} {result.name} ({_format_duration(result.duration)})"
                        )
            except TimeoutError:
                if not args.json:
                    print(
                        f"  ⏱️  Aggregate timeout reached ({aggregate_timeout}s) — cancelling remaining checks"
                    )
                for future in futures:
                    future.cancel()

    # Sort results by category order
    cat_order = {cat.name: i for i, cat in enumerate(CATEGORIES)}
    results.sort(key=lambda r: (cat_order.get(r.category, 99), r.name))

    # Output
    if args.json:
        _print_json_results(results)
    else:
        _print_results_table(results)

    # Exit code
    failed = sum(1 for r in results if not r.passed)
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
