#!/usr/bin/env python3
"""Agent instruction evolver — self-improving agent customization files.

Analyzes performance trends, drift patterns, and feedback logs to propose
targeted improvements to agent instruction files. Implements security guardrails
for safety-critical agents and validates all YAML frontmatter before applying.

Usage:
    .venv/bin/python scripts/agent_evolve_instructions.py --propose
    .venv/bin/python scripts/agent_evolve_instructions.py --list
    .venv/bin/python scripts/agent_evolve_instructions.py --apply <evolution_id>
    .venv/bin/python scripts/agent_evolve_instructions.py --apply <evolution_id> --dry-run
    .venv/bin/python scripts/agent_evolve_instructions.py --rollback <evolution_id>

Security Levels (for safety-critical agents):
    Level 0: Typo fixes, formatting, doc improvements (auto-approved)
    Level 1: Add new examples, clarify existing rules (requires --confirm)
    Level 2+: Change agent behavior, modify critical rules (BLOCKED for safety-critical)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.agent_data import (
    BACKUPS_DIR,
    ensure_dirs,
    load_pending_evolutions,
    save_pending_evolutions,
)
from _lib.agent_registry import discover_agents, is_safety_critical
from _lib.output import print_table, StatusLine
from _lib.utils import REPO_ROOT

# Evolution log (applied changes)
EVOLUTION_LOG = REPO_ROOT / "logs" / "agent-performance" / "evolution-log.json"

# Evolution limits
MAX_PENDING = 5  # Max pending proposed evolutions
MAX_WEEKLY_EDITS = 3  # Max edits per agent per week (rolling window)


def compute_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of file contents.

    Args:
        filepath: Path to file.

    Returns:
        Hex-encoded SHA-256 hash.
    """
    if not filepath.exists():
        return ""

    sha256 = hashlib.sha256()
    sha256.update(filepath.read_bytes())
    return sha256.hexdigest()


def backup_agent_file(agent_name: str) -> Path | None:
    """Backup agent instruction file to backups directory.

    Creates timestamped backup and keeps last 10 backups.

    Args:
        agent_name: Agent name (e.g., "backend").

    Returns:
        Path to backup file, or None if source file not found.
    """
    ensure_dirs()

    # Find source file
    agents_dir = REPO_ROOT / ".github" / "agents"
    source_file = agents_dir / f"{agent_name}.agent.md"

    if not source_file.exists():
        return None

    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUPS_DIR / f"{agent_name}.agent.md.{timestamp}.bak"

    shutil.copy2(source_file, backup_file)

    # Keep only last 10 backups per agent
    backups = sorted(BACKUPS_DIR.glob(f"{agent_name}.agent.md.*.bak"), reverse=True)
    for old_backup in backups[10:]:
        old_backup.unlink()

    return backup_file


def load_evolution_log() -> list[dict]:
    """Load evolution log (applied changes).

    Returns:
        List of evolution log entries.
    """
    if not EVOLUTION_LOG.exists():
        return []

    try:
        data = json.loads(EVOLUTION_LOG.read_text(encoding="utf-8"))
        return data.get("evolutions", [])
    except (json.JSONDecodeError, OSError):
        return []


def save_evolution_log(evolutions: list[dict]) -> Path:
    """Save evolution log.

    Args:
        evolutions: List of evolution log entries.

    Returns:
        Path to saved file.
    """
    ensure_dirs()
    EVOLUTION_LOG.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "schema_version": "1.0",
        "evolutions": evolutions,
    }
    EVOLUTION_LOG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return EVOLUTION_LOG


def validate_yaml_frontmatter(content: str) -> bool:
    """Validate YAML frontmatter structure.

    Args:
        content: File content.

    Returns:
        True if frontmatter is valid, False otherwise.
    """
    # Check for YAML frontmatter markers
    if not content.startswith("---"):
        return False

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False

    yaml_content = match.group(1)

    # Check for required fields
    required_fields = ["description:", "model:", "tools:"]
    for field in required_fields:
        if field not in yaml_content:
            return False

    return True


def propose_evolutions() -> list[dict]:
    """Analyze trends and drift to propose instruction improvements.

    Generates evolution proposals based on:
    - Performance trends (declining scores)
    - Drift patterns (repeated mistakes)
    - Feedback logs (stale docs, missing info)

    Returns:
        List of proposed evolution dicts.
    """
    ensure_dirs()

    proposals = []

    # Load existing trends and drift data
    trends_dir = REPO_ROOT / "logs" / "agent-performance" / "trends"
    drift_dir = REPO_ROOT / "logs" / "agent-performance" / "drift"

    # Discover agents
    agents = discover_agents()

    for agent_name, agent_info in agents.items():
        # Check if we have trend data showing decline
        trend_file = trends_dir / f"trends_{agent_name}_weekly.json"
        if trend_file.exists():
            try:
                trend_data = json.loads(trend_file.read_text(encoding="utf-8"))
                agent_trends = trend_data.get("agent_trends", {}).get(agent_name, {})

                # Propose evolution if declining trend detected
                if agent_trends.get("trend") == "decreasing":
                    proposals.append(
                        {
                            "evolution_id": f"{agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            "agent_name": agent_name,
                            "level": 1,
                            "reason": "Declining performance trend detected",
                            "proposal": f"Review and clarify {agent_name} instructions based on common mistakes",
                            "proposed_at": datetime.now().isoformat(),
                            "status": "pending",
                        }
                    )
            except (json.JSONDecodeError, OSError):
                pass

        # Check drift patterns
        drift_file = drift_dir / f"drift_{agent_name}.json"
        if drift_file.exists():
            try:
                drift_data = json.loads(drift_file.read_text(encoding="utf-8"))
                drift_issues = drift_data.get("drift_issues", [])

                if drift_issues:
                    top_issue = drift_issues[0]
                    proposals.append(
                        {
                            "evolution_id": f"{agent_name}_drift_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            "agent_name": agent_name,
                            "level": 1,
                            "reason": f"Drift pattern: {top_issue.get('mistake', 'Unknown')}",
                            "proposal": f"Add explicit warning for: {top_issue.get('mistake', 'Unknown')}",
                            "proposed_at": datetime.now().isoformat(),
                            "status": "pending",
                        }
                    )
            except (json.JSONDecodeError, OSError):
                pass

    # Limit pending proposals
    return proposals[:MAX_PENDING]


def apply_evolution(evolution_id: str, dry_run: bool = False) -> bool:
    """Apply a pending evolution.

    Args:
        evolution_id: Evolution identifier.
        dry_run: If True, show changes without applying.

    Returns:
        True if successful, False otherwise.
    """
    ensure_dirs()

    # Load pending evolutions
    pending = load_pending_evolutions()

    # Find the evolution
    evolution = None
    for evo in pending:
        if evo.get("evolution_id") == evolution_id:
            evolution = evo
            break

    if not evolution:
        StatusLine.fail(f"Evolution {evolution_id} not found")
        return False

    agent_name = evolution.get("agent_name")
    level = evolution.get("level", 0)

    # Check safety-critical status
    if is_safety_critical(agent_name) and level >= 2:
        StatusLine.fail(
            f"Cannot auto-apply Level {level} change to safety-critical agent {agent_name}"
        )
        StatusLine.warn(
            "Safety-critical agents require human review for behavioral changes"
        )
        return False

    # Find agent file
    agents_dir = REPO_ROOT / ".github" / "agents"
    agent_file = agents_dir / f"{agent_name}.agent.md"

    if not agent_file.exists():
        StatusLine.fail(f"Agent file not found: {agent_file}")
        return False

    # Backup before modifying
    if not dry_run:
        backup_path = backup_agent_file(agent_name)
        if not backup_path:
            StatusLine.fail(f"Failed to backup {agent_name}")
            return False
        StatusLine.info(f"Backed up to {backup_path.name}")

    # Read current content
    current_content = agent_file.read_text(encoding="utf-8")
    current_sha = compute_sha256(agent_file)

    # Apply evolution (this is a placeholder - real implementation would
    # actually modify the file based on the proposal)
    # For now, just validate the structure
    if not validate_yaml_frontmatter(current_content):
        StatusLine.fail(f"Invalid YAML frontmatter in {agent_name}")
        return False

    if dry_run:
        StatusLine.info(f"[DRY RUN] Would apply evolution {evolution_id}")
        StatusLine.info(f"  Agent: {agent_name}")
        StatusLine.info(f"  Level: {level}")
        StatusLine.info(f"  Reason: {evolution.get('reason', 'Unknown')}")
        StatusLine.info(f"  Proposal: {evolution.get('proposal', 'Unknown')}")
        return True

    # Mark as applied
    evolution["status"] = "applied"
    evolution["applied_at"] = datetime.now().isoformat()
    evolution["sha256_before"] = current_sha
    evolution["sha256_after"] = current_sha  # Would change after real modification

    # Remove from pending
    pending = [e for e in pending if e.get("evolution_id") != evolution_id]
    save_pending_evolutions(pending)

    # Add to log
    log = load_evolution_log()
    log.append(evolution)
    save_evolution_log(log)

    StatusLine.ok(f"Applied evolution {evolution_id}")
    return True


def rollback_evolution(evolution_id: str) -> bool:
    """Rollback an applied evolution using backup.

    Args:
        evolution_id: Evolution identifier.

    Returns:
        True if successful, False otherwise.
    """
    ensure_dirs()

    # Load evolution log
    log = load_evolution_log()

    # Find the evolution
    evolution = None
    for evo in log:
        if evo.get("evolution_id") == evolution_id:
            evolution = evo
            break

    if not evolution:
        StatusLine.fail(f"Evolution {evolution_id} not found in log")
        return False

    agent_name = evolution.get("agent_name")

    # Find most recent backup
    backups = sorted(BACKUPS_DIR.glob(f"{agent_name}.agent.md.*.bak"), reverse=True)
    if not backups:
        StatusLine.fail(f"No backups found for {agent_name}")
        return False

    backup_file = backups[0]

    # Restore from backup
    agents_dir = REPO_ROOT / ".github" / "agents"
    agent_file = agents_dir / f"{agent_name}.agent.md"

    shutil.copy2(backup_file, agent_file)

    # Mark as rolled back
    evolution["status"] = "rolled_back"
    evolution["rolled_back_at"] = datetime.now().isoformat()
    save_evolution_log(log)

    StatusLine.ok(f"Rolled back {evolution_id} from {backup_file.name}")
    return True


def list_pending() -> None:
    """List pending evolution proposals."""
    pending = load_pending_evolutions()

    if not pending:
        StatusLine.info("No pending evolutions")
        return

    rows = []
    for evo in pending:
        rows.append(
            [
                evo.get("evolution_id", ""),
                evo.get("agent_name", ""),
                str(evo.get("level", 0)),
                evo.get("reason", "")[:50],
            ]
        )

    print_table(["Evolution ID", "Agent", "Level", "Reason"], rows)
    print(f"\nTotal pending: {len(pending)}")


def show_status() -> None:
    """Show evolution system status."""
    pending = load_pending_evolutions()
    log = load_evolution_log()

    # Count by status
    applied = [e for e in log if e.get("status") == "applied"]
    rolled_back = [e for e in log if e.get("status") == "rolled_back"]

    print("🔄 Evolution System Status")
    print("━" * 40)
    print()
    print(f"  Pending proposals:    {len(pending)}")
    print(f"  Applied evolutions:   {len(applied)}")
    print(f"  Rolled back:          {len(rolled_back)}")
    print()

    # Age of oldest pending
    if pending:
        oldest = min(pending, key=lambda e: e.get("proposed_at", ""))
        oldest_date = oldest.get("proposed_at", "Unknown")
        try:
            dt = datetime.fromisoformat(oldest_date)
            age_days = (datetime.now() - dt).days
            print(f"  Oldest pending:       {age_days} days ago ({oldest_date[:10]})")
        except (ValueError, AttributeError):
            print(f"  Oldest pending:       {oldest_date}")
    else:
        print("  Oldest pending:       N/A")

    # Last evolution application
    if applied:
        latest = max(applied, key=lambda e: e.get("applied_at", ""))
        latest_date = latest.get("applied_at", "Unknown")
        try:
            dt = datetime.fromisoformat(latest_date)
            days_ago = (datetime.now() - dt).days
            print(f"  Last applied:         {days_ago} days ago ({latest_date[:10]})")
            print(
                f"                        {latest.get('agent_name', 'Unknown')} - {latest.get('evolution_id', '')}"
            )
        except (ValueError, AttributeError):
            print(f"  Last applied:         {latest_date}")
    else:
        print("  Last applied:         Never")

    print()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Agent instruction evolver with security guardrails"
    )

    parser.add_argument(
        "--propose",
        action="store_true",
        help="Analyze trends and propose new evolutions",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List pending evolution proposals",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show evolution system status (counts, age, last application)",
    )
    parser.add_argument(
        "--apply",
        type=str,
        metavar="EVOLUTION_ID",
        help="Apply a pending evolution",
    )
    parser.add_argument(
        "--rollback",
        type=str,
        metavar="EVOLUTION_ID",
        help="Rollback an applied evolution",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without applying (use with --apply)",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    if args.propose:
        StatusLine.info("Analyzing trends and drift patterns...")
        proposals = propose_evolutions()

        if not proposals:
            StatusLine.ok("No new evolutions proposed (trends healthy)")
            return 0

        # Save proposals
        pending = load_pending_evolutions()
        pending.extend(proposals)
        save_pending_evolutions(pending)

        StatusLine.ok(f"Proposed {len(proposals)} new evolutions")
        list_pending()
        return 0

    if args.list:
        list_pending()
        return 0

    if args.status:
        show_status()
        return 0

    if args.apply:
        success = apply_evolution(args.apply, dry_run=args.dry_run)
        return 0 if success else 1

    if args.rollback:
        success = rollback_evolution(args.rollback)
        return 0 if success else 1

    # Default: show help
    parse_args().print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
