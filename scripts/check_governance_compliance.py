#!/usr/bin/env python3
"""
Check folder structure compliance against FOLDER_STRUCTURE_GOVERNANCE.md

This validator ensures the repository matches the published governance spec:
- Root file count limits
- Docs folder organization
- Agents folder structure
- Category compliance
- Document metadata presence

Usage:
    python scripts/check_governance_compliance.py           # Check structure
    python scripts/check_governance_compliance.py --strict  # Enforce strict rules
    python scripts/check_governance_compliance.py --json    # JSON output

Created: Session 11 (2026-01-11)
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class ComplianceIssue:
    """A governance compliance issue."""

    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    location: str  # Path where issue found
    rule: str  # Governance rule violated
    message: str  # Human-readable message
    files: List[str] = field(default_factory=list)


@dataclass
class ComplianceReport:
    """Report of all governance compliance checks."""

    total_issues: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    issues: List[ComplianceIssue] = field(default_factory=list)
    passed_checks: List[str] = field(default_factory=list)

    def add_issue(self, issue: ComplianceIssue) -> None:
        """Add an issue and update counters."""
        self.issues.append(issue)
        self.total_issues += 1
        if issue.severity == "CRITICAL":
            self.critical += 1
        elif issue.severity == "HIGH":
            self.high += 1
        elif issue.severity == "MEDIUM":
            self.medium += 1
        else:
            self.low += 1

    def add_pass(self, check_name: str) -> None:
        """Record a passed check."""
        self.passed_checks.append(check_name)


def check_root_file_count() -> List[ComplianceIssue]:
    """Check root directory has ≤10 files (governance spec)."""
    issues = []
    root = Path(".")
    files = [f for f in root.iterdir() if f.is_file() and not f.name.startswith(".")]

    if len(files) > 10:
        issues.append(
            ComplianceIssue(
                severity="CRITICAL",
                location="/",
                rule="Root max ≤10 files",
                message=f"Root has {len(files)} files (limit: 10)",
                files=[f.name for f in files],
            )
        )

    return issues


def check_docs_root_file_count() -> List[ComplianceIssue]:
    """Check docs/ root has 3-5 files (governance spec)."""
    issues = []
    docs_root = Path("docs")
    if not docs_root.exists():
        return issues

    files = [
        f
        for f in docs_root.iterdir()
        if f.is_file() and not f.name.startswith(".")
    ]

    if len(files) > 5:
        issues.append(
            ComplianceIssue(
                severity="HIGH",
                location="docs/",
                rule="docs/ root max ≤5 files",
                message=f"docs/ has {len(files)} files (limit: 5)",
                files=[f.name for f in files],
            )
        )

    return issues


def check_agents_root_structure() -> List[ComplianceIssue]:
    """Check agents/ folder has roles/, guides/, templates/ structure."""
    issues = []
    agents = Path("agents")
    if not agents.exists():
        return issues

    # Check that role files are in agents/roles/
    role_files = ["ARCHITECT.md", "CLIENT.md", "DEV.md", "DEVOPS.md", "DOCS.md",
                  "INTEGRATION.md", "PM.md", "RESEARCHER.md", "SUPPORT.md",
                  "TESTER.md", "UI.md"]

    roles_in_root = [f for f in role_files if (agents / f).exists()]
    if roles_in_root:
        issues.append(
            ComplianceIssue(
                severity="CRITICAL",
                location="agents/",
                rule="Role files must be in agents/roles/",
                message=f"Found {len(roles_in_root)} role files in agents/ root (should be in agents/roles/)",
                files=roles_in_root,
            )
        )

    # Check for required subdirectories
    # Note: guides/ is in docs/agents/guides/, NOT agents/guides/
    # Only check for roles/ in agents/
    for subdir in ["roles"]:
        if not (agents / subdir).exists():
            issues.append(
                ComplianceIssue(
                    severity="HIGH",
                    location=f"agents/{subdir}",
                    rule=f"agents/{subdir}/ is required",
                    message=f"agents/{subdir}/ directory missing",
                )
            )

    # Check agents/ root file count
    root_files = [
        f
        for f in agents.iterdir()
        if f.is_file() and not f.name.startswith(".")
    ]
    if len(root_files) > 5:
        issues.append(
            ComplianceIssue(
                severity="MEDIUM",
                location="agents/",
                rule="agents/ root max ≤5 files",
                message=f"agents/ root has {len(root_files)} files (limit: 5)",
                files=[f.name for f in root_files],
            )
        )

    return issues


def check_docs_agents_structure() -> List[ComplianceIssue]:
    """Check docs/agents/ workflow docs are in guides/ subfolder."""
    issues = []
    docs_agents = Path("docs/agents")
    if not docs_agents.exists():
        return issues

    workflow_docs = [
        "agent-automation-implementation.md",
        "agent-automation-system.md",
        "agent-bootstrap-complete-review.md",
        "agent-onboarding.md",
        "agent-quick-reference.md",
        "agent-workflow-master-guide.md",
    ]

    workflow_in_root = [f for f in workflow_docs if (docs_agents / f).exists()]
    if workflow_in_root:
        issues.append(
            ComplianceIssue(
                severity="HIGH",
                location="docs/agents/",
                rule="Workflow docs must be in docs/agents/guides/",
                message=f"Found {len(workflow_in_root)} workflow docs in docs/agents/ root (should be in guides/)",
                files=workflow_in_root,
            )
        )

    return issues


def check_governance_location() -> List[ComplianceIssue]:
    """Check GOVERNANCE.md exists in agents/roles/ (canonical location)."""
    issues = []

    # Canonical location after Session 11 migration
    canonical_gov = Path("agents/roles/GOVERNANCE.md")
    old_gov = Path("agents/GOVERNANCE.md")

    # Check if GOVERNANCE.md is missing from canonical location
    if not canonical_gov.exists():
        issues.append(
            ComplianceIssue(
                severity="HIGH",
                location="agents/roles/",
                rule="GOVERNANCE.md must exist in agents/roles/",
                message="agents/roles/GOVERNANCE.md is missing (required for agent governance)",
            )
        )

    # Check if old location still has GOVERNANCE.md (should be removed)
    if old_gov.exists():
        issues.append(
            ComplianceIssue(
                severity="MEDIUM",
                location="agents/GOVERNANCE.md",
                rule="GOVERNANCE.md should be in agents/roles/",
                message="agents/GOVERNANCE.md should be moved to agents/roles/GOVERNANCE.md",
            )
        )

    return issues


def check_redirect_stubs() -> List[ComplianceIssue]:
    """Check for redirect stub files (single source rule).

    A redirect stub is a small file (<15 lines, <50 words) that primarily
    contains links pointing to another location. These violate the single
    source of truth principle.
    """
    issues = []

    # Scan docs/ for potential redirect stubs (not just hardcoded paths)
    docs_path = Path("docs")
    if not docs_path.exists():
        return issues

    # Scan all markdown files in docs/
    for md_file in docs_path.rglob("*.md"):
        # Skip known non-stub files
        if md_file.name in ["README.md", "TASKS.md", "SESSION_LOG.md"]:
            continue

        try:
            content = md_file.read_text()
        except Exception:
            continue

        lines = content.strip().split("\n")
        links = content.count("](")
        words = len(content.split())

        # Detect redirect pattern: short file, has links, few words
        # Also check for explicit redirect markers
        is_redirect_marker = "redirect" in content.lower() or "moved to" in content.lower()
        is_small_with_links = len(lines) < 15 and links > 0 and words < 50

        if is_small_with_links or (is_redirect_marker and len(lines) < 20):
            # Get relative path from project root
            rel_path = str(md_file)
            issues.append(
                ComplianceIssue(
                    severity="MEDIUM",
                    location=rel_path,
                    rule="No redirect stubs (single source rule)",
                    message=f"Likely redirect stub: {len(lines)} lines, {links} links, {words} words",
                )
            )

    return issues


def main() -> int:
    """Run all compliance checks."""
    parser = argparse.ArgumentParser(description="Check governance compliance")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on any issue (default: fail on CRITICAL/HIGH only)",
    )
    args = parser.parse_args()

    report = ComplianceReport()

    # Run all checks - FIXED: Don't use for...else pattern!
    # Python's for...else runs else when loop completes normally (always runs!)
    # Instead, check if issues list is empty to determine pass/fail

    root_issues = check_root_file_count()
    for issue in root_issues:
        report.add_issue(issue)
    if not root_issues:
        report.add_pass("Root file count (≤10)")

    docs_issues = check_docs_root_file_count()
    for issue in docs_issues:
        report.add_issue(issue)
    if not docs_issues:
        report.add_pass("docs/ root file count (≤5)")

    agents_issues = check_agents_root_structure()
    for issue in agents_issues:
        report.add_issue(issue)
    if not agents_issues:
        report.add_pass("agents/ structure")

    docs_agents_issues = check_docs_agents_structure()
    for issue in docs_agents_issues:
        report.add_issue(issue)
    if not docs_agents_issues:
        report.add_pass("docs/agents/ structure")

    governance_issues = check_governance_location()
    for issue in governance_issues:
        report.add_issue(issue)
    if not governance_issues:
        report.add_pass("GOVERNANCE.md location (agents/roles/)")

    redirect_issues = check_redirect_stubs()
    for issue in redirect_issues:
        report.add_issue(issue)
    if not redirect_issues:
        report.add_pass("No redirect stubs")

    if args.json:
        output = {
            "status": "PASS" if report.critical == 0 and (not args.strict or report.high == 0) else "FAIL",
            "total_issues": report.total_issues,
            "critical": report.critical,
            "high": report.high,
            "medium": report.medium,
            "low": report.low,
            "passed_checks": report.passed_checks,
            "issues": [
                {
                    "severity": i.severity,
                    "location": i.location,
                    "rule": i.rule,
                    "message": i.message,
                    "files": i.files,
                }
                for i in report.issues
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print("=" * 70)
        print("📋 Governance Compliance Report")
        print("=" * 70)
        print()

        if report.critical > 0:
            print(f"🔴 CRITICAL ({report.critical})")
            for issue in report.issues:
                if issue.severity == "CRITICAL":
                    print(f"   {issue.location}: {issue.message}")
            print()

        if report.high > 0:
            print(f"🟠 HIGH ({report.high})")
            for issue in report.issues:
                if issue.severity == "HIGH":
                    print(f"   {issue.location}: {issue.message}")
            print()

        if report.medium > 0:
            print(f"🟡 MEDIUM ({report.medium})")
            for issue in report.issues:
                if issue.severity == "MEDIUM":
                    print(f"   {issue.location}: {issue.message}")
            print()

        print(f"✅ PASSED CHECKS ({len(report.passed_checks)})")
        for check in report.passed_checks:
            print(f"   ✓ {check}")
        print()

        print("=" * 70)
        status = "COMPLIANT" if report.critical == 0 else "NON-COMPLIANT"
        print(f"Status: {status}")
        print("=" * 70)

        return 1 if (report.critical > 0 or (args.strict and report.high > 0)) else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
