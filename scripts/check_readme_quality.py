#!/usr/bin/env python3
"""
Check README quality across the documentation.

This script analyzes README.md files for quality indicators:
- Minimum line count
- Required sections (tables, links, parent references)
- Freshness (updated date)
- Link density

Usage:
    python scripts/check_readme_quality.py           # Check all READMEs
    python scripts/check_readme_quality.py --strict  # Enforce strict criteria
    python scripts/check_readme_quality.py --json    # Output as JSON

Created: Session 10 (2026-01-11)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class QualityCheck:
    """Quality check result for a README file."""

    path: str
    lines: int
    has_title: bool = False
    has_table: bool = False
    has_parent_link: bool = False
    has_updated_date: bool = False
    has_related_docs: bool = False
    link_count: int = 0
    issues: List[str] = field(default_factory=list)
    score: int = 0  # 0-100

    def calculate_score(self) -> int:
        """Calculate quality score (0-100)."""
        score = 0

        # Line count (max 30 points)
        if self.lines >= 50:
            score += 30
        elif self.lines >= 30:
            score += 20
        elif self.lines >= 15:
            score += 10

        # Structure (max 40 points)
        if self.has_title:
            score += 10
        if self.has_table:
            score += 15
        if self.has_parent_link:
            score += 10
        if self.has_updated_date:
            score += 5

        # Links (max 20 points)
        if self.link_count >= 5:
            score += 20
        elif self.link_count >= 3:
            score += 15
        elif self.link_count >= 1:
            score += 10

        # Related docs section (10 points)
        if self.has_related_docs:
            score += 10

        self.score = min(100, score)
        return self.score


def analyze_readme(path: Path, base_path: Path) -> QualityCheck:
    """Analyze a README file for quality indicators."""
    content = path.read_text(encoding="utf-8")
    lines = content.split("\n")

    try:
        rel_path = str(path.relative_to(base_path))
    except ValueError:
        rel_path = str(path)

    check = QualityCheck(
        path=rel_path,
        lines=len(lines),
    )

    # Check for title (# heading at start)
    check.has_title = bool(re.search(r"^#\s+\S+", content, re.MULTILINE))

    # Check for tables
    check.has_table = bool(re.search(r"\|.*\|.*\|", content))

    # Check for parent link
    check.has_parent_link = bool(
        re.search(r"\*\*Parent\*\*:.*\[", content, re.IGNORECASE)
        or re.search(r"Parent:.*\[", content)
    )

    # Check for updated date
    check.has_updated_date = bool(
        re.search(r"\*\*Updated\*\*:", content, re.IGNORECASE)
        or re.search(r"Updated:\s*\d{4}-\d{2}-\d{2}", content)
    )

    # Check for related docs section
    check.has_related_docs = bool(
        re.search(r"##.*Related.*Documentation", content, re.IGNORECASE)
        or re.search(r"##.*Related.*Docs", content, re.IGNORECASE)
    )

    # Count internal links
    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
    check.link_count = len([l for l in links if not l[1].startswith("http")])

    # Identify issues
    if check.lines < 30:
        check.issues.append(f"Too short ({check.lines} lines, need 30+)")
    if not check.has_title:
        check.issues.append("Missing title heading")
    if not check.has_table:
        check.issues.append("No tables (add content tables)")
    if not check.has_parent_link:
        check.issues.append("Missing parent link")
    if check.link_count < 3:
        check.issues.append(f"Low link count ({check.link_count}, need 3+)")

    check.calculate_score()
    return check


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check README quality")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enforce strict quality criteria (score >= 80)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=60,
        help="Minimum acceptable score (default: 60)",
    )
    args = parser.parse_args()

    if args.strict:
        args.min_score = 80

    # Find all README.md files in docs/
    docs_path = Path("docs")
    if not docs_path.exists():
        print("Error: docs/ directory not found", file=sys.stderr)
        return 1

    base_path = Path.cwd()
    readmes = list(docs_path.rglob("README.md"))
    results: List[QualityCheck] = []

    for readme in sorted(readmes):
        check = analyze_readme(readme, base_path)
        results.append(check)

    if args.json:
        # Output as JSON
        output = {
            "total": len(results),
            "passing": sum(1 for r in results if r.score >= args.min_score),
            "failing": sum(1 for r in results if r.score < args.min_score),
            "average_score": (
                sum(r.score for r in results) / len(results) if results else 0
            ),
            "results": [
                {
                    "path": r.path,
                    "score": r.score,
                    "lines": r.lines,
                    "issues": r.issues,
                }
                for r in results
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        # Pretty print results
        print("=" * 70)
        print("📊 README Quality Report")
        print("=" * 70)
        print()

        failing = [r for r in results if r.score < args.min_score]
        passing = [r for r in results if r.score >= args.min_score]

        if failing:
            print(f"❌ Failing ({len(failing)} files, score < {args.min_score}):")
            print("-" * 70)
            for r in sorted(failing, key=lambda x: x.score):
                print(f"  {r.score:3d}  {r.path}")
                for issue in r.issues:
                    print(f"       ⚠️  {issue}")
            print()

        print(f"✅ Passing ({len(passing)} files):")
        print("-" * 70)
        for r in sorted(passing, key=lambda x: -x.score)[:10]:
            print(f"  {r.score:3d}  {r.path}")
        if len(passing) > 10:
            print(f"  ... and {len(passing) - 10} more")
        print()

        # Summary
        avg_score = sum(r.score for r in results) / len(results) if results else 0
        print("=" * 70)
        print(f"📈 Summary:")
        print(f"   Total READMEs: {len(results)}")
        print(f"   Passing: {len(passing)} ({len(passing) * 100 // len(results)}%)")
        print(f"   Failing: {len(failing)} ({len(failing) * 100 // len(results)}%)")
        print(f"   Average Score: {avg_score:.1f}/100")
        print("=" * 70)

        return 1 if failing else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
