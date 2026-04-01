#!/usr/bin/env python3
"""Agent session collector — gather all session artifacts for scoring.

Collects git commits, files changed, terminal commands, feedback items,
test results, and health data from a session into structured JSON.

Usage:
    .venv/bin/python scripts/agent_session_collector.py
    .venv/bin/python scripts/agent_session_collector.py --since "2026-04-01"
    .venv/bin/python scripts/agent_session_collector.py --session-id "2026-04-01T14:30"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.agent_data import save_session
from _lib.output import StatusLine
from _lib.utils import REPO_ROOT, run_command

# Agent identification heuristics
AGENT_HINTS_FROM_COMMIT = {
    r"^feat\(column\)": "structural-math",
    r"^feat\(slab\)": "structural-math",
    r"^feat\(footing\)": "structural-math",
    r"^feat\(.*is456.*\)": "structural-math",
    r"^docs:": "doc-master",
    r"^test:": "tester",
    r"^fix\(react\)": "frontend",
    r"^feat\(react\)": "frontend",
    r"^fix\(api\)": "api-developer",
    r"^feat\(api\)": "api-developer",
    r"^chore\(ci\)": "ops",
    r"^ci:": "ops",
}

AGENT_HINTS_FROM_FILES = {
    r"react_app/": "frontend",
    r"fastapi_app/": "api-developer",
    r"Python/structural_lib/": "backend",
    r"Python/structural_lib/codes/is456/": "structural-math",
    r"docs/": "doc-master",
    r"\.github/": "ops",
    r"scripts/": "governance",
}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Collect session artifacts for agent scoring"
    )
    parser.add_argument(
        "--since",
        type=str,
        help="Collect commits since date (YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument(
        "--session-id",
        type=str,
        help="Session ID (e.g., 2026-04-01T14:30). Auto-generated if not provided.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path (defaults to logs/agent-performance/sessions/<session_id>.json)",
    )
    return parser.parse_args()


def get_git_commits(since: str) -> list[dict]:
    """Get git commits since a date.

    Args:
        since: Date string (YYYY-MM-DD).

    Returns:
        List of commit dicts.
    """
    cmd = ["git", "log", f"--since={since}", "--oneline", "--no-merges"]
    result = run_command(cmd, capture=True)

    commits: list[dict] = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue

        parts = line.split(" ", 1)
        if len(parts) < 2:
            continue

        sha, message = parts

        # Identify agent hint from commit message
        agent_hint = identify_agent_from_commit(message)

        commits.append(
            {
                "sha": sha,
                "message": message,
                "agent_hint": agent_hint,
            }
        )

    return commits


def identify_agent_from_commit(message: str) -> str | None:
    """Identify agent from commit message patterns."""
    for pattern, agent in AGENT_HINTS_FROM_COMMIT.items():
        if re.match(pattern, message):
            return agent
    return None


def get_files_changed(sha: str) -> dict[str, str]:
    """Get files changed in a commit.

    Args:
        sha: Commit SHA.

    Returns:
        Dict mapping file path to change type (added, modified, deleted).
    """
    cmd = ["git", "diff", "--name-status", f"{sha}~1", sha]
    result = run_command(cmd, capture=True, check=False)

    if result.returncode != 0:
        return {}

    files: dict[str, str] = {}
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue

        parts = line.split("\t", 1)
        if len(parts) < 2:
            continue

        status, filepath = parts
        change_type = {
            "A": "added",
            "M": "modified",
            "D": "deleted",
            "R": "renamed",
        }.get(status[0], "unknown")

        files[filepath] = change_type

    return files


def identify_agent_from_files(files: dict[str, str]) -> str | None:
    """Identify agent from files changed."""
    for filepath in files:
        for pattern, agent in AGENT_HINTS_FROM_FILES.items():
            if re.search(pattern, filepath):
                return agent
    return None


def load_test_results() -> dict[str, int]:
    """Load latest test results from test_stats.json.

    Returns:
        Dict with passed, failed, skipped counts.
    """
    test_stats_file = REPO_ROOT / "Python" / "test_stats.json"
    if not test_stats_file.exists():
        return {"passed": 0, "failed": 0, "skipped": 0}

    try:
        data = json.loads(test_stats_file.read_text(encoding="utf-8"))
        return {
            "passed": data.get("passed", 0),
            "failed": data.get("failed", 0),
            "skipped": data.get("skipped", 0),
        }
    except (json.JSONDecodeError, OSError):
        return {"passed": 0, "failed": 0, "skipped": 0}


def load_latest_health() -> int:
    """Load latest health score from logs/evolution/.

    Returns:
        Health score [0, 100].
    """
    evolution_dir = REPO_ROOT / "logs" / "evolution"
    if not evolution_dir.exists():
        return 0

    health_files = sorted(evolution_dir.glob("health_*.json"), reverse=True)
    if not health_files:
        return 0

    try:
        data = json.loads(health_files[0].read_text(encoding="utf-8"))
        return data.get("overall_score", 0)
    except (json.JSONDecodeError, OSError):
        return 0


def collect_session(since: str, session_id: str) -> dict:
    """Collect all session artifacts.

    Args:
        since: Date string (YYYY-MM-DD).
        session_id: Session ID.

    Returns:
        Session data dict.
    """
    StatusLine.ok(f"Collecting session data since {since}...")

    # Get commits
    commits = get_git_commits(since)

    # Aggregate all files changed
    all_files: dict[str, str] = {}
    agents_active: set[str] = set()

    for commit in commits:
        sha = commit["sha"]
        files = get_files_changed(sha)
        all_files.update(files)
        commit["files_changed"] = len(files)

        # Identify agent from commit or files
        agent = commit["agent_hint"] or identify_agent_from_files(files)
        if agent:
            agents_active.add(agent)

    # Load test results and health
    test_results = load_test_results()
    health_score = load_latest_health()

    # Build session record
    session_data = {
        "schema_version": "1.1",
        "session_id": session_id,
        "collection_timestamp": datetime.now().isoformat(),
        "since_date": since,
        "agents_active": sorted(agents_active),
        "commits": commits,
        "commit_count": len(commits),
        "files_changed": all_files,
        "file_count": len(all_files),
        "test_results": test_results,
        "health_score": health_score,
    }

    return session_data


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Determine since date
    if args.since:
        since = args.since
    else:
        since = datetime.now().strftime("%Y-%m-%d")

    # Determine session ID
    if args.session_id:
        session_id = args.session_id
    else:
        session_id = datetime.now().strftime("%Y-%m-%dT%H:%M")

    # Collect session data
    try:
        session_data = collect_session(since, session_id)
    except Exception as e:
        StatusLine.fail(f"Failed to collect session data: {e}")
        return 1

    # Save session data
    try:
        if args.output:
            output_path = args.output
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps(session_data, indent=2) + "\n",
                encoding="utf-8",
            )
        else:
            output_path = save_session(session_id, session_data)

        StatusLine.ok(f"Session data saved to {output_path}")

        # Print summary
        print("\nSession Summary:")
        print(f"  Session ID: {session_id}")
        print(f"  Commits: {session_data['commit_count']}")
        print(f"  Files changed: {session_data['file_count']}")
        print(
            f"  Agents active: {', '.join(session_data['agents_active']) or 'none detected'}"
        )
        print(
            f"  Tests: {session_data['test_results']['passed']} passed, {session_data['test_results']['failed']} failed"
        )
        print(f"  Health score: {session_data['health_score']}")

        return 0
    except Exception as e:
        StatusLine.fail(f"Failed to save session data: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
