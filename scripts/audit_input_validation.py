#!/usr/bin/env python3
"""
Audit Input Validation Coverage for structural_lib.

This script scans the codebase to identify:
1. Public API functions that accept user input
2. Which inputs are validated vs unvalidated
3. Validation coverage percentage

Part of TASK-274: Security Hardening Baseline

Usage:
    python scripts/audit_input_validation.py
    python scripts/audit_input_validation.py --verbose
    python scripts/audit_input_validation.py --json output.json
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class FunctionInfo:
    """Information about a function and its validation status."""

    name: str
    file: str
    line: int
    parameters: list[str]
    validated_params: list[str] = field(default_factory=list)
    has_type_hints: bool = False
    has_docstring: bool = False
    is_public: bool = True
    validation_calls: list[str] = field(default_factory=list)

    @property
    def coverage(self) -> float:
        """Calculate validation coverage as percentage."""
        if not self.parameters:
            return 100.0
        return (len(self.validated_params) / len(self.parameters)) * 100


class ValidationAuditor(ast.NodeVisitor):
    """AST visitor to analyze validation patterns in Python code."""

    # Known validation function names
    VALIDATION_FUNCTIONS = {
        "validate_dimensions",
        "validate_materials",
        "validate_cover",
        "validate_reinforcement",
        "validate_loads",
        "validate_input",
        "validate_beam_input",
        "validate",
        "_validate",
        "check_positive",
        "check_range",
        "ensure_positive",
    }

    # Known validation patterns in code
    VALIDATION_PATTERNS = {
        "raise ValueError",
        "raise TypeError",
        "raise DesignError",
        "if .* <= 0",
        "if .* < 0",
        "if not isinstance",
    }

    def __init__(self, filename: str):
        self.filename = filename
        self.functions: list[FunctionInfo] = []
        self.current_function: Optional[FunctionInfo] = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        # Skip private/internal functions
        is_public = not node.name.startswith("_")

        # Get parameters (skip self, cls)
        params = []
        for arg in node.args.args:
            if arg.arg not in ("self", "cls"):
                params.append(arg.arg)

        # Check for type hints
        has_hints = any(arg.annotation for arg in node.args.args)

        # Check for docstring
        has_docstring = (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        )

        func_info = FunctionInfo(
            name=node.name,
            file=self.filename,
            line=node.lineno,
            parameters=params,
            has_type_hints=has_hints,
            has_docstring=has_docstring,
            is_public=is_public,
        )

        self.current_function = func_info

        # Visit function body to find validation calls
        self.generic_visit(node)

        self.functions.append(func_info)
        self.current_function = None

    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls to find validation invocations."""
        if self.current_function is None:
            return

        # Get function name being called
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name and func_name in self.VALIDATION_FUNCTIONS:
            self.current_function.validation_calls.append(func_name)

            # Try to identify which parameters are being validated
            for arg in node.args:
                if isinstance(arg, ast.Name):
                    if arg.id in self.current_function.parameters:
                        if arg.id not in self.current_function.validated_params:
                            self.current_function.validated_params.append(arg.id)

        self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> None:
        """Track raise statements as potential validation."""
        if self.current_function is None:
            return

        if node.exc:
            # Track that this function has validation logic
            if isinstance(node.exc, ast.Call):
                if isinstance(node.exc.func, ast.Name):
                    exc_type = node.exc.func.id
                    if exc_type in ("ValueError", "TypeError", "DesignError"):
                        self.current_function.validation_calls.append(
                            f"raise {exc_type}"
                        )

        self.generic_visit(node)


def audit_file(filepath: Path) -> list[FunctionInfo]:
    """Audit a single Python file for validation coverage."""
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"  ⚠️ Syntax error in {filepath}: {e}", file=sys.stderr)
        return []

    auditor = ValidationAuditor(str(filepath))
    auditor.visit(tree)
    return auditor.functions


def audit_directory(directory: Path, verbose: bool = False) -> list[FunctionInfo]:
    """Audit all Python files in a directory."""
    all_functions = []

    # Target the structural_lib source directory
    lib_dir = directory / "Python" / "structural_lib"
    if not lib_dir.exists():
        print(f"Directory not found: {lib_dir}", file=sys.stderr)
        return []

    # Files to audit (main modules, not stubs or migrations)
    target_files = [
        "api.py",
        "validation.py",
        "beam_pipeline.py",
        "job_runner.py",
        "codes/is456/flexure.py",
        "codes/is456/shear.py",
        "codes/is456/detailing.py",
        "codes/is456/serviceability.py",
        "codes/is456/ductile.py",
        "codes/is456/tables.py",
        "codes/is456/materials.py",
    ]

    for target in target_files:
        filepath = lib_dir / target
        if filepath.exists():
            if verbose:
                print(f"  Scanning: {filepath.relative_to(directory)}")
            functions = audit_file(filepath)
            all_functions.extend(functions)

    return all_functions


def generate_report(
    functions: list[FunctionInfo], verbose: bool = False
) -> dict:
    """Generate audit report."""
    # Filter to public functions only
    public_funcs = [f for f in functions if f.is_public]

    # Calculate statistics
    total_public = len(public_funcs)
    with_validation = sum(1 for f in public_funcs if f.validation_calls)
    with_types = sum(1 for f in public_funcs if f.has_type_hints)
    with_docs = sum(1 for f in public_funcs if f.has_docstring)

    # Calculate average coverage
    if total_public > 0:
        avg_coverage = sum(f.coverage for f in public_funcs) / total_public
    else:
        avg_coverage = 0

    # Identify high-risk functions (public, no validation, has params)
    high_risk = [
        f
        for f in public_funcs
        if not f.validation_calls and f.parameters and not f.name.startswith("get_")
    ]

    report = {
        "summary": {
            "total_public_functions": total_public,
            "functions_with_validation": with_validation,
            "functions_with_type_hints": with_types,
            "functions_with_docstrings": with_docs,
            "average_coverage_percent": round(avg_coverage, 1),
            "high_risk_count": len(high_risk),
        },
        "high_risk_functions": [
            {
                "name": f.name,
                "file": f.file,
                "line": f.line,
                "parameters": f.parameters,
            }
            for f in high_risk[:10]  # Top 10
        ],
        "coverage_by_file": {},
    }

    # Group by file
    by_file: dict[str, list[FunctionInfo]] = {}
    for f in public_funcs:
        if f.file not in by_file:
            by_file[f.file] = []
        by_file[f.file].append(f)

    for file, funcs in by_file.items():
        validated = sum(1 for f in funcs if f.validation_calls)
        report["coverage_by_file"][file] = {
            "total": len(funcs),
            "validated": validated,
            "percent": round((validated / len(funcs)) * 100, 1) if funcs else 0,
        }

    return report


def print_report(report: dict, verbose: bool = False) -> None:
    """Print human-readable report."""
    summary = report["summary"]

    print()
    print("=" * 60)
    print("  INPUT VALIDATION AUDIT REPORT")
    print("=" * 60)
    print()

    print("📊 Summary")
    print("-" * 40)
    print(f"  Total public functions:     {summary['total_public_functions']}")
    print(f"  With validation calls:      {summary['functions_with_validation']}")
    print(f"  With type hints:            {summary['functions_with_type_hints']}")
    print(f"  With docstrings:            {summary['functions_with_docstrings']}")
    print(f"  Average coverage:           {summary['average_coverage_percent']}%")
    print(f"  High-risk functions:        {summary['high_risk_count']}")
    print()

    # Coverage by file
    print("📁 Coverage by File")
    print("-" * 40)
    for file, stats in sorted(report["coverage_by_file"].items()):
        short_file = Path(file).name
        bar_len = int(stats["percent"] / 5)  # 20 char max
        bar = "█" * bar_len + "░" * (20 - bar_len)
        print(f"  {short_file:25} [{bar}] {stats['percent']:5.1f}%")
    print()

    # High-risk functions
    if report["high_risk_functions"]:
        print("⚠️  High-Risk Functions (no validation)")
        print("-" * 40)
        for f in report["high_risk_functions"]:
            print(f"  • {f['name']} ({Path(f['file']).name}:{f['line']})")
            print(f"    Params: {', '.join(f['parameters'])}")
        print()

    # Grade
    coverage = summary["average_coverage_percent"]
    if coverage >= 90:
        grade = "A"
        color = "✅"
    elif coverage >= 80:
        grade = "B"
        color = "✅"
    elif coverage >= 70:
        grade = "C"
        color = "⚠️"
    elif coverage >= 60:
        grade = "D"
        color = "⚠️"
    else:
        grade = "F"
        color = "❌"

    print(f"🎯 Overall Grade: {color} {grade} ({coverage}% coverage)")
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Audit input validation coverage for structural_lib"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output"
    )
    parser.add_argument(
        "--json", "-j", type=str, help="Output report as JSON to specified file"
    )
    parser.add_argument(
        "--directory",
        "-d",
        type=str,
        default=".",
        help="Project root directory",
    )

    args = parser.parse_args()

    # Audit the codebase
    project_dir = Path(args.directory).resolve()
    print(f"🔍 Auditing input validation in {project_dir}")

    functions = audit_directory(project_dir, verbose=args.verbose)

    if not functions:
        print("No functions found to audit.")
        return 1

    # Generate report
    report = generate_report(functions, verbose=args.verbose)

    # Output
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {args.json}")
    else:
        print_report(report, verbose=args.verbose)

    # Exit code based on high-risk count
    if report["summary"]["high_risk_count"] > 10:
        return 1  # Too many high-risk functions
    return 0


if __name__ == "__main__":
    sys.exit(main())
