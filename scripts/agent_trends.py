#!/usr/bin/env python3
"""Agent trends — time series analysis and degradation detection.

Computes performance trends across sessions using Mann-Kendall test.
Flags agents with declining scores or degradation patterns.

Usage:
    .venv/bin/python scripts/agent_trends.py --weekly
    .venv/bin/python scripts/agent_trends.py --monthly
    .venv/bin/python scripts/agent_trends.py --agent ops
    .venv/bin/python scripts/agent_trends.py --alert
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, stdev

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.agent_data import ensure_dirs, list_sessions, load_session, TRENDS_DIR
from _lib.output import print_json, print_table, StatusLine


def mann_kendall_trend(values: list[float]) -> tuple[str, float]:
    """Mann-Kendall trend test for monotonic trends.

    Counts concordant (increasing) vs discordant (decreasing) pairs.
    Returns trend direction and S statistic.

    Args:
        values: Time series data (chronological order).

    Returns:
        Tuple of (direction, S_statistic).
        direction: "increasing", "decreasing", "no_trend", or "insufficient_data"
        S: Mann-Kendall S statistic (positive = increasing, negative = decreasing)
    """
    n = len(values)
    if n < 3:
        return ("insufficient_data", 0.0)

    # Compute S statistic
    S = 0.0
    for i in range(n - 1):
        for j in range(i + 1, n):
            if values[j] > values[i]:
                S += 1
            elif values[j] < values[i]:
                S -= 1

    # Critical value for significance (simplified, n >= 10)
    # For small n, use a more lenient threshold
    if n < 10:
        threshold = n * (n - 1) / 4  # ~50% of pairs
    else:
        threshold = 1.96 * ((n * (n - 1) * (2 * n + 5)) / 18) ** 0.5

    # Determine trend direction
    if S > threshold:
        direction = "increasing"
    elif S < -threshold:
        direction = "decreasing"
    else:
        direction = "no_trend"

    return (direction, S)


def compute_consecutive_decline(values: list[float]) -> int:
    """Count consecutive declining values from the end of the series.

    Args:
        values: Time series data.

    Returns:
        Number of consecutive declines at the end.
    """
    if len(values) < 2:
        return 0

    count = 0
    for i in range(len(values) - 1, 0, -1):
        if values[i] < values[i - 1]:
            count += 1
        else:
            break

    return count


def compute_trends(
    sessions: list[str], agent_name: str | None = None
) -> dict[str, dict]:
    """Compute trend statistics for agents across sessions.

    Args:
        sessions: List of session IDs to analyze.
        agent_name: If specified, compute trends for single agent only.

    Returns:
        Dict mapping agent name to trend statistics.
    """
    agent_scores: dict[str, list[float]] = defaultdict(list)

    for session_id in sessions:
        session_data = load_session(session_id)
        if not session_data:
            continue

        agent_scores_data = session_data.get("agent_scores", {})
        for agent, score_record in agent_scores_data.items():
            if agent_name and agent != agent_name:
                continue

            composite = score_record.get("composite")
            if composite is not None:
                agent_scores[agent].append(composite)

    trends: dict[str, dict] = {}
    all_agents = [agent_name] if agent_name else sorted(agent_scores.keys())

    for agent in all_agents:
        scores = agent_scores.get(agent, [])
        if len(scores) < 2:
            trends[agent] = {
                "sessions_analyzed": len(scores),
                "composite_scores": scores,
                "mean": scores[0] if scores else 0.0,
                "std_dev": 0.0,
                "min": scores[0] if scores else 0.0,
                "max": scores[0] if scores else 0.0,
                "latest": scores[-1] if scores else 0.0,
                "trend": "insufficient_data",
                "mann_kendall_s": 0.0,
                "consecutive_decline": 0,
            }
            continue

        trend_direction, mk_s = mann_kendall_trend(scores)
        consecutive_decline = compute_consecutive_decline(scores)

        trends[agent] = {
            "sessions_analyzed": len(scores),
            "composite_scores": scores,
            "mean": round(mean(scores), 2),
            "std_dev": round(stdev(scores), 2) if len(scores) > 1 else 0.0,
            "min": round(min(scores), 2),
            "max": round(max(scores), 2),
            "latest": round(scores[-1], 2),
            "trend": trend_direction,
            "mann_kendall_s": round(mk_s, 1),
            "consecutive_decline": consecutive_decline,
        }

    return trends


def check_alerts(trends: dict[str, dict]) -> list[dict]:
    """Check for agents with concerning performance trends.

    Args:
        trends: Dict of agent trend statistics.

    Returns:
        List of alert dicts with agent, reason, severity.
    """
    alerts = []

    for agent, stats in trends.items():
        if stats["trend"] == "insufficient_data":
            continue

        if stats["mean"] < 5.0:
            alerts.append(
                {
                    "agent": agent,
                    "reason": f"Mean score below 5.0 (actual: {stats['mean']})",
                    "severity": "high",
                    "latest_score": stats["latest"],
                }
            )

        if stats["consecutive_decline"] >= 3:
            alerts.append(
                {
                    "agent": agent,
                    "reason": f"{stats['consecutive_decline']} consecutive declining scores",
                    "severity": "medium",
                    "latest_score": stats["latest"],
                }
            )

        if stats["trend"] == "decreasing":
            alerts.append(
                {
                    "agent": agent,
                    "reason": "Statistically significant decreasing trend detected",
                    "severity": "medium",
                    "latest_score": stats["latest"],
                }
            )

    return alerts


def save_trends(period: str, trends_data: dict, agent_name: str | None = None) -> Path:
    """Save trends data to TRENDS_DIR.

    Args:
        period: "weekly" or "monthly"
        trends_data: Full trends output dict
        agent_name: Optional agent name for filename

    Returns:
        Path to saved file
    """
    ensure_dirs()

    filename = f"trends_{period}.json"
    if agent_name:
        filename = f"trends_{agent_name}_{period}.json"

    output_path = TRENDS_DIR / filename
    output_path.write_text(json.dumps(trends_data, indent=2) + "\n", encoding="utf-8")

    return output_path


def format_trends(trends: dict[str, dict]) -> None:
    """Pretty-print trends to console.

    Args:
        trends: Dict of agent trend statistics
    """
    if not trends:
        StatusLine.warn("No trend data to display")
        return

    # Build table rows
    headers = [
        "Agent",
        "Sessions",
        "Mean",
        "±SD",
        "Min",
        "Max",
        "Latest",
        "Trend",
        "Decline",
    ]
    rows = []

    for agent in sorted(trends.keys()):
        stats = trends[agent]
        trend_symbol = {
            "increasing": "↑",
            "decreasing": "↓",
            "no_trend": "→",
            "insufficient_data": "?",
        }.get(stats["trend"], "?")

        rows.append(
            [
                agent,
                str(stats["sessions_analyzed"]),
                f"{stats['mean']:.1f}",
                f"{stats['std_dev']:.1f}",
                f"{stats['min']:.1f}",
                f"{stats['max']:.1f}",
                f"{stats['latest']:.1f}",
                trend_symbol,
                (
                    str(stats["consecutive_decline"])
                    if stats["consecutive_decline"] > 0
                    else "-"
                ),
            ]
        )

    print_table(headers, rows)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze agent performance trends over time"
    )
    parser.add_argument("--weekly", action="store_true", help="Analyze last 7 sessions")
    parser.add_argument(
        "--monthly", action="store_true", help="Analyze last 30 sessions"
    )
    parser.add_argument("--agent", type=str, help="Analyze single agent only")
    parser.add_argument(
        "--alert", action="store_true", help="Flag agents with degrading performance"
    )
    parser.add_argument(
        "--output", type=Path, help="Save output to file (default: TRENDS_DIR)"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output JSON only (no table)"
    )

    args = parser.parse_args()

    if not args.weekly and not args.monthly and not args.alert:
        args.weekly = True

    ensure_dirs()

    all_sessions = list_sessions()
    if not all_sessions:
        StatusLine.warn("No sessions found")
        return 1

    if args.monthly:
        sessions = all_sessions[-30:] if len(all_sessions) > 30 else all_sessions
        period = "monthly"
    else:
        sessions = all_sessions[-7:] if len(all_sessions) > 7 else all_sessions
        period = "weekly"

    StatusLine.info(f"Analyzing {len(sessions)} sessions ({period})")

    trends = compute_trends(sessions, agent_name=args.agent)

    if not trends:
        StatusLine.warn("No trend data available")
        return 1

    alerts = check_alerts(trends)

    output = {
        "period": period,
        "generated": datetime.now().isoformat(),
        "sessions_analyzed": len(sessions),
        "agent_trends": trends,
        "alerts": alerts,
    }

    # Save to file
    if args.output:
        args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
        StatusLine.ok(f"Saved trends to {args.output}")
    else:
        output_path = save_trends(period, output, agent_name=args.agent)
        StatusLine.ok(f"Saved trends to {output_path.relative_to(Path.cwd())}")

    # Display output
    if args.json:
        print_json(output)
    else:
        format_trends(trends)

    # Show alerts
    if args.alert and alerts:
        StatusLine.warn(f"Found {len(alerts)} alerts:")
        for alert in alerts:
            severity_marker = "⚠️" if alert["severity"] == "medium" else "🚨"
            print(
                f"  {severity_marker} {alert['agent']}: {alert['reason']} (latest: {alert['latest_score']})"
            )
    elif args.alert:
        StatusLine.ok("No performance alerts")

    return 0


if __name__ == "__main__":
    sys.exit(main())
