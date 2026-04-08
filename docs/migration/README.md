# Migration Planning — Multi-Code Library Split

**Type:** Reference
**Version:** 2.0
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-04-07
**Last Updated:** 2026-04-08

---

Master index for splitting the monorepo into:
- **Library Repo** — Pure Python multi-code RC design library (IS 456, ACI 318, EC2) on PyPI
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
| 10 | [10-function-classification.md](10-function-classification.md) | Classification: Canonical table — all 123 current functions categorized (CORE/ORCH/APP) |
| 11 | [11-complete-function-enumeration.md](11-complete-function-enumeration.md) | Complete 564-function enumeration across IS 456, ACI 318, EC2 (5 elements) |

## Summary

- **Current state:** Monorepo with 149 Python files, 176+ scripts, 16 agents, React, Docker
- **Target:** Clean two-repo architecture with multi-code support
- **Scope:** 564 functions across 3 codes (IS 456:2000, ACI 318-19, Eurocode 2) and 5 structural elements
- **Architecture:** 5-layer: core ← common ← codes ← services ← ui
- **Library name:** ⚠️ TBD — `rcdesign` is TAKEN on PyPI (see doc 08)
- **Key tools:** uv 0.11.3 + hatchling + ruff 0.15.9 + basedpyright v1.39.0 + GitHub Actions + Trusted Publishers
- **Timeline:** 6 weeks (4 phases)

## Key Decisions (Finalized)

| Decision | Choice | Evidence |
|----------|--------|----------|
| Package name | ⚠️ **TBD** — `rcdesign` is TAKEN (see doc 08) | Top suggestion: `calcrete` (8 chars, unique, available) |
| Import name | Same as package (no Pillow/PIL confusion) | — |
| Architecture | **5-layer:** core ← common ← codes ← services ← ui | Multi-code requires shared `common` layer |
| Multi-code | **Protocol + Registry pattern** (not if/elif chains) | 9 protocols: Material, Flexural, Shear, Column, Slab, Footing, Detailing, Serviceability, Torsion |
| Build system | **hatchling + uv** | sectionproperties, pydantic, httpx pattern |
| Layout | **src/ layout** | sectionproperties, pytest, COMPAS pattern |
| Agents (library) | **4** — coder, reviewer, tester, math-verifier | math-verifier justified for safety-critical calcs |
| Agents (app) | **5-6** — backend, frontend, api, reviewer, tester, devops | Full-stack needs more roles |
| Param naming | **fck** (no _mpa suffix) for materials, **b_mm** for dimensions | structuralcodes + IS 456 convention |
| Type checker | **basedpyright** (primary) + mypy backup | 2026 best practice — stricter, faster than mypy |
| Docstrings | **NumPy convention** | sectionproperties, polars pattern |
| Coverage target | **95% branch** (90% for Phase 1) | Higher than polars' 85% — safety-critical |
| CI model | **4 workflows** — ci, publish, docs, maintenance | sectionproperties' clean pattern |
| Changelog | **towncrier** | pytest pattern (11 fragment types) |
| Key tools | **uv 0.11.3 + hatchling + ruff 0.15.9 + basedpyright + GitHub Actions** | 2026 toolchain report |
| Python versions | **3.11, 3.12, 3.13** | SPEC-0000 rolling 3-year window |

## Open Items (Need User Decision)

1. ⚠️ **CRITICAL: `rcdesign` is TAKEN on PyPI** — new name needed (see doc 08 for 7 verified alternatives)
2. **Multi-code implementation order** — IS 456 → ACI 318 → EC2 (recommended)
3. **Versioning strategy for multi-code releases** — one version or per-code?
4. **Slab implementation timing** — Before or after migration? (Recommendation: after)
5. **`structural-lib-is456` deprecation** — Final release with redirect notice?

## Research Documents

These companion research docs inform the migration decisions:

| File | Purpose |
|------|---------|
| [docs/research/2026-python-toolchain-report.md](../research/2026-python-toolchain-report.md) | 2026 toolchain recommendations — uv, ruff, basedpyright, tach, mutmut |
| [docs/research/2026-state-of-the-art-report.md](../research/2026-state-of-the-art-report.md) | State-of-the-art competitive analysis — 20+ libraries surveyed |
| [docs/research/claw-code-harness-ideas.md](../research/claw-code-harness-ideas.md) | Claw-code patterns for AI agents and test harnesses |

## Quick Navigation

- **Want to understand WHY?** → Start with [01-adr-library-separation.md](01-adr-library-separation.md)
- **Want to see what peers do?** → Read [02-library-research.md](02-library-research.md) (20 libraries analyzed with deep-dive configs)
- **Want to know WHAT goes where?** → Check [10-function-classification.md](10-function-classification.md)
- **Want to start DOING?** → Follow [07-migration-steps.md](07-migration-steps.md)
- **Want to set up accounts?** → See [08-naming-and-accounts.md](08-naming-and-accounts.md)
- **Want naming details?** → See [08-naming-and-accounts.md](08-naming-and-accounts.md) (fallback names, availability checks)
- **Want coding standards?** → See [09-standards-and-rules.md](09-standards-and-rules.md) (fck convention, 19 ruff rules, 6 test types)
