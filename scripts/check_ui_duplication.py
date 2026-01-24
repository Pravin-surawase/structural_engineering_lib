#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Streamlit UI Duplication Scanner.

Detects code duplication and redundancy in the Streamlit application to:
- Identify repeated utility functions
- Find similar implementations that could be consolidated
- Detect copy-paste code patterns
- Recommend refactoring opportunities

This scanner is part of the V3 automation foundation for maintaining
code quality during the FastAPI migration.

Usage:
    python scripts/check_ui_duplication.py                    # Full scan
    python scripts/check_ui_duplication.py --utils-only       # Just utils/
    python scripts/check_ui_duplication.py --show-similar     # Show code snippets
    python scripts/check_ui_duplication.py --json             # JSON output

Exit codes:
    0 - No significant duplication found
    1 - Duplication detected (above threshold)
    2 - Script error

Created: 2026-01-24 (Session 69)
Related: docs/research/automation-audit-readiness-research.md
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

# =============================================================================
# Configuration
# =============================================================================

# Minimum function body lines to consider for duplication
MIN_FUNCTION_LINES = 5

# Similarity threshold for near-duplicates (0.0 to 1.0)
SIMILARITY_THRESHOLD = 0.7

# Directories to scan
SCAN_DIRS = [
    "streamlit_app/utils",
    "streamlit_app/components",
    "streamlit_app/pages",
]

# File patterns to exclude
EXCLUDE_PATTERNS = [
    "__pycache__",
    ".pyc",
    "_test.py",
    "test_",
]


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class FunctionInfo:
    """Information about a function definition."""

    name: str
    file: Path
    line: int
    end_line: int
    body_hash: str
    body_lines: int
    params: list[str]
    docstring: str | None
    decorators: list[str]
    source: str = ""


@dataclass
class DuplicationReport:
    """Report of duplication findings."""

    exact_duplicates: list[tuple[FunctionInfo, FunctionInfo]] = field(
        default_factory=list
    )
    near_duplicates: list[tuple[FunctionInfo, FunctionInfo, float]] = field(
        default_factory=list
    )
    similar_names: list[tuple[FunctionInfo, FunctionInfo]] = field(default_factory=list)
    import_duplicates: dict[str, list[Path]] = field(default_factory=dict)
    summary: dict = field(default_factory=dict)


# =============================================================================
# AST Extraction
# =============================================================================


def extract_functions(file_path: Path) -> Iterator[FunctionInfo]:
    """Extract function definitions from a Python file."""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"  ⚠️  Skipping {file_path}: {e}")
        return

    source_lines = source.splitlines()

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            # Get function body as string for hashing
            if node.end_lineno and node.lineno:
                body_lines = source_lines[node.lineno - 1 : node.end_lineno]
                body_text = "\n".join(body_lines)
                body_line_count = len(body_lines)
            else:
                body_text = ""
                body_line_count = 0

            # Only process functions with substantial body
            if body_line_count < MIN_FUNCTION_LINES:
                continue

            # Get docstring
            docstring = None
            if (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            ):
                docstring = node.body[0].value.value[:100]

            # Get decorators
            decorators = []
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name):
                    decorators.append(dec.id)
                elif isinstance(dec, ast.Attribute):
                    decorators.append(dec.attr)
                elif isinstance(dec, ast.Call):
                    if isinstance(dec.func, ast.Name):
                        decorators.append(dec.func.id)
                    elif isinstance(dec.func, ast.Attribute):
                        decorators.append(dec.func.attr)

            # Get parameters
            params = [arg.arg for arg in node.args.args]

            # Hash the normalized body (remove whitespace variations)
            normalized = normalize_code(body_text)
            body_hash = hashlib.md5(normalized.encode()).hexdigest()

            yield FunctionInfo(
                name=node.name,
                file=file_path,
                line=node.lineno,
                end_line=node.end_lineno or node.lineno,
                body_hash=body_hash,
                body_lines=body_line_count,
                params=params,
                docstring=docstring,
                decorators=decorators,
                source=body_text,
            )


def normalize_code(code: str) -> str:
    """Normalize code for comparison by removing variable names and whitespace."""
    # Simple normalization: remove extra whitespace
    lines = []
    for line in code.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            lines.append(stripped)
    return "\n".join(lines)


# =============================================================================
# Similarity Detection
# =============================================================================


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def code_similarity(code1: str, code2: str) -> float:
    """Calculate similarity ratio between two code snippets using line matching.

    Uses Jaccard similarity on lines for performance (O(n) vs O(n*m) for Levenshtein).
    """
    lines1 = set(normalize_code(code1).splitlines())
    lines2 = set(normalize_code(code2).splitlines())

    if not lines1 or not lines2:
        return 0.0

    intersection = len(lines1.intersection(lines2))
    union = len(lines1.union(lines2))

    if union == 0:
        return 1.0

    return intersection / union


def name_similarity(name1: str, name2: str) -> float:
    """Calculate similarity between function names."""
    # Split by underscore and compare words
    words1 = set(name1.lower().split("_"))
    words2 = set(name2.lower().split("_"))

    if not words1 or not words2:
        return 0.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    return len(intersection) / len(union)


# =============================================================================
# Import Analysis
# =============================================================================


def extract_imports(file_path: Path) -> list[str]:
    """Extract import statements from a Python file."""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError):
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")

    return imports


# =============================================================================
# Main Scanner
# =============================================================================


def scan_directory(directory: Path) -> list[FunctionInfo]:
    """Scan a directory for function definitions."""
    functions = []

    for py_file in directory.rglob("*.py"):
        # Skip excluded patterns
        if any(pattern in str(py_file) for pattern in EXCLUDE_PATTERNS):
            continue

        functions.extend(extract_functions(py_file))

    return functions


def find_duplicates(functions: list[FunctionInfo]) -> DuplicationReport:
    """Find duplicate and similar functions."""
    report = DuplicationReport()

    # Group by hash for exact duplicates
    hash_groups: dict[str, list[FunctionInfo]] = defaultdict(list)
    for func in functions:
        hash_groups[func.body_hash].append(func)

    # Find exact duplicates
    for hash_val, group in hash_groups.items():
        if len(group) > 1:
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    report.exact_duplicates.append((group[i], group[j]))

    # Track already-compared pairs
    compared = set()

    # Find near-duplicates (different hash but similar code)
    # Limit comparisons to avoid O(n^2) explosion
    near_dup_limit = 50  # Max near-duplicates to find
    comparison_count = 0
    max_comparisons = 1000  # Stop after this many comparisons

    for i, func1 in enumerate(functions):
        for func2 in functions[i + 1 :]:
            comparison_count += 1
            if comparison_count > max_comparisons:
                break
            if len(report.near_duplicates) >= near_dup_limit:
                break

            # Skip exact duplicates (already found)
            if func1.body_hash == func2.body_hash:
                continue

            # Skip if already compared
            pair_key = tuple(sorted([id(func1), id(func2)]))
            if pair_key in compared:
                continue
            compared.add(pair_key)

            # Skip if in same file (often legitimate)
            if func1.file == func2.file:
                continue

            # Calculate similarity
            sim = code_similarity(func1.source, func2.source)
            if sim >= SIMILARITY_THRESHOLD:
                report.near_duplicates.append((func1, func2, sim))

    # Find similar names (potential redundant implementations)
    name_groups: dict[str, list[FunctionInfo]] = defaultdict(list)
    for func in functions:
        # Normalize name for grouping
        base_name = func.name.lower().strip("_")
        name_groups[base_name].append(func)

    for base_name, group in name_groups.items():
        if len(group) > 1:
            # Functions with same base name in different files
            files = {f.file for f in group}
            if len(files) > 1:
                for i in range(len(group)):
                    for j in range(i + 1, len(group)):
                        if group[i].file != group[j].file:
                            report.similar_names.append((group[i], group[j]))

    # Import analysis
    import_locations: dict[str, list[Path]] = defaultdict(list)
    for func in functions:
        imports = extract_imports(func.file)
        for imp in imports:
            import_locations[imp].append(func.file)

    # Find commonly duplicated custom imports
    for imp, files in import_locations.items():
        unique_files = list(set(files))
        if len(unique_files) >= 5 and not imp.startswith(("streamlit", "pandas", "numpy")):
            report.import_duplicates[imp] = unique_files

    # Summary
    report.summary = {
        "total_functions": len(functions),
        "exact_duplicates": len(report.exact_duplicates),
        "near_duplicates": len(report.near_duplicates),
        "similar_names": len(report.similar_names),
        "common_imports": len(report.import_duplicates),
    }

    return report


# =============================================================================
# Output Formatting
# =============================================================================


def format_console_report(report: DuplicationReport, show_similar: bool = False) -> str:
    """Format report for console output."""
    lines = []
    lines.append("=" * 60)
    lines.append("📊 UI Duplication Scan Report")
    lines.append("=" * 60)
    lines.append("")

    # Summary
    lines.append("Summary:")
    lines.append(f"  Total functions analyzed: {report.summary.get('total_functions', 0)}")
    lines.append(f"  Exact duplicates: {report.summary.get('exact_duplicates', 0)}")
    lines.append(f"  Near duplicates (≥{SIMILARITY_THRESHOLD*100:.0f}% similar): {report.summary.get('near_duplicates', 0)}")
    lines.append(f"  Similar names: {report.summary.get('similar_names', 0)}")
    lines.append("")

    # Exact duplicates
    if report.exact_duplicates:
        lines.append("-" * 60)
        lines.append("🔴 EXACT DUPLICATES (identical code)")
        lines.append("-" * 60)
        for func1, func2 in report.exact_duplicates[:10]:
            lines.append(f"  {func1.name}()")
            lines.append(f"    📍 {func1.file}:{func1.line}")
            lines.append(f"    📍 {func2.file}:{func2.line}")
            lines.append(f"    ({func1.body_lines} lines)")
            lines.append("")

        if len(report.exact_duplicates) > 10:
            lines.append(f"  ... and {len(report.exact_duplicates) - 10} more")
            lines.append("")

    # Near duplicates
    if report.near_duplicates:
        lines.append("-" * 60)
        lines.append("🟡 NEAR DUPLICATES (similar code)")
        lines.append("-" * 60)
        for func1, func2, sim in sorted(report.near_duplicates, key=lambda x: -x[2])[:10]:
            lines.append(f"  {func1.name}() ↔ {func2.name()}  ({sim*100:.0f}% similar)")
            lines.append(f"    📍 {func1.file}:{func1.line}")
            lines.append(f"    📍 {func2.file}:{func2.line}")
            if show_similar:
                lines.append("    Code preview:")
                for line in func1.source.splitlines()[:5]:
                    lines.append(f"      {line}")
            lines.append("")

        if len(report.near_duplicates) > 10:
            lines.append(f"  ... and {len(report.near_duplicates) - 10} more")
            lines.append("")

    # Similar names
    if report.similar_names:
        lines.append("-" * 60)
        lines.append("🟢 SIMILAR NAMES (potential redundancy)")
        lines.append("-" * 60)
        seen = set()
        for func1, func2 in report.similar_names[:10]:
            key = tuple(sorted([func1.name, func2.name]))
            if key in seen:
                continue
            seen.add(key)
            lines.append(f"  {func1.name}() ↔ {func2.name}()")
            lines.append(f"    📍 {func1.file}:{func1.line}")
            lines.append(f"    📍 {func2.file}:{func2.line}")
            lines.append("")

        if len(report.similar_names) > 10:
            lines.append(f"  ... and {len(report.similar_names) - 10} more")
            lines.append("")

    # Recommendations
    lines.append("-" * 60)
    lines.append("📋 Recommendations")
    lines.append("-" * 60)

    if report.exact_duplicates:
        lines.append("  1. Consolidate exact duplicates into shared utility module")

    if report.near_duplicates:
        lines.append("  2. Review near-duplicates for refactoring opportunities")

    if report.similar_names:
        lines.append("  3. Audit similar-named functions for potential consolidation")

    if not (report.exact_duplicates or report.near_duplicates):
        lines.append("  ✅ No significant duplication found!")

    lines.append("")
    return "\n".join(lines)


def format_json_report(report: DuplicationReport) -> str:
    """Format report as JSON."""
    data = {
        "summary": report.summary,
        "exact_duplicates": [
            {
                "function": f1.name,
                "file1": str(f1.file),
                "line1": f1.line,
                "file2": str(f2.file),
                "line2": f2.line,
                "body_lines": f1.body_lines,
            }
            for f1, f2 in report.exact_duplicates
        ],
        "near_duplicates": [
            {
                "function1": f1.name,
                "function2": f2.name,
                "file1": str(f1.file),
                "line1": f1.line,
                "file2": str(f2.file),
                "line2": f2.line,
                "similarity": round(sim, 3),
            }
            for f1, f2, sim in report.near_duplicates
        ],
        "similar_names": [
            {
                "function1": f1.name,
                "function2": f2.name,
                "file1": str(f1.file),
                "file2": str(f2.file),
            }
            for f1, f2 in report.similar_names
        ],
    }
    return json.dumps(data, indent=2)


# =============================================================================
# Main Entry Point
# =============================================================================


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Scan Streamlit UI code for duplication"
    )
    parser.add_argument(
        "--utils-only",
        action="store_true",
        help="Only scan utils/ directory",
    )
    parser.add_argument(
        "--show-similar",
        action="store_true",
        help="Show code snippets for similar functions",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=SIMILARITY_THRESHOLD,
        help=f"Similarity threshold for near-duplicates (default: {SIMILARITY_THRESHOLD})",
    )
    parser.add_argument(
        "--min-lines",
        type=int,
        default=MIN_FUNCTION_LINES,
        help=f"Minimum function lines to analyze (default: {MIN_FUNCTION_LINES})",
    )

    args = parser.parse_args()

    # Determine directories to scan
    base_path = Path(__file__).parent.parent
    if args.utils_only:
        dirs_to_scan = [base_path / "streamlit_app" / "utils"]
    else:
        dirs_to_scan = [base_path / d for d in SCAN_DIRS]

    # Collect all functions
    all_functions = []
    for directory in dirs_to_scan:
        if directory.exists():
            if not args.json:
                print(f"Scanning {directory}...")
            all_functions.extend(scan_directory(directory))
        else:
            if not args.json:
                print(f"⚠️  Directory not found: {directory}")

    if not all_functions:
        if args.json:
            print(json.dumps({"error": "No functions found"}))
        else:
            print("No functions found to analyze")
        return 0

    # Analyze
    report = find_duplicates(all_functions)

    # Output
    if args.json:
        print(format_json_report(report))
    else:
        print(format_console_report(report, show_similar=args.show_similar))

    # Exit code based on severity
    if report.exact_duplicates:
        return 1  # Exact duplicates are concerning
    elif len(report.near_duplicates) > 5:
        return 1  # Many near-duplicates
    return 0


if __name__ == "__main__":
    sys.exit(main())
