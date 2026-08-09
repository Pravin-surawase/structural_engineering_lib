#!/usr/bin/env python3
"""
Skill tier classification and management for AI agents.

Classifies skills into three tiers from .github/skills/skill_tiers.json:
  - Core: Available to any agent when the task requires it
  - Specialist: Available to specific agents based on role
  - Experimental: Require explicit activation (new/unstable)

Validates skill assignments in agent_registry.json against tier definitions.

USAGE:
    python scripts/skill_tiers.py list                    # Show all skills by tier
    python scripts/skill_tiers.py --agent backend         # Skills for specific agent
    python scripts/skill_tiers.py validate                # Check for mismatches
    python scripts/skill_tiers.py --json                  # Machine-readable output
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.output import StatusLine, print_json
from _lib.utils import REPO_ROOT

CATALOG_PATH = REPO_ROOT / ".github" / "skills" / "skill_tiers.json"
TIER_NAMES = ("core", "specialist", "experimental")


def load_skill_catalog() -> dict[str, Any]:
    """Load the canonical skill catalog."""
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(f"Skill catalog not found: {CATALOG_PATH}")
    with CATALOG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def catalog_entries(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return skill metadata keyed by name, including each skill's tier."""
    entries: dict[str, dict[str, Any]] = {}
    for tier in TIER_NAMES:
        for item in catalog.get(tier, []):
            name = item.get("name")
            if isinstance(name, str) and name not in entries:
                entries[name] = {**item, "tier": tier}
    return entries


def tier_description(catalog: dict[str, Any], tier: str) -> str:
    """Return the catalog description for a tier."""
    return catalog.get("_meta", {}).get("tiers", {}).get(tier, tier)


@dataclass
class Issue:
    """Skill tier validation issue."""

    level: str  # error, warning, info
    category: str  # missing, mismatch, orphan, unassigned
    description: str
    details: str = ""

    def __str__(self) -> str:
        """Human-readable representation."""
        icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(self.level, "•")
        msg = f"{icon} {self.category.upper()}: {self.description}"
        if self.details:
            msg += f"\n    {self.details}"
        return msg


def discover_available_skills() -> list[str]:
    """Discover all available skills from .github/skills/ directory.

    Returns:
        List of skill names (directory names)
    """
    skills_dir = REPO_ROOT / ".github" / "skills"
    if not skills_dir.exists():
        return []

    skill_dirs = [
        d.name
        for d in skills_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ]
    return sorted(skill_dirs)


def load_agent_registry() -> dict[str, Any]:
    """Load agent_registry.json.

    Returns:
        Dictionary with agent registry data
    """
    registry_path = REPO_ROOT / "agents" / "agent_registry.json"
    if not registry_path.exists():
        raise FileNotFoundError(f"Agent registry not found: {registry_path}")

    with registry_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_skills_for_agent(agent_name: str) -> dict[str, list[str]]:
    """Get skills for a specific agent, classified by tier.

    Args:
        agent_name: Name of the agent

    Returns:
        Dictionary mapping tier name to list of skill names
    """
    registry = load_agent_registry()
    entries = catalog_entries(load_skill_catalog())

    # Find agent in registry
    agent_data = None
    for agent in registry.get("agents", []):
        if agent.get("name") == agent_name:
            agent_data = agent
            break

    if not agent_data:
        raise ValueError(f"Agent not found in registry: {agent_name}")

    # Get agent's assigned skills
    assigned_skills = agent_data.get("skills", [])

    # Classify into tiers
    classified = {
        "core": [],
        "specialist": [],
        "experimental": [],
    }

    for skill in assigned_skills:
        metadata = entries.get(skill)
        if metadata:
            classified[metadata["tier"]].append(skill)

    return classified


def validate_skill_assignments() -> list[Issue]:
    """Validate skill assignments against tier definitions.

    Returns:
        List of Issue objects found
    """
    issues: list[Issue] = []
    registry = load_agent_registry()
    catalog = load_skill_catalog()
    available_skills = discover_available_skills()
    agent_names = {
        agent.get("name") for agent in registry.get("agents", []) if agent.get("name")
    }

    entries: dict[str, dict[str, Any]] = {}
    for tier in TIER_NAMES:
        tier_entries = catalog.get(tier)
        if not isinstance(tier_entries, list):
            issues.append(Issue("error", "catalog", f"Tier '{tier}' must be a list"))
            continue
        for item in tier_entries:
            name = item.get("name") if isinstance(item, dict) else None
            if not isinstance(name, str) or not name:
                issues.append(
                    Issue("error", "catalog", f"Tier '{tier}' has an invalid entry")
                )
                continue
            if name in entries:
                issues.append(
                    Issue(
                        "error",
                        "duplicate",
                        f"Skill '{name}' is classified more than once",
                    )
                )
                continue
            entries[name] = {**item, "tier": tier}

    # Build a reverse map: skill -> agents
    skill_to_agents: dict[str, list[str]] = {}
    for agent in registry.get("agents", []):
        agent_name = agent.get("name")
        assigned = agent.get("skills", [])
        if len(assigned) != len(set(assigned)):
            issues.append(
                Issue("error", "duplicate", f"Agent '{agent_name}' repeats a skill")
            )
        for skill in assigned:
            skill_to_agents.setdefault(skill, []).append(agent_name)

    # Filesystem and catalog must describe exactly the same set of skills.
    for skill in sorted(set(available_skills) - set(entries)):
        issues.append(
            Issue(
                "error", "unclassified", f"Skill '{skill}' is absent from the catalog"
            )
        )
    for skill in sorted(set(entries) - set(available_skills)):
        issues.append(
            Issue("error", "missing", f"Catalog skill '{skill}' has no skill directory")
        )

    # Catalog eligibility must be valid even before a skill receives a route.
    for skill, metadata in sorted(entries.items()):
        available_to = metadata.get("available_to")
        if available_to == "all":
            continue
        if not isinstance(available_to, list):
            issues.append(
                Issue("error", "catalog", f"Skill '{skill}' has invalid available_to")
            )
            continue
        unknown_agents = sorted(set(available_to) - agent_names)
        if unknown_agents:
            issues.append(
                Issue(
                    "error",
                    "catalog",
                    f"Skill '{skill}' names unknown eligible agents",
                    f"Unknown: {', '.join(unknown_agents)}",
                )
            )

    # Registry assignments must exist and respect catalog eligibility.
    for skill, assigned_agents in sorted(skill_to_agents.items()):
        metadata = entries.get(skill)
        if not metadata:
            issues.append(
                Issue(
                    "error",
                    "orphan",
                    f"Registry skill '{skill}' is not in the catalog",
                    f"Assigned to: {', '.join(assigned_agents)}",
                )
            )
            continue
        available_to = metadata.get("available_to")
        if available_to == "all":
            continue
        if not isinstance(available_to, list):
            continue
        unexpected = sorted(set(assigned_agents) - set(available_to))
        if unexpected:
            issues.append(
                Issue(
                    "error",
                    "mismatch",
                    f"Skill '{skill}' is assigned outside available_to",
                    f"Unexpected: {', '.join(unexpected)}",
                )
            )

    # Every stable role-specific skill needs at least one default route.
    for skill, metadata in sorted(entries.items()):
        if metadata["tier"] == "specialist" and skill not in skill_to_agents:
            issues.append(
                Issue(
                    "error",
                    "unassigned",
                    f"Specialist skill '{skill}' has no agent route",
                )
            )

    expected_count = len(entries)
    declared_count = registry.get("_meta", {}).get("skill_count")
    if declared_count != expected_count:
        issues.append(
            Issue(
                "error",
                "metadata",
                "Registry skill_count does not match the canonical catalog",
                f"Declared: {declared_count}, Actual: {expected_count}",
            )
        )

    return issues


def cmd_list(args: argparse.Namespace) -> int:
    """List all skills by tier."""
    catalog = load_skill_catalog()
    available_skills = discover_available_skills()

    if args.json:
        print_json(
            {
                "catalog": catalog,
                "available_skills": available_skills,
            }
        )
        return 0

    print()
    print("🎯 Skill Tiers")
    print("━" * 70)
    print()

    icons = {"core": "✅", "specialist": "🔧", "experimental": "🧪"}
    labels = {
        "core": "Core",
        "specialist": "Specialist",
        "experimental": "Experimental",
    }
    for tier in TIER_NAMES:
        print(f"{labels[tier]}:")
        print(f"  {tier_description(catalog, tier)}")
        print()
        for item in catalog.get(tier, []):
            available_to = item.get("available_to", [])
            route = "all" if available_to == "all" else ", ".join(available_to)
            print(
                f"  {icons[tier]} {item['name']:30s} {item.get('description', '—')} [{route}]"
            )
        print()

    return 0


def cmd_agent(args: argparse.Namespace) -> int:
    """Show skills for a specific agent."""
    agent_name = args.agent

    try:
        skills = get_skills_for_agent(agent_name)
    except (FileNotFoundError, ValueError) as e:
        StatusLine.fail(str(e))
        return 1

    if args.json:
        print_json({"agent": agent_name, "skills": skills})
        return 0

    print()
    print(f"🎯 Skills for Agent: {agent_name}")
    print("━" * 70)
    print()

    for tier_name in ["core", "specialist", "experimental"]:
        tier_skills = skills.get(tier_name, [])
        if not tier_skills:
            continue

        tier_desc = tier_description(load_skill_catalog(), tier_name)
        print(f"{tier_name.capitalize()} ({tier_desc}):")
        for skill in tier_skills:
            print(f"  • {skill}")
        print()

    total = sum(len(s) for s in skills.values())
    print(f"Total skills: {total}")
    print()

    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate skill assignments."""
    try:
        issues = validate_skill_assignments()
    except FileNotFoundError as e:
        StatusLine.fail(str(e))
        return 1

    if args.json:
        errors = [issue for issue in issues if issue.level == "error"]
        print_json(
            {
                "issues": [
                    {
                        "level": issue.level,
                        "category": issue.category,
                        "description": issue.description,
                        "details": issue.details,
                    }
                    for issue in issues
                ],
            }
        )
        return 1 if errors else 0

    print()
    print("🔍 Skill Assignment Validation")
    print("━" * 70)
    print()

    if not issues:
        StatusLine.ok("✅ All assignments consistent")
        print()
        return 0

    # Group issues by level
    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]
    infos = [i for i in issues if i.level == "info"]

    if errors:
        print("Errors:")
        for issue in errors:
            print(f"  {issue}")
        print()

    if warnings:
        print("Warnings:")
        for issue in warnings:
            print(f"  {issue}")
        print()

    if infos:
        print("Info:")
        for issue in infos:
            print(f"  {issue}")
        print()

    # Summary
    total = len(issues)
    print(
        f"Total issues: {total} ({len(errors)} errors, {len(warnings)} warnings, {len(infos)} info)"
    )
    print()

    return 1 if errors else 0


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Skill tier management and validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--agent", help="Show skills for specific agent (list command)")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # list command
    subparsers.add_parser("list", help="List all skills by tier")

    # validate command
    subparsers.add_parser("validate", help="Validate skill assignments")

    args = parser.parse_args()

    # Handle --agent flag as implicit command
    if args.agent and not args.command:
        args.command = "agent"

    if not args.command:
        # Default to list if no command
        args.command = "list"

    try:
        if args.command == "list":
            return cmd_list(args)
        elif args.command == "agent":
            if not args.agent:
                StatusLine.fail("--agent requires an agent name")
                return 1
            return cmd_agent(args)
        elif args.command == "validate":
            return cmd_validate(args)
        else:
            parser.print_help()
            return 1
    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        StatusLine.fail(f"Error: {e}")
        if "--debug" in sys.argv:
            raise
        return 1


if __name__ == "__main__":
    sys.exit(main())
