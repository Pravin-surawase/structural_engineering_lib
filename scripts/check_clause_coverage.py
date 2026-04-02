#!/usr/bin/env python3
"""IS 456 clause coverage gap detection.

Scans clauses.json and compares against @clause() decorated functions
to find unimplemented clauses.

This script:
1. Loads all 119 defined clauses from clauses.json
2. Imports all IS 456 modules to populate the @clause() registry
3. Cross-references to identify coverage gaps
4. Generates coverage reports by category

Usage:
    python scripts/check_clause_coverage.py                  # Full report
    python scripts/check_clause_coverage.py --gaps-only      # Only unimplemented
    python scripts/check_clause_coverage.py --category flexure
    python scripts/check_clause_coverage.py --json           # Machine-readable
    python scripts/check_clause_coverage.py --summary        # Just totals
    python scripts/check_clause_coverage.py --implemented    # Only implemented clauses

Exit Codes:
    0 - Success
    1 - Error loading data
    2 - Invalid arguments
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

# Add Python/ to path for imports
sys.path.insert(0, str(REPO_ROOT / "Python"))

CLAUSES_JSON = (
    REPO_ROOT / "Python" / "structural_lib" / "codes" / "is456" / "clauses.json"
)

# ANSI colors for terminal output
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_BLUE = "\033[94m"
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"

# ---------------------------------------------------------------------------
# Core Functions
# ---------------------------------------------------------------------------


def load_clauses_json() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Load clauses.json and return (clauses, annexures, metadata).

    Returns:
        tuple: (clauses_dict, annexures_dict, metadata_dict)

    Raises:
        FileNotFoundError: If clauses.json doesn't exist
        json.JSONDecodeError: If clauses.json is invalid
    """
    if not CLAUSES_JSON.exists():
        raise FileNotFoundError(f"Clauses database not found: {CLAUSES_JSON}")

    with open(CLAUSES_JSON, encoding="utf-8") as f:
        data = json.load(f)

    return (
        data.get("clauses", {}),
        data.get("annexures", {}),
        data.get("metadata", {}),
    )


def get_implemented_clauses() -> dict[str, list[str]]:
    """Import IS 456 modules to populate the clause registry.

    Returns:
        dict: Inverted registry mapping clause_ref -> [func_names]
    """
    import importlib
    import warnings

    # Suppress warnings during import
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        # Import traceability module directly (avoids full structural_lib import)
        traceability = importlib.import_module(
            "structural_lib.codes.is456.traceability"
        )

        # Import all IS 456 modules to trigger @clause() decorators
        # This populates _CLAUSE_REGISTRY in traceability.py
        modules_to_import = [
            # Top-level modules
            "structural_lib.codes.is456.flexure",
            "structural_lib.codes.is456.shear",
            "structural_lib.codes.is456.detailing",
            "structural_lib.codes.is456.torsion",
            "structural_lib.codes.is456.serviceability",
            "structural_lib.codes.is456.materials",
            "structural_lib.codes.is456.slenderness",
            "structural_lib.codes.is456.compliance",
            # Beam submodules
            "structural_lib.codes.is456.beam.flexure",
            "structural_lib.codes.is456.beam.shear",
            "structural_lib.codes.is456.beam.detailing",
            "structural_lib.codes.is456.beam.serviceability",
            "structural_lib.codes.is456.beam.torsion",
            # Column submodules
            "structural_lib.codes.is456.column.axial",
            "structural_lib.codes.is456.column.uniaxial",
            "structural_lib.codes.is456.column.biaxial",
            "structural_lib.codes.is456.column.slenderness",
        ]

        for module_name in modules_to_import:
            try:
                importlib.import_module(module_name)
            except (ImportError, AttributeError, KeyError):
                # Module might not exist yet or have missing dependencies - that's OK
                pass

    # Get the registry: {func_qualname: [clause_refs]}
    registry = traceability.get_all_registered_functions()

    # Invert it: {clause_ref: [func_names]}
    inverted: dict[str, list[str]] = defaultdict(list)
    for func_name, clause_refs in registry.items():
        for ref in clause_refs:
            inverted[ref].append(func_name)

    return dict(inverted)


def build_coverage_matrix(
    all_clauses: dict[str, Any],
    annexures: dict[str, Any],
    implemented: dict[str, list[str]],
) -> list[dict[str, Any]]:
    """Build coverage matrix: which clauses are implemented.

    Args:
        all_clauses: Dict of clause_id -> clause_info from clauses.json
        annexures: Dict of annexure_id -> annexure_info from clauses.json
        implemented: Dict of clause_ref -> [func_names]

    Returns:
        List of dicts with coverage info for each clause
    """
    results = []

    # Process regular clauses
    for clause_id, info in all_clauses.items():
        functions = implemented.get(clause_id, [])
        results.append(
            {
                "clause": clause_id,
                "title": info.get("title", ""),
                "category": info.get("category", "unknown"),
                "section": info.get("section", ""),
                "implemented": len(functions) > 0,
                "functions": functions,
                "type": "clause",
            }
        )

    # Process annexures
    for annex_id, info in annexures.items():
        functions = implemented.get(annex_id, [])
        # Check both with and without "Annex " prefix
        if not functions and annex_id.startswith("G-"):
            functions = implemented.get(f"Annex {annex_id}", [])
        results.append(
            {
                "clause": f"Annex {annex_id}",
                "title": info.get("title", ""),
                "category": "annexure",
                "section": info.get("section", "Annexures"),
                "implemented": len(functions) > 0,
                "functions": functions,
                "type": "annexure",
            }
        )

    return results


def group_by_category(matrix: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group coverage matrix by category.

    Args:
        matrix: Coverage matrix from build_coverage_matrix()

    Returns:
        Dict mapping category -> list of clause entries
    """
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in matrix:
        category = entry["category"]
        grouped[category].append(entry)
    return dict(grouped)


# ---------------------------------------------------------------------------
# Output Formatters
# ---------------------------------------------------------------------------


def format_summary(matrix: list[dict[str, Any]], metadata: dict[str, Any]) -> str:
    """Format summary statistics only."""
    total = len(matrix)
    implemented = sum(1 for item in matrix if item["implemented"])
    gaps = total - implemented
    pct = round(implemented / total * 100, 1) if total > 0 else 0

    return f"""{implemented}/{total} clauses implemented ({pct}%)
Gaps: {gaps}"""


def format_json_output(matrix: list[dict[str, Any]], metadata: dict[str, Any]) -> str:
    """Format full JSON output."""
    total = len(matrix)
    implemented = sum(1 for item in matrix if item["implemented"])

    output = {
        "metadata": metadata,
        "summary": {
            "total_clauses": total,
            "implemented": implemented,
            "gaps": total - implemented,
            "coverage_pct": round(implemented / total * 100, 1) if total > 0 else 0,
        },
        "clauses": matrix,
    }

    return json.dumps(output, indent=2, ensure_ascii=False)


def format_detailed_report(
    matrix: list[dict[str, Any]],
    metadata: dict[str, Any],
    gaps_only: bool = False,
    implemented_only: bool = False,
    filter_category: str | None = None,
) -> str:
    """Format detailed coverage report.

    Args:
        matrix: Coverage matrix
        metadata: Metadata from clauses.json
        gaps_only: Only show unimplemented clauses
        implemented_only: Only show implemented clauses
        filter_category: Filter by category (e.g., "flexure", "shear")

    Returns:
        Formatted report string
    """
    # Apply filters
    filtered = matrix
    if gaps_only:
        filtered = [item for item in filtered if not item["implemented"]]
    if implemented_only:
        filtered = [item for item in filtered if item["implemented"]]
    if filter_category:
        filtered = [item for item in filtered if item["category"] == filter_category]

    # Group by category
    grouped = group_by_category(filtered)

    # Calculate statistics
    total = len(matrix)
    implemented_count = sum(1 for item in matrix if item["implemented"])
    gaps_count = total - implemented_count
    pct = round(implemented_count / total * 100, 1) if total > 0 else 0

    # Build report
    lines = []
    lines.append(f"{COLOR_BOLD}IS 456:2000 Clause Coverage Report{COLOR_RESET}")
    lines.append("═" * 70)
    lines.append(f"Total Clauses:     {total}")
    lines.append(
        f"Implemented:       {COLOR_GREEN}{implemented_count}{COLOR_RESET} ({pct}%)"
    )
    lines.append(
        f"Gaps:              {COLOR_RED}{gaps_count}{COLOR_RESET} ({100 - pct}%)"
    )
    lines.append(f"Standard:          {metadata.get('title', 'IS 456:2000')}")
    lines.append(f"Version:           {metadata.get('version', 'Unknown')}")
    lines.append("")

    # Show by category
    lines.append(f"{COLOR_BOLD}Coverage by Category{COLOR_RESET}")
    lines.append("─" * 70)

    # Sort categories by coverage percentage (descending)
    category_stats = []
    for category in sorted(grouped.keys()):
        items = grouped[category]
        cat_total = len(items)
        cat_impl = sum(1 for item in items if item["implemented"])
        cat_pct = round(cat_impl / cat_total * 100) if cat_total > 0 else 0
        category_stats.append((category, cat_impl, cat_total, cat_pct, items))

    category_stats.sort(key=lambda x: x[3], reverse=True)

    for category, cat_impl, cat_total, cat_pct, items in category_stats:
        # Progress bar
        bar_width = 16
        filled = int(round(cat_pct / 100 * bar_width))
        bar = "█" * filled + "░" * (bar_width - filled)

        # Status emoji
        if cat_pct == 100:
            status = f"{COLOR_GREEN}✅{COLOR_RESET}"
        elif cat_pct >= 50:
            status = f"{COLOR_YELLOW}🟡{COLOR_RESET}"
        else:
            status = f"{COLOR_RED}🔴{COLOR_RESET}"

        lines.append(
            f"{category:15s} {cat_impl:3d}/{cat_total:<3d}  {bar}  {cat_pct:3d}%  {status}"
        )

        # Show gaps for this category if not 100%
        if cat_pct < 100 and not implemented_only:
            gaps = [item for item in items if not item["implemented"]]
            if gaps and len(gaps) <= 5:  # Only show first 5 gaps
                for gap in gaps[:5]:
                    lines.append(
                        f"  {COLOR_RED}Gap{COLOR_RESET}: {gap['clause']} — {gap['title']}"
                    )
            elif gaps:
                lines.append(
                    f"  {COLOR_RED}Gap{COLOR_RESET}: {len(gaps)} clauses unimplemented"
                )

    lines.append("")

    # Show implemented clauses with functions (if not gaps_only)
    if not gaps_only and implemented_only or (not gaps_only and not filter_category):
        lines.append(f"{COLOR_BOLD}Implemented Clauses with Functions{COLOR_RESET}")
        lines.append("─" * 70)

        impl_items = [item for item in matrix if item["implemented"]]
        # Sort by clause ID
        impl_items.sort(key=lambda x: x["clause"])

        for item in impl_items[:20]:  # Show first 20
            funcs_str = ", ".join(item["functions"][:3])  # Show max 3 funcs
            if len(item["functions"]) > 3:
                funcs_str += f" (+{len(item['functions']) - 3} more)"
            lines.append(f"{item['clause']:10s} → {funcs_str}")

        if len(impl_items) > 20:
            lines.append(f"\n... and {len(impl_items) - 20} more implemented clauses")

    # Show gaps detail if requested
    if gaps_only:
        lines.append(f"{COLOR_BOLD}Unimplemented Clauses{COLOR_RESET}")
        lines.append("─" * 70)

        gaps = [item for item in filtered if not item["implemented"]]
        gaps.sort(key=lambda x: (x["category"], x["clause"]))

        current_category = None
        for gap in gaps:
            if gap["category"] != current_category:
                current_category = gap["category"]
                lines.append(f"\n{COLOR_BLUE}{current_category.upper()}{COLOR_RESET}")
            lines.append(f"  {gap['clause']:10s} — {gap['title']}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="IS 456 clause coverage gap detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Full detailed report
  %(prog)s --gaps-only              # Only show unimplemented clauses
  %(prog)s --implemented            # Only show implemented clauses
  %(prog)s --category flexure       # Filter by category
  %(prog)s --json                   # JSON output
  %(prog)s --summary                # Summary stats only
        """,
    )

    parser.add_argument(
        "--gaps-only",
        action="store_true",
        help="Only show unimplemented clauses",
    )
    parser.add_argument(
        "--implemented",
        action="store_true",
        help="Only show implemented clauses",
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Filter by category (e.g., flexure, shear, columns)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show only summary statistics",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.gaps_only and args.implemented:
        print(
            "Error: --gaps-only and --implemented are mutually exclusive",
            file=sys.stderr,
        )
        return 2

    try:
        # Load data
        clauses, annexures, metadata = load_clauses_json()
        implemented = get_implemented_clauses()

        # Build coverage matrix
        matrix = build_coverage_matrix(clauses, annexures, implemented)

        # Generate output
        if args.json:
            print(format_json_output(matrix, metadata))
        elif args.summary:
            print(format_summary(matrix, metadata))
        else:
            report = format_detailed_report(
                matrix,
                metadata,
                gaps_only=args.gaps_only,
                implemented_only=args.implemented,
                filter_category=args.category,
            )
            print(report)

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error parsing clauses.json: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
