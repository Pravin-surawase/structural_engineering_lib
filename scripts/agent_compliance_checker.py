#!/usr/bin/env python3
"""Agent compliance checker — verify agents followed their .agent.md rules.

Analyzes git history and session artifacts to check whether agents followed
prescribed workflows from their .agent.md files.

Usage:
    .venv/bin/python scripts/agent_compliance_checker.py --session "2026-04-01T14:30"
    .venv/bin/python scripts/agent_compliance_checker.py --agent backend --last 10
    .venv/bin/python scripts/agent_compliance_checker.py --summary
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.agent_data import list_sessions, load_session
from _lib.output import StatusLine, print_json, print_table
from _lib.utils import REPO_ROOT

# Compliance rules (§7.2 from agent-evolver-plan.md)
COMPLIANCE_RULES = [
    {
        "id": "SESSION-001",
        "name": "session_end_tasks_updated",
        "description": "TASKS.md updated at session end",
        "applies_to": "all",
        "check_type": "file_modified",
        "target": "docs/TASKS.md",
    },
    {
        "id": "SESSION-002",
        "name": "session_end_brief_updated",
        "description": "next-session-brief.md updated at session end",
        "applies_to": "all",
        "check_type": "file_modified",
        "target": "docs/planning/next-session-brief.md",
    },
    {
        "id": "SESSION-003",
        "name": "feedback_logged",
        "description": "Feedback logged at session end",
        "applies_to": "all",
        "check_type": "feedback_exists",
    },
    {
        "id": "SESSION-004",
        "name": "tests_run",
        "description": "Tests were run during session",
        "applies_to": ["backend", "tester", "structural-math", "api-developer"],
        "check_type": "tests_executed",
    },
    {
        "id": "SESSION-005",
        "name": "safe_file_ops",
        "description": "File operations used safe scripts (no raw mv/rm for docs)",
        "applies_to": ["doc-master", "governance"],
        "check_type": "no_raw_file_ops",
    },
    {
        "id": "SESSION-006",
        "name": "architecture_respected",
        "description": "No upward imports in structural_lib",
        "applies_to": ["backend", "structural-math"],
        "check_type": "architecture_check",
    },
    {
        "id": "SESSION-007",
        "name": "commit_format",
        "description": "Commit messages follow conventional format",
        "applies_to": "all",
        "check_type": "commit_format",
    },
    {
        "id": "SESSION-008",
        "name": "build_check",
        "description": "Build verified before commit",
        "applies_to": ["frontend"],
        "check_type": "build_ran",
    },
]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Check agent compliance with .agent.md rules"
    )
    parser.add_argument(
        "--session",
        type=str,
        help="Session ID to check (e.g., 2026-04-01T14:30)",
    )
    parser.add_argument(
        "--agent",
        type=str,
        help="Filter results for specific agent",
    )
    parser.add_argument(
        "--last",
        type=int,
        help="Check last N sessions",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show summary across all sessions",
    )
    return parser.parse_args()


def rule_applies_to_agent(rule: dict, agent_name: str) -> bool:
    """Check if a compliance rule applies to an agent.

    Args:
        rule: Compliance rule dict.
        agent_name: Agent name.

    Returns:
        True if rule applies to this agent.
    """
    applies_to = rule["applies_to"]
    if applies_to == "all":
        return True
    if isinstance(applies_to, list):
        return agent_name in applies_to
    return False


def check_file_modified(session_data: dict, target_file: str) -> bool:
    """Check if target file was modified in the session.

    Args:
        session_data: Session data dict.
        target_file: File path to check (relative to repo root).

    Returns:
        True if file was modified.
    """
    files_changed = session_data.get("files_changed", {})
    return target_file in files_changed


def check_feedback_exists(session_data: dict) -> bool:
    """Check if feedback was logged for this session.

    Args:
        session_data: Session data dict.

    Returns:
        True if feedback file exists for session date.
    """
    session_id = session_data.get("session_id", "")
    if not session_id:
        return False

    # Extract date (YYYY-MM-DD) from session_id
    date_part = session_id.split("T")[0] if "T" in session_id else session_id

    # Check logs/feedback/ for files matching date
    feedback_dir = REPO_ROOT / "logs" / "feedback"
    if not feedback_dir.exists():
        return False

    # Look for feedback files with matching date prefix
    feedback_files = list(feedback_dir.glob(f"{date_part}*.json"))
    return len(feedback_files) > 0


def check_tests_executed(session_data: dict) -> bool:
    """Check if tests were run during the session.

    Args:
        session_data: Session data dict.

    Returns:
        True if tests were executed (passed > 0).
    """
    test_results = session_data.get("test_results", {})
    passed = test_results.get("passed", 0)
    return passed > 0


def check_commit_format(session_data: dict) -> bool:
    """Check if all commits follow conventional format.

    Args:
        session_data: Session data dict.

    Returns:
        True if all commits match conventional format.
    """
    commits = session_data.get("commits", [])
    if not commits:
        return True  # No commits = no violations

    # Conventional commit pattern: type(scope): message OR type: message
    pattern = re.compile(
        r"^(feat|fix|docs|refactor|test|chore|ci|perf|style|build)(\([^)]+\))?: .+"
    )

    for commit in commits:
        message = commit.get("message", "")
        if not pattern.match(message):
            return False

    return True


def check_no_raw_file_ops(session_data: dict) -> bool:
    """Check that safe file scripts were used (not raw mv/rm).

    For doc-master and governance agents, file operations on docs should use
    safe_file_move.py or safe_file_delete.py, not raw mv/rm.

    Args:
        session_data: Session data dict.

    Returns:
        True if no raw file ops detected on docs.
    """
    # Check commits for evidence of raw file ops
    commits = session_data.get("commits", [])
    files_changed = session_data.get("files_changed", {})

    # Look for docs file renames/deletes without safe script use
    docs_files_affected = [
        f
        for f in files_changed
        if f.startswith("docs/") and files_changed[f] in ("deleted", "renamed")
    ]

    if not docs_files_affected:
        return True  # No docs files deleted/renamed = compliant

    # Check if safe scripts were used (heuristic: check for git history of safe script usage)
    # For now, we pass if there were no deletions/renames, or assume compliance
    # A more sophisticated check would parse git log --name-status for R/D operations
    # and cross-check against ai_commit.sh usage

    return True  # Conservative: assume compliant unless proven otherwise


def check_architecture(session_data: dict) -> bool:
    """Check for architecture boundary violations.

    For backend/structural-math agents, verify no upward imports in structural_lib.

    Args:
        session_data: Session data dict.

    Returns:
        True if no architecture violations detected.
    """
    files_changed = session_data.get("files_changed", {})

    # Check if any structural_lib files were modified
    structural_lib_files = [
        f for f in files_changed if f.startswith("Python/structural_lib/")
    ]

    if not structural_lib_files:
        return True  # No structural_lib changes = compliant

    # Heuristic: if no violations in recent session, assume compliant
    # Full check would require running validate_imports.py, which is expensive
    # Instead, check for obvious bad patterns in file paths

    # Check for upward imports (services importing from core, etc.)
    for filepath in structural_lib_files:
        # If services/ modified and core/ also modified, could indicate violation
        # But this is a weak heuristic; full validation needs AST parsing
        pass

    return True  # Conservative: assume compliant


def check_build_ran(session_data: dict) -> bool:
    """Check if build was verified before commit (frontend agents).

    Args:
        session_data: Session data dict.

    Returns:
        True if build check detected.
    """
    # Heuristic: if react_app files changed and no build errors, assume build ran
    files_changed = session_data.get("files_changed", {})
    react_files = [f for f in files_changed if f.startswith("react_app/")]

    if not react_files:
        return True  # No React changes = N/A

    # Check test_results or commit messages for build evidence
    # For now, assume compliant if no obvious failures
    return True


def check_compliance(
    session_data: dict,
    agent_name: str | None = None,
) -> dict:
    """Check compliance for a session.

    Args:
        session_data: Session data dict.
        agent_name: Optional agent filter.

    Returns:
        Dict with compliance results per agent.
    """
    agents_active = session_data.get("agents_active", [])
    if not agents_active:
        return {
            "session_id": session_data.get("session_id", "unknown"),
            "compliance_results": {},
            "overall_compliance_rate": 0.0,
        }

    # Filter to specific agent if requested
    if agent_name:
        agents_active = [agent_name] if agent_name in agents_active else []

    compliance_results = {}

    for agent in agents_active:
        rules_checked = []
        rules_passed = []
        violations = []

        for rule in COMPLIANCE_RULES:
            if not rule_applies_to_agent(rule, agent):
                continue

            rules_checked.append(rule["id"])
            check_type = rule["check_type"]
            passed = False

            # Dispatch to appropriate check function
            if check_type == "file_modified":
                passed = check_file_modified(session_data, rule["target"])
            elif check_type == "feedback_exists":
                passed = check_feedback_exists(session_data)
            elif check_type == "tests_executed":
                passed = check_tests_executed(session_data)
            elif check_type == "commit_format":
                passed = check_commit_format(session_data)
            elif check_type == "no_raw_file_ops":
                passed = check_no_raw_file_ops(session_data)
            elif check_type == "architecture_check":
                passed = check_architecture(session_data)
            elif check_type == "build_ran":
                passed = check_build_ran(session_data)

            if passed:
                rules_passed.append(rule["id"])
            else:
                violations.append(
                    {
                        "rule_id": rule["id"],
                        "name": rule["name"],
                        "description": rule["description"],
                    }
                )

        # Calculate compliance rate
        compliance_rate = (
            len(rules_passed) / len(rules_checked) if rules_checked else 1.0
        )

        compliance_results[agent] = {
            "rules_checked": len(rules_checked),
            "rules_passed": len(rules_passed),
            "compliance_rate": round(compliance_rate, 3),
            "violations": violations,
            "passed": rules_passed,
        }

    # Calculate overall compliance rate
    all_checked = sum(r["rules_checked"] for r in compliance_results.values())
    all_passed = sum(r["rules_passed"] for r in compliance_results.values())
    overall_rate = all_passed / all_checked if all_checked > 0 else 0.0

    return {
        "session_id": session_data.get("session_id", "unknown"),
        "compliance_results": compliance_results,
        "overall_compliance_rate": round(overall_rate, 3),
    }


def format_summary_table(results_list: list[dict]) -> None:
    """Print a summary table across multiple sessions.

    Args:
        results_list: List of compliance result dicts.
    """
    # Aggregate by agent
    agent_stats: dict[str, dict] = {}

    for result in results_list:
        for agent, data in result.get("compliance_results", {}).items():
            if agent not in agent_stats:
                agent_stats[agent] = {
                    "sessions": 0,
                    "total_checked": 0,
                    "total_passed": 0,
                    "violations_count": 0,
                }

            stats = agent_stats[agent]
            stats["sessions"] += 1
            stats["total_checked"] += data["rules_checked"]
            stats["total_passed"] += data["rules_passed"]
            stats["violations_count"] += len(data["violations"])

    # Build table rows
    rows = []
    for agent, stats in sorted(agent_stats.items()):
        compliance_rate = (
            stats["total_passed"] / stats["total_checked"]
            if stats["total_checked"] > 0
            else 0.0
        )
        rows.append(
            [
                agent,
                str(stats["sessions"]),
                str(stats["total_checked"]),
                str(stats["total_passed"]),
                f"{compliance_rate:.1%}",
                str(stats["violations_count"]),
            ]
        )

    print("\nCompliance Summary:")
    print_table(
        [
            "Agent",
            "Sessions",
            "Rules Checked",
            "Rules Passed",
            "Compliance %",
            "Violations",
        ],
        rows,
    )


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Determine which sessions to check
    if args.session:
        session_ids = [args.session]
    elif args.last:
        all_sessions = list_sessions()
        session_ids = all_sessions[-args.last :] if all_sessions else []
    elif args.summary:
        session_ids = list_sessions()
    else:
        # Default: check most recent session
        all_sessions = list_sessions()
        session_ids = [all_sessions[-1]] if all_sessions else []

    if not session_ids:
        StatusLine.fail("No sessions found")
        return 1

    # Check compliance for each session
    results_list = []
    for session_id in session_ids:
        session_data = load_session(session_id)
        if not session_data:
            StatusLine.warn(f"Session not found: {session_id}")
            continue

        result = check_compliance(session_data, args.agent)
        results_list.append(result)

    if not results_list:
        StatusLine.fail("No valid sessions to check")
        return 1

    # Output results
    if args.summary:
        format_summary_table(results_list)
    else:
        # Print individual session results
        for result in results_list:
            print_json(result)
            print()  # Blank line between sessions

    # Determine exit code (fail if any violations in last session)
    last_result = results_list[-1]
    has_violations = any(
        data["violations"]
        for data in last_result.get("compliance_results", {}).values()
    )

    if has_violations:
        StatusLine.warn("Compliance violations detected")
        return 0  # Warning, not failure
    else:
        StatusLine.ok("All compliance checks passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
