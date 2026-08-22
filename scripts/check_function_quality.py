#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Outcome-critical and advisory quality checks for IS 456 functions.

Performs eleven AST-based checks on IS 456 code modules. Historical check IDs
2-12 are retained for report compatibility:
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

When to use: after changing IS 456 functions or before their quality-gate review.
``@clause`` is the inventory selector, not a tautological per-function check.
The ``--module`` filter matches paths relative to the IS 456 source root, so a
word in an absolute worktree directory cannot broaden the scan. This checker is
static contract evidence; it does not replace an independent numerical benchmark.

Usage:
    ./scripts/python_runtime.sh scripts/check_function_quality.py
    ./scripts/python_runtime.sh scripts/check_function_quality.py --strict
    ./scripts/python_runtime.sh scripts/check_function_quality.py --module flexure
    ./scripts/python_runtime.sh scripts/check_function_quality.py --json
    ./scripts/python_runtime.sh scripts/check_function_quality.py --summary
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
    "reinforcement",
    "loads",
    "geometry",
    "footing_input",
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
    "_kn",
    "_knm",
    "_kpa",
    "_mpa",
    "_MPa",
    "_percent",
    "_nmm2",
    "_deg",
    "_days",
    "_months",
}

# Public legacy signatures cannot be renamed merely to satisfy a checker. These
# exact function-level declarations make the retained dimensional contract
# reviewable without turning every short scalar name into a global exemption.
LEGACY_PARAMETER_UNITS: dict[str, dict[str, str]] = {
    "beam/detailing.py:calculate_development_length": {"bar_dia": "mm"},
    "beam/detailing.py:calculate_lap_length": {"bar_dia": "mm"},
    "beam/detailing.py:get_min_bend_radius": {"bar_dia": "mm"},
    "beam/detailing.py:calculate_standard_hook": {"bar_dia": "mm"},
    "beam/detailing.py:calculate_anchorage_length": {
        "bar_dia": "mm",
        "available_length": "mm",
    },
    "beam/detailing.py:calculate_stirrup_anchorage": {"stirrup_dia": "mm"},
    "beam/detailing.py:check_anchorage_at_simple_support": {
        "bar_dia": "mm",
        "support_width": "mm",
        "cover": "mm",
    },
    "beam/detailing.py:check_side_face_reinforcement": {
        "D": "mm",
        "b": "mm",
        "cover": "mm",
    },
    "beam/flexure.py:calculate_mu_lim": {"b": "mm", "d": "mm"},
    "beam/flexure.py:calculate_ast_required": {"b": "mm", "d": "mm"},
    "beam/flexure.py:design_singly_reinforced": {
        "b": "mm",
        "d": "mm",
        "d_total": "mm",
    },
    "beam/flexure.py:design_doubly_reinforced": {
        "b": "mm",
        "d": "mm",
        "d_dash": "mm",
        "d_total": "mm",
    },
    "beam/flexure.py:calculate_mu_lim_flanged": {
        "bw": "mm",
        "bf": "mm",
        "d": "mm",
        "Df": "mm",
    },
    "beam/flexure.py:design_flanged_beam": {
        "bw": "mm",
        "bf": "mm",
        "d": "mm",
        "Df": "mm",
        "d_total": "mm",
        "d_dash": "mm",
    },
    "beam/shear.py:calculate_tv": {"b": "mm", "d": "mm"},
    "beam/shear.py:design_shear": {"b": "mm", "d": "mm", "asv": "mm2"},
    "beam/torsion.py:calculate_equivalent_shear": {"b": "mm"},
    "beam/torsion.py:calculate_equivalent_moment": {"d": "mm", "b": "mm"},
    "beam/torsion.py:calculate_torsion_shear_stress": {"b": "mm", "d": "mm"},
    "beam/torsion.py:calculate_torsion_stirrup_area": {
        "b": "mm",
        "d": "mm",
        "b1": "mm",
        "d1": "mm",
        "tc": "N/mm2",
    },
    "beam/torsion.py:calculate_longitudinal_torsion_steel": {
        "b1": "mm",
        "d1": "mm",
        "sv": "mm",
    },
    "beam/torsion.py:design_torsion": {
        "b": "mm",
        "D": "mm",
        "d": "mm",
        "cover": "mm",
        "stirrup_dia": "mm",
    },
}

EXACT_FLOAT_COMPARISON_CONTRACTS: dict[str, dict[str, str]] = {
    "column/uniaxial.py:pm_interaction_curve": {
        "rationale": "Deduplicate the analytically assigned pure-axial endpoint; this is not a safety threshold.",
        "test": "Python/tests/codes/is456/column/test_pm_interaction.py::test_pu_0_cap_last_point_is_pu_0",
    },
    "common/stress_blocks.py:steel_stress_from_strain_5point": {
        "rationale": "Preserve the exact constitutive origin before sign-dependent interpolation.",
        "test": "Python/tests/unit/test_coverage_boost_is456.py::test_steel_stress_5point_zero_strain_returns_zero",
    },
    "slab/two_way_complete.py:design_two_way_slab_panel": {
        "rationale": "Zero is produced by an exact enum factor for corners where torsion is not required.",
        "test": "Python/tests/codes/is456/slab/test_extended_workflows.py::test_free_to_lift_simple_support_has_no_restrained_corner_torsion",
    },
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

    def __init__(
        self,
        func_node: ast.FunctionDef | ast.AsyncFunctionDef,
        module: str | None = None,
    ):
        self.func_node = func_node
        self.module = module
        self.has_safe_divide = False
        self.has_nan_inf_check = False
        self.has_io_imports = False
        self.has_print_calls = False
        self.has_float_equality = False
        self.has_validate_call = False
        self.assign_count = 0
        self.statement_index = 0

    def check_all(self) -> list[CheckResult]:
        """Run the eleven retained checks and return results."""
        results = []

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
        float_comparison_ok, float_comparison_message = (
            self._check_float_comparison_contract()
        )
        results.append(
            CheckResult(
                5,
                "Reviewed float equality",
                float_comparison_ok,
                float_comparison_message,
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
            and node.func.id.lstrip("_").startswith("validate")
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
        all_args: list[ast.arg] = []

        all_args.extend(args.posonlyargs)
        all_args.extend(args.args)
        all_args.extend(args.kwonlyargs)

        missing_units = []
        function_key = (
            f"{self.module}:{self.func_node.name}" if self.module is not None else None
        )
        declared_units = LEGACY_PARAMETER_UNITS.get(function_key or "", {})
        for arg in all_args:
            arg_name = arg.arg
            # Skip structured objects and dimensionless sample/count controls.
            if (
                arg_name in BARE_PARAMS
                or arg_name in declared_units
                or self._is_semantic_parameter(arg)
            ):
                continue
            # Check if has unit suffix
            normalized_name = arg_name.lower()
            if not any(normalized_name.endswith(suffix) for suffix in UNIT_SUFFIXES):
                missing_units.append(arg_name)

        if missing_units:
            return False, f"Params missing unit suffix: {', '.join(missing_units)}"
        return True, ""

    def _is_semantic_parameter(self, arg: ast.arg) -> bool:
        """Recognize non-dimensional typed objects and named scalar controls."""
        name = arg.arg.lower().lstrip("_")
        if (
            name.startswith(("n_", "num_", "is_", "has_", "use_"))
            or name.endswith(("_count", "_ratio", "_strain", "_coefficient", "_ld"))
            or name.startswith(("eps_", "epsilon_", "phi_", "mf_"))
            or name in {"strain", "braced", "in_tension", "at_lap_section"}
        ):
            return True

        if arg.annotation is None:
            return False
        annotation = ast.unparse(arg.annotation).lower()
        numeric_tokens = {"float", "int", "real", "decimal"}
        annotation_names = set(re.findall(r"[a-z_][a-z0-9_]*", annotation))
        return not bool(annotation_names & numeric_tokens)

    def _check_float_comparison_contract(self) -> tuple[bool, str]:
        """Require a rationale and live regression for exact float equality."""
        if not self.has_float_equality:
            return True, ""
        if self.module is None:
            return False, "Found float equality comparison without module-bound review"

        function_key = f"{self.module}:{self.func_node.name}"
        contract = EXACT_FLOAT_COMPARISON_CONTRACTS.get(function_key)
        if contract is None:
            return False, "Found unreviewed float equality comparison"

        test_reference = contract["test"]
        test_path_text, _, selector = test_reference.partition("::")
        test_path = REPO_ROOT / test_path_text
        if not selector or not test_path.is_file():
            return False, f"Float equality review has missing test: {test_reference}"
        if selector not in test_path.read_text(encoding="utf-8"):
            return (
                False,
                f"Float equality review test selector is stale: {test_reference}",
            )
        return True, contract["rationale"]

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
            checker = FunctionChecker(node, filepath.relative_to(IS456_DIR).as_posix())
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
            relative_module = py_file.relative_to(IS456_DIR).as_posix()
            if (
                module_filter not in py_file.stem
                and module_filter not in relative_module
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
        description="IS 456 outcome-critical and advisory function-quality checker",
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
