#!/usr/bin/env python3
"""Check that git automation scripts stay within line budget (TASK-910).

Budget: 2500 total lines across all git scripts.
Per-script limit: 700 lines.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Git automation scripts to track
GIT_SCRIPTS = [
    "scripts/safe_push.sh",
    "scripts/ai_commit.sh",
    "scripts/finish_task_pr.sh",
    "scripts/create_task_pr.sh",
    "scripts/recover_git_state.sh",
    "scripts/validate_git_state.sh",
    "scripts/git-hooks/pre-push",
    "scripts/git-hooks/pre-commit",
]

TOTAL_BUDGET = 2500
PER_SCRIPT_LIMIT = 700


def main() -> int:
    errors = []
    total_lines = 0

    for script_path in GIT_SCRIPTS:
        full_path = REPO_ROOT / script_path
        if not full_path.exists():
            continue
        line_count = len(full_path.read_text(encoding="utf-8").splitlines())
        total_lines += line_count

        if line_count > PER_SCRIPT_LIMIT:
            errors.append(
                f"  {script_path}: {line_count} lines (limit: {PER_SCRIPT_LIMIT})"
            )

    if total_lines > TOTAL_BUDGET:
        errors.insert(
            0,
            f"  TOTAL: {total_lines} lines (budget: {TOTAL_BUDGET})",
        )

    if errors:
        print("Git script line budget exceeded:")
        for err in errors:
            print(err)
        return 1

    print(f"Git script line budget OK: {total_lines}/{TOTAL_BUDGET} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
