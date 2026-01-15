#!/usr/bin/env python3
"""
Predictive Velocity Modeling - TASK-287

Predicts development velocity trends using Exponential Moving Average (EMA)
and alerts before burnout occurs.

Usage:
    python scripts/predict_velocity.py [--days 7] [--output metrics/velocity_predictions.json]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import NamedTuple


class VelocityPrediction(NamedTuple):
    """Velocity prediction result."""

    current_daily: float
    ema_7d: float
    ema_30d: float
    trend_per_day: float
    predicted_7d: float
    predicted_30d: float
    risk_level: str
    recommendation: str


class VelocityPredictor:
    """Predicts development velocity trends using EMA."""

    # Burnout thresholds (commits per day)
    THRESHOLDS = {
        "sustainable": (0, 15),
        "elevated": (15, 40),
        "high": (40, 80),
        "critical": (80, float("inf")),
    }

    def __init__(self, repo_path: Path | None = None):
        """Initialize with repository path."""
        self.repo_path = repo_path or Path.cwd()

    def get_daily_commits(self, days: int = 60) -> list[int]:
        """Get commit counts per day for the last N days."""
        daily_counts = []
        today = datetime.now().date()

        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            next_date = date + timedelta(days=1)
            next_date_str = next_date.strftime("%Y-%m-%d")

            result = subprocess.run(
                [
                    "git",
                    "rev-list",
                    "--count",
                    "HEAD",
                    f"--since={date_str}",
                    f"--until={next_date_str}",
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                check=False,
            )

            count = int(result.stdout.strip()) if result.returncode == 0 else 0
            daily_counts.append(count)

        return list(reversed(daily_counts))

    def calculate_ema(self, values: list[float], period: int) -> float:
        """Calculate Exponential Moving Average."""
        if not values:
            return 0.0

        alpha = 2 / (period + 1)
        ema = float(values[0])

        for value in values[1:]:
            ema = alpha * value + (1 - alpha) * ema

        return ema

    def calculate_trend(self, ema_7d: float, ema_30d: float) -> float:
        """Calculate velocity trend (change per day)."""
        # Trend is the difference normalized by period
        return (ema_7d - ema_30d) / 23.0  # 30 - 7 days

    def assess_risk(self, velocity: float) -> tuple[str, str]:
        """Assess burnout risk based on velocity."""
        if velocity <= self.THRESHOLDS["sustainable"][1]:
            return "🟢 LOW", "Velocity is sustainable. Continue normal pace."

        if velocity <= self.THRESHOLDS["elevated"][1]:
            return "🟡 MODERATE", "Velocity elevated. Monitor for fatigue."

        if velocity <= self.THRESHOLDS["high"][1]:
            return (
                "🟠 HIGH",
                "Velocity high. Consider reducing workload, increasing breaks.",
            )

        return (
            "🔴 CRITICAL",
            "Velocity unsustainable. STOP and reassess. Risk of burnout.",
        )

    def predict(self, days_ahead: int = 7) -> VelocityPrediction:
        """Generate velocity prediction."""
        # Get historical data
        daily_commits = self.get_daily_commits(60)

        if not daily_commits or sum(daily_commits) == 0:
            return VelocityPrediction(
                current_daily=0,
                ema_7d=0,
                ema_30d=0,
                trend_per_day=0,
                predicted_7d=0,
                predicted_30d=0,
                risk_level="🟢 LOW",
                recommendation="No recent activity. Start coding!",
            )

        # Calculate current metrics
        current_daily = sum(daily_commits[-7:]) / 7
        ema_7d = self.calculate_ema(daily_commits[-14:], 7)
        ema_30d = self.calculate_ema(daily_commits, 30)

        # Calculate trend
        trend = self.calculate_trend(ema_7d, ema_30d)

        # Predict future velocity
        predicted_7d = max(0, ema_7d + (trend * 7))
        predicted_30d = max(0, ema_7d + (trend * 30))

        # Assess risk based on predicted velocity
        risk_level, recommendation = self.assess_risk(predicted_7d)

        return VelocityPrediction(
            current_daily=round(current_daily, 1),
            ema_7d=round(ema_7d, 1),
            ema_30d=round(ema_30d, 1),
            trend_per_day=round(trend, 2),
            predicted_7d=round(predicted_7d, 1),
            predicted_30d=round(predicted_30d, 1),
            risk_level=risk_level,
            recommendation=recommendation,
        )

    def generate_report(self, prediction: VelocityPrediction) -> str:
        """Generate human-readable report."""
        trend_direction = "📈 Increasing" if prediction.trend_per_day > 0 else "📉 Decreasing" if prediction.trend_per_day < 0 else "➡️ Stable"

        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║              VELOCITY PREDICTION REPORT                          ║
║              Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}                          ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  📊 Current Metrics                                               ║
║  ├── Daily Average (7d):    {prediction.current_daily:>6.1f} commits/day              ║
║  ├── EMA (7-day):           {prediction.ema_7d:>6.1f} commits/day              ║
║  ├── EMA (30-day):          {prediction.ema_30d:>6.1f} commits/day              ║
║  └── Trend:                 {trend_direction:>20}              ║
║                                                                   ║
║  🔮 Predictions                                                   ║
║  ├── 7-day forecast:        {prediction.predicted_7d:>6.1f} commits/day              ║
║  └── 30-day forecast:       {prediction.predicted_30d:>6.1f} commits/day              ║
║                                                                   ║
║  ⚠️  Risk Assessment                                              ║
║  ├── Risk Level:            {prediction.risk_level:<30}   ║
║  └── Recommendation:                                              ║
║      {prediction.recommendation:<55}  ║
║                                                                   ║
╚══════════════════════════════════════════════════════════════════╝

THRESHOLDS:
  • Sustainable:  0-15 commits/day  (🟢 Healthy pace)
  • Elevated:    16-40 commits/day  (🟡 Monitor closely)
  • High:        41-80 commits/day  (🟠 Reduce workload)
  • Critical:     >80 commits/day   (🔴 Stop and reassess)
"""
        return report


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Predict development velocity and burnout risk"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Days ahead to predict (default: 7)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON file path",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of report",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output, only return exit code",
    )

    args = parser.parse_args()

    # Run prediction
    predictor = VelocityPredictor()
    prediction = predictor.predict(args.days)

    # Output results
    if args.json:
        result = {
            "timestamp": datetime.now().isoformat(),
            "current_daily": prediction.current_daily,
            "ema_7d": prediction.ema_7d,
            "ema_30d": prediction.ema_30d,
            "trend_per_day": prediction.trend_per_day,
            "predicted_7d": prediction.predicted_7d,
            "predicted_30d": prediction.predicted_30d,
            "risk_level": prediction.risk_level,
            "recommendation": prediction.recommendation,
        }
        if not args.quiet:
            print(json.dumps(result, indent=2))
    elif not args.quiet:
        print(predictor.generate_report(prediction))

    # Save to file if requested
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        result = {
            "timestamp": datetime.now().isoformat(),
            "current_daily": prediction.current_daily,
            "ema_7d": prediction.ema_7d,
            "ema_30d": prediction.ema_30d,
            "trend_per_day": prediction.trend_per_day,
            "predicted_7d": prediction.predicted_7d,
            "predicted_30d": prediction.predicted_30d,
            "risk_level": prediction.risk_level,
            "recommendation": prediction.recommendation,
        }
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        if not args.quiet:
            print(f"\n✅ Saved to {args.output}")

    # Return exit code based on risk
    if "CRITICAL" in prediction.risk_level:
        return 2
    if "HIGH" in prediction.risk_level:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
