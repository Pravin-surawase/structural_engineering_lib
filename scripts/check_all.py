#!/usr/bin/env python3
"""Unified check orchestrator — runs all validation scripts in parallel.

When to use: When you want a single command to validate the entire codebase.
Called by `./run.sh check` or directly.

USAGE:
    ./scripts/python_runtime.sh scripts/check_all.py                      # All
    ./scripts/python_runtime.sh scripts/check_all.py --quick              # Fast
    ./scripts/python_runtime.sh scripts/check_all.py --category api       # One category
    ./scripts/python_runtime.sh scripts/check_all.py --changed            # Changed paths

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
from concurrent.futures import Future, as_completed
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.output import StatusLine, print_json
from _lib.utils import REPO_ROOT
from verification import (
    REQUIRED_DOMAINS,
    EvidenceIdentity,
    FingerprintContext,
    VerificationError,
    load_manifest,
    local_evidence_path,
    plan_changes,
    probe_receipt,
    write_receipt,
)

SCRIPTS_DIR = REPO_ROOT / "scripts"
VENV_PYTHON = str(SCRIPTS_DIR / "python_runtime.sh")
PRE_COMMIT_TIMEOUT_SECONDS = 900

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
    cacheable: bool = True


@dataclass
class Category:
    """A group of related checks."""

    name: str
    label: str
    checks: list[Check]
    impact_domains: tuple[str, ...]
    description: str = ""


def _python_runtime(*args: str) -> list[str]:
    """Build a portable command for the repository-selected Python runtime."""
    return ["bash", VENV_PYTHON, *args]


def _py(script: str, *args: str) -> list[str]:
    """Build a Python script command."""
    return _python_runtime(str(SCRIPTS_DIR / script), *args)


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
        impact_domains=("python", "fastapi"),
        checks=[
            Check("API validation", _py("check_api.py", "--all")),
            Check("API contracts", _py("validate_api_contracts.py")),
            Check(
                "API manifest", _py("generate_api_manifest.py", "--check"), timeout=30
            ),
            Check(
                "API classification",
                _py("generate_api_classification.py", "--check"),
                timeout=90,
            ),
        ],
    ),
    Category(
        name="docs",
        label="Docs",
        description="Links, doc versions, metadata, tasks format",
        impact_domains=("docs",),
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
            Check("Brief integrity", _py("check_next_session_brief_length.py")),
            Check(
                "Family facade docs",
                _py("generate_family_facade_docs.py", "--check"),
                timeout=30,
            ),
            Check("Control and context", _py("check_scripts_index.py")),
        ],
    ),
    Category(
        name="arch",
        label="Architecture",
        description="Layer boundaries, circular imports, import validation",
        impact_domains=("python", "fastapi"),
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
        impact_domains=("control_plane", "repository"),
        checks=[
            Check("Governance rules", _py("check_governance.py", "--full")),
            Check("Repo hygiene", _py("check_repo_hygiene.py")),
            Check("Token efficiency", _py("check_token_efficiency.py")),
            Check("Python version", _py("check_python_version.py")),
            Check("Schema snapshots", _py("validate_schema_snapshots.py"), timeout=90),
        ],
    ),
    Category(
        name="fastapi",
        label="FastAPI",
        description="FastAPI issues, Docker config, OpenAPI snapshot",
        impact_domains=("fastapi",),
        checks=[
            Check("FastAPI issues", _py("check_fastapi_issues.py")),
            Check("Docker config", _py("check_docker_config.py")),
            Check("OpenAPI snapshot", _py("check_openapi_snapshot.py")),
        ],
    ),
    Category(
        name="git",
        label="Git",
        description="Read-only Git state, active operations, version consistency",
        impact_domains=REQUIRED_DOMAINS,
        checks=[
            Check(
                "Git state",
                _py("git_state.py", "--guard", "validation"),
                cacheable=False,
            ),
            Check(
                "Unfinished operation",
                _py("git_state.py", "--guard", "operation"),
                cacheable=False,
            ),
            Check(
                "Version consistency",
                _sh("check_version_consistency.sh"),
                cacheable=False,
            ),
            Check(
                "Codex-native Git workflow",
                _py("check_codex_git_workflow.py"),
                cacheable=False,
            ),
        ],
    ),
    Category(
        name="stale",
        label="Stale Refs",
        description="Stale script references, instruction drift, bootstrap freshness",
        impact_domains=("control_plane", "docs", "repository"),
        checks=[
            Check("Script references", _py("validate_script_refs.py")),
            Check("CLI smoke", _py("test_cli_smoke.py")),
            Check("Instruction drift", _py("check_instruction_drift.py")),
            Check("Bootstrap freshness", _py("check_bootstrap_freshness.py")),
        ],
    ),
    Category(
        name="code",
        label="Code Quality",
        description="Type annotations",
        impact_domains=("python", "fastapi"),
        checks=[
            Check("Type annotations", _py("check_type_annotations.py"), timeout=90),
        ],
    ),
]

# Quick checks — a curated fast subset
QUICK_CHECKS: dict[str, list[str]] = {
    "docs": ["Broken links", "Doc versions", "Brief integrity"],
    "arch": ["Import validation"],
    "governance": ["Repo hygiene", "Token efficiency"],
    "git": ["Git state", "Unfinished operation"],
    "stale": ["Script references", "CLI smoke"],
}


def _detect_changed_domains() -> tuple[set[str], bool, tuple[str, ...]]:
    """Use the canonical impact planner; invalid control state selects all."""
    try:
        manifest = load_manifest(require_coverage=False)
        plan = plan_changes(manifest)
    except VerificationError as exc:
        return set(REQUIRED_DOMAINS), True, (str(exc),)
    reasons = (*plan.unknown_paths, *plan.failure_reasons)
    return set(plan.domains), plan.fail_closed, reasons


def _run_pre_commit(*, candidate_integrity: bool = False) -> int:
    """Run ordinary commit guards or the hosted-equivalent candidate hooks."""
    cmd = _python_runtime("-m", "pre_commit", "run")
    if candidate_integrity:
        cmd.extend(("--hook-stage", "manual"))
    cmd.append("--all-files")

    if candidate_integrity:
        print("🧹 Preparing candidate file integrity (may normalize files)...")
    else:
        print("🔍 Running ordinary commit-safety hooks...")
    try:
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            timeout=PRE_COMMIT_TIMEOUT_SECONDS,
        )
        return result.returncode
    except FileNotFoundError:
        print("  ❌ pre-commit not installed. Run: pip install pre-commit")
        return 1
    except subprocess.TimeoutExpired:
        print("  ⏱️  pre-commit timed out after " f"{PRE_COMMIT_TIMEOUT_SECONDS}s")
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
    reused: bool = False
    fingerprint: str = ""


def _append_missing_results(
    results: list[CheckResult],
    futures: dict[Future[CheckResult], tuple[Check, str]],
) -> None:
    """Turn an aggregate-runner omission into an explicit failed result."""
    observed = {(result.category, result.name) for result in results}
    for future, (check, cat_name) in futures.items():
        if (cat_name, check.name) in observed:
            continue
        future.cancel()
        results.append(
            CheckResult(
                name=check.name,
                category=cat_name,
                passed=False,
                exit_code=-1,
                duration=0.0,
                timed_out=True,
                error="aggregate runner did not return a result",
            )
        )


def _run_check(
    check: Check,
    category_name: str,
    use_fix: bool = False,
    identity: EvidenceIdentity | None = None,
    receipt_path: Path | None = None,
    reuse: bool = True,
) -> CheckResult:
    """Run a single check and return the result."""
    cmd = check.fix_cmd if (use_fix and check.fix_cmd) else check.cmd
    start = time.monotonic()

    if reuse and identity is not None and receipt_path is not None:
        valid, _reason = probe_receipt(receipt_path, identity)
        if valid:
            return CheckResult(
                name=check.name,
                category=category_name,
                passed=True,
                exit_code=0,
                duration=time.monotonic() - start,
                reused=True,
                fingerprint=identity.fingerprint,
            )

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
            fingerprint=identity.fingerprint if identity is not None else "",
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
            fingerprint=identity.fingerprint if identity is not None else "",
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
            fingerprint=identity.fingerprint if identity is not None else "",
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
            fingerprint=identity.fingerprint if identity is not None else "",
        )


def _collect_checks(
    category_filter: str | None,
    quick: bool,
    changed_domains: set[str] | None = None,
) -> list[tuple[Check, str]]:
    """Collect checks to run based on filters."""
    checks: list[tuple[Check, str]] = []

    for cat in CATEGORIES:
        # Category filter
        if category_filter and cat.name != category_filter:
            continue

        # Canonical impact-domain filter
        if changed_domains is not None and not (
            set(cat.impact_domains) & changed_domains
        ):
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
    total_reused = 0
    fixable = 0

    for cat_name in [c.name for c in CATEGORIES]:
        cat_results = by_category.get(cat_name, [])
        if not cat_results:
            continue

        label = cat_labels.get(cat_name, cat_name)
        passed = sum(1 for r in cat_results if r.passed)
        failed = len(cat_results) - passed
        timed_out = sum(1 for r in cat_results if r.timed_out)
        reused = sum(1 for r in cat_results if r.reused)

        total_passed += passed
        total_failed += failed
        total_timeout += timed_out
        total_reused += reused

        if failed == 0:
            icon = "✅"
            suffix = f", {reused} reused" if reused else ""
            detail = f"{passed}/{len(cat_results)} passed{suffix}"
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
            f"  ✅ Total: {total_passed}/{total} passed, {total_reused} reused  "
            f"({_format_duration(total_time)})"
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


def _print_json_results(
    results: list[CheckResult], timings: dict[str, float] | None = None
) -> None:
    """Print results as JSON."""
    output = {
        "total": len(results),
        "passed": sum(1 for r in results if r.passed),
        "failed": sum(1 for r in results if not r.passed),
        "duration": round(sum(r.duration for r in results), 2),
        "duration_semantics": "sum_of_child_check_seconds_not_wall_time",
        "timings": timings,
        "reused": sum(1 for r in results if r.reused),
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
                "reused": r.reused,
                "fingerprint": r.fingerprint or None,
                "error": r.error or None,
                "failure_output": (
                    (r.stderr or r.stdout)[-8000:] if not r.passed else None
                ),
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


def _main() -> int:
    wall_started = time.monotonic()
    parser = argparse.ArgumentParser(
        prog="check_all.py",
        description="Run all validation checks in parallel, grouped by category.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  ./run.sh check                       # Run all checks\n"
            "  ./run.sh check --quick               # Fast subset\n"
            "  ./run.sh check --category api        # API checks only\n"
            "  ./run.sh check --changed             # Changed paths only\n"
            "  ./run.sh check --pre-commit          # Run pre-commit hooks\n"
            "  ./run.sh check --candidate-integrity # Prepare hosted file integrity\n"
            "  ./run.sh check --no-reuse            # Force fresh execution\n"
            "  ./run.sh check --fix                 # Auto-fix issues\n"
            "  ./run.sh check --json                # CI output\n"
            "  ./run.sh check --list                # Show categories\n"
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
    pre_commit_mode = parser.add_mutually_exclusive_group()
    pre_commit_mode.add_argument(
        "--pre-commit",
        action="store_true",
        help="Run the three local commit-safety hooks",
    )
    pre_commit_mode.add_argument(
        "--candidate-integrity",
        action="store_true",
        help=(
            "Run the hosted manual all-files hooks before candidate freeze; "
            "may normalize files"
        ),
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
        "--no-reuse",
        action="store_true",
        help="Run checks even when an exact content/runtime PASS receipt exists",
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
        return _run_pre_commit()
    if args.candidate_integrity:
        return _run_pre_commit(candidate_integrity=True)

    # Detect canonical change domains if --changed
    changed_domains = None
    impact_fail_closed = False
    impact_reasons: tuple[str, ...] = ()
    if args.changed:
        changed_domains, impact_fail_closed, impact_reasons = _detect_changed_domains()
        if not changed_domains:
            if not args.json:
                print("✅ No changes detected — nothing to check")
            return 0

    # Collect checks to run
    checks = _collect_checks(args.category, args.quick, changed_domains)

    if not checks:
        if args.category:
            StatusLine.warn(f"No checks found for category: {args.category}")
        else:
            StatusLine.warn("No checks to run")
        return 1

    if not args.json:
        if args.changed and changed_domains:
            mode = f"changed domains: {', '.join(sorted(changed_domains))}"
        elif args.quick:
            mode = "quick"
        elif args.category:
            mode = f"category: {args.category}"
        else:
            mode = "all"
        fix_tag = " (fix mode)" if args.fix else ""
        print(f"🔍 Running {len(checks)} check(s) [{mode}]{fix_tag}...", flush=True)
        print(
            "  Preparing exact input/runtime identities (included in wall timing)...",
            flush=True,
        )
        if impact_fail_closed:
            detail = "; ".join(impact_reasons) or "unknown impact"
            print(f"  ⚠️  Impact is unknown; running every domain: {detail}")

    preparation_started = time.monotonic()
    evidence_context: FingerprintContext | None = None
    evidence_manifest: dict[str, object] | None = None
    prepared: dict[tuple[str, str], tuple[EvidenceIdentity, Path]] = {}
    if not args.fix:
        try:
            evidence_manifest = load_manifest()
            evidence_context = FingerprintContext(evidence_manifest)
            category_domains = {cat.name: cat.impact_domains for cat in CATEGORIES}
            for check, cat_name in checks:
                if not check.cacheable:
                    continue
                identity = evidence_context.identity(
                    profile=f"local-check:{cat_name}:{check.name}",
                    domains=category_domains[cat_name],
                    command=check.cmd,
                )
                receipt_path = local_evidence_path(REPO_ROOT, identity.fingerprint)
                prepared[(cat_name, check.name)] = (identity, receipt_path)
        except (OSError, VerificationError):
            evidence_context = None
            evidence_manifest = None
            prepared = {}

    preparation_seconds = time.monotonic() - preparation_started
    checks_started = time.monotonic()
    # Run checks
    results: list[CheckResult] = []

    if args.serial or len(checks) == 1:
        # Serial execution
        for check, cat_name in checks:
            if not args.json:
                print(f"  ▸ {check.name}...", end="", flush=True)
            identity, receipt_path = prepared.get((cat_name, check.name), (None, None))
            result = _run_check(
                check,
                cat_name,
                use_fix=args.fix,
                identity=identity,
                receipt_path=receipt_path,
                reuse=not args.no_reuse,
            )
            results.append(result)
            if not args.json:
                icon = (
                    "♻️ "
                    if result.reused
                    else (
                        "✅" if result.passed else ("⏱️ " if result.timed_out else "❌")
                    )
                )
                print(f" {icon} ({_format_duration(result.duration)})")
    else:
        # Parallel execution with ThreadPoolExecutor
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {}
            for check, cat_name in checks:
                identity, receipt_path = prepared.get(
                    (cat_name, check.name), (None, None)
                )
                future = executor.submit(
                    _run_check,
                    check,
                    cat_name,
                    args.fix,
                    identity,
                    receipt_path,
                    not args.no_reuse,
                )
                futures[future] = (check, cat_name)

            aggregate_timeout = min(sum(c.timeout for c, _ in checks), 900)
            try:
                for future in as_completed(futures, timeout=aggregate_timeout):
                    result = future.result()
                    results.append(result)
                    if not args.json:
                        icon = (
                            "♻️ "
                            if result.reused
                            else (
                                "✅"
                                if result.passed
                                else ("⏱️ " if result.timed_out else "❌")
                            )
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
            _append_missing_results(results, futures)

    # Sort results by category order
    cat_order = {cat.name: i for i, cat in enumerate(CATEGORIES)}
    results.sort(key=lambda r: (cat_order.get(r.category, 99), r.name))

    checks_seconds = time.monotonic() - checks_started
    postflight_started = time.monotonic()
    # Record only exact PASS identities that remained unchanged through the run.
    # Reused checks cannot publish a new receipt; avoid a redundant context.
    recordable = [
        r
        for r in results
        if r.passed and not r.reused and (r.category, r.name) in prepared
    ]
    if evidence_manifest is not None and recordable:
        try:
            post_context = FingerprintContext(evidence_manifest)
            categories = {cat.name: cat.impact_domains for cat in CATEGORIES}
            checks_by_key = {(cat, check.name): check for check, cat in checks}
            for result in recordable:
                key = (result.category, result.name)
                if not result.passed or result.reused or key not in prepared:
                    continue
                check = checks_by_key[key]
                before, receipt_path = prepared[key]
                after = post_context.identity(
                    profile=before.profile,
                    domains=categories[result.category],
                    command=check.cmd,
                )
                if after.fingerprint == before.fingerprint:
                    write_receipt(receipt_path, after)
        except (OSError, VerificationError):
            pass

    # These are non-overlapping wall intervals. Child durations may overlap.
    timings = {
        "planning_seconds": round(preparation_started - wall_started, 4),
        "preparation_seconds": round(preparation_seconds, 4),
        "checks_wall_seconds": round(checks_seconds, 4),
        "postflight_seconds": round(time.monotonic() - postflight_started, 4),
        "wall_seconds": round(time.monotonic() - wall_started, 4),
    }
    # Output
    if args.json:
        _print_json_results(results, timings)
    else:
        _print_results_table(results)
        print(
            "  Wall timing: "
            + ", ".join(f"{key}={value:.3f}s" for key, value in timings.items())
        )
        print(
            "  Child duration totals overlap in parallel mode; output/usage-recording tail is excluded."
        )

    # Exit code
    failed = sum(1 for r in results if not r.passed)
    return 1 if failed > 0 else 0


def _timing_label(argv: list[str]) -> str:
    if "--candidate-integrity" in argv:
        return "check candidate integrity"
    if "--pre-commit" in argv:
        return "check pre-commit"
    if "--quick" in argv:
        return "check quick"
    if "--changed" in argv:
        return "check changed"
    if "--category" in argv or "-c" in argv:
        return "check category"
    return "check full"


def _record_task_timing(label: str, duration_sec: float, result_code: int) -> None:
    """Best-effort external telemetry; never changes a validation verdict."""
    try:
        subprocess.run(
            _python_runtime(
                str(SCRIPTS_DIR / "session.py"),
                "usage",
                "--event",
                label,
                "--duration-sec",
                f"{duration_sec:.3f}",
                "--result-code",
                str(result_code),
            ),
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        pass


def main() -> int:
    started = time.monotonic()
    result_code = 1
    try:
        result_code = _main()
        return result_code
    finally:
        _record_task_timing(
            _timing_label(sys.argv[1:]), time.monotonic() - started, result_code
        )


if __name__ == "__main__":
    sys.exit(main())
