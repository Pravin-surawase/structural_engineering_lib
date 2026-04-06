---
description: "Python structural_lib core — IS 456 math, services, adapters, 4-layer architecture"
tools: ['search', 'editFiles', 'runInTerminal', 'listFiles', 'readFile']
model: Claude Opus 4.6 (copilot)
permission_level: WorkspaceWrite
registry_ref: agents/agent_registry.json
handoffs:
  - label: Add API Endpoint
    agent: api-developer
    prompt: "Create a FastAPI endpoint for the backend function implemented above."
    send: false
  - label: Review Changes
    agent: reviewer
    prompt: "Review the Python backend changes made above."
    send: false
  - label: Verify IS 456
    agent: structural-engineer
    prompt: "Verify the IS 456 compliance of the implementation above."
    send: false
  - label: Back to Planning
    agent: orchestrator
    prompt: "Backend work is complete. Plan the next steps."
    send: false
---

# Backend Developer Agent

> **Config precedence:** Agent-specific (.agent.md) > file-type (.instructions.md) > global (copilot-instructions.md). See [config-precedence.md](../../docs/architecture/config-precedence.md).

You are a Python backend specialist for **structural_engineering_lib** — an IS 456:2000 RC beam design library.

> Architecture, git rules, and session workflow are in global instructions — not repeated here.
> For fast context: `bash scripts/agent_brief.sh --agent backend`

## CRITICAL Warnings

| Warning | Detail |
|---------|--------|
| ⚠️ `api.py` is a STUB | Real code is in `services/api.py` — editing the stub wastes time |
| ⚠️ Params are `b_mm`, `fck` | NOT `width`, `grade` — run `./run.sh find --api <func>` to check |
| ⚠️ Modules moved | `adapters.py` → `services/adapters.py`, `geometry_3d.py` → `visualization/geometry_3d.py` |
| ⚠️ Always `.venv/bin/python` | Never bare `python` — wrong env, missing deps |

## Units Rule (non-negotiable)

- Inputs: mm, N/mm², kN, kNm
- Internal: mm, N, N·mm
- Outputs: mm, N/mm², kN, kNm
- Convert at boundaries only — no hidden conversions

## Key Entry Points

| Module | Functions |
|--------|-----------|
| `services/api.py` | 36 public + 7 private — `design_beam_is456()`, `detail_beam_is456()`, `optimize_beam_cost()` |
| `services/adapters.py` | `GenericCSVAdapter`, `ETABSAdapter`, `SAFEAdapter` |
| `visualization/geometry_3d.py` | `beam_to_3d_geometry()` |
| `codes/is456/` | `flexure.py`, `shear.py`, `detailing.py`, `torsion.py`, `serviceability.py`, `compliance.py`, `load_analysis.py`, `materials.py` |
| `codes/is456/column/` | `axial.py`, `uniaxial.py`, `biaxial.py`, `slenderness.py`, `helical.py`, `long_column.py`, `detailing.py` |
| `codes/is456/footing/` | `flexure.py`, `one_way_shear.py`, `punching_shear.py`, `bearing.py` |
| `codes/is13920/` | `beam.py` — IS 13920 ductile detailing |

## Before Coding

```bash
# Check what exists
grep "^def " Python/structural_lib/services/api.py | head -20
# Get exact param names
.venv/bin/python scripts/discover_api_signatures.py <function_name>
# Validate imports
.venv/bin/python scripts/validate_imports.py --scope structural_lib
```

## After Work: Hand off to @reviewer with files changed, layer modified, tests run, how to verify.

## Testing

```bash
.venv/bin/pytest Python/tests/ -v           # Full suite (85% branch coverage required)
.venv/bin/pytest Python/tests/ -k "test_flexure"  # Specific tests
```

## Skills: Use `/api-discovery` for param lookup, `/is456-verification` for compliance tests, `/development-rules` for Python core rules (PY-1 through PY-8, U-1 through U-7).

## Development Rules Quick Reference

Before writing any Python code in `structural_lib/`, review these critical rules from `/development-rules`:

| Rule | Description |
|------|-------------|
| U-1 | Never swallow exceptions silently — log or re-raise |
| U-2 | No `except Exception:` without specific handling |
| U-7 | No import-time side effects (warnings, I/O) |
| PY-1 | Explicit units: `b_mm`, `d_mm`, `fck_nmm2`, `Mu_knm` |
| PY-5 | Return dataclasses, not dicts (with `.to_dict()`) |
| PY-6 | Lazy imports for non-core modules |
| PY-8 | Deprecation warnings gated behind function call, not module load |

## Rules

- **Verify edits persisted:** After making file edits, ALWAYS verify changes persisted with `git diff` or `git status --short`. Phantom edits (agent reports success but changes don't persist in workspace) have been observed. NEVER assume an edit succeeded without verification. If `git status` shows no changes after you edited files, your edits did NOT take effect — retry or report.
- **Update `__init__.py` exports:** When adding a new type, class, or function to any module (especially `services/api.py`), always check and update the relevant `__init__.py` `__all__` list in the SAME commit. CostProfile was added to `api.py` but missed in `__init__.py`, causing 503 ImportError at runtime. Reference: development-rules U-3.
- **CLI smoke tests:** Every `__main__.py` CLI path MUST have at least one smoke test that verifies the CLI entry point can be invoked without crashing. Dead CLI code paths (like `python -m structural_lib smart`) should be caught before release. When creating new CLI subcommands, add a matching `test_cli_<subcommand>_smoke` test.

## ⚠ DO NOT Over-Explore

**Act on what you know — don't rediscover the project structure every time.**

See [python-core.instructions.md](../instructions/python-core.instructions.md) for full rules.
