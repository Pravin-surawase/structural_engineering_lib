#!/usr/bin/env python3
"""Analyze documentation redundancy and consolidation opportunities.

This script analyzes 524+ markdown files in docs/ to identify:
1. Duplicate/similar content
2. Overlapping topics
3. Files that can be merged
4. Files that can be archived
5. Consolidation opportunities for AI agent efficiency

**Type:** Analysis
**Purpose:** Reduce cognitive load for AI agents by consolidating redundant docs
**Context:** 100% AI-driven development requires streamlined documentation
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"


def get_all_markdown_files() -> List[Path]:
    """Get all markdown files in docs/."""
    return list(DOCS_DIR.rglob("*.md"))


def analyze_file_metadata(filepath: Path) -> Dict[str, any]:
    """Extract metadata from markdown file."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        first_100_lines = lines[:100]

        # Extract metadata
        metadata = {
            "path": filepath.relative_to(PROJECT_ROOT),
            "size_bytes": len(content),
            "line_count": len(lines),
            "word_count": len(content.split()),
            "heading_count": len([l for l in lines if l.startswith("#")]),
            "code_blocks": content.count("```"),
            "has_type_metadata": any("**Type:**" in line for line in first_100_lines),
            "has_status_metadata": any(
                "**Status:**" in line for line in first_100_lines
            ),
            "has_version_metadata": any(
                "**Version:**" in line for line in first_100_lines
            ),
            "first_heading": "",
            "keywords": set(),
        }

        # Extract first heading
        for line in lines:
            if line.startswith("# "):
                metadata["first_heading"] = line[2:].strip()
                break

        # Extract keywords from title and first heading
        title = filepath.stem.lower()
        keywords = set(re.findall(r"\w+", title))
        if metadata["first_heading"]:
            keywords.update(re.findall(r"\w+", metadata["first_heading"].lower()))

        # Filter common words
        common_words = {
            "the",
            "and",
            "for",
            "with",
            "from",
            "this",
            "that",
            "are",
            "was",
            "have",
            "has",
        }
        metadata["keywords"] = keywords - common_words

        return metadata

    except Exception as e:
        return {
            "path": filepath.relative_to(PROJECT_ROOT),
            "error": str(e),
            "size_bytes": 0,
            "line_count": 0,
        }


def find_similar_files(metadata_list: List[Dict]) -> List[Tuple[Path, Path, Set[str]]]:
    """Find files with similar keywords (potential duplicates)."""
    similar_pairs = []

    for i, meta1 in enumerate(metadata_list):
        if "error" in meta1:
            continue
        for meta2 in metadata_list[i + 1 :]:
            if "error" in meta2:
                continue

            # Calculate keyword overlap
            keywords1 = meta1.get("keywords", set())
            keywords2 = meta2.get("keywords", set())

            if not keywords1 or not keywords2:
                continue

            overlap = keywords1 & keywords2

            # If 3+ keywords overlap, it's potentially similar
            if len(overlap) >= 3:
                similar_pairs.append((meta1["path"], meta2["path"], overlap))

    return similar_pairs


def group_files_by_folder() -> Dict[str, List[Path]]:
    """Group files by parent folder."""
    groups = defaultdict(list)

    for filepath in get_all_markdown_files():
        parent = filepath.parent.relative_to(DOCS_DIR)
        groups[str(parent)].append(filepath)

    return dict(groups)


def analyze_research_folder() -> Dict[str, any]:
    """Special analysis of research/ folder (highest redundancy risk)."""
    research_dir = DOCS_DIR / "research"

    if not research_dir.exists():
        return {}

    research_files = list(research_dir.rglob("*.md"))

    # Group by naming patterns
    patterns = {
        "PHASE": [],
        "SESSION": [],
        "RESEARCH": [],
        "QUICK": [],
        "SUMMARY": [],
        "README": [],
    }

    for filepath in research_files:
        name = filepath.name.upper()
        for pattern in patterns:
            if pattern in name:
                patterns[pattern].append(filepath)

    return {
        "total_files": len(research_files),
        "pattern_groups": {k: len(v) for k, v in patterns.items()},
        "files_by_pattern": patterns,
    }


def identify_archival_candidates() -> List[Tuple[Path, str]]:
    """Identify files that should be archived."""
    candidates = []

    for filepath in get_all_markdown_files():
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Check for archival indicators
            reasons = []

            if "**Status:**" in content and "Deprecated" in content:
                reasons.append("Status: Deprecated")

            if "**Status:**" in content and "Archived" in content:
                reasons.append("Status: Archived")

            if "superseded by" in content.lower():
                reasons.append("Superseded")

            # Check for old session docs (Session 1-10)
            if "Session" in filepath.name:
                match = re.search(r"Session[- ]?(\d+)", content)
                if match and int(match.group(1)) < 15:
                    reasons.append(f"Old session doc (Session {match.group(1)})")

            if reasons:
                candidates.append(
                    (filepath.relative_to(PROJECT_ROOT), ", ".join(reasons))
                )

        except Exception:
            pass

    return candidates


def generate_report():
    """Generate comprehensive redundancy analysis report."""
    print("=" * 80)
    print("DOCUMENTATION REDUNDANCY ANALYSIS")
    print("=" * 80)
    print()

    # Basic stats
    all_files = get_all_markdown_files()
    print(f"📊 Total markdown files: {len(all_files)}")
    print()

    # Analyze metadata
    print("📝 Analyzing file metadata...")
    metadata_list = [analyze_file_metadata(f) for f in all_files]

    # Size distribution
    sizes = [m["size_bytes"] for m in metadata_list if "error" not in m]
    print(f"   Total size: {sum(sizes) / 1024 / 1024:.1f} MB")
    print(f"   Average file size: {sum(sizes) / len(sizes) / 1024:.1f} KB")
    print(f"   Largest file: {max(sizes) / 1024:.1f} KB")
    print()

    # Metadata compliance
    with_type = sum(1 for m in metadata_list if m.get("has_type_metadata", False))
    with_status = sum(1 for m in metadata_list if m.get("has_status_metadata", False))
    print("📋 Metadata compliance:")
    print(
        f"   Files with **Type:** metadata: {with_type} ({with_type/len(all_files)*100:.1f}%)"
    )
    print(
        f"   Files with **Status:** metadata: {with_status} ({with_status/len(all_files)*100:.1f}%)"
    )
    print()

    # Find similar files
    print("🔍 Finding similar files...")
    similar_pairs = find_similar_files(metadata_list)
    print(f"   Found {len(similar_pairs)} potentially similar file pairs")

    if similar_pairs:
        print("\n   Top 10 similar pairs:")
        for path1, path2, overlap in sorted(
            similar_pairs, key=lambda x: len(x[2]), reverse=True
        )[:10]:
            print(f"      • {path1.name} ↔ {path2.name}")
            print(f"        Keywords: {', '.join(sorted(overlap)[:5])}")
    print()

    # Group by folder
    print("📁 Files by folder:")
    groups = group_files_by_folder()
    for folder, files in sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)[
        :15
    ]:
        print(f"   {folder}: {len(files)} files")
    print()

    # Research folder analysis
    print("🔬 Research folder analysis:")
    research_analysis = analyze_research_folder()
    if research_analysis:
        print(f"   Total files: {research_analysis['total_files']}")
        print("   Pattern groups:")
        for pattern, count in sorted(
            research_analysis["pattern_groups"].items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            if count > 0:
                print(f"      {pattern}: {count} files")
    print()

    # Archival candidates
    print("📦 Archival candidates:")
    candidates = identify_archival_candidates()
    print(f"   Found {len(candidates)} files for archival consideration")
    if candidates:
        print("\n   Top candidates:")
        for path, reason in candidates[:15]:
            print(f"      • {path}")
            print(f"        Reason: {reason}")
    print()

    # Consolidation recommendations
    print("💡 CONSOLIDATION RECOMMENDATIONS:")
    print()
    print("1. RESEARCH FOLDER (highest priority)")
    if research_analysis:
        for pattern, files in research_analysis.get("files_by_pattern", {}).items():
            if len(files) > 3:
                print(
                    f"   • {len(files)} {pattern}-prefixed files could be consolidated"
                )
    print()

    print("2. SESSION DOCUMENTATION")
    session_files = [m for m in metadata_list if "session" in str(m["path"]).lower()]
    print(f"   • {len(session_files)} session-related files found")
    print("   • Consider consolidating old session docs (Session 1-14) to _archive/")
    print()

    print("3. SIMILAR CONTENT")
    print(f"   • {len(similar_pairs)} file pairs with overlapping content")
    print("   • Review top 20 pairs for potential merging")
    print()

    print("4. FOLDER STRUCTURE")
    high_count_folders = [
        (f, len(files)) for f, files in groups.items() if len(files) > 20
    ]
    if high_count_folders:
        print("   • Folders with 20+ files (consider sub-grouping):")
        for folder, count in sorted(
            high_count_folders, key=lambda x: x[1], reverse=True
        )[:5]:
            print(f"      {folder}: {count} files")
    print()

    print("=" * 80)
    print("NEXT STEPS:")
    print("1. Review similar file pairs for merging opportunities")
    print("2. Archive deprecated/old session docs")
    print("3. Consolidate PHASE/SESSION/RESEARCH-prefixed files")
    print("4. Update folder structure for high-count folders")
    print("5. Use safe_file_move.py and safe_file_delete.py for operations")
    print("=" * 80)


if __name__ == "__main__":
    generate_report()
