#!/usr/bin/env python3
"""Agent drift detector — detect when agents deviate from prescribed behavior.

Analyzes session data to identify drift: when actual agent actions violate
rules in .agent.md files. Helps catch recurring mistakes before they become
habitual patterns.

Usage:
    .venv/bin/python scripts/agent_drift_detector.py --session "2026-04-01T14:30"
    .venv/bin/python scripts/agent_drift_detector.py --agent ops --last 5
    .venv/bin/python scripts/agent_drift_detector.py --summary
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.agent_data import DRIFT_DIR, ensure_dirs, list_sessions, load_session
from _lib.output import StatusLine, print_table

# Drift rules for each agent type
# Each rule has: id, name, pattern, description, severity
DRIFT_RULES = {
    "ops": {
        "prescribed": [
            {
                "id": "OPS-001",
                "pattern": r"ai_commit\.sh",
                "name": "THE_ONE_RULE",
                "description": "All commits via ai_commit.sh",
            },
        ],
        "forbidden": [
            {
                "id": "OPS-002",
                "pattern": r"^git add",
                "name": "NO_MANUAL_GIT",
                "severity": "CRITICAL",
            },
            {
                "id": "OPS-003",
                "pattern": r"^git commit",
                "name": "NO_MANUAL_GIT",
                "severity": "CRITICAL",
            },
            {
                "id": "OPS-004",
                "pattern": r"^git push",
                "name": "NO_MANUAL_GIT",
                "severity": "CRITICAL",
            },
            {
                "id": "OPS-005",
                "pattern": r"--force|--no-verify",
                "name": "NO_FORCE",
                "severity": "CRITICAL",
            },
            {
                "id": "OPS-006",
                "pattern": r"gh pr merge --admin",
                "name": "NO_ADMIN_MERGE",
                "severity": "CRITICAL",
            },
            {
                "id": "OPS-007",
                "pattern": r"GIT_HOOKS_BYPASS",
                "name": "NO_BYPASS",
                "severity": "CRITICAL",
            },
        ],
    },
    "backend": {
        "prescribed": [
            {
                "id": "BE-001",
                "pattern": r"\.venv/bin/python",
                "name": "VENV_PYTHON",
                "description": "Always use .venv/bin/python",
            },
            {
                "id": "BE-002",
                "pattern": r"discover_api_signatures",
                "name": "API_DISCOVERY",
                "description": "Check API signatures before wrapping",
            },
        ],
        "forbidden": [
            {
                "id": "BE-003",
                "pattern": r"^python\s",
                "name": "NO_BARE_PYTHON",
                "severity": "WARNING",
            },
            {
                "id": "BE-004",
                "pattern": r"\bwidth\b|\bheight\b",
                "name": "WRONG_PARAM_NAMES",
                "severity": "WARNING",
            },
        ],
    },
    "frontend": {
        "prescribed": [
            {
                "id": "FE-001",
                "pattern": r"ls react_app/src/hooks/",
                "name": "CHECK_HOOKS_FIRST",
                "description": "Search existing hooks before creating",
            },
            {
                "id": "FE-002",
                "pattern": r"npm run build",
                "name": "BUILD_BEFORE_COMMIT",
                "description": "Build check before commit",
            },
        ],
        "forbidden": [
            {
                "id": "FE-003",
                "pattern": r"\.css$",
                "name": "NO_CSS_FILES",
                "severity": "WARNING",
            },
        ],
    },
    "doc-master": {
        "prescribed": [
            {
                "id": "DM-001",
                "pattern": r"safe_file_move\.py",
                "name": "SAFE_MOVE",
                "description": "Use safe_file_move.py to preserve links",
            },
            {
                "id": "DM-002",
                "pattern": r"safe_file_delete\.py",
                "name": "SAFE_DELETE",
                "description": "Use safe_file_delete.py to preserve links",
            },
        ],
        "forbidden": [
            {
                "id": "DM-003",
                "pattern": r"^mv\s|^rm\s",
                "name": "NO_RAW_MV_RM",
                "severity": "WARNING",
            },
        ],
    },
    "tester": {
        "prescribed": [
            {
                "id": "TE-001",
                "pattern": r"pytest",
                "name": "RUN_TESTS",
                "description": "Run tests after changes",
            },
        ],
        "forbidden": [],
    },
    "structural-math": {
        "prescribed": [
            {
                "id": "SM-001",
                "pattern": r"discover_api_signatures",
                "name": "API_DISCOVERY",
                "description": "Check API signatures before implementation",
            },
        ],
        "forbidden": [
            {
                "id": "SM-002",
                "pattern": r"gamma_c\s*=\s*1\.[^5]",
                "name": "NO_SAFETY_FACTOR_CHANGE",
                "severity": "CRITICAL",
            },
        ],
    },
    "api-developer": {
        "prescribed": [],
        "forbidden": [],
    },
    "reviewer": {
        "prescribed": [],
        "forbidden": [],
    },
    "structural-engineer": {
        "prescribed": [],
        "forbidden": [],
    },
    "governance": {
        "prescribed": [],
        "forbidden": [],
    },
    "security": {
        "prescribed": [],
        "forbidden": [],
    },
    "library-expert": {
        "prescribed": [],
        "forbidden": [],
    },
    "ui-designer": {
        "prescribed": [],
        "forbidden": [],
    },
    "orchestrator": {
        "prescribed": [],
        "forbidden": [],
    },
}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Detect agent drift from prescribed behavior"
    )
    parser.add_argument(
        "--session",
        type=str,
        help="Session ID to analyze (e.g., 2026-04-01T14:30)",
    )
    parser.add_argument(
        "--agent",
        type=str,
        help="Filter to specific agent",
    )
    parser.add_argument(
        "--last",
        type=int,
        help="Analyze last N sessions",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show all-time drift summary",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path (defaults to logs/agent-performance/drift/<session_id>.json)",
    )
    return parser.parse_args()


def detect_commit_drift(commits: list[dict], agent_name: str) -> list[dict]:
    """Detect drift in commit messages.

    Args:
        commits: List of commit dicts with 'message' field.
        agent_name: Agent name to check rules for.

    Returns:
        List of drift event dicts.
    """
    if agent_name not in DRIFT_RULES:
        return []

    rules = DRIFT_RULES[agent_name]
    drift_events: list[dict] = []

    for commit in commits:
        message = commit.get("message", "")

        # Check forbidden patterns
        for rule in rules.get("forbidden", []):
            pattern = rule["pattern"]
            if re.search(pattern, message, re.IGNORECASE):
                drift_events.append(
                    {
                        "agent": agent_name,
                        "severity": rule.get("severity", "WARNING"),
                        "rule_id": rule["id"],
                        "rule_name": rule["name"],
                        "detail": f"Commit message matches forbidden pattern: {pattern}",
                        "commit_sha": commit.get("sha", ""),
                        "commit_message": message,
                    }
                )

    return drift_events


def detect_file_drift(files_changed: dict[str, str], agent_name: str) -> list[dict]:
    """Detect drift in file operations.

    Args:
        files_changed: Dict mapping file path to change type.
        agent_name: Agent name to check rules for.

    Returns:
        List of drift event dicts.
    """
    if agent_name not in DRIFT_RULES:
        return []

    rules = DRIFT_RULES[agent_name]
    drift_events: list[dict] = []

    for filepath, change_type in files_changed.items():
        # Check forbidden file patterns (e.g., .css for frontend)
        for rule in rules.get("forbidden", []):
            pattern = rule["pattern"]
            if re.search(pattern, filepath):
                drift_events.append(
                    {
                        "agent": agent_name,
                        "severity": rule.get("severity", "WARNING"),
                        "rule_id": rule["id"],
                        "rule_name": rule["name"],
                        "detail": f"File operation violates rule: {filepath}",
                        "filepath": filepath,
                        "change_type": change_type,
                    }
                )

    return drift_events


def drift_score(violations: int, total_rules: int) -> float:
    """Calculate drift score.

    Score = 1.0 - (violations / total_rules)
    1.0 = perfect compliance, 0.0 = total drift

    Args:
        violations: Number of rule violations.
        total_rules: Total number of applicable rules.

    Returns:
        Drift score [0.0, 1.0].
    """
    if total_rules == 0:
        return 1.0
    return max(0.0, 1.0 - violations / total_rules)


def detect_drift(session_data: dict, agent_filter: str | None = None) -> dict:
    """Detect drift events in a session.

    Args:
        session_data: Session data dict from agent_session_collector.
        agent_filter: Optional agent name to filter by.

    Returns:
        Drift analysis dict with events and scores.
    """
    session_id = session_data.get("session_id", "unknown")
    agents_active = session_data.get("agents_active", [])
    commits = session_data.get("commits", [])
    files_changed = session_data.get("files_changed", {})

    # Filter agents if requested
    if agent_filter:
        agents_active = [a for a in agents_active if a == agent_filter]

    all_drift_events: list[dict] = []
    agent_drift_scores: dict[str, float] = {}

    for agent in agents_active:
        if agent not in DRIFT_RULES:
            continue

        # Detect drift in commits
        commit_drift = detect_commit_drift(commits, agent)
        all_drift_events.extend(commit_drift)

        # Detect drift in file operations
        file_drift = detect_file_drift(files_changed, agent)
        all_drift_events.extend(file_drift)

        # Calculate drift score for this agent
        rules = DRIFT_RULES[agent]
        total_rules = len(rules.get("prescribed", [])) + len(rules.get("forbidden", []))
        violations = len([e for e in all_drift_events if e["agent"] == agent])
        agent_drift_scores[agent] = drift_score(violations, total_rules)

    # Summarize by severity
    summary = {
        "total_events": len(all_drift_events),
        "critical": len([e for e in all_drift_events if e["severity"] == "CRITICAL"]),
        "warning": len([e for e in all_drift_events if e["severity"] == "WARNING"]),
    }

    return {
        "session_id": session_id,
        "analysis_timestamp": datetime.now().isoformat(),
        "agents_analyzed": agents_active,
        "drift_events": all_drift_events,
        "agent_drift_scores": agent_drift_scores,
        "summary": summary,
    }


def save_drift_report(drift_data: dict, output_path: Path | None = None) -> Path:
    """Save drift report to file.

    Args:
        drift_data: Drift analysis dict.
        output_path: Optional custom output path.

    Returns:
        Path to saved file.
    """
    ensure_dirs()

    if output_path:
        filepath = output_path
    else:
        session_id = drift_data["session_id"]
        # Use date portion for filename
        date_str = session_id.split("T")[0]
        filepath = DRIFT_DIR / f"drift_{date_str}.json"

    filepath.write_text(json.dumps(drift_data, indent=2) + "\n", encoding="utf-8")
    return filepath


def load_all_drift_reports() -> list[dict]:
    """Load all drift reports from DRIFT_DIR.

    Returns:
        List of drift report dicts.
    """
    if not DRIFT_DIR.exists():
        return []

    reports: list[dict] = []
    for filepath in sorted(DRIFT_DIR.glob("drift_*.json")):
        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
            reports.append(data)
        except (json.JSONDecodeError, OSError):
            continue

    return reports


def print_drift_summary(reports: list[dict], agent_filter: str | None = None) -> None:
    """Print summary of all drift reports.

    Args:
        reports: List of drift report dicts.
        agent_filter: Optional agent name to filter by.
    """
    if not reports:
        StatusLine.warn("No drift reports found")
        return

    # Aggregate by agent
    agent_stats: dict[str, dict] = {}

    for report in reports:
        for agent, score in report.get("agent_drift_scores", {}).items():
            if agent_filter and agent != agent_filter:
                continue

            if agent not in agent_stats:
                agent_stats[agent] = {
                    "sessions": 0,
                    "total_violations": 0,
                    "total_score": 0.0,
                }

            agent_stats[agent]["sessions"] += 1
            agent_stats[agent]["total_score"] += score

            # Count violations for this agent in this report
            violations = len(
                [e for e in report.get("drift_events", []) if e["agent"] == agent]
            )
            agent_stats[agent]["total_violations"] += violations

    # Print table
    rows = []
    for agent, stats in sorted(agent_stats.items()):
        avg_score = stats["total_score"] / stats["sessions"]
        rows.append(
            [
                agent,
                str(stats["sessions"]),
                str(stats["total_violations"]),
                f"{avg_score:.2f}",
            ]
        )

    print_table(
        ["Agent", "Sessions", "Total Violations", "Avg Drift Score"],
        rows,
    )

    StatusLine.ok(
        f"Summary for {len(agent_stats)} agents across {len(reports)} sessions"
    )


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Summary mode: show all-time drift stats
    if args.summary:
        StatusLine.ok("Loading all drift reports...")
        reports = load_all_drift_reports()
        print_drift_summary(reports, agent_filter=args.agent)
        return 0

    # Determine session(s) to analyze
    sessions_to_analyze: list[str] = []

    if args.session:
        sessions_to_analyze = [args.session]
    elif args.last:
        all_sessions = list_sessions()
        sessions_to_analyze = all_sessions[-args.last :]
    else:
        # Default: analyze latest session
        all_sessions = list_sessions()
        if not all_sessions:
            StatusLine.fail("No sessions found in logs/agent-performance/sessions/")
            return 1
        sessions_to_analyze = [all_sessions[-1]]

    # Analyze each session
    for session_id in sessions_to_analyze:
        StatusLine.ok(f"Analyzing session {session_id}...")

        # Load session data
        session_data = load_session(session_id)
        if not session_data:
            StatusLine.fail(f"Session {session_id} not found")
            continue

        # Detect drift
        drift_data = detect_drift(session_data, agent_filter=args.agent)

        # Save report
        output_path = save_drift_report(drift_data, output_path=args.output)
        StatusLine.ok(f"Drift report saved to {output_path}")

        # Print summary
        summary = drift_data["summary"]
        if summary["total_events"] == 0:
            StatusLine.ok("No drift detected")
        else:
            StatusLine.warn(
                f"Drift detected: {summary['total_events']} events "
                f"({summary['critical']} critical, {summary['warning']} warnings)"
            )

            # Print events
            if drift_data["drift_events"]:
                print("\nDrift Events:")
                rows = []
                for event in drift_data["drift_events"]:
                    rows.append(
                        [
                            event["agent"],
                            event["severity"],
                            event["rule_name"],
                            (
                                event["detail"][:60] + "..."
                                if len(event["detail"]) > 60
                                else event["detail"]
                            ),
                        ]
                    )
                print_table(["Agent", "Severity", "Rule", "Detail"], rows)

        # Print drift scores
        if drift_data["agent_drift_scores"]:
            print("\nAgent Drift Scores:")
            rows = []
            for agent, score in sorted(drift_data["agent_drift_scores"].items()):
                status = "✓" if score >= 0.7 else "✗"
                rows.append([agent, f"{score:.2f}", status])
            print_table(["Agent", "Score", "Status"], rows)

    return 0


if __name__ == "__main__":
    sys.exit(main())
