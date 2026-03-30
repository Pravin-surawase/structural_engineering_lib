# AGENTS.md — structural_engineering_lib

> Cross-agent instructions for all AI coding assistants (Copilot, Claude, Cursor, Windsurf, etc.)
> For Claude-specific details: see [CLAUDE.md](CLAUDE.md)
> For Copilot-specific details: see [.github/copilot-instructions.md](.github/copilot-instructions.md)

## What This Is

Open-source IS 456 RC beam design library. Full stack:
- **Python core** (`Python/structural_lib/`) — Pure math, IS 456:2000 code
- **FastAPI backend** (`fastapi_app/`) — REST + WebSocket API (38 endpoints, 12 routers)
- **React 19 frontend** (`react_app/`) — R3F 3D visualization + Tailwind

## Git — THE ONE RULE

```bash
./scripts/ai_commit.sh "type: message"    # ALWAYS use this. NEVER manual git.
```
New flags: `--preview`, `--undo`, `--signoff`, `--status`, `--branch TASK-XXX "desc"`, `--finish`, `--pr-check`.

Full PR lifecycle:
```bash
./scripts/ai_commit.sh --status               # Check state first
./scripts/ai_commit.sh --branch TASK-XXX "d"  # Create task branch + PR
./scripts/ai_commit.sh "type: message"        # Commit on task branch
./scripts/ai_commit.sh --finish "description" # CI poll + merge + cleanup
```

Format: `feat|fix|docs|refactor|test|chore|ci(scope): description`

**PR Enforcement:** Run `./run.sh pr status` before committing. If it says "PR required", create a PR with `./run.sh pr create`. NEVER use `--force` to bypass the PR check — this has caused 10+ hours of wasted rework.

**FORBIDDEN commands (all agents):**
```
NEVER: gh pr merge --admin            ← bypasses required CI checks
NEVER: gh issue close (without user approval) ← destructive, ask first
NEVER: git push origin --delete (without user approval) ← use .venv/bin/python scripts/cleanup_stale_branches.py --dry-run
NEVER: GIT_HOOKS_BYPASS=1             ← bypasses all safety hooks
NEVER: --no-verify / --force          ← breaks CI, causes rework
```

Destructive GitHub operations (closing issues, deleting branches, merging PRs) require **explicit user confirmation** before execution.

## Architecture (4 layers — STRICT)

```
Core types   → Python/structural_lib/core/           # Base classes, types (no IS 456 math)
IS 456 Code  → Python/structural_lib/codes/is456/    # Pure math, NO I/O, explicit units
Services     → Python/structural_lib/services/        # Orchestration: api.py, adapters.py
UI/IO        → react_app/, fastapi_app/
```

**Import rule:** Core ← IS 456 ← Services ← UI. Never import upward.
**Units rule:** Always explicit — mm, N/mm², kN, kNm. No hidden conversions.
**Stub warning:** `Python/structural_lib/api.py` is a backward-compat stub. Real code → `services/api.py`.

## Search Before Coding

```bash
ls react_app/src/hooks/                                         # Existing React hooks
grep -r "@router" fastapi_app/routers/ | head -30               # Existing API routes
grep "^def " Python/structural_lib/services/api.py | head -20   # Public API (23 functions)
.venv/bin/python scripts/discover_api_signatures.py <func>      # Exact param names (b_mm not width)
.venv/bin/python scripts/find_automation.py "task"              # Find existing scripts (83 mapped)
```

## Essential Commands (`./run.sh` — preferred entry point)

```bash
./run.sh session start              # Begin work (verify env, read priorities)
./run.sh commit "type: message"     # Safe commit + push (THE ONE RULE)
./run.sh check --quick              # Fast validation (<30s, 8 checks)
./run.sh check                      # Full validation (28 checks, parallel)
./run.sh test                       # Run pytest suite
./run.sh pr create TASK-XXX "desc"  # Start a PR
./run.sh pr finish                  # Ship the PR
./run.sh find "topic"               # Find the right script
./run.sh find --api func_name       # Get exact API param names
./run.sh audit                      # Full readiness audit
./run.sh generate indexes           # Regenerate folder indexes
./run.sh health                     # Project health scan (0-100 score)
./run.sh health --fix               # Auto-fix fixable issues
./run.sh feedback log --agent X     # Log agent feedback (session end)
./run.sh feedback summary           # Feedback trends & recurring issues
./run.sh evolve                     # Self-evolution cycle (dry-run)
./run.sh evolve --fix               # Apply fixes + commit
./run.sh evolve --review weekly     # Weekly auto-maintenance
./run.sh dev                        # Launch full dev stack (FastAPI + React)
./run.sh dev --docker               # Launch with Docker (needs Colima)
./run.sh dev --kill-only            # Kill all dev services
./run.sh release preflight 0.X.Y   # Pre-release validation
./run.sh release run 0.X.Y         # Bump version + release flow
```

Direct scripts (when run.sh doesn't cover it):
```bash
.venv/bin/python scripts/agent_context.py <name> # Agent startup context (all 14 agents)
.venv/bin/python scripts/agent_context.py --list # List available agents
.venv/bin/python scripts/safe_file_move.py a b   # Move files (preserves 870+ links)
colima start --cpu 4 --memory 4                  # Start Docker runtime (Colima, not Docker Desktop)
docker compose up --build                        # Full stack at :8000/docs
cd react_app && npm run build                    # React build check
```

> **Docker:** This project uses **Colima** (not Docker Desktop) as the Docker runtime on Mac. Always run `colima start` before `docker compose`. If `docker ps` gives "permission denied", Colima isn't running. See [agent-bootstrap.md](docs/getting-started/agent-bootstrap.md) §5 for details.

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

## Session Workflow (MANDATORY)

```bash
# START: Read priorities, verify environment
docs/planning/next-session-brief.md             # What to work on
docs/TASKS.md                                   # Task board
./run.sh session start                          # Environment check

# END: Commit, log, handoff (do NOT skip)
./run.sh commit "type: message"                 # Commit work
./run.sh feedback log --agent <name>             # Log stale docs, issues found
./run.sh session summary                        # Auto-log to SESSION_LOG.md
./run.sh session sync                           # Fix stale doc numbers
# Update: docs/planning/next-session-brief.md + docs/TASKS.md
./run.sh commit "docs: session end"             # Commit doc updates
```

## Key Patterns — Do NOT Reinvent

| Task | Use This | Not This |
|------|----------|----------|
| CSV import | `useCSVFileImport` → API → `GenericCSVAdapter` | Manual CSV parsing |
| 3D geometry | `useBeamGeometry` → API → `geometry_3d` | Manual calculation |
| File move | `scripts/safe_file_move.py` | `mv` or manual rename |
| File delete | `scripts/safe_file_delete.py` | `rm` |
| API params | `scripts/discover_api_signatures.py` | Guessing names |

## Context Tips

- Read `index.json` / `index.md` in folders FIRST — machine-readable summaries
- Large files (read selectively): SESSION_LOG.md (400KB), adapters.py (71KB), CHANGELOG.md (52KB)
- Always use `.venv/bin/python`, never bare `python`

## VS Code Copilot Agents & Skills

### 14 Custom Agents (`.github/agents/`)

| Agent | Role | Tools |
|-------|------|-------|
| `orchestrator` | Planning, delegation | read-only + subagents |
| `frontend` | React 19, R3F, Tailwind | full edit |
| `backend` | Python structural_lib, IS 456 | full edit |
| `structural-math` | IS 456 pure math modules, core types, new elements | full edit |
| `api-developer` | FastAPI routers, endpoints | full edit |
| `ui-designer` | Visual design (design-only) | read-only |
| `structural-engineer` | IS 456 compliance | read + terminal |
| `reviewer` | Code review, testing | read + terminal |
| `tester` | Test creation, coverage, benchmarks | full edit |
| `doc-master` | Docs, archives, session logs | full edit |
| `ops` | Git, CI/CD, Docker | full edit |
| `governance` | Project health, maintenance, metrics | full edit |
| `security` | Security auditing, OWASP, dependency scanning | read + terminal |
| `library-expert` | Library domain expert, IS 456 knowledge, professional standards | read + terminal + web |

### 8 Agent Skills (`.github/skills/`)

| Skill | Slash Command | Purpose |
|-------|--------------|---------|
| `session-management` | `/session-management` | Session start/end automation |
| `safe-file-ops` | `/safe-file-ops` | File move/delete preserving 870+ links |
| `api-discovery` | `/api-discovery` | API function signature lookup |
| `is456-verification` | `/is456-verification` | IS 456 test runner by category |
| `new-structural-element` | `/new-structural-element` | New element workflow (column, slab, footing) |
| `react-validation` | `/react-validation` | React build, lint, type-check, tests |
| `architecture-check` | `/architecture-check` | 4-layer architecture & duplication validation |
| `function-quality-pipeline` | `/function-quality-pipeline` | Mandatory 9-step quality pipeline for every new IS 456 function |

### 15 Prompt Files (`.github/prompts/`)

| Prompt | Purpose |
|--------|--------|
| `new-feature` | New feature workflow |
| `bug-fix` | Bug fix workflow |
| `code-review` | Review checklist |
| `add-api-endpoint` | FastAPI endpoint workflow |
| `add-is456-clause` | IS 456 clause implementation workflow |
| `add-structural-element` | New structural element (column, slab, footing) workflow |
| `function-quality-gate` | IS 456 function quality gate (9-step pipeline) |
| `fix-test-failure` | Test failure diagnosis & fix |
| `performance-optimization` | Profile, optimize, benchmark |
| `session-start` | Session start checklist |
| `session-end` | Session end (mandatory) |
| `file-move` | Safe file migration |
| `is456-verify` | IS 456 formula verification |
| `context-recovery` | Resume after context overflow |
| `master-workflow` | Master workflow orchestration |

### Handoff Chains

- **New feature:** orchestrator → backend → api-developer → frontend → reviewer → tester → doc-master → ops
- **IS 456 change:** orchestrator → structural-engineer → backend → api-developer → reviewer → tester → doc-master → ops
- **New structural element:** orchestrator → structural-engineer (research) → structural-math (types + math) → tester → backend → api-developer → frontend → reviewer → doc-master → ops
- **Bug fix:** orchestrator → backend/frontend → tester → reviewer → doc-master → ops
- **Test failure:** orchestrator → tester → backend/frontend → reviewer → doc-master → ops
- **Session end:** any agent → doc-master → ops
- **Maintenance:** orchestrator → governance → doc-master → ops
- **Security review:** orchestrator → security → backend/frontend/api-developer → reviewer → doc-master → ops
- **Library guidance:** orchestrator → library-expert → structural-engineer → backend → tester → doc-master → ops
