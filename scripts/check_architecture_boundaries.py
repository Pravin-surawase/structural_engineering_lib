#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Architecture Boundary Linter.

Enforces the 3-layer architecture by detecting violations:

1. Core Layer (Python/structural_lib/codes/)
   - Pure calculation functions
   - CANNOT import from Application or UI layers

2. Application Layer (Python/structural_lib/api.py, job_runner.py)
   - Orchestrates core functions
   - CANNOT import from UI layer

3. UI Layer (streamlit_app/)
   - Presentation logic only
   - Can import from any layer

Usage:
    python scripts/check_architecture_boundaries.py             # Full check
    python scripts/check_architecture_boundaries.py --fix       # Show fix hints
    python scripts/check_architecture_boundaries.py --json      # JSON output

Exit codes:
    0 - No violations
    1 - Violations detected
    2 - Script error

Created: 2026-01-24 (Session 69)
Reference: docs/architecture/project-overview.md
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

# =============================================================================
# Architecture Rules
# =============================================================================

# Layer definitions (paths relative to project root)
LAYERS = {
    "core": {
        "paths": [
            "Python/structural_lib/codes",
        ],
        "allowed_imports": [
            # Core can only import from standard lib and core
            "structural_lib.codes",
            "structural_lib.constants",
            "math",
            "dataclasses",
            "typing",
            "enum",
            "decimal",
        ],
        "forbidden_imports": [
            "streamlit",
            "pandas",  # Data processing belongs in application layer
            "structural_lib.api",
            "structural_lib.job_runner",
        ],
    },
    "application": {
        "paths": [
            "Python/structural_lib/api.py",
            "Python/structural_lib/job_runner.py",
            "Python/structural_lib/adapters.py",
            "Python/structural_lib/models.py",
        ],
        "allowed_imports": [
            "structural_lib",
            "pydantic",
            "pandas",
            "numpy",
            "dataclasses",
            "typing",
        ],
        "forbidden_imports": [
            "streamlit",
        ],
    },
    "ui": {
        "paths": [
            "streamlit_app",
        ],
        "allowed_imports": [
            # UI can import anything
        ],
        "forbidden_imports": [
            # UI should not import core internals directly
            "structural_lib.codes.is456.flexure",
            "structural_lib.codes.is456.shear",
            # Should use api.py instead
        ],
    },
}

# Patterns that indicate bad architecture
BAD_PATTERNS = {
    "core_io": {
        "description": "Core layer should not do I/O",
        "patterns": ["open(", "Path(", "read_text", "write_text", "print("],
        "layers": ["core"],
    },
    "core_state": {
        "description": "Core layer should be stateless",
        "patterns": ["global ", "session_state", "st.cache"],
        "layers": ["core"],
    },
    "hidden_units": {
        "description": "Implicit unit conversions are dangerous",
        "patterns": ["* 1000", "/ 1000", "* 1e6", "/ 1e6"],
        "layers": ["core"],
        "severity": "warning",
    },
}


# File patterns to exclude from checking
EXCLUDE_PATTERNS = [
    "__pycache__",
    "_test.py",
    "test_",
    "_cli.py",  # CLI files are allowed to do I/O
    "clause_cli.py",  # Specific CLI file
]


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class Violation:
    """Represents an architecture violation."""

    file: Path
    line: int
    layer: str
    violation_type: str
    message: str
    severity: str = "error"
    fix_hint: str = ""


@dataclass
class ImportInfo:
    """Information about an import statement."""

    module: str
    names: list[str]
    line: int
    is_from_import: bool


@dataclass
class ArchitectureReport:
    """Report of architecture check results."""

    violations: list[Violation] = field(default_factory=list)
    files_checked: int = 0
    layers_analyzed: dict = field(default_factory=dict)

    @property
    def has_errors(self) -> bool:
        return any(v.severity == "error" for v in self.violations)


# =============================================================================
# Import Extraction
# =============================================================================


def extract_imports(file_path: Path) -> Iterator[ImportInfo]:
    """Extract all imports from a Python file."""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"  ⚠️  Skipping {file_path}: {e}")
        return

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield ImportInfo(
                    module=alias.name,
                    names=[alias.asname or alias.name],
                    line=node.lineno,
                    is_from_import=False,
                )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = [alias.name for alias in node.names]
            yield ImportInfo(
                module=module,
                names=names,
                line=node.lineno,
                is_from_import=True,
            )


def extract_patterns(file_path: Path) -> Iterator[tuple[str, int]]:
    """Extract suspicious patterns from source code."""
    try:
        source = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return

    for i, line in enumerate(source.splitlines(), 1):
        # Skip comments
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        yield line, i


# =============================================================================
# Layer Detection
# =============================================================================


def get_layer(file_path: Path, project_root: Path) -> str | None:
    """Determine which layer a file belongs to."""
    rel_path = str(file_path.relative_to(project_root))

    for layer_name, config in LAYERS.items():
        for layer_path in config["paths"]:
            if rel_path.startswith(layer_path):
                return layer_name

    return None


# =============================================================================
# Violation Detection
# =============================================================================


def check_imports(
    file_path: Path, layer: str, project_root: Path
) -> Iterator[Violation]:
    """Check imports for layer violations."""
    config = LAYERS[layer]
    forbidden = config["forbidden_imports"]

    for imp in extract_imports(file_path):
        # Check if import is forbidden for this layer
        for forbidden_pattern in forbidden:
            if imp.module.startswith(forbidden_pattern) or forbidden_pattern in imp.names:
                fix_hint = ""
                if layer == "core" and forbidden_pattern == "streamlit":
                    fix_hint = "Move Streamlit code to streamlit_app/"
                elif layer == "core" and forbidden_pattern == "pandas":
                    fix_hint = "Use pure Python in core; pandas belongs in application layer"
                elif layer == "application" and forbidden_pattern == "streamlit":
                    fix_hint = "Use dependency injection to receive UI callbacks"

                yield Violation(
                    file=file_path,
                    line=imp.line,
                    layer=layer,
                    violation_type="forbidden_import",
                    message=f"Layer '{layer}' cannot import '{imp.module}'",
                    fix_hint=fix_hint,
                )


def check_patterns(file_path: Path, layer: str) -> Iterator[Violation]:
    """Check for bad patterns in code."""
    for pattern_name, config in BAD_PATTERNS.items():
        if layer not in config.get("layers", []):
            continue

        severity = config.get("severity", "error")
        patterns = config["patterns"]

        for line, lineno in extract_patterns(file_path):
            for pattern in patterns:
                if pattern in line:
                    yield Violation(
                        file=file_path,
                        line=lineno,
                        layer=layer,
                        violation_type=pattern_name,
                        message=f"{config['description']}: found '{pattern}'",
                        severity=severity,
                    )


# =============================================================================
# Main Scanner
# =============================================================================


def scan_architecture(project_root: Path) -> ArchitectureReport:
    """Scan project for architecture violations."""
    report = ArchitectureReport()

    for layer_name, config in LAYERS.items():
        layer_files = 0
        layer_violations = 0

        for layer_path in config["paths"]:
            full_path = project_root / layer_path

            if not full_path.exists():
                continue

            # Get all Python files
            if full_path.is_file():
                files = [full_path]
            else:
                files = list(full_path.rglob("*.py"))

            for py_file in files:
                # Skip excluded patterns (cache, tests, CLI files)
                if any(pattern in str(py_file) for pattern in EXCLUDE_PATTERNS):
                    continue

                layer_files += 1
                report.files_checked += 1

                # Check imports
                for violation in check_imports(py_file, layer_name, project_root):
                    report.violations.append(violation)
                    layer_violations += 1

                # Check patterns
                for violation in check_patterns(py_file, layer_name):
                    report.violations.append(violation)
                    layer_violations += 1

        report.layers_analyzed[layer_name] = {
            "files": layer_files,
            "violations": layer_violations,
        }

    return report


# =============================================================================
# Output Formatting
# =============================================================================


def format_console_report(report: ArchitectureReport, show_fix: bool = False) -> str:
    """Format report for console output."""
    lines = []
    lines.append("=" * 60)
    lines.append("🏗️  Architecture Boundary Check")
    lines.append("=" * 60)
    lines.append("")

    # Summary
    lines.append("Summary:")
    lines.append(f"  Files checked: {report.files_checked}")
    lines.append(f"  Total violations: {len(report.violations)}")
    errors = sum(1 for v in report.violations if v.severity == "error")
    warnings = sum(1 for v in report.violations if v.severity == "warning")
    lines.append(f"  Errors: {errors}, Warnings: {warnings}")
    lines.append("")

    # Layer breakdown
    lines.append("Layers analyzed:")
    for layer, stats in report.layers_analyzed.items():
        status = "✅" if stats["violations"] == 0 else "❌"
        lines.append(f"  {status} {layer}: {stats['files']} files, {stats['violations']} violations")
    lines.append("")

    # Violations by layer
    if report.violations:
        lines.append("-" * 60)
        lines.append("Violations:")
        lines.append("-" * 60)

        by_layer = {}
        for v in report.violations:
            by_layer.setdefault(v.layer, []).append(v)

        for layer, violations in by_layer.items():
            lines.append(f"\n📦 {layer.upper()} LAYER:")
            for v in sorted(violations, key=lambda x: (str(x.file), x.line)):
                icon = "🔴" if v.severity == "error" else "🟡"
                lines.append(f"  {icon} {v.file}:{v.line}")
                lines.append(f"     {v.message}")
                if show_fix and v.fix_hint:
                    lines.append(f"     💡 Fix: {v.fix_hint}")
    else:
        lines.append("✅ No architecture violations found!")

    lines.append("")
    return "\n".join(lines)


def format_json_report(report: ArchitectureReport) -> str:
    """Format report as JSON."""
    data = {
        "summary": {
            "files_checked": report.files_checked,
            "total_violations": len(report.violations),
            "errors": sum(1 for v in report.violations if v.severity == "error"),
            "warnings": sum(1 for v in report.violations if v.severity == "warning"),
            "has_errors": report.has_errors,
        },
        "layers": report.layers_analyzed,
        "violations": [
            {
                "file": str(v.file),
                "line": v.line,
                "layer": v.layer,
                "type": v.violation_type,
                "message": v.message,
                "severity": v.severity,
                "fix_hint": v.fix_hint,
            }
            for v in report.violations
        ],
    }
    return json.dumps(data, indent=2)


# =============================================================================
# Main Entry Point
# =============================================================================


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check architecture layer boundaries"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Show fix hints for violations",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--layer",
        choices=["core", "application", "ui"],
        help="Check only specific layer",
    )

    args = parser.parse_args()

    # Find project root
    project_root = Path(__file__).parent.parent

    if not args.json:
        print(f"Scanning {project_root}...")

    # Scan
    report = scan_architecture(project_root)

    # Filter by layer if specified
    if args.layer:
        report.violations = [v for v in report.violations if v.layer == args.layer]

    # Output
    if args.json:
        print(format_json_report(report))
    else:
        print(format_console_report(report, show_fix=args.fix))

    # Exit code
    return 1 if report.has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
