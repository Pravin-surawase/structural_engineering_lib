# Copilot Instructions — structural_engineering_lib

> **FOR AI AGENTS:** This file is loaded by GitHub Copilot/VS Code when the
> `.github/copilot-instructions.md` convention is enabled in your environment.
> These rules are MANDATORY. Following them prevents wasted time on CI failures,
> merge conflicts, and repeated mistakes. Read carefully before any action.

---

## 🚀 Quick Start (First 30 Seconds)

```bash
# Run this immediately:
.venv/bin/python scripts/start_session.py
```

This shows version, branch, active tasks, blockers, and doc freshness.

**Read next:** `docs/AGENT_BOOTSTRAP.md` → `docs/AI_CONTEXT_PACK.md` → `docs/TASKS.md`

---

## What this project is
IS 456 RC beam design library with **Python + VBA parity**.

## Non-negotiables
- Deterministic calculations (no hidden defaults).
- Units must be explicit and consistent.
- Keep Python/VBA behavior aligned.
- Prefer minimal, surgical changes.

## Always load this context first
- docs/AI_CONTEXT_PACK.md
- docs/architecture/project-overview.md
- docs/reference/api.md
- docs/reference/known-pitfalls.md
- docs/TASKS.md

## Coding rules
- Don’t mix UI/I-O code into core calculation modules.
- Add/extend tests with every behavior change (Python at minimum).
- If you move files, keep redirect stubs to avoid breaking links.- Format Python code with `black` before committing.
## Definition of done
- Tests pass (at least Python).
- Docs updated where contracts/examples changed.
- No unrelated refactors.
- Code formatted with `black` (run `python -m black .` in Python/ directory).

---

## Git workflow rules (CRITICAL)

### Before committing Python code:
1. Pre-commit hooks are installed — they auto-run black/ruff on `git commit`
2. If not installed: `pre-commit install` (one-time setup)
3. Run tests locally before pushing: `python -m pytest tests/test_<file>.py -v`

### PR and merge workflow:
1. `git commit` — pre-commit hooks auto-format (may modify files; re-stage and amend if needed)
2. `git push -u origin <branch>`
3. `gh pr create --title "..." --body "..."`
4. **WAIT for CI:** `gh pr checks <num> --watch` — do NOT try to merge immediately
5. Only after all checks pass: `gh pr merge <num> --squash --delete-branch`

> **Note:** Merge authority depends on project governance. If branch protection
> requires human review, stop at step 4 and notify the user.

### When pre-commit modifies files:
If pre-commit hooks fix files during commit, do NOT create a second commit:
```bash
git add -A && git commit --amend --no-edit   # Keep it atomic
```

### After merging a PR (sync local main):
```bash
# PREFERRED: safe, non-destructive
git switch main && git pull --ff-only

# AVOID: git reset --hard origin/main (destructive, can wipe local work)
# Only use reset --hard when git status is clean AND you intend to discard changes
```

### When to merge (batch small changes):
- ✅ Merge after: completing features, meaningful test additions, doc section completions
- ❌ Don't merge for: single-line fixes, formatting-only, every tiny change
- Batch related small changes into one PR instead of many micro-PRs

---

## Layer architecture (always respect)

| Layer | Python | VBA | Rules |
|-------|--------|-----|-------|
| **Core** | `flexure.py`, `shear.py`, `detailing.py`, `serviceability.py`, `compliance.py`, `tables.py`, `ductile.py`, `materials.py`, `constants.py`, `types.py`, `utilities.py` | `M01-M07, M15-M17` | Pure functions, no I/O, explicit units |
| **Application** | `api.py`, `job_runner.py`, `bbs.py`, `rebar_optimizer.py` | `M08_API` | Orchestrates core, no formatting |
| **UI/I-O** | `excel_integration.py`, `dxf_export.py`, `job_cli.py` | `M09_UDFs`, macros | Reads/writes external data |

## Units convention
- **Inputs:** mm, N/mm², kN, kN·m
- **Internal:** mm, N, N·mm (convert at layer boundaries)
- **Outputs:** mm, N/mm², kN, kN·m

## Mac VBA safety (critical for VBA changes)
- Wrap dimension multiplications in `CDbl()`: `CDbl(b) * CDbl(d)`
- Never pass inline boolean expressions to `ByVal` args — use local variable first
- No `Debug.Print` interleaved with floating-point math
- Prefer `Long` over `Integer`

## Testing requirements
- Each calculation function needs unit tests
- Include edge cases: min/max values, boundary conditions
- Tolerance: ±0.1% for areas, ±1mm for dimensions
- Document source for expected values (SP:16, textbook, hand calc)

## Role context (see agents/*.md for full details)
When working on specific task types, apply these focuses:
- **Implementation:** Layer-aware, clause refs in comments, Mac-safe
- **Testing:** Benchmark sources, edge cases, tolerance specs
- **Integration:** Schema validation, unit mapping, error surfacing
- **Docs:** API examples, units documented, changelog entries
---

## Terminal and command rules (CRITICAL)

### Python environment:
- **Always use full venv path:** `"/path/to/.venv/bin/python"` not just `python`
- Run `configure_python_environment` first if `python` command fails
- The venv is at: `.venv/bin/python` relative to project root

### Running tests locally:
```bash
# ALWAYS run tests locally before pushing new test files
.venv/bin/python -m pytest tests/test_<file>.py -v

# Check formatting/linting locally before commit
.venv/bin/python -m black <file>
.venv/bin/python -m ruff check <file>
```

### gh CLI commands:
- `gh pr checks <num>` may show "no checks" if CI hasn't started — wait 5-10 seconds
- If `gh pr merge` fails with "not mergeable", CI is still running — use `gh pr checks <num> --watch`
- Network timeouts happen — retry the command once before investigating

### Git sync issues:
- If push is rejected (non-fast-forward), the auto-format workflow may have pushed
- Solution: `git pull --rebase origin <branch>` then push again
- If unstaged changes block pull: `git stash && git pull --rebase && git stash pop`

---

## Common mistakes to AVOID

| Mistake | Correct Approach |
|---------|------------------|
| Creating Python file → commit → CI fails on black | Create → run black locally → commit (or rely on pre-commit hooks) |
| `gh pr create` → immediately `gh pr merge` | Create → `gh pr checks --watch` → wait → merge |
| Running `python` directly | Use full venv path or configure environment first |
| Multiple micro-PRs for tiny changes | Batch related changes into one PR |
| Reading a file already shown in context | Use the context provided, don't re-read |
| Running dependent commands in parallel | Run sequentially, check output between |
| Editing file without reading current content | Always read file first if there may be changes |
| Unused variables in test code | Check with `ruff check` before commit |
| Creating duplicate documentation | Check if doc exists first |
| Committing unrelated staged files | Run `git status` before commit; stage only intended files |
| Resolving merge conflicts + feature in one commit | Resolve conflicts in separate commit first, then add feature |
| PR title/description doesn't match actual changes | List ALL changed files in PR body; update title if scope changes |
| Pre-commit modifies files → new commit | Use `git add -A && git commit --amend --no-edit` instead |
| Using `git reset --hard` without checking status | Use `git switch main && git pull --ff-only` after merge |
| Claiming "focused commit" but batching unrelated changes | Either truly separate, or be honest about batching scope |

---

## Session workflow (CRITICAL)

### Starting a session:
```bash
# Run at the beginning of each session:
.venv/bin/python scripts/start_session.py

# Quick mode (skip test count check):
.venv/bin/python scripts/start_session.py --quick
```

**What it does:**
- Shows version, branch, uncommitted changes
- Adds SESSION_LOG entry for today if missing
- Shows Active tasks from TASKS.md
- Runs doc freshness checks

### Ending a session:
```bash
# Run before ending any session:
.venv/bin/python scripts/end_session.py

# Auto-fix issues:
.venv/bin/python scripts/end_session.py --fix

# Quick mode:
.venv/bin/python scripts/end_session.py --quick
```

**What it checks:**
- 📁 Uncommitted changes
- 🔍 Handoff checks (date freshness, test counts, versions)
- 📝 SESSION_LOG entry completeness
- 🔗 Doc link validity
- 📊 Today's activity summary

### Manual handoff steps (if needed):
1. Update `docs/planning/next-session-brief.md` with session summary
2. Ensure TASKS.md reflects current state
3. Commit any uncommitted doc changes

---

## Efficiency rules

1. **Don't re-read files in context** — If file content is shown, use it
2. **Batch file edits** — Use multi_replace for multiple edits in same/different files
3. **Check command exit codes** — Before proceeding, verify command succeeded
4. **One terminal command at a time** — Don't run parallel terminal commands
5. **Verify before declaring success** — Run tests, check output, confirm behavior
6. **Read this file first** — Before starting any session, review these rules completely
