#!/usr/bin/env python3
"""Batch migration runner for folder structure Phase 1 & Phase 2.

Moves multiple Python modules at once, updates all imports in a single pass,
and creates backward-compat stubs. Much more efficient than running
migrate_python_module.py one file at a time.

Usage:
    python scripts/batch_migrate_modules.py --phase 1 --dry-run
    python scripts/batch_migrate_modules.py --phase 1
    python scripts/batch_migrate_modules.py --phase 2 --dry-run
    python scripts/batch_migrate_modules.py --phase 2
    python scripts/batch_migrate_modules.py --phase all
"""

from __future__ import annotations

import argparse
import ast
import re
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
LIB_ROOT = PROJECT_ROOT / "Python" / "structural_lib"

# Directories to scan for imports
SEARCH_DIRS = [
    "Python/structural_lib",
    "Python/tests",
    "fastapi_app",
    "scripts",
    "streamlit_app",
    "tests",
]

SKIP_PATTERNS = {
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "node_modules", ".venv", ".git",
}

# ─── Phase Definitions ──────────────────────────────────────────

PHASE_1_MOVES = {
    # source (relative to structural_lib/) -> destination subpackage
    "constants.py": "core/constants.py",
    "types.py": "core/types.py",
    "data_types.py": "core/data_types.py",
    "models.py": "core/models.py",
    "errors.py": "core/errors.py",
    "error_messages.py": "core/error_messages.py",
    "validation.py": "core/validation.py",
    "inputs.py": "core/inputs.py",
    "result_base.py": "core/result_base.py",
    "utilities.py": "core/utilities.py",
}

PHASE_2_MOVES = {
    "api.py": "services/api.py",
    "api_results.py": "services/api_results.py",
    "beam_pipeline.py": "services/beam_pipeline.py",
    "adapters.py": "services/adapters.py",
    "batch.py": "services/batch.py",
    "imports.py": "services/imports.py",
    "etabs_import.py": "services/etabs_import.py",
    "rebar.py": "services/rebar.py",
    "rebar_optimizer.py": "services/rebar_optimizer.py",
    "optimization.py": "services/optimization.py",
    "multi_objective_optimizer.py": "services/multi_objective_optimizer.py",
    "audit.py": "services/audit.py",
    "intelligence.py": "services/intelligence.py",
    "costing.py": "services/costing.py",
    "serialization.py": "services/serialization.py",
    "dashboard.py": "services/dashboard.py",
    "testing_strategies.py": "services/testing_strategies.py",
}


def find_python_files() -> list[Path]:
    """Find all Python files in the project."""
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


def build_module_map(moves: dict[str, str]) -> dict[str, str]:
    """Build old_module -> new_module mapping."""
    mapping = {}
    for src, dst in moves.items():
        old_mod = "structural_lib." + src.replace(".py", "")
        new_mod = "structural_lib." + dst.replace("/", ".").replace(".py", "")
        mapping[old_mod] = new_mod
    return mapping


def update_all_imports(
    module_map: dict[str, str],
    files: list[Path],
    dry_run: bool = False,
) -> int:
    """Update all imports across all files in a single pass."""
    updated_count = 0

    # Sort by longest module name first to avoid partial matches
    sorted_modules = sorted(module_map.keys(), key=len, reverse=True)

    for py_file in files:
        try:
            content = py_file.read_text(encoding="utf-8")
            original = content
        except (OSError, UnicodeDecodeError):
            continue

        for old_module in sorted_modules:
            new_module = module_map[old_module]

            # from structural_lib.core.types import X -> from structural_lib.core.types import X
            content = re.sub(
                rf"(from\s+){re.escape(old_module)}(\s+import)",
                rf"\g<1>{new_module}\g<2>",
                content,
            )

            # import structural_lib.core.types -> import structural_lib.core.types
            content = re.sub(
                rf"(import\s+){re.escape(old_module)}\b",
                rf"\g<1>{new_module}",
                content,
            )

        if content != original:
            if dry_run:
                rel = py_file.relative_to(PROJECT_ROOT)
                # Count changes
                changes = sum(
                    1 for old_mod in sorted_modules
                    if old_mod in original and module_map[old_mod] in content
                )
                print(f"  Would update: {rel}")
            else:
                py_file.write_text(content, encoding="utf-8")
                rel = py_file.relative_to(PROJECT_ROOT)
                print(f"  Updated: {rel}")
            updated_count += 1

    return updated_count


def move_files(
    moves: dict[str, str],
    dry_run: bool = False,
) -> int:
    """Move all files to their new locations."""
    moved = 0
    for src, dst in moves.items():
        src_path = LIB_ROOT / src
        dst_path = LIB_ROOT / dst

        if not src_path.exists():
            print(f"  ⚠️  Skip (not found): {src}")
            continue

        if dst_path.exists():
            print(f"  ⚠️  Skip (exists): {dst}")
            continue

        if dry_run:
            print(f"  Would move: {src} → {dst}")
        else:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            # Ensure __init__.py exists
            init_file = dst_path.parent / "__init__.py"
            if not init_file.exists():
                pkg_name = dst_path.parent.name
                init_file.write_text(
                    f'"""structural_lib.{pkg_name} — Auto-generated package."""\n',
                    encoding="utf-8",
                )
                print(f"  Created: {init_file.relative_to(PROJECT_ROOT)}")

            shutil.move(str(src_path), str(dst_path))
            print(f"  Moved: {src} → {dst}")
        moved += 1

    return moved


def create_stubs(
    moves: dict[str, str],
    module_map: dict[str, str],
    dry_run: bool = False,
) -> int:
    """Create backward-compat stubs at old locations."""
    created = 0
    for src, dst in moves.items():
        src_path = LIB_ROOT / src
        old_module = "structural_lib." + src.replace(".py", "")
        new_module = module_map[old_module]
        dst_path = LIB_ROOT / dst

        if dry_run:
            print(f"  Would create stub: {src}")
            created += 1
            continue

        if src_path.exists():
            # File wasn't moved (maybe dst existed)
            continue

        # Extract public names from the moved file
        public_names = _extract_public_names(dst_path)

        stub_lines = [
            '"""Backward compatibility stub.',
            "",
            f"This module has been migrated to: {new_module}",
            "All functionality is re-exported here for backward compatibility.",
            f'Prefer importing directly from {new_module}."""',
            "",
            "from __future__ import annotations",
            "",
        ]

        if public_names:
            stub_lines.append(f"from {new_module} import (  # noqa: F401, E402")
            for name in sorted(set(public_names)):
                stub_lines.append(f"    {name},")
            stub_lines.append(")")
        else:
            stub_lines.append(
                f"from {new_module} import *  # noqa: F401, F403, E402"
            )

        stub_lines.append("")
        src_path.write_text("\n".join(stub_lines), encoding="utf-8")
        print(f"  Created stub: {src}")
        created += 1

    return created


def _extract_public_names(file_path: Path) -> list[str]:
    """Extract public names from a Python file using AST."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
    except (OSError, SyntaxError):
        return []

    names = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                names.append(node.name)
        elif isinstance(node, ast.ClassDef):
            if not node.name.startswith("_"):
                names.append(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    names.append(target.id)

    # Also check for __all__
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        return [
                            elt.value
                            for elt in node.value.elts
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                        ]

    return names


def validate_syntax(files: list[Path]) -> list[str]:
    """Quick syntax check on all Python files."""
    errors = []
    for py_file in files:
        try:
            content = py_file.read_text(encoding="utf-8")
            compile(content, str(py_file), "exec")
        except SyntaxError as e:
            errors.append(f"  {py_file.relative_to(PROJECT_ROOT)}: {e}")
        except (OSError, UnicodeDecodeError):
            pass
    return errors


def main():
    parser = argparse.ArgumentParser(description="Batch migrate Python modules")
    parser.add_argument(
        "--phase",
        choices=["1", "2", "all"],
        required=True,
        help="Which phase to execute",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes",
    )
    parser.add_argument(
        "--no-stubs",
        action="store_true",
        help="Don't create backward-compat stubs",
    )
    args = parser.parse_args()

    # Determine which moves to execute
    moves: dict[str, str] = {}
    if args.phase in ("1", "all"):
        moves.update(PHASE_1_MOVES)
    if args.phase in ("2", "all"):
        moves.update(PHASE_2_MOVES)

    module_map = build_module_map(moves)

    print("=" * 60)
    print(f"🐍 Batch Module Migration — Phase {args.phase}")
    print("=" * 60)
    print(f"Files to migrate: {len(moves)}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    # Step 1: Move files
    print("📦 Step 1: Moving files...")
    moved = move_files(moves, args.dry_run)
    print(f"   Moved {moved} files")
    print()

    # Step 2: Update imports
    print("🔗 Step 2: Updating imports across entire project...")
    all_files = find_python_files()
    updated = update_all_imports(module_map, all_files, args.dry_run)
    print(f"   Updated {updated} files")
    print()

    # Step 3: Create stubs
    if not args.no_stubs:
        print("📝 Step 3: Creating backward-compat stubs...")
        stubs = create_stubs(moves, module_map, args.dry_run)
        print(f"   Created {stubs} stubs")
    else:
        print("📝 Step 3: Skipped (--no-stubs)")
    print()

    # Step 4: Validate
    if not args.dry_run:
        print("✅ Step 4: Validating syntax...")
        errors = validate_syntax(all_files)
        if errors:
            print(f"   ⚠️  {len(errors)} syntax error(s):")
            for err in errors[:10]:
                print(f"     {err}")
        else:
            print("   All files compile successfully!")
    print()

    # Summary
    print("=" * 60)
    if args.dry_run:
        print("✨ Dry run complete. No changes made.")
        print()
        print(f"To apply: .venv/bin/python scripts/batch_migrate_modules.py --phase {args.phase}")
    else:
        print(f"✨ Phase {args.phase} migration complete!")
        print()
        print("Next steps:")
        print("  1. Run: cd Python && ../.venv/bin/pytest tests/ -v")
        print("  2. Run: .venv/bin/python scripts/validate_imports.py --scope structural_lib")
        print("  3. Commit: ./scripts/ai_commit.sh 'refactor: phase X migration'")
    print("=" * 60)


if __name__ == "__main__":
    main()
