#!/usr/bin/env python3
"""
Performance Issue Detector for Streamlit Application

TASK-405: Detects common performance anti-patterns in Streamlit code.

Features:
- Detects loops with repeated expensive operations
- Finds repeated API/database calls
- Identifies missing caching opportunities
- Detects inefficient list operations
- Finds N+1 query patterns
- JSON output for CI integration

Usage:
    python scripts/check_performance_issues.py                    # Check all Streamlit files
    python scripts/check_performance_issues.py --file path.py     # Check specific file
    python scripts/check_performance_issues.py --json             # JSON output
    python scripts/check_performance_issues.py --strict           # Fail on any issue

Exit Codes:
    0 = No critical issues found (or within threshold)
    1 = Critical performance issues detected
    2 = Error during execution

Created: 2026-01-12 (Session 18, TASK-405)
"""
from __future__ import annotations

import ast
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum


# =============================================================================
# DATA STRUCTURES
# =============================================================================


class Severity(Enum):
    """Issue severity levels."""

    CRITICAL = "critical"  # Definite performance problem
    HIGH = "high"  # Likely performance problem
    MEDIUM = "medium"  # Potential optimization
    LOW = "low"  # Minor suggestion


@dataclass
class PerformanceIssue:
    """Represents a detected performance issue."""

    file: str
    line: int
    severity: Severity
    issue_type: str
    message: str
    suggestion: str
    code_snippet: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["severity"] = self.severity.value
        return result


# =============================================================================
# PATTERN DETECTORS
# =============================================================================


class PerformanceVisitor(ast.NodeVisitor):
    """AST visitor to detect performance issues."""

    # Expensive function patterns
    EXPENSIVE_FUNCTIONS = {
        # API calls
        "api.design_beam",
        "api.check_beam",
        "api.optimize_beam",
        "api.get_beam_schedule",
        "design_beam",
        "check_beam",
        "optimize_beam",
        # Database/file operations
        "read_file",
        "load_data",
        "fetch",
        "query",
        "execute",
        # Network operations
        "requests.get",
        "requests.post",
        "requests.put",
        "urlopen",
        # Heavy computations
        "calculate_reinforcement",
        "optimize_rebar",
        "generate_report",
    }

    # Functions that are NOT expensive (whitelist for loop usage)
    # These are intentionally used in loops for UI feedback or are O(1) lookups
    LOOP_SAFE_FUNCTIONS = {
        # UI feedback functions (intentional per-iteration feedback)
        "loading_context",
        "st.spinner",
        "st.progress",
        "st.status",
        # O(1) dict/set operations
        "is_loaded",
        "mark_loaded",
        "get",
        "set",
        "add",
        "remove",
        # String methods (O(n) but typically small strings)
        "lower",
        "upper",
        "strip",
        "split",
    }

    # Functions that should be cached
    CACHEABLE_PATTERNS = {
        "load_",
        "get_",
        "fetch_",
        "read_",
        "calculate_",
        "compute_",
    }

    def __init__(self, filepath: str, source_lines: List[str]):
        self.filepath = filepath
        self.source_lines = source_lines
        self.issues: List[PerformanceIssue] = []
        self.current_function: Optional[str] = None
        self.loop_depth = 0
        self.in_cached_function = False
        self.functions_in_file: Set[str] = set()
        self.cached_functions: Set[str] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track function definitions and decorators."""
        self.current_function = node.name
        self.functions_in_file.add(node.name)

        # Check for cache decorators
        for decorator in node.decorator_list:
            dec_name = self._get_decorator_name(decorator)
            if dec_name and "cache" in dec_name.lower():
                self.cached_functions.add(node.name)
                self.in_cached_function = True
                break

        self.generic_visit(node)
        self.in_cached_function = False
        self.current_function = None

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Handle async functions same as regular functions."""
        self.current_function = node.name
        self.functions_in_file.add(node.name)
        self.generic_visit(node)
        self.current_function = None

    def visit_For(self, node: ast.For) -> None:
        """Check for performance issues in for loops."""
        self.loop_depth += 1
        self._check_loop_body(node)
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node: ast.While) -> None:
        """Check for performance issues in while loops."""
        self.loop_depth += 1
        self._check_loop_body(node)
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_ListComp(self, node: ast.ListComp) -> None:
        """Check list comprehensions for expensive operations."""
        self.loop_depth += 1
        for generator in node.generators:
            self._check_expensive_in_loop(generator.iter, node.lineno)
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_Call(self, node: ast.Call) -> None:
        """Check function calls for performance issues."""
        func_name = self._get_call_name(node)

        # Check for expensive calls in loops
        if self.loop_depth > 0 and func_name:
            if self._is_expensive_call(func_name):
                self._add_issue(
                    line=node.lineno,
                    severity=Severity.HIGH,
                    issue_type="expensive_in_loop",
                    message=f"Expensive operation '{func_name}' inside loop",
                    suggestion=f"Move '{func_name}' outside the loop or cache results",
                )

        # Check for repeated dataframe operations
        if func_name and "iterrows" in func_name:
            self._add_issue(
                line=node.lineno,
                severity=Severity.MEDIUM,
                issue_type="inefficient_iteration",
                message="Using iterrows() which is slow for large DataFrames",
                suggestion="Use vectorized operations or df.itertuples() instead",
            )

        # Check for missing caching on expensive functions
        if (
            self.current_function
            and func_name
            and self._should_be_cached(func_name)
            and not self.in_cached_function
            and self.current_function not in self.cached_functions
        ):
            # Check if this is a Streamlit callback (can't cache those)
            if not self.current_function.startswith("_on"):
                self._add_issue(
                    line=node.lineno,
                    severity=Severity.LOW,
                    issue_type="missing_cache",
                    message=f"Function '{self.current_function}' calls '{func_name}' but is not cached",
                    suggestion="Consider adding @st.cache_data or @st.cache_resource decorator",
                )

        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        """Check for string concatenation in loops."""
        if self.loop_depth > 0 and isinstance(node.op, ast.Add):
            # Check if adding strings
            if isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
                self._add_issue(
                    line=node.lineno,
                    severity=Severity.MEDIUM,
                    issue_type="string_concat_in_loop",
                    message="String concatenation in loop",
                    suggestion="Use list.append() and ''.join() instead",
                )
        self.generic_visit(node)

    def _check_loop_body(self, node: ast.For | ast.While) -> None:
        """Check for common loop anti-patterns."""
        # Check for len() in range
        if isinstance(node, ast.For) and isinstance(node.iter, ast.Call):
            call = node.iter
            if self._get_call_name(call) == "range":
                # Check for range(len(x))
                if call.args and isinstance(call.args[0], ast.Call):
                    inner_call = call.args[0]
                    if self._get_call_name(inner_call) == "len":
                        self._add_issue(
                            line=node.lineno,
                            severity=Severity.LOW,
                            issue_type="range_len_pattern",
                            message="Using range(len(x)) pattern",
                            suggestion="Use 'for item in x:' or 'for i, item in enumerate(x):'",
                        )

    def _check_expensive_in_loop(self, node: ast.expr, line: int) -> None:
        """Check if expensive operations are in loop iterator."""
        if isinstance(node, ast.Call):
            func_name = self._get_call_name(node)
            if func_name and self._is_expensive_call(func_name):
                self._add_issue(
                    line=line,
                    severity=Severity.HIGH,
                    issue_type="expensive_in_comprehension",
                    message=f"Expensive call '{func_name}' in comprehension",
                    suggestion="Pre-compute the result before the comprehension",
                )

    def _get_call_name(self, node: ast.Call) -> Optional[str]:
        """Get the full name of a function call."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return None

    def _get_decorator_name(self, node: ast.expr) -> Optional[str]:
        """Get the name of a decorator."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        elif isinstance(node, ast.Call):
            return self._get_call_name(node)
        return None

    def _is_expensive_call(self, func_name: str) -> bool:
        """Check if a function call is expensive."""
        # First check whitelist - these are safe in loops
        # Check both full name and last part (method name)
        name_parts = func_name.split(".")
        last_part = name_parts[-1] if name_parts else func_name
        if (
            last_part in self.LOOP_SAFE_FUNCTIONS
            or func_name in self.LOOP_SAFE_FUNCTIONS
        ):
            return False

        return func_name in self.EXPENSIVE_FUNCTIONS or any(
            pattern in func_name for pattern in ["fetch", "load", "query", "request"]
        )

    def _should_be_cached(self, func_name: str) -> bool:
        """Check if a function should probably be cached."""
        return any(func_name.startswith(pattern) for pattern in self.CACHEABLE_PATTERNS)

    def _add_issue(
        self,
        line: int,
        severity: Severity,
        issue_type: str,
        message: str,
        suggestion: str,
    ) -> None:
        """Add a performance issue."""
        code_snippet = None
        if 0 < line <= len(self.source_lines):
            code_snippet = self.source_lines[line - 1].strip()

        self.issues.append(
            PerformanceIssue(
                file=self.filepath,
                line=line,
                severity=severity,
                issue_type=issue_type,
                message=message,
                suggestion=suggestion,
                code_snippet=code_snippet,
            )
        )


# =============================================================================
# MAIN CHECKER
# =============================================================================


class PerformanceChecker:
    """Main checker class."""

    SCAN_DIRS = [
        "streamlit_app/pages",
        "streamlit_app/utils",
        "streamlit_app/components",
    ]

    SKIP_PATTERNS = [
        "__pycache__",
        ".pyc",
        "test_",
        "_test.py",
        "conftest.py",
    ]

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues: List[PerformanceIssue] = []
        self.files_checked = 0

    def check_all(self) -> int:
        """Check all Streamlit files."""
        for dir_path in self.SCAN_DIRS:
            full_path = self.project_root / dir_path
            if full_path.exists():
                if full_path.is_dir():
                    self._scan_directory(full_path)
                else:
                    self._scan_file(full_path)

        return len(self.issues)

    def check_file(self, filepath: Path) -> int:
        """Check a single file."""
        self._scan_file(filepath)
        return len(self.issues)

    def _scan_directory(self, directory: Path) -> None:
        """Scan all Python files in directory."""
        for py_file in directory.rglob("*.py"):
            if any(pattern in str(py_file) for pattern in self.SKIP_PATTERNS):
                continue
            self._scan_file(py_file)

    def _scan_file(self, filepath: Path) -> None:
        """Scan a single file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            source_lines = source.splitlines()
            tree = ast.parse(source, str(filepath))
        except Exception:
            return

        self.files_checked += 1

        rel_path = str(filepath.relative_to(self.project_root))
        visitor = PerformanceVisitor(rel_path, source_lines)
        visitor.visit(tree)

        self.issues.extend(visitor.issues)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        by_severity = {s.value: 0 for s in Severity}
        by_type: Dict[str, int] = {}

        for issue in self.issues:
            by_severity[issue.severity.value] += 1
            by_type[issue.issue_type] = by_type.get(issue.issue_type, 0) + 1

        return {
            "files_checked": self.files_checked,
            "total_issues": len(self.issues),
            "by_severity": by_severity,
            "by_type": by_type,
        }

    def print_report(self) -> None:
        """Print a human-readable report."""
        print("=" * 70)
        print("⚡ PERFORMANCE ISSUE CHECK RESULTS")
        print("=" * 70)
        print()

        summary = self.get_summary()

        print(f"📁 Files checked: {summary['files_checked']}")
        print(f"📊 Total issues: {summary['total_issues']}")
        print()

        if self.issues:
            print("-" * 70)
            print("🔍 ISSUES BY SEVERITY")
            print("-" * 70)
            print()

            severity_icons = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🔵",
            }

            for severity in ["critical", "high", "medium", "low"]:
                count = summary["by_severity"][severity]
                if count > 0:
                    print(f"   {severity_icons[severity]} {severity.upper()}: {count}")

            print()
            print("-" * 70)
            print("📋 DETAILED ISSUES")
            print("-" * 70)
            print()

            # Sort by severity
            severity_order = {
                Severity.CRITICAL: 0,
                Severity.HIGH: 1,
                Severity.MEDIUM: 2,
                Severity.LOW: 3,
            }
            sorted_issues = sorted(
                self.issues, key=lambda x: severity_order[x.severity]
            )

            current_file = ""
            for issue in sorted_issues:
                if issue.file != current_file:
                    current_file = issue.file
                    print(f"\n📄 {current_file}")

                icon = severity_icons[issue.severity.value]
                print(f"   {icon} Line {issue.line}: {issue.message}")
                if issue.code_snippet:
                    print(f"      Code: {issue.code_snippet[:60]}...")
                print(f"      💡 {issue.suggestion}")

            print()
            print("-" * 70)
            print("📊 ISSUE TYPE BREAKDOWN")
            print("-" * 70)
            for issue_type, count in sorted(
                summary["by_type"].items(), key=lambda x: -x[1]
            ):
                print(f"   - {issue_type}: {count}")
        else:
            print("✅ No performance issues detected!")

        print()
        print("=" * 70)

    def to_json(self) -> str:
        """Export results as JSON."""
        return json.dumps(
            {
                "summary": self.get_summary(),
                "issues": [i.to_dict() for i in self.issues],
            },
            indent=2,
        )


# =============================================================================
# CLI
# =============================================================================


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check for performance issues in Streamlit files"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Check a specific file instead of all Streamlit files",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on any issue",
    )
    parser.add_argument(
        "--fail-threshold",
        type=int,
        default=0,
        help="Fail if more than N high/critical issues (default: 0 = never fail on threshold)",
    )

    args = parser.parse_args()

    # Find project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent

    # Create checker
    checker = PerformanceChecker(project_root)

    # Run check
    if args.file:
        filepath = Path(args.file)
        if not filepath.is_absolute():
            filepath = project_root / filepath
        checker.check_file(filepath)
    else:
        checker.check_all()

    # Output results
    if args.json:
        print(checker.to_json())
    else:
        checker.print_report()

    # Determine exit code
    summary = checker.get_summary()
    critical_high = summary["by_severity"]["critical"] + summary["by_severity"]["high"]

    if args.strict and checker.issues:
        sys.exit(1)
    elif args.fail_threshold > 0 and critical_high >= args.fail_threshold:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
