#!/usr/bin/env python3
"""Unified project health scanner with auto-fix capability.

Single command to assess entire project health across 5 categories:
docs, code, agents, infra, feedback. Leverages existing check scripts
and adds new validations.

Usage:
    python scripts/project_health.py                    # Full scan
    python scripts/project_health.py --fix              # Auto-fix fixable issues
    python scripts/project_health.py --score            # Health score only (0-100)
    python scripts/project_health.py --category docs    # Scan one category
    python scripts/project_health.py --quick            # Fast scan (numbers + links only)
    python scripts/project_health.py --json             # Machine-readable output

Part of the Self-Evolving System (docs/architecture/self-evolving-system.md).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT, DOCS_DIR, SCRIPTS_DIR
from _lib.output import print_json

# ─── Config ──────────────────────────────────────────────────────────────────

STALENESS_DAYS = 90  # Docs older than this are flagged
AGENT_DIR = REPO_ROOT / ".github" / "agents"
SKILLS_DIR = REPO_ROOT / ".github" / "skills"
PROMPTS_DIR = REPO_ROOT / ".github" / "prompts"
FEEDBACK_DIR = REPO_ROOT / "logs" / "feedback"
EVOLUTION_DIR = REPO_ROOT / "logs" / "evolution"
VENV_PYTHON = REPO_ROOT / ".venv" / "bin" / "python"

# Category weights for health score
WEIGHTS = {
    "docs": 0.30,
    "code": 0.25,
    "agents": 0.20,
    "infra": 0.15,
    "feedback": 0.10,
}


# ─── Data Classes ────────────────────────────────────────────────────────────


@dataclass
class Issue:
    """A single health issue."""

    category: str
    severity: str  # "error", "warning", "info"
    message: str
    file: str = ""
    fixable: bool = False
    fix_applied: bool = False


@dataclass
class CategoryResult:
    """Health result for one category."""

    name: str
    score: int = 100  # 0-100
    issues: list[Issue] = field(default_factory=list)
    checks_run: int = 0
    checks_passed: int = 0
    fixes_applied: int = 0

    @property
    def checks_failed(self) -> int:
        return self.checks_run - self.checks_passed


@dataclass
class HealthReport:
    """Complete health report."""

    timestamp: str = ""
    overall_score: int = 100
    categories: dict[str, CategoryResult] = field(default_factory=dict)
    total_issues: int = 0
    fixable_issues: int = 0
    fixes_applied: int = 0
    scan_duration_ms: int = 0


# ─── Utility ─────────────────────────────────────────────────────────────────


def _run_check_script(
    script_name: str, args: list[str] | None = None
) -> tuple[int, str]:
    """Run a check script and return (exit_code, output)."""
    cmd = [str(VENV_PYTHON), str(SCRIPTS_DIR / script_name)]
    if args:
        cmd.extend(args)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(REPO_ROOT),
        )
        return result.returncode, result.stdout + result.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return -1, str(e)


def _file_age_days(path: Path) -> int:
    """Days since file was last modified."""
    if not path.exists():
        return -1
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    return (datetime.now() - mtime).days


def _count_pattern(
    directory: Path, pattern: str, extensions: list[str] | None = None
) -> int:
    """Count files matching a glob in a directory."""
    if not directory.exists():
        return 0
    if extensions:
        total = 0
        for ext in extensions:
            total += len(list(directory.rglob(f"*{ext}")))
        return total
    return len(list(directory.rglob(pattern)))


# ─── Category Scanners ───────────────────────────────────────────────────────


def scan_docs(fix: bool = False) -> CategoryResult:
    """Scan documentation health."""
    result = CategoryResult(name="docs")

    # Check 1: Stale numbers (sync_numbers.py)
    result.checks_run += 1
    args = ["--fix"] if fix else []
    code, output = _run_check_script("sync_numbers.py", args)
    if code == 0 and "no drift" in output.lower():
        result.checks_passed += 1
    elif code == 0 and fix:
        # Fixed some drift
        drift_count = output.count("UPDATED") + output.count("Fixed")
        result.fixes_applied += drift_count
        result.checks_passed += 1
        if drift_count > 0:
            result.issues.append(
                Issue(
                    category="docs",
                    severity="info",
                    message=f"Fixed {drift_count} stale number(s) in docs",
                    fixable=True,
                    fix_applied=True,
                )
            )
    else:
        # Count drift items from output
        drift_lines = [
            l
            for l in output.splitlines()
            if "drift" in l.lower() or "stale" in l.lower()
        ]
        result.issues.append(
            Issue(
                category="docs",
                severity="warning",
                message=f"Number drift detected ({len(drift_lines)} items). Run with --fix to resolve.",
                fixable=True,
            )
        )

    # Check 2: Broken links (check_links.py)
    result.checks_run += 1
    link_args = ["--fix"] if fix else []
    code, output = _run_check_script("check_links.py", link_args)
    if code == 0:
        result.checks_passed += 1
    else:
        broken = len(
            [l for l in output.splitlines() if "broken" in l.lower() or "FAIL" in l]
        )
        result.issues.append(
            Issue(
                category="docs",
                severity="warning",
                message=f"Broken links detected ({broken} issues). Run: check_links.py --fix",
                fixable=True,
            )
        )

    # Check 3: Doc metadata (check_docs.py)
    result.checks_run += 1
    doc_args = ["--fix"] if fix else []
    code, output = _run_check_script("check_docs.py", doc_args)
    if code == 0:
        result.checks_passed += 1
    else:
        result.issues.append(
            Issue(
                category="docs",
                severity="info",
                message="Doc metadata/frontmatter issues found. Run: check_docs.py --fix",
                fixable=True,
            )
        )

    # Check 4: Stale docs (age check)
    result.checks_run += 1
    stale_docs: list[str] = []
    active_dir = DOCS_DIR / "_active"
    if active_dir.exists():
        for md in active_dir.rglob("*.md"):
            age = _file_age_days(md)
            if age > STALENESS_DAYS:
                stale_docs.append(f"{md.relative_to(REPO_ROOT)} ({age}d)")
    if stale_docs:
        result.issues.append(
            Issue(
                category="docs",
                severity="info",
                message=f"{len(stale_docs)} doc(s) in _active/ older than {STALENESS_DAYS} days",
            )
        )
    else:
        result.checks_passed += 1

    # Check 5: Bootstrap freshness
    result.checks_run += 1
    code, output = _run_check_script("check_bootstrap_freshness.py", ["--json"])
    if code == 0:
        result.checks_passed += 1
    else:
        try:
            data = json.loads(output)
            missing = data.get("missing_count", 0)
        except (json.JSONDecodeError, AttributeError):
            missing = "unknown"
        result.issues.append(
            Issue(
                category="docs",
                severity="warning",
                message=f"Bootstrap docs stale: {missing} items in code not reflected in bootstrap docs",
            )
        )

    # Calculate score
    if result.checks_run > 0:
        result.score = int((result.checks_passed / result.checks_run) * 100)

    return result


def scan_code(fix: bool = False) -> CategoryResult:
    """Scan code architecture health."""
    result = CategoryResult(name="code")

    # Check 1: Architecture boundaries
    result.checks_run += 1
    code, output = _run_check_script("check_architecture_boundaries.py")
    if code == 0:
        result.checks_passed += 1
    else:
        violations = len([l for l in output.splitlines() if "violation" in l.lower()])
        result.issues.append(
            Issue(
                category="code",
                severity="error",
                message=f"Architecture boundary violations: {violations} found",
            )
        )

    # Check 2: Circular imports
    result.checks_run += 1
    code, output = _run_check_script("check_circular_imports.py")
    if code == 0:
        result.checks_passed += 1
    else:
        result.issues.append(
            Issue(
                category="code",
                severity="error",
                message="Circular imports detected in structural_lib",
            )
        )

    # Check 3: Import validation
    result.checks_run += 1
    code, output = _run_check_script(
        "validate_imports.py", ["--scope", "structural_lib"]
    )
    if code == 0:
        result.checks_passed += 1
    else:
        result.issues.append(
            Issue(
                category="code",
                severity="error",
                message="Broken imports detected. Run: validate_imports.py --scope structural_lib",
            )
        )

    # Check 4: API contract stability
    result.checks_run += 1
    code, output = _run_check_script("check_api.py")
    if code == 0:
        result.checks_passed += 1
    else:
        result.issues.append(
            Issue(
                category="code",
                severity="warning",
                message="API contract issues. Run: check_api.py for details",
            )
        )

    if result.checks_run > 0:
        result.score = int((result.checks_passed / result.checks_run) * 100)

    return result


def scan_agents(fix: bool = False) -> CategoryResult:
    """Scan agent instruction health."""
    result = CategoryResult(name="agents")

    # Check 1: Instruction drift (.github/instructions/ vs .claude/rules/)
    result.checks_run += 1
    code, output = _run_check_script("check_instruction_drift.py", ["--json"])
    if code == 0:
        result.checks_passed += 1
    else:
        result.issues.append(
            Issue(
                category="agents",
                severity="warning",
                message="Instruction drift between .github/instructions/ and .claude/rules/",
            )
        )

    # Check 2: Agent file references validity
    result.checks_run += 1
    invalid_refs: list[str] = []
    if AGENT_DIR.exists():
        for agent_file in AGENT_DIR.glob("*.agent.md"):
            try:
                content = agent_file.read_text(encoding="utf-8")
            except OSError:
                continue
            # Check referenced files exist
            for match in re.finditer(r"`([^`]+\.(?:py|ts|tsx|sh|md))`", content):
                ref_path = match.group(1)
                # Skip if it looks like a command or pattern, not a path
                if ref_path.startswith("-") or "*" in ref_path or " " in ref_path:
                    continue
                full = REPO_ROOT / ref_path
                if not full.exists() and not ref_path.startswith("scripts/"):
                    invalid_refs.append(f"{agent_file.name}: {ref_path}")
    if invalid_refs:
        result.issues.append(
            Issue(
                category="agents",
                severity="warning",
                message=f"{len(invalid_refs)} invalid file reference(s) in agent instructions",
                fixable=fix,
            )
        )
    else:
        result.checks_passed += 1

    # Check 3: Skill files reference valid scripts
    result.checks_run += 1
    skill_issues: list[str] = []
    if SKILLS_DIR.exists():
        for skill_dir in SKILLS_DIR.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                skill_issues.append(f"{skill_dir.name}: missing SKILL.md")
                continue
            try:
                content = skill_file.read_text(encoding="utf-8")
            except OSError:
                continue
            # Check referenced scripts exist
            for match in re.finditer(r"scripts/(\S+\.py)", content):
                script = SCRIPTS_DIR / match.group(1)
                if not script.exists():
                    skill_issues.append(
                        f"{skill_dir.name}: references missing {match.group(0)}"
                    )
    if skill_issues:
        result.issues.append(
            Issue(
                category="agents",
                severity="warning",
                message=f"{len(skill_issues)} skill reference issue(s): {'; '.join(skill_issues[:3])}",
            )
        )
    else:
        result.checks_passed += 1

    # Check 4: Agent count matches docs
    result.checks_run += 1
    actual_agents = len(list(AGENT_DIR.glob("*.agent.md"))) if AGENT_DIR.exists() else 0
    # Check if AGENTS.md, CLAUDE.md mention correct count
    agents_md = REPO_ROOT / "AGENTS.md"
    count_mismatch = False
    if agents_md.exists():
        try:
            text = agents_md.read_text(encoding="utf-8")
            # Look for "11 agents" or similar
            for match in re.finditer(
                r"(\d+)\s+(?:custom\s+)?agents?", text, re.IGNORECASE
            ):
                doc_count = int(match.group(1))
                if doc_count != actual_agents:
                    count_mismatch = True
                    result.issues.append(
                        Issue(
                            category="agents",
                            severity="warning",
                            message=f"AGENTS.md says {doc_count} agents but found {actual_agents}",
                            fixable=True,
                        )
                    )
                break
        except OSError:
            pass
    if not count_mismatch:
        result.checks_passed += 1

    # Check 5: Prompt files exist and have content
    result.checks_run += 1
    empty_prompts: list[str] = []
    if PROMPTS_DIR.exists():
        for prompt_file in PROMPTS_DIR.glob("*.prompt.md"):
            try:
                content = prompt_file.read_text(encoding="utf-8")
                if len(content.strip()) < 50:
                    empty_prompts.append(prompt_file.name)
            except OSError:
                empty_prompts.append(prompt_file.name)
    if empty_prompts:
        result.issues.append(
            Issue(
                category="agents",
                severity="info",
                message=f"{len(empty_prompts)} nearly-empty prompt file(s)",
            )
        )
    else:
        result.checks_passed += 1

    if result.checks_run > 0:
        result.score = int((result.checks_passed / result.checks_run) * 100)

    return result


def scan_infra(fix: bool = False) -> CategoryResult:
    """Scan infrastructure health."""
    result = CategoryResult(name="infra")

    # Check 1: Git hooks installed
    result.checks_run += 1
    hooks_dir = REPO_ROOT / ".git" / "hooks"
    pre_commit = hooks_dir / "pre-commit"
    post_commit = hooks_dir / "post-commit"
    if pre_commit.exists() and post_commit.exists():
        result.checks_passed += 1
    else:
        missing = []
        if not pre_commit.exists():
            missing.append("pre-commit")
        if not post_commit.exists():
            missing.append("post-commit")
        result.issues.append(
            Issue(
                category="infra",
                severity="error",
                message=f"Git hooks missing: {', '.join(missing)}. Run: scripts/install_git_hooks.sh",
                fixable=True,
            )
        )

    # Check 2: Python venv active and has key deps
    result.checks_run += 1
    if VENV_PYTHON.exists():
        code, output = (
            subprocess.run(
                [str(VENV_PYTHON), "-c", "import pydantic, pandas, numpy; print('ok')"],
                capture_output=True,
                text=True,
                timeout=15,
            ).returncode,
            "",
        )
        if code == 0:
            result.checks_passed += 1
        else:
            result.issues.append(
                Issue(
                    category="infra",
                    severity="error",
                    message="Python venv missing key dependencies (pydantic/pandas/numpy)",
                )
            )
    else:
        result.issues.append(
            Issue(
                category="infra",
                severity="error",
                message="Python venv not found at .venv/",
            )
        )

    # Check 3: Scripts are syntactically valid (shell scripts)
    result.checks_run += 1
    broken_scripts: list[str] = []
    for sh_file in SCRIPTS_DIR.glob("*.sh"):
        check = subprocess.run(
            ["bash", "-n", str(sh_file)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if check.returncode != 0:
            broken_scripts.append(sh_file.name)
    if broken_scripts:
        result.issues.append(
            Issue(
                category="infra",
                severity="error",
                message=f"Shell syntax errors in: {', '.join(broken_scripts)}",
            )
        )
    else:
        result.checks_passed += 1

    # Check 4: Docker config valid
    result.checks_run += 1
    code, output = _run_check_script("check_docker_config.py")
    if code == 0:
        result.checks_passed += 1
    else:
        result.issues.append(
            Issue(
                category="infra",
                severity="info",
                message="Docker config issues detected. Run: check_docker_config.py",
            )
        )

    # Check 5: OpenAPI baseline current
    result.checks_run += 1
    baseline = REPO_ROOT / "fastapi_app" / "openapi_baseline.json"
    if baseline.exists():
        age = _file_age_days(baseline)
        if age > 30:
            result.issues.append(
                Issue(
                    category="infra",
                    severity="info",
                    message=f"OpenAPI baseline is {age} days old. Run: check_openapi_snapshot.py --update",
                    fixable=True,
                )
            )
        else:
            result.checks_passed += 1
    else:
        result.checks_passed += 1  # No baseline = no issue

    if result.checks_run > 0:
        result.score = int((result.checks_passed / result.checks_run) * 100)

    return result


def scan_feedback(fix: bool = False) -> CategoryResult:
    """Scan feedback health (pending items, recurring issues)."""
    result = CategoryResult(name="feedback")

    # Check 1: Unresolved feedback items
    result.checks_run += 1
    pending_count = 0
    if FEEDBACK_DIR.exists():
        for fb_file in FEEDBACK_DIR.glob("*.json"):
            try:
                data = json.loads(fb_file.read_text(encoding="utf-8"))
                items = data.get("items", [])
                pending_count += sum(
                    1 for item in items if item.get("status") != "resolved"
                )
            except (json.JSONDecodeError, OSError):
                continue

    if pending_count > 10:
        result.issues.append(
            Issue(
                category="feedback",
                severity="warning",
                message=f"{pending_count} unresolved feedback items. Run: ./run.sh feedback summary",
            )
        )
    elif pending_count > 0:
        result.issues.append(
            Issue(
                category="feedback",
                severity="info",
                message=f"{pending_count} pending feedback item(s)",
            )
        )
        result.checks_passed += 1
    else:
        result.checks_passed += 1

    # Check 2: Recurring issues (same message appears 3+ times)
    result.checks_run += 1
    issue_counts: dict[str, int] = {}
    if FEEDBACK_DIR.exists():
        for fb_file in FEEDBACK_DIR.glob("*.json"):
            try:
                data = json.loads(fb_file.read_text(encoding="utf-8"))
                for item in data.get("items", []):
                    msg = item.get("message", "")[:80]
                    issue_counts[msg] = issue_counts.get(msg, 0) + 1
            except (json.JSONDecodeError, OSError):
                continue
    recurring = {k: v for k, v in issue_counts.items() if v >= 3}
    if recurring:
        result.issues.append(
            Issue(
                category="feedback",
                severity="warning",
                message=f"{len(recurring)} recurring issue(s) need systemic fix",
            )
        )
    else:
        result.checks_passed += 1

    if result.checks_run > 0:
        result.score = int((result.checks_passed / result.checks_run) * 100)

    return result


# ─── Main Scanner ────────────────────────────────────────────────────────────

SCANNERS = {
    "docs": scan_docs,
    "code": scan_code,
    "agents": scan_agents,
    "infra": scan_infra,
    "feedback": scan_feedback,
}


def run_health_scan(
    categories: list[str] | None = None,
    fix: bool = False,
    quick: bool = False,
) -> HealthReport:
    """Run full or partial health scan."""
    start = time.time()
    report = HealthReport(timestamp=datetime.now().isoformat())

    if quick:
        categories = ["docs"]  # Quick = just docs (numbers + links)

    targets = categories or list(SCANNERS.keys())

    for cat_name in targets:
        scanner = SCANNERS.get(cat_name)
        if not scanner:
            continue
        try:
            cat_result = scanner(fix=fix)
        except Exception as e:
            cat_result = CategoryResult(name=cat_name, score=0)
            cat_result.issues.append(
                Issue(
                    category=cat_name,
                    severity="error",
                    message=f"Scanner failed: {e}",
                )
            )
        report.categories[cat_name] = cat_result

    # Calculate overall score
    total_weight = sum(WEIGHTS.get(c, 0.1) for c in report.categories)
    weighted_score = sum(
        report.categories[c].score * WEIGHTS.get(c, 0.1) for c in report.categories
    )
    report.overall_score = int(weighted_score / total_weight) if total_weight > 0 else 0

    # Aggregate totals
    for cat in report.categories.values():
        report.total_issues += len(cat.issues)
        report.fixable_issues += sum(1 for i in cat.issues if i.fixable)
        report.fixes_applied += cat.fixes_applied

    report.scan_duration_ms = int((time.time() - start) * 1000)
    return report


def _score_indicator(score: int) -> str:
    """Return colored indicator for a score."""
    if score >= 90:
        return f"\033[0;32m{score}/100 ●\033[0m"  # Green
    elif score >= 70:
        return f"\033[1;33m{score}/100 ◐\033[0m"  # Yellow
    else:
        return f"\033[0;31m{score}/100 ○\033[0m"  # Red


def print_report(
    report: HealthReport, json_output: bool = False, score_only: bool = False
) -> None:
    """Print health report."""
    if json_output:
        # Serialize for JSON
        data = {
            "timestamp": report.timestamp,
            "overall_score": report.overall_score,
            "categories": {},
            "total_issues": report.total_issues,
            "fixable_issues": report.fixable_issues,
            "fixes_applied": report.fixes_applied,
            "scan_duration_ms": report.scan_duration_ms,
        }
        for name, cat in report.categories.items():
            data["categories"][name] = {
                "score": cat.score,
                "checks_run": cat.checks_run,
                "checks_passed": cat.checks_passed,
                "issues": [asdict(i) for i in cat.issues],
                "fixes_applied": cat.fixes_applied,
            }
        print_json(data)
        return

    if score_only:
        print(f"Health Score: {_score_indicator(report.overall_score)}")
        return

    # Human-readable report
    print()
    print("\033[1m\033[36m━━━ Project Health Report ━━━\033[0m")
    print(f"  Overall: {_score_indicator(report.overall_score)}")
    print(
        f"  Scanned: {datetime.now().strftime('%Y-%m-%d %H:%M')} ({report.scan_duration_ms}ms)"
    )
    print()

    for name, cat in report.categories.items():
        icon = "✅" if cat.score >= 90 else ("⚠️" if cat.score >= 70 else "❌")
        print(
            f"  {icon} {name.upper():10s} {_score_indicator(cat.score)}  "
            f"({cat.checks_passed}/{cat.checks_run} checks passed)"
        )

        for issue in cat.issues:
            sev_icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(
                issue.severity, "·"
            )
            fix_tag = (
                " [FIXED]"
                if issue.fix_applied
                else (" [FIXABLE]" if issue.fixable else "")
            )
            print(f"      {sev_icon} {issue.message}{fix_tag}")

    print()
    summary_parts = [
        f"Issues: {report.total_issues}",
        f"Fixable: {report.fixable_issues}",
    ]
    if report.fixes_applied > 0:
        summary_parts.append(f"Fixed: {report.fixes_applied}")
    print(f"  Summary: {' | '.join(summary_parts)}")

    if report.fixable_issues > report.fixes_applied:
        unfixed = report.fixable_issues - report.fixes_applied
        print(
            f"\n  \033[1;33mTip:\033[0m {unfixed} issue(s) can be auto-fixed. "
            f"Run: ./run.sh health --fix"
        )
    print()


def save_report(report: HealthReport) -> None:
    """Save report to logs/evolution/ for trend tracking."""
    EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
    report_file = EVOLUTION_DIR / f"health_{datetime.now().strftime('%Y-%m-%d')}.json"
    data = {
        "timestamp": report.timestamp,
        "overall_score": report.overall_score,
        "categories": {
            name: {"score": cat.score, "issues": len(cat.issues)}
            for name, cat in report.categories.items()
        },
        "total_issues": report.total_issues,
        "fixes_applied": report.fixes_applied,
    }
    report_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


# ─── CLI ─────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Unified project health scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--fix", action="store_true", help="Auto-fix fixable issues")
    parser.add_argument("--score", action="store_true", help="Print health score only")
    parser.add_argument("--quick", action="store_true", help="Quick scan (docs only)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument(
        "--category",
        choices=list(SCANNERS.keys()),
        help="Scan specific category",
    )
    args = parser.parse_args()

    categories = [args.category] if args.category else None
    report = run_health_scan(
        categories=categories,
        fix=args.fix,
        quick=args.quick,
    )

    print_report(report, json_output=args.json, score_only=args.score)
    save_report(report)

    # Exit with error if critical issues
    has_errors = any(
        any(i.severity == "error" and not i.fix_applied for i in cat.issues)
        for cat in report.categories.values()
    )
    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()
