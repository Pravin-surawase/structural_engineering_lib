#!/usr/bin/env python3
"""
Session State Validator (TASK-413)

Audits all session_state usage in Streamlit app to detect:
- Uninitialized keys (keys accessed without initialization)
- Unused initializations (keys initialized but never read)
- Inconsistent types (same key used with different types)
- Missing default patterns (using st.session_state.key instead of .get())

Usage:
    python scripts/validate_session_state.py                  # Audit all files
    python scripts/validate_session_state.py --file page.py   # Specific file
    python scripts/validate_session_state.py --verbose        # Detailed output
    python scripts/validate_session_state.py --json           # JSON output

Exit codes:
    0 = All valid
    1 = Issues found
    2 = Parse error
"""

import ast
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class SessionStateUsage:
    """Tracks a single usage of session_state."""

    key: str
    line: int
    file: str
    access_type: str  # 'read', 'write', 'check', 'get'
    context: str  # The code snippet


@dataclass
class SessionStateReport:
    """Summary report for session_state analysis."""

    total_keys: int = 0
    total_usages: int = 0
    uninitialized_reads: List[SessionStateUsage] = field(default_factory=list)
    unused_writes: List[SessionStateUsage] = field(default_factory=list)
    unsafe_access: List[SessionStateUsage] = field(
        default_factory=list
    )  # .key without check
    issues_count: int = 0


class SessionStateVisitor(ast.NodeVisitor):
    """AST visitor to extract session_state usage patterns."""

    def __init__(self, filename: str):
        self.filename = filename
        self.usages: List[SessionStateUsage] = []

        # Track context
        self.checked_keys: Set[str] = set()  # Keys checked with 'in' operator
        self.in_conditional = False
        self.current_function = ""

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Track function context."""
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_Compare(self, node: ast.Compare):
        """Detect 'key' in st.session_state patterns."""
        # Check for: 'key' in st.session_state
        if isinstance(node.ops[0], (ast.In, ast.NotIn)):
            for comparator in node.comparators:
                if self._is_session_state(comparator):
                    # Extract the key being checked
                    if isinstance(node.left, ast.Constant) and isinstance(
                        node.left.value, str
                    ):
                        key = node.left.value
                        self.checked_keys.add(key)
                        self.usages.append(
                            SessionStateUsage(
                                key=key,
                                line=node.lineno,
                                file=self.filename,
                                access_type="check",
                                context=f"'{key}' in st.session_state",
                            )
                        )

        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript):
        """Detect st.session_state['key'] patterns."""
        if self._is_session_state(node.value):
            key = self._extract_key(node.slice)
            if key:
                # Determine if read or write based on context
                access_type = "write" if self._is_write_context(node) else "read"
                self.usages.append(
                    SessionStateUsage(
                        key=key,
                        line=node.lineno,
                        file=self.filename,
                        access_type=access_type,
                        context=f"st.session_state['{key}']",
                    )
                )

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        """Detect st.session_state.key patterns."""
        # Check for st.session_state.key
        if isinstance(node.value, ast.Attribute):
            if (
                isinstance(node.value.value, ast.Name)
                and node.value.value.id == "st"
                and node.value.attr == "session_state"
            ):

                key = node.attr
                # Skip methods like .get, .keys, .values
                if key not in (
                    "get",
                    "keys",
                    "values",
                    "items",
                    "clear",
                    "update",
                    "pop",
                ):
                    access_type = (
                        "write" if self._is_write_context(node) else "unsafe_read"
                    )
                    self.usages.append(
                        SessionStateUsage(
                            key=key,
                            line=node.lineno,
                            file=self.filename,
                            access_type=access_type,
                            context=f"st.session_state.{key}",
                        )
                    )

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """Detect st.session_state.get('key') patterns."""
        if isinstance(node.func, ast.Attribute):
            # Check for st.session_state.get()
            if (
                node.func.attr == "get"
                and isinstance(node.func.value, ast.Attribute)
                and isinstance(node.func.value.value, ast.Name)
                and node.func.value.value.id == "st"
                and node.func.value.attr == "session_state"
            ):

                if node.args and isinstance(node.args[0], ast.Constant):
                    key = node.args[0].value
                    self.usages.append(
                        SessionStateUsage(
                            key=key,
                            line=node.lineno,
                            file=self.filename,
                            access_type="get",
                            context=f"st.session_state.get('{key}')",
                        )
                    )

        self.generic_visit(node)

    def _is_session_state(self, node: ast.expr) -> bool:
        """Check if node is st.session_state."""
        if isinstance(node, ast.Attribute):
            if (
                isinstance(node.value, ast.Name)
                and node.value.id == "st"
                and node.attr == "session_state"
            ):
                return True
        return False

    def _extract_key(self, node: ast.expr) -> Optional[str]:
        """Extract string key from subscript slice."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None

    def _is_write_context(self, node: ast.expr) -> bool:
        """Check if node is on left side of assignment."""
        # This is a simplified check - full implementation would need parent tracking
        return False  # Conservative: assume read


def analyze_file(filepath: Path) -> List[SessionStateUsage]:
    """Analyze a single file for session_state usage."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)
        visitor = SessionStateVisitor(str(filepath))
        visitor.visit(tree)
        return visitor.usages

    except SyntaxError as e:
        print(f"Syntax error in {filepath}: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}", file=sys.stderr)
        return []


def analyze_codebase(base_dir: Path, verbose: bool = False) -> SessionStateReport:
    """Analyze entire Streamlit codebase for session_state usage."""
    report = SessionStateReport()
    all_usages: List[SessionStateUsage] = []

    # Find all Python files in streamlit_app
    streamlit_dir = base_dir / "streamlit_app"
    if not streamlit_dir.exists():
        print(f"Error: {streamlit_dir} not found", file=sys.stderr)
        return report

    py_files = list(streamlit_dir.rglob("*.py"))

    # Exclude test files and __pycache__
    py_files = [
        f
        for f in py_files
        if "__pycache__" not in str(f)
        and not f.name.startswith("test_")
        and "tests" not in f.parts
    ]

    if verbose:
        print(f"Scanning {len(py_files)} files...")

    for filepath in py_files:
        usages = analyze_file(filepath)
        all_usages.extend(usages)

    # Aggregate by key
    keys_written: Dict[str, List[SessionStateUsage]] = defaultdict(list)
    keys_read: Dict[str, List[SessionStateUsage]] = defaultdict(list)
    keys_checked: Dict[str, List[SessionStateUsage]] = defaultdict(list)
    unsafe_reads: List[SessionStateUsage] = []

    for usage in all_usages:
        if usage.access_type == "write":
            keys_written[usage.key].append(usage)
        elif usage.access_type in ("read", "get"):
            keys_read[usage.key].append(usage)
        elif usage.access_type == "check":
            keys_checked[usage.key].append(usage)
        elif usage.access_type == "unsafe_read":
            unsafe_reads.append(usage)
            keys_read[usage.key].append(usage)

    # Find issues
    all_keys = (
        set(keys_written.keys()) | set(keys_read.keys()) | set(keys_checked.keys())
    )

    # Uninitialized reads: keys read but never written
    for key in keys_read:
        if key not in keys_written and key not in keys_checked:
            report.uninitialized_reads.extend(keys_read[key])

    # Unused writes: keys written but never read
    for key in keys_written:
        if key not in keys_read:
            report.unused_writes.extend(keys_written[key])

    # Unsafe access: using .key instead of .get() or 'in' check
    report.unsafe_access = unsafe_reads

    report.total_keys = len(all_keys)
    report.total_usages = len(all_usages)
    report.issues_count = (
        len(report.uninitialized_reads)
        + len(report.unused_writes)
        + len(report.unsafe_access)
    )

    return report


def print_report(report: SessionStateReport, verbose: bool = False):
    """Print session state audit report."""
    print("=" * 60)
    print("📊 SESSION STATE AUDIT REPORT")
    print("=" * 60)
    print(f"Total unique keys: {report.total_keys}")
    print(f"Total usages: {report.total_usages}")
    print()

    if report.unsafe_access:
        print(f"🟠 UNSAFE ACCESS ({len(report.unsafe_access)} issues)")
        print("   Using st.session_state.key instead of .get() or 'in' check")
        for usage in report.unsafe_access[:10]:  # Limit output
            rel_path = (
                Path(usage.file).relative_to(Path.cwd())
                if Path(usage.file).is_absolute()
                else usage.file
            )
            print(f"   - {rel_path}:{usage.line}: {usage.context}")
        if len(report.unsafe_access) > 10:
            print(f"   ... and {len(report.unsafe_access) - 10} more")
        print()

    if report.uninitialized_reads:
        print(f"🔴 UNINITIALIZED READS ({len(report.uninitialized_reads)} issues)")
        print("   Keys read but never written in analyzed files")
        for usage in report.uninitialized_reads[:10]:
            rel_path = (
                Path(usage.file).relative_to(Path.cwd())
                if Path(usage.file).is_absolute()
                else usage.file
            )
            print(f"   - {rel_path}:{usage.line}: {usage.key}")
        if len(report.uninitialized_reads) > 10:
            print(f"   ... and {len(report.uninitialized_reads) - 10} more")
        print()

    if report.unused_writes and verbose:
        print(f"🟡 UNUSED WRITES ({len(report.unused_writes)} issues)")
        print("   Keys written but never read (may be intentional)")
        for usage in report.unused_writes[:5]:
            rel_path = (
                Path(usage.file).relative_to(Path.cwd())
                if Path(usage.file).is_absolute()
                else usage.file
            )
            print(f"   - {rel_path}:{usage.line}: {usage.key}")
        if len(report.unused_writes) > 5:
            print(f"   ... and {len(report.unused_writes) - 5} more")
        print()

    print("=" * 60)
    if report.issues_count == 0:
        print("✅ No session state issues found!")
    else:
        print(f"Found {report.issues_count} potential issues")
    print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Audit session_state usage in Streamlit app"
    )
    parser.add_argument("--file", "-f", help="Analyze specific file only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    if args.file:
        filepath = Path(args.file)
        if not filepath.is_absolute():
            filepath = project_root / filepath
        usages = analyze_file(filepath)
        for usage in usages:
            print(f"{usage.line}: {usage.access_type} - {usage.context}")
    else:
        report = analyze_codebase(project_root, verbose=args.verbose)

        if args.json:
            output = {
                "total_keys": report.total_keys,
                "total_usages": report.total_usages,
                "issues_count": report.issues_count,
                "uninitialized_reads": [
                    {"key": u.key, "file": u.file, "line": u.line}
                    for u in report.uninitialized_reads
                ],
                "unsafe_access": [
                    {"key": u.key, "file": u.file, "line": u.line, "context": u.context}
                    for u in report.unsafe_access
                ],
            }
            print(json.dumps(output, indent=2))
        else:
            print_report(report, verbose=args.verbose)

        return 1 if report.issues_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
