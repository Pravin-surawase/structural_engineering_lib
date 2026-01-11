# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
IS 456 Clause CLI
=================

Command-line interface for IS 456 clause lookups and traceability.

Usage:
    python -m structural_lib.codes.is456.clause_cli --clause 38.1
    python -m structural_lib.codes.is456.clause_cli --search shear
    python -m structural_lib.codes.is456.clause_cli --category flexure
    python -m structural_lib.codes.is456.clause_cli --report
    python -m structural_lib.codes.is456.clause_cli --stats
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from structural_lib.codes.is456.traceability import (
    generate_traceability_report,
    get_clause_info,
    get_database_metadata,
    list_clauses_by_category,
    search_clauses,
)


def format_clause_info(clause_ref: str, info: dict[str, Any]) -> str:
    """Format clause information for display."""
    lines = [
        "",
        "=" * 70,
        f"IS 456:2000 - Clause {clause_ref}",
        "=" * 70,
        f"Title:    {info.get('title', 'N/A')}",
        f"Section:  {info.get('section', 'N/A')}",
        f"Category: {info.get('category', 'N/A')}",
        "",
        "Text:",
        f"  {info.get('text', 'N/A')}",
    ]

    if "formula" in info:
        lines.extend(["", "Formula:", f"  {info['formula']}"])

    if "formulas" in info:
        lines.append("")
        lines.append("Formulas:")
        formulas = info["formulas"]
        if isinstance(formulas, dict):
            for name, formula in formulas.items():
                if isinstance(formula, dict):
                    for k, v in formula.items():
                        lines.append(f"  {name}.{k}: {v}")
                else:
                    lines.append(f"  {name}: {formula}")

    if "tables" in info:
        lines.extend(["", "Related Tables:"])
        for table in info["tables"]:
            lines.append(f"  - {table}")

    if "keywords" in info:
        lines.extend(["", f"Keywords: {', '.join(info['keywords'])}"])

    if "values" in info:
        lines.append("")
        lines.append("Values:")
        for k, v in info["values"].items():
            lines.append(f"  {k}: {v}")

    if "limits" in info:
        lines.append("")
        lines.append("Limits:")
        for k, v in info["limits"].items():
            lines.append(f"  {k}: {v}")

    lines.append("=" * 70)
    lines.append("")

    return "\n".join(lines)


def cmd_lookup(clause_ref: str) -> int:
    """Look up a specific clause."""
    info = get_clause_info(clause_ref)
    if info is None:
        print(f"❌ Clause '{clause_ref}' not found in IS 456 database.")
        print("\nTip: Use --search to find clauses by keyword.")
        return 1

    print(format_clause_info(clause_ref, info))
    return 0


def cmd_search(keyword: str) -> int:
    """Search clauses by keyword."""
    results = search_clauses(keyword)

    if not results:
        print(f"❌ No clauses found matching '{keyword}'.")
        return 1

    print(f"\n🔍 Found {len(results)} clause(s) matching '{keyword}':\n")
    print("-" * 70)

    for r in results:
        clause_ref = r.get("clause_ref", "?")
        title = r.get("title", "N/A")
        category = r.get("category", "N/A")
        print(f"  Cl. {clause_ref:12} | {title:35} | [{category}]")

    print("-" * 70)
    print("\nUse --clause <ref> for detailed information.")
    return 0


def cmd_category(category: str) -> int:
    """List clauses in a category."""
    results = list_clauses_by_category(category)

    if not results:
        print(f"❌ No clauses found in category '{category}'.")
        print(
            "\nAvailable categories: flexure, shear, detailing, serviceability, materials, analysis, design_limits, durability"
        )
        return 1

    print(f"\n📚 Clauses in category '{category}' ({len(results)} found):\n")
    print("-" * 70)

    for r in sorted(results, key=lambda x: x.get("clause_ref", "")):
        clause_ref = r.get("clause_ref", "?")
        title = r.get("title", "N/A")
        print(f"  Cl. {clause_ref:12} | {title}")

    print("-" * 70)
    return 0


def cmd_report(output_json: bool = False) -> int:
    """Generate traceability report."""
    report = generate_traceability_report()

    if output_json:
        print(json.dumps(report, indent=2))
        return 0

    print("\n📊 IS 456 Traceability Report")
    print("=" * 50)
    print(f"Total clauses in database: {report['total_clauses_in_db']}")
    print(f"Clauses used in code:      {report['total_clauses_used']}")
    print(f"Coverage:                  {report['coverage_percent']:.1f}%")
    print(f"Registered functions:      {len(report['functions'])}")
    print("=" * 50)

    if report["functions"]:
        print("\nFunctions with clause references:")
        print("-" * 50)
        for f in report["functions"]:
            clauses_str = ", ".join(f["clauses"])
            name = f["function"].split(".")[-1]  # Short name
            print(f"  {name:30} -> {clauses_str}")
        print("-" * 50)

    if report["clauses_used"]:
        print(f"\nClauses referenced: {', '.join(report['clauses_used'])}")

    return 0


def cmd_stats() -> int:
    """Show database statistics."""
    metadata = get_database_metadata()

    print("\n📈 IS 456 Clause Database Statistics")
    print("=" * 50)
    print(f"Standard:      {metadata.get('standard', 'N/A')}")
    print(f"Title:         {metadata.get('title', 'N/A')}")
    print(f"Version:       {metadata.get('version', 'N/A')}")
    print(f"Source:        {metadata.get('source', 'N/A')}")
    print(f"Last Updated:  {metadata.get('last_updated', 'N/A')}")
    print(f"Total Clauses: {metadata.get('total_clauses', 'N/A')}")
    print("=" * 50)

    # Category breakdown
    categories = [
        "flexure",
        "shear",
        "detailing",
        "serviceability",
        "materials",
        "analysis",
        "design_limits",
        "durability",
    ]
    print("\nClauses by Category:")
    print("-" * 30)
    for cat in categories:
        clauses = list_clauses_by_category(cat)
        if clauses:
            print(f"  {cat:20}: {len(clauses):3}")
    print("-" * 30)

    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="IS 456:2000 Clause Database CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --clause 38.1          Look up clause 38.1
  %(prog)s --search shear         Search for shear-related clauses
  %(prog)s --category flexure     List all flexure clauses
  %(prog)s --report               Generate traceability report
  %(prog)s --stats                Show database statistics
        """,
    )

    parser.add_argument(
        "--clause",
        "-c",
        metavar="REF",
        help="Look up a specific clause by reference (e.g., 38.1)",
    )
    parser.add_argument(
        "--search",
        "-s",
        metavar="KEYWORD",
        help="Search clauses by keyword",
    )
    parser.add_argument(
        "--category",
        "-g",
        metavar="CAT",
        help="List clauses in a category (flexure, shear, detailing, etc.)",
    )
    parser.add_argument(
        "--report",
        "-r",
        action="store_true",
        help="Generate traceability report",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show database statistics",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format (for --report)",
    )

    args = parser.parse_args()

    # Handle commands
    if args.clause:
        return cmd_lookup(args.clause)
    elif args.search:
        return cmd_search(args.search)
    elif args.category:
        return cmd_category(args.category)
    elif args.report:
        return cmd_report(output_json=args.json)
    elif args.stats:
        return cmd_stats()
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
