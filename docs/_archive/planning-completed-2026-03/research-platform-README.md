# Research: Platform Access

> **Template version:** 1.0
> Created using multi-agent research workflow

**Last Updated:** 2025-12-29
**Status:** Decided (Stage 4 complete)
**Owner:** PM
**Decision Date:** TBD (post-v1.0)

---

## Problem Statement

Engineers who don't have Python installed (or don't want to use CLI) cannot access the library's design capabilities. They're stuck with Excel-only workflows or need IT support to set up Python environments.

---

## Context

- Current access: Python CLI, Excel/VBA add-in
- Gap: No browser-based or zero-install option
- Trigger: User feedback "I want to try this but can't install Python on work laptop"
- Related: Visual layer research (reports need a delivery mechanism)

---

## Users & Personas

| User | Context | Pain Point |
|------|---------|------------|
| **Junior Engineer** | Work laptop with IT restrictions | "I can't install anything without IT approval" |
| **Freelance Consultant** | Multiple client machines | "I can't set up Python on every client's computer" |
| **Checking Engineer** | Just needs to verify, not design | "I only want to spot-check one beam, not learn Python" |
| **Student** | Learning IS 456 | "I want to play with examples without setup" |
| **Mobile User** | Site visit with tablet | "I need quick calc access in the field" |

---

## Constraints (Non-Negotiables)

- [ ] Deterministic (same input → same output, regardless of platform)
- [ ] No new required dependencies for core library
- [ ] Core calculations must remain in Python (not reimplemented)
- [ ] Free tier must exist (not paid-only)
- [ ] Offline capability preferred (site engineers)
- [ ] Must not compromise security (no arbitrary code execution)

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Time from URL to first result | < 2 minutes |
| Works without installation | Yes |
| Works on mobile browser | Basic functionality |
| Matches CLI output exactly | 100% |

---

## Stage 1 Summary (for next agent)

**Problem defined:** Users without Python can't access the library.

**Personas identified:** 5 user types with distinct constraints.

**Constraints set:** Determinism, free tier, offline preferred, security.

**Next stage:** RESEARCHER to explore platform options.

**Handoff note:** This research is explicitly POST-v1.0. Do not create implementation tasks until v1.0 ships.

---

## Options Explored

### Option A: Streamlit Cloud (Hosted Web App)

**Description:** Deploy a Streamlit app that wraps our CLI. Users visit a URL, enter beam parameters, get results.

**Pros:**
- Zero install for users
- Free tier available (Streamlit Community Cloud)
- Python backend = exact same calculations
- Easy to build (Streamlit is simple)
- Mobile-friendly out of the box

**Cons:**
- Requires internet (no offline)
- Free tier has limits (sleeping apps, resource caps)
- We become dependent on Streamlit's hosting
- UI is Streamlit-style, not custom

**Edge cases (TESTER):**
- What if Streamlit Cloud goes down?
- What if free tier limits are hit?
- Batch mode (500 beams) may timeout

**Dependencies:** `streamlit` (new optional dep)

---

### Option B: Static Site + PyScript (Browser-Only Python)

**Description:** Use PyScript to run Python directly in the browser. No server needed.

**Pros:**
- Works offline after first load
- No server costs
- True zero-install
- Can be hosted on GitHub Pages (free)

**Cons:**
- PyScript is slow (WASM overhead)
- Large download (~20MB Pyodide runtime)
- Limited library support (numpy OK, some deps may not work)
- Still experimental technology

**Edge cases (TESTER):**
- First load time could be 30+ seconds
- Memory limits on mobile browsers
- Some IS 456 tables may need special handling

**Dependencies:** None in core (pure frontend)

---

### Option C: Google Colab Notebooks

**Description:** Provide pre-built Colab notebooks. Users click link, run cells.

**Pros:**
- Free, no install
- Full Python environment
- Easy to share
- Already familiar to students

**Cons:**
- Requires Google account
- Not a "product" feel
- Users must run cells manually
- Can't embed in our site

**Edge cases (TESTER):**
- Colab session timeouts
- Version drift if Colab updates Python

**Dependencies:** None (just notebooks)

---

### Option D: Desktop App (PyInstaller/Electron)

**Description:** Package Python as standalone executable. Download once, run forever.

**Pros:**
- Works offline
- Full control over UX
- No account needed
- Fast after install

**Cons:**
- Still requires download/install
- Platform-specific builds (Win/Mac/Linux)
- Large file size (50-100MB)
- Update mechanism needed

**Edge cases (TESTER):**
- Antivirus false positives
- Code signing costs
- macOS Gatekeeper issues

**Dependencies:** `pyinstaller` or similar (build-time only)

---

### Option E: API + Simple Frontend

**Description:** Host a REST API (FastAPI), provide a simple HTML form frontend.

**Pros:**
- Clean separation (API reusable)
- Frontend can be static (GitHub Pages)
- Scales well
- Enables third-party integrations

**Cons:**
- Requires server hosting (costs money)
- More complex than Streamlit
- Need to handle auth, rate limits
- No offline mode

**Edge cases (TESTER):**
- API abuse (rate limiting needed)
- Latency for remote users
- CORS configuration

**Dependencies:** `fastapi`, `uvicorn` (server-side)

---

## Constraints Verification

| Option | Deterministic | No Core Deps | Free Tier | Offline | Secure | Fits Post-v1.0 |
|--------|---------------|--------------|-----------|---------|--------|----------------|
| A. Streamlit | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| B. PyScript | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| C. Colab | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| D. Desktop | ✓ | ✓ | ✓ | ✓ | ? | ✓ |
| E. API | ✓ | ✓ | ✗ | ✗ | ? | ✓ |

---

## Stage 2 Summary (for next agent)

**Options explored:** 5 platform approaches with pros/cons.

**TESTER edge cases:** Identified for each option.

**Constraints verified:** A, B, C pass most constraints. D, E have gaps.

**Top candidates:** Streamlit (easiest), PyScript (most independent), Colab (quickest).

**Next stage:** DEV to assess feasibility and score options.

**Handoff note:** Remember this is POST-v1.0. Scoring should consider "effort to maintain" not just "effort to build."

---

## Scoring

### Feasibility Notes (DEV Assessment)

#### Option A: Streamlit
- **Effort:** 2-3 days (simple wrapper around existing CLI)
- **Complexity:** Low
- **Maintenance:** Low (Streamlit handles hosting)
- **Architecture fit:** Clean — just imports `api.py`

#### Option B: PyScript
- **Effort:** 1-2 weeks (need to test all deps work in Pyodide)
- **Complexity:** Medium-High (WASM quirks)
- **Maintenance:** Medium (Pyodide updates may break things)
- **Architecture fit:** Risky — some deps may not port

#### Option C: Colab
- **Effort:** 1 day (just create notebooks)
- **Complexity:** Very Low
- **Maintenance:** Very Low
- **Architecture fit:** Perfect — it's just Python

#### Option D: Desktop App
- **Effort:** 1-2 weeks (build pipeline, testing, signing)
- **Complexity:** High
- **Maintenance:** High (platform-specific issues)
- **Architecture fit:** Good but heavy

#### Option E: API
- **Effort:** 1 week (FastAPI wrapper + frontend)
- **Complexity:** Medium
- **Maintenance:** High (server ops, monitoring)
- **Architecture fit:** Good but needs infrastructure

---

### Scoring Rubric Applied

| Option | Trust (5) | Value (5) | Effort (5=low) | Risk (5=low) | Align (5) | Total | Rank |
|--------|-----------|-----------|----------------|--------------|-----------|-------|------|
| A. Streamlit | 5 | 5 | 4 | 4 | 5 | 23 | 🥇 1 |
| B. PyScript | 4 | 5 | 2 | 2 | 4 | 17 | 4 |
| C. Colab | 5 | 4 | 5 | 5 | 5 | 24 | 🥇 1 |
| D. Desktop | 5 | 4 | 2 | 2 | 4 | 17 | 4 |
| E. API | 5 | 5 | 3 | 2 | 3 | 18 | 3 |

---

### Review Findings

| Severity | Finding | Option | Resolution |
|----------|---------|--------|------------|
| **Medium** | Streamlit free tier has cold starts (30s delay) | A | Acceptable for v1 |
| **Low** | Colab requires Google account | C | Document as limitation |
| **Medium** | PyScript may not support all our deps | B | Needs prototype before commit |
| **High** | API needs ongoing hosting costs | E | Not suitable for free tier goal |
| **Medium** | Desktop needs code signing ($300+/year) | D | Defer unless demand proven |

---

## Stage 3 Summary (for next agent)

**Scored:** 5 options with feasibility and rubric.

**Top 2:** Colab (24) and Streamlit (23) — both low effort, high value.

**Review findings:** API has cost issue, Desktop has signing cost, PyScript is risky.

**Recommendation:** Start with Colab (quickest), add Streamlit later.

**Next stage:** PM to make final decision.

**Handoff note:** Both top options can coexist. Consider phased rollout.

---

## Decision

### Chosen Approach: Phased Rollout

**Phase P1 (v1.0.x):** Google Colab Notebooks
- Quickest to ship (1 day)
- Immediate value for students and quick-checkers
- No infrastructure needed

**Phase P2 (v1.1+):** Streamlit Cloud App
- Better UX than notebooks
- Still free tier available
- 2-3 days effort

**Phase P3 (v1.2+ if demand):** PyScript or Desktop
- Only if P1/P2 don't meet needs
- Requires proven user demand

---

### Rationale

1. **Colab first** because it's zero effort and validates demand.
2. **Streamlit second** because it's a better product experience.
3. **Others parked** because they have cost/complexity issues.

---

### What We Will NOT Do (and why)

| Option | Why Not |
|--------|---------|
| **API-first** | Requires hosting costs, conflicts with "free tier" constraint |
| **Desktop-first** | High effort, signing costs, still requires download |
| **PyScript-first** | Too experimental, dependency risk |

---

### Approval

- [x] PM: Approved phased approach
- [x] Scope: Post-v1.0 only (no implementation until v1.0 ships)
- [x] No WIP conflict (this is research documentation only)

---

## Parking Lot

| Idea | Why Parked | Revisit When |
|------|------------|--------------|
| **PyScript offline app** | Experimental, dep risks | v1.3+ if Pyodide matures |
| **Desktop app (PyInstaller)** | High effort, signing costs | Only if enterprise demand |
| **REST API** | Hosting costs | Only if third-party integration needed |
| **Mobile native app** | Way out of scope | Never (browser is enough) |
| **Self-hosted option** | Enterprise feature | v2.0+ if commercial tier added |

---

## Next Steps (for TASKS.md — POST-v1.0 ONLY)

> ⚠️ **DO NOT CREATE TASKS UNTIL v1.0 SHIPS**
> This section is documentation for future reference.

### Future Tasks (when v1.0 is released)

| ID | Task | Agent | Est. | Priority | Depends On |
|----|------|-------|------|----------|------------|
| TASK-TBD | Create example Colab notebooks | DOCS | 4 hrs | High | v1.0 release |
| TASK-TBD | Publish notebooks to repo + docs | DOCS | 2 hrs | High | Colab notebooks |
| TASK-TBD | Build Streamlit app wrapper | DEV | 2 days | Medium | v1.0.x stable |
| TASK-TBD | Deploy to Streamlit Cloud | DEVOPS | 2 hrs | Medium | Streamlit app |
| TASK-TBD | Add platform links to docs | DOCS | 1 hr | Medium | Deployment |

### Implementation Notes (for future DEV)

**Colab notebooks should include:**
- Single beam design example
- Batch design from CSV
- BBS generation example
- DXF export example

**Streamlit app structure:**
```
streamlit_app/
├── app.py              # Main entry
├── pages/
│   ├── 01_single_beam.py
│   ├── 02_batch_design.py
│   └── 03_bbs_export.py
└── requirements.txt    # structural-lib-is456 + streamlit
```

---

## Changelog

| Date | Stage | Agent | Change |
|------|-------|-------|--------|
| 2025-12-29 | 1 | CLIENT | Problem, personas, constraints defined |
| 2025-12-29 | 1 | PM | Marked as post-v1.0, set decision date TBD |
| 2025-12-29 | 2 | RESEARCHER | 5 options explored with pros/cons |
| 2025-12-29 | 2 | TESTER | Edge cases added for each option |
| 2025-12-29 | 3 | DEV | Feasibility assessed, options scored |
| 2025-12-29 | 3 | Review | Findings: API costs, signing costs, PyScript risk |
| 2025-12-29 | 4 | PM | Decision: Colab first, then Streamlit |
| 2025-12-29 | 5 | DOCS | Parking lot, future tasks documented |

---

## Token Management: Handoff Strategy

> **For AI agents with context limits:**

Each stage ends with a **Stage Summary** that contains everything the next agent needs:

1. **What was decided** (not the full discussion)
2. **What's next** (explicit action)
3. **Constraints still active** (non-negotiables)

### How to Resume in New Session

If starting fresh with limited context:

```
1. Read ONLY these sections:
   - Problem Statement (what we're solving)
   - Constraints (non-negotiables)
   - Latest Stage Summary (where we are)
   - Decision (if Stage 4+ complete)

2. Skip:
   - Full option details (unless you need to revisit)
   - Changelog (just for auditing)

3. Start from current stage, not from scratch.
```

### Context Size Estimates

| Section | Lines | Essential? |
|---------|-------|------------|
| Problem + Personas | ~30 | ✅ Yes |
| Constraints | ~10 | ✅ Yes |
| Options (all) | ~100 | ⚠️ Only if revisiting |
| Scoring | ~50 | ⚠️ Only if revisiting |
| Decision | ~30 | ✅ Yes (if decided) |
| Stage Summaries | ~20 | ✅ Yes (latest only) |
| Changelog | ~20 | ❌ No (audit only) |

**Minimum context needed:** ~60 lines (Problem + Constraints + Latest Summary)

---

*Research complete. Implementation blocked until v1.0 release.*
