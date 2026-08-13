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
GIT_STATE_AUTHORITY = REPO_ROOT / "scripts/git_state.py"
GIT_STATE_CONSUMERS = (
    "scripts/prompt_router.py",
    "scripts/session.py",
    "scripts/check_all.py",
)
GIT_STATE_COMPATIBILITY = (
    "scripts/validate_git_state.sh",
    "scripts/check_unfinished_merge.sh",
    "scripts/check_not_main.sh",
)
FAST_CHECKS = REPO_ROOT / ".github/workflows/fast-checks.yml"

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

    if not GIT_STATE_AUTHORITY.exists():
        errors.append("read-only Git state authority is missing: scripts/git_state.py")
    else:
        source = GIT_STATE_AUTHORITY.read_text(encoding="utf-8")
        for token in (
            "GIT_OPTIONAL_LOCKS",
            "--porcelain=v2",
            "--git-common-dir",
            "--git-path",
            "--left-right",
            "NOT_CHECKED",
            "HOLD_UNKNOWN",
        ):
            if token not in source:
                errors.append(
                    f"Git state authority is missing required control: {token}"
                )
        if "ls-remote" in source:
            errors.append("Git state authority must not contact a remote")

    for relative in GIT_STATE_CONSUMERS:
        path = REPO_ROOT / relative
        if not path.exists():
            errors.append(f"Git state consumer is missing: {relative}")
        elif "git_state" not in path.read_text(encoding="utf-8"):
            errors.append(f"Git state consumer does not use the authority: {relative}")

    for relative in GIT_STATE_COMPATIBILITY:
        path = REPO_ROOT / relative
        if not path.exists():
            errors.append(f"Git state compatibility entrypoint is missing: {relative}")
            continue
        content = path.read_text(encoding="utf-8")
        if "git_state.py" not in content:
            errors.append(
                f"Git compatibility entrypoint bypasses the authority: {relative}"
            )
        for retired_semantic in (
            ".git/MERGE_HEAD",
            "git status",
            "git rev-list",
            "git ls-remote",
        ):
            if retired_semantic in content:
                errors.append(
                    f"Git compatibility entrypoint retains independent semantics: "
                    f"{relative} ({retired_semantic})"
                )

    pre_commit = REPO_ROOT / ".pre-commit-config.yaml"
    if pre_commit.exists():
        pre_commit_text = pre_commit.read_text(encoding="utf-8")
        expected_completion_guard = (
            "bash scripts/check_unfinished_merge.sh --allow-operation-completion"
        )
        if expected_completion_guard not in pre_commit_text:
            errors.append(
                "pre-commit operation guard is missing the explicit completion mode"
            )

    if not FAST_CHECKS.exists():
        errors.append("required PR validation workflow is missing")
    else:
        workflow = FAST_CHECKS.read_text(encoding="utf-8")
        for token in (
            "control_plane:",
            "'scripts/git_state.py'",
            "needs.changes.outputs.control_plane == 'true'",
            "Python/tests/test_git_state.py",
            "Python/tests/test_session_automation.py",
        ):
            if token not in workflow:
                errors.append(f"control-plane CI routing is missing: {token}")

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
