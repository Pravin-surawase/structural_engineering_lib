"""Semantic live-guidance discovery and coherence regressions."""

from __future__ import annotations

import importlib
import json
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

checker = importlib.import_module("scripts.check_codex_git_workflow")
REPO_ROOT = Path(__file__).resolve().parents[2]


def _write_index(root: Path, **overrides) -> Path:
    payload = {
        "schema_version": 1,
        "canonical": "guide.md",
        "live_surfaces": ["guide.md"],
        "live_globs": [],
        "indexed_surface_sets": [],
        "historical_exclusions": [],
        "forbidden_tokens": ["ai_commit.sh", "--finish"],
        "forbidden_command_patterns": [r"(^|[` ])git\s+reset\s+--hard(?:[` ]|$)"],
        "forbidden_instruction_patterns": [
            r"(^|[` ])git\s+add\s+(?:\.|-A|--all)(?:[` ]|$)",
            r"(^|[` ])git\s+filter-branch(?:[` ]|$)",
            r"(^|[` ])git\s+checkout\b[^\n]*(?:HEAD|--)\b",
            r"(^|[` ])git\s+reset(?:\s|`|$)",
            r"(^|[` ])git\s+commit\b[^\n]*--amend(?:[` ]|$)",
            r"(^|[` ])git\s+cherry-pick(?:\s|`|$)",
            r"(^|[` ])git\s+checkout\s+-b(?:\s|`|$)",
            r"(^|[` ])git\s+switch\s+-c\s+(?!codex/)",
            (
                r"(?:(?<![A-Za-z0-9])(?:do not|don't|never)\s+push\b"
                r"[^\n.;!?]*\bwithout\s+pull(?:ing)?\s+first\b|"
                r"(?=[^\n]*(?:git|PR|branch|remote|repository|upstream|commit))"
                r"[^\n.;!?]*\bpull(?:\s+(?:the\s+)?(?:PR\s+)?branch)?"
                r"\s+before\s+(?:you\s+)?push(?:ing)?\b|"
                r"(?=[^\n]*(?:git|PR|branch|remote|repository|upstream|commit))"
                r"[^\n.;!?]*\bpull\s+first\b[^\n.;!?]{0,40}"
                r"\b(?:then\s+)?push(?:ing)?\b|"
                r"^\s*(?:always\s+)?pull\s+before\s+you\s+push"
                r"(?:\s+to\s+(?:the\s+)?PR\s+branch)?[.!]?\s*$|"
                r"^\s*pull\s+first\s*,?\s*then\s+push"
                r"(?:\s+the\s+change)?[.!]?\s*$|"
                r"^\s*before\s+you\s+push\s*,\s*pull\s+first[.!]?\s*$)"
            ),
        ],
        "required_contracts": {},
    }
    payload.update(overrides)
    path = root / "live-index.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_live_semantic_contradiction_fails_and_coherent_guidance_passes(tmp_path):
    guide = tmp_path / "guide.md"
    guide.write_text("Use ./scripts/ai_commit.sh --finish.\n", encoding="utf-8")
    index = _write_index(tmp_path)

    errors = checker.check_semantic_guidance(tmp_path, index)

    assert any("ai_commit.sh" in error for error in errors)
    assert any("--finish" in error for error in errors)

    guide.write_text(
        "Use scripts/git_state.py; NOT_CHECKED and UNKNOWN are holds.\n",
        encoding="utf-8",
    )
    assert checker.check_semantic_guidance(tmp_path, index) == []


def test_indexed_deprecated_history_is_excluded_only_with_explicit_boundary(
    tmp_path: Path,
):
    guides = tmp_path / "guides"
    guides.mkdir()
    current = guides / "current.md"
    current.write_text("Current coherent guidance.\n", encoding="utf-8")
    old = guides / "old.md"
    old.write_text(
        """---
status: deprecated
---
> Historical only. Use ./scripts/ai_commit.sh --finish in the old workflow.
""",
        encoding="utf-8",
    )
    generated = guides / "index.json"
    generated.write_text(
        json.dumps({"files": [{"name": "current.md"}, {"name": "old.md"}]}),
        encoding="utf-8",
    )
    index = _write_index(
        tmp_path,
        live_surfaces=[],
        indexed_surface_sets=[
            {
                "index": "guides/index.json",
                "root": "guides",
                "historical_statuses": ["deprecated"],
                "ignore_names": [],
            }
        ],
    )

    surfaces, errors, _config = checker.discover_guidance_surfaces(tmp_path, index)

    assert errors == []
    assert surfaces == [current]

    old.write_text(
        """---
status: deprecated
---
Use ./scripts/ai_commit.sh --finish.
""",
        encoding="utf-8",
    )
    _surfaces, errors, _config = checker.discover_guidance_surfaces(tmp_path, index)
    assert any("lacks an explicit boundary" in error for error in errors)


def test_archive_path_is_explicitly_excluded_from_live_authority(tmp_path: Path):
    guide = tmp_path / "guide.md"
    guide.write_text("Current coherent guidance.\n", encoding="utf-8")
    archive = tmp_path / "docs" / "_archive"
    archive.mkdir(parents=True)
    (archive / "old.md").write_text(
        "Use ./scripts/ai_commit.sh --finish.\n", encoding="utf-8"
    )
    index = _write_index(
        tmp_path,
        historical_exclusions=[
            {"glob": "docs/_archive/**", "boundary": "archive_path"}
        ],
    )

    assert checker.check_semantic_guidance(tmp_path, index) == []


def test_live_aliases_route_to_receipt_and_not_retired_mutation():
    result = subprocess.run(
        [
            str(REPO_ROOT / "scripts/python_runtime.sh"),
            "scripts/find_automation.py",
            "task git handoff receipt",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    assert "git_handoff_receipt.py" in result.stdout
    assert "ai_commit.sh" not in result.stdout
    assert "cleanup_stale_branches.py" not in result.stdout


@pytest.mark.parametrize(
    "instruction",
    [
        "| `git add .` | Stage everything |",
        "```bash\ngit add -A\n```",
        "Use `git filter-branch` to remove the secret.",
        "`git checkout HEAD -- path/to/file`",
        "```bash\ngit reset --soft HEAD~1\n```",
        "```bash\ngit commit --amend --no-edit\n```",
        "Recover the work with `git cherry-pick abc123`.",
        "```bash\ngit checkout -b recovery-branch abc123\n```",
        "Use `git switch -c recovery-branch` to preserve the commit.",
        "Amend the commit with `git commit --amend --no-edit`.",
        "Cherry-pick the recovery using `git cherry-pick abc123`.",
        "Create a recovery branch with `git checkout -b recovery abc123`.",
        "Replay the change via `git cherry-pick abc123`.",
        (
            "Do not delete the worktree; then amend the commit with "
            "`git commit --amend --no-edit`."
        ),
        (
            "Never ignore ownership. Create a recovery branch with "
            "`git checkout -b recovery abc123`."
        ),
        "Do not forget to run git reset --hard.",
        "Never hesitate to recover with git cherry-pick abc123.",
        "Never fail to create a branch with git checkout -b recovery.",
        "Do not fail to run git reset --soft HEAD~1.",
        "Never remember to recover with git cherry-pick abc123.",
        "Do not omit to create a branch with git checkout -b recovery.",
        "`git reset --hard` — do not forget to run this command.",
        "`git cherry-pick abc123` — never hesitate to use this form.",
        "`git reset --hard`; do not run tests.",
        "Do not avoid git reset --hard.",
    ],
)
def test_live_indexed_unsafe_instruction_context_fails(instruction, tmp_path):
    guide = tmp_path / "guide.md"
    guide.write_text(instruction + "\n", encoding="utf-8")
    index = _write_index(tmp_path)

    errors = checker.check_semantic_guidance(tmp_path, index)

    assert any("unsafe Git instruction" in error for error in errors)


@pytest.mark.parametrize(
    "prohibition",
    [
        "Never use `git commit --amend --no-edit`.",
        "Never use git reset --hard.",
        "Do not run git reset --soft HEAD~1.",
        "NEVER: git push --force-with-lease.",
        "Do not recover with `git cherry-pick abc123`.",
        "`git checkout -b recovery abc123` is forbidden.",
        "Using `git switch -c recovery` is prohibited.",
        "`git reset --hard` — **do not run this command**.",
        "`git cherry-pick abc123` — _never use this form_.",
        "Never forget not to run git reset --hard.",
        "Do not fail to avoid git cherry-pick abc123.",
        "Do not fail to avoid running git reset --hard.",
        "Avoid using git reset --hard.",
        "Do not run git reset --hard; however, preserve the worktree.",
    ],
)
def test_genuine_governing_prohibition_is_safe(prohibition, tmp_path):
    guide = tmp_path / "guide.md"
    guide.write_text(prohibition + "\n", encoding="utf-8")
    index = _write_index(tmp_path)

    assert checker.check_semantic_guidance(tmp_path, index) == []


@pytest.mark.parametrize(
    "instruction",
    [
        "Pull before pushing to the PR branch.",
        "Pull the PR branch before pushing.",
        "Pull before you push.",
        "Always pull before you push to the PR branch.",
        "Pull first, then push the change.",
        "Before you push, pull first.",
        "For the PR branch, pull first, then push the change.",
        "Don't push to the PR branch without pulling first.",
    ],
)
def test_data_driven_omitted_git_pull_before_push_instruction_fails(
    instruction, tmp_path
):
    guide = tmp_path / "guide.md"
    guide.write_text(instruction + "\n", encoding="utf-8")
    live_config = json.loads(
        (REPO_ROOT / "docs/git-automation/live-git-guidance-index.json").read_text(
            encoding="utf-8"
        )
    )
    pull_patterns = [
        pattern
        for pattern in live_config["forbidden_instruction_patterns"]
        if "pull" in pattern and "push" in pattern
    ]
    assert len(pull_patterns) == 1
    index = _write_index(tmp_path, forbidden_instruction_patterns=pull_patterns)

    errors = checker.check_semantic_guidance(tmp_path, index)

    assert any("unsafe Git instruction" in error for error in errors)


@pytest.mark.parametrize(
    "safe_context",
    [
        "Do not pull before pushing; inspect branch and upstream first.",
        "Never pull first; inspect with git_state.py.",
        "Historical incident evidence says the old guide required pull before pushing.",
        "Deprecated guidance says pull first, then push.",
        "The lead horse should pull first in the team.",
        "Pull first aid supplies from the cabinet.",
        "For the sled exercise, pull first, then push the load.",
        "The actuator will pull before you push the test lever.",
        "Do not pull before you push; inspect branch and upstream first.",
        "Historical guidance said pull before you push.",
    ],
)
def test_omitted_git_pull_pattern_respects_prohibition_and_history(
    safe_context, tmp_path
):
    guide = tmp_path / "guide.md"
    guide.write_text(safe_context + "\n", encoding="utf-8")
    index = _write_index(tmp_path)

    assert checker.check_semantic_guidance(tmp_path, index) == []


@pytest.mark.parametrize(
    "historical",
    [
        "Historical incident evidence says git reset --soft was used in 2024.",
        "The 2024 incident record says git commit --amend was used.",
        "Historical evidence records git cherry-pick during the old recovery.",
        "The archived incident narrative mentions git checkout -b recovery-old.",
        "Historical evidence records that operators were told not to run git reset.",
    ],
)
def test_harmless_historical_prose_is_not_treated_as_live_instruction(
    historical, tmp_path
):
    guide = tmp_path / "guide.md"
    guide.write_text(
        historical + "\n",
        encoding="utf-8",
    )
    index = _write_index(tmp_path)

    assert checker.check_semantic_guidance(tmp_path, index) == []
