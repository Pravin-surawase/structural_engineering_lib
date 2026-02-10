#!/usr/bin/env python3
"""Validate Python imports across the project after migration.

Checks that all `from X import Y` and `import X` statements resolve
to actual modules. Reports broken imports with suggestions.

Usage:
    python scripts/validate_imports.py                          # Full scan
    python scripts/validate_imports.py --scope structural_lib   # Just structural_lib
    python scripts/validate_imports.py --fix                    # Auto-fix if stub exists
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()

SEARCH_DIRS = {
    "all": [
        "Python/structural_lib",
        "Python/tests",
        "fastapi_app",
        "scripts",
        "streamlit_app",
        "tests",
    ],
    "structural_lib": ["Python/structural_lib"],
    "tests": ["Python/tests", "tests"],
    "fastapi": ["fastapi_app"],
    "scripts": ["scripts"],
}

# Known external packages (don't report these as broken)
EXTERNAL_PACKAGES = {
    "numpy", "scipy", "pandas", "matplotlib", "plotly",
    "streamlit", "fastapi", "uvicorn", "pydantic",
    "pytest", "hypothesis", "coverage", "ruff",
    "requests", "httpx", "aiohttp",
    "typing", "typing_extensions", "dataclasses",
    "pathlib", "os", "sys", "re", "ast", "json",
    "math", "decimal", "fractions", "collections",
    "functools", "itertools", "operator",
    "subprocess", "argparse", "shutil", "tempfile",
    "io", "csv", "logging", "warnings", "copy",
    "abc", "enum", "contextlib", "textwrap",
    "datetime", "time", "hashlib", "inspect",
    "importlib", "pkgutil", "unittest",
    "docker", "yaml", "toml", "tomli", "tomllib",
    "starlette", "jose", "passlib", "multipart",
    "dotenv", "jinja2", "markupsafe",
    "rich", "click", "typer",
    "__future__", "builtins", "types",
    "concurrent", "threading", "multiprocessing",
    "socket", "http", "urllib", "email",
    "xml", "html", "string", "struct",
    "openpyxl", "xlrd", "xlsxwriter",
    "PIL", "cv2", "sklearn", "torch",
}

SKIP_PATTERNS = {"__pycache__", ".pytest_cache", ".mypy_cache", "node_modules", ".venv"}


def find_python_files(scope: str) -> list[Path]:
    """Find Python files for the given scope."""
    dirs = SEARCH_DIRS.get(scope, SEARCH_DIRS["all"])
    files = []
    for d in dirs:
        path = PROJECT_ROOT / d
        if not path.exists():
            continue
        for f in path.rglob("*.py"):
            if any(skip in f.parts for skip in SKIP_PATTERNS):
                continue
            files.append(f)
    return sorted(files)


def get_top_level_package(module_str: str) -> str:
    """Get the top-level package name from a module string."""
    return module_str.split(".")[0]


def can_resolve_module(module_str: str) -> bool:
    """Check if a module can be resolved."""
    top = get_top_level_package(module_str)
    if top in EXTERNAL_PACKAGES:
        return True

    # Try to find it as a file
    parts = module_str.split(".")

    # Check relative to Python/
    python_dir = PROJECT_ROOT / "Python"

    # Try as package dir
    candidate = python_dir / Path(*parts)
    if candidate.is_dir() and (candidate / "__init__.py").exists():
        return True

    # Try as module file
    candidate = python_dir / Path(*parts[:-1]) / (parts[-1] + ".py") if len(parts) > 1 else python_dir / (parts[0] + ".py")
    if candidate.exists():
        return True

    # Try as module file directly
    candidate = python_dir / Path(*parts).with_suffix(".py")
    if candidate.exists():
        return True

    # Check relative to project root
    candidate = PROJECT_ROOT / Path(*parts)
    if candidate.is_dir() and (candidate / "__init__.py").exists():
        return True
    candidate = PROJECT_ROOT / Path(*parts).with_suffix(".py")
    if candidate.exists():
        return True

    # Try importlib (for installed packages)
    try:
        spec = importlib.util.find_spec(module_str)
        return spec is not None
    except (ModuleNotFoundError, ValueError):
        pass

    return False


def extract_imports(file_path: Path) -> list[tuple[int, str, str]]:
    """Extract all import statements from a Python file.

    Returns list of (line_number, module_string, import_type) tuples.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError):
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((node.lineno, alias.name, "import"))
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:  # Absolute imports only
                imports.append((node.lineno, node.module, "from"))

    return imports


def find_similar_modules(broken: str) -> list[str]:
    """Find modules that are similar to the broken import."""
    suggestions = []
    parts = broken.split(".")

    # Look for the module name in common locations
    module_name = parts[-1]

    # Check structural_lib subdirectories
    lib_dir = PROJECT_ROOT / "Python" / "structural_lib"
    if lib_dir.exists():
        for py_file in lib_dir.rglob(f"{module_name}.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                rel = py_file.relative_to(PROJECT_ROOT / "Python")
                module_path = str(rel).replace("/", ".").replace(".py", "")
                suggestions.append(module_path)
            except ValueError:
                pass

    return suggestions[:3]


def main():
    parser = argparse.ArgumentParser(description="Validate Python imports")
    parser.add_argument(
        "--scope",
        choices=list(SEARCH_DIRS.keys()),
        default="all",
        help="Which area to scan (default: all)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show all imports, not just broken"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("🔍 Python Import Validator")
    print("=" * 60)
    print(f"Scope: {args.scope}")
    print()

    files = find_python_files(args.scope)
    print(f"Scanning {len(files)} Python file(s)...")
    print()

    broken_imports: list[tuple[Path, int, str, str]] = []
    total_imports = 0
    internal_imports = 0

    for py_file in files:
        imports = extract_imports(py_file)
        total_imports += len(imports)

        for line_num, module_str, imp_type in imports:
            top = get_top_level_package(module_str)
            if top in EXTERNAL_PACKAGES:
                continue

            internal_imports += 1

            if not can_resolve_module(module_str):
                broken_imports.append((py_file, line_num, module_str, imp_type))

    # Report
    print(f"📊 Import Statistics:")
    print(f"   Total imports:    {total_imports}")
    print(f"   Internal imports: {internal_imports}")
    print(f"   Broken imports:   {len(broken_imports)}")
    print()

    if broken_imports:
        print("❌ Broken Imports:")
        print("-" * 60)
        current_file = None
        for py_file, line_num, module_str, imp_type in broken_imports:
            if py_file != current_file:
                current_file = py_file
                rel = py_file.relative_to(PROJECT_ROOT)
                print(f"\n  {rel}:")

            suggestions = find_similar_modules(module_str)
            print(f"    Line {line_num}: {imp_type} {module_str}")
            if suggestions:
                print(f"      💡 Did you mean: {', '.join(suggestions)}")
        print()
    else:
        print("✅ All internal imports resolve correctly!")
        print()

    # Exit code
    if broken_imports:
        print(f"⚠️  Found {len(broken_imports)} broken import(s)")
        sys.exit(1)
    else:
        print("✨ Import validation passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
