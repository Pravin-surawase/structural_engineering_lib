"""Tests for scripts/session_store.py — JSON session persistence.

Tests cover:
- SessionState creation, save/load round-trip
- Session listing and resume context
- Path traversal prevention (security)
- Invalid JSON and missing file handling
- Session end with duration calculation
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

# Add repo root to sys.path so `scripts.session_store` is importable
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


# ---------------------------------------------------------------------------
# Helpers — import the module under test with mocked SESSIONS_DIR
# ---------------------------------------------------------------------------


def _import_session_store(tmp_path: Path):
    """Import session_store with SESSIONS_DIR pointing to tmp_path."""
    import importlib

    import scripts.session_store as mod

    mod = importlib.reload(mod)
    mod.SESSIONS_DIR = tmp_path
    return mod


# ---------------------------------------------------------------------------
# SessionState dataclass
# ---------------------------------------------------------------------------


class TestSessionStateDataclass:
    """Tests for SessionState creation and serialization."""

    def test_create_session_state(self, tmp_path):
        mod = _import_session_store(tmp_path)
        state = mod.SessionState(
            session_id="S001",
            agent="backend",
            task_id="TASK-100",
            task_description="Test task",
            pipeline_step="PLAN",
        )
        assert state.session_id == "S001"
        assert state.agent == "backend"
        assert state.files_changed == []
        assert state.ended_at is None

    def test_to_dict_round_trip(self, tmp_path):
        mod = _import_session_store(tmp_path)
        state = mod.SessionState(
            session_id="S002",
            agent="tester",
            task_id="TASK-200",
            task_description="Round trip",
            pipeline_step="EXECUTE",
            files_changed=["a.py", "b.py"],
            notes="some notes",
        )
        d = state.to_dict()
        restored = mod.SessionState.from_dict(d)
        assert restored.session_id == state.session_id
        assert restored.files_changed == ["a.py", "b.py"]
        assert restored.notes == "some notes"


# ---------------------------------------------------------------------------
# Save / Load
# ---------------------------------------------------------------------------


class TestSaveLoad:
    """Tests for save_session and load_session."""

    def test_save_and_load(self, tmp_path):
        mod = _import_session_store(tmp_path)
        state = mod.SessionState(
            session_id="S010",
            agent="backend",
            task_id="TASK-300",
            task_description="Save test",
            pipeline_step="GATHER",
        )
        path = mod.save_session(state)
        assert path.exists()

        loaded = mod.load_session("S010")
        assert loaded.session_id == "S010"
        assert loaded.task_description == "Save test"

    def test_load_missing_session_raises(self, tmp_path):
        mod = _import_session_store(tmp_path)
        with pytest.raises(FileNotFoundError, match="Session S999 not found"):
            mod.load_session("S999")

    def test_load_invalid_json(self, tmp_path):
        mod = _import_session_store(tmp_path)
        bad_file = tmp_path / "S050.json"
        bad_file.write_text("{invalid json", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            mod.load_session("S050")


# ---------------------------------------------------------------------------
# Path traversal prevention (SECURITY)
# ---------------------------------------------------------------------------


class TestPathTraversal:
    """Ensure path traversal attacks are rejected."""

    @pytest.mark.parametrize(
        "bad_id",
        [
            "../etc/passwd",
            "..%2F..%2Fetc/shadow",
            "S001/../../secret",
            "S001\\..\\..",
            "hello world",
            "S001;rm -rf /",
            "",
        ],
    )
    def test_validate_id_rejects_traversal(self, tmp_path, bad_id):
        mod = _import_session_store(tmp_path)
        with pytest.raises(ValueError, match="Invalid session_id"):
            mod._validate_id(bad_id, "session_id")

    def test_save_rejects_traversal_id(self, tmp_path):
        mod = _import_session_store(tmp_path)
        state = mod.SessionState(
            session_id="../../../etc/passwd",
            agent="evil",
            task_id="TASK-0",
            task_description="exploit",
            pipeline_step="PLAN",
        )
        with pytest.raises(ValueError, match="Invalid session_id"):
            mod.save_session(state)

    def test_load_rejects_traversal_id(self, tmp_path):
        mod = _import_session_store(tmp_path)
        with pytest.raises(ValueError, match="Invalid session_id"):
            mod.load_session("../../../etc/passwd")

    def test_valid_ids_accepted(self, tmp_path):
        mod = _import_session_store(tmp_path)
        for valid in ["S001", "S123", "my-session", "TASK_100"]:
            mod._validate_id(valid, "session_id")  # Should not raise


# ---------------------------------------------------------------------------
# Session listing
# ---------------------------------------------------------------------------


class TestListSessions:
    """Tests for list_sessions."""

    def test_list_empty(self, tmp_path):
        mod = _import_session_store(tmp_path)
        assert mod.list_sessions() == []

    def test_list_returns_sessions(self, tmp_path):
        mod = _import_session_store(tmp_path)
        for i in range(3):
            state = mod.SessionState(
                session_id=f"S{i + 1:03d}",
                agent="tester",
                task_id=f"TASK-{i}",
                task_description=f"Task {i}",
                pipeline_step="PLAN",
            )
            mod.save_session(state)

        sessions = mod.list_sessions(last_n=10)
        assert len(sessions) == 3

    def test_list_respects_last_n(self, tmp_path):
        mod = _import_session_store(tmp_path)
        for i in range(5):
            state = mod.SessionState(
                session_id=f"S{i + 1:03d}",
                agent="tester",
                task_id=f"TASK-{i}",
                task_description=f"Task {i}",
                pipeline_step="PLAN",
            )
            mod.save_session(state)

        sessions = mod.list_sessions(last_n=2)
        assert len(sessions) == 2


# ---------------------------------------------------------------------------
# Session resume
# ---------------------------------------------------------------------------


class TestResumeContext:
    """Tests for resume_context."""

    def test_resume_generates_context(self, tmp_path):
        mod = _import_session_store(tmp_path)
        state = mod.SessionState(
            session_id="S020",
            agent="backend",
            task_id="TASK-500",
            task_description="Resume test",
            pipeline_step="EXECUTE",
            files_changed=["foo.py"],
            notes="halfway done",
        )
        mod.save_session(state)

        context = mod.resume_context("S020")
        assert "S020" in context
        assert "TASK-500" in context
        assert "EXECUTE" in context
        assert "foo.py" in context


# ---------------------------------------------------------------------------
# End session
# ---------------------------------------------------------------------------


class TestEndSession:
    """Tests for end_session."""

    def test_end_session_sets_timestamp(self, tmp_path):
        mod = _import_session_store(tmp_path)
        state = mod.SessionState(
            session_id="S030",
            agent="tester",
            task_id="TASK-600",
            task_description="End test",
            pipeline_step="COMMIT",
        )
        mod.save_session(state)

        ended = mod.end_session("S030", notes="all done")
        assert ended.ended_at is not None
        assert ended.duration_min is not None
        assert ended.duration_min >= 0
        assert "all done" in ended.notes

    def test_end_no_active_session_raises(self, tmp_path):
        mod = _import_session_store(tmp_path)
        with pytest.raises(ValueError, match="No active session"):
            mod.end_session()


# ---------------------------------------------------------------------------
# Generate session ID
# ---------------------------------------------------------------------------


class TestGenerateSessionId:
    """Tests for generate_session_id."""

    def test_first_session_is_s001(self, tmp_path):
        mod = _import_session_store(tmp_path)
        assert mod.generate_session_id() == "S001"

    def test_increments_from_last(self, tmp_path):
        mod = _import_session_store(tmp_path)
        # Create S003.json
        (tmp_path / "S003.json").write_text("{}", encoding="utf-8")
        assert mod.generate_session_id() == "S004"
