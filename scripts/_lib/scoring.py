"""Scoring framework constants and computation.

Implements the 11-dimension scoring framework from agent-evolver plan §8.
"""

from __future__ import annotations

# Dimension weights (normal agents)
DIMENSIONS: dict[str, float] = {
    "task_completion": 0.18,
    "code_quality": 0.12,
    "terminal_efficiency": 0.08,
    "context_utilization": 0.10,
    "pipeline_compliance": 0.10,
    "error_rate": 0.08,
    "instruction_adherence": 0.10,
    "handoff_quality": 0.05,
    "regression_avoidance": 0.04,
    "engineering_accuracy": 0.15,
    # collaboration is experimental, not weighted yet
}

# Weight overrides for structural-engineer and structural-math agents
STRUCTURAL_WEIGHT_OVERRIDES: dict[str, float] = {
    "task_completion": 0.18,
    "code_quality": 0.08,
    "terminal_efficiency": 0.05,
    "context_utilization": 0.10,
    "pipeline_compliance": 0.10,
    "error_rate": 0.08,
    "instruction_adherence": 0.10,
    "handoff_quality": 0.05,
    "regression_avoidance": 0.01,
    "engineering_accuracy": 0.25,  # Boosted for structural agents
}

# Auto-scored dimensions (no human input needed)
AUTO_SCORED_DIMENSIONS: set[str] = {
    "terminal_efficiency",
    "pipeline_compliance",
    "error_rate",
    "engineering_accuracy",
    "instruction_adherence",
    "handoff_quality",
    "regression_avoidance",
}

# Auto-overridable dimensions (auto by default, manual override allowed)
AUTO_OVERRIDABLE_DIMENSIONS: set[str] = {
    "handoff_quality",
    "regression_avoidance",
    "code_quality",
}

# Manual dimensions (require human scoring)
MANUAL_DIMENSIONS: set[str] = {
    "task_completion",
    "context_utilization",
    "collaboration",
}


def composite_score(
    scores: dict[str, float | None],
    agent_name: str = "",
) -> float:
    """Compute weighted composite score from 11 dimensions.

    Args:
        scores: Dict mapping dimension name to score [0, 10] or None.
        agent_name: Agent name for structural weight override detection.

    Returns:
        Composite score [0, 10].
    """
    # Choose weights based on agent type
    is_structural = agent_name in {"structural-engineer", "structural-math"}
    weights = STRUCTURAL_WEIGHT_OVERRIDES if is_structural else DIMENSIONS

    # Compute weighted sum, skipping None dimensions
    total_score = 0.0
    total_weight = 0.0

    for dim, weight in weights.items():
        score_val = scores.get(dim)
        if score_val is not None:
            total_score += weight * score_val
            total_weight += weight

    # Renormalize if some dimensions were missing
    if total_weight == 0:
        return 0.0

    return total_score / total_weight


def grade(composite: float) -> str:
    """Map composite score to letter grade.

    Args:
        composite: Composite score [0, 10].

    Returns:
        Grade string: Excellent, Good, Needs Improvement, or Critical.
    """
    if composite >= 9.0:
        return "Excellent"
    elif composite >= 7.0:
        return "Good"
    elif composite >= 5.0:
        return "Needs Improvement"
    else:
        return "Critical"
