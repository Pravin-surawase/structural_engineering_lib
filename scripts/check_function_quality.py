#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""12-point quality checklist for IS 456 functions.

Performs AST-based static analysis on IS 456 code modules to check:
  1. @clause() decorator present
  2. Type-annotated return
  3. Docstring present
  4. Formula comments (# IS 456 Cl)
  5. No float == comparisons
  6. safe_divide usage for division (advisory)
  7. NaN/Inf check present (advisory)
  8. No I/O operations
  9. Units in parameter names
  10. Intermediate variables used (advisory)
  11. validate_* called early (advisory)
  12. Errors as tuple return (advisory)

Usage:
    python scripts/check_function_quality.py                  # Default: --warn mode
    python scripts/check_function_quality.py --strict         # Exit 1 on failures
    python scripts/check_function_quality.py --module flexure # Specific module
    python scripts/check_function_quality.py --json           # Machine-readable output
    python scripts/check_function_quality.py --summary        # Just totals
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import tokenize
from dataclasses import dataclass, field
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
IS456_DIR = REPO_ROOT / "Python" / "structural_lib" / "codes" / "is456"

# Parameter names allowed without unit suffixes
BARE_PARAMS = {
    "fck",
    "fy",
    "pt",
    "pc",
    "n_bars",
    "dia",
    "bars",
    "self",
    "cls",
    "section",
    "materials",
    "loads",
    "geometry",
    "config",
    "options",
    "end_condition",
    "end_condition_b",
    "alpha_n",
    "xu_d",
}

# Known unit suffixes
UNIT_SUFFIXES = {
    "_mm",
    "_mm2",
    "_mm3",
    "_mm4",
    "_kN",
    "_kNm",
    "_mpa",
    "_MPa",
    "_percent",
}

# Advisory checks (warnings, not failures in --warn mode)
ADVISORY_CHECKS = {6, 7, 10, 11, 12}


@dataclass
class CheckResult:
    """Result of a single quality check."""

    check_num: int
    name: str
    passed: bool
    message: str = ""
    advisory: bool = False


@dataclass
class FunctionReport:
    """Quality report for a single function."""

    name: str
    module: str
    line: int
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def score(self) -> tuple[int, int]:
        """Return (passed, total) for non-advisory checks."""
        non_advisory = [c for c in self.checks if not c.advisory]
        passed = sum(1 for c in non_advisory if c.passed)
        return passed, len(non_advisory)

    @property
    def has_failures(self) -> bool:
        """Check if any non-advisory checks failed."""
        return any(not c.passed and not c.advisory for c in self.checks)


# ═══════════════════════════════════════════════════════════════════════════
# AST Checkers
# ═══════════════════════════════════════════════════════════════════════════


class FunctionChecker(ast.NodeVisitor):
    """AST visitor to check quality metrics for a function."""

    def __init__(self, func_node: ast.FunctionDef | ast.AsyncFunctionDef):
        self.func_node = func_node
        self.has_safe_divide = False
        self.has_nan_inf_check = False
        self.has_io_imports = False
        self.has_print_calls = False
        self.has_float_equality = False
        self.has_validate_call = False
        self.assign_count = 0
        self.statement_index = 0

    def check_all(self) -> list[CheckResult]:
        """Run all 12 checks and return results."""
        results = []

        # Check 1: @clause decorator
        has_clause = any(
            isinstance(dec, ast.Call)
            and isinstance(dec.func, ast.Name)
            and dec.func.id == "clause"
            or isinstance(dec, ast.Name)
            and dec.id == "clause"
            for dec in self.func_node.decorator_list
        )
        results.append(
            CheckResult(
                1,
                "@clause() decorator",
                has_clause,
                "" if has_clause else "No @clause decorator found",
            )
        )

        # Check 2: Type-annotated return
        has_return_annotation = self.func_node.returns is not None
        results.append(
            CheckResult(
                2,
                "Type-annotated return",
                has_return_annotation,
                "" if has_return_annotation else "Missing return type annotation",
            )
        )

        # Check 3: Docstring
        docstring = ast.get_docstring(self.func_node)
        has_docstring = docstring is not None and len(docstring.strip()) > 0
        results.append(
            CheckResult(
                3,
                "Docstring present",
                has_docstring,
                "" if has_docstring else "Missing docstring",
            )
        )

        # Check 4: Formula comments - handled separately with tokenize
        # Placeholder here
        results.append(CheckResult(4, "Formula comments", True, "", advisory=True))

        # Check 5-12: Visit the AST
        self.visit(self.func_node)

        # Check 5: No float == comparisons
        results.append(
            CheckResult(
                5,
                "No float == comparisons",
                not self.has_float_equality,
                (
                    "Found float equality comparison (use math.isclose)"
                    if self.has_float_equality
                    else ""
                ),
            )
        )

        # Check 6: safe_divide usage (advisory)
        results.append(
            CheckResult(
                6,
                "safe_divide for division",
                self.has_safe_divide,
                (
                    "Consider using safe_divide for division"
                    if not self.has_safe_divide
                    else ""
                ),
                advisory=True,
            )
        )

        # Check 7: NaN/Inf checks (advisory)
        results.append(
            CheckResult(
                7,
                "NaN/Inf check present",
                self.has_nan_inf_check,
                (
                    "Consider adding NaN/Inf validation"
                    if not self.has_nan_inf_check
                    else ""
                ),
                advisory=True,
            )
        )

        # Check 8: No I/O operations
        has_io = self.has_io_imports or self.has_print_calls
        results.append(
            CheckResult(
                8,
                "No I/O operations",
                not has_io,
                "Found I/O operations (print/file ops)" if has_io else "",
            )
        )

        # Check 9: Units in parameter names
        param_check = self._check_parameter_units()
        results.append(
            CheckResult(9, "Units in parameter names", param_check[0], param_check[1])
        )

        # Check 10: Intermediate variables (advisory)
        has_intermediates = self.assign_count >= 3
        results.append(
            CheckResult(
                10,
                "Intermediate variables used",
                has_intermediates,
                (
                    f"Only {self.assign_count} assignments (consider ≥3 for readability)"
                    if not has_intermediates
                    else ""
                ),
                advisory=True,
            )
        )

        # Check 11: validate_* called early (advisory)
        results.append(
            CheckResult(
                11,
                "validate_* called early",
                self.has_validate_call,
                (
                    "No validate_* call in first 5 statements"
                    if not self.has_validate_call
                    else ""
                ),
                advisory=True,
            )
        )

        # Check 12: Errors as tuple return (advisory)
        has_error_tuple = self._check_error_tuple_return()
        results.append(
            CheckResult(
                12,
                "Errors as tuple return",
                has_error_tuple,
                (
                    "Return annotation doesn't mention tuple with DesignError"
                    if not has_error_tuple
                    else ""
                ),
                advisory=True,
            )
        )

        return results

    def visit_Call(self, node: ast.Call) -> None:
        """Check function calls."""
        # Check for safe_divide
        if isinstance(node.func, ast.Name) and node.func.id == "safe_divide":
            self.has_safe_divide = True

        # Check for NaN/Inf checks
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ("isnan", "isinf"):
                self.has_nan_inf_check = True
        elif isinstance(node.func, ast.Name):
            if node.func.id in ("isnan", "isinf"):
                self.has_nan_inf_check = True

        # Check for print
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            self.has_print_calls = True

        # Check for validate_* calls in first 5 statements
        if (
            self.statement_index < 5
            and isinstance(node.func, ast.Name)
            and node.func.id.startswith("validate")
        ):
            self.has_validate_call = True

        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        """Check for float equality comparisons."""
        for op in node.ops:
            if isinstance(op, (ast.Eq, ast.NotEq)):
                # Check if either side is a float literal
                if isinstance(node.left, ast.Constant) and isinstance(
                    node.left.value, float
                ):
                    self.has_float_equality = True
                for comparator in node.comparators:
                    if isinstance(comparator, ast.Constant) and isinstance(
                        comparator.value, float
                    ):
                        self.has_float_equality = True
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Count assignments for intermediate variable check."""
        self.assign_count += 1
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        """Count augmented assignments."""
        self.assign_count += 1
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:
        """Track statement index for validate check."""
        self.statement_index += 1
        self.generic_visit(node)

    def _check_parameter_units(self) -> tuple[bool, str]:
        """Check if parameters have unit suffixes or are in allowed bare names."""
        args = self.func_node.args
        all_args = []

        # Regular args
        all_args.extend(arg.arg for arg in args.args)
        # Keyword-only args
        all_args.extend(arg.arg for arg in args.kwonlyargs)

        missing_units = []
        for arg_name in all_args:
            # Skip if in bare params
            if arg_name in BARE_PARAMS:
                continue
            # Check if has unit suffix
            if not any(arg_name.endswith(suffix) for suffix in UNIT_SUFFIXES):
                missing_units.append(arg_name)

        if missing_units:
            return False, f"Params missing unit suffix: {', '.join(missing_units)}"
        return True, ""

    def _check_error_tuple_return(self) -> bool:
        """Check if return annotation mentions tuple with error type."""
        if self.func_node.returns is None:
            return False

        # Convert return annotation to string
        return_str = ast.unparse(self.func_node.returns)

        # Check for tuple and Error in return type
        has_tuple = "tuple" in return_str.lower() or "Tuple" in return_str
        has_error = "Error" in return_str

        return has_tuple and has_error


def check_formula_comments(filepath: Path, func_name: str, func_lineno: int) -> bool:
    """Check if function has IS 456 formula comments using tokenize."""
    try:
        with open(filepath, "rb") as f:
            tokens = tokenize.tokenize(f.readline)
            for tok in tokens:
                # Check if comment is within function (rough check)
                if (
                    tok.type == tokenize.COMMENT
                    and tok.start[0] >= func_lineno
                    and re.search(r"IS 456 Cl", tok.string, re.IGNORECASE)
                ):
                    return True
    except Exception:
        pass
    return False


# ═══════════════════════════════════════════════════════════════════════════
# Module Scanning
# ═══════════════════════════════════════════════════════════════════════════


def scan_module(filepath: Path) -> list[FunctionReport]:
    """Scan a Python module and return quality reports for all functions."""
    reports = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source, filename=str(filepath))

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            # Skip private functions
            if node.name.startswith("_"):
                continue

            # Check if function has @clause decorator or is public
            has_clause = any(
                isinstance(dec, ast.Call)
                and isinstance(dec.func, ast.Name)
                and dec.func.id == "clause"
                or isinstance(dec, ast.Name)
                and dec.id == "clause"
                for dec in node.decorator_list
            )

            # Only check functions with @clause decorator
            if not has_clause:
                continue

            # Run checks
            checker = FunctionChecker(node)
            checks = checker.check_all()

            # Update formula comment check
            has_formula_comments = check_formula_comments(
                filepath, node.name, node.lineno
            )
            for check in checks:
                if check.check_num == 4:
                    check.passed = has_formula_comments
                    if not has_formula_comments:
                        check.message = "No '# IS 456 Cl' comments found"
                    check.advisory = True  # Make this advisory

            report = FunctionReport(
                name=node.name,
                module=filepath.relative_to(IS456_DIR).as_posix(),
                line=node.lineno,
                checks=checks,
            )
            reports.append(report)

    except Exception as e:
        print(f"⚠️  Error scanning {filepath}: {e}", file=sys.stderr)

    return reports


def scan_all_modules(
    module_filter: str | None = None,
) -> dict[str, list[FunctionReport]]:
    """Scan all IS 456 modules and return reports grouped by module."""
    all_reports: dict[str, list[FunctionReport]] = {}

    # Find all Python files
    py_files = sorted(IS456_DIR.rglob("*.py"))

    for py_file in py_files:
        # Skip __init__.py and test files
        if py_file.name == "__init__.py" or "test" in py_file.name:
            continue

        # Apply module filter
        if module_filter:
            if (
                module_filter not in py_file.stem
                and module_filter not in py_file.as_posix()
            ):
                continue

        reports = scan_module(py_file)
        if reports:
            module_name = py_file.relative_to(IS456_DIR).as_posix()
            all_reports[module_name] = reports

    return all_reports


# ═══════════════════════════════════════════════════════════════════════════
# Output Formatting
# ═══════════════════════════════════════════════════════════════════════════


def format_human_report(
    all_reports: dict[str, list[FunctionReport]], show_passing: bool = True
) -> str:
    """Format reports as human-readable text."""
    lines = []
    lines.append("Function Quality Report — IS 456 Modules")
    lines.append("═" * 60)

    total_funcs = 0
    total_pass = 0
    total_fail = 0

    for module_name in sorted(all_reports.keys()):
        reports = all_reports[module_name]
        lines.append(f"\nModule: {module_name}")

        for report in reports:
            total_funcs += 1
            score, total_checks = report.score

            if report.has_failures:
                total_fail += 1
                status = "❌"
            else:
                total_pass += 1
                status = "✅"

            lines.append(
                f"  {report.name} {'.' * (40 - len(report.name))} {score}/{total_checks} {status}"
            )

            # Show failed/warning checks
            for check in report.checks:
                if not check.passed and check.message:
                    icon = "⚠️ " if check.advisory else "❌"
                    lines.append(f"    {icon} Check {check.check_num}: {check.message}")

    # Summary
    lines.append("\n" + "─" * 60)
    pass_rate = (total_pass / total_funcs * 100) if total_funcs > 0 else 0
    lines.append(
        f"Summary: {total_funcs} functions checked, {total_pass} pass ({pass_rate:.1f}%), {total_fail} with failures"
    )

    return "\n".join(lines)


def format_json_report(all_reports: dict[str, list[FunctionReport]]) -> str:
    """Format reports as JSON."""
    output = {
        "modules": {},
        "summary": {"total_functions": 0, "passed": 0, "failed": 0},
    }

    for module_name, reports in all_reports.items():
        module_data = []
        for report in reports:
            score, total = report.score
            output["summary"]["total_functions"] += 1
            if report.has_failures:
                output["summary"]["failed"] += 1
            else:
                output["summary"]["passed"] += 1

            module_data.append(
                {
                    "name": report.name,
                    "line": report.line,
                    "score": score,
                    "total_checks": total,
                    "checks": [
                        {
                            "num": c.check_num,
                            "name": c.name,
                            "passed": c.passed,
                            "message": c.message,
                            "advisory": c.advisory,
                        }
                        for c in report.checks
                    ],
                }
            )
        output["modules"][module_name] = module_data

    return json.dumps(output, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
# Main CLI
# ═══════════════════════════════════════════════════════════════════════════


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="12-point quality checker for IS 456 functions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any non-advisory check fails",
    )
    parser.add_argument(
        "--module",
        type=str,
        help='Check only specific module (e.g., "flexure" or "column/biaxial")',
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output", help="Output as JSON"
    )
    parser.add_argument(
        "--summary", action="store_true", help="Show only summary statistics"
    )

    args = parser.parse_args()

    # Scan modules
    all_reports = scan_all_modules(args.module)

    if not all_reports:
        print("No functions found to check.", file=sys.stderr)
        return 1

    # Output results
    if args.json_output:
        print(format_json_report(all_reports))
    elif args.summary:
        total_funcs = sum(len(reports) for reports in all_reports.values())
        total_pass = sum(
            1 for reports in all_reports.values() for r in reports if not r.has_failures
        )
        total_fail = total_funcs - total_pass
        pass_rate = (total_pass / total_funcs * 100) if total_funcs > 0 else 0
        print(
            f"Summary: {total_funcs} functions, {total_pass} pass ({pass_rate:.1f}%), {total_fail} fail"
        )
    else:
        print(format_human_report(all_reports))

    # Determine exit code
    if args.strict:
        has_failures = any(
            r.has_failures for reports in all_reports.values() for r in reports
        )
        return 1 if has_failures else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
