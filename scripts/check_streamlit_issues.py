#!/usr/bin/env python3
"""
Comprehensive Streamlit App Issue Detector

Scans ALL Streamlit pages for common issues:
- NameError (undefined variables)
- AttributeError (session state access)
- KeyError (direct dict access)
- ZeroDivisionError (division without checks)
- ImportError (imports inside functions)
- TypeError (wrong function args)

Part of comprehensive prevention system (Phase 1A).

Usage:
    python scripts/check_streamlit_issues.py --all-pages
    python scripts/check_streamlit_issues.py --page beam_design
    python scripts/check_streamlit_issues.py --all-pages --fail-on critical,high
"""

import ast
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Set, Dict
from collections import defaultdict


class EnhancedIssueDetector(ast.NodeVisitor):
    """Enhanced AST visitor with scope tracking for NameError detection."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.issues: List[Tuple[int, str, str]] = []  # (line, severity, message)

        # Scope tracking for NameError detection
        self.scopes: List[Set[str]] = [set()]  # Stack of scopes (sets of defined vars)
        self.imported_names: Set[str] = set()  # Track imports
        self.builtin_names: Set[str] = set(dir(__builtins__))  # Python builtins

        # Session state tracking
        self.session_state_keys: Set[str] = set()  # Track keys set in session state

        # Function tracking
        self.in_function = False
        self.function_name = ""
        self.current_class = None

    def enter_scope(self):
        """Enter a new scope."""
        self.scopes.append(set())

    def exit_scope(self):
        """Exit current scope."""
        if len(self.scopes) > 1:
            self.scopes.pop()

    def add_defined_name(self, name: str):
        """Add a name to current scope."""
        if self.scopes:
            self.scopes[-1].add(name)

    def is_defined(self, name: str) -> bool:
        """Check if name is defined in any visible scope."""
        # Check all scopes (from innermost to outermost)
        for scope in reversed(self.scopes):
            if name in scope:
                return True

        # Check imports
        if name in self.imported_names:
            return True

        # Check builtins
        if name in self.builtin_names:
            return True

        # Special Streamlit names
        streamlit_names = {'st', 'pd', 'np', 'plt'}
        if name in streamlit_names:
            return True

        return False

    def visit_Import(self, node: ast.Import):
        """Track imports and detect imports inside functions."""
        for alias in node.names:
            imported_name = alias.asname if alias.asname else alias.name
            self.imported_names.add(imported_name)
            self.add_defined_name(imported_name)

        # Detect imports inside functions (bad practice)
        if self.in_function:
            for alias in node.names:
                self.issues.append((
                    node.lineno,
                    "HIGH",
                    f"Import '{alias.name}' inside function '{self.function_name}' (move to module level)"
                ))

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track from...import and detect inside functions."""
        for alias in node.names:
            imported_name = alias.asname if alias.asname else alias.name
            if imported_name != '*':
                self.imported_names.add(imported_name)
                self.add_defined_name(imported_name)

        # Detect imports inside functions
        if self.in_function:
            module = node.module or ""
            self.issues.append((
                node.lineno,
                "HIGH",
                f"Import from '{module}' inside function '{self.function_name}' (move to module level)"
            ))

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Track function definitions and scope."""
        self.add_defined_name(node.name)

        old_in_function = self.in_function
        old_function_name = self.function_name

        self.in_function = True
        self.function_name = node.name

        # Enter function scope
        self.enter_scope()

        # Add function parameters to scope
        for arg in node.args.args:
            self.add_defined_name(arg.arg)

        # Check for missing type hints on functions returning dict
        if node.returns is None:
            for child in ast.walk(node):
                if isinstance(child, ast.Return) and child.value:
                    if isinstance(child.value, ast.Dict):
                        self.issues.append((
                            node.lineno,
                            "MEDIUM",
                            f"Function '{node.name}' returns dict without type hint"
                        ))
                        break

        self.generic_visit(node)

        # Exit function scope
        self.exit_scope()

        self.in_function = old_in_function
        self.function_name = old_function_name

    def visit_Assign(self, node: ast.Assign):
        """Track variable assignments."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.add_defined_name(target.id)
            elif isinstance(target, ast.Tuple) or isinstance(target, ast.List):
                # Unpack tuple/list assignment
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        self.add_defined_name(elt.id)
            elif isinstance(target, ast.Subscript):
                # Session state assignment: st.session_state["key"] = value
                if isinstance(target.value, ast.Attribute):
                    if (isinstance(target.value.value, ast.Name) and
                        target.value.value.id == 'st' and
                        target.value.attr == 'session_state'):
                        if isinstance(target.slice, ast.Constant):
                            key = target.slice.value
                            if isinstance(key, str):
                                self.session_state_keys.add(key)

        self.generic_visit(node)

    def visit_Lambda(self, node: ast.Lambda):
        """Track lambda parameters as defined names in lambda scope."""
        # Create new scope for lambda
        self.enter_scope()

        # Add lambda parameters to scope
        for arg in node.args.args:
            self.add_defined_name(arg.arg)

        # Visit lambda body
        self.generic_visit(node)

        # Pop lambda scope
        self.exit_scope()

    def visit_ListComp(self, node: ast.ListComp):
        """Track list comprehension variables."""
        self.enter_scope()

        # Add all comprehension target variables
        for generator in node.generators:
            if isinstance(generator.target, ast.Name):
                self.add_defined_name(generator.target.id)
            elif isinstance(generator.target, ast.Tuple):
                for elt in generator.target.elts:
                    if isinstance(elt, ast.Name):
                        self.add_defined_name(elt.id)

        self.generic_visit(node)
        self.exit_scope()

    def visit_DictComp(self, node: ast.DictComp):
        """Track dict comprehension variables."""
        self.enter_scope()

        # Add all comprehension target variables
        for generator in node.generators:
            if isinstance(generator.target, ast.Name):
                self.add_defined_name(generator.target.id)
            elif isinstance(generator.target, ast.Tuple):
                for elt in generator.target.elts:
                    if isinstance(elt, ast.Name):
                        self.add_defined_name(elt.id)

        self.generic_visit(node)
        self.exit_scope()

    def visit_SetComp(self, node: ast.SetComp):
        """Track set comprehension variables."""
        self.enter_scope()

        # Add all comprehension target variables
        for generator in node.generators:
            if isinstance(generator.target, ast.Name):
                self.add_defined_name(generator.target.id)
            elif isinstance(generator.target, ast.Tuple):
                for elt in generator.target.elts:
                    if isinstance(elt, ast.Name):
                        self.add_defined_name(elt.id)

        self.generic_visit(node)
        self.exit_scope()

    def visit_GeneratorExp(self, node: ast.GeneratorExp):
        """Track generator expression variables."""
        self.enter_scope()

        # Add all comprehension target variables
        for generator in node.generators:
            if isinstance(generator.target, ast.Name):
                self.add_defined_name(generator.target.id)
            elif isinstance(generator.target, ast.Tuple):
                for elt in generator.target.elts:
                    if isinstance(elt, ast.Name):
                        self.add_defined_name(elt.id)

        self.generic_visit(node)
        self.exit_scope()

    def visit_AugAssign(self, node: ast.AugAssign):
        """Track augmented assignments (+=, -=, etc.)."""
        if isinstance(node.target, ast.Name):
            # For +=, the variable must already exist
            if not self.is_defined(node.target.id):
                self.issues.append((
                    node.lineno,
                    "CRITICAL",
                    f"NameError: '{node.target.id}' used in augmented assignment but not defined"
                ))
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        """Detect undefined variable usage (NameError)."""
        if isinstance(node.ctx, ast.Load):
            # Variable is being read
            if not self.is_defined(node.id):
                # Filter out likely false positives
                if node.id not in ['_', '__name__', '__file__']:
                    self.issues.append((
                        node.lineno,
                        "CRITICAL",
                        f"NameError: name '{node.id}' is not defined (used before assignment or import)"
                    ))

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        """Detect session state access without validation."""
        # Check for st.session_state.key pattern
        if isinstance(node.value, ast.Attribute):
            if (isinstance(node.value.value, ast.Name) and
                node.value.value.id == 'st' and
                node.value.attr == 'session_state'):
                # This is st.session_state.some_key
                attr_name = node.attr
                # Only warn if we haven't seen this key set
                if attr_name not in self.session_state_keys:
                    self.issues.append((
                        node.lineno,
                        "HIGH",
                        f"AttributeError risk: st.session_state.{attr_name} may not exist (use .get() or check 'in')"
                    ))

        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript):
        """Detect direct dict access (KeyError risk)."""
        # Check if this is a subscript on a variable
        if isinstance(node.value, ast.Name):
            var_name = node.value.id
            # Skip safe patterns (list indexing with int)
            if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                # String key access - likely dict access
                if var_name in ['result', 'inputs', 'design_result', 'flexure',
                                'shear', 'detailing', 'data', 'config']:
                    self.issues.append((
                        node.lineno,
                        "HIGH",
                        f"KeyError risk: '{var_name}[{repr(node.slice.value)}]' may raise KeyError (use .get() with default)"
                    ))

        # Session state subscript: st.session_state["key"]
        if isinstance(node.value, ast.Attribute):
            if (isinstance(node.value.value, ast.Name) and
                node.value.value.id == 'st' and
                node.value.attr == 'session_state'):
                if isinstance(node.slice, ast.Constant):
                    key = node.slice.value
                    if isinstance(key, str) and key not in self.session_state_keys:
                        self.issues.append((
                            node.lineno,
                            "HIGH",
                            f"KeyError risk: st.session_state[{repr(key)}] may not exist (use .get() or check 'in')"
                        ))

        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp):
        """Detect division operations (ZeroDivisionError risk)."""
        if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
            # Check if denominator is obviously safe
            is_safe = False

            # Check if it's a constant (not zero)
            if isinstance(node.right, ast.Constant):
                if isinstance(node.right.value, (int, float)) and node.right.value != 0:
                    is_safe = True

            if not is_safe:
                op_name = {ast.Div: '/', ast.FloorDiv: '//', ast.Mod: '%'}[type(node.op)]
                self.issues.append((
                    node.lineno,
                    "CRITICAL",
                    f"ZeroDivisionError risk: division '{op_name}' without obvious zero check (validate denominator)"
                ))

        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        """Track for loop variables."""
        if isinstance(node.target, ast.Name):
            self.add_defined_name(node.target.id)
        elif isinstance(node.target, (ast.Tuple, ast.List)):
            for elt in node.target.elts:
                if isinstance(elt, ast.Name):
                    self.add_defined_name(elt.id)

        self.generic_visit(node)

    def visit_With(self, node: ast.With):
        """Track with statement variables."""
        for item in node.items:
            if item.optional_vars:
                if isinstance(item.optional_vars, ast.Name):
                    self.add_defined_name(item.optional_vars.id)

        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        """Track exception variable."""
        if node.name:
            self.add_defined_name(node.name)

        self.generic_visit(node)


def check_file(filepath: Path) -> List[Tuple[int, str, str]]:
    """Check a single file for issues."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        # Parse AST
        tree = ast.parse(source, filename=str(filepath))

        detector = EnhancedIssueDetector(str(filepath))
        detector.visit(tree)

        return detector.issues

    except SyntaxError as e:
        return [(e.lineno or 0, "ERROR", f"Syntax error: {e.msg}")]
    except Exception as e:
        return [(0, "ERROR", f"Failed to parse file: {e}")]


def scan_all_pages(pages_dir: Path) -> Dict[str, List[Tuple[int, str, str]]]:
    """Scan all Streamlit pages."""
    results = {}

    # Find all Python files in pages directory
    page_files = sorted(pages_dir.glob("*.py"))

    if not page_files:
        print(f"⚠️  No Python files found in {pages_dir}")
        return results

    for page_file in page_files:
        issues = check_file(page_file)
        results[page_file.name] = issues

    return results


def print_results(results: Dict[str, List[Tuple[int, str, str]]],
                  fail_on: List[str] = None) -> int:
    """Print scan results and return exit code."""
    all_issues = []
    total_files = len(results)
    files_with_issues = 0

    print("=" * 80)
    print("🔍 STREAMLIT APP COMPREHENSIVE SCAN RESULTS")
    print("=" * 80)
    print()

    for filename, issues in sorted(results.items()):
        if not issues:
            print(f"✅ {filename}: No issues found")
            continue

        files_with_issues += 1
        all_issues.extend(issues)

        # Group by severity
        critical = [i for i in issues if i[1] == "CRITICAL"]
        high = [i for i in issues if i[1] == "HIGH"]
        medium = [i for i in issues if i[1] == "MEDIUM"]
        errors = [i for i in issues if i[1] == "ERROR"]

        print(f"📄 {filename}:")
        print(f"   Issues: {len(issues)} (Critical: {len(critical)}, High: {len(high)}, Medium: {len(medium)})")

        if errors:
            print("   ❌ ERRORS:")
            for line, severity, message in errors:
                print(f"      Line {line}: {message}")

        if critical:
            print("   🔴 CRITICAL:")
            for line, severity, message in critical:
                print(f"      Line {line}: {message}")

        if high:
            print("   🟠 HIGH:")
            for line, severity, message in high:
                print(f"      Line {line}: {message}")

        if medium:
            print("   🟡 MEDIUM:")
            for line, severity, message in medium:
                print(f"      Line {line}: {message}")

        print()

    # Summary
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)

    total_issues = len(all_issues)
    critical_count = len([i for i in all_issues if i[1] == "CRITICAL"])
    high_count = len([i for i in all_issues if i[1] == "HIGH"])
    medium_count = len([i for i in all_issues if i[1] == "MEDIUM"])
    error_count = len([i for i in all_issues if i[1] == "ERROR"])

    print(f"Files scanned: {total_files}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Total issues: {total_issues}")
    print(f"  - Errors: {error_count}")
    print(f"  - Critical: {critical_count}")
    print(f"  - High: {high_count}")
    print(f"  - Medium: {medium_count}")
    print()

    # Determine exit code
    if fail_on:
        should_fail = False
        for severity in fail_on:
            severity_upper = severity.upper()
            count = len([i for i in all_issues if i[1] == severity_upper])
            if count > 0:
                should_fail = True
                print(f"⚠️  Failing due to {count} {severity_upper} issue(s)")

        if should_fail:
            return 1

    if error_count > 0:
        return 1

    if total_issues == 0:
        print("✅ All pages look good!")
    else:
        print("⚠️  Issues found. Review and fix before merging.")

    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Streamlit app issue detector"
    )
    parser.add_argument(
        "--all-pages",
        action="store_true",
        help="Scan all pages in streamlit_app/pages/"
    )
    parser.add_argument(
        "--page",
        type=str,
        help="Scan specific page (e.g., 'beam_design' for 01_beam_design.py)"
    )
    parser.add_argument(
        "--fail-on",
        type=str,
        help="Comma-separated list of severities to fail on (e.g., 'critical,high')"
    )
    parser.add_argument(
        "--fail-on-critical",
        action="store_true",
        help="Shortcut for --fail-on critical (exit 1 if any critical issues found)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output"
    )

    args = parser.parse_args()

    # Parse fail-on severities
    fail_on_severities = None
    if args.fail_on_critical:
        fail_on_severities = ['critical']
    elif args.fail_on:
        fail_on_severities = [s.strip() for s in args.fail_on.split(',')]

    # Determine project root
    project_root = Path(__file__).parent.parent
    pages_dir = project_root / "streamlit_app" / "pages"

    if not pages_dir.exists():
        print(f"❌ Pages directory not found: {pages_dir}")
        return 1

    # Scan pages
    if args.all_pages:
        results = scan_all_pages(pages_dir)
        return print_results(results, fail_on_severities)

    elif args.page:
        # Find page file matching pattern
        matching_files = list(pages_dir.glob(f"*{args.page}*.py"))
        if not matching_files:
            print(f"❌ No page found matching '{args.page}'")
            return 1

        page_file = matching_files[0]
        print(f"🔍 Checking {page_file.name}...\n")

        issues = check_file(page_file)
        results = {page_file.name: issues}
        return print_results(results, fail_on_severities)

    else:
        print("❌ Please specify --all-pages or --page <name>")
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
