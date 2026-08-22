#!/usr/bin/env python3
"""
Unified tool registry — connects agents, skills, scripts, and operations.

Loads from:
- agents/agent_registry.json (16 agents)
- scripts/control-plane.json (operation, command, alias, and permission metadata)

Usage:
    python scripts/tool_registry.py --list
    python scripts/tool_registry.py --find "beam design"
    python scripts/tool_registry.py --agent backend
    python scripts/tool_registry.py --category Git
    python scripts/tool_registry.py --permission ReadOnly
    python scripts/tool_registry.py --alias design
    python scripts/tool_registry.py --stats
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Add _lib to path
sys.path.insert(0, str(Path(__file__).parent))
from _lib.output import StatusLine
from _lib.utils import REPO_ROOT
from control_plane import (
    load_registry as load_control_registry,
    operation_map,
    operation_name_for_alias,
)


@dataclass
class ToolEntry:
    """A unified tool/operation entry."""

    name: str
    description: str
    agent: str
    category: str
    script: str | None
    permission: str | None
    permission_modes: dict[str, str] = field(default_factory=dict)
    keywords: list[str] = field(default_factory=list)
    skill: str | None = None
    aliases: list[str] = field(default_factory=list)


# Stopwords for keyword extraction
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
}


def extract_keywords(name: str, description: str) -> list[str]:
    """Extract keywords from name and description."""
    # Split on non-alphanumeric
    tokens = re.split(r"[\s/\-_]+", f"{name} {description}".lower())

    # Filter stopwords and short tokens
    keywords = [t for t in tokens if t and len(t) > 2 and t not in STOPWORDS]

    # Deduplicate while preserving order
    seen = set()
    unique_keywords = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)

    return unique_keywords


def load_registry() -> dict[str, ToolEntry]:
    """Load unified tools from the agent and canonical control registries."""
    registry: dict[str, ToolEntry] = {}

    # Load agent registry
    agent_reg_path = REPO_ROOT / "agents" / "agent_registry.json"
    if agent_reg_path.exists():
        with open(agent_reg_path, "r", encoding="utf-8") as f:
            agent_data = json.load(f)

        # Add agent tools
        for agent in agent_data.get("agents", []):
            agent_name = agent["name"]

            # Each agent is a tool
            tool_name = f"agent:{agent_name}"
            registry[tool_name] = ToolEntry(
                name=tool_name,
                description=agent["description"],
                agent=agent_name,
                category="Agent",
                script=None,
                permission=agent.get("permission_level", "WorkspaceWrite"),
                keywords=agent.get("keywords", []),
                skill=None,
                aliases=[],
            )

            # Add agent's skills as tools
            for skill in agent.get("skills", []):
                skill_tool_name = f"skill:{skill}"
                if skill_tool_name not in registry:
                    registry[skill_tool_name] = ToolEntry(
                        name=skill_tool_name,
                        description=f"Skill: {skill}",
                        agent=agent_name,
                        category="Skill",
                        script=None,
                        permission=agent.get("permission_level", "ReadOnly"),
                        keywords=[skill.replace("-", " ")],
                        skill=skill,
                        aliases=[],
                    )

    # The registry only lists skills assigned directly to agents. Discover the
    # complete Copilot skill catalog as well so unassigned specialist gates are
    # not invisible to tool search.
    skill_agents = {
        "quality-gate": "reviewer",
        "release-preflight": "ops",
        "user-acceptance-test": "tester",
        "development-rules": "reviewer",
    }
    for skill_file in sorted((REPO_ROOT / ".github" / "skills").glob("*/SKILL.md")):
        skill = skill_file.parent.name
        tool_name = f"skill:{skill}"
        content = skill_file.read_text(encoding="utf-8")
        description_match = re.search(
            r'^description:\s*["\']?(.*?)["\']?\s*$', content, re.MULTILINE
        )
        description = (
            description_match.group(1) if description_match else f"Skill: {skill}"
        )
        if tool_name in registry:
            registry[tool_name].description = description
            continue
        registry[tool_name] = ToolEntry(
            name=tool_name,
            description=description,
            agent=skill_agents.get(skill, "orchestrator"),
            category="Skill",
            script=None,
            permission="ReadOnly",
            keywords=[skill.replace("-", " ")],
            skill=skill,
            aliases=[],
        )

    # Add canonical script operations.
    control_registry = load_control_registry()
    for task_name, task_info in operation_map(
        control_registry, active_only=True
    ).items():
        script = task_info.get("command", {}).get("display", "")
        description = task_info.get("description", "")
        group = task_info.get("group", "Uncategorized")

        permission = task_info.get("permission")
        permission_modes = task_info.get("permission_modes", {})

        # Extract keywords
        keywords = extract_keywords(task_name, description)

        # Determine primary agent based on task characteristics
        agent = task_info.get("agent") or infer_agent_from_task(
            task_name, description, group
        )

        registry[task_name] = ToolEntry(
            name=task_name,
            description=description,
            agent=agent,
            category=group,
            script=script,
            permission=permission,
            permission_modes=permission_modes,
            keywords=keywords,
            skill=None,
            aliases=[str(alias) for alias in task_info.get("aliases", [])],
        )

    return registry


def infer_agent_from_task(task_name: str, description: str, group: str) -> str:
    """Infer the primary agent responsible for a task."""
    text = f"{task_name} {description}".lower()

    # Agent-specific keywords
    if "backend" in text or "structural_lib" in text or "is456" in text:
        return "backend"
    if "react" in text or "component" in text or "ui" in text or "frontend" in text:
        return "frontend"
    if "fastapi" in text or "endpoint" in text or "router" in text:
        return "api-developer"
    if "test" in text or "coverage" in text:
        return "tester"
    if "doc" in text or "markdown" in text or "session" in text:
        return "doc-master"
    if "git" in text or "commit" in text or "push" in text:
        return "ops"
    if "governance" in text or "health" in text or "audit" in text:
        return "governance"
    if "review" in text or "quality" in text:
        return "reviewer"

    # Group-based fallback
    group_to_agent = {
        "Git": "ops",
        "Testing": "tester",
        "Docs": "doc-master",
        "Quality": "governance",
        "Session": "doc-master",
        "Infrastructure": "ops",
        "Generation": "doc-master",
    }

    return group_to_agent.get(group, "orchestrator")


def find_tools(
    query: str, registry: dict[str, ToolEntry], limit: int = 5
) -> list[tuple[ToolEntry, float]]:
    """Find tools matching the query using token-based scoring."""
    tokens = set(re.split(r"[\s/\-_]+", query.lower()))
    results = []

    for tool in registry.values():
        score = 0.0
        searchable = (
            f"{tool.name} {tool.description} {' '.join(tool.keywords)} "
            f"{' '.join(tool.aliases)}"
        ).lower()

        for token in tokens:
            if not token:
                continue

            # Exact match in searchable text
            if token in searchable:
                score += 1.0

            # Bonus for exact name match
            if token in tool.name.lower():
                score += 2.0

            # Bonus for keyword match
            if token in [kw.lower() for kw in tool.keywords]:
                score += 1.5

            # Bonus for alias match
            if token in [alias.lower() for alias in tool.aliases]:
                score += 2.5

        if score > 0:
            results.append((tool, score))

    # Sort by score (descending)
    results.sort(key=lambda x: -x[1])

    return results[:limit]


def get_agent_tools(agent_name: str, registry: dict[str, ToolEntry]) -> list[ToolEntry]:
    """Get all tools for a specific agent."""
    return [tool for tool in registry.values() if tool.agent == agent_name]


def get_tools_by_category(
    category: str, registry: dict[str, ToolEntry]
) -> list[ToolEntry]:
    """Get all tools in a category."""
    return [tool for tool in registry.values() if tool.category == category]


def get_tools_by_permission(
    level: str, registry: dict[str, ToolEntry]
) -> list[ToolEntry]:
    """Get all tools with a specific permission level."""
    normalized_level = level.lower()
    return [
        tool
        for tool in registry.values()
        if (tool.permission or "Unspecified").lower() == normalized_level
    ]


def resolve_alias(alias: str) -> str | None:
    """Resolve an alias to the full tool name."""
    return operation_name_for_alias(alias)


def print_tool(tool: ToolEntry, show_score: bool = False, score: float = 0.0):
    """Print a tool entry."""
    agent_tag = f"[@{tool.agent}]" if tool.agent else ""
    category_tag = f"[{tool.category}]" if tool.category else ""
    permission_label = tool.permission or "Unspecified"
    permission_icon = {
        "ReadOnly": "🔍",
        "ReadOnlyTerminal": "🖥️",
        "WorkspaceWrite": "✏️",
        "DangerFullAccess": "⚠️",
    }.get(permission_label, "❓")

    score_tag = f" (score: {score:.1f})" if show_score and score > 0 else ""

    print(f"  {permission_icon} {tool.name} {agent_tag} {category_tag}{score_tag}")
    print(f"     {tool.description}")

    if tool.script:
        print(f"     Script: {tool.script}")
    print(f"     Permission: {permission_label}")
    if tool.permission_modes:
        modes = ", ".join(
            f"{mode}={level}" for mode, level in tool.permission_modes.items()
        )
        print(f"     Modes: {modes}")

    if tool.aliases:
        aliases_str = ", ".join(tool.aliases)
        print(f"     Aliases: {aliases_str}")

    if tool.skill:
        print(f"     Skill: {tool.skill}")

    print()


def list_registry(registry: dict[str, ToolEntry]):
    """List all tools grouped by category."""
    # Group by category
    by_category: dict[str, list[ToolEntry]] = {}
    for tool in registry.values():
        category = tool.category or "Uncategorized"
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(tool)

    # Print each category
    for category in sorted(by_category.keys()):
        print(f"\n📂 {category} ({len(by_category[category])} tools)")
        print("=" * 60)
        for tool in sorted(by_category[category], key=lambda t: t.name):
            print_tool(tool)


def show_stats(registry: dict[str, ToolEntry]):
    """Show registry statistics."""
    total = len(registry)

    # By category
    by_category: dict[str, int] = {}
    for tool in registry.values():
        category = tool.category or "Uncategorized"
        by_category[category] = by_category.get(category, 0) + 1

    # By agent
    by_agent: dict[str, int] = {}
    for tool in registry.values():
        agent = tool.agent or "None"
        by_agent[agent] = by_agent.get(agent, 0) + 1

    # By permission
    by_permission: dict[str, int] = {}
    for tool in registry.values():
        permission = tool.permission or "Unspecified"
        by_permission[permission] = by_permission.get(permission, 0) + 1

    # Scripts vs skills vs agents
    has_script = sum(1 for t in registry.values() if t.script)
    has_skill = sum(1 for t in registry.values() if t.skill)
    is_agent = sum(1 for t in registry.values() if t.name.startswith("agent:"))

    StatusLine.info("Tool Registry Statistics")
    print(f"\n📊 Total tools: {total}")
    print(f"   - Script-backed operations: {has_script}")
    print(f"   - Skills: {has_skill}")
    print(f"   - Agents: {is_agent}")
    print(f"   - Aliases: {sum(len(tool.aliases) for tool in registry.values())}")

    print("\n📂 By Category:")
    for category in sorted(by_category.keys()):
        print(f"   - {category}: {by_category[category]}")

    print(f"\n👤 By Agent ({len(by_agent)} agents):")
    for agent in sorted(by_agent.keys(), key=lambda a: -by_agent[a])[:10]:
        print(f"   - {agent}: {by_agent[agent]}")

    print("\n🔐 By Permission:")
    for permission in sorted(by_permission.keys()):
        icon = {
            "ReadOnly": "🔍",
            "ReadOnlyTerminal": "🖥️",
            "WorkspaceWrite": "✏️",
            "DangerFullAccess": "⚠️",
        }.get(permission, "")
        print(f"   - {icon} {permission}: {by_permission[permission]}")


def main():
    parser = argparse.ArgumentParser(
        description="Unified tool registry — query agents, skills, and scripts"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--list", action="store_true", help="List all tools by category")
    group.add_argument(
        "--find", metavar="QUERY", help="Search for tools matching query"
    )
    group.add_argument("--agent", metavar="NAME", help="Show tools for specific agent")
    group.add_argument("--category", metavar="NAME", help="Show tools in category")
    group.add_argument(
        "--permission", metavar="LEVEL", help="Show tools by permission level"
    )
    group.add_argument("--alias", metavar="ALIAS", help="Resolve an alias")
    group.add_argument("--stats", action="store_true", help="Show registry statistics")

    parser.add_argument(
        "--limit", type=int, default=5, help="Limit search results (default: 5)"
    )

    args = parser.parse_args()

    # Load registry
    registry = load_registry()

    if not registry:
        StatusLine.fail("Registry is empty — check source files")
        return 1

    # Handle commands
    if args.stats:
        show_stats(registry)

    elif args.list:
        list_registry(registry)

    elif args.find:
        results = find_tools(args.find, registry, limit=args.limit)
        if not results:
            StatusLine.warn(f"No tools found matching: {args.find}")
            return 1

        StatusLine.ok(f"Found {len(results)} tools matching '{args.find}':")
        print()
        for tool, score in results:
            print_tool(tool, show_score=True, score=score)

    elif args.agent:
        tools = get_agent_tools(args.agent, registry)
        if not tools:
            StatusLine.warn(f"No tools found for agent: {args.agent}")
            return 1

        StatusLine.ok(f"{len(tools)} tools for @{args.agent}:")
        print()
        for tool in sorted(tools, key=lambda t: t.name):
            print_tool(tool)

    elif args.category:
        tools = get_tools_by_category(args.category, registry)
        if not tools:
            StatusLine.warn(f"No tools found in category: {args.category}")
            return 1

        StatusLine.ok(f"{len(tools)} tools in category '{args.category}':")
        print()
        for tool in sorted(tools, key=lambda t: t.name):
            print_tool(tool)

    elif args.permission:
        tools = get_tools_by_permission(args.permission, registry)
        if not tools:
            StatusLine.warn(f"No tools found with permission: {args.permission}")
            return 1

        StatusLine.ok(f"{len(tools)} tools with permission '{args.permission}':")
        print()
        for tool in sorted(tools, key=lambda t: t.name):
            print_tool(tool)

    elif args.alias:
        resolved = resolve_alias(args.alias)
        if not resolved:
            StatusLine.warn(f"Unknown alias: {args.alias}")
            return 1

        StatusLine.ok(f"Alias '{args.alias}' → '{resolved}'")

        # Show the resolved tool
        if resolved in registry:
            print()
            print_tool(registry[resolved])

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
