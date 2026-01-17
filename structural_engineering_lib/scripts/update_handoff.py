#!/usr/bin/env python3
"""Update next-session-brief.md with a concise handoff block."""

from __future__ import annotations

from pathlib import Path
import re

REPO_ROOT = Path(__file__).parent.parent
SESSION_LOG = REPO_ROOT / "docs" / "SESSION_LOG.md"
NEXT_BRIEF = REPO_ROOT / "docs" / "planning" / "next-session-brief.md"

DATE_RE = re.compile(r"##\s+(\d{4}-\d{2}-\d{2})\s+—\s+Session")


def _latest_session_block(lines: list[str]) -> tuple[str, list[str]]:
    start_idx = -1
    date_str = ""
    for idx, line in enumerate(lines):
        match = DATE_RE.match(line.strip())
        if match:
            start_idx = idx
            date_str = match.group(1)
            break

    if start_idx == -1:
        raise ValueError("No session header found in SESSION_LOG.md")

    end_idx = len(lines)
    for idx in range(start_idx + 1, len(lines)):
        if lines[idx].startswith("## "):
            end_idx = idx
            break

    return date_str, lines[start_idx:end_idx]


def _parse_focus(block: list[str]) -> str:
    for line in block:
        if line.startswith("**Focus:**"):
            return line.split("**Focus:**", 1)[1].strip()
    return ""


def _parse_completed(block: list[str]) -> list[str]:
    completed: list[str] = []
    in_completed = False
    for line in block:
        if line.startswith("**Completed:**"):
            in_completed = True
            continue
        if in_completed:
            if line.startswith("### ") or line.startswith("## "):
                break
            if line.strip().startswith("-"):
                item = line.strip().lstrip("-").strip()
                if item:
                    completed.append(item)
            elif line.strip() == "":
                if completed:
                    break
    return completed


def _parse_prs(block: list[str]) -> list[str]:
    prs: list[str] = []
    for line in block:
        match = re.search(r"\|\s*#(\d+)", line)
        if match:
            prs.append(f"#{match.group(1)}")
    return prs


def _build_handoff_lines(date_str: str, block: list[str]) -> list[str]:
    focus = _parse_focus(block)
    completed = _parse_completed(block)[:3]
    prs = _parse_prs(block)[:6]

    lines = [f"- Date: {date_str}"]
    if focus:
        lines.append(f"- Focus: {focus}")
    if completed:
        lines.append(f"- Completed: {'; '.join(completed)}")
    if prs:
        lines.append(f"- PRs: {', '.join(prs)}")
    return lines


def _update_next_brief(handoff_lines: list[str]) -> None:
    text = NEXT_BRIEF.read_text(encoding="utf-8")
    start_marker = "<!-- HANDOFF:START -->"
    end_marker = "<!-- HANDOFF:END -->"

    block = "\n".join(
        [
            "## Latest Handoff (auto)",
            "",
            start_marker,
            *handoff_lines,
            end_marker,
            "",
        ]
    )

    if start_marker in text and end_marker in text:
        pattern = re.compile(
            r"## Latest Handoff \(auto\)\n\n"
            + re.escape(start_marker)
            + r"[\s\S]*?"
            + re.escape(end_marker)
        )
        new_text = pattern.sub(block.rstrip(), text)
    else:
        lines = text.splitlines()
        insert_idx = None
        for idx, line in enumerate(lines):
            if line.strip() == "---":
                insert_idx = idx + 1
                break
        if insert_idx is None:
            insert_idx = 2
        new_lines = lines[:insert_idx] + ["", block, ""] + lines[insert_idx:]
        new_text = "\n".join(new_lines)

    NEXT_BRIEF.write_text(new_text.strip() + "\n", encoding="utf-8")


def main() -> int:
    if not SESSION_LOG.exists():
        print("ERROR: docs/SESSION_LOG.md not found")
        return 1
    if not NEXT_BRIEF.exists():
        print("ERROR: docs/planning/next-session-brief.md not found")
        return 1

    lines = SESSION_LOG.read_text(encoding="utf-8").splitlines()
    date_str, block = _latest_session_block(lines)
    handoff_lines = _build_handoff_lines(date_str, block)

    if not handoff_lines:
        print("ERROR: Could not build handoff lines from SESSION_LOG.md")
        return 1

    _update_next_brief(handoff_lines)
    print("Updated next-session-brief.md handoff block.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
