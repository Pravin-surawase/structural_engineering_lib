---
owner: Main Agent
status: active
last_updated: 2026-04-02
doc_type: guide
complexity: intermediate
tags: []
---

# How to Use Copilot Agents — Practical Guide

**Type:** Guide
**Audience:** Developers
**Status:** Approved
**Importance:** High
**Created:** 2026-03-27
**Last Updated:** 2026-04-02

---

## Quick Overview

You have **16 agents**, **10 skills**, and **16 prompt files** configured in VS Code Copilot. This guide shows you when and how to use each one.

### How to invoke

| What | How | Example |
|------|-----|---------|
| **Agent** | Type `@agent-name` in Copilot Chat | `@backend fix the flexure calculation` |
| **Skill** | Type `/skill-name` in Copilot Chat | `/api-discovery design_beam_is456` |
| **Prompt** | Type `#prompt-name` in Copilot Chat | `#new-feature add torsion endpoint` |

---

## The 16 Agents — When to Use Each

### Start Here: `@orchestrator`

**Use when:** You're not sure which agent to use, or the task spans multiple areas.

```
@orchestrator I need to add a deflection check feature — plan the work
```

The orchestrator will:
- Break the task into steps
- Tell you which specialist to use for each step
- Provide handoff prompts to chain agents together

---

### Frontend: `@frontend`

**Use when:** Working on React components, hooks, 3D visualization, Tailwind styling.

```
@frontend add a deflection results panel to the DesignView
@frontend why is the 3D viewport not showing stirrups?
@frontend create a hook for the new /api/v1/analysis/deflection endpoint
```

**It knows about:** All 18+ existing hooks, component structure, Tailwind-only rule, Zustand stores.

---

### Backend: `@backend`

**Use when:** Working on Python structural_lib — IS 456 math, services, adapters.

```
@backend add a deflection check to the serviceability module
@backend why is design_beam_is456 returning wrong Ast for doubly reinforced?
@backend add a new function to services/api.py
```

**It knows about:** 4-layer architecture, units rules, all 23 API functions, the api.py stub warning.

---

### API Developer: `@api-developer`

**Use when:** Adding or modifying FastAPI endpoints.

```
@api-developer add POST /api/v1/analysis/deflection endpoint
@api-developer the /design/beam endpoint is returning 422 — fix validation
```

**It knows about:** All 47 existing endpoints across 13 routers, Pydantic models, Docker testing.

---

### Structural Engineer: `@structural-engineer`

**Use when:** Verifying IS 456 compliance, checking formulas, reviewing calculations.

```
@structural-engineer verify the shear design formula in shear.py matches IS 456 Cl 40
@structural-engineer check if our minimum reinforcement calculation handles fck=50
@structural-engineer review the torsion implementation against Cl 41
```

**It knows about:** All IS 456 clause references, SP:16, benchmark problems, edge cases, units table.

> **Read-only** — it reviews and advises but doesn't edit code. It hands off to `@backend` for implementation.

---

### Reviewer: `@reviewer`

**Use when:** You want a code review before committing.

```
@reviewer review my changes to the flexure module
@reviewer check if my new endpoint follows project conventions
```

**It checks:** Architecture boundaries, units, IS 456 compliance, test coverage, no code duplication.

> **Read-only** — it reviews but doesn't edit. It hands off to `@doc-master` for doc updates.

---

### UI Designer: `@ui-designer`

**Use when:** Planning the visual layout of a new feature before coding it.

```
@ui-designer design the layout for a batch design results dashboard
@ui-designer suggest how to display deflection check results in the beam detail panel
```

**It knows about:** Existing components, color palette, Tailwind patterns, accessibility.

> **Read-only** — it designs but doesn't code. It hands off to `@frontend` for implementation.

---

### Doc Master: `@doc-master`

**Use when:** Updating docs, running session end, archiving old files, fixing indexes.

```
@doc-master run session end
@doc-master archive the old planning docs from Q1
@doc-master regenerate folder indexes after the file moves
```

**It knows about:** Session workflow, safe file ops, doc metadata, archive policy, canonical docs.

---

### Governance: `@governance`

**Use when:** Checking project health, maintenance metrics, enforcing standards.

```
@governance run a project health check
@governance validate folder conventions
@governance check doc budget
```

**It knows about:** Doc budget, folder structure conventions, project health scoring, maintenance tasks.

---

### Security: `@security`

**Use when:** Auditing for OWASP vulnerabilities, scanning dependencies, reviewing auth.

```
@security audit the FastAPI routers for injection vulnerabilities
@security scan dependencies for known CVEs
@security review the auth middleware
```

**It knows about:** OWASP Top 10, dependency scanning, security best practices, permission enforcement.

> **Read-only** — it audits and advises but doesn't edit code. It hands off to `@backend` for fixes.

---

### Library Expert: `@library-expert`

**Use when:** Need IS 456 domain expertise, professional engineering standards, or library design guidance.

```
@library-expert what does IS 456 Cl 26.5.1.1 require for minimum reinforcement?
@library-expert review the API design for the new column module
@library-expert compare our deflection approach vs SP:16 recommendations
```

**It knows about:** IS 456:2000 in depth, SP:16, professional structural engineering practice, library API design.

> **Read-only** — it advises but doesn't edit code. It hands off to `@backend` or `@structural-engineer`.

---

### Agent Evolver: `@agent-evolver`

**Use when:** Improving agent instructions, detecting drift, scoring agent performance.

```
@agent-evolver score all agents and detect instruction drift
@agent-evolver propose improvements for the backend agent
@agent-evolver run weekly auto-maintenance review
```

**It knows about:** Agent registry, instruction evolution, performance scoring, drift detection.

---

### Structural Math: `@structural-math`

**Use when:** Adding new IS 456 pure math modules, core types, or new structural elements.

```
@structural-math implement the column interaction curve calculation
@structural-math add torsion design per IS 456 Cl 41
@structural-math create the footing core types
```

**It knows about:** 4-layer architecture (codes layer), pure math implementation, IS 456 formulas, units rules.

---

### Tester: `@tester`

**Use when:** Creating tests, improving coverage, running benchmarks.

```
@tester add tests for the new deflection check function
@tester check coverage for the shear module
@tester create benchmark tests against SP:16 examples
```

**It knows about:** pytest setup, test patterns, IS 456 benchmarks, coverage requirements (85% branch).

---

### Innovator: `@innovator`

**Use when:** Starting innovation research, identifying capability gaps, proposing novel features.

```
@innovator research sustainability scoring for structural designs
@innovator what capabilities are we missing compared to other structural tools?
@innovator propose a generative design approach for beam optimization
```

**It knows about:** Research methodologies, capability gap analysis, novel engineering approaches.

> **Won't do:** Implement production code (delegates to specialists).

---

### Ops: `@ops`

**Use when:** Git issues, Docker problems, CI/CD, environment setup.

```
@ops I have a merge conflict — help me resolve it
@ops Docker compose is failing — Colima issue?
@ops create a PR for the deflection feature
```

**It knows about:** THE ONE RULE (ai_commit.sh), PR workflow, Colima/Docker, port management, emergency recovery.

---

## The 10 Skills — Quick Actions

Skills are shortcuts for common tasks. Use them inline in any chat.

### `/session-management`

Start or end a work session:
```
/session-management start a new session
/session-management end the session
```

### `/api-discovery`

Look up exact function signatures (prevents the #1 mistake — wrong param names):
```
/api-discovery design_beam_is456
/api-discovery --filter rebar
/api-discovery --all
```

### `/safe-file-ops`

Move or delete files without breaking 870+ internal links:
```
/safe-file-ops move docs/old-guide.md to docs/guides/new-guide.md
/safe-file-ops delete the deprecated planning doc
```

### `/is456-verification`

Run IS 456 compliance tests by category:
```
/is456-verification run compliance tests
/is456-verification check detailing rules
/is456-verification full regression
```

### `/react-validation`

Run React build, lint, type-check, and test validation:
```
/react-validation run full check
/react-validation check types only
```

### `/agent-evolution`

Run self-evolution cycle — score agents, detect drift, propose improvements:
```
/agent-evolution score all agents
/agent-evolution detect drift
/agent-evolution weekly review
```

### `/new-structural-element`

Step-by-step workflow for adding a new structural element:
```
/new-structural-element add column design
/new-structural-element add footing design
```

### `/function-quality-pipeline`

Mandatory 9-step quality pipeline for every new IS 456 function:
```
/function-quality-pipeline check design_singly_reinforced
/function-quality-pipeline run full pipeline
```

### `/architecture-check`

Validate 4-layer architecture boundaries and import direction:
```
/architecture-check validate imports
/architecture-check check for duplication
```

### `/innovation-research`

Run a guided innovation research cycle:
```
/innovation-research sustainability
/innovation-research generative-design
```

---

## The 16 Prompt Files — Workflow Templates

Prompt files are reusable workflow templates. Reference them with `#`.

| Prompt | When to Use | Example |
|--------|-------------|--------|
| `#new-feature` | Starting any new feature | `#new-feature add deflection check` |
| `#bug-fix` | Fixing a bug | `#bug-fix shear design returns wrong stirrup spacing` |
| `#code-review` | Reviewing changes | `#code-review check my PR` |
| `#add-api-endpoint` | Adding a FastAPI route | `#add-api-endpoint POST /analysis/deflection` |
| `#add-is456-clause` | Implementing an IS 456 clause | `#add-is456-clause implement Cl 41 torsion` |
| `#add-structural-element` | New structural element workflow | `#add-structural-element add column design` |
| `#function-quality-gate` | IS 456 function quality gate (9-step) | `#function-quality-gate check_deflection` |
| `#fix-test-failure` | Diagnosing and fixing test failures | `#fix-test-failure test_shear_design fails` |
| `#performance-optimization` | Profile, optimize, benchmark | `#performance-optimization optimize beam pipeline` |
| `#session-start` | Beginning a session | `#session-start` |
| `#session-end` | Ending a session | `#session-end` |
| `#file-move` | Moving/renaming files | `#file-move old_module.py to services/` |
| `#is456-verify` | Checking formulas | `#is456-verify verify Cl 38.1 flexure` |
| `#context-recovery` | Resuming after context overflow | `#context-recovery` |
| `#master-workflow` | Master workflow orchestration | `#master-workflow plan full feature delivery` |
| `#innovation-research` | Innovation research cycle | `#innovation-research sustainability scoring` |

---

## Common Workflows — Step by Step

### 1. Daily Session

```
1. #session-start                              → Read priorities, check env
2. @orchestrator what should I work on today?   → Get a plan
3. (work with specialist agents)                → @backend, @frontend, etc.
4. @reviewer review my changes                  → Before committing
5. #session-end                                 → Log, handoff, commit
```

### 2. New Feature (Full Stack)

```
1. @orchestrator plan: add deflection check feature
2. @backend add serviceability check to codes/is456/serviceability.py
3. @structural-engineer verify the implementation matches IS 456 Cl 43
4. @api-developer add POST /api/v1/analysis/deflection endpoint
5. @frontend create useDeflectionCheck hook and results panel
6. @reviewer review all changes
7. @doc-master update docs and session end
```

### 3. Bug Fix

```
1. #bug-fix shear design returns wrong result for fck=50
2. @backend investigate and fix                → Finds and fixes the issue
3. @structural-engineer verify the fix         → Checks IS 456 compliance
4. @reviewer review the fix                    → Validates quality
```

### 4. IS 456 Formula Change

```
1. @structural-engineer review current Cl 40 shear implementation
2. @backend implement the corrections
3. /is456-verification run shear tests          → Verify nothing broke
4. @api-developer update endpoint if API contract changed
5. @reviewer final review
```

### 5. Quick Tasks (No Agent Needed)

For simple, single-file tasks, just use Copilot directly:
- Fix a typo
- Add a test case
- Update a config value

---

## Agent Handoff — How It Works

When an agent finishes its part, it shows **handoff buttons** at the bottom of its response:

```
[Review Changes]  [Frontend Integration]  [Back to Planning]
```

Click the button to switch to the next agent with context carried over. The typical flow:

```
orchestrator → backend → api-developer → frontend → reviewer → doc-master → ops
```

You can also manually invoke agents at any point — you're not locked into the chain.

---

## Tips & Common Mistakes

### Do

- **Start with `@orchestrator`** for multi-step tasks
- **Use `/api-discovery`** before wrapping any Python function
- **Run `#session-end`** at the end of every session — this is mandatory
- **Use `#code-review`** before committing production code
- **Click handoff buttons** to maintain context across agents

### Don't

- **Don't skip session end** — it costs 10+ hours of rework for the next session
- **Don't guess parameter names** — use `/api-discovery` (it's `b_mm` not `width`)
- **Don't use `git commit` manually** — always `./scripts/ai_commit.sh`
- **Don't create new hooks without checking** — ask `@frontend` to search first
- **Don't edit `Python/structural_lib/api.py`** — it's a stub, real code is in `services/api.py`
- **Don't create `.css` files** — Tailwind only

---

## Quick Reference Card

```
AGENTS:      @orchestrator  @frontend  @backend  @api-developer
             @structural-math  @structural-engineer  @reviewer
             @ui-designer  @doc-master  @ops  @governance
             @security  @library-expert  @agent-evolver  @tester

SKILLS:      /session-management  /api-discovery  /safe-file-ops
             /is456-verification  /react-validation  /agent-evolution
             /new-structural-element  /function-quality-pipeline
             /architecture-check

PROMPTS:     #new-feature  #bug-fix  #code-review  #add-api-endpoint
             #add-is456-clause  #add-structural-element
             #function-quality-gate  #fix-test-failure
             #performance-optimization  #session-start  #session-end
             #file-move  #is456-verify  #context-recovery
             #master-workflow

GIT:         ./scripts/ai_commit.sh "type: message"    (ALWAYS)
PR:          ./run.sh pr status → ./run.sh pr create    (when required)
```

---

## Context Management — Working Through Long Sessions

### Problem: LLM Context Overflow

Long sessions cause the LLM to lose track of what it was doing. Symptoms:
- Agent starts repeating earlier work
- Agent forgets decisions made earlier in the conversation
- Responses become generic or miss project-specific rules

### Solution: Checkpoint & Recover

**Before overflow hits** (when conversation feels long):
```
Save a checkpoint: summarize what we've done, what's in progress,
and what's left. Write it to docs/planning/next-session-brief.md
```

**After starting a new chat:**
```
#context-recovery
```

Or manually:
```
Read these to recover context:
1. docs/planning/next-session-brief.md
2. docs/TASKS.md (first 60 lines)
3. .github/copilot-instructions.md
4. git log --oneline -20
Then continue from where I left off.
```

### Efficiency Tips for Context

| Tip | Why |
|-----|-----|
| Commit frequently | Each commit is a save point you can reference |
| Use `next-session-brief.md` as scratchpad | It survives between chats |
| Keep conversations focused | One feature per chat session |
| Use `@orchestrator` to re-plan | When resuming, it reads priorities and re-orients |
| Read `index.json` files first | Faster than reading individual files |
| Use `grep_search` before `read_file` | Find the right lines without reading entire files |

### Large Files — Read Selectively

These files are too large to read in full:

| File | Size | How to Read |
|------|------|-------------|
| `docs/SESSION_LOG.md` | 400KB+ | `tail -100` or search for specific session |
| `services/adapters.py` | 71KB | Search by class/function name first |
| `CHANGELOG.md` | 52KB | `head -50` for recent entries |

---

## Efficiency Patterns

### 1. Parallel Agent Handoffs

For independent tasks, you can run agents in parallel (open multiple chat windows):
```
Chat 1: @backend implement the serviceability check
Chat 2: @frontend design the results panel layout
```
Then merge with a review:
```
Chat 3: @reviewer review changes in both areas
```

### 2. Skill Chaining

Combine skills with agents for faster work:
```
/api-discovery design_beam_is456          → Get exact params
@api-developer add endpoint using those params  → Build the route
@frontend create hook for the endpoint           → Wire up the UI
```

### 3. Prompt + Agent Combo

Start with a prompt template, then refine with an agent:
```
#new-feature add deflection check         → Gets the workflow
@backend implement step 2 from the plan   → Executes specifically
```

### 4. Batch Operations

For repetitive tasks across files:
```
@doc-master regenerate all folder indexes after the restructure
@ops commit all the doc changes in one batch
```

### 5. Pre-Flight Before Deep Work

Before a large feature, get oriented:
```
@orchestrator I need to add column design — what exists already,
what needs to be added, and which agents should work on each part?
```
