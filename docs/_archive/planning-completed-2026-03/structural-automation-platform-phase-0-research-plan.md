# Structural Automation Platform — Phase 0 Research Plan

**Type:** Plan
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-01-16
**Last Updated:** 2026-01-16
**Related Tasks:** AUTOMATION-PHASE0
**Abstract:** Step-by-step Phase 0 research plan to define a practical, innovative “platform for structural engineering automation” (SDK + runtime), focused on outputs a structural firm can adopt.

---

## Summary

We are not building a single automation. We are defining the **platform** that enables many engineers (and firms) to build and share their own automations safely.

This plan is intentionally “small steps”: each step produces a concrete artifact (spec/table/schema/API sketch) and a decision.

## Research Questions (What must be true?)

1) **Adoption:** Why would a structural firm switch from Excel/macros/ETABS exports to this platform?
2) **Trust:** How do we make outputs *auditable* and *defensible* (liability-aware) without being slow?
3) **Build experience:** What’s the simplest “builder interface” that engineers will actually use?
4) **Interoperability:** What’s the minimal set of data contracts to connect ETABS/Excel/3D and future tools?
5) **Governance:** How do firms manage versions/permissions/approvals of internal tools?

## Practical Outputs (Phase 0 must produce these)

Phase 0 should output artifacts that a real firm can review and say: “Yes, we can pilot this.”

**Required outputs:**
1) **Platform MVP spec**: what the platform is / is not.
2) **StructJSON v0.1**: the canonical data contract(s) for inputs + results + visualization.
3) **SDK primitive list** (names + signatures) that enables building a tool in ~20 lines.
4) **Plugin template**: a reference “tool plugin” that uses the primitives.
5) **Governance model**: versioning + approval workflow + audit trail rules.
6) **Pilot scenarios**: 2–3 workflows a firm can test in 1 week.

## Plan (Small Steps)

### Step 1 — Engineer-in-firm Reality Check (Practicality First) ✅ (do this now)

Goal: Define what a structural engineer in a firm would actually accept as “platform outputs” and what will be rejected.

#### Step 1A: Firm personas (who uses what)

1) **Design Engineer (0–5 yrs)**
	- Lives in Excel + ETABS exports + checklists.
	- Needs: fast checks, fewer mistakes, clear “what to fix.”

2) **Checker / Team Lead (5–15 yrs)**
	- Needs: explainability, consistency across team, diffs between revisions.
	- Hates: undocumented assumptions and “magic.”

3) **Principal / QA/QC**
	- Needs: traceability, auditability, standardization, approval controls.
	- Hates: liability exposure and uncontrolled tool changes.

4) **Automation champion (engineer who codes a bit)**
	- Needs: SDK primitives + templates + stable contracts.
	- Hates: boilerplate UI and reinventing parsing/validation.

#### Step 1B: What “practical outputs” look like in a firm

These are the outputs that survive real project constraints.

**Output 1 — Canonical data contract (StructJSON) with unit safety**
- A firm will accept a platform only if data exchange is predictable.
- Contract must include explicit units (e.g., `span_mm`, `mu_knm`) and strict validation.

**Output 2 — Deterministic run record (RunLog)**
- For every run: input hash, tool version, code version, timestamp, warnings/errors.
- This is essential for QA/QC and “why did the numbers change?” questions.

**Output 3 — Review artifacts (tables + diffs)**
- A checker wants a table they can sign off:
  - pass/fail per element
  - governing checks
  - top 3 reasons for failure
  - delta vs baseline (if applicable)

**Output 4 — One-click exports compatible with existing review flow**
- CSV/Excel export of summaries (still the lingua franca).
- PDF can be later; HTML + CSV is acceptable early.

**Output 5 — A small SDK that reduces build time dramatically**
- The platform must make tool-building faster than “plain Streamlit.”
- Example measurable target: “a new internal tool skeleton in < 30 minutes.”

#### Step 1C: What will NOT be practical (reject list)

1) **Anything that requires full BIM integration on day 1** (Revit/Tekla API heavy).
2) **Anything that replaces ETABS analysis** (we integrate; we don’t compete early).
3) **AI that produces unverified numbers** (AI can assist UX/search, but math must be deterministic).
4) **A node-graph builder as the primary interface** (great later; too heavy for Phase 0).

#### Step 1D: The innovation that *is* practical (innovation without fantasy)

1) **Glass-box verification objects**
	- Every check returns: value, limit, pass/fail, governing clause reference, message.
	- This is both practical and a strong differentiator vs Excel/ETABS.

2) **Structural diffs / time machine**
	- Firms constantly revise models; versioned diffs are immediately valuable.

3) **Semantic 3D review**
	- 3D is not decoration: it’s a QA layer (color by status/utilization).
	- Practical because it catches “mapping/ID/story” errors early.

#### Step 1E: Step 1 decision outputs (locked after Step 1)

After Step 1 we lock:
1) The **minimum list of platform outputs** (StructJSON + RunLog + ReviewTable).
2) The **primary persona** for Phase 0 (recommendation: Automation champion + Checker).
3) The “no-go” list above.

### Step 2 — Workflow Map & Pain Points (Firm jobs-to-be-done)

Goal: Map 8–12 firm workflows to platform opportunities and decide the 2–3 pilot scenarios.

### Step 3 — Platform Primitives & Contracts

Goal: Define `sk.ui`, `sk.engine`, `sk.viz`, `sk.io` minimal primitives + signatures and the `StructJSON v0.1` schema(s).

### Step 4 — Governance & Ecosystem (Registry, versions, approvals)

Goal: Define how firms can safely publish internal tools and lock versions.

### Step 5 — Repo Fit Check

Goal: Validate the plan against current repo architecture (Core/Application/UI) and existing 3D contract.

### Step 6 — Phase 0 Deliverables & Acceptance Criteria

Goal: Write acceptance tests for Phase 0 outputs (docs + sample plugin + schema validation).

## Next Steps (Do next, one step only)

Proceed to **Step 2**: map firm workflows and select 2–3 pilot scenarios with clear acceptance criteria.

---

*This document follows the metadata standard defined in copilot-instructions.md.*
