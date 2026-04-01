#!/usr/bin/env python3
"""
Skill tier classification and management for AI agents.

Classifies skills into three tiers:
  - Core: Always available to all agents
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

# Skill tier definitions
SKILL_TIERS: dict[str, dict[str, Any]] = {
    "core": {
        "description": "Always available to all agents",
        "skills": ["session-management", "api-discovery", "safe-file-ops"],
        "auto_load": True,
    },
    "specialist": {
        "description": "Available to specific agents based on role",
        "skills": [
            "is456-verification",
            "new-structural-element",
            "function-quality-pipeline",
            "react-validation",
            "architecture-check",
            "agent-evolution",
        ],
        "auto_load": False,
        "requires_agent_match": True,
    },
    "experimental": {
        "description": "Require explicit activation — new or unstable skills",
        "skills": [],  # None yet — placeholder for future skills
        "auto_load": False,
        "requires_activation": True,
    },
}

# Specialist skill to agent mappings
SPECIALIST_SKILL_AGENTS: dict[str, list[str]] = {
    "is456-verification": [
        "structural-math",
        "structural-engineer",
        "tester",
        "backend",
    ],
    "new-structural-element": ["structural-math"],
    "function-quality-pipeline": ["structural-math", "tester", "reviewer"],
    "react-validation": ["frontend", "reviewer"],
    "architecture-check": ["reviewer"],
    "agent-evolution": ["agent-evolver"],
}


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
        # Check which tier this skill belongs to
        found = False
        for tier_name, tier_config in SKILL_TIERS.items():
            if skill in tier_config["skills"]:
                classified[tier_name].append(skill)
                found = True
                break

        # If not found in any tier, treat as specialist (assume it's a valid skill)
        if not found:
            classified["specialist"].append(skill)

    return classified


def validate_skill_assignments() -> list[Issue]:
    """Validate skill assignments against tier definitions.

    Returns:
        List of Issue objects found
    """
    issues = []
    registry = load_agent_registry()
    available_skills = discover_available_skills()

    # Build a reverse map: skill -> agents
    skill_to_agents: dict[str, list[str]] = {}
    for agent in registry.get("agents", []):
        agent_name = agent.get("name")
        for skill in agent.get("skills", []):
            if skill not in skill_to_agents:
                skill_to_agents[skill] = []
            skill_to_agents[skill].append(agent_name)

    # Check 1: All agents should have core skills
    core_skills = SKILL_TIERS["core"]["skills"]
    for agent in registry.get("agents", []):
        agent_name = agent.get("name")
        agent_skills = agent.get("skills", [])

        missing_core = [skill for skill in core_skills if skill not in agent_skills]
        if missing_core:
            issues.append(
                Issue(
                    level="warning",
                    category="missing",
                    description=f"Agent '{agent_name}' missing core skills",
                    details=f"Missing: {', '.join(missing_core)}",
                )
            )

    # Check 2: Specialist skills assigned to correct agents
    for skill, expected_agents in SPECIALIST_SKILL_AGENTS.items():
        assigned_agents = skill_to_agents.get(skill, [])

        # Check for unexpected assignments
        unexpected = [a for a in assigned_agents if a not in expected_agents]
        if unexpected:
            issues.append(
                Issue(
                    level="warning",
                    category="mismatch",
                    description=f"Skill '{skill}' assigned to unexpected agents",
                    details=f"Expected: {', '.join(expected_agents)}, Got: {', '.join(unexpected)}",
                )
            )

        # Check for missing assignments
        missing = [a for a in expected_agents if a not in assigned_agents]
        if missing:
            issues.append(
                Issue(
                    level="info",
                    category="unassigned",
                    description=f"Skill '{skill}' not assigned to expected agents",
                    details=f"Missing from: {', '.join(missing)}",
                )
            )

    # Check 3: Skills in registry but not in SKILL_TIERS or available
    all_tier_skills = []
    for tier_config in SKILL_TIERS.values():
        all_tier_skills.extend(tier_config["skills"])

    for skill, agents in skill_to_agents.items():
        if skill not in all_tier_skills and skill not in available_skills:
            issues.append(
                Issue(
                    level="warning",
                    category="orphan",
                    description=f"Skill '{skill}' in registry but not in tiers or available",
                    details=f"Assigned to: {', '.join(agents)}",
                )
            )

    # Check 4: Skills in SKILL_TIERS but not assigned to any agent
    for tier_name, tier_config in SKILL_TIERS.items():
        for skill in tier_config["skills"]:
            if skill not in skill_to_agents:
                # Core skills should be on ALL agents
                if tier_name == "core":
                    issues.append(
                        Issue(
                            level="error",
                            category="missing",
                            description=f"Core skill '{skill}' not assigned to any agent",
                        )
                    )
                else:
                    issues.append(
                        Issue(
                            level="info",
                            category="unassigned",
                            description=f"{tier_name.capitalize()} skill '{skill}' not assigned",
                        )
                    )

    return issues


def cmd_list(args: argparse.Namespace) -> int:
    """List all skills by tier."""
    available_skills = discover_available_skills()

    if args.json:
        print_json(
            {
                "tiers": SKILL_TIERS,
                "specialist_assignments": SPECIALIST_SKILL_AGENTS,
                "available_skills": available_skills,
            }
        )
        return 0

    print()
    print("🎯 Skill Tiers")
    print("━" * 70)
    print()

    # Core tier
    core_config = SKILL_TIERS["core"]
    print("Core (always available):")
    print(f"  {core_config['description']}")
    print()
    for skill in core_config["skills"]:
        # Get skill description from SKILL.md if available
        skill_dir = REPO_ROOT / ".github" / "skills" / skill
        description = "—"
        if skill_dir.exists():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                # Read first line of description from SKILL.md
                content = skill_file.read_text(encoding="utf-8")
                lines = [
                    line
                    for line in content.split("\n")
                    if line.strip() and not line.startswith("#")
                ]
                if lines:
                    description = lines[0][:60] + ("..." if len(lines[0]) > 60 else "")

        print(f"  ✅ {skill:30s} {description}")
    print()

    # Specialist tier
    specialist_config = SKILL_TIERS["specialist"]
    print("Specialist (role-specific):")
    print(f"  {specialist_config['description']}")
    print()
    for skill in specialist_config["skills"]:
        agents = SPECIALIST_SKILL_AGENTS.get(skill, [])
        agent_list = ", ".join(agents) if agents else "unassigned"
        print(f"  🔧 {skill:30s} → {agent_list}")
    print()

    # Experimental tier
    experimental_config = SKILL_TIERS["experimental"]
    print("Experimental:")
    print(f"  {experimental_config['description']}")
    print()
    if experimental_config["skills"]:
        for skill in experimental_config["skills"]:
            print(f"  🧪 {skill}")
    else:
        print("  (none)")
    print()

    # Available skills not in tiers
    all_tier_skills = []
    for tier_config in SKILL_TIERS.values():
        all_tier_skills.extend(tier_config["skills"])

    orphaned = [s for s in available_skills if s not in all_tier_skills]
    if orphaned:
        print("Available but unclassified:")
        for skill in orphaned:
            print(f"  ❓ {skill}")
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

        tier_desc = SKILL_TIERS[tier_name]["description"]
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
        return 0

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
