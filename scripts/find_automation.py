#!/usr/bin/env python3
"""
Find the right automation script for a task.

Usage:
    python scripts/find_automation.py "commit code"
    python scripts/find_automation.py "move file"
    python scripts/find_automation.py --list
    python scripts/find_automation.py --category git_workflow
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


def find_task(query: str, automation_map: dict) -> list[tuple[str, dict]]:
    """Find tasks matching the query."""
    tasks = automation_map.get("tasks", {})
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
    print(f"  📋 {task_name}")
    print(f"     Script: {task_info['script']}")
    print(f"     {task_info.get('description', '')}")
    if "never_use" in task_info:
        never = ", ".join(task_info["never_use"])
        print(f"     ⚠️  Never use: {never}")
    if "prereq" in task_info:
        print(f"     📌 First run: {task_info['prereq']}")
    print()


def list_category(category: str, automation_map: dict):
    """List all tasks in a category."""
    categories = automation_map.get("categories", {})
    tasks = automation_map.get("tasks", {})

    if category not in categories:
        print(f"❌ Unknown category: {category}")
        print(f"   Available: {', '.join(categories.keys())}")
        sys.exit(1)

    print(f"\n📂 Category: {category}\n")
    for task_name in categories[category]:
        if task_name in tasks:
            print_task(task_name, tasks[task_name])


def list_all_categories(automation_map: dict):
    """List all categories and their tasks."""
    categories = automation_map.get("categories", {})

    print("\n📚 Available Automation Categories\n")
    for cat_name, task_list in categories.items():
        print(f"  {cat_name}: {len(task_list)} tasks")
    print()
    print("Use: python scripts/find_automation.py --category <name>")


def main():
    parser = argparse.ArgumentParser(
        description="Find the right automation script for a task"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Task description to search for"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all categories"
    )
    parser.add_argument(
        "--category",
        help="List tasks in a specific category"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    automation_map = load_automation_map()

    if args.list:
        list_all_categories(automation_map)
        return

    if args.category:
        list_category(args.category, automation_map)
        return

    if not args.query:
        parser.print_help()
        sys.exit(1)

    matches = find_task(args.query, automation_map)

    if args.json:
        result = [
            {"task": name, **info}
            for name, info in matches
        ]
        print(json.dumps(result, indent=2))
        return

    if not matches:
        print(f"\n❌ No automation found for: \"{args.query}\"")
        print("   Try: python scripts/find_automation.py --list")
        sys.exit(1)

    print(f"\n🔍 Automation for: \"{args.query}\"\n")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    for task_name, task_info in matches:
        print_task(task_name, task_info)

    if len(matches) == 1:
        print("✅ Copy and use the script above!")


if __name__ == "__main__":
    main()
