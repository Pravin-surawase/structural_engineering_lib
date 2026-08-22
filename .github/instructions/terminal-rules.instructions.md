---
applyTo: "**"
---

# Terminal Rules (ALL Agents)

## Project Root
Absolute path: `/Users/pravinsurawase/VS_code_project/structural_engineering_lib`
All commands below assume cwd = this directory unless stated otherwise.

## Python Runtime and venv Location
The approved `.venv/` may be in this checkout or the primary worktree. Always
use the launcher so imports bind to the invoking worktree.
```
CORRECT: ./scripts/python_runtime.sh ...
CORRECT: ./scripts/python_runtime.sh -m pytest Python/tests/ -v
CHECK:   ./scripts/python_runtime.sh --diagnose
WRONG:   cd Python && python -m pytest tests/          ← cwd and interpreter are implicit
WRONG:   python scripts/...                        ← wrong env, missing deps
```

## cwd Persists Between Commands
If you run `cd react_app`, your NEXT command is still in `react_app/`.
Always use full paths from root, or prefix with explicit `cd`:
```
SAFE:    ./scripts/python_runtime.sh -m pytest Python/tests/ -v          ← works from root
SAFE:    ./run.sh frontend build                     ← root-stable, pinned Node
DANGER:  npm run build                              ← cwd and Node are implicit
```

## Shell-Safe Literal Arguments (zsh)

Quote patterns and package extras before the shell can interpret them. Prefer
an exact path discovered with `rg --files` over a speculative glob.

```bash
# Globs passed as data: quote the whole pattern.
rg "design_beam" --glob '*.py' Python/

# Literal backticks: single quotes prevent command substitution.
rg -n 'the `local_state_receipt_hash` field' docs/

# Wheel/package extras: quote the complete requirement.
./scripts/python_runtime.sh -m pip install 'structural-lib-is456[pmm]'
```

An unmatched unquoted glob is a command error in zsh; it is not evidence that
the intended path is absent. Discover the path, then rerun the inspection with
the exact path or a quoted pattern.

## run.sh Fallback Chain
If `./run.sh <cmd>` produces no output or fails:
1. Try: `bash run.sh <cmd>`
2. Try: the direct script (see table below)
3. Try: the underlying CLI command directly

| run.sh Command | Direct Script Fallback | CLI Fallback |
|----------------|----------------------|--------------|
| `./run.sh test` | `./scripts/python_runtime.sh -m pytest Python/tests/ -v` | Python suite only |
| `./run.sh test --fastapi` | `./scripts/python_runtime.sh -m pytest fastapi_app/tests/` | — |
| `./run.sh test --react` | `./scripts/python_runtime.sh scripts/node_runtime.py -- npm --prefix react_app test` | — |
| `./run.sh frontend check` | `./scripts/python_runtime.sh scripts/node_runtime.py -- npm --prefix react_app test` | Run lint and build through the same wrapper |
| `./run.sh check --quick` | `./scripts/python_runtime.sh scripts/check_all.py --quick` | — |
| `./run.sh find --api func` | `./scripts/python_runtime.sh scripts/discover_api_signatures.py func` | — |
| `./run.sh session summary` | `./scripts/python_runtime.sh scripts/session.py summary` | Add `--write` only intentionally |
| `./run.sh generate indexes` | `./scripts/python_runtime.sh scripts/generate_enhanced_index.py --all` | — |
| `./run.sh dev` | `bash scripts/launch_stack.sh` | `colima start && docker compose up --build` |
| `./run.sh dev --docker` | `bash scripts/launch_stack.sh --docker` | `colima start && docker compose up --build` |
| `./run.sh dev --kill-only` | `bash scripts/launch_stack.sh --kill-only` | Stop only listeners started for this task; never kill arbitrary port owners |

## Common Commands Quick Reference

### Python
```bash
./scripts/python_runtime.sh -m pytest Python/tests/ -v                    # All tests
./scripts/python_runtime.sh -m pytest Python/tests/ -v -k "test_shear"    # Specific tests
./scripts/python_runtime.sh scripts/discover_api_signatures.py design_beam_is456  # API params
./scripts/python_runtime.sh scripts/validate_imports.py --scope structural_lib    # Check imports
```

### React (pinned `.nvmrc` runtime)
```bash
./run.sh frontend runtime                             # Selected Node/npm
./run.sh frontend test                                # Tests
./run.sh frontend build                               # Build check
./run.sh frontend check                               # Lint + tests + build
./run.sh frontend dev                                 # Dev server :5173
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

### Git and GitHub — Codex Native
```bash
git status --short                                    # Inspect worktree
git branch --show-current                             # Inspect branch
git diff --check                                      # Check patch hygiene
git log --oneline -10                                 # Inspect recent history
```

Codex inspects the state and diff, stages only intended paths, creates a conventional commit, pushes without rewriting history, and creates or updates the PR through the connected GitHub integration. Repository scripts must not automate that lifecycle. See `docs/git-automation/git-workflow-single-source.md`.

**FORBIDDEN (causes merge conflicts, rework, and lost changes):**
```
NEVER: rm file.md                                     ← use ./scripts/python_runtime.sh scripts/safe_file_delete.py
NEVER: mv old.md new.md                               ← use ./scripts/python_runtime.sh scripts/safe_file_move.py
NEVER: --no-verify or --force                         ← has caused 10+ hours of rework
NEVER: git rebase --skip                              ← can silently drop commits
NEVER: cat > file << 'EOF' ... EOF   ← heredoc fails in agent terminals; use editFiles tool
```

Routine Git writes are performed intentionally by Codex after inspecting scope.
Codex may merge an in-scope PR after verifying its reviewed head, required
checks, conflicts, and blockers. Other destructive or history-rewriting actions
require explicit user approval.

**FORBIDDEN GitHub operations (all agents):**
```
NEVER: gh pr merge --admin            ← bypasses required CI checks
NEVER: gh issue close (without user approval) ← destructive, ask first
NEVER: git push origin --delete (without user approval) ← inspect with ./scripts/python_runtime.sh scripts/classify_branch_disposition.py; deletion remains separate
```

Closing issues or pull requests and deleting branches require **explicit user
confirmation**. In-scope PR merges do not require additional confirmation once
the reviewed head and required checks are verified.

## File Creation (IMPORTANT)

**NEVER use heredoc syntax in terminals.** It fails because the terminal tool doesn't handle multi-line input properly.

```bash
# ❌ WRONG — heredoc delimiter gets "command not found":
cat > file.py << 'EOF'
content
EOF

# ❌ WRONG — multiline printf fails with escaping issues:
printf "line1\nline2\n" > file.py

# ✅ RIGHT — use the editFiles tool (available to most agents):
# Simply use the VS Code file editing tool to create/write files.
# This is the ONLY reliable method for creating files with content.

# ✅ ACCEPTABLE — create empty placeholder, then fill with editFiles tool:
touch file.py
# Then use editFiles tool to add content
```

**Rule:** If your agent has `editFiles` in its tool list, ALWAYS use it for file creation. Never attempt to write file content through terminal commands.

**Agents with editFiles:** backend, structural-math, api-developer, tester, frontend, doc-master, governance, agent-evolver, ops
**Agents WITHOUT editFiles:** orchestrator, ui-designer, structural-engineer, reviewer, library-expert, security — delegate file creation to @backend or @doc-master

## MANDATORY: Document Terminal Issues

When you encounter ANY of these, document them in your handoff message:
- A command that produces no output when it should
- A command you had to try 3+ times with variations
- A path that doesn't exist where documentation says it should
- A permission or execution error on a script
- Getting stuck in a wrong directory

Format: `⚠️ TERMINAL ISSUE: [what happened] → [what worked instead]`

This helps the orchestrator fix the root cause and update instructions.
