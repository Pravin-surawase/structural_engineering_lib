#!/usr/bin/env python3
"""Report standard-namespaced clause/reference decorator registration.

This is a traceability report. Registration does not prove implementation,
numerical verification, provenance, whole-standard coverage, or engineering
approval. Capability scope is reported separately by ``parity_dashboard.py``.

Usage:
    ./scripts/python_runtime.sh scripts/check_clause_coverage.py
    ./scripts/python_runtime.sh scripts/check_clause_coverage.py --standard IS456
    ./scripts/python_runtime.sh scripts/check_clause_coverage.py --gaps-only
    ./scripts/python_runtime.sh scripts/check_clause_coverage.py --registered
    ./scripts/python_runtime.sh scripts/check_clause_coverage.py --json
    ./scripts/python_runtime.sh scripts/check_clause_coverage.py --summary
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from typing import Any

from _lib.indian_code_manifest import load_manifest

COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"


def _selected_standards(
    manifest: dict[str, Any], selector: str | None
) -> list[dict[str, Any]]:
    standards = manifest["standards"]
    if selector is None:
        return standards
    normalized = selector.replace(" ", "").upper()
    selected = [
        standard
        for standard in standards
        if normalized
        in {
            standard["standard_id"].replace(" ", "").upper(),
            standard["namespace"].replace(" ", "").upper(),
        }
    ]
    if not selected:
        available = ", ".join(item["namespace"] for item in standards)
        raise ValueError(f"Unknown standard {selector!r}; available: {available}")
    return selected


def _filtered_references(
    standard: dict[str, Any],
    *,
    discrepancies_only: bool = False,
    registered_only: bool = False,
    category: str | None = None,
) -> list[dict[str, Any]]:
    references = standard["references"]
    if discrepancies_only:
        references = [
            item for item in references if item["registration_status"] != "REGISTERED"
        ]
    if registered_only:
        references = [
            item for item in references if item["registration_status"] == "REGISTERED"
        ]
    if category:
        references = [item for item in references if item["category"] == category]
    return references


def _aggregate_summary(standards: list[dict[str, Any]]) -> dict[str, Any]:
    known = sum(item["registration_summary"]["known_references"] for item in standards)
    registered = sum(
        item["registration_summary"]["registered_known_references"]
        for item in standards
    )
    metadata_only = sum(
        item["registration_summary"]["metadata_only_references"]
        for item in standards
    )
    registration_only = sum(
        item["registration_summary"]["registration_only_references"]
        for item in standards
    )
    return {
        "known_references": known,
        "registered_known_references": registered,
        "metadata_only_references": metadata_only,
        "registration_only_references": registration_only,
        "registration_pct": round(registered / known * 100, 1) if known else None,
    }


def build_report(
    manifest: dict[str, Any],
    *,
    standard_selector: str | None = None,
    discrepancies_only: bool = False,
    registered_only: bool = False,
    category: str | None = None,
) -> dict[str, Any]:
    """Build the machine-readable registration report."""
    standards = _selected_standards(manifest, standard_selector)
    report_standards = []
    for standard in standards:
        report_standards.append(
            {
                "standard_id": standard["standard_id"],
                "namespace": standard["namespace"],
                "edition": standard["edition"],
                "summary": standard["registration_summary"],
                "references": _filtered_references(
                    standard,
                    discrepancies_only=discrepancies_only,
                    registered_only=registered_only,
                    category=category,
                ),
            }
        )
    return {
        "schema_version": manifest["schema_version"],
        "report_kind": "STANDARD_REFERENCE_DECORATOR_REGISTRATION",
        "claim_boundary": manifest["claim_boundaries"]["registration_status"],
        "summary": _aggregate_summary(standards),
        "standards": report_standards,
    }


def format_summary(report: dict[str, Any]) -> str:
    """Format compact, explicitly bounded registration statistics."""
    lines = [report["claim_boundary"]]
    for standard in report["standards"]:
        summary = standard["summary"]
        pct = summary["registration_pct"]
        pct_text = "not applicable" if pct is None else f"{pct}%"
        lines.append(
            f"{standard['namespace']}: "
            f"{summary['registered_known_references']}/"
            f"{summary['known_references']} known references registered ({pct_text}); "
            f"metadata-only={summary['metadata_only_references']}; "
            f"registration-only={summary['registration_only_references']}"
        )
    return "\n".join(lines)


def format_json_output(report: dict[str, Any]) -> str:
    """Format the complete report as JSON."""
    return json.dumps(report, indent=2, ensure_ascii=False)


def _status_color(status: str) -> str:
    if status == "REGISTERED":
        return COLOR_GREEN
    if status == "REGISTRATION_ONLY":
        return COLOR_BLUE
    return COLOR_YELLOW


def format_detailed_report(report: dict[str, Any]) -> str:
    """Format a detailed report without calling registrations implemented."""
    lines = [
        f"{COLOR_BOLD}Indian-code Reference Registration Report{COLOR_RESET}",
        "═" * 78,
        report["claim_boundary"],
        "",
    ]
    for standard in report["standards"]:
        summary = standard["summary"]
        pct = summary["registration_pct"]
        pct_text = "not applicable" if pct is None else f"{pct}%"
        lines.extend(
            [
                f"{COLOR_BOLD}{standard['namespace']}{COLOR_RESET}",
                f"Known references:       {summary['known_references']}",
                f"Registered known:       {COLOR_GREEN}{summary['registered_known_references']}{COLOR_RESET} ({pct_text})",
                f"Metadata only:          {COLOR_YELLOW}{summary['metadata_only_references']}{COLOR_RESET}",
                f"Registration only:      {COLOR_BLUE}{summary['registration_only_references']}{COLOR_RESET}",
            ]
        )
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for reference in standard["references"]:
            grouped[reference["category"]].append(reference)
        for category in sorted(grouped):
            lines.append(f"\n  {category}")
            for reference in grouped[category]:
                status = reference["registration_status"]
                functions = ", ".join(reference["functions"][:2])
                if len(reference["functions"]) > 2:
                    functions += f" (+{len(reference['functions']) - 2} more)"
                suffix = f" -> {functions}" if functions else ""
                lines.append(
                    f"    {_status_color(status)}{status:17s}{COLOR_RESET} "
                    f"{reference['reference_id']}{suffix}"
                )
        lines.append("")
    return "\n".join(lines).rstrip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Standard-namespaced decorator registration report"
    )
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--gaps-only",
        action="store_true",
        help="Show metadata-only and registration-only discrepancies",
    )
    selection.add_argument(
        "--registered",
        action="store_true",
        help="Show only registered known references",
    )
    selection.add_argument(
        "--implemented",
        action="store_true",
        help="Deprecated alias for --registered; registration is not implementation",
    )
    parser.add_argument("--standard", help="Standard id or namespace")
    parser.add_argument("--category", help="Filter displayed references by category")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--summary", action="store_true", help="Show summary only")
    args = parser.parse_args()

    try:
        report = build_report(
            load_manifest(),
            standard_selector=args.standard,
            discrepancies_only=args.gaps_only,
            registered_only=args.registered or args.implemented,
            category=args.category,
        )
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(format_json_output(report))
    elif args.summary:
        print(format_summary(report))
    else:
        print(format_detailed_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
