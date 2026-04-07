# GitHub Copilot Agents & Automation

**Type:** Reference
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-04-07
**Last Updated:** 2026-04-08

---

## Current State (Monorepo)

- **16 Agents** — orchestrator, frontend, backend, structural-math, api-developer, ui-designer, agent-evolver, structural-engineer, reviewer, tester, doc-master, ops, governance, security, library-expert, innovator
- **14 Skills** — session-management, safe-file-ops, api-discovery, is456-verification, new-structural-element, react-validation, architecture-check, function-quality-pipeline, innovation-research, agent-evolution, development-rules, quality-gate, release-preflight, user-acceptance-test
- **16 Prompts** — new-feature, bug-fix, code-review, add-api-endpoint, add-is456-clause, add-structural-element, function-quality-gate, fix-test-failure, performance-optimization, session-start, session-end, file-move, is456-verify, context-recovery, master-workflow, innovation-research

**Assessment:** This is overkill for focused repos. Research shows 3–5 agents for a library, 5–7 for an app.

### Why 4 Agents, Not 16

The current monorepo has 16 agents because it covers Python math, FastAPI, React, Docker, CI/CD, docs, governance, and agent meta-evolution. The library repo only needs:

| Concern | Monorepo Agent | Library Equivalent |
|---------|---------------|-------------------|
| Writing IS 456 math | backend, structural-math | **coder** (combined) |
| Code review + IS 456 compliance | reviewer, structural-engineer | **reviewer** (combined) |
| Test writing + benchmarks | tester | **tester** |
| Formula verification + SP:16 | library-expert | **math-verifier** |
| Frontend (React) | frontend, ui-designer | N/A — no frontend |
| API (FastAPI) | api-developer | N/A — no API |
| DevOps (Docker, CI) | ops | Handled by CI config |
| Documentation | doc-master | README + mkdocs (coder handles it) |
| Security | security | Ruff `S` rules + Dependabot |
| Meta-agents | orchestrator, governance, innovator, agent-evolver | N/A — overhead not justified |

**Rule of thumb:** One agent per distinct *permission boundary*. Library has only 2 permission levels (edit and read-only), so 4 agents is optimal.

The current monorepo has 16 agents, which caused:
- Coordination overhead between agents
- Drift and repeated mistakes across sessions
- 70+ audit findings in v0.21.0–v0.21.3

Research findings:
- **Top libraries (pytest, pydantic, httpx)** use minimal or zero AI agent infrastructure
- **claw-code harness** pattern: few agents with clear tool boundaries are more effective
- **@innovator analysis** recommended 3 agents, but @reviewer validated that **4 is correct** — the math-verifier agent serves a unique safety-critical role (IS 456 clause verification, SP:16 benchmarks)
- **Reduction:** 16 → 4 for library, 16 → 5-6 for app

---

## Library Repo Agents (4 agents)

### 1. coder.agent.md

**Role:** Main implementation — writes IS 456 math, core types, API functions
**Tools:** editFiles, runInTerminal, search
**Permission:** WorkspaceWrite

**Rules:**
- Always explicit units (mm, N/mm², kN, kNm) in parameter names
- No I/O in math modules — pure functions only
- Test every function before commit
- Return typed models, never raw dicts
- Follow src/ layout conventions
- Run `ruff check` + `mypy --strict` before handoff

**Handoff:** → reviewer after implementation

### 2. reviewer.agent.md

**Role:** Code review, architecture validation, IS 456 compliance
**Tools:** search, readFile (**NO edit tools — read-only**)
**Permission:** ReadOnly

**Rules:**
- Check SP:16 benchmarks for accuracy
- Verify units are explicit in all params
- Validate return types are typed models
- Check import direction (no upward imports)
- Verify clause references in docstrings
- Flag any I/O in math modules

**Handoff:** → tester for test creation

### 3. tester.agent.md

**Role:** Test writing, coverage analysis, benchmark validation
**Tools:** editFiles, runInTerminal, search
**Permission:** WorkspaceWrite

**Rules:**
- 6 test types for every IS 456 function (unit, edge, degenerate, SP:16, textbook, Hypothesis)
- SP:16 benchmarks must achieve ±0.1% accuracy
- `xfail_strict = true` — a passing xfail is a bug
- 95%+ branch coverage required
- Use `pytest-benchmark` for performance regression

**Handoff:** → coder for fixes if tests fail

### 4. math-verifier.agent.md

**Role:** IS 456 formula verification, SP:16 benchmark checking
**Tools:** search, readFile, web (for IS 456 reference lookup)
**Permission:** ReadOnly

**Rules:**
- Verify every formula against IS 456:2000 clause text
- Check numerical accuracy against SP:16 Charts 1–62
- Cross-reference with Pillai & Menon, Varghese textbooks
- Flag any deviation > 0.1% from published values
- Maintain clause traceability

---

### Claw-Code Patterns Adopted

From our analysis of the claw-code harness (114K stars):

1. **Tool permission context per agent** — Each agent gets only the tools it needs (coder: editFiles+terminal, reviewer: search+readFile only, etc.)
2. **Trust-gated initialization** — Agent reads its full .agent.md before any task execution
3. **Session persistence** — JSON state in logs/ for resumable work across conversations
4. **Pre/post hooks** — Pre-commit validation, post-commit CI check, pre-route permission check

### copilot-instructions.md Template (~50 lines)

```markdown
# rcdesign — IS 456 RC Design Library

Pure Python IS 456:2000 structural design calculations.
4 agents: coder, reviewer, tester, math-verifier.

## Git
Always use `./scripts/commit.sh "type: message"`. Never manual git.

## Architecture
src/rcdesign/: beam/, column/, footing/, slab/, common/, core/
tests/: unit/, benchmarks/, hypothesis/
Code modules: codes/is456/ → pure math, NO I/O, explicit units

## Before Coding
- Search existing code first (duplication = #1 mistake)
- Run `uv run python -c "import rcdesign; print(dir(rcdesign))"` to check API
- Read the relevant .agent.md file completely

## Testing
- 6 types: unit, edge, degenerate, SP:16 (±0.1%), textbook, Hypothesis
- Coverage: 95% branch minimum
- `uv run pytest --strict-markers --strict-config`

## Key Rules
- fck (not fck_mpa) — IS 456 standard symbols, units in docstrings
- b_mm, d_mm, Mu_kNm — dimensions get unit suffixes
- Every function cites IS 456 clause in docstring
- Return typed models, never raw dicts
```

---

## Library Repo Skills (2 skills)

### test-pipeline (SKILL.md)

Run full test pipeline: unit → SP:16 benchmarks → Hypothesis property tests → coverage report

```bash
# Usage: /test-pipeline
pytest tests/ -v                          # Unit + edge + degenerate
pytest tests/ -m benchmark -v             # SP:16 benchmarks
pytest tests/ -m hypothesis -v            # Property-based tests
pytest tests/ --cov=rcdesign --cov-report=term-missing  # Coverage
```

### is456-verify (SKILL.md)

Verify IS 456 compliance: formula check → benchmark comparison → code audit

```bash
# Usage: /is456-verify <function_name>
# Steps:
# 1. Find function source and extract formula
# 2. Compare against IS 456:2000 clause text
# 3. Run SP:16 benchmark for that function
# 4. Check edge cases (zero input, max reinforcement, min section)
# 5. Report accuracy and any deviations
```

---

## Library Repo Prompts (4 prompts)

### new-feature.prompt.md

Workflow: identify IS 456 clause → implement math → write 6 test types → verify SP:16 → review

### fix-bug.prompt.md

Workflow: reproduce → root cause → fix → regression test → verify SP:16 accuracy unchanged

### add-clause.prompt.md

Workflow: read IS 456 section → extract formula → implement pure function → 6 test types → SP:16 verify → docstring with clause reference

### release.prompt.md

Workflow: version bump → changelog → CI pass → TestPyPI publish → verify install → PyPI publish

---

## Library Repo Instructions (3 files)

### python.instructions.md (applyTo: '\*\*/\*.py')

- src/ layout with hatchling
- Dimensions use unit suffixes (`b_mm`, `d_mm`, `Mu_kNm`)
- Material properties use IS 456 standard symbols (`fck`, `fy`) — units documented in docstrings
- No I/O in math modules — pure functions only
- Return typed models, never raw dicts
- Pattern: `verb_element_specific()`
- Ban relative imports (`ban-relative-imports = "all"`)
- Every function: docstring with Args, Returns, Raises, IS 456 Reference, Example

### tests.instructions.md (applyTo: 'tests/\*\*')

- pytest strict markers
- SP:16 benchmarks ±0.1% accuracy
- Hypothesis property-based testing for invariants
- `xfail_strict = true` — failing expected-fail = real bug
- 95%+ branch coverage
- Use fixtures from `conftest.py` for standard sections

### docs.instructions.md (applyTo: 'docs/\*\*')

- MkDocs Material format
- API docs auto-generated from docstrings via mkdocstrings
- Every function has a usage example
- Theory pages for derivations and assumptions
- Verification pages with benchmark results

---

## App Repo Agents (6 agents)

> **Note:** Consider merging `api` into `backend` (5 agents instead of 6)

### 1. backend.agent.md

**Role:** FastAPI services, adapters, business logic (NOT IS 456 math)
**Tools:** editFiles, runInTerminal, search
**Rules:** Import from `rcdesign` — never reimplement math. Services layer only.
**Handoff:** → reviewer after implementation

### 2. frontend.agent.md

**Role:** React 19, R3F 3D visualization, Tailwind CSS
**Tools:** editFiles, runInTerminal, search
**Rules:** Tailwind only (no CSS files). All data flows through FastAPI. Reuse existing hooks.
**Handoff:** → reviewer after implementation

### 3. api.agent.md

**Role:** FastAPI router design, OpenAPI schema, request/response models
**Tools:** editFiles, runInTerminal, search
**Rules:** Check existing routes before adding. Never duplicate endpoints. Consistent naming.
**Handoff:** → tester for endpoint tests

### 4. reviewer.agent.md

**Role:** Code review for both backend and frontend
**Tools:** search, readFile (read-only)
**Rules:** Verify app doesn't reimplement library math. Check API consistency.
**Handoff:** → devops for deployment

### 5. tester.agent.md

**Role:** Backend (pytest + httpx) and frontend (vitest) test writing
**Tools:** editFiles, runInTerminal, search
**Rules:** Integration tests for API endpoints. Component tests for React.
**Handoff:** → reviewer for test review

### 6. devops.agent.md

**Role:** Docker, CI/CD, deployment, infrastructure
**Tools:** editFiles, runInTerminal, search
**Rules:** Colima for Docker on Mac. Multi-stage builds. Health checks in compose.
**Handoff:** → none (terminal agent)

---

## Handoff Chains

### Library Repo
```
coder → reviewer → tester → coder (if fixes needed)
```

### App Repo
```
backend/frontend → api (if new endpoint) → tester → reviewer → devops
```

---

## Automation Scripts for Library Repo

| Script | Purpose |
|--------|---------|
| `scripts/verify_sp16.py` | Run SP:16 benchmark suite against Charts 1–62 |
| `scripts/check_coverage.py` | Verify 95%+ branch coverage |
| `scripts/check_types.py` | Run `mypy --strict` + `pyright` |
| `scripts/release.py` | Automated release: bump version → changelog → build → publish |
| `scripts/verify_install.py` | Install from TestPyPI and run smoke tests |

---

## Historical Mistakes to Avoid (Knowledge Base)

From the current monorepo's 70+ audit findings — encode these into agent instructions:

1. **Never guess API parameter names** — always check signatures first
2. **Never bypass CI** with `--force` or `--no-verify` — caused 10+ hours rework
3. **Never duplicate existing hooks/functions** — search before coding (#1 agent mistake)
4. **Never mix IS 456 math with I/O code** — violates architecture
5. **Always use explicit units** (`b_mm` not `width`, `fck` not `concrete_grade`)
6. **Always run full test suite** before commit
7. **Never manual git** — always use the commit script
8. **Search before coding** — duplication is the #1 agent mistake
