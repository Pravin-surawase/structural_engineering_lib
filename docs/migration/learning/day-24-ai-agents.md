# Day 24: AI Agent System

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** High
**Created:** 2026-04-08
**Last Updated:** 2026-04-08
**Prerequisites:** Day 23 (or general familiarity with the project structure)
**Library files:** `agents/agent_registry.json`, `scripts/prompt_router.py`, `scripts/tool_permissions.py`, `scripts/pipeline_state.py`
**Related docs:** `.github/agents/*.agent.md`, `.github/skills/*/SKILL.md`

---

## What You'll Learn Today

By the end of this module you'll understand:
- What an AI agent system is and why a structural engineering library needs one
- How our 16 specialized agents divide responsibilities
- How `agent_registry.json` defines permissions, skills, and keywords
- How the prompt router turns natural language into agent assignments
- What agent skills are and how they get reused across agents
- How the 8-step pipeline ensures nothing gets skipped
- How permission enforcement prevents agents from doing things they shouldn't
- How the agent-evolver keeps the system improving over time

---

## 📖 Theory

### 1. What Is an AI Agent System?

Imagine you're running a construction project. You wouldn't ask the electrician to pour the concrete foundation, or the architect to wire the circuit breakers. Each specialist has defined expertise and clear boundaries around what they should touch.

An **AI agent system** works the same way. Instead of one general-purpose LLM doing everything (and making mistakes everywhere), you create *specialized assistants* — each with:

- **Knowledge** — what files and concepts they understand best
- **Permissions** — what they're allowed to read, write, or delete
- **Skills** — reusable capabilities they can invoke
- **Handoff targets** — who they pass work to next

> **Think of it like...** a software team org chart. The orchestrator is the tech lead, the backend agent is the Python developer, the frontend agent is the React developer, and the reviewer is the senior engineer who checks everyone's work.

Why does a structural engineering library need this? Because the codebase spans IS 456 pure math, FastAPI endpoints, React 3D visualization, Docker deployment, documentation, and testing. No single agent prompt can hold all that context without making mistakes. Specialization prevents the #1 agent failure mode: **doing things outside your expertise**.

---

### 2. Our 16 Agents

The agents live in `.github/agents/`, one file per agent. Here's the team:

**Planning & Delegation:**
| Agent | Role | Permission |
|-------|------|------------|
| `orchestrator` | Plans, triages, delegates tasks | ReadOnly |

**Full Edit Agents (write code):**
| Agent | Role | File Scope |
|-------|------|------------|
| `backend` | Python structural_lib core | `Python/structural_lib/**` |
| `frontend` | React 19, R3F, Tailwind | `react_app/**` |
| `api-developer` | FastAPI routers, endpoints | `fastapi_app/**` |
| `structural-math` | IS 456 pure math, new elements | `Python/structural_lib/codes/**` |
| `tester` | Tests, coverage, benchmarks | test files |
| `doc-master` | Docs, session logs, archives | `docs/**` |
| `ops` | Git, CI/CD, Docker | infrastructure |
| `governance` | Health metrics, maintenance | project-wide |

**Read + Terminal Agents (review, don't write):**
| Agent | Role |
|-------|------|
| `structural-engineer` | IS 456 compliance verification |
| `reviewer` | Code review, architecture validation |
| `library-expert` | Domain knowledge, professional standards |
| `security` | OWASP auditing, dependency scanning |

**Specialized Agents:**
| Agent | Role |
|-------|------|
| `ui-designer` | Visual design (design-only, no code) |
| `agent-evolver` | Meta-agent: scores agents, detects drift |
| `innovator` | Research & innovation, discovers gaps |

The key insight: **not every agent can edit files**. The structural-engineer can *verify* a shear formula but can't *change* flexure.py. The reviewer can *flag* a bug but can't *fix* it. This prevents accidental damage.

---

### 3. The Agent Registry

All 16 agents are defined in `agents/agent_registry.json`. Each entry looks like this:

```json
{
  "name": "backend",
  "description": "Python structural_lib core — IS 456 math, services, adapters.",
  "tools": ["search", "editFiles", "runInTerminal", "listFiles", "readFile"],
  "model": "Claude Sonnet 4.5",
  "permission_level": "WorkspaceWrite",
  "skills": ["api-discovery", "is456-verification"],
  "scripts": [
    "discover_api_signatures.py",
    "validate_imports.py",
    "check_architecture_boundaries.py",
    "migrate_python_module.py"
  ],
  "keywords": ["python", "structural", "beam", "flexure", "shear", ...],
  "handoff_targets": ["api-developer", "reviewer", "structural-engineer"],
  "can_edit_files": true,
  "file_scope": "Python/structural_lib/**"
}
```

The important fields:

- **`permission_level`** — One of `ReadOnly`, `ReadOnlyTerminal`, `WorkspaceWrite`, or `DangerFullAccess`. Controls what operations the agent can perform.
- **`skills`** — Which reusable skills the agent can invoke (like `/api-discovery`).
- **`keywords`** — Used by the prompt router to match tasks to agents.
- **`file_scope`** — A glob pattern limiting which files the agent can modify. `null` means read-only.
- **`handoff_targets`** — When this agent finishes its part, who does it hand off to?

---

### 4. The Prompt Router

When you say "fix the shear calculation in flexure.py", something needs to figure out *which agent* should handle it. That's `scripts/prompt_router.py`.

It works in three stages:

**Stage 1 — Priority Rules (pattern matching):**
```python
PRIORITY_RULES = [
    # (keywords_to_match, agent_name, weight_bonus)
    ({"react", "component", "hook", "tailwind"}, "frontend", 3.0),
    ({"fastapi", "router", "endpoint", "pydantic"}, "api-developer", 3.0),
    ({"is456", "clause", "formula", "flexure"}, "structural-math", 2.5),
    ({"beam", "column", "shear", "design"}, "structural-math", 2.0),
    ({"test", "coverage", "benchmark", "pytest"}, "tester", 3.0),
    ({"security", "owasp", "vulnerability"}, "security", 3.0),
    ({"git", "commit", "docker", "deploy"}, "ops", 3.0),
    ...
]
```

**Stage 2 — Combo Rules (multi-keyword boost):**
```python
COMBO_RULES = [
    ({"is456", "verify"}, "structural-engineer", 4.0),
    ({"is456", "implement"}, "structural-math", 4.0),
    ({"test", "write"}, "tester", 3.0),
    ({"verify", "compliance"}, "structural-engineer", 3.5),
    ...
]
```

**Stage 3 — Suppression Rules (reduce false matches):**
```python
SUPPRESSION_RULES = {
    "ui-designer": {"beam", "column", "slab", "structural"},
    "library-expert": {"implement", "code", "write", "create"},
}
```

Example: *"fix the shear calculation"* → tokenized to `{fix, shear, calculation}` → `shear` matches `structural-math` priority rule → result: **@structural-math** with confidence 0.85.

---

### 5. Agent Skills

Skills are reusable capabilities — like plugins any agent can invoke. We have 14:

| Skill | What It Does |
|-------|-------------|
| `/session-management` | Start/end session automation |
| `/api-discovery` | Look up exact function signatures |
| `/is456-verification` | Run IS 456 compliance tests |
| `/new-structural-element` | Guided workflow for column, slab, footing |
| `/react-validation` | Build, lint, type-check React app |
| `/architecture-check` | Validate 4-layer import boundaries |
| `/function-quality-pipeline` | 9-step quality gate for new functions |
| `/safe-file-ops` | Move/delete files preserving 870+ links |
| `/quality-gate` | Pre-merge quality checks |
| `/release-preflight` | Pre-release validation (5 phases) |
| `/agent-evolution` | Score agents, detect drift |
| `/development-rules` | 46 hard-learned rules by domain |
| `/innovation-research` | Guided research cycle |
| `/user-acceptance-test` | End-user perspective testing |

The difference between a skill and a script: a skill is a *documented workflow* with instructions, while a script is a *standalone program* that does one thing. Skills invoke scripts.

---

### 6. The 8-Step Pipeline

Every task in the project follows this pipeline:

```
PLAN → RESEARCH → GATHER → EXECUTE → TEST → VERIFY → DOCUMENT → COMMIT
```

- **PLAN** — What needs to change? Which IS 456 clause? Which files?
- **RESEARCH** — Read the code, check SP:16, understand the domain
- **GATHER** — Find existing code, check for duplicates, get API signatures
- **EXECUTE** — Write the code (only *now* do we touch files)
- **TEST** — Unit tests, golden benchmarks, degenerate cases
- **VERIFY** — Architecture boundaries, import validation, type check
- **DOCUMENT** — Update docs, API reference, CHANGELOG
- **COMMIT** — PR creation, CI, merge

This is tracked by `scripts/pipeline_state.py`. If an agent crashes mid-pipeline, the next session can resume from where it left off.

> **Why not just... code?** Because agents that skip PLAN and RESEARCH end up duplicating existing code, using wrong parameter names, and breaking architecture boundaries. The pipeline prevents that.

---

### 7. Permission Enforcement

`scripts/tool_permissions.py` is the bouncer at the door. It classifies every operation:

```python
READ_OPS  = {"read", "search", "list", "find", "check", "validate"}
WRITE_OPS = {"edit", "create", "modify", "write", "add", "update"}
DANGER_OPS = {"delete", "push", "merge", "force", "rm", "deploy"}
```

Then checks the agent's permission level:

| Permission Level | Can Read? | Can Write? | Can Delete/Push? |
|-----------------|-----------|------------|-----------------|
| `ReadOnly` | ✅ | ❌ | ❌ |
| `ReadOnlyTerminal` | ✅ | ❌ | ❌ |
| `WorkspaceWrite` | ✅ | ✅ | ❌ |
| `DangerFullAccess` | ✅ | ✅ | ✅ |

Example: If `reviewer` (ReadOnlyTerminal) tries to edit `flexure.py`, the check fails:
```
❌ Agent 'reviewer' (ReadOnlyTerminal) cannot perform 'edit' — requires WorkspaceWrite
```

Unknown operations default to `danger` — **fail-safe, not fail-open**.

---

### 8. Agent Evolution

Without feedback, agents repeat the same mistakes forever. The `agent-evolver` fixes this:

1. **Scoring** — `scripts/agent_scorer.py` rates each agent on task completion, error rate, and follow-through
2. **Drift Detection** — `scripts/agent_drift_detector.py` checks if agent instructions have drifted from actual behavior
3. **Instruction Evolution** — `scripts/agent_evolve_instructions.py` proposes updates to agent `.md` files

This runs every session via `./run.sh evolve --status` and weekly via `./run.sh evolve --review weekly`.

---

## 🏗️ Library Examples

### Reading the Agent Registry

```bash
# List all agents with their permissions
cat agents/agent_registry.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for a in data['agents']:
    print(f\"{a['name']:20s} {a['permission_level']:20s} scope={a.get('file_scope', 'none')}\")
"
```

### Routing a Task

```bash
# Route a natural language task to an agent
.venv/bin/python scripts/prompt_router.py "fix the shear calculation in flexure.py"
# → Agent: structural-math (confidence: 0.85)

.venv/bin/python scripts/prompt_router.py "add a FastAPI endpoint for column design"
# → Agent: api-developer (confidence: 0.90)

.venv/bin/python scripts/prompt_router.py "security audit of the authentication module"
# → Agent: security (confidence: 0.95)
```

### Checking Permissions

```bash
# Can the backend agent edit a core file?
.venv/bin/python scripts/tool_permissions.py check \
  --agent backend --op edit --path Python/structural_lib/api.py
# → ✅ Allowed

# Can the reviewer edit the same file?
.venv/bin/python scripts/tool_permissions.py check \
  --agent reviewer --op edit --path Python/structural_lib/api.py
# → ❌ Denied (ReadOnlyTerminal cannot edit)
```

---

## 🎯 Simple Examples

### Example 1: Tracing a Bug Fix Through the System

A user reports: *"The shear check returns wrong Vu for T-beams."*

1. **Prompt router** → `structural-math` (keywords: shear, check)
2. **Pipeline starts at PLAN** → identify the clause (IS 456 Cl 40.1)
3. **RESEARCH** → read `codes/is456/shear.py`, find the function
4. **GATHER** → `discover_api_signatures.py check_shear_is456` to get exact params
5. **EXECUTE** → `structural-math` fixes the math
6. **TEST** → `tester` writes regression test
7. **VERIFY** → `reviewer` checks the fix
8. **DOCUMENT** → `doc-master` updates docs
9. **COMMIT** → `ops` creates PR and merges

### Example 2: Handoff Chain

A new feature request: *"Add column biaxial bending check per IS 456 Cl 39.6."*

```
orchestrator → structural-engineer (verify clause interpretation)
            → structural-math (implement pure math)
            → tester (write tests + benchmarks)
            → backend (wire into services/api.py)
            → api-developer (create FastAPI endpoint)
            → frontend (add UI controls)
            → reviewer (code review)
            → doc-master (update docs)
            → ops (create PR, merge)
```

Each agent does *only* its part and hands off to the next.

---

## 🔧 Exercise

Given these task descriptions, determine which agent should handle each one:

1. *"The deflection formula uses wrong coefficient for cantilever beams"*
2. *"Add pagination to the beam list API endpoint"*
3. *"The 3D viewport crashes when rendering beams with zero width"*
4. *"Run security scan on all FastAPI endpoints"*
5. *"Archive stale planning docs older than 30 days"*
6. *"Write tests for the new column detailing function"*

**Bonus:** For task #1, list the full 8-step pipeline and which agent handles each step.

<details>
<summary>Answers</summary>

1. **structural-math** — formula fix in IS 456 code layer
2. **api-developer** — FastAPI endpoint modification
3. **frontend** — React/R3F 3D visualization bug
4. **security** — security audit task
5. **governance** or **doc-master** — doc maintenance
6. **tester** — test creation

**Bonus (Task #1):**
- PLAN: orchestrator identifies scope
- RESEARCH: structural-engineer verifies the correct coefficient
- GATHER: structural-math reads deflection.py, checks existing tests
- EXECUTE: structural-math fixes the formula
- TEST: tester writes regression tests
- VERIFY: reviewer + structural-engineer check
- DOCUMENT: doc-master updates reference
- COMMIT: ops creates PR

</details>

---

## 💬 Can You Explain?

Test yourself — can you answer these in one sentence each?

1. Why does the reviewer agent have ReadOnly permission instead of WorkspaceWrite?
2. What's the difference between a "skill" and a "script" in this system?
3. Why does `tool_permissions.py` default unknown operations to "danger"?
4. What problem does the 8-step pipeline solve that "just coding" doesn't?
5. Why does the prompt router have suppression rules?

---

## 📎 References

- [Agent registry](../../../agents/agent_registry.json) — all 16 agents defined
- [Prompt router](../../../scripts/prompt_router.py) — NLP-based task routing
- [Tool permissions](../../../scripts/tool_permissions.py) — programmatic access control
- [Pipeline state](../../../scripts/pipeline_state.py) — resumable task pipeline
- [Copilot agents guide](../../guides/copilot-agents-usage-guide.md) — how to use agents in VS Code
- [Agent bootstrap](../../getting-started/agent-bootstrap.md) — full setup guide