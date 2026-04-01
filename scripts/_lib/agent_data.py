"""Data I/O for agent-performance directory.

Handles reading/writing session data, trends, scorecards, and evolution logs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .utils import REPO_ROOT

# Schema version for data files
SCHEMA_VERSION = "1.1"

# Performance data paths
PERFORMANCE_DIR = REPO_ROOT / "logs" / "agent-performance"
SESSIONS_DIR = PERFORMANCE_DIR / "sessions"
TRENDS_DIR = PERFORMANCE_DIR / "trends"
DRIFT_DIR = PERFORMANCE_DIR / "drift"
BACKUPS_DIR = PERFORMANCE_DIR / "backups"
PAPER_DIR = PERFORMANCE_DIR / "paper-export"


def ensure_dirs() -> None:
    """Create all necessary subdirectories if they don't exist."""
    for directory in [
        PERFORMANCE_DIR,
        SESSIONS_DIR,
        TRENDS_DIR,
        DRIFT_DIR,
        BACKUPS_DIR,
        PAPER_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)


def save_session(session_id: str, data: dict[str, Any]) -> Path:
    """Save session data to sessions directory.

    Args:
        session_id: Session identifier (e.g., "2026-04-01T14:30").
        data: Session data dict.

    Returns:
        Path to saved file.
    """
    ensure_dirs()
    filepath = SESSIONS_DIR / f"{session_id}.json"
    filepath.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return filepath


def load_session(session_id: str) -> dict[str, Any] | None:
    """Load session data from sessions directory.

    Args:
        session_id: Session identifier.

    Returns:
        Session data dict, or None if not found.
    """
    filepath = SESSIONS_DIR / f"{session_id}.json"
    if not filepath.exists():
        return None

    try:
        return json.loads(filepath.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def list_sessions() -> list[str]:
    """List all session IDs, sorted chronologically.

    Returns:
        Sorted list of session IDs.
    """
    if not SESSIONS_DIR.exists():
        return []

    session_files = sorted(SESSIONS_DIR.glob("*.json"))
    return [f.stem for f in session_files]


def save_scorecard_index(data: dict[str, Any]) -> Path:
    """Save scorecard index (latest score per agent).

    Args:
        data: Scorecard index dict.

    Returns:
        Path to saved file.
    """
    ensure_dirs()
    filepath = PERFORMANCE_DIR / "scorecard_index.json"
    filepath.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return filepath


def load_scorecard_index() -> dict[str, Any]:
    """Load scorecard index.

    Returns:
        Scorecard index dict, empty if not found.
    """
    filepath = PERFORMANCE_DIR / "scorecard_index.json"
    if not filepath.exists():
        return {}

    try:
        return json.loads(filepath.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def load_pending_evolutions() -> list[dict[str, Any]]:
    """Load pending evolution proposals.

    Returns:
        List of pending evolution dicts.
    """
    filepath = PERFORMANCE_DIR / "pending-evolutions.json"
    if not filepath.exists():
        return []

    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
        return data.get("evolutions", [])
    except (json.JSONDecodeError, OSError):
        return []


def save_pending_evolutions(evolutions: list[dict[str, Any]]) -> Path:
    """Save pending evolution proposals.

    Args:
        evolutions: List of evolution dicts.

    Returns:
        Path to saved file.
    """
    ensure_dirs()
    filepath = PERFORMANCE_DIR / "pending-evolutions.json"
    data = {
        "schema_version": SCHEMA_VERSION,
        "evolutions": evolutions,
    }
    filepath.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return filepath
