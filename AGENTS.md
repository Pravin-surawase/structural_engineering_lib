# AGENTS.md — structural_engineering_lib

> Cross-agent instructions for all AI coding assistants (Copilot, Claude, Cursor, Windsurf, etc.)
> For Claude-specific details: see [CLAUDE.md](CLAUDE.md)
> For Copilot-specific details: see [.github/copilot-instructions.md](.github/copilot-instructions.md)

## What This Is

Open-source IS 456 RC beam design library. Full stack:
- **Python core** (`Python/structural_lib/`) — Pure math, IS 456:2000 code
- **FastAPI backend** (`fastapi_app/`) — REST + WebSocket API (35 endpoints, 12 routers)
- **React 19 frontend** (`react_app/`) — R3F 3D visualization + Tailwind

## Git — THE ONE RULE

```bash
./scripts/ai_commit.sh "type: message"    # ALWAYS use this. NEVER manual git.
```

Format: `feat|fix|docs|refactor|test|chore|ci(scope): description`

**PR Enforcement:** Run `./run.sh pr status` before committing. If it says "PR required", create a PR with `./run.sh pr create`. NEVER use `--force` to bypass the PR check — this has caused 10+ hours of wasted rework.

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
```

Direct scripts (when run.sh doesn't cover it):
```bash
.venv/bin/python scripts/safe_file_move.py a b  # Move files (preserves 870+ links)
colima start --cpu 4 --memory 4                 # Start Docker runtime (Colima, not Docker Desktop)
docker compose up --build                       # Full stack at :8000/docs
cd react_app && npm run build                   # React build check
```

> **Docker:** This project uses **Colima** (not Docker Desktop) as the Docker runtime on Mac. Always run `colima start` before `docker compose`. If `docker ps` gives "permission denied", Colima isn't running. See [agent-bootstrap.md](docs/getting-started/agent-bootstrap.md) §5 for details.

## Session Workflow (MANDATORY)

```bash
# START: Read priorities, verify environment
docs/planning/next-session-brief.md             # What to work on
docs/TASKS.md                                   # Task board
./run.sh session start                          # Environment check

# END: Commit, log, handoff (do NOT skip)
./run.sh commit "type: message"                 # Commit work
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

### 9 Custom Agents (`.github/agents/`)

| Agent | Role | Tools |
|-------|------|-------|
| `orchestrator` | Planning, delegation | read-only + subagents |
| `frontend` | React 19, R3F, Tailwind | full edit |
| `backend` | Python structural_lib, IS 456 | full edit |
| `api-developer` | FastAPI routers, endpoints | full edit |
| `ui-designer` | Visual design (design-only) | read-only |
| `structural-engineer` | IS 456 compliance | read + terminal |
| `reviewer` | Code review, testing | read + terminal |
| `doc-master` | Docs, archives, session logs | full edit |
| `ops` | Git, CI/CD, Docker | full edit |

### 4 Agent Skills (`.github/skills/`)

| Skill | Slash Command | Purpose |
|-------|--------------|---------|
| `session-management` | `/session-management` | Session start/end automation |
| `safe-file-ops` | `/safe-file-ops` | File move/delete preserving 870+ links |
| `api-discovery` | `/api-discovery` | API function signature lookup |
| `is456-verification` | `/is456-verification` | IS 456 test runner by category |

### 9 Prompt Files (`.github/prompts/`)

| Prompt | Purpose |
|--------|--------|
| `new-feature` | New feature workflow |
| `bug-fix` | Bug fix workflow |
| `code-review` | Review checklist |
| `add-api-endpoint` | FastAPI endpoint workflow |
| `session-start` | Session start checklist |
| `session-end` | Session end (mandatory) |
| `file-move` | Safe file migration |
| `is456-verify` | IS 456 formula verification |
| `context-recovery` | Resume after context overflow |

### Handoff Chains

- **New feature:** orchestrator → backend → api-developer → frontend → reviewer → doc-master
- **IS 456 change:** orchestrator → structural-engineer → backend → api-developer → reviewer
- **Session end:** any agent → doc-master → ops
