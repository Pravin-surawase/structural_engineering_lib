#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
API Contract Testing Script
===========================

Validates that Streamlit pages use correct API signatures and response keys.
This script is designed to run in CI and pre-commit hooks to prevent
API signature mismatches that cause runtime errors.

Usage:
    python scripts/check_api_signatures.py              # Check all pages
    python scripts/check_api_signatures.py --fix        # Show suggested fixes
    python scripts/check_api_signatures.py page.py      # Check specific file

Exit Codes:
    0 - No issues found
    1 - Issues found

Author: AI Agent (Session 24 Part 4)
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

# API Function signatures (canonical)
API_SIGNATURES = {
    "cached_design": {
        "required_params": [
            "mu_knm",
            "vu_kn",
            "b_mm",
            "D_mm",
            "d_mm",
            "fck_nmm2",
            "fy_nmm2",
        ],
        "optional_params": ["exposure", "span_mm"],
    },
    "cached_smart_analysis": {
        "required_params": [
            "mu_knm",
            "vu_kn",
            "b_mm",
            "D_mm",
            "d_mm",
            "fck_nmm2",
            "fy_nmm2",
            "span_mm",
        ],
        "optional_params": ["include_cost", "include_suggestions"],
    },
    "build_design_params": {
        "required_params": [
            "mu_knm",
            "vu_kn",
            "b_mm",
            "D_mm",
            "d_mm",
            "fck_nmm2",
            "fy_nmm2",
            "cover_mm",
        ],
        "optional_params": [],
    },
}

# Response key mappings (correct vs incorrect)
# These are only flagged when used as API parameter names or dict keys
RESPONSE_KEY_MAPPINGS = {
    # Flexure response keys (dict access)
    "Ast_req": "ast_required",
    "Ast_prov": "ast_provided",
    "spacing_mm": "spacing",
    # Note: bar_diameter is valid in UI layer (3D visualizations)
    # Core library uses bar_dia for consistency with IS 456 notation
    "n_bars": "num_bars",
}

# Parameter name variants (only for API calls)
PARAM_NAME_MAPPINGS = {
    "fck": "fck_nmm2",
    "fy": "fy_nmm2",
    "cover": "cover_mm",
}


class APISignatureChecker(ast.NodeVisitor):
    """AST visitor to check API function calls."""

    def __init__(self, filename: str):
        self.filename = filename
        self.issues: list[dict] = []
        self.local_functions: set[str] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track locally defined functions to avoid false positives."""
        self.local_functions.add(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Track locally defined async functions to avoid false positives."""
        self.local_functions.add(node.name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Check function calls for API signature issues."""
        func_name = self._get_func_name(node)

        # Skip if it's a locally defined function (not the API)
        if func_name in API_SIGNATURES and func_name not in self.local_functions:
            self._check_api_call(node, func_name)

        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        """Check dictionary subscript access for incorrect keys.

        Only flags issues when accessing keys that look like API response
        access (e.g., result['Ast_req']), not DataFrame column access.
        """
        if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
            key = node.slice.value

            # Only check RESPONSE_KEY_MAPPINGS for direct dict access
            # Skip if it looks like DataFrame access (common patterns)
            if key in RESPONSE_KEY_MAPPINGS:
                # Check if this is likely DataFrame access by looking at context
                # DataFrame patterns: df["col"], results_df["col"], data["col"]
                if isinstance(node.value, ast.Name):
                    var_name = node.value.id.lower()
                    # Skip DataFrame-like variable names
                    if any(
                        pattern in var_name
                        for pattern in ["df", "data", "result", "row", "record"]
                    ):
                        self.generic_visit(node)
                        return

                correct_key = RESPONSE_KEY_MAPPINGS[key]
                self.issues.append(
                    {
                        "type": "wrong_key",
                        "line": node.lineno,
                        "key": key,
                        "correct_key": correct_key,
                        "message": f"Use '{correct_key}' instead of '{key}'",
                    }
                )

        self.generic_visit(node)

    def _get_func_name(self, node: ast.Call) -> str:
        """Extract function name from call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return ""

    def _check_api_call(self, node: ast.Call, func_name: str) -> None:
        """Check if API call uses correct parameters."""
        spec = API_SIGNATURES[func_name]
        required = set(spec["required_params"])

        # Get keyword arguments used
        used_kwargs = set()
        for keyword in node.keywords:
            if keyword.arg:
                used_kwargs.add(keyword.arg)

        # Check for wrong parameter names (only for known API parameter mappings)
        for kwarg in used_kwargs:
            if kwarg in PARAM_NAME_MAPPINGS:
                correct = PARAM_NAME_MAPPINGS[kwarg]
                self.issues.append(
                    {
                        "type": "wrong_param",
                        "line": node.lineno,
                        "function": func_name,
                        "param": kwarg,
                        "correct_param": correct,
                        "message": f"Use '{correct}' instead of '{kwarg}' in {func_name}()",
                    }
                )

        # Check for missing required parameters (only if using keyword args)
        if used_kwargs:
            missing = required - used_kwargs
            if missing:
                # Allow positional args to satisfy requirements
                positional_count = len(node.args)
                required_list = spec["required_params"]
                covered_by_positional = set(required_list[:positional_count])
                still_missing = missing - covered_by_positional
                if still_missing:
                    self.issues.append(
                        {
                            "type": "missing_params",
                            "line": node.lineno,
                            "function": func_name,
                            "missing": list(still_missing),
                            "message": f"Missing required parameters: {still_missing}",
                        }
                    )


def check_file(filepath: Path) -> list[dict]:
    """Check a single Python file for API signature issues.

    Args:
        filepath: Path to Python file

    Returns:
        List of issue dictionaries
    """
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except SyntaxError as e:
        return [
            {
                "type": "syntax_error",
                "line": e.lineno or 0,
                "message": f"Syntax error: {e.msg}",
            }
        ]

    checker = APISignatureChecker(str(filepath))
    checker.visit(tree)
    return checker.issues


def check_all_pages(pages_dir: Path) -> dict[str, list[dict]]:
    """Check all Streamlit pages for API issues.

    Args:
        pages_dir: Path to pages directory

    Returns:
        Dictionary mapping file names to issues
    """
    results = {}

    for page_file in pages_dir.glob("*.py"):
        if page_file.name.startswith("_"):
            continue

        issues = check_file(page_file)
        if issues:
            results[page_file.name] = issues

    return results


def format_issues(results: dict[str, list[dict]], show_fix: bool = False) -> str:
    """Format issues for display.

    Args:
        results: Dictionary of filename -> issues
        show_fix: Whether to show suggested fixes

    Returns:
        Formatted output string
    """
    lines = []
    total_issues = 0

    for filename, issues in sorted(results.items()):
        lines.append(f"\n📄 {filename}:")
        for issue in issues:
            total_issues += 1
            line_num = issue.get("line", 0)
            issue_type = issue.get("type", "unknown")
            message = issue.get("message", "Unknown issue")

            if issue_type == "wrong_key":
                icon = "🔑"
            elif issue_type == "wrong_param":
                icon = "⚙️"
            elif issue_type == "missing_params":
                icon = "❓"
            else:
                icon = "⚠️"

            lines.append(f"   {icon} Line {line_num}: {message}")

            if show_fix:
                if issue_type in ("wrong_key", "wrong_param"):
                    correct = issue.get("correct_key") or issue.get("correct_param")
                    wrong = issue.get("key") or issue.get("param")
                    lines.append(f"      Fix: Replace '{wrong}' with '{correct}'")

    lines.insert(0, f"\n{'=' * 60}")
    lines.insert(1, "API SIGNATURE CHECK RESULTS")
    lines.insert(2, f"{'=' * 60}")

    lines.append(f"\n{'=' * 60}")
    lines.append(f"Total issues: {total_issues}")
    lines.append(f"Files with issues: {len(results)}")
    lines.append(f"{'=' * 60}")

    return "\n".join(lines)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check Streamlit pages for API signature issues"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Specific files to check (default: all pages)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Show suggested fixes",
    )
    parser.add_argument(
        "--pages-dir",
        default="streamlit_app/pages",
        help="Path to pages directory",
    )

    args = parser.parse_args()

    # Determine project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent

    pages_dir = project_root / args.pages_dir

    if not pages_dir.exists():
        print(f"❌ Pages directory not found: {pages_dir}")
        return 1

    if args.files:
        # Check specific files
        results = {}
        for file_path in args.files:
            path = Path(file_path)
            if not path.exists():
                path = pages_dir / file_path
            if path.exists():
                issues = check_file(path)
                if issues:
                    results[path.name] = issues
    else:
        # Check all pages
        results = check_all_pages(pages_dir)

    if results:
        print(format_issues(results, show_fix=args.fix))
        return 1
    else:
        print("✅ No API signature issues found!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
