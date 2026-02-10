#!/usr/bin/env python3
"""
Check documentation files for proper metadata headers.

USAGE:
    # Check all staged markdown files
    python scripts/check_doc_metadata.py

    # Check all markdown files
    python scripts/check_doc_metadata.py --all

    # Check specific file
    python scripts/check_doc_metadata.py docs/research/my-file.md

    # Fail on missing metadata (for CI)
    python scripts/check_doc_metadata.py --strict

This script validates that markdown files have the required metadata fields:
- **Type:** (required)
- **Audience:** (required)
- **Status:** (required)
- **Importance:** (optional)
- **Created:** (optional)
- **Last Updated:** (optional)

Exit codes:
- 0: All files pass or warnings only
- 1: Files missing metadata (only with --strict)
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

# Folders exempt from metadata requirements (legacy/auto-generated)
EXEMPT_FOLDERS = [
    "_archive",
    "_internal",
    "_references",
    "research/",  # Legacy research files (UPPERCASE naming)
    "getting-started/NEW-DEVELOPER",
    "learning-materials",
    "external_data",
    "htmlcov",
    "build",
    "structural_lib_is456.egg-info",
    "UNKNOWN.egg-info",
]

# Files exempt from metadata requirements
EXEMPT_FILES = [
    "README.md",  # Auto-generated indexes
    "index.md",  # Auto-generated indexes
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "AUTHORS.md",
    "SECURITY.md",
    "LICENSE.md",
    "LICENSE_ENGINEERING.md",
    "llms.txt",
    "CITATION.cff",
    "SESSION_LOG.md",  # Append-only log
    "TASKS.md",  # Special format
    "next-session-brief.md",  # Short handoff doc
    "handoff.md",
]

# Required metadata fields
REQUIRED_FIELDS = ["Type", "Audience", "Status"]

# Valid values for each field
VALID_VALUES = {
    "Type": [
        "Guide",
        "Research",
        "Reference",
        "Architecture",
        "Decision",
        "Implementation",
        "Plan",
        "Index",
        "Hub",
        "Session",
        "Catalog",
        "Specification",
        "Blog",
        "Lesson",
    ],
    "Audience": [
        "All Agents",
        "Developers",
        "Users",
        "Maintainers",
        "Architects",
        "Implementation Agents",
        "Support Agents",
    ],
    "Status": [
        "Draft",
        "In Progress",
        "Review",
        "Approved",
        "Complete",
        "Deprecated",
        "Production Ready",
        "Phase 1 Complete",
        "Phase 2 Complete",
    ],
    "Importance": ["Critical", "High", "Medium", "Low"],
}


def validate_doc_name(file_path: Path) -> list[str]:
    """Validate document naming conventions."""
    issues = []
    name = file_path.name
    path_str = str(file_path)

    # Exempt common index files
    if name in {"README.md", "index.md"}:
        return issues

    # Enforce lowercase for new docs (warn only)
    if re.search(r"[A-Z]", name):
        issues.append("Use lowercase filenames (avoid uppercase letters).")

    # Discourage underscores
    if "_" in name:
        issues.append("Prefer hyphens over underscores in filenames.")

    # Disallow numbered prefixes for non-ordered content
    if re.match(r"^\\d+[-_]", name):
        issues.append("Avoid numbered prefixes (e.g., 01- or 02_).")

    # Discourage agent/session prefixes outside agent-specific folders
    if re.match(r"^(agent|session)-", name) and not (
        "docs/agents/" in path_str or path_str.startswith("agents/")
    ):
        issues.append("Avoid agent/session prefixes for canonical docs.")

    # Basic allowed pattern (warn if unexpected)
    if not re.match(r"^(adr-\\d+-)?[a-z0-9][a-z0-9.-]*\\.md$", name):
        issues.append("Filename pattern is unusual; prefer lowercase + hyphens.")

    return issues


def is_exempt_path(file_path: Path) -> bool:
    """Check if file path is exempt from metadata requirements."""
    path_str = str(file_path)

    # Check folder exemptions
    for exempt in EXEMPT_FOLDERS:
        if exempt in path_str:
            return True

    # Check file exemptions
    if file_path.name in EXEMPT_FILES:
        return True

    # Only check docs/ folder (not Python/, VBA/, etc.)
    if not path_str.startswith("docs/") and not path_str.startswith("agents/"):
        return True

    return False


def get_staged_markdown_files() -> list[Path]:
    """Get list of staged markdown files."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        files = []
        for line in result.stdout.strip().split("\n"):
            if line.endswith(".md"):
                files.append(Path(line))
        return files
    except Exception as e:
        print(f"Warning: Could not get staged files: {e}")
        return []


def get_all_markdown_files() -> list[Path]:
    """Get all markdown files in docs/ and agents/ folders."""
    files = []
    for pattern in ["docs/**/*.md", "agents/**/*.md"]:
        files.extend(REPO_ROOT.glob(pattern))
    return [f.relative_to(REPO_ROOT) for f in files]


def extract_metadata(content: str) -> dict[str, str]:
    """Extract metadata fields from markdown content."""
    metadata = {}

    # Pattern: **Field:** Value
    pattern = r"\*\*(\w+):\*\*\s*(.+?)(?:\n|$)"

    for match in re.finditer(pattern, content[:2000]):  # Only check first 2000 chars
        field = match.group(1)
        value = match.group(2).strip()
        metadata[field] = value

    return metadata


def validate_metadata(file_path: Path, content: str) -> tuple[list[str], list[str]]:
    """
    Validate metadata in a file.

    Returns:
        Tuple of (errors, warnings)
    """
    errors = []
    warnings = []

    metadata = extract_metadata(content)

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in metadata:
            errors.append(f"Missing required field: **{field}:**")
        elif metadata[field] not in VALID_VALUES.get(field, []):
            warnings.append(
                f"Unknown value for {field}: '{metadata[field]}' "
                f"(valid: {', '.join(VALID_VALUES.get(field, [])[:5])}...)"
            )

    # Check optional fields (warnings only)
    optional_fields = ["Created", "Last Updated", "Importance"]
    for field in optional_fields:
        if field not in metadata:
            warnings.append(f"Consider adding: **{field}:**")

    return errors, warnings


def check_file(file_path: Path) -> tuple[int, int]:
    """
    Check a single file for metadata.

    Returns:
        Tuple of (error_count, warning_count)
    """
    if is_exempt_path(file_path):
        return 0, 0

    full_path = REPO_ROOT / file_path
    if not full_path.exists():
        return 0, 0

    try:
        content = full_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ⚠️  Could not read {file_path}: {e}")
        return 0, 1

    errors, warnings = validate_metadata(file_path, content)
    naming_issues = validate_doc_name(file_path)
    warnings.extend(naming_issues)

    if errors or warnings:
        print(f"\n📄 {file_path}")
        for error in errors:
            print(f"  ❌ {error}")
        for warning in warnings:
            print(f"  ⚠️  {warning}")

    return len(errors), len(warnings)


def main():
    parser = argparse.ArgumentParser(description="Check documentation metadata headers")
    parser.add_argument(
        "files",
        nargs="*",
        help="Specific files to check (default: staged files)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Check all markdown files in docs/ and agents/",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error if metadata is missing",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only show errors, not warnings",
    )

    args = parser.parse_args()

    print("📋 Checking documentation metadata...")

    # Determine files to check
    if args.files:
        files = [Path(f) for f in args.files]
    elif args.all:
        files = get_all_markdown_files()
    else:
        files = get_staged_markdown_files()

    if not files:
        print("✅ No markdown files to check")
        return 0

    # Filter exempt files
    files_to_check = [f for f in files if not is_exempt_path(f)]

    if not files_to_check:
        print("✅ All files are exempt from metadata requirements")
        return 0

    print(f"   Checking {len(files_to_check)} file(s)...")

    total_errors = 0
    total_warnings = 0

    for file_path in files_to_check:
        errors, warnings = check_file(file_path)
        total_errors += errors
        if not args.quiet:
            total_warnings += warnings

    # Summary
    print()
    if total_errors == 0 and total_warnings == 0:
        print("✅ All checked files have proper metadata!")
        return 0
    elif total_errors == 0:
        print(f"⚠️  {total_warnings} warning(s) found (metadata recommended)")
        return 0  # Warnings don't fail
    else:
        print(f"❌ {total_errors} error(s), {total_warnings} warning(s)")
        if args.strict:
            print(
                "\n💡 Tip: Use 'python scripts/create_doc.py <path> <title>' to create files with proper metadata"
            )
            return 1
        else:
            print("   (Use --strict to enforce metadata requirements)")
            return 0


if __name__ == "__main__":
    sys.exit(main())
