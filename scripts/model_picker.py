#!/usr/bin/env python3
"""Recommend a GPT-5.6 model and reasoning effort for a repository task.

When to use: Before choosing a model for a new bounded repository task.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / "agents" / "model_policy.json"

REPETITIVE = {
    "classify",
    "extract",
    "format",
    "formatting",
    "index",
    "list",
    "metadata",
    "search",
    "status",
    "summary",
    "summarize",
    "sync",
    "typo",
}
BOUNDED = {
    "assertion",
    "boilerplate",
    "docs",
    "documentation",
    "fixture",
    "json",
    "lint",
    "mechanical",
    "regenerate",
    "repetitive",
    "test",
    "worklog",
}
IMPLEMENTATION = {
    "api",
    "backend",
    "bug",
    "code",
    "component",
    "fastapi",
    "fix",
    "frontend",
    "implement",
    "python",
    "react",
    "refactor",
}
COMPLEX = {
    "ambiguous",
    "architecture",
    "comprehensive",
    "cross-layer",
    "diagnose",
    "intermittent",
    "migration",
    "performance",
    "race",
    "research",
    "root-cause",
    "unknown",
}
PLANNING = {"brainstorm", "plan", "planning", "roadmap", "strategy"}
IMPORTANT = {"complicated", "critical", "high-value", "important"}
HIGH_RISK = {
    "authorization",
    "capacity",
    "clause",
    "compliance",
    "destructive",
    "formula",
    "is456",
    "permission",
    "production",
    "reinforcement",
    "release",
    "security",
    "structural",
}


@dataclass(frozen=True)
class ModelRecommendation:
    profile: str
    model: str
    reasoning_effort: str
    relative_token_rate: int
    approval_required: bool
    fallback_profile: str
    fallback_requires_approval: bool
    rationale: str
    escalation_trigger: str


def _load_policy() -> dict:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def _tokens(query: str) -> set[str]:
    return {token for token in re.split(r"[^a-z0-9-]+", query.lower()) if token}


def _profile(policy: dict, profile_id: str) -> dict:
    return next(
        profile for profile in policy["profiles"] if profile["id"] == profile_id
    )


def recommend(
    query: str,
    *,
    risk: str = "auto",
    repeatable: bool = False,
    ambiguous: bool = False,
    important: bool = False,
    orchestrator: bool = False,
) -> ModelRecommendation:
    policy = _load_policy()
    tokens = _tokens(query)

    is_high_risk = risk in {"high", "critical"} or bool(tokens & HIGH_RISK)
    is_complex = ambiguous or bool(tokens & COMPLEX)
    is_repetitive = repeatable or bool(tokens & REPETITIVE)
    is_bounded = bool(tokens & BOUNDED)
    is_implementation = bool(tokens & IMPLEMENTATION)
    is_planning = bool(tokens & PLANNING)
    is_important = important or bool(tokens & IMPORTANT)

    if orchestrator:
        selected, fallback = "terra-medium", "terra-high"
        rationale = (
            "Terra Medium is the efficient advisory parent profile when the user has "
            "not selected one; an active user selection always takes precedence."
        )
    elif risk == "critical" or is_important or ambiguous:
        selected, fallback = "terra-high", "sol-high"
        rationale = (
            "Start important or explicitly complicated work on Terra High; request "
            "approval before escalating to Sol High."
        )
    elif is_planning and not is_bounded and not is_repetitive:
        selected, fallback = "terra-medium", "terra-high"
        rationale = (
            "Substantial planning normally fits Terra Medium; use Terra High only "
            "after a concrete quality gap."
        )
    elif is_high_risk or is_complex:
        selected, fallback = "terra-high", "sol-high"
        rationale = (
            "Start complex or high-risk implementation on Terra High; Sol High is "
            "pre-authorized if a concrete quality gap remains."
        )
    elif is_repetitive and not is_implementation:
        selected, fallback = "luna-low", "luna-medium"
        rationale = (
            "The task is clear and repeatable, which is Luna's most efficient workload."
        )
    elif is_bounded and is_implementation:
        selected, fallback = "luna-high", "terra-low"
        rationale = "The code work is bounded and pattern-driven; try Luna high before moving tiers."
    elif is_bounded:
        selected, fallback = "luna-medium", "terra-low"
        rationale = "The acceptance boundary is explicit and needs moderate checking."
    elif is_implementation:
        selected, fallback = "terra-medium", "terra-high"
        rationale = "Normal implementation benefits from Terra's balanced tool use and judgment."
    else:
        selected, fallback = "terra-medium", "terra-high"
        rationale = "The task lacks enough low-risk structure for an automatic Luna recommendation."

    if risk == "low" and selected.startswith("terra") and not is_complex:
        selected, fallback = "luna-medium", "terra-low"
        rationale = "Explicit low risk allows a cheaper Luna-first attempt."

    selected_profile = _profile(policy, selected)
    fallback_profile = _profile(policy, fallback)
    relative_rate = policy["relative_token_rates"][selected_profile["model"]]

    return ModelRecommendation(
        profile=selected,
        model=selected_profile["model"],
        reasoning_effort=selected_profile["reasoning"],
        relative_token_rate=relative_rate,
        approval_required=selected_profile["approval_required"],
        fallback_profile=fallback,
        fallback_requires_approval=fallback_profile["approval_required"],
        rationale=rationale,
        escalation_trigger=(
            "Escalate only after a concrete quality gap, unresolved ambiguity, failed targeted "
            "verification, or a safety boundary the selected profile cannot resolve."
        ),
    )


def _print_recommendation(result: ModelRecommendation, query: str) -> None:
    print(f'Model recommendation: "{query}"')
    print(f"  Profile: {result.profile}")
    print(f"  Model: {result.model}")
    print(f"  Reasoning: {result.reasoning_effort}")
    print(f"  Relative per-token rate: {result.relative_token_rate}x Luna")
    print(f"  Approval required: {'yes' if result.approval_required else 'no'}")
    if result.profile == "sol-high":
        print("  Authorization: explicit user selection or approval required")
    print(f"  Fallback: {result.fallback_profile}")
    if result.fallback_requires_approval:
        print("  Fallback approval: required")
    print(f"  Why: {result.rationale}")
    print(f"  Escalate when: {result.escalation_trigger}")
    print("  Apply in desktop: /model")
    print(
        "  CLI: codex -m "
        f"{result.model} -c model_reasoning_effort={result.reasoning_effort}"
    )


def _print_table() -> None:
    policy = _load_policy()
    print("Profile       Rate  Approval  Best use")
    print(
        "------------  ----  --------  -----------------------------------------------"
    )
    for profile in policy["profiles"]:
        rate = policy["relative_token_rates"][profile["model"]]
        approval = "yes" if profile["approval_required"] else "no"
        print(f"{profile['id']:<12}  {rate:>2}x   {approval:<8}  {profile['use_for']}")
    print()
    print(
        "Rates compare equal token mixes; reasoning effort has no fixed cost multiplier."
    )
    print(
        "Max is single-agent quality-first; Ultra may spawn agents. Both require approval here."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="*", help="task description")
    parser.add_argument(
        "--risk", choices=("auto", "low", "normal", "high", "critical"), default="auto"
    )
    parser.add_argument("--repeatable", action="store_true")
    parser.add_argument("--ambiguous", action="store_true")
    parser.add_argument("--important", action="store_true")
    parser.add_argument(
        "--orchestrator",
        action="store_true",
        help="show the efficient advisory parent profile without overriding the user's active model",
    )
    parser.add_argument(
        "--table", action="store_true", help="compare all supported profiles"
    )
    parser.add_argument(
        "--json", action="store_true", help="machine-readable recommendation"
    )
    args = parser.parse_args()

    if args.table:
        _print_table()
        return 0

    query = " ".join(args.query).strip()
    if not query:
        parser.error("provide a task description or use --table")

    result = recommend(
        query,
        risk=args.risk,
        repeatable=args.repeatable,
        ambiguous=args.ambiguous,
        important=args.important,
        orchestrator=args.orchestrator,
    )
    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        _print_recommendation(result, query)
    return 0


if __name__ == "__main__":
    sys.exit(main())
