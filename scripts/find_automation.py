#!/usr/bin/env python3
"""
Find the right automation script for a task.

When to use: When you need a script but do not know which one. Searches the
current non-deprecated automation tasks and derives categories from their
canonical `group` metadata.

Usage:
    ./scripts/python_runtime.sh scripts/find_automation.py "move file"
    ./scripts/python_runtime.sh scripts/find_automation.py --list
    ./scripts/python_runtime.sh scripts/find_automation.py --group Docs
"""

from __future__ import annotations

import argparse
import json
import sys
from difflib import get_close_matches
from pathlib import Path


def load_automation_map() -> dict:
    """Load the automation map."""
    script_dir = Path(__file__).parent
    map_path = script_dir / "automation-map.json"

    if not map_path.exists():
        print("❌ automation-map.json not found")
        sys.exit(1)

    with open(map_path, "r", encoding="utf-8") as f:
        return json.load(f)


def active_tasks(automation_map: dict) -> dict[str, dict]:
    """Return discoverable tasks; deprecated migration aliases stay hidden."""
    return {
        name: info
        for name, info in automation_map.get("tasks", {}).items()
        if not info.get("deprecated", False)
    }


def find_task(query: str, automation_map: dict) -> list[tuple[str, dict]]:
    """Find tasks matching the query."""
    tasks = active_tasks(automation_map)
    query_lower = query.lower()

    # Direct match
    if query_lower in tasks:
        return [(query_lower, tasks[query_lower])]

    # Partial match
    matches = []
    for task_name, task_info in tasks.items():
        if query_lower in task_name:
            matches.append((task_name, task_info))
        elif query_lower in task_info.get("description", "").lower():
            matches.append((task_name, task_info))

    if matches:
        return matches

    # Fuzzy match
    task_names = list(tasks.keys())
    close = get_close_matches(query_lower, task_names, n=3, cutoff=0.4)
    return [(name, tasks[name]) for name in close]


def print_task(task_name: str, task_info: dict):
    """Print a task nicely."""
    group = task_info.get("group", "")
    group_tag = f" [{group}]" if group else ""
    print(f"  📋 {task_name}{group_tag}")
    print(f"     Script: {task_info['script']}")
    print(f"     {task_info.get('description', '')}")
    if "context_docs" in task_info:
        print("     📚 Context docs:")
        for doc in task_info["context_docs"]:
            print(f"        - {doc}")
    if "never_use" in task_info:
        never = ", ".join(task_info["never_use"])
        print(f"     ⚠️  Never use: {never}")
    if "prereq" in task_info:
        print(f"     📌 First run: {task_info['prereq']}")
    print()


def get_tasks_by_group(automation_map: dict) -> dict[str, list[tuple[str, dict]]]:
    """Group tasks by their 'group' field."""
    tasks = active_tasks(automation_map)
    groups: dict[str, list[tuple[str, dict]]] = {}
    for task_name, task_info in tasks.items():
        group = task_info.get("group", "Ungrouped")
        groups.setdefault(group, []).append((task_name, task_info))
    return groups


def list_group(group_name: str, automation_map: dict):
    """List all tasks in a specific group."""
    groups = get_tasks_by_group(automation_map)
    # Case-insensitive lookup
    matched = None
    for g in groups:
        if g.lower() == group_name.lower():
            matched = g
            break
    if not matched:
        print(f"❌ Unknown group: {group_name}")
        print(f"   Available: {', '.join(sorted(groups.keys()))}")
        sys.exit(1)
    print(f"\n📂 Group: {matched} ({len(groups[matched])} tasks)\n")
    for task_name, task_info in groups[matched]:
        print_task(task_name, task_info)


def list_all_groups(automation_map: dict):
    """List all groups with their task counts, then tasks under each."""
    groups = get_tasks_by_group(automation_map)
    total = sum(len(v) for v in groups.values())
    print(f"\n📚 Script Groups ({total} tasks in {len(groups)} groups)\n")
    for group_name in sorted(groups.keys()):
        task_list = groups[group_name]
        print(f"━━ {group_name} ({len(task_list)}) ━━")
        for task_name, task_info in task_list:
            print(f"  • {task_name}: {task_info.get('description', '')[:80]}")
        print()
    print("Use: ./scripts/python_runtime.sh scripts/find_automation.py --group <name>")


def main():
    parser = argparse.ArgumentParser(
        description="Find the right automation script for a task"
    )
    parser.add_argument("query", nargs="?", help="Task description to search for")
    parser.add_argument("--list", action="store_true", help="List all categories")
    parser.add_argument(
        "--group",
        "--category",
        dest="group",
        help="List tasks in a canonical group; --category is a compatibility alias",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    automation_map = load_automation_map()

    if args.list:
        list_all_groups(automation_map)
        return

    if args.group:
        list_group(args.group, automation_map)
        return

    if not args.query:
        parser.print_help()
        sys.exit(1)

    matches = find_task(args.query, automation_map)

    if args.json:
        result = [{"task": name, **info} for name, info in matches]
        print(json.dumps(result, indent=2))
        return

    if not matches:
        print(f'\n❌ No automation found for: "{args.query}"')
        print("   Try: ./scripts/python_runtime.sh scripts/find_automation.py --list")
        sys.exit(1)

    print(f'\n🔍 Automation for: "{args.query}"\n')
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    for task_name, task_info in matches:
        print_task(task_name, task_info)

    if len(matches) == 1:
        print("✅ Copy and use the script above!")


if __name__ == "__main__":
    main()
