---
applyTo: "**"
---

# Terminal Rules (ALL Agents)

## Project Root
Absolute path: `/Users/pravinsurawase/VS_code_project/structural_engineering_lib`
All commands below assume cwd = this directory unless stated otherwise.

## venv Location
`.venv/` is at the PROJECT ROOT — NOT inside `Python/` subdirectory.
```
CORRECT: .venv/bin/python ...
CORRECT: .venv/bin/pytest Python/tests/ -v
WRONG:   cd Python && .venv/bin/pytest tests/     ← .venv not in Python/
WRONG:   python scripts/...                        ← wrong env, missing deps
```

## cwd Persists Between Commands
If you run `cd react_app`, your NEXT command is still in `react_app/`.
Always use full paths from root, or prefix with explicit `cd`:
```
SAFE:    .venv/bin/pytest Python/tests/ -v          ← works from root
SAFE:    cd react_app && npm run build              ← explicit cd
DANGER:  npm run build                              ← only works if already in react_app/
```

## run.sh Fallback Chain
If `./run.sh <cmd>` produces no output or fails:
1. Try: `bash run.sh <cmd>`
2. Try: the direct script (see table below)
3. Try: the underlying CLI command directly

| run.sh Command | Direct Script Fallback | CLI Fallback |
|----------------|----------------------|--------------|
| `./run.sh commit "msg"` | `./scripts/ai_commit.sh "msg"` | Flags: `--preview`, `--undo`, `--signoff` |
| `./run.sh pr status` | `./scripts/should_use_pr.sh` | `gh pr list --head $(git branch --show-current)` |
| `./run.sh pr create ID "desc"` | `./scripts/create_task_pr.sh ID "desc"` | `gh pr create --title "..." --base main` |
| `./run.sh test` | `.venv/bin/pytest Python/tests/ -v` | — |
| `./run.sh check --quick` | `.venv/bin/python scripts/check_all.py --quick` | — |
| `./run.sh find --api func` | `.venv/bin/python scripts/discover_api_signatures.py func` | — |
| `./run.sh session summary` | `.venv/bin/python scripts/session_summary.py` | — |
| `./run.sh generate indexes` | `.venv/bin/python scripts/generate_enhanced_index.py --all` | — |
| `./run.sh dev` | `bash scripts/launch_stack.sh` | `colima start && docker compose up --build` |
| `./run.sh dev --docker` | `bash scripts/launch_stack.sh --docker` | `colima start && docker compose up --build` |
| `./run.sh dev --kill-only` | `bash scripts/launch_stack.sh --kill-only` | `lsof -ti :8000 \| xargs kill -9` |

## Common Commands Quick Reference

### Python
```bash
.venv/bin/pytest Python/tests/ -v                    # All tests
.venv/bin/pytest Python/tests/ -v -k "test_shear"    # Specific tests
.venv/bin/python scripts/discover_api_signatures.py design_beam_is456  # API params
.venv/bin/python scripts/validate_imports.py --scope structural_lib    # Check imports
```

### React
```bash
cd react_app && npm run build                         # Build check
cd react_app && npm run dev                           # Dev server :5173
cd react_app && npx vitest run                        # Tests
```

### Full-Stack Dev Launcher (PREFERRED)
```bash
./run.sh dev                                          # Local: FastAPI + React (default)
./run.sh dev --docker                                 # Docker mode (needs Colima running)
./run.sh dev --docker-dev                             # Docker dev mode (hot reload)
./run.sh dev --kill-only                              # Kill all dev services
./run.sh dev --no-react                               # FastAPI only
./run.sh dev --no-fastapi                             # React only
./run.sh dev --open                                   # Launch + open browser automatically
```
Fallback: `bash scripts/launch_stack.sh [--local|--docker|--docker-dev] [options]`

### FastAPI / Docker (manual)
```bash
colima start --cpu 4 --memory 4                       # Start Docker runtime FIRST
docker compose up --build                            # Production at :8000/docs
docker compose -f docker-compose.dev.yml up           # Dev with hot reload
```

### Git — NEVER Manual (ALL agents)
```bash
./scripts/ai_commit.sh "type(scope): message"         # Commit + push (THE ONE RULE)
./scripts/ai_commit.sh "msg" --preview                # Preview changes before committing
./scripts/ai_commit.sh --undo                         # Undo last unpushed commit
./scripts/ai_commit.sh "msg" --signoff                # DCO sign-off
./scripts/ai_commit.sh --status                        # Check project state
./scripts/ai_commit.sh --branch TASK-XXX "desc"        # Create task branch
./scripts/ai_commit.sh --finish "description"          # CI poll + merge PR
./scripts/ai_commit.sh --pr-check                     # Check if PR required
git status --short                                    # Check state (read-only OK)
git branch --show-current                             # Current branch (read-only OK)
git log --oneline -10                                 # Recent history (read-only OK)
```

**FORBIDDEN (causes merge conflicts, rework, and lost changes):**
```
NEVER: git add / git commit / git push / git pull     ← use ai_commit.sh instead
NEVER: rm file.md                                     ← use .venv/bin/python scripts/safe_file_delete.py
NEVER: mv old.md new.md                               ← use .venv/bin/python scripts/safe_file_move.py
NEVER: git commit --amend                             ← use ./scripts/ai_commit.sh --amend
NEVER: --no-verify or --force                         ← has caused 10+ hours of rework
```

**Read-only git commands are OK:** `git status`, `git log`, `git diff`, `git branch`, `git show`.

**FORBIDDEN GitHub operations (all agents):**
```
NEVER: gh pr merge --admin            ← bypasses required CI checks
NEVER: gh issue close (without user approval) ← destructive, ask first
NEVER: git push origin --delete (without user approval) ← use .venv/bin/python scripts/cleanup_stale_branches.py --dry-run
NEVER: GIT_HOOKS_BYPASS=1             ← bypasses all safety hooks
```

Destructive GitHub operations (closing issues, deleting branches, merging PRs) require **explicit user confirmation** before execution.

## MANDATORY: Document Terminal Issues

When you encounter ANY of these, document them in your handoff message:
- A command that produces no output when it should
- A command you had to try 3+ times with variations
- A path that doesn't exist where documentation says it should
- A permission or execution error on a script
- Getting stuck in a wrong directory

Format: `⚠️ TERMINAL ISSUE: [what happened] → [what worked instead]`

This helps the orchestrator fix the root cause and update instructions.
