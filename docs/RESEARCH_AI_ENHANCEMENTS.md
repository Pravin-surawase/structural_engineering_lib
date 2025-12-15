# Research Log — AI/High-Value Enhancements

**Research Version:** v0.8-ideation  
**Last Updated:** 2025-12-15  
**Scope:** Identify additions that make the library materially more valuable for professional use (beyond current v0.7 strength/detailing scope).

This log captures goals/mindset, a lightweight online-scan snapshot, and a prioritized shortlist of high-value additions (serviceability, rebar optimizer, BBS/BOM export, load-combo compliance checking), plus longer-horizon AI/NL helper ideas.

---

## Mindset & Goals
- Deliver **high-leverage, low-friction** features that slot into existing workflows (Excel/Python) without heavy user training.
- Maintain **code compliance** (IS 456/IS 875/IS 1893) as the non-negotiable backbone; AI is an accelerator, not a substitute for code checks.
- Keep **Python/VBA parity** for core calculations; advanced/AI helpers can remain Python-first where needed.
- Prioritize **explainability** (calculations, inputs, assumptions) to make AI features auditable.

---

## Quick Online Scan (Dec 15, 2025)
- **Structural health monitoring + ML**: abundant academic work (e.g., “deep learning for SHM review” queries surface review papers on vibration-based damage detection). Relevance: informs future module for post-construction monitoring, but not immediate for design library.
- **Rebar optimization / layout automation**: industry chatter around automated detailing/rebar schedulers; most proprietary (e.g., CAD plugins) with few open-source options. Opportunity: open, transparent optimizer tied to code rules.
- **Crack/deflection ML prediction**: some papers use ML to predict serviceability (deflection/crack) from geometry/material inputs. Relevance: a data-driven checker could complement code formulas but must remain secondary to codified checks.
- Note: This is a lightweight scan of publicly available material (not a systematic literature review). The takeaways above are synthesized from high-level search results and general domain trends.

---

## Candidate Initiatives

1) **Serviceability Module (Deflection + Crack Width)**  
   - Value: Mandatory for professional acceptance; unblocks “production-ready” status.  
   - Scope: IS 456 Cl. 23.2 (span/depth + modification factors), Annex C (detailed), Annex F (crack width limits by exposure).  
   - Deliverables: `serviceability.py` + `M17_Serviceability.bas`, 20+ tests, docs, API/README updates.

2) **Load Combination & Compliance Checker**  
   - Value: One-click “code compliance” verdict for a beam row from ETABS/CSV.  
   - Scope: IS 875 load combos, IS 456 limit state checks (strength + serviceability), output structured pass/fail with remarks.  
   - Deliverables: Combo generator, wrapper that calls flexure/shear/serviceability; Excel-friendly summary.

3) **Rebar Arrangement Optimizer (Cost/Weight/Constructability)**  
   - Value: Converts required Ast into best bar pattern (size/count/layers) respecting spacing, cover, constructability, and stocking rules.  
   - Approach: Small search/ILP over standard diameters; optional objective (min steel weight / min bar count / min congestion).  
   - Output: Pattern, spacing check, callouts, and “why chosen”.

4) **Bar Bending Schedule (BBS) + BOM Export**  
   - Value: Moves detailing into fabrication deliverables; high utility for site teams.  
   - Scope: From detailing result → cutting lengths, hooks, bends, quantities; export CSV/PDF; align with IS 2502 conventions.  
   - VBA/Python parity: Python-first for generation; VBA formatter for Excel users.

5) **IFC/DXF/BIM Bridge (Lightweight)**  
   - Value: Interop with CAD/BIM without locking into proprietary plugins.  
   - Scope: Export beam detailing to IFC entities (beam + rebars as proxy geometry), enrich DXF with metadata layers, optional glTF preview.  
   - Constraint: Keep dependencies optional (Python-only).

6) **Parametric Batch Runner + Sensitivity/Monte Carlo**  
   - Value: Helps engineers test robustness (cover variations, material strengths, bar sizes).  
   - Scope: Simple API to sweep parameters and produce histograms/summaries; flags brittle designs.  
   - Output: CSV/plots (plots optional to keep deps light).

7) **Natural-Language Assistant / Explainer (Python-first)**  
   - Value: Converts plain-language prompts (“Design 300x500 beam, M25/Fe500, Mu=150, span 4m”) into structured calls; produces “calculation sheet” style explanations.  
   - Guardrails: Always show inputs/outputs and clause references; no hidden calculations.  
   - Deployment: Optional CLI flag or notebook helper; no hard dependency on an LLM runtime.

8) **Post-Construction Monitoring Hook (Future)**  
   - Value: Long-term roadmap item—ingest SHM data (strain, vibration) and compare against design/serviceability envelopes.  
   - Status: Parked until core design/serviceability is complete.

---

## Prioritized Shortlist (High Impact / Moderate Effort)
- **P1:** Serviceability module (Deflection + Crack) — prerequisite for production.
- **P2:** Rebar arrangement optimizer — immediate user value, small search space, improves constructability/cost outcomes.
- **P3:** BBS/BOM export — closes loop to fabrication, pairs with optimizer.
- **P4:** Compliance checker with load combos — “one-button” pass/fail for ETABS/CSV rows.

---

## Proposed Next Steps (v0.8-v0.9)
- **v0.8:** Implement P1 (deflection + crack) + baseline P4 (combination wrapper using existing design checks).  
- **v0.9:** Add P2 (optimizer) and P3 (BBS/BOM), wire outputs to DXF/Excel schedules; explore lightweight IFC metadata.
- **Research follow-up:** If time permits, prototype P7 (NL assistant) as an opt-in CLI/notebook helper that emits the exact function calls used.

---

## Notes
- Keep any AI-driven feature **transparent and overrideable**; always show the deterministic calculation path.
- Prefer **small, deterministic search/optimization** over heavyweight ML to avoid reproducibility issues in regulated contexts.

---

## Research Update (Pass 2 — Repo-Aware Design Notes, Dec 15, 2025)

This pass focuses on *how* the shortlisted initiatives would fit into the current codebase (Python + VBA), and what “done” should mean in terms of APIs, outputs, and tests.

### Repo Scan Takeaways
- The Python package is organized around small, testable modules (e.g., `flexure.py`, `shear.py`) with simple dataclass outputs in `types.py`.
- The current public API surface in `api.py` is intentionally small, suggesting new features should remain **module-first** and only add API wrappers once stable.
- Existing design functions already compute intermediate quantities useful for serviceability/compliance (e.g., `xu`, `pt_provided`, `tv/tc/tc_max`). New features should reuse these outputs rather than re-derive values in multiple places.

### 1) Serviceability Module — Practical Implementation Notes
- **Keep two levels of rigor:**
   - Level A (fast): span/depth checks and modification-factor based deflection verification (good for Excel “quick check”).
   - Level B (detailed): optional calculations where inputs are available (sustained loads, creep/shrinkage assumptions, cracked section behavior).
- **Output structure:** add a `ServiceabilityResult` dataclass in `types.py` with fields like `deflection_ok`, `crack_ok`, `limit_values`, `governing_case`, and `remarks`.
- **Avoid silent assumptions:** make any assumed values explicit (e.g., sustained load fraction, effective span definition, exposure-driven crack limits).
- **Acceptance criteria (tests):**
   - “No crash” tests across typical ranges.
   - Boundary tests around $L/d$ limits and modification factor transitions.
   - Deterministic results for representative benchmark examples (even if the benchmark values are from the standard’s worked examples or internal reference sheets).

### 2) Load Combination + Compliance Checker — Minimal Useful Shape
- Treat this as a **reporting/orchestration** layer: it should not duplicate flexure/shear math.
- **Two outputs:**
   - Machine-friendly: a list of per-combo results (pass/fail + controlling ratio).
   - Excel-friendly: a compact summary row with governing combo + remarks.
- **Design principle:** include “why fail” text (e.g., “Tv > Tc,max”, “Ast > 4% bD”, “serviceability deflection exceeds limit”).
- **Acceptance criteria (tests):**
   - Given known combo inputs, the governing combo is stable.
   - Any failure in a sub-check propagates correctly to overall verdict.

### 3) Rebar Arrangement Optimizer — Constraints to Encode First
Prioritize deterministic, engineer-explainable constraints before any fancy objective function.

- **Hard constraints (must-pass):**
   - Bar diameters from a standard set.
   - Maximum bars per layer (based on beam width, cover, stirrup dia, bar dia, min clear spacing).
   - Min spacing checks and “constructability sanity” (avoid extreme congestion).
   - Limit on layers (e.g., 2–3) unless user opts in.
- **Soft objectives (choose one):** minimize steel weight, minimize bar count, or minimize congestion.
- **Output structure:** a `RebarLayoutResult` that includes chosen diameters/counts/layers plus a list of passed/failed spacing checks.
- **Acceptance criteria (tests):**
   - For fixed Ast demand and geometry, solution is deterministic.
   - If no feasible layout exists, return a structured failure with actionable reason (“insufficient width for min spacing”).

### 4) BBS/BOM Export — Keep It Code-Agnostic
- Start from **detailing outputs** (bar counts/lengths/shapes) rather than trying to infer detailing from strength design.
- Represent BBS as a list of line-items (shape code, dia, cut length, quantity, mark) and export CSV first.
- Add PDF/pretty Excel formatting later; keep core generation logic independent.
- **Acceptance criteria (tests):**
   - Known detailing input produces stable total weight and total length.
   - Hooks/bends and length rounding rules are explicit and tested.

### 5) VBA/Python Parity Guidance
- Keep **core deterministic calculations** parity across Python/VBA (serviceability “Level A”, compliance wrapper, basic spacing checks).
- Keep advanced helpers Python-first if they need non-trivial search/optimization; provide VBA as a consumer (call Python or use simplified VBA variant) only if required.

### AI/NL Helper — Guardrails Clarified
- If an NL assistant is added later, it should only:
   - parse user intent → structured inputs,
   - call the same deterministic functions as everyone else,
   - return a calculation-sheet style explanation with clause references.
- It must not introduce alternative computation paths.

### Open Questions (Needed Before Implementation)
- Beam scope: simply supported vs continuous (effective span rules differ).
- Exposure classes to support first for crack limits.
- Whether “compliance checker” should accept **factored design actions only** (simpler) or generate combos from unfactored loads (more helpful but requires clearer conventions).
