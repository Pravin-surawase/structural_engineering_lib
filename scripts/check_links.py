#!/usr/bin/env python3
"""Check and fix broken internal links in markdown files.

Consolidates link checking and fixing into one script:
  - Scan mode (default): find broken links
  - Fix mode (--fix): auto-fix using fuzzy file matching
  - Map mode (--map): use explicit migration mapping for fixes

Replaces:
  - check_links.py (old version)
  - fix_broken_links.py

Usage:
    python scripts/check_links.py                         # Check all links
    python scripts/check_links.py --fix                   # Auto-fix with fuzzy match
    python scripts/check_links.py --fix --verbose         # Fix with details
    python scripts/check_links.py --map links.json --fix  # Fix with migration map
    python scripts/check_links.py --exclude-archive       # Skip _archive dirs

Exit Codes:
    0: No broken links
    1: Broken links found (or fixed)
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent

# Skip these patterns — placeholders/examples in docs
SKIP_LINK_PATTERNS = [
    r"^text$", r"^Link \d+$", r"^\$\w+$", r"^\.\*",
    r"^\'.*\'$", r"^path/to/", r"^target\.md$",
    r"^old-file\.md", r"^Old_File\.md", r"^file\.md",
]

# Skip files in these directories
SKIP_DIRECTORIES = [
    "agents/agent-9",
    "docs/_archive",
    "docs/research",
]


def _is_placeholder(text: str, target: str) -> bool:
    """Check if a link is a placeholder/example."""
    for pattern in SKIP_LINK_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE) or re.search(pattern, target, re.IGNORECASE):
            return True
    return False


def _should_skip_file(file_path: Path) -> bool:
    """Check if file should be skipped based on directory."""
    try:
        rel_path = str(file_path.relative_to(REPO_ROOT))
        return any(rel_path.startswith(d) for d in SKIP_DIRECTORIES)
    except ValueError:
        return False


def _find_links(content: str) -> list[tuple[str, str, int]]:
    """Find all markdown links [text](target) with positions."""
    pattern = r"(?<!!)\[([^\]]+)\]\(([^)]+)\)"
    return [(m.group(1), m.group(2), m.start()) for m in re.finditer(pattern, content)]


# ═══════════════════════════════════════════════════════════════════════════
# FUZZY FILE MATCHING (from fix_broken_links.py)
# ═══════════════════════════════════════════════════════════════════════════

def _build_file_index() -> dict[str, list[Path]]:
    """Build index of all files by lowercase filename."""
    index: dict[str, list[Path]] = defaultdict(list)
    for md_file in REPO_ROOT.rglob("*.md"):
        if any(p.startswith(".") or p == "node_modules" for p in md_file.parts):
            continue
        index[md_file.name.lower()].append(md_file)
    for py_file in REPO_ROOT.rglob("*.py"):
        if any(p.startswith(".") or p == "node_modules" for p in py_file.parts):
            continue
        index[py_file.name.lower()].append(py_file)
    return index


def _normalize(name: str) -> str:
    """Normalize filename for fuzzy matching."""
    return name.lower().replace("_", "-")


def _find_best_match(
    target_path: str, source_file: Path, file_index: dict[str, list[Path]],
) -> Optional[Path]:
    """Find the best matching file for a broken link target using fuzzy matching."""
    target = Path(target_path)
    filename = target.name.lower()

    # Exact filename match
    if filename in file_index:
        candidates = file_index[filename]
        if len(candidates) == 1:
            return candidates[0]
        # Multiple matches — prefer closest by directory overlap
        source_parts = set(source_file.parent.relative_to(REPO_ROOT).parts)
        best_score, best_match = -1, None
        for c in candidates:
            cparts = set(c.parent.relative_to(REPO_ROOT).parts)
            score = len(source_parts & cparts)
            if score > best_score:
                best_score, best_match = score, c
        return best_match

    # Normalized match (handle UPPERCASE, snake_case → kebab)
    normalized = _normalize(filename)
    for indexed_name, candidates in file_index.items():
        if _normalize(indexed_name) == normalized:
            if len(candidates) == 1:
                return candidates[0]
            for c in candidates:
                if "docs" in c.parts:
                    return c
            return candidates[0]

    # Stem match (ignore extension differences)
    stem = _normalize(target.stem)
    for indexed_name, candidates in file_index.items():
        if _normalize(Path(indexed_name).stem) == stem:
            if len(candidates) == 1:
                return candidates[0]
            for c in candidates:
                if "docs" in c.parts:
                    return c
            return candidates[0]

    return None


def _relative_path(from_file: Path, to_file: Path) -> str:
    """Compute relative path between two files."""
    from_dir = from_file.parent
    try:
        return str(to_file.relative_to(from_dir))
    except ValueError:
        from_rel = from_dir.relative_to(REPO_ROOT)
        to_rel = to_file.relative_to(REPO_ROOT)
        from_parts = from_rel.parts
        to_parts = to_rel.parts
        common_length = 0
        for i, (f, t) in enumerate(zip(from_parts, to_parts)):
            if f == t:
                common_length = i + 1
            else:
                break
        ups = len(from_parts) - common_length
        downs = to_parts[common_length:]
        return "/".join([".."] * ups + list(downs))


# ═══════════════════════════════════════════════════════════════════════════
# MAIN CHECK/FIX LOGIC
# ═══════════════════════════════════════════════════════════════════════════

def check_and_fix(
    fix: bool = False,
    verbose: bool = False,
    link_map: dict[str, str] | None = None,
    exclude_archive: bool = False,
) -> int:
    """Check all markdown files for broken links. Optionally fix them."""
    # Collect markdown files
    md_files = list((REPO_ROOT / "docs").rglob("*.md"))
    agents_dir = REPO_ROOT / "agents"
    if agents_dir.exists():
        md_files.extend(agents_dir.rglob("*.md"))
    for extra in ["Python/README.md", "README.md"]:
        p = REPO_ROOT / extra
        if p.exists():
            md_files.append(p)

    if exclude_archive:
        md_files = [f for f in md_files if "_archive" not in str(f)]

    # Build file index for fuzzy matching (only if fixing)
    file_index = _build_file_index() if fix else {}

    broken_links: list[dict] = []
    file_count = 0
    link_count = 0

    for md_file in md_files:
        if not md_file.exists():
            continue
        if _should_skip_file(md_file):
            continue

        file_count += 1
        content = md_file.read_text(encoding="utf-8")
        links = _find_links(content)

        for text, target, _pos in links:
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if _is_placeholder(text, target):
                continue

            link_count += 1
            target_path = target.split("#")[0]
            anchor = "#" + target.split("#")[1] if "#" in target else ""
            if not target_path:
                continue

            full_path = (md_file.parent / target_path).resolve()
            if full_path.exists():
                continue

            # Try to find suggestion
            suggestion = None
            if link_map:
                suggestion = link_map.get(target_path)
            if not suggestion and fix and file_index:
                match = _find_best_match(target_path, md_file, file_index)
                if match:
                    suggestion = _relative_path(md_file, match)

            broken_links.append({
                "file": str(md_file.relative_to(REPO_ROOT)),
                "file_path": md_file,
                "link_text": text,
                "target": target,
                "target_path": target_path,
                "anchor": anchor,
                "suggestion": suggestion,
            })

    # Report
    print(f"\n🔍 Checked {file_count} markdown files")
    print(f"   Found {link_count} internal links")
    print(f"   Broken links: {len(broken_links)}\n")

    if not broken_links:
        print("✅ All internal links are valid!")
        return 0

    # Show broken links
    for bl in broken_links:
        print(f"❌ {bl['file']}")
        print(f"   [{bl['link_text']}]({bl['target']})")
        if bl["suggestion"]:
            print(f"   💡 Suggestion: {bl['suggestion']}")
        print()

    # Apply fixes
    if fix:
        fixable = [bl for bl in broken_links if bl["suggestion"]]
        if fixable:
            files_to_update: dict[Path, str] = {}
            for bl in fixable:
                fp = bl["file_path"]
                if fp not in files_to_update:
                    files_to_update[fp] = fp.read_text(encoding="utf-8")
                old_link = f"]({bl['target']})"
                new_link = f"]({bl['suggestion']}{bl['anchor']})"
                files_to_update[fp] = files_to_update[fp].replace(old_link, new_link)

            for fp, content in files_to_update.items():
                fp.write_text(content, encoding="utf-8")

            print(f"✅ Fixed {len(fixable)} links in {len(files_to_update)} files")
            unfixed = len(broken_links) - len(fixable)
            if unfixed:
                print(f"⚠️  {unfixed} links could not be auto-fixed")
        else:
            print("⚠️  No links could be auto-fixed (no matches found)")
    else:
        fixable = sum(1 for bl in broken_links if bl.get("suggestion"))
        print(f"💡 Run with --fix to auto-fix {fixable if fixable else 'fixable'} links:")
        print("   python scripts/check_links.py --fix")

    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check and fix broken markdown links",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/check_links.py                         # Scan only\n"
            "  python scripts/check_links.py --fix                   # Auto-fix\n"
            "  python scripts/check_links.py --fix --verbose         # Fix + details\n"
            "  python scripts/check_links.py --map links.json --fix  # Use migration map\n"
        ),
    )
    parser.add_argument("--fix", action="store_true", help="Auto-fix broken links using fuzzy matching")
    parser.add_argument("--map", help="Path to link mapping JSON (old → new paths)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--exclude-archive", action="store_true", help="Skip _archive directories")

    args = parser.parse_args()

    link_map: dict[str, str] | None = None
    if args.map and Path(args.map).exists():
        with open(args.map) as f:
            link_map = json.load(f)
        print(f"📋 Loaded {len(link_map)} mappings from {args.map}")

    return check_and_fix(
        fix=args.fix,
        verbose=args.verbose,
        link_map=link_map,
        exclude_archive=args.exclude_archive,
    )


if __name__ == "__main__":
    raise SystemExit(main())
