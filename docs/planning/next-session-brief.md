# Next Session Briefing

**Last Updated:** 2025-12-28
**Status:** v0.10.3 (current release)
**Branch:** `main` (all PRs merged through #95)

---

## 🎯 Immediate Priority: v0.20.0 Stable Release

**v0.20.0 Stabilization Status:**
- 🔴 **Critical:** 14/15 complete (only S-007 manual test remains)
- 🟡 **High Priority:** 12/12 complete ✅
- 🟢 **Nice to Have:** 0/4 (post v0.20.0)

**What's blocking v0.20.0:**
- **S-007:** One external engineer tries CLI cold (requires human tester)

**Stabilization checklist:** `docs/planning/v0.20-stabilization-checklist.md`

**To release v0.20.0 (after S-007 passes):**
```bash
python scripts/release.py 0.20.0
```

---

## 🚨 STOP — READ THIS FIRST (Mandatory for New Agents)

Before writing ANY code or making changes, you MUST understand this project. Failure to read context leads to:
- Breaking Python ↔ VBA parity
- Violating layer architecture
- Creating code that doesn't match IS 456 requirements
- Wasting time on already-solved problems

### Step 1: Read These Documents (in order)

| Priority | Document | Why |
|----------|----------|-----|
| **1** | `.github/copilot-instructions.md` | Layer rules, units, Mac VBA safety, testing requirements |
| **2** | `docs/AI_CONTEXT_PACK.md` | Complete project context for AI agents |
| **3** | `docs/architecture/deep-project-map.md` | Code structure, data flow, parity hotspots |
| **4** | `docs/TASKS.md` | Canonical backlog — what's done, what's pending |
| **5** | `docs/planning/pre-release-checklist.md` | Beta gates and validation status |

### Step 2: Understand the Project

**What this is:** IS 456 (Indian Standard) RC beam design library with Python + VBA parity.

**Who uses it:**
- Structural engineers designing RC beams
- Excel users via VBA add-in (`Excel/StructEngLib.xlam`)
- Python users via pip package (`pip install structural-lib-is456`)

**Core workflow:**
```
Input (beam geometry, loads, materials)
    ↓
Flexure Design (Mu → Ast/Asc, neutral axis depth)
    ↓
Shear Design (Vu → stirrup spacing)
    ↓
Detailing (development length, lap length, spacing checks)
    ↓
Serviceability (deflection, crack width) [optional but recommended]
    ↓
Output (design results, BBS, DXF drawings)
```

### Step 3: Understand the Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ UI/I-O Layer (reads/writes external data)                   │
│ Python: excel_integration.py, dxf_export.py, job_cli.py     │
│ VBA: M09_UDFs, macros                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Application Layer (orchestrates core, no formatting)        │
│ Python: api.py, job_runner.py, bbs.py, rebar_optimizer.py   │
│ VBA: M08_API                                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Core Layer (pure functions, no I/O, explicit units)         │
│ Python: flexure.py, shear.py, detailing.py, serviceability.py│
│         compliance.py, tables.py, ductile.py, materials.py   │
│ VBA: M01-M07, M15-M17                                        │
└─────────────────────────────────────────────────────────────┘
```

**RULE:** Never put I/O code in Core. Never put calculations in UI.

### Step 4: Understand Units Convention

| Context | Units |
|---------|-------|
| **Inputs** | mm, N/mm², kN, kN·m |
| **Internal** | mm, N, N·mm (convert at layer boundaries) |
| **Outputs** | mm, N/mm², kN, kN·m |

### Step 5: Before Making Changes

- [ ] Run tests first: `cd Python && python -m pytest -q`
- [ ] Check if VBA needs matching changes (parity requirement)
- [ ] Add tests for any new behavior
- [ ] Format with black: `cd Python && python -m black .`
- [ ] Update docs if API/behavior changes

---

## TL;DR (What Changed Recently)

### Latest Session (2025-12-28): Stabilization Sprint

**PRs Merged (#89-95):**
| PR | Description |
|----|-------------|
| #89 | S-015: Fixed 4 broken links + `scripts/check_links.py` |
| #90 | S-014: Fixed expected output in beginners-guide (942→882mm²) |
| #91 | S-009: Fixed D1 expected Ld value (752→777mm) |
| #92 | S-006: Improved job_runner error messages |
| #93 | S-020–S-032: All High Priority items verified |
| #95 | Documentation updates for stabilization sprint |

**Key Deliverables:**
- `scripts/check_links.py` — Reusable link checker (85 md files, 173 links)
- Improved error messages in `job_runner.py`
- All robustness + performance items verified:
  - Edge cases: Zero/negative inputs return `is_safe=False`
  - Performance: 0.009ms per beam, 94,000 beams/second
  - Large batch: 1000 beams tested successfully

**Test Stats:** 1810 passed, 91 skipped, 92% branch coverage

---

## ⚡ Fast Re-Onboarding (start here next session)

If you want to resume quickly without re-reading the repo:

1. **Whole-project map (architecture + data flow + parity hotspots):** `docs/architecture/deep-project-map.md`
2. **Version management:** `docs/_internal/VERSION_STRATEGY.md`
3. **Canonical backlog:** `docs/TASKS.md`
4. **Primary reference index:** `docs/README.md`
5. **Pre-release checklist:** `docs/planning/pre-release-checklist.md`
6. **Git governance (branch protection):** `docs/_internal/GIT_GOVERNANCE.md`

**Verified state (as of 2025-12-28):**
- Release version is **v0.10.3** (merged to main, published to PyPI).
- **Tests:** 1810 passed, 91 skipped, 92% branch coverage
- **Stabilization:** 26/31 items complete (see `docs/planning/v0.20-stabilization-checklist.md`)
- Unified CLI: **implemented** (`python -m structural_lib design|bbs|dxf|job`).
- Cutting-stock optimizer: **implemented** (first-fit-decreasing bin packing).
- VBA BBS + Compliance: **implemented** (parity with Python modules).
- Serviceability (Level A+B): **implemented** (deflection + crack width).
- Compliance checker: **implemented** (multi-case orchestration + summary).
- BBS Module: **implemented** (cut lengths, weights, CSV/JSON export).
- **Validation examples:** **complete** (6 verification examples verified).
- **API docs UX:** **complete** (all 6 phases).

**How to re-verify quickly (avoids drift):**
- Latest commit (local): `git rev-parse --short HEAD`
- CI truth (GitHub): https://github.com/Pravin-surawase/structural_engineering_lib/actions
- Version: `python -c "from structural_lib import api; print(api.get_library_version())"`

**Branch protection (documented in `docs/_internal/GIT_GOVERNANCE.md`):**
- `main` requires PR (no direct pushes)
- 5 required status checks: `test`, `lint`, `type-check`, `build`, `docs`
- Force pushes and branch deletion disabled
- Tags trigger PyPI publish workflow

---

## 🎯 What to Work on Next

### High Priority (v0.20.0 Release)
1. **S-007: External engineer test** — Have someone try CLI cold, note friction points
   - This is the ONLY blocking item for v0.20.0
   - Requires a human engineer (not automatable)

### After v0.20.0 (Nice to Have)
2. **S-050: VBA parity automation** — Automated comparison of Python vs VBA outputs
3. **S-051: Performance benchmarks** — Track regression over time
4. **S-052: Fuzz testing** — Random input testing
5. **S-053: Security audit** — Dependency scan

### Backlog (v1.0+)
6. **Level C Serviceability** — Shrinkage + creep deflection (Annex C full)
7. **Torsion Design** — Equivalent shear/moment + closed stirrups (Cl. 41)
8. **Side-Face Reinforcement** — D > 750mm check (Cl. 26.5.1.3)
9. **Anchorage Space Check** — Verify Ld at supports (Cl. 26.2)

---

## ✅ Session Summary (2025-12-28) — Stabilization Sprint

### PRs Merged This Session (#89-95)

| PR | Task ID | Description |
|----|---------|-------------|
| #89 | S-015 | Fixed 4 broken internal links, added `scripts/check_links.py` |
| #90 | S-014 | Fixed expected output in beginners-guide (942→882mm²) |
| #91 | S-009 | Fixed D1 expected Ld value in verification examples (752→777mm) |
| #92 | S-006 | Improved job_runner error messages for missing fields |
| #93 | S-020–S-032 | Verified all High Priority items (robustness + performance) |
| #95 | — | Documentation updates (SESSION_LOG, CHANGELOG, TASKS) |

### Key Deliverables
- **Link checker:** `scripts/check_links.py` — validates 173 internal links across 85 markdown files
- **Error messages:** `job_runner.py` now gives specific errors for missing `code`, `schema_version`
- **Robustness verified:** Zero/negative inputs return `is_safe=False` with clear error messages
- **Performance verified:** 0.009ms per beam, 94,000 beams/second batch tested

### Stabilization Status After This Session
- 🔴 Critical: 14/15 complete (only S-007 manual test remains)
- 🟡 High Priority: 12/12 complete ✅
- 🟢 Nice to Have: 0/4 (post v0.20.0)

### Lessons Learned
- Run `scripts/check_links.py` before releases to catch broken doc links
- Verify expected values in examples match actual code output
- Stateless functions = no memory leak concerns

---

## 📜 Historical Sessions

For older session summaries, see:
- `docs/SESSION_LOG.md` — Full append-only history of all sessions
- `docs/_archive/` — Archived planning documents

---

*End of next-session-brief.md*
