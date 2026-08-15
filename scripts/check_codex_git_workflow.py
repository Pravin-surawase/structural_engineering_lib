#!/usr/bin/env python3
"""Guard the Codex-native Git/GitHub workflow contract.

This check prevents retired lifecycle wrappers and hook enforcement from being
reintroduced. It is intentionally read-only and performs no Git mutation.
"""

from __future__ import annotations

import subprocess
import sys
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL = REPO_ROOT / "docs/git-automation/git-workflow-single-source.md"
GIT_STATE_AUTHORITY = REPO_ROOT / "scripts/git_state.py"
HANDOFF_RECEIPT = REPO_ROOT / "scripts/git_handoff_receipt.py"
DISPOSITION_CLASSIFIER = REPO_ROOT / "scripts/classify_branch_disposition.py"
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
DEPLOY_DOCS = REPO_ROOT / ".github/workflows/deploy-docs.yml"
GUIDANCE_INDEX = REPO_ROOT / "docs/git-automation/live-git-guidance-index.json"

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
    "scripts/cleanup_stale_branches.py",
)

HISTORICAL_MARKERS = ("historical", "archive", "legacy")


def _front_matter_status(content: str) -> str | None:
    if not content.startswith("---\n"):
        return None
    front_matter = content.split("---", 2)[1]
    match = re.search(r"^status:\s*([^\s]+)\s*$", front_matter, re.MULTILINE)
    return match.group(1).lower() if match else None


def _historical_boundary_is_explicit(path: Path, boundary: str) -> bool:
    if boundary == "archive_path":
        return "_archive" in path.parts
    content = path.read_text(encoding="utf-8", errors="replace")
    first_lines = "\n".join(content.splitlines()[:24]).lower()
    if boundary == "front_matter_status_deprecated":
        return _front_matter_status(content) == "deprecated" and any(
            marker in first_lines for marker in HISTORICAL_MARKERS
        )
    return False


def discover_guidance_surfaces(
    repo_root: Path = REPO_ROOT, index_path: Path = GUIDANCE_INDEX
) -> tuple[list[Path], list[str], dict]:
    """Resolve live guidance from the maintained index, failing on ambiguity."""
    errors: list[str] = []
    try:
        config = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], [f"live guidance index is missing or malformed: {exc}"], {}
    if config.get("schema_version") != 1:
        errors.append("live guidance index schema is unknown")

    surfaces: set[Path] = set()
    for relative in config.get("live_surfaces", []):
        path = repo_root / relative
        if path.is_file():
            surfaces.add(path)
        else:
            errors.append(f"indexed live guidance is missing: {relative}")
    for pattern in config.get("live_globs", []):
        matches = sorted(repo_root.glob(pattern))
        if not matches:
            errors.append(f"indexed live guidance glob matched nothing: {pattern}")
        surfaces.update(path for path in matches if path.is_file())

    for surface_set in config.get("indexed_surface_sets", []):
        index = repo_root / surface_set.get("index", "")
        root = repo_root / surface_set.get("root", "")
        try:
            entries = json.loads(index.read_text(encoding="utf-8")).get("files", [])
        except (OSError, json.JSONDecodeError, AttributeError) as exc:
            errors.append(f"indexed guidance set is malformed: {index}: {exc}")
            continue
        ignored = set(surface_set.get("ignore_names", []))
        historical_statuses = set(surface_set.get("historical_statuses", []))
        for entry in entries:
            name = entry.get("name") if isinstance(entry, dict) else None
            if not name or name in ignored or not name.endswith(".md"):
                continue
            path = root / name
            if not path.is_file():
                errors.append(
                    f"indexed guidance entry is missing: {path.relative_to(repo_root)}"
                )
                continue
            content = path.read_text(encoding="utf-8", errors="replace")
            status = _front_matter_status(content)
            if status in historical_statuses:
                if not _historical_boundary_is_explicit(
                    path, "front_matter_status_deprecated"
                ):
                    errors.append(
                        f"historical exclusion lacks an explicit boundary: "
                        f"{path.relative_to(repo_root)}"
                    )
                continue
            surfaces.add(path)

    for exclusion in config.get("historical_exclusions", []):
        pattern = exclusion.get("glob", "")
        boundary = exclusion.get("boundary", "")
        for path in repo_root.glob(pattern):
            if path.is_file() and not _historical_boundary_is_explicit(path, boundary):
                errors.append(
                    f"historical exclusion lacks an explicit boundary: "
                    f"{path.relative_to(repo_root)}"
                )
    return sorted(surfaces), errors, config


def check_semantic_guidance(
    repo_root: Path = REPO_ROOT, index_path: Path = GUIDANCE_INDEX
) -> list[str]:
    """Reject lifecycle contradictions across every indexed live surface."""
    surfaces, errors, config = discover_guidance_surfaces(repo_root, index_path)
    forbidden_tokens = tuple(config.get("forbidden_tokens", []))
    patterns: list[re.Pattern[str]] = []
    for raw in config.get("forbidden_command_patterns", []):
        try:
            patterns.append(re.compile(raw, re.IGNORECASE))
        except re.error as exc:
            errors.append(f"invalid semantic guidance pattern {raw!r}: {exc}")
    instruction_patterns: list[re.Pattern[str]] = []
    for raw in config.get("forbidden_instruction_patterns", []):
        try:
            instruction_patterns.append(re.compile(raw, re.IGNORECASE))
        except re.error as exc:
            errors.append(f"invalid semantic instruction pattern {raw!r}: {exc}")
    required = config.get("required_contracts", {})

    for path in surfaces:
        relative = path.relative_to(repo_root).as_posix()
        content = path.read_text(encoding="utf-8", errors="replace")
        for token in forbidden_tokens:
            if token in content:
                errors.append(f"{relative} prescribes retired lifecycle token: {token}")
        in_fence = False
        for line_number, line in enumerate(content.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_fence = not in_fence
                continue
            lowered = line.lower()
            if any(marker in lowered for marker in ("never:", "never ", "do not ")):
                continue
            for pattern in patterns:
                if pattern.search(line):
                    errors.append(
                        f"{relative}:{line_number} prescribes prohibited Git mutation: "
                        f"{line.strip()}"
                    )
            instruction_context = (
                in_fence
                or stripped.startswith(
                    ("| `git ", "- `git ", "* `git ", "`git ", "git ")
                )
                or re.search(
                    r"\b(use|run|execute|stage|restore|undo|recover)\b[^\n]*`?git\s",
                    line,
                    re.IGNORECASE,
                )
                is not None
            )
            if instruction_context:
                for pattern in instruction_patterns:
                    if pattern.search(line):
                        errors.append(
                            f"{relative}:{line_number} prescribes unsafe Git "
                            f"instruction: {stripped}"
                        )
        for phrase in required.get(relative, []):
            if phrase not in content:
                errors.append(f"{relative} is missing semantic contract: {phrase}")
    return errors


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

    if not HANDOFF_RECEIPT.exists():
        errors.append("task-to-Git handoff receipt contract is missing")
    else:
        source = HANDOFF_RECEIPT.read_text(encoding="utf-8")
        for token in (
            "collect_repository_state",
            "receipt_sha256",
            "NOT_CHECKED",
            "UNKNOWN",
            "is_git_retention_evidence",
            "REVIEWED_HEAD_MISMATCH",
            "SQUASH_TREE_EQUIVALENCE_UNKNOWN",
        ):
            if token not in source:
                errors.append(f"handoff receipt is missing required contract: {token}")
        if "subprocess" in source or "ls-remote" in source:
            errors.append(
                "handoff receipt must not read Git or remote state independently"
            )

    if not DISPOSITION_CLASSIFIER.exists():
        errors.append(
            "inspection-only classifier is missing: "
            "scripts/classify_branch_disposition.py"
        )
    else:
        source = DISPOSITION_CLASSIFIER.read_text(encoding="utf-8")
        for token in (
            "GIT_OPTIONAL_LOCKS",
            "NOT_CHECKED",
            "HOLD_ATTACHED_OR_DIRTY",
            "HOLD_UNKNOWN_OWNER",
            "HOLD_OPEN_OR_DEPENDENT_PR",
            "HOLD_UNIQUE_OR_UNPUBLISHED_WORK",
            "HOLD_EVIDENCE_RETENTION",
            "PATCH_EQUIVALENT_REVIEW_REQUIRED",
            "RETIREMENT_READY_PENDING_APPROVAL",
            "SEPARATE_EXACT_TARGET_APPROVAL_REQUIRED",
        ):
            if token not in source:
                errors.append(
                    f"branch disposition classifier is missing contract: {token}"
                )
        help_result = subprocess.run(
            [sys.executable, str(DISPOSITION_CLASSIFIER), "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if help_result.returncode != 0:
            errors.append("branch disposition classifier help is not executable")
        for action_flag in ("--delete", "--execute", "--apply"):
            if action_flag in help_result.stdout:
                errors.append(
                    f"branch disposition classifier exposes action flag: {action_flag}"
                )

    errors.extend(check_semantic_guidance())

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
            "docs:",
            "'scripts/**'",
            "'docs/**'",
            "control-plane-validation:",
            "documentation-validation:",
            "needs.changes.outputs.control_plane == 'true'",
            "needs.changes.outputs.docs == 'true'",
            "Python/tests/test_git_state.py",
            "Python/tests/test_git_handoff_receipt.py",
            "Python/tests/test_git_guidance_semantics.py",
            "Python/tests/test_branch_disposition.py",
            "Python/tests/test_session_automation.py",
            "Python/tests/test_session_store.py",
            "Python/tests/test_pipeline_state.py",
            "Python/tests/test_agent_governance_automation.py",
            "Python/tests/test_ci_workflow_contract.py",
            "CONTROL_PLANE_RESULT:",
            "DOCS_RESULT:",
            "require_component 'Control Plane Validation'",
            "require_component 'Documentation Validation'",
        ):
            if token not in workflow:
                errors.append(f"required PR Gate routing is missing: {token}")
        expected_concurrency = (
            "group: ${{ github.workflow }}-"
            "${{ github.event.pull_request.number || github.run_id }}"
        )
        if expected_concurrency not in workflow:
            errors.append("PR validation concurrency is not scoped per pull request")
        focused_marker = (
            "- name: Validate Git, intake, session, and governance controls"
        )
        if focused_marker in workflow:
            focused_step = workflow.partition(focused_marker)[2].partition(
                "\n      - name:"
            )[0]
            runtime_binding = 'STRUCTURAL_LIB_PYTHON="$(command -v python)"'
            if runtime_binding not in focused_step:
                errors.append(
                    "control-plane CI tests do not bind the setup-python interpreter"
                )

    if not DEPLOY_DOCS.exists():
        errors.append("post-merge documentation workflow is missing")
    else:
        deploy_docs = DEPLOY_DOCS.read_text(encoding="utf-8")
        trigger_block = deploy_docs.partition("\non:\n")[2].partition("\npermissions:")[
            0
        ]
        if "pull_request:" in trigger_block:
            errors.append(
                "documentation PR validation must run inside required PR Gate"
            )
        if "group: ${{ github.workflow }}-${{ github.ref }}" not in deploy_docs:
            errors.append("post-merge documentation concurrency is not scoped per ref")
        if "group: deploy-docs" in deploy_docs:
            errors.append("global documentation concurrency group is still active")

    if errors:
        print("Codex-native Git workflow check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Codex-native Git workflow check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
