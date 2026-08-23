#!/usr/bin/env python3
"""Validate cross-platform instruction projections and semantic contracts.

When to use: after changing any root, platform, role, prompt, skill, or scoped
instruction file. Similarity is diagnostic only: maintained scoped-rule bodies
must match exactly and the shared safety/session contract must pass.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

PAIRS = {
    "docs": ("docs.instructions.md", "docs.md"),
    "fastapi": ("fastapi.instructions.md", "fastapi.md"),
    "python-core": ("python-core.instructions.md", "python-core.md"),
    "react": ("react.instructions.md", "react.md"),
}

DIRECT_RUNTIME = re.compile(r"\.venv/bin/(?:python|pytest)")
STALE_PHRASES = (
    "final explicit index refresh",
    "refreshing affected indexes once",
)
CANONICAL_START = "./run.sh session begin --task-id <task> --agent <role>"


def _strip_frontmatter(text: str) -> str:
    """Remove one YAML frontmatter block at the start of Markdown."""
    if not text.startswith("---"):
        return text
    match = re.match(r"^---\r?\n.*?\r?\n---\r?\n?", text, re.DOTALL)
    return text[match.end() :] if match else text


def _normalize(text: str) -> list[str]:
    """Normalize line endings and trailing whitespace after frontmatter."""
    return [line.rstrip() for line in _strip_frontmatter(text).splitlines()]


def check_pair(
    name: str, github_file: Path, claude_file: Path, verbose: bool = False
) -> dict:
    """Require an exact normalized body match for one scoped-rule pair."""
    result = {
        "name": name,
        "github_exists": github_file.exists(),
        "claude_exists": claude_file.exists(),
        "status": "ok",
        "similarity": 1.0,
        "details": "",
    }
    if not github_file.exists() and not claude_file.exists():
        result["status"] = "both_missing"
        return result
    if not github_file.exists():
        result["status"] = "github_missing"
        return result
    if not claude_file.exists():
        result["status"] = "claude_missing"
        return result

    github_lines = _normalize(github_file.read_text(encoding="utf-8"))
    claude_lines = _normalize(claude_file.read_text(encoding="utf-8"))
    ratio = difflib.SequenceMatcher(None, github_lines, claude_lines).ratio()
    result["similarity"] = round(ratio, 3)

    if github_lines != claude_lines:
        result["status"] = "content_drift"
        if verbose:
            result["details"] = "\n".join(
                list(
                    difflib.unified_diff(
                        github_lines,
                        claude_lines,
                        fromfile=str(github_file),
                        tofile=str(claude_file),
                        lineterm="",
                        n=2,
                    )
                )[:60]
            )
    return result


def check_all_pairs(root: Path = REPO_ROOT, verbose: bool = False) -> list[dict]:
    """Check every maintained GitHub/Claude scoped-rule pair."""
    github_dir = root / ".github" / "instructions"
    claude_dir = root / ".claude" / "rules"
    return [
        check_pair(name, github_dir / github_name, claude_dir / claude_name, verbose)
        for name, (github_name, claude_name) in sorted(PAIRS.items())
    ]


def active_instruction_paths(root: Path = REPO_ROOT) -> list[Path]:
    """Return maintained executable surfaces, excluding archives."""
    fixed = [
        root / "AGENTS.md",
        root / "CLAUDE.md",
        root / ".github" / "copilot-instructions.md",
        root / ".github" / "copilot" / "instructions.md",
        root / "agents" / "README.md",
        root / "docs" / "architecture" / "config-precedence.md",
        root / "scripts" / "agent_brief.sh",
        root / "scripts" / "agent_context.py",
    ]
    patterns = (
        ".github/agents/*.agent.md",
        ".github/prompts/*.prompt.md",
        ".github/skills/*/SKILL.md",
        ".github/instructions/*.instructions.md",
        ".claude/rules/*.md",
    )
    discovered = [path for pattern in patterns for path in root.glob(pattern)]
    return sorted({path for path in fixed + discovered if path.exists()})


def _text(root: Path, relative: str) -> str:
    path = root / relative
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _issue(category: str, path: str, message: str) -> dict[str, str]:
    return {"category": category, "path": path, "message": message}


def instruction_contract_issues(root: Path = REPO_ROOT) -> list[dict[str, str]]:
    """Return outcome-changing ownership, command, and safety violations."""
    issues: list[dict[str, str]] = []

    for path in active_instruction_paths(root):
        relative = str(path.relative_to(root))
        content = path.read_text(encoding="utf-8")
        if DIRECT_RUNTIME.search(content):
            issues.append(
                _issue(
                    "runtime",
                    relative,
                    "uses a checkout-specific Python/pytest binary",
                )
            )
        lowered = content.lower()
        for phrase in STALE_PHRASES:
            if phrase in lowered:
                issues.append(
                    _issue("retired-workflow", relative, f"contains: {phrase}")
                )

    required_start_paths = (
        "AGENTS.md",
        "CLAUDE.md",
        ".github/copilot-instructions.md",
        ".github/agents/orchestrator.agent.md",
        ".github/prompts/session-start.prompt.md",
        ".github/prompts/master-workflow.prompt.md",
    )
    for relative in required_start_paths:
        if CANONICAL_START not in _text(root, relative):
            issues.append(
                _issue(
                    "session-start",
                    relative,
                    f"does not name canonical task start: {CANONICAL_START}",
                )
            )

    claude = _text(root, "CLAUDE.md")
    if not re.search(r"^@AGENTS\.md$", claude, re.MULTILINE):
        issues.append(_issue("composition", "CLAUDE.md", "must import @AGENTS.md"))
    if len(claude.splitlines()) > 200:
        issues.append(_issue("size", "CLAUDE.md", "must stay below 200 lines"))

    for relative, limit in {
        "AGENTS.md": 24_000,
        ".github/agents/orchestrator.agent.md": 24_000,
    }.items():
        size = len(_text(root, relative).encode("utf-8"))
        if size > limit:
            issues.append(
                _issue("size", relative, f"is {size} bytes; limit is {limit}")
            )

    manifest_path = root / "scripts" / "context-manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        read_first = manifest.get("areas", {}).get("agents", {}).get("read_first", [])
        if "agents/README.md" in read_first:
            issues.append(
                _issue(
                    "routing",
                    "scripts/context-manifest.json",
                    "routes live context through compatibility README",
                )
            )

    governance = _text(root, ".github/agents/governance.agent.md").lower()
    for phrase in ("commit maintenance", "archive stale docs", "clean branches"):
        if phrase in governance:
            issues.append(
                _issue(
                    "governance-safety",
                    ".github/agents/governance.agent.md",
                    f"contains unsafe shortcut: {phrase}",
                )
            )

    if "\x60" * 3 in _text(root, ".github/copilot/instructions.md"):
        issues.append(
            _issue(
                "compatibility",
                ".github/copilot/instructions.md",
                "compatibility path must remain pointer-only",
            )
        )

    legacy_readme = _text(root, "agents/README.md").lower()
    for phrase in ("older than 7 days", "clean worktrees", "handoff chains"):
        if phrase in legacy_readme:
            issues.append(
                _issue(
                    "legacy-routing",
                    "agents/README.md",
                    f"contains executable legacy workflow: {phrase}",
                )
            )

    composition_doc = _text(root, "docs/architecture/config-precedence.md").lower()
    if "universal precedence ladder" not in composition_doc:
        issues.append(
            _issue(
                "composition",
                "docs/architecture/config-precedence.md",
                "must reject a universal cross-platform precedence ladder",
            )
        )
    if "may not weaken" not in composition_doc:
        issues.append(
            _issue(
                "composition",
                "docs/architecture/config-precedence.md",
                "must preserve non-weakenable safety boundaries",
            )
        )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true", help="Show diffs")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args()

    pairs = check_all_pairs(verbose=args.verbose)
    contract_issues = instruction_contract_issues()
    failed = bool(contract_issues) or any(result["status"] != "ok" for result in pairs)

    if args.json:
        print(
            json.dumps(
                {
                    "status": "fail" if failed else "pass",
                    "pairs": pairs,
                    "contract_issues": contract_issues,
                },
                indent=2,
            )
        )
        return 1 if failed else 0

    print("=" * 68)
    print("Instruction Composition Check")
    print("=" * 68)
    print("Maintained scoped-rule bodies:")
    for result in pairs:
        icon = "PASS" if result["status"] == "ok" else "FAIL"
        similarity = f"{result['similarity'] * 100:.0f}%"
        print(
            f"  {icon:4s} {result['name']:15s} "
            f"exact={result['status'] == 'ok'} similarity={similarity}"
        )
        if result.get("details"):
            print(result["details"])

    print("\nSemantic contract:")
    if not contract_issues:
        print("  PASS no ownership, runtime, session, or safety conflicts")
    else:
        for issue in contract_issues:
            print(f"  FAIL [{issue['category']}] {issue['path']}: {issue['message']}")

    print()
    if failed:
        print("FAIL instruction composition has blocking conflicts")
    else:
        print("PASS instruction composition is consistent")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
