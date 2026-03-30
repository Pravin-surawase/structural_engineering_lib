# Library Expansion Master Blueprint v4.0

**Type:** Planning
**Audience:** All Agents
**Status:** Active
**Importance:** Critical
**Created:** 2026-03-29
**Last Updated:** 2026-03-30
**Version:** 4.0
**Previous:** [v3.0](../_archive/planning-completed-2026-03/library-expansion-blueprint.md) (archived)

> Single source of truth for expanding structural_engineering_lib from beam-only to a full IS 456 structural design suite.
> **v4.0 adds:** Quality pipeline integration, agent coordination updates, incremental complexity enforcement.

---

## 1. What Changed in v4.0

| Change | Details |
|--------|---------|
| **Quality Pipeline** | Every function goes through 9-step pipeline (new `/function-quality-pipeline` skill) |
| **Agent Updates** | All 8 specialist agents updated with quality checklist, numerical rules, math verification |
| **Golden Tests** | SP:16 benchmarks are permanent — can never be deleted |
| **Incremental Complexity** | Simplest case first, verify, then add complexity |
| **Peer Math Verification** | Every formula verified by 2 agents (structural-math writes, structural-engineer verifies) |
| **Degenerate Case Testing** | Every function tested with zero/extreme inputs |
| **Monotonicity Testing** | Mathematical properties verified via Hypothesis |
| **Error Recovery Guidance** | Every error tells user what to do next |
| **Shared Math Extraction** | `codes/is456/common/` for cross-element math |
| **New Prompt** | `function-quality-gate.prompt.md` for invoking the pipeline |

---

## 2. Quality Pipeline (NEW — Mandatory for Every Function)

Every new IS 456 function MUST go through this pipeline. Skill: `/function-quality-pipeline`

```
Step 1: PLAN          → @orchestrator + @structural-engineer
Step 2: MATH REVIEW   → @structural-engineer verifies formula independently
Step 3: IMPLEMENT     → @structural-math writes (12-point checklist)
Step 4: TEST          → @tester writes (6 test types: unit, edge, degenerate, SP:16, textbook, Hypothesis)
Step 5: REVIEW        → Two-pass: @structural-engineer (math) + @reviewer (code)
Step 6: API WIRE      → @backend adds to services/api.py
Step 7: ENDPOINT      → @api-developer creates FastAPI router
Step 8: DOCUMENT      → @doc-master updates all docs
Step 9: COMMIT        → @ops safe commit via ai_commit.sh
```

### Quality Gates (MUST pass before proceeding)

| Gate | Between Steps | What Must Pass |
|------|---------------|----------------|
| Formula Gate | 2 → 3 | @structural-engineer signs off on formula |
| Implementation Gate | 3 → 4 | 12-point checklist passes, function runs |
| Test Gate | 4 → 5 | All tests pass (SP:16 ±0.1%, textbook ±1%) |
| Review Gate | 5 → 6 | Both math and code reviews APPROVED |
| API Gate | 7 → 8 | Endpoint works, tests pass |

### Incremental Complexity (ENFORCED)

For new elements, implement in this order:

**Column:**
1. `calculate_min_eccentricity` (simplest — just arithmetic)
2. `design_short_column_axial` (pure axial — Cl 39.3)
3. `design_short_column_uniaxial` (axial + moment — Cl 39.5)
4. `pm_interaction_curve` (P-M diagram — Annex G)
5. `biaxial_bending_check` (Bresler — Cl 39.6)
6. `calculate_effective_length` (Cl 25.2, Table 28)
7. `calculate_additional_moment` (Ma iteration — Cl 39.7.1)
8. `design_long_column` (iterative — Cl 39.7)
9. `check_helical_reinforcement` (Cl 39.8)

Each function must pass the full pipeline before the next one starts.

---

## 3. Phased Implementation (Updated)

### Phase 0: Quality Infrastructure (NEW — Do FIRST)

| # | Task | Files | Status | Notes |
|---|------|-------|--------|-------|
| 0.1 | Function Quality Pipeline skill | `.github/skills/function-quality-pipeline/SKILL.md` | ✅ Done | v4.0 |
| 0.2 | Quality Gate prompt | `.github/prompts/function-quality-gate.prompt.md` | ✅ Done | v4.0 |
| 0.3 | Update structural-math agent | `.github/agents/structural-math.agent.md` | ✅ Done | 12-point checklist, numerical rules |
| 0.4 | Update tester agent | `.github/agents/tester.agent.md` | ✅ Done | Benchmark, degenerate, monotonicity tests |
| 0.5 | Update reviewer agent | `.github/agents/reviewer.agent.md` | ✅ Done | Two-pass review, IS 456 quality checks |
| 0.6 | Update api-developer agent | `.github/agents/api-developer.agent.md` | ✅ Done | Endpoint quality, plausibility guards |
| 0.7 | Update structural-engineer agent | `.github/agents/structural-engineer.agent.md` | ✅ Done | Math verification protocol |
| 0.8 | Update governance agent | `.github/agents/governance.agent.md` | ✅ Done | Quality metrics tracking |
| 0.9 | Update doc-master agent | `.github/agents/doc-master.agent.md` | ✅ Done | Element doc checklist |
| 0.10 | Update library-expert agent | `.github/agents/library-expert.agent.md` | ✅ Done | Quality enforcement rules |

### Phase 1: Foundation Cleanup (Before Column Work)

| # | Task | Files | Status | Priority |
|---|------|-------|--------|----------|
| 1.1 | Create `core/numerics.py` | `safe_divide()`, `approx_equal()`, `clamp()`, epsilon constants | ✅ Done | 🔴 P0 |
| 1.2 | Extract shared math | `codes/is456/common/stress_blocks.py`, `reinforcement.py`, `minimums.py` | ✅ Done | 🔴 P0 |
| 1.3 | Hardcode safety factors | `codes/is456/common/constants.py` — γc=1.5, γs=1.15 | ✅ Done | 🔴 P0 |
| 1.4 | Create `@deprecated` decorator | `core/deprecation.py` | 📋 TODO | 🔴 High |
| 1.5 | Populate clauses.json | Add ~66 subclauses for column, footing, slab | 📋 TODO | 🔴 High |
| 1.6 | Add IS 13920 references | `clauses.json` (~15 entries) | 📋 TODO | 🔴 High |
| 1.7 | Create test assertion helpers | `tests/helpers/is456_assertions.py` | 📋 TODO | 🟡 Medium |
| 1.8 | Top-level `__init__.py` exports | `structural_lib/__init__.py` | 📋 TODO | 🟡 Medium |
| 1.9 | Unit plausibility guards | `services/api.py` — range checks | 📋 TODO | 🟡 Medium |
| 1.10 | Stack trace sanitization | `fastapi_app/main.py` catch-all handler | 📋 TODO | 🟡 Medium |
| 1.11 | Add `recovery` field to `DesignError` | `core/errors.py` — optional, non-breaking | 📋 TODO | 🟡 Medium |
| 1.12 | `check_function_quality.py` script | Automated 12-point checklist CI | 📋 TODO | 🟡 Medium |
| 1.13 | `check_clause_coverage.py` script | IS 456 clause gap detection CI | 📋 TODO | 🟡 Medium |
| 1.14 | `check_new_element_completeness.py` script | Verify types + math + tests + API + docs | 📋 TODO | 🟡 Medium |
| 1.15 | `X-Process-Time` middleware | `fastapi_app/main.py` | 📋 TODO | 🟢 Low |
| 1.16 | Add `formula_signatures` to `clauses.json` | Cross-reference validation | 📋 TODO | 🟢 Low |
| 1.17 | Create maintenance playbook | `docs/governance/maintenance-playbook.md` | 📋 TODO | 🟢 Low |

### Phase 2: Column Design (Priority 1)

**IS 456 Clauses:** Cl 25, 26.5, 39 | **IS 13920:** Cl 7.3-7.4.8
**SP:16 Charts:** 27-62 | **Benchmarks:** Pillai & Menon Ch.13, Ramamrutham Ch.15

**Implementation order (incremental complexity):**

| # | Function | Clause | Complexity | Prerequisite |
|---|----------|--------|------------|-------------|
| 2.1 | `calculate_min_eccentricity` | Cl 39.1 | Simple | Phase 1 complete |
| 2.2 | `design_short_column_axial` | Cl 39.3 | Simple | 2.1 verified |
| 2.3 | `design_short_column_uniaxial` | Cl 39.5 | Medium | 2.2 verified |
| 2.4 | `pm_interaction_curve` | Cl 39.5, Annex G | Complex | 2.3 verified |
| 2.5 | `biaxial_bending_check` | Cl 39.6 | Complex | 2.4 verified |
| 2.6 | `calculate_effective_length` | Cl 25.2 | Simple | Independent |
| 2.7 | `calculate_additional_moment` | Cl 39.7.1 | Medium | 2.6 verified |
| 2.8 | `design_long_column` | Cl 39.7 | Complex | 2.7 verified |
| 2.9 | `check_helical_reinforcement` | Cl 39.8 | Simple | Independent |
| 2.10 | `design_column_is456` (orchestrator) | All | Integration | All above verified |

**Types (create before math):**
- `core/inputs.py` → `ColumnGeometryInput`, `ColumnLoadsInput`
- `core/data_types.py` → `ColumnResult`, `ColumnInteractionPoint`, `ColumnType` enum
- `core/errors.py` → `E_COLUMN_001` through `E_COLUMN_015`

**Tests per function:** 50+ total (unit + SP:16 golden + Hypothesis + degenerate)
**API:** `design_column_is456()` in `services/api.py` + `POST /api/v1/design/column`

### Phase 3: Footing Design (Priority 2)

**IS 456 Clauses:** Cl 34, Cl 31.6 | **IS 13920:** Cl 10

| # | Function | Clause | Complexity |
|---|----------|--------|------------|
| 3.1 | `design_isolated_footing` | Cl 34 | Medium |
| 3.2 | `punching_shear_check` | Cl 31.6 | Medium |
| 3.3 | `one_way_shear_check` | Cl 34.2.4 | Simple |
| 3.4 | `calculate_bearing_pressure` | Cl 34.4 | Simple |
| 3.5 | `check_dowel_bars` | Cl 34.2.5 | Simple |

### Phase 4: One-Way Slab (Priority 3)

**IS 456 Clauses:** Cl 24 | **SP:16 Charts:** 1-26

| # | Function | Clause | Complexity |
|---|----------|--------|------------|
| 4.1 | `design_oneway_slab` | Cl 24 | Medium |
| 4.2 | `calculate_distribution_steel` | Cl 26.5.2.1 | Simple |
| 4.3 | `check_slab_deflection` | Cl 23.2 | Simple |

### Phase 5: Two-Way Slab (Priority 4)

**IS 456 Clauses:** Cl 24, Annex D | **Tables:** 26, 27, 28

| # | Function | Clause | Complexity |
|---|----------|--------|------------|
| 5.1 | `design_twoway_slab` | Annex D | Complex |
| 5.2 | `moment_coefficients` | Table 26, 27 | Medium |
| 5.3 | `torsion_reinforcement` | Annex D-1.8 | Simple |

### Phase 6: Staircase & Shear Wall (Priority 5)

**Staircase:** Cl 33 | **Shear Wall:** Cl 32, IS 13920 Cl 9

---

## 4. Agent Coordination for Quality Pipeline

### Who Does What

| Step | Agent | Duration | Skill |
|------|-------|----------|-------|
| PLAN | @orchestrator | 15 min | — |
| MATH REVIEW | @structural-engineer | 30 min | `/is456-verification` |
| IMPLEMENT | @structural-math | 1-2 hrs | `/function-quality-pipeline` |
| TEST | @tester | 1-2 hrs | `/is456-verification` |
| REVIEW (math) | @structural-engineer | 30 min | `/is456-verification` |
| REVIEW (code) | @reviewer | 30 min | `/architecture-check` |
| API WIRE | @backend | 30 min | `/api-discovery` |
| ENDPOINT | @api-developer | 30 min | `/api-discovery` |
| DOCUMENT | @doc-master | 15 min | `/safe-file-ops` |
| COMMIT | @ops | 5 min | — |

### Handoff Chain

```
@orchestrator → @structural-engineer (clause research)
             → @structural-math (implementation)
             → @tester (comprehensive tests)
             → @structural-engineer (math verification)
             → @reviewer (code quality)
             → @backend (API wiring)
             → @api-developer (endpoint)
             → @doc-master (documentation)
             → @ops (commit)
```

Each handoff must include:
- Files changed
- What was done
- How to verify
- Any issues or concerns

---

## 5. Timeline Estimate

| Phase | Functions | Est. Sessions | Notes |
|-------|-----------|---------------|-------|
| Phase 0 | — | ✅ Done | Quality infrastructure |
| Phase 1 | — | 3-4 sessions | Foundation cleanup |
| Phase 2 | 10 column funcs | 8-12 sessions | With full pipeline per function |
| Phase 3 | 5 footing funcs | 4-6 sessions | Simpler than column |
| Phase 4 | 3 one-way slab funcs | 3-4 sessions | Similar to beam |
| Phase 5 | 3 two-way slab funcs | 4-6 sessions | Complex coefficients |
| Phase 6 | 6 staircase + wall funcs | 6-8 sessions | Advanced |

**Total: ~28-40 sessions** (developing slowly with accuracy)

---

## 6. Success Criteria

| Metric | Target |
|--------|--------|
| SP:16 benchmark pass rate | 100% at ±0.1% |
| 12-point checklist compliance | 100% |
| Degenerate case coverage | ≥2 per function |
| Monotonicity test coverage | ≥2 per function |
| Golden test permanence | 0 deleted |
| Safety factor lockdown | γc, γs never as parameters |
| Error recovery guidance | Every DesignError has recovery hint |
| Clause coverage | 100% of required IS 456 clauses |
| Functions verified by 2 agents | 100% |

---

## 7. References

- [v3.0 Blueprint](../_archive/planning-completed-2026-03/library-expansion-blueprint.md) — previous version (archived)
- [Function Quality Pipeline](../../.github/skills/function-quality-pipeline/SKILL.md) — skill
- [Quality Gate Prompt](../../.github/prompts/function-quality-gate.prompt.md) — prompt
- IS 456:2000 — Indian Standard for Plain and Reinforced Concrete
- SP:16:1980 — Design Aids for Reinforced Concrete
- IS 13920:2016 — Ductile Detailing of RC Structures