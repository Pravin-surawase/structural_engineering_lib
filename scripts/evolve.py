#!/usr/bin/env python3
"""Self-evolution engine — orchestrates project health, feedback, and auto-fixes.

The brain of the self-evolving system. Combines health scanning, feedback
analysis, and auto-fixing into a single evolution cycle. Run periodically
or on-demand to keep the project self-maintaining.

Usage:
    python scripts/evolve.py                        # Full evolution cycle (dry-run)
    python scripts/evolve.py --fix                  # Apply all auto-fixes + commit
    python scripts/evolve.py --report               # Generate evolution report only
    python scripts/evolve.py --review weekly         # Quick weekly review
    python scripts/evolve.py --review monthly        # Comprehensive monthly review
    python scripts/evolve.py --status                # Last run + next review dates

Part of the Self-Evolving System (docs/architecture/self-evolving-system.md).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT, SCRIPTS_DIR
from _lib.output import StatusLine, print_json

# Lazy imports to avoid circular dependency issues
# project_health and agent_feedback are imported inside functions


# ─── Config ──────────────────────────────────────────────────────────────────

VENV_PYTHON = REPO_ROOT / ".venv" / "bin" / "python"
EVOLUTION_DIR = REPO_ROOT / "logs" / "evolution"
FEEDBACK_DIR = REPO_ROOT / "logs" / "feedback"
AI_COMMIT = REPO_ROOT / "scripts" / "ai_commit.sh"
TASKS_MD = REPO_ROOT / "docs" / "TASKS.md"


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _run_script(name: str, args: list[str] | None = None) -> tuple[int, str]:
    """Run a script from scripts/ dir."""
    cmd = [str(VENV_PYTHON), str(SCRIPTS_DIR / name)]
    if args:
        cmd.extend(args)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(REPO_ROOT),
        )
        return result.returncode, result.stdout + result.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return -1, str(e)


def _load_last_evolution() -> dict | None:
    """Load the most recent evolution report."""
    if not EVOLUTION_DIR.exists():
        return None
    reports = sorted(EVOLUTION_DIR.glob("evolution_*.json"), reverse=True)
    if not reports:
        return None
    try:
        return json.loads(reports[0].read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _save_evolution_report(report: dict) -> Path:
    """Save evolution report to logs/evolution/."""
    EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    filepath = EVOLUTION_DIR / f"evolution_{timestamp}.json"
    filepath.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return filepath


def _auto_commit(message: str) -> bool:
    """Auto-commit changes via ai_commit.sh."""
    if not AI_COMMIT.exists():
        StatusLine.warn("ai_commit.sh not found, skipping auto-commit")
        return False
    try:
        result = subprocess.run(
            ["bash", str(AI_COMMIT), message],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(REPO_ROOT),
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _append_tasks(tasks: list[str]) -> None:
    """Append auto-discovered tasks to TASKS.md."""
    if not tasks or not TASKS_MD.exists():
        return
    try:
        content = TASKS_MD.read_text(encoding="utf-8")
    except OSError:
        return

    # Find the "Auto-discovered" section or create one
    marker = "## Auto-Discovered (by evolve.py)"
    today = datetime.now().strftime("%Y-%m-%d")

    new_items = "\n".join(f"- [ ] {task} (discovered {today})" for task in tasks)

    if marker in content:
        # Append under existing section
        content = content.replace(marker, f"{marker}\n{new_items}")
    else:
        # Add new section at end
        content = content.rstrip() + f"\n\n{marker}\n{new_items}\n"

    TASKS_MD.write_text(content, encoding="utf-8")


# ─── Evolution Steps ─────────────────────────────────────────────────────────


def step_health_scan(fix: bool = False) -> dict:
    """Step 1: Run project health scan."""
    StatusLine.ok("Running health scan...")
    args = ["--json"]
    if fix:
        args.append("--fix")
    code, output = _run_script("project_health.py", args)

    try:
        health_data = json.loads(output)
    except json.JSONDecodeError:
        health_data = {"overall_score": 0, "error": "Failed to parse health output"}

    return {
        "step": "health_scan",
        "score": health_data.get("overall_score", 0),
        "total_issues": health_data.get("total_issues", 0),
        "fixes_applied": health_data.get("fixes_applied", 0),
        "categories": health_data.get("categories", {}),
    }


def step_sync_numbers(fix: bool = False) -> dict:
    """Step 2: Sync stale numbers in docs."""
    StatusLine.ok("Syncing numbers...")
    args = ["--fix"] if fix else []
    code, output = _run_script("sync_numbers.py", args)
    drift_count = output.count("UPDATED") + output.count("Fixed") + output.count("→")
    return {
        "step": "sync_numbers",
        "drift_found": drift_count,
        "fixed": fix and drift_count > 0,
    }


def step_regenerate_indexes(fix: bool = False) -> dict:
    """Step 3: Check if indexes need regeneration."""
    if not fix:
        return {"step": "regenerate_indexes", "skipped": True, "reason": "dry-run mode"}

    StatusLine.ok("Regenerating indexes...")
    code, output = _run_script("check_scripts_index.py")
    if code != 0:
        # Regenerate
        gen_script = SCRIPTS_DIR / "generate_all_indexes.sh"
        if gen_script.exists():
            subprocess.run(
                ["bash", str(gen_script)],
                capture_output=True,
                timeout=120,
                cwd=str(REPO_ROOT),
            )
            return {"step": "regenerate_indexes", "regenerated": True}
    return {"step": "regenerate_indexes", "up_to_date": True}


def step_process_feedback() -> dict:
    """Step 4: Analyze feedback patterns."""
    StatusLine.ok("Analyzing feedback...")

    if not FEEDBACK_DIR.exists():
        return {"step": "feedback_analysis", "items": 0, "recurring": []}

    code, output = _run_script("agent_feedback.py", ["stats", "--json"])
    try:
        stats = json.loads(output)
    except json.JSONDecodeError:
        stats = {}

    # Find recurring issues
    code2, output2 = _run_script("agent_feedback.py", ["pending", "--json"])
    recurring: list[str] = []
    try:
        pending_data = json.loads(output2)
        msg_counts: dict[str, int] = {}
        for item in pending_data.get("pending", []):
            msg = item.get("message", "")[:60].lower()
            msg_counts[msg] = msg_counts.get(msg, 0) + 1
        recurring = [msg for msg, count in msg_counts.items() if count >= 2]
    except json.JSONDecodeError:
        pass

    return {
        "step": "feedback_analysis",
        "total": stats.get("total_items", 0),
        "pending": stats.get("pending", 0),
        "resolution_rate": stats.get("resolution_rate", "N/A"),
        "recurring_issues": recurring,
    }


def step_check_instruction_drift() -> dict:
    """Step 5: Check agent instruction drift."""
    StatusLine.ok("Checking instruction drift...")
    code, output = _run_script("check_instruction_drift.py", ["--json"])
    try:
        drift_data = json.loads(output)
    except json.JSONDecodeError:
        drift_data = {"error": "Could not parse drift output"}

    return {
        "step": "instruction_drift",
        "drifted": code != 0,
        "details": drift_data,
    }


def step_archive_stale_docs(fix: bool = False) -> dict:
    """Step 6: Archive old docs from _active/."""
    active_dir = REPO_ROOT / "docs" / "_active"
    if not active_dir.exists():
        return {"step": "archive_stale", "stale_count": 0}

    stale: list[str] = []
    now = datetime.now()
    for md in active_dir.rglob("*.md"):
        mtime = datetime.fromtimestamp(md.stat().st_mtime)
        age = (now - mtime).days
        if age > 90:
            stale.append(f"{md.relative_to(REPO_ROOT)} ({age}d)")

    if stale and fix:
        StatusLine.ok(f"Archiving {len(stale)} stale doc(s)...")
        archive_script = SCRIPTS_DIR / "archive_old_files.sh"
        if archive_script.exists():
            subprocess.run(
                ["bash", str(archive_script)],
                capture_output=True,
                timeout=60,
                cwd=str(REPO_ROOT),
            )

    return {
        "step": "archive_stale",
        "stale_count": len(stale),
        "stale_files": stale[:10],  # Show first 10
        "archived": fix and bool(stale),
    }


def step_generate_todo_items(evolution_data: dict) -> list[str]:
    """Step 7: Generate TODO items from evolution findings."""
    todos: list[str] = []

    # From health issues
    health = evolution_data.get("health_scan", {})
    for cat_name, cat_data in health.get("categories", {}).items():
        for issue in cat_data.get("issues", []):
            if issue.get("severity") == "error" and not issue.get("fix_applied"):
                todos.append(f"[{cat_name}] {issue.get('message', 'Unknown issue')}")

    # From recurring feedback
    feedback = evolution_data.get("feedback_analysis", {})
    for recurring in feedback.get("recurring_issues", []):
        todos.append(f"[recurring feedback] {recurring}")

    # From instruction drift
    drift = evolution_data.get("instruction_drift", {})
    if drift.get("drifted"):
        todos.append(
            "[agents] Sync instruction drift between .github/instructions/ and .claude/rules/"
        )

    return todos[:10]  # Cap at 10


# ─── Review Modes ────────────────────────────────────────────────────────────


def review_weekly(fix: bool = False) -> dict:
    """Quick weekly review: numbers, links, feedback trends."""
    print("\n\033[1m\033[36m━━━ Weekly Review ━━━\033[0m\n")

    results = {
        "type": "weekly",
        "timestamp": datetime.now().isoformat(),
        "steps": {},
    }

    results["steps"]["numbers"] = step_sync_numbers(fix=fix)
    results["steps"]["health"] = step_health_scan(fix=fix)
    results["steps"]["feedback"] = step_process_feedback()

    return results


def review_monthly(fix: bool = False) -> dict:
    """Comprehensive monthly review: all categories + archive."""
    print("\n\033[1m\033[36m━━━ Monthly Review ━━━\033[0m\n")

    results = {
        "type": "monthly",
        "timestamp": datetime.now().isoformat(),
        "steps": {},
    }

    results["steps"]["health"] = step_health_scan(fix=fix)
    results["steps"]["numbers"] = step_sync_numbers(fix=fix)
    results["steps"]["indexes"] = step_regenerate_indexes(fix=fix)
    results["steps"]["feedback"] = step_process_feedback()
    results["steps"]["instruction_drift"] = step_check_instruction_drift()
    results["steps"]["archive"] = step_archive_stale_docs(fix=fix)

    # Generate TODOs
    todos = step_generate_todo_items(results["steps"])
    results["steps"]["todos_generated"] = todos
    if fix and todos:
        _append_tasks(todos)
        StatusLine.ok(f"Added {len(todos)} TODO items to TASKS.md")

    return results


# ─── Full Evolution Cycle ────────────────────────────────────────────────────


def run_evolution(fix: bool = False, report_only: bool = False) -> dict:
    """Run full evolution cycle."""
    print("\n\033[1m\033[36m━━━ Evolution Cycle ━━━\033[0m")
    print(f"  Mode: {'FIX' if fix else 'DRY-RUN'}")
    print()

    start = time.time()
    evolution = {
        "type": "full",
        "timestamp": datetime.now().isoformat(),
        "mode": "fix" if fix else "dry-run",
        "steps": {},
    }

    # Step 1: Health scan
    evolution["steps"]["health_scan"] = step_health_scan(fix=fix)
    score = evolution["steps"]["health_scan"]["score"]
    print(f"  Health Score: {score}/100")

    # Step 2: Sync numbers
    evolution["steps"]["sync_numbers"] = step_sync_numbers(fix=fix)

    # Step 3: Regenerate indexes
    evolution["steps"]["indexes"] = step_regenerate_indexes(fix=fix)

    # Step 4: Process feedback
    evolution["steps"]["feedback_analysis"] = step_process_feedback()

    # Step 5: Instruction drift
    evolution["steps"]["instruction_drift"] = step_check_instruction_drift()

    # Step 6: Archive stale docs
    evolution["steps"]["archive_stale"] = step_archive_stale_docs(fix=fix)

    # Step 7: Generate TODOs
    todos = step_generate_todo_items(evolution["steps"])
    evolution["steps"]["todos"] = todos

    # Calculate elapsed time
    elapsed = time.time() - start
    evolution["duration_seconds"] = round(elapsed, 1)

    # Save report
    report_path = _save_evolution_report(evolution)

    # Apply tasks
    if fix and todos:
        _append_tasks(todos)
        StatusLine.ok(f"Added {len(todos)} TODO items to TASKS.md")

    # Auto-commit if fixes were applied
    if fix:
        fixes = evolution["steps"]["health_scan"].get("fixes_applied", 0) + evolution[
            "steps"
        ]["sync_numbers"].get("drift_found", 0)
        if fixes > 0:
            StatusLine.ok(f"Auto-committing {fixes} fix(es)...")
            _auto_commit(f"chore: evolve - auto-fix {fixes} issue(s)")

    # Print summary
    _print_evolution_summary(evolution, report_path)

    return evolution


def _print_evolution_summary(evolution: dict, report_path: Path) -> None:
    """Print evolution summary."""
    print()
    print("\033[1m\033[36m━━━ Evolution Summary ━━━\033[0m")

    steps = evolution.get("steps", {})
    health = steps.get("health_scan", {})
    sync = steps.get("sync_numbers", {})
    feedback = steps.get("feedback_analysis", {})
    drift = steps.get("instruction_drift", {})
    archive = steps.get("archive_stale", {})
    todos = steps.get("todos", [])

    print(f"  Health Score:     {health.get('score', '?')}/100")
    print(f"  Issues Found:     {health.get('total_issues', 0)}")
    print(f"  Fixes Applied:    {health.get('fixes_applied', 0)}")
    print(f"  Number Drift:     {sync.get('drift_found', 0)}")
    print(f"  Pending Feedback: {feedback.get('pending', 0)}")
    print(f"  Recurring Issues: {len(feedback.get('recurring_issues', []))}")
    print(f"  Instruction Drift:{' YES ⚠️' if drift.get('drifted') else ' No ✅'}")
    print(f"  Stale Docs:       {archive.get('stale_count', 0)}")
    print(f"  TODOs Generated:  {len(todos)}")
    print(f"  Duration:         {evolution.get('duration_seconds', '?')}s")
    print(f"  Report:           {report_path.relative_to(REPO_ROOT)}")

    if todos:
        print("\n  Auto-Discovered TODOs:")
        for todo in todos[:5]:
            print(f"    → {todo}")

    mode = evolution.get("mode", "dry-run")
    if mode == "dry-run":
        print("\n  \033[1;33mThis was a dry run. Use --fix to apply changes.\033[0m")
    print()


def cmd_status(args: argparse.Namespace) -> int:
    """Show last evolution run and status."""
    last = _load_last_evolution()

    if not last:
        print("No evolution runs found yet.")
        print("  Run: ./run.sh evolve")
        return 0

    print()
    print("\033[1m\033[36m━━━ Evolution Status ━━━\033[0m")
    print(f"  Last Run:    {last.get('timestamp', 'unknown')}")
    print(f"  Type:        {last.get('type', 'unknown')}")
    print(f"  Mode:        {last.get('mode', 'unknown')}")

    # Health trend
    health_reports = (
        sorted(EVOLUTION_DIR.glob("health_*.json")) if EVOLUTION_DIR.exists() else []
    )
    if len(health_reports) >= 2:
        try:
            prev = json.loads(health_reports[-2].read_text(encoding="utf-8"))
            curr = json.loads(health_reports[-1].read_text(encoding="utf-8"))
            prev_score = prev.get("overall_score", 0)
            curr_score = curr.get("overall_score", 0)
            delta = curr_score - prev_score
            trend = "↑" if delta > 0 else ("↓" if delta < 0 else "→")
            print(f"  Health Trend: {prev_score} → {curr_score} {trend}")
        except (json.JSONDecodeError, OSError, IndexError):
            pass

    # Suggest next review
    last_date = last.get("timestamp", "")[:10]
    try:
        last_dt = datetime.strptime(last_date, "%Y-%m-%d")
        days_since = (datetime.now() - last_dt).days
        if days_since >= 30:
            print(
                f"\n  \033[1;33m⚠️  {days_since} days since last run. Monthly review recommended.\033[0m"
            )
            print("     Run: ./run.sh evolve --review monthly --fix")
        elif days_since >= 7:
            print(
                f"\n  \033[1;33m⚠️  {days_since} days since last run. Weekly review recommended.\033[0m"
            )
            print("     Run: ./run.sh evolve --review weekly --fix")
        else:
            print(f"\n  ✅ Last run was {days_since} day(s) ago. System is current.")
    except ValueError:
        pass

    print()
    return 0


# ─── CLI ─────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Self-evolution engine for structural_engineering_lib",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                         Full evolution cycle (dry-run)
  %(prog)s --fix                   Apply fixes and commit
  %(prog)s --review weekly         Quick weekly review
  %(prog)s --review monthly --fix  Monthly review with auto-fix
  %(prog)s --status                Last run info + recommendations
        """,
    )
    parser.add_argument(
        "--fix", action="store_true", help="Apply auto-fixes and commit"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate evolution report only (no fixes)",
    )
    parser.add_argument(
        "--review", choices=["weekly", "monthly"], help="Run periodic review"
    )
    parser.add_argument(
        "--status", action="store_true", help="Show last run and recommendations"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    if args.status:
        return cmd_status(args)

    if args.review:
        if args.review == "weekly":
            result = review_weekly(fix=args.fix)
        else:
            result = review_monthly(fix=args.fix)

        report_path = _save_evolution_report(result)
        if args.json:
            print_json(result)
        else:
            print(f"\n  Report saved: {report_path.relative_to(REPO_ROOT)}\n")
        return 0

    result = run_evolution(fix=args.fix, report_only=args.report)

    if args.json:
        print_json(result)

    return 0


if __name__ == "__main__":
    sys.exit(main())
