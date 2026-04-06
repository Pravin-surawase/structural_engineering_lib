# Next Session Brief

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-04-07
<!-- HANDOFF:END -->

**Last Updated:** 2026-04-07
**Last Session:** Post-merge audit review — version accuracy fixes, endpoint count sync, PR #544 verified

## What Was Completed
- **Audit remediation merged (PR #544):** All 8 external audit fixes confirmed on main (ETABS units, story collision, geometry merge, SmartDesigner CLI, template packaging, README batch example, bbs import, README version)
- **Version accuracy:** Fixed 0.21.5 → 0.21.6 in README.md, CITATION.cff, package.json (pyproject.toml already correct)
- **TASKS.md accuracy:** Changed v0.21.6 from "Released" to "COMPLETE (unreleased)"
- **Endpoint count sync:** Fixed 59 → 60 in 8 files (11 edits)
- **Full test pass:** 5081 tests passing on main

## Current State
- **v0.21.5** = last PyPI release (tag: v0.21.5)
- **v0.21.6** = feature-complete, NOT yet released to PyPI (pyproject.toml says 0.21.6)
- All version references synchronized across README.md, CITATION.cff, package.json, pyproject.toml
- 60 endpoints, 13 routers — counts verified and synchronized across docs
- 5081 tests passing, 99% branch coverage on codes/is456/

## Priorities (Updated)

### Immediate (v0.21.7 — Security Hardening)
1. **JSON body size limit middleware** (TASK-728) — @api-developer
2. **Cross-field plausibility guards** (TASK-729) — @api-developer
3. **Input validation audit** (TASK-730) — @security
4. **WebSocket message rate limit** — @api-developer
5. **Computation timeout** — @api-developer

### Next (v0.21.8 — Performance & Property Testing)
6. **pytest-benchmark integration** (TASK-732) — @tester
7. **Hypothesis test expansion** (TASK-733) — @tester
8. **Performance regression baselines** (TASK-734) — @ops

### Architecture Reference
- Unified architecture: `docs/architecture/unified-architecture-v1.md`
- Complete roadmap: §20 of architecture doc (v0.21.5→v1.0)
- Quality gates per version: §9 of architecture doc

## Key Patterns Established
- `check_code("IS456")` validates code implementation contract — reports tech debt (36 issues: unfrozen results, missing decorators, params without unit suffixes)
- `show_versions()` follows scikit-learn pattern — both print and programmatic modes
- OpenAPI baseline diffing in CI prevents silent API drift
- Limitation docs prevent users from misapplying functions
- Version accuracy: v0.21.5 is last PyPI release, v0.21.6 is dev version (not "Released")

## Blockers
- None
