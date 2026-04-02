#!/usr/bin/env python3
"""
JSON-based session state persistence for AI agent sessions.

Provides state storage, retrieval, and resume context for multi-step agent workflows.

USAGE:
    python scripts/session_store.py new --agent backend --task TASK-856 --desc "Create session store"
    python scripts/session_store.py list [--last N]
    python scripts/session_store.py show <session_id>
    python scripts/session_store.py end [session_id] [--notes "summary"]
    python scripts/session_store.py resume <session_id>
    python scripts/session_store.py active
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.output import StatusLine, print_json
from _lib.utils import REPO_ROOT

SESSIONS_DIR = REPO_ROOT / "logs" / "sessions"


def _validate_id(id_value: str, id_type: str = "session_id") -> None:
    """Validate ID to prevent path traversal attacks.

    Args:
        id_value: The ID to validate
        id_type: Type of ID for error messages (e.g., "session_id", "pipeline_id")

    Raises:
        ValueError: If ID contains invalid characters
    """
    if not re.match(r"^[A-Za-z0-9_-]+$", id_value):
        raise ValueError(
            f"Invalid {id_type}: '{id_value}'. "
            f"Only alphanumeric characters, underscores, and hyphens are allowed."
        )


@dataclass
class SessionState:
    """AI agent session state with pipeline tracking."""

    session_id: str
    agent: str
    task_id: str
    task_description: str
    pipeline_step: str  # PLAN|GATHER|EXECUTE|TEST|VERIFY|DOCUMENT|COMMIT
    files_changed: list[str] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    ended_at: Optional[str] = None
    duration_min: Optional[float] = None
    scripts_run: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> SessionState:
        """Load from JSON dict."""
        return cls(**data)


def _ensure_sessions_dir() -> None:
    """Create logs/sessions/ directory if it doesn't exist."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    gitkeep = SESSIONS_DIR / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()


def generate_session_id() -> str:
    """Auto-increment from last saved session (S001, S002, etc.)."""
    _ensure_sessions_dir()

    existing = sorted(SESSIONS_DIR.glob("S*.json"))
    if not existing:
        return "S001"

    # Extract last session number
    last_session = existing[-1].stem  # e.g., "S005"
    try:
        last_num = int(last_session[1:])  # Extract "005" -> 5
        return f"S{last_num + 1:03d}"
    except (ValueError, IndexError):
        return "S001"


def save_session(state: SessionState) -> Path:
    """Write session state to logs/sessions/{session_id}.json."""
    _validate_id(state.session_id, "session_id")
    _ensure_sessions_dir()

    session_file = SESSIONS_DIR / f"{state.session_id}.json"
    with session_file.open("w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)

    return session_file


def load_session(session_id: str) -> SessionState:
    """Read session state from JSON file."""
    _validate_id(session_id, "session_id")
    session_file = SESSIONS_DIR / f"{session_id}.json"
    if not session_file.exists():
        raise FileNotFoundError(f"Session {session_id} not found at {session_file}")

    with session_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return SessionState.from_dict(data)


def list_sessions(last_n: int = 10) -> list[SessionState]:
    """List recent sessions, sorted by start time."""
    _ensure_sessions_dir()

    session_files = sorted(SESSIONS_DIR.glob("S*.json"), reverse=True)[:last_n]
    sessions = []

    for session_file in session_files:
        try:
            sessions.append(load_session(session_file.stem))
        except Exception as e:
            StatusLine.warn(f"Failed to load {session_file.name}: {e}")

    return sessions


def get_active_session() -> Optional[SessionState]:
    """Find the most recent session without ended_at."""
    _ensure_sessions_dir()

    session_files = sorted(SESSIONS_DIR.glob("S*.json"), reverse=True)

    for session_file in session_files:
        try:
            session = load_session(session_file.stem)
            if session.ended_at is None:
                return session
        except Exception:
            continue

    return None


def end_session(session_id: Optional[str] = None, notes: str = "") -> SessionState:
    """Set ended_at and calculate duration for a session."""
    if session_id is None:
        # End the active session
        session = get_active_session()
        if session is None:
            raise ValueError("No active session found to end")
    else:
        session = load_session(session_id)

    if session.ended_at is not None:
        StatusLine.warn(
            f"Session {session.session_id} was already ended at {session.ended_at}"
        )
        return session

    # Set end time and calculate duration
    session.ended_at = datetime.now().isoformat()
    start_dt = datetime.fromisoformat(session.started_at)
    end_dt = datetime.fromisoformat(session.ended_at)
    session.duration_min = (end_dt - start_dt).total_seconds() / 60.0

    # Append notes if provided
    if notes:
        session.notes = f"{session.notes}\n{notes}".strip()

    save_session(session)
    return session


def resume_context(session_id: str) -> str:
    """Generate a context prompt for resuming work."""
    session = load_session(session_id)

    lines = [
        f"## Session Resume — {session.session_id}",
        f"- Agent: {session.agent}",
        f"- Task: {session.task_id} — {session.task_description}",
        f"- Pipeline Step: {session.pipeline_step}",
    ]

    if session.files_changed:
        lines.append(f"- Files Changed: {', '.join(session.files_changed)}")

    lines.append(f"- Started: {session.started_at}")

    if session.ended_at:
        lines.append(f"- Ended: {session.ended_at} ({session.duration_min:.1f} min)")
    else:
        lines.append("- Status: ACTIVE (not yet completed)")

    if session.scripts_run:
        lines.append(f"- Scripts Run: {', '.join(session.scripts_run)}")

    if session.notes:
        lines.append(f"- Notes: {session.notes}")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# CLI Interface
# ─────────────────────────────────────────────────────────────────────────────


def cmd_new(args: argparse.Namespace) -> None:
    """Create a new session."""
    session_id = generate_session_id()
    state = SessionState(
        session_id=session_id,
        agent=args.agent,
        task_id=args.task,
        task_description=args.desc,
        pipeline_step=args.step,
    )

    session_file = save_session(state)
    StatusLine.ok(f"Created session {session_id} at {session_file}")
    print(f"\nSession ID: {session_id}")
    print(f"Agent: {args.agent}")
    print(f"Task: {args.task} — {args.desc}")
    print(f"Pipeline Step: {args.step}")


def cmd_list(args: argparse.Namespace) -> None:
    """List recent sessions."""
    sessions = list_sessions(last_n=args.last)

    if not sessions:
        StatusLine.warn("No sessions found")
        return

    print(
        f"\n{'Session':<8} {'Agent':<15} {'Task':<12} {'Step':<10} {'Status':<10} {'Started':<20}"
    )
    print("─" * 90)

    for session in sessions:
        status = "ACTIVE" if session.ended_at is None else "COMPLETE"
        started = session.started_at[:19].replace("T", " ")  # Trim microseconds

        print(
            f"{session.session_id:<8} {session.agent:<15} {session.task_id:<12} "
            f"{session.pipeline_step:<10} {status:<10} {started:<20}"
        )


def cmd_show(args: argparse.Namespace) -> None:
    """Show full details of a session."""
    try:
        session = load_session(args.session_id)
        print_json(session.to_dict())
    except FileNotFoundError as e:
        StatusLine.fail(str(e))
        sys.exit(1)


def cmd_end(args: argparse.Namespace) -> None:
    """End a session (active or specified)."""
    try:
        session = end_session(session_id=args.session_id, notes=args.notes)
        StatusLine.ok(
            f"Ended session {session.session_id} ({session.duration_min:.1f} min)"
        )
        print(f"\nTask: {session.task_id} — {session.task_description}")
        print(f"Files Changed: {len(session.files_changed)}")
        if session.notes:
            print(f"Notes: {session.notes}")
    except (FileNotFoundError, ValueError) as e:
        StatusLine.fail(str(e))
        sys.exit(1)


def cmd_resume(args: argparse.Namespace) -> None:
    """Generate resume context for a session."""
    try:
        context = resume_context(args.session_id)
        print(context)
    except FileNotFoundError as e:
        StatusLine.fail(str(e))
        sys.exit(1)


def cmd_active(args: argparse.Namespace) -> None:
    """Show the active session."""
    session = get_active_session()

    if session is None:
        StatusLine.warn("No active session")
        return

    StatusLine.ok(f"Active session: {session.session_id}")
    print(f"\nAgent: {session.agent}")
    print(f"Task: {session.task_id} — {session.task_description}")
    print(f"Pipeline Step: {session.pipeline_step}")
    print(f"Started: {session.started_at}")
    print(f"Files Changed: {len(session.files_changed)}")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="JSON-based session state persistence for AI agent sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # new
    new_parser = subparsers.add_parser("new", help="Create a new session")
    new_parser.add_argument("--agent", required=True, help="Agent name (e.g., backend)")
    new_parser.add_argument("--task", required=True, help="Task ID (e.g., TASK-856)")
    new_parser.add_argument("--desc", required=True, help="Task description")
    new_parser.add_argument(
        "--step", default="PLAN", help="Pipeline step (default: PLAN)"
    )
    new_parser.set_defaults(func=cmd_new)

    # list
    list_parser = subparsers.add_parser("list", help="List recent sessions")
    list_parser.add_argument(
        "--last", type=int, default=10, help="Number of sessions to show"
    )
    list_parser.set_defaults(func=cmd_list)

    # show
    show_parser = subparsers.add_parser("show", help="Show full details of a session")
    show_parser.add_argument("session_id", help="Session ID (e.g., S001)")
    show_parser.set_defaults(func=cmd_show)

    # end
    end_parser = subparsers.add_parser("end", help="End a session")
    end_parser.add_argument(
        "session_id", nargs="?", help="Session ID (defaults to active)"
    )
    end_parser.add_argument("--notes", default="", help="Summary notes")
    end_parser.set_defaults(func=cmd_end)

    # resume
    resume_parser = subparsers.add_parser("resume", help="Generate resume context")
    resume_parser.add_argument("session_id", help="Session ID (e.g., S001)")
    resume_parser.set_defaults(func=cmd_resume)

    # active
    active_parser = subparsers.add_parser("active", help="Show the active session")
    active_parser.set_defaults(func=cmd_active)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
