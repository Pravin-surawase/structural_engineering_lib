#!/usr/bin/env python3
"""
Release Cadence Optimization - TASK-288

Analyzes release history and metrics to recommend optimal release cadence.
Uses bug rate, velocity, test coverage, and feature completion to score releases.

Usage:
    python scripts/analyze_release_cadence.py [--releases 5] [--json] [--output docs/release/CADENCE_ANALYSIS.md]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import NamedTuple


class ReleaseMetrics(NamedTuple):
    """Metrics for a single release."""

    version: str
    date: str
    commits: int
    days_since_prev: int
    bug_fixes: int
    features: int
    docs: int


class CadenceRecommendation(NamedTuple):
    """Cadence recommendation result."""

    current_cadence: str
    recommended_cadence: str
    score: int
    rationale: list[str]
    releases_analyzed: list[ReleaseMetrics]


class ReleaseCadenceAnalyzer:
    """Analyzes release history to recommend optimal cadence."""

    CADENCE_THRESHOLDS = {
        "daily": (0, 2),          # 0-2 days between releases
        "bi-daily": (2, 4),       # 2-4 days
        "weekly": (4, 10),        # ~1 week
        "bi-weekly": (10, 18),    # ~2 weeks
        "monthly": (18, 45),      # ~1 month
        "quarterly": (45, 120),   # ~3 months
    }

    def __init__(self, repo_path: Path | None = None):
        """Initialize with repository path."""
        self.repo_path = repo_path or Path.cwd()

    def _run_command(self, cmd: list[str]) -> str:
        """Run shell command and return output."""
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.repo_path,
            check=False,
        )
        return result.stdout.strip()

    def get_release_tags(self, count: int = 10) -> list[str]:
        """Get recent release tags sorted by date."""
        result = self._run_command(
            ["git", "tag", "--sort=-creatordate", "-l", "v*"]
        )
        if not result:
            return []
        tags = result.split("\n")
        return tags[:count]

    def get_tag_date(self, tag: str) -> str:
        """Get date when tag was created."""
        result = self._run_command(
            ["git", "log", "-1", "--format=%ci", tag]
        )
        if result:
            return result.split()[0]  # Just the date part
        return "unknown"

    def count_commits_between(self, tag1: str, tag2: str) -> int:
        """Count commits between two tags."""
        result = self._run_command(
            ["git", "rev-list", "--count", f"{tag2}..{tag1}"]
        )
        return int(result) if result.isdigit() else 0

    def count_commit_types(self, tag1: str, tag2: str) -> dict[str, int]:
        """Count different types of commits between tags."""
        result = self._run_command(
            ["git", "log", "--oneline", f"{tag2}..{tag1}"]
        )

        counts = {"bug_fixes": 0, "features": 0, "docs": 0, "other": 0}

        for line in result.split("\n"):
            if not line:
                continue
            line_lower = line.lower()
            if "fix" in line_lower or "bug" in line_lower:
                counts["bug_fixes"] += 1
            elif "feat" in line_lower or "add" in line_lower:
                counts["features"] += 1
            elif "doc" in line_lower or "readme" in line_lower:
                counts["docs"] += 1
            else:
                counts["other"] += 1

        return counts

    def calculate_days_between(self, date1: str, date2: str) -> int:
        """Calculate days between two dates."""
        try:
            d1 = datetime.strptime(date1, "%Y-%m-%d")
            d2 = datetime.strptime(date2, "%Y-%m-%d")
            return abs((d1 - d2).days)
        except ValueError:
            return 0

    def determine_cadence(self, avg_days: float) -> str:
        """Determine cadence category from average days."""
        for cadence, (low, high) in self.CADENCE_THRESHOLDS.items():
            if low <= avg_days < high:
                return cadence
        return "infrequent"

    def calculate_cadence_score(self, releases: list[ReleaseMetrics]) -> int:
        """Calculate cadence health score (0-100)."""
        if len(releases) < 2:
            return 50  # Not enough data

        score = 100

        # Factor 1: Bug rate trend (30 points)
        # Declining bugs = good
        bug_counts = [r.bug_fixes for r in releases]
        if len(bug_counts) >= 3:
            trend = bug_counts[0] - bug_counts[-1]  # Negative = improving
            if trend < 0:
                score -= 0  # Bugs decreasing = good
            elif trend > 3:
                score -= 15  # Bugs increasing significantly
            elif trend > 0:
                score -= 5  # Bugs slightly increasing

        # Factor 2: Velocity consistency (25 points)
        commits = [r.commits for r in releases]
        if commits:
            avg_commits = sum(commits) / len(commits)
            variance = sum((c - avg_commits) ** 2 for c in commits) / len(commits)
            if variance > 100:
                score -= 15  # High variance = inconsistent
            elif variance > 50:
                score -= 10

        # Factor 3: Days between releases (20 points)
        days = [r.days_since_prev for r in releases if r.days_since_prev > 0]
        if days:
            avg_days = sum(days) / len(days)
            if avg_days < 1:
                score -= 10  # Too frequent (overwhelming)
            elif avg_days > 30:
                score -= 10  # Too infrequent (stale)

        # Factor 4: Feature/Bug ratio (15 points)
        total_features = sum(r.features for r in releases)
        total_bugs = sum(r.bug_fixes for r in releases)
        if total_bugs > 0:
            ratio = total_features / total_bugs
            if ratio < 0.5:
                score -= 10  # Mostly bug fixes = technical debt
            elif ratio > 3:
                score -= 5  # Mostly features, might be neglecting bugs

        # Factor 5: Documentation included (10 points)
        total_docs = sum(r.docs for r in releases)
        if total_docs == 0:
            score -= 10  # No docs = poor practice

        return max(0, min(100, score))

    def recommend_cadence(self, score: int, current_cadence: str) -> str:
        """Recommend cadence based on score and current state."""
        if score >= 85:
            # High quality - can afford longer cycles
            if current_cadence in ["daily", "bi-daily"]:
                return "weekly"
            if current_cadence == "weekly":
                return "bi-weekly"
            return current_cadence

        if score >= 70:
            # Good quality - maintain or slightly extend
            return current_cadence

        if score >= 50:
            # Fair - tighten cadence for faster feedback
            if current_cadence in ["monthly", "quarterly"]:
                return "bi-weekly"
            if current_cadence == "bi-weekly":
                return "weekly"
            return current_cadence

        # Poor score - need rapid iteration
        return "weekly"

    def analyze(self, release_count: int = 5) -> CadenceRecommendation:
        """Analyze release history and generate recommendation."""
        tags = self.get_release_tags(release_count + 1)

        if len(tags) < 2:
            return CadenceRecommendation(
                current_cadence="unknown",
                recommended_cadence="weekly",
                score=50,
                rationale=["Insufficient release history for analysis"],
                releases_analyzed=[],
            )

        releases = []
        for i, tag in enumerate(tags[:-1]):
            prev_tag = tags[i + 1]
            date = self.get_tag_date(tag)
            prev_date = self.get_tag_date(prev_tag)
            days = self.calculate_days_between(date, prev_date)
            commits = self.count_commits_between(tag, prev_tag)
            types = self.count_commit_types(tag, prev_tag)

            releases.append(
                ReleaseMetrics(
                    version=tag,
                    date=date,
                    commits=commits,
                    days_since_prev=days,
                    bug_fixes=types["bug_fixes"],
                    features=types["features"],
                    docs=types["docs"],
                )
            )

        # Calculate metrics
        avg_days = sum(r.days_since_prev for r in releases) / len(releases)
        current_cadence = self.determine_cadence(avg_days)
        score = self.calculate_cadence_score(releases)
        recommended_cadence = self.recommend_cadence(score, current_cadence)

        # Generate rationale
        rationale = []

        if score >= 85:
            rationale.append(f"Score {score}/100: Excellent release quality")
        elif score >= 70:
            rationale.append(f"Score {score}/100: Good release quality")
        elif score >= 50:
            rationale.append(f"Score {score}/100: Fair release quality, room for improvement")
        else:
            rationale.append(f"Score {score}/100: Needs attention")

        rationale.append(f"Average {avg_days:.1f} days between releases ({current_cadence} cadence)")

        avg_commits = sum(r.commits for r in releases) / len(releases)
        rationale.append(f"Average {avg_commits:.0f} commits per release")

        total_bugs = sum(r.bug_fixes for r in releases)
        total_features = sum(r.features for r in releases)
        rationale.append(f"Feature/Bug ratio: {total_features}:{total_bugs}")

        if recommended_cadence != current_cadence:
            rationale.append(f"Recommend changing from {current_cadence} to {recommended_cadence}")
        else:
            rationale.append(f"Current {current_cadence} cadence is appropriate")

        return CadenceRecommendation(
            current_cadence=current_cadence,
            recommended_cadence=recommended_cadence,
            score=score,
            rationale=rationale,
            releases_analyzed=releases,
        )

    def generate_report(self, rec: CadenceRecommendation) -> str:
        """Generate human-readable report."""
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║              RELEASE CADENCE ANALYSIS                            ║
║              Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}                          ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  📊 Summary                                                       ║
║  ├── Current Cadence:    {rec.current_cadence:<20}                 ║
║  ├── Recommended:        {rec.recommended_cadence:<20}                 ║
║  └── Quality Score:      {rec.score:>3}/100                              ║
║                                                                   ║
╠══════════════════════════════════════════════════════════════════╣
║  📈 Release History                                               ║
║                                                                   ║
"""

        for r in rec.releases_analyzed:
            report += f"║  {r.version:<10} │ {r.date} │ {r.commits:>3} commits │ {r.days_since_prev:>2}d │ F:{r.features} B:{r.bug_fixes} D:{r.docs} ║\n"

        report += """║                                                                   ║
╠══════════════════════════════════════════════════════════════════╣
║  💡 Analysis                                                      ║
║                                                                   ║
"""

        for line in rec.rationale:
            line_truncated = line[:55] if len(line) > 55 else line
            report += f"║    • {line_truncated:<55}  ║\n"

        report += """║                                                                   ║
╚══════════════════════════════════════════════════════════════════╝

CADENCE GUIDE:
  • Daily/Bi-daily: Rapid iteration, early development phase
  • Weekly: Active development, good feedback loop
  • Bi-weekly: Maturing product, stable features
  • Monthly: Mature product, maintenance mode
  • Quarterly: Enterprise, breaking changes only
"""
        return report


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze release cadence and recommend optimal timing"
    )
    parser.add_argument(
        "--releases",
        type=int,
        default=5,
        help="Number of releases to analyze (default: 5)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file path (markdown or JSON based on extension)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of report",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output, only return exit code",
    )

    args = parser.parse_args()

    # Run analysis
    analyzer = ReleaseCadenceAnalyzer()
    recommendation = analyzer.analyze(args.releases)

    # Output results
    if args.json:
        result = {
            "timestamp": datetime.now().isoformat(),
            "current_cadence": recommendation.current_cadence,
            "recommended_cadence": recommendation.recommended_cadence,
            "score": recommendation.score,
            "rationale": recommendation.rationale,
            "releases": [
                {
                    "version": r.version,
                    "date": r.date,
                    "commits": r.commits,
                    "days_since_prev": r.days_since_prev,
                    "bug_fixes": r.bug_fixes,
                    "features": r.features,
                    "docs": r.docs,
                }
                for r in recommendation.releases_analyzed
            ],
        }
        if not args.quiet:
            print(json.dumps(result, indent=2))
    elif not args.quiet:
        print(analyzer.generate_report(recommendation))

    # Save to file if requested
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)

        if args.output.suffix == ".json":
            result = {
                "timestamp": datetime.now().isoformat(),
                "current_cadence": recommendation.current_cadence,
                "recommended_cadence": recommendation.recommended_cadence,
                "score": recommendation.score,
                "rationale": recommendation.rationale,
                "releases": [
                    {
                        "version": r.version,
                        "date": r.date,
                        "commits": r.commits,
                        "days_since_prev": r.days_since_prev,
                        "bug_fixes": r.bug_fixes,
                        "features": r.features,
                        "docs": r.docs,
                    }
                    for r in recommendation.releases_analyzed
                ],
            }
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
        else:
            with open(args.output, "w") as f:
                f.write(analyzer.generate_report(recommendation))

        if not args.quiet:
            print(f"\n✅ Saved to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
