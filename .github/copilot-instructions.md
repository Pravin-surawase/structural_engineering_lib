# Copilot Instructions — structural_engineering_lib

Open-source IS 456 RC beam design library. V3 stack: React 19 + R3F + Tailwind → FastAPI → Python structural_lib.
Current focus: See [TASKS.md](../docs/TASKS.md) for active work and priorities.

## IMPORTANT: Git

ALWAYS use `./scripts/ai_commit.sh "type: message"` for commits. NEVER use manual git add/commit/push/pull.
Manual git causes 10-30min conflicts. The script handles staging, hooks, pull, and push.

## Architecture (3 layers — never mix)

- **Core** (`codes/is456/`) — Pure math, NO I/O, explicit units (mm, N/mm2, kN, kNm)
- **App** (`api.py`, `beam_pipeline.py`) — Orchestration
- **UI/IO** (`react_app/`, `streamlit_app/`, `fastapi_app/`) — Interfaces

Core CANNOT import from App or UI.

## IMPORTANT: Search before coding

Agents keep duplicating code. Check what exists BEFORE writing new code:
```bash
ls react_app/src/hooks/                                    # React hooks
grep -r "@router" fastapi_app/routers/ | head -20          # FastAPI routes
grep -r "^def " Python/structural_lib/api.py | head -20    # Library functions
.venv/bin/python scripts/discover_api_signatures.py <func> # Exact param names
```

Key patterns: CSV → `useCSVFileImport`, 3D geometry → `useBeamGeometry`, adapters → `GenericCSVAdapter`.

## Commands

```bash
./scripts/agent_start.sh --quick                # Session start
./scripts/ai_commit.sh "type: message"          # Commit
./scripts/should_use_pr.sh --explain            # PR vs direct
docker compose up --build                       # FastAPI at :8000/docs
cd react_app && npm run dev                     # React at :5173
cd Python && .venv/bin/pytest tests/ -v         # Tests (85% coverage gate)
.venv/bin/python scripts/safe_file_move.py a b  # Safe file move
.venv/bin/python scripts/find_automation.py "x" # Find automation
```

## Migration & Folder Structure Scripts

```bash
.venv/bin/python scripts/migrate_python_module.py <src> <dst> --dry-run   # Move Python module + update imports
.venv/bin/python scripts/migrate_react_component.py <src> <dst> --dry-run # Move React component + update imports
.venv/bin/python scripts/validate_imports.py --scope structural_lib       # Check for broken imports
.venv/bin/python scripts/validate_folder_structure.py                     # Validate folder conventions
.venv/bin/python scripts/generate_enhanced_index.py <folder>              # Generate index.json + index.md
.venv/bin/python scripts/generate_enhanced_index.py --all                 # Regenerate all folder indexes
```

## Folder Indexes (AI Agent Context)

Each key folder has `index.json` + `index.md` for fast context loading:
- `index.json` — Machine-readable: file list, classes, functions, params, descriptions
- `index.md` — Human-readable: tables with descriptions, exports, line counts
- Read indexes FIRST before diving into individual files
- After moving files, regenerate indexes: `.venv/bin/python scripts/generate_enhanced_index.py <folder>`

Always use `.venv/bin/python`, never bare `python`. Verify outdated info (AI models, versions) online with `fetch_webpage`.

## Context Size (413 Error Prevention)

- Read targeted file sections (use offset/limit) instead of full large files
- Use `grep_search` to find relevant lines before reading entire files
- Large files to read selectively: SESSION_LOG.md (400KB), CHANGELOG.md (52KB), adapters.py (71KB)

## Key References

- **Full bootstrap:** [agent-bootstrap.md](../docs/getting-started/agent-bootstrap.md)
- **Current tasks:** [TASKS.md](../docs/TASKS.md)
- **Last session:** [next-session-brief.md](../docs/planning/next-session-brief.md)
- **API reference:** [api.md](../docs/reference/api.md)
- **Command cheat sheet:** [agent-quick-reference.md](../docs/agents/guides/agent-quick-reference.md)

Domain-specific rules (Streamlit, React, VBA, Python core) are in `.github/instructions/` and load automatically per file type.
