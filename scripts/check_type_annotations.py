#!/usr/bin/env python3
"""
Type Annotation Checker for Streamlit Application

TASK-402: Detects functions and methods missing type annotations.

Features:
- Checks all function definitions for parameter type hints
- Checks for return type annotations
- Configurable strictness levels (strict, normal, lenient)
- Supports both pages and utility modules
- JSON output for CI integration

Usage:
    python scripts/check_type_annotations.py                    # Check all Streamlit files
    python scripts/check_type_annotations.py --strict           # Require all annotations
    python scripts/check_type_annotations.py --file path.py     # Check specific file
    python scripts/check_type_annotations.py --json             # JSON output
    python scripts/check_type_annotations.py --fix-suggestions  # Show fix suggestions

Strictness Levels:
    --lenient   Only warn on public functions (no underscore prefix)
    --normal    Warn on all functions except __dunder__ (default)
    --strict    Require annotations on ALL functions including private

Exit Codes:
    0 = All functions have proper annotations
    1 = Missing annotations found
    2 = Error during execution

Created: 2026-01-12 (Session 18, TASK-402)
"""
from __future__ import annotations

import ast
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from collections import defaultdict

# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class AnnotationIssue:
    """Represents a missing annotation issue."""

    file: str
    line: int
    function_name: str
    issue_type: str  # "missing_param_type", "missing_return_type", "missing_all"
    param_name: Optional[str] = None
    suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FunctionAnnotationStatus:
    """Tracks annotation status for a function."""

    name: str
    line: int
    params: Dict[str, bool]  # param_name -> has_annotation
    has_return: bool
    is_public: bool
    is_dunder: bool

    @property
    def is_fully_annotated(self) -> bool:
        return self.has_return and all(self.params.values())

    @property
    def missing_params(self) -> List[str]:
        return [name for name, annotated in self.params.items() if not annotated]

    @property
    def annotation_percentage(self) -> float:
        total = len(self.params) + 1  # params + return
        annotated = sum(1 for a in self.params.values() if a) + (1 if self.has_return else 0)
        return (annotated / total * 100) if total > 0 else 100.0


# =============================================================================
# AST VISITOR
# =============================================================================


class TypeAnnotationVisitor(ast.NodeVisitor):
    """AST visitor that checks for type annotations."""

    # Parameters that don't need annotations
    SKIP_PARAMS = {"self", "cls", "args", "kwargs"}

    def __init__(self, strictness: str = "normal"):
        self.strictness = strictness
        self.functions: List[FunctionAnnotationStatus] = []
        self.issues: List[AnnotationIssue] = []
        self.current_file: str = ""

    def analyze_file(self, filepath: Path) -> List[AnnotationIssue]:
        """Analyze a single file for type annotation issues."""
        self.current_file = str(filepath)
        self.functions = []
        self.issues = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source, str(filepath))
            self.visit(tree)
        except SyntaxError as e:
            self.issues.append(
                AnnotationIssue(
                    file=self.current_file,
                    line=e.lineno or 0,
                    function_name="<parse_error>",
                    issue_type="syntax_error",
                    suggestion=f"Fix syntax error: {e.msg}",
                )
            )
        except Exception as e:
            self.issues.append(
                AnnotationIssue(
                    file=self.current_file,
                    line=0,
                    function_name="<file_error>",
                    issue_type="file_error",
                    suggestion=f"Error reading file: {e}",
                )
            )

        return self.issues

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition and check annotations."""
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definition and check annotations."""
        self._check_function(node)
        self.generic_visit(node)

    def _check_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> None:
        """Check a function for type annotations."""
        name = node.name
        is_dunder = name.startswith("__") and name.endswith("__")
        is_private = name.startswith("_") and not is_dunder
        is_public = not name.startswith("_")

        # Check if we should skip based on strictness
        if self.strictness == "lenient" and not is_public:
            return
        if self.strictness == "normal" and is_dunder:
            return

        # Analyze parameters
        params: Dict[str, bool] = {}
        for arg in node.args.args:
            if arg.arg in self.SKIP_PARAMS:
                continue
            params[arg.arg] = arg.annotation is not None

        # Check kwonly args
        for arg in node.args.kwonlyargs:
            if arg.arg in self.SKIP_PARAMS:
                continue
            params[arg.arg] = arg.annotation is not None

        # Check *args and **kwargs (only if they have annotations)
        if node.args.vararg and node.args.vararg.arg not in self.SKIP_PARAMS:
            params[f"*{node.args.vararg.arg}"] = node.args.vararg.annotation is not None
        if node.args.kwarg and node.args.kwarg.arg not in self.SKIP_PARAMS:
            params[f"**{node.args.kwarg.arg}"] = node.args.kwarg.annotation is not None

        # Check return type
        has_return = node.returns is not None

        # Create status
        status = FunctionAnnotationStatus(
            name=name,
            line=node.lineno,
            params=params,
            has_return=has_return,
            is_public=is_public,
            is_dunder=is_dunder,
        )
        self.functions.append(status)

        # Generate issues
        self._generate_issues(status)

    def _generate_issues(self, status: FunctionAnnotationStatus) -> None:
        """Generate issues for missing annotations."""
        missing_params = status.missing_params

        if not status.has_return and missing_params:
            # Missing both
            self.issues.append(
                AnnotationIssue(
                    file=self.current_file,
                    line=status.line,
                    function_name=status.name,
                    issue_type="missing_all",
                    suggestion=self._suggest_signature(status),
                )
            )
        elif not status.has_return:
            # Only missing return
            self.issues.append(
                AnnotationIssue(
                    file=self.current_file,
                    line=status.line,
                    function_name=status.name,
                    issue_type="missing_return_type",
                    suggestion=f"Add return type: def {status.name}(...) -> ReturnType:",
                )
            )
        elif missing_params:
            # Only missing param types
            for param in missing_params:
                self.issues.append(
                    AnnotationIssue(
                        file=self.current_file,
                        line=status.line,
                        function_name=status.name,
                        issue_type="missing_param_type",
                        param_name=param,
                        suggestion=f"Add type: {param}: Type",
                    )
                )

    def _suggest_signature(self, status: FunctionAnnotationStatus) -> str:
        """Generate a suggested signature with type annotations."""
        params = []
        for name, has_ann in status.params.items():
            if has_ann:
                params.append(f"{name}: ...")
            else:
                params.append(f"{name}: Type")

        return f"def {status.name}({', '.join(params)}) -> ReturnType:"


# =============================================================================
# MAIN CHECKER
# =============================================================================


class TypeAnnotationChecker:
    """Main checker class that orchestrates the analysis."""

    # Directories to scan
    STREAMLIT_DIRS = [
        "streamlit_app/pages",
        "streamlit_app/utils",
        "streamlit_app/components",
    ]

    # Files/patterns to skip
    SKIP_PATTERNS = [
        "__pycache__",
        ".pyc",
        "test_",
        "_test.py",
        "conftest.py",
    ]

    def __init__(self, project_root: Path, strictness: str = "normal"):
        self.project_root = project_root
        self.strictness = strictness
        self.visitor = TypeAnnotationVisitor(strictness)
        self.all_issues: List[AnnotationIssue] = []
        self.file_stats: Dict[str, Dict[str, Any]] = {}

    def check_all(self) -> int:
        """Check all Streamlit files. Returns issue count."""
        for dir_path in self.STREAMLIT_DIRS:
            full_path = self.project_root / dir_path
            if full_path.exists():
                self._check_directory(full_path)
        return len(self.all_issues)

    def check_file(self, filepath: Path) -> int:
        """Check a single file. Returns issue count."""
        issues = self.visitor.analyze_file(filepath)
        self.all_issues.extend(issues)
        self._record_stats(filepath, self.visitor.functions)
        return len(issues)

    def _check_directory(self, directory: Path) -> None:
        """Recursively check all Python files in directory."""
        for py_file in directory.rglob("*.py"):
            # Skip files matching skip patterns
            if any(pattern in str(py_file) for pattern in self.SKIP_PATTERNS):
                continue

            issues = self.visitor.analyze_file(py_file)
            self.all_issues.extend(issues)
            self._record_stats(py_file, self.visitor.functions)

    def _record_stats(
        self, filepath: Path, functions: List[FunctionAnnotationStatus]
    ) -> None:
        """Record statistics for a file."""
        rel_path = str(filepath.relative_to(self.project_root))

        total_functions = len(functions)
        fully_annotated = sum(1 for f in functions if f.is_fully_annotated)
        public_functions = sum(1 for f in functions if f.is_public)
        public_annotated = sum(
            1 for f in functions if f.is_public and f.is_fully_annotated
        )

        self.file_stats[rel_path] = {
            "total_functions": total_functions,
            "fully_annotated": fully_annotated,
            "annotation_rate": (
                (fully_annotated / total_functions * 100) if total_functions > 0 else 100
            ),
            "public_functions": public_functions,
            "public_annotated": public_annotated,
            "public_rate": (
                (public_annotated / public_functions * 100)
                if public_functions > 0
                else 100
            ),
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        total_files = len(self.file_stats)
        total_functions = sum(s["total_functions"] for s in self.file_stats.values())
        total_annotated = sum(s["fully_annotated"] for s in self.file_stats.values())

        return {
            "files_checked": total_files,
            "total_functions": total_functions,
            "fully_annotated": total_annotated,
            "annotation_rate": (
                (total_annotated / total_functions * 100) if total_functions > 0 else 100
            ),
            "total_issues": len(self.all_issues),
            "issues_by_type": self._count_by_type(),
        }

    def _count_by_type(self) -> Dict[str, int]:
        """Count issues by type."""
        counts: Dict[str, int] = defaultdict(int)
        for issue in self.all_issues:
            counts[issue.issue_type] += 1
        return dict(counts)

    def print_report(self, verbose: bool = False, show_suggestions: bool = False) -> None:
        """Print a human-readable report."""
        print("=" * 70)
        print("🔍 TYPE ANNOTATION CHECK RESULTS")
        print("=" * 70)
        print()

        summary = self.get_summary()

        # Overall stats
        print(f"📁 Files checked: {summary['files_checked']}")
        print(f"📝 Functions analyzed: {summary['total_functions']}")
        print(f"✅ Fully annotated: {summary['fully_annotated']}")
        print(f"📊 Annotation rate: {summary['annotation_rate']:.1f}%")
        print()

        if self.all_issues:
            print("-" * 70)
            print("⚠️  MISSING ANNOTATIONS")
            print("-" * 70)

            # Group by file
            by_file: Dict[str, List[AnnotationIssue]] = defaultdict(list)
            for issue in self.all_issues:
                by_file[issue.file].append(issue)

            for filepath, issues in sorted(by_file.items()):
                rel_path = Path(filepath).relative_to(self.project_root)
                print(f"\n📄 {rel_path}:")

                for issue in sorted(issues, key=lambda x: x.line):
                    icon = self._get_issue_icon(issue.issue_type)
                    print(f"   {icon} Line {issue.line}: {issue.function_name}")
                    if issue.param_name:
                        print(f"      Parameter '{issue.param_name}' missing type")
                    if show_suggestions and issue.suggestion:
                        print(f"      💡 {issue.suggestion}")

            print()
            print("-" * 70)
            print("📊 ISSUE SUMMARY")
            print("-" * 70)
            for issue_type, count in sorted(summary["issues_by_type"].items()):
                print(f"   {issue_type}: {count}")
        else:
            print("✅ All functions have proper type annotations!")

        print()
        print("=" * 70)

    def _get_issue_icon(self, issue_type: str) -> str:
        """Get emoji icon for issue type."""
        icons = {
            "missing_all": "🔴",
            "missing_return_type": "🟠",
            "missing_param_type": "🟡",
            "syntax_error": "❌",
            "file_error": "❌",
        }
        return icons.get(issue_type, "⚪")

    def to_json(self) -> str:
        """Export results as JSON."""
        return json.dumps(
            {
                "summary": self.get_summary(),
                "file_stats": self.file_stats,
                "issues": [issue.to_dict() for issue in self.all_issues],
            },
            indent=2,
        )


# =============================================================================
# CLI
# =============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Check Streamlit files for missing type annotations"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Check a specific file instead of all Streamlit files",
    )
    parser.add_argument(
        "--strict",
        action="store_const",
        const="strict",
        dest="strictness",
        help="Require annotations on ALL functions including private",
    )
    parser.add_argument(
        "--lenient",
        action="store_const",
        const="lenient",
        dest="strictness",
        help="Only check public functions (no underscore prefix)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--fix-suggestions",
        action="store_true",
        help="Show suggested fixes for each issue",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output",
    )
    parser.add_argument(
        "--fail-threshold",
        type=int,
        default=0,
        help="Exit with error if annotation rate is below this percentage",
    )

    parser.set_defaults(strictness="normal")
    args = parser.parse_args()

    # Find project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent

    # Create checker
    checker = TypeAnnotationChecker(project_root, strictness=args.strictness)

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
        checker.print_report(
            verbose=args.verbose, show_suggestions=args.fix_suggestions
        )

    # Determine exit code
    summary = checker.get_summary()
    if args.fail_threshold > 0:
        # When --fail-threshold is set, only check the rate threshold
        if summary["annotation_rate"] < args.fail_threshold:
            sys.exit(1)
        # Threshold passed, exit success
        sys.exit(0)

    # Default behavior: exit with error if issues found
    if summary["total_issues"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
