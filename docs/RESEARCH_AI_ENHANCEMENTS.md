# Research Log — AI/High-Value Enhancements

**Research Version:** v0.8-ideation  
**Last Updated:** 2025-12-15  
**Scope:** Identify additions that make the library materially more valuable for professional use (beyond current v0.7 strength/detailing scope).

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
- Limitations: DuckDuckGo API returns minimal snippets; insights above are distilled from high-level search terms and known industry trends.

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
