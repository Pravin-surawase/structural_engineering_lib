#!/usr/bin/env python3
"""
Cleanup stale remote branches.

This script identifies and optionally deletes remote branches that:
1. Have been merged into main
2. Are older than 30 days
3. Match task branch patterns (task/TASK-*)

Usage:
    python scripts/cleanup_stale_branches.py           # Dry run
    python scripts/cleanup_stale_branches.py --delete  # Actually delete

Example output:
    Found 15 stale branches:
      - task/TASK-085 (merged, 45 days old)
      - task/TASK-AI-FIX (merged, 30 days old)

    Run with --delete to remove these branches.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timedelta


def run_git(args: list[str]) -> str:
    """Run git command and return output."""
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def get_remote_branches() -> list[str]:
    """Get list of remote branches (excluding HEAD and main)."""
    output = run_git(["branch", "-r"])
    branches = []
    for line in output.split("\n"):
        branch = line.strip()
        if branch and not branch.endswith("/HEAD") and not branch.endswith("/main"):
            branches.append(branch)
    return branches


def is_merged(branch: str) -> bool:
    """Check if branch is merged into main."""
    # Get commits in branch that aren't in main
    output = run_git([
        "log",
        "--oneline",
        f"origin/main..{branch}",
        "--",
    ])
    return len(output.strip()) == 0


def get_branch_age_days(branch: str) -> int:
    """Get age of last commit on branch in days."""
    output = run_git([
        "log",
        "-1",
        "--format=%ci",
        branch,
    ])
    if not output:
        return 999  # Very old if we can't get date

    try:
        # Parse date like "2026-01-15 10:30:00 +0530"
        date_str = output.split()[0]
        commit_date = datetime.strptime(date_str, "%Y-%m-%d")
        age = datetime.now() - commit_date
        return age.days
    except Exception:
        return 999


def is_task_branch(branch: str) -> bool:
    """Check if branch matches task pattern."""
    patterns = [
        "task/TASK-",
        "task/FIX-",
        "task/P8-",
        "feature/",
        "copilot-worktree-",
        "dependabot/",
    ]
    return any(pattern in branch for pattern in patterns)


def cleanup_branches(delete: bool = False, min_age_days: int = 30) -> None:
    """Find and optionally delete stale branches."""
    print("Fetching remote branches...")
    run_git(["fetch", "--prune"])

    branches = get_remote_branches()
    print(f"Found {len(branches)} remote branches (excluding main)\n")

    stale_branches = []

    for branch in branches:
        merged = is_merged(branch)
        age = get_branch_age_days(branch)
        is_task = is_task_branch(branch)

        # Consider stale if:
        # 1. Merged and older than 7 days, OR
        # 2. Task branch older than min_age_days, OR
        # 3. Any branch older than 90 days
        is_stale = (
            (merged and age > 7) or
            (is_task and age > min_age_days) or
            (age > 90)
        )

        if is_stale:
            reason = []
            if merged:
                reason.append("merged")
            if age > 0:
                reason.append(f"{age} days old")
            stale_branches.append((branch, ", ".join(reason)))

    if not stale_branches:
        print("✅ No stale branches found!")
        return

    print(f"Found {len(stale_branches)} stale branches:\n")
    for branch, reason in stale_branches:
        remote_name = branch.replace("remotes/origin/", "origin/")
        print(f"  - {branch} ({reason})")

    if delete:
        print("\n🗑️  Deleting stale branches...")
        for branch, _ in stale_branches:
            # Extract branch name without remotes/origin/
            branch_name = branch.replace("remotes/origin/", "")
            print(f"  Deleting {branch_name}...", end=" ")
            try:
                result = subprocess.run(
                    ["git", "push", "origin", "--delete", branch_name],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    print("✅")
                else:
                    print(f"❌ {result.stderr.strip()}")
            except Exception as e:
                print(f"❌ {e}")

        print(f"\n✅ Cleaned up {len(stale_branches)} branches")
    else:
        print(f"\n💡 Run with --delete to remove these branches:")
        print(f"   python scripts/cleanup_stale_branches.py --delete")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cleanup stale remote branches"
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Actually delete the stale branches",
    )
    parser.add_argument(
        "--min-age",
        type=int,
        default=30,
        help="Minimum age in days for task branches (default: 30)",
    )

    args = parser.parse_args()
    cleanup_branches(delete=args.delete, min_age_days=args.min_age)


if __name__ == "__main__":
    main()
