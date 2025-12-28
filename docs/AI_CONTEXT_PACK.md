# AI Context Pack (VS Code “Vibe Coding”)

Use this file as the single entrypoint for AI agents working in VS Code.

**Current version:** v0.10.3
**Test count:** See CI for current totals

## 0) Golden rule
- Prefer small, deterministic changes.
- Keep Python + VBA parity (same formulas, same units, same edge-case behavior).
- Update docs *in the same change* when behavior/API changes.

---

## 1) What this repo is
- IS 456 RC beam design library.
- Implementations: Python package under `Python/` + VBA modules under `VBA/`.
- Strength design + detailing + DXF export + serviceability + compliance + BBS done (v0.8+).
- **v0.9.4 adds:** Unified CLI (`python -m structural_lib`), cutting-stock optimizer, VBA BBS/Compliance parity.

Start here for architecture and boundaries:
- [architecture/project-overview.md](architecture/project-overview.md)

---

## 2) "Load these docs first" (minimal context)
Use these as the default context set for most tasks:
- [architecture/project-overview.md](architecture/project-overview.md) (layering + intent)
- [reference/api.md](reference/api.md) (public API contracts)
- [reference/known-pitfalls.md](reference/known-pitfalls.md) (units/table rules/edge cases)
- [reference/troubleshooting.md](reference/troubleshooting.md) (VBA/Mac quirks, fixes)
- [TASKS.md](TASKS.md) (canonical backlog + acceptance mindset)
- [planning/next-session-brief.md](planning/next-session-brief.md) (where to resume quickly)

---

## 3) When you’re implementing code
### Python
- Package root: `Python/structural_lib/`
- Tests: `Python/tests/`

Recommended workflow:
1) Add/modify function in Python.
2) Add/modify the matching VBA module function.
3) Add/extend Python unit tests.
4) (If feasible) add/update VBA test harness cases.

### VBA
- Library modules: `VBA/Modules/`
- VBA tests: `VBA/Tests/`

Import order matters; see:
- [contributing/vba-guide.md](contributing/vba-guide.md)

---

## 4) Planning & research (what to read)
- Active v0.8+ research log: [planning/research-ai-enhancements.md](planning/research-ai-enhancements.md)
- Production checklist summary: [planning/production-roadmap.md](planning/production-roadmap.md)
- Release ledger (append-only): [RELEASES.md](RELEASES.md)

Architecture decisions (short, auditable decision notes):
- [adr/README.md](adr/README.md)

Historical reference material lives here:
- [docs/_archive/RESEARCH_AND_FINDINGS.md](_archive/RESEARCH_AND_FINDINGS.md)

---

## 5) Git & CI Rules (CRITICAL for all agents)

**Read `.github/copilot-instructions.md` for complete rules. Summary:**

### Before committing:
- Pre-commit hooks auto-run `black` + `ruff` — install with `pre-commit install`
- If hooks modify files, re-stage them before committing
- Run tests locally: `.venv/bin/python -m pytest tests/test_<file>.py -v`

### PR workflow:
1. `git commit` → `git push` → `gh pr create`
2. **WAIT:** `gh pr checks <num> --watch` (don't merge until CI passes!)
3. If governance allows: `gh pr merge <num> --squash --delete-branch`
4. If human review required: stop and notify the user

### When to merge:
- ✅ After: features, meaningful tests, doc sections
- ❌ NOT for: single-line fixes, formatting, micro-changes (batch them)

### Common mistakes to avoid:
- Don't run `python` directly — use full venv path
- Don't try to merge before CI completes
- Don't create multiple micro-PRs — batch related changes

---

## 6) Agent roles (prompt building blocks)
Role prompt templates live here:
- [../agents/README.md](../agents/README.md)

Internal governance docs (rarely needed during normal coding):
- [docs/_internal/AGENT_WORKFLOW.md](_internal/AGENT_WORKFLOW.md)
- [docs/_internal/GIT_GOVERNANCE.md](_internal/GIT_GOVERNANCE.md)

---

## 7) Copy-paste prompt recipes
### Implement a feature (Python + VBA parity)
"Use PROJECT_OVERVIEW and API_REFERENCE as context. Act as DEV + TESTER. Implement TASK-XXX in Python and VBA with identical behavior and units. Add Python tests. Where VBA tests are practical, add at least one regression case. Output should be deterministic and auditable."

### Debug a mismatch (Python vs VBA)
"Use KNOWN_PITFALLS + TROUBLESHOOTING. Act as TESTER. Create a minimal repro input set, identify the first divergence point, then propose the smallest parity fix with tests."

### Update docs after code change
"Act as DOCS. Update API_REFERENCE examples and any impacted guides. Keep wording precise; no claims about tooling you didn’t run."
