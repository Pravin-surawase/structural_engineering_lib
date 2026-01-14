#!/usr/bin/env python3
"""
Automated detection of common cost optimizer issues.

This script checks for patterns that cause bugs in the cost optimizer:
- Direct dict access (use .get() instead)
- Division without zero checks
- Imports inside functions
- Missing type hints on dict returns
- Session state access without validation

Run as pre-commit hook or in CI.
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Tuple


class IssueDetector(ast.NodeVisitor):
    """AST visitor to detect code issues."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.issues: List[Tuple[int, str, str]] = []  # (line, severity, message)
        self.in_function = False
        self.function_name = ""

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Track when we're inside a function."""
        old_in_function = self.in_function
        old_function_name = self.function_name

        self.in_function = True
        self.function_name = node.name

        # Check for missing type hints on functions returning dict
        if node.returns is None:
            # Look for return statements
            for child in ast.walk(node):
                if isinstance(child, ast.Return) and child.value:
                    if isinstance(child.value, ast.Dict):
                        self.issues.append(
                            (
                                node.lineno,
                                "MEDIUM",
                                f"Function '{node.name}' returns dict without type hint",
                            )
                        )
                        break

        self.generic_visit(node)

        self.in_function = old_in_function
        self.function_name = old_function_name

    def visit_Import(self, node: ast.Import):
        """Detect imports inside functions."""
        if self.in_function:
            for alias in node.names:
                self.issues.append(
                    (
                        node.lineno,
                        "HIGH",
                        f"Import '{alias.name}' inside function '{self.function_name}' (move to module level)",
                    )
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Detect from...import inside functions."""
        if self.in_function:
            module = node.module or ""
            self.issues.append(
                (
                    node.lineno,
                    "HIGH",
                    f"Import from '{module}' inside function '{self.function_name}' (move to module level)",
                )
            )
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript):
        """Detect direct dict access (result["key"] instead of result.get("key"))."""
        # Check if this is a subscript on a variable (not a list/dict literal)
        if isinstance(node.value, ast.Name):
            var_name = node.value.id
            # Skip common safe patterns (list indexing with int, etc.)
            if isinstance(node.slice, ast.Constant) and isinstance(
                node.slice.value, str
            ):
                # This is string key access - likely dict access
                if var_name in [
                    "result",
                    "inputs",
                    "design_result",
                    "flexure",
                    "st.session_state",
                    "session_state",
                ]:
                    self.issues.append(
                        (
                            node.lineno,
                            "HIGH",
                            f"Direct dict access '{var_name}[...]' may raise KeyError (use .get() with default)",
                        )
                    )
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp):
        """Detect division operations."""
        if isinstance(node.op, ast.Div):
            # Check if there's an obvious zero check nearby
            # This is a heuristic - not perfect but catches most cases
            self.issues.append(
                (
                    node.lineno,
                    "CRITICAL",
                    "Division operation without obvious zero check (validate denominator)",
                )
            )
        self.generic_visit(node)


def check_file(filepath: Path) -> List[Tuple[int, str, str]]:
    """Check a single file for issues."""
    try:
        with open(filepath, "r") as f:
            source = f.read()

        # Parse AST
        tree = ast.parse(source, filename=str(filepath))

        detector = IssueDetector(str(filepath))
        detector.visit(tree)

        # Additional regex-based checks (for patterns AST can't catch)
        lines = source.split("\n")

        for i, line in enumerate(lines, 1):
            # Check for st.session_state access without .get()
            if "st.session_state." in line and "[" in line and ".get(" not in line:
                detector.issues.append(
                    (
                        i,
                        "HIGH",
                        "Session state access may fail if key missing (use .get() or check key exists)",
                    )
                )

            # Check for hardcoded defaults in .get() calls that mask errors
            if re.search(r"\.get\([^,]+,\s*0\s*\)", line):
                detector.issues.append(
                    (
                        i,
                        "MEDIUM",
                        "Using 0 as default in .get() may mask missing data (consider None or raise error)",
                    )
                )

        return detector.issues

    except SyntaxError as e:
        return [(e.lineno or 0, "ERROR", f"Syntax error: {e.msg}")]
    except Exception as e:
        return [(0, "ERROR", f"Failed to parse file: {e}")]


def main():
    """Main entry point."""
    # Check cost optimizer file
    project_root = Path(__file__).parent.parent
    cost_optimizer_file = (
        project_root / "streamlit_app" / "pages" / "02_💰_cost_optimizer.py"
    )

    if not cost_optimizer_file.exists():
        print(f"❌ File not found: {cost_optimizer_file}")
        return 1

    print(f"🔍 Checking {cost_optimizer_file.name} for common issues...\n")

    issues = check_file(cost_optimizer_file)

    # Group by severity
    critical = [i for i in issues if i[1] == "CRITICAL"]
    high = [i for i in issues if i[1] == "HIGH"]
    medium = [i for i in issues if i[1] == "MEDIUM"]
    errors = [i for i in issues if i[1] == "ERROR"]

    # Print results
    if errors:
        print("❌ ERRORS:")
        for line, severity, message in errors:
            print(f"  Line {line}: {message}")
        print()
        return 1

    if critical:
        print("🔴 CRITICAL ISSUES:")
        for line, severity, message in critical:
            print(f"  Line {line}: {message}")
        print()

    if high:
        print("🟠 HIGH PRIORITY ISSUES:")
        for line, severity, message in high:
            print(f"  Line {line}: {message}")
        print()

    if medium:
        print("🟡 MEDIUM PRIORITY ISSUES:")
        for line, severity, message in medium:
            print(f"  Line {line}: {message}")
        print()

    total = len(critical) + len(high) + len(medium)

    if total == 0:
        print("✅ No issues found! Good job!")
        return 0
    else:
        print(f"📊 Total issues found: {total}")
        print(f"   Critical: {len(critical)}, High: {len(high)}, Medium: {len(medium)}")
        print()
        print("⚠️  These issues should be addressed before merging.")
        print("    See docs/_internal/COST_OPTIMIZER_FIX_PLAN.md for solutions.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
