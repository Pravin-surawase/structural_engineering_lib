# CLAUDE.md — structural_engineering_lib

Open-source IS 456 RC beam design library. V3 stack: React 19 + R3F + Tailwind → FastAPI → Python structural_lib.

## IMPORTANT: Git

ALWAYS use `./scripts/ai_commit.sh "type: message"` for commits. NEVER use manual git add/commit/push/pull.

**PR Rule:** When `./run.sh pr status` says "PR required", you MUST use a PR. NEVER use `--force` to bypass. No exceptions.

**FORBIDDEN commands (all agents):**
```
NEVER: gh pr merge --admin            ← bypasses required CI checks
NEVER: gh issue close (without user approval) ← destructive, ask first
NEVER: git push origin --delete (without user approval) ← use github_maintenance.sh --dry-run
NEVER: GIT_HOOKS_BYPASS=1             ← bypasses all safety hooks
NEVER: --no-verify / --force          ← breaks CI, causes rework
```

Destructive GitHub operations (closing issues, deleting branches, merging PRs) require **explicit user confirmation** before execution.

## Architecture (4 layers — STRICT, never mix)

- **Core types** (`Python/structural_lib/core/`) — Base classes, types, constants (no IS 456 math)
- **IS 456 Code** (`Python/structural_lib/codes/is456/`) — Pure math, NO I/O, explicit units (mm, N/mm²,  kN, kNm)
- **Services** (`Python/structural_lib/services/`) — Orchestration: `api.py`, `adapters.py`, `beam_pipeline.py` (no formatting)
- **UI/IO** (`react_app/`, `fastapi_app/`) — External interfaces only

> `Python/structural_lib/api.py` is a **backward-compat stub** — all real code is in `services/api.py`.
> `adapters.py` → `services/adapters.py` | `geometry_3d.py` → `visualization/geometry_3d.py`

Core CANNOT import from Services or UI. Services CANNOT import from UI.

## IMPORTANT: Search before coding

Agents keep duplicating code. Check what exists BEFORE writing new code:

```bash
ls react_app/src/hooks/                                         # React hooks (CSV, geometry, export, insights)
grep -r "@router" fastapi_app/routers/ | head -30               # FastAPI endpoints (12 routers)
grep "^def " Python/structural_lib/services/api.py | head -20   # 26 public + 6 private helpers
.venv/bin/python scripts/discover_api_signatures.py <func>      # Get exact param names (b_mm not width)
```

Key patterns: CSV import → `useCSVFileImport` | 3D geometry → `useBeamGeometry` | adapters → `GenericCSVAdapter` | export → `useExport`.

## Commands (`./run.sh` — preferred entry point)

```bash
./run.sh session start              # Begin work (verify env, read priorities)
./run.sh commit "type: message"     # Commit safely (THE ONE RULE)
./run.sh dev                        # Launch full development stack (FastAPI + React)
./run.sh check                      # Validate everything (28 checks, parallel)
./run.sh check --quick              # Fast validation (<30s)
./run.sh pr create TASK-XXX "desc"  # Start a PR
./run.sh pr finish                  # Ship the PR
./run.sh session end                # Wrap up (logs, sync, handoff)
./run.sh find "topic"               # Find the right script
./run.sh find --api func_name       # Get API signatures
./run.sh test                       # Run test suite
./run.sh test --ci                  # Full local CI
./run.sh audit                      # Full readiness audit
./run.sh generate indexes           # Regenerate folder indexes
./run.sh health                     # Project health scan (0-100 score)
./run.sh health --fix               # Auto-fix fixable issues
./run.sh info                       # Library metadata, API, elements, architecture
./run.sh info --json                # Machine-readable project metadata
./run.sh feedback log --agent X     # Log agent feedback (session end)
./run.sh feedback summary           # Feedback trends & recurring issues
./run.sh evolve                     # Self-evolution cycle (dry-run)
./run.sh evolve --fix               # Apply fixes + commit
./run.sh evolve --review weekly     # Weekly auto-maintenance
```

### Direct scripts (when run.sh doesn't cover it)

```bash
.venv/bin/python scripts/safe_file_move.py a b  # Move files (preserves 870+ links)
.venv/bin/python scripts/safe_file_delete.py f  # Delete files safely
.venv/bin/python scripts/create_doc.py path     # Create doc with metadata
bash scripts/launch_stack.sh --help              # Launch script usage (flags: --docker, --local, --kill-only, etc.)
colima start --cpu 4 --memory 4                 # Start Docker runtime (Colima, not Docker Desktop)
```

> **Docker note:** This project uses **Colima** (not Docker Desktop) as the Docker runtime on Mac. Start Colima before any `docker` command: `colima start`. If `docker ps` gives "permission denied", Colima isn't running.

## IMPORTANT: Terminal Path Rules

**All commands assume cwd = workspace root.** Terminal cwd persists between calls — if a previous command did `cd react_app`, the next command is STILL in `react_app/`.

```
WRONG: cd Python && .venv/bin/pytest tests/ -v     ← .venv is NOT inside Python/
RIGHT: .venv/bin/pytest Python/tests/ -v           ← run from workspace root
RIGHT: .venv/bin/python scripts/check_links.py     ← scripts are at workspace root

WRONG: npm run build                               ← only works if already in react_app/
RIGHT: cd react_app && npm run build               ← explicit cd first
```

**Key paths (all relative to workspace root):**
- `.venv/bin/pytest` — pytest binary
- `.venv/bin/python` — Python binary
- `Python/tests/` — Python test directory
- `react_app/` — React app directory
- `scripts/` — utility scripts

### run.sh Fallback Chain
If `./run.sh` produces no output or fails, try these in order:
1. `bash run.sh <command>` — explicit bash invocation
2. Direct script (e.g., `./scripts/ai_commit.sh` instead of `./run.sh commit`)
3. Direct CLI command (e.g., `gh pr create` instead of `./run.sh pr create`)

See `.github/instructions/terminal-rules.instructions.md` for the full fallback table.

### MANDATORY: Document Terminal Issues
When you encounter terminal problems (commands failing, wrong directory, scripts not found), include in your handoff:
`⚠️ TERMINAL ISSUE: [what happened] → [what worked instead]`
This feeds the improvement loop — recurring issues get fixed in agent instructions.

## Session End (auto-summary + sync)

```bash
./run.sh session summary            # Auto-generate summary from git log
./run.sh session sync               # Sync stale doc numbers
./run.sh session end                # Run end-of-session checks
./run.sh commit "docs: session end" # Commit doc updates
```

Or just scan numbers: `.venv/bin/python scripts/sync_numbers.py --fix`

## IMPORTANT: Session Logging (MANDATORY)

Every AI agent session MUST follow this workflow. Skipping these steps breaks continuity for the next agent/session.

### Session Start
1. Read `docs/planning/next-session-brief.md` to understand current priorities
2. Read `docs/TASKS.md` for active work items
3. Run `./run.sh session start` to verify environment

### During Session
- Commit frequently with descriptive conventional messages via `./run.sh commit`
- Track what you changed, what you decided, and what's unfinished

### Session End (REQUIRED — do NOT skip)
1. Run `./run.sh commit` for any uncommitted work
2. Run `./run.sh feedback log --agent <name>` — log stale docs, missing info, issues found
3. Run `./run.sh session summary` — auto-generates SESSION_LOG entry
4. Run `./run.sh session sync` — fixes stale numbers in docs
4. Append to `docs/WORKLOG.md` — one line per change (date | task | what | commit)
5. Update `docs/planning/next-session-brief.md` — what the NEXT agent should do first
6. Update `docs/TASKS.md` — mark completed items, add new items discovered
7. Run `./run.sh commit "docs: session end"` — commit all doc updates

### Why This Matters
- **WORKLOG.md** is the compact change log — one line per item, prevents rework
- **SESSION_LOG.md** is the project memory — gaps mean lost context
- **next-session-brief.md** is the handoff — without it, the next agent wastes time rediscovering state
- **TASKS.md** tracks priorities — unupdated tasks get repeated or lost
- Empty sessions (no log, no handoff) have caused 10+ hours of wasted rework historically

## Migration & Folder Structure Scripts

```bash
.venv/bin/python scripts/migrate_python_module.py <src> <dst> --dry-run   # Move Python module + update imports
.venv/bin/python scripts/migrate_react_component.py <src> <dst> --dry-run # Move React component + update imports
.venv/bin/python scripts/validate_imports.py --scope structural_lib       # Check for broken imports
.venv/bin/python scripts/check_governance.py --structure                  # Validate folder conventions
.venv/bin/python scripts/generate_enhanced_index.py <folder>              # Generate index.json + index.md
.venv/bin/python scripts/generate_enhanced_index.py --all                 # Regenerate all folder indexes
```

## Folder Indexes (AI Agent Context)

Each key folder has `index.json` + `index.md` for fast context loading:
- `index.json` — Machine-readable: file list, classes, functions, params, descriptions
- `index.md` — Human-readable: tables with descriptions, exports, line counts
- **Read indexes FIRST** before diving into individual files
- After moving files, regenerate: `.venv/bin/python scripts/generate_enhanced_index.py <folder>`

Always use `.venv/bin/python`, never bare `python`.

## Key References

- **Full bootstrap:** docs/getting-started/agent-bootstrap.md
- **Copilot agents guide:** docs/guides/copilot-agents-usage-guide.md
- **Current tasks:** docs/TASKS.md
- **Last session:** docs/planning/next-session-brief.md
- **API reference:** docs/reference/api.md

## Context Recovery (When LLM Loses Context)

If context is lost mid-session, start fresh with:
```
Read these to recover context:
1. docs/planning/next-session-brief.md
2. docs/TASKS.md (first 60 lines)
3. CLAUDE.md
4. git log --oneline -20
Then continue from where I left off.
```

## Context Management

- Use `Grep`/`Glob` to find relevant code before reading full files
- Read targeted sections (`offset`/`limit`) for large files
- Large files to read selectively: SESSION_LOG.md (400KB+), CHANGELOG.md (52KB), services/adapters.py (71KB)

## What Exists — Do NOT Reinvent

React hooks: `useCSVFileImport`, `useCSVTextImport`, `useDualCSVImport`, `useBatchDesign` (useCSVImport.ts) | `useBeamGeometry` | `useLiveDesign`, `useAutoDesign` | `useBuildingGeometry`, `useCrossSectionGeometry` (useGeometryAdvanced.ts) | `useExport` (BBS/DXF/report) | `useInsights`, `useCodeChecks`, `useRebarSuggestions` | `useRebarValidation`, `useRebarApply` | `useDesignWebSocket`

FastAPI routers (12 routers, 38 endpoints): `design`, `detailing`, `analysis`, `geometry`, `imports`, `insights`, `optimization`, `rebar`, `export`, `streaming`, `websocket`, `health`
