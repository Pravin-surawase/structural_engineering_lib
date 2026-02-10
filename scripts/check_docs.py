#!/usr/bin/env python3
"""
Unified documentation checker — consolidates 4 doc validation scripts.

Subcommands:
    --metadata       Check doc metadata headers (Type, Audience, Status)
    --frontmatter    Check YAML front-matter validation
    --index          Check docs/README.md heading structure
    --index-links    Check docs/README.md link resolution
    --all            Run all checks (default)

Replaces:
    - check_doc_metadata.py
    - check_doc_frontmatter.py
    - check_docs_index.py
    - check_docs_index_links.py

Usage:
    python scripts/check_docs.py                  # Run all checks
    python scripts/check_docs.py --metadata       # Metadata only
    python scripts/check_docs.py --frontmatter    # Front-matter only
    python scripts/check_docs.py --index          # Index structure only
    python scripts/check_docs.py --index-links    # Index links only
    python scripts/check_docs.py --all --strict   # All checks, strict mode

Exit Codes:
    0: All checks pass
    1: One or more checks failed
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT, DOCS_DIR
DOCS_INDEX = DOCS_DIR / "README.md"

# ═══════════════════════════════════════════════════════════════════════════
# CHECK 1: FRONTMATTER — YAML front-matter validation
# ═══════════════════════════════════════════════════════════════════════════

# Required/optional fields for front-matter
FM_REQUIRED_FIELDS = ["owner", "status", "last_updated", "doc_type"]
FM_OPTIONAL_FIELDS = ["complexity", "tags"]
FM_VALID_VALUES = {
    "status": ["active", "draft", "deprecated", "archived"],
    "doc_type": ["guide", "reference", "tutorial", "index", "spec", "log"],
    "complexity": ["beginner", "intermediate", "advanced"],
}
FM_SKIP_DIRS = {"_archive", "node_modules", ".git", "__pycache__", ".venv"}
FM_SKIP_FILES = {
    "README.md",
    "index.md",
    "TASKS.md",
    "SESSION_LOG.md",
    "CHANGELOG.md",
}


def _parse_frontmatter(content: str) -> tuple[dict[str, Any] | None, str]:
    """Parse YAML front-matter from markdown content."""
    if not content.startswith("---"):
        return None, content
    end_match = re.search(r"\n---\s*\n", content[3:])
    if not end_match:
        return None, content
    fm_text = content[4 : end_match.start() + 3]
    remaining = content[end_match.end() + 4 :]
    fm_dict: dict[str, Any] = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip("'\"")
            if value.startswith("[") and value.endswith("]"):
                value = [
                    v.strip().strip("'\"") for v in value[1:-1].split(",") if v.strip()
                ]
            fm_dict[key] = value
    return fm_dict, remaining


def _validate_frontmatter_fields(fm: dict[str, Any]) -> list[str]:
    """Validate front-matter field values."""
    errors = []
    for field in FM_REQUIRED_FIELDS:
        if field not in fm:
            errors.append(f"Missing required field: {field}")
    for field, valid_values in FM_VALID_VALUES.items():
        if field in fm and fm[field] not in valid_values:
            errors.append(f"Invalid {field}: '{fm[field]}' (valid: {valid_values})")
    if "last_updated" in fm:
        try:
            datetime.strptime(str(fm["last_updated"]), "%Y-%m-%d")
        except ValueError:
            errors.append(
                f"Invalid last_updated format: '{fm['last_updated']}' (use YYYY-MM-DD)"
            )
    return errors


def check_frontmatter(add_missing: bool = False, json_output: bool = False) -> int:
    """Check all docs for YAML front-matter.

    Returns exit code: 0 pass, 1 fail.
    """
    if not DOCS_DIR.exists():
        print(f"❌ docs directory not found: {DOCS_DIR}")
        return 1

    report: dict[str, Any] = {
        "total": 0,
        "with_frontmatter": 0,
        "without_frontmatter": 0,
        "invalid_frontmatter": 0,
        "skipped": 0,
        "files_without": [],
        "files_invalid": [],
    }

    for md_file in DOCS_DIR.rglob("*.md"):
        if any(skip in md_file.parts for skip in FM_SKIP_DIRS):
            report["skipped"] += 1
            continue
        if md_file.name in FM_SKIP_FILES:
            report["skipped"] += 1
            continue

        report["total"] += 1
        rel_path = md_file.relative_to(DOCS_DIR)

        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        fm, _ = _parse_frontmatter(content)
        if fm is None:
            report["without_frontmatter"] += 1
            report["files_without"].append(str(rel_path))
            if add_missing:
                doc_type = "guide"
                for dt in ("reference", "tutorial", "spec"):
                    if dt in str(rel_path):
                        doc_type = dt
                        break
                today = datetime.now().strftime("%Y-%m-%d")
                template = (
                    f"---\nowner: Main Agent\nstatus: active\n"
                    f"last_updated: {today}\ndoc_type: {doc_type}\n"
                    f"complexity: intermediate\ntags: []\n---\n\n"
                )
                md_file.write_text(template + content, encoding="utf-8")
                print(f"  ✅ Added front-matter: {rel_path}")
        else:
            report["with_frontmatter"] += 1
            errors = _validate_frontmatter_fields(fm)
            if errors:
                report["invalid_frontmatter"] += 1
                report["files_invalid"].append({"file": str(rel_path), "errors": errors})

    if json_output:
        print(json.dumps(report, indent=2))
        return 0

    print("\n📊 Front-Matter Report")
    print(f"{'=' * 40}")
    print(f"Total docs checked: {report['total']}")
    print(f"With front-matter: {report['with_frontmatter']}")
    print(f"Without front-matter: {report['without_frontmatter']}")
    print(f"Invalid front-matter: {report['invalid_frontmatter']}")
    print(f"Skipped: {report['skipped']}")

    if report["files_without"] and not add_missing:
        print(f"\n⚠️  Files without front-matter ({len(report['files_without'])}):")
        for f in report["files_without"][:10]:
            print(f"   - {f}")
        if len(report["files_without"]) > 10:
            print(f"   ... and {len(report['files_without']) - 10} more")

    if report["files_invalid"]:
        print(f"\n❌ Files with invalid front-matter ({len(report['files_invalid'])}):")
        for item in report["files_invalid"][:5]:
            print(f"   - {item['file']}")
            for err in item["errors"]:
                print(f"     • {err}")

    return 1 if report["without_frontmatter"] or report["invalid_frontmatter"] else 0


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 2: METADATA — Metadata headers (Type, Audience, Status)
# ═══════════════════════════════════════════════════════════════════════════

META_EXEMPT_FOLDERS = [
    "_archive", "_internal", "_references", "research/",
    "getting-started/NEW-DEVELOPER", "learning-materials",
    "external_data", "htmlcov", "build",
    "structural_lib_is456.egg-info", "UNKNOWN.egg-info",
]
META_EXEMPT_FILES = [
    "README.md", "index.md", "CHANGELOG.md", "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md", "AUTHORS.md", "SECURITY.md", "LICENSE.md",
    "LICENSE_ENGINEERING.md", "llms.txt", "CITATION.cff",
    "SESSION_LOG.md", "TASKS.md", "next-session-brief.md", "handoff.md",
]
META_REQUIRED_FIELDS = ["Type", "Audience", "Status"]
META_VALID_VALUES = {
    "Type": [
        "Guide", "Research", "Reference", "Architecture", "Decision",
        "Implementation", "Plan", "Index", "Hub", "Session", "Catalog",
        "Specification", "Blog", "Lesson",
    ],
    "Audience": [
        "All Agents", "Developers", "Users", "Maintainers",
        "Architects", "Implementation Agents", "Support Agents",
    ],
    "Status": [
        "Draft", "In Progress", "Review", "Approved", "Complete",
        "Deprecated", "Production Ready", "Phase 1 Complete", "Phase 2 Complete",
    ],
    "Importance": ["Critical", "High", "Medium", "Low"],
}


def _is_meta_exempt(file_path: Path) -> bool:
    """Check if file is exempt from metadata requirements."""
    path_str = str(file_path)
    for exempt in META_EXEMPT_FOLDERS:
        if exempt in path_str:
            return True
    if file_path.name in META_EXEMPT_FILES:
        return True
    if not path_str.startswith("docs/") and not path_str.startswith("agents/"):
        return True
    return False


def _extract_metadata(content: str) -> dict[str, str]:
    """Extract **Field:** Value metadata from markdown."""
    metadata = {}
    pattern = r"\*\*(\w+):\*\*\s*(.+?)(?:\n|$)"
    for match in re.finditer(pattern, content[:2000]):
        metadata[match.group(1)] = match.group(2).strip()
    return metadata


def _validate_metadata(content: str) -> tuple[list[str], list[str]]:
    """Validate metadata fields. Returns (errors, warnings)."""
    errors = []
    warnings = []
    metadata = _extract_metadata(content)
    for field in META_REQUIRED_FIELDS:
        if field not in metadata:
            errors.append(f"Missing required field: **{field}:**")
        elif metadata[field] not in META_VALID_VALUES.get(field, []):
            warnings.append(
                f"Unknown value for {field}: '{metadata[field]}' "
                f"(valid: {', '.join(META_VALID_VALUES.get(field, [])[:5])}...)"
            )
    for field in ("Created", "Last Updated", "Importance"):
        if field not in metadata:
            warnings.append(f"Consider adding: **{field}:**")
    return errors, warnings


def check_metadata(
    files: list[str] | None = None,
    check_all: bool = False,
    strict: bool = False,
    quiet: bool = False,
) -> int:
    """Check documentation metadata headers.

    Returns exit code: 0 pass, 1 fail (strict mode only).
    """
    if files:
        md_files = [Path(f) for f in files]
    elif check_all:
        md_files = []
        for pattern in ("docs/**/*.md", "agents/**/*.md"):
            md_files.extend(
                f.relative_to(REPO_ROOT) for f in REPO_ROOT.glob(pattern)
            )
    else:
        # Staged files
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                capture_output=True, text=True, cwd=REPO_ROOT,
            )
            md_files = [Path(l) for l in result.stdout.strip().split("\n") if l.endswith(".md")]
        except Exception:
            md_files = []

    files_to_check = [f for f in md_files if not _is_meta_exempt(f)]
    if not files_to_check:
        print("✅ No markdown files to check (all exempt or none found)")
        return 0

    print(f"   Checking {len(files_to_check)} file(s) for metadata...")

    total_errors = 0
    total_warnings = 0
    for fp in files_to_check:
        full = REPO_ROOT / fp
        if not full.exists():
            continue
        try:
            content = full.read_text(encoding="utf-8")
        except Exception:
            continue
        errors, warnings = _validate_metadata(content)
        if errors or (warnings and not quiet):
            print(f"\n📄 {fp}")
            for e in errors:
                print(f"  ❌ {e}")
            if not quiet:
                for w in warnings:
                    print(f"  ⚠️  {w}")
        total_errors += len(errors)
        if not quiet:
            total_warnings += len(warnings)

    print()
    if total_errors == 0 and total_warnings == 0:
        print("✅ All checked files have proper metadata!")
        return 0
    elif total_errors == 0:
        print(f"⚠️  {total_warnings} warning(s) found (metadata recommended)")
        return 0
    else:
        print(f"❌ {total_errors} error(s), {total_warnings} warning(s)")
        return 1 if strict else 0


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 3: INDEX — docs/README.md heading structure
# ═══════════════════════════════════════════════════════════════════════════

INDEX_REQUIRED_HEADINGS = [
    "# Docs Index (Start Here)",
    "## Quick CLI Reference",
    "## For Most Users",
    "## Visual Outputs",
    "## For Contributors / Maintainers",
    "## Planning / Research",
    "## Release History",
    "## Internal (multi-agent workflow)",
]


def check_index() -> int:
    """Validate docs/README.md heading structure.

    Returns exit code: 0 pass, 1 fail.
    """
    if not DOCS_INDEX.exists():
        print("ERROR: docs/README.md not found")
        return 1

    text = DOCS_INDEX.read_text(encoding="utf-8")
    lines = text.splitlines()

    missing = []
    for heading in INDEX_REQUIRED_HEADINGS:
        if not any(line.startswith(heading) for line in lines):
            missing.append(heading)

    if missing:
        for h in missing:
            print(f"ERROR: Missing heading: {h}")
        return 1

    print("✅ docs/README.md heading structure OK")
    return 0


# ═══════════════════════════════════════════════════════════════════════════
# CHECK 4: INDEX-LINKS — docs/README.md link resolution
# ═══════════════════════════════════════════════════════════════════════════

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^```")


def _strip_code_blocks(text: str) -> str:
    """Remove fenced code blocks from markdown."""
    lines = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    return "\n".join(lines)


def check_index_links() -> int:
    """Ensure docs/README.md links resolve to real files/dirs.

    Returns exit code: 0 pass, 1 fail.
    """
    if not DOCS_INDEX.exists():
        print("ERROR: docs/README.md not found")
        return 1

    text = _strip_code_blocks(DOCS_INDEX.read_text(encoding="utf-8"))
    base = DOCS_INDEX.parent

    errors: list[str] = []
    for match in LINK_RE.finditer(text):
        link = match.group(1).strip()
        if not link or link.startswith(("http://", "https://", "mailto:", "#")):
            continue
        link_path = link.split("#", 1)[0]
        if not link_path:
            continue
        resolved = (base / link_path).resolve()
        if not resolved.exists():
            errors.append(f"Missing: {link_path}")

    if errors:
        print("ERROR: docs/README.md contains broken local links:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("✅ docs/README.md links OK")
    return 0


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Unified documentation checker (metadata, front-matter, index, links)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/check_docs.py                  # Run all checks\n"
            "  python scripts/check_docs.py --metadata       # Metadata only\n"
            "  python scripts/check_docs.py --frontmatter    # Front-matter only\n"
            "  python scripts/check_docs.py --index          # Index heading structure\n"
            "  python scripts/check_docs.py --index-links    # Index link resolution\n"
            "  python scripts/check_docs.py --all --strict   # All checks, strict mode\n"
        ),
    )

    # Subcommand selectors
    group = parser.add_argument_group("Check selectors (default: --all)")
    group.add_argument("--metadata", action="store_true", help="Check doc metadata headers")
    group.add_argument("--frontmatter", action="store_true", help="Check YAML front-matter")
    group.add_argument("--index", action="store_true", help="Check docs/README.md headings")
    group.add_argument("--index-links", action="store_true", help="Check docs/README.md links")
    group.add_argument("--all", action="store_true", help="Run all checks (default)")

    # Metadata options
    meta_group = parser.add_argument_group("Metadata options")
    meta_group.add_argument("--strict", action="store_true", help="Fail on missing metadata")
    meta_group.add_argument("--quiet", action="store_true", help="Only show errors, not warnings")
    meta_group.add_argument("files", nargs="*", help="Specific files to check (metadata)")
    meta_group.add_argument(
        "--check-all-files", action="store_true",
        help="Check all markdown files (metadata), not just staged",
    )

    # Frontmatter options
    fm_group = parser.add_argument_group("Frontmatter options")
    fm_group.add_argument("--add", action="store_true", help="Add front-matter template to files without it")
    fm_group.add_argument("--json", action="store_true", help="Output JSON report (frontmatter)")

    args = parser.parse_args()

    # Default to --all when no selector given
    run_all = args.all or not any([args.metadata, args.frontmatter, args.index, args.index_links])

    results: list[int] = []

    if run_all or args.metadata:
        print("📋 Checking documentation metadata...")
        rc = check_metadata(
            files=args.files or None,
            check_all=args.check_all_files or run_all,
            strict=args.strict,
            quiet=args.quiet,
        )
        results.append(rc)

    if run_all or args.frontmatter:
        print("🔍 Checking documentation front-matter...")
        rc = check_frontmatter(add_missing=args.add, json_output=args.json)
        results.append(rc)

    if run_all or args.index:
        print("📑 Checking docs/README.md heading structure...")
        rc = check_index()
        results.append(rc)

    if run_all or args.index_links:
        print("🔗 Checking docs/README.md link resolution...")
        rc = check_index_links()
        results.append(rc)

    # Overall exit code: 0 if all pass, 1 if any fail
    if any(rc != 0 for rc in results):
        print(f"\n{'='*40}")
        print(f"❌ {sum(1 for rc in results if rc != 0)}/{len(results)} check(s) failed")
        return 1
    else:
        print(f"\n{'='*40}")
        print(f"✅ All {len(results)} check(s) passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
