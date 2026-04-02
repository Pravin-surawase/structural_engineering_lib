#!/usr/bin/env python3
"""
Prompt router — routes natural language queries to the best agent + skills.

Takes a query like "design beam 300x500" and returns which agent, skills,
and scripts should handle it, using weighted keyword matching against
agents/agent_registry.json.

Usage:
    python scripts/prompt_router.py "design beam 300x500"
    python scripts/prompt_router.py --json "fix test failure"
    python scripts/prompt_router.py --all "security audit"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Add _lib to path
sys.path.insert(0, str(Path(__file__).parent))
from _lib.output import StatusLine, print_json
from _lib.utils import REPO_ROOT


@dataclass
class RoutingResult:
    """Result of routing a query to an agent."""

    agent: str
    skills: list[str]
    scripts: list[str]
    confidence: float
    reasoning: str
    alternatives: list[str] = field(default_factory=list)


# Priority routing rules — checked first, before keyword matching.
# Each rule: (keywords_to_match, agent_name, weight_bonus)
PRIORITY_RULES: list[tuple[set[str], str, float]] = [
    # Frontend
    (
        {"react", "component", "hook", "tailwind", "r3f", "viewport", "zustand"},
        "frontend",
        3.0,
    ),
    # API developer
    (
        {"fastapi", "router", "endpoint", "pydantic", "openapi", "rest"},
        "api-developer",
        3.0,
    ),
    # Structural math — pure IS 456 math
    (
        {
            "is456",
            "clause",
            "formula",
            "flexure",
            "strain",
            "stress",
            "reinforcement",
            "slab",
            "footing",
            "deflection",
            "crack",
        },
        "structural-math",
        2.5,
    ),
    # Structural elements — design tasks
    (
        {"beam", "column", "shear", "bending", "design", "detailing"},
        "structural-math",
        2.0,
    ),
    # Tester
    (
        {"test", "coverage", "benchmark", "pytest", "regression", "hypothesis"},
        "tester",
        3.0,
    ),
    # Security
    ({"security", "owasp", "vulnerability", "injection", "scan"}, "security", 3.0),
    # Doc-master
    (
        {"docs", "documentation", "session", "log", "archive", "index", "worklog"},
        "doc-master",
        3.0,
    ),
    # Ops
    (
        {"git", "commit", "docker", "ci", "deploy", "release", "branch", "push"},
        "ops",
        3.0,
    ),
    # Reviewer
    ({"review", "architecture", "quality", "validate"}, "reviewer", 2.5),
    # Governance
    ({"health", "metrics", "maintenance", "governance", "audit"}, "governance", 2.5),
    # Backend — general Python structural_lib
    ({"python", "service", "adapter", "pipeline", "api", "library"}, "backend", 2.0),
    # Library expert
    (
        {"standard", "professional", "guidance", "domain", "usage"},
        "library-expert",
        2.0,
    ),
    # Agent evolver
    ({"evolve", "drift", "score", "instruction", "performance"}, "agent-evolver", 2.5),
    # UI designer
    ({"ux", "wireframe", "layout", "accessibility", "visual"}, "ui-designer", 2.5),
]

# Suppression rules — reduce score by 50% if agent matches suppression keywords
SUPPRESSION_RULES: dict[str, set[str]] = {
    "ui-designer": {
        "beam",
        "column",
        "slab",
        "footing",
        "shear",
        "flexure",
        "is456",
        "structural",
    },
    "library-expert": {
        "implement",
        "code",
        "write",
        "create",
        "fix",
        "add",
    },
}

# Combo rules — bonus when ALL keywords in a set are present
# (keywords_required, agent_name, bonus_score)
COMBO_RULES: list[tuple[set[str], str, float]] = [
    ({"is456", "verify"}, "structural-engineer", 4.0),
    ({"is456", "implement"}, "structural-math", 4.0),
    ({"is456", "usage"}, "library-expert", 4.0),
    ({"test", "write"}, "tester", 3.0),
    ({"test", "review"}, "reviewer", 3.0),
    ({"verify", "compliance"}, "structural-engineer", 3.5),
    ({"implement", "formula"}, "structural-math", 3.5),
]

# Stopwords to ignore in query tokenization
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "he",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "that",
    "the",
    "to",
    "was",
    "will",
    "with",
    "or",
    "this",
    "all",
    "if",
    "any",
    "do",
    "can",
    "how",
    "what",
    "where",
    "when",
    "which",
    "who",
    "i",
    "me",
    "my",
    "we",
    "you",
    "your",
    "need",
    "want",
    "should",
    "please",
    "help",
    "using",
    "use",
}


def _tokenize(text: str) -> set[str]:
    """Split text into lowercase keyword tokens, filtering stopwords."""
    tokens = set(re.split(r"[\s/\-_.,;:!?()\"']+", text.lower()))
    return {t for t in tokens if t and len(t) > 1 and t not in STOPWORDS}


def _load_agents() -> list[dict]:
    """Load agent entries from agent_registry.json."""
    path = REPO_ROOT / "agents" / "agent_registry.json"
    if not path.exists():
        StatusLine.fail(f"Agent registry not found: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("agents", [])


def route(query: str) -> RoutingResult:
    """Route a natural language query to the best agent.

    Scoring:
        - Exact keyword match against priority rules: rule weight
        - Exact keyword match against agent_registry keywords: 1.0
        - Partial (substring) match against agent_registry keywords: 0.5
        - Category/description match: 0.3

    Returns the best-scoring agent with associated skills and scripts.
    """
    tokens = _tokenize(query)
    if not tokens:
        return RoutingResult(
            agent="orchestrator",
            skills=["session-management"],
            scripts=[],
            confidence=0.1,
            reasoning="Empty or unparseable query — defaulting to orchestrator",
        )

    agents = _load_agents()
    if not agents:
        return RoutingResult(
            agent="orchestrator",
            skills=[],
            scripts=[],
            confidence=0.0,
            reasoning="Could not load agent registry",
        )

    # Score each agent
    scores: dict[str, float] = {}
    match_details: dict[str, list[str]] = {}

    for agent in agents:
        name = agent["name"]
        score = 0.0
        matched: list[str] = []

        # Phase 1: Priority rules
        for rule_keywords, rule_agent, weight in PRIORITY_RULES:
            if rule_agent != name:
                continue
            hits = tokens & rule_keywords
            if hits:
                bonus = len(hits) * weight
                score += bonus
                matched.extend(f"{kw}(rule)" for kw in sorted(hits))

        # Phase 2: Agent registry keyword matching
        agent_keywords = {kw.lower() for kw in agent.get("keywords", [])}
        for token in tokens:
            # Exact match
            if token in agent_keywords:
                score += 1.0
                if f"{token}(rule)" not in matched:
                    matched.append(f"{token}(kw)")
            else:
                # Partial match (token is substring of a keyword or vice versa)
                for akw in agent_keywords:
                    if token in akw or akw in token:
                        score += 0.5
                        if f"{token}(partial)" not in matched:
                            matched.append(f"{token}(partial)")
                        break

        # Phase 3: Description match
        desc_lower = agent.get("description", "").lower()
        for token in tokens:
            if token in desc_lower:
                score += 0.3

        # Phase 4: Combo rules — bonus when ALL keywords in a combo match
        for combo_keywords, combo_agent, bonus in COMBO_RULES:
            if combo_agent == name and combo_keywords.issubset(tokens):
                score += bonus
                matched.append(f"combo({'+'.join(sorted(combo_keywords))})")

        # Phase 5: Suppression — reduce score if suppression keywords match
        suppressed_keywords = SUPPRESSION_RULES.get(name, set())
        if suppressed_keywords:
            suppression_hits = tokens & suppressed_keywords
            if suppression_hits:
                score *= 0.5
                matched.append(f"suppressed({','.join(sorted(suppression_hits))})")

        scores[name] = score
        match_details[name] = matched

    # Rank agents by score
    ranked = sorted(scores.items(), key=lambda x: -x[1])

    # Best agent
    best_name, best_score = ranked[0]
    best_agent = next(a for a in agents if a["name"] == best_name)

    # Normalize confidence to 0-1 range
    # Use a sigmoid-like mapping: score of 5+ → ~0.95
    max_possible = max(best_score, 1.0)
    confidence = min(best_score / (best_score + 3.0), 0.99) if best_score > 0 else 0.05

    # Build reasoning from matched keywords
    matched_kws = match_details.get(best_name, [])
    kw_display = (
        ", ".join(kw.split("(")[0] for kw in matched_kws) if matched_kws else "none"
    )
    reasoning = f"Matched keywords: {kw_display} → {best_name}"

    # Alternatives (agents with score > 0, excluding the best)
    alternatives = []
    for name, sc in ranked[1:]:
        if sc > 0:
            alternatives.append(f"@{name} ({sc:.2f})")
        if len(alternatives) >= 4:
            break

    return RoutingResult(
        agent=best_name,
        skills=best_agent.get("skills", []),
        scripts=best_agent.get("scripts", []),
        confidence=round(confidence, 2),
        reasoning=reasoning,
        alternatives=alternatives,
    )


def route_all(query: str) -> list[RoutingResult]:
    """Route a query and return ALL candidate agents ranked by score."""
    tokens = _tokenize(query)
    agents = _load_agents()
    if not agents or not tokens:
        return [route(query)]

    # Score each agent (same logic as route())
    results: list[tuple[dict, float, list[str]]] = []

    for agent in agents:
        name = agent["name"]
        score = 0.0
        matched: list[str] = []

        for rule_keywords, rule_agent, weight in PRIORITY_RULES:
            if rule_agent != name:
                continue
            hits = tokens & rule_keywords
            if hits:
                score += len(hits) * weight
                matched.extend(sorted(hits))

        agent_keywords = {kw.lower() for kw in agent.get("keywords", [])}
        for token in tokens:
            if token in agent_keywords:
                score += 1.0
                if token not in matched:
                    matched.append(token)
            else:
                for akw in agent_keywords:
                    if token in akw or akw in token:
                        score += 0.5
                        break

        desc_lower = agent.get("description", "").lower()
        for token in tokens:
            if token in desc_lower:
                score += 0.3

        # Combo rules
        for combo_keywords, combo_agent, bonus in COMBO_RULES:
            if combo_agent == name and combo_keywords.issubset(tokens):
                score += bonus

        # Suppression rules
        suppressed_keywords = SUPPRESSION_RULES.get(name, set())
        if suppressed_keywords:
            suppression_hits = tokens & suppressed_keywords
            if suppression_hits:
                score *= 0.5

        if score > 0:
            results.append((agent, score, matched))

    results.sort(key=lambda x: -x[1])

    routing_results = []
    for agent, score, matched in results:
        confidence = min(score / (score + 3.0), 0.99) if score > 0 else 0.05
        kw_display = ", ".join(matched) if matched else "none"
        routing_results.append(
            RoutingResult(
                agent=agent["name"],
                skills=agent.get("skills", []),
                scripts=agent.get("scripts", []),
                confidence=round(confidence, 2),
                reasoning=f"Matched keywords: {kw_display} → {agent['name']}",
            )
        )

    if not routing_results:
        routing_results.append(route(query))

    return routing_results


def _print_result(result: RoutingResult, query: str) -> None:
    """Print a routing result in human-readable format."""
    print(f'\n🎯 Routing: "{query}"')
    print("━" * 50)
    print()
    print(f"  Agent:      @{result.agent}")
    print(f"  Skills:     {', '.join(result.skills) if result.skills else 'none'}")
    print(f"  Scripts:    {', '.join(result.scripts) if result.scripts else 'none'}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Reasoning:  {result.reasoning}")

    if result.alternatives:
        print()
        print("  Alternatives:")
        for alt in result.alternatives:
            print(f"    {alt}")
    print()


def _print_all_results(results: list[RoutingResult], query: str) -> None:
    """Print all routing candidates ranked."""
    print(f'\n🎯 All candidates for: "{query}"')
    print("━" * 50)
    for i, r in enumerate(results, 1):
        marker = "→" if i == 1 else " "
        skills_str = f" | skills: {', '.join(r.skills)}" if r.skills else ""
        print(
            f"  {marker} {i}. @{r.agent} ({r.confidence:.2f}) — {r.reasoning}{skills_str}"
        )
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Route natural language queries to the best agent + skills.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python scripts/prompt_router.py "design beam 300x500 with IS 456"
  python scripts/prompt_router.py --json "fix csv import bug"
  python scripts/prompt_router.py --all "security audit"
""",
    )
    parser.add_argument("query", help="Natural language query to route")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--all", action="store_true", help="Show all candidates ranked")

    args = parser.parse_args()

    if args.all:
        results = route_all(args.query)
        if args.json:
            print_json([asdict(r) for r in results])
        else:
            _print_all_results(results, args.query)
    else:
        result = route(args.query)
        if args.json:
            print_json(asdict(result))
        else:
            _print_result(result, args.query)


if __name__ == "__main__":
    main()
