#!/usr/bin/env python3
"""Agent scorer — score agents on 11 performance dimensions.

Combines auto-scored metrics (terminal efficiency, pipeline compliance,
error rate, engineering accuracy, instruction adherence) with manual
assessments (task completion, code quality, context utilization,
handoff quality, regression avoidance, collaboration).

Usage:
    # Auto-score only (runs at session end automatically)
    .venv/bin/python scripts/agent_scorer.py --auto-only --session "2026-04-01T14:30"

    # Full scoring (adds manual dimensions)
    .venv/bin/python scripts/agent_scorer.py --session "2026-04-01T14:30" \
      --agent backend --task-completion 8 --code-quality 9 --context-utilization 7 \
      --handoff-quality 7 --regression-avoidance 8

    # View latest scores
    .venv/bin/python scripts/agent_scorer.py --view
    .venv/bin/python scripts/agent_scorer.py --view --agent backend
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.agent_data import (
    load_scorecard_index,
    load_session,
    save_scorecard_index,
    save_session,
)
from _lib.agent_registry import discover_agents
from _lib.output import StatusLine, print_table
from _lib.scoring import (
    AUTO_SCORED_DIMENSIONS,
    DIMENSIONS,
    composite_score,
    grade,
)


def auto_score_agent(session_data: dict, agent_name: str) -> dict[str, float | None]:
    """Compute auto-scored dimensions from session data.

    Args:
        session_data: Session data dict from agent_session_collector.
        agent_name: Agent name for structural weighting.

    Returns:
        Dict mapping dimension name to score [0, 10] or None.
    """
    scores: dict[str, float | None] = {}

    # 1. Terminal efficiency (prescribed command usage)
    # Since we don't track terminal commands yet, default to 7.0 (neutral)
    terminal_commands = session_data.get("terminal_commands", [])
    if terminal_commands:
        prescribed = sum(1 for cmd in terminal_commands if cmd.get("prescribed", False))
        total = len(terminal_commands)
        scores["terminal_efficiency"] = (prescribed / total * 10) if total > 0 else 7.0
    else:
        scores["terminal_efficiency"] = 7.0

    # 2. Pipeline compliance (standard artifacts present)
    pipeline_score = 0.0
    commits = session_data.get("commits", [])
    test_results = session_data.get("test_results", {})
    files_changed = session_data.get("files_changed", {})

    # Check for pipeline artifacts
    if commits:
        pipeline_score += 2.0  # Commits present

    if test_results.get("passed", 0) > 0 or test_results.get("failed", 0) > 0:
        pipeline_score += 2.0  # Tests run

    # Check if files were read before write (proxy: session collector ran)
    if "collection_timestamp" in session_data:
        pipeline_score += 2.0

    # Check for session-end docs updates
    doc_files = [
        "docs/TASKS.md",
        "docs/planning/next-session-brief.md",
        "docs/WORKLOG.md",
    ]
    if any(f in files_changed for f in doc_files):
        pipeline_score += 2.0

    # Check for feedback logging
    feedback_files = [f for f in files_changed if "feedback" in f.lower()]
    if feedback_files:
        pipeline_score += 2.0

    scores["pipeline_compliance"] = min(pipeline_score, 10.0)

    # 3. Error rate (from test results)
    passed = test_results.get("passed", 0)
    failed = test_results.get("failed", 0)
    total_tests = passed + failed

    if total_tests > 0:
        pass_rate = passed / total_tests
        scores["error_rate"] = pass_rate * 10
    else:
        scores["error_rate"] = None  # No test data

    # 4. Engineering accuracy (structural code changes + tests pass)
    structural_files = [
        "Python/structural_lib/codes/is456/",
        "Python/structural_lib/core/",
        "Python/structural_lib/services/",
    ]

    has_structural_changes = any(
        any(pattern in filepath for pattern in structural_files)
        for filepath in files_changed
    )

    if has_structural_changes:
        # If structural changes, high test pass rate = high accuracy
        if passed > 0 and failed == 0:
            scores["engineering_accuracy"] = 9.0
        elif passed > 0 and pass_rate >= 0.9:
            scores["engineering_accuracy"] = 8.0
        elif passed > 0 and pass_rate >= 0.7:
            scores["engineering_accuracy"] = 7.0
        else:
            scores["engineering_accuracy"] = 6.0
    else:
        scores["engineering_accuracy"] = None  # No structural changes

    # 5. Instruction adherence (from compliance data if available)
    compliance_data = session_data.get("compliance", {})
    if compliance_data and agent_name in compliance_data:
        compliance_rate = compliance_data[agent_name].get("rate", 0.0)
        scores["instruction_adherence"] = compliance_rate * 10
    else:
        scores["instruction_adherence"] = None  # No compliance data yet

    return scores


def score_session(
    session_id: str,
    agent_name: str,
    auto_only: bool = False,
    manual_scores: dict[str, float] | None = None,
) -> dict:
    """Score a session and update records.

    Args:
        session_id: Session identifier.
        agent_name: Agent name.
        auto_only: If True, only compute auto-scored dimensions.
        manual_scores: Manual dimension scores (0-10).

    Returns:
        Updated session data with scores.
    """
    # Load session data
    session_data = load_session(session_id)
    if not session_data:
        StatusLine.fail(f"Session {session_id} not found")
        sys.exit(1)

    # Compute auto-scores
    auto_scores = auto_score_agent(session_data, agent_name)

    # Merge manual scores if provided
    all_scores = auto_scores.copy()
    if not auto_only and manual_scores:
        all_scores.update(manual_scores)

    # Compute composite score
    composite = composite_score(all_scores, agent_name)
    score_grade = grade(composite)

    # Build score record
    score_record = {
        "agent": agent_name,
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "scores": all_scores,
        "composite": composite,
        "grade": score_grade,
    }

    # Update session data with score
    if "agent_scores" not in session_data:
        session_data["agent_scores"] = {}
    session_data["agent_scores"][agent_name] = score_record

    # Save updated session
    save_session(session_id, session_data)

    # Update scorecard index (latest score per agent)
    scorecard = load_scorecard_index()
    if agent_name not in scorecard:
        scorecard[agent_name] = []

    scorecard[agent_name].append(score_record)
    # Keep last 20 scores per agent
    scorecard[agent_name] = scorecard[agent_name][-20:]

    save_scorecard_index(scorecard)

    return score_record


def view_scores(agent_name: str | None = None) -> None:
    """Display current agent scores in table format.

    Args:
        agent_name: If provided, show only this agent's scores.
    """
    scorecard = load_scorecard_index()

    if not scorecard:
        StatusLine.warn("No scores available yet")
        return

    # Filter by agent if specified
    if agent_name:
        if agent_name not in scorecard:
            StatusLine.warn(f"No scores for agent '{agent_name}'")
            return
        agents_to_show = {agent_name: scorecard[agent_name]}
    else:
        agents_to_show = scorecard

    # Build table rows
    rows = []
    for agent, score_records in sorted(agents_to_show.items()):
        if not score_records:
            continue

        # Get latest score
        latest = score_records[-1]
        scores = latest["scores"]

        row = [
            agent,
            f"{latest['composite']:.2f}",
            latest["grade"],
            (
                f"{scores.get('task_completion', 0) or '-':.1f}"
                if scores.get("task_completion")
                else "-"
            ),
            (
                f"{scores.get('code_quality', 0) or '-':.1f}"
                if scores.get("code_quality")
                else "-"
            ),
            (
                f"{scores.get('terminal_efficiency', 0) or '-':.1f}"
                if scores.get("terminal_efficiency")
                else "-"
            ),
            (
                f"{scores.get('pipeline_compliance', 0) or '-':.1f}"
                if scores.get("pipeline_compliance")
                else "-"
            ),
            (
                f"{scores.get('engineering_accuracy', 0) or '-':.1f}"
                if scores.get("engineering_accuracy")
                else "-"
            ),
        ]
        rows.append(row)

    # Print table
    headers = [
        "Agent",
        "Composite",
        "Grade",
        "Task",
        "Quality",
        "Terminal",
        "Pipeline",
        "Engineering",
    ]

    print("\nAgent Scorecard (Latest Scores)\n")
    print_table(headers, rows)

    # Print legend
    print("\nLegend:")
    print("  Excellent: 9.0+")
    print("  Good: 7.0-8.9")
    print("  Needs Improvement: 5.0-6.9")
    print("  Critical: <5.0")
    print()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Score agents on 11 performance dimensions"
    )

    parser.add_argument(
        "--session",
        type=str,
        help="Session ID to score (e.g., 2026-04-01T14:30)",
    )

    parser.add_argument(
        "--agent",
        type=str,
        help="Agent name to score",
    )

    parser.add_argument(
        "--auto-only",
        action="store_true",
        help="Only compute auto-scored dimensions (no manual input)",
    )

    parser.add_argument(
        "--view",
        action="store_true",
        help="View current agent scores",
    )

    # Manual scoring dimensions
    parser.add_argument(
        "--task-completion",
        type=float,
        metavar="SCORE",
        help="Task completion score (0-10)",
    )

    parser.add_argument(
        "--code-quality",
        type=float,
        metavar="SCORE",
        help="Code quality score (0-10)",
    )

    parser.add_argument(
        "--context-utilization",
        type=float,
        metavar="SCORE",
        help="Context utilization score (0-10)",
    )

    parser.add_argument(
        "--handoff-quality",
        type=float,
        metavar="SCORE",
        help="Handoff quality score (0-10)",
    )

    parser.add_argument(
        "--regression-avoidance",
        type=float,
        metavar="SCORE",
        help="Regression avoidance score (0-10)",
    )

    parser.add_argument(
        "--collaboration",
        type=float,
        metavar="SCORE",
        help="Collaboration score (0-10)",
    )

    return parser.parse_args()


def validate_score(value: float | None, name: str) -> None:
    """Validate a score is in [0, 10] range.

    Args:
        value: Score value.
        name: Dimension name for error message.
    """
    if value is not None and (value < 0 or value > 10):
        StatusLine.fail(f"{name} must be between 0 and 10, got {value}")
        sys.exit(1)


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # View mode
    if args.view:
        view_scores(args.agent)
        return 0

    # Scoring mode requires --session and --agent
    if not args.session:
        StatusLine.fail("--session is required for scoring")
        return 1

    if not args.agent:
        StatusLine.fail("--agent is required for scoring")
        return 1

    # Validate agent exists
    agents = discover_agents()
    if args.agent not in agents:
        StatusLine.fail(f"Unknown agent: {args.agent}")
        StatusLine.warn(f"Available: {', '.join(sorted(agents.keys()))}")
        return 1

    # Collect manual scores
    manual_scores: dict[str, float] = {}

    if args.task_completion is not None:
        validate_score(args.task_completion, "task-completion")
        manual_scores["task_completion"] = args.task_completion

    if args.code_quality is not None:
        validate_score(args.code_quality, "code-quality")
        manual_scores["code_quality"] = args.code_quality

    if args.context_utilization is not None:
        validate_score(args.context_utilization, "context-utilization")
        manual_scores["context_utilization"] = args.context_utilization

    if args.handoff_quality is not None:
        validate_score(args.handoff_quality, "handoff-quality")
        manual_scores["handoff_quality"] = args.handoff_quality

    if args.regression_avoidance is not None:
        validate_score(args.regression_avoidance, "regression-avoidance")
        manual_scores["regression_avoidance"] = args.regression_avoidance

    if args.collaboration is not None:
        validate_score(args.collaboration, "collaboration")
        manual_scores["collaboration"] = args.collaboration

    # Require manual scores unless --auto-only
    if not args.auto_only and not manual_scores:
        StatusLine.warn(
            "No manual scores provided. Use --auto-only for auto-scoring, "
            "or provide manual scores via --task-completion, --code-quality, etc."
        )
        return 1

    # Score the session
    try:
        score_record = score_session(
            args.session,
            args.agent,
            args.auto_only,
            manual_scores if manual_scores else None,
        )

        StatusLine.ok(
            f"Scored {args.agent} for session {args.session}: "
            f"{score_record['composite']:.2f} ({score_record['grade']})"
        )

        # Print score breakdown
        print("\nScore Breakdown:")
        scores = score_record["scores"]
        for dim in sorted(DIMENSIONS.keys()):
            score_val = scores.get(dim)
            if score_val is not None:
                auto_marker = " (auto)" if dim in AUTO_SCORED_DIMENSIONS else ""
                print(f"  {dim:25s} {score_val:5.1f}{auto_marker}")
            else:
                print(f"  {dim:25s}     - (no data)")

        return 0

    except Exception as e:
        StatusLine.fail(f"Failed to score session: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
