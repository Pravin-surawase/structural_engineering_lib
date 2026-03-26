# Structural Automation Platform — Competitor Scan (RC Python Libraries)

**Type:** Research
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-01-16
**Last Updated:** 2026-01-16
**Related Tasks:** AUTOMATION-PHASE0
**Abstract:** Research scan of existing reinforced concrete (RC) Python libraries and adjacent tooling (solvers/testing/perf) to identify differentiation opportunities for a “platform for structural engineering automation” and a verification-first RC design/search engine.

---

## Summary

This scan is driven by a practical question: **as a structural engineer in a firm, what would I adopt next month?**

Key early finding: “RC design calculations” alone is not a moat; multiple projects already exist. The differentiator for our platform/library must be:
1) **Verification-first outputs** (audit trails, clause-linked decision traces)
2) **Search over buildable solutions** (constraint-driven candidate generation)
3) **Test methodology as a first-class feature** (property/metamorphic/differential + visual regression)

## Inputs from Other-Agent Review (treated as hypotheses to validate)

The review suggests a direction that is both innovative and plausibly practical:

### H1 — “Verification-grade design search engine” is a real gap
Instead of a single “design result”, the engine enumerates **buildable** detailing candidates and returns ranked recommendations with traces.

### H2 — Constraint programming is well-suited for detailing layouts
Using CP-SAT (e.g., OR-Tools) to generate only feasible cages avoids brute-force garbage.

### H3 — Testing is the credibility moat
Property-based tests (Hypothesis), metamorphic relations (numerical invariants), and differential tests against curated references create trust.

### H4 — UI should be a “Test Studio”
Not just a front-end: it proves correctness, shows decision traces, and locks regression baselines.

## Competitor/Library Scan (Current)

### 1) `rcdesign` (IS 456:2000)

**Sources:**
- PyPI: https://pypi.org/project/rcdesign/
- GitHub: https://github.com/satish-annigeri/rcdesign
- Docs: https://rcdesign.readthedocs.io/en/latest/

**What it is (positioning):**
- A Python package for analysis/design of RC sections as per IS 456:2000.
- Has examples runnable via `python -m rcdesign` (suggests a packaged, documented library focus).

**Strong points (why engineers might use it):**
- Clear scope (IS 456:2000) and documentation.
- Has references to IS 456 and related handbooks (SP:24, SP:16) which is a credibility signal.
- Looks like a maintained Python package with modern tooling signals (e.g., Ruff mentioned).

**Weak points / gaps (opportunity for us):**
- Likely focused on “compute/design” outcomes; unclear if it provides:
	- decision traces suitable for firm QA/QC
	- versioned run records and diffs
	- buildable detailing enumeration (constructability constraints)
	- a platform SDK for others to assemble tools

**Key learnings for our platform:**
1) We must not compete by “just implementing IS456 checks.”
2) We can integrate/align with this style: strong docs + examples + references.
3) Differentiation must be in the *platform outputs* (RunLog, traces, diffs, schemas) and *search/verification*.

### 2) `ConcreteDesignPy` (ACI/NSCP) — APEC internal-use package

**Source discovered via installed package metadata (pip show):**
- Home page: https://github.com/albertp16/apec-py
- Summary: “APEC internal use only for Concrete Design using ACI and NSCP”

**What it is:**
- A firm-internal style library published to PyPI (at least historically), oriented around ACI/NSCP workflows.

**Strong points:**
- Confirms market reality: firms do publish internal concrete design tools.
- Likely built around practical deliverables (plots/reports) rather than research.

**Weak points / gaps:**
- Internal-use positioning suggests limited generalization:
	- may not be robust as a public SDK
	- unclear validation/audit story
	- unclear extensibility for ecosystem / plugins

**Key learnings for our platform:**
1) “Firm tool library” is a real thing; our platform should support private registries.
2) Governance/versioning/audit trails matter more than shiny features.

### 3) `PyRCD` (RC beam design + multi-objective optimization + 2D/3D detailing)

**Sources:**
- GitHub: https://github.com/TabishIzhar/PyRCD
- Docs: https://pyrcd.readthedocs.io/
- Software Impacts mirror: https://github.com/SoftwareImpacts/SIMPAC-2024-37 (forked from TabishIzhar/PyRCD)

**Identity resolution (important):**
- It appears **not published on PyPI** (at least under the name `PyRCD`), which is consistent with `pip install PyRCD` failing.
- Installation is described as “from Git repository” (clone + install requirements).

**What it is:**
- A Python library focused on **reinforced concrete beam** design + **multi-objective design optimization**.
- The main module `RCbeam` exposes a class `rcb(...)` with explicit units (e.g., width/depth in mm, length in m, moments in kNm, shear in kN).

**Strong points (why it matters to our differentiation research):**
1) It already implements a version of the “search over candidates” idea: `beam_optimization()` produces a Pareto front (dataframe).
2) It explicitly includes **constructability** in optimization (rounding dimensions, market practice constraints).
3) It includes **detail visualization** outputs: `plotting()` produces both **2D and 3D detailing** (via Plotly HTML export in examples).
4) It treats objectives beyond weight/cost: includes **environmental impact** (kgCO2 emission) as a named objective.

**Weak points / gaps (where a firm-grade platform can still win):**
- Distribution/governance: no obvious packaged release cadence; Git-clone install is friction for firms.
- Verification story: docs describe algorithms and parameters, but there’s no obvious concept of:
	- run records (inputs → outputs) that are signed/versioned
	- clause-linked decision traces suitable for QA/QC
	- diffs between runs for review/approval
- Scope is beam-centric; unclear coverage for slabs/columns/walls, load combinations, and project-level workflows.

**Key learnings for us:**
1) The “enumerate buildable candidates + show Pareto front + render detailing” concept already exists in the wild.
2) Our moat must be *engineering-process-grade*: deterministic artifacts, review workflows, regression tests, and code/clause traceability.
3) If we pursue CP-SAT-based detailing search, we should explicitly surpass PyRCD on:
	- constraint transparency (why candidate A is infeasible)
	- reproducibility (seeded search + locked inputs)
	- extensibility (plugins for company bar catalogs, constructability rules, local standards)

## Adjacent Tooling Scan (to support the differentiator)

### OR-Tools CP-SAT (constraint programming)

**Relevance:** Candidate generation under cover/spacing/bars-per-layer constraints.

**Risk/learning:** CP-SAT is powerful, but introducing it has:
- dependency and packaging implications
- learning curve for contributors

Phase 0 stance: research and prototype in isolation before committing to core.

### Numba (performance)

**Relevance:** Fast batch scoring of many candidates (hot loops).

**Risk/learning:** Adds constraints around supported Python/NumPy constructs; might complicate debugging.

Phase 0 stance: profile first; consider Numba only where needed.

### Hypothesis (property-based testing)

**Relevance:** Auto-generate edge cases and enforce invariants; credibility moat.

Phase 0 stance: adopt for kernel invariants once contracts are stable.

### Playwright (visual regression testing)

**Relevance:** Snapshot testing for the 3D viewer/test studio.

Risk/learning: needs CI setup and deterministic rendering strategy.

Phase 0 stance: research minimal viable approach (one golden scene + screenshot baseline).

## Next Steps (Small Step)

1) Add 3–5 more RC-related libraries/tools (even if partial) with the same template: scope, strong points, weak points, learnings.
2) Produce a “Differentiation Map” table: feature vs library vs our plan.

## Added Libraries (Deep Scan Round 2)

### 4) `concreteproperties` (RC section properties, M-ϕ, interaction diagrams)

**Sources:**
- Docs: https://concrete-properties.readthedocs.io/
- PyPI metadata (installed): `concreteproperties` v0.7.0

**What it is:**
- A package for reinforced concrete cross-section properties and non-linear section analyses.
- Explicitly covers: gross/cracked/ultimate properties, moment-curvature, moment interaction and biaxial bending diagrams, and “stress plots”.

**Strong points:**
- Strong documentation and clear feature listing.
- Focused scope: section behavior and response surfaces (M-ϕ, interaction), which are reusable building blocks.
- Practical for engineering workflows where section capacity diagrams are needed.

**Weak points / gaps (platform opportunity):**
- This is a **component library**, not a firm platform: it doesn’t solve governance, audits, diffs, or tool assembly.
- It targets section analysis rather than code-specific “pass/fail” checks + clause traces.

**Key learnings for us:**
1) Our platform should treat “section response engines” as interchangeable kernels.
2) We can borrow their documentation quality and “disclaimer + responsibility” framing.
3) For RC design, we should cleanly separate:
	- section analysis primitives
	- code-check primitives
	- detailing/search primitives

### 5) `sectionproperties` (general section analysis via FEM)

**Sources:**
- Docs: https://sectionproperties.readthedocs.io/
- PyPI metadata (installed): `sectionproperties` v3.10.0

**What it is:**
- Arbitrary cross-section analysis using finite element method.
- Determines section properties for structural design; can visualise stresses under applied forces/moments.

**Strong points:**
- A mature “geometry → properties → stresses” engine.
- Very reusable for many materials and cross-section shapes.

**Weak points / gaps:**
- Not a code design library and not a platform.
- Doesn’t address RC detailing feasibility/search, firm outputs, audit logs.

**Key learnings for us:**
1) Differentiation is not in “we can compute section properties.”
2) Our platform should integrate such engines via contracts rather than re-implement.

### 6) `PyNiteFEA` / `Pynite` (3D elastic structural FEA library)

**Sources:**
- GitHub: https://github.com/JWock82/Pynite
- PyPI metadata (installed): `PyNiteFEA` v2.2.0

**What it is:**
- A simple elastic 3D structural finite element analysis library.
- Notably includes: load cases/combos, shear/moment/deflection results, rendering of models/loads/deformed shapes, and PDF report generation.

**Strong points:**
- Strong open-source engineering practice: testing against textbook problems + CI emphasis.
- Focus on simplicity and documentation (examples-first learning).
- Visualization is treated as part of usability (pyvista/VTK rendering).

**Weak points / gaps (relative to our target):**
- FEA focus; not code-checking or RC detailing/search.
- Like other libs, it doesn’t define a firm governance model (approvals, run diffs, tool registry).

**Key learnings for us:**
1) Their stated objectives are a blueprint: correctness + simplicity + incremental improvement + examples.
2) Our “Test Studio” concept matches their philosophy, but we must extend it to:
	- clause-linked decision traces
	- deterministic run records and diffs
	- buildable detailing candidate search

## Added Libraries (Platform Enablers Round 3)

These are not RC design engines, but they are highly relevant for a *platform* that must interoperate with BIM/CAD and offer credible analysis pipelines.

### 7) `OpenSeesPy` (nonlinear structural analysis runtime)

**Sources:**
- GitHub: https://github.com/zhuminjie/OpenSeesPy
- Docs: https://openseespydoc.readthedocs.io/en/latest/index.html
- PyPI (mentioned by project): https://pypi.org/project/openseespy/

**What it is:**
- A Python interface and distribution channel for OpenSees (structural analysis framework).

**Strong points:**
1) Mature, widely known solver ecosystem; Python makes it more automatable.
2) Clear documentation pointer and packaging story (separate docs + pip folder).

**Weak points / risks (platform implications):**
- Licensing constraints for commercial redistribution are explicitly called out by the project (important for a “platform” product path).
- Not an RC design/detailing library; it’s an analysis runtime.

**Key learnings for us:**
1) A serious platform must treat solver licensing as a first-class constraint.
2) Our contracts should allow “analysis backends” as pluggable components (OpenSees, Code_Aster, commercial APIs) without entangling the core.

### 8) `IfcOpenShell` (IFC toolkit + geometry engine)

**Sources:**
- Website: https://ifcopenshell.org/
- GitHub: https://github.com/IfcOpenShell/IfcOpenShell

**What it is:**
- An open-source toolkit to read/write/modify IFC BIM models, with geometry support and a large ecosystem of tools.
- Includes an explicit tool called `ifcdiff` (“Compare changes between IFC models”), plus other CLI/apps.

**Strong points:**
1) Demonstrates what “ecosystem + tooling suite” looks like in AEC.
2) Includes native concepts we care about: model auditing/testing tools and model diffs.

**Weak points / gaps (relative to our RC automation focus):**
- It’s BIM infrastructure, not code-checking or RC detailing.
- Its licensing mix (LGPL/GPL components) impacts how it can be embedded.

**Key learnings for us:**
1) “Diff” is a huge adoption feature in practice; structural automation should have *design diffs* the way BIM has model diffs.
2) Treat standards + ecosystem tooling as a product surface, not just a library.

### 9) `CadQuery` (parametric CAD-as-code, STEP/DXF export)

**Sources:**
- GitHub: https://github.com/CadQuery/cadquery
- Docs: https://cadquery.readthedocs.io/en/latest/

**What it is:**
- A Python library for building parametric 3D CAD models; supports “high quality CAD formats like STEP and DXF”.

**Strong points:**
1) Makes geometry generation programmable and reproducible (exactly what automation needs).
2) Produces exchange formats (STEP/DXF) that matter for downstream drawings and coordination.

**Weak points / platform risks:**
- Heavy CAD-kernel dependency stack; distribution and CI become more complex.
- Not structural semantics; it’s geometry.

**Key learnings for us:**
1) If we want *drawing export* later (V1.1), CAD-as-code libraries are proven building blocks.
2) Keep geometry generation modular so the core design engine doesn’t depend on CAD kernels.

### 10) `build123d` (modern CAD-as-code, BREP modeling)

**Sources:**
- GitHub: https://github.com/gumyr/build123d
- Docs: https://build123d.readthedocs.io/en/latest/

**What it is:**
- A Python parametric BREP modeling framework built on Open Cascade, emphasizing maintainability, typing, and composable modeling.

**Strong points:**
1) Strong “engineering quality” signals: type hints, linting/mypy workflows, docs.
2) Explicit “data interchange” section (import/export formats), and guidance on viewers.

**Weak points:**
- Like CadQuery, it’s geometry-first; not a structural design library.

**Key learnings for us:**
1) Their “stateless vs builder mode” framing is a useful pattern for us:
	- stateless core computations
	- stateful UI/workflow layers

### 11) `ezdxf` (DXF I/O toolkit)

**Sources:**
- GitHub: https://github.com/mozman/ezdxf
- Docs: https://ezdxf.readthedocs.io/

**What it is:**
- A robust library to create/read/modify DXF across many DXF versions, with CLI tools and add-ons.

**Strong points:**
1) DXF is still a practical interoperability format in firms.
2) Explicit attention to preserving third-party content is a strong “don’t break drawings” design value.

**Weak points:**
- It’s file I/O, not structural design.

**Key learnings for us:**
1) A platform needs reliable interchange primitives (DXF/CSV/JSON/IFC) as *core* plumbing.
2) For later DXF export features, we should keep a “lossless round-trip” mindset.

## Practical Differentiation Map (Draft)

This is a *directional* map; we’ll refine after resolving PyRCD identity and adding 3–5 more libraries.

**Common in existing libraries:**
- Numerical engines (section analysis, FEA)
- Documentation + examples

**Rare / missing (our practical innovation target):**
1) **Buildable detailing search** (constraint-driven enumeration)
2) **Verification artifacts** (RunLog + clause traces + diffs)
3) **Platform SDK** (primitives that let engineers build internal tools quickly)

## Feature-by-Feature Differentiation Table (Draft)

Legend: ✅ = present / explicit focus, ⚠️ = partial / indirect, ❌ = not the focus.

| Feature / Capability | rcdesign | ConcreteDesignPy | PyRCD | concreteproperties | sectionproperties | PyNiteFEA | OpenSeesPy | IfcOpenShell | CadQuery / build123d | ezdxf | Our target (platform) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| RC code checks (IS456/ACI/NSCP) | ✅ (IS456) | ✅ (ACI/NSCP) | ✅ (IS456 default constraints) | ⚠️ (section behavior) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ multi-code kernels + traces |
| RC beam design (produce bars) | ⚠️ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (detailing candidates) |
| Multi-objective optimization | ❌ | ? | ✅ (Pareto front) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (cost/CO2/weight/constructability) |
| Explicit constructability constraints | ⚠️ | ? | ✅ (constructability + rounding) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (catalogs + firm rules) |
| 2D/3D detailing visualization | ❌ | ? | ✅ (2D/3D via Plotly) | ⚠️ (plots) | ⚠️ (stress plots) | ✅ (rendering) | ❌ | ⚠️ (geometry) | ✅ (CAD) | ❌ | ✅ (CAD-quality + JSON contract) |
| Section analysis primitives (M-ϕ, interaction) | ⚠️ | ? | ⚠️ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (as interchangeable engines) |
| Full structural analysis / solver runtime | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (elastic) | ✅ | ❌ | ❌ | ❌ | ⚠️ (pluggable backends) |
| BIM data model I/O (IFC) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ⚠️ (later: IFC connectors) |
| CAD / drawing interchange (STEP/DXF) | ❌ | ❌ | ❌ | ❌ | ❌ | ⚠️ | ❌ | ⚠️ | ✅ | ✅ | ✅ (later: DXF export V1.1) |
| Deterministic run records + diffs | ❌ | ? | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (ifcdiff for IFC) | ❌ | ❌ | ✅ (RunLog + design diffs) |
| Clause-linked decision traceability | ❌ | ? | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (core differentiator) |
| “Test Studio” / regression harness baked in | ❌ | ? | ❌ | ❌ | ❌ | ⚠️ (tests philosophy) | ❌ | ⚠️ (bimtester/ifctester ecosystem) | ❌ | ❌ | ✅ (property + visual regression) |


---

*This document follows the metadata standard defined in copilot-instructions.md.*
