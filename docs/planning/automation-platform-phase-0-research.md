# Automation Platform Phase 0 - Research & Mapping

**Type:** Plan
**Audience:** All Agents
**Status:** Approved
**Importance:** Critical
**Created:** 2026-01-16
**Last Updated:** 2026-01-16
**Related Tasks:** AUTOMATION-PHASE0
**Abstract:** Defines the "Phase 0" roadmap with a focus on industry-leading innovation. Maps 15 core workflows, identifies Excel dominance patterns, and proposes 5 "Flagship" automation targets to validate against feasibility and impact.

---

## Summary & Innovation Vision

Phase 0 isn't just about "digitizing calculations" - it's about moving structural engineering from **static spreadsheets** to **live intelligence**.

**The Innovation Gap:**
- **Legacy Tools (ETABS, SAP2000):** Powerful but blocked box; slow iteration cycles; poor data portability.
- **Modern Platforms (Speckle, Viktor):** Great connectors/builders, but often generic "data hoses" without deep domain intelligence for specific codes (IS 456).
- **Our Unique Value:** A **Code-Aware Design Engine** that targets near-real-time feedback, versioned design traces ("Run log + diff"), and domain-specific AI-assisted optimization.

**Phase 0 Primitives:**
1. **Live Design Loop:** Input -> Validation -> Design -> 3D Visualization with explicit performance budgets.
2. **Structural Intelligence:** Not just "Pass/Fail", but "Why?" (linked to IS 456 clauses).
3. **Data Freedom:** Frictionless interchange via a canonical JSON schema + CSV adapters.

---

## Reality Checks (Issues Found) + Fixes

**Issue 1: Unrealistic latency claims (<50ms for full loop).**
**Fix:** Define tiered budgets:
- Compute-only (single beam): <150ms target, <300ms acceptable
- 3D update (single beam): <300ms target, <600ms acceptable
- Batch runs: async with progress + caching

**Issue 2: "Git for Beams" implies full VCS.**
**Fix:** Rename to **Run Log + Diff**:
- Store inputs, outputs, and schema version
- Compute diff between runs for review

**Issue 3: "Platform CSV" as canonical is limiting.**
**Fix:** Canonical **JSON schema** with CSV import/export adapters.
CSV remains a bridge, not the core.

**Issue 4: Clause-level trace to source line is heavy.**
**Fix:** Start with clause tags + formula references.
Add line-level trace only when stable.

**Issue 5: Missing workflows W6-W15.**
**Fix:** List them explicitly in Phase 0 to avoid hidden scope.

**Issue 6: ETABS forensic flow needs geometry mapping.**
**Fix:** Require geometry mapping inputs or a fallback: "force-only check".

---

## Step 1 - User Journeys & Workflow Map

### Selection Rubric
We prioritize workflows that are high-frequency, prone to human error, and suffer from "black box" opaqueness in current tools.

### Visual Workflow Map (15 User Journeys)

#### W1) The "Video Game" Feedback Loop (Student/Engineer)
- **Concept:** "Play" with structure.
- **Inputs:** Sliders for Depth, Width, Loads.
- **Experience:** As user drags "Depth" slider, the 3D rebar cage updates *instantly* (React-like latency). Utilization ratios color-code in real-time.
- **Innovation:** Builds structural intuition faster than any textbook. Most tools require "Run Analysis" buttons; we aim for "Always-on" calculation.

#### W2) ETABS "Forensic" Investigator (Engineer)
- **Concept:** Debug the black box.
- **Inputs:** ETABS Element Forces CSV + Geometry.
- **Experience:** "Why did beam B23 fail?" User clicks B23. System parses force envelope, runs IS 456 check, and highlights the *exact* governing clause (e.g., "Shear stress 3.1 N/mm^2 > tau_cmax").
- **Innovation:** Explains the failure in plain English/Engineering terms, unlike ETABS which just shows "O/S" (Over Stress).
- **Note:** Requires geometry mapping or a force-only check fallback.

#### W3) The "Structural Diff" (Team Lead)
- **Concept:** Git for Engineering.
- **Experience:** Compare "Design V1" vs "Design V2".
- **Visuals:** 3D model shows unchanged elements in Ghost Grey, Cost Increases in Red, Savings in Green.
- **Innovation:** Move beyond "spot checking" heaps of paper. deterministic, visual change management.

#### W4) Batch Optimization Engine (Project Manager)
- **Concept:** "Find the best cost/performance trade-off."
- **Experience:** "Run 500 beams. Minimize Concrete Volume while keeping Rebar < 2.5%."
- **Output:** Pareto frontier chart (Cost vs Carbon vs Depth).
- **Innovation:** Proactive optimization, not just reactive checking.

#### W5) Automatic "Red-Line" Compliance Audit (Principal)
- **Concept:** Instant QA/QC.
- **Inputs:** CSV/JSON of entire floor.
- **Experience:** System runs 50+ heuristic checks (e.g., "Mismatched units", "Depth < L/20", "Rebar congestion probable").
- **Innovation:** Captures "Senior Engineer wisdom" into automated, always-running rules.

#### W6) Report Generator (Engineer)
- One-click report: inputs, checks, outputs, remarks.

#### W7) BBS + Quantity Summary (Engineer)
- Generate bar schedules and material takeoff.

#### W8) Compliance Summary (Reviewer)
- Highlight failed clauses and assumptions.

#### W9) Student Tutor Loop (Student)
- Step-by-step explanation with visual feedback.

#### W10) Quick Sensitivity Study (Engineer)
- Sweep one parameter (depth, bar dia) and compare results.

#### W11) Drawing Prep Pack (Engineer)
- Export DXF/CSV with consistent naming and units.

#### W12) Revision Tracker (Team Lead)
- Compare Run A vs Run B with a diff summary.

#### W13) Project Dashboard (Manager)
- Status by story, pass/fail summary, outstanding checks.

#### W14) Parametric Optimization (Engineer)
- Multi-objective trade-offs (cost vs. steel vs. depth).

#### W15) Library of Templates (Firm)
- Standardized workflows per firm or school.

---

## Step 2 - Excel Dominance & The "Platform Schema"

Excel is the incumbent because it is flexible. To win, we must be **compatible with Excel** but **better at Logic**.

### The "Universal Bridge" Strategy
We define a **Canonical Platform Schema** (JSON) that acts as the universal adapter.
- **Input:** Adapters for at least one ETABS CSV export + custom Excel formats.
- **Core:** Immutable, versioned Platform Schema (Strict Types, Explicit Units).
- **Output:** Renderers for Report generation, 3D Viewing, Drawing generation.

### Key Excel Patterns to Absorb
1.  **Input Tables:** Columns like `b_mm`, `D_mm`, `Mu_kNm` (Rows = Beams).
2.  **Result Tables:** `Ast_required`, `Status`, `Remarks`.
3.  **Station Data:** Handling 3-point envelopes (Start/Mid/End) vs 15-station outputs.

---

## Step 3 - Innovation & Differentiation Strategy

This is the "Blue Sky" layer that answers the user's request for uniqueness.

### 1. "Live Design" (The Performance Budget)
- **Problem:** Engineering software is sluggish. "Run Analysis" -> Wait -> "View Results".
- **Solution:** We treat the structural model like a **Game State**.
- **Tech:** Streamlit Fragments (`@st.fragment`) + caching for pure functions.
- **Differentiation:** A feel of "tangible" structure.
- **Safety:** Fast path for quick checks, full checks on demand.

### 2. "Glass Box" Verification
- **Problem:** "Trust me, it passes."
- **Solution:** Every calculation emits a Trace Object linked to IS 456 clauses and formula references.
- **UI:** Click any number in the report -> Highlight the formula and clause in sidebar.
- **Differentiation:** Total transparency vs ETABS black box.

### 3. "Semantic" 3D Visualization
- **Problem:** BIM tools show *geometry* (lines/volumes).
- **Solution:** We show *performance*.
- **Tech:** Three.js overlays for `Utilization_Ratio`, `Shear_Demand`, or `Cost_Density`.
- **Differentiation:** 3D as a diagnostic tool, not just a pretty picture.

---

## Step 4 - Candidate "Flagship" Targets (The Top 5)

These are the renamed, ambitious targets for Phase 1.

### Target I1: The "Live" Generative Beam Designer
*(Evolution of Single Beam Design)*
- **Goal:** The fastest beam design tool in the world.
- **Features:**
    - Real-time slider inputs (Geometry/Loads).
    - Instant 3D rebar cage rendering (stirrups, anchors, cutoffs).
    - "Traffic Light" compliance panel (Pass/Fail/Warn updates instantly).
- **Innovation:** Single-beam compute <150ms target.

### Target I2: Automated Optimization Engine
*(Evolution of ETABS Batch)*
- **Goal:** Turn 8 hours of "Trial and Error" into 8 minutes of compute.
- **Features:**
    - Import 100+ beams from ETABS.
    - "Auto-Fix": System increases Depth/Reinforcement automatically to satisfy code.
    - Output: "Optimized Schedule" ready for construction.
- **Innovation:** Assisted optimization with human review.

### Target I3: 4D Project Health Monitor
*(Evolution of Building Viewer)*
- **Goal:** Visual project status at a glance.
- **Features:**
    - Load full building geometry.
    - Color-code by "Design Status" (Not Started, Failed, Optimized, Locked).
    - Filter by Story/Section.
- **Innovation:** Project management meets 3D visualization.

### Target I4: The Structural "Time Machine"
*(Evolution of Design Review)*
- **Goal:** Never lose track of a change.
- **Features:**
    - Load "Yesterday's Run" and "Today's Run".
    - Table Diff: "Beam B12: Ast increased +12%".
    - 3D Diff: Visual heatmap of changes.
- **Innovation:** Run logs + diff for review.

### Target I5: "Ask the Engineer" (AI Assistant Prototype)
*(Evolution of Parametric Study)*
- **Goal:** Natural Language interface for data interrogation.
- **Features:**
    - Shape: "Find all beams with Depth > 600mm."
    - Logic: "Show me the top 3 critical failures in Story 2."
    - Visualization: A simple chat interface (Streamlit Chat) returning tables/3D views.
- **Innovation:** Low-code/No-code access to complex structural data.

---

## Phase 0 Acceptance Criteria (Go/No-Go)

Phase 0 is complete when these are true:
1. **Workflow map (15)** documented with inputs/outputs and time cost.
2. **Platform JSON schema v1** drafted and reviewed.
3. **Two prototypes** working:
   - Live single-beam loop
   - ETABS forensic check (force-only or mapped geometry)
4. **Performance budgets** defined and measured on a baseline machine.
5. **Run log + diff** prototype defined (schema or mock storage).

If these are not met, Phase 1 should not start.

---

## Execution Plan & Next Steps

1. **Define Phase 0 deliverables:** workflow map, schema, performance budgets, risk register.
2. **Prototype two flows:** Live single-beam loop and ETABS forensic check.
3. **Data:** Finalize the Platform JSON schema to support run logs and diff.
4. **Performance:** Profile critical functions and set budgets.

*This refines Phase 0 to be innovative but realistic and testable.*
