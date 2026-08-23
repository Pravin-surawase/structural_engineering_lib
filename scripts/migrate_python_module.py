#!/usr/bin/env python3
"""Migrate a Python module to a new location with import updates.

When to use: When moving a Python module to a new path. Updates all imports automatically.

Safely moves a .py file within structural_lib/ and updates ALL import
statements across the entire project (Python, tests, FastAPI, scripts).

Features:
1. Moves .py file to new location
2. Updates all Python imports (from X import Y, import X)
3. Creates backward-compat re-export stub at old location
4. Updates __init__.py files
5. Validates no broken imports after move

Usage:
    python scripts/migrate_python_module.py structural_lib/api.py structural_lib/services/api.py --dry-run
    python scripts/migrate_python_module.py structural_lib/types.py structural_lib/core/types.py

Options:
    --dry-run     Show what would change without making changes
    --no-stub     Don't create backward-compat stub
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.safe_file_ops import (
    SafeFileError,
    capture_snapshots,
    resolve_new_destination,
    resolve_regular_source,
    restore_snapshots,
)

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
STRUCTURAL_LIB = PROJECT_ROOT / "Python" / "structural_lib"

# Directories to search for imports
SEARCH_DIRS = [
    "Python/structural_lib",
    "Python/tests",
    "fastapi_app",
    "scripts",
    "tests",
]

# Patterns to skip
SKIP_PATTERNS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    ".venv",
    ".git",
}


def _resolve_source_path(path_str: str) -> Path:
    """Resolve source path with support for both Python/ and structural_lib/ forms."""
    raw = Path(path_str)
    if raw.is_absolute():
        return raw.resolve()

    candidates: list[Path] = []
    candidates.append(PROJECT_ROOT / raw)

    if raw.parts and raw.parts[0] == "Python":
        candidates.append(PROJECT_ROOT / Path(*raw.parts[1:]))
    else:
        candidates.append(PROJECT_ROOT / "Python" / raw)

    for candidate in candidates:
        if candidate.exists():
            return candidate.absolute()

    # Fall back to canonical Python/ path for consistent error messaging.
    if raw.parts and raw.parts[0] == "Python":
        return (PROJECT_ROOT / raw).absolute()
    return (PROJECT_ROOT / "Python" / raw).absolute()


def _resolve_destination_path(path_str: str) -> Path:
    """Resolve destination path without duplicating Python/ prefix."""
    raw = Path(path_str)
    if raw.is_absolute():
        return raw.absolute()
    if raw.parts and raw.parts[0] == "Python":
        return (PROJECT_ROOT / raw).absolute()
    if raw.parts and raw.parts[0] == "structural_lib":
        return (PROJECT_ROOT / "Python" / raw).absolute()
    return (PROJECT_ROOT / "Python" / raw).absolute()


def path_to_module(file_path: Path) -> str:
    """Convert file path to Python module path.

    Python/structural_lib/api.py -> structural_lib.api
    Python/structural_lib/codes/is456/flexure.py -> structural_lib.codes.is456.flexure
    """
    try:
        rel = file_path.relative_to(PROJECT_ROOT / "Python")
    except ValueError:
        rel = file_path
    module = str(rel).replace("/", ".").replace("\\", ".")
    if module.endswith(".py"):
        module = module[:-3]
    if module.endswith(".__init__"):
        module = module[:-9]
    return module


def find_python_files() -> list[Path]:
    """Find all Python files in the project that might have imports."""
    files = []
    for search_dir in SEARCH_DIRS:
        search_path = PROJECT_ROOT / search_dir
        if not search_path.exists():
            continue
        for py_file in search_path.rglob("*.py"):
            if any(skip in py_file.parts for skip in SKIP_PATTERNS):
                continue
            files.append(py_file)
    return sorted(files)


def find_import_references(
    old_module: str, files: list[Path]
) -> list[tuple[Path, int, str, str]]:
    """Find all files that import from the old module.

    Returns list of (file, line_number, old_line, import_type) tuples.
    import_type is one of: 'from_import', 'import', 'string_ref'
    """
    references = []

    # Patterns to match
    # from structural_lib.services.api import X
    from_pattern = re.compile(
        rf"^(\s*)(from\s+{re.escape(old_module)}\s+import\s+.+)$", re.MULTILINE
    )
    # import structural_lib.services.api
    import_pattern = re.compile(
        rf"^(\s*)(import\s+{re.escape(old_module)}\b.*)$", re.MULTILINE
    )
    # String references like "structural_lib.api"
    string_pattern = re.compile(rf'["\']({re.escape(old_module)})["\']')

    for py_file in files:
        try:
            content = py_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        for i, line in enumerate(content.split("\n"), 1):
            stripped = line.strip()

            # Skip comments
            if stripped.startswith("#"):
                continue

            # Check from ... import
            if from_pattern.search(line):
                references.append((py_file, i, line, "from_import"))
            elif import_pattern.search(line):
                references.append((py_file, i, line, "import"))
            elif string_pattern.search(line):
                references.append((py_file, i, line, "string_ref"))

    return references


def update_imports(
    old_module: str,
    new_module: str,
    files: list[Path],
    dry_run: bool = False,
) -> tuple[int, list[str]]:
    """Update all imports from old_module to new_module.

    Returns number of files updated.
    """
    updated_count = 0
    updated_files: list[str] = []

    for py_file in files:
        try:
            content = py_file.read_text(encoding="utf-8")
            original = content
        except (OSError, UnicodeDecodeError):
            continue

        # Replace import patterns
        # from structural_lib.services.api import X -> from structural_lib.services.api import X
        content = re.sub(
            rf"(from\s+){re.escape(old_module)}(\s+import)",
            rf"\g<1>{new_module}\g<2>",
            content,
        )

        # import structural_lib.services.api -> import structural_lib.services.api
        content = re.sub(
            rf"(import\s+){re.escape(old_module)}\b",
            rf"\g<1>{new_module}",
            content,
        )

        # "structural_lib.old_module" -> "structural_lib.new_module"
        # Keep quoted module-path string references in sync with import rewrites.
        content = re.sub(
            rf"([\"']){re.escape(old_module)}([\"'])",
            rf"\g<1>{new_module}\g<2>",
            content,
        )

        if content != original:
            if dry_run:
                rel = py_file.relative_to(PROJECT_ROOT)
                print(f"  Would update: {rel}")
            else:
                py_file.write_text(content, encoding="utf-8")
                rel = py_file.relative_to(PROJECT_ROOT)
                print(f"  Updated: {rel}")
            updated_count += 1
            updated_files.append(str(rel))

    return updated_count, updated_files


def create_backward_compat_stub(
    old_path: Path, old_module: str, new_module: str
) -> str:
    """Create backward-compat stub at old location that re-exports from new location."""
    # Get all public names from the module
    new_path = STRUCTURAL_LIB.parent / new_module.replace(".", "/")
    if not new_path.suffix:
        new_path = new_path.with_suffix(".py")

    # Read the new file to get its exports
    public_names = []
    try:
        content = new_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    public_names.append(node.name)
            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith("_"):
                    public_names.append(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and not target.id.startswith("_"):
                        public_names.append(target.id)
    except Exception:
        # Fallback: use wildcard import
        public_names = []

    # Generate stub content
    stub_lines = [
        '"""Backward compatibility stub.',
        "",
        f"This module has been migrated to: {new_module}",
        "",
        "All functionality is re-exported here for backward compatibility.",
        'Prefer importing directly from the new location."""',
        "",
        "from __future__ import annotations",
        "",
        "import warnings",
        "",
        "warnings.warn(",
        f'    "Importing from {old_module} is deprecated. "',
        f'    "Use {new_module} instead.",',
        "    DeprecationWarning,",
        "    stacklevel=2,",
        ")",
        "",
    ]

    if public_names:
        # Explicit re-exports
        stub_lines.append(f"from {new_module} import (  # noqa: F401, E402")
        for name in sorted(set(public_names)):
            stub_lines.append(f"    {name},")
        stub_lines.append(")")
    else:
        # Wildcard import
        stub_lines.append(f"from {new_module} import *  # noqa: F401, F403, E402")

    stub_lines.append("")

    old_path.write_text("\n".join(stub_lines), encoding="utf-8")
    rel = str(old_path.relative_to(PROJECT_ROOT))
    print(f"  Created backward-compat stub: {rel}")
    return rel


def validate_imports(files: list[Path]) -> list[str]:
    """Quick syntax check - try to compile all affected files."""
    errors = []
    for py_file in files:
        try:
            content = py_file.read_text(encoding="utf-8")
            compile(content, str(py_file), "exec")
        except SyntaxError as e:
            errors.append(f"  Syntax error in {py_file}: {e}")
    return errors


def run_migration(args: argparse.Namespace) -> tuple[int, dict[str, object]]:
    """Execute a previewable, byte-restorable Python module migration."""
    result: dict[str, object] = {
        "tool": "migrate_python_module",
        "dry_run": bool(args.dry_run),
        "mode": "dry-run" if args.dry_run else "live",
        "success": False,
        "source": args.source,
        "destination": args.destination,
        "moved": False,
        "rolled_back": False,
    }

    try:
        source = resolve_regular_source(_resolve_source_path(args.source), PROJECT_ROOT)
        destination = resolve_new_destination(
            _resolve_destination_path(args.destination), PROJECT_ROOT, source
        )
    except SafeFileError as exc:
        result["error"] = str(exc)
        print(f"❌ {exc}")
        return 1, result

    old_module = path_to_module(source)
    new_module = path_to_module(destination)
    result["source"] = str(source.relative_to(PROJECT_ROOT))
    result["destination"] = str(destination.relative_to(PROJECT_ROOT))
    result["old_module"] = old_module
    result["new_module"] = new_module

    print("=" * 60)
    print("🐍 Python Module Migration")
    print("=" * 60)
    print(f"Source:      {source.relative_to(PROJECT_ROOT)}")
    print(f"Destination: {destination.relative_to(PROJECT_ROOT)}")
    print(f"Old module:  {old_module}")
    print(f"New module:  {new_module}")
    print(f"Mode:        {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    print("🔍 Step 1: Finding import references...")
    all_files = find_python_files()
    references = find_import_references(old_module, all_files)
    reference_files = sorted({reference[0] for reference in references})
    print(f"   Found {len(references)} reference(s) in {len(reference_files)} files")
    result["references_count"] = len(references)
    result["references"] = [
        {
            "file": str(ref_file.relative_to(PROJECT_ROOT)),
            "line": line_num,
            "type": imp_type,
        }
        for ref_file, line_num, _line, imp_type in references
    ]

    if references:
        for ref_file, line_num, line, imp_type in references[:10]:
            rel = ref_file.relative_to(PROJECT_ROOT)
            print(f"     {rel}:{line_num} [{imp_type}]")
        if len(references) > 10:
            print(f"     ... and {len(references) - 10} more")
    print()

    baseline_errors = validate_imports([source, *reference_files])
    if baseline_errors:
        result["error"] = "Affected Python files do not have a valid baseline"
        result["validation"] = {
            "checked": True,
            "errors": baseline_errors,
            "ok": False,
        }
        print("❌ Affected Python files do not compile before mutation.")
        return 1, result

    init_file = destination.parent / "__init__.py"
    init_will_create = not init_file.exists()
    created_init = (
        str(init_file.relative_to(PROJECT_ROOT)) if init_will_create else None
    )
    stub_file = str(source.relative_to(PROJECT_ROOT)) if not args.no_stub else None
    expected_updated_files = [
        str(file.relative_to(PROJECT_ROOT)) for file in reference_files
    ]
    changed_files = set(expected_updated_files)
    changed_files.update(
        {
            str(source.relative_to(PROJECT_ROOT)),
            str(destination.relative_to(PROJECT_ROOT)),
        }
    )
    if created_init:
        changed_files.add(created_init)
    if stub_file:
        changed_files.add(stub_file)
    result["changed_files"] = sorted(changed_files)
    result["created_init"] = created_init
    result["stub_created"] = not args.no_stub
    result["stub_file"] = stub_file
    result["updated_count"] = len(reference_files)
    result["updated_files"] = expected_updated_files

    if args.dry_run:
        print(f"📦 Would move: {source.name} → {destination}")
        if created_init:
            print(f"   Would create: {created_init}")
        if stub_file:
            print(f"   Would create compatibility stub: {stub_file}")
        result["validation"] = {"checked": True, "errors": [], "ok": True}
        result["success"] = True
        print("✨ Dry run complete. No changes made.")
        return 0, result

    snapshot_paths = {PROJECT_ROOT / path for path in result["changed_files"]}
    snapshots = capture_snapshots(snapshot_paths, PROJECT_ROOT)
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if init_will_create:
            init_file.write_text(
                '"""Auto-generated __init__.py for package."""\n',
                encoding="utf-8",
            )
        source.rename(destination)
        result["moved"] = True
        updated, updated_files = update_imports(
            old_module, new_module, all_files, dry_run=False
        )
        if sorted(updated_files) != sorted(expected_updated_files):
            raise SafeFileError("Live import updates differed from the preview")
        if not args.no_stub:
            create_backward_compat_stub(source, old_module, new_module)
        validation_files = [
            destination,
            *reference_files,
            *([init_file] if init_will_create else []),
            *([source] if not args.no_stub else []),
        ]
        validation_errors = validate_imports(validation_files)
        if validation_errors:
            raise SafeFileError("; ".join(validation_errors))
        result["updated_count"] = updated
        result["validation"] = {"checked": True, "errors": [], "ok": True}
    except Exception as exc:
        try:
            restore_snapshots(snapshots, PROJECT_ROOT)
            result["rolled_back"] = True
            result["moved"] = False
        except Exception as rollback_exc:
            result["rollback_error"] = str(rollback_exc)
        result["error"] = str(exc)
        result["validation"] = {
            "checked": True,
            "errors": [str(exc)],
            "ok": False,
        }
        print(f"❌ Migration failed: {exc}")
        return 1, result

    result["success"] = True
    print("✨ Migration complete and validated.")
    return 0, result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate Python module with import updates"
    )
    parser.add_argument(
        "source", help="Source module path (e.g., structural_lib/api.py)"
    )
    parser.add_argument(
        "destination",
        help="Destination module path (e.g., structural_lib/services/api.py)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen")
    parser.add_argument(
        "--no-stub", action="store_true", help="Don't create backward-compat stub"
    )
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    args = parser.parse_args()

    if args.json:
        with contextlib.redirect_stdout(sys.stderr):
            exit_code, payload = run_migration(args)
        print(json.dumps(payload, indent=2))
        return exit_code

    exit_code, _payload = run_migration(args)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
