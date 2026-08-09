#!/usr/bin/env python3
"""Guard the Codex-native Git/GitHub workflow contract.

This check prevents retired lifecycle wrappers and hook enforcement from being
reintroduced. It is intentionally read-only and performs no Git mutation.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL = REPO_ROOT / "docs/git-automation/git-workflow-single-source.md"

RETIRED_PATHS = (
    "scripts/ai_commit.sh",
    "scripts/safe_push.sh",
    "scripts/recover_git_state.sh",
    "scripts/finish_task_pr.sh",
    "scripts/create_task_pr.sh",
    "scripts/should_use_pr.sh",
    "scripts/install_git_hooks.sh",
    "scripts/git-hooks/pre-commit",
    "scripts/git-hooks/pre-push",
    "scripts/git-hooks/commit-msg",
)

LIVE_FILES_WITHOUT_WRAPPER_CALLS = (
    "AGENTS.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
    "run.sh",
    "scripts/agent_start.sh",
    "agents/agent-9/KNOWLEDGE_BASE.md",
    "agents/agent-9/RESEARCH_PLAN.md",
    "agents/agent-9/research/AGENT_9_CONSTRAINTS.md",
    "agents/agent-9/workflows/LINK_GOVERNANCE.md",
    "agents/roles/GOVERNANCE.md",
    "docs/guidelines/migration-workflow-guide.md",
    "docs/guidelines/folder-cleanup-workflow.md",
    "docs/guidelines/file-operations-safety-guide.md",
)


def main() -> int:
    errors: list[str] = []

    for relative in RETIRED_PATHS:
        if (REPO_ROOT / relative).exists():
            errors.append(f"retired Git lifecycle path exists: {relative}")

    hooks_path = subprocess.run(
        ["git", "config", "--get", "core.hooksPath"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    if hooks_path.endswith("scripts/git-hooks"):
        errors.append(f"retired core.hooksPath is active: {hooks_path}")

    if not CANONICAL.exists():
        errors.append("canonical Codex-native workflow is missing")
    else:
        content = CANONICAL.read_text(encoding="utf-8")
        required_phrases = ("Codex", "connected GitHub", "explicit user confirmation")
        for phrase in required_phrases:
            if phrase not in content:
                errors.append(
                    f"canonical workflow is missing required phrase: {phrase}"
                )

    retired_names = tuple(Path(path).name for path in RETIRED_PATHS[:7])
    for relative in LIVE_FILES_WITHOUT_WRAPPER_CALLS:
        path = REPO_ROOT / relative
        if not path.exists():
            errors.append(f"required live instruction file is missing: {relative}")
            continue
        content = path.read_text(encoding="utf-8")
        for name in retired_names:
            if name in content:
                errors.append(f"{relative} still invokes or prescribes retired {name}")

    if errors:
        print("Codex-native Git workflow check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Codex-native Git workflow check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
