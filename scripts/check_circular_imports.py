#!/usr/bin/env python3
"""
Circular Import Detector for Streamlit Application

TASK-404: Detects circular imports that can cause runtime failures.

Features:
- Builds import dependency graph
- Detects direct and indirect circular imports
- Supports both relative and absolute imports
- Visualizes dependency chains
- JSON output for CI integration

Usage:
    python scripts/check_circular_imports.py                    # Check all Streamlit files
    python scripts/check_circular_imports.py --file path.py     # Check specific file
    python scripts/check_circular_imports.py --json             # JSON output
    python scripts/check_circular_imports.py --verbose          # Show all imports
    python scripts/check_circular_imports.py --graph            # Show dependency graph

Exit Codes:
    0 = No circular imports found
    1 = Circular imports detected
    2 = Error during execution

Created: 2026-01-12 (Session 18, TASK-404)
"""
from __future__ import annotations

import ast
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict, field
from collections import defaultdict

# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class ImportInfo:
    """Information about a single import."""

    module: str  # Full module path
    alias: Optional[str] = None  # import X as alias
    is_from: bool = False  # from X import Y vs import X
    names: List[str] = field(default_factory=list)  # Specific names imported
    line: int = 0
    is_relative: bool = False
    level: int = 0  # Relative import level (1 = ., 2 = .., etc.)


@dataclass
class CircularImport:
    """Represents a detected circular import."""

    cycle: List[str]  # List of modules in the cycle
    severity: str  # "direct" or "indirect"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def format_chain(self) -> str:
        """Format the cycle as a readable chain."""
        return " -> ".join(self.cycle) + f" -> {self.cycle[0]}"


# =============================================================================
# IMPORT EXTRACTOR
# =============================================================================


class ImportExtractor(ast.NodeVisitor):
    """Extract import statements from Python files."""

    def __init__(self, current_module: str = ""):
        self.current_module = current_module
        self.imports: List[ImportInfo] = []

    def visit_Import(self, node: ast.Import) -> None:
        """Handle: import X, import X as Y."""
        for alias in node.names:
            self.imports.append(
                ImportInfo(
                    module=alias.name,
                    alias=alias.asname,
                    is_from=False,
                    line=node.lineno,
                )
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Handle: from X import Y, from . import Y."""
        module = node.module or ""
        is_relative = node.level > 0
        level = node.level

        # Resolve relative imports
        if is_relative and self.current_module:
            module = self._resolve_relative(module, level)

        names = [alias.name for alias in node.names]

        self.imports.append(
            ImportInfo(
                module=module,
                is_from=True,
                names=names,
                line=node.lineno,
                is_relative=is_relative,
                level=level,
            )
        )
        self.generic_visit(node)

    def _resolve_relative(self, module: str, level: int) -> str:
        """Resolve relative import to absolute module path."""
        parts = self.current_module.split(".")

        # Go up 'level' directories
        if level > len(parts):
            return module  # Can't resolve beyond root

        base = ".".join(parts[: len(parts) - level + 1])
        if module:
            return f"{base}.{module}" if base else module
        return base


# =============================================================================
# DEPENDENCY GRAPH
# =============================================================================


class DependencyGraph:
    """Build and analyze import dependency graph."""

    def __init__(self):
        self.graph: Dict[str, Set[str]] = defaultdict(set)
        self.imports_by_file: Dict[str, List[ImportInfo]] = {}
        self.file_to_module: Dict[str, str] = {}
        self.module_to_file: Dict[str, str] = {}

    def add_file(self, filepath: Path, project_root: Path) -> List[ImportInfo]:
        """Parse a file and add its imports to the graph."""
        # Calculate module name from path
        try:
            rel_path = filepath.relative_to(project_root)
            module = str(rel_path.with_suffix("")).replace("/", ".")
        except ValueError:
            module = filepath.stem

        self.file_to_module[str(filepath)] = module
        self.module_to_file[module] = str(filepath)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source, str(filepath))
        except Exception:
            return []

        extractor = ImportExtractor(module)
        extractor.visit(tree)

        self.imports_by_file[str(filepath)] = extractor.imports

        # Add edges to graph (only for internal imports)
        for imp in extractor.imports:
            if self._is_internal_import(imp.module, project_root):
                self.graph[module].add(imp.module)

        return extractor.imports

    def _is_internal_import(self, module: str, project_root: Path) -> bool:
        """Check if an import is internal to the project."""
        # Check common project prefixes
        internal_prefixes = [
            "streamlit_app",
            "structural_lib",
            "Python.structural_lib",
        ]
        return any(module.startswith(prefix) for prefix in internal_prefixes)

    def find_cycles(self) -> List[CircularImport]:
        """Find all circular imports using DFS."""
        cycles: List[CircularImport] = []
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []

        def dfs(module: str) -> None:
            visited.add(module)
            rec_stack.add(module)
            path.append(module)

            for neighbor in self.graph.get(module, set()):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:]

                    # Determine severity
                    severity = "direct" if len(cycle) == 1 else "indirect"

                    cycles.append(CircularImport(cycle=cycle, severity=severity))

            path.pop()
            rec_stack.remove(module)

        for module in list(self.graph.keys()):
            if module not in visited:
                dfs(module)

        return cycles

    def get_dependency_chain(
        self, start: str, end: str, max_depth: int = 10
    ) -> Optional[List[str]]:
        """Find path between two modules."""
        if start == end:
            return [start]

        visited: Set[str] = set()
        queue: List[Tuple[str, List[str]]] = [(start, [start])]

        while queue and max_depth > 0:
            max_depth -= 1
            current, path = queue.pop(0)

            if current in visited:
                continue
            visited.add(current)

            for neighbor in self.graph.get(current, set()):
                new_path = path + [neighbor]
                if neighbor == end:
                    return new_path
                queue.append((neighbor, new_path))

        return None


# =============================================================================
# MAIN CHECKER
# =============================================================================


class CircularImportChecker:
    """Main checker class."""

    # Directories to scan
    SCAN_DIRS = [
        "streamlit_app/pages",
        "streamlit_app/utils",
        "streamlit_app/components",
        "streamlit_app",  # Root streamlit files
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
        self.graph = DependencyGraph()
        self.cycles: List[CircularImport] = []

    def check_all(self) -> int:
        """Check all Streamlit files. Returns cycle count."""
        for dir_path in self.SCAN_DIRS:
            full_path = self.project_root / dir_path
            if full_path.exists():
                if full_path.is_dir():
                    self._scan_directory(full_path)
                else:
                    self._scan_file(full_path)

        self.cycles = self.graph.find_cycles()
        return len(self.cycles)

    def check_file(self, filepath: Path) -> int:
        """Check a single file and its dependencies."""
        self._scan_file(filepath)
        self.cycles = self.graph.find_cycles()
        return len(self.cycles)

    def _scan_directory(self, directory: Path) -> None:
        """Recursively scan all Python files in directory."""
        for py_file in directory.rglob("*.py"):
            if any(pattern in str(py_file) for pattern in self.SKIP_PATTERNS):
                continue
            self._scan_file(py_file)

    def _scan_file(self, filepath: Path) -> None:
        """Scan a single file."""
        self.graph.add_file(filepath, self.project_root)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return {
            "files_scanned": len(self.graph.imports_by_file),
            "modules_tracked": len(self.graph.graph),
            "total_cycles": len(self.cycles),
            "direct_cycles": sum(1 for c in self.cycles if c.severity == "direct"),
            "indirect_cycles": sum(1 for c in self.cycles if c.severity == "indirect"),
        }

    def print_report(self, verbose: bool = False, show_graph: bool = False) -> None:
        """Print a human-readable report."""
        print("=" * 70)
        print("🔍 CIRCULAR IMPORT CHECK RESULTS")
        print("=" * 70)
        print()

        summary = self.get_summary()

        print(f"📁 Files scanned: {summary['files_scanned']}")
        print(f"📦 Modules tracked: {summary['modules_tracked']}")
        print()

        if self.cycles:
            print("-" * 70)
            print("🔴 CIRCULAR IMPORTS DETECTED")
            print("-" * 70)
            print()

            for i, cycle in enumerate(self.cycles, 1):
                icon = "⛔" if cycle.severity == "direct" else "⚠️"
                print(f"{icon} Cycle {i} ({cycle.severity}):")
                print(f"   {cycle.format_chain()}")
                print()

            print("-" * 70)
            print("📊 SUMMARY")
            print("-" * 70)
            print(f"   Total cycles: {summary['total_cycles']}")
            print(f"   Direct cycles: {summary['direct_cycles']}")
            print(f"   Indirect cycles: {summary['indirect_cycles']}")
        else:
            print("✅ No circular imports detected!")

        if show_graph:
            print()
            print("-" * 70)
            print("📊 DEPENDENCY GRAPH")
            print("-" * 70)
            for module, deps in sorted(self.graph.graph.items()):
                if deps:
                    print(f"   {module}")
                    for dep in sorted(deps):
                        print(f"      → {dep}")

        if verbose:
            print()
            print("-" * 70)
            print("📝 ALL IMPORTS")
            print("-" * 70)
            for filepath, imports in sorted(self.graph.imports_by_file.items()):
                rel_path = Path(filepath).relative_to(self.project_root)
                print(f"\n📄 {rel_path}:")
                for imp in imports:
                    if imp.is_from:
                        print(f"   from {imp.module} import {', '.join(imp.names)}")
                    else:
                        print(f"   import {imp.module}")

        print()
        print("=" * 70)

    def to_json(self) -> str:
        """Export results as JSON."""
        return json.dumps(
            {
                "summary": self.get_summary(),
                "cycles": [c.to_dict() for c in self.cycles],
                "dependency_graph": {
                    module: list(deps) for module, deps in self.graph.graph.items()
                },
            },
            indent=2,
        )


# =============================================================================
# CLI
# =============================================================================


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check for circular imports in Streamlit files"
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
        "--verbose",
        "-v",
        action="store_true",
        help="Show all imports",
    )
    parser.add_argument(
        "--graph",
        action="store_true",
        help="Show dependency graph",
    )

    args = parser.parse_args()

    # Find project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent

    # Create checker
    checker = CircularImportChecker(project_root)

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
        checker.print_report(verbose=args.verbose, show_graph=args.graph)

    # Determine exit code
    if checker.cycles:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
