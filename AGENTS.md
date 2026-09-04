# AGENTS.md — structural_engineering_lib

> Cross-agent instructions for all AI coding assistants (Copilot, Claude, Cursor, Windsurf, etc.)
> For Claude-specific details: see [CLAUDE.md](CLAUDE.md)
> For Copilot-specific details: see [.github/copilot-instructions.md](.github/copilot-instructions.md)

## What This Is

Open-source IS 456 RC beam design library. Full stack:
- **Python core** (`Python/structural_lib/`) — Pure math, IS 456:2000 code
- **FastAPI backend** (`fastapi_app/`) — 93 OpenAPI HTTP operations across 28 router modules, plus a WebSocket route
- **React 19 frontend** (`react_app/`) — R3F 3D visualization + Tailwind

The separate Excel-DNA XLL planning/learning track starts at
[docs/planning/xll-product/README.md](docs/planning/xll-product/README.md).
Read its original architecture and narrower Windows packet before interpreting
its P0–P6 phases; it does not replace the library's six-phase beam programme.

## Owner Decision — Required IS Code Content and Distribution (2026-08-10/11)

- The owner authorizes direct implementation of any IS code content needed for
  an approved feature scope, including formulas, normalized tables, limits,
  figure-derived values, lookup, and interpolation. This includes, but is not
  limited to, slab Tables 12, 13, 26, and 27. Do not avoid required engineering
  logic and do not ask for this implementation permission again.
- Preserve source/table/case provenance in runtime results and tests. Do not copy
  protected clause prose, page images, or unrelated standard content into the
  repository.
- On 2026-08-11 the owner confirmed that source/licensing permission has been
  obtained for public distribution of normalized IS code data within approved
  feature scopes. The gate is passed and must not be reported as pending or
  requested again unless the owner explicitly revokes or changes the decision.
  The canonical machine-readable record is
  `docs/verification/is456-public-distribution-permission.json`.
- This standing permission does not authorize a tag, package publication, or
  GitHub Release. Each release still requires the repository's per-release
  owner authorization and software/evidence gates.
- This source-use decision does not expand feature scope. Flat slabs, for
  example, remain a separately approved extension.

## Token-Efficiency Policy (MANDATORY)

The canonical policy is [docs/guidelines/ai-token-efficiency.md](docs/guidelines/ai-token-efficiency.md); project efficiency defaults are enforced by [`.codex/config.toml`](.codex/config.toml).

- Keep one parent task active. An explicit model or reasoning selection by the user controls. When the user explicitly delegates model choice for a task, the orchestrator may choose suitable available parent and subagent profiles in proportion to task risk; repository defaults remain advisory. If the user asks for a recommendation, prefer Luna for clear repeatable work, Terra for normal implementation, and Sol only after explicit selection, case-specific approval, or delegated model-choice authority.
- Keep Fast mode off unless the user explicitly prioritizes speed over usage.
- Default to no subagents. Use at most two concurrent subagents, only for independent bounded work that materially benefits from delegation.
- Never pass full parent history to a subagent. Send a concise packet with the objective, exact files, constraints, question, commands, and expected output.
- The orchestrator must add non-goals, likely pitfalls, measurable acceptance criteria, narrow tests, and a return format to each packet, then independently inspect and verify the result before acceptance.
- Named handoff chains below are quality roles, not mandatory agent processes. The parent normally performs implementation, testing, documentation, and operations passes itself.
- Start one exact task with `./run.sh session begin --task-id <task> --agent <role>`;
  it records timing before the compact brief and environment check. Then use
  targeted `rg` and `./run.sh context show <area>` only when the brief cannot
  answer a concrete question; do not load full agent files or large logs by default.
- Use implementation-first, batched verification for each agreed bounded packet.
  Complete the scoped code, tests, documentation, and other intended writes
  before the routine verification sequence. While implementing, run only a
  narrow reproducer, test, or diagnostic that is needed to guide or debug the
  current change; do not rerun quick, full, or unchanged suites after each
  edit. After content freezes, run the affected focused checks together and
  publish one batched PR for the required hosted checks. Ordinary commits run
  only the three mutation-safety hooks; broad local validation is explicit and
  risk-driven, not a mandatory pre-publication duplicate. If an outcome-changing
  repair alters the frozen candidate, rerun only its affected focused evidence.
- A milestone branch may contain several sequential internal implementation
  units when they share one accepted authority and do not cross an installed-
  application, mutation-authorization, or external-artifact gate. Internal
  units get only their affected focused tests and any required independent
  benchmark while work is in progress; they do not each trigger broad local
  gates, a push, a PR, or hosted CI. After all intended units are integrated
  and content freezes, run their union of focused/benchmark evidence, push the
  commits together once, and use one required hosted PR cycle for the milestone.
  Run the broad
  Python suite and `./run.sh check` (currently 32 checks) only at the plan's
  named cumulative gate. Run any broad gate earlier only when an outcome-
  changing failure or repository-wide surface makes it necessary; never bypass
  required checks on a published milestone candidate.
- Route changed paths by their maintained callers and outcome owners. A shared
  folder name alone must not select unrelated product domains; unknown or
  unclassified impact still fails closed to every domain.
- Use `/status` and Settings → Usage for Codex usage. Run `./run.sh efficiency
  check` for repository-side policy validation, and record the required
  non-overlapping timing/candidate/retry counters with a closeout
  `./run.sh session usage` checkpoint.
- Run `./run.sh model "task"` only when the user asks for a recommendation,
  has not selected a model, or has delegated model choice. The picker is
  advisory: Luna-first for clear repeatable work, Terra for normal or high-risk
  implementation, and Sol only after explicit selection, case-specific
  approval, or delegated model-choice authority.

## Surgical Work and Essential-Only Review (MANDATORY)

- Keep work surgical, evidence-driven, and complete within the agreed scope. Inspect enough of the main process to find confirmed defects, then finish the scoped work to a good standard without adjacent improvements.
- Always trace a confirmed defect to its root cause and fix that cause. Do not stop at a workaround, suppress the symptom, or apply a superficial patch; verify that the main-process outcome is corrected.
- For every review finding, ask: **Would fixing this change the outcome of the main process?** If not, ignore it. If a non-essential concern needs preservation, file a follow-up bead/task only when necessary; do not expand the current scope.
- Review only essential main-process behavior. Do not report issues about comments, edge cases, test-coverage or falsification gaps, generic hardening, or adjacent improvements. Do not add tests during review. Reject security or concurrency observations that are merely hardening and do not change the main-process outcome.

## Root-Cause and Session-Issue Record (MANDATORY)

- Each agent records material issues in the newest task-owned
  `docs/SESSION_LOG.md` entry. Material means outcome-changing, command-blocking,
  stale-contract, or likely-to-repeat.
- Each entry needs `### Issues encountered`, `### Root causes and resolutions`,
  and `### Rework and recurrence`. Record symptom/impact, confirmed root cause
  (or `unconfirmed`), solution, and proof. When recurrence exists, each row
  references one `RR-NNN`, `occurrences=N`, and `minutes=unknown|N|N-N`; update
  the count/time and short solution once in
  `docs/verification/rework-recurrence-index.json`. Reuse IDs for the same cause
  and create one only for a distinct pattern; otherwise write `- None encountered.`
- Exclude secrets, transient noise, speculative hardening, and unrelated
  failures. Trace the path; an error message alone does not prove root cause.
- `session begin` shows compact recurrence controls. Subagents receive relevant
  controls and return issue/root-cause/evidence; the parent writes one
  deduplicated entry. `session end` fails if a required section or index mapping
  is absent or stale.

## Git and GitHub — Codex Native

Codex owns the normal branch, stage, commit, push, pull-request, and check-status
workflow through its native local-Git and connected GitHub capabilities. Do not
recreate that lifecycle in repository scripts. The canonical process is
[docs/git-automation/git-workflow-single-source.md](docs/git-automation/git-workflow-single-source.md).

- Inspect the branch, upstream, worktree, diff, and current PR before mutation.
- Verify the actual command working directory and repository remote; a saved
  app project folder can differ from an existing task's working directory.
  Follow the multi-device checks in the canonical Git workflow before writes.
- Use `./scripts/python_runtime.sh scripts/git_state.py --json` for current-lane
  evidence and add `--worktrees` for bounded sibling inspection. This is the
  sole read-only Git-state authority; `NOT_CHECKED` remote freshness must not be
  represented as current remote proof.
- Use a `codex/<task-slug>` branch when a new branch is needed.
- Stage only intended paths; preserve unrelated staged, unstaged, untracked, and
  stashed work.
- Before publishing or merging a side packet, inspect every task-owned
  unmerged candidate worktree and compare its base/head plus changed paths. If
  the side packet would advance `main` ahead of an active candidate or overlaps
  shared/generated paths, integrate the predecessor first or explicitly
  replan/rebind the candidate. A clean isolated worktree is not sufficient
  evidence that merge ordering is safe.
- Use `feat|fix|docs|refactor|test|chore|ci(scope): description` commits.
- Push without rewriting history and create/update the PR through connected
  GitHub. Never bypass required checks.
- When Git is conflicted, detached, behind, or diverged, inspect first and stop
  before reset, clean, checkout, stash/drop, rebase, or force push.

**FORBIDDEN commands (all agents):**
```
NEVER: gh pr merge --admin            ← bypasses required CI checks
NEVER: gh pr merge <N> --squash (with failing CI) ← fix failures first, then merge
NEVER: gh issue close (without user approval) ← destructive, ask first
NEVER: git push origin --delete (without user approval) ← inspect with ./scripts/python_runtime.sh scripts/classify_branch_disposition.py; deletion remains separate
NEVER: --no-verify / --force          ← breaks CI, causes rework
NEVER: git rebase --skip              ← silently drops conflicting commits
NEVER: git push --force-with-lease     ← rewrites shared history
```

Codex may mark an in-scope PR ready and merge it without additional user
confirmation when the reviewed head commit is unchanged, required checks pass,
and there are no conflicts or unresolved blockers. Closing issues or pull
requests and deleting branches still require **explicit user confirmation**.

**Permission enforcement:** Agent permissions are now programmatically enforced via `tool_permissions.py`. Each agent has a `permission_level` (ReadOnly, WorkspaceWrite, DangerFullAccess) defined in `agents/agent_registry.json`.

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

### Agent Infrastructure

- **Agent Registry:** `agents/agent_registry.json` — 16 agents with permissions, skills, keywords
- **Control Registry:** `scripts/control-plane.json` — canonical operations, commands, aliases, permissions, and compatibility projection
- **Tool Registry:** `scripts/tool_registry.py` — unified search across agents, skills, scripts
- **Prompt Router:** `scripts/prompt_router.py` — NLP-based task → agent routing
- **Permission Enforcement:** `scripts/tool_permissions.py` — programmatic access control
- **Session Persistence:** `scripts/session_store.py` — JSON session state in logs/sessions/
- **Pipeline Resume:** `scripts/pipeline_state.py` — resumable 8-step task pipeline
- **Routing controls:** `scripts/prompt_router.py` and `scripts/tool_permissions.py` — canonical routing and permission enforcement
- **Parity Dashboard:** `scripts/parity_dashboard.py` — declared Indian-code capability plus endpoint/test/hook coverage
- **Skill Tiers:** Core (task-eligible), Specialist (role-based), Experimental (explicit)

## Search Before Coding

```bash
ls react_app/src/hooks/                                         # Existing React hooks
grep -r "@router" fastapi_app/routers/ | head -30               # Existing API routes
./run.sh find --api <func>                                   # Public API exact signature (68 functions)
./scripts/python_runtime.sh scripts/discover_api_signatures.py <func>      # Exact param names (b_mm not width)
./scripts/python_runtime.sh scripts/find_automation.py "task"              # Find an active registered operation
./run.sh control validate                                                   # Validate registry, permissions, targets, and projection
```

## Essential Commands (`./run.sh` — preferred entry point)

```bash
./run.sh session begin --task-id <task> --agent <role> # Canonical task start
./run.sh check --quick              # Fast validation (<30s, 10 checks)
./run.sh check                      # Full validation (32 checks, parallel)
./run.sh test                       # Run Python package pytest suite
./run.sh test --fastapi             # Run complete FastAPI test suite
./run.sh test --react               # Run complete React test suite on pinned Node
./run.sh test --all                 # Run Python + FastAPI + React tests
./run.sh frontend check             # React lint + tests + production build
./run.sh frontend runtime           # Show selected .nvmrc Node/npm runtime
# Git/GitHub lifecycle is handled directly by Codex, not run.sh.
./run.sh find "topic"               # Find the right script
./run.sh find --api func_name       # Get exact API param names
./run.sh audit                      # Full readiness audit
./run.sh context validate           # Validate canonical context and index retirement
./run.sh context summary <area>     # Summarize live worktree files on demand
./run.sh verification plan          # Show whole-candidate validation domains
./run.sh health                     # Project health scan (0-100 score)
./run.sh health --fix               # Auto-fix fixable issues
./run.sh feedback log --agent X     # Log concrete feedback when found
./run.sh feedback summary           # Feedback trends & recurring issues
./run.sh evolve                     # Self-evolution cycle (dry-run)
./run.sh evolve --fix               # Apply fixes; Codex reviews and commits separately
./run.sh evolve --review weekly     # Weekly report-only review
./run.sh dev                        # Launch full dev stack (FastAPI + React)
./run.sh dev --docker               # Launch with Docker (needs Colima)
./run.sh dev --kill-only            # Kill all dev services
./run.sh release preflight 0.X.Y   # Pre-release validation
./run.sh release preflight --docker # Run preflight in Docker (2GB memory limit)
./run.sh release run 0.X.Y         # Bump version + release flow
./run.sh route "task description"   # Route task to best agent (NLP-based)
./run.sh tools [--list|--find|--agent] # Unified tool/script registry
./run.sh parity                     # Indian-code capability and cross-layer parity dashboard
./run.sh pipeline status TASK-XXX   # Check pipeline step for a task
./run.sh session compact            # Archive old SESSION_LOG entries (<50KB)
./run.sh efficiency check           # Validate low-token project controls
./run.sh session usage --summary    # Model/reasoning/agent checkpoints
./run.sh session trust              # Check session trust state
```

Direct scripts (when run.sh doesn't cover it):
```bash
./scripts/python_runtime.sh scripts/agent_context.py <name> # Agent startup context (all 16 agents)
./scripts/python_runtime.sh scripts/agent_context.py --list # List available agents
./scripts/python_runtime.sh scripts/safe_file_move.py a b   # Move files (preserves 870+ links)
colima start --cpu 4 --memory 4                  # Start Docker runtime (Colima, not Docker Desktop)
docker compose up --build                        # Full stack at :8000/docs
./run.sh frontend build                          # React build on pinned Node
```

> **Docker:** This project uses **Colima** (not Docker Desktop) as the Docker runtime on Mac. Always run `colima start` before `docker compose`. If `docker ps` gives "permission denied", Colima isn't running. See [agent-bootstrap.md](docs/getting-started/agent-bootstrap.md) §5 for details.

## IMPORTANT: Terminal Path Rules

**All commands assume cwd = workspace root.** Terminal cwd persists between calls — if a previous command did `cd react_app`, the next command is STILL in `react_app/`.

```
WRONG: cd Python && python -m pytest tests/ -v          ← cwd and interpreter are implicit
RIGHT: ./scripts/python_runtime.sh -m pytest Python/tests/ -v           ← run from workspace root
RIGHT: ./scripts/python_runtime.sh scripts/check_links.py     ← scripts are at workspace root

WRONG: npm run build                               ← only works if already in react_app/
RIGHT: cd react_app && npm run build               ← explicit cd first
```

**Key paths (all relative to workspace root):**
- `./scripts/python_runtime.sh -m pytest` — worktree-bound pytest launcher
- `./scripts/python_runtime.sh` — worktree-bound Python launcher; the selected
  `.venv` may live in the primary checkout
- `Python/tests/` — Python test directory
- `react_app/` — React app directory
- `scripts/` — utility scripts

### run.sh Fallback Chain
If `./run.sh` produces no output or fails, try these in order:
1. `bash run.sh <command>` — explicit bash invocation
2. Direct validation or implementation script
3. The underlying CLI command for non-GitHub project operations

See `.github/instructions/terminal-rules.instructions.md` for the full fallback table.

### MANDATORY: Document Terminal Issues
When you encounter terminal problems (commands failing, wrong directory, scripts not found), include in your handoff:
`⚠️ TERMINAL ISSUE: [what happened] → [what worked instead]`
This feeds the improvement loop — recurring issues get fixed in agent instructions.

## Session Workflow (MANDATORY)

```bash
# START: task-bound timer + bounded orientation + environment check
./run.sh session begin --task-id <task> --agent <role>

# END: update task/handoff only when state changed, then use Codex Git/GitHub
# Run affected focused diagnostics; comprehensive assurance belongs to the PR.
# Codex stages intended paths and creates the immutable candidate commit.
./run.sh session end --agent <role>              # Final read-only validation
# Codex pushes and creates/updates the PR.
```

**Closeout freeze:** Finish every owned session/task/handoff/evidence update and
the pre-commit Git handoff receipt. Before freezing repository-facing evidence
identities, run `./run.sh check --candidate-integrity`; if it writes, review,
rebind only affected repository identities, and rerun clean. Preserve separately
declared raw installed-artifact identities. Folder indexes are retired;
`./run.sh context validate` is read-only and requires no final generated write.
Create the immutable candidate commit, run final read-only `session end`, then
push. After push or PR creation, keep hosted-check and merge facts in GitHub and
the external handoff; never append them to the same candidate and restart CI. A
material post-push defect requires a repair candidate.

`session end --fix` is preparation mode, not final validation. It must run
before candidate freeze when explicitly needed. Review all resulting writes,
create the candidate commit, and rerun `session end` without `--fix`. A
preparation run that otherwise passes exits `2`, never `0`, so automation
cannot mistake it for the final verdict. Expected dirty preparation content
does not by itself change that `2`; unknown Git state, an operation/conflict,
missing receipt, or another failed preparation check still exits `1`.

Log feedback only when a concrete stale instruction or missing control was found. `session summary`, `session sync`, and `session end` are read-only by default; `--write` or `--fix` must be intentional. Agent evolution is scheduled governance work, not a mandatory session-end mutation.

## Key Patterns — Do NOT Reinvent

| Task | Use This | Not This |
|------|----------|----------|
| CSV import | `useCSVFileImport` → API → `GenericCSVAdapter` | Manual CSV parsing |
| 3D geometry | `useBeamGeometry` → API → `geometry_3d` | Manual calculation |
| File move | `scripts/safe_file_move.py` | `mv` or manual rename |
| File delete | `scripts/safe_file_delete.py` | `rm` |
| API params | `scripts/discover_api_signatures.py` | Guessing names |

## Context Tips

- Use `./run.sh context show <area>` for authoritative routing and
  `./run.sh context summary <area-or-folder>` for a bounded live inventory.
- Use targeted `rg` for exact symbols and callers; generic folder indexes are retired.
- Large files (read selectively): SESSION_LOG.md (400KB), adapters.py (71KB), CHANGELOG.md (52KB)
- Always use `./scripts/python_runtime.sh`, never bare `python`. In linked
  worktrees, verify the current source binding with
  `./scripts/python_runtime.sh --diagnose`.

## Instruction Surface Ownership

Avoid copying agent, skill, prompt, or handoff inventories into entry files.
Those catalogs drift as roles evolve. Use these maintained owners instead:

- `AGENTS.md` — cross-agent safety, architecture, Git, session, and execution
  contract.
- `agents/agent_registry.json` — agent roles, permissions, skills, and routing.
- `.github/skills/skill_tiers.json` and `.github/skills/*/SKILL.md` — available
  workflows and their exact procedures.
- `.github/prompts/*.prompt.md` — invocation templates, not independent policy.
- `scripts/control-plane.json` — command, alias, permission, and operation truth.
- `.github/instructions/*.instructions.md` — maintained path-scoped rules.
- `.claude/rules/*.md` — exact Claude projections of the maintained scoped-rule
  bodies.

Platform entry files may add only platform-specific loading guidance. They may
not weaken this contract, invent a different session or Git workflow, or carry
their own executable role catalogs. Validate the composition with:

```bash
./scripts/python_runtime.sh scripts/check_instruction_drift.py
./scripts/python_runtime.sh scripts/config_precedence.py audit
```
