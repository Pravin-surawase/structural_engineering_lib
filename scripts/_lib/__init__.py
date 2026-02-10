"""Shared utilities for scripts/ directory.

Three sub-modules:
    utils        — Path constants (REPO_ROOT, etc.), run_command, find_python_files
    output       — JSON/table/summary formatting (print_json, print_table, StatusLine)
    ast_helpers  — Safe AST parsing, import/function/class extraction

Usage from any script in scripts/:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _lib.utils import REPO_ROOT
    # or: from _lib import REPO_ROOT
"""

from .utils import (
    DOCS_DIR,
    PYTHON_DIR,
    REPO_ROOT,
    SCRIPTS_DIR,
    STRUCTURAL_LIB,
    add_python_path,
    find_python_files,
    get_repo_root,
    run_command,
)

from .output import (
    CheckResult,
    StatusLine,
    print_json,
    print_summary,
    print_table,
)

from .ast_helpers import (
    ClassInfo,
    FunctionInfo,
    ImportInfo,
    extract_imports,
    extract_imports_from_file,
    find_classes,
    find_constants,
    find_functions,
    parse_python_file,
)

__all__ = [
    # utils
    "DOCS_DIR",
    "PYTHON_DIR",
    "REPO_ROOT",
    "SCRIPTS_DIR",
    "STRUCTURAL_LIB",
    "add_python_path",
    "find_python_files",
    "get_repo_root",
    "run_command",
    # output
    "CheckResult",
    "StatusLine",
    "print_json",
    "print_summary",
    "print_table",
    # ast_helpers
    "ClassInfo",
    "FunctionInfo",
    "ImportInfo",
    "extract_imports",
    "extract_imports_from_file",
    "find_classes",
    "find_constants",
    "find_functions",
    "parse_python_file",
]
