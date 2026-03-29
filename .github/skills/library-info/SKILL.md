---
name: library-info
description: "Get library metadata, API surface, architecture, element support, CLI commands, scripts, and agent inventory in one command. Use at session start or when agents need project context fast."
argument-hint: "Optional flag: --api, --architecture, --elements, --cli, --scripts, --agents, --json, --all"
---

# Library Info Skill

Quick access to consolidated project metadata. Prevents agents from hunting through scattered files for version, API functions, architecture, element support, and tooling info.

## When to Use

- At session start — get a quick project snapshot
- Before planning work — check what elements are implemented vs placeholder
- Before writing API code — see all 26 public functions at a glance
- When onboarding to a new area — understand architecture rules
- For handoff context — generate JSON for machine consumption

## Quick Overview (default)

```bash
.venv/bin/python scripts/library_info.py
```

Shows: version, Python requirement, API count, element status, script/agent counts, stack summary.

## Drill-Down Options

### Public API Functions
```bash
.venv/bin/python scripts/library_info.py --api
```
Lists all 26 public functions from `services/api.py` with parameter names and line numbers.

> For detailed signatures with types and defaults, use `/api-discovery` skill instead.

### Architecture (4-Layer Rules)
```bash
.venv/bin/python scripts/library_info.py --architecture
```
Shows the 4-layer import hierarchy, units rule, and element isolation rule.

### IS 456 Element Support
```bash
.venv/bin/python scripts/library_info.py --elements
```
Shows which elements (beam, column, slab, footing, wall, staircase) are implemented vs placeholder, with their module files.

### CLI Commands
```bash
.venv/bin/python scripts/library_info.py --cli
```
Lists available `python -m structural_lib` subcommands.

### Scripts & Automation
```bash
.venv/bin/python scripts/library_info.py --scripts
```
Shows script counts and how to discover automation tasks.

### Agents, Skills & Prompts
```bash
.venv/bin/python scripts/library_info.py --agents
```
Lists all 12 agents with descriptions, 8 skills, and 14 prompts.

### Everything
```bash
.venv/bin/python scripts/library_info.py --all
```
Prints all sections above in one output.

### Machine-Readable JSON
```bash
.venv/bin/python scripts/library_info.py --json
```
Full project metadata as JSON — useful for programmatic consumption or agent context injection.

## Integration with run.sh

```bash
./run.sh info                    # Quick overview
./run.sh info --api              # API functions
./run.sh info --elements         # Element support map
./run.sh info --json             # JSON output
```

## Relationship to Other Skills

| Need | Use This Skill |
|------|---------------|
| Quick project snapshot | **library-info** (this skill) |
| Exact function signatures with types | `/api-discovery` |
| Run IS 456 compliance tests | `/is456-verification` |
| Check architecture boundaries | `/architecture-check` |
| Add a new structural element | `/new-structural-element` |

## Key Facts This Skill Surfaces

- **Version**: Current release from `pyproject.toml`
- **26 public API functions** in `services/api.py` (not the stub `api.py`)
- **3 implemented elements**: beam (7 modules), column (2 modules), common (3 modules)
- **4 placeholder elements**: slab, footing, wall, staircase
- **86+ scripts** across Python and shell
- **12 agents**, **8 skills**, **14 prompts** for AI workflow
- **4-layer architecture**: Core → Codes → Services → UI (strict import direction)
