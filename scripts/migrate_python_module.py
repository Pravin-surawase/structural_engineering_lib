#!/usr/bin/env python3
"""Migrate a Python module to a new location with import updates.

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
    --force       Overwrite destination if exists
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
STRUCTURAL_LIB = PROJECT_ROOT / "Python" / "structural_lib"

# Directories to search for imports
SEARCH_DIRS = [
    "Python/structural_lib",
    "Python/tests",
    "fastapi_app",
    "scripts",
    "streamlit_app",
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
        names_str = ", ".join(sorted(set(public_names)))
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
    """Execute migration and return (exit_code, structured_result)."""
    result: dict[str, object] = {
        "tool": "migrate_python_module",
        "dry_run": bool(args.dry_run),
        "mode": "dry-run" if args.dry_run else "live",
        "success": False,
        "source": args.source,
        "destination": args.destination,
    }

    # Resolve paths
    source = Path(args.source)
    if not source.is_absolute():
        # Try relative to Python/ first, then project root
        if (PROJECT_ROOT / "Python" / source).exists():
            source = PROJECT_ROOT / "Python" / source
        elif (PROJECT_ROOT / source).exists():
            source = PROJECT_ROOT / source
        else:
            source = PROJECT_ROOT / "Python" / source
    source = source.resolve()

    destination = Path(args.destination)
    if not destination.is_absolute():
        if args.destination.startswith("structural_lib"):
            destination = PROJECT_ROOT / "Python" / destination
        else:
            destination = PROJECT_ROOT / "Python" / destination
    destination = destination.resolve()

    # Validate
    if not source.exists():
        print(f"❌ Source not found: {source}")
        result["error"] = f"Source not found: {source}"
        return 1, result

    if destination.exists() and not args.force:
        print(f"❌ Destination exists: {destination}")
        print("   Use --force to overwrite")
        result["error"] = f"Destination exists: {destination}"
        return 1, result

    # Calculate module paths
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

    # Step 1: Find all import references
    print("🔍 Step 1: Finding import references...")
    all_files = find_python_files()
    references = find_import_references(old_module, all_files)
    print(f"   Found {len(references)} reference(s) in {len(set(r[0] for r in references))} files")
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

    # Step 2: Move file
    print("📦 Step 2: Moving module...")
    created_init: str | None = None
    if args.dry_run:
        print(f"   Would move: {source.name} → {destination}")
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Ensure __init__.py exists in new directory
        init_file = destination.parent / "__init__.py"
        if not init_file.exists():
            init_file.write_text(
                '"""Auto-generated __init__.py for package."""\n',
                encoding="utf-8",
            )
            created_init = str(init_file.relative_to(PROJECT_ROOT))
            print(f"   Created: {created_init}")

        source.rename(destination)
        print(f"   Moved: {source.name} → {destination.relative_to(PROJECT_ROOT)}")
    result["moved"] = not args.dry_run
    result["created_init"] = created_init
    print()

    # Step 3: Update imports
    print("🔗 Step 3: Updating imports...")
    updated, updated_files = update_imports(old_module, new_module, all_files, args.dry_run)
    print(f"   Updated {updated} file(s)")
    result["updated_count"] = updated
    result["updated_files"] = updated_files
    print()

    # Step 4: Create backward-compat stub
    stub_file: str | None = None
    if not args.no_stub:
        print("📝 Step 4: Creating backward-compat stub...")
        if args.dry_run:
            print(f"   Would create stub at: {source.relative_to(PROJECT_ROOT)}")
            stub_file = str(source.relative_to(PROJECT_ROOT))
        else:
            stub_file = create_backward_compat_stub(source, old_module, new_module)
    else:
        print("📝 Step 4: Skipped (--no-stub)")
    print()
    result["stub_created"] = not args.no_stub
    result["stub_file"] = stub_file

    # Step 5: Validate
    print("✅ Step 5: Validating...")
    validation_errors: list[str] = []
    if args.dry_run:
        print("   Skipped (dry run)")
    else:
        validation_errors = validate_imports(all_files)
        if validation_errors:
            print("   ⚠️  Syntax errors found:")
            for error in validation_errors:
                print(f"     {error}")
        else:
            print("   All files compile successfully!")
    result["validation"] = {
        "checked": not args.dry_run,
        "errors": validation_errors,
        "ok": len(validation_errors) == 0,
    }
    print()

    # Summary
    print("=" * 60)
    if args.dry_run:
        print("✨ Dry run complete. No changes made.")
        print()
        print("To apply:")
        cmd = f"  .venv/bin/python scripts/migrate_python_module.py {args.source} {args.destination}"
        print(cmd)
    else:
        print("✨ Migration complete!")
        print()
        print("Next steps:")
        print("  1. Run tests: cd Python && .venv/bin/pytest tests/ -v")
        print("  2. Run FastAPI tests: .venv/bin/pytest fastapi_app/tests/ -v")
        print("  3. Commit: ./scripts/ai_commit.sh 'refactor: move module'")
    print("=" * 60)
    changed_files = set(updated_files)
    changed_files.update({
        str(source.relative_to(PROJECT_ROOT)),
        str(destination.relative_to(PROJECT_ROOT)),
    })
    if created_init:
        changed_files.add(created_init)
    if stub_file:
        changed_files.add(stub_file)
    result["changed_files"] = sorted(changed_files)
    success = args.dry_run or len(validation_errors) == 0
    result["success"] = success
    return (0 if success else 1), result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate Python module with import updates"
    )
    parser.add_argument("source", help="Source module path (e.g., structural_lib/api.py)")
    parser.add_argument(
        "destination",
        help="Destination module path (e.g., structural_lib/services/api.py)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would happen"
    )
    parser.add_argument(
        "--no-stub", action="store_true", help="Don't create backward-compat stub"
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite destination if exists"
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
