# CLAUDE.md — structural_engineering_lib

Open-source IS 456 RC beam design library. V3 stack: React 19 + R3F + Tailwind → FastAPI → Python structural_lib.

## IMPORTANT: Git

ALWAYS use `./scripts/ai_commit.sh "type: message"` for commits. NEVER use manual git add/commit/push/pull.

## Architecture (3 layers — never mix)

- **Core** (`Python/structural_lib/codes/is456/`) — Pure math, NO I/O, explicit units (mm, N/mm2, kN, kNm)
- **App** (`api.py`, `beam_pipeline.py`) — Orchestration, no formatting
- **UI/IO** (`react_app/`, `streamlit_app/`, `fastapi_app/`) — External interfaces only

Core CANNOT import from App or UI.

## IMPORTANT: Search before coding

Agents keep duplicating code. Check what exists BEFORE writing new code:

```bash
ls react_app/src/hooks/                                    # React hooks (CSV import, geometry, live design)
grep -r "@router" fastapi_app/routers/ | head -20          # FastAPI endpoints
grep -r "^def " Python/structural_lib/api.py | head -20    # 43 public library functions
.venv/bin/python scripts/discover_api_signatures.py <func> # Get exact param names (b_mm not width)
```

Key patterns: CSV import → `useCSVFileImport` hook, 3D geometry → `useBeamGeometry` hook, adapters → `GenericCSVAdapter`.

## Commands

```bash
./scripts/agent_start.sh --quick                # Session start (6s)
./scripts/ai_commit.sh "type: message"          # Commit (THE ONE RULE)
./scripts/should_use_pr.sh --explain            # PR vs direct commit
docker compose up --build                       # FastAPI at :8000/docs
cd react_app && npm run dev                     # React at :5173
cd Python && .venv/bin/pytest tests/ -v         # Python tests (85% coverage gate)
.venv/bin/python scripts/safe_file_move.py a b  # Move files (preserves 870+ links)
.venv/bin/python scripts/find_automation.py "x" # Find existing automation
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
- **Read indexes FIRST** before diving into individual files
- After moving files, regenerate: `.venv/bin/python scripts/generate_enhanced_index.py <folder>`

Always use `.venv/bin/python`, never bare `python`.

## Key References

- **Full bootstrap:** docs/getting-started/agent-bootstrap.md
- **Current tasks:** docs/TASKS.md
- **Last session:** docs/planning/next-session-brief.md
- **API reference:** docs/reference/api.md

## Context Management

- Use `Grep`/`Glob` to find relevant code before reading full files
- Read targeted sections (`offset`/`limit`) for large files
- Large files to read selectively: SESSION_LOG.md (400KB), CHANGELOG.md (52KB), adapters.py (71KB)
