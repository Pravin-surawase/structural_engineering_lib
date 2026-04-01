"""Agent registry — single source of truth for agent list.

Auto-discovers agents from .github/agents/*.agent.md and provides
a central API for agent metadata.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .utils import REPO_ROOT

# Safety-critical agents require human approval for ALL modifications
SAFETY_CRITICAL_AGENTS = {"structural-engineer", "structural-math"}


@dataclass
class AgentInfo:
    """Agent metadata extracted from .agent.md file."""

    name: str
    description: str
    tools: list[str]
    model: str
    md_path: Path
    is_safety_critical: bool


# Cache for discovered agents
_AGENT_CACHE: dict[str, AgentInfo] | None = None


def discover_agents() -> dict[str, AgentInfo]:
    """Discover all agents from .github/agents/*.agent.md files.

    Parses YAML frontmatter to extract agent metadata.
    Results are cached after first discovery.

    Returns:
        Dict mapping agent name to AgentInfo.
    """
    global _AGENT_CACHE

    if _AGENT_CACHE is not None:
        return _AGENT_CACHE

    agents: dict[str, AgentInfo] = {}
    agents_dir = REPO_ROOT / ".github" / "agents"

    if not agents_dir.exists():
        _AGENT_CACHE = agents
        return agents

    for agent_file in sorted(agents_dir.glob("*.agent.md")):
        agent_name = agent_file.stem

        try:
            content = agent_file.read_text(encoding="utf-8")
            metadata = _parse_frontmatter(content)

            agents[agent_name] = AgentInfo(
                name=agent_name,
                description=metadata.get("description", ""),
                tools=metadata.get("tools", []),
                model=metadata.get("model", ""),
                md_path=agent_file,
                is_safety_critical=agent_name in SAFETY_CRITICAL_AGENTS,
            )
        except (OSError, UnicodeDecodeError):
            # Skip files that can't be read
            continue

    _AGENT_CACHE = agents
    return agents


def _parse_frontmatter(content: str) -> dict[str, Any]:
    """Parse YAML frontmatter from markdown content.

    Extracts description, tools, model from the YAML block.
    """
    # Look for YAML frontmatter between --- markers
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    yaml_content = match.group(1)
    metadata: dict[str, Any] = {}

    # Simple YAML parser for our specific fields
    for line in yaml_content.split("\n"):
        line = line.strip()

        # Description (quoted string)
        if line.startswith("description:"):
            desc = line.split(":", 1)[1].strip().strip('"')
            metadata["description"] = desc

        # Model (may be quoted)
        elif line.startswith("model:"):
            model = line.split(":", 1)[1].strip().strip('"')
            metadata["model"] = model

        # Tools (array)
        elif line.startswith("tools:"):
            tools_match = re.search(r"\[(.*?)\]", line)
            if tools_match:
                tools_str = tools_match.group(1)
                tools = [t.strip().strip("'\"") for t in tools_str.split(",")]
                metadata["tools"] = tools

    return metadata


def get_agent_names() -> list[str]:
    """Get sorted list of all agent names.

    Returns:
        Sorted list of agent names (e.g., ["backend", "frontend", ...])
    """
    agents = discover_agents()
    return sorted(agents.keys())


def is_safety_critical(agent_name: str) -> bool:
    """Check if agent is safety-critical (structural-engineer, structural-math).

    Safety-critical agents require human approval for all modifications.

    Args:
        agent_name: Name of the agent.

    Returns:
        True if agent is safety-critical.
    """
    return agent_name in SAFETY_CRITICAL_AGENTS


def get_agent_info(agent_name: str) -> AgentInfo | None:
    """Get metadata for a specific agent.

    Args:
        agent_name: Name of the agent.

    Returns:
        AgentInfo if found, None otherwise.
    """
    agents = discover_agents()
    return agents.get(agent_name)
