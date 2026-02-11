#!/usr/bin/env python3
"""Unified governance checker — folder structure + compliance validation.

Consolidates two former scripts into one with subcommands:
  --structure    Validate folder structure (root limits, naming, Python lib)
  --compliance   Check governance compliance (roles, redirect stubs, metadata)
  --full         Run all checks (default)

Replaces:
  - validate_folder_structure.py
  - check_governance_compliance.py

Usage:
    python scripts/check_governance.py                    # All checks
    python scripts/check_governance.py --structure        # Folder structure only
    python scripts/check_governance.py --compliance       # Governance compliance only
    python scripts/check_governance.py --lib-only         # Python lib structure only
    python scripts/check_governance.py --json             # JSON output

Exit Codes:
    0: All checks pass
    1: Violations found
"""
from __future__ import annotations

import argparse
import ast
import copy
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT

# ═══════════════════════════════════════════════════════════════════════════
# GOVERNANCE RULES
# ═══════════════════════════════════════════════════════════════════════════

GOVERNANCE_LIMITS_PATH = REPO_ROOT / "docs" / "guidelines" / "governance-limits.json"

DEFAULT_RULES = {
    "root": {
        "max_files": 15,
        "allowed_extensions": [
            ".md", ".txt", ".toml", ".yaml", ".yml", ".json",
            ".cfg", ".ini", ".cff", ".py", ".ipynb",
        ],
        "allowed_files": [
            "README.md", "CHANGELOG.md", "CONTRIBUTING.md", "LICENSE",
            "LICENSE_ENGINEERING.md", "CODE_OF_CONDUCT.md", "AUTHORS.md",
            "pyproject.toml", ".gitignore", ".pre-commit-config.yaml",
            "CITATION.cff", "llms.txt",
            "Dockerfile", "Dockerfile.fastapi",
            "docker-compose.yml", "docker-compose.dev.yml",
            "pytest.ini", "requirements.txt",
            "test_quality_assessment.py", "test_scanner_detection.py",
            "test_xlwings_bridge.py",
        ],
    },
    "docs_root": {
        "max_files": 5,
        "allowed_files": [
            "README.md", "TASKS.md", "SESSION_LOG.md", "CHANGELOG.md", "TODO.md",
        ],
    },
    "agents_root": {
        "max_files": 5,
        "allowed_files": ["README.md", "index.md", "index.json"],
    },
    "category_folders": {
        "required": [
            "docs/getting-started", "docs/reference", "docs/contributing",
            "docs/architecture", "docs/guidelines", "docs/agents",
        ],
        "must_have_readme": True,
    },
    "naming": {
        "docs_pattern": r"^(v\d+\.\d+(-v\d+\.\d+)?[-_])?(task-\d+\.\d+[-_])?[a-z0-9\-_]+([-_][a-z0-9\-_]+)*\.md$",
        "docs_preferred": r"^(v\d+\.\d+[-])?[a-z0-9\-]+([-][a-z0-9\-]+)*\.md$",
        "folder_pattern": r"^[a-z0-9\-_]+$",
        "folder_preferred": r"^[a-z0-9\-]+$",
    },
    "dated_files": {
        "allowed_locations": [
            "docs/_active", "docs/_archive", "docs/planning", "docs/_internal",
            "docs/research", "docs/architecture", "docs/reference",
            "streamlit_app/docs",
        ],
        "pattern": r"-202[0-9]-",
    },
    "python_lib": {
        "required_folders": [
            "core",
            "codes",
            "codes/is456",
            "services",
            "insights",
            "reports",
            "visualization",
        ],
        "required_entry_files": [
            "core/__init__.py",
            "codes/__init__.py",
            "codes/is456/__init__.py",
            "services/__init__.py",
            "services/api.py",
            "insights/__init__.py",
            "reports/__init__.py",
            "visualization/__init__.py",
        ],
        "layer_imports": {
            "core": ["core"],
            "codes": ["core", "codes"],
            "services": ["core", "codes", "services"],
            "insights": ["core", "codes", "services", "insights", "reports", "visualization"],
            "reports": ["core", "codes", "services", "insights", "reports", "visualization"],
            "visualization": ["core", "codes", "services", "insights", "reports", "visualization"],
        },
        "layer_import_exceptions": {
            "codes/is456/detailing.py": ["visualization"],
            "services/api.py": ["insights", "visualization"],
            "services/intelligence.py": ["insights"],
            "services/rebar.py": ["visualization"],
        },
    },
}

RULES = copy.deepcopy(DEFAULT_RULES)


# ═══════════════════════════════════════════════════════════════════════════
# SHARED DATA MODEL
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class GovernanceIssue:
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, ERROR, WARNING, INFO
    location: str
    rule: str
    message: str
    files: list[str] = field(default_factory=list)


@dataclass
class GovernanceReport:
    errors: list[GovernanceIssue] = field(default_factory=list)
    warnings: list[GovernanceIssue] = field(default_factory=list)
    info: list[str] = field(default_factory=list)
    passed: list[str] = field(default_factory=list)

    def add_error(self, msg: str, **kw: Any) -> None:
        self.errors.append(GovernanceIssue(severity="ERROR", message=msg, **kw))

    def add_warning(self, msg: str, **kw: Any) -> None:
        self.warnings.append(GovernanceIssue(severity="WARNING", message=msg, **kw))

    def add_info(self, msg: str) -> None:
        self.info.append(msg)

    def add_pass(self, check: str) -> None:
        self.passed.append(check)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


def _deep_merge_rules(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge governance overrides into default rules."""
    for key, value in overrides.items():
        if (
            key in base
            and isinstance(base[key], dict)
            and isinstance(value, dict)
        ):
            _deep_merge_rules(base[key], value)
        else:
            base[key] = value
    return base


def load_governance_rules(report: GovernanceReport) -> dict[str, Any]:
    """Load governance limits from the shared JSON source-of-truth."""
    rules = copy.deepcopy(DEFAULT_RULES)
    if not GOVERNANCE_LIMITS_PATH.exists():
        report.add_warning(
            f"Governance limits file not found: {GOVERNANCE_LIMITS_PATH.relative_to(REPO_ROOT)}",
            location="docs/guidelines/",
            rule="Governance config",
        )
        return rules

    try:
        payload = json.loads(GOVERNANCE_LIMITS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        report.add_error(
            f"Invalid JSON in governance limits file: {exc}",
            location=str(GOVERNANCE_LIMITS_PATH.relative_to(REPO_ROOT)),
            rule="Governance config",
        )
        return rules
    except OSError as exc:
        report.add_error(
            f"Cannot read governance limits file: {exc}",
            location=str(GOVERNANCE_LIMITS_PATH.relative_to(REPO_ROOT)),
            rule="Governance config",
        )
        return rules

    if not isinstance(payload, dict):
        report.add_error(
            "Governance limits file must contain a JSON object",
            location=str(GOVERNANCE_LIMITS_PATH.relative_to(REPO_ROOT)),
            rule="Governance config",
        )
        return rules

    merged = _deep_merge_rules(rules, payload)
    report.add_info(
        f"✅ Loaded governance limits from {GOVERNANCE_LIMITS_PATH.relative_to(REPO_ROOT)}"
    )
    return merged


# ═══════════════════════════════════════════════════════════════════════════
# STRUCTURE CHECKS (from validate_folder_structure.py)
# ═══════════════════════════════════════════════════════════════════════════

def check_root_files(report: GovernanceReport) -> None:
    """Check project root file count and content."""
    root_files = [
        f for f in REPO_ROOT.iterdir()
        if f.is_file() and not f.name.startswith(".")
    ]
    if len(root_files) > RULES["root"]["max_files"]:
        report.add_error(
            f"Root directory has {len(root_files)} files, max is {RULES['root']['max_files']}",
            location="/", rule="Root max ≤15 files",
        )
    else:
        report.add_pass(f"Root file count ({len(root_files)} ≤ {RULES['root']['max_files']})")

    allowed = RULES["root"]["allowed_files"]
    for f in root_files:
        if f.name not in allowed and f.suffix not in RULES["root"]["allowed_extensions"]:
            report.add_warning(
                f"Unexpected file in root: {f.name}",
                location="/", rule="Root allowed files",
            )


def check_docs_root(report: GovernanceReport) -> None:
    """Check docs/ root file count."""
    docs_path = REPO_ROOT / "docs"
    if not docs_path.exists():
        report.add_error("docs/ directory not found", location="docs/", rule="Required dirs")
        return
    docs_files = [f for f in docs_path.iterdir() if f.is_file() and f.suffix == ".md"]
    if len(docs_files) > RULES["docs_root"]["max_files"]:
        report.add_error(
            f"docs/ root has {len(docs_files)} files, max is {RULES['docs_root']['max_files']}",
            location="docs/", rule="docs/ root max ≤5",
            files=[f.name for f in docs_files],
        )
    else:
        report.add_pass(f"docs/ root file count ({len(docs_files)} ≤ {RULES['docs_root']['max_files']})")


def check_agents_root(report: GovernanceReport) -> None:
    """Check agents/ root file count and structure."""
    agents_path = REPO_ROOT / "agents"
    if not agents_path.exists():
        report.add_warning("agents/ directory not found", location="agents/", rule="Required dirs")
        return

    # Check file count
    agents_files = [f for f in agents_path.iterdir() if f.is_file() and f.suffix == ".md"]
    if len(agents_files) > RULES["agents_root"]["max_files"]:
        report.add_error(
            f"agents/ root has {len(agents_files)} files, max is {RULES['agents_root']['max_files']}",
            location="agents/", rule="agents/ root max ≤5",
            files=[f.name for f in agents_files],
        )

    # Check role files are in agents/roles/
    role_files = [
        "ARCHITECT.md", "CLIENT.md", "DEV.md", "DEVOPS.md", "DOCS.md",
        "INTEGRATION.md", "PM.md", "RESEARCHER.md", "SUPPORT.md",
        "TESTER.md", "UI.md",
    ]
    roles_in_root = [f for f in role_files if (agents_path / f).exists()]
    if roles_in_root:
        report.add_error(
            f"Found {len(roles_in_root)} role files in agents/ root (should be in agents/roles/)",
            location="agents/", rule="Role files in agents/roles/",
            files=roles_in_root,
        )

    # Check roles/ exists
    if not (agents_path / "roles").exists():
        report.add_error(
            "agents/roles/ directory missing",
            location="agents/roles/", rule="Required subdirs",
        )
    else:
        report.add_pass("agents/roles/ structure")


def check_category_folders(report: GovernanceReport) -> None:
    """Check required category folders exist and have README."""
    for folder in RULES["category_folders"]["required"]:
        folder_path = REPO_ROOT / folder
        if not folder_path.exists():
            report.add_warning(f"Required folder not found: {folder}/", location=folder, rule="Required dirs")
        elif RULES["category_folders"]["must_have_readme"]:
            readme = folder_path / "README.md"
            if not readme.exists():
                report.add_warning(f"Category folder missing README.md: {folder}/", location=folder, rule="README required")
    report.add_pass("Category folders check")


def check_dated_files(report: GovernanceReport) -> None:
    """Check dated files are in allowed locations."""
    pattern = re.compile(RULES["dated_files"]["pattern"])
    allowed_locations = RULES["dated_files"]["allowed_locations"]
    violations = 0
    for md_file in REPO_ROOT.rglob("*.md"):
        if pattern.search(md_file.name):
            rel_path = md_file.relative_to(REPO_ROOT)
            in_allowed = any(str(rel_path).startswith(loc) for loc in allowed_locations)
            if not in_allowed:
                report.add_error(
                    f"Dated file in wrong location: {rel_path}",
                    location=str(rel_path), rule="Dated files location",
                )
                violations += 1
    if violations == 0:
        report.add_pass("Dated files location")


def check_naming_conventions(report: GovernanceReport) -> None:
    """Check file and folder naming conventions."""
    docs_pattern = re.compile(RULES["naming"]["docs_pattern"])
    folder_pattern = re.compile(RULES["naming"]["folder_pattern"])
    docs_path = REPO_ROOT / "docs"
    if not docs_path.exists():
        return

    skip_names = {"README.md", "TASKS.md", "SESSION_LOG.md", "CHANGELOG.md"}
    skip_paths = ["_internal", "_archive", "_references", "research/", "getting-started/NEW-DEVELOPER"]

    for md_file in docs_path.rglob("*.md"):
        if md_file.name in skip_names:
            continue
        rel_path = str(md_file.relative_to(REPO_ROOT))
        if any(skip in rel_path for skip in skip_paths):
            continue
        if not docs_pattern.match(md_file.name):
            report.add_error(
                f"Invalid doc filename: {md_file.relative_to(REPO_ROOT)}",
                location=rel_path, rule="Naming conventions",
            )

    skip_folder_names = {"images", "assets", "_active", "_archive", "adr"}
    for folder in docs_path.rglob("*"):
        if not folder.is_dir() or folder.name.startswith(".") or folder.name.startswith("_"):
            continue
        if folder.name in skip_folder_names:
            continue
        if "data" in str(folder.relative_to(REPO_ROOT)) or "navigation_study" in str(folder.relative_to(REPO_ROOT)):
            continue
        if not folder_pattern.match(folder.name):
            report.add_error(
                f"Invalid folder name: {folder.relative_to(REPO_ROOT)}",
                location=str(folder.relative_to(REPO_ROOT)), rule="Naming conventions",
            )

    report.add_pass("Naming conventions check")


def check_python_lib_structure(report: GovernanceReport) -> None:
    """Check Python library structure for multi-code architecture."""
    lib_root = REPO_ROOT / "Python" / "structural_lib"
    if not lib_root.exists():
        report.add_warning("Python/structural_lib/ not found — skipping lib checks", location="Python/", rule="Lib structure")
        return

    required_folders = RULES.get("python_lib", {}).get(
        "required_folders",
        ["core", "codes", "codes/is456", "services", "insights", "reports", "visualization"],
    )
    for folder in required_folders:
        path = lib_root / folder
        if path.exists() and path.is_dir():
            report.add_info(f"✅ structural_lib/{folder}/")
        else:
            report.add_error(
                f"Missing required lib folder: structural_lib/{folder}/",
                location=f"structural_lib/{folder}/", rule="Lib structure",
            )

    required_files = {
        "core/__init__.py": ["CodeRegistry", "RectangularSection", "MaterialFactory"],
        "core/base.py": ["DesignCode", "DesignResult", "FlexureDesigner"],
        "core/materials.py": ["Concrete", "Steel", "MaterialFactory"],
        "core/geometry.py": ["Section", "RectangularSection", "TSection"],
        "core/registry.py": ["CodeRegistry", "register_code"],
        "codes/__init__.py": ["is456"],
        "codes/is456/__init__.py": ["IS456Code"],
        "services/api.py": [],
        "services/__init__.py": [],
        "insights/__init__.py": [],
        "reports/__init__.py": [],
        "visualization/__init__.py": [],
    }
    for entry_file in RULES.get("python_lib", {}).get("required_entry_files", []):
        required_files.setdefault(str(entry_file), [])

    for file_path, exports in required_files.items():
        full = lib_root / file_path
        if not full.exists():
            report.add_error(f"Missing lib file: structural_lib/{file_path}", location=f"structural_lib/{file_path}", rule="Lib files")
            continue
        content = full.read_text(encoding="utf-8")
        missing = [e for e in exports if e not in content]
        if missing:
            report.add_warning(
                f"structural_lib/{file_path} missing exports: {', '.join(missing)}",
                location=f"structural_lib/{file_path}", rule="Lib exports",
            )

    # Code registration check
    try:
        sys.path.insert(0, str(REPO_ROOT / "Python"))
        from structural_lib.core import CodeRegistry
        from structural_lib.codes import is456  # noqa: F401
        if CodeRegistry.is_registered("IS456"):
            report.add_info("✅ IS456 registered in CodeRegistry")
        else:
            report.add_error("IS456 not registered in CodeRegistry", location="structural_lib/codes/", rule="Code registration")
    except ImportError as e:
        report.add_warning(f"Cannot verify code registration: {e}", location="structural_lib/", rule="Code registration")

    report.add_pass("Python lib structure")


def _is_main_guard_if(node: ast.If) -> bool:
    """Return True if node is `if __name__ == "__main__": ...`."""
    test = node.test
    if not isinstance(test, ast.Compare):
        return False
    if not isinstance(test.left, ast.Name) or test.left.id != "__name__":
        return False
    if len(test.ops) != 1 or not isinstance(test.ops[0], ast.Eq):
        return False
    if len(test.comparators) != 1:
        return False
    comp = test.comparators[0]
    return isinstance(comp, ast.Constant) and comp.value == "__main__"


def _is_warnings_warn_expr(node: ast.Expr) -> bool:
    """Return True if expression is `warnings.warn(...)`."""
    if not isinstance(node.value, ast.Call):
        return False
    func = node.value.func
    return (
        isinstance(func, ast.Attribute)
        and isinstance(func.value, ast.Name)
        and func.value.id == "warnings"
        and func.attr == "warn"
    )


def _is_allowed_stub_try(node: ast.Try) -> bool:
    """Allow import-only try/except blocks used for compatibility shims."""
    allowed_stmt_types = (ast.Import, ast.ImportFrom, ast.Pass)
    body_ok = all(isinstance(stmt, allowed_stmt_types) for stmt in node.body)
    handlers_ok = True
    for handler in node.handlers:
        if not all(isinstance(stmt, allowed_stmt_types) for stmt in handler.body):
            handlers_ok = False
            break
    orelse_ok = all(isinstance(stmt, allowed_stmt_types) for stmt in node.orelse)
    final_ok = all(isinstance(stmt, allowed_stmt_types) for stmt in node.finalbody)
    return body_ok and handlers_ok and orelse_ok and final_ok


def check_root_python_stub_only(report: GovernanceReport) -> None:
    """Ensure root structural_lib/*.py files remain compatibility stubs only."""
    lib_root = REPO_ROOT / "Python" / "structural_lib"
    if not lib_root.exists():
        return

    root_modules = sorted(
        p for p in lib_root.glob("*.py")
        if p.name not in {"__init__.py", "__main__.py"}
    )

    violations: list[str] = []
    for module_path in root_modules:
        rel = module_path.relative_to(REPO_ROOT)
        try:
            source = module_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception as exc:
            report.add_error(
                f"Cannot parse stub module {rel}: {exc}",
                location=str(rel), rule="Root stub-only modules",
            )
            continue

        has_reexport_import = False
        for idx, stmt in enumerate(tree.body):
            if (
                idx == 0
                and isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and isinstance(stmt.value.value, str)
            ):
                # Module docstring
                continue

            if isinstance(stmt, (ast.Import, ast.ImportFrom, ast.Assign, ast.AnnAssign, ast.Pass)):
                if isinstance(stmt, ast.ImportFrom):
                    mod = stmt.module or ""
                    if mod.startswith("structural_lib"):
                        has_reexport_import = True
                continue

            if isinstance(stmt, ast.Expr) and _is_warnings_warn_expr(stmt):
                continue

            if isinstance(stmt, ast.Try) and _is_allowed_stub_try(stmt):
                continue

            if isinstance(stmt, ast.If) and _is_main_guard_if(stmt):
                continue

            # Disallow executable logic drift (functions/classes/loops/custom runtime logic).
            violations.append(f"{rel}: disallowed top-level {type(stmt).__name__}")

        if not has_reexport_import:
            violations.append(f"{rel}: missing structural_lib re-export import")

    if violations:
        report.add_error(
            f"Found {len(violations)} root modules that are not stub-only",
            location="Python/structural_lib", rule="Root stub-only modules",
            files=violations[:20],
        )
    else:
        report.add_pass("Root structural_lib modules are stub-only")


def _iter_layer_files(lib_root: Path, layer: str) -> list[Path]:
    layer_dir = lib_root / layer
    if not layer_dir.exists():
        return []
    return sorted(
        p
        for p in layer_dir.rglob("*.py")
        if "__pycache__" not in p.parts
    )


def _absolute_structural_imports(py_file: Path) -> list[tuple[int, str]]:
    imports: list[tuple[int, str]] = []
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("structural_lib."):
                    imports.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module and node.module.startswith("structural_lib."):
                imports.append((node.lineno, node.module))
    return imports


def check_python_layer_boundaries(report: GovernanceReport) -> None:
    """Enforce 4-layer architecture import boundaries for structural_lib."""
    lib_root = REPO_ROOT / "Python" / "structural_lib"
    if not lib_root.exists():
        return

    layer_imports = RULES.get("python_lib", {}).get("layer_imports", {})
    exceptions = RULES.get("python_lib", {}).get("layer_import_exceptions", {})
    if not isinstance(layer_imports, dict) or not layer_imports:
        report.add_warning(
            "No layer import rules configured; skipping boundary check",
            location="Python/structural_lib",
            rule="Layer boundaries",
        )
        return

    configured_layers = set(layer_imports.keys())
    violations: list[str] = []

    for layer, allowed_list in layer_imports.items():
        allowed = set(allowed_list) if isinstance(allowed_list, list) else set()
        for py_file in _iter_layer_files(lib_root, layer):
            rel = py_file.relative_to(REPO_ROOT)
            rel_in_lib = str(rel).replace("Python/structural_lib/", "")
            file_exceptions = set(exceptions.get(rel_in_lib, []))
            for line_no, module in _absolute_structural_imports(py_file):
                parts = module.split(".")
                if len(parts) < 2:
                    continue
                target_layer = parts[1]
                if target_layer not in configured_layers:
                    violations.append(
                        f"{rel}:{line_no} imports legacy root module {module}"
                    )
                    continue
                if target_layer in file_exceptions:
                    continue
                if target_layer not in allowed:
                    violations.append(
                        f"{rel}:{line_no} imports disallowed layer {module}"
                    )

    if violations:
        report.add_error(
            f"Found {len(violations)} layer-boundary violation(s)",
            location="Python/structural_lib",
            rule="Layer boundaries",
            files=violations[:30],
        )
    else:
        report.add_pass("Python layer boundary imports")


# ═══════════════════════════════════════════════════════════════════════════
# COMPLIANCE CHECKS (from check_governance_compliance.py)
# ═══════════════════════════════════════════════════════════════════════════

def check_docs_agents_structure(report: GovernanceReport) -> None:
    """Check docs/agents/ workflow docs are in guides/ subfolder."""
    docs_agents = REPO_ROOT / "docs" / "agents"
    if not docs_agents.exists():
        return
    workflow_docs = [
        "agent-automation-implementation.md", "agent-automation-system.md",
        "agent-bootstrap-complete-review.md", "agent-onboarding.md",
        "agent-quick-reference.md", "agent-workflow-master-guide.md",
    ]
    workflow_in_root = [f for f in workflow_docs if (docs_agents / f).exists()]
    if workflow_in_root:
        report.add_error(
            f"Found {len(workflow_in_root)} workflow docs in docs/agents/ root (should be in guides/)",
            location="docs/agents/", rule="Workflow docs in guides/",
            files=workflow_in_root,
        )
    else:
        report.add_pass("docs/agents/ structure")


def check_governance_location(report: GovernanceReport) -> None:
    """Check GOVERNANCE.md exists in agents/roles/."""
    canonical_gov = REPO_ROOT / "agents" / "roles" / "GOVERNANCE.md"
    old_gov = REPO_ROOT / "agents" / "GOVERNANCE.md"
    if not canonical_gov.exists():
        report.add_error(
            "agents/roles/GOVERNANCE.md is missing",
            location="agents/roles/", rule="GOVERNANCE.md location",
        )
    else:
        report.add_pass("GOVERNANCE.md location")
    if old_gov.exists():
        report.add_warning(
            "agents/GOVERNANCE.md should be moved to agents/roles/GOVERNANCE.md",
            location="agents/", rule="GOVERNANCE.md location",
        )


def check_redirect_stubs(report: GovernanceReport) -> None:
    """Check for redirect stub files (single source rule)."""
    docs_path = REPO_ROOT / "docs"
    if not docs_path.exists():
        return
    skip_dirs = {"_archive", "node_modules", "__pycache__", ".venv"}
    violations = 0

    for md_file in docs_path.rglob("*.md"):
        if any(skip_dir in md_file.parts for skip_dir in skip_dirs):
            continue
        if md_file.name in ["README.md", "TASKS.md", "SESSION_LOG.md"]:
            continue
        try:
            content = md_file.read_text()
        except Exception:
            continue
        lines = content.strip().split("\n")
        links = content.count("](")
        words = len(content.split())
        is_redirect_marker = "redirect" in content.lower() or "moved to" in content.lower()
        is_small_with_links = len(lines) < 15 and links > 0 and words < 50
        if is_small_with_links or (is_redirect_marker and len(lines) < 20):
            rel_path = str(md_file.relative_to(REPO_ROOT))
            report.add_warning(
                f"Likely redirect stub: {len(lines)} lines, {links} links, {words} words",
                location=rel_path, rule="No redirect stubs",
            )
            violations += 1

    if violations == 0:
        report.add_pass("No redirect stubs")


# ═══════════════════════════════════════════════════════════════════════════
# CLI & OUTPUT
# ═══════════════════════════════════════════════════════════════════════════

def run_structure(report: GovernanceReport, lib_only: bool = False) -> None:
    """Run all structure checks."""
    if not lib_only:
        check_root_files(report)
        check_docs_root(report)
        check_agents_root(report)
        check_category_folders(report)
        check_dated_files(report)
        check_naming_conventions(report)
    check_python_lib_structure(report)
    check_root_python_stub_only(report)
    check_python_layer_boundaries(report)


def run_compliance(report: GovernanceReport) -> None:
    """Run all compliance checks."""
    check_docs_agents_structure(report)
    check_governance_location(report)
    check_redirect_stubs(report)


def print_report(report: GovernanceReport) -> None:
    """Print human-readable governance report."""
    print()
    print("=" * 60)
    print("📋 Governance Report")
    print("=" * 60)

    if report.errors:
        print(f"\n❌ {len(report.errors)} ERROR(S):")
        for issue in report.errors:
            loc = f" [{issue.location}]" if issue.location else ""
            print(f"  • {issue.message}{loc}")

    if report.warnings:
        print(f"\n⚠️  {len(report.warnings)} WARNING(S):")
        for issue in report.warnings:
            loc = f" [{issue.location}]" if issue.location else ""
            print(f"  • {issue.message}{loc}")

    if report.info:
        print(f"\nℹ️  {len(report.info)} INFO:")
        for msg in report.info:
            print(f"  • {msg}")

    if report.passed:
        print(f"\n✅ PASSED ({len(report.passed)}):")
        for check in report.passed:
            print(f"  ✓ {check}")

    print()
    if report.success:
        if report.warnings:
            print("✅ No errors (warnings only)")
        else:
            print("✅ All governance checks passed!")
    else:
        print(f"❌ {len(report.errors)} error(s) found")
    print()


def print_json_report(report: GovernanceReport) -> None:
    """Print JSON governance report."""
    output = {
        "status": "PASS" if report.success else "FAIL",
        "errors": [{"severity": i.severity, "location": i.location, "rule": i.rule, "message": i.message, "files": i.files} for i in report.errors],
        "warnings": [{"severity": i.severity, "location": i.location, "rule": i.rule, "message": i.message, "files": i.files} for i in report.warnings],
        "info": report.info,
        "passed_checks": report.passed,
    }
    print(json.dumps(output, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Unified governance checker (structure + compliance)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/check_governance.py                    # All checks\n"
            "  python scripts/check_governance.py --structure        # Folder structure\n"
            "  python scripts/check_governance.py --compliance       # Compliance rules\n"
            "  python scripts/check_governance.py --lib-only         # Python lib only\n"
            "  python scripts/check_governance.py --json             # JSON output\n"
        ),
    )

    group = parser.add_argument_group("Check selectors (default: --full)")
    group.add_argument("--structure", action="store_true", help="Validate folder structure")
    group.add_argument("--compliance", action="store_true", help="Check governance compliance")
    group.add_argument("--full", action="store_true", help="Run all checks (default)")

    parser.add_argument("--lib-only", action="store_true", help="Python lib structure only")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings too")

    args = parser.parse_args()
    run_all = args.full or not any([args.structure, args.compliance])

    report = GovernanceReport()
    global RULES
    RULES = load_governance_rules(report)

    if run_all or args.structure:
        run_structure(report, lib_only=args.lib_only)

    if (run_all or args.compliance) and not args.lib_only:
        run_compliance(report)

    if args.json:
        print_json_report(report)
    else:
        print_report(report)

    if args.strict and report.warnings:
        return 1
    return 0 if report.success else 1


if __name__ == "__main__":
    sys.exit(main())
