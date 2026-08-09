#!/usr/bin/env python3
"""Validate that active control paths reference existing scripts.

Scans the unified CLI, pre-commit configuration, GitHub workflows, and active
top-level scripts. References to archived, retired, or otherwise missing script
targets fail when they occur in an executable control path.

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
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
CONTROL_FILES = {
    REPO_ROOT / "run.sh",
    REPO_ROOT / ".pre-commit-config.yaml",
}
RETIRED_NAMES = {
    "ai_commit.sh",
    "safe_push.sh",
    "recover_git_state.sh",
    "finish_task_pr.sh",
    "create_task_pr.sh",
    "should_use_pr.sh",
    "install_git_hooks.sh",
}

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
    r"(?:scripts|\$SCRIPTS|\$\{SCRIPTS\})/\S+\.(py|sh)",
]

SCRIPT_REFERENCE_RE = re.compile(
    r"(?:scripts|\$SCRIPTS|\$\{SCRIPTS\})/([A-Za-z0-9_.-]+\.(?:py|sh))"
)


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
    return archived | RETIRED_NAMES


def is_doc_line(line: str) -> bool:
    """Check if line is documentation, not a runtime reference."""
    for pattern in DOC_PATTERNS:
        if re.search(pattern, line):
            return True
    return False


def _is_control_surface(filepath: Path) -> bool:
    """Return whether every script reference in *filepath* is executable."""
    if filepath in CONTROL_FILES:
        return True
    try:
        filepath.relative_to(WORKFLOWS_DIR)
    except ValueError:
        return False
    return filepath.suffix in {".yml", ".yaml"}


def _reference_severity(filepath: Path, line: str) -> str:
    """Classify a missing target reference by how the containing line is used."""
    if _is_control_surface(filepath):
        return "error"

    patterns = RUNTIME_PATTERNS_PY if filepath.suffix == ".py" else RUNTIME_PATTERNS_SH
    severity = (
        "error" if any(re.search(pattern, line) for pattern in patterns) else "info"
    )
    if "echo " in line or "print(" in line:
        return "warning"
    return severity


def check_file(filepath: Path, archived_names: set[str]) -> list[dict]:
    """Check a single file for stale references to known archived scripts."""
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

            issues.append(
                {
                    "file": str(filepath.relative_to(REPO_ROOT)),
                    "line": i,
                    "target": name,
                    "severity": _reference_severity(filepath, line),
                    "text": line.strip()[:120],
                }
            )

    return issues


def check_missing_targets(filepath: Path) -> list[dict]:
    """Return references whose top-level ``scripts/`` target does not exist."""
    issues = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return issues

    for line_number, line in enumerate(content.splitlines(), 1):
        if is_doc_line(line):
            continue
        code = line.split("#", 1)[0]
        for match in SCRIPT_REFERENCE_RE.finditer(code):
            name = match.group(1)
            if (SCRIPTS_DIR / name).is_file():
                continue
            issues.append(
                {
                    "file": str(filepath.relative_to(REPO_ROOT)),
                    "line": line_number,
                    "target": name,
                    "severity": _reference_severity(filepath, line),
                    "text": line.strip()[:120],
                }
            )
    return issues


def scan_files() -> list[Path]:
    """Return executable repository surfaces that may invoke scripts."""
    files = set(CONTROL_FILES)
    files.update(SCRIPTS_DIR.glob("*.py"))
    files.update(SCRIPTS_DIR.glob("*.sh"))
    if WORKFLOWS_DIR.is_dir():
        files.update(WORKFLOWS_DIR.glob("*.yml"))
        files.update(WORKFLOWS_DIR.glob("*.yaml"))
    return sorted(filepath for filepath in files if filepath.is_file())


def main() -> int:
    show_fix = "--fix" in sys.argv
    archived_names = get_archived_names()
    all_issues: list[dict] = []

    for filepath in scan_files():
        all_issues.extend(check_file(filepath, archived_names))
        all_issues.extend(check_missing_targets(filepath))

    # A known archived name may also be found by the generic missing-target scan.
    unique_issues = {}
    for issue in all_issues:
        key = (issue["file"], issue["line"], issue["target"])
        unique_issues[key] = issue
    all_issues = list(unique_issues.values())

    if not all_issues:
        print("✅ All active script control-path targets exist.")
        return 0

    errors = [i for i in all_issues if i["severity"] == "error"]
    warnings = [i for i in all_issues if i["severity"] == "warning"]
    infos = [i for i in all_issues if i["severity"] == "info"]

    print(f"Found {len(all_issues)} reference(s) to missing scripts:")
    print(f"  ❌ {len(errors)} runtime breaks (actual calls to missing scripts)")
    print(f"  ⚠️  {len(warnings)} misleading output (echo/print of missing scripts)")
    print(f"  ℹ️  {len(infos)} informational (comments, docstrings)")
    print()

    if errors:
        print("❌ RUNTIME BREAKS (will fail when called):")
        for issue in errors:
            print(f"  {issue['file']}:{issue['line']} → {issue['target']}")
            if show_fix:
                print(f"    {issue['text']}")
        print()

    if warnings:
        print("⚠️  MISLEADING OUTPUT (references non-existent scripts):")
        for issue in warnings:
            print(f"  {issue['file']}:{issue['line']} → {issue['target']}")
            if show_fix:
                print(f"    {issue['text']}")
        print()

    if show_fix and infos:
        print("ℹ️  INFORMATIONAL (documentation references — low priority):")
        for issue in infos:
            print(f"  {issue['file']}:{issue['line']} → {issue['target']}")
        print()

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
