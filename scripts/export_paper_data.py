#!/usr/bin/env python3
"""Export agent performance data for academic paper.

Generates CSV tables and statistical summaries for publication.
Includes bootstrap confidence intervals and effect size calculations.

Usage:
    .venv/bin/python scripts/export_paper_data.py --all
    .venv/bin/python scripts/export_paper_data.py --table
    .venv/bin/python scripts/export_paper_data.py --stats
    .venv/bin/python scripts/export_paper_data.py --output-dir custom/path
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import sys
from datetime import datetime
from pathlib import Path
from statistics import mean, stdev

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.agent_data import ensure_dirs, list_sessions, load_session, PAPER_DIR
from _lib.output import StatusLine
from _lib.scoring import DIMENSIONS, grade


def export_agent_scores_csv(sessions: list[str], output_dir: Path) -> Path:
    """Export agent scores to CSV for paper analysis.

    Columns: session_id, agent, composite, grade, task_completion, code_quality,
             terminal_efficiency, context_utilization, pipeline_compliance,
             error_rate, instruction_adherence, handoff_quality,
             regression_avoidance, engineering_accuracy, collaboration

    Args:
        sessions: List of session IDs to export.
        output_dir: Output directory for CSV files.

    Returns:
        Path to the generated CSV file.
    """
    output_path = output_dir / "agent_scores.csv"

    # Extract all dimension names for header
    dimension_names = sorted(DIMENSIONS.keys()) + ["collaboration"]

    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["session_id", "agent", "composite", "grade"] + dimension_names
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for session_id in sessions:
            session_data = load_session(session_id)
            if not session_data:
                continue

            scorecards = session_data.get("scorecards", {})
            for agent, scorecard in scorecards.items():
                row = {
                    "session_id": session_id,
                    "agent": agent,
                    "composite": scorecard.get("composite_score", 0.0),
                    "grade": scorecard.get("grade", "N/A"),
                }

                # Add all dimension scores
                scores = scorecard.get("scores", {})
                for dim in dimension_names:
                    row[dim] = scores.get(dim, "")

                writer.writerow(row)

    StatusLine.success(f"Exported agent scores to {output_path.name}")
    return output_path


def export_dimension_trends_csv(sessions: list[str], output_dir: Path) -> Path:
    """Export dimension trends to CSV for time series analysis.

    Columns: session_id, agent, dimension, value

    Args:
        sessions: List of session IDs to export.
        output_dir: Output directory for CSV files.

    Returns:
        Path to the generated CSV file.
    """
    output_path = output_dir / "dimension_trends.csv"

    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=["session_id", "agent", "dimension", "value"]
        )
        writer.writeheader()

        for session_id in sessions:
            session_data = load_session(session_id)
            if not session_data:
                continue

            scorecards = session_data.get("scorecards", {})
            for agent, scorecard in scorecards.items():
                scores = scorecard.get("scores", {})
                for dimension, value in scores.items():
                    if value is not None:
                        writer.writerow(
                            {
                                "session_id": session_id,
                                "agent": agent,
                                "dimension": dimension,
                                "value": value,
                            }
                        )

    StatusLine.success(f"Exported dimension trends to {output_path.name}")
    return output_path


def bootstrap_ci(
    values: list[float], confidence: float = 0.95, n_iterations: int = 1000
) -> tuple[float, float]:
    """Calculate bootstrap confidence interval.

    Args:
        values: Sample data.
        confidence: Confidence level (default 0.95 for 95% CI).
        n_iterations: Number of bootstrap iterations.

    Returns:
        Tuple of (lower_bound, upper_bound).
    """
    if len(values) < 2:
        return (0.0, 0.0)

    bootstrap_means = []
    n = len(values)

    for _ in range(n_iterations):
        # Resample with replacement
        resample = random.choices(values, k=n)
        bootstrap_means.append(mean(resample))

    # Sort and get percentiles
    bootstrap_means.sort()
    alpha = 1 - confidence
    lower_idx = int(n_iterations * (alpha / 2))
    upper_idx = int(n_iterations * (1 - alpha / 2))

    return (bootstrap_means[lower_idx], bootstrap_means[upper_idx])


def hedges_g(pre: list[float], post: list[float]) -> float:
    """Calculate Hedges' g effect size.

    Hedges' g is a bias-corrected version of Cohen's d for small samples.

    Args:
        pre: Pre-intervention scores.
        post: Post-intervention scores.

    Returns:
        Effect size (Hedges' g).
    """
    if len(pre) < 2 or len(post) < 2:
        return 0.0

    mean_pre = mean(pre)
    mean_post = mean(post)
    std_pre = stdev(pre)
    std_post = stdev(post)

    # Pooled standard deviation
    n1 = len(pre)
    n2 = len(post)
    pooled_sd = math.sqrt(
        ((n1 - 1) * std_pre**2 + (n2 - 1) * std_post**2) / (n1 + n2 - 2)
    )

    if pooled_sd == 0:
        return 0.0

    # Cohen's d
    cohens_d = (mean_post - mean_pre) / pooled_sd

    # Bias correction factor for Hedges' g
    correction = 1 - (3 / (4 * (n1 + n2) - 9))

    return cohens_d * correction


def export_summary_stats(sessions: list[str], output_dir: Path) -> Path:
    """Export summary statistics with bootstrap CIs.

    Per-agent stats: n_sessions, mean, std, ci_lower, ci_upper, trend

    Args:
        sessions: List of session IDs to analyze.
        output_dir: Output directory for JSON output.

    Returns:
        Path to the generated JSON file.
    """
    output_path = output_dir / "summary_stats.json"

    agent_scores: dict[str, list[float]] = {}

    # Collect composite scores
    for session_id in sessions:
        session_data = load_session(session_id)
        if not session_data:
            continue

        scorecards = session_data.get("scorecards", {})
        for agent, scorecard in scorecards.items():
            composite = scorecard.get("composite_score")
            if composite is not None:
                if agent not in agent_scores:
                    agent_scores[agent] = []
                agent_scores[agent].append(composite)

    # Compute summary stats per agent
    summary: dict[str, dict] = {}

    for agent, scores in sorted(agent_scores.items()):
        if len(scores) < 2:
            summary[agent] = {
                "n_sessions": len(scores),
                "mean": scores[0] if scores else 0.0,
                "std": 0.0,
                "ci_lower": 0.0,
                "ci_upper": 0.0,
                "trend": "insufficient_data",
            }
            continue

        ci_lower, ci_upper = bootstrap_ci(scores)
        summary[agent] = {
            "n_sessions": len(scores),
            "mean": round(mean(scores), 2),
            "std": round(stdev(scores), 2),
            "ci_lower": round(ci_lower, 2),
            "ci_upper": round(ci_upper, 2),
            "trend": "stable",  # Placeholder - actual trend from mann_kendall
        }

    output_data = {
        "generated": datetime.now().isoformat(),
        "sessions_analyzed": len(sessions),
        "agents": summary,
    }

    output_path.write_text(json.dumps(output_data, indent=2) + "\n", encoding="utf-8")
    StatusLine.success(f"Exported summary stats to {output_path.name}")
    return output_path


def print_paper_table(sessions: list[str]) -> None:
    """Print formatted table matching paper §16.1.

    Format:
        Agent            | N   | Mean ± SD  | 95% CI        | Grade
        ---------------- | --- | ---------- | ------------- | -----
        orchestrator     | 45  | 8.2 ± 0.9  | [7.9, 8.5]    | Good
        ...
    """
    agent_scores: dict[str, list[float]] = {}

    # Collect scores
    for session_id in sessions:
        session_data = load_session(session_id)
        if not session_data:
            continue

        scorecards = session_data.get("scorecards", {})
        for agent, scorecard in scorecards.items():
            composite = scorecard.get("composite_score")
            if composite is not None:
                if agent not in agent_scores:
                    agent_scores[agent] = []
                agent_scores[agent].append(composite)

    # Print header
    print("\n" + "=" * 80)
    print("Agent Performance Summary (for Academic Paper)")
    print("=" * 80)
    print(
        f"{'Agent':<20} | {'N':>3} | {'Mean ± SD':>12} | {'95% CI':>15} | {'Grade':<18}"
    )
    print("-" * 80)

    # Print rows
    for agent in sorted(agent_scores.keys()):
        scores = agent_scores[agent]
        n = len(scores)

        if n < 2:
            mean_val = scores[0] if scores else 0.0
            std_val = 0.0
            ci_lower, ci_upper = 0.0, 0.0
        else:
            mean_val = mean(scores)
            std_val = stdev(scores)
            ci_lower, ci_upper = bootstrap_ci(scores)

        grade_str = grade(mean_val)

        print(
            f"{agent:<20} | {n:>3} | {mean_val:>5.2f} ± {std_val:>4.2f} | "
            f"[{ci_lower:>5.2f}, {ci_upper:>5.2f}] | {grade_str:<18}"
        )

    print("=" * 80 + "\n")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Export agent performance data for academic paper"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Export all data (scores CSV, trends CSV, summary stats)",
    )
    parser.add_argument(
        "--table", action="store_true", help="Print formatted paper table"
    )
    parser.add_argument(
        "--stats", action="store_true", help="Export summary statistics JSON"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Custom output directory (default: logs/agent-performance/paper-export)",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Default to --all if nothing specified
    if not args.all and not args.table and not args.stats:
        args.all = True

    ensure_dirs()

    # Determine output directory
    output_dir = args.output_dir if args.output_dir else PAPER_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get all sessions
    all_sessions = list_sessions()
    if not all_sessions:
        StatusLine.warning("No sessions found in logs/agent-performance/sessions/")
        return 1

    StatusLine.info(f"Found {len(all_sessions)} sessions")

    # Export data
    if args.all or args.stats:
        export_summary_stats(all_sessions, output_dir)

    if args.all:
        export_agent_scores_csv(all_sessions, output_dir)
        export_dimension_trends_csv(all_sessions, output_dir)

    if args.table:
        print_paper_table(all_sessions)

    if args.all or args.stats or args.table:
        StatusLine.success(f"Export complete → {output_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
