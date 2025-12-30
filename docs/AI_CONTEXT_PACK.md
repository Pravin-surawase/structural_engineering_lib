# AI Context Pack

> **For AI Agents:** Use this as your single entrypoint when working in VS Code.

| Metric | Value |
|--------|-------|
| **Current Release** | v0.12.0 (on PyPI) |
| **Next Planned Release** | v0.12.1 (test hardening + verification gates) |
| **Next Milestone** | v0.20.0 (blocked by S-007) |
| **Tests** | 1956 passed, 91 skipped |
| **Coverage** | 92% branch |
| **Visual v0.11** | V03–V09 delivered (critical set, report HTML, batch packaging, golden tests) |

> **Status details:** See [TASKS.md](TASKS.md) for current/next release info.

---

## 🎯 Golden Rules

1. **Small, deterministic changes** — no hidden defaults
2. **Python + VBA parity** — same formulas, units, edge-case behavior
3. **Update docs with code** — in the same PR

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
# Pre-commit hooks auto-format
git commit -m "message"

# Create PR and wait for CI
gh pr create --title "..." --body "..."
gh pr checks <num> --watch

# Merge only after CI passes
gh pr merge <num> --squash --delete-branch
```

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
