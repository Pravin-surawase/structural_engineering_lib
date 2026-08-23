#!/usr/bin/env python3
"""
Cross-platform instruction composition auditing.

Lists repository contracts, platform entries, scoped rules, and role prompts in
their composition order. Agent platforms load these surfaces differently, so
the script does not claim a universal precedence ladder.

When to use: after changing agent or instruction files, or while diagnosing rule conflicts.

COMPOSITION:
  1. Repository contract:   AGENTS.md
  2. Platform entries:      CLAUDE.md, .github/copilot-instructions.md
  3. Path-scoped rules:     .github/instructions/, .claude/rules/
  4. Role scope:            .github/agents/*.agent.md

Narrower guidance may add constraints but may not weaken cross-agent safety.

USAGE:
    ./scripts/python_runtime.sh scripts/config_precedence.py show <file_path>
    ./scripts/python_runtime.sh scripts/config_precedence.py audit
    ./scripts/python_runtime.sh scripts/config_precedence.py list
    ./scripts/python_runtime.sh scripts/config_precedence.py --json audit
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.output import StatusLine, print_json
from _lib.utils import REPO_ROOT
from check_instruction_drift import instruction_contract_issues


@dataclass
class InstructionFile:
    """Metadata for an instruction file."""

    path: Path
    level: str  # contract, platform, scoped-github, scoped-claude, role
    priority: int  # composition display order; not universal platform precedence
    applies_to: list[str] = field(default_factory=list)  # Patterns or globs
    description: str = ""

    def __str__(self) -> str:
        """Human-readable representation."""
        rel_path = self.path.relative_to(REPO_ROOT)
        return f"[{self.level}] {rel_path}"


@dataclass
class Issue:
    """Instruction composition issue."""

    level: str  # error, warning, info
    category: str  # conflict, redundancy, gap, mismatch
    description: str
    files: list[Path] = field(default_factory=list)
    details: str = ""

    def __str__(self) -> str:
        """Human-readable representation."""
        icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(self.level, "•")
        file_list = ", ".join(str(f.relative_to(REPO_ROOT)) for f in self.files)
        msg = f"{icon} {self.category.upper()}: {self.description}"
        if file_list:
            msg += f"\n    Files: {file_list}"
        if self.details:
            msg += f"\n    {self.details}"
        return msg


def discover_instruction_files() -> list[InstructionFile]:
    """Discover instruction files and classify by composition surface."""
    files = []

    # Role-specific prompts load after the repository/platform contract.
    agent_files = list((REPO_ROOT / ".github" / "agents").glob("*.agent.md"))
    for path in agent_files:
        # Extract applies_to from YAML frontmatter if present
        applies_to = []
        content = path.read_text(encoding="utf-8")
        # Look for file_scope in YAML frontmatter
        match = re.search(r"file_scope:\s*[\"']?([^\"'\n]+)", content)
        if match:
            applies_to = [match.group(1)]

        files.append(
            InstructionFile(
                path=path,
                level="role",
                priority=4,
                applies_to=applies_to,
                description=f"Agent {path.stem} rules",
            )
        )

    # Maintained GitHub path-scoped rules.
    instruction_files = list(
        (REPO_ROOT / ".github" / "instructions").glob("*.instructions.md")
    )
    for path in instruction_files:
        # Extract applyTo from YAML frontmatter
        applies_to = []
        content = path.read_text(encoding="utf-8")
        match = re.search(r"applyTo:\s*[\"']?([^\"'\n]+)", content)
        if match:
            applies_to = [match.group(1)]

        files.append(
            InstructionFile(
                path=path,
                level="scoped-github",
                priority=3,
                applies_to=applies_to,
                description=f"File-type rules: {path.stem}",
            )
        )

    # Exact Claude projections of maintained path-scoped rule bodies.
    claude_dir = REPO_ROOT / ".claude" / "rules"
    if claude_dir.exists():
        claude_files = list(claude_dir.glob("*.md"))
        for path in claude_files:
            # Extract globs from YAML frontmatter
            applies_to = []
            content = path.read_text(encoding="utf-8")
            match = re.search(r"globs:\s*([^\n]+)", content)
            if match:
                applies_to = [g.strip() for g in match.group(1).split(",")]

            files.append(
                InstructionFile(
                    path=path,
                    level="scoped-claude",
                    priority=3,
                    applies_to=applies_to,
                    description=f"Claude-only: {path.stem}",
                )
            )

    # Copilot platform entry. It is standalone on surfaces without AGENTS.md.
    copilot_inst = REPO_ROOT / ".github" / "copilot-instructions.md"
    if copilot_inst.exists():
        files.append(
            InstructionFile(
                path=copilot_inst,
                level="platform",
                priority=2,
                applies_to=["**"],  # Applies to everything
                description="Global Copilot instructions",
            )
        )

    # Canonical repository contract.
    agents_path = REPO_ROOT / "AGENTS.md"
    if agents_path.exists():
        files.append(
            InstructionFile(
                path=agents_path,
                level="contract",
                priority=1,
                applies_to=["**"],
                description="Canonical cross-agent repository contract",
            )
        )

    # Claude platform entry imports the repository contract.
    claude_path = REPO_ROOT / "CLAUDE.md"
    if claude_path.exists():
        files.append(
            InstructionFile(
                path=claude_path,
                level="platform",
                priority=2,
                applies_to=["**"],
                description="Claude Code entry and loading guidance",
            )
        )

    # Sort only for readable composition output.
    files.sort(key=lambda f: f.priority)
    return files


def file_matches_pattern(file_path: str, pattern: str) -> bool:
    """Check if a file path matches a glob pattern.

    Args:
        file_path: Relative file path (e.g., "Python/structural_lib/api.py")
        pattern: Glob pattern (e.g., "**/structural_lib/**", "docs/**")

    Returns:
        True if file matches pattern
    """
    from fnmatch import fnmatch

    # Normalize paths
    file_path = file_path.replace("\\", "/")
    pattern = pattern.replace("\\", "/")

    # Handle ** wildcard for recursive matching
    if "**" in pattern:
        # Convert ** to regex pattern
        regex_pattern = pattern.replace("**", ".*").replace("*", "[^/]*")
        return bool(re.match(regex_pattern, file_path))

    # Fall back to fnmatch for simple patterns
    return fnmatch(file_path, pattern)


def show_precedence(file_path: str, agent: str | None = None) -> list[InstructionFile]:
    """Show instruction surfaces relevant to a file path.

    Args:
        file_path: Relative file path from repo root
        agent: Optional agent name to show its role-specific scope

    Returns:
        Relevant surfaces in readable composition order
    """
    all_files = discover_instruction_files()
    applicable = []

    for inst_file in all_files:
        # Repository and platform entry surfaces are shown for orientation.
        if inst_file.level in ("contract", "platform"):
            applicable.append(inst_file)
            continue

        # Role-specific scope only applies if the requested role matches.
        if inst_file.level == "role":
            role_name = inst_file.path.name.removesuffix(".agent.md")
            if agent and role_name == agent:
                applicable.append(inst_file)
            continue

        # File-type and Claude rules: check patterns
        for pattern in inst_file.applies_to:
            if file_matches_pattern(file_path, pattern):
                applicable.append(inst_file)
                break

    return applicable


def validate_precedence() -> list[Issue]:
    """Validate the instruction composition contract.

    Returns:
        List of Issue objects found
    """
    issues = []
    all_files = discover_instruction_files()

    # Ambiguous patterns can cause overlapping GitHub scoped rules.
    file_type_rules = [f for f in all_files if f.level == "scoped-github"]
    patterns_seen = {}

    for inst_file in file_type_rules:
        for pattern in inst_file.applies_to:
            if pattern in patterns_seen:
                issues.append(
                    Issue(
                        level="warning",
                        category="ambiguity",
                        description=f"Multiple GitHub scoped rules for pattern: {pattern}",
                        files=[patterns_seen[pattern], inst_file.path],
                        details="Check if these rules conflict or can be merged",
                    )
                )
            else:
                patterns_seen[pattern] = inst_file.path

    # Semantic ownership and safety rules are shared with the drift validator.
    for contract_issue in instruction_contract_issues(REPO_ROOT):
        issue_path = REPO_ROOT / contract_issue["path"]
        issues.append(
            Issue(
                level="error",
                category=contract_issue["category"],
                description=contract_issue["message"],
                files=[issue_path] if issue_path.exists() else [],
            )
        )

    return issues


def audit() -> dict[str, Any]:
    """Full audit of instruction composition.

    Returns:
        Dictionary with audit results
    """
    all_files = discover_instruction_files()
    issues = validate_precedence()

    # Count by level
    level_counts = {}
    for inst_file in all_files:
        level_counts[inst_file.level] = level_counts.get(inst_file.level, 0) + 1

    # Find files with no pattern coverage
    file_type_rules = [f for f in all_files if f.level == "scoped-github"]
    claude_rules = [f for f in all_files if f.level == "scoped-claude"]

    all_patterns = []
    for inst_file in file_type_rules + claude_rules:
        all_patterns.extend(inst_file.applies_to)

    return {
        "total_files": len(all_files),
        "by_level": level_counts,
        "issues": issues,
        "patterns_covered": len(set(all_patterns)),
        "files": [
            {
                "path": str(f.path.relative_to(REPO_ROOT)),
                "level": f.level,
                "priority": f.priority,
                "applies_to": f.applies_to,
                "description": f.description,
            }
            for f in all_files
        ],
    }


def list_files_by_level() -> dict[str, list[InstructionFile]]:
    """List all instruction files grouped by composition surface.

    Returns:
        Dictionary mapping level name to list of files
    """
    all_files = discover_instruction_files()
    by_level = {}

    for inst_file in all_files:
        if inst_file.level not in by_level:
            by_level[inst_file.level] = []
        by_level[inst_file.level].append(inst_file)

    return by_level


def cmd_show(args: argparse.Namespace) -> int:
    """Show instruction composition for a file."""
    file_path = args.file_path
    agent = args.agent

    # Make path relative to repo root if absolute
    try:
        path_obj = Path(file_path)
        if path_obj.is_absolute():
            file_path = str(path_obj.relative_to(REPO_ROOT))
    except ValueError:
        pass

    applicable = show_precedence(file_path, agent=agent)

    if args.json:
        print_json(
            {
                "file": file_path,
                "agent": agent,
                "applicable_files": [
                    {
                        "path": str(f.path.relative_to(REPO_ROOT)),
                        "level": f.level,
                        "priority": f.priority,
                        "description": f.description,
                    }
                    for f in applicable
                ],
            }
        )
        return 0

    print()
    print("📋 Instruction composition for:", file_path)
    if agent:
        print(f"   (agent: {agent})")
    print("━" * 70)
    print()

    if not applicable:
        StatusLine.warn("No instruction files apply to this file")
        return 0

    for i, inst_file in enumerate(applicable, 1):
        rel_path = inst_file.path.relative_to(REPO_ROOT)
        print(f"{i}. [{inst_file.level.upper()}] {rel_path}")
        if inst_file.applies_to and inst_file.applies_to != ["**"]:
            print(f"   Patterns: {', '.join(inst_file.applies_to)}")
        if inst_file.description:
            print(f"   {inst_file.description}")
        print()

    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    """Run full composition audit."""
    audit_result = audit()

    if args.json:
        print_json(audit_result)
        return (
            1 if any(issue.level == "error" for issue in audit_result["issues"]) else 0
        )

    print()
    print("🔍 Instruction Composition Audit")
    print("━" * 70)
    print()
    print(f"Total instruction files: {audit_result['total_files']}")
    print()
    print("By level:")
    for level in [
        "contract",
        "platform",
        "scoped-github",
        "scoped-claude",
        "role",
    ]:
        count = audit_result["by_level"].get(level, 0)
        print(f"  {level:12s}: {count:2d}")
    print()
    print(f"Unique patterns covered: {audit_result['patterns_covered']}")
    print()

    issues = audit_result["issues"]
    if not issues:
        StatusLine.ok("✅ No issues found")
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


def cmd_list(args: argparse.Namespace) -> int:
    """List all instruction files by composition surface."""
    by_level = list_files_by_level()

    if args.json:
        print_json(
            {
                level: [
                    {
                        "path": str(f.path.relative_to(REPO_ROOT)),
                        "applies_to": f.applies_to,
                        "description": f.description,
                    }
                    for f in files
                ]
                for level, files in by_level.items()
            }
        )
        return 0

    print()
    print("📚 Instruction Files by Composition Surface")
    print("━" * 70)
    print()

    level_names = {
        "contract": "1. Canonical Repository Contract",
        "platform": "2. Platform Entry Files",
        "scoped-github": "3. Maintained GitHub Path Rules",
        "scoped-claude": "3. Claude Path Projections",
        "role": "4. Role-Specific Scope",
    }

    for level in [
        "contract",
        "platform",
        "scoped-github",
        "scoped-claude",
        "role",
    ]:
        files = by_level.get(level, [])
        if not files:
            continue

        print(level_names.get(level, level.upper()))
        print()

        for inst_file in files:
            rel_path = inst_file.path.relative_to(REPO_ROOT)
            print(f"  • {rel_path}")
            if inst_file.applies_to and inst_file.applies_to != ["**"]:
                print(f"    Patterns: {', '.join(inst_file.applies_to)}")
        print()

    return 0


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Cross-platform instruction composition auditing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # show command
    show_parser = subparsers.add_parser(
        "show", help="Show instruction composition for a file"
    )
    show_parser.add_argument("file_path", help="File path to check")
    show_parser.add_argument(
        "--agent", help="Agent name to include role-specific scope"
    )

    # audit command
    subparsers.add_parser("audit", help="Run full composition audit")

    # list command
    subparsers.add_parser("list", help="List instruction files by surface")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "show":
            return cmd_show(args)
        elif args.command == "audit":
            return cmd_audit(args)
        elif args.command == "list":
            return cmd_list(args)
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
