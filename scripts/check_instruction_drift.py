#!/usr/bin/env python3
"""Check for content drift between .github/instructions/ and .claude/rules/.

When to use: After editing any agent instruction file. Detects when the two
instruction platforms have diverged significantly, which causes agents on
different platforms to get inconsistent rules.

Usage:
    python scripts/check_instruction_drift.py           # Check all pairs
    python scripts/check_instruction_drift.py --verbose  # Show diff details
    python scripts/check_instruction_drift.py --json     # Machine-readable output
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GITHUB_DIR = REPO_ROOT / ".github" / "instructions"
CLAUDE_DIR = REPO_ROOT / ".claude" / "rules"

# Mapping: base name → (github file, claude file)
PAIRS = {
    "docs": ("docs.instructions.md", "docs.md"),
    "fastapi": ("fastapi.instructions.md", "fastapi.md"),
    "python-core": ("python-core.instructions.md", "python-core.md"),
    "react": ("react.instructions.md", "react.md"),
    "streamlit": ("streamlit.instructions.md", "streamlit.md"),
    "vba": ("vba.instructions.md", "vba.md"),
}


def _strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter (--- delimited block at start)."""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            text = text[end + 3:].lstrip("\n")
    return text


def _normalize(text: str) -> list[str]:
    """Normalize text for comparison: strip frontmatter, normalize whitespace."""
    text = _strip_frontmatter(text)
    # Normalize heading markers (# vs ##)
    lines = text.splitlines()
    normalized = []
    for line in lines:
        stripped = line.rstrip()
        if stripped:
            normalized.append(stripped)
    return normalized


def _extract_sections(text: str) -> set[str]:
    """Extract section headings from markdown."""
    headings = set()
    for line in text.splitlines():
        match = re.match(r"^#{1,3}\s+(.+)", line)
        if match:
            headings.add(match.group(1).strip().lower())
    return headings


def check_pair(
    name: str, github_file: Path, claude_file: Path, verbose: bool = False
) -> dict:
    """Compare one instruction pair and return drift metrics."""
    result = {
        "name": name,
        "github_exists": github_file.exists(),
        "claude_exists": claude_file.exists(),
        "status": "ok",
        "similarity": 1.0,
        "missing_sections": [],
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

    github_text = github_file.read_text(encoding="utf-8")
    claude_text = claude_file.read_text(encoding="utf-8")

    github_lines = _normalize(github_text)
    claude_lines = _normalize(claude_text)

    # Compute similarity ratio
    ratio = difflib.SequenceMatcher(None, github_lines, claude_lines).ratio()
    result["similarity"] = round(ratio, 3)

    # Check for section-level gaps
    github_sections = _extract_sections(github_text)
    claude_sections = _extract_sections(claude_text)

    only_github = github_sections - claude_sections
    only_claude = claude_sections - github_sections

    if only_github:
        result["missing_sections"].append(
            {"only_in": "github", "sections": sorted(only_github)}
        )
    if only_claude:
        result["missing_sections"].append(
            {"only_in": "claude", "sections": sorted(only_claude)}
        )

    # Determine status
    if ratio < 0.5:
        result["status"] = "high_drift"
    elif ratio < 0.75:
        result["status"] = "moderate_drift"
    elif only_github or only_claude:
        result["status"] = "section_drift"
    else:
        result["status"] = "ok"

    if verbose and ratio < 0.95:
        diff = list(
            difflib.unified_diff(
                github_lines,
                claude_lines,
                fromfile=f".github/instructions/{github_file.name}",
                tofile=f".claude/rules/{claude_file.name}",
                lineterm="",
                n=1,
            )
        )
        result["details"] = "\n".join(diff[:40])  # Cap output

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true", help="Show diff details")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args()

    results = []
    for name, (gh_name, cl_name) in sorted(PAIRS.items()):
        r = check_pair(
            name,
            GITHUB_DIR / gh_name,
            CLAUDE_DIR / cl_name,
            verbose=args.verbose,
        )
        results.append(r)

    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    # Pretty output
    print("=" * 60)
    print("🔍 Instruction Drift Check")
    print("=" * 60)
    print(f"  .github/instructions/ ↔ .claude/rules/\n")

    status_icons = {
        "ok": "✅",
        "section_drift": "⚠️ ",
        "moderate_drift": "🟡",
        "high_drift": "🔴",
        "github_missing": "❌",
        "claude_missing": "❌",
        "both_missing": "❌",
    }

    issues = 0
    for r in results:
        icon = status_icons.get(r["status"], "?")
        sim_pct = f"{r['similarity'] * 100:.0f}%"
        print(f"  {icon} {r['name']:15s}  similarity={sim_pct:>4s}  [{r['status']}]")

        if r["missing_sections"]:
            for ms in r["missing_sections"]:
                loc = ".github/" if ms["only_in"] == "github" else ".claude/"
                print(f"      Sections only in {loc}: {', '.join(ms['sections'])}")

        if r.get("details"):
            print(f"\n{r['details']}\n")

        if r["status"] not in ("ok",):
            issues += 1

    print()
    if issues == 0:
        print("✅ All instruction files are in sync")
    else:
        print(f"⚠️  {issues} file(s) have diverged — consider syncing content")

    return 1 if any(r["status"] in ("high_drift", "github_missing", "claude_missing") for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
