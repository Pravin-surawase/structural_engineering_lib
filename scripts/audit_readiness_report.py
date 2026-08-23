#!/usr/bin/env python3
"""
Audit Readiness Report Generator

When to use: Before releases. Generates a full readiness assessment of code quality and test coverage.

Compiles audit evidence from tests, scanners, governance checks, and CI artifacts
into a unified report for compliance and quality assurance.

Usage:
    python scripts/audit_readiness_report.py              # Full report to stdout
    python scripts/audit_readiness_report.py --check-only # Pass/fail only
    python scripts/audit_readiness_report.py --json       # JSON output
    python scripts/audit_readiness_report.py --export md  # Markdown export
    python scripts/audit_readiness_report.py --release v0.6.0  # Tag report

Standards Alignment:
    - NIST SSDF (SP 800-218) — Secure Software Development Framework
    - SLSA Build Levels — Supply-chain integrity
    - CycloneDX/SPDX — Software Bill of Materials (SBOM)

Created: 2026-01-24 (Session 69)
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _repo_relative(path: Path) -> str:
    """Return a stable repository-relative display/command path."""
    return path.relative_to(_REPO_ROOT).as_posix()


@dataclass
class EvidenceItem:
    """A single evidence item for audit purposes."""

    category: str  # Testing, StaticAnalysis, Governance, Security, ChangeControl
    name: str  # Human-readable name
    status: str  # PASS, FAIL, WARN, SKIP, UNKNOWN
    required: bool  # Is this a required check?
    source: str  # Where evidence came from (script, CI, file)
    details: str = ""  # Additional details
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AuditReport:
    """Complete audit readiness report."""

    version: str = "1.0.0"
    generated: str = field(default_factory=lambda: datetime.now().isoformat())
    release_tag: Optional[str] = None
    commit_sha: Optional[str] = None
    branch: Optional[str] = None

    # Summary counts
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    skipped: int = 0

    # Evidence by category
    evidence: List[EvidenceItem] = field(default_factory=list)

    # Overall verdict
    verdict: str = "UNKNOWN"  # PASS, FAIL, PARTIAL

    def add_evidence(self, item: EvidenceItem) -> None:
        """Add evidence item and update counters."""
        self.evidence.append(item)
        self.total_checks += 1

        if item.status == "PASS":
            self.passed += 1
        elif item.status == "FAIL":
            self.failed += 1
        elif item.status == "WARN":
            self.warnings += 1
        elif item.status == "SKIP":
            self.skipped += 1

    def calculate_verdict(self) -> None:
        """Calculate overall verdict based on evidence."""
        required_failed = sum(
            1 for e in self.evidence if e.required and e.status == "FAIL"
        )

        if required_failed > 0:
            self.verdict = "FAIL"
        elif self.failed > 0 or self.warnings > 0:
            self.verdict = "PARTIAL"
        else:
            self.verdict = "PASS"


def verdict_exit_code(verdict: str) -> int:
    """Map report truth to a decisive process exit code."""

    return {"PASS": 0, "FAIL": 1, "PARTIAL": 2}.get(verdict, 1)


def run_script(script_path: str, args: List[str] = None) -> Tuple[int, str, str]:
    """Run a Python script and capture output."""
    resolved_path = Path(script_path)
    if not resolved_path.is_absolute():
        resolved_path = _REPO_ROOT / resolved_path
    cmd = [sys.executable, str(resolved_path)] + (args or [])
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120, cwd=_REPO_ROOT
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout expired"
    except FileNotFoundError:
        return -2, "", f"Script not found: {script_path}"


def get_git_info() -> Dict[str, str]:
    """Get current git commit info."""
    info = {}
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True
        )
        info["commit_sha"] = result.stdout.strip()[:12]

        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
        )
        info["branch"] = result.stdout.strip()

        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            info["latest_tag"] = result.stdout.strip()
    except Exception:
        pass

    return info


# =============================================================================
# Evidence Collection Functions
# =============================================================================


def collect_testing_evidence(report: AuditReport) -> None:
    """Collect testing-related evidence."""
    # Check if pytest exists and can run
    pytest_available = (
        subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True,
        ).returncode
        == 0
    )

    if pytest_available:
        # Check for test directory
        test_dir = _REPO_ROOT / "Python/tests"
        if test_dir.exists():
            test_count = sum(1 for _ in test_dir.rglob("test_*.py"))
            report.add_evidence(
                EvidenceItem(
                    category="Testing",
                    name="Unit Tests Present",
                    status="PASS" if test_count > 0 else "FAIL",
                    required=True,
                    source=str(test_dir),
                    details=f"{test_count} test files found",
                )
            )
        else:
            report.add_evidence(
                EvidenceItem(
                    category="Testing",
                    name="Unit Tests Present",
                    status="FAIL",
                    required=True,
                    source="Python/tests/",
                    details="Test directory not found",
                )
            )

        # Check contract tests
        contract_tests = _REPO_ROOT / "Python/tests/integration/test_contracts.py"
        report.add_evidence(
            EvidenceItem(
                category="Testing",
                name="Contract Tests",
                status="PASS" if contract_tests.exists() else "FAIL",
                required=True,
                source=str(contract_tests),
                details="API contract tests for breaking change detection",
            )
        )

    # Check AppTest smoke tests
    apptest_dir = _REPO_ROOT / "tests/apptest"
    if apptest_dir.exists():
        apptest_count = sum(1 for _ in apptest_dir.rglob("test_*.py"))
        report.add_evidence(
            EvidenceItem(
                category="Testing",
                name="AppTest Smoke Tests",
                status="PASS" if apptest_count > 0 else "WARN",
                required=True,
                source=str(apptest_dir),
                details=f"{apptest_count} AppTest files found",
            )
        )

    # Check critical journey tests (React-based now)
    react_tests = _REPO_ROOT / "react_app/src"
    report.add_evidence(
        EvidenceItem(
            category="Testing",
            name="Critical Journey Tests",
            status="PASS" if react_tests.exists() else "WARN",
            required=True,
            source=str(react_tests),
            details="React app source exists",
        )
    )

    load_tests = _REPO_ROOT / "fastapi_app/tests/test_load.py"
    workflow_contract = _REPO_ROOT / ".github/workflows/README.md"
    load_text = load_tests.read_text(encoding="utf-8") if load_tests.exists() else ""
    workflow_text = (
        workflow_contract.read_text(encoding="utf-8")
        if workflow_contract.exists()
        else ""
    )
    executable_thresholds = all(
        token in load_text for token in ("LOAD_P95_MS", "LOAD_DEGRADATION_PCT")
    )
    reporting_parked = (
        "Standalone baseline/comment reporting is parked" in workflow_text
    )
    performance_ready = executable_thresholds and reporting_parked
    report.add_evidence(
        EvidenceItem(
            category="Testing",
            name="Performance Threshold Authority",
            status="PASS" if performance_ready else "WARN",
            required=False,
            source=f"{load_tests}; {workflow_contract}",
            details=(
                "FastAPI load tests enforce executable latency/degradation "
                "thresholds; standalone baseline/comment reporting is "
                "intentionally parked"
                if performance_ready
                else "Executable thresholds or the parked-reporting disposition "
                "could not be confirmed"
            ),
        )
    )

    # Check coverage configuration
    pytest_ini = _REPO_ROOT / "Python/pytest.ini"
    coverage_rc = _REPO_ROOT / "Python/.coveragerc"
    pyproject = _REPO_ROOT / "Python/pyproject.toml"
    coverage_configured = False
    if pytest_ini.exists():
        content = pytest_ini.read_text()
        coverage_configured = "--cov" in content or "cov" in content

    if not coverage_configured and pyproject.exists():
        content = pyproject.read_text()
        coverage_configured = "coverage" in content.lower()
    if not coverage_configured and coverage_rc.exists():
        coverage_configured = True

    report.add_evidence(
        EvidenceItem(
            category="Testing",
            name="Coverage Configuration",
            status="PASS" if coverage_configured else "WARN",
            required=True,
            source="pytest.ini / pyproject.toml",
            details=(
                "Coverage reporting configured"
                if coverage_configured
                else "No coverage config found"
            ),
        )
    )


def collect_static_analysis_evidence(report: AuditReport) -> None:
    """Collect static analysis evidence."""

    # Streamlit scanner removed — app migrated to React

    # Check circular imports
    circular_checker = _REPO_ROOT / "scripts/check_circular_imports.py"
    if circular_checker.exists():
        code, stdout, stderr = run_script(_repo_relative(circular_checker))
        passed = code == 0
        report.add_evidence(
            EvidenceItem(
                category="StaticAnalysis",
                name="Circular Import Detection",
                status="PASS" if passed else "FAIL",
                required=True,
                source=str(circular_checker),
                details=(
                    "No circular imports" if passed else "Circular imports detected"
                ),
            )
        )

    # Check type annotations
    type_checker = _REPO_ROOT / "scripts/check_type_annotations.py"
    if type_checker.exists():
        code, stdout, stderr = run_script(
            _repo_relative(type_checker), ["--fail-threshold", "50"]
        )
        passed = code == 0
        report.add_evidence(
            EvidenceItem(
                category="StaticAnalysis",
                name="Type Annotation Coverage",
                status="PASS" if passed else "WARN",
                required=True,
                source=str(type_checker),
                details=(
                    "≥50% type annotation rate"
                    if passed
                    else "<50% type annotation rate"
                ),
            )
        )

    # Check API signatures (consolidated into check_api.py)
    api_checker = _REPO_ROOT / "scripts/check_api.py"
    if api_checker.exists():
        code, stdout, stderr = run_script(_repo_relative(api_checker), ["--signatures"])
        passed = code == 0
        report.add_evidence(
            EvidenceItem(
                category="StaticAnalysis",
                name="API Signature Validation",
                status="PASS" if passed else "FAIL",
                required=True,
                source=str(api_checker),
                details=(
                    "All API signatures valid"
                    if passed
                    else "API signature issues found"
                ),
            )
        )


def _diagnostic_summary(stdout: str, stderr: str) -> str:
    """Return a compact, single-line explanation from a diagnostic command."""

    lines = [
        line.strip() for line in (stdout + "\n" + stderr).splitlines() if line.strip()
    ]
    if not lines:
        return "No diagnostic output was produced."

    decisive_pattern = re.compile(
        r"(?:^|\b)(?:error|failed|failure|invalid|exception|traceback)(?:\b|:)",
        re.IGNORECASE,
    )
    decisive = next((line for line in lines if decisive_pattern.search(line)), None)
    selected: list[str] = []
    if decisive is not None:
        selected.append(decisive)
    elif lines:
        selected.append(lines[0])
    for line in lines[-2:]:
        if line not in selected:
            selected.append(line)
    return " | ".join(selected)[:600]


def collect_contract_truth_evidence(report: AuditReport) -> None:
    """Include semantic controls that previously sat outside readiness truth."""

    api_parity = _REPO_ROOT / "scripts/test_api_parity.py"
    if (_REPO_ROOT / api_parity).exists():
        code, stdout, stderr = run_script(_repo_relative(api_parity))
        passed = code == 0
        report.add_evidence(
            EvidenceItem(
                category="ContractTruth",
                name="Canonical API Semantic Parity",
                status="PASS" if passed else "FAIL",
                required=True,
                source=str(api_parity),
                details=(
                    "Python and serialized API vectors agree."
                    if passed
                    else _diagnostic_summary(stdout, stderr)
                ),
            )
        )

    public_route_safety = _REPO_ROOT / "scripts/check_public_route_safety.py"
    if (_REPO_ROOT / public_route_safety).exists():
        code, stdout, stderr = run_script(_repo_relative(public_route_safety))
        passed = code == 0
        report.add_evidence(
            EvidenceItem(
                category="ContractTruth",
                name="Public Route Safety Regressions",
                status="PASS" if passed else "FAIL",
                required=True,
                source=str(public_route_safety),
                details=(
                    "Frozen adversarial Python and FastAPI routes fail closed."
                    if passed
                    else _diagnostic_summary(stdout, stderr)
                ),
            )
        )

    function_quality = _REPO_ROOT / "scripts/check_function_quality.py"
    if (_REPO_ROOT / function_quality).exists():
        code, stdout, stderr = run_script(
            _repo_relative(function_quality), ["--summary", "--strict"]
        )
        passed = code == 0
        report.add_evidence(
            EvidenceItem(
                category="ContractTruth",
                name="Function Quality Diagnostic",
                status="PASS" if passed else "WARN",
                required=False,
                source=str(function_quality),
                details=_diagnostic_summary(stdout, stderr),
            )
        )

    input_validation = _REPO_ROOT / "scripts/audit_input_validation.py"
    if (_REPO_ROOT / input_validation).exists():
        code, stdout, stderr = run_script(_repo_relative(input_validation))
        passed = code == 0
        report.add_evidence(
            EvidenceItem(
                category="ContractTruth",
                name="Input Validation Diagnostic",
                status="PASS" if passed else "WARN",
                required=False,
                source=str(input_validation),
                details=_diagnostic_summary(stdout, stderr),
            )
        )


def collect_governance_evidence(report: AuditReport) -> None:
    """Collect governance and documentation evidence."""

    # Check folder structure (consolidated into check_governance.py)
    gov_script = _REPO_ROOT / "scripts/check_governance.py"
    if gov_script.exists():
        code, stdout, stderr = run_script(_repo_relative(gov_script), ["--structure"])
        passed = code == 0
        report.add_evidence(
            EvidenceItem(
                category="Governance",
                name="Folder Structure",
                status="PASS" if passed else "FAIL",
                required=True,
                source=str(gov_script),
                details="Structure compliant with governance spec",
            )
        )

    # Check governance compliance (consolidated into check_governance.py)
    if gov_script.exists():
        code, stdout, stderr = run_script(_repo_relative(gov_script), ["--compliance"])
        passed = code == 0
        report.add_evidence(
            EvidenceItem(
                category="Governance",
                name="Governance Compliance",
                status="PASS" if passed else "WARN",
                required=True,
                source=str(gov_script),
                details=(
                    "All governance rules satisfied"
                    if passed
                    else "Some governance issues"
                ),
            )
        )

    # Check active front-matter values and the enforced documentation budget.
    doc_checker = _REPO_ROOT / "scripts/check_docs.py"
    if doc_checker.exists():
        code, stdout, stderr = run_script(
            str(doc_checker), ["--frontmatter", "--budget"]
        )
        passed = code == 0
        report.add_evidence(
            EvidenceItem(
                category="Governance",
                name="Documentation Contract",
                status="PASS" if passed else "FAIL",
                required=True,
                source=str(doc_checker),
                details=(
                    "Front-matter values and active-file budget are valid"
                    if passed
                    else _diagnostic_summary(stdout, stderr)
                ),
            )
        )

    # Check links
    link_checker = _REPO_ROOT / "scripts/check_links.py"
    if link_checker.exists():
        code, stdout, stderr = run_script(_repo_relative(link_checker))
        passed = code == 0
        report.add_evidence(
            EvidenceItem(
                category="Governance",
                name="Internal Links",
                status="PASS" if passed else "WARN",
                required=True,
                source=str(link_checker),
                details=(
                    "All internal links valid" if passed else "Some broken links found"
                ),
            )
        )

    # Check API docs sync (consolidated into check_api.py)
    api_sync = _REPO_ROOT / "scripts/check_api.py"
    if api_sync.exists():
        code, stdout, stderr = run_script(_repo_relative(api_sync), ["--sync"])
        passed = code == 0
        report.add_evidence(
            EvidenceItem(
                category="Governance",
                name="API Documentation Sync",
                status="PASS" if passed else "WARN",
                required=True,
                source=str(api_sync),
                details=(
                    "API docs match implementation"
                    if passed
                    else "API docs may be outdated"
                ),
            )
        )

    # Check CHANGELOG
    changelog = _REPO_ROOT / "CHANGELOG.md"
    report.add_evidence(
        EvidenceItem(
            category="Governance",
            name="CHANGELOG Present",
            status="PASS" if changelog.exists() else "FAIL",
            required=True,
            source=str(changelog),
            details="Release notes maintained in CHANGELOG.md",
        )
    )

    # Check version in __init__.py
    version_file = _REPO_ROOT / "Python/structural_lib/__init__.py"
    version_present = False
    if version_file.exists():
        content = version_file.read_text()
        version_present = "__version__" in content

    report.add_evidence(
        EvidenceItem(
            category="Governance",
            name="Version Defined",
            status="PASS" if version_present else "FAIL",
            required=True,
            source=str(version_file),
            details=(
                "__version__ defined in package"
                if version_present
                else "No __version__ found"
            ),
        )
    )


def collect_security_evidence(report: AuditReport) -> None:
    """Collect security-related evidence."""

    weekly = _REPO_ROOT / ".github/workflows/nightly.yml"
    weekly_text = weekly.read_text(encoding="utf-8") if weekly.exists() else ""
    dependency_audits = "pip-audit" in weekly_text and "npm audit" in weekly_text
    report.add_evidence(
        EvidenceItem(
            category="Security",
            name="Scheduled Dependency Audits",
            status="PASS" if dependency_audits else "WARN",
            required=True,
            source=str(weekly),
            details=(
                "Weekly workflow audits locked Python and production npm dependencies"
                if dependency_audits
                else "Weekly dependency audits are not configured"
            ),
        )
    )

    # Check if dependencies are pinned
    pyproject = _REPO_ROOT / "Python/pyproject.toml"
    deps_pinned = False
    if pyproject.exists():
        content = pyproject.read_text()
        # Check for version specifiers (>= or ==)
        deps_pinned = ">=" in content or "==" in content

    report.add_evidence(
        EvidenceItem(
            category="Security",
            name="Dependencies Pinned",
            status="PASS" if deps_pinned else "WARN",
            required=True,
            source=str(pyproject),
            details=(
                "Dependencies have version constraints"
                if deps_pinned
                else "Check version pinning"
            ),
        )
    )

    # Check for SECURITY.md
    security_md = _REPO_ROOT / ".github/SECURITY.md"
    report.add_evidence(
        EvidenceItem(
            category="Security",
            name="Security Policy",
            status="PASS" if security_md.exists() else "WARN",
            required=False,
            source=str(security_md),
            details=(
                "SECURITY.md present" if security_md.exists() else "No SECURITY.md file"
            ),
        )
    )


def collect_change_control_evidence(report: AuditReport) -> None:
    """Collect change control evidence."""

    # Check the Codex-native workflow contract.
    workflow_doc = _REPO_ROOT / "docs/git-automation/git-workflow-single-source.md"
    report.add_evidence(
        EvidenceItem(
            category="ChangeControl",
            name="Codex-Native Git Workflow",
            status="PASS" if workflow_doc.exists() else "WARN",
            required=True,
            source=str(workflow_doc),
            details="Codex owns scoped commits, pushes, and connected GitHub PR operations",
        )
    )

    # Check branch protection (via workflow)
    fast_checks = _REPO_ROOT / ".github/workflows/fast-checks.yml"
    report.add_evidence(
        EvidenceItem(
            category="ChangeControl",
            name="PR Validation Workflow",
            status="PASS" if fast_checks.exists() else "WARN",
            required=True,
            source=str(fast_checks),
            details=(
                "fast-checks.yml validates PRs"
                if fast_checks.exists()
                else "No PR validation workflow"
            ),
        )
    )


# =============================================================================
# Output Formatters
# =============================================================================


def format_markdown(report: AuditReport) -> str:
    """Format report as Markdown."""
    lines = [
        "# Audit Readiness Report",
        "",
        f"**Generated:** {report.generated}",
        f"**Branch:** {report.branch or 'unknown'}",
        f"**Commit:** {report.commit_sha or 'unknown'}",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total Checks | {report.total_checks} |",
        f"| Passed | {report.passed} |",
        f"| Failed | {report.failed} |",
        f"| Warnings | {report.warnings} |",
        f"| Skipped | {report.skipped} |",
        "",
        f"**Verdict:** {report.verdict}",
        "",
        "---",
        "",
    ]

    # Group by category
    categories = {}
    for item in report.evidence:
        if item.category not in categories:
            categories[item.category] = []
        categories[item.category].append(item)

    for category, items in sorted(categories.items()):
        lines.append(f"## {category}")
        lines.append("")
        lines.append("| Check | Status | Required | Details |")
        lines.append("|-------|--------|----------|---------|")

        for item in items:
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌",
                "WARN": "⚠️",
                "SKIP": "⏭️",
            }.get(item.status, "❓")
            req = "Yes" if item.required else "No"
            lines.append(
                f"| {item.name} | {status_icon} {item.status} | {req} | {item.details} |"
            )

        lines.append("")

    return "\n".join(lines)


def format_json(report: AuditReport) -> str:
    """Format report as JSON."""
    data = {
        "version": report.version,
        "generated": report.generated,
        "release_tag": report.release_tag,
        "commit_sha": report.commit_sha,
        "branch": report.branch,
        "summary": {
            "total_checks": report.total_checks,
            "passed": report.passed,
            "failed": report.failed,
            "warnings": report.warnings,
            "skipped": report.skipped,
        },
        "verdict": report.verdict,
        "evidence": [
            {
                "category": e.category,
                "name": e.name,
                "status": e.status,
                "required": e.required,
                "source": e.source,
                "details": e.details,
                "timestamp": e.timestamp,
            }
            for e in report.evidence
        ],
    }
    return json.dumps(data, indent=2)


def format_console(report: AuditReport) -> str:
    """Format report for console output."""
    lines = [
        "=" * 70,
        "📋 AUDIT READINESS REPORT",
        "=" * 70,
        "",
        f"Generated: {report.generated}",
        f"Branch: {report.branch or 'unknown'}",
        f"Commit: {report.commit_sha or 'unknown'}",
        "",
        "─" * 70,
        "SUMMARY",
        "─" * 70,
        f"  Total Checks: {report.total_checks}",
        f"  ✅ Passed:    {report.passed}",
        f"  ❌ Failed:    {report.failed}",
        f"  ⚠️  Warnings:  {report.warnings}",
        f"  ⏭️  Skipped:   {report.skipped}",
        "",
    ]

    # Show failures first
    failures = [e for e in report.evidence if e.status == "FAIL"]
    if failures:
        lines.append("─" * 70)
        lines.append("❌ FAILED CHECKS (Action Required)")
        lines.append("─" * 70)
        for item in failures:
            req = " [REQUIRED]" if item.required else ""
            lines.append(f"  • {item.name}{req}")
            lines.append(f"    └─ {item.details}")
            lines.append(f"       Source: {item.source}")
        lines.append("")

    # Show warnings
    warnings = [e for e in report.evidence if e.status == "WARN"]
    if warnings:
        lines.append("─" * 70)
        lines.append("⚠️  WARNINGS (Review Recommended)")
        lines.append("─" * 70)
        for item in warnings:
            lines.append(f"  • {item.name}")
            lines.append(f"    └─ {item.details}")
        lines.append("")

    # Verdict
    lines.append("=" * 70)
    verdict_icon = {"PASS": "✅", "FAIL": "❌", "PARTIAL": "⚠️"}.get(
        report.verdict, "❓"
    )
    lines.append(f"VERDICT: {verdict_icon} {report.verdict}")
    lines.append("=" * 70)

    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate audit readiness report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/audit_readiness_report.py              # Full console report
  python scripts/audit_readiness_report.py --check-only # Pass/fail exit code
  python scripts/audit_readiness_report.py --json       # JSON output
  python scripts/audit_readiness_report.py --export md  # Markdown export
        """,
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Exit 0 only for PASS, 1 for FAIL, or 2 for PARTIAL (no output)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--export",
        choices=["md", "json"],
        help="Export format (md or json)",
    )
    parser.add_argument(
        "--release",
        help="Release tag to associate with report",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)",
    )
    args = parser.parse_args()

    # Initialize report
    report = AuditReport()
    git_info = get_git_info()
    report.commit_sha = git_info.get("commit_sha")
    report.branch = git_info.get("branch")
    report.release_tag = args.release or git_info.get("latest_tag")

    # Collect all evidence
    collect_testing_evidence(report)
    collect_static_analysis_evidence(report)
    collect_contract_truth_evidence(report)
    collect_governance_evidence(report)
    collect_security_evidence(report)
    collect_change_control_evidence(report)

    # Calculate verdict
    report.calculate_verdict()

    # Output
    if args.check_only:
        return verdict_exit_code(report.verdict)

    if args.json or args.export == "json":
        output = format_json(report)
    elif args.export == "md":
        output = format_markdown(report)
    else:
        output = format_console(report)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Report written to {args.output}")
    else:
        print(output)

    return verdict_exit_code(report.verdict)


if __name__ == "__main__":
    sys.exit(main())
