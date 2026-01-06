# Learning Paths for Contributors

Pick the smallest reading path that still protects quality. Each path lists the minimum docs to read before you work.

## Quick selector

| Task type | Path | Read first |
| --- | --- | --- |
| Docs-only change | Beginner | `../../.github/copilot-instructions.md`, `../GIT_WORKFLOW_AI_AGENTS.md` |
| Small bug fix in existing module | Beginner | `../AI_CONTEXT_PACK.md`, `../reference/known-pitfalls.md` |
| New feature in existing domain | Intermediate | `../architecture/project-overview.md`, `testing-strategy.md` |
| Refactor or API change | Advanced | `../reference/api.md`, `../architecture/deep-project-map.md` |
| VBA or Excel change | Intermediate | `vba-guide.md`, `excel-addin-guide.md` |
| Release or CI change | Advanced | `solo-maintainer-operating-system.md`, `../_internal/GIT_GOVERNANCE.md` |

## Path A: Beginner (docs-only or tiny fix)

Read in order:
1. `../../.github/copilot-instructions.md`
2. `../AGENT_BOOTSTRAP.md`
3. `../GIT_WORKFLOW_AI_AGENTS.md`
4. `../reference/known-pitfalls.md`

Use this path for:
- Typo fixes, link repairs, small README updates
- One-line code fixes with no behavior change

Checks to run:
- `./scripts/should_use_pr.sh --explain`
- `./scripts/ai_commit.sh "docs: ..."` or PR workflow if required

## Path B: Intermediate (feature work in existing modules)

Read in order:
1. `../AI_CONTEXT_PACK.md`
2. `../architecture/project-overview.md`
3. `testing-strategy.md`
4. `../reference/api.md`

Use this path for:
- New behavior inside existing modules
- New CLI flags that do not change existing outputs
- VBA or Excel work (add `vba-guide.md`, `excel-addin-guide.md`)

Checks to run:
- `./scripts/should_use_pr.sh --explain`
- `./scripts/quick_check.sh` (for code changes)

## Path C: Advanced (refactor, API, or release)

Read in order:
1. `../architecture/deep-project-map.md`
2. `../reference/api.md`
3. `solo-maintainer-operating-system.md`
4. `../_internal/GIT_GOVERNANCE.md`
5. `../reference/known-pitfalls.md`

Use this path for:
- Refactors across modules or layers
- API surface changes or deprecations
- CI or release workflow changes

Checks to run:
- `./scripts/ci_local.sh` (or targeted tests)
- `./scripts/check_links.py` (for doc moves)

## Scenario map (examples)

| Scenario | Minimum docs |
| --- | --- |
| Fix a flaky test | `testing-strategy.md`, `../reference/known-pitfalls.md` |
| Add a new CLI subcommand | `../reference/api.md`, `../architecture/project-overview.md` |
| Update docs structure | `../GIT_WORKFLOW_AI_AGENTS.md`, `../reference/known-pitfalls.md` |
| Plan a new feature | `../architecture/project-overview.md`, `../planning/next-session-brief.md` |
| Adopt a new tool | `../research/modern-python-tooling.md`, `solo-maintainer-operating-system.md` |

---

If unsure, start with Path B. It is the safest default for non-trivial work.
