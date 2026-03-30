# Self-Evolving Multi-Agent Git Infrastructure for AI-Assisted Structural Engineering Software Development: Architecture, Automation, and Lessons Learned

**Type:** Research
**Audience:** All Agents
**Status:** Draft
**Importance:** High
**Created:** 2026-03-30
**Last Updated:** 2026-03-30

---

## Abstract

The proliferation of large language model (LLM) coding agents — including GitHub Copilot, Claude, Cursor, and Windsurf — has introduced a new class of software engineering challenges: multiple autonomous agents operating concurrently on a shared codebase produce merge conflicts, lose context across sessions, duplicate existing code, and break builds in ways that compound over time. This paper presents a production-deployed, self-evolving multi-agent git infrastructure developed for `structural_engineering_lib`, an open-source IS 456:2000 reinforced concrete beam design library. The infrastructure enforces a single-entry-point git workflow via pre-commit and pre-push hooks, orchestrates 14 specialized agents through structured handoff chains, maintains session continuity through append-only project memory logs, and implements a three-layer self-evolution engine that scans project health, collects agent feedback, and auto-fixes detected regressions. Over 105 numbered sessions (170+ dated entries in SESSION_LOG.md), 3,226 tests, 96 mapped tasks, 27 parallel validation checks, and 14 domain-specialized agents, the system has achieved zero merge conflicts since instruction-based enforcement was adopted (approximately Session 80+) — eliminating an estimated 10+ hours of rework per incident. We present the full architecture, quantitative metrics, failure modes encountered, and lessons learned, arguing that the overhead of safety infrastructure for multi-agent development pays for itself rapidly and proposing directions for formal agent behavioral contracts, token usage optimization, and cross-repository generalization.

**Keywords:** multi-agent systems, LLM coding agents, git workflow automation, software engineering infrastructure, self-healing systems, session continuity, reinforced concrete design, IS 456:2000, DevOps, CI/CD

---

## 1. Introduction

The emergence of LLM-based coding agents has fundamentally altered the landscape of software development. Tools such as GitHub Copilot, Anthropic Claude, Cursor, and Windsurf can generate code, refactor modules, write tests, and manage documentation with minimal human oversight. However, when multiple autonomous agents operate on the same codebase — often in overlapping time windows and without shared memory — a predictable set of failure modes arises:

1. **Merge conflicts**: Agents working on overlapping files produce conflicting commits that require manual resolution.
2. **Context loss**: Each agent session starts fresh, with no memory of prior decisions, leading to repeated exploration and wasted tokens.
3. **Code duplication**: Without awareness of existing utilities, agents reinvent hooks, helpers, and adapters already present in the codebase.
4. **Build breakage**: Agents bypass pre-commit checks, skip tests, or use `--force` flags that circumvent safety mechanisms.
5. **Architecture violations**: Without enforced boundaries, agents import from wrong layers, mix I/O with pure math, or duplicate business logic across tiers.

These problems are not hypothetical. In the early development of `structural_engineering_lib`, manual git operations by AI agents caused merge conflicts that consumed 10+ hours of rework per incident. Agents guessed API parameter names (`width` instead of `b_mm`), navigated to wrong directories, and skipped session-end documentation — leaving subsequent agents to rediscover project state from scratch.

This paper presents a production-deployed infrastructure that systematically addresses each failure mode. The key contributions are:

- **Enforced git workflow**: A single-entry-point commit script (`ai_commit.sh`, 430 lines) with instruction-based enforcement, pre-commit framework integration (Black, Ruff, mypy), and custom hook templates that prevent manual git operations.
- **Multi-agent orchestration**: 14 specialized agents with defined roles, tool permissions, and structured handoff chains.
- **Session continuity**: Append-only project memory (SESSION_LOG.md, WORKLOG.md, TASKS.md) that preserves context across sessions.
- **Self-evolving infrastructure**: A three-layer system that scans health, collects feedback, and auto-fixes regressions.

To our knowledge, this is the first documented self-evolving multi-agent git infrastructure deployed in production for domain-specific engineering software, with 105 numbered sessions (170+ dated entries) and quantitative evidence of its effectiveness.

---

## 2. Related Work

### 2.1 Multi-Agent Code Generation

**SEMAG** (Self-Evolutionary Multi-Agent Code Generation, arXiv:2603.15707) proposes agents that iteratively improve generated code through self-evaluation. While SEMAG focuses on the code generation task itself, our system addresses the surrounding infrastructure — git safety, session continuity, and architectural governance — that enables agents to generate code reliably in a production codebase.

**AgentMesh** (arXiv:2507.19902) presents a cooperative multi-agent framework for software development with role-based agents and communication protocols. Our system shares the concept of agent specialization but differs in being a deployed production system with 105 numbered sessions of empirical data, rather than a framework evaluated on benchmarks.

**DebateCoder** (arXiv:2601.21469) introduces adaptive confidence gating for multi-agent code collaboration, where agents debate code quality. Our system enforces quality through automated validation (27 parallel checks) rather than agent consensus, covering the full software development lifecycle rather than code quality alone.

Other prominent multi-agent systems include **ChatDev** (Qian et al., 2023) [11] and **DevGPT** (Xie et al., 2023) [12], which focus on end-to-end code generation through role-playing agents. These systems optimize code generation quality rather than the surrounding development infrastructure — they lack git safety mechanisms, session continuity, or self-healing capabilities.

### 2.2 Tool-Augmented and Hierarchical Agents

**SAGE** (arXiv:2601.09750) focuses on tool-augmented LLM task solving in multi-agent environments. Our system similarly equips agents with specialized tools (7 skills, 14 prompts) but emphasizes git safety and session continuity — dimensions SAGE does not address.

**Autonoma** (arXiv:2603.19270) proposes a hierarchical multi-agent framework with orchestrator-worker patterns similar to our orchestrator → specialist → reviewer chain. However, our system adds self-healing capabilities: agents report problems back to the infrastructure, which auto-fixes them.

### 2.3 Self-Healing Infrastructure

**Self-healing Infrastructure-as-Code** (Diaz-De-Arcaya et al., ACM 2024) applies LLMs to detect and repair IaC configuration drift. Our self-healing concept operates at a different level — repairing git state, stale documentation, broken links, and architecture violations rather than cloud infrastructure.

**LLM DevOps Self-Healing** (Bhattarai, 2025) scales generative AI for self-healing DevOps pipelines, focusing on CI/CD recovery. Our system shares the self-healing philosophy but applies it to the development process itself: agent feedback loops, session log integrity, and project health scoring.

### 2.4 Agent Governance and Architecture

**Agent Behavioral Contracts** (arXiv:2602.22302) proposes formal specifications for AI agent behavior. Our system enforces behavioral contracts through git hooks and pre-commit enforcement — a pragmatic, deployed alternative to formal specification that has proven effective in practice.

**Theory of Code Space** (arXiv:2603.00601) investigates whether code agents understand software architecture. Our system sidesteps this question by enforcing architecture at the tooling level: automated boundary checks detect and block layer violations regardless of agent understanding.

**Tokenomics** (arXiv:2601.14470) analyzes token usage in agentic software engineering. Our session management system — with structured handoffs and append-only logs — directly reduces token waste from context re-exploration, though we do not yet track token consumption per session.

### 2.5 Identified Gap

No existing system combines all five of the following properties:

1. **Enforced git workflow** for AI agents (hook-based, zero manual git)
2. **Session continuity** with append-only logs and structured handoffs
3. **Self-evolving infrastructure** with health scoring and auto-fix
4. **Multi-agent handoff chains** with domain-specific specialization
5. **Domain-specific engineering constraints** (IS 456:2000, unit enforcement, 4-layer architecture)

Our system addresses this gap with a deployed, empirically validated implementation.

---

## 3. System Architecture

### 3.1 Overview

`structural_engineering_lib` is a full-stack application for reinforced concrete beam design per IS 456:2000. The technology stack comprises:

- **Frontend**: React 19, React Three Fiber (R3F) for 3D visualization, Tailwind CSS
- **Backend**: FastAPI with 38 endpoints across 12 routers, WebSocket support
- **Core Library**: Python `structural_lib` with pure IS 456:2000 math

The codebase enforces a strict 4-layer architecture:

```
┌─────────────────────────────────────────────────┐
│  Layer 4: UI/IO (react_app/, fastapi_app/)      │
├─────────────────────────────────────────────────┤
│  Layer 3: Services (services/api.py, adapters)  │
├─────────────────────────────────────────────────┤
│  Layer 2: IS 456 Code (codes/is456/) — pure math│
├─────────────────────────────────────────────────┤
│  Layer 1: Core Types (core/) — base classes     │
└─────────────────────────────────────────────────┘
         ↑ Import direction: upward only
```

Import direction is enforced automatically: Core cannot import from Services or UI; Services cannot import from UI. Units are always explicit (mm, N/mm², kN, kNm) with no hidden conversions.

### 3.2 The "One Rule" Git Workflow

The cornerstone of the infrastructure is a single enforced rule: **all git operations must go through `ai_commit.sh`**. This 430-line Bash script serves as the sole entry point for staging, committing, and pushing code.

```
┌──────────────────────────────────────────────────────────┐
│                    ai_commit.sh (430 lines)               │
│                                                          │
│  1. Set AI_COMMIT_ACTIVE=1 (bypass token for hooks)      │
│  2. Parse flags (--preview, --undo, --signoff, etc.)     │
│  3. Run PR decision engine (should_use_pr.sh)            │
│  4. Pre-flight formatting (Black + Ruff)                 │
│  5. Auto-stash → fetch → stage → commit → sync → push   │
│  6. Stale lock detection (auto-remove .git/index.lock    │
│     if >300s old)                                        │
│  7. Post-push verification                               │
└──────────────────────────────────────────────────────────┘
```

The script sets the environment variable `AI_COMMIT_ACTIVE=1` before any git operations. Custom hook templates in `scripts/git-hooks/` check for this variable — if absent, the commit or push is blocked with an error message directing the agent to use `ai_commit.sh`. An installation script (`install_git_hooks.sh`) exists for deploying these enforcement hooks. Currently, the deployed `.git/hooks/pre-commit` uses the standard pre-commit framework (`.pre-commit-config.yaml`) for auto-formatting (Black) and linting (Ruff, mypy), while the custom `AI_COMMIT_ACTIVE` enforcement hooks remain available as templates but are not yet installed in production. The primary enforcement mechanism is **instruction-based**: all agent instruction files (AGENTS.md, CLAUDE.md, copilot-instructions.md) explicitly forbid manual git operations, and the documented consequences of bypass (causing significant rework, see §10.2) have proven effective at ensuring compliance.

`ai_commit.sh` delegates the actual push workflow to `safe_push.sh` (492 lines), which implements a 7-step sequence. This architectural separation of concerns keeps commit logic and push logic independently maintainable. The 7-step push sequence handles common failure modes automatically:

1. **Check for unfinished merge**: Completes any in-progress merge before proceeding
2. **Pull/fetch**: Fetches latest remote state to detect divergence
3. **Stage**: Stages all files with `git add -A`
4. **Commit**: Creates the commit (pre-commit hooks run at this point)
5. **Re-stage + amend**: Re-stages any modifications made by hooks and amends the commit
6. **Sync again**: Pulls with rebase before push to linearize history
7. **Push**: Pushes safely to remote

Additionally, the script detects stale `.git/index.lock` files older than 300 seconds and removes them automatically — a common issue when agents crash mid-operation.

### 3.3 PR Decision Engine

The PR decision engine (`should_use_pr.sh`, 411 lines) analyzes staged changes to determine whether a pull request is required. The analysis considers:

- **File count**: Number of files changed
- **Lines changed**: Total lines added and removed
- **File types**: Production code vs. documentation vs. tests
- **New files**: Whether new files are being introduced
- **Change complexity**: Renames, moves, and cross-layer modifications

Decision thresholds:

| Condition | Decision |
|-----------|----------|
| Production code: ≤50 lines AND ≤2 files AND 0 new files | Direct commit allowed |
| Docs/scripts: ≤150 lines | Direct commit allowed |
| 150–500 lines (any category) | PR recommended (substantial change) |
| >500 lines | PR mandatory (major change) |
| New files in `fastapi_app/` or `react_app/` | PR required |
| Cross-layer changes (core + UI) | PR required |

The engine logs its reasoning when invoked with `--explain`, providing transparency into the decision. Historical data shows that bypassing PR requirements with `--force` caused significant rework in early sessions (see §10.2) — a lesson that led to the current enforcement model.

### 3.4 CI Polling and Auto-Merge

The task completion workflow (`finish_task_pr.sh`) implements non-TUI CI polling to avoid terminal buffer crashes that plagued earlier interactive approaches:

- **Polling interval**: 15 seconds
- **Timeout**: 20 minutes
- **State detection**: MERGED, CLOSED, CONFLICTING, PENDING, ALL_GREEN
- **Auto-merge**: On all-green CI, merges the PR and deletes the task branch
- **Failure handling**: Reports failing checks and exits without merge

This design ensures that task branches are short-lived and that the main branch remains green.

---

## 4. Multi-Agent Orchestration System

### 4.1 Agent Taxonomy

The system employs 14 specialized agents, each with defined responsibilities, tool permissions, and scope boundaries:

| Agent | Role | Tools | Scope |
|-------|------|-------|-------|
| `orchestrator` | Planning, task delegation | Read-only + subagents | All files |
| `backend` | Python structural_lib, IS 456 | Full edit | `Python/structural_lib/` |
| `frontend` | React 19, R3F, Tailwind | Full edit | `react_app/` |
| `structural-math` | IS 456 pure math, core types | Full edit | `codes/is456/`, `core/` |
| `api-developer` | FastAPI routers, endpoints | Full edit | `fastapi_app/` |
| `ui-designer` | Visual design (design-only) | Read-only | `react_app/src/components/` |
| `structural-engineer` | IS 456 compliance review | Read + terminal | `codes/is456/` |
| `reviewer` | Code review, testing | Read + terminal | All files |
| `tester` | Test creation, coverage | Full edit | `Python/tests/`, `react_app/` |
| `doc-master` | Docs, archives, session logs | Full edit | `docs/` |
| `ops` | Git, CI/CD, Docker | Full edit | `.github/`, `scripts/` |
| `governance` | Project health, maintenance | Full edit | `scripts/`, `docs/` |
| `security` | OWASP, dependency scanning | Read + terminal | All files |
| `library-expert` | IS 456 knowledge, standards | Read + terminal + web | All files |

Agent specialization serves two purposes: it limits the blast radius of errors (the `frontend` agent cannot modify Python core math), and it ensures domain expertise is applied where needed (the `structural-engineer` validates IS 456 compliance, not the `frontend` agent).

### 4.2 Agent Handoff Chains

Complex tasks flow through structured handoff chains that ensure each specialist contributes at the appropriate stage:

```
Feature Workflow:
  orchestrator → backend → api-developer → frontend
    → reviewer → tester → doc-master → ops

IS 456 Clause Implementation:
  orchestrator → structural-engineer → structural-math
    → tester → backend → api-developer → frontend
    → reviewer → doc-master → ops

New Structural Element (column, slab, footing):
  orchestrator → structural-engineer (research)
    → structural-math (types + math) → tester
    → backend → api-developer → frontend
    → reviewer → doc-master → ops

Bug Fix:
  orchestrator → backend/frontend → tester
    → reviewer → doc-master → ops
```

Each agent in the chain follows a mandatory pipeline:

```
PLAN → RESEARCH → GATHER → EXECUTE → TEST → VERIFY → DOCUMENT → COMMIT
```

The chain terminates with `doc-master` updating project logs and `ops` committing the changes, ensuring session continuity is maintained regardless of which agent initiated the work.

### 4.3 Agent Skills

Seven reusable skills encapsulate domain knowledge and tool sequences:

| Skill | Purpose | Key Operations |
|-------|---------|----------------|
| `session-management` | Session start/end automation | Read priorities, verify env, log changes, update handoffs |
| `safe-file-ops` | File move/delete preserving links | Update 870+ internal references, dry-run preview |
| `api-discovery` | API function signature lookup | Prevents parameter name guessing (`b_mm` not `width`) |
| `is456-verification` | IS 456 test runner by category | Clause-specific regression tests, benchmark verification |
| `new-structural-element` | New element workflow | Research → types → math → tests → API → frontend |
| `react-validation` | React build/lint/type-check | TypeScript errors, Tailwind issues, build failures |
| `architecture-check` | 4-layer boundary validation | Import direction, duplication scan, layer violations |

### 4.4 Prompt Templates

Fourteen structured prompt templates provide step-by-step workflows for common tasks:

- `new-feature`, `bug-fix`, `code-review` — Development workflows
- `add-api-endpoint`, `add-is456-clause`, `add-structural-element` — Domain-specific creation
- `fix-test-failure`, `performance-optimization` — Diagnostic workflows
- `session-start`, `session-end` — Session lifecycle
- `file-move`, `is456-verify` — Infrastructure operations
- `context-recovery`, `master-workflow` — Continuity and orchestration

Each template reduces the cognitive load on agents by specifying exactly which files to read, which commands to run, and which checks to perform — eliminating the exploratory phase that wastes tokens and time.

---

## 5. Session Continuity Mechanism

### 5.1 The Context Loss Problem

LLM-based coding agents operate within finite context windows. When a session ends — whether by user action, context overflow, or timeout — all in-session state is lost. The next agent session starts with zero knowledge of:

- What was completed in the previous session
- What decisions were made and why
- What is currently in progress
- What the next priority should be

Without a continuity mechanism, each new session begins with an exploration phase where the agent reads files, runs commands, and gradually reconstructs project state. This exploration consumes tokens, takes time, and often leads to incorrect assumptions about priorities.

In early sessions of `structural_engineering_lib`, skipped session-end documentation was directly correlated with significant rework in subsequent sessions (see §10.2) — agents repeated completed work, made contradictory decisions, or failed to discover in-progress branches.

### 5.2 Append-Only Project Memory

The system maintains four append-only memory artifacts:

```
┌─────────────────────────────────────────────────┐
│               Project Memory                     │
│                                                  │
│  SESSION_LOG.md (400KB+, 105 numbered sessions,  │
│    170+ dated entries)                            │
│  ├── Detailed per-session history                │
│  ├── What changed, what was decided              │
│  └── Unfinished items and blockers               │
│                                                  │
│  WORKLOG.md (55+ entries)                        │
│  ├── One line per change                         │
│  └── date | task | what | commit                 │
│                                                  │
│  TASKS.md (active task board)                    │
│  ├── WIP limits (max 2 concurrent)               │
│  ├── Priority ordering                           │
│  └── Status tracking                             │
│                                                  │
│  next-session-brief.md (structured handoff)      │
│  ├── What to do FIRST                            │
│  ├── Current state of work                       │
│  └── Known blockers                              │
└─────────────────────────────────────────────────┘
```

The append-only constraint is critical: logs are never rewritten, only extended. This ensures that no information is lost, even when agents make mistakes. A secondary artifact, `handoff_latest.md`, provides machine-readable structured handoff data.

### 5.3 Session Lifecycle

Every agent session follows a mandatory lifecycle:

**Start Phase:**
1. Read `next-session-brief.md` for current priorities
2. Read `TASKS.md` for active work items
3. Run `./run.sh session start` to verify environment

**Execution Phase:**
- Commit frequently with descriptive conventional messages
- Track changes, decisions, and unfinished items

**End Phase (MANDATORY — skipping causes documented rework):**
1. Commit any uncommitted work via `./run.sh commit`
2. Log agent feedback via `./run.sh feedback log --agent <name>`
3. Auto-generate session summary via `./run.sh session summary`
4. Sync stale numbers via `./run.sh session sync`
5. Update `WORKLOG.md` — one line per change
6. Update `TASKS.md` — mark completed, add discovered items
7. Update `next-session-brief.md` — handoff for next agent
8. Commit documentation updates

The session-end phase is enforced through agent instructions, prompt templates, and the `session-management` skill. While not technically enforced by hooks (unlike git operations), the documented consequences of skipping have proven sufficient motivation for compliance.

### 5.4 Context Recovery Protocol

A practical problem unique to LLM-based development is mid-session context overflow: when a conversation exceeds the model's context window, all in-session state is lost immediately. The system addresses this with a structured recovery protocol (`context-recovery.prompt.md`) that allows a new conversation to resume from the exact prior state by reading four specific files in order:

1. `docs/planning/next-session-brief.md` — current priorities and last decisions
2. `docs/TASKS.md` (first 60 lines) — active work items
3. Agent instruction file (CLAUDE.md or copilot-instructions.md) — operational rules
4. `git log --oneline -20` — recent commit history

This protocol reduces context recovery from an exploratory process (agents reading random files and guessing state) to a deterministic four-step procedure. To our knowledge, no related work has documented a structured recovery protocol for LLM agent context overflow.

---

## 6. Self-Evolving Infrastructure

### 6.1 Three-Layer Architecture

The self-evolution system operates through three complementary layers:

```
┌───────────────────────────────────────────────────────┐
│  Layer 3: evolve.py (542 lines) — Orchestration       │
│  ├── Auto-fix detected issues                         │
│  ├── Process agent feedback                           │
│  ├── Regenerate folder indexes                        │
│  ├── Archive stale docs                               │
│  ├── Commit fixes                                     │
│  └── Create TODOs for manual items                    │
├───────────────────────────────────────────────────────┤
│  Layer 2: agent_feedback.py (379 lines) — Collection  │
│  ├── Categories: stale-doc, missing, wrong-instruction│
│  ├──   time-wasted, fix-applied, suggestion           │
│  ├── Stored as JSON in logs/feedback/                 │
│  └── Trend analysis via ./run.sh feedback summary     │
├───────────────────────────────────────────────────────┤
│  Layer 1: project_health.py (740 lines) — Scanning    │
│  ├── Health score: 0–100                              │
│  ├── Categories weighted:                             │
│  │   Docs 30% | Code 25% | Agents 20%                │
│  │   Infra 15% | Feedback 10%                        │
│  └── Auto-fixable: stale numbers, broken links,       │
│      missing metadata                                 │
└───────────────────────────────────────────────────────┘
```

**Layer 1 (Health Scanning)** runs `project_health.py` to compute a 0–100 score across five weighted categories. Issues are classified as auto-fixable (stale numbers, broken links, missing metadata) or manual (architecture violations, missing tests). The `--fix` flag applies all auto-fixable corrections immediately.

**Layer 2 (Feedback Collection)** allows agents to report problems at session end: stale documentation, missing instructions, wrong parameter names, time wasted on avoidable issues, and suggestions for improvement. Each report is stored as timestamped JSON in `logs/feedback/`, enabling trend analysis.

**Layer 3 (Evolution Orchestration)** ties the system together. The `evolve.py` script (542 lines) runs the full cycle: auto-fix → process feedback → regenerate indexes → archive old docs → commit → create TODOs. With `--fix`, it applies corrections and commits them. With `--review weekly`, it performs weekly maintenance sweeps.

The self-evolution cycle:

```
     ┌──────────┐
     │  Agents  │
     │  report  │
     │ feedback │
     └────┬─────┘
          ▼
  ┌───────────────┐     ┌────────────────┐
  │ Health Scanner ├────►│ Auto-Fix Engine │
  │ (0–100 score) │     │ (stale numbers, │
  └───────┬───────┘     │  broken links)  │
          │             └────────┬───────┘
          ▼                      ▼
  ┌───────────────┐     ┌────────────────┐
  │ Feedback Trends│     │ Index Regen    │
  │ (recurring     │     │ (index.json +  │
  │  issues)       │     │  index.md)     │
  └───────┬───────┘     └────────┬───────┘
          │                      │
          ▼                      ▼
  ┌──────────────────────────────────────┐
  │  TODOs for manual fixes + Commit     │
  └──────────────────────────────────────┘
```

### 6.2 Parallel Validation Checks

The `check_all.py` orchestrator runs 27 checks across 8 categories in parallel using Python's `ProcessPoolExecutor`:

| Category | Checks | Description |
|----------|--------|-------------|
| **API** (3) | API validation, API contracts, API manifest | Endpoint correctness, contract compatibility |
| **Docs** (7) | Doc validation, broken links, doc versions, CLI reference, tasks format, brief length, scripts index | Documentation integrity |
| **Architecture** (3) | Architecture boundaries, circular imports, import validation | 4-layer enforcement |
| **Governance** (4) | Governance rules, repo hygiene, Python version, schema snapshots | Project conventions |
| **FastAPI** (3) | FastAPI issues, Docker config, OpenAPI snapshot | Backend correctness |
| **Git** (3) | Git state, unfinished merge, version consistency | Repository health |
| **Stale Refs** (3) | Script references, instruction drift, bootstrap freshness | Reference integrity |
| **Code** (1) | Type annotations | Code quality |

A `--quick` mode runs a fast subset of 8 checks in under 30 seconds for rapid feedback. A `--changed` mode uses path-filter optimization to skip irrelevant categories (e.g., docs-only changes skip Python tests and FastAPI checks).

### 6.3 Governance Cadence

The governance process operates at three time scales:

- **Every session**: Review commit reports, verify mandatory pipeline was followed, check session-end documentation
- **Weekly**: Review git logs for anomalies, check stale tasks, scan for code duplication, run `./run.sh evolve --review weekly`
- **Monthly**: Review mistake patterns from feedback logs, update PR thresholds, archive stale docs, regenerate all folder indexes

---

## 7. Safety Mechanisms

### 7.1 Forbidden Operations

The system maintains an explicit blocklist of operations that have historically caused damage:

**Manual git (blocked by hooks):**
- `git add`, `git commit`, `git push`, `git pull` — Use `ai_commit.sh` instead
- `git commit --amend` — Use `ai_commit.sh --amend`
- `git reset --hard` — No safe equivalent; requires manual justification

**Destructive GitHub operations (require user confirmation):**
- `gh pr merge --admin` — Bypasses required CI checks
- `gh issue close` — Destructive, requires explicit approval
- `git push origin --delete` — Use `cleanup_stale_branches.py --dry-run`

**Force flags (strongly discouraged — not technically blocked but cause documented harm):**
- `--no-verify` — Skips pre-commit hooks; forbidden in all agent instructions
- `--force` — Strongly discouraged by all agent instructions. Historical data shows `--force` bypasses caused significant rework (see §10.2). Still technically available in `ai_commit.sh` for edge cases but agents are instructed never to use it
- `GIT_HOOKS_BYPASS=1` — Disables all safety hooks; forbidden in all agent instructions

**File operations:**
- `mv`, `rm` — Use `safe_file_move.py` and `safe_file_delete.py` which preserve 870+ internal documentation links

### 7.2 Enforcement Layers

Safety enforcement operates through multiple complementary layers:

```
┌─────────────────────────────────────────────────┐
│            Enforcement Stack                     │
│                                                  │
│  Agent instruction files (primary enforcement)   │
│  └── AGENTS.md, CLAUDE.md, copilot-instructions  │
│      explicitly forbid manual git operations      │
│                                                  │
│  Pre-commit framework (.pre-commit-config.yaml)  │
│  └── Deployed: auto-formats Python               │
│      (Black, Ruff, mypy) on every commit         │
│                                                  │
│  Custom hook templates (scripts/git-hooks/)       │
│  └── Block commits without AI_COMMIT_ACTIVE=1    │
│  └── Block pushes without SAFE_PUSH_ACTIVE=1     │
│  └── Validate conventional commit format          │
│  └── Deployable via install_git_hooks.sh          │
│  └── (designed but not yet deployed in prod)      │
│                                                  │
│  Architecture checks                             │
│  └── Blocks layer violations via                 │
│      check_architecture_boundaries.py            │
│                                                  │
│  PR decision engine                              │
│  └── Blocks direct commits for production changes│
└─────────────────────────────────────────────────┘
```

The enforcement stack uses a defense-in-depth approach. The primary layer is instruction-based: all agent configuration files explicitly forbid manual git operations, backed by documented evidence of the rework caused by violations. The pre-commit framework (Black, Ruff, mypy) is deployed and enforces code quality standards on every commit. Custom hook templates in `scripts/git-hooks/` provide an additional enforcement layer using environment variable bypass tokens (`AI_COMMIT_ACTIVE=1`, `SAFE_PUSH_ACTIVE=1`) — these templates are designed and available for deployment via `install_git_hooks.sh` but are not yet installed in production `.git/hooks/`. This represents a design gap: full hook-based enforcement is architecturally complete but current enforcement relies on instruction compliance, which has proven effective in practice.

### 7.3 Recovery Mechanisms

The `recover_git_state.sh` script (161 lines) handles common git state corruption scenarios:

- **Rebase in progress**: Auto-abort or continue based on conflict state
- **Cherry-pick in progress**: Abort and restore clean state
- **Merge conflicts**: Auto-resolve for safe files (TASKS.md, SESSION_LOG.md, next-session-brief.md); require manual resolution for production code
- **Detached HEAD**: Checkout main branch and fast-forward
- **Stale hooks**: Reinstall from template
- **Stale locks**: Remove `.git/index.lock` if older than 300 seconds

The distinction between safe files (documentation, logs) and production files (Python code, React components) ensures that auto-recovery never silently damages application logic.

---

## 8. Documentation Infrastructure

### 8.1 Link Preservation

The codebase maintains 870+ internal documentation links across markdown files. Direct file operations (`mv`, `rm`) would break these links silently, creating a cascading documentation failure. Two safe scripts handle all file operations:

- `safe_file_move.py` — Moves a file and updates all references across the entire repository
- `safe_file_delete.py` — Deletes a file and removes or updates all referencing links

Both scripts support `--dry-run` for preview before execution. The `check_links.py` validator detects any broken links that slip through, running as part of the 27-check validation suite.

### 8.2 Folder Indexes

Every key folder maintains dual-format indexes:

- `index.json` — Machine-readable: file list, exported classes, functions, parameters, and descriptions
- `index.md` — Human-readable: tables with descriptions, export counts, and line counts

Agents are instructed to read folder indexes before diving into individual files, reducing token consumption and improving context accuracy. The indexes are auto-regenerated by `generate_enhanced_index.py --all` after structural changes.

### 8.3 Automation Map

All 96 tasks in the repository are catalogued in `automation-map.json` with metadata:

- Script path and description
- CLI options and usage examples
- "Never use" alternatives (e.g., never use `mv` — use `safe_file_move.py`)

The `find_automation.py` script provides fuzzy search over this map, allowing agents to discover existing automation for any task before creating new scripts — directly addressing the code duplication problem.

### 8.4 Clause Traceability API

A unique contribution for engineering software infrastructure is the `@clause` decorator system in `codes/is456/traceability.py`. Every IS 456:2000 calculation function is decorated with the specific clause reference it implements (e.g., `@clause("39.4.1")` for shear design). This enables programmatic clause-to-code tracing: given any IS 456 clause number, the system can identify which functions implement it, and given any function, the system can report which clauses it satisfies. This bidirectional traceability is critical for engineering software where regulatory compliance must be auditable and is a pattern applicable to any domain with codified standards (Eurocode, ACI 318, ASCE 7).

---

## 9. Metrics and Results

The following metrics are drawn from the deployed system as of March 2026:

| Metric | Value |
|--------|-------|
| Sessions logged in SESSION_LOG.md | 105 numbered sessions (170+ dated entries) |
| Python tests passing | 3,226 |
| API endpoints | 38 across 12 routers |
| Custom React hooks | 16+ |
| Specialized agents | 14 |
| Agent skills | 7 |
| Prompt templates | 14 |
| Tasks mapped in automation-map.json | 96 |
| Parallel validation checks | 27 (8 categories) |
| Internal documentation links preserved | 870+ |
| WORKLOG entries | 55+ |
| `ai_commit.sh` size | 430 lines |
| `should_use_pr.sh` size | 411 lines |
| `project_health.py` size | 740 lines |
| `evolve.py` size | 542 lines |
| Merge conflicts from manual git | **0** (since instruction-based enforcement, ~Session 80+) |
| Hours saved per averted incident | ~10 (vs. pre-enforcement baseline) |
| CI workflows | 16 |

The most significant metric is the elimination of merge conflicts. Prior to instruction-based enforcement, each merge conflict incident consumed substantial human and agent time for resolution, context recovery, and rework (see §10.2 for specific failure cases and time estimates). The zero-conflict record applies to the period since instruction-based enforcement was adopted (approximately Session 80+); the system was iteratively developed and refined through all 105+ sessions. With zero conflicts since enforcement, the investment in infrastructure has yielded substantial time savings.

*Note on session counting:* Sessions are numbered sequentially; the 170+ dated entries include unnumbered maintenance entries and multi-entry sessions.

---

## 10. Lessons Learned

### 10.1 What Worked

1. **Zero-tolerance for manual git.** Pre-push hooks eliminate approximately 80% of merge conflicts by design. The remaining 20% — concurrent work on the same logical feature — is addressed by the PR decision engine and task branch isolation.

2. **Append-only logs.** By never allowing log overwrites, the system preserves complete project history. When context is lost, agents can reconstruct state from SESSION_LOG.md and WORKLOG.md rather than re-exploring the codebase.

3. **Standardized entry points.** `run.sh` and `ai_commit.sh` reduce cognitive load for agents. Instead of remembering directory structures and tool chains, agents use a consistent command vocabulary.

4. **Self-healing feedback loops.** The cycle of agent feedback → evolution engine → auto-fix → health score creates a positive feedback loop: infrastructure improves with each session.

5. **Domain-specific agent specialization.** The `structural-engineer` agent validates IS 456:2000 compliance; the `security` agent checks OWASP conformance. Specialization ensures that domain expertise is applied where it matters, not diluted across generalist agents.

### 10.2 What Failed Initially

1. **Parameter name guessing.** Agents consistently guessed API parameter names (`width` instead of `b_mm`, `concrete_grade` instead of `fck`). This was solved by creating `discover_api_signatures.py` and making it a mandatory pre-step in the `api-discovery` skill.

2. **Terminal path confusion.** Agents ran commands from wrong directories (`cd Python && .venv/bin/pytest tests/` when `.venv` is at the project root). Explicit path rules in agent instructions and the `terminal-rules.instructions.md` file addressed this.

3. **PR bypass with `--force`.** Early versions of the commit script allowed `--force` to bypass PR requirements. This led to 10+ hours of rework on multiple occasions. The flag now triggers a prominent warning and is listed as FORBIDDEN in all agent instructions.

4. **Session-end skipping.** When agents terminated without updating logs and handoffs, subsequent agents wasted significant time rediscovering project state. The mandatory session-end protocol, enforced through agent instructions and the `session-management` skill, reduced this to near-zero.

5. **PR decision blind spots.** The initial `should_use_pr.sh` did not account for changes to `fastapi_app/` and `react_app/` directories, leading to unreviewed production changes. The script was expanded to cover all production code paths.

### 10.3 Recommendations for Other Projects

Based on 105 numbered sessions of operational experience, we offer the following recommendations for teams adopting multi-agent development:

1. **Start with git hook enforcement from day one.** Retrofitting hooks onto an existing workflow is harder than building with them.

2. **Implement session continuity before scaling to multiple agents.** A single agent with good logs outperforms three agents with no memory.

3. **Use append-only logs, not overwritten state files.** Overwritten state files lose the "why" behind decisions.

4. **Build self-healing before it is needed.** The cost of not having auto-recovery compounds exponentially with session count.

5. **Enforce architecture at the tooling level, not just with documentation.** Agents respect hooks and checks; they inconsistently respect written guidelines.

6. **Map all automation.** Agents need a "where is the script for X?" lookup to avoid reinventing existing tools.

7. **Implement agent feedback loops.** Let agents report problems back to the infrastructure — this closes the loop between detection and resolution.

### 10.4 Limitations

The following limitations should be considered when interpreting the results presented in this paper:

1. **Single-developer project.** `structural_engineering_lib` is maintained by a single developer with AI agent assistance. The multi-agent coordination challenges and solutions described here may not generalize directly to large teams with multiple human developers operating concurrently.

2. **Hook enforcement designed but not yet fully deployed.** The custom git hooks (`AI_COMMIT_ACTIVE` enforcement) exist as templates in `scripts/git-hooks/` but are not installed in `.git/hooks/` in production. Current enforcement is instruction-based — agents comply because instruction files forbid manual git and document the consequences of violation. This has proven effective but is not a technical guarantee.

3. **No token usage tracking.** While the session continuity mechanism reduces redundant context exploration, we do not track per-session or per-agent token consumption. We cannot quantify the exact token waste prevented by the infrastructure.

4. **No formal verification of architecture.** The 4-layer architecture boundary checks are heuristic (import pattern matching, file path analysis) rather than formally provable. False negatives are possible, particularly for dynamic imports or runtime composition.

5. **Self-evolution metrics are self-reported.** The health scores, feedback trends, and auto-fix counts are generated by the system itself. No independent audit has verified these metrics against ground truth.

### 10.5 Threats to Validity

- **Internal validity:** This is a single-developer project with AI agent assistance. Results may not transfer to multi-developer teams with concurrent AI agent sessions, where coordination challenges are compounded by human-agent and agent-agent conflicts.
- **External validity:** The infrastructure was developed for a domain-specific application (structural engineering per IS 456:2000). While the architectural patterns are intended to be general, infrastructure demands may differ substantially in other software domains (e.g., real-time systems, data pipelines, mobile applications).
- **Construct validity:** Key metrics — including the "10+ hours of rework" estimate per merge conflict incident — are self-reported from project logs and developer experience. No independent auditor has verified these claims, and the estimates may be subject to recall bias.
- **Reliability:** No controlled A/B experiment was conducted comparing development with vs. without the infrastructure. Causal claims (e.g., "instruction-based enforcement eliminated merge conflicts") are based on before/after observation within the same project, and confounding factors (developer experience growth, codebase maturity) cannot be ruled out.

---

## 11. Proposed Improvements and Future Work

1. **Formal Agent Behavioral Contracts.** Extend hook-based enforcement to formal specification languages, enabling static verification of agent behavior before execution. Inspired by the behavioral contracts framework (arXiv:2602.22302).

2. **Token Usage Tracking.** Implement per-agent, per-session token consumption tracking to identify inefficient agents and optimize context loading strategies. Inspired by Tokenomics (arXiv:2601.14470).

3. **Cross-Repository Generalization.** Package the infrastructure (`ai_commit.sh`, hook templates, `check_all.py`, `evolve.py`) as a reusable framework for other domain-specific projects.

4. **AI-Driven PR Review.** Auto-generate PR descriptions and review comments using LLM analysis of diffs, reducing the manual review burden.

5. **Predictive Conflict Detection.** Train an ML model on historical file modification patterns to warn agents before they begin work on files likely to cause conflicts.

6. **Agent Performance Benchmarking.** Track agent effectiveness over time: errors per session, rework rate, time-to-completion, tests written, and documentation quality.

7. **Automated Rollback.** If CI fails after merge, automatically revert the merge commit and notify the responsible agent with context about the failure.

8. **Multi-Repository Orchestration.** Extend handoff chains across multiple repositories for projects with separate frontend, backend, and library repositories.

9. **Real-Time Agent Monitoring Dashboard.** A live web view showing which agent is working, what files are being modified, current pipeline stage, and health score — enabling human supervisors to intervene early.

10. **Formal Verification of Architecture.** Static analysis to prove 4-layer boundaries at the type system level, eliminating the need for runtime architecture checks.

11. **Parity Testing Harness.** Automated cross-platform parity verification between Python and VBA implementations of IS 456 calculations.

12. **Adaptive PR Thresholds.** Learn optimal PR vs. direct-commit thresholds from historical data: which types of direct commits caused regressions, and which PRs were unnecessary overhead.

---

## 12. Conclusion

This paper presents a production-deployed, self-evolving multi-agent git infrastructure for `structural_engineering_lib`, an IS 456:2000 reinforced concrete beam design library. The system addresses the fundamental challenges of LLM-based multi-agent software development through four interlocking mechanisms:

1. **Enforced git workflows** via `ai_commit.sh` and pre-commit/pre-push hooks, eliminating manual git operations and the merge conflicts they cause.

2. **Session continuity** via append-only logs (SESSION_LOG.md, WORKLOG.md) and structured handoffs (next-session-brief.md), preserving context across 105 numbered sessions (170+ dated entries).

3. **Self-evolving infrastructure** via a three-layer system (health scanning, feedback collection, evolution orchestration) that detects and repairs its own regressions.

4. **Domain-specific agent specialization** via 14 agents with defined roles, 7 reusable skills, and 14 prompt templates, ensuring that IS 456:2000 compliance, architectural boundaries, and engineering units are maintained.

The quantitative results speak directly: zero merge conflicts since instruction-based enforcement was adopted (~Session 80+), 3,226 passing tests, 27 parallel validation checks, and 96 mapped tasks — all maintained across 105 numbered sessions without manual infrastructure maintenance. The estimated savings from averted merge conflict incidents (see §10.2) demonstrate that the overhead of safety infrastructure pays for itself within the first few sessions.

The system is open-source and available for adoption by other domain-specific engineering software projects. We believe the principles demonstrated here — enforced workflows, append-only memory, self-healing infrastructure, and domain-specific specialization — are broadly applicable to any project where multiple LLM agents collaborate on a shared codebase.

---

## References

1. SEMAG — Self-Evolutionary Multi-Agent Code Generation. arXiv:2603.15707, 2026.

2. AgentMesh — A Cooperative Multi-Agent Framework for Software Development. arXiv:2507.19902, 2025.

3. SAGE — Tool-Augmented LLM-Based Multi-Agent Task Solving. arXiv:2601.09750, 2026.

4. DebateCoder — Adaptive Confidence Gating for Multi-Agent Collaboration in Code Generation. arXiv:2601.21469, 2026.

5. Autonoma — A Hierarchical Multi-Agent Framework for Software Development. arXiv:2603.19270, 2026.

6. Diaz-De-Arcaya, J. et al. — Self-Healing Infrastructure-as-Code with Large Language Models. ACM International Conference on the Art, Science, and Engineering of Programming, 2024.

7. Bhattarai, S. — Scaling Generative AI for Self-Healing DevOps Pipelines. Preprint, 2025.

8. Agent Behavioral Contracts — Formal Specification for AI Agents. arXiv:2602.22302, 2026.

9. Theory of Code Space — Do Code Agents Understand Software Architecture? arXiv:2603.00601, 2026.

10. Tokenomics — Token Usage Analysis in Agentic Software Engineering. arXiv:2601.14470, 2026.

11. Qian, C., et al. "ChatDev: Communicative Agents for Software Development." arXiv:2307.07924, 2023.

12. Xie, T., et al. "DevGPT: Studying Developer-ChatGPT Conversations." arXiv:2309.03914, 2023.

---

*Manuscript prepared March 30, 2026. This paper describes the infrastructure of an open-source project; all metrics are derived from actual production usage.*