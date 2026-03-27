#!/usr/bin/env python3
"""Fix broken internal links in markdown files.

When to use: After cleanup/archival removes files that are still referenced.
This script removes or converts broken links to plain text based on context:
  - Table rows referencing deleted files → remove the row
  - List items referencing deleted files → remove the item
  - Inline links in prose → convert [text](broken) to just text
  - SESSION_LOG.md → convert links to plain text (preserve history)

Usage:
    python scripts/fix_broken_links.py --dry-run    # Preview changes
    python scripts/fix_broken_links.py               # Apply fixes
    python scripts/fix_broken_links.py --verbose     # Show details
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Map of (source_file_relative, link_target_substring) → action
# Actions: "remove_line", "plain_text", "remove_row"
# Most broken links are to deleted streamlit/vba/excel/xlwings files.
# We identify them by the target path containing these keywords.

DELETED_TARGETS = {
    # Streamlit files/docs
    "streamlit_app/",
    "streamlit-comprehensive-prevention-system.md",
    "streamlit-issues-catalog.md",
    "streamlit-maintenance-guide.md",
    "streamlit-prevention-system-review.md",
    "streamlit-fragment-best-practices.md",
    "streamlit-phase-3-implementation-plan.md",
    "streamlit-code-quality-research.md",
    "streamlit-validation.md",
    "agent-6-streamlit-hub.md",
    # VBA/Excel files/docs
    "vba/",
    "vba-guide.md",
    "vba-testing-guide.md",
    "vba-api-reference.md",
    "vba-udt-reference.md",
    "vba-vscode-workflow.md",
    "vscode-vba-quickstart.md",
    "etabs-vba-user-guide.md",
    "etabs-vba-implementation-plan.md",
    "etabs-vba-questions-answered.md",
    "excel-quickstart.md",
    "excel-tutorial.md",
    "excel-addin-guide.md",
    "VBA/Modules/",
    # xlwings docs
    "xlwings-migration-plan.md",
    "xlwings-quick-start.md",
    "xlwings-solution-summary.md",
    "xlwings-test-results.md",
    "python-excel-research-2025.md",
    "task-0.1-xlwings-installation-copilot.md",
    # Deleted learning/planning docs
    "v3-fastapi-learning-guide.md",
    "docker-fundamentals-guide.md",
    "automation-foundation-learning-guide.md",
    "v3-streamlit-parity-library-evolution-plan.md",
}


def is_broken_target(target: str) -> bool:
    """Check if a link target matches a known deleted file."""
    for pattern in DELETED_TARGETS:
        if pattern in target:
            return True
    return False


def is_table_row(line: str) -> bool:
    """Check if line is a markdown table row."""
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def is_table_separator(line: str) -> bool:
    """Check if line is a table separator (|---|---|)."""
    stripped = line.strip()
    return bool(re.match(r"^\|[\s\-:|]+\|$", stripped))


def is_list_item(line: str) -> bool:
    """Check if line is a markdown list item."""
    stripped = line.lstrip()
    return stripped.startswith("- ") or stripped.startswith("* ") or bool(
        re.match(r"^\d+\.\s", stripped)
    )


# Regex to match markdown links: [text](target)
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def fix_file(filepath: Path, dry_run: bool = False, verbose: bool = False) -> int:
    """Fix broken links in a single file. Returns number of fixes."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ⚠ Cannot read {filepath}: {e}")
        return 0

    lines = content.split("\n")
    new_lines: list[str] = []
    fixes = 0
    is_session_log = "SESSION_LOG" in filepath.name

    i = 0
    while i < len(lines):
        line = lines[i]
        links = LINK_RE.findall(line)
        broken_links = [(text, target) for text, target in links if is_broken_target(target)]

        if not broken_links:
            new_lines.append(line)
            i += 1
            continue

        # Decide fix strategy based on line context
        if is_table_row(line) and not is_table_separator(line):
            # Count non-broken content in the row
            # If ALL links in the row are broken, remove the row
            # EXCEPT in SESSION_LOG.md — always convert to plain text (preserve history)
            all_links_broken = all(is_broken_target(t) for _, t in links) if links else False

            if all_links_broken and not is_session_log:
                if verbose or dry_run:
                    print(f"  🗑  REMOVE row: {filepath.relative_to(REPO_ROOT)}:{i + 1}")
                    print(f"      {line.strip()[:100]}")
                fixes += 1
                i += 1
                continue  # skip this line
            else:
                # Mixed row — convert broken links to plain text
                fixed_line = line
                for text, target in broken_links:
                    fixed_line = fixed_line.replace(f"[{text}]({target})", text)
                new_lines.append(fixed_line)
                if verbose or dry_run:
                    print(f"  ✏️  PLAIN TEXT: {filepath.relative_to(REPO_ROOT)}:{i + 1}")
                    print(f"      [{broken_links[0][0]}](...) → {broken_links[0][0]}")
                fixes += 1
                i += 1
                continue

        elif is_list_item(line):
            # Check if the list item is ONLY a broken link (no meaningful other content)
            stripped = line.lstrip()
            # Remove the list marker
            after_marker = re.sub(r"^[-*]\s+|\d+\.\s+", "", stripped)
            # If the remaining content is just the broken link (maybe with trailing description)
            # and it's not in SESSION_LOG, remove the line
            if not is_session_log and len(broken_links) == len(links):
                if verbose or dry_run:
                    print(f"  🗑  REMOVE item: {filepath.relative_to(REPO_ROOT)}:{i + 1}")
                    print(f"      {line.strip()[:100]}")
                fixes += 1
                i += 1
                continue  # skip this line
            else:
                # Convert to plain text
                fixed_line = line
                for text, target in broken_links:
                    fixed_line = fixed_line.replace(f"[{text}]({target})", text)
                new_lines.append(fixed_line)
                if verbose or dry_run:
                    print(f"  ✏️  PLAIN TEXT: {filepath.relative_to(REPO_ROOT)}:{i + 1}")
                fixes += 1
                i += 1
                continue

        else:
            # Inline text — convert to plain text
            fixed_line = line
            for text, target in broken_links:
                fixed_line = fixed_line.replace(f"[{text}]({target})", text)
            new_lines.append(fixed_line)
            if verbose or dry_run:
                print(f"  ✏️  PLAIN TEXT: {filepath.relative_to(REPO_ROOT)}:{i + 1}")
                for text, target in broken_links:
                    print(f"      [{text}]({target}) → {text}")
            fixes += 1
            i += 1
            continue

        new_lines.append(line)
        i += 1

    if fixes > 0 and not dry_run:
        filepath.write_text("\n".join(new_lines), encoding="utf-8")

    return fixes


def main() -> int:
    parser = argparse.ArgumentParser(description="Fix broken markdown links")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed changes")
    args = parser.parse_args()

    docs_dir = REPO_ROOT / "docs"
    if not docs_dir.exists():
        print("❌ docs/ directory not found")
        return 1

    # Find all markdown files
    md_files = sorted(docs_dir.rglob("*.md"))

    # Skip archived docs
    skip_dirs = {"_archive", "research"}
    md_files = [
        f
        for f in md_files
        if not any(part in skip_dirs for part in f.relative_to(docs_dir).parts)
    ]

    total_fixes = 0
    files_fixed = 0

    mode = "DRY RUN" if args.dry_run else "FIXING"
    print(f"\n🔧 {mode}: Broken links in {len(md_files)} markdown files\n")

    for filepath in md_files:
        fixes = fix_file(filepath, dry_run=args.dry_run, verbose=args.verbose)
        if fixes > 0:
            total_fixes += fixes
            files_fixed += 1
            if not args.verbose and not args.dry_run:
                print(f"  ✅ {filepath.relative_to(REPO_ROOT)} — {fixes} fix(es)")

    print(f"\n{'=' * 50}")
    print(f"  Total fixes: {total_fixes} across {files_fixed} files")
    if args.dry_run:
        print("  (dry run — no files were modified)")
    print(f"{'=' * 50}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
