# AGENTS.md — structural_engineering_lib

> Cross-agent instructions for all AI coding assistants (Copilot, Claude, Cursor, Windsurf, etc.)
> For Claude-specific details: see [CLAUDE.md](CLAUDE.md)
> For Copilot-specific details: see [.github/copilot-instructions.md](.github/copilot-instructions.md)

## What This Is

Open-source IS 456 RC beam design library. Full stack:
- **Python core** (`Python/structural_lib/`) — Pure math, IS 456:2000 code
- **FastAPI backend** (`fastapi_app/`) — REST + WebSocket API (35 endpoints, 12 routers)
- **React 19 frontend** (`react_app/`) — R3F 3D visualization + Tailwind
- **Streamlit app** (`streamlit_app/`) — Legacy interactive UI
- **VBA/Excel** (`VBA/`, `Excel/`) — Spreadsheet implementations

## Git — THE ONE RULE

```bash
./scripts/ai_commit.sh "type: message"    # ALWAYS use this. NEVER manual git.
```

Format: `feat|fix|docs|refactor|test|chore|ci(scope): description`

## Architecture (4 layers — STRICT)

```
Core types   → Python/structural_lib/core/           # Base classes, types (no IS 456 math)
IS 456 Code  → Python/structural_lib/codes/is456/    # Pure math, NO I/O, explicit units
Services     → Python/structural_lib/services/        # Orchestration: api.py, adapters.py
UI/IO        → react_app/, streamlit_app/, fastapi_app/
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

## Essential Commands

```bash
./scripts/agent_start.sh --quick                # Session start (6s)
./scripts/ai_commit.sh "type: message"          # Safe commit + push
./scripts/should_use_pr.sh --explain            # Check if PR required
cd Python && .venv/bin/pytest tests/ -v         # Run tests (85% coverage gate)
cd react_app && npm run build                   # React build check
docker compose up --build                       # Full stack at :8000/docs
```

## Session Workflow (MANDATORY)

```bash
# START: Read priorities, verify environment
docs/planning/next-session-brief.md             # What to work on
docs/TASKS.md                                   # Task board
./scripts/agent_start.sh --quick                # Environment check

# END: Commit, log, handoff (do NOT skip)
./scripts/ai_commit.sh "type: message"          # Commit work
.venv/bin/python scripts/session.py summary --write  # Auto-log to SESSION_LOG.md
.venv/bin/python scripts/session.py sync --fix       # Fix stale doc numbers
# Update: docs/planning/next-session-brief.md + docs/TASKS.md
./scripts/ai_commit.sh "docs: session end"           # Commit doc updates
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
