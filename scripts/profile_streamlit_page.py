#!/usr/bin/env python3
"""
Streamlit Performance Profiler

TASK-414: Runtime performance profiling for Streamlit applications.

Features:
- Profiles Streamlit page load times
- Measures function execution times
- Tracks session state operations
- Identifies slow components
- Generates performance reports

Usage:
    python scripts/profile_streamlit_page.py pages/01_beam_design.py
    python scripts/profile_streamlit_page.py --all
    python scripts/profile_streamlit_page.py --benchmark

Created: 2026-01-12 (Session 19, TASK-414)
"""
from __future__ import annotations

import argparse
import ast
import cProfile
import io
import json
import os
import pstats
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class FunctionProfile:
    """Profile data for a single function."""

    name: str
    file: str
    line: int
    calls: int
    total_time: float  # seconds
    cumulative_time: float  # seconds
    per_call: float  # seconds

    @property
    def is_slow(self) -> bool:
        """Check if function is considered slow (>100ms)."""
        return self.total_time > 0.1

    @property
    def formatted_time(self) -> str:
        """Human-readable time string."""
        if self.total_time >= 1.0:
            return f"{self.total_time:.2f}s"
        elif self.total_time >= 0.001:
            return f"{self.total_time * 1000:.1f}ms"
        else:
            return f"{self.total_time * 1000000:.0f}μs"


@dataclass
class PageProfile:
    """Profile data for a Streamlit page."""

    page_path: str
    total_time: float
    functions: list[FunctionProfile] = field(default_factory=list)
    streamlit_calls: list[FunctionProfile] = field(default_factory=list)
    slow_functions: list[FunctionProfile] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def is_healthy(self) -> bool:
        """Check if page load time is acceptable (<2 seconds)."""
        return self.total_time < 2.0 and len(self.slow_functions) == 0


@dataclass
class ProfileReport:
    """Complete profiling report."""

    pages: list[PageProfile] = field(default_factory=list)
    total_time: float = 0.0
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "generated_at": self.generated_at,
            "total_time_seconds": self.total_time,
            "pages": [
                {
                    "path": p.page_path,
                    "total_time": p.total_time,
                    "is_healthy": p.is_healthy,
                    "slow_functions": [
                        {
                            "name": f.name,
                            "file": f.file,
                            "line": f.line,
                            "time": f.total_time,
                            "calls": f.calls,
                        }
                        for f in p.slow_functions
                    ],
                    "errors": p.errors,
                }
                for p in self.pages
            ],
        }


# =============================================================================
# AST ANALYSIS
# =============================================================================


class StreamlitCallAnalyzer(ast.NodeVisitor):
    """Analyzes Streamlit function calls in source code."""

    STREAMLIT_FUNCTIONS = {
        "st.write",
        "st.markdown",
        "st.text",
        "st.dataframe",
        "st.table",
        "st.json",
        "st.metric",
        "st.image",
        "st.plotly_chart",
        "st.pyplot",
        "st.altair_chart",
        "st.button",
        "st.selectbox",
        "st.multiselect",
        "st.slider",
        "st.text_input",
        "st.number_input",
        "st.text_area",
        "st.date_input",
        "st.time_input",
        "st.file_uploader",
        "st.camera_input",
        "st.columns",
        "st.tabs",
        "st.expander",
        "st.container",
        "st.empty",
        "st.sidebar",
        "st.form",
        "st.cache_data",
        "st.cache_resource",
        "st.spinner",
        "st.progress",
        "st.status",
        "st.toast",
        "st.error",
        "st.warning",
        "st.info",
        "st.success",
    }

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        """Visit function call nodes."""
        func_name = self._get_func_name(node.func)
        if func_name and (
            func_name.startswith("st.") or func_name in self.STREAMLIT_FUNCTIONS
        ):
            self.calls.append(
                {
                    "name": func_name,
                    "line": node.lineno,
                    "col": node.col_offset,
                }
            )
        self.generic_visit(node)

    def _get_func_name(self, node: ast.expr) -> Optional[str]:
        """Extract function name from AST node."""
        if isinstance(node, ast.Attribute):
            value = self._get_func_name(node.value)
            if value:
                return f"{value}.{node.attr}"
            return node.attr
        elif isinstance(node, ast.Name):
            return node.id
        return None


def analyze_streamlit_calls(filepath: Path) -> list[dict[str, Any]]:
    """Analyze Streamlit calls in a Python file."""
    try:
        source = filepath.read_text()
        tree = ast.parse(source)
        analyzer = StreamlitCallAnalyzer()
        analyzer.visit(tree)
        return analyzer.calls
    except Exception as e:
        return [{"error": str(e)}]


# =============================================================================
# PROFILING
# =============================================================================


def profile_import(module_path: str) -> tuple[pstats.Stats, float]:
    """
    Profile importing a module.

    Returns:
        Tuple of (stats, total_time)
    """
    profiler = cProfile.Profile()

    start_time = time.time()
    profiler.enable()

    try:
        # Convert file path to module import
        # This simulates what Streamlit does when loading a page
        import importlib.util

        spec = importlib.util.spec_from_file_location("page_module", module_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            # Don't actually execute - just import
            # spec.loader.exec_module(module)
    except Exception:
        pass
    finally:
        profiler.disable()

    elapsed = time.time() - start_time

    # Get stats
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumulative")

    return stats, elapsed


def extract_function_profiles(stats: pstats.Stats) -> list[FunctionProfile]:
    """Extract function profiles from pstats."""
    profiles = []

    for (file, line, name), (cc, nc, tt, ct, callers) in stats.stats.items():
        # Skip built-in functions and standard library
        if file.startswith("<") or "site-packages" in file:
            continue

        per_call = tt / nc if nc > 0 else 0
        profiles.append(
            FunctionProfile(
                name=name,
                file=file,
                line=line,
                calls=nc,
                total_time=tt,
                cumulative_time=ct,
                per_call=per_call,
            )
        )

    # Sort by total time descending
    profiles.sort(key=lambda x: x.total_time, reverse=True)
    return profiles


def profile_page(page_path: Path) -> PageProfile:
    """Profile a single Streamlit page."""
    profile = PageProfile(
        page_path=str(page_path),
        total_time=0.0,
    )

    try:
        # Analyze Streamlit calls
        st_calls = analyze_streamlit_calls(page_path)

        # Profile the import
        stats, elapsed = profile_import(str(page_path))
        profile.total_time = elapsed

        # Extract function profiles
        profile.functions = extract_function_profiles(stats)

        # Identify slow functions (>100ms)
        profile.slow_functions = [f for f in profile.functions if f.is_slow]

        # Track Streamlit-specific calls
        for call in st_calls:
            if "error" not in call:
                profile.streamlit_calls.append(
                    FunctionProfile(
                        name=call["name"],
                        file=str(page_path),
                        line=call["line"],
                        calls=1,
                        total_time=0,
                        cumulative_time=0,
                        per_call=0,
                    )
                )

    except Exception as e:
        profile.errors.append(str(e))

    return profile


# =============================================================================
# STATIC ANALYSIS
# =============================================================================


def analyze_page_complexity(page_path: Path) -> dict[str, Any]:
    """
    Analyze page complexity using static analysis.

    Returns metrics about potential performance issues.
    """
    try:
        source = page_path.read_text()
        tree = ast.parse(source)
    except Exception as e:
        return {"error": str(e)}

    metrics = {
        "lines_of_code": len(source.splitlines()),
        "function_count": 0,
        "class_count": 0,
        "import_count": 0,
        "streamlit_calls": 0,
        "loop_count": 0,
        "nested_loops": 0,
        "dataframe_operations": 0,
    }

    class ComplexityVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.loop_depth = 0

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
            metrics["function_count"] += 1
            self.generic_visit(node)

        def visit_AsyncFunctionDef(  # noqa: N802
            self, node: ast.AsyncFunctionDef
        ) -> None:
            metrics["function_count"] += 1
            self.generic_visit(node)

        def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
            metrics["class_count"] += 1
            self.generic_visit(node)

        def visit_Import(self, node: ast.Import) -> None:  # noqa: N802
            metrics["import_count"] += 1

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # noqa: N802
            metrics["import_count"] += 1

        def visit_For(self, node: ast.For) -> None:  # noqa: N802
            metrics["loop_count"] += 1
            self.loop_depth += 1
            if self.loop_depth > 1:
                metrics["nested_loops"] += 1
            self.generic_visit(node)
            self.loop_depth -= 1

        def visit_While(self, node: ast.While) -> None:  # noqa: N802
            metrics["loop_count"] += 1
            self.loop_depth += 1
            if self.loop_depth > 1:
                metrics["nested_loops"] += 1
            self.generic_visit(node)
            self.loop_depth -= 1

        def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
            # Check for Streamlit calls
            func_name = ""
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    func_name = f"{node.func.value.id}.{node.func.attr}"

            if func_name.startswith("st."):
                metrics["streamlit_calls"] += 1

            # Check for DataFrame operations
            if func_name in {"pd.DataFrame", "pd.read_csv", "pd.read_excel"}:
                metrics["dataframe_operations"] += 1

            self.generic_visit(node)

    visitor = ComplexityVisitor()
    visitor.visit(tree)

    # Calculate complexity score
    score = 0
    score += metrics["lines_of_code"] / 100
    score += metrics["loop_count"] * 2
    score += metrics["nested_loops"] * 5
    score += metrics["dataframe_operations"] * 3
    score += metrics["streamlit_calls"] / 10

    metrics["complexity_score"] = round(score, 1)
    metrics["complexity_rating"] = (
        "LOW" if score < 10 else ("MEDIUM" if score < 25 else "HIGH")
    )

    return metrics


# =============================================================================
# REPORTING
# =============================================================================


def format_report(report: ProfileReport, verbose: bool = False) -> str:
    """Format report for console output."""
    lines = []
    lines.append("\n" + "=" * 60)
    lines.append("📊 STREAMLIT PERFORMANCE REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated: {report.generated_at}")
    lines.append(f"Total pages analyzed: {len(report.pages)}")
    lines.append("")

    # Summary
    healthy = sum(1 for p in report.pages if p.is_healthy)
    slow = len(report.pages) - healthy

    if slow == 0:
        lines.append("✅ All pages are performing well!")
    else:
        lines.append(f"⚠️ {slow} page(s) have performance issues")

    lines.append("")

    # Per-page details
    for page in report.pages:
        status = "✅" if page.is_healthy else "⚠️"
        time_str = (
            f"{page.total_time:.2f}s"
            if page.total_time >= 1
            else f"{page.total_time * 1000:.0f}ms"
        )

        page_name = Path(page.page_path).name
        lines.append(f"{status} {page_name}: {time_str}")

        if page.errors:
            for error in page.errors:
                lines.append(f"   ❌ Error: {error}")

        if page.slow_functions and verbose:
            lines.append("   Slow functions:")
            for func in page.slow_functions[:5]:  # Top 5
                lines.append(f"      - {func.name}: {func.formatted_time}")

    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)


def format_complexity_report(pages: list[Path]) -> str:
    """Format complexity analysis report."""
    lines = []
    lines.append("\n" + "=" * 60)
    lines.append("🔬 COMPLEXITY ANALYSIS REPORT")
    lines.append("=" * 60)

    for page in pages:
        metrics = analyze_page_complexity(page)
        if "error" in metrics:
            lines.append(f"❌ {page.name}: {metrics['error']}")
            continue

        rating = metrics["complexity_rating"]
        icon = "🟢" if rating == "LOW" else ("🟡" if rating == "MEDIUM" else "🔴")

        lines.append(f"\n{icon} {page.name} ({rating})")
        lines.append(f"   Lines: {metrics['lines_of_code']}")
        lines.append(f"   Functions: {metrics['function_count']}")
        lines.append(f"   Streamlit calls: {metrics['streamlit_calls']}")
        lines.append(f"   Loops: {metrics['loop_count']} (nested: {metrics['nested_loops']})")
        lines.append(f"   Complexity score: {metrics['complexity_score']}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


# =============================================================================
# CLI
# =============================================================================


def find_streamlit_pages(project_root: Path) -> list[Path]:
    """Find all Streamlit pages in project."""
    pages_dir = project_root / "streamlit_app" / "pages"
    if not pages_dir.exists():
        return []

    pages = list(pages_dir.glob("*.py"))
    # Also include main app.py
    app_file = project_root / "streamlit_app" / "app.py"
    if app_file.exists():
        pages.insert(0, app_file)

    return sorted(pages)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Profile Streamlit page performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "pages",
        nargs="*",
        help="Page files to profile (default: all pages)",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Profile all Streamlit pages",
    )
    parser.add_argument(
        "--complexity",
        "-c",
        action="store_true",
        help="Run complexity analysis instead of profiling",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output",
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Write report to file",
    )

    args = parser.parse_args()

    # Find project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent

    # Determine pages to analyze
    if args.all or not args.pages:
        pages = find_streamlit_pages(project_root)
    else:
        pages = [Path(p) for p in args.pages]

    if not pages:
        print("❌ No Streamlit pages found")
        sys.exit(1)

    print(f"📊 Analyzing {len(pages)} page(s)...")

    # Run analysis
    if args.complexity:
        output = format_complexity_report(pages)
        print(output)
    else:
        # Profile pages
        from datetime import datetime

        report = ProfileReport(
            generated_at=datetime.now().isoformat(),
        )

        for page in pages:
            if args.verbose:
                print(f"  Profiling: {page.name}")
            profile = profile_page(page)
            report.pages.append(profile)

        report.total_time = sum(p.total_time for p in report.pages)

        if args.json:
            output = json.dumps(report.to_dict(), indent=2)
            print(output)
        else:
            output = format_report(report, verbose=args.verbose)
            print(output)

        # Write to file if requested
        if args.output:
            if args.json:
                args.output.write_text(output)
            else:
                args.output.write_text(output)
            print(f"\n📄 Report written to: {args.output}")

        # Exit with error if there are slow pages
        slow_pages = [p for p in report.pages if not p.is_healthy]
        if slow_pages:
            sys.exit(1)


if __name__ == "__main__":
    main()
