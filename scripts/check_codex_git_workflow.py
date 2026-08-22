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
HISTORICAL_CONTEXT = re.compile(
    r"\b(?:historical|archived|deprecated|legacy|old workflow|"
    r"incident (?:record|evidence|narrative))\b",
    re.IGNORECASE,
)
HISTORICAL_NARRATION = re.compile(
    r"\b(?:says?|said|records?|mentions?|describes?|documents?|was|were|used|"
    r"ran|during)\b",
    re.IGNORECASE,
)
IMPERATIVE_LIFECYCLE_VERBS = re.compile(
    r"\b(?:use|run|execute|invoke|issue|perform|stage|restore|undo|recover|"
    r"amend|cherry-pick|create|checkout|switch|reset|commit|push|pull|revert|"
    r"merge|rebase|stash|clean|prune|delete|remove|force|replay|apply|move|"
    r"branch|fetch)\b",
    re.IGNORECASE,
)
CLAUSE_BOUNDARY = re.compile(
    r"(?:[.;!?]\s+|\b(?:but|however|then|instead|nevertheless|yet)\b[:,]?\s*)",
    re.IGNORECASE,
)
GUIDANCE_CONTEXT_BOUNDARY = re.compile(r"[.;!?](?:\s+|$)")
NEGATING_DIRECTIVE = re.compile(
    r"(?<![A-Za-z0-9])(?:never|do not|don't|must not|should not|shall not|"
    r"cannot|can't)\b"
    r"|\b(?:forbidden|prohibited)\s*:\s*$",
    re.IGNORECASE,
)
DIRECT_ACTION = re.compile(
    r"\b(?:use|run|execute|invoke|issue|perform|stage|restore|undo|"
    r"recover|amend|cherry-pick|create|checkout|switch|reset|commit|push|"
    r"pull|revert|merge|rebase|stash|clean|prune|delete|remove|force|replay|"
    r"apply|move|fetch)\b",
    re.IGNORECASE,
)
DIRECTIVE_PUNCTUATION_ONLY = re.compile(r"^[\s`*_:~—–\-()\[\]]*$")
SUFFIX_EXACT_OBJECT_LEAD = re.compile(
    r"^[^.;!?]*[—–][\s`*_~()\[\]-]*$",
    re.IGNORECASE,
)
INNER_ACTION_NEGATION = re.compile(r"\bnot\s+to[\s`*_~]*$", re.IGNORECASE)
AVOID_GOVERNOR = re.compile(r"\bavoid\b", re.IGNORECASE)
EXACT_OBJECT_SUFFIX = re.compile(
    r"^[\s`*_~]*(?:(?:this|that)\s+"
    r"(?:command|form|expression|example))?[\s`*_~.!,:;()\[\]-]*$",
    re.IGNORECASE,
)
NEGATING_PREDICATE = re.compile(
    r"\b(?:is|are)\s+(?:strictly\s+)?(?:forbidden|prohibited|not allowed)\b"
    r"|\b(?:must|should|shall)\s+not\s+be\s+"
    r"(?:used|run|executed)\b",
    re.IGNORECASE,
)


def _local_clause(line: str, start: int, end: int) -> tuple[str, str]:
    """Return text locally governing a command, excluding prior/later clauses."""
    before = line[:start]
    after = line[end:]
    prior = list(CLAUSE_BOUNDARY.finditer(before))
    following = CLAUSE_BOUNDARY.search(after)
    return (
        before[prior[-1].end() :] if prior else before,
        after[: following.start()] if following else after,
    )


def _is_governing_prohibition(line: str, start: int, end: int) -> bool:
    """True only when the nearest action prohibits this Git expression."""
    before, after = _local_clause(line, start, end)
    actions = list(DIRECT_ACTION.finditer(before))
    if actions:
        action = actions[-1]
        action_prefix = before[: action.start()]
        if INNER_ACTION_NEGATION.search(action_prefix) is not None:
            return True
        directives = list(NEGATING_DIRECTIVE.finditer(action_prefix))
        if directives and DIRECTIVE_PUNCTUATION_ONLY.fullmatch(
            action_prefix[directives[-1].end() :]
        ):
            return True

    avoidances = list(AVOID_GOVERNOR.finditer(before))
    if avoidances and (not actions or avoidances[-1].start() > actions[-1].end()):
        avoid = avoidances[-1]
        directives = list(NEGATING_DIRECTIVE.finditer(before[: avoid.start()]))
        directly_negated = directives and DIRECTIVE_PUNCTUATION_ONLY.fullmatch(
            before[directives[-1].end() : avoid.start()]
        )
        if not directly_negated:
            return True

    directives = list(NEGATING_DIRECTIVE.finditer(before))
    if directives and DIRECTIVE_PUNCTUATION_ONLY.fullmatch(
        before[directives[-1].end() :]
    ):
        return True

    suffix_directives = list(NEGATING_DIRECTIVE.finditer(after))
    if suffix_directives:
        directive = suffix_directives[0]
        suffix_actions = list(DIRECT_ACTION.finditer(after[directive.end() :]))
        if suffix_actions:
            action = suffix_actions[0]
            action_start = directive.end() + action.start()
            action_end = directive.end() + action.end()
            suffix_lead = after[: directive.start()]
            if (
                (
                    DIRECTIVE_PUNCTUATION_ONLY.fullmatch(suffix_lead)
                    or SUFFIX_EXACT_OBJECT_LEAD.fullmatch(suffix_lead)
                )
                and DIRECTIVE_PUNCTUATION_ONLY.fullmatch(
                    after[directive.end() : action_start]
                )
                and EXACT_OBJECT_SUFFIX.fullmatch(after[action_end:])
            ):
                return True
    return NEGATING_PREDICATE.search(after) is not None


def _is_historical_narration(line: str, start: int) -> bool:
    """Recognize explicit past evidence, not a historical-looking directive."""
    prefix = line[:start]
    if HISTORICAL_CONTEXT.search(line) is None:
        return False
    if HISTORICAL_NARRATION.search(line) is None:
        return False
    prior = list(CLAUSE_BOUNDARY.finditer(prefix))
    local_prefix = prefix[prior[-1].end() :] if prior else prefix
    return IMPERATIVE_LIFECYCLE_VERBS.search(local_prefix) is None


def _unsafe_match_is_instruction(line: str, match: re.Match[str]) -> bool:
    """Fail closed unless the command is locally prohibited or historical."""
    return _instruction_span_is_unsafe(line, match.start(), match.end(), match.group(0))


def _instruction_span_is_unsafe(line: str, start: int, end: int, matched: str) -> bool:
    """Classify one action-starting span with the shared semantic grammar."""
    directive = NEGATING_DIRECTIVE.search(matched)
    if (
        directive is not None
        and DIRECTIVE_PUNCTUATION_ONLY.fullmatch(matched[: directive.start()])
        and re.search(r"\bwithout\b", matched[directive.end() :], re.IGNORECASE) is None
    ):
        action = DIRECT_ACTION.search(matched, directive.end())
        if action is not None:
            start += action.start()
    return not _is_governing_prohibition(line, start, end) and not (
        _is_historical_narration(line, start)
    )


def _clause_spans(line: str) -> list[tuple[int, int]]:
    """Return sentence/semicolon-local spans without crossing context boundaries."""
    spans: list[tuple[int, int]] = []
    start = 0
    for boundary in GUIDANCE_CONTEXT_BOUNDARY.finditer(line):
        if boundary.start() > start:
            spans.append((start, boundary.start()))
        start = boundary.end()
    if start < len(line):
        spans.append((start, len(line)))
    return spans


def _structured_instruction_errors(
    line: str,
    action_pattern: re.Pattern[str],
    context_pattern: re.Pattern[str],
    standalone_patterns: tuple[re.Pattern[str], ...],
) -> list[tuple[int, int]]:
    """Match one data-driven action rule within its own lexical context clause."""
    errors: list[tuple[int, int]] = []
    for clause_start, clause_end in _clause_spans(line):
        clause = line[clause_start:clause_end]
        has_context = context_pattern.search(clause) is not None
        is_standalone = any(
            pattern.fullmatch(clause.strip()) is not None
            for pattern in standalone_patterns
        )
        if not has_context and not is_standalone:
            continue
        for match in action_pattern.finditer(clause):
            start = clause_start + match.start()
            end = clause_start + match.end()
            if _instruction_span_is_unsafe(line, start, end, match.group(0)):
                errors.append((start, end))
    return errors


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

    if config.get("indexed_surface_sets"):
        errors.append("indexed guidance sets are retired; use live_surface_sets")

    for surface_set in config.get("live_surface_sets", []):
        root = repo_root / surface_set.get("root", "")
        pattern = surface_set.get("glob", "*.md")
        if not root.is_dir():
            errors.append(f"live guidance root is missing: {root}")
            continue
        matches = sorted(path for path in root.glob(pattern) if path.is_file())
        if not matches:
            errors.append(
                f"live guidance set matched nothing: "
                f"{root.relative_to(repo_root)}/{pattern}"
            )
            continue
        ignored = set(surface_set.get("ignore_names", []))
        historical_statuses = set(surface_set.get("historical_statuses", []))
        for path in matches:
            if path.name in ignored:
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
    structured_instruction_rules: list[
        tuple[re.Pattern[str], re.Pattern[str], tuple[re.Pattern[str], ...]]
    ] = []
    for raw in config.get("forbidden_instruction_patterns", []):
        if isinstance(raw, dict):
            if raw.get("kind") != "clause_action":
                errors.append(f"invalid semantic instruction rule kind: {raw!r}")
                continue
            try:
                structured_instruction_rules.append(
                    (
                        re.compile(raw["action_pattern"], re.IGNORECASE),
                        re.compile(raw["context_pattern"], re.IGNORECASE),
                        tuple(
                            re.compile(pattern, re.IGNORECASE)
                            for pattern in raw["standalone_clause_patterns"]
                        ),
                    )
                )
            except (KeyError, TypeError, re.error) as exc:
                errors.append(f"invalid semantic instruction rule {raw!r}: {exc}")
            continue
        if not isinstance(raw, str):
            errors.append(f"invalid semantic instruction pattern: {raw!r}")
            continue
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
            for pattern in patterns:
                match = pattern.search(line)
                if match and _unsafe_match_is_instruction(line, match):
                    errors.append(
                        f"{relative}:{line_number} prescribes prohibited Git mutation: "
                        f"{line.strip()}"
                    )
            for pattern in instruction_patterns:
                match = pattern.search(line)
                if match and _unsafe_match_is_instruction(line, match):
                    errors.append(
                        f"{relative}:{line_number} prescribes unsafe Git "
                        f"instruction: {stripped}"
                    )
            for action, context, standalone in structured_instruction_rules:
                if _structured_instruction_errors(line, action, context, standalone):
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
