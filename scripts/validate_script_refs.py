#!/usr/bin/env python3
"""Validate that active scripts don't reference archived scripts at runtime.

Scans scripts/*.py and scripts/*.sh for references to scripts in scripts/_archive/.
Distinguishes between documentation comments (OK) and actual runtime calls (broken).

Usage:
    python scripts/validate_script_refs.py          # Check only
    python scripts/validate_script_refs.py --fix    # Show fix suggestions
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
ARCHIVE_DIR = SCRIPTS_DIR / "_archive"

# Patterns that indicate documentation, not runtime calls
DOC_PATTERNS = [
    r"^\s*#",  # Comments
    r"Replaces:",  # Consolidation docs
    r"Consolidates:",  # Consolidation docs
    r"Previously:",  # History notes
    r"replaced:",  # History notes
    r"was:",  # History notes
    r"→.*archived",  # Archive notes
    r"merged into",  # Consolidation notes
]

# Patterns that indicate actual runtime references
RUNTIME_PATTERNS_PY = [
    r'Path\(["\']scripts/',  # Path("scripts/foo.py")
    r'_run_script\(["\']',  # _run_script("foo.py")
    r"subprocess\.run\(.*scripts/",  # subprocess.run(["scripts/..."])
    r'run_script\(["\']',  # run_script("foo.py")
]

RUNTIME_PATTERNS_SH = [
    r"scripts/\S+\.(py|sh)",  # Direct script invocation in bash
]


def get_archived_names() -> set[str]:
    """Get set of archived script filenames that DON'T have active replacements."""
    if not ARCHIVE_DIR.exists():
        return set()
    archived = set()
    for f in ARCHIVE_DIR.iterdir():
        if f.is_file() and not f.name.startswith("."):
            # Only count as archived if no active version exists
            active_version = SCRIPTS_DIR / f.name
            if not active_version.exists():
                archived.add(f.name)
    return archived


def is_doc_line(line: str) -> bool:
    """Check if line is documentation, not a runtime reference."""
    for pattern in DOC_PATTERNS:
        if re.search(pattern, line):
            return True
    return False


def check_file(filepath: Path, archived_names: set[str]) -> list[dict]:
    """Check a single file for stale references to archived scripts."""
    issues = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return issues

    for i, line in enumerate(content.splitlines(), 1):
        for name in archived_names:
            if name not in line:
                continue
            if is_doc_line(line):
                continue

            # Determine severity
            severity = "info"
            if filepath.suffix == ".py":
                for pattern in RUNTIME_PATTERNS_PY:
                    if re.search(pattern, line):
                        severity = "error"
                        break
            elif filepath.suffix == ".sh":
                for pattern in RUNTIME_PATTERNS_SH:
                    if re.search(pattern, line):
                        severity = "error"
                        break

            # Echo/print references are warnings (misleading output)
            if "echo " in line or "print(" in line:
                severity = "warning"

            issues.append(
                {
                    "file": str(filepath.relative_to(REPO_ROOT)),
                    "line": i,
                    "archived": name,
                    "severity": severity,
                    "text": line.strip()[:120],
                }
            )

    return issues


def main() -> int:
    show_fix = "--fix" in sys.argv
    archived_names = get_archived_names()
    if not archived_names:
        print("No archived scripts found.")
        return 0

    all_issues: list[dict] = []

    # Scan active scripts only
    for ext in ("*.py", "*.sh"):
        for filepath in SCRIPTS_DIR.glob(ext):
            if filepath.parent == ARCHIVE_DIR:
                continue
            all_issues.extend(check_file(filepath, archived_names))

    if not all_issues:
        print("✅ No stale references to archived scripts found.")
        return 0

    errors = [i for i in all_issues if i["severity"] == "error"]
    warnings = [i for i in all_issues if i["severity"] == "warning"]
    infos = [i for i in all_issues if i["severity"] == "info"]

    print(f"Found {len(all_issues)} stale reference(s) to archived scripts:")
    print(f"  ❌ {len(errors)} runtime breaks (actual calls to missing scripts)")
    print(f"  ⚠️  {len(warnings)} misleading output (echo/print of missing scripts)")
    print(f"  ℹ️  {len(infos)} informational (comments, docstrings)")
    print()

    if errors:
        print("❌ RUNTIME BREAKS (will fail when called):")
        for issue in errors:
            print(f"  {issue['file']}:{issue['line']} → {issue['archived']}")
            if show_fix:
                print(f"    {issue['text']}")
        print()

    if warnings:
        print("⚠️  MISLEADING OUTPUT (references non-existent scripts):")
        for issue in warnings:
            print(f"  {issue['file']}:{issue['line']} → {issue['archived']}")
            if show_fix:
                print(f"    {issue['text']}")
        print()

    if show_fix and infos:
        print("ℹ️  INFORMATIONAL (documentation references — low priority):")
        for issue in infos:
            print(f"  {issue['file']}:{issue['line']} → {issue['archived']}")
        print()

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
