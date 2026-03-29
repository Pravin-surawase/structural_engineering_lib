#!/usr/bin/env python3
"""Library info aggregator — single command to surface key project metadata.

Consolidates version, API surface, architecture, element support, CLI commands,
scripts, and health score into one queryable output.

Usage:
    python scripts/library_info.py                    # Full overview
    python scripts/library_info.py --api              # Public API functions
    python scripts/library_info.py --architecture     # 4-layer summary
    python scripts/library_info.py --elements         # IS 456 element support
    python scripts/library_info.py --cli              # CLI commands
    python scripts/library_info.py --scripts          # Automation scripts
    python scripts/library_info.py --agents           # Agent/skill/prompt inventory
    python scripts/library_info.py --json             # Machine-readable output
    python scripts/library_info.py --all              # Everything (verbose)
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PYTHON_ROOT = REPO_ROOT / "Python"
LIB_ROOT = PYTHON_ROOT / "structural_lib"
IS456_ROOT = LIB_ROOT / "codes" / "is456"
PYPROJECT = PYTHON_ROOT / "pyproject.toml"
LLMS_TXT = REPO_ROOT / "llms.txt"


def _read_version() -> str:
    """Extract version from pyproject.toml."""
    try:
        text = PYPROJECT.read_text()
        m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
        return m.group(1) if m else "unknown"
    except FileNotFoundError:
        return "unknown"


def _read_python_requires() -> str:
    """Extract requires-python from pyproject.toml."""
    try:
        text = PYPROJECT.read_text()
        m = re.search(r'^requires-python\s*=\s*"([^"]+)"', text, re.MULTILINE)
        return m.group(1) if m else "unknown"
    except FileNotFoundError:
        return "unknown"


def _count_tests() -> int:
    """Count test files."""
    test_dir = PYTHON_ROOT / "tests"
    if not test_dir.exists():
        return 0
    return sum(1 for f in test_dir.rglob("test_*.py"))


def _get_api_functions() -> list[dict]:
    """Extract public function names and signatures from services/api.py."""
    api_file = LIB_ROOT / "services" / "api.py"
    if not api_file.exists():
        return []

    functions = []
    try:
        tree = ast.parse(api_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                params = []
                for arg in node.args.args:
                    if arg.arg != "self":
                        params.append(arg.arg)
                functions.append({
                    "name": node.name,
                    "params": params,
                    "line": node.lineno,
                })
    except (SyntaxError, FileNotFoundError):
        pass
    return functions


def _get_element_support() -> list[dict]:
    """Scan codes/is456/ for element subfolders and their modules."""
    elements = []
    if not IS456_ROOT.exists():
        return elements

    for d in sorted(IS456_ROOT.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        modules = [
            f.stem for f in sorted(d.glob("*.py"))
            if f.stem != "__init__" and not f.stem.startswith("_")
        ]
        has_code = len(modules) > 0
        elements.append({
            "element": d.name,
            "status": "implemented" if has_code else "placeholder",
            "modules": modules,
        })
    return elements


def _get_cli_commands() -> list[str]:
    """Extract CLI subcommands from __main__.py or llms.txt."""
    commands = []
    main_file = LIB_ROOT / "__main__.py"
    if main_file.exists():
        text = main_file.read_text()
        for m in re.finditer(r"add_parser\(['\"](\w+)['\"]", text):
            commands.append(m.group(1))
    if not commands and LLMS_TXT.exists():
        text = LLMS_TXT.read_text()
        in_cli = False
        for line in text.splitlines():
            if "CLI" in line and "python -m" in line:
                in_cli = True
                continue
            if in_cli:
                m = re.match(r"^- (\w+)\s+:", line)
                if m:
                    commands.append(m.group(1))
                elif line.strip() and not line.startswith("-"):
                    in_cli = False
    return commands


def _get_scripts_summary() -> dict:
    """Count scripts and load automation map if available."""
    scripts_dir = REPO_ROOT / "scripts"
    script_count = sum(1 for f in scripts_dir.glob("*.py")) if scripts_dir.exists() else 0
    shell_count = sum(1 for f in scripts_dir.glob("*.sh")) if scripts_dir.exists() else 0

    auto_map = scripts_dir / "automation-map.json"
    categories = 0
    tasks = 0
    if auto_map.exists():
        try:
            data = json.loads(auto_map.read_text())
            if isinstance(data, dict):
                categories = len(data)
                tasks = sum(len(v) if isinstance(v, list) else 1 for v in data.values())
        except (json.JSONDecodeError, KeyError):
            pass

    return {
        "python_scripts": script_count,
        "shell_scripts": shell_count,
        "automation_categories": categories,
        "automation_tasks": tasks,
    }


def _get_agents_summary() -> dict:
    """Count agents, skills, and prompts."""
    agents_dir = REPO_ROOT / ".github" / "agents"
    skills_dir = REPO_ROOT / ".github" / "skills"
    prompts_dir = REPO_ROOT / ".github" / "prompts"

    agents = []
    if agents_dir.exists():
        for f in sorted(agents_dir.glob("*.agent.md")):
            name = f.stem.replace(".agent", "")
            # Read description from YAML frontmatter
            text = f.read_text()
            desc = ""
            m = re.search(r'description:\s*["\']?([^"\'\n]+)', text)
            if m:
                desc = m.group(1).strip()
            agents.append({"name": name, "description": desc})

    skills = []
    if skills_dir.exists():
        for d in sorted(skills_dir.iterdir()):
            skill_file = d / "SKILL.md"
            if skill_file.exists():
                text = skill_file.read_text()
                desc = ""
                m = re.search(r'description:\s*["\']?([^"\'\n]+)', text)
                if m:
                    desc = m.group(1).strip()
                skills.append({"name": d.name, "description": desc})

    prompts = []
    if prompts_dir.exists():
        for f in sorted(prompts_dir.glob("*.prompt.md")):
            name = f.stem.replace(".prompt", "")
            prompts.append(name)

    return {
        "agents": agents,
        "skills": skills,
        "prompts": prompts,
    }


ARCHITECTURE = """
4-Layer Architecture (STRICT — never mix)
══════════════════════════════════════════
Layer 1: Core Types    → core/           Code-agnostic base classes, types, constants
Layer 2: Design Codes  → codes/is456/    Pure math, NO I/O, explicit units (mm, N/mm², kN, kNm)
Layer 3: Services      → services/       Orchestration: api.py, adapters.py, pipelines
Layer 4: UI/IO         → react_app/, fastapi_app/

Import rule: Core ← Codes ← Services ← UI (never upward)
Units rule:  All explicit — mm, N/mm², kN, kNm. No hidden conversions.
Element rule: beam/ cannot import from column/ — shared code in common/ only
"""


def _print_header(title: str) -> None:
    print(f"\n{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}")


def _print_overview() -> None:
    version = _read_version()
    python_req = _read_python_requires()
    test_count = _count_tests()
    api_funcs = _get_api_functions()
    elements = _get_element_support()
    scripts = _get_scripts_summary()
    agents_info = _get_agents_summary()

    implemented = [e for e in elements if e["status"] == "implemented"]
    placeholder = [e for e in elements if e["status"] == "placeholder"]

    _print_header("structural-lib-is456 — Library Overview")
    print(f"""
  Version:         {version}
  Python:          {python_req}
  Package:         structural-lib-is456 (PyPI)
  Design Code:     IS 456:2000 (Indian Standard for RC)

  Public API:      {len(api_funcs)} functions (services/api.py)
  Test Files:      {test_count}
  Elements:        {len(implemented)} implemented, {len(placeholder)} placeholder
  Scripts:         {scripts['python_scripts']} Python + {scripts['shell_scripts']} shell ({scripts['automation_tasks']} tasks mapped)
  Agents:          {len(agents_info['agents'])} agents, {len(agents_info['skills'])} skills, {len(agents_info['prompts'])} prompts

  Stack:           React 19 + R3F → FastAPI → Python structural_lib
""")


def _print_api() -> None:
    funcs = _get_api_functions()
    _print_header("Public API Functions (services/api.py)")
    if not funcs:
        print("  No functions found.")
        return
    for f in funcs:
        params = ", ".join(f["params"][:6])
        if len(f["params"]) > 6:
            params += ", ..."
        print(f"  L{f['line']:>4}  {f['name']}({params})")
    print(f"\n  Total: {len(funcs)} public functions")
    print(f"  Lookup: .venv/bin/python scripts/discover_api_signatures.py <func>")


def _print_architecture() -> None:
    _print_header("Architecture")
    print(ARCHITECTURE)


def _print_elements() -> None:
    elements = _get_element_support()
    _print_header("IS 456 Element Support (codes/is456/)")
    for e in elements:
        icon = "✅" if e["status"] == "implemented" else "⬜"
        mods = ", ".join(e["modules"]) if e["modules"] else "(empty)"
        print(f"  {icon} {e['element']:<12} {mods}")
    print()


def _print_cli() -> None:
    commands = _get_cli_commands()
    _print_header("CLI Commands (python -m structural_lib)")
    if commands:
        for cmd in commands:
            print(f"  - {cmd}")
    else:
        print("  Run: python -m structural_lib --help")
    print()


def _print_scripts() -> None:
    info = _get_scripts_summary()
    _print_header("Scripts & Automation")
    print(f"  Python scripts:  {info['python_scripts']}")
    print(f"  Shell scripts:   {info['shell_scripts']}")
    print(f"  Mapped tasks:    {info['automation_tasks']} across {info['automation_categories']} categories")
    print(f"\n  Discovery:  .venv/bin/python scripts/find_automation.py <query>")
    print(f"  Full list:  .venv/bin/python scripts/find_automation.py --list")
    print()


def _print_agents() -> None:
    info = _get_agents_summary()
    _print_header("Agents, Skills & Prompts")

    print("\n  Agents:")
    for a in info["agents"]:
        print(f"    {a['name']:<22} {a['description']}")

    print(f"\n  Skills ({len(info['skills'])}):")
    for s in info["skills"]:
        print(f"    {s['name']:<28} {s['description'][:60]}")

    print(f"\n  Prompts ({len(info['prompts'])}):")
    for i, p in enumerate(info["prompts"]):
        if i % 4 == 0:
            print("    ", end="")
        print(f"{p:<24}", end="")
        if (i + 1) % 4 == 0:
            print()
    print("\n")


def _print_json() -> None:
    data = {
        "version": _read_version(),
        "python_requires": _read_python_requires(),
        "api_functions": _get_api_functions(),
        "elements": _get_element_support(),
        "cli_commands": _get_cli_commands(),
        "scripts": _get_scripts_summary(),
        "agents": _get_agents_summary(),
        "test_files": _count_tests(),
    }
    json.dump(data, sys.stdout, indent=2)
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Library info aggregator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--api", action="store_true", help="Public API functions")
    parser.add_argument("--architecture", action="store_true", help="4-layer architecture")
    parser.add_argument("--elements", action="store_true", help="IS 456 element support")
    parser.add_argument("--cli", action="store_true", help="CLI commands")
    parser.add_argument("--scripts", action="store_true", help="Scripts & automation")
    parser.add_argument("--agents", action="store_true", help="Agent/skill/prompt inventory")
    parser.add_argument("--json", action="store_true", help="Machine-readable JSON output")
    parser.add_argument("--all", action="store_true", help="Show everything")
    args = parser.parse_args()

    has_flag = any([args.api, args.architecture, args.elements, args.cli,
                    args.scripts, args.agents, args.json, args.all])

    if args.json:
        _print_json()
        return

    if not has_flag:
        _print_overview()
        return

    if args.all or args.api:
        _print_api()
    if args.all or args.architecture:
        _print_architecture()
    if args.all or args.elements:
        _print_elements()
    if args.all or args.cli:
        _print_cli()
    if args.all or args.scripts:
        _print_scripts()
    if args.all or args.agents:
        _print_agents()

    if args.all:
        _print_overview()


if __name__ == "__main__":
    main()
