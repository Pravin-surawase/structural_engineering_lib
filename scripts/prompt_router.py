#!/usr/bin/env python3
"""
Prompt router — routes natural language queries to the best agent + skills.

Takes a query like "design beam 300x500" and returns which agent, skills,
and scripts should handle it, using weighted keyword matching against
agents/agent_registry.json.

When to use: when selecting an existing repository role for a concrete task.

Usage:
    ./scripts/python_runtime.sh scripts/prompt_router.py "design beam 300x500"
    ./scripts/python_runtime.sh scripts/prompt_router.py --json "fix test failure"
    ./scripts/python_runtime.sh scripts/prompt_router.py --all "security audit"
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# Add _lib to path
sys.path.insert(0, str(Path(__file__).parent))
from _lib.output import StatusLine, print_json
from _lib.utils import REPO_ROOT
from tool_registry import ToolEntry, find_tools, load_registry

AUTOMATION_MAP_PATH = REPO_ROOT / "scripts" / "automation-map.json"


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

GENERIC_TASK_WORDS = {
    "add", "change", "create", "efficient", "faster", "fix", "make", "new",
    "smart", "task", "update", "without", "work",
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


def _git(args: list[str], *, cwd: Path = REPO_ROOT) -> str | None:
    """Run one read-only Git query and return stripped stdout."""
    try:
        result = subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                                text=True, check=False, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def _parse_worktrees(raw: str) -> list[dict[str, str]]:
    """Parse ``git worktree list --porcelain`` records."""
    records: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in [*raw.splitlines(), ""]:
        if not line:
            if current:
                records.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value
    return records


def collect_lane_state() -> dict[str, Any]:
    """Collect current and sibling worktree state without mutating Git."""
    branch = _git(["branch", "--show-current"]) or "DETACHED"
    head = _git(["rev-parse", "--short", "HEAD"]) or "unknown"
    status = _git(["status", "--porcelain=v1"])
    upstream = _git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"])
    base_ref = upstream or (
        "origin/main" if _git(["rev-parse", "--verify", "origin/main"]) else "main"
    )
    base = _git(["merge-base", "HEAD", base_ref])
    current_root = REPO_ROOT.resolve()
    worktrees: list[dict[str, Any]] = []
    for record in _parse_worktrees(_git(["worktree", "list", "--porcelain"]) or ""):
        worktree_path = Path(record.get("worktree", ""))
        worktree_status = _git(["status", "--porcelain=v1"], cwd=worktree_path)
        try:
            is_current = worktree_path.resolve() == current_root
        except OSError:
            is_current = False
        worktrees.append({
            "path": str(worktree_path),
            "branch": record.get("branch", "DETACHED").removeprefix("refs/heads/"),
            "head": record.get("HEAD", "unknown")[:8],
            "dirty_files": len(worktree_status.splitlines()) if worktree_status is not None else None,
            "current": is_current,
        })
    dirty_files = len(status.splitlines()) if status else 0
    attention: list[str] = []
    if branch == "DETACHED":
        attention.append("Current worktree is detached; inspect Git state before editing.")
    elif branch in {"main", "master"}:
        attention.append("Current worktree is on the default branch; use Codex-native Git to isolate the task.")
    if dirty_files:
        attention.append(f"Current worktree has {dirty_files} changed file(s); confirm task ownership before editing.")
    if any(not item["current"] and (item["dirty_files"] or 0) > 0 for item in worktrees):
        attention.append("Other worktrees contain changes; preserve those active lanes.")
    return {
        "root": str(REPO_ROOT), "branch": branch, "head": head, "dirty_files": dirty_files,
        "upstream": upstream or "none", "base_ref": base_ref,
        "base": base[:8] if base else "unknown",
        "worktrees": worktrees, "attention": attention,
    }


def _task_tokens(text: str) -> set[str]:
    return {token for token in re.split(r"[^a-z0-9]+", text.lower())
            if len(token) > 2 and token not in STOPWORDS | GENERIC_TASK_WORDS}


def _relevant_tools(query: str, *, limit: int = 4) -> list[tuple[ToolEntry, float]]:
    query_tokens = _task_tokens(query)
    relevant: list[tuple[ToolEntry, float]] = []
    seen_commands: set[str] = set()
    for tool, score in find_tools(query, load_registry(), limit=25):
        if not tool.script or tool.script in seen_commands:
            continue
        if query_tokens and not query_tokens & _task_tokens(f"{tool.name} {tool.description} {' '.join(tool.keywords)}"):
            continue
        relevant.append((tool, score))
        seen_commands.add(tool.script)
        if len(relevant) == limit:
            break
    return relevant


def _initial_context(skills: list[str], tools: list[tuple[ToolEntry, float]]) -> list[str]:
    context = ["AGENTS.md", "docs/TASKS.md", "docs/planning/next-session-brief.md"]
    for skill in skills:
        path = f".github/skills/{skill}/SKILL.md"
        if (REPO_ROOT / path).exists():
            context.append(path)
    task_map = json.loads(AUTOMATION_MAP_PATH.read_text(encoding="utf-8")).get("tasks", {})
    for tool, _score in tools:
        for path in task_map.get(tool.name, {}).get("context_docs", []):
            if path not in context and (REPO_ROOT / path).exists():
                context.append(path)
            if len(context) >= 7:
                return context
    return context


def build_task_brief(query: str) -> dict[str, Any]:
    """Compose read-only lane, routing, and automation guidance for ``query``."""
    routing = route(query)
    tools = _relevant_tools(query)
    return {
        "task": query, "lane": collect_lane_state(), "route": asdict(routing),
        "matching_tools": [
            {"name": tool.name, "description": tool.description, "command": tool.script,
             "permission": tool.permission or "Unspecified", "score": score}
            for tool, score in tools
        ],
        "initial_context": _initial_context(routing.skills, tools),
        "workflow": {
            "start": [f"./run.sh session brief --agent {routing.agent}", "./run.sh session start"],
            "close": ["./run.sh check --quick", f"./run.sh session end --agent {routing.agent}"],
            "git_rule": "Codex owns Git/worktree/PR operations; this command is inspection-only.",
        },
    }


def _print_task_brief(brief: dict[str, Any]) -> None:
    lane, routing = brief["lane"], brief["route"]
    print("\nEfficient Task Brief\n" + "=" * 60)
    print(f"Task: {brief['task']}")
    print(f"Lane: {lane['branch']} @ {lane['head']} | dirty={lane['dirty_files']} | base={lane['base']} ({lane['base_ref']}) | upstream={lane['upstream']}")
    print("Worktrees:")
    for item in lane["worktrees"]:
        print(f" {'*' if item['current'] else ' '} {item['branch']} | dirty={item['dirty_files']} | {item['path']}")
    print(f"\nRoute: @{routing['agent']} ({routing['confidence']:.2f})")
    print("Existing tools:")
    for item in brief["matching_tools"]:
        print(f" - {item['name']} [{item['permission']}] -> {item['command']}")
    if not brief["matching_tools"]:
        print(" - No task-specific automation match; inspect the affected folder index.")
    print("\nSafe start: " + " -> ".join(brief["workflow"]["start"]))
    print("Safe close: " + " -> ".join(brief["workflow"]["close"]))
    print(f"Note: {brief['workflow']['git_rule']}\n")


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
  ./scripts/python_runtime.sh scripts/prompt_router.py "design beam 300x500 with IS 456"
  ./scripts/python_runtime.sh scripts/prompt_router.py --json "fix csv import bug"
  ./scripts/python_runtime.sh scripts/prompt_router.py --all "security audit"
  ./scripts/python_runtime.sh scripts/prompt_router.py --brief "fix csv import bug"
""",
    )
    parser.add_argument("query", help="Natural language query to route")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--all", action="store_true", help="Show all candidates ranked")
    mode.add_argument("--brief", action="store_true", help="Build a read-only lane and automation brief")

    args = parser.parse_args()

    if args.brief:
        brief = build_task_brief(args.query)
        if args.json:
            print_json(brief)
        else:
            _print_task_brief(brief)
    elif args.all:
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
