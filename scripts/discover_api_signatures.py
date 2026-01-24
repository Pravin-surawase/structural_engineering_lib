#!/usr/bin/env python3
"""
Discover and display structural_lib API function signatures.

CRITICAL: Run this BEFORE implementing any API wrappers (FastAPI endpoints, etc.)
This prevents guessing parameter names and return types incorrectly.

Usage:
    # Discover specific function signature
    python scripts/discover_api_signatures.py design_beam_is456

    # Discover multiple functions
    python scripts/discover_api_signatures.py design_beam_is456 check_beam_is456

    # Discover all public API functions
    python scripts/discover_api_signatures.py --all

    # Show only design-related functions
    python scripts/discover_api_signatures.py --filter design

    # Output as JSON (for programmatic use)
    python scripts/discover_api_signatures.py design_beam_is456 --json

Examples:
    # Before implementing FastAPI /design/beam endpoint:
    python scripts/discover_api_signatures.py design_beam_is456

    # Before implementing batch processing:
    python scripts/discover_api_signatures.py --filter beam

Created: 2026-01-24 (Session 73)
Purpose: Prevent API signature guessing mistakes
See: docs/research/api-integration-mistakes-analysis.md
"""

from __future__ import annotations

import argparse
import inspect
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, get_type_hints

# Add Python path for structural_lib
sys.path.insert(0, str(Path(__file__).parent.parent / "Python"))


@dataclass
class ParameterInfo:
    """Information about a function parameter."""

    name: str
    annotation: str
    default: str | None
    is_required: bool
    description: str = ""


@dataclass
class SignatureInfo:
    """Complete function signature information."""

    name: str
    module: str
    signature: str
    parameters: list[ParameterInfo]
    return_type: str
    docstring: str | None
    return_attributes: list[str]  # Known attributes of return type


def get_return_type_attributes(return_annotation: Any) -> list[str]:
    """Extract known attributes from return type annotation."""
    type_str = str(return_annotation)

    # Map known return types to their key attributes
    known_types = {
        "ComplianceCaseResult": [
            ".flexure.ast_required",
            ".flexure.mu_lim",
            ".flexure.xu",
            ".flexure.xu_max",
            ".flexure.asc_required",
            ".flexure.is_safe",
            ".shear.tv",
            ".shear.tc",
            ".shear.tc_max",
            ".shear.spacing",
            ".shear.is_safe",
        ],
        "ComplianceReport": [
            ".cases (list of ComplianceCaseResult)",
            ".is_ok",
            ".summary (dict)",
            ".governing_case_id",
            ".governing_utilization",
        ],
        "BeamDetailingResult": [
            ".beam_id",
            ".bars",
            ".stirrups",
            ".development_lengths",
        ],
        "CostOptimizationResult": [
            ".optimal_design.b_mm",
            ".optimal_design.D_mm",
            ".optimal_design.cost_breakdown.total_cost",
            ".alternatives (list)",
            ".candidates_evaluated",
            ".candidates_valid",
            ".savings_percent",
        ],
        "SmartAnalysisResult": [
            ".summary_data (dict: design_status, safety_score, ...)",
            ".suggestions (dict: suggestions list)",
            ".cost (dict: current_cost, optimal_cost)",
            ".sensitivity (dict)",
            ".constructability (dict)",
        ],
        "DesignAndDetailResult": [
            ".design (ComplianceCaseResult)",
            ".detailing (BeamDetailingResult)",
            ".is_ok",
            ".summary()",
        ],
    }

    for type_name, attrs in known_types.items():
        if type_name in type_str:
            return attrs

    return []


def discover_signature(func: Any, func_name: str) -> SignatureInfo:
    """Discover complete signature information for a function."""
    try:
        sig = inspect.signature(func)
    except (ValueError, TypeError):
        return SignatureInfo(
            name=func_name,
            module=getattr(func, "__module__", "unknown"),
            signature="(unable to inspect)",
            parameters=[],
            return_type="unknown",
            docstring=None,
            return_attributes=[],
        )

    parameters = []
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue

        annotation = str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any"
        # Clean up annotation string
        annotation = annotation.replace("typing.", "").replace("<class '", "").replace("'>", "")

        default = None
        is_required = True
        if param.default != inspect.Parameter.empty:
            default = repr(param.default)
            is_required = False

        # Add unit hints based on parameter name
        description = ""
        if name.endswith("_mm"):
            description = "(mm)"
        elif name.endswith("_knm"):
            description = "(kN·m)"
        elif name.endswith("_kn"):
            description = "(kN)"
        elif name.endswith("_nmm2"):
            description = "(N/mm²)"
        elif name == "units":
            description = 'Must be "IS456"'

        parameters.append(ParameterInfo(
            name=name,
            annotation=annotation,
            default=default,
            is_required=is_required,
            description=description,
        ))

    return_annotation = sig.return_annotation
    return_type = str(return_annotation) if return_annotation != inspect.Parameter.empty else "None"
    return_type = return_type.replace("typing.", "").replace("<class '", "").replace("'>", "")

    return_attrs = get_return_type_attributes(return_annotation)

    return SignatureInfo(
        name=func_name,
        module=getattr(func, "__module__", "unknown"),
        signature=str(sig),
        parameters=parameters,
        return_type=return_type,
        docstring=inspect.getdoc(func),
        return_attributes=return_attrs,
    )


def format_signature_text(info: SignatureInfo, verbose: bool = False) -> str:
    """Format signature info as readable text."""
    lines = [
        f"\n{'='*60}",
        f"📦 {info.name}",
        f"{'='*60}",
        f"Module: {info.module}",
        "",
        "Parameters:",
    ]

    for param in info.parameters:
        req = "REQUIRED" if param.is_required else f"default={param.default}"
        desc = f" {param.description}" if param.description else ""
        lines.append(f"  {param.name}: {param.annotation} ({req}){desc}")

    lines.append("")
    lines.append(f"Returns: {info.return_type}")

    if info.return_attributes:
        lines.append("")
        lines.append("Return Type Attributes:")
        for attr in info.return_attributes:
            lines.append(f"  {attr}")

    if verbose and info.docstring:
        lines.append("")
        lines.append("Docstring:")
        for line in info.docstring.split("\n")[:10]:  # First 10 lines
            lines.append(f"  {line}")

    return "\n".join(lines)


def format_signature_json(info: SignatureInfo) -> dict:
    """Format signature info as JSON-serializable dict."""
    return {
        "name": info.name,
        "module": info.module,
        "signature": info.signature,
        "parameters": [
            {
                "name": p.name,
                "type": p.annotation,
                "required": p.is_required,
                "default": p.default,
                "description": p.description,
            }
            for p in info.parameters
        ],
        "return_type": info.return_type,
        "return_attributes": info.return_attributes,
    }


def get_all_api_functions() -> dict[str, Any]:
    """Get all public functions from structural_lib.api."""
    try:
        from structural_lib import api
    except ImportError as e:
        print(f"❌ Cannot import structural_lib.api: {e}")
        print("   Make sure you're running from the project root with .venv activated")
        sys.exit(1)

    functions = {}
    for name in dir(api):
        if name.startswith("_"):
            continue
        obj = getattr(api, name)
        if callable(obj) and not isinstance(obj, type):
            functions[name] = obj

    return functions


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Discover structural_lib API signatures. Run BEFORE implementing wrappers!",
        epilog="See: docs/research/api-integration-mistakes-analysis.md",
    )
    parser.add_argument(
        "functions",
        nargs="*",
        help="Function names to discover (e.g., design_beam_is456)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Show all public API functions",
    )
    parser.add_argument(
        "--filter",
        type=str,
        help="Filter functions by substring (e.g., --filter design)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Include docstrings",
    )

    args = parser.parse_args()

    if not args.functions and not args.all and not args.filter:
        parser.print_help()
        print("\n💡 Examples:")
        print("   python scripts/discover_api_signatures.py design_beam_is456")
        print("   python scripts/discover_api_signatures.py --all")
        print("   python scripts/discover_api_signatures.py --filter design")
        sys.exit(0)

    all_functions = get_all_api_functions()

    # Determine which functions to show
    if args.all:
        target_names = sorted(all_functions.keys())
    elif args.filter:
        target_names = sorted(
            name for name in all_functions.keys()
            if args.filter.lower() in name.lower()
        )
    else:
        target_names = args.functions

    if not target_names:
        print("❌ No matching functions found")
        sys.exit(1)

    results = []
    for name in target_names:
        if name not in all_functions:
            print(f"⚠️  Function '{name}' not found in structural_lib.api")
            print(f"   Available functions containing '{name[:5]}': ", end="")
            matches = [n for n in all_functions if name[:5].lower() in n.lower()]
            print(", ".join(matches[:5]) if matches else "none")
            continue

        info = discover_signature(all_functions[name], name)
        results.append(info)

    if args.json:
        output = [format_signature_json(info) for info in results]
        print(json.dumps(output, indent=2))
    else:
        print("\n" + "="*60)
        print("🔍 API SIGNATURE DISCOVERY")
        print("="*60)
        print("Run this BEFORE implementing API wrappers!")
        print("See: docs/research/api-integration-mistakes-analysis.md")

        for info in results:
            print(format_signature_text(info, verbose=args.verbose))

        print("\n" + "="*60)
        print(f"✅ Discovered {len(results)} function(s)")
        print("="*60)


if __name__ == "__main__":
    main()
