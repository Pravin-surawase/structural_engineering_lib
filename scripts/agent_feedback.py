#!/usr/bin/env python3
"""Agent feedback collection and analysis.

Agents log issues they encounter during sessions. Over time, patterns emerge
that drive systemic fixes — the feedback loop that makes the system self-evolving.

Usage:
    # Log feedback (at session end)
    python scripts/agent_feedback.py log --agent backend \
      --stale-doc "api.md had wrong param name" \
      --missing "No docs on batch endpoint" \
      --time-wasted "15min finding geometry hook"

    # Analyze patterns
    python scripts/agent_feedback.py summary              # Recent trends
    python scripts/agent_feedback.py pending               # Unresolved items
    python scripts/agent_feedback.py resolve <id>          # Mark resolved
    python scripts/agent_feedback.py stats                 # Aggregate stats

Part of the Self-Evolving System (docs/architecture/self-evolving-system.md).
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT
from _lib.output import StatusLine, print_json

# ─── Config ──────────────────────────────────────────────────────────────────

FEEDBACK_DIR = REPO_ROOT / "logs" / "feedback"
VALID_AGENTS = [
    "orchestrator",
    "backend",
    "frontend",
    "api-developer",
    "structural-engineer",
    "reviewer",
    "tester",
    "doc-master",
    "ops",
    "governance",
    "ui-designer",
]
FEEDBACK_CATEGORIES = [
    "stale-doc",
    "missing",
    "wrong-instruction",
    "time-wasted",
    "fix-applied",
    "suggestion",
]


# ─── Data ────────────────────────────────────────────────────────────────────


def _make_item(category: str, message: str, agent: str) -> dict:
    """Create a feedback item."""
    return {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "category": category,
        "message": message,
        "status": "pending",
    }


def _load_all_feedback() -> list[dict]:
    """Load all feedback items from all files."""
    items: list[dict] = []
    if not FEEDBACK_DIR.exists():
        return items
    for fb_file in sorted(FEEDBACK_DIR.glob("*.json")):
        try:
            data = json.loads(fb_file.read_text(encoding="utf-8"))
            for item in data.get("items", []):
                item["_file"] = str(fb_file.name)
                items.append(item)
        except (json.JSONDecodeError, OSError):
            continue
    return items


def _save_feedback_file(filepath: Path, data: dict) -> None:
    """Save a feedback file."""
    filepath.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


# ─── Commands ────────────────────────────────────────────────────────────────


def cmd_log(args: argparse.Namespace) -> int:
    """Log feedback items from current session."""
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)

    agent = args.agent
    items: list[dict] = []

    # Collect all feedback categories from args
    for category in FEEDBACK_CATEGORIES:
        attr = category.replace("-", "_")
        messages = getattr(args, attr, None)
        if messages:
            for msg in messages:
                items.append(_make_item(category, msg, agent))

    if not items:
        StatusLine.warn("No feedback items provided. Use --stale-doc, --missing, etc.")
        return 1

    # Save to dated file
    date_str = datetime.now().strftime("%Y-%m-%d")
    session_id = str(uuid.uuid4())[:8]
    filename = f"{date_str}_{agent}_{session_id}.json"
    filepath = FEEDBACK_DIR / filename

    data = {
        "session_date": date_str,
        "agent": agent,
        "created": datetime.now().isoformat(),
        "items": items,
    }
    _save_feedback_file(filepath, data)

    StatusLine.ok(f"Logged {len(items)} feedback item(s) → logs/feedback/{filename}")
    for item in items:
        print(f"  [{item['category']}] {item['message']}")

    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    """Show feedback summary and trends."""
    items = _load_all_feedback()
    if not items:
        StatusLine.ok("No feedback items found. System is clean!")
        return 0

    # Group by status
    pending = [i for i in items if i.get("status") != "resolved"]
    resolved = [i for i in items if i.get("status") == "resolved"]

    # Group by category
    by_category: dict[str, int] = {}
    for item in items:
        cat = item.get("category", "unknown")
        by_category[cat] = by_category.get(cat, 0) + 1

    # Group by agent
    by_agent: dict[str, int] = {}
    for item in items:
        agent = item.get("agent", "unknown")
        by_agent[agent] = by_agent.get(agent, 0) + 1

    # Find recurring issues (similar messages)
    msg_counts: dict[str, int] = {}
    for item in pending:
        # Normalize message for grouping
        msg = item.get("message", "")[:60].lower().strip()
        msg_counts[msg] = msg_counts.get(msg, 0) + 1
    recurring = {k: v for k, v in msg_counts.items() if v >= 2}

    if args.json:
        print_json(
            {
                "total": len(items),
                "pending": len(pending),
                "resolved": len(resolved),
                "by_category": by_category,
                "by_agent": by_agent,
                "recurring_count": len(recurring),
            }
        )
        return 0

    # Human output
    print()
    print("\033[1m\033[36m━━━ Feedback Summary ━━━\033[0m")
    print(
        f"  Total: {len(items)} | Pending: {len(pending)} | Resolved: {len(resolved)}"
    )
    print()

    if by_category:
        print("  By Category:")
        for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
            bar = "█" * min(count, 20)
            print(f"    {cat:20s} {count:3d} {bar}")
        print()

    if by_agent:
        print("  By Agent:")
        for agent, count in sorted(by_agent.items(), key=lambda x: -x[1]):
            print(f"    {agent:20s} {count:3d}")
        print()

    if recurring:
        print("  \033[1;33mRecurring Issues (need systemic fix):\033[0m")
        for msg, count in sorted(recurring.items(), key=lambda x: -x[1])[:5]:
            print(f"    [{count}x] {msg}")
        print()

    # Recent items (last 5)
    recent = sorted(pending, key=lambda x: x.get("timestamp", ""), reverse=True)[:5]
    if recent:
        print("  Recent Pending:")
        for item in recent:
            date = item.get("timestamp", "")[:10]
            print(
                f"    {date} [{item.get('category', '?'):15s}] "
                f"{item.get('message', '')[:60]}"
            )
        print()

    return 0


def cmd_pending(args: argparse.Namespace) -> int:
    """List pending (unresolved) feedback items."""
    items = _load_all_feedback()
    pending = [i for i in items if i.get("status") != "resolved"]

    if args.brief:
        if pending:
            print(f"⚠️  {len(pending)} pending feedback item(s)")
        else:
            print("✅ No pending feedback")
        return 0

    if not pending:
        StatusLine.ok("No pending feedback items")
        return 0

    if args.json:
        print_json({"pending": pending})
        return 0

    print(f"\n\033[1mPending Feedback ({len(pending)} items):\033[0m\n")
    for item in sorted(pending, key=lambda x: x.get("timestamp", ""), reverse=True):
        date = item.get("timestamp", "")[:10]
        print(
            f"  {item.get('id', '?'):8s} {date} [{item.get('agent', '?'):15s}] "
            f"[{item.get('category', '?'):15s}] {item.get('message', '')}"
        )
    print()
    print("  \033[2mResolve with: ./run.sh feedback resolve <id>\033[0m\n")
    return 0


def cmd_resolve(args: argparse.Namespace) -> int:
    """Mark a feedback item as resolved."""
    target_id = args.id
    found = False

    if not FEEDBACK_DIR.exists():
        StatusLine.fail(f"Feedback item {target_id} not found")
        return 1

    for fb_file in FEEDBACK_DIR.glob("*.json"):
        try:
            data = json.loads(fb_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        modified = False
        for item in data.get("items", []):
            if item.get("id") == target_id:
                item["status"] = "resolved"
                item["resolved_at"] = datetime.now().isoformat()
                modified = True
                found = True
                break

        if modified:
            _save_feedback_file(fb_file, data)
            StatusLine.ok(f"Resolved feedback item: {target_id}")
            break

    if not found:
        StatusLine.fail(f"Feedback item {target_id} not found")
        return 1

    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Show aggregate feedback statistics."""
    items = _load_all_feedback()

    if not items:
        print("No feedback data yet.")
        return 0

    # Time analysis
    dates = [i.get("timestamp", "")[:10] for i in items if i.get("timestamp")]
    unique_dates = sorted(set(dates))

    # Resolution rate
    resolved = sum(1 for i in items if i.get("status") == "resolved")
    resolution_rate = (resolved / len(items) * 100) if items else 0

    # Top issues by category
    cat_counts: dict[str, int] = {}
    for item in items:
        cat = item.get("category", "unknown")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    stats = {
        "total_items": len(items),
        "resolved": resolved,
        "pending": len(items) - resolved,
        "resolution_rate": f"{resolution_rate:.0f}%",
        "date_range": (
            f"{unique_dates[0]} to {unique_dates[-1]}" if unique_dates else "N/A"
        ),
        "sessions_with_feedback": len(unique_dates),
        "top_category": max(cat_counts, key=cat_counts.get) if cat_counts else "N/A",
        "agents_reporting": len(set(i.get("agent", "") for i in items)),
    }

    if args.json:
        print_json(stats)
    else:
        print()
        print("\033[1m\033[36m━━━ Feedback Statistics ━━━\033[0m")
        for key, val in stats.items():
            print(f"  {key.replace('_', ' ').title():25s} {val}")
        print()

    return 0


# ─── CLI ─────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Agent feedback collection and analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", help="Command to run")

    # log
    p_log = sub.add_parser("log", help="Log feedback from session")
    p_log.add_argument(
        "--agent",
        required=True,
        choices=VALID_AGENTS,
        help="Agent that encountered the issue",
    )
    p_log.add_argument(
        "--stale-doc",
        dest="stale_doc",
        action="append",
        help="Doc with stale/wrong info",
    )
    p_log.add_argument(
        "--missing", action="append", help="Missing documentation or info"
    )
    p_log.add_argument(
        "--wrong-instruction",
        dest="wrong_instruction",
        action="append",
        help="Incorrect agent instruction",
    )
    p_log.add_argument(
        "--time-wasted",
        dest="time_wasted",
        action="append",
        help="Time lost due to info gap",
    )
    p_log.add_argument(
        "--fix-applied",
        dest="fix_applied",
        action="append",
        help="Fix the agent applied",
    )
    p_log.add_argument("--suggestion", action="append", help="Improvement suggestion")

    # summary
    p_summary = sub.add_parser("summary", help="Show feedback summary")
    p_summary.add_argument("--json", action="store_true")

    # pending
    p_pending = sub.add_parser("pending", help="List unresolved items")
    p_pending.add_argument("--brief", action="store_true", help="One-line summary")
    p_pending.add_argument("--json", action="store_true")

    # resolve
    p_resolve = sub.add_parser("resolve", help="Resolve a feedback item")
    p_resolve.add_argument("id", help="Feedback item ID to resolve")

    # stats
    p_stats = sub.add_parser("stats", help="Aggregate statistics")
    p_stats.add_argument("--json", action="store_true")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1

    cmd_map = {
        "log": cmd_log,
        "summary": cmd_summary,
        "pending": cmd_pending,
        "resolve": cmd_resolve,
        "stats": cmd_stats,
    }
    return cmd_map[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
