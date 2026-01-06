# AI Context Pack

> **For AI Agents:** Use this as your single entrypoint when working in VS Code.

| Metric | Value |
|--------|-------|
| **Current Release** | v0.14.0 (on PyPI, 2026-01-06) |
| **Next Planned Release** | v0.15.0 (smart insights ecosystem) |
| **Tests** | 2231+ passed, 0 skipped (as of 2026-01-06) |
| **Coverage** | 86% overall, 100% on 10 modules |
| **Recent Features** | SmartDesigner, comparison module, cost optimization, design suggestions |

> **Status details:** See [TASKS.md](TASKS.md) and [next-session-brief.md](planning/next-session-brief.md).

---

## ⚠️ BEFORE ANYTHING ELSE: Git Workflow

**NEVER use manual git commands! Use the automation scripts:**

```bash
./scripts/ai_commit.sh "commit message"
```

**DO NOT use:** `git add`, `git commit`, `git push`, `git pull` manually!

Canonical workflow: `docs/GIT_WORKFLOW_AI_AGENTS.md`
See [.github/copilot-instructions.md](../.github/copilot-instructions.md) for full rules.

---

## 🎯 Golden Rules

1. **Small, deterministic changes** — no hidden defaults
2. **Python + VBA parity** — same formulas, units, edge-case behavior
3. **Update docs with code** — in the same PR
4. **Git workflow:** ALWAYS use `./scripts/ai_commit.sh`

---

## 📖 Required Reading

Load these docs first for most tasks:

| Priority | Document | Purpose |
|----------|----------|---------|
| 1 | `.github/copilot-instructions.md` | **CRITICAL** — rules, layers, Git workflow |
| 2 | `docs/architecture/project-overview.md` | Architecture + intent |
| 3 | `docs/reference/api.md` | Public API contracts |
| 4 | `docs/reference/known-pitfalls.md` | Units, tables, edge cases |
| 5 | `docs/TASKS.md` | Current task board |
| 6 | `docs/planning/next-session-brief.md` | Where to resume |

---

## 🏗️ Project Structure

```
Python/structural_lib/     ← Python package
Python/tests/              ← Python tests
VBA/Modules/               ← VBA library modules
VBA/Tests/                 ← VBA test harness
docs/                      ← Documentation
scripts/                   ← Automation scripts
```

### Layer Architecture

| Layer | Python Files | Purpose |
|-------|-------------|---------|
| **Core** | `flexure.py`, `shear.py`, `detailing.py` | Pure math, no I/O |
| **App** | `api.py`, `beam_pipeline.py`, `job_runner.py` | Orchestration |
| **I/O** | `__main__.py`, `dxf_export.py` | CLI, file handling |

---

## ⚙️ Development Workflow

### Python
```bash
# Run tests
.venv/bin/python -m pytest tests/ -v

# Format
.venv/bin/python -m black Python/

# Check
.venv/bin/python -m ruff check Python/
```

### VBA
- Import order matters — see `docs/contributing/vba-guide.md`
- Mac safety: wrap dimension multiplications in `CDbl()`

### Git
```bash
# Decide PR vs direct
./scripts/should_use_pr.sh --explain

# Direct commit (docs-only)
./scripts/ai_commit.sh "docs: update guide"

# PR workflow
./scripts/create_task_pr.sh TASK-XXX "description"
./scripts/ai_commit.sh "feat: implement X"
./scripts/finish_task_pr.sh TASK-XXX "description"
```

---

## 🤖 Automation Scripts (42 Total)

**Before implementing manually, check if a script exists!**

### Key Scripts by Category

**Session Management (3):**
- `start_session.py` — Initialize agent (run first every session)
- `end_session.py` — Validate handoff before ending
- `update_handoff.py` — Auto-update handoff docs

**Git Workflow (10):** ⭐ CRITICAL
- `ai_commit.sh` — Primary entrypoint (enforces PR rules)
- `safe_push.sh` — Low-level commit/push workflow
- `should_use_pr.sh` — Decision helper (PR vs direct commit)
- `recover_git_state.sh` — Recovery helper (prints exact fix)
- `verify_git_fix.sh` — Validate whitespace fix (CI)
- `test_should_use_pr.sh` — Workflow decision tests (13 scenarios)
- `create_task_pr.sh` — Create PR for task
- `finish_task_pr.sh` — Complete and merge PR

**Documentation Quality (8):**
- `check_links.py` — Broken link detection
- `check_doc_versions.py` — Version drift detection
- `check_api_docs_sync.py` — API doc synchronization
- `check_cli_reference.py` — CLI doc completeness

**Release Management (4):**
- `release.py` — One-command release helper
- `bump_version.py` — Version bumping
- `verify_release.py` — Post-release validation
- `check_pre_release_checklist.py` — Release checklist

**Testing & Quality (5):**
- `ci_local.sh` — Local CI simulation (~2-3 min)
- `quick_check.sh` — Fast pre-commit checks (~30 sec)
- `check_tasks_format.py` — TASKS.md validation
- `check_session_docs.py` — Session doc consistency

**Code Quality (4):**
- `audit_error_handling.py` — Error handling compliance
- `lint_vba.py` — VBA linting
- `update_test_stats.py` — Test coverage tracking

**Specialized (8):**
- `dxf_render.py` — DXF visualization
- `external_cli_test.py` — CLI testing (S-007)
- More in full catalog...

**📚 Full Catalog:** [automation-catalog.md](reference/automation-catalog.md) — Complete reference with usage, examples, when-to-use guidance for all 41 scripts.

---

## 🤖 Agent Roles

| Role | Use For |
|------|---------|
| **DEV** | Implementation, refactoring |
| **TESTER** | Test design, edge cases |
| **DOCS** | API docs, guides |
| **DEVOPS** | CI, releases, automation |

Full list: `agents/README.md`

---

## 📋 Prompt Recipes

### Implement a feature
```
Use PROJECT_OVERVIEW and API_REFERENCE as context.
Act as DEV + TESTER.
Implement TASK-XXX in Python and VBA with identical behavior.
Add Python tests. Output should be deterministic.
```

### Debug a mismatch
```
Use KNOWN_PITFALLS + TROUBLESHOOTING.
Act as TESTER.
Create minimal repro, identify divergence point,
propose smallest parity fix with tests.
```

### Update docs
```
Act as DOCS.
Update API_REFERENCE examples and impacted guides.
Keep wording precise; no claims about untested tooling.
```

---

## 📚 Additional Resources

| Category | Document |
|----------|----------|
| Research | `docs/planning/research-ai-enhancements.md` |
| Releases | `docs/RELEASES.md` |
| ADRs | `docs/adr/README.md` |
| Archive | `docs/_archive/` |
| Handoff | `docs/HANDOFF.md` |

---

## ⚠️ Common Mistakes

| Mistake | Correct |
|---------|---------|
| Running `python` directly | Use `.venv/bin/python` |
| Merging before CI passes | Wait for `gh pr checks --watch` |
| Multiple micro-PRs | Batch related changes |
| Editing without reading | Check file content first |

---

*Last updated: 2025-12-29*
