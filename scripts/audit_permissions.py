#!/usr/bin/env python3
"""Permission audit report for all agents.

Generates a report of all agent permissions, file scopes, and detects
anomalies (conflicts, mismatches, warnings) in agent_registry.json.

Usage:
    python scripts/audit_permissions.py               # Full audit report
    python scripts/audit_permissions.py --json         # Machine-readable JSON
    python scripts/audit_permissions.py --agent backend  # Single agent deep-dive
    python scripts/audit_permissions.py --check        # Anomaly check only (exit 1 if found)
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib.output import StatusLine, print_json  # noqa: E402
from tool_permissions import (  # noqa: E402
    DANGER_OPS,
    READ_OPS,
    WRITE_OPS,
    _load_registry,
)

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class Anomaly:
    """A detected permission anomaly."""

    agent: str
    severity: str  # CONFLICT, WARNING, MISMATCH
    message: str


@dataclass
class AgentPermissionInfo:
    """Summarised permission info for one agent."""

    name: str
    permission_level: str
    file_scope: str | None
    can_edit_files: bool
    tools: list[str]
    anomalies: list[Anomaly] = field(default_factory=list)


@dataclass
class AuditReport:
    """Complete audit results."""

    agents: list[AgentPermissionInfo]
    anomalies: list[Anomaly]
    summary: dict[str, int]  # permission_level → count


# Write-capable tool keywords
_WRITE_TOOLS = {"editFiles", "edit", "write", "create"}
_RUN_TOOLS = {"runInTerminal", "run", "terminal"}


def _has_write_tools(tools: list[str]) -> bool:
    """Check if tool list contains write-capable tools."""
    return bool(set(tools) & _WRITE_TOOLS)


def _has_run_tools(tools: list[str]) -> bool:
    """Check if tool list contains terminal/run tools."""
    return bool(set(tools) & _RUN_TOOLS)


# ---------------------------------------------------------------------------
# Core audit logic
# ---------------------------------------------------------------------------


def audit_permissions() -> AuditReport:
    """Run full permission audit across all agents."""
    agents_raw = _load_registry()
    all_anomalies: list[Anomaly] = []
    agent_infos: list[AgentPermissionInfo] = []
    level_counts: dict[str, int] = {}

    for agent in agents_raw:
        name = agent.get("name", "unknown")
        perm = agent.get("permission_level", "ReadOnly")
        scope = agent.get("file_scope")
        can_edit = agent.get("can_edit_files", False)
        tools = agent.get("tools", [])

        level_counts[perm] = level_counts.get(perm, 0) + 1

        anomalies: list[Anomaly] = []

        # Check 1: can_edit_files=true but ReadOnly permission → CONFLICT
        if can_edit and perm == "ReadOnly":
            anomalies.append(
                Anomaly(
                    agent=name,
                    severity="CONFLICT",
                    message=(
                        "can_edit_files=true but permission_level=ReadOnly — "
                        "registry is inconsistent"
                    ),
                )
            )

        # Check 2: DangerFullAccess with no file_scope → WARNING
        if perm == "DangerFullAccess" and scope is None:
            anomalies.append(
                Anomaly(
                    agent=name,
                    severity="WARNING",
                    message=(
                        "DangerFullAccess with no file_scope restriction — "
                        "agent can write anywhere"
                    ),
                )
            )

        # Check 3: Write tools but ReadOnly permission → MISMATCH
        if _has_write_tools(tools) and perm == "ReadOnly":
            anomalies.append(
                Anomaly(
                    agent=name,
                    severity="MISMATCH",
                    message=(
                        f"Has write tools ({', '.join(set(tools) & _WRITE_TOOLS)}) "
                        f"but permission_level=ReadOnly"
                    ),
                )
            )

        # Check 4: can_edit_files=false but WorkspaceWrite/Danger → INFO-level warning
        if not can_edit and perm in ("WorkspaceWrite", "DangerFullAccess"):
            anomalies.append(
                Anomaly(
                    agent=name,
                    severity="MISMATCH",
                    message=(
                        f"permission_level={perm} but can_edit_files=false — "
                        f"may want to align"
                    ),
                )
            )

        # Check 5: Terminal tool + permission level consistency
        has_terminal = _has_run_tools(tools)
        terminal_allowlist = agent.get("terminal_allowlist", [])

        # ReadOnly + terminal tools WITHOUT allowlist → MISMATCH
        if has_terminal and perm == "ReadOnly" and not terminal_allowlist:
            anomalies.append(
                Anomaly(
                    agent=name,
                    severity="MISMATCH",
                    message=(
                        f"Has terminal tools ({', '.join(set(tools) & _RUN_TOOLS)}) "
                        f"with permission_level=ReadOnly but no terminal_allowlist — "
                        f"should be ReadOnlyTerminal with allowlist"
                    ),
                )
            )

        # ReadOnlyTerminal without terminal tools → MISMATCH
        if perm == "ReadOnlyTerminal" and not has_terminal:
            anomalies.append(
                Anomaly(
                    agent=name,
                    severity="MISMATCH",
                    message=(
                        "permission_level=ReadOnlyTerminal but no runInTerminal tool — "
                        "terminal tier requires terminal tool access"
                    ),
                )
            )

        # Check 6: ReadOnlyTerminal should have terminal_allowlist
        if perm == "ReadOnlyTerminal" and not terminal_allowlist:
            anomalies.append(
                Anomaly(
                    agent=name,
                    severity="WARNING",
                    message=(
                        "permission_level=ReadOnlyTerminal but no terminal_allowlist — "
                        "agent can run any terminal command"
                    ),
                )
            )

        all_anomalies.extend(anomalies)
        agent_infos.append(
            AgentPermissionInfo(
                name=name,
                permission_level=perm,
                file_scope=scope,
                can_edit_files=can_edit,
                tools=tools,
                anomalies=anomalies,
            )
        )

    return AuditReport(
        agents=agent_infos,
        anomalies=all_anomalies,
        summary=level_counts,
    )


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------


def _print_report(report: AuditReport) -> None:
    """Print human-readable audit report."""
    print("🔒 Permission Audit Report")
    print("━" * 40)
    print()

    # Summary by permission level
    print("Summary:")
    for level in ("ReadOnly", "ReadOnlyTerminal", "WorkspaceWrite", "DangerFullAccess"):
        count = report.summary.get(level, 0)
        names = [a.name for a in report.agents if a.permission_level == level]
        print(f"  {level + ':':22s} {count} agent{'s' if count != 1 else ''}", end="")
        if names:
            print(f" ({', '.join(names)})", end="")
        print()
    print()

    # File scope coverage
    print("File Scope Coverage:")
    for agent in report.agents:
        if agent.file_scope:
            print(f"  {agent.name + ':':22s} {agent.file_scope}")
    unrestricted = [a.name for a in report.agents if a.file_scope is None]
    if unrestricted:
        print(f"  {'(unrestricted):':22s} {', '.join(unrestricted)}")
    print()

    # Anomalies
    if report.anomalies:
        print(f"⚠ Anomalies: {len(report.anomalies)} detected")
        for a in report.anomalies:
            icon = {"CONFLICT": "🔴", "WARNING": "🟡", "MISMATCH": "🟠"}.get(
                a.severity, "⚪"
            )
            print(f"  {icon} [{a.severity}] {a.agent}: {a.message}")
    else:
        print("⚠ Anomalies: 0 detected")
        StatusLine.ok("All permissions consistent")


def _print_agent_detail(report: AuditReport, agent_name: str) -> None:
    """Print detailed info for a single agent."""
    matches = [a for a in report.agents if a.name.lower() == agent_name.lower()]
    if not matches:
        StatusLine.fail(f"Agent '{agent_name}' not found in registry")
        return

    agent = matches[0]
    print(f"🔍 Agent: {agent.name}")
    print("━" * 40)
    print(f"  Permission Level: {agent.permission_level}")
    print(f"  Can Edit Files:   {agent.can_edit_files}")
    print(f"  File Scope:       {agent.file_scope or '(unrestricted)'}")
    print(f"  Tools:            {', '.join(agent.tools)}")
    print()

    # Operation matrix
    print("  Operation Matrix:")
    for op_set, label in [
        (READ_OPS, "read"),
        (WRITE_OPS, "write"),
        (DANGER_OPS, "danger"),
    ]:
        allowed = (
            (label == "read")
            or (
                label == "write"
                and agent.permission_level in ("WorkspaceWrite", "DangerFullAccess")
            )
            or (label == "danger" and agent.permission_level == "DangerFullAccess")
        )
        icon = "✅" if allowed else "🚫"
        ops_str = ", ".join(sorted(op_set))
        print(f"    {icon} {label:8s} → {ops_str}")
    print()

    if agent.anomalies:
        print(f"  Anomalies ({len(agent.anomalies)}):")
        for a in agent.anomalies:
            print(f"    [{a.severity}] {a.message}")
    else:
        StatusLine.ok(f"  No anomalies for {agent.name}")


def _report_to_dict(report: AuditReport) -> dict:
    """Convert audit report to JSON-serializable dict."""
    return {
        "summary": report.summary,
        "agents": [
            {
                "name": a.name,
                "permission_level": a.permission_level,
                "file_scope": a.file_scope,
                "can_edit_files": a.can_edit_files,
                "tools": a.tools,
                "anomalies": [
                    {"severity": an.severity, "message": an.message}
                    for an in a.anomalies
                ],
            }
            for a in report.agents
        ],
        "anomalies": [
            {"agent": a.agent, "severity": a.severity, "message": a.message}
            for a in report.anomalies
        ],
        "total_agents": len(report.agents),
        "total_anomalies": len(report.anomalies),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit agent permissions from agent_registry.json",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output as JSON",
    )
    parser.add_argument(
        "--agent",
        default=None,
        help="Deep-dive into a single agent",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check for anomalies (exit 1 if found)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    report = audit_permissions()

    if args.as_json:
        print_json(_report_to_dict(report))
        return 1 if args.check and report.anomalies else 0

    if args.agent:
        _print_agent_detail(report, args.agent)
        agent_anomalies = [
            a for a in report.anomalies if a.agent.lower() == args.agent.lower()
        ]
        return 1 if args.check and agent_anomalies else 0

    if args.check:
        if report.anomalies:
            StatusLine.fail(f"{len(report.anomalies)} anomalies detected")
            for a in report.anomalies:
                print(f"  [{a.severity}] {a.agent}: {a.message}")
            return 1
        StatusLine.ok("No anomalies — all permissions consistent")
        return 0

    _print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
