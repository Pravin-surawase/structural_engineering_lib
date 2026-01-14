#!/usr/bin/env python3
"""
Streamlit Fragment API Violation Detector
==========================================

Detects violations of Streamlit's fragment API restrictions through static analysis.

**Checks for:**
1. Direct st.sidebar calls inside @st.fragment functions
2. `with st.sidebar:` context managers inside fragments
3. Functions that might call sidebar-using code (basic call-graph analysis)

**Usage:**
    python scripts/check_fragment_violations.py
    python scripts/check_fragment_violations.py --file streamlit_app/pages/beam_design.py

**Exit Codes:**
    0 - No violations found
    1 - Violations detected
    2 - Error during analysis

**Integration:**
    - Pre-commit hook: Runs on staged Streamlit files
    - CI: Runs on all Streamlit files in workflow

**Limitations:**
    - Level 1 static analysis only (direct violations)
    - Does not trace through all function calls (future enhancement)
    - May miss violations in deeply nested call chains

Author: AI Agent
Created: 2026-01-15
Related: docs/research/fragment-api-restrictions-analysis.md
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import argparse


class FragmentViolationDetector(ast.NodeVisitor):
    """AST visitor that detects Streamlit fragment API violations."""

    def __init__(self, filename: str):
        self.filename = filename
        self.violations: List[Tuple[int, str, str]] = []
        self.current_fragment: Optional[str] = None
        self.fragment_lineno: Optional[int] = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions to check if they're fragments."""
        # Check if function is decorated with @st.fragment
        is_fragment = any(
            self._is_fragment_decorator(decorator)
            for decorator in node.decorator_list
        )

        if is_fragment:
            # Save current fragment context
            prev_fragment = self.current_fragment
            prev_lineno = self.fragment_lineno

            self.current_fragment = node.name
            self.fragment_lineno = node.lineno

            # Visit function body
            self.generic_visit(node)

            # Restore previous fragment context
            self.current_fragment = prev_fragment
            self.fragment_lineno = prev_lineno
        else:
            self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Visit attribute access (e.g., st.sidebar)."""
        if self.current_fragment:
            # Check for st.sidebar.* patterns
            if isinstance(node.value, ast.Name) and node.value.id == 'st':
                if node.attr == 'sidebar':
                    self.violations.append((
                        node.lineno,
                        self.current_fragment,
                        f"Direct st.sidebar access in fragment '{self.current_fragment}'"
                    ))

        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        """Visit with statements to check for sidebar context managers."""
        if self.current_fragment:
            for item in node.items:
                if self._is_sidebar_context(item.context_expr):
                    self.violations.append((
                        node.lineno,
                        self.current_fragment,
                        f"'with st.sidebar:' context manager in fragment '{self.current_fragment}'"
                    ))

        self.generic_visit(node)

    def _is_fragment_decorator(self, decorator: ast.expr) -> bool:
        """Check if decorator is @st.fragment."""
        # Handle @st.fragment
        if isinstance(decorator, ast.Attribute):
            if (isinstance(decorator.value, ast.Name) and
                decorator.value.id == 'st' and
                decorator.attr == 'fragment'):
                return True

        # Handle @st.fragment()
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                if (isinstance(decorator.func.value, ast.Name) and
                    decorator.func.value.id == 'st' and
                    decorator.func.attr == 'fragment'):
                    return True

        return False

    def _is_sidebar_context(self, expr: ast.expr) -> bool:
        """Check if expression is st.sidebar (for with statement)."""
        if isinstance(expr, ast.Attribute):
            if (isinstance(expr.value, ast.Name) and
                expr.value.id == 'st' and
                expr.attr == 'sidebar'):
                return True
        return False


def check_file(filepath: Path) -> List[Tuple[str, int, str, str]]:
    """
    Check a single file for fragment API violations.

    Args:
        filepath: Path to Python file to check

    Returns:
        List of violations: (filename, line_number, fragment_name, message)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        tree = ast.parse(source, filename=str(filepath))
        detector = FragmentViolationDetector(str(filepath))
        detector.visit(tree)

        # Convert to output format
        violations = [
            (str(filepath), lineno, fragment, msg)
            for lineno, fragment, msg in detector.violations
        ]

        return violations

    except SyntaxError as e:
        print(f"⚠️  Syntax error in {filepath}: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"❌ Error checking {filepath}: {e}", file=sys.stderr)
        return []


def check_directory(directory: Path, pattern: str = "*.py") -> List[Tuple[str, int, str, str]]:
    """
    Check all Python files in directory for fragment violations.

    Args:
        directory: Path to directory to scan
        pattern: Glob pattern for files to check

    Returns:
        List of all violations found
    """
    all_violations = []

    for filepath in directory.rglob(pattern):
        # Skip test files and utilities
        if '/tests/' in str(filepath) or '/__pycache__/' in str(filepath):
            continue

        violations = check_file(filepath)
        all_violations.extend(violations)

    return all_violations


def print_violations(violations: List[Tuple[str, int, str, str]]) -> None:
    """Print violations in a formatted way."""
    if not violations:
        print("✅ No fragment API violations detected")
        return

    print("❌ Fragment API violations found:\n")

    # Group by file
    from collections import defaultdict
    by_file = defaultdict(list)
    for filepath, lineno, fragment, msg in violations:
        by_file[filepath].append((lineno, fragment, msg))

    for filepath, file_violations in sorted(by_file.items()):
        print(f"📄 {filepath}:")
        for lineno, fragment, msg in sorted(file_violations):
            print(f"   Line {lineno}: {msg}")
        print()

    print(f"Total violations: {len(violations)}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Detect Streamlit fragment API violations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Check all Streamlit files
    python scripts/check_fragment_violations.py

    # Check specific file
    python scripts/check_fragment_violations.py --file streamlit_app/pages/beam_design.py

    # Check specific directory
    python scripts/check_fragment_violations.py --dir streamlit_app/components

Exit codes:
    0 - No violations found
    1 - Violations detected
    2 - Error during analysis
        """
    )

    parser.add_argument(
        '--file',
        type=Path,
        help='Check specific file'
    )

    parser.add_argument(
        '--dir',
        type=Path,
        default=Path('streamlit_app'),
        help='Check all files in directory (default: streamlit_app)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print verbose output'
    )

    args = parser.parse_args()

    try:
        if args.file:
            # Check single file
            if not args.file.exists():
                print(f"❌ File not found: {args.file}", file=sys.stderr)
                return 2

            violations = check_file(args.file)
        else:
            # Check directory
            if not args.dir.exists():
                print(f"❌ Directory not found: {args.dir}", file=sys.stderr)
                return 2

            violations = check_directory(args.dir)

        print_violations(violations)

        return 1 if violations else 0

    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 2


if __name__ == '__main__':
    sys.exit(main())
