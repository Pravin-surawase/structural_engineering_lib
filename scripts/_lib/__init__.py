"""Shared utilities for scripts/ directory.

Sub-modules:
    utils          — Path constants (REPO_ROOT, etc.), run_command, find_python_files
    output         — JSON/table/summary formatting (print_json, print_table, StatusLine)
    ast_helpers    — Safe AST parsing, import/function/class extraction
    agent_registry — Agent discovery from .github/agents/*.agent.md
    scoring        — 11-dimension scoring framework
    agent_data     — I/O for logs/agent-performance data

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

from .agent_registry import (
    AgentInfo,
    SAFETY_CRITICAL_AGENTS,
    discover_agents,
    get_agent_info,
    get_agent_names,
    is_safety_critical,
)

from .scoring import (
    AUTO_SCORED_DIMENSIONS,
    DIMENSIONS,
    MANUAL_DIMENSIONS,
    STRUCTURAL_WEIGHT_OVERRIDES,
    composite_score,
    grade,
)

from .agent_data import (
    BACKUPS_DIR,
    DRIFT_DIR,
    PAPER_DIR,
    PERFORMANCE_DIR,
    SCHEMA_VERSION,
    SESSIONS_DIR,
    TRENDS_DIR,
    ensure_dirs,
    list_sessions,
    load_pending_evolutions,
    load_scorecard_index,
    load_session,
    save_pending_evolutions,
    save_scorecard_index,
    save_session,
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
    # agent_registry
    "AgentInfo",
    "SAFETY_CRITICAL_AGENTS",
    "discover_agents",
    "get_agent_info",
    "get_agent_names",
    "is_safety_critical",
    # scoring
    "AUTO_SCORED_DIMENSIONS",
    "DIMENSIONS",
    "MANUAL_DIMENSIONS",
    "STRUCTURAL_WEIGHT_OVERRIDES",
    "composite_score",
    "grade",
    # agent_data
    "BACKUPS_DIR",
    "DRIFT_DIR",
    "PAPER_DIR",
    "PERFORMANCE_DIR",
    "SCHEMA_VERSION",
    "SESSIONS_DIR",
    "TRENDS_DIR",
    "ensure_dirs",
    "list_sessions",
    "load_pending_evolutions",
    "load_scorecard_index",
    "load_session",
    "save_pending_evolutions",
    "save_scorecard_index",
    "save_session",
]
