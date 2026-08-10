# Copilot Instructions — structural_engineering_lib

Open-source IS 456 RC beam design library. V3 stack: React 19 + R3F + Tailwind → FastAPI → Python structural_lib.
Current focus: See [TASKS.md](../docs/TASKS.md) for active work and priorities.

## Surgical Work and Essential-Only Review (MANDATORY)

- Keep work surgical, evidence-driven, and complete within the agreed scope. Inspect enough of the main process to find confirmed defects, then finish the scoped work to a good standard without adjacent improvements.
- Always trace a confirmed defect to its root cause and fix that cause. Do not stop at a workaround, suppress the symptom, or apply a superficial patch; verify that the main-process outcome is corrected.
- For every review finding, ask: **Would fixing this change the outcome of the main process?** If not, ignore it. If a non-essential concern needs preservation, file a follow-up bead/task only when necessary; do not expand the current scope.
- Review only essential main-process behavior. Do not report issues about comments, edge cases, test-coverage or falsification gaps, generic hardening, or adjacent improvements. Do not add tests during review. Reject security or concurrency observations that are merely hardening and do not change the main-process outcome.

## Root-Cause and Session-Issue Record (MANDATORY)

- Record every material task issue in the newest task-owned
  `docs/SESSION_LOG.md` entry under `### Issues encountered`, and pair it with a
  `### Root causes and resolutions` record containing the confirmed cause,
  implemented fix, and verification evidence. Use `- None encountered.` when
  truthful; never infer a cause from an error message alone.
- Material means the issue changed the main-process outcome, blocked a required
  command, exposed a stale instruction/contract, or would cause repeated work.
  Exclude secrets, transient noise, speculative hardening, and unrelated
  non-impacting failures.
- Subagents return symptom, impact, cause or `unconfirmed`, solution, and proof;
  the parent maintains the single deduplicated versioned record. Session closeout
  fails when the newest entry omits either required section.

## IMPORTANT: Git and GitHub — Codex Native

Codex owns the Git/GitHub lifecycle directly. Follow [AGENTS.md](../AGENTS.md) and the canonical [Codex-native workflow](../docs/git-automation/git-workflow-single-source.md): inspect state, stage only intended files, use a conventional commit, push without rewriting history, and create or update the PR through the connected GitHub integration.

Do not add repository wrappers that commit, push, create PRs, merge PRs, or recover Git state. Issue closure, branch deletion, release, and history rewriting remain explicit user-confirmation actions. Codex may merge an in-scope PR once its reviewed head and required checks are verified.

**FORBIDDEN commands (all agents):**
```
NEVER: gh pr merge --admin            ← bypasses required CI checks
NEVER: gh pr merge <N> --squash (with failing CI) ← fix failures first, then merge
NEVER: gh issue close (without user approval) ← destructive, ask first
NEVER: git push origin --delete (without user approval) ← use ./scripts/python_runtime.sh scripts/cleanup_stale_branches.py
NEVER: GIT_HOOKS_BYPASS=1             ← bypasses all safety hooks
NEVER: --no-verify / --force          ← breaks CI, causes rework
```

Codex may mark an in-scope PR ready and merge it without additional user
confirmation when the reviewed head commit is unchanged, required checks pass,
and there are no conflicts or unresolved blockers. Closing issues or pull
requests and deleting branches still require **explicit user confirmation**.

**Permission enforcement:** Agent permissions are now programmatically enforced via `tool_permissions.py`. Each agent has a `permission_level` (ReadOnly, WorkspaceWrite, DangerFullAccess) defined in `agents/agent_registry.json`.

## Architecture (4 layers — STRICT, never mix)

- **Core types** (`Python/structural_lib/core/`) — Base classes, types, constants (no IS 456 math)
- **IS 456 Code** (`Python/structural_lib/codes/is456/`) — Pure math, NO I/O, explicit units (mm, N/mm², kN, kNm)
- **Services** (`Python/structural_lib/services/`) — Orchestration: `api.py`, `adapters.py`, `beam_pipeline.py`
- **UI/IO** (`react_app/`, `fastapi_app/`) — Interfaces

> `Python/structural_lib/api.py` is a **backward-compat stub** — real code is in `services/api.py`.

Core CANNOT import from Services or UI.

### Agent Infrastructure

- **Agent Registry:** `agents/agent_registry.json` — 16 agents with permissions, skills, keywords
- **Tool Registry:** `scripts/tool_registry.py` — unified search across agents, skills, scripts
- **Prompt Router:** `scripts/prompt_router.py` — NLP-based task → agent routing
- **Permission Enforcement:** `scripts/tool_permissions.py` — programmatic access control
- **Session Persistence:** `scripts/session_store.py` — JSON session state in logs/sessions/
- **Pipeline Resume:** `scripts/pipeline_state.py` — resumable 8-step task pipeline
- **Hooks Framework:** `scripts/hooks/` — non-Git execution hooks such as `pre_route`
- **Parity Dashboard:** `scripts/parity_dashboard.py` — IS 456 clause/endpoint/test coverage
- **Skill Tiers:** Core (always), Specialist (role-based), Experimental (explicit)

## IMPORTANT: Search before coding

Agents keep duplicating code. Check what exists BEFORE writing new code:
```bash
ls react_app/src/hooks/                                         # React hooks (CSV, geometry, export, insights)
grep -r "@router" fastapi_app/routers/ | head -30               # FastAPI routes (17 routers)
./run.sh find --api <func>                                   # Public API exact signature (68 functions)
.venv/bin/python scripts/discover_api_signatures.py <func>      # Exact param names
```

Key patterns: CSV → `useCSVFileImport` | 3D geometry → `useBeamGeometry` | adapters → `GenericCSVAdapter` | export → `useExport`.

> `adapters.py` → `services/adapters.py` | `geometry_3d.py` → `visualization/geometry_3d.py`

## Commands (`./run.sh` — preferred entry point)

```bash
./run.sh session start              # Begin work (verify env, read priorities)
./run.sh check                      # Validate everything (29 checks, parallel)
./run.sh check --quick              # Fast validation (<30s)
./run.sh session end                # Validate closeout (read-only by default)
./run.sh find "topic"               # Find the right script
./run.sh find --api func_name       # Get API signatures
./run.sh test                       # Run test suite
./run.sh audit                      # Full readiness audit
./run.sh generate indexes           # Regenerate folder indexes
./run.sh health                     # Project health scan (0-100 score)
./run.sh health --fix               # Auto-fix fixable issues
./run.sh feedback log --agent X     # Log concrete feedback when found
./run.sh feedback summary           # Feedback trends & recurring issues
./run.sh evolve                     # Self-evolution cycle (dry-run)
./run.sh evolve --fix               # Apply fixes for Codex review
./run.sh evolve --review weekly     # Weekly report-only review
./run.sh dev                        # Launch full dev stack (FastAPI + React)
./run.sh dev --docker               # Launch with Docker (needs Colima)
./run.sh dev --kill-only            # Kill all dev services
./run.sh release preflight 0.X.Y   # Pre-release validation
./run.sh release preflight --docker # Run preflight in Docker (2GB memory limit)
./run.sh release run 0.X.Y         # Bump version + release flow
./run.sh route "task description"   # Route task to best agent (NLP-based)
./run.sh tools [--list|--find|--agent] # Unified tool/script registry
./run.sh parity                     # IS 456 clause/endpoint/test coverage dashboard
./run.sh pipeline status TASK-XXX   # Check pipeline step for a task
./run.sh session compact            # Archive old SESSION_LOG entries (<50KB)
./run.sh session costs --summary    # Legacy Git-activity proxy (not tokens/cost)
./run.sh session usage --summary    # Model/reasoning/agent checkpoints
./run.sh session trust              # Check session trust state
```

### Direct scripts (when run.sh doesn't cover it)

```bash
.venv/bin/python scripts/safe_file_move.py a b  # Move files (preserves 870+ links)
.venv/bin/python scripts/safe_file_delete.py f  # Delete files safely
colima start --cpu 4 --memory 4                 # Start Docker runtime (Colima, not Docker Desktop)
docker compose up --build                       # FastAPI at :8000/docs
cd react_app && npm run dev                     # React at :5173
```

> **Docker:** Uses **Colima** on Mac (not Docker Desktop). Run `colima start` before any `docker` command. "Permission denied" on `docker ps` = Colima not running.

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
2. Direct read-only script for the same validation or discovery task
3. Direct CLI validation command

See `.github/instructions/terminal-rules.instructions.md` for the full fallback table.

### MANDATORY: Document Terminal Issues
When you encounter terminal problems (commands failing, wrong directory, scripts not found), include in your handoff:
`⚠️ TERMINAL ISSUE: [what happened] → [what worked instead]`
This feeds the improvement loop — recurring issues get fixed in agent instructions.

## Session Closeout

```bash
./run.sh check --quick
# Codex inspects the diff, stages intended paths, commits, pushes, and manages the PR.
./run.sh session end --agent <role> # Validate; no hidden writes
```

`session summary`, `session sync`, and `session end` are read-only by default. Use `--write` or `--fix` only when that mutation is explicitly required.

## IMPORTANT: Session Logging (MANDATORY)

Every coding session uses the bounded workflow below.

### Session Start
1. Run `./run.sh session brief --agent <role>` for bounded priorities.
2. Run `./run.sh session start` once to verify the environment.

### During Session
- Use targeted checks while editing and one intentional Codex-managed task commit.
- Track what you changed, what you decided, and what's unfinished

### Session End (REQUIRED — do NOT skip)
1. Update `docs/TASKS.md` and `docs/planning/next-session-brief.md` only when their state changed or a durable handoff is needed.
2. Run `./run.sh check --quick` once before commit.
3. Have Codex inspect the final diff, commit and push the intended paths, and create or update the PR.
4. Run `./run.sh session end --agent <role>` to validate the clean handoff.
5. Log feedback only when a concrete stale or missing control was found.

### Why This Matters
- **next-session-brief.md** carries task-specific continuation state.
- **TASKS.md** tracks real project-state changes.
- Global logs, metrics, indexes, and evolution reviews are updated only by tasks that own them.

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
- Read indexes FIRST before diving into individual files
- After moving files, regenerate indexes: `.venv/bin/python scripts/generate_enhanced_index.py <folder>`

Always use `.venv/bin/python`, never bare `python`. Verify outdated info (AI models, versions) online with `fetch_webpage`.

## Context Size (413 Error Prevention)

- Read targeted file sections (use offset/limit) instead of full large files
- Use `grep_search` to find relevant lines before reading entire files
- Large files to read selectively: SESSION_LOG.md (400KB), CHANGELOG.md (52KB), services/adapters.py (71KB)

## Key References

- **Full bootstrap:** [agent-bootstrap.md](../docs/getting-started/agent-bootstrap.md)
- **Copilot agents guide:** [copilot-agents-usage-guide.md](../docs/guides/copilot-agents-usage-guide.md)
- **Current tasks:** [TASKS.md](../docs/TASKS.md)
- **Last session:** [next-session-brief.md](../docs/planning/next-session-brief.md)
- **API reference:** [api.md](../docs/reference/api.md)
- **Command cheat sheet:** [agent-quick-reference.md](../docs/agents/guides/agent-quick-reference.md)

## VS Code Copilot Agents & Skills

### 16 Custom Agents (`.github/agents/`)

| Agent | Role | Tools |
|-------|------|-------|
| `orchestrator` | Planning, delegation | read-only + subagents |
| `frontend` | React 19, R3F, Tailwind | full edit |
| `backend` | Python structural_lib, IS 456 | full edit |
| `structural-math` | IS 456 pure math modules, core types, new elements | full edit |
| `api-developer` | FastAPI routers, endpoints | full edit |
| `ui-designer` | Visual design (design-only) | read-only |
| `agent-evolver` | Meta-agent: performance scoring, drift detection, instruction evolution | read + terminal |
| `structural-engineer` | IS 456 compliance | read + terminal |
| `reviewer` | Code review, testing | read + terminal |
| `tester` | Test creation, coverage, benchmarks | full edit |
| `doc-master` | Docs, archives, session logs | full edit |
| `ops` | Git, CI/CD, Docker | full edit |
| `governance` | Project health, maintenance, metrics | full edit |
| `security` | Security auditing, OWASP, dependency scanning | read + terminal |
| `library-expert` | Library domain expert, IS 456 knowledge, professional standards | read + terminal + web |
| `innovator` | Research & innovation — discovers missing capabilities, proposes novel approaches | read + edit + web |

### 14 Agent Skills (`.github/skills/`)

| Skill | Slash Command | Purpose |
|-------|--------------|--------|
| `session-management` | `/session-management` | Session start/end automation |
| `safe-file-ops` | `/safe-file-ops` | File move/delete preserving 870+ links |
| `api-discovery` | `/api-discovery` | API function signature lookup |
| `is456-verification` | `/is456-verification` | IS 456 test runner by category |
| `new-structural-element` | `/new-structural-element` | New element workflow (column, slab, footing) |
| `react-validation` | `/react-validation` | React build, lint, type-check, tests |
| `architecture-check` | `/architecture-check` | 4-layer architecture & duplication validation |
| `function-quality-pipeline` | `/function-quality-pipeline` | Mandatory 9-step quality pipeline for every new IS 456 function |
| `innovation-research` | `/innovation-research` | Guided innovation research cycle |
| `agent-evolution` | `/agent-evolution` | Evidence-gated scoring, drift detection, and scheduled instruction evolution |
| `development-rules` | `/development-rules` | 46 hard-learned rules by domain (Python, FastAPI, React, testing, security) |
| `quality-gate` | `/quality-gate` | 3-level pre-merge quality checks (commit, PR, release) |
| `release-preflight` | `/release-preflight` | 5-phase pre-release validation (packaging, UAT, security, API/doc, CI) |
| `user-acceptance-test` | `/user-acceptance-test` | End-user perspective testing (pip install + all workflows) |

### 16 Prompt Files (`.github/prompts/`)

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
| `session-end` | Compact closeout validation |
| `file-move` | Safe file migration |
| `is456-verify` | IS 456 formula verification |
| `context-recovery` | Resume after context overflow |
| `master-workflow` | Master workflow orchestration |
| `innovation-research` | Innovation research cycle workflow |

### Handoff Chains

These labels describe quality concerns, not mandatory agent invocations. The
active parent normally performs them; delegate only an independent bounded
packet that materially benefits from another agent.

- **New feature:** orchestrator → backend → api-developer → frontend → reviewer → tester → doc-master → ops
- **IS 456 change:** orchestrator → structural-engineer → backend → api-developer → reviewer → tester → doc-master → ops
- **New structural element:** orchestrator → structural-engineer (research) → structural-math (types + math) → tester → backend → api-developer → frontend → reviewer → doc-master → ops
- **Bug fix:** orchestrator → backend/frontend → tester → reviewer → doc-master → ops
- **Test failure:** orchestrator → tester → backend/frontend → reviewer → doc-master → ops
- **Session closeout:** active parent validates; use doc-master or ops only when the task owns that work
- **Maintenance:** orchestrator → governance → doc-master → ops
- **Security review:** orchestrator → security → backend/frontend/api-developer → reviewer → doc-master → ops
- **Library guidance:** orchestrator → library-expert → structural-engineer → backend → tester → doc-master → ops
- **Agent evolution:** orchestrator → agent-evolver → governance → doc-master → ops
- **Innovation research:** orchestrator → innovator → structural-engineer (gate) → structural-math → tester → reviewer → doc-master → ops
- **Release:** orchestrator → tester (UAT) → reviewer (quality gate) → ops (preflight + release) → tester (post-release verify) → doc-master (CHANGELOG + docs) → agent-evolver (metrics) → Codex Git/GitHub closeout

## Context Recovery (When LLM Loses Context)

If the conversation gets too long, start a new chat and paste:
```
Read these to recover context:
1. docs/planning/next-session-brief.md
2. docs/TASKS.md (first 60 lines)
3. .github/copilot-instructions.md
4. git log --oneline -20
Then continue from where I left off.
```

Domain-specific rules (React, Python core) are in `.github/instructions/` and load automatically per file type.
