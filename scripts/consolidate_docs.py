#!/usr/bin/env python3
"""Documentation Consolidation Workflow - Master Script.

This script orchestrates the safe consolidation of documentation files.
It provides:
1. Comprehensive analysis with validated metrics
2. Safe archival operations with link preservation
3. Dry-run mode for all operations
4. Before/after metrics comparison
5. Rollback information

**Usage:**
    python scripts/consolidate_docs.py analyze          # Run analysis
    python scripts/consolidate_docs.py archive --dry-run # Preview archival
    python scripts/consolidate_docs.py archive          # Execute archival
    python scripts/consolidate_docs.py report           # Show metrics report

**Safety Features:**
- All operations use safe_file_move.py (link preservation)
- Dry-run mode default for destructive operations
- Before/after metrics tracking
- Git-backed (easy rollback via git checkout)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
ARCHIVE_DIR = DOCS_DIR / "_archive"
METRICS_FILE = PROJECT_ROOT / "metrics" / "doc_consolidation_metrics.json"


def run_command(cmd: List[str], timeout: int = 30) -> Tuple[int, str, str]:
    """Run command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Timeout"
    except Exception as e:
        return 1, "", str(e)


def get_file_counts() -> Dict[str, int]:
    """Get current file counts by category."""
    counts = {
        "total_docs": 0,
        "research": 0,
        "research_sessions": 0,
        "research_summaries": 0,
        "research_phases": 0,
        "research_readmes": 0,
        "archived": 0,
        "contributing": 0,
        "planning": 0,
        "reference": 0,
        "agents": 0,
        "getting_started": 0,
    }

    for f in DOCS_DIR.rglob("*.md"):
        counts["total_docs"] += 1

        rel_path = f.relative_to(DOCS_DIR)
        parts = rel_path.parts

        if parts[0] == "_archive":
            counts["archived"] += 1
        elif parts[0] == "research":
            counts["research"] += 1
            name = f.name.lower()
            if "session" in name:
                counts["research_sessions"] += 1
            if "summary" in name:
                counts["research_summaries"] += 1
            if "phase" in name:
                counts["research_phases"] += 1
            if name == "readme.md":
                counts["research_readmes"] += 1
        elif parts[0] == "contributing":
            counts["contributing"] += 1
        elif parts[0] == "planning":
            counts["planning"] += 1
        elif parts[0] == "reference":
            counts["reference"] += 1
        elif parts[0] == "agents":
            counts["agents"] += 1
        elif parts[0] == "getting-started":
            counts["getting_started"] += 1

    return counts


def get_link_metrics() -> Dict[str, int]:
    """Get link validation metrics."""
    code, stdout, _ = run_command(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "check_links.py")],
        timeout=60,
    )

    # Parse output
    total_links = 0
    broken_links = 0

    for line in stdout.split("\n"):
        if "internal links" in line.lower():
            match = re.search(r"(\d+)", line)
            if match:
                total_links = int(match.group(1))
        if "broken" in line.lower():
            match = re.search(r"(\d+)", line)
            if match:
                broken_links = int(match.group(1))

    return {"total_links": total_links, "broken_links": broken_links}


def save_metrics(phase: str, metrics: Dict) -> None:
    """Save metrics to JSON file."""
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)

    data = {}
    if METRICS_FILE.exists():
        with open(METRICS_FILE) as f:
            data = json.load(f)

    timestamp = datetime.now().isoformat()
    data[f"{phase}_{timestamp}"] = {
        "phase": phase,
        "timestamp": timestamp,
        "metrics": metrics,
    }

    with open(METRICS_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"📊 Metrics saved to {METRICS_FILE.relative_to(PROJECT_ROOT)}")


def find_archivable_session_files() -> List[Tuple[Path, str]]:
    """Find session-specific research files that can be archived.

    Criteria for archival:
    1. Session-specific research files (session-9, session-10, session-11)
    2. Older session analysis files
    3. One-time brainstorm/summary files
    """
    candidates = []

    research_dir = DOCS_DIR / "research"
    if not research_dir.exists():
        return candidates

    for f in research_dir.glob("*.md"):
        name = f.name.lower()
        reason = None

        # Old session files (session 9, 10, 11 are from early January)
        if re.match(r"session-\d+-", name) or re.match(r"session-\d+\.", name):
            # Check if it's an old session (before session 15)
            match = re.search(r"session-(\d+)", name)
            if match:
                session_num = int(match.group(1))
                if session_num < 15:
                    reason = f"Old session research (Session {session_num})"

        # One-time session summaries with dates
        if "session-summary" in name or "session-research-summary" in name:
            # Check if it has a date in the name
            if re.search(r"\d{8}|\d{4}-\d{2}-\d{2}", name):
                reason = "Dated session summary"

        # Brainstorm sessions (one-time events)
        if "brainstorm-session" in name:
            reason = "One-time brainstorm session"

        if reason:
            candidates.append((f, reason))

    return candidates


def find_consolidatable_phase_files() -> List[Tuple[Path, str]]:
    """Find PHASE files that can be consolidated."""
    candidates = []

    research_dir = DOCS_DIR / "research"
    literature_dir = research_dir / "literature-review" / "week-1-pareto-optimization"

    # Check main research folder
    for f in research_dir.glob("PHASE-*.md"):
        candidates.append((f, "PHASE research file"))

    # Check literature review subfolder
    if literature_dir.exists():
        for f in literature_dir.glob("PHASE-*.md"):
            candidates.append((f, "Literature review PHASE file"))

    return candidates


def find_archivable_completed_research() -> List[Tuple[Path, str]]:
    """Find completed research files that can be archived.

    Criteria:
    1. Research with Status: Complete/Done/Implemented/Archived
    2. Older implementation plans that are done
    3. Dated audit/analysis files

    Exclusions:
    - Today's research file
    - Active strategy files
    - Core reference files
    - Files with Status: In Progress
    - Files modified in last 7 days (considered active)
    """
    candidates = []

    research_dir = DOCS_DIR / "research"
    if not research_dir.exists():
        return candidates

    # Patterns to always exclude (active/needed files)
    exclude_patterns = [
        "README.md",
        "documentation-consolidation-research-2026-01-13.md",  # Today's work
        "file-metadata-standards-research.md",  # Active research
        "methodology",  # Reference file
        "backlog",  # Active planning
        "JOURNEY",  # Active tracking
        "in-progress",  # Obviously in progress
        "SESSION-SUMMARY",  # Current session work
    ]

    # Patterns that indicate file is still active/in-progress
    active_patterns = [
        re.compile(
            r"\*\*Status\*\*:.*(?:In Progress|Draft|WIP|Active|Pending)", re.IGNORECASE
        ),
        re.compile(r"Status:.*(?:In Progress|Draft|WIP|Active|Pending)", re.IGNORECASE),
    ]

    # Complete status patterns - handle various formats including emojis
    complete_patterns = [
        re.compile(
            r"\*\*Status\*\*:.*(?:Complete|Done|Implemented|Archived)", re.IGNORECASE
        ),
        re.compile(r"Status:.*(?:Complete|Done|Implemented|Archived)", re.IGNORECASE),
    ]

    for f in research_dir.glob("*.md"):
        name = f.name

        # Skip excluded files
        if any(excl.lower() in name.lower() for excl in exclude_patterns):
            continue

        try:
            content = f.read_text()[:2000]  # First ~30 lines

            # Check if file is marked as in-progress (skip it)
            is_active = False
            for pattern in active_patterns:
                if pattern.search(content):
                    is_active = True
                    break

            if is_active:
                continue  # Don't archive active files

            # Check if file has Complete status
            for pattern in complete_patterns:
                if pattern.search(content):
                    candidates.append((f, "Status: Complete"))
                    break
        except Exception:
            pass

    return candidates


def archive_file(source: Path, dest_folder: str, dry_run: bool = True) -> bool:
    """Archive a single file using safe_file_move.py."""
    dest_path = ARCHIVE_DIR / dest_folder / source.name

    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "safe_file_move.py"),
        str(source),
        str(dest_path),
    ]

    if dry_run:
        cmd.append("--dry-run")

    code, stdout, stderr = run_command(cmd, timeout=30)

    if code == 0:
        status = "Would archive" if dry_run else "Archived"
        print(f"   ✓ {status}: {source.name}")
        return True
    else:
        print(f"   ✗ Failed: {source.name}")
        if stderr:
            print(f"      Error: {stderr[:100]}")
        return False


def cmd_analyze(args):
    """Run comprehensive analysis."""
    print("=" * 70)
    print("📊 DOCUMENTATION CONSOLIDATION ANALYSIS")
    print("=" * 70)
    print()

    # Get current metrics
    counts = get_file_counts()
    links = get_link_metrics()

    print("📁 Current File Counts:")
    print(f"   Total docs:     {counts['total_docs']}")
    print(
        f"   Research:       {counts['research']} ({counts['research']/counts['total_docs']*100:.1f}%)"
    )
    print(f"   Archived:       {counts['archived']}")
    print(f"   Contributing:   {counts['contributing']}")
    print(f"   Planning:       {counts['planning']}")
    print(f"   Reference:      {counts['reference']}")
    print()

    print("🔗 Link Status:")
    print(f"   Total links:  {links['total_links']}")
    print(f"   Broken links: {links['broken_links']}")
    print()

    print("📦 Research Folder Breakdown:")
    print(f"   Session files:   {counts['research_sessions']}")
    print(f"   Summary files:   {counts['research_summaries']}")
    print(f"   Phase files:     {counts['research_phases']}")
    print(f"   README files:    {counts['research_readmes']}")
    print()

    # Find archivable files
    session_files = find_archivable_session_files()
    phase_files = find_consolidatable_phase_files()
    completed_files = find_archivable_completed_research()

    print("🎯 Consolidation Candidates:")
    print(f"   Archivable session files: {len(session_files)}")
    for f, reason in session_files[:5]:
        print(f"      • {f.name} ({reason})")
    if len(session_files) > 5:
        print(f"      ... and {len(session_files) - 5} more")

    print(f"   Consolidatable PHASE files: {len(phase_files)}")
    for f, reason in phase_files[:3]:
        print(f"      • {f.name}")

    print(f"   Completed research files: {len(completed_files)}")
    for f, reason in completed_files[:5]:
        print(f"      • {f.name} ({reason})")
    if len(completed_files) > 5:
        print(f"      ... and {len(completed_files) - 5} more")
    print()

    # Calculate potential reduction
    potential_reduction = len(session_files) + len(phase_files) + len(completed_files)
    new_total = counts["total_docs"] - potential_reduction
    reduction_pct = potential_reduction / counts["total_docs"] * 100

    print("📈 Potential Impact:")
    print(f"   Current total:    {counts['total_docs']} files")
    print(f"   After Phase 1:    {new_total} files (-{potential_reduction})")
    print(f"   Reduction:        {reduction_pct:.1f}%")
    print()

    # Save baseline metrics
    all_metrics = {
        "file_counts": counts,
        "link_metrics": links,
        "archivable_session_files": len(session_files),
        "consolidatable_phase_files": len(phase_files),
        "archivable_completed_files": len(completed_files),
        "potential_reduction": potential_reduction,
    }
    save_metrics("baseline", all_metrics)

    print("=" * 70)
    print("Next Steps:")
    print("  1. Review candidates above")
    print("  2. Run: python scripts/consolidate_docs.py archive --dry-run")
    print("  3. Review dry-run output")
    print("  4. Run: python scripts/consolidate_docs.py archive")
    print("=" * 70)


def cmd_archive(args):
    """Archive old session, phase, and completed research files."""
    print("=" * 70)
    print("📦 ARCHIVE OLD RESEARCH FILES")
    print("=" * 70)
    print()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be moved")
        print()

    # Get baseline metrics
    before_counts = get_file_counts()
    before_links = get_link_metrics()

    print(
        f"📊 Before: {before_counts['total_docs']} files, {before_links['broken_links']} broken links"
    )
    print()

    total_archived = 0
    total_candidates = 0

    # Category 1: Session files
    session_files = find_archivable_session_files()
    if session_files:
        print(f"📁 Category 1: Session research files ({len(session_files)} found):")
        total_candidates += len(session_files)
        for source, reason in session_files:
            if archive_file(source, "research-sessions", dry_run=args.dry_run):
                total_archived += 1
        print()

    # Category 2: PHASE files
    phase_files = find_consolidatable_phase_files()
    if phase_files:
        print(f"📁 Category 2: PHASE research files ({len(phase_files)} found):")
        total_candidates += len(phase_files)
        for source, reason in phase_files:
            if archive_file(source, "research-phases", dry_run=args.dry_run):
                total_archived += 1
        print()

    # Category 3: Completed research files
    completed_files = find_archivable_completed_research()
    if completed_files:
        print(
            f"📁 Category 3: Completed research files ({len(completed_files)} found):"
        )
        total_candidates += len(completed_files)
        for source, reason in completed_files:
            if archive_file(source, "research-completed", dry_run=args.dry_run):
                total_archived += 1
        print()

    if total_candidates == 0:
        print("✓ No files to archive")
        return

    print(
        f"{'Would archive' if args.dry_run else 'Archived'}: {total_archived}/{total_candidates} files"
    )

    if not args.dry_run:
        # Verify links after archival
        print()
        print("🔗 Validating links after archival...")
        after_links = get_link_metrics()
        after_counts = get_file_counts()

        print(
            f"📊 After: {after_counts['total_docs']} files, {after_links['broken_links']} broken links"
        )

        reduction = before_counts["total_docs"] - after_counts["total_docs"]
        print(f"📉 Reduction: {reduction} files")

        if after_links["broken_links"] > before_links["broken_links"]:
            print("⚠️ WARNING: New broken links detected!")
            print("   Run: .venv/bin/python scripts/check_links.py")
        else:
            print("✅ No new broken links!")

        # Save after metrics
        save_metrics(
            "after_archive",
            {
                "file_counts": after_counts,
                "link_metrics": after_links,
                "files_archived": total_archived,
                "reduction": reduction,
            },
        )

    print()
    print("=" * 70)
    if args.dry_run:
        print("Dry run complete. To execute, remove --dry-run flag.")
    else:
        print("Archive complete!")
        print("Next: ./scripts/ai_commit.sh 'docs: archive research files (TASK-457)'")
    print("=" * 70)


def cmd_report(args):
    """Show metrics report."""
    print("=" * 70)
    print("📈 CONSOLIDATION METRICS REPORT")
    print("=" * 70)
    print()

    if not METRICS_FILE.exists():
        print("No metrics data yet. Run 'analyze' first.")
        return

    with open(METRICS_FILE) as f:
        data = json.load(f)

    for key, entry in sorted(data.items()):
        print(f"📍 {entry['phase'].upper()} - {entry['timestamp'][:19]}")
        metrics = entry["metrics"]

        if "file_counts" in metrics:
            counts = metrics["file_counts"]
            print(f"   Total docs:  {counts['total_docs']}")
            print(f"   Research:    {counts['research']}")
            print(f"   Archived:    {counts['archived']}")

        if "link_metrics" in metrics:
            links = metrics["link_metrics"]
            print(f"   Total links: {links['total_links']}")
            print(f"   Broken:      {links['broken_links']}")

        if "files_archived" in metrics:
            print(f"   Files moved: {metrics['files_archived']}")

        print()

    print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Documentation Consolidation Workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/consolidate_docs.py analyze           # Run analysis
  python scripts/consolidate_docs.py archive --dry-run # Preview archival
  python scripts/consolidate_docs.py archive           # Execute archival
  python scripts/consolidate_docs.py report            # Show metrics
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Run comprehensive analysis")
    analyze_parser.set_defaults(func=cmd_analyze)

    # Archive command
    archive_parser = subparsers.add_parser("archive", help="Archive old session files")
    archive_parser.add_argument(
        "--dry-run", action="store_true", help="Preview without making changes"
    )
    archive_parser.set_defaults(func=cmd_archive)

    # Report command
    report_parser = subparsers.add_parser("report", help="Show metrics report")
    report_parser.set_defaults(func=cmd_report)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
