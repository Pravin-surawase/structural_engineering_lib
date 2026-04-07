# Migration Planning — Two-Repo Split

**Type:** Reference
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-04-07
**Last Updated:** 2026-04-08

---

Master index for splitting the monorepo into:
- **Library Repo** — Pure Python IS 456 structural design library (PyPI package)
- **App Repo** — FastAPI + React full-stack application

## Documents

| # | File | Purpose |
|---|------|---------|
| 01 | [01-adr-library-separation.md](01-adr-library-separation.md) | ADR: Decision record — why two repos, naming (`rcdesign`), architecture |
| 02 | [02-library-research.md](02-library-research.md) | Research: 20 libraries deep-dived (pyproject.toml configs, CI/CD, pre-commit, structural eng libs) |
| 03 | [03-library-repo-blueprint.md](03-library-repo-blueprint.md) | Blueprint: Complete library repo — dir structure, pyproject.toml with hatch-vcs + 19 ruff rules |
| 04 | [04-app-repo-blueprint.md](04-app-repo-blueprint.md) | Blueprint: `rcdesign-app` repo — FastAPI + React, depends on `rcdesign` from PyPI |
| 05 | [05-agents-and-automation.md](05-agents-and-automation.md) | Agents: 4 library agents (coder, reviewer, tester, math-verifier) + claw-code patterns |
| 06 | [06-ci-cd-and-tooling.md](06-ci-cd-and-tooling.md) | CI/CD: GitHub Actions (alls-green, Trusted Publishers), pre-commit (7 hooks), codecov, dependabot |
| 07 | [07-migration-steps.md](07-migration-steps.md) | Steps: 4-phase checklist with rollback plans and backward compatibility |
| 08 | [08-naming-and-accounts.md](08-naming-and-accounts.md) | Setup: `rcdesign` naming, PyPI/TestPyPI, fallback names, availability checks |
| 09 | [09-standards-and-rules.md](09-standards-and-rules.md) | Standards: `fck` convention, 19 ruff rule sets, 6 test types, clause referencing |
| 10 | [10-function-classification.md](10-function-classification.md) | Classification: Canonical table — all 123 functions categorized (CORE/ORCH/APP) |

## Summary

- **Current state:** Monorepo with 149 Python files, 176+ scripts, 16 agents, React, Docker
- **Target:** Clean two-repo architecture
- **Library name candidates:** rcdesign, concretepy, structlib, is456py
- **Key tools:** uv + hatchling + ruff + mypy + GitHub Actions + Trusted Publishers
- **Timeline:** 6 weeks (4 phases)

## Key Decisions (Finalized)

| Decision | Choice | Evidence |
|----------|--------|----------|
| Package name | **rcdesign** | Short, professional, not locked to one code |
| Import name | **rcdesign** | Same as package (no Pillow/PIL confusion) |
| Build system | **hatchling + uv** | sectionproperties, pydantic, httpx pattern |
| Layout | **src/ layout** | sectionproperties, pytest, COMPAS pattern |
| Agents (library) | **4** — coder, reviewer, tester, math-verifier | math-verifier justified for safety-critical calcs |
| Agents (app) | **5-6** — backend, frontend, api, reviewer, tester, devops | Full-stack needs more roles |
| Param naming | **fck** (no _mpa suffix) for materials, **b_mm** for dimensions | structuralcodes + IS 456 convention |
| Type checking | **mypy strict + pyright strict** | polars, httpx, sectionproperties pattern |
| Docstrings | **NumPy convention** | sectionproperties, polars pattern |
| Coverage target | **95% branch** (90% for Phase 1) | Higher than polars' 85% — safety-critical |
| CI model | **4 workflows** — ci, publish, docs, maintenance | sectionproperties' clean pattern |
| Changelog | **towncrier** | pytest pattern (11 fragment types) |
| Python versions | **3.11, 3.12, 3.13** | SPEC-0000 rolling 3-year window |

## Open Items (Need User Decision)

1. **PyPI availability** — Verify `rcdesign` is available on PyPI before Phase 1
2. **Fallback names** — `rcdesign-py`, `rc-design` if taken
3. **Slab implementation timing** — Before or after migration? (Recommendation: after)
4. **`structural-lib-is456` deprecation** — Final release with redirect notice?

## Quick Navigation

- **Want to understand WHY?** → Start with [01-adr-library-separation.md](01-adr-library-separation.md)
- **Want to see what peers do?** → Read [02-library-research.md](02-library-research.md) (20 libraries analyzed with deep-dive configs)
- **Want to know WHAT goes where?** → Check [10-function-classification.md](10-function-classification.md)
- **Want to start DOING?** → Follow [07-migration-steps.md](07-migration-steps.md)
- **Want to set up accounts?** → See [08-naming-and-accounts.md](08-naming-and-accounts.md)
- **Want naming details?** → See [08-naming-and-accounts.md](08-naming-and-accounts.md) (fallback names, availability checks)
- **Want coding standards?** → See [09-standards-and-rules.md](09-standards-and-rules.md) (fck convention, 19 ruff rules, 6 test types)
