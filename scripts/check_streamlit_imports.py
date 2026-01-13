#!/usr/bin/env python3
"""
Streamlit Import Validation Script
===================================

Validates that all Streamlit pages can be imported without errors.
Catches common runtime issues before deployment:
- ModuleNotFoundError (missing dependencies)
- ImportError (broken imports)
- SyntaxError (invalid Python)
- NameError (undefined variables at import time)
- TypeError (signature mismatches in top-level code)

Usage:
    python scripts/check_streamlit_imports.py [--verbose] [--fix-suggestions]

Exit Codes:
    0 - All imports successful
    1 - Import errors detected

Author: AI Agent (Session 19P15)
Created: 2026-01-15
"""

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import NamedTuple


class ImportResult(NamedTuple):
    """Result of attempting to import a module."""
    file_path: Path
    success: bool
    error_type: str | None
    error_message: str | None


# Files that use relative imports and can only be tested via running Streamlit app
# These are expected false positives for standalone import testing
KNOWN_RELATIVE_IMPORT_FILES = {
    "global_styles.py",      # Uses: from .styled_components import ...
    "plotly_theme.py",       # Uses: from .styled_components import ...
    "styled_components.py",  # Uses: from .global_styles import ...
    "design_system_demo.py", # Uses: import design_system (package-level)
}


def validate_import(file_path: Path) -> ImportResult:
    """
    Attempt to import a Python file and capture any errors.

    Args:
        file_path: Path to the Python file to import

    Returns:
        ImportResult with success status and any error details
    """
    try:
        spec = importlib.util.spec_from_file_location(
            f"_test_import_{file_path.stem}",
            file_path
        )
        if spec is None or spec.loader is None:
            return ImportResult(
                file_path=file_path,
                success=False,
                error_type="SpecError",
                error_message="Could not create module spec"
            )

        module = importlib.util.module_from_spec(spec)
        # Don't add to sys.modules to avoid side effects
        spec.loader.exec_module(module)

        return ImportResult(
            file_path=file_path,
            success=True,
            error_type=None,
            error_message=None
        )

    except ModuleNotFoundError as e:
        return ImportResult(
            file_path=file_path,
            success=False,
            error_type="ModuleNotFoundError",
            error_message=str(e)
        )
    except ImportError as e:
        return ImportResult(
            file_path=file_path,
            success=False,
            error_type="ImportError",
            error_message=str(e)
        )
    except SyntaxError as e:
        return ImportResult(
            file_path=file_path,
            success=False,
            error_type="SyntaxError",
            error_message=f"Line {e.lineno}: {e.msg}"
        )
    except TypeError as e:
        return ImportResult(
            file_path=file_path,
            success=False,
            error_type="TypeError",
            error_message=str(e)
        )
    except NameError as e:
        return ImportResult(
            file_path=file_path,
            success=False,
            error_type="NameError",
            error_message=str(e)
        )
    except Exception as e:
        return ImportResult(
            file_path=file_path,
            success=False,
            error_type=type(e).__name__,
            error_message=str(e)
        )


def get_fix_suggestion(result: ImportResult) -> str | None:
    """
    Provide fix suggestions for common errors.

    Args:
        result: ImportResult with error details

    Returns:
        Suggestion string or None
    """
    if result.success:
        return None

    msg = result.error_message or ""

    if result.error_type == "ModuleNotFoundError":
        if "reportlab" in msg:
            return "Install with: pip install reportlab\nOr: pip install structural-lib-is456[pdf]"
        if "ezdxf" in msg:
            return "Install with: pip install ezdxf\nOr: pip install structural-lib-is456[dxf]"
        if "streamlit" in msg:
            return "Install with: pip install streamlit"
        if "plotly" in msg:
            return "Install with: pip install plotly"
        # Generic suggestion
        module = msg.split("'")[1] if "'" in msg else "unknown"
        return f"Install missing module: pip install {module}"

    if result.error_type == "TypeError":
        if "unexpected keyword argument" in msg:
            # Extract the argument name
            arg = msg.split("'")[1] if "'" in msg else "unknown"
            return f"Check function signature - argument '{arg}' may have been renamed"

    if result.error_type == "ImportError":
        if "cannot import name" in msg:
            name = msg.split("'")[1] if "'" in msg else "unknown"
            return f"'{name}' may have been removed or renamed in the source module"

    return None


def find_streamlit_pages(app_dir: Path) -> list[Path]:
    """Find all Streamlit page files."""
    pages = []

    # Main app file
    main_app = app_dir / "Home.py"
    if main_app.exists():
        pages.append(main_app)

    # Pages directory
    pages_dir = app_dir / "pages"
    if pages_dir.exists():
        for page_file in sorted(pages_dir.glob("*.py")):
            if not page_file.name.startswith("_"):
                pages.append(page_file)

    return pages


def find_util_modules(app_dir: Path) -> list[Path]:
    """Find all utility modules in streamlit_app."""
    utils = []

    # Utils directory
    utils_dir = app_dir / "utils"
    if utils_dir.exists():
        for util_file in sorted(utils_dir.glob("*.py")):
            if not util_file.name.startswith("_"):
                utils.append(util_file)

    # Components directory
    components_dir = app_dir / "components"
    if components_dir.exists():
        for comp_file in sorted(components_dir.glob("*.py")):
            if not comp_file.name.startswith("_"):
                utils.append(comp_file)

    return utils


def main():
    parser = argparse.ArgumentParser(
        description="Validate Streamlit app imports"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output for each file"
    )
    parser.add_argument(
        "--fix-suggestions", "-f",
        action="store_true",
        help="Show fix suggestions for errors"
    )
    parser.add_argument(
        "--utils-only",
        action="store_true",
        help="Only check utils/components (not pages)"
    )
    parser.add_argument(
        "--pages-only",
        action="store_true",
        help="Only check pages (not utils/components)"
    )
    parser.add_argument(
        "--skip-known",
        action="store_true",
        default=True,
        help="Skip known relative-import files (default: True)"
    )
    parser.add_argument(
        "--check-all",
        action="store_true",
        help="Check all files including known relative-import files"
    )

    args = parser.parse_args()

    # Find project root and app directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    app_dir = project_root / "streamlit_app"

    if not app_dir.exists():
        print(f"❌ Streamlit app directory not found: {app_dir}")
        sys.exit(1)

    # Add paths for imports - both project root and streamlit_app
    # This mimics how Streamlit resolves imports when running the app
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(app_dir))

    # Collect files to check
    files_to_check = []

    if not args.pages_only:
        files_to_check.extend(find_util_modules(app_dir))

    if not args.utils_only:
        files_to_check.extend(find_streamlit_pages(app_dir))

    # Filter out known relative-import files if --skip-known (default)
    skip_known = args.skip_known and not args.check_all
    skipped_files = []
    if skip_known:
        original_count = len(files_to_check)
        filtered = []
        for f in files_to_check:
            if f.name in KNOWN_RELATIVE_IMPORT_FILES:
                skipped_files.append(f)
            else:
                filtered.append(f)
        files_to_check = filtered

    if not files_to_check:
        print("No files found to check")
        sys.exit(0)

    # Run import validation
    print("=" * 60)
    print("Streamlit Import Validation")
    print("=" * 60)
    print(f"Checking {len(files_to_check)} files...")
    if skipped_files:
        print(f"Skipping {len(skipped_files)} known relative-import files (use --check-all to include)")
    print()

    results = []
    for file_path in files_to_check:
        result = validate_import(file_path)
        results.append(result)

        relative_path = file_path.relative_to(project_root)

        if result.success:
            if args.verbose:
                print(f"  ✅ {relative_path}")
        else:
            print(f"  ❌ {relative_path}")
            print(f"     {result.error_type}: {result.error_message}")

            if args.fix_suggestions:
                suggestion = get_fix_suggestion(result)
                if suggestion:
                    print(f"     💡 Suggestion: {suggestion}")
            print()

    # Summary
    print("=" * 60)
    success_count = sum(1 for r in results if r.success)
    fail_count = len(results) - success_count

    if fail_count == 0:
        print(f"✅ All {success_count} files imported successfully!")
        sys.exit(0)
    else:
        print(f"❌ {fail_count} file(s) failed to import, {success_count} succeeded")

        # Group errors by type
        error_types = {}
        for r in results:
            if not r.success:
                error_types.setdefault(r.error_type, []).append(r)

        print("\nErrors by type:")
        for error_type, errors in sorted(error_types.items()):
            print(f"  {error_type}: {len(errors)} file(s)")

        sys.exit(1)


if __name__ == "__main__":
    main()
