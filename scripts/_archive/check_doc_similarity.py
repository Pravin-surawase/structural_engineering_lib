#!/usr/bin/env python3
"""
Check for similar documents before creating a new one.

Prevents duplication by:
1. Checking docs-canonical.json for existing canonical docs
2. Fuzzy matching against existing document titles
3. Warning about potential duplicates

Usage:
    python scripts/check_doc_similarity.py "AI Agent Effectiveness"
    python scripts/check_doc_similarity.py --check-file docs/research/new-doc.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import NamedTuple


class SimilarDoc(NamedTuple):
    """A document that may be similar to the query."""
    path: str
    title: str
    similarity: float
    reason: str


def extract_title_from_file(filepath: Path) -> str:
    """Extract the title from a markdown file (first H1 heading)."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    return line[2:].strip()
                # Stop after 20 lines to avoid reading entire file
                if f.tell() > 2000:
                    break
    except Exception:
        pass
    return filepath.stem.replace("-", " ").replace("_", " ").title()


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    # Convert to lowercase
    text = text.lower()
    # Remove common prefixes/suffixes
    for prefix in ["guide-", "research-", "reference-", "decision-", "adr-"]:
        if text.startswith(prefix):
            text = text[len(prefix):]
    # Remove file extension
    text = re.sub(r"\.md$", "", text)
    # Replace separators with spaces
    text = re.sub(r"[-_]", " ", text)
    # Remove extra whitespace
    text = " ".join(text.split())
    return text


def extract_keywords(text: str) -> set[str]:
    """Extract meaningful keywords from text."""
    text = normalize_text(text)
    # Common stopwords to exclude
    stopwords = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
        "be", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "must", "shall", "can", "this",
        "that", "these", "those", "it", "its", "guide", "reference", "research",
        "document", "documentation", "docs", "md"
    }
    words = set(text.split())
    return words - stopwords


def similarity_score(text1: str, text2: str) -> float:
    """Calculate similarity between two texts."""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)

    # Sequence matcher for overall similarity
    seq_sim = SequenceMatcher(None, norm1, norm2).ratio()

    # Keyword overlap
    kw1 = extract_keywords(text1)
    kw2 = extract_keywords(text2)
    if kw1 and kw2:
        overlap = len(kw1 & kw2) / max(len(kw1), len(kw2))
    else:
        overlap = 0

    # Combined score (weight keyword overlap more heavily)
    return 0.4 * seq_sim + 0.6 * overlap


def load_canonical_docs(project_root: Path) -> dict:
    """Load the canonical document registry."""
    canonical_path = project_root / "docs" / "docs-canonical.json"
    if canonical_path.exists():
        try:
            with open(canonical_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def check_canonical_match(query: str, canonical_data: dict) -> list[SimilarDoc]:
    """Check if query matches any canonical topic."""
    matches = []
    query_keywords = extract_keywords(query)

    topics = canonical_data.get("topics", {})
    for topic_name, topic_info in topics.items():
        topic_keywords = extract_keywords(topic_name)
        if query_keywords & topic_keywords:
            matches.append(SimilarDoc(
                path=topic_info.get("canonical", ""),
                title=topic_name,
                similarity=1.0,
                reason=f"Matches canonical topic '{topic_name}'"
            ))

    return matches


def find_similar_docs(query: str, project_root: Path, threshold: float = 0.4) -> list[SimilarDoc]:
    """Find documents similar to the query."""
    similar = []
    docs_dir = project_root / "docs"

    # Skip archive directories
    skip_dirs = {"_archive", "node_modules", ".git", "__pycache__"}

    for md_file in docs_dir.rglob("*.md"):
        # Skip archived files
        if any(skip in md_file.parts for skip in skip_dirs):
            continue

        title = extract_title_from_file(md_file)
        filename = md_file.stem

        # Check similarity against both title and filename
        title_sim = similarity_score(query, title)
        filename_sim = similarity_score(query, filename)
        best_sim = max(title_sim, filename_sim)

        if best_sim >= threshold:
            rel_path = md_file.relative_to(project_root)
            reason = "Title match" if title_sim > filename_sim else "Filename match"
            similar.append(SimilarDoc(
                path=str(rel_path),
                title=title,
                similarity=best_sim,
                reason=f"{reason} ({best_sim:.0%})"
            ))

    # Sort by similarity descending
    similar.sort(key=lambda x: x.similarity, reverse=True)
    return similar[:10]  # Top 10


def main():
    parser = argparse.ArgumentParser(
        description="Check for similar documents before creating a new one"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Title or topic to check for duplicates"
    )
    parser.add_argument(
        "--check-file",
        help="Check a specific file for potential duplicates"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.4,
        help="Similarity threshold (0-1, default 0.4)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Get query
    if args.check_file:
        query = extract_title_from_file(Path(args.check_file))
    elif args.query:
        query = args.query
    else:
        parser.print_help()
        sys.exit(1)

    # Load canonical docs
    canonical_data = load_canonical_docs(project_root)

    # Check canonical matches first
    canonical_matches = check_canonical_match(query, canonical_data)

    # Find similar documents
    similar_docs = find_similar_docs(query, project_root, args.threshold)

    # Output results
    if args.json:
        result = {
            "query": query,
            "canonical_matches": [
                {"path": m.path, "title": m.title, "reason": m.reason}
                for m in canonical_matches
            ],
            "similar_docs": [
                {"path": m.path, "title": m.title, "similarity": m.similarity, "reason": m.reason}
                for m in similar_docs
            ]
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"\n🔍 Checking for duplicates: \"{query}\"\n")

        if canonical_matches:
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("🎯 CANONICAL DOCUMENT EXISTS!")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            for match in canonical_matches:
                print(f"  Topic: {match.title}")
                print(f"  Path:  {match.path}")
                print(f"  → Update this file instead of creating a new one!")
            print()

        if similar_docs:
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("📄 Similar Documents Found:")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            for doc in similar_docs[:5]:
                emoji = "🔴" if doc.similarity > 0.7 else "🟡" if doc.similarity > 0.5 else "🟢"
                print(f"  {emoji} {doc.path}")
                print(f"     Title: {doc.title}")
                print(f"     {doc.reason}")
            print()

        if not canonical_matches and not similar_docs:
            print("✅ No similar documents found. Safe to create a new one.")
        elif canonical_matches:
            print("⚠️  Consider updating the canonical document instead.")
            sys.exit(1)
        elif any(d.similarity > 0.7 for d in similar_docs):
            print("⚠️  High similarity detected. Please review before creating.")
            sys.exit(1)
        else:
            print("✅ Low similarity matches only. Proceed with caution.")


if __name__ == "__main__":
    main()
