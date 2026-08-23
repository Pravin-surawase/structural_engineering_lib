# GitHub Copilot Instructions — structural_engineering_lib

This is the concise global contract for Copilot surfaces that may not load root
`AGENTS.md`. When `AGENTS.md` is also loaded, it is the canonical detailed
cross-agent contract; this file must remain compatible with it. Path-specific
rules under `.github/instructions/` add narrower guidance and may not weaken
these safety boundaries.

## Repository and Architecture

This repository contains an IS 456 RC design stack:

- `Python/structural_lib/core/` — base types; no IS 456 math.
- `Python/structural_lib/codes/is456/` — pure math; no I/O; explicit units.
- `Python/structural_lib/services/` — orchestration and adapters.
- `fastapi_app/` and `react_app/` — transport and UI.

Imports flow Core → IS 456 → Services → UI. Never import upward. Keep units
explicit: mm, N/mm², kN, and kNm. `Python/structural_lib/api.py` is a
compatibility stub; new service code belongs in `services/api.py`.

Within an approved feature scope, normalized IS-code formulas, tables, limits,
lookups, and interpolation are authorized. Preserve provenance, but do not copy
protected clause prose, page images, or unrelated standard content. This does
not authorize a release, package publication, tag, or scope expansion.

## Work Contract

- Inspect the task, branch, upstream, worktree, diff, and current PR before
  mutation. Preserve dirty, detached, foreign, uncertain, and sibling lanes.
- Keep changes surgical and outcome-driven. Trace confirmed failures to their
  root cause; do not expand into unrelated hardening or cleanup.
- Default to one active parent and no subagents. Use at most two only for
  independent bounded work that materially benefits from delegation.
- Finish the agreed code, tests, docs, and evidence before consolidated
  verification. Do not rerun unchanged suites after every edit.
- Record material issues and their confirmed root causes, resolutions, and
  proof in the newest task-owned `docs/SESSION_LOG.md` entry.
- Never delete, archive, reset, clean, stash, rebase, force-push, close an issue
  or PR, or delete a branch merely to make progress. Exact destructive actions
  require the authorization defined in `AGENTS.md`.
- Never bypass hooks or required checks. Releases always require separate owner
  authorization.

## Canonical Commands

Run from the repository root:

```bash
./run.sh session begin --task-id <task> --agent <role>
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
./run.sh context show <area>
./run.sh find --api <function>
./run.sh check --quick
```

Always use `./scripts/python_runtime.sh`; never call a checkout-specific Python
or pytest binary directly. Use `safe_file_move.py` and `safe_file_delete.py`
only within an explicitly approved exact file operation. Git/GitHub lifecycle
is performed directly by Codex after inspection, not recreated in repository
scripts.

## Maintained Owners

- Roles and permissions: `agents/agent_registry.json`
- Skills and workflows: `.github/skills/skill_tiers.json` and
  `.github/skills/*/SKILL.md`
- Invocation templates: `.github/prompts/*.prompt.md`
- Commands and aliases: `scripts/control-plane.json`
- Git lifecycle: `docs/git-automation/git-workflow-single-source.md`
- Current priorities: `docs/TASKS.md`

Do not add copied role, skill, prompt, route, or handoff catalogs here. Validate
instruction changes with:

```bash
./scripts/python_runtime.sh scripts/check_instruction_drift.py
./scripts/python_runtime.sh scripts/config_precedence.py audit
```
