#!/usr/bin/env python3
"""
Pipeline state tracking for multi-step agent workflows.

Enables interrupted workflows to resume from the exact step they left off,
with full context about what was completed and what remains.

USAGE:
    python scripts/pipeline_state.py new --task TASK-857 --agent backend [--steps PLAN,GATHER,EXECUTE]
    python scripts/pipeline_state.py advance <pipeline_id> [--notes "completed X"] [--artifacts file1.py,file2.py]
    python scripts/pipeline_state.py advance-parallel <pipeline_id> --steps TEST,DOCUMENT [--notes "parallel work"]
    python scripts/pipeline_state.py fail <pipeline_id> --reason "test failed"
    python scripts/pipeline_state.py show <pipeline_id>
    python scripts/pipeline_state.py list [--status running]
    python scripts/pipeline_state.py resume <pipeline_id>
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
from _lib.output import StatusLine
from _lib.utils import REPO_ROOT

PIPELINES_DIR = REPO_ROOT / "logs" / "pipelines"


def _validate_id(id_value: str, id_type: str = "pipeline_id") -> None:
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


# Default pipeline step sequences
DEFAULT_STEPS = [
    "PLAN",
    "RESEARCH",
    "GATHER",
    "EXECUTE",
    "TEST",
    "VERIFY",
    "DOCUMENT",
    "COMMIT",
]
IS456_STEPS = [
    "PLAN",
    "MATH_REVIEW",
    "IMPLEMENT",
    "TEST",
    "REVIEW",
    "API_WIRE",
    "ENDPOINT",
    "DOCUMENT",
    "COMMIT",
]

# Parallel step groups - steps that can run simultaneously
PARALLEL_GROUPS = {
    "standard": [
        ["TEST", "DOCUMENT"],  # Tests and docs can run in parallel
    ],
    "is456": [
        ["MATH_REVIEW"],  # Must be sequential (gate)
        ["IMPLEMENT"],  # Must be sequential
        ["TEST", "DOCUMENT"],  # Can run in parallel
        ["API_WIRE", "ENDPOINT"],  # Can run in parallel if independent
    ],
}


@dataclass
class StepState:
    """State of a single pipeline step."""

    name: str
    status: str  # pending, running, completed, failed, skipped
    agent: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    notes: str = ""
    artifacts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> StepState:
        """Load from JSON dict."""
        return cls(**data)


@dataclass
class PipelineState:
    """Multi-step pipeline state with resumability."""

    pipeline_id: str
    task_id: str
    agent: str
    steps: list[StepState]
    current_step: int = 0
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    ended_at: Optional[str] = None
    status: str = "running"  # running, paused, completed, failed
    parallel_groups: list[list[str]] = field(
        default_factory=list
    )  # Parallelizable step groups

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        data = asdict(self)
        # Ensure steps are serialized correctly
        data["steps"] = [
            step.to_dict() if hasattr(step, "to_dict") else step
            for step in data["steps"]
        ]
        return data

    @classmethod
    def from_dict(cls, data: dict) -> PipelineState:
        """Load from JSON dict."""
        # Convert steps back to StepState objects
        if "steps" in data:
            data["steps"] = [
                StepState.from_dict(step) if isinstance(step, dict) else step
                for step in data["steps"]
            ]
        return cls(**data)


def _ensure_pipelines_dir() -> None:
    """Create logs/pipelines/ directory if it doesn't exist."""
    PIPELINES_DIR.mkdir(parents=True, exist_ok=True)
    gitkeep = PIPELINES_DIR / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()


def _generate_pipeline_id(task_id: str) -> str:
    """Generate pipeline ID: TASK-XXX-pipeline or TASK-XXX-pipeline-2 if duplicate."""
    _ensure_pipelines_dir()

    base_id = f"{task_id}-pipeline"
    pipeline_file = PIPELINES_DIR / f"{base_id}.json"

    if not pipeline_file.exists():
        return base_id

    # Find next available suffix
    counter = 2
    while True:
        candidate = f"{base_id}-{counter}"
        if not (PIPELINES_DIR / f"{candidate}.json").exists():
            return candidate
        counter += 1


def create_pipeline(
    task_id: str,
    agent: str,
    step_names: list[str] | None = None,
) -> PipelineState:
    """Create a new pipeline with ordered steps.

    Args:
        task_id: Task identifier (e.g., "TASK-857")
        agent: Agent responsible for the pipeline
        step_names: Ordered list of step names (defaults to DEFAULT_STEPS)

    Returns:
        PipelineState with all steps initialized as "pending"
    """
    if step_names is None:
        step_names = DEFAULT_STEPS

    pipeline_id = _generate_pipeline_id(task_id)

    # Initialize all steps as pending
    steps = [
        StepState(
            name=name,
            status="pending",
            agent=agent,  # Can be overridden per step later
        )
        for name in step_names
    ]

    # Mark first step as running
    if steps:
        steps[0].status = "running"
        steps[0].started_at = datetime.now().isoformat()

    pipeline = PipelineState(
        pipeline_id=pipeline_id,
        task_id=task_id,
        agent=agent,
        steps=steps,
        current_step=0,
        status="running",
    )

    _save_pipeline(pipeline)
    return pipeline


def _save_pipeline(pipeline: PipelineState) -> Path:
    """Save pipeline state to disk."""
    _validate_id(pipeline.pipeline_id, "pipeline_id")
    _ensure_pipelines_dir()

    pipeline_file = PIPELINES_DIR / f"{pipeline.pipeline_id}.json"
    with pipeline_file.open("w", encoding="utf-8") as f:
        json.dump(pipeline.to_dict(), f, indent=2, ensure_ascii=False)

    return pipeline_file


def get_pipeline(pipeline_id: str) -> PipelineState:
    """Load pipeline state from disk."""
    _validate_id(pipeline_id, "pipeline_id")
    pipeline_file = PIPELINES_DIR / f"{pipeline_id}.json"
    if not pipeline_file.exists():
        raise FileNotFoundError(f"Pipeline {pipeline_id} not found at {pipeline_file}")

    with pipeline_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return PipelineState.from_dict(data)


def advance_step(
    pipeline_id: str,
    notes: str = "",
    artifacts: list[str] | None = None,
) -> PipelineState:
    """Mark current step as completed and advance to next step.

    Args:
        pipeline_id: Pipeline identifier
        notes: Notes about what was completed
        artifacts: Files created/modified in this step

    Returns:
        Updated PipelineState
    """
    pipeline = get_pipeline(pipeline_id)

    if pipeline.status in ("completed", "failed"):
        raise ValueError(f"Cannot advance {pipeline.status} pipeline")

    # Complete current step
    current = pipeline.steps[pipeline.current_step]
    current.status = "completed"
    current.completed_at = datetime.now().isoformat()
    current.notes = notes
    if artifacts:
        current.artifacts.extend(artifacts)

    # Move to next step
    pipeline.current_step += 1

    if pipeline.current_step >= len(pipeline.steps):
        # Pipeline complete
        pipeline.status = "completed"
        pipeline.ended_at = datetime.now().isoformat()
    else:
        # Start next step
        next_step = pipeline.steps[pipeline.current_step]
        next_step.status = "running"
        next_step.started_at = datetime.now().isoformat()

    _save_pipeline(pipeline)
    return pipeline


def fail_step(pipeline_id: str, reason: str) -> PipelineState:
    """Mark current step as failed and halt pipeline.

    Args:
        pipeline_id: Pipeline identifier
        reason: Failure reason

    Returns:
        Updated PipelineState
    """
    pipeline = get_pipeline(pipeline_id)

    if pipeline.status in ("completed", "failed"):
        raise ValueError(f"Cannot fail {pipeline.status} pipeline")

    # Fail current step
    current = pipeline.steps[pipeline.current_step]
    current.status = "failed"
    current.completed_at = datetime.now().isoformat()
    current.notes = reason

    # Halt pipeline
    pipeline.status = "failed"
    pipeline.ended_at = datetime.now().isoformat()

    _save_pipeline(pipeline)
    return pipeline


def list_pipelines(status: str | None = None) -> list[PipelineState]:
    """List all pipelines, optionally filtered by status.

    Args:
        status: Filter by status (running, paused, completed, failed)

    Returns:
        List of PipelineState objects, sorted by started_at
    """
    _ensure_pipelines_dir()

    pipeline_files = sorted(PIPELINES_DIR.glob("*.json"))
    pipelines = []

    for pipeline_file in pipeline_files:
        if pipeline_file.name == ".gitkeep":
            continue

        try:
            pipeline = get_pipeline(pipeline_file.stem)
            if status is None or pipeline.status == status:
                pipelines.append(pipeline)
        except Exception as e:
            StatusLine.warn(f"Failed to load {pipeline_file.name}: {e}")

    # Sort by started_at (newest first)
    pipelines.sort(key=lambda p: p.started_at, reverse=True)
    return pipelines


def can_parallelize(pipeline: PipelineState) -> list[str]:
    """Check if current step can run in parallel with other steps.

    Args:
        pipeline: Pipeline state

    Returns:
        List of step names that can run in parallel with current step
    """
    if pipeline.current_step >= len(pipeline.steps):
        return []

    current_step = pipeline.steps[pipeline.current_step]

    # Check parallel groups
    for group in pipeline.parallel_groups:
        if current_step.name in group:
            # Return other steps in the same group that are still pending
            parallel_candidates = []
            for step_name in group:
                if step_name == current_step.name:
                    continue
                # Find step in pipeline
                for step in pipeline.steps:
                    if step.name == step_name and step.status == "pending":
                        parallel_candidates.append(step_name)
                        break
            return parallel_candidates

    return []


def advance_parallel(
    pipeline_id: str,
    step_names: list[str],
    notes: str = "",
    artifacts: list[str] | None = None,
) -> PipelineState:
    """Mark multiple steps as completed simultaneously (parallel execution).

    Args:
        pipeline_id: Pipeline identifier
        step_names: List of step names to mark as completed
        notes: Notes about what was completed
        artifacts: Files created/modified

    Returns:
        Updated PipelineState
    """
    pipeline = get_pipeline(pipeline_id)

    if pipeline.status in ("completed", "failed"):
        raise ValueError(f"Cannot advance {pipeline.status} pipeline")

    # Validate that all steps are in the same parallel group
    found_group = None
    for group in pipeline.parallel_groups:
        if all(name in group for name in step_names):
            found_group = group
            break

    if not found_group:
        raise ValueError(f"Steps {step_names} are not in the same parallel group")

    # Mark all specified steps as completed
    completed_time = datetime.now().isoformat()
    for step_name in step_names:
        for step in pipeline.steps:
            if step.name == step_name:
                if step.status != "running" and step.status != "pending":
                    raise ValueError(
                        f"Step {step_name} is not running or pending: {step.status}"
                    )
                step.status = "completed"
                step.completed_at = completed_time
                if notes:
                    step.notes = notes
                if artifacts:
                    step.artifacts.extend(artifacts)
                break

    # Find next step that's not completed
    next_idx = pipeline.current_step
    while next_idx < len(pipeline.steps):
        if pipeline.steps[next_idx].status != "completed":
            break
        next_idx += 1

    pipeline.current_step = next_idx

    if pipeline.current_step >= len(pipeline.steps):
        # Pipeline complete
        pipeline.status = "completed"
        pipeline.ended_at = datetime.now().isoformat()
    else:
        # Start next step
        next_step = pipeline.steps[pipeline.current_step]
        if next_step.status == "pending":
            next_step.status = "running"
            next_step.started_at = datetime.now().isoformat()

    _save_pipeline(pipeline)
    return pipeline


def resume_context(pipeline_id: str) -> str:
    """Generate a context string for resuming an interrupted pipeline.

    Args:
        pipeline_id: Pipeline identifier

    Returns:
        Markdown-formatted context string
    """
    pipeline = get_pipeline(pipeline_id)

    lines = [
        f"# Pipeline Resume Context: {pipeline.pipeline_id}",
        "",
        f"**Task:** {pipeline.task_id}",
        f"**Agent:** {pipeline.agent}",
        f"**Status:** {pipeline.status}",
        f"**Started:** {pipeline.started_at}",
        "",
        "## Progress",
        "",
    ]

    for i, step in enumerate(pipeline.steps):
        status_icon = {
            "completed": "✅",
            "running": "🔄",
            "pending": "⏳",
            "failed": "❌",
            "skipped": "⏭️",
        }.get(step.status, "❓")

        marker = "→" if i == pipeline.current_step else " "
        lines.append(f"{marker} {status_icon} **{step.name}** ({step.status})")

        if step.notes:
            lines.append(f"   Notes: {step.notes}")
        if step.artifacts:
            lines.append(f"   Artifacts: {', '.join(step.artifacts)}")

    lines.extend(
        [
            "",
            "## Next Actions",
            "",
        ]
    )

    if pipeline.status == "completed":
        lines.append("✅ Pipeline completed successfully")
    elif pipeline.status == "failed":
        current = pipeline.steps[pipeline.current_step]
        lines.append(f"❌ Pipeline failed at step: {current.name}")
        if current.notes:
            lines.append(f"   Reason: {current.notes}")
    elif pipeline.current_step < len(pipeline.steps):
        current = pipeline.steps[pipeline.current_step]
        lines.append(f"🔄 Resume at step: **{current.name}**")
        lines.append(f"   Agent: {current.agent}")

        # Check for parallel opportunities
        parallel_steps = can_parallelize(pipeline)
        if parallel_steps:
            lines.append("")
            lines.append(
                f"⚡ Parallel opportunity: {current.name} + {', '.join(parallel_steps)} can run simultaneously"
            )

        # Show remaining steps
        remaining = [s.name for s in pipeline.steps[pipeline.current_step + 1 :]]
        if remaining:
            lines.append(f"   Remaining: {' → '.join(remaining)}")

    return "\n".join(lines)


def cmd_new(args: argparse.Namespace) -> int:
    """Create a new pipeline."""
    step_names = None
    if args.steps:
        step_names = [s.strip() for s in args.steps.split(",")]

    pipeline = create_pipeline(
        task_id=args.task,
        agent=args.agent,
        step_names=step_names,
    )

    print()
    StatusLine.ok(f"Created pipeline: {pipeline.pipeline_id}")
    print()
    print(f"  Task:   {pipeline.task_id}")
    print(f"  Agent:  {pipeline.agent}")
    print(f"  Steps:  {len(pipeline.steps)}")
    print(f"  First:  {pipeline.steps[0].name}")
    print()
    print(f"📁 Saved to: logs/pipelines/{pipeline.pipeline_id}.json")
    print()

    return 0


def cmd_advance(args: argparse.Namespace) -> int:
    """Advance to the next pipeline step."""
    artifacts = None
    if args.artifacts:
        artifacts = [a.strip() for a in args.artifacts.split(",")]

    try:
        pipeline = advance_step(
            pipeline_id=args.pipeline_id,
            notes=args.notes or "",
            artifacts=artifacts,
        )
    except Exception as e:
        StatusLine.fail(f"Failed to advance: {e}")
        return 1

    current_idx = pipeline.current_step - 1  # Just completed
    completed_step = pipeline.steps[current_idx]

    print()
    StatusLine.ok(f"Completed step: {completed_step.name}")
    print()

    if pipeline.status == "completed":
        print("  ✅ Pipeline completed!")
        print(f"  Total steps: {len(pipeline.steps)}")
        print()
    else:
        next_step = pipeline.steps[pipeline.current_step]
        print(f"  ▶️  Next step: {next_step.name}")
        remaining = len(pipeline.steps) - pipeline.current_step
        print(
            f"  📊 Progress: {pipeline.current_step}/{len(pipeline.steps)} ({remaining} remaining)"
        )

        # Check for parallel opportunities
        parallel_steps = can_parallelize(pipeline)
        if parallel_steps:
            print(
                f"  ⚡ Parallel opportunity: {next_step.name} + {', '.join(parallel_steps)} can run simultaneously"
            )
        print()

    return 0


def cmd_advance_parallel(args: argparse.Namespace) -> int:
    """Advance multiple parallel steps simultaneously."""
    step_names = [s.strip() for s in args.steps.split(",")]
    artifacts = None
    if args.artifacts:
        artifacts = [a.strip() for a in args.artifacts.split(",")]

    try:
        pipeline = advance_parallel(
            pipeline_id=args.pipeline_id,
            step_names=step_names,
            notes=args.notes or "",
            artifacts=artifacts,
        )
    except Exception as e:
        StatusLine.fail(f"Failed to advance parallel steps: {e}")
        return 1

    print()
    StatusLine.ok(f"Completed parallel steps: {', '.join(step_names)}")
    print()

    if pipeline.status == "completed":
        print("  ✅ Pipeline completed!")
        print(f"  Total steps: {len(pipeline.steps)}")
        print()
    else:
        next_step = pipeline.steps[pipeline.current_step]
        print(f"  ▶️  Next step: {next_step.name}")
        remaining = len(pipeline.steps) - pipeline.current_step
        print(
            f"  📊 Progress: {pipeline.current_step}/{len(pipeline.steps)} ({remaining} remaining)"
        )
        print()

    return 0


def cmd_fail(args: argparse.Namespace) -> int:
    """Mark current step as failed."""
    try:
        pipeline = fail_step(
            pipeline_id=args.pipeline_id,
            reason=args.reason,
        )
    except Exception as e:
        StatusLine.fail(f"Failed to mark as failed: {e}")
        return 1

    failed_step = pipeline.steps[pipeline.current_step]

    print()
    StatusLine.fail(f"Pipeline failed at step: {failed_step.name}")
    print()
    print(f"  Reason: {args.reason}")
    print(f"  Progress: {pipeline.current_step + 1}/{len(pipeline.steps)}")
    print()

    return 1


def cmd_show(args: argparse.Namespace) -> int:
    """Show pipeline state."""
    try:
        pipeline = get_pipeline(args.pipeline_id)
    except FileNotFoundError as e:
        StatusLine.fail(str(e))
        return 1

    print()
    print("=" * 60)
    print(f"Pipeline: {pipeline.pipeline_id}")
    print("=" * 60)
    print()
    print(f"  Task:    {pipeline.task_id}")
    print(f"  Agent:   {pipeline.agent}")
    print(f"  Status:  {pipeline.status}")
    print(f"  Started: {pipeline.started_at}")
    if pipeline.ended_at:
        print(f"  Ended:   {pipeline.ended_at}")
    print()
    print(f"  Progress: {pipeline.current_step}/{len(pipeline.steps)} steps")
    print()
    print("Steps:")
    print()

    for i, step in enumerate(pipeline.steps):
        status_icon = {
            "completed": "✅",
            "running": "🔄",
            "pending": "⏳",
            "failed": "❌",
            "skipped": "⏭️",
        }.get(step.status, "❓")

        marker = "→" if i == pipeline.current_step else " "
        print(f"  {marker} {status_icon} {i + 1}. {step.name} ({step.status})")

        if step.started_at:
            print(f"      Started: {step.started_at}")
        if step.completed_at:
            print(f"      Completed: {step.completed_at}")
        if step.notes:
            print(f"      Notes: {step.notes}")
        if step.artifacts:
            print(f"      Artifacts: {', '.join(step.artifacts)}")
        print()

    print("=" * 60)
    print()

    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """List pipelines."""
    pipelines = list_pipelines(status=args.status)

    if not pipelines:
        filter_msg = f" with status '{args.status}'" if args.status else ""
        print(f"No pipelines found{filter_msg}")
        return 0

    print()
    print("=" * 60)
    print(f"Pipelines ({len(pipelines)})")
    print("=" * 60)
    print()

    for pipeline in pipelines:
        status_icon = {
            "running": "🔄",
            "paused": "⏸️",
            "completed": "✅",
            "failed": "❌",
        }.get(pipeline.status, "❓")

        current_step_name = (
            pipeline.steps[pipeline.current_step].name
            if pipeline.current_step < len(pipeline.steps)
            else "DONE"
        )

        print(f"  {status_icon} {pipeline.pipeline_id}")
        print(f"     Task: {pipeline.task_id}")
        print(f"     Agent: {pipeline.agent}")
        print(f"     Progress: {pipeline.current_step}/{len(pipeline.steps)} steps")
        print(f"     Current: {current_step_name}")
        print(f"     Started: {pipeline.started_at}")
        print()

    print("=" * 60)
    print()

    return 0


def cmd_resume(args: argparse.Namespace) -> int:
    """Generate resume context."""
    try:
        context = resume_context(args.pipeline_id)
    except FileNotFoundError as e:
        StatusLine.fail(str(e))
        return 1

    print()
    print(context)
    print()

    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="pipeline_state.py",
        description="Pipeline state tracking for multi-step agent workflows",
    )
    sub = parser.add_subparsers(dest="command", required=True, help="Pipeline command")

    # new
    p_new = sub.add_parser("new", help="Create a new pipeline")
    p_new.add_argument("--task", required=True, help="Task ID (e.g., TASK-857)")
    p_new.add_argument("--agent", required=True, help="Agent name (e.g., backend)")
    p_new.add_argument(
        "--steps",
        help="Comma-separated step names (default: PLAN,RESEARCH,GATHER,EXECUTE,TEST,VERIFY,DOCUMENT,COMMIT)",
    )

    # advance
    p_advance = sub.add_parser("advance", help="Complete current step and advance")
    p_advance.add_argument("pipeline_id", help="Pipeline ID")
    p_advance.add_argument("--notes", default="", help="Notes about what was completed")
    p_advance.add_argument("--artifacts", help="Comma-separated list of files changed")

    # advance-parallel (NEW)
    p_advance_parallel = sub.add_parser(
        "advance-parallel", help="Complete multiple parallel steps simultaneously"
    )
    p_advance_parallel.add_argument("pipeline_id", help="Pipeline ID")
    p_advance_parallel.add_argument(
        "--steps",
        required=True,
        help="Comma-separated step names to complete in parallel",
    )
    p_advance_parallel.add_argument(
        "--notes", default="", help="Notes about what was completed"
    )
    p_advance_parallel.add_argument(
        "--artifacts", help="Comma-separated list of files changed"
    )

    # fail
    p_fail = sub.add_parser("fail", help="Mark current step as failed")
    p_fail.add_argument("pipeline_id", help="Pipeline ID")
    p_fail.add_argument("--reason", required=True, help="Failure reason")

    # show
    p_show = sub.add_parser("show", help="Show pipeline details")
    p_show.add_argument("pipeline_id", help="Pipeline ID")

    # list
    p_list = sub.add_parser("list", help="List all pipelines")
    p_list.add_argument(
        "--status",
        choices=["running", "paused", "completed", "failed"],
        help="Filter by status",
    )

    # resume
    p_resume = sub.add_parser("resume", help="Generate resume context")
    p_resume.add_argument("pipeline_id", help="Pipeline ID")

    return parser


def main() -> int:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()

    cmd_map = {
        "new": cmd_new,
        "advance": cmd_advance,
        "advance-parallel": cmd_advance_parallel,
        "fail": cmd_fail,
        "show": cmd_show,
        "list": cmd_list,
        "resume": cmd_resume,
    }

    cmd_func = cmd_map.get(args.command)
    if not cmd_func:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1

    return cmd_func(args)


if __name__ == "__main__":
    sys.exit(main())
