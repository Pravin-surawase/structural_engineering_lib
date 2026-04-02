"""Tests for scripts/pipeline_state.py — Pipeline step tracking + resume.

Tests cover:
- Pipeline creation and save/load round-trip
- Step progression through DEFAULT_STEPS
- Pipeline resume from saved state
- Path traversal prevention (security)
- Fail step handling
- Advance on completed/failed pipeline
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Add repo root to sys.path so `scripts.pipeline_state` is importable
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


# ---------------------------------------------------------------------------
# Helpers — import the module under test with mocked PIPELINES_DIR
# ---------------------------------------------------------------------------


def _import_pipeline_state(tmp_path: Path):
    """Import pipeline_state with PIPELINES_DIR pointing to tmp_path."""
    import importlib

    import scripts.pipeline_state as mod

    mod = importlib.reload(mod)
    mod.PIPELINES_DIR = tmp_path
    return mod


# ---------------------------------------------------------------------------
# Pipeline creation
# ---------------------------------------------------------------------------


class TestCreatePipeline:
    """Tests for create_pipeline."""

    def test_create_with_default_steps(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        pipeline = mod.create_pipeline(task_id="TASK-100", agent="backend")
        assert pipeline.task_id == "TASK-100"
        assert pipeline.agent == "backend"
        assert pipeline.status == "running"
        assert len(pipeline.steps) == len(mod.DEFAULT_STEPS)
        # First step should be running
        assert pipeline.steps[0].status == "running"
        assert pipeline.steps[0].started_at is not None
        # Remaining steps should be pending
        for step in pipeline.steps[1:]:
            assert step.status == "pending"

    def test_create_with_custom_steps(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        pipeline = mod.create_pipeline(
            task_id="TASK-200",
            agent="tester",
            step_names=["PLAN", "EXECUTE", "COMMIT"],
        )
        assert len(pipeline.steps) == 3
        assert [s.name for s in pipeline.steps] == ["PLAN", "EXECUTE", "COMMIT"]

    def test_create_generates_unique_id(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        p1 = mod.create_pipeline(task_id="TASK-300", agent="backend")
        p2 = mod.create_pipeline(task_id="TASK-300", agent="backend")
        assert p1.pipeline_id != p2.pipeline_id
        assert p1.pipeline_id == "TASK-300-pipeline"
        assert p2.pipeline_id == "TASK-300-pipeline-2"


# ---------------------------------------------------------------------------
# Save / Load round-trip
# ---------------------------------------------------------------------------


class TestSaveLoad:
    """Tests for _save_pipeline and get_pipeline."""

    def test_save_and_load_round_trip(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        pipeline = mod.create_pipeline(task_id="TASK-400", agent="backend")
        pid = pipeline.pipeline_id

        loaded = mod.get_pipeline(pid)
        assert loaded.pipeline_id == pid
        assert loaded.task_id == "TASK-400"
        assert loaded.status == "running"
        assert len(loaded.steps) == len(mod.DEFAULT_STEPS)
        # Verify steps survived round-trip as StepState objects
        assert loaded.steps[0].name == "PLAN"
        assert loaded.steps[0].status == "running"

    def test_load_missing_pipeline_raises(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        with pytest.raises(FileNotFoundError, match="Pipeline .* not found"):
            mod.get_pipeline("TASK-MISSING-pipeline")

    def test_load_invalid_json(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        bad_file = tmp_path / "TASK-BAD-pipeline.json"
        bad_file.write_text("not json{{{", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            mod.get_pipeline("TASK-BAD-pipeline")


# ---------------------------------------------------------------------------
# Step progression
# ---------------------------------------------------------------------------


class TestStepProgression:
    """Tests for advance_step through the pipeline."""

    def test_advance_single_step(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        pipeline = mod.create_pipeline(
            task_id="TASK-500",
            agent="backend",
            step_names=["PLAN", "EXECUTE", "COMMIT"],
        )
        pid = pipeline.pipeline_id

        # Advance past PLAN
        updated = mod.advance_step(pid, notes="plan complete", artifacts=["plan.md"])
        assert updated.current_step == 1
        assert updated.steps[0].status == "completed"
        assert updated.steps[0].notes == "plan complete"
        assert "plan.md" in updated.steps[0].artifacts
        assert updated.steps[1].status == "running"

    def test_advance_all_steps_completes_pipeline(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        pipeline = mod.create_pipeline(
            task_id="TASK-510",
            agent="backend",
            step_names=["PLAN", "EXECUTE", "COMMIT"],
        )
        pid = pipeline.pipeline_id

        mod.advance_step(pid)  # PLAN → EXECUTE
        mod.advance_step(pid)  # EXECUTE → COMMIT
        final = mod.advance_step(pid)  # COMMIT → done

        assert final.status == "completed"
        assert final.ended_at is not None
        assert all(s.status == "completed" for s in final.steps)

    def test_advance_completed_pipeline_raises(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        pipeline = mod.create_pipeline(
            task_id="TASK-520",
            agent="backend",
            step_names=["PLAN"],
        )
        pid = pipeline.pipeline_id
        mod.advance_step(pid)  # Complete the only step

        with pytest.raises(ValueError, match="Cannot advance completed"):
            mod.advance_step(pid)


# ---------------------------------------------------------------------------
# Fail step
# ---------------------------------------------------------------------------


class TestFailStep:
    """Tests for fail_step."""

    def test_fail_marks_step_and_pipeline(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        pipeline = mod.create_pipeline(
            task_id="TASK-600",
            agent="backend",
            step_names=["PLAN", "EXECUTE"],
        )
        pid = pipeline.pipeline_id

        failed = mod.fail_step(pid, reason="plan failed badly")
        assert failed.status == "failed"
        assert failed.ended_at is not None
        assert failed.steps[0].status == "failed"
        assert failed.steps[0].notes == "plan failed badly"

    def test_fail_on_completed_pipeline_raises(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        pipeline = mod.create_pipeline(
            task_id="TASK-610",
            agent="backend",
            step_names=["PLAN"],
        )
        mod.advance_step(pipeline.pipeline_id)

        with pytest.raises(ValueError, match="Cannot fail completed"):
            mod.fail_step(pipeline.pipeline_id, reason="too late")

    def test_advance_failed_pipeline_raises(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        pipeline = mod.create_pipeline(
            task_id="TASK-620",
            agent="backend",
            step_names=["PLAN", "EXECUTE"],
        )
        mod.fail_step(pipeline.pipeline_id, reason="nope")

        with pytest.raises(ValueError, match="Cannot advance failed"):
            mod.advance_step(pipeline.pipeline_id)


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
            "TASK-001/../../secret",
            "TASK-001\\..\\..",
            "hello world",
            "TASK;rm -rf /",
            "",
        ],
    )
    def test_validate_id_rejects_traversal(self, tmp_path, bad_id):
        mod = _import_pipeline_state(tmp_path)
        with pytest.raises(ValueError, match="Invalid pipeline_id"):
            mod._validate_id(bad_id, "pipeline_id")

    def test_get_pipeline_rejects_traversal(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        with pytest.raises(ValueError, match="Invalid pipeline_id"):
            mod.get_pipeline("../../../etc/passwd")

    def test_save_pipeline_rejects_traversal(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        pipeline = mod.PipelineState(
            pipeline_id="../../../etc/passwd",
            task_id="TASK-0",
            agent="evil",
            steps=[],
        )
        with pytest.raises(ValueError, match="Invalid pipeline_id"):
            mod._save_pipeline(pipeline)

    def test_valid_pipeline_ids_accepted(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        for valid in ["TASK-100-pipeline", "TASK_200-pipeline-2", "my-pipe"]:
            mod._validate_id(valid, "pipeline_id")  # Should not raise


# ---------------------------------------------------------------------------
# Resume context
# ---------------------------------------------------------------------------


class TestResumeContext:
    """Tests for resume_context."""

    def test_resume_running_pipeline(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        pipeline = mod.create_pipeline(
            task_id="TASK-700",
            agent="backend",
            step_names=["PLAN", "EXECUTE", "COMMIT"],
        )
        mod.advance_step(pipeline.pipeline_id, notes="plan done")

        context = mod.resume_context(pipeline.pipeline_id)
        assert "TASK-700" in context
        assert "EXECUTE" in context
        assert "Resume at step" in context

    def test_resume_completed_pipeline(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        pipeline = mod.create_pipeline(
            task_id="TASK-710",
            agent="backend",
            step_names=["PLAN"],
        )
        mod.advance_step(pipeline.pipeline_id)

        context = mod.resume_context(pipeline.pipeline_id)
        assert "completed successfully" in context

    def test_resume_failed_pipeline(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        pipeline = mod.create_pipeline(
            task_id="TASK-720",
            agent="backend",
            step_names=["PLAN", "EXECUTE"],
        )
        mod.fail_step(pipeline.pipeline_id, reason="crash")

        context = mod.resume_context(pipeline.pipeline_id)
        assert "failed" in context.lower()
        assert "crash" in context


# ---------------------------------------------------------------------------
# List pipelines
# ---------------------------------------------------------------------------


class TestListPipelines:
    """Tests for list_pipelines."""

    def test_list_empty(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        assert mod.list_pipelines() == []

    def test_list_returns_pipelines(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        mod.create_pipeline(task_id="TASK-800", agent="backend")
        mod.create_pipeline(task_id="TASK-801", agent="tester")

        pipelines = mod.list_pipelines()
        assert len(pipelines) == 2

    def test_list_filters_by_status(self, tmp_path):
        mod = _import_pipeline_state(tmp_path)
        p1 = mod.create_pipeline(
            task_id="TASK-810", agent="backend", step_names=["PLAN"]
        )
        mod.create_pipeline(task_id="TASK-811", agent="backend")
        # Complete first pipeline
        mod.advance_step(p1.pipeline_id)

        running = mod.list_pipelines(status="running")
        completed = mod.list_pipelines(status="completed")
        assert len(running) == 1
        assert len(completed) == 1
        assert completed[0].task_id == "TASK-810"
